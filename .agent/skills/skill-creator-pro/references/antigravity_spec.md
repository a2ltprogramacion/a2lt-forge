# Antigravity Skill Specification

## Structure Overview
Skills are self-contained modules located in the `.agent/catalog/skills/<name>/` directory. They follow the "Level 5: Composition" architecture.

### Core Components
1.  **SKILL.md (Required):** The main orchestrator. Contains YAML frontmatter for activation matching and markdown instructions for the core workflow.
2.  **scripts/:** Python or Shell executable scripts. Used to encapsulate highly deterministic, fragile, or multi-step operations that LLMs usually fail at formatting properly.
3.  **references/:** Plain text or markdown documentation. Loaded conditionally on-demand via the `view_file` tool.
4.  **assets/:** Static resources like application boilerplates, code templates, or schemas.

## Frontmatter Schema
```yaml
---
name: kebab-case-name
description: |
  High-activation description string. Must include:
  - Precise operational purpose.
  - Required activation phrases / verbs.
  - Explicit "Do not use when" (negative filtering) cases.
---
```

## Progressive Disclosure Rules
- The main `SKILL.md` instruction set MUST stay under 5,000 tokens (approx. 500 lines).
- Deeper logic, massive command lists, API routes, or complex architectural schemas MUST be moved to `references/` and explicitly linked in `SKILL.md`.
