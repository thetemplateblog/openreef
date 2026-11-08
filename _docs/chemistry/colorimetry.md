---
title: Phosphate & nitrate
summary: Self-blanked colorimetry in a 22 mm cuvette with an 11-channel spectral sensor.
---

## The run (both tests)

1. Rinse Cell B twice; home any un-homed reagent pump; fill and level to 10.0 mL; stir 5 s to shed bubbles; settle 8 s; read temperature.
2. **Blank:** dark reading, then LED on → I₀ for all 10 channels (16 samples averaged).
3. Dose reagents in order from the test's profile, stirring between doses.
4. Develop for `develop_s` with the stirrer off (optionally reading every 30 s to log kinetics).
5. **Sample:** dark + lit reading → I. Compute absorbance, apply temperature correction and the calibration curve. Store, drain, rinse twice, park.

<div class="math">A = log₁₀( (I₀ − D) / (I − D) );   A₂₅ = A / (1 + k·(T − 25));   ppm = c₀ + c₁·A₂₅ + c₂·A₂₅²</div>

## Phosphate

- Chemistry: ascorbic acid / molybdenum blue (APHA 4500-P E). With the Trident NP kit this is reagents **3a** and **3b**; lab-mixed it is the sulfuric molybdate–antimony reagent plus ascorbic acid.
- Readout: 850 nm LED on the AS7341 `nir` channel (primary), `f8_680` under the white LED as the secondary (≈0.65 of primary for a clean molybdenum-blue spectrum).
- Development: 8–10 min; colour is stable for another 20 min. Temperature coefficient ≈ +0.4 %/°C, corrected to 25 °C.
- Sensitivity: ≈0.47 A per ppm PO₄ in the 22 mm cell after reagent dilution, so 1.0 ppm ≈ 0.47 A — comfortably on the linear part of the curve. 0.01 ppm is ≈0.005 A, resolved by 16-sample averaging of 16-bit counts.
- Interference: silicate above ~5 ppm reads as phosphate (slowly); arsenate likewise. Both are rare in reef systems.

## Nitrate

- Chemistry: reduction to nitrite followed by the Griess reaction (sulfanilamide + NEDD → pink azo dye). Trident NP reagents **1** and **2**; lab-mixed, the vanadium(III) chloride single reagent.
- Readout: white LED, `f5_555` primary, `f4_515` secondary (≈0.85 of primary).
- Development: 25 min default for the NP kit profile; VCl₃ chemistry needs 30–45 min at 22 °C or ~10 min at 45 °C (optional heater).
- Range: 0–50 ppm. Above ~60 ppm the absorbance passes 1.2 and the `over_range` flag is set; dilute the sample or shorten the path (a 12 mm cuvette) if your tank runs that high.
- Nitrite is read as nitrate; in a reef tank that is < 0.1 ppm.

## Spectral-shape check

After calibration the software stores the mean secondary/primary absorbance ratio. A result whose ratio deviates by more than 25 % gets the `spectral_shape_mismatch` flag and half quality. Causes: a bubble in the light path (flat spectrum), precipitate (scatter rising to the blue), the wrong reagent in a bottle, or a dying LED.

## Reagent characterisation mode

`POST /api/v1/calibration/{test}/characterize {standard_ppm, minutes}` runs the test on a known standard and records all ten channels every 30 s for up to two hours. Use it when you adopt a new reagent kit to pick the primary channel (largest, cleanest absorbance), the development time (where the curve plateaus) and the dose volumes (increase until absorbance stops growing). The curve is stored as a `characterization` calibration record and plotted in the dashboard.

## Quality flags

| Flag | Meaning |
|---|---|
| `negative_absorbance` | sample brighter than blank — bubbles cleared during development, or the cuvette moved |
| `over_range` | A > `cal_abs_max` |
| `low_light` | blank counts < 500 — LED failing, dirty cuvette, gain too low |
| `spectral_shape_mismatch` | see above |

## Configuration

```yaml
chemistry:
  phosphate:
    doses: [{np_r3a: 400}, {np_r3b: 400}]   # µL, in order
    mix_s: 20
    develop_s: 600
    led: ir
    primary_channel: nir
    secondary_channel: f8_680
    temp_coeff_per_c: 0.004
    cal_coeffs: [0.0, 2.1, 0.0]              # replaced by the fit
  nitrate:
    doses: [{np_r1: 500}, {np_r2: 500}]
    mix_s: 30
    develop_s: 1500
    led: white
    primary_channel: f5_555
    secondary_channel: f4_515
```

<div class="callout warn">The Trident NP dose volumes and development times shipped in <code>config.example.yaml</code> are starting points inferred from the kit's 60-tests-per-bottle sizing, not Neptune's specification. Run the characterisation mode on your own standards before trusting nitrate or phosphate numbers.</div>
