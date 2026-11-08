---
title: Overview
summary: What OpenReef is, what it measures, and how the parts fit together.
---

OpenReef is a bench-top analyzer for reef aquaria. It measures **total alkalinity** by Gran acid titration and **nitrate** and **phosphate** by self-blanked colorimetry, on a schedule, and publishes every result through a REST and WebSocket API. You build it from off-the-shelf parts and a few printed pieces for about **$849**.

| Parameter | Method | Range | Resolution | Target accuracy | Sample | Cycle |
|---|---|---|---|---|---|---|
| Alkalinity | Gran titration, 0.02 N HCl, pH electrode | 4–14 dKH | 0.02 dKH | ±0.05 dKH | 20 mL | 6–8 min |
| Phosphate (PO₄) | Molybdenum blue, 850/880 nm | 0.00–1.00 ppm | 0.01 ppm | ±0.02 ppm or 5 % | 10 mL | 10–12 min |
| Nitrate (NO₃) | Reduction + Griess azo dye, 540 nm | 0–50 ppm | 0.1 ppm | ±1 ppm or 5 % | 10 mL | 15–30 min |

## What is in the box

```
 ┌──────────────────────────────┬──────────────┐
 │  WET BAY                     │  DRY BAY     │
 │  Cell A  20 mL titration     │  Raspberry   │
 │     pH electrode, DS18B20,   │  Pi 4        │
 │     stir bar                 │              │
 │  Cell B  10 mL cuvette       │  5× TMC2209  │
 │     AS7341 + white/IR LEDs   │  MCP23017    │
 │  5× syringe pumps            │  8× MOSFET   │
 │     acid, NP R1/R2/R3a/R3b   │  relay       │
 │  6× peristaltic (fill/level/ │              │
 │     drain per cell), 2 stir  │  12 V 5 A    │
 │  reagent tray · leak sensor  │              │
 └──────────────────────────────┴──────────────┘
                 waste bottle (HDPE, float switch)
```

One Python service (`firmware/openreef_analyzer`) runs the fluidics, the chemistry math, a scheduler, SQLite history, the dashboard and the API. The same code runs against a hardware simulator with a carbonate-system model, so you can develop and test without the analyzer.

## Design goals

1. **Trustworthy numbers.** Every result stores its raw titration curve or absorbance channels, the calibration it used and a quality score, so a bad reading is visible instead of silently logged.
2. **Off-the-shelf parts only**, total under $1000 including the first two months of reagents.
3. **One codebase, one board.** No microcontroller firmware to flash; the Pi drives steppers with DMA-timed pulses.
4. **Reagents you can buy.** Neptune's Trident NP kit for NO₃/PO₄ and ordinary 0.1 N HCl for alkalinity, with lab-standard chemistry documented as a fallback.
5. **Fail safe.** Leak sensor, waste-full float, reagent accounting, homing before every fill and a watchdog stop pumps before they make a mess.

## Default schedule and consumption

Alkalinity every 6 hours; nitrate and phosphate once a day. That uses about 75 mL of tank water and 1.5 mL of 0.02 N acid per alkalinity test, one Trident NP reagent set every 60 days, and 500 mL of 0.1 N HCl every 4 months.

## Where to go next

- Building one: [Build order](/docs/getting-started/build-order/) → [Bill of materials](/docs/hardware/bom/)
- Understanding the chemistry: [How it measures](/docs/introduction/measurement/)
- Integrating: [REST & WebSocket API](/docs/software/api/), [Hydros, MQTT & webhooks](/docs/software/integrations/)
- The original 2025 colorimeter is preserved under [Legacy](/docs/project/legacy/).
