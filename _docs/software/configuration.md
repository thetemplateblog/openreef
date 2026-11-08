---
title: Configuration
summary: Everything hardware- and chemistry-specific lives in one YAML file.
---

The service reads `$OPENREEF_CONFIG`, then `./config.yaml`, then `/etc/openreef/config.yaml`, then falls back to `config.example.yaml`. Validate with `openreef check-config`.

## Sections

| Section | What it holds |
|---|---|
| `hardware` | backend (`sim`/`rpi`), I²C addresses, Pi GPIO pins, the five `steppers` (STEP/DIR pins, home pin, lead-screw and syringe geometry, reagent, target cell), the eight `dc` channels (MCP23017 pin, flow rate, cell, role), the two `cells` (metered volume, path length) |
| `chemistry` | `reagents` (bottle sizes and pump assignment), the `alkalinity` titration profile, the `phosphate` and `nitrate` colorimetric profiles (doses, mixing, development, LED and channels, temperature coefficient, starting calibration coefficients) |
| `schedule` | list of `{test, cron, enabled}`; editable live through the API |
| `limits` | `[low, high]` alert bands per parameter |
| `hydros`, `mqtt`, `webhooks` | integrations |
| `api` | bind address, port, API keys, CORS |
| `sim_speedup` | simulator time factor |

## Pin numbering

`step_pin`, `dir_pin`, `leak_pin`, `alarm_relay_pin`, `led_*_pin`, `heater_pwm_pin` are **Raspberry Pi BCM** numbers. Stepper `home_pin` and DC `pin` are **MCP23017** pins: 0–7 = port A (inputs), 8–15 = port B (outputs).

## Syringe geometry

```yaml
steppers:
  - { name: SP1, step_pin: 27, dir_pin: 22, home_pin: 0, reagent: hcl, cell: A,
      steps_per_mm: 1600, syringe_bore_mm: 12.0, stroke_mm: 45, max_speed_mm_s: 2.5 }
```

`steps_per_mm = 200 × microsteps / lead_mm`. For a 1 mm-lead T8×1 screw use 3200; for a 10 mL syringe (bore ≈ 14.5 mm) set `syringe_bore_mm` accordingly. The software computes µL per step from these.

## Values that persist outside the file

Calibration results (`acid_normality`, curve coefficients, secondary ratios), reagent remaining volumes, edited limits and schedule are stored in the SQLite `settings` and `reagents` tables and override the YAML. Delete the database to start clean.

## Example

The full annotated example is `firmware/openreef_analyzer/config.example.yaml` in the repository.
