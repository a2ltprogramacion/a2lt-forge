import asyncio
import os
import httpx
import logging
from typing import Optional, Dict, Any
from .auth import GHLAuth
from .limiter import GHLLimiter

class GHLClient:
    """
    Cliente Maestro Refactorizado para GoHighLevel API 2.0.
    Cumple con el Blueprint y la Directiva 0 de La Forja.
    """
    
    BASE_URL = "https://services.leadconnectorhq.com"
    API_VERSION = "2021-07-28"

    def __init__(self, auth: Optional[GHLAuth] = None, limiter: Optional[GHLLimiter] = None):
        self.auth = auth or GHLAuth()
        self.limiter = limiter or GHLLimiter()
        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            timeout=30.0
        )

    def _get_headers(self) -> Dict[str, str]:
        token = self.auth.get_token()
        if not token:
            raise ValueError("No hay token válido (Access Token expirado o API Key ausente)")
            
        return {
            "Authorization": f"Bearer {token}",
            "Version": self.API_VERSION,
            "Content-Type": "application/json"
        }

    async def _refresh_oauth_token(self):
        """
        Lógica de rotación de Refresh Tokens según API 2.0.
        Implementar cuando se use OAuth2 (requiere client_id y secret).
        """
        refresh_token = self.auth.get_refresh_token()
        if not refresh_token:
            return # Estamos en modo PIT o no hay OAuth configurado
            
        logging.info("Intentando rotación de Refresh Token OAuth2...")
        # NOTA: Endpoint /oauth/token requiere credenciales de la app (no PIT)
        # Por ahora lanzamos error informativo indicando que requiere re-auth manual
        # si no están las credenciales en .env
        pass

    async def request(self, method: str, path: str, version: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        await self.limiter.wait_if_needed()
        
        headers = self._get_headers()
        if version:
            headers["Version"] = version
            
        retries = 3
        backoff = 2
        
        for i in range(retries):
            try:
                response = await self.client.request(
                    method, 
                    path, 
                    headers=headers, 
                    **kwargs
                )
                
                # Manejo de expiración de token
                if response.status_code == 401:
                    await self._refresh_oauth_token()
                    continue

                if response.status_code == 429:
                    wait = backoff ** (i + 1)
                    logging.warning(f"429 Too Many Requests. Reintentando en {wait}s...")
                    await asyncio.sleep(wait)
                    continue
                    
                response.raise_for_status()
                return response.json()
                
            except httpx.HTTPStatusError as e:
                if i == retries - 1:
                    logging.error(f"Error HTTP definitivo [{e.response.status_code}]: {e.response.text}")
                    raise
                wait = backoff ** (i + 1)
                await asyncio.sleep(wait)
            except Exception as e:
                logging.error(f"Error crítico en request: {str(e)}")
                raise
