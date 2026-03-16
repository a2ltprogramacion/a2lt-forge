from core.client import GHLClient
from typing import Dict, Any

class GHLSocial:
    """Gestión de Social Planner en GHL API 2.0."""
    def __init__(self, client: GHLClient):
        self.client = client

    async def list_social_accounts(self, location_id: str) -> Dict[str, Any]:
        """Alias para cumplir con auditoría y consistencia."""
        return await self.client.request("GET", f"/social-media-posting/{location_id}/accounts")

    async def get_social_accounts(self, location_id: str) -> Dict[str, Any]:
        """Método principal solicitado por auditoría."""
        return await self.list_social_accounts(location_id)

    async def schedule_post(self, location_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.client.request("POST", f"/social-media-posting/{location_id}/posts", json=data)
