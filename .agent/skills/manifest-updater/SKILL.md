---
name: manifest-updater
version: 1.0.0
type: utility
subtype: skill
tier: all
description: |
  Manages La Forja's three manifest files: ./.agent/manifest.json,
  ./catalogo/manifest.json, and ./output/[project]/package-manifest.json.
  Handles add, update, deprecate, and full integrity validation operations.
  Activate at Paso 5 of any forge flow after successful deployment, or when
  the operator needs to register, update, or audit a component.
  Trigger phrases: "actualiza el manifiesto", "registra el componente",
  "depreca la skill", "valida el manifiesto", "update manifest", "register component".
  Do NOT activate for reading the manifest — use rag-query or direct file inspection.
  Do NOT activate during quarantine — only after successful deployment.

triggers:
  primary: ["actualiza manifiesto", "registra componente", "update manifest", "register component"]
  secondary: ["depreca", "valida manifiesto", "manifest integrity", "nuevo componente desplegado"]
  context: ["paso 5", "forge shutdown", "post-deployment", "después de desplegar"]

inputs:
  - name: operation
    type: string
    required: true
    description: "One of: add | update | deprecate | validate"
  - name: plane
    type: string
    required: true
    description: "Target manifest: agent | catalogo | package"
  - name: component
    type: object
    required: false
    description: "Component entry data. Required for add/update/deprecate. Not needed for validate."
  - name: project_name
    type: string
    required: false
    description: "Required only when plane=package. Must match ./output/[project_name]/ directory."

outputs:
  - name: manifest_path
    type: string
    description: Path to the manifest file that was modified
  - name: validation_report
    type: object
    description: "For validate operation: list of errors and warnings found"

dependencies: []
framework_version: ">=2.3.0"
---

# Manifest Updater — Gestión de Manifiestos de La Forja

You are acting as a **Registry Keeper** for La Forja (A2LT Soluciones).
The manifests are the source of truth for the entire ecosystem — Health Checks,
DAG validation, RAG indexing, and deployment all depend on them being accurate.

**One mistake here cascades silently.** Read this document completely before
touching any manifest file.

---

## 0. Reglas Absolutas

- **Backup obligatorio antes de cualquier escritura.** Run `manifest_updater.py`
  with `--dry-run` first. Review the diff. Then run without `--dry-run`.
- **Nunca editar manifiestos a mano** durante un flujo activo. Only use the script.
- **`active` es el único status que el ecosistema consume.** `deprecated` and
  `experimental` components are ignored by Health Check and RAG indexing.
- **El `path` debe ser relativo a la raíz del proyecto**, not to the manifest location.
- **`dependencies: []` is mandatory**, even when empty. A missing key breaks the DAG check.

---

## 1. Schema de Manifiesto

### Estructura del archivo

```json
{
  "schema_version": "1.0.0",
  "plane": "agent | catalogo | package",
  "last_updated": "YYYY-MM-DDTHH:MM:SSZ",
  "components": []
}
```

### Entrada de componente — campos obligatorios

```json
{
  "name": "kebab-case-name",
  "version": "1.0.0",
  "kind": "skill | agent | workflow",
  "status": "active | deprecated | experimental",
  "path": "./.agent/skills/nombre | ./catalogo/skills/nombre",
  "dependencies": []
}
```

### Campos opcionales (del frontmatter §3.4)

```json
{
  "type": "backend | frontend | integration | utility",
  "tier": "vcard | authority | enterprise | all",
  "compatibility": ">=2.3.0",
  "description": "Single line, in English."
}
```

### Entrada de dependencia (dentro de `dependencies`)

```json
{
  "name": "dep-skill-name",
  "version": ">=1.0.0",
  "optional": false
}
```

---

## 2. Los Tres Manifiestos

| Manifiesto | Ruta | Plano | Quién lo actualiza |
|---|---|---|---|
| Core | `./.agent/manifest.json` | Infraestructura interna | Forge flow §7.2/§7.3 — Paso 5 |
| Catálogo | `./catalogo/manifest.json` | Activos de cliente | Forge flow §7.2/§7.3 — Paso 5 |
| Paquete | `./output/[proyecto]/package-manifest.json` | Ensamble de proyecto | Flujo de empaquetado §7.4 |

**Regla de plano:** Un componente vive en un solo manifiesto. Si una skill del Core
se exporta al Catálogo, crea una entrada nueva en `catalogo/manifest.json` — no
duplica la entrada del Core ni la mueve.

---

## 3. Flujo por Operación

### 3.1 ADD — Registrar componente nuevo

Cuándo: After successful deployment in Paso 5 of §7.2 or §7.3.

```
1. Verify component directory exists at declared path
2. Read frontmatter from SKILL.md or AGENT.md to extract optional fields
3. Check name does not already exist in target manifest (case-insensitive)
   → If exists: STOP — use UPDATE instead, not ADD
4. Run: python scripts/manifest_updater.py --operation add \
         --plane [agent|catalogo] \
         --component '<json>'
5. Confirm new entry in output
```

**Exit criteria:** Entry present in manifest with `status: active`.

---

### 3.2 UPDATE — Actualizar versión o status

Cuándo: When a component is re-forged with a new version, or when changing status.

```
1. Verify component exists in manifest by name
   → If not found: STOP — use ADD instead
2. Identify what changed: version bump, status change, dependency update
3. Run: python scripts/manifest_updater.py --operation update \
         --plane [agent|catalogo] \
         --component '<json with updated fields>'
4. Confirm updated entry in output
```

**SemVer rules for version bumps** `[DEPENDENCIAS §8.6]`:
- New scripts or breaking interface change → MAJOR
- New fields, new steps, backward-compatible additions → MINOR
- Bug fixes, doc updates, internal refactor → PATCH

---

### 3.3 DEPRECATE — Marcar componente como obsoleto

Cuándo: When a component is superseded by a newer version or removed from active use.

```
1. Verify component exists with status: active
2. Check for active dependents — components that list this as a dependency:
   Run: python scripts/manifest_updater.py --operation check-dependents \
         --plane [agent|catalogo] --name [component-name]
   → If active dependents exist: STOP — emit [ALTO]:
     "No se puede deprecar [nombre]: es dependencia activa de [lista]"
   → If no dependents: continue
3. Run: python scripts/manifest_updater.py --operation deprecate \
         --plane [agent|catalogo] --name [component-name]
4. Notify operator: deprecated components are ignored by Health Check and RAG
```

---

### 3.4 VALIDATE — Auditoría de integridad

Cuándo: On demand, or automatically triggered by `rag-indexer` before indexing.

The validation script checks all three manifests for:

| Check | Descripción | Severidad |
|---|---|---|
| Schema compliance | All required fields present per entry | Fatal |
| Name uniqueness | No duplicate names within a plane | Fatal |
| Path existence | Component directory exists on filesystem | Fatal |
| SKILL.md/AGENT.md presence | Entry file exists at path | Fatal |
| Version format | Follows SemVer X.Y.Z | Warning |
| Dependency resolution | All declared deps exist in some manifest | Warning |
| Circular dependencies | DAG check — no cycles | Fatal |
| Orphan paths | Directories in agent/skills or catalogo/skills not in manifest | Warning |

```bash
python scripts/manifest_updater.py --operation validate --plane all
```

Output: JSON report with `errors` (fatal) and `warnings` (advisory) lists.
If any fatal errors: emit `[ALTO]` per `[TASK §2.4]`. Do not proceed with
RAG indexing or deployment until resolved.

---

## 4. Inicialización de Manifiestos (Primera vez)

If a manifest does not exist yet, initialize it before adding entries:

```bash
python scripts/manifest_updater.py --operation init --plane agent
python scripts/manifest_updater.py --operation init --plane catalogo
python scripts/manifest_updater.py --operation init --plane package \
  --project-name [nombre]
```

This creates the manifest with the correct schema and empty `components: []`.

---

## 5. Script de Soporte

### `manifest_updater.py`

Full manifest management script. All operations are atomic — the file is
read, modified in memory, validated, then written. Partial writes are not possible.

```bash
# Initialize a new manifest
python scripts/manifest_updater.py --operation init \
  --plane agent|catalogo|package \
  [--project-name NAME]          # required for package plane

# Add a new component
python scripts/manifest_updater.py --operation add \
  --plane agent|catalogo|package \
  --component '<json>'

# Update an existing component
python scripts/manifest_updater.py --operation update \
  --plane agent|catalogo|package \
  --component '<json with name field>'

# Deprecate a component
python scripts/manifest_updater.py --operation deprecate \
  --plane agent|catalogo \
  --name component-name

# Check active dependents of a component
python scripts/manifest_updater.py --operation check-dependents \
  --plane agent|catalogo \
  --name component-name

# Validate one or all manifests
python scripts/manifest_updater.py --operation validate \
  --plane agent|catalogo|package|all

# Preview changes without writing (safe inspection)
python scripts/manifest_updater.py --operation add|update|deprecate \
  [args] --dry-run

# Exit codes:
# 0 — Operation successful
# 1 — Component not found
# 2 — Duplicate name detected
# 3 — Schema validation failed
# 4 — Path does not exist on filesystem
# 5 — Active dependents block deprecation
# 6 — Circular dependency detected
# 7 — Manifest file not found (run --operation init first)
```

---

## 6. Referencia Rápida (Load on Demand)

- `references/schema_reference.md` — complete schema with all field definitions,
  valid values, and examples for each manifest type
- `assets/templates/agent_manifest.json` — empty initialized Core manifest
- `assets/templates/catalogo_manifest.json` — empty initialized Catálogo manifest
- `assets/templates/package_manifest.json` — empty initialized package manifest
