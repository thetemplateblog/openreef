---
title: Calibration
summary: pH electrode, acid normality, colorimetric curves, volume check — in that order, and how often.
---

## Schedule

| What | When | Takes |
|---|---|---|
| pH electrode (7.00 then 4.00) | every 2 weeks, and after electrode replacement | 5 min |
| Acid standardisation (Na₂CO₃) | every acid refill, and monthly | 10 min |
| PO₄ curve (2–3 standards) | every reagent kit change, and monthly | 30 min |
| NO₃ curve (2–3 standards) | every reagent kit change, and monthly | 1 h |
| Cell volume check (scale) | once at build, then yearly | 10 min |
| Reagent characterisation | once per new reagent brand/lot type | 40–120 min |

All calibration runs require the analyzer to be idle; the dashboard's **Calibration** tab drives every step below.

## 1. pH electrode

Pause the schedule. Lift the Cell A cap, rinse the electrode with DI, place it in pH 7.00 buffer, wait 60 s, press **pH 7.00** (`POST /api/v1/calibration/ph {point: mid, value: 7}`). Repeat with pH 4.00 as `low`. The EZO circuit reports slope; replace the electrode when slope falls below 90 %. Refit the cap and run **Flush**.

## 2. Acid standardisation

Make 1.000 L of 0.1000 g/L Na₂CO₃ in DI (dry the salt at 250 °C for an hour first, or accept ~0.5 % error). Move the intake line into the standard and run `POST /api/v1/calibration/alkalinity/standardize {known_ta_meq_l: 1.887}`. The run titrates normally and solves for the normality that reproduces 1.887 meq/L; the value is stored and used from then on. Expect 0.0195–0.0205 N for a 1:5 dilution of 0.1 N acid. Put the intake back in the sump and run **Flush**.

A certified alkalinity standard (sold for reef testers) works the same way — enter its value in meq/L (dKH ÷ 2.8).

## 3. Colorimetric curves

For each test, prepare two or three standards in nutrient-free saltwater spanning your range (PO₄: 0.05, 0.20, 0.50 ppm; NO₃: 2, 10, 30 ppm). For each standard: intake into the standard, `POST /api/v1/calibration/{test}/point {standard_ppm}`. The run records (absorbance₂₅, ppm). Then `POST /api/v1/calibration/{test}/fit {degree: 1, through_zero: true}`. The self-blanking makes a zero standard unnecessary, so a line through the origin with two points is the minimum; three points let you check linearity (R² is returned). Use `degree: 2` only with four or more points.

The fit also stores the mean secondary/primary ratio used by the spectral-shape check. Clear stale points with `DELETE /api/v1/calibration/{test}/points` before a new kit.

## 4. Cell volume

Fill and level each cell with the dashboard, then pipette or pour the contents into a tared cup on a 0.01 g scale. Adjust the dip-tube depth until Cell A holds 20.0 ± 0.2 g and Cell B 10.0 ± 0.1 g. Record the values in `config.yaml` (`hardware.cells[].volume_ml`). This is the one calibration the software cannot do for you.

## 5. Verification

After calibrating, run the Trident NP calibration solution (or a mid-range standard) as a normal test and confirm the reported value is within 5 %. Then run tank water and compare with a careful hand test. Keep the results: the dashboard's history shows calibration records as markers so a step change can be traced to a calibration.

## What is stored

| Record | Where | Used by |
|---|---|---|
| `acid_normality` | settings + `calibrations(kind=acid_normality)` | alkalinity runs |
| `{test}_cal_coeffs`, `{test}_secondary_ratio` | settings + `calibrations(kind=curve)` | colorimetric runs |
| `{test}_cal_points` | settings | the next fit |
| `ph_electrode` | `calibrations` | audit only |
| `characterization` | `calibrations` | reagent profiling |

Every result row records the `calibration_id` in force, so re-analysis is always possible.
