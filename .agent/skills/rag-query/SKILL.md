---
name: rag-query
version: 1.0.0
type: utility
subtype: skill
tier: all
description: |
  Queries the local ChromaDB index for existing components, architectural decisions,
  and patterns within La Forja ecosystem. Primary tool for discovering if something
  already exists before forging new components. Use at Paso 0 of any forge flow.
  Trigger phrases: "busca en el índice", "qué tenemos de", "existe algo sobre",
  "search the index", "find existing pattern", "rag-query".
  Do NOT activate for web searches — use web-search for external information.
  Do NOT activate if the operator is using skill-search — that's for external repos.

triggers:
  primary: ["rag-query", "busca en índice", "qué tenemos", "search index"]
  secondary: ["existe algo sobre", "busca patrón", "find pattern", "existing component"]
  context: ["paso 0", "forge discovery", "antes de forjar", "prior to forge"]

inputs:
  - name: query
    type: string
    required: true
    description: Natural language question or component name to search
  - name: collection
    type: string
    required: false
    description: "Specific collection to search: proyecto-docs | decisiones-arq | all (default)"
  - name: top_k
    type: int
    required: false
    description: "Number of results to return. Default: 5. Max: 10"
  - name: min_score
    type: float
    required: false
    description: "Minimum relevance score (0.0-1.0). Default: 0.7"

outputs:
  - name: results
    type: list
    description: "List of chunks with source, relevance score, and excerpt"
  - name: no_results
    type: bool
    description: "True if min_score threshold not met in any collection"

dependencies: []
framework_version: ">=2.3.0"

notes: |
  [REVISIÓN REQUERIDA]
  Bootstrap skill created manually to resolve circular dependency.
  Once deployed, enable RAG-based discovery across ecosystem.
  Requires: ChromaDB installed, ./rag/index/ populated.
---

# RAG Query — Inteligencia Interna del Ecosistema

You are the **Knowledge Retriever** for La Forja. Your mission: find what already
exists in the ecosystem — skills, agents, patterns, decisions — before anyone
attempts to build it again.

A skill that can be absorbed from the internal catalog is always faster than forging new.

---

## 0. Regla de Oro

**El índice local es la primera parada.** Always query before searching external sources.
If local results have score ≥ 0.7, use them as intelligence input for brainstorming.
Only if local results are empty or low-scoring (< 0.7), activate skill-search.

---

## 1. Arquitectura de Índice

### Colecciones indexadas (./rag/config.yaml)

| Colección | Contenido | Granularidad |
|---|---|---|
| **proyecto-docs** | AGENTS.md, SKILL.md, AGENT.md, README.md del Core y Catálogo | Chunks de 512 tokens |
| **decisiones-arq** | ADRs, historial de sesiones, manifiestos | Chunks de 1024 tokens |

### Modelo de embeddings

- **Modelo:** `sentence-transformers/all-MiniLM-L6-v2`
- **Ventaja:** Open source, local, sin API keys
- **Velocidad:** ~50ms por query en máquina estándar

---

## 2. Flujo de Consulta

1. Recibe: `query` (natural language) + collection (optional) + parámetros
2. **Tokeniza** la query
3. **Genera embedding** usando modelo local
4. **Búsqueda semántica** contra collection(s) especificadas
5. **Filtra** resultados por min_score (default: 0.7)
6. **Retorna:** Top K resulta ordenados por relevancia + source + excerpt

### Ejemplo de consulta exitosa

```
Input:
  query: "validation YAML against schema"
  collection: "proyecto-docs"
  top_k: 3

Output:
  results: [
    {
      "source": "./.agent/skills/yaml-validator/SKILL.md",
      "score": 0.92,
      "excerpt": "Validates YAML files against JSON schema. Essential for component metadata validation (§3.4)."
    },
    {
      "source": "./AGENTS.md",
      "score": 0.85,
      "excerpt": "§3.4 Estándar de Metadatos de Componentes. Todo agente o skill — en ./.agent/ o ./catalogo/ — debe incluir metadatos YAML."
    }
  ]
  no_results: false
```

### Ejemplo de consulta sin resultados

```
Input:
  query: "some non-existent skill about quantum computing"

Output:
  results: []
  no_results: true
```

---

## 3. Integración con Dinámicas

### Paso 0 de cualquier flujo (§7.2, §7.3)

```
Operador: "Necesito una skill que valide emails"

rag-query (automático):
  → query: "email validation"
  → collection: "proyecto-docs"
  → Score 0.82: yaml-validator menciona "metadata validation"... no es email
  → Score 0.71: Catálogo vacío, no hay skill
  → no_results: true

Resultado: Activar skill-search → busca externos
           Si skill-search retorna nada → brainstorming → forja
```

---

## 4. Limpieza de Índice

**Política:** El índice se re-indexa automáticamente al desplegar componentes (Paso 7).
Si cambias un SKILL.md manualmente, el índice queda stale hasta el próximo despliegue.

Para reindexar manualmente:
```bash
python ./.agent/skills/rag-indexer/scripts/reindex.py --collection proyecto-docs
```

---

## 5. Rendimiento

| Escenario | Tiempo esperado |
|---|---|
| Query en índice con 100 documentos | < 100ms |
| Query con 0 resultados | < 100ms |
| Re-indexado completo (100+ items) | < 5 segundos |

---

## 6. Límites y Salvaguardas

- **No es búsqueda web.** Para información externa, usa `web-search`.
- **No es fuente de verdad.** El índice es ayuda al contexto. La fuente de verdad sigue siendo `manifest.json`.
- **Desactivar si índice corrupto:** Si ChromaDB falla, activar fallback a búsqueda manual en manifiestos.
