---
name: ghl-list-workflows
description: Utiliza la API v2 de GoHighLevel para listar los Workflows y automatizaciones asociadas a una ubicación específica.
---

# GoHighLevel: List Workflows Skill

## Usage Context

Use this skill when the user requests to list, audit, search, or review Workflows (automations) available within their GoHighLevel (GHL) account.

## Technical Context and Rules (GHL API v2)

1. **Strategic Endpoint**: The agent MUST always use the `GET` method targeting `https://services.leadconnectorhq.com/workflows/`.
2. **Query Parameters**: The `locationId` is mandatory and must be sent as a query parameter (`?locationId=...`).
3. **Strict Headers**:
   - `Authorization: Bearer <GHL_API_KEY>`
   - `Version: 2021-07-28`
   - `Accept: application/json`
   - `User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36` (Critical for bypassing Cloudflare WAF).

### Example cURL Command

```bash
   curl -L 'https://services.leadconnectorhq.com/workflows/?locationId=<GHL_LOCATION_ID>' \
-H 'Accept: application/json' \
-H 'Version: 2021-07-28' \
-H 'Authorization: Bearer <GHL_API_KEY>' \
-H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
```

## Execution Protocol

The agent will execute the provided Python script. The script utilizes environment variables for dynamic configuration and implements a Plug & Play credential check.

**Plug & Play Strategy (Automatic .env):**
If credentials are not configured, the script will **automatically search for or generate a `.env` template** in the forge root `.agent/.env`. The script will halt execution with `Exit Code 1` and explicitly request the operator to fill in the required data. Do not force the operator to use manual `export` commands.

Execution command:

```bash
python .agent/catalog/skills/ghl-list-workflows/scripts/fetch_workflows.py
```

```powershell
python .agent\catalog\skills\ghl-list-workflows\scripts\fetch_workflows.py
```
