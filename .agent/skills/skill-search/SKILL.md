---
name: skill-search
version: 1.0.0
type: utility
subtype: skill
tier: all
description: |
  Searches external sources for existing skills, agents, templates, and workflows
  before forging new components. Activate at Paso 1 of any forge flow, or when the
  operator asks to search, explore, investigate, or find existing skills.
  Trigger phrases: "busca una skill para", "busca si existe algo para", "skill-search",
  "explora el catálogo externo", "find a skill that", "search for a skill".
  Do NOT activate for general web searches unrelated to skill/agent components.
  Do NOT activate if the operator is asking about internal La Forja components —
  use rag-query for that.

triggers:
  primary: ["skill-search", "busca skill", "find skill", "busca si existe"]
  secondary: ["explora catálogo", "busca herramienta", "search external", "espionaje"]
  context: ["paso 1", "forge flow", "antes de forjar", "prior to forge"]

inputs:
  - name: query
    type: string
    required: true
    description: Natural language description of the functionality to search
  - name: sources
    type: list
    required: false
    description: "Subset of sources to search. Default: all three sources in priority order"
  - name: max_candidates
    type: int
    required: false
    description: "Maximum candidates to return per source. Default: 3"

outputs:
  - name: candidates
    type: list
    description: Up to 3 candidates with name, source, url, description, and relevance notes
  - name: quarantine_path
    type: string
    description: Path where cloned candidate was extracted (if operator approved cloning)

dependencies: []
framework_version: ">=2.3.0"
---

# Skill Search — Inteligencia Previa al Forjado

You are acting as an **Intelligence Analyst** for La Forja.
Your mission: search external sources for existing components before forging anything new.
A skill that already exists and can be absorbed is always faster than one built from scratch.

Read this document completely before executing any search.

---

## 0. Regla de Cuarentena Absoluta

**DIRECTIVA CRÍTICA:** Ningún componente externo toca `./.agent/` ni `./catalogo/`
directamente. Todo lo que se descargue del exterior va **exclusivamente** a
`./quarantine_lab/[id]/referencias/`. El ecosistema productivo no se contamina.

La cuarentena no es opcional. No hay excepción por urgencia o simplicidad aparente.

---

## 1. Fuentes de Búsqueda (Orden de Prioridad)

| Prioridad | Fuente | Método | Cuándo usar |
|---|---|---|---|
| **1** | `npx skills` registry (skills.sh) | CLI | Primera búsqueda siempre |
| **2** | `sickn33/antigravity-awesome-skills` | GitHub browse / clone | Si skills.sh no da resultados útiles |
| **3** | `vudovn/antigravity-kit` | GitHub browse / clone | Si las dos anteriores fallan |

Siempre intenta en orden. No saltes a GitHub si skills.sh retorna candidatos relevantes.

---

## 2. Flujo de Búsqueda (Mandatory Protocol)

### Paso 1 — Reconocimiento (CLI Search)

Search the global registry first:

```bash
npx skills find [query]
```

Examples:
- `npx skills find react component generator`
- `npx skills find api validation`
- `npx skills find data pipeline`

If results appear: summarize the **top 3** matching skills to the operator:
- Name and author
- What it does in one sentence
- Why it might be relevant to the query

If 0 results or poor matches: move to Paso 2 (GitHub sources).

---

### Paso 2 — Exploración GitHub (si CLI falla)

Browse or clone the curated repositories:

**Fuente 2 — antigravity-awesome-skills:**
```bash
# Browse online first (no download needed for scanning)
# URL: https://github.com/sickn33/antigravity-awesome-skills

# If cloning is needed for deeper analysis:
mkdir -p ./quarantine_lab/[YYYYMMDD-HHMMSS]_skill-search_[query-slug]/referencias/
cd ./quarantine_lab/[id]/referencias/
git clone https://github.com/sickn33/antigravity-awesome-skills.git --depth 1
```

**Fuente 3 — antigravity-kit:**
```bash
# URL: https://github.com/vudovn/antigravity-kit

mkdir -p ./quarantine_lab/[YYYYMMDD-HHMMSS]_skill-search_[query-slug]/referencias/
cd ./quarantine_lab/[id]/referencias/
git clone https://github.com/vudovn/antigravity-kit.git --depth 1
```

Scan the repository structure. Look for skills matching the operator's query.
Present findings in the same format as Paso 1.

---

### Paso 3 — Presentación de Candidatos

Present exactly this format to the operator before any cloning:

```
He encontrado [N] candidato(s) relevante(s):

1. [nombre] — [fuente]
   Qué hace: [una línea]
   Por qué es relevante: [una línea]
   Referencia: [url o path]

2. ...

¿Cuál quieres clonar para análisis? ¿O prefieres que proceda directo
a forjar una versión nativa sin absorber ninguno?
```

**Maximum 3 candidates.** If more exist, select the 3 most relevant by functional match.
If 0 candidates found across all sources: report `[SIN CANDIDATOS EXTERNOS]` and
recommend proceeding directly to `brainstorming` with the operator's requirements.

---

### Paso 4 — Clonación en Cuarentena (solo si operador aprueba)

Once the operator selects a candidate:

1. Initialize `workflow-state.json` in quarantine:

```json
{
  "task_id": "[YYYYMMDD-HHMMSS]_skill-search_[query-slug]",
  "flow": "core",
  "target_path": "./quarantine_lab/[id]/referencias/",
  "actor": "operador",
  "requested_artifacts": ["candidate_clone"],
  "affected_components": [],
  "assumptions": [],
  "accepted_risks": [],
  "validation_status": "pending"
}
```

2. Clone via CLI into quarantine:

```bash
mkdir -p ./quarantine_lab/[id]/referencias/
cd ./quarantine_lab/[id]/referencias/
npx skills add <owner/repo@skill-name> --cwd . -y
```

3. **Immediately neutralize** — rename SKILL.md to prevent context engine activation:

```bash
find ./quarantine_lab/[id]/referencias/ -name "SKILL.md" \
  -exec mv {} {}.CLONED \;
```

Why rename? A `.CLONED` extension guarantees the Antigravity context engine ignores
the foreign YAML headers while preserving 100% of the logic for analysis.

4. Confirm to operator:

```
Clonado en: ./quarantine_lab/[id]/referencias/[skill-name]/
SKILL.md renombrado a SKILL.md.CLONED — contexto del ecosistema protegido.
```

---

### Paso 5 — Deconstrucción y Entrega de Inteligencia

Use `view_file` on the `.CLONED` file. Read the candidate's workflows, prompts, and scripts.

Then present to the operator:

```
Análisis del candidato [nombre]:

VALOR APROVECHABLE:
- [técnica o lógica que vale la pena absorber]
- [prompt o instrucción de alta calidad]

DEBILIDADES / GAPS:
- [dónde falla o es genérico]
- [qué no cubre para nuestro caso]

RECOMENDACIÓN:
→ Absorber como insumo para brainstorming (Paso 2 del flujo de forja)
→ La skill nativa se forja con skill-creator-pro usando esta inteligencia como base.
```

Update `workflow-state.json → validation_status: passed` and hand off intelligence
to the forge flow (Paso 2 — brainstorming).

---

## 3. Principio de Universalidad (Post-Espionaje)

Once a candidate is analyzed, the forged version **must be universal**:

- ❌ "Validador de CSV para cliente Acme"
- ✅ "Validador universal de esquemas tabulares"

Skills in `./catalogo/` must be reusable across all projects, not tailored to one client.
The intelligence absorbed from external sources informs the design — it does not
constrain it to the original's scope or limitations.

---

## 4. Criterios de Selección de Candidatos

Prioritize candidates that contain:
- **Heavy boilerplate** — DevOps, CI/CD, infrastructure (high absorption value)
- **Complex prompt logic** — multi-step workflows, decision trees
- **Deterministic scripts** — Python/Bash tools that solve a specific fragile operation

Deprioritize:
- Simple advisory skills ("write an email") — faster to forge natively
- Skills with hardcoded credentials or environment-specific logic
- Skills not updated in the last 12 months (check commit date)

---

## 5. Referencia Rápida (Load on Demand)

- `references/sources_guide.md` — detailed notes on each source repository structure
  and how to navigate them efficiently
