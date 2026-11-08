---
title: Bill of materials
summary: Every part, with a source and a price. $849 as priced in November 2026; most prices are estimates, the two marked verified were checked at the vendor.
---

Prices are US dollars from common suppliers (Adafruit, Amazon, AliExpress, lab-supply houses). The two items marked **verified** were checked at the vendor in Nov 2026; everything else is an estimate — expect ±15 %. The CSV source is `hardware/analyzer/cad/bom.csv`.


## Compute

| Item | Qty | Unit | Ext. | Source / part | Notes |
|---|---|---|---|---|---|
| Raspberry Pi 4 Model B 2 GB | 1 | $45 | $45 | Raspberry Pi reseller | Pi Zero 2 W also works (slower dashboard) |
| microSD 32 GB A2 | 1 | $8 | $8 | any | Raspberry Pi OS Lite 64-bit |
| 12 V 5 A power supply (barrel) | 1 | $14 | $14 | Mean Well GST60A12 or similar | fused |
| 5 V 3 A buck converter module | 1 | $4 | $4 | MP1584 / LM2596 | feeds Pi 5 V pin |
| MCP23017 breakout | 1 | $6 | $6 | Adafruit 5346 | I2C 0x20 |
| 8-channel low-side MOSFET module | 1 | $10 | $10 | IRF520/IRLZ44N board | 12 V pumps + stirrers |
| TMC2209 StepStick driver | 5 | $4 | $20 | BTT/Fysetc | 1/16 microstep; VREF 0.6 V |
| 1-ch 5 V relay module | 1 | $3 | $3 | any | dry contact to Hydros Sense port |
| Perfboard 9x15 cm + headers + screw terminals + JST-XH kit + wire | 1 | $25 | $25 | any | stepper carrier board |
| DS18B20 waterproof probe | 1 | $3 | $3 | any | + 4.7 k resistor |
| Water leak sensor module | 1 | $4 | $4 | any | drip tray |
| Float switch (waste bottle) | 1 | $4 | $4 | any | NC/NO selectable |

## Sensing

| Item | Qty | Unit | Ext. | Source / part | Notes |
|---|---|---|---|---|---|
| Atlas Scientific pH Kit KIT-101P (EZO-pH + lab-grade probe + isolated carrier + buffers) | 1 | $167 | $167 | atlas-scientific.com | **verified** Nov 2026 |
| Adafruit AS7341 10-channel spectral sensor | 1 | $16 | $16 | Adafruit 4698 | I2C 0x39 |
| LEDs: 5 mm white high-CRI, 5 mm 850 nm IR, resistors, 2N7002 | 1 | $4 | $4 | any |  |

## Fluidics

| Item | Qty | Unit | Ext. | Source / part | Notes |
|---|---|---|---|---|---|
| NEMA17 stepper 34 mm (17HS4023) | 5 | $9 | $45 | any | 0.7-1.0 A |
| T8x2 lead screw 150 mm + brass nut | 5 | $5 | $25 | any | 2 mm lead (single start) |
| 5 mm to 8 mm flexible coupler | 5 | $1.6 | $8 | any |  |
| 8 mm smooth rod 120 mm + LM8UU | 5 | $3 | $15 | any |  |
| 5 mL glass luer-lock syringe | 5 | $6 | $30 | Fortuna Optima / Socorex | PP Norm-Ject acceptable for reagents |
| Luer one-way check valve (PP/silicone) | 10 | $2 | $20 | Qosina / Cole-Parmer | 2 per pump |
| Micro limit switch | 5 | $0.8 | $4 | any | home switch |
| 12 V peristaltic pump with silicone tube | 6 | $12 | $72 | Kamoer KPHM100 or generic | 1-1.5 mL/s |
| 40 mm 12 V fan + N52 8x3 magnets + PTFE stir bars (25 mm & 8 mm) | 2 | $6 | $12 | any | magnetic stirrers |
| Silicone tubing 2x4 mm 5 m | 1 | $8 | $8 | any | pump + sample lines |
| PTFE tubing 1/16 ID x 1/8 OD 5 m | 1 | $12 | $12 | any | acid + reagent lines |
| Luer barbs / 1/8 barbs / Y / plug fitting kit | 1 | $12 | $12 | any |  |
| Inline 100 um sample filter | 1 | $6 | $6 | any | on intake |
| 60 mL borosilicate vial 40x100 mm (Cell A) | 1 | $6 | $6 | any |  |
| Hanna HI731331 22 mm glass cuvettes (4 pk) (Cell B) | 1 | $12 | $12 | Hanna |  |
| 2 L HDPE waste bottle + 500 mL HDPE acid bottle | 1 | $12 | $12 | any | Trident NP waste requires HDPE/glass |
| Bottle caps with 2 ports + tube weights | 6 | $1.5 | $9 | any |  |

## Enclosure

| Item | Qty | Unit | Ext. | Source / part | Notes |
|---|---|---|---|---|---|
| Cast acrylic 3 mm 600x900 mm | 2 | $20 | $40 | any | sides/top/front/bulkhead/shelves |
| Cast acrylic 6 mm 300x600 mm | 1 | $18 | $18 | any | base/back/bottle tray |
| M3 hardware + heat-set inserts + hinges + magnets + grommets | 1 | $20 | $20 | any |  |
| PETG filament (~500 g) | 1 | $12 | $12 | any | pumps/caps/holder/brackets |

## Chemistry

| Item | Qty | Unit | Ext. | Source / part | Notes |
|---|---|---|---|---|---|
| Neptune Trident NP 2-month reagent kit | 1 | $60 | $60 | BRS / Saltwater Aquarium | 60 tests each; ground ship only |
| 0.1 N HCl certified 1 L | 1 | $15 | $15 | Hach/LabChem/Ricca | dilute 1:5 |
| Na2CO3 ACS primary standard 100 g | 1 | $14 | $14 | any | alkalinity reference |
| KNO3 ACS + KH2PO4 ACS (standards) | 1 | $24 | $24 | any |  |
| DI water 4 L | 1 | $5 | $5 | store |  |

## Totals

| Section | USD |
|---|---|
| Compute | $146 |
| Sensing | $187 |
| Fluidics | $308 |
| Enclosure | $90 |
| Chemistry | $118 |
| **Total** | **$849** |

Not included: a 3D printer and laser-cutter time, DI water on an ongoing basis, and a Hydros controller if you want that integration. Budget about $35/month for consumables at the default schedule (Trident NP kit $60/2 months, acid, standards).

## Substitutions that keep the price down

- **Raspberry Pi Zero 2 W** instead of the Pi 4 saves $30; the dashboard is slower but the analyzer is unaffected (pigpio works on both).
- **Plastic Norm-Ject syringes** (PP/PE, no rubber) instead of glass save $22; replace them yearly.
- **Skip the Atlas lab-grade probe** and use a $25 generic BNC electrode with the EZO circuit: Gran titration tolerates a mediocre electrode better than a pH monitor does, but expect to replace it every 6–9 months.
- **Three syringe pumps instead of five** if you use lab-mixed reagents (one acid + one reagent per test) saves $70.

## Substitutions that are not worth it

- Peristaltic pumps for reagent dosing: tube wear changes volume per revolution by several percent within weeks.
- A single photodiode instead of the AS7341: you lose the secondary-wavelength check and the reagent characterisation mode for $8.
- Open-bottle reagents without check valves: siphoning and air ingestion will ruin the dosing accuracy.
