"""POST selected events to user-configured webhook URLs (JSON body, 10 s timeout)."""
from __future__ import annotations

import logging
from typing import Any, Dict, List

import httpx

log = logging.getLogger(__name__)

FORWARDED = {"result", "alert", "run_finished", "reagent_low", "calibration"}


class Webhooks:
    def __init__(self, urls: List[str]):
        self.urls = list(urls)
        self._client = httpx.AsyncClient(timeout=10.0)

    async def close(self) -> None:
        await self._client.aclose()

    async def handle_event(self, evt: Dict[str, Any]) -> None:
        if evt["type"] not in FORWARDED or not self.urls:
            return
        for url in self.urls:
            try:
                await self._client.post(url, json=evt)
            except Exception as e:
                log.warning("webhook %s failed: %s", url, e)
