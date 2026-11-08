"""Hardware abstraction layer.

`Hardware` is the only thing the sequence engine talks to.  Two implementations
exist: `SimHardware` (a chemistry model so the whole stack runs on a laptop) and
`RpiHardware` (pigpio + I2C on a Raspberry Pi).  Shared syringe-pump bookkeeping
lives here so both backends behave identically.
"""
from __future__ import annotations

import abc
import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Dict, Literal, Optional

from ..config import HardwareConfig, StepperChannel

log = logging.getLogger(__name__)

Led = Literal["white", "ir"]

# AS7341 channel names used throughout the project (nm = filter centre).
SPECTRAL_CHANNELS = ("f1_415", "f2_445", "f3_480", "f4_515", "f5_555",
                     "f6_590", "f7_630", "f8_680", "clear", "nir")


class HardwareError(RuntimeError):
    pass


class SafetyStop(HardwareError):
    """Raised when the leak sensor or waste float trips mid-sequence."""


@dataclass
class SyringeState:
    cfg: StepperChannel
    position_ul: float = 0.0           # liquid currently in the syringe
    homed: bool = False
    total_dispensed_ul: float = 0.0
    refills: int = 0
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)


class Hardware(abc.ABC):
    """Async hardware interface. All volumes in microlitres, times in seconds."""

    def __init__(self, cfg: HardwareConfig, speedup: float = 1.0):
        self.cfg = cfg
        self.speedup = max(speedup, 1e-6)
        self.syringes: Dict[str, SyringeState] = {s.name: SyringeState(s) for s in cfg.steppers}
        self._dc_state: Dict[str, bool] = {d.name: False for d in cfg.dc}
        self._leds: Dict[str, bool] = {"white": False, "ir": False}
        self._alarm = False
        self._estop = False

    # ------------------------------------------------------------------ lifecycle
    async def start(self) -> None: ...
    async def stop(self) -> None:
        await self.all_off()

    async def all_off(self) -> None:
        for name in list(self._dc_state):
            try:
                await self.dc_off(name)
            except Exception:  # pragma: no cover - best effort
                log.exception("dc_off %s failed", name)
        for led in ("white", "ir"):
            await self.set_led(led, False)
        await self._steppers_enable(False)

    def emergency_stop(self) -> None:
        self._estop = True

    def clear_estop(self) -> None:
        self._estop = False

    # ------------------------------------------------------------------ timing
    async def sleep(self, seconds: float) -> None:
        """Sleep that honours the simulation speed-up and the e-stop."""
        remaining = seconds / self.speedup
        while remaining > 0:
            if self._estop:
                raise SafetyStop("emergency stop")
            chunk = min(remaining, 0.25)
            await asyncio.sleep(chunk)
            remaining -= chunk

    # ------------------------------------------------------------------ safety
    @abc.abstractmethod
    def leak_detected(self) -> bool: ...

    @abc.abstractmethod
    def waste_full(self) -> bool: ...

    def check_safety(self) -> None:
        if self._estop:
            raise SafetyStop("emergency stop")
        if self.leak_detected():
            raise SafetyStop("leak detected in drip tray")
        if self.waste_full():
            raise SafetyStop("waste container full")

    @abc.abstractmethod
    async def set_alarm(self, on: bool) -> None: ...

    # ------------------------------------------------------------------ DC loads
    @abc.abstractmethod
    async def _dc_write(self, pin: int, on: bool) -> None: ...

    async def dc_on(self, name: str) -> None:
        self.check_safety()
        ch = self.cfg.dc_channel(name)
        await self._dc_write(ch.pin, True)
        self._dc_state[name] = True

    async def dc_off(self, name: str) -> None:
        ch = self.cfg.dc_channel(name)
        await self._dc_write(ch.pin, False)
        self._dc_state[name] = False

    async def dc_run(self, name: str, seconds: float) -> None:
        await self.dc_on(name)
        try:
            await self.sleep(seconds)
        finally:
            await self.dc_off(name)

    async def pump_ml(self, name: str, ml: float) -> None:
        """Run a peristaltic pump long enough to move `ml` (timing based)."""
        ch = self.cfg.dc_channel(name)
        if ch.ml_per_s <= 0:
            raise HardwareError(f"{name} has no flow rate configured")
        await self.dc_run(name, ml / ch.ml_per_s)

    # ------------------------------------------------------------------ steppers
    @abc.abstractmethod
    async def _steppers_enable(self, on: bool) -> None: ...

    @abc.abstractmethod
    async def _move_steps(self, s: SyringeState, steps: int, push: bool, speed_mm_s: float) -> None:
        """Move the plunger `steps` microsteps. push=True expels liquid."""

    @abc.abstractmethod
    def _home_switch(self, s: SyringeState) -> bool: ...

    async def home(self, name: str) -> None:
        """Retract to the limit switch (syringe full) in two passes."""
        s = self.syringes[name]
        async with s.lock:
            await self._home_locked(s)

    async def _home_locked(self, s: SyringeState) -> None:
        await self._steppers_enable(True)
        # fast approach, then back off and slow approach for repeatability
        await self._seek_home(s, speed=s.cfg.max_speed_mm_s)
        await self._move_steps(s, int(0.5 * s.cfg.steps_per_mm), push=True, speed_mm_s=1.0)
        await self._seek_home(s, speed=0.5)
        s.position_ul = s.cfg.capacity_ul
        s.homed = True

    async def _seek_home(self, s: SyringeState, speed: float) -> None:
        limit = int((s.cfg.stroke_mm + 5) * s.cfg.steps_per_mm)
        chunk = max(1, int(0.2 * s.cfg.steps_per_mm))
        moved = 0
        while not self._home_switch(s):
            if moved >= limit:
                raise HardwareError(f"{s.cfg.name}: home switch not found")
            await self._move_steps(s, chunk, push=False, speed_mm_s=speed)
            moved += chunk

    async def dispense(self, name: str, ul: float, speed_mm_s: Optional[float] = None) -> float:
        """Dispense `ul` through the outlet check valve, refilling from the
        bottle as needed. Returns the volume actually delivered."""
        s = self.syringes[name]
        if ul <= 0:
            return 0.0
        self.check_safety()
        async with s.lock:
            await self._steppers_enable(True)
            if not s.homed:
                # Homing expels ~60 uL through the outlet; it must happen while the
                # cell is empty (procedures call ensure_homed before filling).
                raise HardwareError(f"{name} not homed; run home/prime before dispensing")
            speed = speed_mm_s or s.cfg.max_speed_mm_s
            remaining = ul
            delivered = 0.0
            while remaining > 1e-6:
                if s.position_ul < min(remaining, 1.0):
                    await self._refill(s)
                shot = min(remaining, s.position_ul)
                steps = int(round(shot / s.cfg.ul_per_step))
                if steps <= 0:
                    break
                await self._move_steps(s, steps, push=True, speed_mm_s=speed)
                actual = steps * s.cfg.ul_per_step
                s.position_ul -= actual
                remaining -= actual
                delivered += actual
            s.total_dispensed_ul += delivered
            return delivered

    async def _refill(self, s: SyringeState) -> None:
        """Pull the plunger back to the home switch: aspirates from the bottle
        through the inlet check valve. Then purge a little to clear air."""
        log.info("%s refilling syringe", s.cfg.name)
        await self._seek_home(s, speed=1.5)
        s.position_ul = s.cfg.capacity_ul
        s.refills += 1
        await self.sleep(0.5)   # let the check valve seat

    # ------------------------------------------------------------------ sensors
    @abc.abstractmethod
    async def read_ph(self) -> float: ...

    @abc.abstractmethod
    async def read_temp_c(self) -> float: ...

    @abc.abstractmethod
    async def set_led(self, led: Led, on: bool) -> None: ...

    @abc.abstractmethod
    async def read_spectral(self, gain: int = 64, integration_ms: float = 100.0,
                            averages: int = 8) -> Dict[str, float]: ...

    async def read_absorbance_counts(self, led: Led, averages: int = 16) -> Dict[str, float]:
        """Dark-subtracted counts for every channel with the given LED on."""
        await self.set_led(led, False)
        await self.sleep(0.05)
        dark = await self.read_spectral(averages=max(4, averages // 2))
        await self.set_led(led, True)
        await self.sleep(0.15)   # LED thermal settle
        lit = await self.read_spectral(averages=averages)
        await self.set_led(led, False)
        return {k: max(lit[k] - dark.get(k, 0.0), 1e-9) for k in lit}

    async def wait_ph_stable(self, dph_per_s: float, timeout_s: float, interval_s: float = 1.0):
        """Poll pH until drift is below threshold. Returns (pH, stable: bool)."""
        last = await self.read_ph()
        waited = 0.0
        while waited < timeout_s:
            await self.sleep(interval_s)
            waited += interval_s
            now = await self.read_ph()
            if abs(now - last) / interval_s < dph_per_s:
                return now, True
            last = now
        return last, False

    # ------------------------------------------------------------------ status
    def status(self) -> dict:
        return {
            "backend": self.cfg.backend,
            "estop": self._estop,
            "leak": self.leak_detected(),
            "waste_full": self.waste_full(),
            "alarm": self._alarm,
            "leds": dict(self._leds),
            "dc": dict(self._dc_state),
            "syringes": {
                n: {"position_ul": round(s.position_ul, 1), "homed": s.homed,
                    "total_dispensed_ul": round(s.total_dispensed_ul, 1), "refills": s.refills}
                for n, s in self.syringes.items()
            },
        }
