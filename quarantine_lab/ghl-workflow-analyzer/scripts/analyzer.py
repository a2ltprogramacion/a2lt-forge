import os
import sys
import json
from glob import glob
from pathlib import Path
from collections import defaultdict

# ─────────────────────────────────────────────────────────────────────────────
# GHL WORKFLOW ANALYZER v2 — Produces:
#   1. output/{location_id}/reports/wf_{id}.md  → individual per-workflow report
#   2. output/{location_id}/audit_global.md     → cross-workflow global analysis
#   3. All raw JSONs already placed prior to this by the sniffer
# Schema reference: GHL internal API (backend.leadconnectorhq.com)
#   - triggers: data['triggers']  (array)
#   - steps:    data['workflow']['workflowData']['templates']  (array)
# ─────────────────────────────────────────────────────────────────────────────

ACTION_LABELS = {
    "add_contact_tag":             "Añadir Etiqueta",
    "remove_contact_tag":          "Eliminar Etiqueta",
    "if_else":                     "Condición If/Else",
    "assign_user":                 "Asignar Asesor",
    "add_to_workflow":             "Enviar a Workflow",
    "goto":                        "Salto a Nodo",
    "internal_create_opportunity": "Crear Oportunidad",
    "internal-add-opportunity-owner": "Asignar Dueño de Oportunidad",
    "internal_notification":       "Notificación Interna (Email)",
    "wait":                        "Espera Temporizada",
    "send_email":                  "Enviar Email",
    "send_sms":                    "Enviar SMS",
}

def label(action_type):
    return ACTION_LABELS.get(action_type, action_type)


def analyze_workflows(location_id):
    # ── Input: JSONs in quarantine_lab (written by sniffer) ──
    spy_path   = Path(f".agent/quarantine_lab/ghl-spy/{location_id}")
    # ── Output: clean folder requested by Operator Argenis ──
    out_root   = Path(f"output/{location_id}")
    reports_dir = out_root / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    json_files = sorted(spy_path.glob("dna_*.json"))

    if not json_files:
        print(f"[!] No DNA files found in {spy_path}. Run dna-sniffer first.")
        sys.exit(1)

    print(f"[*] Found {len(json_files)} workflow DNA files. Processing…")

    # ── Registry for inter-workflow cross-analysis ──
    trigger_registry    = defaultdict(list)   # trigger_type → [wf_name, ...]
    tag_add_registry    = defaultdict(list)   # tag → [wf_name, ...]
    tag_remove_registry = defaultdict(list)   # tag → [wf_name, ...]
    handoff_registry    = defaultdict(list)   # target_wf_id → [source_wf_name, ...]
    goto_registry       = defaultdict(list)   # target_node_id → [wf_name, ...]
    workflow_index      = {}                  # wf_id → wf_name

    per_wf_summaries = []

    for file_path in json_files:
        try:
            data = json.loads(file_path.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"[!] Cannot parse {file_path.name}: {e}")
            continue

        # ── Normalización de Estructura ──
        # Algunos endpoints devuelven {"workflow": {...}, "triggers": [...]}, otros el objeto directo.
        if "workflow" in data:
            wf = data.get("workflow", {})
            triggers = data.get("triggers", [])
        else:
            wf = data
            triggers = data.get("triggers", []) # Por si vienen en el mismo nivel

        wf_id    = wf.get("_id", wf.get("id", "unknown"))
        wf_name  = wf.get("name", "Sin Nombre")
        wf_status = wf.get("status", "unknown")
        steps    = wf.get("workflowData", {}).get("templates", [])
        
        # Si triggers no se encontró arriba, buscarlo en la raíz o en workflowData
        if not triggers:
             triggers = wf.get("triggers", []) # A veces vienen dentro del objeto principal

        workflow_index[wf_id] = wf_name

        # ── Register triggers ──
        for t in triggers:
            t_type = t.get("type", "unknown")
            trigger_registry[t_type].append(wf_name)

        # ── Classify steps ──
        tags_added   = []
        tags_removed = []
        conditions   = []
        handoffs     = []
        gotos        = []
        dead_ends    = []
        action_log   = []

        for step in steps:
            s_type  = step.get("type", "")
            s_name  = step.get("name", "")
            attrs   = step.get("attributes", {})
            node_type = step.get("nodeType", "")

            action_log.append(f"- `{label(s_type)}` — **{s_name}**")

            if s_type == "add_contact_tag":
                raw_tags = attrs.get("tags", [])
                custom   = attrs.get("customTags", "")
                for t in raw_tags:
                    tags_added.append(t)
                    tag_add_registry[t].append(wf_name)
                if custom:
                    tags_added.append(f"(dyn) {custom}")

            elif s_type == "remove_contact_tag":
                raw_tags = attrs.get("tags", [])
                for t in raw_tags:
                    tags_removed.append(t)
                    tag_remove_registry[t].append(wf_name)

            elif s_type == "if_else":
                cond_name = attrs.get("conditionName", s_name)
                conditions.append(cond_name)
                # A branch-yes or branch-no with no 'next' is a dead end
                if node_type in ("branch-yes", "branch-no") and not step.get("next"):
                    dead_ends.append(f"{cond_name} → {s_name} (sin salida definida)")

            elif s_type == "add_to_workflow":
                target_wf = attrs.get("workflow_id", "")
                if target_wf:
                    handoffs.append(target_wf)
                    handoff_registry[target_wf].append(wf_name)

            elif s_type == "goto":
                target_node = attrs.get("targetNodeId", "")
                if target_node:
                    gotos.append(target_node)
                    goto_registry[target_node].append(wf_name)

        # ── Build individual workflow report ──
        wf_report = reports_dir / f"wf_{wf_id}.md"
        lines = [
            f"# Informe de Workflow: {wf_name}",
            f"",
            f"| Campo     | Valor |",
            f"|-----------|-------|",
            f"| **ID**    | `{wf_id}` |",
            f"| **Estado**| `{wf_status}` |",
            f"| **Pasos** | {len(steps)} |",
            f"",
            f"## Triggers de Activación",
        ]
        for t in triggers:
            lines.append(f"- `{t.get('type', 'N/A')}` — {t.get('name', '')} (activo: {t.get('active', '?')})")

        lines += ["", "## Mapa de Acciones"]
        lines += action_log if action_log else ["*(Sin acciones registradas)*"]

        lines += ["", "## Etiquetas Añadidas"]
        lines += [f"- `{t}`" for t in tags_added] or ["*(ninguna)*"]

        lines += ["", "## Etiquetas Eliminadas"]
        lines += [f"- `{t}`" for t in tags_removed] or ["*(ninguna)*"]

        lines += ["", "## Condiciones If/Else"]
        lines += [f"- {c}" for c in conditions] or ["*(ninguna)*"]

        lines += ["", "## Handoffs a Otros Workflows"]
        lines += [f"- Workflow ID: `{h}`" for h in handoffs] or ["*(ninguno)*"]

        lines += ["", "## ⚠️ Dead Ends Detectados"]
        lines += [f"- {d}" for d in dead_ends] or ["*(no detectados en esta pasada)*"]

        wf_report.write_text("\n".join(lines), encoding="utf-8")
        per_wf_summaries.append((wf_id, wf_name, wf_status, len(triggers), len(steps), len(dead_ends), len(handoffs)))
        print(f"  [✓] Reporte individual: {wf_report}")

    # ── Build global cross-analysis report ──
    global_report = out_root / "audit_global.md"
    g = []
    g.append("# Auditoría Global de Workflows — Análisis de Interrelaciones")
    g.append(f"\n**Location ID:** `{location_id}`  \n**Workflows Analizados:** {len(per_wf_summaries)}\n")

    g.append("## Tabla de Inventario")
    g.append("| # | Nombre | Estado | Triggers | Pasos | Dead Ends | Handoffs |")
    g.append("|---|--------|--------|----------|-------|-----------|---------|")
    for i, (wid, wname, wstatus, ntrig, nsteps, nde, nhoff) in enumerate(per_wf_summaries, 1):
        de_flag = f"⚠️ {nde}" if nde else "✅ 0"
        g.append(f"| {i} | {wname} | `{wstatus}` | {ntrig} | {nsteps} | {de_flag} | {nhoff} |")

    g.append("\n## Vector 1 — Race Conditions (Triggers Compartidos)")
    found_v1 = False
    for t_type, names in trigger_registry.items():
        if len(names) > 1:
            g.append(f"- **⚠️ `{t_type}`** activado por: {', '.join(f'`{n}`' for n in names)}")
            found_v1 = True
    if not found_v1:
        g.append("- ✅ No se detectaron triggers compartidos entre workflows.")

    g.append("\n## Vector 2 — Cycle Detection (Etiquetas que pueden crear bucles)")
    cycles_found = False
    for tag, adders in tag_add_registry.items():
        if tag in tag_remove_registry:
            removers = tag_remove_registry[tag]
            g.append(f"- **⚠️ Tag `{tag}`:** Añadida por {adders}, Eliminada por {removers} → Riesgo de ciclo si ambas condiciones se activan secuencialmente.")
            cycles_found = True
    if not cycles_found:
        g.append("- ✅ No se detectaron ciclos de tags evidentes.")

    g.append("\n## Vector 3 — Handoffs (Workflows que inyectan contactos a otros Workflows)")
    if handoff_registry:
        for target_id, sources in handoff_registry.items():
            target_name = workflow_index.get(target_id, f"ID desconocido: `{target_id}`")
            g.append(f"- **`{target_name}`** recibe contactos desde: {', '.join(f'`{s}`' for s in sources)}")
    else:
        g.append("- ✅ No se detectaron handoffs entre workflows.")

    g.append("\n## Vector 4 — Dead Ends Globales")
    total_dead_ends = sum(nde for _, _, _, _, _, nde, _ in per_wf_summaries)
    if total_dead_ends:
        g.append(f"- **⚠️ {total_dead_ends} dead end(s) detectados** a través de los workflows. Ver reportes individuales para detalle.")
    else:
        g.append("- ✅ No se detectaron dead ends evidentes.")

    g.append("\n## Vector 5 — Tags con Escritura Redundante")
    redundant_tags = False
    for tag, writers in tag_add_registry.items():
        if len(writers) > 1:
            g.append(f"- **⚠️ Tag `{tag}`** es añadida por múltiples workflows: {', '.join(f'`{w}`' for w in writers)}")
            redundant_tags = True
    if not redundant_tags:
        g.append("- ✅ No se detectaron tags con escritura redundante.")

    global_report.write_text("\n".join(g), encoding="utf-8")
    print(f"\n[✓] Reporte global: {global_report}")
    print(f"[✓] Reportes individuales en: {reports_dir}/")
    sys.exit(0)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        analyze_workflows(sys.argv[1])
    else:
        print("Uso: python scripts/analyzer.py <location_id>")
        sys.exit(1)
