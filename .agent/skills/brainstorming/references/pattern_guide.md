# Pattern Guide — brainstorming
# Load when the design pattern choice is not immediately obvious.

## Los 4 Patrones de Skills

### High Freedom
**Estructura:** `SKILL.md` only  
**Mecanismo:** Pure text instructions, examples, heuristics  
**Usar cuando:**
- The task is advisory, creative, or stylistic
- Acceptable variance in output — no single "correct" result
- No file system operations or external API calls required
- Examples: writing assistants, code review guides, style guides

**Señal de alerta:** If you find yourself wanting to add a script "just to be safe",
reconsider — the task may actually be Deterministic.

---

### Deterministic
**Estructura:** `SKILL.md` + `scripts/`  
**Mecanismo:** Agent gathers context → instructs execution of script → interprets exit code  
**Usar cuando:**
- The task involves file manipulation, API calls, or system operations
- Errors are costly or hard to reverse (deployments, deletions, transformations)
- The same input must always produce the same output
- Examples: validators, file generators, deployment scripts, API bridges

**Señal de alerta:** If the script logic requires the LLM to "think" during execution,
split into: (1) LLM prepares parameters, (2) script executes deterministically.

---

### Deep Domain
**Estructura:** `SKILL.md` + `references/`  
**Mecanismo:** SKILL.md keeps high-level flow; agent loads references conditionally  
**Usar cuando:**
- The knowledge base is large (> 500 lines if inlined)
- Different parts of the documentation are needed in different scenarios
- Examples: large API docs, internal policy guides, complex schema references

**Señal de alerta:** If you're tempted to put everything in SKILL.md, check the
token count first. > 5000 tokens = move to references/.

---

### Template
**Estructura:** `SKILL.md` + `assets/templates/`  
**Mecanismo:** Agent reads template → injects variables → writes output  
**Usar cuando:**
- The output is always the same structure with variable content
- Multiple projects will use the same boilerplate
- Examples: project scaffolding, config file generators, component starters

**Señal de alerta:** If the template requires significant modification per use case,
consider whether it's actually a High Freedom skill with examples.

---

### Composite (advanced)
**Estructura:** Multiple skills that activate sequentially  
**Mecanismo:** Each skill handles one stage; handoff via explicit output format  
**Usar cuando:**
- The task has 3+ distinct stages each requiring different expertise
- Stages can fail independently and need isolated error handling
- Examples: data pipeline (extract → transform → load), multi-stage validation

**Señal de alerta:** Only use Composite if a single skill genuinely can't handle
the full scope. Premature decomposition adds coordination overhead.

---

## Matriz de Decisión Rápida

| Pregunta | Respuesta → Patrón |
|---|---|
| ¿Requiere ejecución determinista (archivos, APIs, scripts)? | Sí → **Deterministic** |
| ¿La base de conocimiento supera 500 líneas si se inlinea? | Sí → **Deep Domain** |
| ¿El output siempre tiene la misma estructura con variables? | Sí → **Template** |
| ¿Tiene 3+ etapas con fallos independientes? | Sí → **Composite** |
| ¿Ninguna de las anteriores? | → **High Freedom** |

---

## Combinaciones Válidas

Algunos componentes requieren más de un patrón:

- **Deterministic + Deep Domain:** script + large reference docs
  → `SKILL.md` + `scripts/` + `references/`
- **Template + Deterministic:** template generation + validation script
  → `SKILL.md` + `scripts/` + `assets/templates/`

Nunca combinar High Freedom con scripts — si necesitas scripts, no es High Freedom.
