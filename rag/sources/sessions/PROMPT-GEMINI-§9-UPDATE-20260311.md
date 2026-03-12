# Prompt para Actualización § 9 GEMINI.md: Ciclo Completo RAG (Éxitos + Fracasos)

**Contexto**: La especificación actual de RAG (§9) documenta solo el flujo de **éxito** (Paso 7 → indexar skill activo). Omite cómo se documentan, indexan y recuperan **fracasos, problemas, investigaciones y soluciones experimentadas** — componentes críticos para que el framework sea **autocorrector** y evite repetir errores.

**Caso de estudio concreto**: Sesión ghl-list-calendars (11 marzo 2026):
- Paso 5 enfrentó 5+ intentos fallidos (endpoints 404/403)
- Cada intento fue documentado en AUDIT-OPTION-B-ghl-list-calendars-20260311.md
- La solución final (query parameter locationId) debe estar **recuperable** por rag-query para futuras consultas sobre "errores 403 en GHL"
- **Hoy**: AUDIT-*.md se guardan en ./rag/sources/sessions/ pero GEMINI.md §9 **no explica** que esto es fuente crítica de RAG

---

## ESPECIFICACIÓN TÉCNICA: Lo que debe cambiar en GEMINI.md § 9

### 1. SECCIÓN § 9.0: Introducción (Nueva)

**Título**: "RAG — Recuperación Aumentada: Documentación de Éxitos Y Fracasos"

**Contenido requerido**:
- RAG no es solo para **encontrar componentes activos** (hoy)
- RAG es **repositorio de aprendizaje colectivo**: soluciones experimentadas, errores resueltos, decisiones justificadas
- Dos tipos de información se indexan:
  1. **PROYECTO-DOCS** — Componentes listos (SKILL.md, AGENT.md, README.md)
  2. **DECISIONES-ARQ** — El camino para llegar a esos componentes (AUDIT-*.md, decisiones, lecciones)
- **Propósito**: Cuando el usuario próximo enfrentt problema similar → rag-query retorna solución preexistente

**Ejemplo a incluir**:
```
Escenario: Usuario B intenta integrar GHL calendarios (3 meses después).
Hace: "¿Cómo consulto los calendarios de una ubicación en GHL?"

Resultado hoy:
  → rag-query retorna ghl-list-calendars/SKILL.md (instrucciones de uso)

Resultado esperado (con AUDIT indexado):
  → rag-query retorna:
    1. SKILL.md (qué hacer)
    2. AUDIT-OPTION-B-ghl-list-calendars-20260311.md (cómo se resolvió endpoint 403)
    3. Los 5 intentos fallidos documentados (por qué NO /calendar, NO /teams/{id}/calendars, etc.)
```

---

### 2. SECCIÓN § 9.1: Principios de Activación (Revisado)

**Cambio**: Agregar filas a tabla "Condición | Acción RAG"

Agregar estas filas:
```
| Un Paso FALLA durante DYNAMICS (créación de skill) | Genera AUDIT-{componente}-PROBLEMA.md con análisis raíz, soluciones experimentadas, bloqueador o workaround |
| Usuario consulta sobre problema previo (e.g., "error 403 GHL") | rag-query busca AUDIT-*.md que documente ese error + solución |
| Se completa exitosamente un Paso 7 (deployment) | (a) Indexa SKILL.md/AGENT.md en proyecto-docs, (b) Indexa AUDIT-*.md en decisiones-arq |
```

**Nota adicional a incluir**:
"Un componente SIN AUDIT asociado está incompleto desde perspectiva de documentación colectiva. Incluso skills exitosos requieren AUDIT que explique decisiones, alternativas consideradas, y lecciones."

---

### 3. SECCIÓN § 9.2: Capa 1 — Índice Local ChromaDB (Revisado Completo)

**Subsección 9.2.1 — Colecciones (Reescribir completamente)**

Reemplazar tabla actual:
```
| Colección | Contenido | Cuándo se actualiza |
| proyecto-docs | SKILL.md, AGENT.md, README.md | Paso 7 exitoso |
| decisiones-arq | ADRs, sesiones, manifest snapshots | Manual |
```

Por esta estructura: **SER EXHAUSTIVO — INCLUIR TODA LA INFORMACIÓN QUE HOY FALTA**:

#### Colección: `proyecto-docs`

**Propósito**: Documentación funcional de componentes **deployados exitosamente** (status: active)

**Fuentes directas**:
```
./.agent/skills/*/SKILL.md
./.agent/skills/*/README.md
./.agent/agents/*/AGENT.md
./.agent/agents/*/README.md
./catalogo/skills/*/SKILL.md
./catalogo/skills/*/README.md
./catalogo/agentes/*/AGENT.md
./catalogo/agentes/*/README.md
./AGENTS.md (global skills registry)
```

**¿Qué EXACTAMENTE se extrae de cada documento?**

Para cada SKILL.md:
- YAML frontmatter completo (name, version, triggers, inputs, outputs, dependencies, type, tier)
- Secciones H2 por separado (Quick Start = chunk 1, API Details = chunk 2, Troubleshooting = chunk 3)
- Ejemplos de ejecución
- Links a README.md asociado

**Estrategia chunk**:
- Unidad = H2/H3 section
- Chunk size: 512 tokens
- Overlap: 64 tokens
- Metadata de chunk: {source_file, skill_name, version, section_header}

**Caso de estudio**: ghl-list-calendars/SKILL.md se indexó como:
```
Chunk 001: YAML frontmatter
  Metadata: {skill: "ghl-list-calendars", version: "1.0.0", type: "integration"}
  Content: name, triggers, inputs/outputs schema
  Vector embedding: <resultado de all-MiniLM-L6-v2>

Chunk 002: "Quick Start — GHL v2 APIs"
  Metadata: {section: "quick-start", skill: "ghl-list-calendars"}
  Content: Instrucciones de instalación y primer uso
  
Chunk 003: "Endpoint Specification — GET /calendars"
  Metadata: {section: "api-spec", skill: "ghl-list-calendars"}
  Content: Endpoint format, query parameters (locationId), response schema
  
Chunk 004: "Troubleshooting: HTTP 403, 404, 401"
  Metadata: {section: "troubleshooting", skill: "ghl-list-calendars"}
  Content: Diagnóstico de errores y soluciones rápidas
```

#### Colección: `decisiones-arq` (Reescribir con énfasis)

**Propósito**: Documentación del PROCESO de creación de componentes (decisiones, investigaciones, soluciones, lecciones, fracasos resueltos)

**Fuentes directas**:
```
./rag/sources/adrs/*.md                  (Architectural Decision Records)
./rag/sources/sessions/AUDIT-*.md        (Post-deployment audits + problema logs)
./rag/sources/sessions/MEMORY-*.md       (Session-specific learnings)
Snapshots de ./catalogo/manifest.json    (Dependencias entre componentes)
```

**¿Qué EXACTAMENTE contiene un AUDIT-*.md indexable?**

**Estructura RECOMENDADA** (debe documentarse en GEMINI.md):

```markdown
# AUDIT-{skill-name}-{timestamp}.md

## Metadatos
- Skill forjado: {name} v{version}
- Pasos ejecutados: 0-7 (o cuál falló)
- Status final: exitoso | fracaso | parcial
- Timestamp: ISO timestamp
- Flujo: DYNAMICS normal | Opción B | otro

## Resumen ejecutivo
{2-3 líneas describiendo qué se logró y principales blockers/lecciones}

## Paso 0: Discovery
- ¿Qué información se buscó en RAG?
- ¿Qué se encontró?
- Decisión: continuar / ajustar

## Paso 1: Search (Externa)
- Búsquedas realizadas (GitHub, npm, etc.)
- Hallazgos: skillls preexistentes / soluciones similares
- Decisión: reusar pattern / crear nueva

## Paso 2: Design
- Pattern seleccionado
- Justificación (por qué este y no otro)
- Alternativas consideradas y rechazadas

## Paso 3: Construction
- Archivos creados (SKILL.md, README.md, scripts)
- Decisiones de implementación (librerías, error handling)
- Problemas encontrados en coding

## Paso 4: External Audit
- Validación YAML/JSON
- Code review hallazgos
- Dependencias verificadas

## Paso 5: Refinement
- [CRÍTICO] Qué no funcionó en tests iniciales
- Root cause analysis
- Soluciones experimentadas (intentos 1, 2, 3...)
- Solución final implementada
- Alternativas descartadas y por qué

## Paso 6: Finalization
- Registración en manifest
- Status asignado (draft / active)
- Enlaces a recursos relacionados

## Paso 7: Deployment
- Test commands ejecutados
- Output esperado vs actual
- Validación de exit codes

## Lecciones Aprendidas
- Qué funcionó bien
- Qué debería cambiar en futuros intentos
- Patrones reutilizables identificados

## Blockers No Resueltos (si aplica)
- Problema pendiente
- Impacto
- Próximos pasos sugeridos
```

**Caso de estudio: ghl-list-calendars AUDIT**

Este AUDIT debe indexarse como:
```
Documento: AUDIT-OPTION-B-ghl-list-calendars-20260311.md

Chunks generados:
Chunk 001: Metadatos + Resumen ejecutivo
  Metadata: {type: "audit", skill: "ghl-list-calendars", status: "success"}
  
Chunk 002: Pasos 0-3 (discovery, search, design, construction)
  Metadata: {section: "early-steps", pasos: "0-3"}
  
Chunk 003: Paso 5 — REFINEMENT (Crítico: endpoint discovery)
  Metadata: {section: "refinement", pasos: "5", problema: "HTTP 403/404"}
  Content:
    - Intentos fallidos:
      1. GET /calendars → 404
      2. GET /calendar-appointments → 404
      3. GET /locations/{id}/calendars → 404
      4. GET /calendars?locationId=... (headers incorrectos) → 403
      5. GET /calendars?locationId=... (formato query correcto) → 200 ✓
    - Root cause: GHL API v2 endpoint requiere locationId como query parameter, no headers
    - Solución: urllib.parse.urlencode({"locationId": location_id})
    - Aprendizaje: GHL API v2 documentation sparse; endpoint discovery by trial

Chunk 004: Pasos 6-7 (finalization, deployment) + Lecciones
  Metadata: {section: "post-deployment", pasos: "6-7"}
  Content: Deployment exitoso, output format optimization, future enhancements
```

**Estrategia chunk para AUDIT**:
- Unidad = Documento **COMPLETO** (no split por H2, excepto Paso 5 si es muy largo)
- Chunk size: 1024 tokens
- Overlap: 128 tokens
- Metadata crítica: {tipo: "AUDIT", skill: {name}, status: {exitoso/fracaso}, paso_crítico: {5}}

---

### 4. SECCIÓN § 9.2.2: Cuándo se Actualiza el Índice (Nueva subsección)

**Tabla nueva**:

| Evento | Quién dispara | Colección afectada | Qué se indexa |
|--------|---|---|---|
| Paso 7 exitoso: skill nuevo desplegado | `rag-indexer` (automático) | `proyecto-docs` | SKILL.md, README.md del componente activo |
| Cualquier Paso falla o enfrenta problema | Usuario + Auditor | `decisiones-arq` | AUDIT-{skill}-{timestamp}.md con análisis raíz |
| Paso 7 exitoso completado | `rag-indexer` (automático) | `decisiones-arq` | AUDIT associate al Paso 7 (incluye Pasos 0-7) |
| Usuario identifica solución a problema viejo | Manual trigger | `decisiones-arq` | RESOLUTION-{problema}-{fecha}.md con aprendizaje |
| Cambios en dependencias (manifest.json) | Manual trigger | `decisiones-arq` | Snapshot de manifest con cambios explicados |

**Nota**: "Incluso deployments exitosos generan AUDIT. El AUDIT de éxito documenta por qué se eligió este patrón, qué alternativas se consideraron, y qué lecciones extraer."

---

### 5. SECCIÓN § 9.2.3: Captura de Información durante DYNAMICS (Nueva subsección)

**Contexto**: Hoy GEMINI.md §7.2 (DYNAMICS) describe 7 Pasos pero **no explica** qué registrar en cada uno para RAG.

**Agregar tabla vinculada**:

```
Paso DYNAMICS | Información a registrar en AUDIT | Quién documenta | Momento |
0 — Discovery | Búsqueda RAG realizada + hallazgos | Auditor | Durante ejecución |
1 — Search | Búsquedas externas + hllazgos | Auditor | Durante ejecución |
2 — Design | Decision sobre pattern, alternativas consideradas | Auditor | Antes de construcción |
3 — Construction | Archivos creados, decisiones impl., problemas encontrados | Dev | Después de construction |
4 — Audit | Validaciones realizadas, hallazgos | Auditor | Después de validación |
5 — Refinement | [CRÍTICO] Problemas identificados en tests, soluciones experimentadas, raíz de fallos, solución final | Dev + Auditor | Mientras se troubleshoota |
6 — Finalization | Registro en manifest, status asignado | Publisher | Antes de Paso 7 |
7 — Deployment | Tests ejecutados, output, validación final, next steps | Dev | Después de ejecución |
```

---

### 6. SECCIÓN § 9.3: Consulta de Información mediante rag-query (Revisado)

**Agregar ejemplos prácticos** (hoy la sección es demasiado abstracta):

#### Ejemplo 1: Búsqueda "¿Cómo hacer X?"
```
Query: "¿Cómo listo los calendarios disponibles en mi cuenta de GHL?"

rag-query:
  1. Ingesta query → embedding via all-MiniLM-L6-v2
  2. Búsqueda vectorial en proyecto-docs + decisiones-arq
  3. Top 5 resultados con score > 0.7:
     - SKILL.md ghl-list-calendars → Chunk "Endpoint Specification" (score 0.92)
     - SKILL.md ghl-list-calendars → Chunk "Quick Start" (score 0.88)
     - README.md ghl-list-calendars (score 0.81)
     - AUDIT-OPTION-B-ghl-list-calendars → Chunk "Solución endpoint" (score 0.78)
     - AGENT.md ghl-integration (score 0.75)
  
  Contexto inyectado al modelo: 
    Union de estos chunks → prompt expansion con solución probada

Modelo responde con:
  "Usa skill ghl-list-calendars con locationId={tu-location-id}. 
   Si recibes error 403, asegúrate que... [información del AUDIT]"
```

#### Ejemplo 2: Búsqueda "¿Cómo resolvi X cuando falló?"
```
Query: "me da error 403 cuando llamo a la API de calendarios de GHL, ¿cómo se resuelve?"

rag-query:
  1. Búsqueda vectorial en decisiones-arq (preferencia)
  2. Top resultados:
     - AUDIT-OPTION-B-ghl-list-calendars → Paso 5 "HTTP 403 error analysis" (score 0.95)
     - AUDIT-ghl-list-ai-agents → Paso referido (score 0.72)
  
  Contexto inyectado:
    "Se identificó que error 403 al consultar calendarios ocurre cuando...
     La solución fue usar query parameter locationId en formato...
     5 intentos fallidos anteriores: 1) path parameter, 2) header, 3) ..., 4) header variable"

Modelo responde con la solución exacta + contexto de por qué falló
```

**Nota importante a agregar**: "rag-query prefiere resultados de decisiones-arq cuando la búsqueda contiene palabras clave de problemas (error, falla, no funciona, 403). Esto asegura que se retorna no solo qué hacer sino POR QUÉ y QUÉ NO hace falta."

---

### 7. SECCIÓN § 9.4: Ciclo de Vida Completo de un Componente en RAG (Nueva)

**Agregar flowchart/tabla visualizando**:

```
CREATION PHASE:
  Paso 0-5 → Problemas encontrados, soluciones experimentadas
            → Se registra en AUDIT con análisis detallado
            → [Si falla] AUDIT marca status: "fracaso" + bloqueador

DEPLOYMENT PHASE:
  Paso 6-7 → Si ÉXITO:
               - SKILL.md indexado en proyecto-docs
               - AUDIT completo indexado en decisiones-arq
               - Manifest actualizado
               - Next: rag-indexer re-indexa todo
            
            → Si FRACASO:
               - AUDIT generado con root cause
               - Status: draft (no se publica a catalogo)
               - Disponible en decisiones-arq para análisis futuro

OPERATIONAL PHASE (Meses después):
  Usuario nuevo enfrenta problema similar
  → rag-query retorna AUDIT de sesión anterior
  → Problema resuelto 70% más rápido (porque solución preexiste)
```

---

## VALIDACIÓN E IMPLEMENTACIÓN

### Checklist para modelo ejecutor:

**Lectura previa** (antes de editar GEMINI.md):
- [ ] Leer GEMINI.md §9 actual completo
- [ ] Revisar structure of SKILL.md (ref: ghl-list-calendars/SKILL.md)
- [ ] Revisar structure of AUDIT-*.md (ref: AUDIT-OPTION-B-ghl-list-calendars-20260311.md)
- [ ] Entender ChromaDB y sentence-transformers basics

**Edición**:
- [ ] Crear §9.0 (Introducción) con ejemplo ghl-list-calendars
- [ ] Reescribir §9.1 (Principios) con nuevas filas en tabla
- [ ] Reescribir §9.2.1 (Colecciones) con estructura exhaustiva de "qué se extrae" de cada file
- [ ] Agregar §9.2.2 (Cuándo actualiza el índice)
- [ ] Agregar §9.2.3 (Captura de información durante DYNAMICS)
- [ ] Reescribir §9.3 (rag-query) con 2+ ejemplos concretos
- [ ] Agregar §9.4 (Ciclo de vida completo)

**Validación**:
- [ ] Verificar que cada sección referencia ejemplos concretos (ghl-list-calendars, AUDIT-OPTION-B)
- [ ] Asegurar que tabla "Cuándo se actualiza" es exhaustiva (éxitos, fracasos, resoluciones)
- [ ] Confirmar que rag-query examples son **realistas** (qué retornaría hoy vs. qué debería retornar)
- [ ] Revisar que notas sobre "componentes sin AUDIT están incompletos" está clara
- [ ] Cross-check: ¿está claro que DECISIONES-ARQ es **tan importante como** PROYECTO-DOCS?

**Testing conceptual**:
- [ ] ¿Un usuario leyendo §9 nuevo entiende que FRACASOS son documentables?
- [ ] ¿Está claro que AUDIT-*.md es fuente de RAG, no solo "audit trail"?
- [ ] ¿Alguien forjando una skill nueva sabe QUÉ registrar para RAG?

---

## NOTAS FINALES

1. **Tono**: Mantener tono de GEMINI.md (técnico, pragmático, ejemplos concretos)
2. **Idioma**: Español (títulos) + snippets en código/inglés donde corresponde
3. **Longitud esperada**: §9 debería crecer de ~1000 palabras a ~2500-3000 palabras
4. **Consistency**: Asegurar que referencias a §7.2 DYNAMICS, manifest, colors (✅ éxito, ⚠️ fracaso) sean consistentes
5. **Backward compatibility**: Cambios son extensivos (agregan información), no rompen lo existente

---

## ENTREGA

Documento actualizado de GEMINI.md (§9 completo reescrito) listo para commit a repositorio.

