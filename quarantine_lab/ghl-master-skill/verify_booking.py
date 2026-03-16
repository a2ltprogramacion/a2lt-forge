import asyncio
import json
import sys
import os

sys.path.append(os.path.join(os.getcwd(), "scripts"))

from core.auth import GHLAuth
from core.limiter import GHLLimiter
from core.client import GHLClient

async def verify_booking():
    auth = GHLAuth()
    limiter = GHLLimiter()
    client = GHLClient(auth, limiter)
    
    appt_id = "xnKpEskUNuioSRNS7omf"
    
    print(f"--- Verificando detalles de la cita {appt_id} ---")
    try:
        # En v2 a veces es /calendars/events/{id} or /calendars/appointments/{id}
        resp = await client.request("GET", f"/calendars/events/{appt_id}")
        print(json.dumps(resp, indent=2))
        
    except Exception as e:
        print(f"Error verificando cita: {e}")

if __name__ == "__main__":
    asyncio.run(verify_booking())
