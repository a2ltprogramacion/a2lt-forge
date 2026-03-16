import asyncio
import time
import logging
from typing import List

class GHLLimiter:
    """
    Middleware de Rate Limiting para GHL API 2.0.
    - Burst Limit: 100 req / 10s.
    - Daily Limit: Monitoreo vía Headers (vía Client).
    """
    
    def __init__(self, burst_limit: int = 100, burst_period: int = 10):
        self.burst_limit = burst_limit
        self.burst_period = burst_period
        self.requests: List[float] = []

    async def wait_if_needed(self):
        """Bloquea si se ha alcanzado el límite de ráfaga."""
        now = time.time()
        # Filtrar requests fuera de la ventana de tiempo
        self.requests = [r for r in self.requests if now - r < self.burst_period]
        
        if len(self.requests) >= self.burst_limit:
            wait_time = self.burst_period - (now - self.requests[0])
            if wait_time > 0:
                logging.warning(f"[RATE LIMIT] Burst alcanzado. Esperando {wait_time:.2f}s...")
                await asyncio.sleep(wait_time)
        
        self.requests.append(time.time())
