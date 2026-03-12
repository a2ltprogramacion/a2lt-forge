---
name: journal-writer
version: 2.0.0
type: utility
subtype: skill
tier: all
description: |
  Core skill that writes, validates, and manages La Forja's institutional memory journal.
  Activate when closing a forge task (Paso 5), when a problem is resolved, when an
  architectural decision is made, when a usage pattern is detected, or when field feedback
  from a client project is available.
  Trigger phrases: "registra en el journal", "guarda esta decisión", "escribe la entrada",
  "log this", "journal entry", "forge shutdown journal".
  Do NOT activate for general note-taking outside La Forja context. Do NOT activate
  for temporary quarantine notes — those live in workflow-state.json, not here.

triggers:
  primary: ["journal", "registra", "guarda decisión", "log this", "forge shutdown"]
  secondary: ["entrada de journal", "memoria institucional", "ADR", "patrón detectado"]
  context: ["forge shutdown", "paso 5", "problema resuelto", "field feedback"]

inputs:
  - name: entry_type
    type: string
    required: true
    description: "One of: forge | problem | adr | pattern | field"
  - name: payload
    type: object
    required: true
    description: "Entry data matching the schema for the given entry_type"
  - name: requires_confirmation
    type: bool
    required: false
    description: "If true, present entry to operator before persisting. Default: false for forge/problem, true for adr/pattern/field"

outputs:
  - name: entry_path
    type: string
    description: Full path to the written journal entry
  - name: report_generated
    type: bool
    description: Whether a pattern report was triggered by this entry

dependencies:
  - name: rag-indexer
    version: ">=1.0.0"
    optional: true

framework_version: ">=2.3.0"
---

# Journal Writer — Memoria Institucional de La Forja

This skill is the write interface to La Forja's institutional memory.
It produces structured Markdown journal entries that are human-readable,
RAG-indexable, and evolvable over time.

Read this document completely before writing any entry.

---

## 0. Principios del Journal

- **Entradas son permanentes.** Never delete or overwrite entries — append corrections
  as new entries of the same type referencing the original by filename.
- **Un problema = una entrada.** Do not bundle multiple unrelated issues.
- **Confirmación para juicio.** Entries requiring architectural judgment (adr, pattern, field)
  are presented to the operator before persisting. Factual entries (forge, problem) are
  written automatically.
- **RAG primero.** Before writing an `adr` or `pattern` entry, invoke `rag-query` to check
  if a similar decision or pattern already exists. If it does, reference it — don't duplicate.

---

## 1. Estructura del Sistema de Journal

```
.agent/memory/journal/
├── .forge-counter.json     ← contador de forjas + umbral de reporte
├── entries/                ← entradas de tipos pattern y field
└── reports/                ← reportes auto-generados

rag/sources/sessions/       ← destino de forge (AUDIT-SUCCESS) y problem (AUDIT-FAILURE)
rag/sources/adrs/           ← destino de tipo adr
```

**Filename convention:**
```
[YYYYMMDD-HHMMSS]_[type]_[slug].md
```
Examples:
- `20250311-143022_forge_rag-query-v1.md`
- `20250311-150845_problem_chromadb-path-conflict.md`
- `20250311-162300_adr_embedding-model-selection.md`

---

## 2. Tipos de Entrada y Sus Plantillas

### 2.1 Tipo: `forge` → AUDIT-SUCCESS
**Cuándo:** Al completar Paso 7 de cualquier forja exitosa.
**Destino:** `rag/sources/sessions/AUDIT-[component]-[date].md`
**Confirmación:** None — se escribe directamente.

Load template: `assets/templates/forge.md`

Required fields:
- `component_name` — exact name from manifest
- `component_type` — skill | agent | workflow
- `target_plane` — agent | catalogo
- `version` — SemVer from frontmatter
- `pattern_used` — High Freedom | Deterministic | Deep Domain | Template | Composite
- `duration_minutes` — approximate forge time
- `external_audit` — true | false
- `rag_query_result` — what rag-query found before forging (or "no results")
- `notes` — any relevant operational observations

---

### 2.2 Tipo: `problem` → AUDIT-FAILURE
**Cuándo:** Cuando un `[ALTO]` se dispara, un script falla, o el operador reporta un problema.
**Destino:** `rag/sources/sessions/AUDIT-FAILURE-[component]-[date].md`
**Confirmación:** None — se escribe directamente.

Load template: `assets/templates/problem.md`

Required fields:
- `title` — concise problem statement (max 80 chars)
- `context` — what was being attempted when the problem appeared
- `root_cause` — diagnosed cause, not just symptoms
- `solution` — exact steps that resolved it
- `mitigation` — what was changed to prevent recurrence
- `affected_components` — list of skill/agent names
- `severity` — low | medium | high | critical
- `recurrence_risk` — low | medium | high

---

### 2.3 Tipo: `adr` (Architectural Decision Record)
**Cuándo:** Cuando se toma una decisión arquitectónica significativa.
**Destino:** `rag/sources/adrs/ADR-NNN-[title]-[date].md`
**Confirmación:** Required — se presenta al operador antes de persistir.

Load template: `assets/templates/adr.md`

Required fields:
- `title` — decision statement (max 100 chars)
- `context` — what situation forced this decision
- `decision` — what was chosen
- `alternatives_considered` — list of options that were evaluated
- `reasoning` — why this option was selected over alternatives
- `consequences` — known trade-offs or future implications
- `status` — accepted | superseded | deprecated
- `supersedes` — filename of previous ADR if this replaces one

---

### 2.4 Tipo: `pattern`
**Cuándo:** When the same problem or solution appears 2+ times across different
components or projects. The agent detects this by cross-referencing `problem` entries.
**Confirmación:** Required — present to operator before persisting.

Load template: `assets/templates/pattern.md`

Required fields:
- `title` — pattern name (concise, action-oriented)
- `description` — what this pattern is and when it applies
- `evidence` — list of journal entry filenames that exhibit this pattern
- `recommendation` — concrete action to apply or avoid this pattern
- `applies_to` — skill types or contexts where this pattern is relevant
- `first_seen` — date of earliest evidence entry

---

### 2.5 Tipo: `field`
**Cuándo:** When a Catálogo skill or agent is used in a real client project
and produces observable results — positive or negative.
**Confirmación:** Required — present to operator before persisting.

Load template: `assets/templates/field.md`

Required fields:
- `skill_or_agent` — component name from manifest
- `project_context` — type of project (no client names — describe by industry/use case)
- `usage_description` — what the component was used for
- `outcome` — what actually happened
- `client_friction` — any confusion, errors, or complaints from the end user
- `suggested_improvement` — concrete change to the skill/agent based on this experience
- `operator_rating` — 1-5 (how well did the component serve the project)

---

## 3. Flujo de Escritura

### Para entradas automáticas (forge, problem):

```
1. Collect required fields from current task context
2. Load corresponding template from assets/templates/
3. Populate all fields — no empty fields allowed
4. Run: python scripts/journal_write.py --type forge|problem --payload '<json>'
5. Confirm entry_path in output
6. Increment forge counter (forge type only)
7. Check if report threshold reached → generate report if yes
```

### Para entradas con confirmación (adr, pattern, field):

```
1. Invoke rag-query to check for duplicates or related entries
2. Collect required fields from context
3. Load template and populate all fields
4. PAUSE — present formatted entry to operator with:
   "He preparado esta entrada de journal. ¿La guardamos tal cual, la ajustas, o la descartamos?"
5. On operator approval: run journal_write.py
6. On adjustment: incorporate changes, re-present once, then save
7. On discard: log [JOURNAL-DESCARTADO: reason] in workflow-state.json only
```

---

## 4. Contador de Forjas y Reportes Automáticos

The `.forge-counter.json` file tracks forge completions and triggers pattern reports:

```json
{
  "total_forges": 0,
  "report_threshold": 10,
  "last_report_at": 0,
  "last_report_file": null
}
```

**Trigger logic:**
- On every successful `forge` entry: increment `total_forges`
- If `total_forges - last_report_at >= report_threshold`: generate pattern report
- Update `last_report_at` to current `total_forges` after report generation

**Changing the threshold:**
Edit `report_threshold` in `.forge-counter.json` directly. The agent respects
whatever value it finds there. Default is 10.

**Report content** (see `references/report_structure.md`):
- Summary of forges in the batch (component names, types, patterns used)
- Problem frequency analysis (which problems recurred)
- ADR changes since last report
- Field feedback synthesis
- Recommendations for catalog improvement

---

## 5. Scripts de Soporte

### `journal_write.py`
Writes a new journal entry from a JSON payload and template.

```bash
python scripts/journal_write.py \
  --type forge|problem|adr|pattern|field \
  --payload '{"component_name": "rag-query", ...}' \
  [--journal-dir ./.agent/memory/journal]

# Exit codes:
# 0 — Entry written successfully
# 1 — Invalid entry type
# 2 — Missing required fields for this entry type
# 3 — Journal directory not found or not writable
# 4 — Duplicate detection: similar entry found (use --force to override)
```

### `journal_report.py`
Generates a pattern report from all entries since the last report.

```bash
python scripts/journal_report.py \
  [--journal-dir ./.agent/memory/journal] \
  [--since-entry <filename>]

# Exit codes:
# 0 — Report generated
# 1 — No entries found since last report
# 2 — Journal directory not found
```

### `journal_query.py`
Text-based search across journal entries (complement to RAG for exact matches).

```bash
python scripts/journal_query.py \
  --term "chromadb" \
  --type problem \
  [--journal-dir ./.agent/memory/journal]

# Returns: matching entry filenames + first 3 lines of each
# Exit codes: 0 found, 1 none found, 2 directory error
```

---

## 6. Integración con RAG

Journal entries feed the `decisiones-arq` ChromaDB collection via `rag-indexer`.

- `rag-indexer` indexes `./.agent/memory/journal/entries/` on every deployment
- Query prefix for journal entries in RAG: `[JOURNAL]` — included in each entry's header
- The `pattern` and `adr` entry types have the highest RAG retrieval value;
  `forge` entries are primarily for audit, not semantic search

**When rag-query returns a journal entry:**
Treat it as institutional memory — not as a rule, but as informed context.
If a previous ADR conflicts with a new decision, surface the conflict to the operator
before proceeding.

---

## 7. Referencias Rápidas (Load on Demand)

- `references/report_structure.md` — Pattern report format and section guide
- `references/entry_examples.md` — Filled example of each entry type
