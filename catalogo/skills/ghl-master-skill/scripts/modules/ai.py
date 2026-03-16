from core.client import GHLClient
from typing import Dict, Any

class GHLAI:
    """Gestión de Agentes de IA en GHL (Conversation, Voice y Agent Studio)."""
    def __init__(self, client: GHLClient):
        self.client = client

    async def list_conversation_ai_agents(self, location_id: str) -> Dict[str, Any]:
        """Agentes de IA de Conversación (Chat/Texto)."""
        return await self.client.request(
            "GET", 
            "/conversation-ai/agents/search", 
            params={"locationId": location_id}, 
            version="2021-04-15"
        )

    async def list_voice_ai_agents(self, location_id: str) -> Dict[str, Any]:
        """Agentes de Voice AI (Bots de Voz)."""
        return await self.client.request(
            "GET", 
            "/voice-ai/agents", 
            params={"locationId": location_id}
        )

    async def list_agent_studio_agents(self, location_id: str) -> Dict[str, Any]:
        """Agentes de Agent Studio."""
        return await self.client.request(
            "GET", 
            "/agent-studio/agents", 
            params={"locationId": location_id}
        )

    async def get_voice_ai_logs(self, location_id: str) -> Dict[str, Any]:
        return await self.client.request("GET", "/voice-ai/logs", params={"locationId": location_id})

    # Alias para compatibilidad anterior
    async def list_ai_agents(self, location_id: str) -> Dict[str, Any]:
        return await self.list_conversation_ai_agents(location_id)
