import asyncio
import json
import sys
import os
import time
from datetime import datetime, timedelta

sys.path.append(os.path.join(os.getcwd(), "scripts"))

from core.auth import GHLAuth
from core.limiter import GHLLimiter
from core.client import GHLClient
from modules.system import GHLSystem

async def find_slots_with_user():
    # Cargar prep
    with open("booking_prep.json", "r") as f:
        prep = json.load(f)
    
    auth = GHLAuth()
    limiter = GHLLimiter()
    client = GHLClient(auth, limiter)
    system = GHLSystem(client)
    
    location_id = prep["location_id"]
    calendar_id = prep["calendar_id"]
    
    print(f"--- Obteniendo CompanyId para la Ubicación {location_id} ---")
    loc_resp = await client.request("GET", f"/locations/{location_id}")
    company_id = loc_resp.get("location", {}).get("companyId")
    
    if not company_id:
        print("No se pudo obtener el CompanyId.")
        return
        
    print(f"CompanyId identificado: {company_id}")
    
    print("--- Listando Usuarios ---")
    users_resp = await system.list_users(company_id=company_id)
    users = users_resp.get("users", [])
    
    if not users:
        print("No se encontraron usuarios.")
        return

    # Rango: Próximos 30 días
    start_dt = datetime.now()
    end_dt = start_dt + timedelta(days=30)
    start_ms = int(start_dt.timestamp() * 1000)
    end_ms = int(end_dt.timestamp() * 1000)
    
    for u in users:
        user_id = u["id"]
        print(f"Probando slots con usuario: {u.get('name')} ({user_id})")
        try:
            params = {
                "startDate": start_ms,
                "endDate": end_ms,
                "timezone": "America/Caracas",
                "userId": user_id
            }
            resp = await client.request("GET", f"/calendars/{calendar_id}/free-slots", params=params)
            slots = resp.get("slots", {})
            
            if slots:
                print(f"¡ÉXITO! Se encontraron slots con usuario {u.get('name')}")
                # Procesar el primero
                first_slot = None
                if isinstance(slots, dict):
                    for date_key, day_slots in slots.items():
                        if day_slots:
                            first_slot = day_slots[0]
                            break
                elif isinstance(slots, list) and len(slots) > 0:
                    first_slot = slots[0]

                if first_slot:
                    print(f"Slot seleccionado: {first_slot}")
                    prep["selected_slot"] = first_slot
                    prep["user_id"] = user_id
                    with open("booking_prep.json", "w") as f:
                        json.dump(prep, f, indent=2)
                    return # Salimos al encontrar el primero
            else:
                print(f"Sin slots para {u.get('name')}")
                
        except Exception as e:
            print(f"Error con usuario {u.get('name')}: {e}")

    print("No se encontraron slots con ninguno de los usuarios listados.")

if __name__ == "__main__":
    asyncio.run(find_slots_with_user())
