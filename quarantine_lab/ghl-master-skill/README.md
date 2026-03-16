# GHL Master Skill (API 2.0)

Skill modular diseñada para la integración total con el CRM GoHighLevel bajo los estándares de la API 2.0.

## Características Core
- **OAuth2 & PIT Support**: Manejo robusto de tokens y autenticación de subcuenta.
- **Auto-Rate Limiting**: Burst limit de 100 req / 10s integrado.
- **Modularidad por Dominios**: Código limpio separado en Contacts, Calendars, Operations, etc.

## Uso
Ejecuta acciones a través del script `main.py`:
```bash
python scripts/main.py contacts search --params '{"location_id": "LOC_ID", "query": "test@example.com"}'
```

## Estructura
- `/core`: Cliente HTTP y Auth.
- `/modules`: Endpoints específicos de la API 2.0.
- `/tests`: Validación técnica.
