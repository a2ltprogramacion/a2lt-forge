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

async def scan_locations_for_calendar():
    auth = GHLAuth()
    limiter = GHLLimiter()
    client = GHLClient(auth, limiter)
    
    # Necesitamos el companyId
    # Intentar obtenerlo de la locación actual or listing company
    location_id = "Taooh0nQJLaaDDxbtG0L"
    loc_resp = await client.request("GET", f"/locations/{location_id}")
    company_id = loc_resp.get("location", {}).get("companyId")
    
    if not company_id:
        print("No se pudo obtener el CompanyId.")
        return

    print(f"--- Escaneando Locations de Company: {company_id} ---")
    try:
        # Listar locations
        locs_resp = await client.request("GET", f"/locations/search", params={"companyId": company_id})
        locations = locs_resp.get("locations", [])
        
        if not locations:
            print("No se encontraron locations.")
            return

        print(f"Buscando en {len(locations)} locations...")
        
        for loc in locations:
            l_id = loc["id"]
            l_name = loc["name"]
            print(f"Revisando: {l_name} ({l_id})...")
            
            try:
                # Listar calendarios
                cals_resp = await client.request("GET", "/calendars/", params={"locationId": l_id})
                cals = cals_resp.get("calendars", [])
                
                for c in cals:
                    if c.get("isActive") or c.get("active"):
                        c_id = c["id"]
                        print(f"  - Calendario Activo Encontrado: {c['name']} ({c_id})")
                        
                        # Probar slots
                        start_dt = datetime.now()
                        end_dt = start_dt + timedelta(days=15)
                        params = {
                            "startDate": int(start_dt.timestamp() * 1000),
                            "endDate": int(end_dt.timestamp() * 1000),
                            "timezone": "America/Caracas"
                        }
                        slots_resp = await client.request("GET", f"/calendars/{c_id}/free-slots", params=params)
                        slots = slots_resp.get("slots", {})
                        
                        if slots:
                            print(f"  ¡SLOTS ENCONTRADOS en {l_name}!")
                            # Guardar estado y salir
                            state = {
                                "location_id": l_id,
                                "calendar_id": c_id,
                                "selected_slot": None 
                            }
                            # Identificar el primer slot
                            first_slot = None
                            if isinstance(slots, dict):
                                for d, sl in slots.items():
                                    if sl: 
                                        first_slot = sl[0]
                                        break
                            elif isinstance(slots, list) and slots:
                                first_slot = slots[0]
                            
                            if first_slot:
                                state["selected_slot"] = first_slot
                                with open("booking_prep.json", "w") as f:
                                    json.dump(state, f, indent=2)
                                print("Prep de agendamiento completado.")
                                return # ÉXITO TOTAL
            except Exception as e:
                # print(f"  Error en {l_name}: {e}")
                pass
                
        print("No se encontró ningún calendario con slots abiertos en ninguna subcuenta.")
        
    except Exception as e:
        print(f"Error escaneando locations: {e}")

if __name__ == "__main__":
    asyncio.run(scan_locations_for_calendar())
