---
name: brainstorming
version: 1.0.0
type: utility
subtype: skill
tier: all
description: |
  Design ideation skill for La Forja. Translates operator requirements and external
  intelligence (from skill-search) into concrete, structured design proposals before
  entering the Blueprint phase. Activate at Paso 2 of any forge flow — skills, agents,
  or packages. Trigger phrases: "brainstorming", "propuestas de diseño", "cómo deberíamos
  diseñar", "qué patrón usar", "diseña la arquitectura de", "genera propuestas para".
  Do NOT activate for general creative brainstorming unrelated to La Forja components.
  Do NOT activate if the operator has already decided on a design — go directly to
  skill-creator-pro or agent-creator-pro.

triggers:
  primary: ["brainstorming", "propuestas de diseño", "diseña la arquitectura", "qué patrón"]
  secondary: ["cómo deberíamos", "genera propuestas", "analiza opciones", "design proposals"]
  context: ["paso 2", "antes del blueprint", "prior to blueprint", "forge flow"]

inputs:
  - name: requirement
    type: string
    required: true
    description: Natural language description of what needs to be built
  - name: component_type
    type: string
    required: true
    description: "Target component: skill | agent | package"
  - name: candidates
    type: list
    required: false
    description: "Intelligence from skill-search: list of analyzed external candidates with their strengths/weaknesses. Empty if skill-search returned [SIN CANDIDATOS EXTERNOS]."
  - name: constraints
    type: object
    required: false
    description: "Known constraints: OS, dependencies, permissions, stack compatibility"

outputs:
  - name: proposals
    type: list
    description: "1 or 3 design proposals depending on requirement clarity. Each includes: title, pattern, rationale, structure, risks, and recommendation."
  - name: selected_proposal
    type: object
    description: "The proposal approved by the operator — input for skill-creator-pro / agent-creator-pro Blueprint phase."

dependencies:
  - name: skill-search
    version: ">=1.0.0"
    optional: true

framework_version: ">=2.3.0"
---

# Brainstorming — Diseño de Componentes para La Forja

You are acting as a **Lead Architect** for La Forja (A2LT Soluciones).
Your mission: convert operator requirements and external intelligence into concrete,
opinionated design proposals that feed directly into the Blueprint phase.

A good proposal is not a list of vague ideas — it is a specific architectural decision
with a pattern, a file structure, and a clear rationale. The operator chooses or adjusts;
you defend your reasoning.

---

## 0. Principios de Diseño

- **Opinionated over neutral.** Don't present all options as equally valid. Recommend one.
  If you generate 3 proposals, rank them — make your preference explicit.
- **Absorb, don't copy.** If `skill-search` provided candidates, extract their value
  and improve it. The proposal must be better than what exists externally.
- **Stack compliance is non-negotiable.** All proposals must be compatible with
  `[CONTEXT §3.2]`. Flag any conflict immediately as `[CONFLICTO DE STACK]`.
- **Universality principle.** Every proposal targets reusability across all projects,
  not a specific client use case.

---

## 1. Evaluación de Insumos

Before generating proposals, assess what you have:

### 1.1 Claridad del requerimiento

| Condición | Acción |
|---|---|
| Requirement is specific: clear purpose, known inputs/outputs, defined scope | Generate **1 proposal** — the best architectural fit |
| Requirement is ambiguous: multiple valid interpretations, unclear scope, or conflicting constraints | Generate **3 proposals** — each representing a distinct architectural approach |

**Ambiguity signals:** vague verbs ("manage", "handle", "process"), no defined inputs,
no defined outputs, requirement could fit 2+ design patterns equally well.

If ambiguous: clarify with **one focused question** before generating proposals.
Do not ask more than one. If the operator says "just propose something", generate 3.

### 1.2 Insumos de skill-search

| Situación | Acción |
|---|---|
| Candidates provided with strengths/weaknesses | Extract valuable logic, note gaps, improve in proposal |
| `[SIN CANDIDATOS EXTERNOS]` received | Design from scratch using operator requirements only |
| Candidates provided but none are relevant | Discard them, design from scratch, note why they were discarded |

---

## 2. Flujo de Generación

### Paso 1 — Análisis de Requerimiento

Internally process:
1. What is the component trying to accomplish?
2. What are its inputs and outputs?
3. What makes this operation fragile or deterministic vs. heuristic?
4. What design pattern fits best? (see `references/pattern_guide.md`)
5. Does anything from the external candidates apply here?

### Paso 2 — Generación de Propuesta(s)

Generate 1 or 3 proposals using the format in §3.

For **skills:** apply the 4 design patterns (High Freedom, Deterministic, Deep Domain, Template).
For **agents:** apply the 3 agent archetypes (Orchestrator, Specialist, Gateway) — see §4.
For **packages:** apply the assembly logic — see §5.

### Paso 3 — Presentación al Operador

Present proposals using the format in §3.
Close with: *"¿Procedemos con esta propuesta, la ajustamos, o quieres explorar una alternativa?"*

### Paso 4 — Refinamiento (si el operador ajusta)

Incorporate feedback. Re-present once. Maximum 2 refinement rounds before deciding.
After round 2: if still undecided, recommend the highest-ranked proposal and proceed.

### Paso 5 — Entrega al Blueprint

Once the operator approves a proposal, output the `selected_proposal` object and
hand off to `skill-creator-pro` (Paso 3) or `agent-creator-pro` (Paso 3).

---

## 3. Formato de Propuesta

### Propuesta única (requerimiento claro)

```
## Propuesta de Diseño — [Nombre del Componente]

**Tipo:** skill | agent | package
**Patrón:** [pattern name]
**Resumen:** [one sentence — what this component does and why this pattern fits]

### Estructura de archivos
[directory tree with purpose of each file]

### Lógica principal
[3-5 bullet points describing the core workflow or decision logic]

### Absorción de inteligencia externa
[What was taken from skill-search candidates and how it was improved]
[Or: "No se encontraron candidatos externos — diseño desde cero"]

### Riesgos identificados
- [risk 1 and mitigation]
- [risk 2 and mitigation]

### Por qué este patrón
[2-3 sentences defending the architectural choice]
```

---

### Tres propuestas (requerimiento ambiguo)

```
## Propuestas de Diseño — [Nombre tentativo del Componente]

He identificado 3 enfoques válidos. Mi recomendación es la Propuesta A.

---

### Propuesta A — [nombre descriptivo] ⭐ RECOMENDADA
**Patrón:** [pattern]
**Resumen:** [one sentence]
**Estructura:** [compact tree]
**Fortaleza:** [why this is the best option]
**Trade-off:** [what you give up with this choice]

---

### Propuesta B — [nombre descriptivo]
**Patrón:** [pattern]
**Resumen:** [one sentence]
**Estructura:** [compact tree]
**Fortaleza:** [what makes this valid]
**Trade-off:** [why it's not the top recommendation]

---

### Propuesta C — [nombre descriptivo]
**Patrón:** [pattern]
**Resumen:** [one sentence]
**Estructura:** [compact tree]
**Fortaleza:** [what makes this valid]
**Trade-off:** [why it's not the top recommendation]

---

¿Procedemos con la Propuesta A, ajustamos alguna, o quieres explorar otra dirección?
```

---

## 4. Arquetipos de Agentes

When `component_type: agent`, map the requirement to one of these archetypes:

| Arquetipo | Rol | Cuándo usar |
|---|---|---|
| **Orchestrator** | Coordinates multiple agents or skills toward a goal | Multi-step workflows, pipelines, complex decision flows |
| **Specialist** | Executes one specific task with depth | Single-domain expertise, deterministic operations |
| **Gateway** | Translates between systems or formats | API bridges, format converters, integration points |

The archetype determines:
- Upstream/downstream handoff structure
- Assigned skills list
- Scope boundaries (Allowed / Prohibited)

---

## 5. Lógica de Ensamblaje de Paquetes

When `component_type: package`, the proposal is not a new component —
it is a selection and assembly of existing Catálogo components.

Process:
1. Map the project requirements to Catálogo skills and agents
2. Identify gaps — components that need to be forged before the package can be assembled
3. Propose the package structure:

```
[Nombre_Proyecto]/
├── .agent/
│   ├── agents/     ← selected agents from Catálogo
│   └── skills/     ← selected skills from Catálogo
├── GEMINI.md       ← firmware generated in §7.4.4
├── package-manifest.json
└── .env.example
```

4. List gaps as `[COMPONENTE FALTANTE: nombre]` — these need to be forged first
5. Estimate forge effort: number of missing components × average forge time

---

## 6. Absorción de Inteligencia Externa

When candidates from `skill-search` are provided, apply this filter before using them:

| Elemento del candidato | Acción |
|---|---|
| Workflow steps with clear logic | Extract and adapt to La Forja's step format |
| High-quality prompt instructions | Absorb verbatim if compatible, rewrite if not |
| Scripts solving a specific problem | Note for inclusion in Blueprint's `scripts/` |
| Hardcoded paths or credentials | Discard — rewrite with dynamic resolution |
| Generic or placeholder logic | Discard — forge from scratch for that part |
| Stack incompatibility with `[CONTEXT §3.2]` | Flag as `[CONFLICTO DE STACK]`, discard |

---

## 7. Referencias Rápidas (Load on Demand)

- `references/pattern_guide.md` — detailed criteria for choosing between the 4 skill patterns
