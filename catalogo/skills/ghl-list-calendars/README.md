# ghl-list-calendars

**GoHighLevel Calendars Inventory Skill**

## Quick Reference

Retrieves all calendars from a GoHighLevel account via API v2.

- **Version**: 1.0.0
- **Status**: Production
- **Type**: Integration (external API gateway)
- **Execution**: `python catalogo/skills/ghl-list-calendars/scripts/list_calendars.py`

## Setup

1. Ensure `.env` has:
   ```
   GHL_API_KEY=<your-key>
   GHL_LOCATION_ID=<your-id>
   ```

2. Run:
   ```bash
   cd catalogo/skills/ghl-list-calendars
   pip install python-dotenv>=1.0.0
   python scripts/list_calendars.py
   ```

## Output Example

```
✓ Connection successful. Calendars for location abc123:

1. Sales Team Calendar
   ID: cal-xyz | Type: team
   Owner: sales-lead | Available: Yes | Timezone: America/New_York

2. Personal Schedule
   ID: cal-qwe | Type: personal
   Owner: user1 | Available: Yes | Timezone: EST

3. Holiday Calendar
   ID: cal-asd | Type: shared
   Owner: admin | Available: Yes | Timezone: UTC
```

## Integration

- Used in scheduling automation workflows
- Results can be indexed by `rag-indexer` for later discovery
- Part of production Catálogo (user-facing skills)

See [SKILL.md](SKILL.md) for complete technical documentation.
