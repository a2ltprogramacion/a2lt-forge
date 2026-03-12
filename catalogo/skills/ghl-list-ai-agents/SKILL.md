---
name: ghl-list-ai-agents
version: 1.0.0
type: integration
tier: production
description: Retrieves list of Conversation AI agents from a GoHighLevel account using GHL API v2 gateway. Primary use case is auditing agent configurations, verifying active deployments, and collecting agent metadata for orchestration decisions.
triggers:
  primary:
    - "ghl-list-ai-agents"
    - "list ghl agents"
    - "busca agentes ghl"
    - "audit conversation ai"
    - "qué agentes tengo"
  secondary:
    - "ghl agents"
    - "agentes ia"
    - "conversation ai inventory"
inputs:
  - name: location_id
    type: string
    required: false
    description: GoHighLevel location ID (auto-loaded from GHL_LOCATION_ID env var if not provided)
  - name: output_format
    type: string
    required: false
    default: "text"
    description: Output format - 'text' (human readable) or 'json' (machine readable)
outputs:
  - name: agents_list
    type: list[dict]
    description: Array of agent objects with id, name, mode, channels, sleepEnabled status
  - name: summary
    type: dict
    description: Metadata object with count, location_id, timestamp, execution_status
  - name: errors
    type: string
    description: Human-readable error message if execution fails
dependencies:
  - name: python-dotenv
    version: ">=1.0.0"
    reason: "Load GHL_API_KEY and GHL_LOCATION_ID from .env"
  - name: urllib3
    version: ">=1.26.0"
    reason: "HTTP client for GHL API v2 requests (built-in, but optional for performance)"
trigger_conditions:
  environment: ["GHL_API_KEY", "GHL_LOCATION_ID"]
  external_dependencies: ["GoHighLevel API v2 (https://services.leadconnectorhq.com)"]
execution_model: "synchronous"
framework_version: ">=2.3.0"
notes: "Integration skill for GoHighLevel Conversation AI. Critical for multi-agent orchestration workflows where agent inventory lookup is a prerequisite. Version 1.0 supports read-only operations."
---

# GoHighLevel: List Conversation AI Agents

## Overview

Fetches and inventories all Conversation AI agents deployed in a GoHighLevel account. This skill is essential for:
- **Agent Auditing**: Verify active AI agent configurations
- **Orchestration**: Discover available agents before delegating tasks
- **Compliance**: Track agent deployment status and channel associations
- **Integration**: Feed agent metadata into Forja agent creation workflows

## Quick Start

```bash
python catalogo/skills/ghl-list-ai-agents/scripts/fetch_ai_agents.py
```

**Prerequisites:**
- `GHL_API_KEY` and `GHL_LOCATION_ID` configured in `.env` (root directory)
- Python 3.10+
- Network access to `https://services.leadconnectorhq.com`

## Technical Context

### API Behavior (GHL v2)

- **Endpoint**: `GET https://services.leadconnectorhq.com/conversation-ai/agents/search`
- **LocationId Inference**: Auto-inferred from Bearer token — **NEVER include in URL params** (causes 422/Timeout)
- **Response Groups**: Agents returned under `agents` key (or fallback to `data` key)
- **Required Headers**:
  - `Authorization: Bearer <GHL_API_KEY>`
  - `Version: 2021-04-15`
  - `Accept: application/json`

### Agent Object Schema

Each agent in the response includes:
```json
{
  "id": "agent-123abc",
  "name": "Sales Qualification Bot",
  "mode": "hybrid|agentic|templated",
  "channels": ["sms", "email", "voice"],
  "sleepEnabled": true,
  "customFields": {...}
}
```

## Execution Protocol

### Plug & Play Credential Loading

If credentials are missing, the script:
1. Auto-generates `.env` template (if missing)
2. Exits gracefully with Exit Code 1
3. Displays clear instruction for operator to fill in `GHL_API_KEY` and `GHL_LOCATION_ID`
4. Does NOT require manual `export` commands

### Exit Codes

- `0` – Success (agents found or list empty)
- `1` – Missing credentials/configuration
- `2` – HTTP Error (API communication failure)
- `3` – System error (unexpected exception)

## Integration Points

**Upstream (Triggers this skill):**
- User requests to audit/list agents
- Custom orchestration workflows

**Downstream (Uses outputs of this skill):**
- `rag-indexer` (optional: indexes agent metadata for later queries)
- Custom workflows that depend on agent inventory

## Optimization Notes (v1.0.0)

- Uses `urllib` (stdlib) instead of `requests` — zero heavy dependencies
- Handles GHL API quirks (locationId inference, variable response formats)
- Supports both dict and list response formats for robustness
- Auto-fallback for missing agent fields (graceful degradation)

## Troubleshooting

| Symptom | Cause | Solution |
|---------|-------|----------|
| `Exit Code 1` | Missing credentials | Fill `.env` with `GHL_API_KEY` and `GHL_LOCATION_ID` |
| `Exit Code 2 (422)` | LocationId in URL params | Verify script doesn't send params (it shouldn't) |
| `Exit Code 2 (401)` | Invalid API key | Check `GHL_API_KEY` format and permissions |
| `Connection failed` | Network isolation | Verify firewall allows `services.leadconnectorhq.com` access |
| `No agents found` | Location has no AI agents | Normal if location doesn't have Conversation AI enabled |

## Future Enhancements

- [ ] Pagination support for accounts with 100+ agents
- [ ] Filter agents by mode, channel, or custom field values
- [ ] Bulk agent configuration export (to/from CSV)
- [ ] Real-time agent status monitoring (health checks)
