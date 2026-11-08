"""Configuration model for OpenReef.

Everything hardware-specific (GPIO numbers, I2C addresses, pump geometry, cell
volumes) and chemistry-specific (reagent profiles, calibration defaults) lives in
one YAML file so the same code runs on the bench, in the simulator and in tests.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List, Literal, Optional

import yaml
from pydantic import BaseModel, Field


# --------------------------------------------------------------------------- #
# Hardware
# --------------------------------------------------------------------------- #
class StepperChannel(BaseModel):
    """A stepper-driven syringe pump (self-refilling via two check valves)."""

    name: str
    step_pin: int
    dir_pin: int
    home_pin: int                      # MCP23017 pin (port A) for the limit switch
    steps_per_mm: float = 1600.0       # 200 steps * 16 microsteps / 2 mm lead
    syringe_bore_mm: float = 12.0      # 5 mL glass luer syringe
    stroke_mm: float = 45.0            # usable travel
    max_speed_mm_s: float = 2.5
    reagent: Optional[str] = None      # reagent id this pump dispenses
    cell: Literal["A", "B"] = "A"

    @property
    def ul_per_mm(self) -> float:
        import math
        return math.pi * (self.syringe_bore_mm / 2) ** 2  # mm^3 == uL

    @property
    def ul_per_step(self) -> float:
        return self.ul_per_mm / self.steps_per_mm

    @property
    def capacity_ul(self) -> float:
        return self.ul_per_mm * self.stroke_mm


class DcChannel(BaseModel):
    """A 12 V peristaltic pump or stirrer on the MOSFET board (MCP23017 port B)."""

    name: str
    pin: int
    ml_per_s: float = 0.0             # approximate flow for timing; 0 for stirrers
    cell: Optional[Literal["A", "B"]] = None
    role: Literal["fill", "level", "drain", "stir", "other"] = "other"


class Cell(BaseModel):
    name: Literal["A", "B"]
    volume_ml: float                   # set by the level dip tube
    path_mm: float = 0.0               # optical path (cell B)
    description: str = ""


class HardwareConfig(BaseModel):
    backend: Literal["sim", "rpi"] = "sim"
    i2c_bus: int = 1
    ezo_ph_addr: int = 0x63
    as7341_addr: int = 0x39
    mcp23017_addr: int = 0x20
    onewire_id: Optional[str] = None   # DS18B20 id, None = first found
    stepper_enable_pin: int = 17
    leak_pin: int = 26
    alarm_relay_pin: int = 20
    led_white_pin: int = 19
    led_ir_pin: int = 21
    heater_pwm_pin: Optional[int] = 18
    waste_float_mcp_pin: int = 5
    steppers: List[StepperChannel]
    dc: List[DcChannel]
    cells: List[Cell]

    def stepper(self, name: str) -> StepperChannel:
        for s in self.steppers:
            if s.name == name:
                return s
        raise KeyError(name)

    def dc_channel(self, name: str) -> DcChannel:
        for d in self.dc:
            if d.name == name:
                return d
        raise KeyError(name)

    def cell(self, name: str) -> Cell:
        for c in self.cells:
            if c.name == name:
                return c
        raise KeyError(name)


# --------------------------------------------------------------------------- #
# Chemistry
# --------------------------------------------------------------------------- #
class Reagent(BaseModel):
    id: str
    name: str
    bottle_ml: float
    remaining_ml: float
    pump: str                          # stepper channel name
    low_fraction: float = 0.10


class ColorimetricProfile(BaseModel):
    """How to run one colorimetric test with a given reagent set."""

    doses: List[Dict[str, float]]      # ordered list of {reagent_id: uL}
    mix_s: float = 20.0
    develop_s: float = 600.0
    led: Literal["white", "ir"] = "ir"
    primary_channel: str = "nir"       # AS7341 channel name
    secondary_channel: Optional[str] = "f8_680"
    temp_coeff_per_c: float = 0.0      # fractional absorbance change per deg C from 25
    # calibration: conc = c0 + c1*A + c2*A^2 (defaults are placeholders, overwritten by calibration)
    cal_coeffs: List[float] = Field(default_factory=lambda: [0.0, 1.0, 0.0])
    cal_abs_max: float = 1.2           # above this the reading is flagged "over-range"


class AlkalinityProfile(BaseModel):
    acid_reagent: str = "hcl"
    acid_normality: float = 0.0200     # eq/L, updated by standardisation
    sample_ml: float = 20.0
    initial_dose_ul: float = 900.0     # one jump to get near pH 4
    step_ul: float = 60.0
    gran_ph_min: float = 3.0
    gran_ph_max: float = 3.8
    min_points: int = 6
    max_points: int = 14
    stable_dph_per_s: float = 0.005
    stable_timeout_s: float = 25.0
    max_total_ul: float = 4000.0


class ChemistryConfig(BaseModel):
    reagents: List[Reagent]
    alkalinity: AlkalinityProfile = AlkalinityProfile()
    phosphate: ColorimetricProfile
    nitrate: ColorimetricProfile

    def reagent(self, rid: str) -> Reagent:
        for r in self.reagents:
            if r.id == rid:
                return r
        raise KeyError(rid)


# --------------------------------------------------------------------------- #
# Service
# --------------------------------------------------------------------------- #
class ScheduleEntry(BaseModel):
    test: Literal["alkalinity", "phosphate", "nitrate", "full"]
    cron: str                          # "min hour dom mon dow" (5-field, * or lists)
    enabled: bool = True


class HydrosConfig(BaseModel):
    enabled: bool = False
    base_url: str = "https://api.coralvuehydros.com"
    provider_key: str = ""
    device_key: str = ""
    poll_s: int = 300
    # output name on the Hydros to override when a rule fires, e.g. the alk doser outlet
    rules: List[Dict] = Field(default_factory=list)


class MqttConfig(BaseModel):
    enabled: bool = False
    host: str = "localhost"
    port: int = 1883
    username: Optional[str] = None
    password: Optional[str] = None
    base_topic: str = "openreef"
    ha_discovery: bool = True


class ApiConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8080
    api_keys: List[str] = Field(default_factory=list)   # empty list = open (LAN only!)
    cors_origins: List[str] = Field(default_factory=lambda: ["*"])


class Limits(BaseModel):
    """Alert thresholds; crossing one emits an `alert` event and drives the relay."""

    alk_dkh: List[float] = Field(default_factory=lambda: [7.5, 9.5])
    no3_ppm: List[float] = Field(default_factory=lambda: [2.0, 15.0])
    po4_ppm: List[float] = Field(default_factory=lambda: [0.03, 0.15])


class AppConfig(BaseModel):
    name: str = "OpenReef"
    db_path: str = "openreef.db"
    hardware: HardwareConfig
    chemistry: ChemistryConfig
    schedule: List[ScheduleEntry] = Field(default_factory=list)
    limits: Limits = Limits()
    hydros: HydrosConfig = HydrosConfig()
    mqtt: MqttConfig = MqttConfig()
    api: ApiConfig = ApiConfig()
    webhooks: List[str] = Field(default_factory=list)
    sim_speedup: float = 1.0           # >1 makes simulated waits shorter


DEFAULT_CONFIG_PATHS = [
    os.environ.get("OPENREEF_CONFIG", ""),
    "config.yaml",
    "/etc/openreef/config.yaml",
    str(Path(__file__).resolve().parent.parent / "config.example.yaml"),
]


def load_config(path: Optional[str] = None) -> AppConfig:
    candidates = [path] if path else DEFAULT_CONFIG_PATHS
    for p in candidates:
        if p and Path(p).exists():
            with open(p, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            return AppConfig.model_validate(data)
    raise FileNotFoundError("No config.yaml found; copy config.example.yaml")
