from core.client import GHLClient
from typing import Dict, Any, List

class GHLAutomations:
    """Gestión de Workflows y Webhooks en GHL API 2.0."""
    def __init__(self, client: GHLClient):
        self.client = client

    async def list_workflows(self, location_id: str) -> Dict[str, Any]:
        return await self.client.request("GET", "/workflows/", params={"locationId": location_id})

    async def add_to_workflow(self, contact_id: str, workflow_id: str) -> Dict[str, Any]:
        return await self.client.request("POST", f"/workflows/{workflow_id}/contacts/{contact_id}")

    async def remove_from_workflow(self, contact_id: str, workflow_id: str) -> Dict[str, Any]:
        return await self.client.request("DELETE", f"/workflows/{workflow_id}/contacts/{contact_id}")

    async def create_webhook(self, location_id: str, url: str, events: List[str]) -> Dict[str, Any]:
        return await self.client.request("POST", "/webhooks/", json={"locationId": location_id, "url": url, "events": events})
