# ghl-list-ai-agents

**GoHighLevel Conversation AI Agents Inventory Skill**

## Quick Reference

Retrieves all Conversation AI agents from a GoHighLevel account via API v2.

- **Version**: 1.0.0
- **Status**: Production
- **Type**: Integration (external API gateway)
- **Execution**: `python .agent/skills/ghl-list-ai-agents/scripts/fetch_ai_agents.py`

## Setup

1. Ensure `.env` has:
   ```
   GHL_API_KEY=<your-key>
   GHL_LOCATION_ID=<your-id>
   ```

2. Run:
   ```bash
   cd .agent/skills/ghl-list-ai-agents
   pip install python-dotenv>=1.0.0
   python scripts/fetch_ai_agents.py
   ```

## Output Example

```
Connection Successful. Evaluating Conversation AI configuration for location abc123:

[-] Agent: Sales Qualification Bot
    ID: agent-xyz | Mode: hybrid
    Canales: sms, email | Sleep Mode: No

[-] Agent: Customer Support Escalation
    ID: agent-qwe | Mode: agentic
    Canales: email, voice | Sleep Mode: Yes
```

## Integration

- Used by `agent-creator-pro` (Paso 0 Discovery)
- Feeds agent metadata into orchestration workflows
- Results can be indexed by `rag-indexer` for later queries

See [SKILL.md](SKILL.md) for complete technical documentation.
