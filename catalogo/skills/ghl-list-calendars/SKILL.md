---
name: ghl-list-calendars
version: 1.0.0
type: integration
tier: production
description: Retrieves list of all calendars available in a GoHighLevel account using GHL API v2. Primary use case is calendar discovery, availability verification, and collecting calendar metadata for scheduling and automation workflows.
triggers:
  primary:
    - "ghl-list-calendars"
    - "list ghl calendars"
    - "busca calendarios ghl"
    - "calendar inventory"
    - "qué calendarios tengo"
  secondary:
    - "ghl calendars"
    - "calendarios disponibles"
    - "list all calendars"
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
  - name: calendars_list
    type: list[dict]
    description: Array of calendar objects with id, name, type, owner, availability status
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
trigger_conditions:
  environment: ["GHL_API_KEY", "GHL_LOCATION_ID"]
  external_dependencies: ["GoHighLevel API v2 (https://services.leadconnectorhq.com)"]
execution_model: "synchronous"
framework_version: ">=2.3.0"
notes: "Integration skill for GoHighLevel Calendar management. Enables discovery of available calendars for scheduling automation and availability checking. Version 1.0 supports read-only operations."
---

# GoHighLevel: List Calendars

## Overview

Fetches and inventories all calendars configured in a GoHighLevel account. This skill is essential for:
- **Calendar Discovery**: Identify all available calendars in the location
- **Scheduling**: Verify calendar availability before automation setup
- **Availability Checks**: Track calendar status and owner information
- **Integration**: Feed calendar metadata into scheduling and automation workflows

## Quick Start

```bash
python catalogo/skills/ghl-list-calendars/scripts/list_calendars.py
```

**Prerequisites:**
- `GHL_API_KEY` and `GHL_LOCATION_ID` configured in `.env` (root directory)
- Python 3.10+
- Network access to `https://services.leadconnectorhq.com`

## Technical Context

### API Behavior (GHL v2)

- **Endpoint**: `GET https://services.leadconnectorhq.com/calendars/`
- **Query Parameters**: `locationId` is MANDATORY and must be sent as query param (`?locationId=...`)
- **Response Groups**: Calendars returned under `calendars` key
- **Required Headers**:
  - `Authorization: Bearer <GHL_API_KEY>`
  - `Version: 2021-04-15`
  - `Accept: application/json`

### Calendar Object Schema

Each calendar in the GHL response includes:
```json
{
  "id": "cal-123abc",
  "name": "Sales Team Calendar",
  "timezone": "UTC"
}
```

*Note: GHL API v2 returns minimal metadata. Additional fields (type, owner, isAvailable) may be available through extended API calls.*

## Execution Protocol

### Plug & Play Credential Loading

If credentials are missing, the script:
1. Auto-generates `.env` template (if missing)
2. Exits gracefully with Exit Code 1
3. Displays clear instruction for operator to fill in `GHL_API_KEY` and `GHL_LOCATION_ID`
4. Does NOT require manual `export` commands

### Exit Codes

- `0` – Success (calendars found or list empty)
- `1` – Missing credentials/configuration
- `2` – HTTP Error (API communication failure)
- `3` – System error (unexpected exception)

## Integration Points

**Upstream (Triggers this skill):**
- User requests to audit/list calendars
- Scheduling automation workflows

**Downstream (Uses outputs of this skill):**
- `rag-indexer` (optional: indexes calendar metadata for queries)
- Custom scheduling workflows that depend on calendar inventory

## Optimization Notes (v1.0.0)

- Uses `urllib` (stdlib) instead of `requests` — zero heavy dependencies
- Handles GHL API quirks (variable response formats)
- Supports both dict and list response formats for robustness
- Auto-fallback for missing calendar fields (graceful degradation)

## Troubleshooting

| Symptom | Cause | Solution |
|---------|-------|----------|
| `Exit Code 1` | Missing credentials | Fill `.env` with `GHL_API_KEY` and `GHL_LOCATION_ID` |
| `Exit Code 2 (401)` | Invalid API key | Check `GHL_API_KEY` format and permissions |
| `Exit Code 2 (403)` | Insufficient permissions | Verify API key has calendar access permissions |
| `Connection failed` | Network isolation | Verify firewall allows `services.leadconnectorhq.com` access |
| `No calendars found` | Location has no calendars | Normal if location just created or calendars not yet configured |

## Future Enhancements

- [ ] Filter calendars by type, owner, or availability
- [ ] Timezone detection and normalization
- [ ] Calendar sharing status and permissions audit
- [ ] Bulk calendar export (to/from iCalendar format)
- [ ] Real-time calendar status monitoring
