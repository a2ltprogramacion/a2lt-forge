from core.client import GHLClient
from typing import Dict, Any, List

class CustomObjectsModule:
    """Gestión de Esquemas y Registros de Custom Objects."""
    
    def __init__(self, client: GHLClient):
        self.client = client

    async def get_schemas(self) -> List[Dict[str, Any]]:
        data = await self.client.request("GET", "/objects/schemas")
        return data.get("schemas", [])

    async def search_records(self, schema_key: str, query: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Busca registros en un objeto personalizado."""
        payload = query or {}
        data = await self.client.request("POST", f"/objects/{schema_key}/records/search", json=payload)
        return data.get("records", [])

    async def create_record(self, schema_key: str, data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.client.request("POST", f"/objects/{schema_key}/records", json=data)
