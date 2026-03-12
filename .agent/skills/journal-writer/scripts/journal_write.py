#!/usr/bin/env python3
# journal_write.py — La Forja / A2LT Soluciones (v2.0.0)
# Escritor unificado de memoria institucional.
# Tipos forge/problem → generan AUDIT-SUCCESS/AUDIT-FAILURE en rag/sources/sessions/
# Tipo adr → genera ADR en rag/sources/adrs/
# Tipos pattern/field → generan entradas en .agent/memory/journal/entries/
#
# Usage (.venv):
#   .venv/Scripts/python.exe .agent/skills/journal-writer/scripts/journal_write.py \
#     --type forge --payload '{"component_name": "rag-query", ...}'

import os
import sys
import json
import re
import argparse
from datetime import datetime, timezone


# ─── Campos requeridos por tipo ──────────────────────────────────────────────

REQUIRED_FIELDS = {
    "forge": [
        "component_name", "component_type", "target_plane", "version",
        "pattern_used", "duration_minutes", "external_audit",
        "rag_query_result", "notes"
    ],
    "problem": [
        "title", "context", "root_cause", "solution",
        "mitigation", "affected_components", "severity", "recurrence_risk"
    ],
    "adr": [
        "title", "context", "decision", "alternatives_considered",
        "reasoning", "consequences", "status"
    ],
    "pattern": [
        "title", "description", "evidence",
        "recommendation", "applies_to", "first_seen"
    ],
    "field": [
        "skill_or_agent", "project_context", "usage_description",
        "outcome", "client_friction", "suggested_improvement", "operator_rating"
    ],
}

VALID_TYPES = set(REQUIRED_FIELDS.keys())

# Tipos que se redirigen a AUDIT en rag/sources/sessions/
AUDIT_TYPES = {"forge", "problem"}
# Tipo que se redirige a rag/sources/adrs/
ADR_TYPE = "adr"
# Tipos que van al journal propio
JOURNAL_TYPES = {"pattern", "field"}


# ─── Helpers ─────────────────────────────────────────────────────────────────

def find_project_root(start: str) -> str:
    """Busca la raíz del proyecto subiendo directorios hasta encontrar GEMINI.md."""
    current = os.path.abspath(start)
    for _ in range(10):
        if os.path.exists(os.path.join(current, "GEMINI.md")):
            return current
        if os.path.exists(os.path.join(current, "AGENTS.md")):
            return current
        if os.path.exists(os.path.join(current, ".agent", "manifest.json")):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    return os.path.abspath(start)


def slugify(text: str) -> str:
    """Convierte texto a slug seguro para nombres de archivo."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text[:50].strip('-')


def render_template(template_path: str, payload: dict, timestamp: str) -> str:
    """Reemplaza placeholders {{field}} en template con valores del payload."""
    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()

    payload["timestamp"] = timestamp

    def replace_field(match):
        key = match.group(1).strip()
        value = payload.get(key)
        if value is None:
            return f"{{{{MISSING:{key}}}}}"
        if isinstance(value, list):
            return "\n".join(f"- {item}" for item in value)
        return str(value)

    return re.sub(r'\{\{(\w+)\}\}', replace_field, content)


def load_forge_counter(journal_dir: str) -> dict:
    """Carga el contador de forjas."""
    counter_path = os.path.join(journal_dir, ".forge-counter.json")
    default = {
        "total_forges": 0,
        "report_threshold": 10,
        "last_report_at": 0,
        "last_report_file": None
    }
    if not os.path.exists(counter_path):
        return default
    try:
        with open(counter_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for k, v in default.items():
            data.setdefault(k, v)
        return data
    except Exception:
        return default


def save_forge_counter(journal_dir: str, counter: dict) -> None:
    """Guarda el contador de forjas."""
    counter_path = os.path.join(journal_dir, ".forge-counter.json")
    with open(counter_path, "w", encoding="utf-8") as f:
        json.dump(counter, f, indent=2, ensure_ascii=False)


def check_duplicate(entries_dir: str, entry_type: str, slug: str) -> str | None:
    """Busca duplicados por tipo+slug en el directorio de destino."""
    if not os.path.exists(entries_dir):
        return None
    for fname in os.listdir(entries_dir):
        # Para AUDITs, buscar por nombre de componente
        if slug in fname.lower() and fname.endswith(".md"):
            return fname
    return None


def next_adr_number(adrs_dir: str) -> int:
    """Calcula el siguiente número de ADR disponible."""
    if not os.path.exists(adrs_dir):
        return 1
    max_num = 0
    for fname in os.listdir(adrs_dir):
        match = re.match(r'ADR-(\d+)', fname)
        if match:
            max_num = max(max_num, int(match.group(1)))
    return max_num + 1


# ─── Routing por tipo ────────────────────────────────────────────────────────

def resolve_output_path(
    entry_type: str,
    payload: dict,
    project_root: str,
    timestamp_str: str
) -> tuple[str, str]:
    """
    Determina el directorio y nombre de archivo según el tipo de entrada.
    Retorna (output_dir, filename).
    """
    date_str = timestamp_str[:8]  # YYYYMMDD

    if entry_type == "forge":
        # → AUDIT-SUCCESS en rag/sources/sessions/
        component = payload.get("component_name", "unknown")
        output_dir = os.path.join(project_root, "rag", "sources", "sessions")
        filename = f"AUDIT-{component}-{date_str}.md"

    elif entry_type == "problem":
        # → AUDIT-FAILURE en rag/sources/sessions/
        component = payload.get("affected_components", ["unknown"])
        if isinstance(component, list):
            component = component[0] if component else "unknown"
        slug = slugify(component)
        output_dir = os.path.join(project_root, "rag", "sources", "sessions")
        filename = f"AUDIT-FAILURE-{slug}-{date_str}.md"

    elif entry_type == "adr":
        # → ADR en rag/sources/adrs/
        output_dir = os.path.join(project_root, "rag", "sources", "adrs")
        adr_num = next_adr_number(output_dir)
        title_slug = slugify(payload.get("title", "decision"))
        filename = f"ADR-{adr_num:03d}-{title_slug}-{date_str}.md"

    else:
        # pattern, field → journal/entries/
        slug_source = {
            "pattern": payload.get("title", "unknown"),
            "field": f"{payload.get('skill_or_agent', 'unknown')}-{payload.get('project_context', '')}",
        }
        slug = slugify(slug_source.get(entry_type, "entry"))
        output_dir = os.path.join(project_root, ".agent", "memory", "journal", "entries")
        filename = f"{timestamp_str}_{entry_type}_{slug}.md"

    return output_dir, filename


# ─── Escritor principal ──────────────────────────────────────────────────────

def write_entry(
    entry_type: str,
    payload: dict,
    project_root: str,
    force: bool = False
) -> tuple[str, bool]:
    """
    Escribe la entrada del journal. Retorna (entry_path, report_triggered).
    Raises SystemExit on validation failure.
    """
    if entry_type not in VALID_TYPES:
        print(
            f"ERROR: Tipo de entrada inválido: '{entry_type}'. "
            f"Válidos: {sorted(VALID_TYPES)}",
            file=sys.stderr
        )
        sys.exit(1)

    # Validar campos requeridos
    required = REQUIRED_FIELDS[entry_type]
    missing = [f for f in required if f not in payload or payload[f] == ""]
    if missing:
        print(
            f"ERROR: Campos requeridos faltantes para tipo '{entry_type}': {missing}",
            file=sys.stderr
        )
        sys.exit(2)

    # Timestamp
    timestamp_str = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")

    # Resolver ruta de salida
    output_dir, filename = resolve_output_path(
        entry_type, payload, project_root, timestamp_str
    )
    os.makedirs(output_dir, exist_ok=True)
    entry_path = os.path.join(output_dir, filename)

    # Verificar duplicados (salvo --force)
    existing = check_duplicate(output_dir, entry_type, slugify(
        payload.get("component_name", payload.get("title", ""))
    ))
    if existing and not force:
        print(
            f"ADVERTENCIA: Ya existe una entrada similar: {existing}\n"
            "       Usa --force para crear una entrada adicional.",
            file=sys.stderr
        )
        sys.exit(4)

    # Buscar y renderizar template
    skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_path = os.path.join(skill_dir, "assets", "templates", f"{entry_type}.md")

    if not os.path.exists(template_path):
        print(f"ERROR: Template no encontrado: {template_path}", file=sys.stderr)
        sys.exit(3)

    rendered = render_template(template_path, payload, timestamp_str)

    # Verificar placeholders sin rellenar
    unfilled = re.findall(r'\{\{MISSING:(\w+)\}\}', rendered)
    if unfilled:
        print(
            f"ADVERTENCIA: Campos marcados como MISSING: {unfilled}",
            file=sys.stderr
        )

    # Escribir entrada
    with open(entry_path, "w", encoding="utf-8") as f:
        f.write(rendered)

    # Indicar destino para claridad
    dest_label = {
        "forge": "AUDIT-SUCCESS → rag/sources/sessions/",
        "problem": "AUDIT-FAILURE → rag/sources/sessions/",
        "adr": "ADR → rag/sources/adrs/",
        "pattern": "PATTERN → .agent/memory/journal/entries/",
        "field": "FIELD → .agent/memory/journal/entries/",
    }
    print(f"[Journal] [{dest_label[entry_type]}] {filename}")

    # Actualizar forge counter si es tipo forge
    report_triggered = False
    journal_dir = os.path.join(project_root, ".agent", "memory", "journal")
    if entry_type == "forge":
        os.makedirs(journal_dir, exist_ok=True)
        counter = load_forge_counter(journal_dir)
        counter["total_forges"] += 1

        forges_since_report = counter["total_forges"] - counter["last_report_at"]
        if forges_since_report >= counter["report_threshold"]:
            report_triggered = True
            print(
                f"[Journal] Umbral de reporte alcanzado "
                f"({forges_since_report} forjas desde el último reporte). "
                f"Invoca journal_report.py para generar el análisis."
            )
            counter["last_report_at"] = counter["total_forges"]

        save_forge_counter(journal_dir, counter)

    return entry_path, report_triggered


# ─── CLI ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="La Forja Journal v2.0 — Escritor unificado de memoria institucional."
    )
    parser.add_argument(
        "--type",
        required=True,
        choices=list(VALID_TYPES),
        help="Tipo de entrada: forge | problem | adr | pattern | field"
    )
    parser.add_argument(
        "--payload",
        required=True,
        help="JSON string con los campos de la entrada."
    )
    parser.add_argument(
        "--project-root",
        default=None,
        help="Ruta raíz del proyecto. Por defecto: auto-detecta desde CWD."
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Permite crear entrada aunque exista una con slug similar."
    )
    parser.add_argument(
        "--help-json",
        action="store_true",
        help="Output help en formato JSON."
    )
    args = parser.parse_args()

    if args.help_json:
        print(json.dumps({
            "description": "Escritor unificado de memoria institucional de La Forja",
            "version": "2.0.0",
            "routing": {
                "forge": "→ AUDIT-SUCCESS en rag/sources/sessions/",
                "problem": "→ AUDIT-FAILURE en rag/sources/sessions/",
                "adr": "→ ADR en rag/sources/adrs/",
                "pattern": "→ .agent/memory/journal/entries/",
                "field": "→ .agent/memory/journal/entries/"
            },
            "types": list(VALID_TYPES),
            "required_fields": REQUIRED_FIELDS,
            "exit_codes": {
                "0": "Entrada escrita exitosamente",
                "1": "Tipo inválido",
                "2": "Campos requeridos faltantes",
                "3": "Template o directorio no encontrado",
                "4": "Duplicado detectado (usa --force)"
            }
        }, indent=2, ensure_ascii=False))
        return

    # Resolver raíz del proyecto
    project_root = args.project_root or find_project_root(os.getcwd())

    # Parsear payload
    try:
        payload = json.loads(args.payload)
    except json.JSONDecodeError as e:
        print(f"ERROR: JSON inválido en --payload: {e}", file=sys.stderr)
        sys.exit(1)

    entry_path, report_triggered = write_entry(
        entry_type=args.type,
        payload=payload,
        project_root=project_root,
        force=args.force
    )

    # Output machine-readable
    result = {
        "entry_path": entry_path,
        "report_triggered": report_triggered
    }
    print(json.dumps(result))
    sys.exit(0)


if __name__ == "__main__":
    main()
