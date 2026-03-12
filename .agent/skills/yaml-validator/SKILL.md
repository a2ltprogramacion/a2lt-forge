---
name: yaml-validator
version: 1.0.0
type: utility
subtype: skill
tier: all
description: Validates YAML files against JSON schema. Returns detailed error report with line numbers and suggestions. Essential for component metadata validation in La Forja.

triggers:
  primary: ["validate yaml", "yaml check", "schema validation"]
  secondary: ["frontmatter validate", "metadata check"]
  context: ["automation", "quality assurance", "ci-cd"]

entrypoint:
  command: "python scripts/yaml_validator.py"
  args_schema: "--help"

inputs:
  - name: filepath
    type: string
    required: true
    description: "Absolute or relative path to YAML file to validate"
  - name: schema_path
    type: string
    required: false
    description: "Path to JSON Schema file. If omitted, applies La Forja default schema (§3.4)"
  - name: strict_mode
    type: bool
    required: false
    description: "If true, treats warnings as errors. Default: false"

outputs:
  - name: valid
    type: bool
    description: "Whether YAML is valid against schema"
  - name: errors
    type: array
    description: "List of validation errors with line numbers and suggestions"
  - name: warnings
    type: array
    description: "List of non-blocking issues (missing optional fields, deprecated patterns)"
  - name: metadata
    type: object
    description: "Extracted metadata if validation passed"

dependencies:
  - name: pyyaml
    version: ">=6.0"
    optional: false
  - name: jsonschema
    version: ">=4.17"
    optional: false

framework_version: ">=2.0.0"
---

# YAML Validator

## When to use this skill

- Validating La Forja component frontmatter (SKILL.md, AGENT.md) against schema §3.4
- Pre-deployment audits to catch YAML errors early (before Paso 7 de §7.2/7.3)
- CI/CD pipeline validation before committing to manifest
- Verifying `.env.example` structure
- **No usar cuando:** YAML is already validated by IDE; for simple lint checking without schema

## How to use it

**Invocación CLI:**

```bash
python scripts/yaml_validator.py --filepath "catalogo/skills/ejemplo/SKILL.md" --strict-mode
```

**Parámetros:**
| Parámetro | Tipo | Requerido | Descripción |
|---|---|---|---|
| --filepath | string | Sí | Ruta al archivo YAML a validar |
| --schema-path | string | No | Ruta al esquema JSON. Si se omite, usa esquema default de La Forja |
| --strict-mode | bool | No | Si está presente, trata warnings como errores |
| --output-format | string | No | json (default) \| text \| markdown |

**Parámetro de ejemplo de respuesta:**

```json
{
  "valid": true,
  "errors": [],
  "warnings": [
    {
      "line": 8,
      "field": "tier",
      "message": "Optional field missing. Assumes tier=all if not specified."
    }
  ],
  "metadata": {
    "name": "yaml-validator",
    "version": "1.0.0",
    "type": "utility"
  }
}
```

**Ejemplo de error capturado:**

```json
{
  "valid": false,
  "errors": [
    {
      "line": 3,
      "field": "version",
      "message": "Invalid SemVer. Expected format: MAJOR.MINOR.PATCH",
      "suggestion": "Change '1.0' to '1.0.0'"
    },
    {
      "line": 25,
      "field": "dependencies[0].version",
      "message": "Version range invalid. Expected >=1.0.0,<2.0.0",
      "suggestion": "Check §8.3 for proper SemVer range syntax"
    }
  ],
  "warnings": [],
  "metadata": null
}
```

## Decision Trees

**Árbol 1: ¿Qué hacer si hay errores?**

```
┌─ ¿Errores críticos (YAML malformado)?
│  └─ Sí → Arregla sintaxis YAML
│  └─ No → Continúa
├─ ¿Errores de esquema (campo faltante)?
│  └─ Sí → Agrega el campo obligatorio
│  └─ No → Continúa
├─ ¿Warnings (información incompleta)?
│  └─ strict-mode ON → Trata como error
│  └─ strict-mode OFF → Log pero no bloquea
```

**Árbol 2: ¿Cuándo escalar?**

```
┌─ ¿Esquema customizado requerido?
│  └─ Sí → Proporciona --schema-path a validator
│  └─ No → Usa default de La Forja
├─ ¿El error no está en la lista de sugerencias?
│  └─ Sí → Escalate a operador con output JSON completo
```
