"""Sequence engine: runs one procedure at a time against the hardware, records
progress, results and failures, and publishes events."""
from __future__ import annotations

import asyncio
import logging
import time
import traceback
from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Dict, Optional

from ..config import AppConfig
from ..db import Database
from ..events import EventBus
from ..hal import Hardware, SafetyStop

log = logging.getLogger(__name__)


class Aborted(Exception):
    pass


@dataclass
class Progress:
    run_id: Optional[int] = None
    test: Optional[str] = None
    step: str = "idle"
    percent: float = 0.0
    started: Optional[float] = None
    detail: Dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Any]:
        return {"run_id": self.run_id, "test": self.test, "step": self.step,
                "percent": round(self.percent, 1), "started": self.started,
                "elapsed_s": round(time.time() - self.started, 1) if self.started else 0,
                "detail": self.detail}


class Context:
    """What a procedure gets: hardware, config, db, and a progress reporter."""

    def __init__(self, engine: "Engine", test: str, run_id: int):
        self.engine = engine
        self.hw: Hardware = engine.hw
        self.cfg: AppConfig = engine.cfg
        self.db: Database = engine.db
        self.bus: EventBus = engine.bus
        self.test = test
        self.run_id = run_id
        self.t0 = time.time()

    async def step(self, name: str, percent: float, **detail: Any) -> None:
        if self.engine._abort.is_set():
            raise Aborted()
        self.engine.progress.step = name
        self.engine.progress.percent = percent
        self.engine.progress.detail = detail
        await self.bus.publish("progress", run_id=self.run_id, test=self.test, step=name,
                               percent=percent, **detail)

    async def dispense(self, reagent_id: str, ul: float) -> float:
        """Dispense through the reagent's pump and book the consumption."""
        reagent = self.cfg.chemistry.reagent(reagent_id)
        delivered = await self.hw.dispense(reagent.pump, ul)
        remaining = self.db.consume_reagent(reagent_id, delivered / 1000.0)
        if remaining <= reagent.bottle_ml * reagent.low_fraction:
            await self.bus.publish("reagent_low", reagent=reagent_id, remaining_ml=remaining)
        return delivered

    def elapsed(self) -> float:
        return time.time() - self.t0


Procedure = Callable[[Context], Awaitable[Dict[str, Any]]]


class Engine:
    def __init__(self, cfg: AppConfig, hw: Hardware, db: Database, bus: EventBus):
        self.cfg = cfg
        self.hw = hw
        self.db = db
        self.bus = bus
        self.progress = Progress()
        self._lock = asyncio.Lock()
        self._abort = asyncio.Event()
        self._task: Optional[asyncio.Task] = None
        self.last_error: Optional[str] = None

    @property
    def busy(self) -> bool:
        return self._lock.locked()

    async def run(self, test: str, proc: Procedure, trigger: str = "api") -> Dict[str, Any]:
        """Run `proc` exclusively. Returns the procedure's result dict."""
        if self._lock.locked():
            raise RuntimeError("engine busy")
        async with self._lock:
            self._abort.clear()
            run_id = self.db.start_run(test, trigger)
            self.progress = Progress(run_id=run_id, test=test, step="starting", started=time.time())
            await self.bus.publish("run_started", run_id=run_id, test=test, trigger=trigger)
            ctx = Context(self, test, run_id)
            try:
                self.hw.check_safety()
                result = await proc(ctx)
                self.db.end_run(run_id, "done")
                await self.bus.publish("run_finished", run_id=run_id, test=test, status="done")
                return result
            except Aborted:
                self.db.end_run(run_id, "aborted")
                await self._safe_shutdown()
                await self.bus.publish("run_finished", run_id=run_id, test=test, status="aborted")
                raise
            except SafetyStop as e:
                self.last_error = str(e)
                self.db.end_run(run_id, "failed", str(e))
                await self._safe_shutdown()
                await self.hw.set_alarm(True)
                await self.bus.publish("alert", level="critical", code="safety_stop", message=str(e),
                                       run_id=run_id, test=test)
                await self.bus.publish("run_finished", run_id=run_id, test=test, status="failed", error=str(e))
                raise
            except Exception as e:
                self.last_error = f"{e}\n{traceback.format_exc()}"
                self.db.end_run(run_id, "failed", str(e))
                await self._safe_shutdown()
                await self.bus.publish("run_finished", run_id=run_id, test=test, status="failed", error=str(e))
                raise
            finally:
                self.progress = Progress(step="idle")

    def start_background(self, test: str, proc: Procedure, trigger: str = "api") -> asyncio.Task:
        if self._lock.locked():
            raise RuntimeError("engine busy")
        self._task = asyncio.create_task(self._bg(test, proc, trigger))
        return self._task

    async def _bg(self, test: str, proc: Procedure, trigger: str) -> None:
        try:
            await self.run(test, proc, trigger)
        except Exception as e:
            log.warning("background run %s ended: %s", test, e)

    def abort(self) -> bool:
        if not self._lock.locked():
            return False
        self._abort.set()
        self.hw.emergency_stop()
        return True

    async def _safe_shutdown(self) -> None:
        try:
            await self.hw.all_off()
        finally:
            self.hw.clear_estop()
