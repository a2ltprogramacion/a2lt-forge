---
name: ghl-list-calendars
description: Utiliza la API v2 de GoHighLevel para listar los calendarios asociados a una ubicación específica.
---

# GoHighLevel: List Calendars Skill

## Usage Context

Use this skill when the user requests to list, view, search, or audit available calendars within their GoHighLevel (GHL) account.

## Technical Context and Rules (GHL API v2)

1. **Strategic Endpoint**: The agent MUST always use the `GET` method targeting `https://services.leadconnectorhq.com/calendars/`.
2. **Query Parameters**: `locationId` is mandatory and must be sent as a query parameter (`?locationId=...`).
3. **Strict Headers**:
   - `Authorization: Bearer <GHL_API_KEY>`
   - `Version: 2021-04-15`
   - `Accept: application/json`

## Execution Protocol

The agent only needs to execute the provided Python script to interact with the API.

**Plug & Play Strategy (Automatic .env):**
If credentials are not configured, the script will **automatically search for or generate a `.env` template** in the forge root `.agent/.env`. The script will halt execution with `Exit Code 1` and explicitly request the operator to fill in the required data. Do not force the operator to use manual `export` commands.

Execution command:

```bash
python .agent/catalog/skills/ghl-list-calendars/scripts/fetch_calendars.py
```
