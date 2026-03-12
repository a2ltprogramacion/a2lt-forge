# yaml-validator

Skill de validación de archivos YAML contra esquemas JSON.

**Propósito:** Valida componentes de La Forja (SKILL.md, AGENT.md) antes de despliegue.

**Dependencias:** PyYAML, jsonschema

**Ubicación:** `./.agent/skills/yaml-validator/`

**Invocación:**
```bash
python scripts/yaml_validator.py --filepath "./catalogo/skills/ejemplo/SKILL.md" --strict-mode
```

Para detalles completos, ver SKILL.md en este directorio.
