---
name: ghl-list-ai-agents
description: Utiliza la API v2 de GoHighLevel para listar los Agentes de Conversation AI asociados a una ubicación.
---

# GoHighLevel: List Conversation AI Agents Skill

## Usage Context

Use this skill when the user requests to list, audit, search, or verify available Conversation AI agents or Agent Studio profiles within their GoHighLevel (GHL) account.

## Technical Context and Rules (GHL API v2)

1. **Strategic Endpoint**: The agent MUST always use the `GET` method targeting `https://services.leadconnectorhq.com/conversation-ai/agents/search`.
2. **Query Parameters**: NONE. The `locationId` MUST NOT be sent in the URL, as it is automatically inferred from the Access Token. Sending a payload will cause the request to fail (422/Timeout).
3. **Strict Headers**:
   - `Authorization: Bearer <GHL_API_KEY>`
   - `Version: 2021-04-15`
   - `Accept: application/json`

## Execution Protocol

The agent only needs to execute the provided Python script to interact with the API.

**Plug & Play Strategy (Automatic .env):**
If credentials are not configured, the script will **automatically search for or generate a `.env` template** in the forge root `.agent/.env`. The script will halt execution with `Exit Code 1` and explicitly request the operator to fill in the required keys. Do not force the operator to use manual `export` commands.

Execution command:

```bash
python .agent/catalog/skills/ghl-list-ai-agents/scripts/fetch_ai_agents.py
```
