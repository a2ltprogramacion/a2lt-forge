from core.client import GHLClient
from typing import Dict, Any, List

class GHLCalendars:
    """Gestión de Calendarios y Reservas."""
    def __init__(self, client: GHLClient):
        self.client = client

    async def list_calendars(self, location_id: str) -> List[Dict[str, Any]]:
        data = await self.client.request("GET", "/calendars/", params={"locationId": location_id})
        return data.get("calendars", [])

    async def get_free_slots(self, calendar_id: str, start_time: int, end_time: int) -> List[Dict[str, Any]]:
        params = {"startDate": start_time, "endDate": end_time}
        data = await self.client.request("GET", f"/calendars/{calendar_id}/free-slots", params=params)
        return data.get("slots", [])

    async def create_appointment(self, calendar_id: str, location_id: str, contact_id: str, start_time: str, **kwargs) -> Dict[str, Any]:
        payload = {"calendarId": calendar_id, "locationId": location_id, "contactId": contact_id, "startTime": start_time, **kwargs}
        return await self.client.request("POST", "/calendars/events/appointments", json=payload)
