import asyncio
import json
import sys
import os

sys.path.append(os.path.join(os.getcwd(), "scripts"))

from core.auth import GHLAuth
from core.limiter import GHLLimiter
from core.client import GHLClient

async def create_test_calendar():
    auth = GHLAuth()
    limiter = GHLLimiter()
    client = GHLClient(auth, limiter)
    location_id = "Taooh0nQJLaaDDxbtG0L"
    
    calendar_payload = {
        "name": "Test Antigravity V2",
        "locationId": location_id,
        "eventType": "round_robin",
        "calendarType": "service",
        "isActive": True,
        "availabilities": [
            {
                "dayOfWeek": 1, "slots": [{"startTime": "09:00", "endTime": "17:00"}]
            },
            {
                "dayOfWeek": 2, "slots": [{"startTime": "09:00", "endTime": "17:00"}]
            },
            {
                "dayOfWeek": 3, "slots": [{"startTime": "09:00", "endTime": "17:00"}]
            },
            {
                "dayOfWeek": 4, "slots": [{"startTime": "09:00", "endTime": "17:00"}]
            },
            {
                "dayOfWeek": 5, "slots": [{"startTime": "09:00", "endTime": "17:00"}]
            }
        ]
    }
    
    print("--- Creando Calendario de Prueba Corregido ---")
    try:
        resp = await client.request("POST", "/calendars/", json=calendar_payload)
        # En v2 la respuesta suele ser un objeto con el ID o el objeto completo
        cal_id = resp.get("id") or resp.get("calendar", {}).get("id")
        if cal_id:
            print(f"Calendario creado exitosamente: {cal_id}")
            # Guardar en prep
            with open("booking_prep.json", "r") as f:
                prep = json.load(f)
            prep["calendar_id"] = cal_id
            with open("booking_prep.json", "w") as f:
                json.dump(prep, f, indent=2)
        else:
            print(f"No se pudo obtener el ID del calendario. Respuesta: {json.dumps(resp)}")
            
    except Exception as e:
        print(f"Error creando calendario: {e}")

if __name__ == "__main__":
    asyncio.run(create_test_calendar())
