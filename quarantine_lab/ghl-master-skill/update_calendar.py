import asyncio
import json
import sys
import os

sys.path.append(os.path.join(os.getcwd(), "scripts"))

from core.auth import GHLAuth
from core.limiter import GHLLimiter
from core.client import GHLClient

async def update_calendar_availability():
    auth = GHLAuth()
    limiter = GHLLimiter()
    client = GHLClient(auth, limiter)
    
    # Usar el calendario activo pero vacío
    calendar_id = "ytwyTJdRIJglt3QdwYdB"
    
    # Disponibilidad para Viernes (5)
    payload = {
        "availabilities": [
            {
                "dayOfWeek": 5,
                "slots": [{"startTime": "09:00", "endTime": "17:00"}]
            }
        ]
    }
    
    print(f"--- Actualizando Disponibilidad para el calendario {calendar_id} ---")
    try:
        resp = await client.request("PUT", f"/calendars/{calendar_id}", json=payload)
        print("Calendario actualizado exitosamente.")
        
        # Actualizar prep por si acaso
        with open("booking_prep.json", "r") as f:
            prep = json.load(f)
        prep["calendar_id"] = calendar_id
        with open("booking_prep.json", "w") as f:
            json.dump(prep, f, indent=2)
            
    except Exception as e:
        print(f"Error actualizando calendario: {e}")

if __name__ == "__main__":
    asyncio.run(update_calendar_availability())
