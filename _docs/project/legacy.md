---
title: Legacy colorimeter (v1)
summary: The 2025 OpenReef was a Raspberry Pi colorimeter for Red Sea powder kits. It still works; it lives under legacy/.
---

The first OpenReef (2025) was a Raspberry Pi colorimeter — TSL2591 light sensor, Adafruit Motor HAT, MCP23017 solenoid driver, a Flask web interface — that automated Red Sea Pro phosphate and nitrate kits in a 10 mm cuvette with RO-water flushing, for about $250. It had no alkalinity, no API beyond the web page, and dosed reagents with peristaltic pumps.

Version 2 (this site) started over: Gran-titration alkalinity, syringe-pump dosing, an 11-channel spectral sensor with self-blanking, liquid reagents, a real API, a simulator and a test suite.

Everything from v1 is preserved unchanged in the repository under `legacy/`:

| Path | Contents |
|---|---|
| `legacy/open_colorimeter_pi/` | Flask app, templates, install scripts, JSON config templates |
| `legacy/hardware/` | OpenSCAD enclosure, pump brackets, bottle caps, Fusion 360 / FreeCAD guides, the OpenColorimeter V1 STEP |
| `legacy/docs/` | the v1 assay protocols, calibration guide, Pi setup and hardware guide |
| `legacy/tools/` | calibration analysis script |

If you built a v1, the Pi, Motor HAT and MCP23017 carry over; the TSL2591 and solenoids do not. The IO Rodeo [Open Colorimeter](https://blog.iorodeo.com/open-colorimeter-product-guide/) that inspired the v1 cuvette holder remains a fine hand-held instrument.
