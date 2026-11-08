# OpenReef

**Open-source automated reef water analyzer — alkalinity, nitrate and phosphate on a schedule, with a real API.**

[![Site](https://img.shields.io/badge/docs-openreef.dev-0f8b8d.svg)](https://openreef.dev)
![Hardware](https://img.shields.io/badge/hardware-CERN--OHL--P-blue.svg)
![Software](https://img.shields.io/badge/software-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)
![Status](https://img.shields.io/badge/status-v2%20design%20complete%2C%20first%20build-orange.svg)

OpenReef measures **total alkalinity by Gran acid titration** (0.02 dKH resolution) and **nitrate and phosphate by self-blanked colorimetry** (0.1 ppm / 0.01 ppm), unattended, from about **$849** of off-the-shelf parts and a few 3D-printed pieces. One Python service on a Raspberry Pi runs the fluidics, the chemistry math, a scheduler, SQLite history, a dashboard and a 40-endpoint REST/WebSocket API, with Hydros, MQTT/Home Assistant, webhook and Prometheus integrations. A hardware simulator with a carbonate-system model runs the whole stack on a laptop.

| Parameter | Method | Range | Resolution | Cycle |
|---|---|---|---|---|
| Alkalinity | Gran titration, 0.02 N HCl, lab-grade pH electrode | 4–14 dKH | 0.02 dKH | 6–8 min |
| Phosphate | Molybdenum blue, 850 nm, AS7341 | 0–1.0 ppm | 0.01 ppm | 10–12 min |
| Nitrate | Reduction + Griess azo dye, 540 nm | 0–50 ppm | 0.1 ppm | 15–30 min |

## Repository

```
firmware/openreef_analyzer/   Python service (openreef/ package), tests, deploy scripts, config.example.yaml
hardware/analyzer/cad/        OpenSCAD parts + renders/, finger-joint panel generator (panels.py), 3D assembly, wiring.svg, bom.csv
_docs/ _layouts/ _includes/   openreef.dev (Jekyll, GitHub Pages, custom theme)
legacy/                       the 2025 OpenReef colorimeter (Flask + TSL2591), unchanged
```

## Quick start (no hardware)

```bash
cd firmware/openreef_analyzer
./dev.sh          # creates .venv, installs, runs the simulator at http://localhost:8080 (Swagger at /docs)
./dev.sh test     # same venv, runs the 8 tests
```

(`dev.sh` is just `python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"`; needs Python 3.11+.)

## Quick start (Raspberry Pi)

```bash
git clone https://github.com/thetemplateblog/openreef.git
cd openreef/firmware/openreef_analyzer && ./deploy/install.sh
```

Then follow the [build order](https://openreef.dev/docs/getting-started/build-order/) and [calibration](https://openreef.dev/docs/chemistry/calibration/) guides.

## How it works

- **Alkalinity**: 20 mL sample, 0.02 N HCl in 60 µL steps from a printed syringe pump (0.07 µL/step), pH tracked by an Atlas Scientific EZO-pH; a DIC-corrected Gran fit over pH 3.0–3.8 gives TA independent of electrode offset. Acid is standardised against Na₂CO₃.
- **Nitrate / phosphate**: 10 mL in a 22 mm cuvette, read before and after reagent (self-blanking), 11-channel AS7341 with white and 850 nm LEDs, primary + secondary wavelength per test as a spectral-shape check. Liquid reagents from the Neptune Trident NP kit; lab-standard chemistry documented as a fallback.
- **Fluidics**: six cheap peristaltic pumps move sample and waste; a dip tube sets the cell volume; five syringe pumps with check valves do the precise work.
- **Safety**: leak sensor, waste float, homing only into empty cells, reagent accounting, alarm relay, systemd watchdog.

Full design document, chemistry, CAD and wiring: **https://openreef.dev**

## Status

v2 is a complete design with working software (simulator-validated) and printable/cuttable hardware files. The first physical build and validation against reference standards is in progress — treat nitrate and phosphate dose volumes for the Trident NP kit as starting points until characterised.

## Licence

Hardware CERN-OHL-P v2 · Software MIT · Documentation CC BY 4.0. OpenReef is not affiliated with Neptune Systems, CoralVue, Hanna Instruments or Atlas Scientific.
