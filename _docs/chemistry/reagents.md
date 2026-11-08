---
title: Reagents
summary: What to buy, what to mix, how long it lasts and how the analyzer keeps count.
---

## Buy

| Consumable | Product | Tests / unit | Cost | Notes |
|---|---|---|---|---|
| NO₃ + PO₄ reagents | [Neptune Trident NP 2-Month Reagent Kit](https://shop.neptunesystems.com/products/trident-np-reagent-kit) | 60 of each | $60–84 | Reagent 1, 2, 3a, 3b + calibration solution + waste neutralizer. Ground shipping only, contiguous US. HDPE or glass waste. |
| Alkalinity titrant | 0.1 N HCl, certified (Hach, LabChem, Ricca), 1 L | ~650 after 1:5 dilution | $12–18 | Dilute with DI to 0.02 N; standardise. |
| Alkalinity reference | Na₂CO₃ ACS primary standard | many | $14 | 0.1000 g/L = 1.887 meq/L = 5.28 dKH |
| NO₃ standard | KNO₃ ACS → 1000 ppm NO₃ stock | many | $12 | 1.631 g KNO₃ per litre DI = 1000 ppm NO₃ |
| PO₄ standard | KH₂PO₄ ACS → 100 ppm PO₄ stock | many | $12 | 0.1433 g KH₂PO₄ per litre DI = 100 ppm PO₄; refrigerate, remake monthly |
| pH buffers | 4.00 and 7.00 | — | $10/yr | in the Atlas kit, then 250 mL bottles |

Why the Trident NP kit: it is the only automation-grade *liquid* nitrate/phosphate reagent set sold to hobbyists. Hanna Checker, Salifert and Red Sea refills are powder packets and cannot be pumped. OpenReef is not affiliated with Neptune; using their reagents in this device is at your own risk and will not be supported by them.

Make calibration standards in **nitrate- and phosphate-free saltwater** (fresh salt mix with RO/DI), not DI water, so the matrix matches the tank.

## Mix (fallback if the kit is unavailable)

**Phosphate, APHA 4500-P E**

- Reagent A (combined): 50 mL 5 N H₂SO₄ + 5 mL 4 % ammonium molybdate + 15 mL 0.27 % potassium antimonyl tartrate; stable 6 months in HDPE.
- Reagent B: 1.76 g ascorbic acid in 100 mL DI; 1 week refrigerated, or add 2 mL formic acid for ~3 months.
- Dose 400 µL A + 400 µL B per 10 mL. Read at 880 nm after 10 min.

**Nitrate, vanadium(III) chloride (Schnetger & Lehners 2014)**

- 0.5 g VCl₃ in 100 mL 1 M HCl, then 0.2 g sulfanilamide and 0.01 g NEDD. Dark bottle, refrigerate; 1 month.
- Dose 1000 µL per 10 mL. 30–45 min at room temperature or 10 min at 45 °C. Read at 540 nm.
- Vanadium is toxic: gloves, HDPE waste, chemical-waste disposal.

The same hardware runs either chemistry; only the reagent profile in `config.yaml` changes (dose volumes, channels, development time). With two reagents per test you need only three syringe pumps.

## Accounting

Every dispense subtracts from the bottle's remaining volume in the database. The API reports remaining millilitres, estimated tests left and raises `reagent_low` at 10 %. After a bottle change call `POST /api/v1/reagents/{id}/refill` (optionally with the new volume) and `POST /api/v1/reagents/{id}/prime` to pull fresh reagent through the line. Run the kit's calibration solution as a check sample afterwards.

## Shelf life and storage

| Reagent | Opened shelf life | Storage |
|---|---|---|
| Trident NP reagents | 2 months (per Neptune) | in the bottle tray, out of sunlight |
| 0.02 N HCl | 3–4 months (evaporation shifts normality) | HDPE, cap with small vent |
| Na₂CO₃ standard solution | 1 month | glass, cool |
| PO₄ / NO₃ stocks | 1 month | refrigerated |
| pH buffers | 6 months after opening | capped |

## Handling

- Acid and reagent lines are PTFE; pump tube segments platinum-cured silicone; caps and fittings PP/PETG.
- Waste is collected in a 2 L HDPE bottle with a float switch; add the neutralizer at emptying; never return waste to the tank.
- Reagent bottles sit below the analyzer so a failed check valve cannot siphon reagent into a cell.
