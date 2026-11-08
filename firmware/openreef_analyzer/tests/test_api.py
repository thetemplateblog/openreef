import asyncio
import os
import tempfile

import pytest
from httpx import ASGITransport, AsyncClient

from openreef.api import create_app
from openreef.config import load_config

CFG = os.path.join(os.path.dirname(__file__), "..", "config.example.yaml")


@pytest.fixture
async def client():
    cfg = load_config(CFG)
    cfg.sim_speedup = 400.0
    cfg.api.api_keys = ["testkey"]
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    cfg.db_path = tmp.name
    app = create_app(cfg)
    state = app.state.openreef
    await state.start()
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t",
                               headers={"X-API-Key": "testkey"}) as c:
            yield c, state
    finally:
        await state.stop()
        os.unlink(tmp.name)


async def test_auth_required(client):
    c, _ = client
    r = await c.get("/api/v1/status", headers={"X-API-Key": "wrong"})
    assert r.status_code == 401
    r = await c.get("/api/v1/health")          # health is open
    assert r.status_code == 200 and r.json()["ok"]


async def test_full_flow(client):
    c, state = client
    r = await c.get("/api/v1/status")
    assert r.status_code == 200 and r.json()["progress"]["step"] == "idle"

    # start a test, second start conflicts, wait for completion
    r = await c.post("/api/v1/tests/alkalinity")
    assert r.status_code == 202
    run_id = r.json()["run_id"]
    r = await c.post("/api/v1/tests/phosphate")
    assert r.status_code == 409
    for _ in range(600):
        await asyncio.sleep(0.05)
        if not state.engine.busy:
            break
    assert not state.engine.busy
    runs = (await c.get("/api/v1/runs")).json()
    assert runs[0]["id"] == run_id and runs[0]["status"] == "done"

    latest = (await c.get("/api/v1/results/latest")).json()
    assert abs(latest["alkalinity"]["value"] - 8.3) < 0.1
    rid = latest["alkalinity"]["id"]
    raw = (await c.get(f"/api/v1/results/{rid}")).json()
    assert len(raw["raw"]["points"]) > 6
    csv = (await c.get("/api/v1/results/export.csv")).text
    assert "alkalinity" in csv

    # reagents, schedule, limits, metrics, sim knob
    rs = (await c.get("/api/v1/reagents")).json()
    assert any(x["id"] == "hcl" and x["remaining_ml"] < 500 for x in rs)
    assert (await c.post("/api/v1/reagents/hcl/refill", json={})).json()["remaining_ml"] == 500
    r = await c.put("/api/v1/schedule", json=[{"test": "nitrate", "cron": "0 3 * * *"}])
    assert r.status_code == 200 and r.json()["entries"][0]["test"] == "nitrate"
    assert (await c.get("/api/v1/schedule")).json()["upcoming"][0]["test"] == "nitrate"
    r = await c.put("/api/v1/config/limits", json={"alk_dkh": [7, 9], "no3_ppm": [1, 20], "po4_ppm": [0.02, 0.2]})
    assert r.status_code == 200
    m = (await c.get("/metrics")).text
    assert 'openreef_value{test="alkalinity"' in m
    assert (await c.post("/api/v1/sim/tank", json={"alk_dkh": 9.9})).json()["alk_dkh"] == 9.9
    # dashboard + openapi
    assert "OpenReef" in (await c.get("/")).text
    paths = (await c.get("/openapi.json")).json()["paths"]
    assert "/api/v1/tests/{test}" in paths and "/api/v1/calibration/{test}/fit" in paths


async def test_calibration_endpoints(client):
    c, state = client
    state.hw.tank.po4_ppm = 0.25
    r = await c.post("/api/v1/calibration/phosphate/point", json={"standard_ppm": 0.25})
    assert r.status_code == 202
    for _ in range(600):
        await asyncio.sleep(0.05)
        if not state.engine.busy:
            break
    r = await c.post("/api/v1/calibration/phosphate/fit", json={"degree": 1, "through_zero": True})
    assert r.status_code == 200
    coeffs = r.json()["coeffs"]
    assert coeffs[0] == 0.0 and 1.5 < coeffs[1] < 3.0      # ~2.1 ppm per A in the sim
