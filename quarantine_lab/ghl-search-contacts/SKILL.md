---
name: ghl-search-contacts
description: Utiliza la API v2 de GoHighLevel para buscar y listar contactos de una ubicación específica.
---

# GoHighLevel: Search Contacts Skill

## Usage Context

Use this skill when the user requests to list, read, search, or verify contacts within their GoHighLevel (GHL) account.

## Technical Context and Rules (GHL API v2)

1. **Strategic Endpoint**: The legacy `GET /contacts/` endpoint is deprecated. The agent MUST always use `POST https://services.leadconnectorhq.com/contacts/search`.
2. **Strict Headers**:
   - `Authorization: Bearer <GHL_API_KEY>`
   - `Version: 2021-07-28`
   - `Content-Type: application/json`
3. **Payload**: The JSON request body must include the `locationId`.

## Execution Protocol

The agent only needs to execute the provided Python script to interact with the API.

**Plug & Play Strategy (Automatic .env):**
If the user hasn't configured credentials, the script will **automatically generate a `.env` template** and halt execution with `Exit Code 1`, requesting the operator to fill in the required keys. Do not force the operator to use manual `export` commands unless debugging the global environment.

Execution command:

```bash
python .agent/catalog/skills/ghl-search-contacts/scripts/fetch_contacts.py
```
