from core.client import GHLClient
from typing import Dict, Any

class GHLSystem:
    """Gestión de Usuarios y Repositorio de Medios en GHL API 2.0."""
    def __init__(self, client: GHLClient):
        self.client = client

    async def list_users(self, company_id: str) -> Dict[str, Any]:
        return await self.client.request("GET", "/users/search", params={"companyId": company_id})

    async def upload_media(self, location_id: str, file_url: str) -> Dict[str, Any]:
        return await self.client.request("POST", "/medias/upload-file", json={"locationId": location_id, "fileUrl": file_url})
