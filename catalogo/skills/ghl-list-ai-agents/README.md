# ghl-list-ai-agents

**GoHighLevel Conversation AI Agents Inventory Skill**

## Quick Reference

Retrieves all Conversation AI agents from a GoHighLevel account via API v2.

- **Version**: 1.0.0
- **Status**: Production
- **Type**: Integration (external API gateway)
- **Execution**: `python catalogo/skills/ghl-list-ai-agents/scripts/fetch_ai_agents.py`

## Setup

1. Ensure `.env` has:
   ```
   GHL_API_KEY=<your-key>
   GHL_LOCATION_ID=<your-id>
   ```

2. Run:
   ```bash
   cd catalogo/skills/ghl-list-ai-agents
   pip install python-dotenv>=1.0.0
   python scripts/fetch_ai_agents.py
   ```

## Output Example

```
✓ Connection successful. Agents for location abc123:

1. Sales Qualification Bot
   ID: agent-xyz | Mode: hybrid
   Channels: sms, email | Sleep Mode: No

2. Customer Support Escalation
   ID: agent-qwe | Mode: agentic
   Channels: email, voice | Sleep Mode: Yes
```

## Integration

- Can be used in custom orchestration workflows
- Results can be indexed by `rag-indexer` for later queries
- Part of production Catálogo (user-facing skills)

See [SKILL.md](SKILL.md) for complete technical documentation.
