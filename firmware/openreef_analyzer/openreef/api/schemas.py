from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field

TestName = Literal["alkalinity", "phosphate", "nitrate"]


class StartTestResponse(BaseModel):
    run_id: int
    test: str
    status: str = "started"


class Progress(BaseModel):
    run_id: Optional[int]
    test: Optional[str]
    step: str
    percent: float
    started: Optional[float]
    elapsed_s: float
    detail: Dict[str, Any] = {}


class Result(BaseModel):
    id: int
    ts: float
    test: str
    value: Optional[float]
    unit: Optional[str]
    quality: Optional[float]
    flags: List[str] = []
    temp_c: Optional[float]
    duration_s: Optional[float]
    run_id: Optional[int]
    calibration_id: Optional[int]
    raw: Optional[Dict[str, Any]] = None


class PhCalibration(BaseModel):
    point: Literal["mid", "low", "high", "clear"]
    value: float = 7.0


class StandardizeAcid(BaseModel):
    known_ta_meq_l: float = Field(..., gt=0, description="e.g. 1.887 for 0.1 g/L Na2CO3")


class CalPoint(BaseModel):
    standard_ppm: float = Field(..., ge=0)


class CalFit(BaseModel):
    degree: int = Field(1, ge=1, le=2)
    through_zero: bool = True


class Characterize(BaseModel):
    standard_ppm: float = Field(..., gt=0)
    minutes: float = Field(40, ge=5, le=120)
    every_s: float = Field(30, ge=10, le=300)


class Refill(BaseModel):
    remaining_ml: Optional[float] = Field(None, ge=0)


class PumpCmd(BaseModel):
    name: str
    seconds: Optional[float] = Field(None, gt=0, le=120)
    ml: Optional[float] = Field(None, gt=0, le=200)


class DispenseCmd(BaseModel):
    pump: str
    ul: float = Field(..., gt=0, le=20000)


class LedCmd(BaseModel):
    led: Literal["white", "ir"]
    on: bool


class AlarmCmd(BaseModel):
    on: bool


class Limits(BaseModel):
    alk_dkh: List[float]
    no3_ppm: List[float]
    po4_ppm: List[float]


class ScheduleEntryIn(BaseModel):
    test: Literal["alkalinity", "phosphate", "nitrate", "full"]
    cron: str
    enabled: bool = True


class SimTank(BaseModel):
    alk_dkh: Optional[float] = None
    no3_ppm: Optional[float] = None
    po4_ppm: Optional[float] = None
    temp_c: Optional[float] = None
    leak: Optional[bool] = None


class HydrosOverride(BaseModel):
    output: str
    state: Literal["on", "off", "auto"] = "on"
    minutes: int = Field(30, ge=1, le=1440)
