from core.client import GHLClient
from typing import Dict, Any

class GHLSaaS:
    """Gestión de SaaS Configurator y Snapshots en GHL API 2.0."""
    def __init__(self, client: GHLClient):
        self.client = client

    async def list_snapshots(self, company_id: str) -> Dict[str, Any]:
        return await self.client.request("GET", "/snapshots/", params={"companyId": company_id})

    async def get_saas_locations(self, company_id: str) -> Dict[str, Any]:
        return await self.client.request("GET", "/saas-api/locations/", params={"companyId": company_id})
