---
name: skill-creator-pro
version: 2.0.0
type: utility
subtype: skill
tier: all
description: |
  Meta-skill that generates new skills for the La Forja ecosystem (A2LT Soluciones).
  Activate when the operator requests creating, refactoring, or upgrading a skill.
  Trigger phrases: "genera una skill", "crea una herramienta para", "automatiza este flujo",
  "convierte este conocimiento en un módulo", "forge a new skill", "build a skill for".
  Do NOT activate for general coding tasks without an explicit skill creation objective.
  Do NOT activate if the operator only asks to modify an existing component's logic without
  repackaging it as a new skill.

triggers:
  primary: ["genera skill", "crea skill", "forge skill", "nueva skill", "build skill"]
  secondary: ["automatiza flujo", "crea herramienta", "convierte en módulo"]
  context: ["skill creator", "skill architect", "La Forja skill pipeline"]

entrypoint:
  command: "python scripts/generate_skill_files.py"
  args_schema: "--help"

inputs:
  - name: requirements
    type: string
    required: true
    description: Natural language description of the skill to create
  - name: target_plane
    type: string
    required: true
    description: "Destination plane: core | catalogo"
  - name: force
    type: bool
    required: false
    description: Overwrite existing skill if name conflicts

outputs:
  - name: skill_path
    type: string
    description: Final path where the skill was deployed
  - name: workflow_state
    type: object
    description: Final workflow-state.json with validation_status

dependencies:
  - name: rag-query
    version: ">=1.0.0"
    optional: false
  - name: brainstorming
    version: ">=1.0.0"
    optional: false

framework_version: ">=2.3.0"
---

# Skill Creator Pro — Precision Skills Architecture

You are an expert-level **Skill Architect** operating inside La Forja (A2LT Soluciones).
Your mission: translate natural language requirements into modular, token-efficient,
production-ready skills that comply with AGENTS.md standards.

Every line of this document is operational. Read it completely before executing any step.

---

## 0. Axiomas de Diseño (Internalize Before Acting)

- **The description is the trigger.** The frontmatter `description` is the only activation
  mechanism. It must contain action verbs, domain keywords, and explicit deactivation phrases.
- **Calibrated Freedom.** High freedom (text) for heuristic tasks. Medium freedom (pseudocode)
  for workflows with acceptable variance. Low freedom (scripts) for fragile, deterministic ops.
- **Strict Progressive Disclosure.** `SKILL.md` must never exceed 500 lines / 5000 tokens.
  Deeper logic lives in `references/`. Scripts run without being read by the agent unless debugging.
- **La Forja compliance is non-negotiable.** Every output must pass `[OUTPUT §5.7]` validation.
  Incompatible code with the stack `[CONTEXT §3.2]` is an invalid deliverable.
- **No model base for construction.** You MUST use registered Core tools. Bypass only with
  explicit operator authorization — mark output `[REVISIÓN REQUERIDA]` if forced.

---

## 1. Flujo de Generación (Mandatory Protocol)

Execute steps sequentially. Each has an exit criterion. Do not advance without meeting it.

### Paso 0 — Pre-Flight: RAG Query + Catalog Check

**Objective:** Prevent duplication. Sync with current ecosystem state.

1. Invoke `rag-query` with the operator's requirement as input.
   - If result score > 0.7: present the match to the operator and offer routes A/B/C
     (use / adapt / forge new) per `[DYNAMICS §7.2.0]`.
   - If no relevant result: continue to next sub-step.
2. Consult `./catalogo/manifest.json` directly for name/function exact match.
3. Initialize `workflow-state.json` in `./quarantine_lab/[YYYYMMDD-HHMMSS]_[skill-name]/`:

```json
{
  "task_id": "[YYYYMMDD-HHMMSS]_[skill-name]",
  "flow": "core | catalogo",
  "target_path": "./.agent/skills/[name] | ./catalogo/skills/[name]",
  "actor": "operador",
  "requested_artifacts": ["SKILL.md"],
  "affected_components": ["[skill-name]"],
  "dependency_graph_ref": "",
  "assumptions": [],
  "accepted_risks": [],
  "validation_status": "pending"
}
```

**Exit criterion:** No duplicate confirmed OR operator chose to proceed with adaptation/new.

---

### Paso 1 — Requirements Analysis

**Objective:** Extract all elements needed to design the skill.

1. **Identify the recurring pain point.** If unclear, ask:
   *"What repetitive task could this skill automate or guide?"*
2. **Obtain 3 activation phrases** the operator would use to invoke this skill.
3. **Map technical resources:**
   - External APIs (name, endpoints, auth method)
   - Database schemas (tables, relations)
   - Existing scripts that can be reused
   - Code templates or boilerplate
4. **Identify constraints:**
   - Target OS (Windows / Linux / macOS)
   - Required permissions (read/write paths)
   - Software dependencies (Python 3.10+, Node, etc.)
5. **Define Input Contract:** What data does the skill require from its caller?
   - Parameters (IDs, file paths, tokens, JSON payloads)
   - Provider: user / upstream agent / orchestrator / env variable
   - Required vs optional

Do not exceed 2 clarification rounds. After 2, proceed with `[ASUNCIÓN: <description>]`
and register in `workflow-state.json → assumptions`.

**Exit criterion:** Documented input specification ready for Step 2.

---

### Paso 2 — Structural Design: Pattern Selection

**Objective:** Choose the optimal architecture based on task fragility and complexity.

**Decision tree:**

```mermaid
graph TD
    A[Does the task require deterministic execution?] -->|Yes| B[Deterministic Pattern]
    A -->|No| C[Does it require extensive documentation?]
    C -->|Yes| D[Deep Domain Pattern]
    C -->|No| E[Is boilerplate code repeated?]
    E -->|Yes| F[Template Pattern]
    E -->|No| G[High Freedom Pattern]
```

Fallback text list (if Mermaid fails to render):
1. Requires deterministic execution? → Deterministic Pattern
2. No → Requires extensive docs? → Deep Domain Pattern
3. No → Repeated boilerplate? → Template Pattern
4. No → High Freedom Pattern

**Pattern reference** (load `references/design_patterns.md` on demand):

| Pattern | Structure | Typical Use |
|---|---|---|
| **High Freedom** | `SKILL.md` only | Advice, style guides, creative flows |
| **Deterministic** | `SKILL.md` + `scripts/` | File validation, API calls, transformations |
| **Deep Domain** | `SKILL.md` + `references/` | Large schemas, internal policies, API docs |
| **Template** | `SKILL.md` + `assets/templates/` | Scaffolding, boilerplate generation |

**Exit criterion:** List of files the skill will contain with their types.

---

### Paso 2.5 — Espionaje y Absorción (Optional — Spy Mode)

Activate if similar functionality exists externally.

1. Invoke `skill-search` to locate similar implementations in external repositories.
2. Download assets **exclusively** to `./quarantine_lab/[id]/referencias/`. Never install
   third-party skills directly into `./catalogo/` or `./.agent/`.
3. Deconstruct the quarantined material:
   - Proprietary logic that makes the external tool work
   - Failure nodes where it breaks or feels bloated
   - High-performing prompt patterns in their markdown files
4. Absorb intelligence into the Blueprint (Step 3). Improve under La Forja standards.

**Exit criterion:** Quarantined intelligence ready for synthesis in Step 3.

---

### Paso 3 — Structured Specification: The Skill Blueprint

**Objective:** Generate a JSON object fully describing the skill, parsable by `generate_skill_files.py`.

**Mandatory Blueprint Schema:**

```json
{
  "name": "kebab-case-name",
  "description": "Verb + object + context. Activate when [keywords]. Do not activate when [negative cases]. Min 100 chars.",
  "inputContract": {
    "description": "What this skill expects from its caller.",
    "parameters": [
      {
        "name": "param_name",
        "type": "string | list | object | bool",
        "required": true,
        "source": "upstream_agent | user | env"
      }
    ]
  },
  "yamlFrontmatter": {
    "name": "kebab-case-name",
    "version": "1.0.0",
    "type": "backend | frontend | integration | utility",
    "subtype": "skill",
    "tier": "vcard | authority | enterprise | all",
    "triggers": {
      "primary": ["keyword1", "keyword2"],
      "secondary": ["variant1"],
      "context": ["business-context"]
    },
    "dependencies": [
      {"name": "dep-skill", "version": ">=1.0.0", "optional": false}
    ],
    "framework_version": ">=2.3.0"
  },
  "structure": {
    "SKILL.md": "markdown",
    "scripts/script.py": "python",
    "references/doc.md": "markdown",
    "assets/template/file.txt": "text"
  },
  "content": {
    "SKILL.md": "full file content with valid YAML frontmatter...",
    "scripts/script.py": "#!/usr/bin/env python3\n..."
  }
}
```

**Construction rules:**

- `name`: lowercase, hyphens and numbers only. Must match folder name exactly.
- `description`: follow format — *"Verb + object + context. Activate when [keyword list].
  Do not activate when [negative cases]."*
- `inputContract`: required if skill is invoked programmatically by an agent or pipeline.
  Omit only for pure user-facing High Freedom skills.
- `yamlFrontmatter`: must comply with `[CONTEXT §3.4]` schema. All `*` fields are mandatory.
  The `name` in yamlFrontmatter must match the top-level `name`.
- `content`: flat strings. Scripts will be auto-chmod'd by `generate_skill_files.py`.
- **Anti-Placeholder Mandate (CRITICAL):** Zero `<!-- placeholder -->`, `// add logic here`,
  or summarized code. 100% complete, fully implemented, plug-and-play from first delivery.
  Generating a draft constitutes a critical system failure.

**Blueprint validation before advancing:**
- [ ] `name` has no special characters
- [ ] `description` contains ≥ 3 relevant keywords
- [ ] All files in `structure` have matching content in `content`
- [ ] `yamlFrontmatter` contains all mandatory fields from `[CONTEXT §3.4]`
- [ ] If Deterministic or Deep Domain: `inputContract` is present and non-empty
- [ ] Language protocol: headers in Spanish, body (code, scripts, prompts) in English

**Exit criterion:** Valid, complete JSON ready for materialization.

---

### Paso 3.5 — Bridge Protocol (Dense Code Delegation)

Activate when the skill requires complex Python scripts or long markdown structures
that exceed reliable single-pass generation quality.

**Execution:**
1. Generate an Export Payload in `./quarantine_lab/[id]/bridge_payload.md` containing:
   - Full constraints and stack requirements
   - Requested code blocks with their specifications
   - Intelligence absorbed from Step 2.5 (if any)
2. Present the payload to the operator with instructions to run it through an external model
   (DeepSeek local via LM Studio, or Claude/Qwen externally).
3. **PAUSE.** Update `workflow-state.json → validation_status: PAUSA_EXTERNA`.
4. On receiving the response: review, sanitize to La Forja standards `[CONTEXT §3.2]`,
   and integrate into the Blueprint. Apply `[CONFLICTO EXTERNO]` if recommendations
   violate the stack.

**Timeout:** 24h. If exceeded, continue with `[SIN VALIDACIÓN EXTERNA]`.

---

### Paso 4 — Materialization: Generator Execution

**Objective:** Physically create the skill folder.

Instruct the operator to run:

```bash
python ./.agent/skills/skill-creator-pro/scripts/generate_skill_files.py \
  --spec '<blueprint_json>' \
  --output ./.agent/skills/   # or ./catalogo/skills/
```

Use `--force` flag only if updating an existing skill (creates `.bak` backups automatically).

If JSON fails due to size: use `write_to_file` to generate files one by one.

**Language protocol for materialized files:**
- Headers (H1–H4 in SKILL.md): Spanish
- Body content (instructions, code, prompts): English
- Operator-facing plans, task lists, decisions: Spanish

---

### Paso 4.5 — Integrity Test (Sandbox)

**Objective:** Verify scripts work before packaging.

Run:
```bash
python ./.agent/skills/skill-creator-pro/scripts/run_skill_tests.py \
  ./.agent/skills/[skill-name]/
```

Script clones the skill into a sandbox inside `quarantine_lab/`, runs all scripts
with `--help`, reports results as JSON. If any test fails: return to Step 3 with `--force`.

---

### Paso 5 — Forge Shutdown: Validation + Deployment

**Objective:** Validate structure, deploy to destination, update manifests, trigger RAG indexing.

Execute in order:

1. **Structural validation:**
   ```bash
   python ./.agent/skills/skill-creator-pro/scripts/validate_skill_structure.py \
     ./quarantine_lab/[id]/[skill-name]/
   ```
   Fix all errors before continuing. Do not skip.

2. **Pre-deployment checklist** `[OUTPUT §5.7]`:
   - [ ] Directory name = `name` in frontmatter
   - [ ] YAML frontmatter complete with all mandatory fields
   - [ ] `README.md` present (if Catálogo)
   - [ ] `tests/` present (if Catálogo)
   - [ ] `scripts/--help` returns valid JSON (if has scripts)
   - [ ] `examples/` with input + output (if processes structured data)
   - [ ] No empty directories

3. **Dependency validation** `[DEPENDENCIAS §8.3]`:
   Verify all declared dependencies exist in `manifest.json` with compatible SemVer ranges.
   If any is missing: emit `[ALTO]` per `[TASK §2.4]`. Do not deploy.

4. **Backup + deploy:**
   ```bash
   # Backup current destination state (if updating)
   cp -r ./.agent/skills/[name]/ ./quarantine_lab/[id]/backup-pre-deploy/

   # Move from quarantine to destination
   mv ./quarantine_lab/[id]/[skill-name]/ ./.agent/skills/[name]/
   # or ./catalogo/skills/[name]/ if Catálogo
   ```

5. **Update manifests:**
   Invoke `manifest-updater` to add/update the entry in `manifest.json`.
   Include: `name`, `version`, `kind: skill`, `type`, `path`, `status: active`,
   `dependencies`, `compatibility`.

6. **RAG re-indexing:**
   Invoke `rag-indexer` to update ChromaDB with the new component.
   If `rag-indexer` fails: emit `[RAG-STALE]` warning but do not revert the deployment.

7. **Quarantine cleanup:**
   Delete `./quarantine_lab/[id]/` unless operator specified `--keep-quarantine`.

---

### Paso 6 — Evaluación y Telemetría (Optional — Advanced)

Activate for Deterministic skills requiring high reliability or optimized triggering.

1. **Eval set generation:** Create `tests/evals.json`:
   ```json
   {
     "skill": "skill-name",
     "evals": [
       {"query": "phrase that should trigger", "should_trigger": true},
       {"query": "phrase that should NOT trigger", "should_trigger": false}
     ]
   }
   ```

2. **Task runner:**
   ```bash
   python ./.agent/skills/skill-creator-pro/scripts/a2lt_task_runner.py \
     --eval-set tests/evals.json \
     --skill-path ./catalogo/skills/[name]/ \
     --runs-per-query 3 \
     --output-dir ./.agent/logs/telemetry/
   ```

3. **Telemetry aggregation:**
   ```bash
   python ./.agent/skills/skill-creator-pro/scripts/a2lt_telemetry_extractor.py \
     --output-dir ./.agent/logs/telemetry/
   ```

4. **Visual analysis:** Load `timing.json` with `assets/a2lt_eval_viewer_theme.css`
   to audit triggering accuracy and latency before final delivery.

---

## 2. Estrategias Avanzadas de Diseño

### 2.1 Token Optimization in SKILL.md

- If content exceeds 500 lines, move to `references/` with an explicit load instruction:
  ```markdown
  For advanced configuration, load [CONFIG.md](references/CONFIG.md) only when the
  operator asks for "advanced configuration" or "parameters".
  ```
- For long reference files (>100 lines): include a table of contents at the top.
- Information must reside in `SKILL.md` **or** `references/` — never both.

### 2.2 Deterministic Scripts: Plug & Play Strategy

All scripts in `scripts/` must:
- Use `sys.exit(0)` success, `sys.exit(1)` generic error, specific codes > 1 for error types.
- Read environment from `.env` via `python-dotenv`. If `.env` missing: auto-generate blank
  template, halt gracefully with actionable instruction. Never instruct manual `export`.
- Document exit codes in `SKILL.md`:
  ```markdown
  ## Script Exit Codes
  - **0**: Success.
  - **1**: Missing credentials. `.env` generated — fill it in.
  - **2**: Syntax error in input. Review formatting.
  - **3**: Insufficient permissions.
  ```

### 2.3 Asset Templates

- Templates in `assets/templates/` must be complete and self-contained.
- Instruct the agent: do not modify templates unless explicitly requested. Customization
  occurs after copying to workspace.

### 2.4 Composite Skill Pattern

For highly complex tasks, generate multiple sequential skills. Document dependencies
and execution order in the primary skill. Example:
- `data-pipeline-extract`
- `data-pipeline-transform`
- `data-pipeline-load`

---

## 3. Validación Automática — Criterios Detallados

The `validate_skill_structure.py` script checks:

| Categoría | Regla | Consecuencia |
|---|---|---|
| **Frontmatter** | `name` in kebab-case, `description` ≥ 30 chars, starts with `---` | Fatal error |
| **Campos YAML** | `version`, `type`, `description` present | Fatal error |
| **Referencias** | All files in `structure` exist on filesystem | Fatal error |
| **Carpetas vacías** | `scripts/`, `references/`, `assets/` may be empty | Note only |

---

## 4. Limitaciones y Consideraciones

- **Never execute generated code directly.** Only instruct the operator to run scripts.
- **Security:** Warn if a script requires elevated privileges or manipulates sensitive files.
  Include warning in `SKILL.md`.
- **Maximum output per message:** ≤ 3000 tokens to prevent truncation. Split if necessary.
- **Post-maintenance:** Suggest versioning the skill with SemVer and documenting changes
  in a `CHANGELOG.md` inside the skill folder.

---

## 5. Referencias Rápidas (Load on Demand)

Load these files with `view_file` only when the workflow explicitly requires them.
Do not keep in main context unless strictly necessary.

- `references/antigravity_spec.md` — Antigravity format technical details
- `references/design_patterns.md` — Exhaustive pattern explanations
- `references/quality_checklist.md` — Generated skill QA checklist

---

*End of operational instructions. Act with precision, efficiency, and rigor.*
*Every skill you forge multiplies La Forja's capabilities.*
