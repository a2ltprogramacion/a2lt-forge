import asyncio
import json
import sys
import os

sys.path.append(os.path.join(os.getcwd(), "scripts"))

from core.auth import GHLAuth
from core.limiter import GHLLimiter
from core.client import GHLClient

async def check_business():
    auth = GHLAuth()
    limiter = GHLLimiter()
    client = GHLClient(auth, limiter)
    location_id = "Taooh0nQJLaaDDxbtG0L"
    
    print(f"--- Consultando Business Hours de {location_id} ---")
    try:
        loc_resp = await client.request("GET", f"/locations/{location_id}")
        business = loc_resp.get("location", {}).get("business", {})
        print(json.dumps(business, indent=2))
        
        # Guardar en booking_prep por si lo necesitamos
        with open("booking_prep.json", "r") as f:
            prep = json.load(f)
        prep["business_hours"] = business
        with open("booking_prep.json", "w") as f:
            json.dump(prep, f, indent=2)
            
    except Exception as e:
        print(f"Error consultando business: {e}")

if __name__ == "__main__":
    asyncio.run(check_business())
