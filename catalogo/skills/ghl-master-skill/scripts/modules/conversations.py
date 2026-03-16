from core.client import GHLClient
from typing import Dict, Any, List

class GHLConversations:
    """Mensajería omnicanal (SMS, Email, Webchat)."""
    def __init__(self, client: GHLClient):
        self.client = client

    async def list_conversations(self, location_id: str) -> List[Dict[str, Any]]:
        data = await self.client.request("GET", "/conversations/search", params={"locationId": location_id})
        return data.get("conversations", [])

    async def list_messages(self, conversation_id: str) -> List[Dict[str, Any]]:
        data = await self.client.request("GET", f"/conversations/{conversation_id}/messages")
        return data.get("messages", [])

    async def send_message(self, contact_id: str, type: str, message: str, **kwargs) -> Dict[str, Any]:
        payload = {"contactId": contact_id, "type": type, "message": message, **kwargs}
        return await self.client.request("POST", "/conversations/messages", json=payload)
