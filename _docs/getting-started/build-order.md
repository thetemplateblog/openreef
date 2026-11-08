---
title: Build order
summary: Two weekends. Print while parts ship, wire and flash before you plumb, calibrate before you trust it.
---

## Week 0 — order and print

1. Order the [bill of materials](/docs/hardware/bom/). The Atlas pH kit and the Trident NP reagents have the longest lead times (reagents ship ground only).
2. Print from `hardware/analyzer/cad/`: 5× `syringe_pump.scad` (frame, carriage, plunger clip), `cell_a_cap.scad`, `cell_b_holder.scad` (body in **black** PETG, lid), 16× `corner_bracket.scad`.
3. Cut the panels from `hardware/analyzer/cad/panels.svg` (3 mm and 6 mm cast acrylic). Engrave the drip-tray outline and standoff marks on the base.
4. While waiting: run the [simulator](/docs/software/simulator/) on your laptop and get familiar with the dashboard and API.

## Week 1 — electronics and software

5. Assemble the stepper carrier board: five StepStick sockets, 100 µF across each VMOT, shared EN, screw terminals for motors and limit switches. Set VREF to 0.6 V.
6. Mount Pi, carrier, MCP23017, MOSFET board, relay and buck in the dry bay. Wire per the [wiring diagram](/docs/hardware/electronics/). Do not connect the 12 V rail to motors yet.
7. Flash Raspberry Pi OS Lite (64-bit), enable I²C and 1-Wire, then run [`deploy/install.sh`](/docs/software/install/). `i2cdetect -y 1` must show 0x20, 0x39 and 0x63.
8. Set `hardware.backend: rpi` in `/etc/openreef/config.yaml`, restart, open the dashboard → **Hardware**. Jog each peristaltic pump 3 s; home each syringe; read pH and the spectral channels (cover the holder: dark counts should be < 50).

## Week 2 — fluidics

9. Mount the shelves and fit the cells. Trim the Cell A level tube so the retained volume is 20.0 g of water on a scale (and 10.0 g for Cell B); record both in `config.yaml`.
10. Build the syringe pumps: inlet check valve from bottle, outlet check valve to the cell's drip tip. Check-valve arrows point toward the cell.
11. Run reagent and acid lines in PTFE, sample lines in silicone. Install the 100 µm intake filter and the waste float switch.
12. Fill the acid bottle with 0.02 N HCl (100 mL of 0.1 N + 400 mL DI). Install the Trident NP bottles. **Prime** every pump from the dashboard (dispenses ~7 mL to waste).
13. Run **Flush**, then a manual alkalinity test on tank water and check the raw curve: smooth pH descent, 6–10 points between pH 3.0 and 3.8.

## Week 2 — calibrate and schedule

14. pH buffers 7.00 then 4.00; acid standardisation against Na₂CO₃; two standards each for PO₄ and NO₃. See [Calibration](/docs/chemistry/calibration/).
15. Compare three alkalinity results with your hand test kit or a reference. Expect agreement within the hand kit's own resolution.
16. Set alert limits, the schedule, and (optionally) Hydros/MQTT in `config.yaml`. Done.

<div class="callout tip">Keep a log of acid normality and curve coefficients after each calibration (the dashboard records them). A slow drift in acid normality means the acid bottle is absorbing moisture or evaporating — replace it.</div>
