---
title: Bring-up & first test
summary: A checklist to walk a freshly built analyzer from power-on to a trusted result.
---

## 1. Power and buses

```bash
sudo systemctl status pigpiod openreef
i2cdetect -y 1          # expect 0x20 (MCP23017), 0x39 (AS7341), 0x63 (EZO-pH)
ls /sys/bus/w1/devices/ # expect 28-xxxxxxxxxxxx (DS18B20)
journalctl -u openreef -f
```

## 2. Dry checks (no liquids)

- **Hardware → Pumps**: each peristaltic pump turns the right way (fill pumps push toward the cell, level/drain pumps pull from it). Swap the motor leads if not.
- **Home all syringes**: each carriage retracts to its switch, backs off 0.5 mm and re-homes slowly. If a pump runs into the far end, flip that pump's `DIR` sense by swapping one motor coil pair.
- **Sensors**: pH in air reads anything stable; spectral dark counts < 50 with the holder closed; white LED on gives 20 000–40 000 counts on `f5_555` through an empty cuvette (adjust gain if clipping at 65 535).
- Trip the leak sensor with a wet finger: the dashboard status goes red and the alarm relay clicks.

## 3. Wet checks

- Put the intake in a glass of tank water and the drain in a cup. Run **Flush**. Cell A should fill, level to 20 mL and drain fully twice; same for Cell B.
- Weigh the retained volume after a fill+level: adjust tube depth until 20.0 ± 0.2 g and 10.0 ± 0.1 g.
- Prime each syringe pump; confirm drops appear at the correct drip tip.

## 4. First alkalinity run

Start a test from **Overview**. Watch the live log: `initial_dose`, then `approach` steps of 200 µL until pH < 4.3, then `titrate` steps of 60 µL. Open the result's raw data: `r2` should be > 0.999 and `dic_est_mmol_l` between 1.5 and 3.5. If `v_eq_outside_expected` is flagged, the first dose was too large — lower `initial_dose_ul` for the first run (later runs size it from the previous result).

## 5. First colorimetric run

Run phosphate. In the raw data, `channels_abs.nir` should be positive and `f8_680` about 0.65× of it (shape check). A negative absorbance means bubbles on the cuvette wall: increase the settle time or the post-fill stir.

## 6. Calibrate

Follow [Calibration](/docs/chemistry/calibration/) before you act on any number.
