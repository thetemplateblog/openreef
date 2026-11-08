import asyncio
import os
import tempfile

import pytest

from openreef.config import load_config
from openreef.db import Database
from openreef.events import EventBus
from openreef.hal import SimHardware
from openreef.sequences import Engine, procedures as P

CFG = os.path.join(os.path.dirname(__file__), "..", "config.example.yaml")


@pytest.fixture
def stack():
    cfg = load_config(CFG)
    cfg.sim_speedup = 400.0
    hw = SimHardware(cfg.hardware, speedup=cfg.sim_speedup)
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    db = Database(tmp.name)
    for r in cfg.chemistry.reagents:
        db.upsert_reagent(r.id, r.name, r.bottle_ml, r.remaining_ml, r.pump)
    bus = EventBus()
    eng = Engine(cfg, hw, db, bus)
    yield cfg, hw, db, bus, eng
    db.close()
    os.unlink(tmp.name)


async def test_alkalinity_recovers_tank_value(stack):
    cfg, hw, db, bus, eng = stack
    hw.tank.alk_dkh = 8.30
    res = await eng.run("alkalinity", P.alkalinity)
    assert res["unit"] == "dKH"
    assert abs(res["value"] - 8.30) < 0.08, res
    assert res["r2"] > 0.999
    assert round(db.latest()["alkalinity"]["value"], 3) == res["value"]
    # second run uses the first result to size the initial dose
    hw.tank.alk_dkh = 7.1
    res2 = await eng.run("alkalinity", P.alkalinity)
    assert abs(res2["value"] - 7.1) < 0.08, res2


async def test_acid_standardization(stack):
    cfg, hw, db, bus, eng = stack
    # pretend the configured normality is wrong by 5 %
    db.set_setting("acid_normality", 0.0210)
    hw.tank.alk_dkh = 5.28  # 1.887 meq/L Na2CO3 standard as the "tank"
    res = await eng.run("alkalinity", lambda c: P.alkalinity(c, standard_ta_meq_l=1.887))
    assert abs(res["acid_normality"] - 0.0200) < 0.0003, res
    assert db.get_setting("acid_normality") == res["acid_normality"]


async def test_phosphate_and_nitrate(stack):
    cfg, hw, db, bus, eng = stack
    # calibrate with two standards each, then measure the tank
    for ppm in (0.10, 0.50):
        hw.tank.po4_ppm = ppm
        await eng.run("phosphate", lambda c, p=ppm: P.colorimetric(c, "phosphate", standard_ppm=p))
    pts = db.get_setting("phosphate_cal_points")
    assert len(pts) == 2
    from openreef.chem import fit_calibration
    coeffs, r2 = fit_calibration([(p["abs"], p["ppm"]) for p in pts], degree=1, through_zero=True)
    db.set_setting("phosphate_cal_coeffs", coeffs)
    hw.tank.po4_ppm = 0.08
    res = await eng.run("phosphate", lambda c: P.colorimetric(c, "phosphate"))
    assert abs(res["value"] - 0.08) < 0.01, res

    for ppm in (5.0, 25.0):
        hw.tank.no3_ppm = ppm
        await eng.run("nitrate", lambda c, p=ppm: P.colorimetric(c, "nitrate", standard_ppm=p))
    pts = db.get_setting("nitrate_cal_points")
    coeffs, r2 = fit_calibration([(p["abs"], p["ppm"]) for p in pts], degree=1, through_zero=True)
    db.set_setting("nitrate_cal_coeffs", coeffs)
    hw.tank.no3_ppm = 12.0
    res = await eng.run("nitrate", lambda c: P.colorimetric(c, "nitrate"))
    assert abs(res["value"] - 12.0) < 0.8, res


async def test_reagent_accounting_and_events(stack):
    cfg, hw, db, bus, eng = stack
    q = bus.queue()
    before = db.reagent("hcl")["remaining_ml"]
    await eng.run("alkalinity", P.alkalinity)
    after = db.reagent("hcl")["remaining_ml"]
    assert 1.0 < before - after < 4.5          # ~3 mL of 0.02 N acid for 8.3 dKH / 20 mL
    types = set()
    while not q.empty():
        types.add(q.get_nowait()["type"])
    assert {"run_started", "progress", "result", "run_finished"} <= types


async def test_leak_aborts_run(stack):
    cfg, hw, db, bus, eng = stack
    hw.inject_leak(True)
    with pytest.raises(Exception):
        await eng.run("alkalinity", P.alkalinity)
    assert db.runs(1)[0]["status"] == "failed"
    assert hw.status()["alarm"] is True
