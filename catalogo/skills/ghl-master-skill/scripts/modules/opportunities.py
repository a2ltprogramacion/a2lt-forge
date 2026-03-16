from core.client import GHLClient
from typing import Dict, Any, List, Optional

class GHLOpportunities:
    """Gestión de Pipelines y Oportunidades."""
    def __init__(self, client: GHLClient):
        self.client = client

    async def list_pipelines(self, location_id: str) -> List[Dict[str, Any]]:
        """Lista todos los pipelines de una ubicación."""
        data = await self.client.request("GET", f"/opportunities/pipelines", params={"locationId": location_id})
        return data.get("pipelines", [])

    async def list_opportunities(self, location_id: str, pipeline_id: str = None, **kwargs) -> List[Dict[str, Any]]:
        """Lista las oportunidades (deals) de una ubicación filtrando por pipeline."""
        params = {"location_id": location_id}
        if pipeline_id:
            params["pipelineId"] = pipeline_id
        data = await self.client.request("GET", "/opportunities/search", params={**params, **kwargs})
        return data.get("opportunities", [])

    async def upsert_opportunity(self, location_id: str, pipeline_id: str, stage_id: str, title: str, **kwargs) -> Dict[str, Any]:
        """Crea o actualiza una oportunidad."""
        payload = {"locationId": location_id, "pipelineId": pipeline_id, "pipelineStageId": stage_id, "name": title, **kwargs}
        return await self.client.request("POST", "/opportunities/upsert", json=payload)
