from core.client import GHLClient
from typing import Dict, Any, Optional

class GHLContent:
    """Gestión de Blogs, Embudos y Formularios en GHL API 2.0."""
    def __init__(self, client: GHLClient):
        self.client = client

    async def list_funnels(self, location_id: str) -> Dict[str, Any]:
        """Lista páginas de embudo (Funnels)."""
        return await self.client.request("GET", "/funnels/page", params={"locationId": location_id})

    async def list_funnel_pages(self, location_id: str) -> Dict[str, Any]:
        """Alias para list_funnels."""
        return await self.list_funnels(location_id)

    async def list_blogs(self, alt_id: str, alt_type: str = "location") -> Dict[str, Any]:
        """Lista posts de blog."""
        return await self.client.request("GET", "/blogs/posts", params={"altId": alt_id, "altType": alt_type})

    async def get_blog_posts(self, alt_id: str, alt_type: str = "location") -> Dict[str, Any]:
        return await self.list_blogs(alt_id, alt_type)

    async def list_forms(self, location_id: str) -> Dict[str, Any]:
        return await self.client.request("GET", "/forms/", params={"locationId": location_id})

    async def get_survey_submissions(self, survey_id: str, location_id: str) -> Dict[str, Any]:
        return await self.client.request("GET", f"/surveys/submissions", params={"surveyId": survey_id, "locationId": location_id})
