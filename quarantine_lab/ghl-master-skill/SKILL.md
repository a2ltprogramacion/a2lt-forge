---
name: ghl-master-skill
version: 2.0.0
type: execution
subtype: skill
tier: enterprise
description: |
  Master Skill definitiva para GoHighLevel API 2.0. Reúne CRM, Pagos, Automatizaciones, 
  Contenido, SaaS, IA y Social Planner en un único componente robusto con 
  persistencia de tokens y control de ráfagas.

triggers:
  primary: ["ghl", "gohighlevel", "crm", "api 2.0"]
  secondary: ["pagos", "facturación", "workflow", "automatización", "saas", "social planner", "ai agent"]

inputs:
  - name: module
    type: string
    required: true
    description: "Módulo objetivo: contacts, calendars, conversations, opportunities, payments, automations, content, saas, ai, social, system"
  - name: action
    type: string
    required: true
    description: "Método a ejecutar dentro del módulo"
  - name: params
    type: object
    required: false
    description: "Argumentos para la función seleccionada"

outputs:
  - name: result
    type: object
    description: "Respuesta nativa de la API de GoHighLevel"

dependencies:
  - name: httpx
    version: ">=0.24.0"
  - name: python
    version: ">=3.10"

entrypoint: scripts/main.py
---

# GHL Master Skill — La Forja Core

Esta skill es el puente maestro entre La Forja y el ecosistema de GoHighLevel. 
Utiliza el estándar de seguridad OAuth 2.0 y permite la rotación automática de tokens.

## Módulos Integrados

1. **CRM & Finanzas**: 
   - Gestión integral de contactos, oportunidades y pipelines.
   - Procesamiento de pagos, facturas y suscripciones.
2. **Automatización & IA**:
   - Control de Workflows y Webhooks.
   ### Módulo 9: Inteligencia Artificial (AI)
   Integración con los motores de IA de GHL.

   | Acción | Trigger | Input | Output |
   | :--- | :--- | :--- | :--- |
   | `list_conversation_ai_agents` | "lista agentes ia conversación" | `location_id` | Lista de agentes de chat (ej. Anna, Atlas) |
   | `list_voice_ai_agents` | "lista agentes voz" | `location_id` | Lista de agentes de voz (Voice AI) |
   | `list_agent_studio_agents` | "lista agentes studio" | `location_id` | Lista de agentes personalizados (Agent Studio) |
   | `get_voice_ai_logs` | "historial voz" | `location_id` | Logs de llamadas procesadas por IA |
3. **Contenido & Digital**:
   - Social Planner para todas las plataformas.
   - Gestión de Embudos, Blogs y Formularios.
4. **SaaS & Infraestructura**:
   - Snapshot deployment y configuración SaaS.
   - Administración de usuarios y archivos permanentes.

## Uso Experto

```bash
# Ejemplo: Buscar contactos que coincidan con un email
python scripts/main.py --module contacts --action search_contacts --params '{"location_id": "LOC_ID", "email": "test@example.com"}'
```

> [!IMPORTANT]
> Requiere un archivo `auth_state.json` válido o variables de entorno `GHL_API_KEY` (PIT) o `GHL_CLIENT_ID/SECRET` (OAuth2).
