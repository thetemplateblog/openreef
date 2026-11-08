---
title: REST & WebSocket API
summary: Forty endpoints under /api/v1, a WebSocket event stream, OpenAPI schema and Prometheus metrics.
---

Base URL `http://<host>:8080/api/v1`. Interactive docs (Swagger UI) at `/docs`, machine-readable schema at `/openapi.json` (a copy ships in `firmware/openreef_analyzer/docs/openapi.json`).

## Authentication

Set `api.api_keys` in `config.yaml`; then every `/api/v1` request needs `X-API-Key: <key>` (or `?api_key=`). With the list empty the API is open — only do that on a trusted LAN. `/api/v1/health`, `/healthz` and `/metrics` are always open.

## Conventions

- Long-running actions (`POST /tests/…`, calibration runs, prime, home, flush) return **202** with a `run_id` and run in the background; one run at a time — a second request gets **409**.
- Progress streams on the WebSocket and is also available at `GET /runs/current`.
- Results carry `value`, `unit`, `quality` (0–1), `flags`, `temp_c`, `duration_s`, `calibration_id`; `GET /results/{id}` adds `raw` (titration points or spectral channels).
- Times are Unix seconds (`ts`); cron expressions are 5-field, local time.

## Endpoints

| Method | Path | Tag | Summary |
|---|---|---|---|
| GET | `/api/v1/health` | system | Health |
| GET | `/api/v1/status` | system | Status  |
| GET | `/api/v1/config` | system | Get Config |
| PUT | `/api/v1/config/limits` | system | Put Limits |
| POST | `/api/v1/tests/{test}` | tests | Start Test |
| POST | `/api/v1/tests/abort` | tests | Abort |
| GET | `/api/v1/runs` | tests | Runs |
| GET | `/api/v1/runs/current` | tests | Current |
| GET | `/api/v1/results` | results | Results |
| GET | `/api/v1/results/latest` | results | Latest |
| GET | `/api/v1/results/export.csv` | results | Export Csv |
| GET | `/api/v1/results/{rid}` | results | Result |
| GET | `/api/v1/calibration` | calibration | Calibrations |
| POST | `/api/v1/calibration/ph` | calibration | Calibrate Ph |
| POST | `/api/v1/calibration/alkalinity/standardize` | calibration | Standardize |
| POST | `/api/v1/calibration/{test}/point` | calibration | Cal Point |
| POST | `/api/v1/calibration/{test}/fit` | calibration | Cal Fit |
| DELETE | `/api/v1/calibration/{test}/points` | calibration | Cal Clear |
| POST | `/api/v1/calibration/{test}/characterize` | calibration | Characterize |
| GET | `/api/v1/reagents` | reagents | Reagents |
| POST | `/api/v1/reagents/{rid}/refill` | reagents | Refill |
| POST | `/api/v1/reagents/{rid}/prime` | reagents | Prime |
| GET | `/api/v1/hardware` | hardware | Hardware |
| POST | `/api/v1/hardware/pump` | hardware | Pump |
| POST | `/api/v1/hardware/dispense` | hardware | Dispense |
| POST | `/api/v1/hardware/home` | hardware | Home |
| POST | `/api/v1/hardware/flush` | hardware | Flush |
| POST | `/api/v1/hardware/led` | hardware | Led |
| GET | `/api/v1/hardware/ph` | hardware | Read Ph |
| GET | `/api/v1/hardware/spectral` | hardware | Read Spectral |
| POST | `/api/v1/hardware/alarm` | hardware | Alarm |
| POST | `/api/v1/hardware/estop` | hardware | Estop |
| GET | `/api/v1/schedule` | schedule | Schedule |
| PUT | `/api/v1/schedule` | schedule | Put Schedule |
| POST | `/api/v1/schedule/pause` | schedule | Pause |
| POST | `/api/v1/schedule/resume` | schedule | Resume |
| GET | `/api/v1/events` | events | Events |
| GET | `/api/v1/hydros/device` | hydros | Hydros Device |
| GET | `/api/v1/hydros/state` | hydros | Hydros State |
| POST | `/api/v1/hydros/override` | hydros | Hydros Override |
| POST | `/api/v1/sim/tank` | simulator | Sim Tank |

## WebSocket

`ws://<host>:8080/ws/events?api_key=…` sends a `hello` with the current progress and latest results, then every event as JSON:

```json
{"type": "progress", "run_id": 418, "test": "alkalinity", "step": "titrate", "percent": 61.4, "ph": 3.412, "acid_ul": 3340, "points": 7, "ts": 1794094012.2}
{"type": "result", "test": "alkalinity", "value": 8.29, "unit": "dKH", "quality": 0.98, "flags": [], "id": 1203, "ts": 1794094201.9}
{"type": "alert", "level": "warning", "code": "phosphate_out_of_range", "value": 0.21, "low": 0.03, "high": 0.15, "ts": …}
```

Event types: `service_started`, `run_started`, `progress`, `result`, `run_finished`, `alert`, `reagent_low`, `reagent_refilled`, `calibration`, `calibration_point`, `hydros_action`. Everything except `progress` is also persisted and queryable at `GET /events`.

## Examples

```bash
KEY=change-me
H="X-API-Key: $KEY"; B=http://openreef.local:8080/api/v1

curl -s -H "$H" $B/results/latest | jq
curl -s -H "$H" "$B/results?test=alkalinity&since=$(date -d '-7 days' +%s)" | jq '.[].value'
curl -s -H "$H" -X POST $B/tests/phosphate
curl -s -H "$H" -X POST $B/calibration/alkalinity/standardize -d '{"known_ta_meq_l":1.887}' -H 'Content-Type: application/json'
curl -s -H "$H" -X PUT $B/schedule -H 'Content-Type: application/json' \
  -d '[{"test":"alkalinity","cron":"0 */6 * * *"},{"test":"phosphate","cron":"30 9 * * *"},{"test":"nitrate","cron":"0 10 * * *"}]'
curl -s $B/../metrics | grep openreef_value
```

Python:

```python
import httpx, websockets, asyncio, json
B, H = "http://openreef.local:8080/api/v1", {"X-API-Key": "change-me"}
print(httpx.get(f"{B}/results/latest", headers=H).json()["alkalinity"]["value"])

async def tail():
    async with websockets.connect("ws://openreef.local:8080/ws/events?api_key=change-me") as ws:
        async for msg in ws:
            e = json.loads(msg)
            if e["type"] == "result": print(e["test"], e["value"], e["unit"])
asyncio.run(tail())
```

## Prometheus

`GET /metrics` exposes `openreef_value{test,unit}`, `openreef_quality{test}`, `openreef_result_age_seconds{test}`, `openreef_reagent_ml{reagent}`, `openreef_alarm`, `openreef_busy`.

## Versioning

The path prefix is the API version. Breaking changes bump it; additive changes do not. The OpenAPI document is the contract.
