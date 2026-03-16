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
from modules.calendars import GHLCalendars

async def find_slots():
    # Cargar prep
    with open("booking_prep.json", "r") as f:
        prep = json.load(f)
    
    auth = GHLAuth()
    limiter = GHLLimiter()
    client = GHLClient(auth, limiter)
    calendars = GHLCalendars(client)
    
    calendar_id = prep["calendar_id"]
    
    # Rango: Próximos 30 días
    start_dt = datetime.now()
    end_dt = start_dt + timedelta(days=30)
    
    # Convertir a milisegundos epoch
    start_ms = int(start_dt.timestamp() * 1000)
    end_ms = int(end_dt.timestamp() * 1000)
    
    print(f"--- Buscando Slots Libres para el calendario {calendar_id} ---")
    print(f"Rango: {start_dt} a {end_dt}")
    
    try:
        # Algunos calendarios requieren timezone
        params = {
            "startDate": start_ms,
            "endDate": end_ms,
            "timezone": "America/Caracas"
        }
        data = await client.request("GET", f"/calendars/{calendar_id}/free-slots", params=params)
        slots = data.get("slots", {})
        if slots:
            # Los slots suelen venir como lista de strings ISO o diccionarios con la fecha
            # En v2 a veces es una lista de fechas
            print(f"Se encontraron {len(slots)} slots disponibles.")
            
            # Tomamos el primero para la prueba
            first_slot = None
            for date_key, day_slots in slots.items() if isinstance(slots, dict) else []:
                if day_slots:
                    first_slot = day_slots[0]
                    break
            
            # Si slots es una lista de diccionarios (depende de la versión exacta de GHL v2)
            if not first_slot and isinstance(slots, list) and len(slots) > 0:
                first_slot = slots[0]

            if first_slot:
                print(f"Slot seleccionado: {json.dumps(first_slot)}")
                prep["selected_slot"] = first_slot
                with open("booking_prep.json", "w") as f:
                    json.dump(prep, f, indent=2)
            else:
                # Si slots es un dict plano o algo más
                print(f"Formato de slots no esperado: {type(slots)}")
                print(json.dumps(slots, indent=2))
        else:
            print("No se encontraron slots libres en este rango.")
            
    except Exception as e:
        print(f"Error buscando slots: {e}")

if __name__ == "__main__":
    asyncio.run(find_slots())
