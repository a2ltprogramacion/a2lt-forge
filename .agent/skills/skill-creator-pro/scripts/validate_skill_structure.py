#!/usr/bin/env python3
# validate_skill_structure.py — La Forja / A2LT Soluciones
# Validates a skill directory against La Forja standards (AGENTS.md §5.7 + §3.4).
# Usage: python validate_skill_structure.py <skill_path> [--plane agent|catalogo]

import os
import sys
import json
import re
import argparse


# ---------------------------------------------------------------------------
# YAML frontmatter parser
# ---------------------------------------------------------------------------

def parse_yaml_frontmatter(content: str) -> dict:
    """Regex-based parser for YAML frontmatter. Handles multiline | blocks."""
    data = {}
    match = re.search(r'^---\s*\n(.*?)\n---\s*(\n|$)', content, re.DOTALL)
    if not match:
        raise ValueError("No se encontró un bloque de frontmatter YAML válido (--- ... ---).")

    yaml_block = match.group(1)

    # name
    name_match = re.search(r'^name:\s*(.+)$', yaml_block, re.MULTILINE)
    if name_match:
        data['name'] = name_match.group(1).strip().strip('"\'')

    # version
    version_match = re.search(r'^version:\s*(.+)$', yaml_block, re.MULTILINE)
    if version_match:
        data['version'] = version_match.group(1).strip().strip('"\'')

    # type
    type_match = re.search(r'^type:\s*(.+)$', yaml_block, re.MULTILINE)
    if type_match:
        data['type'] = type_match.group(1).strip().strip('"\'')

    # description (multiline | or single-line)
    desc_match = re.search(r'^description:\s*\|\s*\n((?:[ \t]+.*\n?)+)', yaml_block, re.MULTILINE)
    if desc_match:
        data['description'] = desc_match.group(1).strip()
    else:
        desc_single = re.search(r'^description:\s*(.+)$', yaml_block, re.MULTILINE)
        if desc_single:
            data['description'] = desc_single.group(1).strip().strip('"\'')

    return data


# ---------------------------------------------------------------------------
# Manifest check
# ---------------------------------------------------------------------------

def check_manifest_entry(root: str, skill_name: str, plane: str) -> tuple[bool, str]:
    """
    Checks if the skill is registered in the target plane's manifest.json.
    Returns (found: bool, message: str).
    """
    manifest_path = os.path.join(root, plane, "manifest.json")
    if not os.path.exists(manifest_path):
        return False, f"manifest.json no encontrado en ./{plane}/."

    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
    except json.JSONDecodeError as e:
        return False, f"manifest.json inválido: {e}"

    # Support both {"skills": [...]} and flat list formats
    skills = manifest.get("skills", manifest if isinstance(manifest, list) else [])
    for entry in skills:
        if isinstance(entry, dict) and entry.get("name") == skill_name:
            return True, f"Encontrado en manifest con status: {entry.get('status', 'unknown')}"

    return False, f"Skill '{skill_name}' no encontrada en manifest.json."


# ---------------------------------------------------------------------------
# Main validator
# ---------------------------------------------------------------------------

def find_project_root(start_path: str) -> str:
    current = os.path.abspath(start_path)
    for _ in range(10):
        if os.path.exists(os.path.join(current, "AGENTS.md")):
            return current
        if os.path.exists(os.path.join(current, "agent", "manifest.json")):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    return os.path.abspath(start_path)


def validate_skill(skill_path: str, plane: str = "catalogo", strict: bool = False) -> bool:
    """
    Validates skill_path against La Forja standards.
    strict=True: manifest entry required (use for pre-deployment validation).
    strict=False: manifest check is advisory only (use during quarantine).
    Returns True if all FATAL checks pass.
    """
    errors   = []   # Fatal — blocks deployment
    warnings = []   # Advisory — logged but don't block

    skill_name = os.path.basename(os.path.normpath(skill_path))

    # ------------------------------------------------------------------
    # 1. SKILL.md existence and frontmatter
    # ------------------------------------------------------------------
    skill_md_path = os.path.join(skill_path, "SKILL.md")
    if not os.path.exists(skill_md_path):
        errors.append("SKILL.md no existe en el directorio de la skill.")
    else:
        with open(skill_md_path, "r", encoding="utf-8") as f:
            content = f.read()

        if not content.startswith("---"):
            errors.append("SKILL.md debe comenzar con frontmatter YAML (---).")
        else:
            try:
                header = parse_yaml_frontmatter(content)

                # name
                if not header.get("name"):
                    errors.append("Frontmatter: campo 'name' ausente.")
                else:
                    if not re.match(r'^[a-z0-9][a-z0-9-]*[a-z0-9]$', header["name"]):
                        errors.append(f"Frontmatter: 'name' no cumple kebab-case: {header['name']}")
                    if header["name"] != skill_name:
                        errors.append(
                            f"Frontmatter: 'name' ({header['name']}) no coincide con el "
                            f"nombre del directorio ({skill_name})."
                        )

                # version
                if not header.get("version"):
                    errors.append("Frontmatter: campo 'version' ausente. Requerido por §3.4.")
                else:
                    if not re.match(r'^\d+\.\d+\.\d+$', header["version"]):
                        warnings.append(
                            f"Frontmatter: 'version' ({header['version']}) no sigue SemVer (X.Y.Z)."
                        )

                # type
                if not header.get("type"):
                    errors.append("Frontmatter: campo 'type' ausente. Requerido por §3.4.")
                else:
                    valid_types = {"backend", "frontend", "integration", "utility"}
                    if header["type"] not in valid_types:
                        warnings.append(
                            f"Frontmatter: 'type' ({header['type']}) no es uno de los valores "
                            f"estándar: {sorted(valid_types)}."
                        )

                # description
                if not header.get("description"):
                    errors.append("Frontmatter: campo 'description' ausente.")
                elif len(header["description"]) < 30:
                    errors.append(
                        f"Frontmatter: 'description' muy corta ({len(header['description'])} chars). "
                        "Mínimo 30 chars para valor de activación adecuado."
                    )

            except ValueError as e:
                errors.append(f"Error parseando frontmatter: {e}")

    # ------------------------------------------------------------------
    # 2. Empty folder warnings (non-fatal)
    # ------------------------------------------------------------------
    for folder in ["scripts", "references", "assets"]:
        folder_path = os.path.join(skill_path, folder)
        if os.path.exists(folder_path) and not os.listdir(folder_path):
            warnings.append(f"Carpeta '{folder}/' existe pero está vacía.")

    # ------------------------------------------------------------------
    # 3. Catálogo-specific checks (only for plane=catalogo)
    # ------------------------------------------------------------------
    if plane == "catalogo":
        readme_path = os.path.join(skill_path, "README.md")
        if not os.path.exists(readme_path):
            errors.append("Catálogo requiere README.md por estándar de entrega §5.7.")

    # ------------------------------------------------------------------
    # 4. Manifest check
    # ------------------------------------------------------------------
    root = find_project_root(skill_path)
    manifest_found, manifest_msg = check_manifest_entry(root, skill_name, plane)
    if not manifest_found:
        if strict:
            errors.append(f"[MANIFEST] {manifest_msg} Registra el componente antes de desplegar.")
        else:
            warnings.append(f"[MANIFEST] {manifest_msg} Registra antes del despliegue final.")

    # ------------------------------------------------------------------
    # Output
    # ------------------------------------------------------------------
    if warnings:
        print("\n[La Forja] Advertencias:")
        for w in warnings:
            print(f"  ⚠ {w}")

    if errors:
        print("\n[La Forja] Validación FALLIDA — errores fatales:", file=sys.stderr)
        for e in errors:
            print(f"  ✗ {e}", file=sys.stderr)
        return False

    print(f"\n[La Forja] Validación EXITOSA — '{skill_name}' cumple estándares La Forja.")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="La Forja — Valida estructura de skill contra AGENTS.md §5.7 + §3.4."
    )
    parser.add_argument("skill_path", help="Ruta al directorio de la skill.")
    parser.add_argument(
        "--plane",
        choices=["agent", "catalogo"],
        default="catalogo",
        help="Plano de destino para validación de manifiesto (default: catalogo)."
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Modo estricto: entrada en manifest.json es requerida (usar en Paso 5 pre-deploy)."
    )
    args = parser.parse_args()

    if not os.path.isdir(args.skill_path):
        print(f"ERROR: '{args.skill_path}' no es un directorio válido.", file=sys.stderr)
        sys.exit(1)

    success = validate_skill(args.skill_path, plane=args.plane, strict=args.strict)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
