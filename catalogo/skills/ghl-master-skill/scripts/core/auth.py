import os
import json
import time
import logging
from typing import Dict, Optional
from dotenv import load_dotenv

# Cargar variables de entorno desde el root del proyecto
load_dotenv("y:/Proyectos IA/a2lt-forge/.env")

class GHLAuth:
    """
    Gestor de autenticación para GHL API 2.0.
    Maneja la persistencia de tokens OAuth2 y Private Integration Tokens (PIT).
    """
    
    def __init__(self, storage_path: str = "auth_state.json", api_key: Optional[str] = None):
        self.storage_path = storage_path
        self.api_key_override = api_key
        self.state = self._load_state()

    def _load_state(self) -> Dict:
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                logging.error(f"Error cargando persistencia de auth: {e}")
        return {}

    def save_state(self, access_token: str, refresh_token: Optional[str] = None, expires_in: int = 86400):
        self.state = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_at": time.time() + expires_in,
            "updated_at": time.time()
        }
        with open(self.storage_path, "w") as f:
            json.dump(self.state, f, indent=2)

    def get_token(self) -> Optional[str]:
        """Retorna el token actual si no ha expirado."""
        if self.api_key_override:
            return self.api_key_override
            
        if not self.state:
            return os.getenv("GHL_API_KEY") # Fallback a PIT vía Env
            
        # Si expira en menos de 5 minutos, consideramos que expiró
        if time.time() > self.state.get("expires_at", 0) - 300:
            return None
            
        return self.state.get("access_token")

    def get_refresh_token(self) -> Optional[str]:
        return self.state.get("refresh_token")
