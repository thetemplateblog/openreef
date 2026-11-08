"""Tiny async pub/sub used by the sequence engine to broadcast progress, results
and alerts to WebSocket clients, MQTT, webhooks and the Hydros adapter."""
from __future__ import annotations

import asyncio
import logging
import time
from typing import Any, Awaitable, Callable, Dict, List

log = logging.getLogger(__name__)

Handler = Callable[[Dict[str, Any]], Awaitable[None]]


class EventBus:
    def __init__(self) -> None:
        self._handlers: List[Handler] = []
        self._queues: List[asyncio.Queue] = []

    def subscribe(self, handler: Handler) -> None:
        self._handlers.append(handler)

    def queue(self, maxsize: int = 200) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue(maxsize=maxsize)
        self._queues.append(q)
        return q

    def unqueue(self, q: asyncio.Queue) -> None:
        if q in self._queues:
            self._queues.remove(q)

    async def publish(self, type_: str, **payload: Any) -> Dict[str, Any]:
        evt = {"type": type_, "ts": time.time(), **payload}
        for q in list(self._queues):
            try:
                q.put_nowait(evt)
            except asyncio.QueueFull:
                log.warning("event queue full; dropping %s", type_)
        for h in self._handlers:
            try:
                await h(evt)
            except Exception:
                log.exception("event handler failed for %s", type_)
        return evt
