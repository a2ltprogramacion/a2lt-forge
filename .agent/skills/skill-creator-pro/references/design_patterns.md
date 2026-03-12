# Skill Design Patterns

## 1. High-Freedom Pattern (Textual)
- **Use for:** Advice, formatting, style guidelines, creative tasks.
- **Structure:** `SKILL.md` ONLY (Instructions).
- **Mechanism:** Provide textual guidance and examples without relying on any external deterministic scripts.

## 2. Deterministic Pattern (Scripted)
- **Use for:** File manipulation, CI/CD triggering, validation, API calls, deployment.
- **Structure:** `SKILL.md` + `scripts/`.
- **Mechanism:** Agent gathers context/data → instructs user to execute script (e.g., Python/Bash) → interprets exit code and provides feedback. 

## 3. Deep Domain Pattern (Referential)
- **Use for:** Large operational manuals, massive schemas, internal policies, API docs.
- **Structure:** `SKILL.md` + `references/`.
- **Mechanism:** `SKILL.md` keeps high-level flow and instructs the agent exactly *when* to load specific `references/` via the `view_file` tool to avoid overwhelming the token window.

## 4. Templated Pattern (Asset-based)
- **Use for:** Generating boilerplates, scaffolding new apps, standardized configuration files.
- **Structure:** `SKILL.md` + `assets/templates/`.
- **Mechanism:** Agent reads template from `assets/` → injects dynamic variables based on user input → writes file to the workspace.
