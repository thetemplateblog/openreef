---
layout: single
title: Nitrate Assay Protocol
permalink: /docs/assays/nitrate/
toc: true
---

# Nitrate Assay Protocol

## Overview

The nitrate assay uses **cadmium reduction followed by the Griess test** to measure nitrate (NO₃⁻) concentration in aqueous samples. This two-step colorimetric method first reduces nitrate to nitrite, then produces a pink/purple azo dye whose intensity is proportional to nitrate concentration.

## Chemistry

### Reaction Mechanism

1. **Reduction Step**: Nitrate (NO₃⁻) is reduced to nitrite (NO₂⁻) using cadmium metal in acidic conditions

2. **Diazotization**: Nitrite reacts with sulfanilamide under acidic conditions to form a diazonium salt

3. **Coupling**: The diazonium salt couples with N-(1-naphthyl)-ethylenediamine (NED) to form a pink/purple azo dye

### Chemical Equations

**Step 1: Cadmium Reduction**
```
NO₃⁻ + Cd + 2H⁺ → NO₂⁻ + Cd²⁺ + H₂O
```

**Step 2: Griess Reaction**
```
NO₂⁻ + Sulfanilamide + H⁺ → Diazonium salt
Diazonium salt + NED → Pink/Purple Azo Dye (λmax = 540 nm, measured at 528 nm)
```

## Specifications

| Parameter | Value |
|-----------|-------|
| **Detection Method** | Colorimetric (cadmium reduction + Griess) |
| **Wavelength** | 528 nm (green LED) |
| **Measurement Range** | 0-90 ppm NO₃ (can measure 0-40 ppm with API kit) |
| **Reaction Time** | Minimum 5 minutes |
| **Color** | Pink/Purple (intensity ∝ concentration) |
| **pH Range** | Acidic (reagents adjust pH) |

## Reagents

### Required Materials

1. **API Nitrate Test Kit**
   - Bottle #1: Cadmium reduction reagent
   - Bottle #2: Griess reagent (sulfanilamide + NED)
   - **Important**: Shake Bottle #2 vigorously before use (contains suspension)
   - Typical shelf life: Check expiration date

2. **Nitrate Standard**
   - 1,000 ppm N stock (equivalent to 4,430 ppm as NO₃)
   - Commercially available or prepare from KNO₃
   - Store in dark at room temperature

3. **Distilled or RO Water**
   - For dilutions and blanks
   - Must be nitrate-free

### Preparing Calibration Standards

#### Working Stock (1,000 ppm NO₃)

From 4,430 ppm (1,000 ppm N) standard:
- Add **4.51 mL** of 4,430 ppm standard to a 50 mL tube
- Add **15.49 mL** distilled water
- Mix thoroughly
- Final volume: 20 mL at 1,000 ppm NO₃
- Label and date

#### Intermediate Stock (250 ppm NO₃)

From 1,000 ppm working stock:
- Add **6.25 mL** of 1,000 ppm stock to a 25 mL volumetric flask
- Dilute to 25 mL with distilled water
- Mix thoroughly

#### Calibration Series

From 250 ppm intermediate stock, prepare:

| Standard | Concentration (ppm NO₃) | 250 ppm Stock | Distilled Water | Total Volume |
|----------|------------------------|---------------|-----------------|--------------|
| Blank | 0 | 0 mL | 25 mL | 25 mL |
| S1 | 5 | 0.50 mL | 24.50 mL | 25 mL |
| S2 | 10 | 1.00 mL | 24.00 mL | 25 mL |
| S3 | 20 | 2.00 mL | 23.00 mL | 25 mL |
| S4 | 40 | 4.00 mL | 21.00 mL | 25 mL |
| S5 | 60 | 6.00 mL | 19.00 mL | 25 mL |
| S6 | 80 | 8.00 mL | 17.00 mL | 25 mL |
| S7 | 90 | 9.00 mL | 16.00 mL | 25 mL |

**Note**: Standards should be prepared fresh for calibration. Can be stored for up to 2 weeks in dark bottles at 4°C.

## Manual Protocol

### Equipment Needed

- Cuvettes (glass or plastic)
- Pipettes (accurate to 0.1 mL)
- Sample bottles with caps (for mixing)
- Colorimeter with 528 nm capability (green LED)
- Timer

### Step-by-Step Procedure

1. **Sample Preparation**
   - Fill sample bottle to **5 mL mark** with water sample
   - If sample is turbid, filter or allow to settle
   - Record sample ID and time

2. **Add Reagent #1** (Cadmium Reduction)
   - Add **10 drops** of Bottle #1 to sample
   - Cap and invert 3-4 times to mix
   - Solution should remain clear

3. **Prepare Reagent #2**
   - **SHAKE BOTTLE #2 VIGOROUSLY** for 30-60 seconds
   - Reagent contains a suspension that must be mixed
   - Inadequate shaking will result in low readings

4. **Add Reagent #2** (Griess Reagent)
   - Add **10 drops** of Bottle #2
   - **Shake sample thoroughly** (more vigorous than typical)
   - Solution will begin to turn pink/purple
   - **START TIMER**

5. **Incubation**
   - Wait **at least 5 minutes** for color development
   - Color is stable after 5 minutes
   - Can be read anytime after 5 minutes (no upper time limit like phosphate)

6. **Measurement** (After 5+ minutes)
   - Transfer sample to clean cuvette
   - Wipe cuvette exterior
   - Insert into colorimeter
   - Read absorbance at 528 nm (green LED)
   - Record reading

7. **Data Recording**
   - Note absorbance value
   - Note time since Reagent #2 addition
   - Compare to calibration curve

### Key Differences from Phosphate Assay

| Feature | Phosphate | Nitrate |
|---------|-----------|---------|
| Reagent drops | 6 drops each | 10 drops each |
| Bottle #2 prep | No special prep | **MUST shake 30-60 sec** |
| Mixing intensity | Gentle inversion | **Vigorous shaking** |
| Timing window | 5-10 min (strict) | 5+ min (flexible) |
| Color stability | Becomes cloudy after 10 min | Stable indefinitely |

## Automated Protocol (OpenReef System)

### System Requirements

- Calibrated colorimeter at 528 nm (green LED)
- Peristaltic pumps calibrated for 10-drop equivalent volumes (bidirectional)
- Bubble mixing via pump reversal (vigorous for nitrate)
- Reagent bottle bubble mixing for Bottle #2 (to suspend cadmium particles)

### Automated Sequence

```
1. System Cleaning
   └─ Flush with RO water → Waste

2. Sample Loading
   └─ Fill cuvette (5 mL test water)

3. Baseline Measurement
   └─ Zero colorimeter with sample

4. Reagent #2 Preparation
   └─ Bubble mix Reagent #2 bottle (5s reverse, 10s settle)

5. Reagent #1 Addition
   ├─ Pump 10 drops equivalent (~0.50 mL)
   ├─ Clear reagent line
   └─ Bubble mix (3s reverse, 5s settle)

6. Reagent #2 Addition
   ├─ Pump 10 drops equivalent (~0.50 mL)
   ├─ Clear reagent line
   ├─ START TIMER
   └─ Vigorous bubble mix (5s reverse, 10s settle)

7. Incubation
   └─ Wait 5 minutes minimum

8. Measurement
   ├─ Read absorbance @ 528 nm
   └─ Calculate concentration from calibration

9. System Cleaning
   └─ Flush with RO water → Waste

Total Time: ~10 minutes
```

### Critical: Reagent #2 Bottle Mixing

The automated system MUST bubble mix the Reagent #2 bottle before each use:
- Reverse pump for 5 seconds to create vigorous bubbles
- Allow 10 seconds for bubbles to suspend cadmium particles
- Bubble mixing can be repeated between tests if needed
- Without proper mixing, the cadmium particles settle, causing low readings

### Pump Calibration for Reagents

API test kit "drops" must be converted to volume:

- Measure volume of 10 drops from each reagent bottle
- Calculate average drop volume
- Typical: 1 drop ≈ 0.05 mL
- For 10 drops: ~0.50 mL per reagent
- Calibrate peristaltic pump to dispense accurate volume

## Interpreting Results

### Calibration Curve

Plot absorbance (y-axis) vs. concentration (x-axis) for standards:
- Should be linear in 0-90 ppm range
- R² > 0.99 for good calibration
- May show slight non-linearity at high concentrations
- Use linear regression: `y = mx + b`
  - y = absorbance
  - x = concentration (ppm NO₃)
  - m = slope (sensitivity)
  - b = y-intercept (blank absorbance)

### Calculating Concentration

From measured absorbance (A):

```
Concentration (ppm NO₃) = (A - b) / m
```

Where:
- A = measured absorbance
- b = y-intercept from calibration
- m = slope from calibration

### Quality Control

**Valid Result Criteria**:
- Absorbance within calibrated range
- Measurement taken after 5 minutes
- Blank absorbance < 0.050
- Duplicate samples within 15% RSD (higher tolerance than phosphate)

**Duplicate Measurements**:
- Always run samples in duplicate
- Average the two readings
- If difference > 15%, run a third replicate

**Out of Range**:
- If absorbance > calibration max: dilute sample 1:10 and re-test
- If absorbance < 0.010: may be below detection limit

### Detection Limits

- **Limit of Detection (LOD)**: ~0.2 ppm NO₃
- **Limit of Quantification (LOQ)**: ~0.5 ppm NO₃
- **Optimal Range**: 1-80 ppm NO₃

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| No color development | Expired reagents | Replace API kit |
| | Bottle #2 not shaken | Shake vigorously 30-60 sec |
| | Wrong reagent order | Ensure Bottle #1 before #2 |
| Very weak color | Bottle #2 settled | Shake Bottle #2 before EVERY use |
| | Insufficient mixing | Shake sample vigorously |
| | Low nitrate | Normal - within sensitivity |
| Inconsistent results | Bottle #2 not mixed properly | **Always shake Bottle #2** |
| | Temperature variation | Control temperature (20-25°C) |
| | Dirty cuvettes | Clean with dilute HCl, rinse well |
| Results lower than expected | Cadmium particles settled | Shake Bottle #2 longer |
| | Reagent degradation | Replace Bottle #2 |
| Color fades over time | Normal for very low concentrations | Read within 30 min |
| Precipitate in reagent bottle | Cadmium particles (normal) | Shake vigorously before use |
| High blank readings | Contaminated distilled water | Use fresh nitrate-free water |
| | Reagent contamination | Prepare fresh blank |

## Interferences

### Positive Interferences (False High)
- Nitrite (NO₂⁻): measured directly by Griess reaction (adds to reading)
- High chloride (> 1,000 ppm): can interfere with cadmium reduction
- Iron (Fe²⁺): can interfere with color development

### Negative Interferences (False Low)
- High sulfide: inhibits Griess reaction
- EDTA or other chelators: bind cadmium, prevent reduction

### Mitigation
- For nitrite interference: measure nitrite separately and subtract
- Dilute high-salinity samples (1:10 or 1:100)
- Remove sulfide by purging or oxidation before analysis

## Safety

### Reagent Hazards

**Bottle #1 (Cadmium Reduction)**:
- Contains cadmium metal (toxic heavy metal)
- Wear gloves and eye protection
- Avoid ingestion and inhalation
- Handle in well-ventilated area

**Bottle #2 (Griess Reagent)**:
- Contains sulfanilamide and NED
- Mild irritant
- Avoid skin contact

### Waste Disposal

⚠️ **IMPORTANT**: This test uses cadmium, which is a toxic heavy metal.

- **DO NOT** dispose of waste down the drain
- Collect all waste in a designated cadmium waste container
- Dispose as hazardous chemical waste
- Follow local environmental regulations
- Contact your institution's EH&S or local hazardous waste facility

### Cadmium Exposure Prevention

- Wear nitrile gloves when handling reagents
- Work in well-ventilated area
- Wash hands thoroughly after testing
- Do not eat, drink, or smoke while performing assay
- Clean work surfaces after use

## References

1. APHA Standard Method 4500-NO₃⁻ B: Cadmium Reduction Method
2. Griess, P. (1879) Bemerkungen zu der Abhandlung der HH. Weselsky und Benedikt
3. API Nitrate Test Kit Instructions
4. IoRodeo Nitrate Protocol: https://sites.google.com/iorodeo.com/biorodeo/nitrate

## Appendix: Conversion Factors

### Nitrate Units

Different reporting conventions:

```
NO₃⁻ (as NO₃) ÷ 4.427 = N (as N)
N (as N) × 4.427 = NO₃⁻ (as NO₃)
```

Example:
- 44.3 ppm NO₃ = 10.0 ppm N
- 10.0 ppm N = 44.3 ppm NO₃

### Common Reporting Formats

| Unit | Conversion |
|------|------------|
| ppm NO₃ | As measured |
| ppm NO₃-N | Divide by 4.427 |
| mg/L NO₃ | Same as ppm NO₃ |
| mg/L N | Divide by 4.427 |
| mM NO₃ | Divide by 62.0 |

### Standard Preparation

To prepare 1,000 ppm N (4,430 ppm NO₃) from KNO₃:

```
1,000 ppm N = 7,218 mg KNO₃ per liter

Calculation:
MW(KNO₃) = 101.1 g/mol
MW(N) = 14.0 g/mol

(1,000 mg N/L) × (101.1/14.0) = 7,218 mg KNO₃/L
```

Procedure:
1. Dissolve 7.218 g KNO₃ in ~800 mL distilled water
2. Add 2 mL chloroform (preservative, optional)
3. Dilute to 1 liter
4. Store in dark bottle, stable for 6 months

## Comparison: Nitrate vs Nitrite

The Griess test actually measures **nitrite (NO₂⁻)**, not nitrate directly. The cadmium reduction step converts nitrate to nitrite.

| Species | Measured By | Notes |
|---------|-------------|-------|
| NO₃⁻ (Nitrate) | Cadmium reduction + Griess | Total test (this protocol) |
| NO₂⁻ (Nitrite) | Griess only (skip Bottle #1) | Direct measurement |

To measure **nitrite only**:
- Skip Bottle #1
- Add only Bottle #2
- Result is nitrite concentration

To calculate **nitrate only**:
- Run test with both bottles (total = NO₃ + NO₂)
- Run test with only Bottle #2 (nitrite only)
- Nitrate = Total - Nitrite
