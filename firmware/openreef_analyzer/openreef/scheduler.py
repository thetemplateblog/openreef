"""Minimal 5-field cron scheduler (minute hour day-of-month month day-of-week).
Supports `*`, lists `a,b`, ranges `a-b` and steps `*/n`. Local time."""
from __future__ import annotations

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Callable, Awaitable, List, Optional, Set

from .config import ScheduleEntry

log = logging.getLogger(__name__)


def _parse_field(field: str, lo: int, hi: int) -> Set[int]:
    out: Set[int] = set()
    for part in field.split(","):
        part = part.strip()
        step = 1
        if "/" in part:
            part, s = part.split("/")
            step = int(s)
        if part == "*":
            rng = range(lo, hi + 1)
        elif "-" in part:
            a, b = part.split("-")
            rng = range(int(a), int(b) + 1)
        else:
            rng = range(int(part), int(part) + 1)
        out.update(x for x in rng if (x - lo) % step == 0 or step == 1)
    return out


class Cron:
    def __init__(self, expr: str):
        f = expr.split()
        if len(f) != 5:
            raise ValueError(f"bad cron expression {expr!r}")
        self.minute = _parse_field(f[0], 0, 59)
        self.hour = _parse_field(f[1], 0, 23)
        self.dom = _parse_field(f[2], 1, 31)
        self.month = _parse_field(f[3], 1, 12)
        self.dow = _parse_field(f[4], 0, 6)        # 0 = Sunday

    def matches(self, dt: datetime) -> bool:
        return (dt.minute in self.minute and dt.hour in self.hour and dt.day in self.dom
                and dt.month in self.month and (dt.weekday() + 1) % 7 in self.dow)

    def next_after(self, dt: datetime) -> datetime:
        t = dt.replace(second=0, microsecond=0) + timedelta(minutes=1)
        for _ in range(60 * 24 * 366):
            if self.matches(t):
                return t
            t += timedelta(minutes=1)
        raise ValueError("no match within a year")


class Scheduler:
    def __init__(self, entries: List[ScheduleEntry], runner: Callable[[str, str], Awaitable[None]]):
        self.entries = [(e, Cron(e.cron)) for e in entries]
        self.runner = runner
        self._task: Optional[asyncio.Task] = None
        self.enabled = True
        self.last_fired: dict = {}

    def start(self) -> None:
        self._task = asyncio.create_task(self._loop())

    def stop(self) -> None:
        if self._task:
            self._task.cancel()

    def upcoming(self, n: int = 10) -> List[dict]:
        now = datetime.now()
        items = []
        for e, c in self.entries:
            if not e.enabled:
                continue
            t = now
            for _ in range(3):
                t = c.next_after(t)
                items.append({"test": e.test, "at": t.isoformat(timespec="minutes"), "ts": t.timestamp()})
        items.sort(key=lambda x: x["ts"])
        return items[:n]

    async def _loop(self) -> None:
        last_minute = None
        while True:
            now = datetime.now()
            key = now.strftime("%Y%m%d%H%M")
            if key != last_minute:
                last_minute = key
                if self.enabled:
                    for e, c in self.entries:
                        if e.enabled and c.matches(now):
                            log.info("schedule fired: %s", e.test)
                            self.last_fired[e.test] = time.time()
                            try:
                                await self.runner(e.test, "schedule")
                            except Exception as ex:
                                log.warning("scheduled %s not started: %s", e.test, ex)
            await asyncio.sleep(5)
