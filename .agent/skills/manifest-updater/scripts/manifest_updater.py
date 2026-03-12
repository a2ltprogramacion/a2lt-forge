#!/usr/bin/env python3
# manifest_updater.py — La Forja / A2LT Soluciones
# Atomic manifest management: init, add, update, deprecate, validate, check-dependents.
# All writes are atomic: read → modify in memory → validate → write.
# Usage: python manifest_updater.py --operation <op> --plane <plane> [options]

import os
import sys
import json
import re
import argparse
import shutil
from datetime import datetime, timezone
from collections import defaultdict


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VALID_OPERATIONS  = {"init", "add", "update", "deprecate", "check-dependents", "validate"}
VALID_PLANES      = {"agent", "catalogo", "package", "all"}
VALID_KINDS       = {"skill", "agent", "workflow"}
VALID_STATUSES    = {"active", "draft", "deprecated", "pending_validation"}
VALID_TYPES       = {"backend", "frontend", "integration", "utility"}
VALID_TIERS       = {"vcard", "authority", "enterprise", "all"}

# Schema v2.0.0 alineado con manifest.json en producción
REQUIRED_FIELDS   = {"name", "version", "kind", "type", "status", "path", "description"}
OPTIONAL_FIELDS   = {"dependencies", "compatibility", "notes", "tier"}
LEGACY_PATH_PREFIX = "./.agent/"  # Prohibido — usar ./agent/ en su lugar

SEMVER_RE         = re.compile(r'^\d+\.\d+\.\d+$')
KEBAB_RE          = re.compile(r'^[a-z0-9][a-z0-9-]*[a-z0-9]$')


# ---------------------------------------------------------------------------
# Project root + manifest path resolution
# ---------------------------------------------------------------------------

def find_project_root(start: str) -> str:
    current = os.path.abspath(start)
    for _ in range(10):
        if os.path.exists(os.path.join(current, "AGENTS.md")):
            return current
        if os.path.exists(os.path.join(current, "agent", "manifest.json")):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    return os.path.abspath(start)


def resolve_manifest_path(root: str, plane: str, project_name: str = "") -> str:
    if plane == "agent":
        return os.path.join(root, "agent", "manifest.json")
    if plane == "catalogo":
        return os.path.join(root, "catalogo", "manifest.json")
    if plane == "package":
        if not project_name:
            print("ERROR: --project-name requerido para plane=package.", file=sys.stderr)
            sys.exit(7)
        return os.path.join(root, "output", project_name, "package-manifest.json")
    return ""  # 'all' handled separately


# ---------------------------------------------------------------------------
# Manifest I/O
# ---------------------------------------------------------------------------

def load_manifest(path: str) -> dict:
    if not os.path.exists(path):
        print(f"ERROR: Manifiesto no encontrado: {path}\n"
              "       Ejecuta --operation init primero.", file=sys.stderr)
        sys.exit(7)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"ERROR: JSON inválido en {path}: {e}", file=sys.stderr)
        sys.exit(3)


def save_manifest(path: str, data: dict, dry_run: bool = False) -> None:
    data["last_updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    if dry_run:
        print("\n[DRY RUN] Cambios que se aplicarían:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return

    # Atomic write: write to .tmp, then rename
    tmp_path = path + ".tmp"
    backup_path = path + ".bak"

    try:
        # Backup current
        if os.path.exists(path):
            shutil.copy2(path, backup_path)

        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")

        os.replace(tmp_path, path)
        print(f"[Manifest] Guardado: {path}")

    except Exception as e:
        # Restore backup if available
        if os.path.exists(backup_path):
            shutil.copy2(backup_path, path)
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        print(f"ERROR: Fallo al escribir {path}: {e}", file=sys.stderr)
        sys.exit(3)


def init_manifest(path: str, plane: str, dry_run: bool = False) -> None:
    if os.path.exists(path) and not dry_run:
        print(f"ERROR: El manifiesto ya existe: {path}\n"
              "       Usa --operation validate para auditarlo.", file=sys.stderr)
        sys.exit(2)

    plane_labels = {
        "agent":    "La Forja - Core Toolkit",
        "catalogo": "La Forja - Catálogo",
        "package":  project_name or "La Forja - Paquete",
    }
    data = {
        "schema_version": "2.0.0",
        "plane": plane,
        "ecosystem": plane_labels.get(plane, "La Forja"),
        "version": "1.0.0",
        "description": f"Manifest of {plane_labels.get(plane, plane)} layer.",
        "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "last_author": "Argenis",
        "components": [],
        "metadata": {
            "source_url": f"./{'agent' if plane == 'agent' else plane}/manifest.json",
            "is_canonical_source": True,
            "schema_version": "2.0.0",
            "notes": "Actualizar SOLO al desplegar exitosamente (Paso 7 §7.2/7.3)."
        }
    }

    os.makedirs(os.path.dirname(path), exist_ok=True)
    save_manifest(path, data, dry_run)
    if not dry_run:
        print(f"[Manifest] Inicializado: {path}")


# ---------------------------------------------------------------------------
# Component validation
# ---------------------------------------------------------------------------

def validate_component_schema(comp: dict) -> list[str]:
    """Returns list of error strings. Empty = valid."""
    errors = []

    # Required fields
    for field in REQUIRED_FIELDS:
        if field not in comp:
            errors.append(f"Campo obligatorio ausente: '{field}'")

    if "name" in comp:
        if not KEBAB_RE.match(comp["name"]):
            errors.append(f"'name' no cumple kebab-case: {comp['name']}")

    if "version" in comp:
        if not SEMVER_RE.match(str(comp["version"])):
            errors.append(f"'version' no sigue SemVer X.Y.Z: {comp['version']}")

    if "kind" in comp and comp["kind"] not in VALID_KINDS:
        errors.append(f"'kind' inválido: {comp['kind']}. Válidos: {sorted(VALID_KINDS)}")

    if "status" in comp and comp["status"] not in VALID_STATUSES:
        errors.append(f"'status' inválido: {comp['status']}. Válidos: {sorted(VALID_STATUSES)}")

    # dependencies: optional pero si existe debe ser objeto {internal:[], external:[]}
    if "dependencies" in comp:
        deps = comp["dependencies"]
        if not isinstance(deps, dict):
            errors.append("'dependencies' debe ser un objeto con claves 'internal' y 'external'.")
        else:
            for key in ("internal", "external"):
                if key in deps and not isinstance(deps[key], list):
                    errors.append(f"'dependencies.{key}' debe ser una lista.")

    # path: detectar ruta legacy
    if "path" in comp and comp["path"].startswith(LEGACY_PATH_PREFIX):
        errors.append(
            f"[RUTA-LEGACY §0.4] 'path' usa prefijo prohibido './.agent/'. "
            f"Usar './agent/' en su lugar: {comp['path']}"
        )

    # Optional field validation
    if "type" in comp and comp["type"] not in VALID_TYPES:
        errors.append(f"'type' inválido: {comp['type']}. Válidos: {sorted(VALID_TYPES)}")

    if "tier" in comp and comp["tier"] not in VALID_TIERS:
        errors.append(f"'tier' inválido: {comp['tier']}. Válidos: {sorted(VALID_TIERS)}")

    return errors


def validate_manifest_integrity(
    manifest: dict,
    root: str,
    plane: str
) -> tuple[list[str], list[str]]:
    """
    Full integrity check. Returns (errors, warnings).
    errors = fatal, warnings = advisory.
    """
    errors   = []
    warnings = []
    components = manifest.get("components", [])

    # Schema top-level
    for field in ("schema_version", "plane", "components"):
        if field not in manifest:
            errors.append(f"Campo de manifiesto ausente: '{field}'")

    # Per-component checks
    seen_names = {}
    for i, comp in enumerate(components):
        prefix = f"[{comp.get('name', f'entry#{i}')}]"

        # Schema
        schema_errors = validate_component_schema(comp)
        for e in schema_errors:
            errors.append(f"{prefix} {e}")

        # Name uniqueness
        name = comp.get("name", "").lower()
        if name in seen_names:
            errors.append(
                f"{prefix} Nombre duplicado. Ya existe en posición {seen_names[name]}."
            )
        else:
            seen_names[name] = i

        # Path existence
        path = comp.get("path", "")
        if path:
            full_path = os.path.join(root, path.lstrip("./"))
            if not os.path.exists(full_path):
                errors.append(f"{prefix} Directorio no encontrado: {path}")
            else:
                # SKILL.md / AGENT.md presence
                kind = comp.get("kind", "")
                entry_file = "SKILL.md" if kind == "skill" else "AGENT.md"
                entry_path = os.path.join(full_path, entry_file)
                if not os.path.exists(entry_path):
                    errors.append(
                        f"{prefix} {entry_file} no encontrado en: {path}"
                    )

        # Version format (warning if missing patch)
        version = str(comp.get("version", ""))
        if version and not SEMVER_RE.match(version):
            warnings.append(f"{prefix} Versión no sigue SemVer: {version}")

    # Dependency resolution (cross-component) — schema v2.0.0
    all_names = {c.get("name") for c in components if c.get("status") == "active"}
    for comp in components:
        deps = comp.get("dependencies", {})
        # Solo validar dependencias internas (las externas son paquetes PyPI/npm)
        if isinstance(deps, dict):
            internal_deps = deps.get("internal", [])
        else:
            internal_deps = deps  # fallback lista plana
        for dep in internal_deps:
            dep_name = dep.get("name") if isinstance(dep, dict) else dep
            optional  = dep.get("optional", False) if isinstance(dep, dict) else False
            if dep_name and dep_name not in all_names:
                if optional:
                    warnings.append(
                        f"[{comp.get('name')}] Dependencia interna opcional no encontrada "
                        f"en componentes activos de este plano: '{dep_name}'"
                    )
                else:
                    warnings.append(
                        f"[{comp.get('name')}] Dependencia interna '{dep_name}' no encontrada "
                        f"en componentes activos de este manifiesto."
                    )

    # DAG check — circular dependencies
    cycle = find_cycle(components)
    if cycle:
        errors.append(f"[CICLO DAG] Dependencia circular detectada: {' → '.join(cycle)}")

    # Orphan check — directories not in manifest
    if plane in ("agent", "catalogo"):
        skills_dir = os.path.join(root, plane if plane == "catalogo" else "agent", "skills")
        agentes_dir = os.path.join(
            root,
            "catalogo/agentes" if plane == "catalogo" else "agent/agents"
        )
        registered_paths = {
            os.path.normpath(os.path.join(root, c.get("path", "").lstrip("./")))
            for c in components
        }
        for d in (skills_dir, agentes_dir):
            if os.path.exists(d):
                for entry in os.listdir(d):
                    entry_path = os.path.join(d, entry)
                    if os.path.isdir(entry_path):
                        if os.path.normpath(entry_path) not in registered_paths:
                            warnings.append(
                                f"Directorio no registrado en manifiesto: "
                                f"{os.path.relpath(entry_path, root)}"
                            )

    return errors, warnings


def find_cycle(components: list[dict]) -> list[str] | None:
    """Detects circular dependencies via DFS. Returns cycle path or None."""
    graph = {c["name"]: [] for c in components if "name" in c}
    for comp in components:
        name = comp.get("name")
        if not name:
            continue
        deps = comp.get("dependencies", {})
        # Schema v2.0.0: object; v1.0.0 fallback: flat list
        if isinstance(deps, dict):
            all_deps = deps.get("internal", []) + deps.get("external", [])
        else:
            all_deps = deps
        for dep in all_deps:
            dep_name = dep.get("name") if isinstance(dep, dict) else dep
            if dep_name and dep_name in graph:
                graph[name].append(dep_name)

    visited = set()
    rec_stack = set()
    path = []

    def dfs(node):
        visited.add(node)
        rec_stack.add(node)
        path.append(node)
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                result = dfs(neighbor)
                if result:
                    return result
            elif neighbor in rec_stack:
                cycle_start = path.index(neighbor)
                return path[cycle_start:] + [neighbor]
        path.pop()
        rec_stack.discard(node)
        return None

    for node in list(graph.keys()):
        if node not in visited:
            result = dfs(node)
            if result:
                return result
    return None


# ---------------------------------------------------------------------------
# Operations
# ---------------------------------------------------------------------------

def op_add(manifest: dict, component: dict, root: str) -> dict:
    schema_errors = validate_component_schema(component)
    if schema_errors:
        print("ERROR: El componente no pasa validación de schema:", file=sys.stderr)
        for e in schema_errors:
            print(f"  ✗ {e}", file=sys.stderr)
        sys.exit(3)

    existing = [c for c in manifest["components"]
                if c.get("name", "").lower() == component["name"].lower()]
    if existing:
        print(
            f"ERROR: '{component['name']}' ya existe en el manifiesto. "
            "Usa --operation update para modificarlo.",
            file=sys.stderr
        )
        sys.exit(2)

    # Verify path exists
    full_path = os.path.join(root, component.get("path", "").lstrip("./"))
    if not os.path.exists(full_path):
        print(
            f"ERROR: El path declarado no existe: {component['path']}\n"
            "       Despliega el componente antes de registrarlo.",
            file=sys.stderr
        )
        sys.exit(4)

    # Inicializar dependencies como objeto si no viene declarado
    if "dependencies" not in component:
        component["dependencies"] = {"internal": [], "external": []}

    manifest["components"].append(component)
    print(f"[Manifest] Componente agregado: {component['name']} v{component['version']}")
    return manifest


def op_update(manifest: dict, component: dict) -> dict:
    name = component.get("name", "").lower()
    for i, comp in enumerate(manifest["components"]):
        if comp.get("name", "").lower() == name:
            # Merge: keep existing fields, overwrite with provided ones
            manifest["components"][i] = {**comp, **component}
            print(
                f"[Manifest] Actualizado: {comp['name']} "
                f"v{comp.get('version')} → v{component.get('version', comp.get('version'))}"
            )
            return manifest

    print(
        f"ERROR: '{component.get('name')}' no encontrado. "
        "Usa --operation add para registrarlo.",
        file=sys.stderr
    )
    sys.exit(1)


def op_deprecate(manifest: dict, name: str) -> dict:
    name_lower = name.lower()
    for i, comp in enumerate(manifest["components"]):
        if comp.get("name", "").lower() == name_lower:
            if comp.get("status") == "deprecated":
                print(f"[Manifest] '{name}' ya está deprecado.")
                return manifest
            manifest["components"][i]["status"] = "deprecated"
            print(f"[Manifest] Deprecado: {comp['name']}")
            return manifest

    print(f"ERROR: '{name}' no encontrado en el manifiesto.", file=sys.stderr)
    sys.exit(1)


def op_check_dependents(manifest: dict, name: str) -> list[str]:
    """Returns list of active component names that depend on `name`.
    Handles schema v2.0.0: dependencies = {"internal": [...], "external": [...]}
    """
    dependents = []
    name_lower = name.lower()
    for comp in manifest["components"]:
        if comp.get("status") not in ("active", "draft", "pending_validation"):
            continue
        deps = comp.get("dependencies", {})
        # Schema v2.0.0: object with internal/external keys
        if isinstance(deps, dict):
            all_deps = deps.get("internal", []) + deps.get("external", [])
        else:
            # Fallback: schema v1.0.0 flat list
            all_deps = deps
        for dep in all_deps:
            dep_name = dep.get("name") if isinstance(dep, dict) else dep
            if dep_name and dep_name.lower() == name_lower:
                dependents.append(comp["name"])
    return dependents


def op_validate(manifest_path: str, root: str, plane: str) -> tuple[list, list]:
    manifest = load_manifest(manifest_path)
    errors, warnings = validate_manifest_integrity(manifest, root, plane)

    print(f"\n[Manifest] Validando: {manifest_path}")

    if warnings:
        print(f"\n  Advertencias ({len(warnings)}):")
        for w in warnings:
            print(f"    ⚠ {w}")

    if errors:
        print(f"\n  Errores fatales ({len(errors)}):", file=sys.stderr)
        for e in errors:
            print(f"    ✗ {e}", file=sys.stderr)
        print("\n[ALTO] El manifiesto tiene errores fatales. "
              "Resuelve antes de continuar con RAG indexing o deployment.",
              file=sys.stderr)
    else:
        print(f"\n  [Manifest] Validación exitosa — sin errores fatales.")

    return errors, warnings


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="La Forja — Gestión atómica de manifiestos del ecosistema."
    )
    parser.add_argument(
        "--operation",
        required=True,
        choices=list(VALID_OPERATIONS),
        help="Operación a ejecutar."
    )
    parser.add_argument(
        "--plane",
        required=True,
        choices=list(VALID_PLANES),
        help="Manifiesto destino: agent | catalogo | package | all (solo para validate)."
    )
    parser.add_argument(
        "--component",
        default=None,
        help="JSON string con los datos del componente (requerido para add/update)."
    )
    parser.add_argument(
        "--name",
        default=None,
        help="Nombre del componente (requerido para deprecate y check-dependents)."
    )
    parser.add_argument(
        "--project-name",
        default=None,
        help="Nombre del proyecto (requerido cuando --plane package)."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without writing to disk."
    )
    parser.add_argument(
        "--json-output",
        action="store_true",
        help="Output results as JSON (for programmatic consumption)."
    )
    args = parser.parse_args()

    root = find_project_root(os.getcwd())

    # --- VALIDATE ALL ---
    if args.operation == "validate" and args.plane == "all":
        all_errors = {}
        all_warnings = {}
        planes = ["agent", "catalogo"]
        for p in planes:
            mpath = resolve_manifest_path(root, p, "")
            if os.path.exists(mpath):
                errs, warns = op_validate(mpath, root, p)
                all_errors[p]   = errs
                all_warnings[p] = warns
            else:
                print(f"[Manifest] Omitido (no existe): {mpath}")

        if args.json_output:
            print(json.dumps(
                {"errors": all_errors, "warnings": all_warnings},
                indent=2, ensure_ascii=False
            ))

        has_errors = any(v for v in all_errors.values())
        sys.exit(3 if has_errors else 0)

    # --- SINGLE PLANE OPERATIONS ---
    if args.plane == "all" and args.operation != "validate":
        print("ERROR: --plane all solo está disponible para --operation validate.",
              file=sys.stderr)
        sys.exit(3)

    manifest_path = resolve_manifest_path(root, args.plane, args.project_name or "")

    # INIT
    if args.operation == "init":
        init_manifest(manifest_path, args.plane, args.dry_run)
        sys.exit(0)

    # VALIDATE (single plane)
    if args.operation == "validate":
        errs, warns = op_validate(manifest_path, root, args.plane)
        if args.json_output:
            print(json.dumps(
                {"errors": errs, "warnings": warns},
                indent=2, ensure_ascii=False
            ))
        sys.exit(3 if errs else 0)

    # CHECK-DEPENDENTS
    if args.operation == "check-dependents":
        if not args.name:
            print("ERROR: --name requerido para check-dependents.", file=sys.stderr)
            sys.exit(3)
        manifest = load_manifest(manifest_path)
        dependents = op_check_dependents(manifest, args.name)
        if dependents:
            print(f"[Manifest] Dependientes activos de '{args.name}': {dependents}")
            if args.json_output:
                print(json.dumps({"dependents": dependents}, indent=2))
            sys.exit(5)  # exit 5 = has dependents (blocks deprecation)
        else:
            print(f"[Manifest] '{args.name}' no tiene dependientes activos.")
            if args.json_output:
                print(json.dumps({"dependents": []}, indent=2))
            sys.exit(0)

    # ADD / UPDATE / DEPRECATE — require --component or --name
    manifest = load_manifest(manifest_path)

    if args.operation in ("add", "update"):
        if not args.component:
            print("ERROR: --component requerido para add/update.", file=sys.stderr)
            sys.exit(3)
        try:
            component = json.loads(args.component)
        except json.JSONDecodeError as e:
            print(f"ERROR: JSON inválido en --component: {e}", file=sys.stderr)
            sys.exit(3)

        if args.operation == "add":
            manifest = op_add(manifest, component, root)
        else:
            manifest = op_update(manifest, component)

    elif args.operation == "deprecate":
        if not args.name:
            print("ERROR: --name requerido para deprecate.", file=sys.stderr)
            sys.exit(3)
        # Auto check-dependents before deprecating
        dependents = op_check_dependents(manifest, args.name)
        if dependents:
            print(
                f"[ALTO] No se puede deprecar '{args.name}': "
                f"es dependencia activa de: {dependents}\n"
                "       Actualiza o depreca los dependientes primero.",
                file=sys.stderr
            )
            sys.exit(5)
        manifest = op_deprecate(manifest, args.name)

    save_manifest(manifest_path, manifest, args.dry_run)
    sys.exit(0)


if __name__ == "__main__":
    main()
