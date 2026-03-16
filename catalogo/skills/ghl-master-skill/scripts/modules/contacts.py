from core.client import GHLClient
from typing import Dict, Any, List, Optional

class GHLContacts:
    """Gestión avanzada de contactos en GHL API 2.0."""
    def __init__(self, client: GHLClient):
        self.client = client

    async def search_contacts(self, location_id: str, query: Optional[str] = None, page_limit: int = 20) -> List[Dict[str, Any]]:
        payload = {"locationId": location_id, "pageLimit": page_limit}
        if query:
            payload["query"] = query
        data = await self.client.request("POST", "/contacts/search", json=payload)
        return data.get("contacts", [])

    async def get_contact(self, contact_id: str) -> Dict[str, Any]:
        return await self.client.request("GET", f"/contacts/{contact_id}")

    async def upsert_contact(self, location_id: str, email: str, **kwargs) -> Dict[str, Any]:
        payload = {"locationId": location_id, "email": email, **kwargs}
        return await self.client.request("POST", "/contacts/upsert", json=payload)
