from core.client import GHLClient
from typing import Dict, Any, Optional

class GHLPayments:
    """Gestión de Pagos, Facturas y Suscripciones en GHL API 2.0."""
    def __init__(self, client: GHLClient):
        self.client = client

    async def list_invoices(self, alt_id: str, alt_type: str = "location", skip: int = 0, limit: int = 20) -> Dict[str, Any]:
        return await self.client.request("GET", "/invoices/", params={"altId": alt_id, "altType": alt_type, "limit": limit, "offset": skip})

    async def create_invoice(self, location_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.client.request("POST", "/invoices/", json={**data, "locationId": location_id})

    async def get_payment(self, payment_id: str, alt_id: str) -> Dict[str, Any]:
        return await self.client.request("GET", f"/payments/{payment_id}", params={"altId": alt_id, "altType": "location"})

    async def list_orders(self, location_id: str, **kwargs) -> Dict[str, Any]:
        """Lista las órdenes de pago de una ubicación."""
        return await self.client.request("GET", "/payments/orders", params={"locationId": location_id, **kwargs})

    async def list_subscriptions(self, alt_id: str, contact_id: Optional[str] = None) -> Dict[str, Any]:
        params = {"altId": alt_id, "altType": "location"}
        if contact_id:
            params["contactId"] = contact_id
        return await self.client.request("GET", "/payments/subscriptions", params=params)
