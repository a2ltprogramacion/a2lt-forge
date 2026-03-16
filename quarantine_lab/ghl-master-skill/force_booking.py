import asyncio
import json
import sys
import os
from datetime import datetime, timedelta

sys.path.append(os.path.join(os.getcwd(), "scripts"))

from core.auth import GHLAuth
from core.limiter import GHLLimiter
from core.client import GHLClient
from modules.calendars import GHLCalendars

async def force_booking():
    auth = GHLAuth()
    limiter = GHLLimiter()
    client = GHLClient(auth, limiter)
    calendars = GHLCalendars(client)
    
    # Datos confirmados
    location_id = "Taooh0nQJLaaDDxbtG0L"
    contact_id = "T6WL65ngx3ZOo6YSVq0z"
    calendar_id = "ytwyTJdRIJglt3QdwYdB"
    
    # Mañana Viernes 13 a las 10 AM
    booking_time = "2026-03-13T10:00:00-04:00"
    
    print(f"--- Intentando Agendamiento Forzado ---")
    print(f"Calendario: {calendar_id}")
    print(f"Contacto: {contact_id}")
    print(f"Hora: {booking_time}")
    
    try:
        resp = await calendars.create_appointment(
            calendar_id=calendar_id,
            location_id=location_id,
            contact_id=contact_id,
            start_time=booking_time,
            title="Prueba Técnica Antigravity"
        )
        print("¡AGENDAMIENTO EXITOSO!")
        print(json.dumps(resp, indent=2))
    except Exception as e:
        print(f"Fallo el agendamiento: {e}")

if __name__ == "__main__":
    asyncio.run(force_booking())
