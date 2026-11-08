"""Hydros (CoralVue) developer API adapter.

The official API (https://www.coralvuehydros.com/api/, docs at
https://developers.api.coralvuehydros.com/) authenticates with
`Authorization: {provider_key}:{device_key}` and offers device lookup, live
state, logs/export, metadata and *output overrides*.  As documented, it does not
accept pushed sensor values, so OpenReef integrates two ways:

1. Rules in config.yaml: when a result crosses a threshold, override a Hydros
   output (e.g. turn the alkalinity doser outlet on for 30 minutes).
2. The analyzer's dry-contact alarm relay wired to a Hydros Sense port, so the
   controller can build its own rules on "OpenReef alarm".

The exact paths for state and overrides live in the Hydros REST reference and
may change; they are read from `endpoints` so you can adjust them without
touching code.  Rate limits (per device): lookup 60/min, state + overrides
10/min, polling sessions 5/hour.
"""
from __future__ import annotations

import logging
import re
import time
from typing import Any, Dict, Optional

import httpx

from ..config import HydrosConfig

log = logging.getLogger(__name__)

DEFAULT_ENDPOINTS = {
    "device": "/api/v1/device",
    "state": "/api/v1/state",
    "override": "/api/v1/override",
}

_RULE_RE = re.compile(r"^\s*(alk_dkh|no3_ppm|po4_ppm)\s*(<|>|<=|>=)\s*([0-9.]+)\s*$")
_KEYS = {"alkalinity": "alk_dkh", "nitrate": "no3_ppm", "phosphate": "po4_ppm"}


class HydrosClient:
    def __init__(self, cfg: HydrosConfig, endpoints: Optional[Dict[str, str]] = None):
        self.cfg = cfg
        self.endpoints = {**DEFAULT_ENDPOINTS, **(endpoints or {})}
        self._client = httpx.AsyncClient(base_url=cfg.base_url, timeout=15.0,
                                         headers={"Authorization": f"{cfg.provider_key}:{cfg.device_key}",
                                                  "Accept": "application/json"})
        self.last_state: Optional[Dict[str, Any]] = None
        self.last_state_ts: float = 0.0
        self._last_override_ts: Dict[str, float] = {}

    async def close(self) -> None:
        await self._client.aclose()

    async def device(self) -> Any:
        r = await self._client.get(self.endpoints["device"])
        r.raise_for_status()
        return r.json()

    async def state(self) -> Any:
        r = await self._client.get(self.endpoints["state"])
        r.raise_for_status()
        self.last_state = r.json()
        self.last_state_ts = time.time()
        return self.last_state

    async def override(self, output: str, state: str, minutes: int) -> Any:
        """Override an output (name as shown in the Hydros app). Payload shape
        follows the REST reference; adjust here if your firmware differs."""
        payload = {"output": output, "state": state, "duration_minutes": minutes}
        r = await self._client.post(self.endpoints["override"], json=payload)
        r.raise_for_status()
        self._last_override_ts[output] = time.time()
        return r.json() if r.content else {}

    async def apply_rules(self, test: str, value: float) -> list:
        """Evaluate config rules against a fresh result; returns the actions taken."""
        key = _KEYS.get(test)
        actions = []
        for rule in self.cfg.rules:
            m = _RULE_RE.match(str(rule.get("when", "")))
            if not m or m.group(1) != key:
                continue
            op, thr = m.group(2), float(m.group(3))
            hit = {"<": value < thr, ">": value > thr, "<=": value <= thr, ">=": value >= thr}[op]
            if not hit:
                continue
            output, state, minutes = rule["output"], rule.get("state", "on"), int(rule.get("minutes", 30))
            # respect the 10/min write limit and avoid hammering the same output
            if time.time() - self._last_override_ts.get(output, 0) < 60:
                continue
            try:
                await self.override(output, state, minutes)
                actions.append({"rule": rule["when"], "output": output, "state": state, "minutes": minutes})
            except Exception as e:
                log.warning("Hydros override failed: %s", e)
                actions.append({"rule": rule["when"], "error": str(e)})
        return actions
