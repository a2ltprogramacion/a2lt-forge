# Schema Reference — manifest-updater
# Load when you need field definitions, valid values, or examples.

## Estructura raíz del manifiesto

```json
{
  "schema_version": "1.0.0",
  "plane": "agent | catalogo | package",
  "last_updated": "2026-03-11T20:00:00Z",
  "components": []
}
```

| Campo | Tipo | Requerido | Descripción |
|---|---|---|---|
| `schema_version` | string | Sí | Versión del schema. Actualmente `"1.0.0"` |
| `plane` | string | Sí | Plano al que pertenece el manifiesto |
| `last_updated` | string | Sí | ISO 8601 UTC. Actualizado automáticamente por el script |
| `components` | array | Sí | Lista de entradas de componentes |

---

## Campos obligatorios por entrada

| Campo | Tipo | Valores válidos | Descripción |
|---|---|---|---|
| `name` | string | kebab-case, mín. 2 chars | Identificador único del componente en su plano |
| `version` | string | SemVer X.Y.Z | Versión del componente |
| `kind` | string | `skill` \| `agent` \| `workflow` | Tipo de componente |
| `status` | string | `active` \| `deprecated` \| `experimental` | Estado operativo |
| `path` | string | Ruta relativa desde raíz del proyecto | Directorio donde vive el componente |
| `dependencies` | array | Lista de objetos dep o `[]` | Dependencias declaradas. Vacío = `[]` |

---

## Campos opcionales por entrada

| Campo | Tipo | Valores válidos | Descripción |
|---|---|---|---|
| `type` | string | `backend` \| `frontend` \| `integration` \| `utility` | Dominio funcional |
| `tier` | string | `vcard` \| `authority` \| `enterprise` \| `all` | Tier de proyecto compatible |
| `compatibility` | string | `>=X.Y.Z` | Versión mínima del framework requerida |
| `description` | string | Texto libre, una línea, en inglés | Descripción corta para consumo del RAG |

---

## Estructura de una dependencia

```json
{
  "name": "skill-search",
  "version": ">=1.0.0",
  "optional": false
}
```

| Campo | Requerido | Descripción |
|---|---|---|
| `name` | Sí | Nombre del componente del que depende |
| `version` | No | Constraint de versión. Si omitido, cualquier versión es válida |
| `optional` | No | `false` por defecto. Si `true`, ausencia solo genera warning |

---

## Ejemplos completos

### Skill en plano agent (mínimo)

```json
{
  "name": "skill-search",
  "version": "1.0.0",
  "kind": "skill",
  "status": "active",
  "path": "./.agent/skills/skill-search",
  "dependencies": []
}
```

### Skill en plano agent (completo)

```json
{
  "name": "manifest-updater",
  "version": "1.0.0",
  "kind": "skill",
  "status": "active",
  "path": "./.agent/skills/manifest-updater",
  "dependencies": [],
  "type": "utility",
  "tier": "all",
  "compatibility": ">=2.3.0",
  "description": "Atomic management of La Forja manifest files."
}
```

### Agente en plano catalogo

```json
{
  "name": "web-analyst",
  "version": "2.1.0",
  "kind": "agent",
  "status": "active",
  "path": "./catalogo/agentes/web-analyst",
  "dependencies": [
    { "name": "skill-search", "version": ">=1.0.0", "optional": false },
    { "name": "brainstorming", "version": ">=1.0.0", "optional": true }
  ],
  "type": "frontend",
  "tier": "authority",
  "compatibility": ">=2.3.0",
  "description": "Analyzes competitor websites and generates UX improvement proposals."
}
```

### Componente deprecado

```json
{
  "name": "old-validator",
  "version": "0.9.0",
  "kind": "skill",
  "status": "deprecated",
  "path": "./.agent/skills/old-validator",
  "dependencies": []
}
```

---

## Los tres manifiestos — rutas canónicas

| Plano | Ruta | Inicializar con |
|---|---|---|
| Core / Infraestructura | `./.agent/manifest.json` | `--plane agent` |
| Catálogo / Cliente | `./catalogo/manifest.json` | `--plane catalogo` |
| Paquete de proyecto | `./output/[nombre]/package-manifest.json` | `--plane package --project-name [nombre]` |

---

## Reglas de SemVer para La Forja

| Cambio | Bump | Ejemplo |
|---|---|---|
| Nuevos scripts, breaking interface, cambio de inputs/outputs | MAJOR | `1.0.0 → 2.0.0` |
| Nuevos pasos, nuevos campos opcionales, mejoras backward-compatible | MINOR | `1.0.0 → 1.1.0` |
| Bug fix, corrección doc, refactor interno sin cambio de interfaz | PATCH | `1.0.0 → 1.0.1` |

---

## Status — comportamiento en el ecosistema

| Status | Health Check | RAG indexing | Consumible por agentes |
|---|---|---|---|
| `active` | ✅ Incluido | ✅ Indexado | ✅ Sí |
| `experimental` | ⚠ Warning | ✅ Indexado | ⚠ Solo con flag explícito |
| `deprecated` | ❌ Ignorado | ❌ Excluido | ❌ No |
