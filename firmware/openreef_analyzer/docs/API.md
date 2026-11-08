# OpenReef REST API

Base path `/api/v1`. Auth: `X-API-Key` header (or `?api_key=`) when `api.api_keys` is set. Interactive docs at `/docs`, schema at `/openapi.json`, live events on `ws://host:8080/ws/events`, Prometheus metrics at `/metrics`.

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
