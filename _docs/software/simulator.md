---
title: Simulator
summary: The whole stack on a laptop, with a carbonate-system model that produces realistic titration curves.
---

```bash
cd firmware/openreef_analyzer
./dev.sh                 # = python3 -m venv .venv && .venv/bin/pip install -e ".[dev]" && .venv/bin/openreef serve --sim --speedup 50
```

Open `http://localhost:8080`. Every button works; a "6-minute" alkalinity test finishes in about seven seconds at 50× speed.

## What is modelled

- **Cell A** holds total alkalinity and acid as absolute amounts; pH is solved from the charge balance `TA = HCO₃⁻ + 2 CO₃²⁻ + OH⁻ − H⁺` with seawater K₁, K₂ and DIC ≈ 0.92 × TA. The resulting curve has the real inflection and the real Gran-region curvature, which is how the DIC-corrected fit was validated.
- **Cell B** develops colour with first-order kinetics (τ = 150 s phosphate, 500 s nitrate) toward `0.47 A/ppm` (PO₄) and `0.020 A/ppm` (NO₃), with each dye's spectral shape across the ten channels, LED spectra, dark counts and shot noise.
- Fill, level and drain pumps move volume with ±0.4 % metering noise; overflow goes to a waste counter; dispenses are routed to the right cell by pump configuration.
- Syringe pumps track plunger position, home switches and refills exactly as the real driver does.
- Leak and waste-full conditions can be injected.

## Changing the "tank"

```bash
curl -X POST localhost:8080/api/v1/sim/tank -H 'Content-Type: application/json' \
  -d '{"alk_dkh": 7.2, "po4_ppm": 0.18, "no3_ppm": 12, "leak": false}'
```

## Tests

```bash
pytest -q
```

The suite runs five simulated chemistry scenarios (alkalinity recovery within 0.08 dKH, acid standardisation within 0.0003 N, two-point PO₄ and NO₃ calibrations then measurement, reagent accounting and event flow, leak abort) and three API scenarios (auth, the full REST surface, calibration endpoints) in about 30 seconds.

## Using it for development

The `Hardware` base class in `openreef/hal/base.py` is the only contract. To support a different sensor or pump, subclass it (or `RpiHardware`) and point `hardware.backend` at your class. Procedures in `openreef/sequences/procedures.py` never touch GPIO directly, so a new procedure written against the simulator will run unchanged on the analyzer.
