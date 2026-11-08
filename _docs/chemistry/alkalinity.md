---
title: Alkalinity (Gran titration)
summary: How the titration runs, the DIC-corrected Gran fit, and what the quality flags mean.
---

## The run

1. Rinse Cell A twice with tank water; home the acid pump if needed; fill and level to 20.0 mL; stir 15 s; read temperature and starting pH.
2. **Initial dose.** 97 % of the acid expected from the previous result (or `initial_dose_ul` on the first run) in one shot, so the titration lands just short of equivalence.
3. **Approach.** 200 µL steps until pH < 4.3.
4. **Titrate.** 60 µL steps, waiting for pH drift < 0.005 pH/s after each (timeout 25 s), until pH < 3.0 or 14 points have been collected in the 3.0–3.8 window.
5. Fit, store, drain, rinse once, park the cell full of tank water.

A typical 8 dKH titration uses 2.9 mL of 0.02 N acid and takes six to eight minutes.

## The math

Below pH 4 the carbonate species are essentially all CO₂, and the charge balance on the solution is

<div class="math">[H⁺] = [HCO₃⁻] − TA_remaining,  with [HCO₃⁻] ≈ C_T · K₁ / [H⁺]</div>

Multiplying by the total volume (V₀ + v) and substituting `TA_remaining·(V₀+v) = TA₀·V₀ − c·v` and `C_T·(V₀+v) = C_T0·V₀` gives a straight line:

<div class="math">(V₀ + v)·[H⁺] − c·v  =  −TA₀·V₀  +  C_T0 · ( V₀·K₁ / [H⁺] )</div>

A least-squares line of the left side against `x = V₀K₁/[H⁺]` has intercept `−TA₀V₀` and slope `C_T0`: alkalinity *and* an estimate of dissolved inorganic carbon from the same points. With pK₁ = 5.86 (seawater, 25 °C), the DIC term is 2–4 % of [H⁺] in the window and ignoring it — as the classic Gran extrapolation does — biases alkalinity 2–5 % low. OpenReef reports both: `ta_meq_l` (corrected, primary) and `ta_classic_meq_l`.

`dKH = 2.80 × TA (meq/L)`; 1 meq/L = 50 ppm CaCO₃.

### Why it tolerates a mediocre electrode

A constant pH offset changes every [H⁺] by the same factor; the fit's x-intercept does not move. Slope errors matter more, so calibrate at pH 7 and 4 (bracketing the window) every two weeks, and let the EZO circuit's temperature compensation run from the DS18B20.

### Standardising the acid

Rather than trusting the label, run the titration on a reference of known alkalinity — 0.1000 g/L anhydrous Na₂CO₃ (dried at 250 °C) is 1.887 meq/L = 5.28 dKH — and solve for the normality that reproduces it (`POST /api/v1/calibration/alkalinity/standardize`). The DIC-corrected fit depends on *c*, so the solver bisects on *c* until TA matches. Re-standardise whenever you refill the acid bottle.

## Quality flags

| Flag | Meaning | What to do |
|---|---|---|
| `low_r2` | fit R² < 0.999 | electrode noisy or stirring poor; check bubbles on the bulb |
| `noisy_fit` | relative residual rms > 1 % | same; halves the quality score |
| `v_eq_outside_expected` | equivalence volume not before the first window point | first dose too large; lower `initial_dose_ul` |
| `dic_estimate_implausible` | DIC < 0 or > 2× TA | window too narrow or pH scale off; recalibrate pH |

The quality score (0–1) is derived from R² and residuals; the dashboard greys out points below 0.5.

## Configuration

```yaml
chemistry:
  alkalinity:
    acid_normality: 0.0200   # replaced by standardisation
    sample_ml: 20.0
    initial_dose_ul: 900
    step_ul: 60
    gran_ph_min: 3.0
    gran_ph_max: 3.8
    min_points: 6
    max_points: 14
    stable_dph_per_s: 0.005
    stable_timeout_s: 25
```

## References

- Dickson, Sabine & Christian (eds.), *Guide to best practices for ocean CO₂ measurements*, PICES Special Publication 3 (2007), SOP 3b — open-cell alkalinity titration.
- Gran, G. (1952). Determination of the equivalence point in potentiometric titrations, Part II. *Analyst* 77:661–671.
- Millero, F. J. (2010). Carbonate constants for estuarine waters. *Marine and Freshwater Research* 61:139–142.
