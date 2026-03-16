import asyncio
import json
import sys
import os

sys.path.append(os.path.join(os.getcwd(), "scripts"))

from core.auth import GHLAuth
from core.limiter import GHLLimiter
from core.client import GHLClient

async def find_working_calendar():
    auth = GHLAuth()
    limiter = GHLLimiter()
    client = GHLClient(auth, limiter)
    location_id = "Taooh0nQJLaaDDxbtG0L"
    
    print("--- Buscando Citas Existentes ---")
    try:
        # Intentar obtener citas de los últimos 30 días
        # startDate y endDate son requeridos en v2 appointments
        import time
        now_ms = int(time.time() * 1000)
        past_ms = now_ms - (30 * 24 * 60 * 60 * 1000)
        future_ms = now_ms + (30 * 24 * 60 * 60 * 1000)
        
        params = {
            "locationId": location_id,
            "startDate": past_ms,
            "endDate": future_ms
        }
        resp = await client.request("GET", "/calendars/events/appointments", params=params)
        events = resp.get("events", [])
        
        if events:
            print(f"Se encontraron {len(events)} citas.")
            cal_id = events[0].get("calendarId")
            print(f"Calendario funcional identificado de cita existente: {cal_id}")
            
            # Guardar en prep
            with open("booking_prep.json", "r") as f:
                prep = json.load(f)
            prep["calendar_id"] = cal_id
            with open("booking_prep.json", "w") as f:
                json.dump(prep, f, indent=2)
        else:
            print("No se encontraron citas recientes.")
            
    except Exception as e:
        print(f"Error buscando citas: {e}")

if __name__ == "__main__":
    asyncio.run(find_working_calendar())
