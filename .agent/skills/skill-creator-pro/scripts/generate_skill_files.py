#!/usr/bin/env python3
# generate_skill_files.py — La Forja / A2LT Soluciones
# Generates or updates Antigravity skill files from a JSON Blueprint spec.
# Usage: python generate_skill_files.py --spec '<json>' --output ./agent/skills/
#        python generate_skill_files.py --file blueprint.json --output ./catalogo/skills/ --force

import os
import json
import argparse
import sys
import re
import stat
import shutil


def find_project_root(start_path: str) -> str:
    """Walk up from start_path until we find AGENTS.md or agent/manifest.json."""
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


def clean_llm_json(raw_text: str) -> str:
    """Cleans common LLM JSON artifacts (markdown fences, trailing commas)."""
    text = re.sub(r'^```json\s*', '', raw_text.strip())
    text = re.sub(r'```.*$', '', text, flags=re.DOTALL)
    text = re.sub(r',\s*([\]}])', r'\1', text)
    return text.strip()


def check_manifest(root: str, plane: str) -> bool:
    """Warns if the target plane manifest is missing. Does not block execution."""
    manifest_path = os.path.join(root, plane, "manifest.json")
    if not os.path.exists(manifest_path):
        print(
            f"[ADVERTENCIA] manifest.json no encontrado en ./{plane}/. "
            "Crea el manifiesto antes del despliegue final.",
            file=sys.stderr
        )
        return False
    return True


def generate_skill(spec: dict, output_dir: str, force: bool = False) -> str:
    """
    Materializes the skill directory from the Blueprint spec.
    Returns the full path to the created skill directory.
    """
    name = spec.get("name")
    if not name:
        print("ERROR: 'name' es requerido en el Blueprint.", file=sys.stderr)
        sys.exit(1)

    if not re.match(r'^[a-z0-9][a-z0-9-]*[a-z0-9]$', name):
        print(
            f"ERROR: El nombre '{name}' no cumple kebab-case. "
            "Solo minúsculas, números y guiones. No puede empezar ni terminar con guión.",
            file=sys.stderr
        )
        sys.exit(1)

    skill_path = os.path.join(output_dir, name)

    if os.path.exists(skill_path) and not force:
        print(
            f"ERROR: El directorio '{skill_path}' ya existe. "
            "Usa --force para sobrescribir. OPERACIÓN ABORTADA para prevenir pérdida de datos.",
            file=sys.stderr
        )
        sys.exit(1)

    os.makedirs(skill_path, exist_ok=True)

    structure = spec.get("structure", {})
    content  = spec.get("content", {})

    # Validate content completeness before touching the filesystem
    missing_content = [f for f in structure if f not in content]
    if missing_content:
        print(
            f"ERROR: Los siguientes archivos están en 'structure' pero faltan en 'content': "
            f"{missing_content}",
            file=sys.stderr
        )
        sys.exit(1)

    for file_path, _file_type in structure.items():
        full_path = os.path.join(skill_path, file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        # Backup before overwrite
        if os.path.exists(full_path) and force:
            backup_path = full_path + ".bak"
            shutil.copy2(full_path, backup_path)
            print(f"  [backup] {file_path} → {file_path}.bak")

        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content[file_path])

        print(f"  [ok] {file_path}")

        # Auto-chmod for executable scripts
        if "scripts/" in file_path or file_path.endswith((".sh", ".py")):
            st = os.stat(full_path)
            os.chmod(full_path, st.st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
            print(f"       → chmod +x aplicado")

    return skill_path


def main():
    parser = argparse.ArgumentParser(
        description="La Forja — Materializa archivos de skill desde un Blueprint JSON."
    )
    parser.add_argument("--spec", help="JSON string con el Blueprint de la skill.")
    parser.add_argument("--file", help="Ruta a un archivo JSON con el Blueprint.")
    parser.add_argument(
        "--output",
        default=".",
        help="Directorio destino (ej: ./agent/skills/ o ./catalogo/skills/)."
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Sobrescribe archivos existentes y crea backups .bak automáticamente."
    )
    parser.add_argument(
        "--plane",
        choices=["agent", "catalogo"],
        default="catalogo",
        help="Plano de destino para verificación de manifiesto (default: catalogo)."
    )
    args = parser.parse_args()

    # Read spec
    spec_text = ""
    if args.spec:
        spec_text = args.spec
    elif args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                spec_text = f.read()
        except FileNotFoundError:
            print(f"ERROR: Archivo no encontrado: {args.file}", file=sys.stderr)
            sys.exit(1)
    else:
        print("ERROR: Debes proveer --spec o --file.", file=sys.stderr)
        parser.print_help()
        sys.exit(1)

    # Parse JSON
    try:
        clean_text = clean_llm_json(spec_text)
        spec_data  = json.loads(clean_text)
    except json.JSONDecodeError as e:
        print(f"ERROR al parsear el Blueprint JSON: {e}", file=sys.stderr)
        print("Verifica que el JSON sea válido y no tenga caracteres sin escapar.", file=sys.stderr)
        sys.exit(1)

    # Manifest check (non-blocking warning)
    root = find_project_root(os.getcwd())
    check_manifest(root, args.plane)

    # Materialize
    skill_name = spec_data.get("name", "?")
    print(f"\n[La Forja] Materializando skill '{skill_name}'...")
    print(f"  Destino: {os.path.abspath(args.output)}\n")

    skill_path = generate_skill(spec_data, args.output, force=args.force)

    print(f"\n[La Forja] Skill materializada en: {skill_path}")
    print("  Siguiente: ejecuta validate_skill_structure.py para validación pre-despliegue.")
    sys.exit(0)


if __name__ == "__main__":
    main()
