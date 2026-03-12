#!/usr/bin/env python3
# journal_report.py — La Forja / A2LT Soluciones
# Generates a pattern analysis report from journal entries since the last report.
# Usage: python journal_report.py [--journal-dir <path>] [--since-entry <filename>]

import os
import sys
import json
import re
import argparse
from datetime import datetime, timezone
from collections import defaultdict


# ---------------------------------------------------------------------------
# Helpers
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


def parse_entry_meta(filename: str) -> dict:
    """Extract timestamp, type, slug from filename convention."""
    match = re.match(r'^(\d{8}-\d{6})_([a-z]+)_(.+)\.md$', filename)
    if not match:
        return {}
    return {
        "timestamp": match.group(1),
        "type":      match.group(2),
        "slug":      match.group(3),
        "filename":  filename,
    }


def read_entry_fields(entry_path: str) -> dict:
    """Extract key fields from a journal entry for report synthesis."""
    fields = {}
    try:
        with open(entry_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract type from comment
        type_match = re.search(r'\[JOURNAL\] type:(\w+)', content)
        if type_match:
            fields["type"] = type_match.group(1)

        # Extract first H1 as title
        h1_match = re.search(r'^# (.+)$', content, re.MULTILINE)
        if h1_match:
            fields["title"] = h1_match.group(1).strip()

        # For problem entries: extract severity and recurrence_risk
        sev_match = re.search(r'\*\*Severidad:\*\*\s*(.+)', content)
        if sev_match:
            fields["severity"] = sev_match.group(1).strip()

        rec_match = re.search(r'\*\*Riesgo de recurrencia:\*\*\s*(.+)', content)
        if rec_match:
            fields["recurrence_risk"] = rec_match.group(1).strip()

        # For forge entries: extract pattern_used
        pat_match = re.search(r'\*\*Patrón de diseño:\*\*\s*(.+)', content)
        if pat_match:
            fields["pattern_used"] = pat_match.group(1).strip()

        comp_match = re.search(r'\*\*Tipo de componente:\*\*\s*(.+)', content)
        if comp_match:
            fields["component_type"] = comp_match.group(1).strip()

        # For field entries: extract rating
        rating_match = re.search(r'\*\*Rating del operador:\*\*\s*(\d+)/5', content)
        if rating_match:
            fields["operator_rating"] = int(rating_match.group(1))

        # For adr: extract status
        status_match = re.search(r'\*\*Estado:\*\*\s*(.+)', content)
        if status_match:
            fields["status"] = status_match.group(1).strip()

    except Exception as e:
        fields["read_error"] = str(e)

    return fields


def load_forge_counter(journal_dir: str) -> dict:
    counter_path = os.path.join(journal_dir, ".forge-counter.json")
    if not os.path.exists(counter_path):
        return {"total_forges": 0, "last_report_at": 0, "last_report_file": None}
    try:
        with open(counter_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"total_forges": 0, "last_report_at": 0, "last_report_file": None}


def save_forge_counter_report(journal_dir: str, report_filename: str) -> None:
    counter_path = os.path.join(journal_dir, ".forge-counter.json")
    counter = load_forge_counter(journal_dir)
    counter["last_report_file"] = report_filename
    with open(counter_path, "w", encoding="utf-8") as f:
        json.dump(counter, f, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Report generator
# ---------------------------------------------------------------------------

def generate_report(journal_dir: str, since_entry: str | None = None) -> str:
    entries_dir = os.path.join(journal_dir, "entries")
    reports_dir = os.path.join(journal_dir, "reports")

    if not os.path.exists(entries_dir):
        print("ERROR: No existe el directorio de entradas.", file=sys.stderr)
        sys.exit(2)

    os.makedirs(reports_dir, exist_ok=True)

    # Get all entries sorted by filename (chronological)
    all_files = sorted([
        f for f in os.listdir(entries_dir)
        if f.endswith(".md") and re.match(r'^\d{8}-\d{6}_', f)
    ])

    if not all_files:
        print("ERROR: No se encontraron entradas en el journal.", file=sys.stderr)
        sys.exit(1)

    # Filter by since_entry if provided
    if since_entry:
        try:
            idx = all_files.index(since_entry)
            target_files = all_files[idx + 1:]
        except ValueError:
            print(
                f"ADVERTENCIA: since-entry '{since_entry}' no encontrado. "
                "Procesando todas las entradas.",
                file=sys.stderr
            )
            target_files = all_files
    else:
        # Use last_report_file from counter as boundary
        counter = load_forge_counter(journal_dir)
        last_report_file = counter.get("last_report_file")
        if last_report_file:
            # Find the entry that triggered the last report
            try:
                # Get entries created after the last report timestamp
                last_ts = last_report_file[:15] if last_report_file else ""
                target_files = [f for f in all_files if f[:15] > last_ts]
            except Exception:
                target_files = all_files
        else:
            target_files = all_files

    if not target_files:
        print("ERROR: No hay entradas nuevas desde el último reporte.", file=sys.stderr)
        sys.exit(1)

    # Parse all entries
    entries_by_type = defaultdict(list)
    for fname in target_files:
        meta = parse_entry_meta(fname)
        if not meta:
            continue
        fields = read_entry_fields(os.path.join(entries_dir, fname))
        entry = {**meta, **fields}
        entries_by_type[meta.get("type", "unknown")].append(entry)

    # Build report
    now = datetime.now(timezone.utc)
    batch_num = load_forge_counter(journal_dir).get("total_forges", 0)
    report_filename = f"{now.strftime('%Y%m%d')}_pattern-report_batch-{batch_num}.md"
    report_path = os.path.join(reports_dir, report_filename)

    forges   = entries_by_type.get("forge",   [])
    problems = entries_by_type.get("problem", [])
    adrs     = entries_by_type.get("adr",     [])
    patterns = entries_by_type.get("pattern", [])
    fields   = entries_by_type.get("field",   [])
    total    = len(target_files)

    lines = []
    lines.append(f"# Reporte de Patrones — Batch {batch_num}")
    lines.append(f"\n**Generado:** {now.strftime('%Y-%m-%d %H:%M UTC')}")
    lines.append(f"**Entradas analizadas:** {total}")
    lines.append(f"**Rango:** {target_files[0][:15]} → {target_files[-1][:15]}")

    # --- Forge summary ---
    lines.append("\n---\n")
    lines.append(f"## Forjas del Batch ({len(forges)})\n")
    if forges:
        pattern_count = defaultdict(int)
        type_count = defaultdict(int)
        for f in forges:
            pattern_count[f.get("pattern_used", "desconocido")] += 1
            type_count[f.get("component_type", "desconocido")] += 1

        lines.append("**Por patrón de diseño:**")
        for pat, count in sorted(pattern_count.items(), key=lambda x: -x[1]):
            lines.append(f"- {pat}: {count}")

        lines.append("\n**Por tipo de componente:**")
        for ctype, count in sorted(type_count.items(), key=lambda x: -x[1]):
            lines.append(f"- {ctype}: {count}")

        lines.append("\n**Componentes forjados:**")
        for f in forges:
            lines.append(f"- `{f.get('slug', '?')}` ({f.get('timestamp', '?')})")
    else:
        lines.append("_No hay forjas en este batch._")

    # --- Problem analysis ---
    lines.append("\n---\n")
    lines.append(f"## Análisis de Problemas ({len(problems)})\n")
    if problems:
        sev_count  = defaultdict(int)
        rec_count  = defaultdict(int)
        for p in problems:
            sev_count[p.get("severity", "?")]         += 1
            rec_count[p.get("recurrence_risk", "?")] += 1

        lines.append("**Por severidad:**")
        for sev in ["critical", "high", "medium", "low"]:
            if sev_count[sev]:
                lines.append(f"- {sev}: {sev_count[sev]}")

        lines.append("\n**Por riesgo de recurrencia:**")
        for risk in ["high", "medium", "low"]:
            if rec_count[risk]:
                lines.append(f"- {risk}: {rec_count[risk]}")

        # Flag high-recurrence problems
        high_recurrence = [p for p in problems if p.get("recurrence_risk") == "high"]
        if high_recurrence:
            lines.append("\n**⚠ Problemas con alto riesgo de recurrencia — requieren mitigación:**")
            for p in high_recurrence:
                lines.append(f"- {p.get('title', p.get('slug', '?'))} → `{p['filename']}`")
    else:
        lines.append("_No se registraron problemas en este batch._")

    # --- ADR changes ---
    lines.append("\n---\n")
    lines.append(f"## Decisiones Arquitectónicas ({len(adrs)})\n")
    if adrs:
        for a in adrs:
            status = a.get("status", "?")
            lines.append(f"- [{status.upper()}] {a.get('title', a.get('slug', '?'))} → `{a['filename']}`")
    else:
        lines.append("_No se registraron ADRs en este batch._")

    # --- Pattern registry ---
    lines.append("\n---\n")
    lines.append(f"## Patrones Detectados ({len(patterns)})\n")
    if patterns:
        for p in patterns:
            lines.append(f"- {p.get('title', p.get('slug', '?'))} → `{p['filename']}`")
    else:
        lines.append("_No se registraron patrones nuevos en este batch._")

    # --- Field feedback ---
    lines.append("\n---\n")
    lines.append(f"## Field Feedback ({len(fields)})\n")
    if fields:
        ratings = [f.get("operator_rating") for f in fields if f.get("operator_rating")]
        if ratings:
            avg_rating = sum(ratings) / len(ratings)
            lines.append(f"**Rating promedio:** {avg_rating:.1f}/5\n")
        for f in fields:
            rating_str = f"{f.get('operator_rating', '?')}/5"
            lines.append(
                f"- `{f.get('slug', '?')}` — rating: {rating_str} → `{f['filename']}`"
            )
    else:
        lines.append("_No hay field feedback en este batch._")

    # --- Recommendations ---
    lines.append("\n---\n")
    lines.append("## Recomendaciones para el Catálogo\n")

    recommendations = []

    if high_recurrence if problems else []:
        recommendations.append(
            "Revisar los componentes afectados por problemas de alto riesgo de recurrencia "
            "y actualizar sus SKILLs o READMEs con las mitigaciones documentadas."
        )

    low_rated_fields = [f for f in fields if f.get("operator_rating", 5) <= 2]
    if low_rated_fields:
        names = [f.get("slug", "?") for f in low_rated_fields]
        recommendations.append(
            f"Los siguientes componentes recibieron rating ≤ 2/5 en campo — "
            f"priorizar mejoras: {', '.join(names)}."
        )

    if len(patterns) > 0:
        recommendations.append(
            f"Se detectaron {len(patterns)} patrón(es) nuevo(s). "
            "Considerar si alguno debe materializarse como skill del Core."
        )

    if not recommendations:
        recommendations.append(
            "No se identificaron acciones críticas. El ecosistema opera dentro de parámetros normales."
        )

    for i, rec in enumerate(recommendations, 1):
        lines.append(f"{i}. {rec}")

    lines.append(f"\n---\n*Reporte generado automáticamente por journal_report.py — La Forja v2.3*")

    # Write report
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"[Journal] Reporte generado: {report_path}")
    save_forge_counter_report(journal_dir, report_filename)
    return report_path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="La Forja Journal — Genera un reporte de patrones desde las entradas del journal."
    )
    parser.add_argument(
        "--journal-dir",
        default=None,
        help="Ruta al directorio del journal. Por defecto: ./agent/memory/journal/ desde raíz."
    )
    parser.add_argument(
        "--since-entry",
        default=None,
        help="Filename de la entrada a partir de la cual generar el reporte (exclusivo)."
    )
    args = parser.parse_args()

    if args.journal_dir:
        journal_dir = os.path.abspath(args.journal_dir)
    else:
        root = find_project_root(os.getcwd())
        journal_dir = os.path.join(root, "agent", "memory", "journal")

    if not os.path.exists(journal_dir):
        print(f"ERROR: Directorio del journal no encontrado: {journal_dir}", file=sys.stderr)
        sys.exit(2)

    generate_report(journal_dir, since_entry=args.since_entry)
    sys.exit(0)


if __name__ == "__main__":
    main()
