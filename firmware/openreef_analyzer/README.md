# openreef_analyzer

The OpenReef analyzer service: hardware abstraction (Raspberry Pi + simulator), measurement procedures, chemistry math, scheduler, SQLite persistence, REST/WebSocket API, dashboard and integrations.

```
openreef/
├── config.py            pydantic models for config.yaml
├── hal/                 Hardware interface: base.py (syringe/pump logic), sim.py (chemistry model), rpi.py (pigpio + I2C)
├── chem/                gran.py (DIC-corrected Gran fit, acid standardisation), colorimetry.py (absorbance, curve fits, QC)
├── sequences/           engine.py (one-run-at-a-time executor, progress, safety), procedures.py (alkalinity, colorimetric, prime, flush…)
├── scheduler.py         5-field cron scheduler
├── db.py                SQLite: results, runs, events, calibrations, reagents, settings
├── events.py            async pub/sub
├── integrations/        hydros.py, mqtt.py (HA discovery), webhooks.py
├── api/                 FastAPI app (app.py), request/response schemas
├── web/index.html       dashboard (vanilla JS, same design tokens as openreef.dev)
└── main.py              `openreef serve` / `openreef check-config`
tests/                   8 tests: simulated chemistry end-to-end + API surface
deploy/                  install.sh, update.sh, openreef.service
docs/                    openapi.json, API.md (generated)
cad/                     OpenSCAD parts, panels.svg, wiring.svg, bom.csv (mirrored to hardware/analyzer/cad)
```

## Develop

```bash
./dev.sh          # venv + install + simulator at http://localhost:8080
./dev.sh test     # venv + install + pytest
# or by hand:
python3 -m venv .venv && .venv/bin/pip install -e ".[dev]" && .venv/bin/openreef serve --sim --speedup 50
```

Regenerate the API docs after changing endpoints:

```bash
python -c "import json; from openreef.config import load_config; from openreef.api import create_app; json.dump(create_app(load_config('config.example.yaml')).openapi(), open('docs/openapi.json','w'), indent=1)"
```

## Deploy

`deploy/install.sh` on Raspberry Pi OS Lite 64-bit; see https://openreef.dev/docs/software/install/.
