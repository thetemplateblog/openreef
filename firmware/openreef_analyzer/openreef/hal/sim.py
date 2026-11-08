"""Simulated hardware with a small chemistry model.

Good enough to exercise every sequence end-to-end: the alkalinity titration
produces a realistic pH curve (carbonate system + excess acid), and the optical
cell develops colour with first-order kinetics so the Gran fit and absorbance
math are tested against known inputs.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Dict, Optional

from ..config import HardwareConfig
from .base import Hardware, Led, SyringeState, SPECTRAL_CHANNELS

# Seawater carbonate constants (approx, 25 C, S=35, free scale)
K1 = 10 ** -5.86
K2 = 10 ** -8.92
KW = 10 ** -13.2

# Effective absorbance per ppm in the 22 mm cell after reagent dilution.
PO4_A_PER_PPM = 0.47        # molybdenum blue, 880 nm
NO3_A_PER_PPM = 0.020       # azo dye at 540 nm, kit-diluted so 50 ppm ~ 1.0 A

# Spectral shape of each dye across AS7341 channels (fraction of peak absorbance).
PO4_SHAPE = {"f1_415": 0.02, "f2_445": 0.02, "f3_480": 0.02, "f4_515": 0.03, "f5_555": 0.05,
             "f6_590": 0.12, "f7_630": 0.35, "f8_680": 0.65, "clear": 0.25, "nir": 1.0}
NO3_SHAPE = {"f1_415": 0.10, "f2_445": 0.15, "f3_480": 0.30, "f4_515": 0.85, "f5_555": 1.0,
             "f6_590": 0.45, "f7_630": 0.10, "f8_680": 0.03, "clear": 0.35, "nir": 0.01}

# LED spectra reaching the sensor through DI water (counts at gain 64 / 100 ms).
I0_WHITE = {"f1_415": 9000, "f2_445": 22000, "f3_480": 26000, "f4_515": 30000, "f5_555": 34000,
            "f6_590": 31000, "f7_630": 26000, "f8_680": 18000, "clear": 60000, "nir": 2500}
I0_IR = {"f1_415": 80, "f2_445": 90, "f3_480": 100, "f4_515": 120, "f5_555": 140,
         "f6_590": 180, "f7_630": 260, "f8_680": 900, "clear": 9000, "nir": 42000}
DARK = {c: 35.0 for c in SPECTRAL_CHANNELS}


@dataclass
class TankState:
    alk_dkh: float = 8.3
    no3_ppm: float = 5.0
    po4_ppm: float = 0.08
    temp_c: float = 25.4
    salinity_ppt: float = 35.0


@dataclass
class CellState:
    volume_ml: float = 0.0                       # liquid present
    max_ml: float = 30.0                         # overflow limit
    # cell A chemistry
    ta_meq: float = 0.0                          # total alkalinity, meq (absolute amount)
    acid_meq: float = 0.0                        # acid added, meq
    # cell B chemistry
    analyte: Optional[str] = None                # "po4" | "no3"
    analyte_ppm_in_sample: float = 0.0
    reagent_ul: Dict[str, float] = field(default_factory=dict)
    reagent_t: Optional[float] = None            # sim time when reagent complete
    reagents_needed: int = 2


class SimHardware(Hardware):
    def __init__(self, cfg: HardwareConfig, speedup: float = 1.0, seed: int = 7):
        super().__init__(cfg, speedup)
        self.rng = random.Random(seed)
        self.tank = TankState()
        self.cells: Dict[str, CellState] = {
            "A": CellState(max_ml=cfg.cell("A").volume_ml * 1.5),
            "B": CellState(max_ml=cfg.cell("B").volume_ml * 1.5),
        }
        self._plunger_steps: Dict[str, int] = {s.name: 0 for s in cfg.steppers}  # 0 = fully retracted (home)
        self._t = 0.0                   # simulated seconds
        self._leak = False
        self._waste_ml = 0.0
        self._waste_capacity_ml = 2000.0
        self.ph_noise = 0.002
        self.counts_noise = 0.0008

    # ---------------------------------------------------------------- time
    async def sleep(self, seconds: float) -> None:
        self._t += seconds
        await super().sleep(seconds)

    # ---------------------------------------------------------------- safety
    def leak_detected(self) -> bool:
        return self._leak

    def waste_full(self) -> bool:
        return self._waste_ml >= self._waste_capacity_ml

    async def set_alarm(self, on: bool) -> None:
        self._alarm = on

    def inject_leak(self, on: bool = True) -> None:
        self._leak = on

    # ---------------------------------------------------------------- DC loads
    async def _dc_write(self, pin: int, on: bool) -> None:
        pass  # state is tracked in base; effects applied in dc_run below

    async def dc_run(self, name: str, seconds: float) -> None:
        ch = self.cfg.dc_channel(name)
        await super().dc_run(name, seconds)
        if ch.cell is None:
            return
        cell = self.cells[ch.cell]
        ml = ch.ml_per_s * seconds
        if ch.role == "fill":
            self._fill(cell, ml)
        elif ch.role == "level":
            target = self.cfg.cell(ch.cell).volume_ml * (1 + self.rng.gauss(0, 0.004))
            if cell.volume_ml > target and ml > (cell.volume_ml - target):
                removed = cell.volume_ml - target
                self._scale_cell(cell, target / cell.volume_ml)
                self._waste_ml += removed
            elif cell.volume_ml > target:
                self._scale_cell(cell, (cell.volume_ml - ml) / cell.volume_ml)
                self._waste_ml += ml
        elif ch.role == "drain":
            removed = min(ml, cell.volume_ml)
            self._waste_ml += removed
            if ml >= cell.volume_ml:
                self._empty(cell)
            else:
                self._scale_cell(cell, (cell.volume_ml - ml) / cell.volume_ml)

    def _fill(self, cell: CellState, ml: float) -> None:
        """Add tank water. Everything above max_ml overflows to waste."""
        ta_meq_per_ml = self.tank.alk_dkh / 2.8 / 1000.0      # meq/mL
        new_total = cell.volume_ml + ml
        cell.ta_meq += ml * ta_meq_per_ml
        if cell.volume_ml == 0 or cell.analyte is None:
            cell.analyte = None
        # fresh sample dilutes any residual reagent/acid
        if new_total > cell.max_ml:
            overflow = new_total - cell.max_ml
            self._scale_cell(cell, cell.max_ml / new_total, keep_volume=cell.max_ml)
            self._waste_ml += overflow
        else:
            cell.volume_ml = new_total

    def _scale_cell(self, cell: CellState, frac: float, keep_volume: Optional[float] = None) -> None:
        cell.ta_meq *= frac
        cell.acid_meq *= frac
        for k in cell.reagent_ul:
            cell.reagent_ul[k] *= frac
        cell.volume_ml = keep_volume if keep_volume is not None else cell.volume_ml * frac

    def _empty(self, cell: CellState) -> None:
        cell.volume_ml = 0.0
        cell.ta_meq = 0.0
        cell.acid_meq = 0.0
        cell.analyte = None
        cell.reagent_ul = {}
        cell.reagent_t = None

    # ---------------------------------------------------------------- steppers
    async def _steppers_enable(self, on: bool) -> None:
        pass

    def _home_switch(self, s: SyringeState) -> bool:
        return self._plunger_steps[s.cfg.name] <= 0

    async def _move_steps(self, s: SyringeState, steps: int, push: bool, speed_mm_s: float) -> None:
        name = s.cfg.name
        mm = steps / s.cfg.steps_per_mm
        await self.sleep(mm / max(speed_mm_s, 0.01))
        if push:
            self._plunger_steps[name] += steps
            ul = steps * s.cfg.ul_per_step
            self._deliver(s, ul)
        else:
            self._plunger_steps[name] = max(0, self._plunger_steps[name] - steps)

    def _deliver(self, s: SyringeState, ul: float) -> None:
        cell = self.cells[s.cfg.cell]
        rid = s.cfg.reagent or s.cfg.name
        if rid == "hcl":
            # 0.0200 N acid (the true normality the standardisation should recover)
            cell.acid_meq += ul * 1e-3 * 0.0200
        else:
            cell.reagent_ul[rid] = cell.reagent_ul.get(rid, 0.0) + ul
            if rid.startswith("np_r3"):
                cell.analyte = "po4"
                cell.analyte_ppm_in_sample = self.tank.po4_ppm
            elif rid.startswith("np_r"):
                cell.analyte = "no3"
                cell.analyte_ppm_in_sample = self.tank.no3_ppm
            if len(cell.reagent_ul) >= cell.reagents_needed:
                cell.reagent_t = self._t
        cell.volume_ml += ul * 1e-3

    # ---------------------------------------------------------------- sensors
    async def read_temp_c(self) -> float:
        return self.tank.temp_c + self.rng.gauss(0, 0.02)

    async def read_ph(self) -> float:
        cell = self.cells["A"]
        if cell.volume_ml <= 0:
            return 7.0 + self.rng.gauss(0, 0.05)       # electrode in air / storage
        v_l = cell.volume_ml / 1000.0
        ta = (cell.ta_meq - cell.acid_meq) / 1000.0 / v_l         # eq/L, may be negative
        ct = cell.ta_meq / 1000.0 / v_l * 0.92                    # DIC ~ 0.92 * initial TA
        h = _solve_h(ta, ct)
        return -math.log10(h) + self.rng.gauss(0, self.ph_noise)

    async def set_led(self, led: Led, on: bool) -> None:
        self._leds[led] = on

    async def read_spectral(self, gain: int = 64, integration_ms: float = 100.0,
                            averages: int = 8) -> Dict[str, float]:
        cell = self.cells["B"]
        out: Dict[str, float] = {}
        for ch in SPECTRAL_CHANNELS:
            i0 = 0.0
            if self._leds["white"]:
                i0 += I0_WHITE[ch]
            if self._leds["ir"]:
                i0 += I0_IR[ch]
            a = self._absorbance(cell, ch) if cell.volume_ml > 0 else 0.0
            if cell.volume_ml <= 0 and i0 > 0:
                i0 *= 1.08       # empty cell, no refraction loss
            counts = i0 * 10 ** (-a) + DARK[ch]
            noise = self.rng.gauss(0, self.counts_noise * counts + 0.3) / math.sqrt(averages)
            out[ch] = max(0.0, counts + noise)
        return out

    def _absorbance(self, cell: CellState, ch: str) -> float:
        if cell.analyte is None or cell.reagent_t is None:
            return 0.0
        dt = self._t - cell.reagent_t
        if cell.analyte == "po4":
            peak = PO4_A_PER_PPM * cell.analyte_ppm_in_sample
            frac = 1 - math.exp(-dt / 150.0)
            return peak * frac * PO4_SHAPE[ch]
        peak = NO3_A_PER_PPM * cell.analyte_ppm_in_sample
        frac = 1 - math.exp(-dt / 500.0)
        return peak * frac * NO3_SHAPE[ch]

    # ---------------------------------------------------------------- introspection
    def status(self) -> dict:
        d = super().status()
        d["sim"] = {
            "tank": self.tank.__dict__,
            "t_s": round(self._t, 1),
            "waste_ml": round(self._waste_ml, 1),
            "cells": {k: {"volume_ml": round(c.volume_ml, 2), "analyte": c.analyte,
                          "ta_meq": round(c.ta_meq, 4), "acid_meq": round(c.acid_meq, 4)}
                      for k, c in self.cells.items()},
        }
        return d


def _solve_h(ta: float, ct: float) -> float:
    """Solve the charge balance TA = HCO3 + 2 CO3 + OH - H for [H+] by bisection on pH."""
    def f(ph: float) -> float:
        h = 10 ** -ph
        denom = h * h + K1 * h + K1 * K2
        hco3 = ct * K1 * h / denom
        co3 = ct * K1 * K2 / denom
        return hco3 + 2 * co3 + KW / h - h - ta

    lo, hi = 1.0, 11.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if f(mid) > 0:
            hi = mid
        else:
            lo = mid
    return 10 ** -(0.5 * (lo + hi))
