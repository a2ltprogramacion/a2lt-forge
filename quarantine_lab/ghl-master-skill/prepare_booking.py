import asyncio
import json
import sys
import os
import time

sys.path.append(os.path.join(os.getcwd(), "scripts"))

from core.auth import GHLAuth
from core.limiter import GHLLimiter
from core.client import GHLClient
from modules.contacts import GHLContacts
from modules.calendars import GHLCalendars

async def prepare_booking():
    auth = GHLAuth()
    limiter = GHLLimiter()
    client = GHLClient(auth, limiter)
    location_id = "Taooh0nQJLaaDDxbtG0L"
    
    contacts = GHLContacts(client)
    calendars = GHLCalendars(client)
    
    print("--- Buscando Contacto 'Prueba Antigravity' ---")
    contact_list = await contacts.search_contacts(location_id, query="Prueba Antigravity")
    contact_id = None
    if contact_list and len(contact_list) > 0:
        contact_id = contact_list[0]["id"]
        print(f"Contacto encontrado: {contact_id}")
    else:
        print("Contacto no encontrado. Creando uno nuevo...")
        new_contact = await contacts.upsert_contact(location_id, {
            "firstName": "Prueba",
            "lastName": "Antigravity",
            "email": "test_booking@a2lt.com",
            "phone": "+1234567890"
        })
        contact_id = new_contact.get("contact", {}).get("id")
        print(f"Nuevo contacto creado: {contact_id}")

    print("\n--- Listando Calendarios ---")
    cal_list = await calendars.list_calendars(location_id)
    cal_id = None
    if cal_list:
        print(f"Se encontraron {len(cal_list)} calendarios:")
        for c in cal_list:
            status = "Activo" if c.get("isActive") or c.get("active") else "Inactivo"
            print(f"- {c['name']} ({c['id']}) [ {status} ]")
            if (c.get("isActive") or c.get("active")) and not cal_id:
                cal_id = c["id"]
                cal_name = c["name"]
        
    if cal_id:
        print(f"\nSeleccionado para prueba: {cal_name} ({cal_id})")
        print("--- Obteniendo detalles del calendario ---")
        try:
            cal_details = await client.request("GET", f"/calendars/{cal_id}")
            print(json.dumps(cal_details, indent=2))
        except Exception as e:
            print(f"Error obteniendo detalles: {e}")
    else:
        print("\nNo se encontró ningún calendario marcado como activo.")

    # Guardamos IDs para el siguiente paso
    state = {
        "contact_id": contact_id,
        "calendar_id": cal_id,
        "location_id": location_id
    }
    with open("booking_prep.json", "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    asyncio.run(prepare_booking())
