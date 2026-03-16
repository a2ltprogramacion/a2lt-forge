import asyncio
import argparse
import json
import os
import sys
from core.auth import GHLAuth
from core.limiter import GHLLimiter
from core.client import GHLClient

# Importar módulos de dominio
from modules.contacts import GHLContacts
from modules.calendars import GHLCalendars
from modules.conversations import GHLConversations
from modules.opportunities import GHLOpportunities
from modules.payments import GHLPayments
from modules.automations import GHLAutomations
from modules.content import GHLContent
from modules.saas import GHLSaaS
from modules.ai import GHLAI
from modules.social import GHLSocial
from modules.system import GHLSystem

async def main():
    parser = argparse.ArgumentParser(description="GHL Master Skill CLI")
    parser.add_argument("--module", required=True, help="Módulo a ejecutar")
    parser.add_argument("--action", required=True, help="Acción a realizar")
    parser.add_argument("--params", type=str, default="{}", help="Parámetros en JSON")
    
    # Soporte para --help en formato JSON según GEMINI.md
    if "--help" in sys.argv:
        help_info = {
            "modules": ["contacts", "calendars", "conversations", "opportunities", "payments", "automations", "content", "saas", "ai", "social", "system"],
            "description": "GHL Master Skill unificada con soporte total API 2.0"
        }
        print(json.dumps(help_info))
        return

    args = parser.parse_args()
    params = json.loads(args.params)

    # Inicializar Core
    auth = GHLAuth()
    limiter = GHLLimiter()
    client = GHLClient(auth, limiter)

    # Mapeo de módulos
    modules = {
        "contacts": GHLContacts(client),
        "calendars": GHLCalendars(client),
        "conversations": GHLConversations(client),
        "opportunities": GHLOpportunities(client),
        "payments": GHLPayments(client),
        "automations": GHLAutomations(client),
        "content": GHLContent(client),
        "saas": GHLSaaS(client),
        "ai": GHLAI(client),
        "social": GHLSocial(client),
        "system": GHLSystem(client)
    }

    if args.module not in modules:
        print(json.dumps({"error": f"Módulo '{args.module}' no encontrado"}))
        return

    module_inst = modules[args.module]
    if not hasattr(module_inst, args.action):
        print(json.dumps({"error": f"Acción '{args.action}' no encontrada en el módulo '{args.module}'"}))
        return

    # Ejecutar acción
    func = getattr(module_inst, args.action)
    try:
        result = await func(**params)
        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({"error": str(e)}))

if __name__ == "__main__":
    asyncio.run(main())
