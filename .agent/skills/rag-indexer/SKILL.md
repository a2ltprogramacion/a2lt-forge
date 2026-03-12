---
name: rag-indexer
version: 1.0.0
type: utility
subtype: skill
tier: all
description: |
  Builds and updates the ChromaDB vector index for La Forja ecosystem.
  Scans defined sources (SKILL.md, AGENT.md, README.md, ADRs) and indexes them.
  Activate automatically at Paso 7 (post-deployment) of any successful forge flow.
  Manual activation: when you suspect the index is stale or after bulk imports.
  Trigger phrases: "reindex", "actualiza índice", "rebuild rag", "update embeddings".
  Do NOT activate continuously — index updates only on deployment or explicit request.

triggers:
  primary: ["reindex", "actualiza índice", "rebuild rag", "update embeddings"]
  secondary: ["rag-stale", "indexa", "popula índice"]
  context: ["paso 7", "forge shutdown", "post-deployment", "after deploy"]

inputs:
  - name: collections
    type: list
    required: false
    description: "Collections to rebuild: proyecto-docs | decisiones-arq | all (default)"
  - name: force_rebuild
    type: bool
    required: false
    description: "If true, deletes and rebuilds from scratch. Default: false (incremental)"

outputs:
  - name: indexed_count
    type: int
    description: "Number of documents indexed"
  - name: index_status
    type: string
    description: "success | partial | error"
  - name: timestamp
    type: string
    description: "ISO timestamp of indexing completion"

dependencies: []
framework_version: ">=2.3.0"

notes: |
  [REVISIÓN REQUERIDA]
  Bootstrap skill created manually to resolve circular dependency.
  Once deployed, enables automated RAG re-indexing on component deployments.
  Requires: ChromaDB installed, ./rag/config.yaml, ./rag/sources/ populated.
---

# RAG Indexer — Construcción del Índice Vectorial

You are the **Index Builder** for La Forja. Your mission: keep the local knowledge
base (ChromaDB) fresh and searchable. Every time a skill, agent, or architectural
decision is deployed, you update the index so rag-query can find it.

---

## 0. Axioma de Disponibilidad

**El índice está solo para ayudar.** Si falla, el ecosistema no se cae — sigue
funcionando con búsqueda manual en manifiestos. Pero si está disponible, debe estar actualizado.

---

## 1. Fuentes Indexables (./rag/config.yaml)

### Colección: proyecto-docs

**Contiene:** AGENTS.md + todos los SKILL.md, AGENT.md, README.md del Core y Catálogo

```
Directorios escaneados:
  - ./.agent/skills/*/SKILL.md
  - ./.agent/skills/*/README.md
  - ./.agent/agents/*/AGENT.md
  - ./.agent/agents/*/README.md
  - ./catalogo/skills/*/SKILL.md
  - ./catalogo/skills/*/README.md
  - ./catalogo/agentes/*/AGENT.md
  - ./catalogo/agentes/*/README.md
  - ./AGENTS.md
```

**Chunk strategy:** Markdown headers → uno chunk por sección (H2, H3)
**Chunk size:** 512 tokens con 64 tokens overlapping

### Colección: decisiones-arq

**Contiene:** ADRs, sesiones registradas, snapshots de manifiestos

```
Directorios escaneados:
  - ./rag/sources/adrs/*.md
  - ./rag/sources/sessions/*.md
```

**Chunk strategy:** Documento completo = un chunk
**Chunk size:** 1024 tokens con 128 tokens overlapping

---

## 2. Flujo de Indexación

### Indexación incremental (default)

```
1. Leer config.yaml
2. Para cada colección:
   a. Listar archivos en sources
   b. Calcular hash de cada archivo
   c. Comparar contra hashes en ChromaDB
   d. Solo procesar archivos modificados
3. Generar embeddings con sentence-transformers
4. Insertar/actualizar en ChromaDB
5. Actualizar metadatos (timestamp, recuento)
```

**Ventaja:** Rápido (solo deltas)
**Costo:** ~100ms por archivo nuevo

### Indexación forzada (--force-rebuild)

```
1. Eliminar índice existente
2. Re-crear colecciones vacías
3. Indexar TODO desde cero
4. Reconstruir metadatos
```

**Ventaja:** Garantiza consistencia después de corrupción
**Costo:** Lento (~5 segundos para 100+ docs)

---

## 3. Integración Automática (Paso 7)

Al completar Paso 7 de dinámicas (despliegue exitoso):

```python
# Pseudocode
deployment_success = validate_pre_deploy(component)
if deployment_success:
    backup_to_quarantine_lab()
    move_to_destination()  # ./.agent/ o ./catalogo/
    update_manifest()
    rag_indexer.run(collections=["proyecto-docs"])  # ← AQUÍ
    cleanup_quarantine_lab()
```

---

## 4. Rendimiento Esperado

| Escenario | Tiempo |
|---|---|
| Indexar 1 nuevo SKILL.md | ~500ms |
| Re-indexar 10 archivos | ~3 segundos |
| Rebuild completo (100+ docs) | ~5 segundos |
| Query post-indexación | < 100ms |

---

## 5. Fallback ante Fallo

Si rag-indexer falla en Paso 7:

```
[RAG-STALE] 
Componente desplegado exitosamente. Índice no actualizado.
Estado: Componente EN PRODUCCIÓN pero no discoverable vía rag-query.
Acción: Reintenta manualmente: python scripts/reindex.py --force-rebuild
```

El componente está OK. Solo falló el índice.

---

## 6. Mantenimiento

### Verificar integridad del índice

```bash
python scripts/reindex.py --validate
# Output: OK | CORRUPTED | STALE
```

### Limpiar índice obsoleto

```bash
python scripts/reindex.py --prune-deprecated
# Elimina referencias a componentes con status=deprecated
```

