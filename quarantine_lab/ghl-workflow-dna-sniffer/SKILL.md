---
name: ghl-workflow-dna-sniffer
description: Recibe un location_id y un workflow_id. Aplica un modelo híbrido para extraer el JSON de forma masiva (Phase B). Si el token falta, usa browser_subagent para extraer el JWT de sesión (Phase A) y re-intenta.
---

# GHL DNA Sniffer — Hybrid Bulk Extractor (Phase A / Phase B)

## Arquitectura de Delegación de Carga

Para evitar colapsos por límite de tokens (Token Limit Exceeded) al procesar flujos masivos, esta skill utiliza un modelo dividido:

- **Phase A (browser_subagent):** Solo para capturar llaves de acceso cortas (JWT).
- **Phase B (Python Host):** Descarga rápida y masiva del JSON directo al disco.

## Input Contract

This skill ALWAYS receives two inputs from the orchestrating agent:

- `location_id`: The GHL subaccount ID.
- `workflow_id`: The ID of the workflow to extract.

## Execution Protocol (Agent Autonomous Action)

Para **cada** `workflow_id`, Antigravity MUST act as follows:

### Paso 1: Disparar el Motor Híbrido

Ejecutar el script principal:
`python .agent/catalog/skills/ghl-workflow-dna-sniffer/scripts/capture_dna.py {location_id} {workflow_id}`

### Paso 2: Análisis de Respuesta (Ramificación)

**Escenario 1: [SUCCESS] (Phase B Exitosa)**
Si el script reporta `[SUCCESS] DNA lógico extraído`, el ciclo ha terminado para ese flujo. Avanzar al siguiente.

**Escenario 2: [PHASE_A_REQUIRED] (Token faltante o expirado)**
Si el script falla pidiendo un token, Antigravity **DEBE** usar de inmediato el `browser_subagent` con esta misión exacta:

1. Navegar a: `https://{GHL_WL_DOMAIN}/location/{location_id}/workflow/{workflow_id}`
2. Interceptar peticiones a `backend.leadconnectorhq.com`
3. Capturar el string del Header `Authorization` (ej. `Bearer eyJhbG...`).
4. REPORTAR ÚNICAMENTE EL JWT en la respuesta final de texto (NO el payload JSON).
5. Editar el archivo `.agent/.env` y establecer `GHL_SESSION_TOKEN=eyJhbG...` (Omitir la palabra Bearer).
6. Repetir el Paso 1.

## Regla de Oro (Límite de Tokens)

**NUNCA**, bajo ninguna circunstancia, ordenes al `browser_subagent` reportar o imprimir el payload JSON completo del Workflow. Utiliza siempre el flujo Phase A / Phase B para forzar al script de Python a escribir el archivo directamente en `quarantine_lab`.
