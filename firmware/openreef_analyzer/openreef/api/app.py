"""FastAPI application: REST + WebSocket API and the built-in dashboard.

Run with `openreef serve` (see main.py).  OpenAPI docs at /docs, schema at /openapi.json.
"""
from __future__ import annotations

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query, Request, WebSocket, WebSocketDisconnect, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse
from fastapi.security import APIKeyHeader

from .. import __version__
from ..config import AppConfig, ScheduleEntry
from ..db import Database
from ..events import EventBus
from ..hal import SimHardware, build_hardware
from ..integrations import HydrosClient, Webhooks
from ..scheduler import Scheduler
from ..sequences import Engine, procedures as P
from . import schemas as S

log = logging.getLogger(__name__)
WEB_DIR = Path(__file__).resolve().parent.parent / "web"


class AppState:
    def __init__(self, cfg: AppConfig):
        self.cfg = cfg
        self.bus = EventBus()
        self.db = Database(cfg.db_path)
        self.hw = build_hardware(cfg, cfg.sim_speedup)
        self.engine = Engine(cfg, self.hw, self.db, self.bus)
        self.scheduler = Scheduler(cfg.schedule, self.start_test)
        self.hydros: Optional[HydrosClient] = HydrosClient(cfg.hydros) if cfg.hydros.enabled else None
        self.webhooks = Webhooks(cfg.webhooks)
        self.mqtt = None
        self.started = time.time()
        for r in cfg.chemistry.reagents:
            if not self.db.reagent(r.id):
                self.db.upsert_reagent(r.id, r.name, r.bottle_ml, r.remaining_ml, r.pump)
            else:
                self.db.upsert_reagent(r.id, r.name, r.bottle_ml, self.db.reagent(r.id)["remaining_ml"], r.pump)

    async def start(self) -> None:
        await self.hw.start()
        self.bus.subscribe(self._persist_event)
        self.bus.subscribe(self.webhooks.handle_event)
        if self.hydros:
            self.bus.subscribe(self._hydros_event)
        if self.cfg.mqtt.enabled:
            try:
                from ..integrations.mqtt import MqttBridge
                self.mqtt = MqttBridge(self.cfg.mqtt)
                self.mqtt.start()
                self.bus.subscribe(self.mqtt.handle_event)
            except Exception as e:  # pragma: no cover
                log.warning("MQTT disabled: %s", e)
        self.scheduler.start()
        await self.bus.publish("service_started", version=__version__, backend=self.cfg.hardware.backend)

    async def stop(self) -> None:
        self.scheduler.stop()
        if self.mqtt:
            self.mqtt.stop()
        await self.webhooks.close()
        if self.hydros:
            await self.hydros.close()
        await self.hw.stop()
        self.db.close()

    async def _persist_event(self, evt: Dict[str, Any]) -> None:
        if evt["type"] != "progress":
            self.db.add_event(evt["type"], evt)

    async def _hydros_event(self, evt: Dict[str, Any]) -> None:
        if evt["type"] == "result" and self.hydros:
            actions = await self.hydros.apply_rules(evt["test"], evt["value"])
            if actions:
                await self.bus.publish("hydros_action", actions=actions)

    # -- test launcher used by API and scheduler -------------------------------
    def procedure_for(self, test: str):
        return {
            "alkalinity": P.alkalinity,
            "phosphate": lambda c: P.colorimetric(c, "phosphate"),
            "nitrate": lambda c: P.colorimetric(c, "nitrate"),
            "full": P.full_cycle,
        }[test]

    async def start_test(self, test: str, trigger: str = "api") -> int:
        if self.engine.busy:
            raise RuntimeError("a run is already in progress")
        task = self.engine.start_background(test, self.procedure_for(test), trigger)
        await asyncio.sleep(0.05)       # let run() allocate the run id
        return self.engine.progress.run_id or -1


def create_app(cfg: AppConfig) -> FastAPI:
    state = AppState(cfg)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        await state.start()
        try:
            yield
        finally:
            await state.stop()

    app = FastAPI(title="OpenReef Analyzer API", version=__version__, lifespan=lifespan,
                  description="Automated alkalinity / nitrate / phosphate analyzer for reef aquaria. "
                              "All endpoints are under /api/v1; live events on /ws/events.")
    app.state.openreef = state
    app.add_middleware(CORSMiddleware, allow_origins=cfg.api.cors_origins, allow_methods=["*"],
                       allow_headers=["*"])

    # ------------------------------------------------------------------ auth
    header_scheme = APIKeyHeader(name="X-API-Key", auto_error=False)

    async def auth(request: Request, key: Optional[str] = Depends(header_scheme)) -> None:
        if not cfg.api.api_keys:
            return
        k = key or request.query_params.get("api_key")
        if k not in cfg.api.api_keys:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid or missing API key")

    dep = [Depends(auth)]
    v1 = "/api/v1"

    def busy_guard():
        if state.engine.busy:
            raise HTTPException(status.HTTP_409_CONFLICT, "analyzer busy; abort or wait")

    # ------------------------------------------------------------------ dashboard
    @app.get("/", include_in_schema=False)
    async def index() -> FileResponse:
        return FileResponse(WEB_DIR / "index.html")

    @app.get("/healthz", include_in_schema=False)
    async def healthz():
        return {"ok": True}

    # ------------------------------------------------------------------ system
    @app.get(f"{v1}/health", tags=["system"])
    async def health():
        return {"ok": True, "version": __version__, "uptime_s": round(time.time() - state.started),
                "backend": cfg.hardware.backend, "busy": state.engine.busy}

    @app.get(f"{v1}/status", tags=["system"], dependencies=dep)
    async def status_():
        return {
            "progress": state.engine.progress.as_dict(),
            "hardware": state.hw.status(),
            "latest": state.db.latest(),
            "reagents": reagents_view(),
            "schedule": {"enabled": state.scheduler.enabled, "upcoming": state.scheduler.upcoming(5)},
            "limits": cfg.limits.model_dump(),
            "last_error": state.engine.last_error,
        }

    @app.get(f"{v1}/config", tags=["system"], dependencies=dep)
    async def get_config():
        d = cfg.model_dump()
        d["hydros"]["provider_key"] = "***" if d["hydros"]["provider_key"] else ""
        d["hydros"]["device_key"] = "***" if d["hydros"]["device_key"] else ""
        d["api"]["api_keys"] = ["***"] * len(d["api"]["api_keys"])
        d["mqtt"]["password"] = "***" if d["mqtt"].get("password") else None
        return d

    @app.put(f"{v1}/config/limits", tags=["system"], dependencies=dep)
    async def put_limits(body: S.Limits):
        for k, v in body.model_dump().items():
            if len(v) != 2 or v[0] >= v[1]:
                raise HTTPException(422, f"{k} must be [low, high]")
            setattr(cfg.limits, k, v)
        state.db.set_setting("limits", cfg.limits.model_dump())
        return cfg.limits.model_dump()

    # ------------------------------------------------------------------ tests / runs
    @app.post(f"{v1}/tests/{{test}}", tags=["tests"], dependencies=dep, response_model=S.StartTestResponse,
              status_code=202)
    async def start_test(test: str):
        if test not in ("alkalinity", "phosphate", "nitrate", "full"):
            raise HTTPException(404, "unknown test")
        busy_guard()
        run_id = await state.start_test(test, "api")
        return S.StartTestResponse(run_id=run_id, test=test)

    @app.post(f"{v1}/tests/abort", tags=["tests"], dependencies=dep)
    async def abort():
        return {"aborted": state.engine.abort()}

    @app.get(f"{v1}/runs", tags=["tests"], dependencies=dep)
    async def runs(limit: int = Query(50, le=500)):
        return state.db.runs(limit)

    @app.get(f"{v1}/runs/current", tags=["tests"], dependencies=dep, response_model=S.Progress)
    async def current():
        return state.engine.progress.as_dict()

    # ------------------------------------------------------------------ results
    @app.get(f"{v1}/results", tags=["results"], dependencies=dep, response_model=List[S.Result])
    async def results(test: Optional[str] = None, since: Optional[float] = None,
                      until: Optional[float] = None, limit: int = Query(200, le=5000)):
        return state.db.results(test, since, until, limit)

    @app.get(f"{v1}/results/latest", tags=["results"], dependencies=dep)
    async def latest():
        return state.db.latest()

    @app.get(f"{v1}/results/export.csv", tags=["results"], dependencies=dep)
    async def export_csv(test: Optional[str] = None):
        return PlainTextResponse(state.db.export_csv(test), media_type="text/csv")

    @app.get(f"{v1}/results/{{rid}}", tags=["results"], dependencies=dep, response_model=S.Result)
    async def result(rid: int):
        r = state.db.result(rid)
        if not r:
            raise HTTPException(404)
        return r

    # ------------------------------------------------------------------ calibration
    @app.get(f"{v1}/calibration", tags=["calibration"], dependencies=dep)
    async def calibrations(test: Optional[str] = None):
        return {
            "records": state.db.calibrations(test),
            "acid_normality": state.db.get_setting("acid_normality", cfg.chemistry.alkalinity.acid_normality),
            "phosphate": {"coeffs": state.db.get_setting("phosphate_cal_coeffs", cfg.chemistry.phosphate.cal_coeffs),
                          "points": state.db.get_setting("phosphate_cal_points", [])},
            "nitrate": {"coeffs": state.db.get_setting("nitrate_cal_coeffs", cfg.chemistry.nitrate.cal_coeffs),
                        "points": state.db.get_setting("nitrate_cal_points", [])},
        }

    @app.post(f"{v1}/calibration/ph", tags=["calibration"], dependencies=dep)
    async def calibrate_ph(body: S.PhCalibration):
        busy_guard()
        if hasattr(state.hw, "ezo_calibrate"):
            msg = await state.hw.ezo_calibrate(body.point, body.value)   # type: ignore[attr-defined]
        else:
            msg = "simulated"
        state.db.add_calibration("alkalinity", "ph_electrode", {"point": body.point, "value": body.value, "msg": msg})
        return {"ok": True, "message": msg}

    @app.post(f"{v1}/calibration/alkalinity/standardize", tags=["calibration"], dependencies=dep, status_code=202)
    async def standardize(body: S.StandardizeAcid):
        busy_guard()
        state.engine.start_background("alkalinity_standardize",
                                      lambda c: P.alkalinity(c, standard_ta_meq_l=body.known_ta_meq_l),
                                      "calibration")
        await asyncio.sleep(0.05)
        return {"run_id": state.engine.progress.run_id}

    @app.post(f"{v1}/calibration/{{test}}/point", tags=["calibration"], dependencies=dep, status_code=202)
    async def cal_point(test: S.TestName, body: S.CalPoint):
        if test == "alkalinity":
            raise HTTPException(422, "use /calibration/alkalinity/standardize")
        busy_guard()
        state.engine.start_background(f"{test}_calibration",
                                      lambda c: P.colorimetric(c, test, standard_ppm=body.standard_ppm),
                                      "calibration")
        await asyncio.sleep(0.05)
        return {"run_id": state.engine.progress.run_id}

    @app.post(f"{v1}/calibration/{{test}}/fit", tags=["calibration"], dependencies=dep)
    async def cal_fit(test: S.TestName, body: S.CalFit):
        from ..chem import fit_calibration
        pts = state.db.get_setting(f"{test}_cal_points", [])
        try:
                coeffs, r2 = fit_calibration([(p["abs"], p["ppm"]) for p in pts], body.degree, body.through_zero)
        except ValueError as e:
            raise HTTPException(422, f"{e} (have {len(pts)})")
        state.db.set_setting(f"{test}_cal_coeffs", coeffs)
        ratios = [p["secondary_ratio"] for p in pts if p.get("secondary_ratio")]
        if ratios:
            state.db.set_setting(f"{test}_secondary_ratio", sum(ratios) / len(ratios))
        cal_id = state.db.add_calibration(test, "curve", {"coeffs": coeffs, "r2": r2, "points": pts})
        await state.bus.publish("calibration", test=test, kind="curve", coeffs=coeffs, r2=r2)
        return {"coeffs": coeffs, "r2": r2, "n": len(pts), "calibration_id": cal_id}

    @app.delete(f"{v1}/calibration/{{test}}/points", tags=["calibration"], dependencies=dep)
    async def cal_clear(test: S.TestName):
        state.db.set_setting(f"{test}_cal_points", [])
        return {"ok": True}

    @app.post(f"{v1}/calibration/{{test}}/characterize", tags=["calibration"], dependencies=dep, status_code=202)
    async def characterize(test: S.TestName, body: S.Characterize):
        if test == "alkalinity":
            raise HTTPException(422, "characterization is for colorimetric tests")
        busy_guard()
        state.engine.start_background(f"{test}_characterize",
                                      lambda c: P.characterize(c, test, body.standard_ppm, body.minutes, body.every_s),
                                      "calibration")
        await asyncio.sleep(0.05)
        return {"run_id": state.engine.progress.run_id}

    # ------------------------------------------------------------------ reagents
    def reagents_view() -> List[Dict[str, Any]]:
        out = []
        per_test = {"hcl": 3.0, "np_r1": 0.5, "np_r2": 0.5, "np_r3a": 0.4, "np_r3b": 0.4}
        for r in state.db.reagents():
            use = per_test.get(r["id"], 0.5)
            r = dict(r)
            r["tests_remaining"] = int(r["remaining_ml"] / use) if use else None
            r["fraction"] = round(r["remaining_ml"] / r["bottle_ml"], 3) if r["bottle_ml"] else None
            out.append(r)
        return out

    @app.get(f"{v1}/reagents", tags=["reagents"], dependencies=dep)
    async def reagents():
        return reagents_view()

    @app.post(f"{v1}/reagents/{{rid}}/refill", tags=["reagents"], dependencies=dep)
    async def refill(rid: str, body: S.Refill):
        try:
            r = state.db.refill_reagent(rid, body.remaining_ml)
        except KeyError:
            raise HTTPException(404)
        await state.bus.publish("reagent_refilled", reagent=rid, remaining_ml=r["remaining_ml"])
        return r

    @app.post(f"{v1}/reagents/{{rid}}/prime", tags=["reagents"], dependencies=dep, status_code=202)
    async def prime(rid: str):
        try:
            cfg.chemistry.reagent(rid)
        except KeyError:
            raise HTTPException(404)
        busy_guard()
        state.engine.start_background(f"prime_{rid}", lambda c: P.prime(c, rid), "maintenance")
        await asyncio.sleep(0.05)
        return {"run_id": state.engine.progress.run_id}

    # ------------------------------------------------------------------ hardware
    @app.get(f"{v1}/hardware", tags=["hardware"], dependencies=dep)
    async def hardware():
        return state.hw.status()

    @app.post(f"{v1}/hardware/pump", tags=["hardware"], dependencies=dep)
    async def pump(body: S.PumpCmd):
        busy_guard()
        try:
            cfg.hardware.dc_channel(body.name)
        except KeyError:
            raise HTTPException(404, "unknown channel")
        if body.ml:
            await state.hw.pump_ml(body.name, body.ml)
        else:
            await state.hw.dc_run(body.name, body.seconds or 1.0)
        return {"ok": True}

    @app.post(f"{v1}/hardware/dispense", tags=["hardware"], dependencies=dep)
    async def dispense(body: S.DispenseCmd):
        busy_guard()
        if body.pump not in state.hw.syringes:
            raise HTTPException(404, "unknown pump")
        if not state.hw.syringes[body.pump].homed:
            await state.hw.home(body.pump)
        delivered = await state.hw.dispense(body.pump, body.ul)
        return {"delivered_ul": delivered}

    @app.post(f"{v1}/hardware/home", tags=["hardware"], dependencies=dep, status_code=202)
    async def home():
        busy_guard()
        state.engine.start_background("home", P.home_all, "maintenance")
        await asyncio.sleep(0.05)
        return {"run_id": state.engine.progress.run_id}

    @app.post(f"{v1}/hardware/flush", tags=["hardware"], dependencies=dep, status_code=202)
    async def flush():
        busy_guard()
        state.engine.start_background("flush", P.flush, "maintenance")
        await asyncio.sleep(0.05)
        return {"run_id": state.engine.progress.run_id}

    @app.post(f"{v1}/hardware/led", tags=["hardware"], dependencies=dep)
    async def led(body: S.LedCmd):
        await state.hw.set_led(body.led, body.on)
        return {"ok": True}

    @app.get(f"{v1}/hardware/ph", tags=["hardware"], dependencies=dep)
    async def read_ph():
        return {"ph": await state.hw.read_ph(), "temp_c": await state.hw.read_temp_c()}

    @app.get(f"{v1}/hardware/spectral", tags=["hardware"], dependencies=dep)
    async def read_spectral(led: Optional[str] = None):
        if led in ("white", "ir"):
            return await state.hw.read_absorbance_counts(led, averages=8)   # type: ignore[arg-type]
        return await state.hw.read_spectral()

    @app.post(f"{v1}/hardware/alarm", tags=["hardware"], dependencies=dep)
    async def alarm(body: S.AlarmCmd):
        await state.hw.set_alarm(body.on)
        return {"alarm": body.on}

    @app.post(f"{v1}/hardware/estop", tags=["hardware"], dependencies=dep)
    async def estop():
        state.engine.abort()
        await state.hw.all_off()
        return {"ok": True}

    # ------------------------------------------------------------------ schedule
    @app.get(f"{v1}/schedule", tags=["schedule"], dependencies=dep)
    async def schedule():
        return {"enabled": state.scheduler.enabled,
                "entries": [e.model_dump() for e, _ in state.scheduler.entries],
                "upcoming": state.scheduler.upcoming(10), "last_fired": state.scheduler.last_fired}

    @app.put(f"{v1}/schedule", tags=["schedule"], dependencies=dep)
    async def put_schedule(entries: List[S.ScheduleEntryIn]):
        new = [ScheduleEntry(**e.model_dump()) for e in entries]
        state.scheduler.stop()
        state.scheduler = Scheduler(new, state.start_test)
        state.scheduler.start()
        state.db.set_setting("schedule", [e.model_dump() for e in new])
        return {"entries": [e.model_dump() for e in new]}

    @app.post(f"{v1}/schedule/pause", tags=["schedule"], dependencies=dep)
    async def pause():
        state.scheduler.enabled = False
        return {"enabled": False}

    @app.post(f"{v1}/schedule/resume", tags=["schedule"], dependencies=dep)
    async def resume():
        state.scheduler.enabled = True
        return {"enabled": True}

    # ------------------------------------------------------------------ events
    @app.get(f"{v1}/events", tags=["events"], dependencies=dep)
    async def events(limit: int = Query(100, le=1000), type: Optional[str] = None):
        return state.db.events(limit, type)

    @app.websocket("/ws/events")
    async def ws_events(ws: WebSocket):
        if cfg.api.api_keys and ws.query_params.get("api_key") not in cfg.api.api_keys:
            await ws.close(code=4401)
            return
        await ws.accept()
        q = state.bus.queue()
        try:
            await ws.send_json({"type": "hello", "progress": state.engine.progress.as_dict(),
                                "latest": state.db.latest()})
            while True:
                evt = await q.get()
                await ws.send_json(evt)
        except WebSocketDisconnect:
            pass
        finally:
            state.bus.unqueue(q)

    # ------------------------------------------------------------------ integrations
    @app.get(f"{v1}/hydros/device", tags=["hydros"], dependencies=dep)
    async def hydros_device():
        if not state.hydros:
            raise HTTPException(404, "Hydros integration disabled")
        return await state.hydros.device()

    @app.get(f"{v1}/hydros/state", tags=["hydros"], dependencies=dep)
    async def hydros_state():
        if not state.hydros:
            raise HTTPException(404, "Hydros integration disabled")
        return await state.hydros.state()

    @app.post(f"{v1}/hydros/override", tags=["hydros"], dependencies=dep)
    async def hydros_override(body: S.HydrosOverride):
        if not state.hydros:
            raise HTTPException(404, "Hydros integration disabled")
        return await state.hydros.override(body.output, body.state, body.minutes)

    # ------------------------------------------------------------------ simulator
    @app.post(f"{v1}/sim/tank", tags=["simulator"], dependencies=dep)
    async def sim_tank(body: S.SimTank):
        if not isinstance(state.hw, SimHardware):
            raise HTTPException(404, "not running the simulator")
        for k in ("alk_dkh", "no3_ppm", "po4_ppm", "temp_c"):
            v = getattr(body, k)
            if v is not None:
                setattr(state.hw.tank, k, v)
        if body.leak is not None:
            state.hw.inject_leak(body.leak)
        return state.hw.tank.__dict__

    # ------------------------------------------------------------------ metrics
    @app.get("/metrics", include_in_schema=False)
    async def metrics():
        lines = []
        for test, r in state.db.latest().items():
            lines.append(f'openreef_value{{test="{test}",unit="{r["unit"]}"}} {r["value"]}')
            lines.append(f'openreef_quality{{test="{test}"}} {r["quality"]}')
            lines.append(f'openreef_result_age_seconds{{test="{test}"}} {time.time() - r["ts"]:.0f}')
        for r in state.db.reagents():
            lines.append(f'openreef_reagent_ml{{reagent="{r["id"]}"}} {r["remaining_ml"]:.2f}')
        hw = state.hw.status()
        lines.append(f'openreef_alarm {int(bool(hw["alarm"]))}')
        lines.append(f'openreef_busy {int(state.engine.busy)}')
        return PlainTextResponse("\n".join(lines) + "\n", media_type="text/plain; version=0.0.4")

    return app
