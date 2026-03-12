# Quality Checklist — La Forja Skills
# Load this file only when running Paso 5 (Forge Shutdown) validation.
# Reference: AGENTS.md §5.7 + §3.4

## Frontmatter YAML (Fatal if missing)
- [ ] `name` is kebab-case and matches the folder name exactly
- [ ] `version` follows SemVer (X.Y.Z)
- [ ] `type` is one of: backend | frontend | integration | utility
- [ ] `description` present, in English, ≥ 30 chars, includes activation + deactivation phrases
- [ ] `triggers.primary` has at least 2 entries
- [ ] `framework_version` present and set to `>=2.3.0` or higher

## Structure and Content
- [ ] Clear 1-to-N step workflow documented
- [ ] SKILL.md is under 500 lines / 5000 tokens
- [ ] All files listed in Blueprint `structure` exist on filesystem
- [ ] All files in Blueprint `content` are 100% complete — zero placeholders
- [ ] Language protocol applied: headers Spanish, body (code/scripts/prompts) English

## Scripts (if Deterministic pattern)
- [ ] All scripts accept `--help` and return exit code 0 or 1
- [ ] Exit codes documented in SKILL.md
- [ ] Scripts read credentials from `.env` via python-dotenv (not hardcoded)
- [ ] If `.env` missing: script auto-generates template and exits gracefully
- [ ] `inputContract` defined in Blueprint JSON

## References (if Deep Domain pattern)
- [ ] All `references/` files linked explicitly in SKILL.md with load conditions
- [ ] Reference files have a table of contents if > 100 lines

## Assets (if Template pattern)
- [ ] Templates in `assets/templates/` are complete and self-contained
- [ ] SKILL.md instructs: do not modify templates unless explicitly requested

## Deployment Readiness
- [ ] `validate_skill_structure.py --strict` passes with 0 errors
- [ ] `run_skill_tests.py` passes (if has scripts)
- [ ] Skill registered in target plane `manifest.json`
- [ ] `rag-indexer` invoked after successful deployment
- [ ] `quarantine_lab/[id]/` cleaned up

## Catálogo-specific (if plane=catalogo)
- [ ] `README.md` present and complete
- [ ] `tests/` directory with `evals.json` (recommended for Deterministic)
- [ ] `examples/` with input + output samples (if processes structured data)
