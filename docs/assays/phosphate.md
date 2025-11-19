---
layout: single
title: Phosphate Assay Protocol
permalink: /docs/assays/phosphate/
toc: true
---

# Phosphate Assay Protocol

## Overview

The phosphate assay uses the **ascorbic acid method** (APHA Standard Method 4500-P E) to measure orthophosphate (PO₄³⁻) concentration in aqueous samples. This colorimetric method produces a blue color whose intensity is proportional to phosphate concentration.

## Chemistry

### Reaction Mechanism

1. **Complex Formation**: Orthophosphate reacts with ammonium molybdate and potassium antimonyl tartrate to form a heteropoly acid (phosphomolybdic acid)

2. **Reduction**: Ascorbic acid reduces the phosphomolybdic acid complex to form an intensely blue-colored molybdenum blue compound

3. **Color Development**: The blue color intensity is directly proportional to phosphate concentration

### Chemical Equation (Simplified)

```
PO₄³⁻ + Mo⁶⁺ + Sb³⁺ → [PMo₁₂O₄₀]³⁻ (phosphomolybdate complex)
                         ↓ Ascorbic acid
                    Molybdenum Blue (λmax = 880 nm, measured at 625 nm)
```

## Specifications

| Parameter | Value |
|-----------|-------|
| **Detection Method** | Colorimetric (ascorbic acid reduction) |
| **Wavelength** | 625 nm (red LED) |
| **Measurement Range** | 0-30 ppm PO₄ (API kit) |
| **Alternative Ranges** | 0-5 ppm or 0-90 ppm with different kits |
| **Reaction Time** | 5-10 minutes |
| **Color** | Blue (intensity ∝ concentration) |
| **pH Range** | Acidic (reagents adjust pH) |

## Reagents

### Required Materials

1. **API Phosphate Test Kit**
   - Bottle #1: Molybdate reagent
   - Bottle #2: Ascorbic acid reagent
   - Typical shelf life: Check expiration date

2. **Phosphate Standard**
   - 1,000 ppm PO₄ stock (330 ppm as P)
   - Commercially available or prepare from KH₂PO₄
   - Store in dark at room temperature

3. **Distilled or RO Water**
   - For dilutions and blanks
   - Must be phosphate-free

### Preparing Calibration Standards

#### Working Stock (37.5 ppm PO₄)

From 1,000 ppm standard:
- Add **3.75 mL** of 1,000 ppm standard to a 100 mL volumetric flask
- Dilute to 100 mL with distilled water
- Mix thoroughly
- Label and date

#### Calibration Series

From 37.5 ppm working stock, prepare:

| Standard | Concentration (ppm PO₄) | Working Stock | Distilled Water | Total Volume |
|----------|------------------------|---------------|-----------------|--------------|
| Blank | 0 | 0 mL | 25 mL | 25 mL |
| S1 | 1.0 | 0.67 mL | 24.33 mL | 25 mL |
| S2 | 2.5 | 1.67 mL | 23.33 mL | 25 mL |
| S3 | 5.0 | 3.33 mL | 21.67 mL | 25 mL |
| S4 | 10.0 | 6.67 mL | 18.33 mL | 25 mL |
| S5 | 15.0 | 10.0 mL | 15.0 mL | 25 mL |
| S6 | 20.0 | 13.33 mL | 11.67 mL | 25 mL |
| S7 | 30.0 | 20.0 mL | 5.0 mL | 25 mL |

**Note**: Standards should be prepared fresh for calibration. Can be stored for up to 1 week in dark bottles at 4°C.

## Manual Protocol

### Equipment Needed

- Cuvettes (glass or plastic)
- Pipettes (accurate to 0.1 mL)
- Sample bottles with caps (for mixing)
- Colorimeter with 625 nm capability
- Timer

### Step-by-Step Procedure

1. **Sample Preparation**
   - Fill sample bottle to **5 mL mark** with water sample
   - If sample is turbid, filter or allow to settle
   - Record sample ID and time

2. **Add Reagent #1** (Molybdate)
   - Add **6 drops** of Bottle #1 to sample
   - Cap and invert 3-4 times to mix
   - Solution should be clear

3. **Add Reagent #2** (Ascorbic Acid)
   - Add **6 drops** of Bottle #2
   - **START TIMER immediately**
   - Cap and invert 3-4 times to mix thoroughly
   - Solution will begin to turn blue

4. **Incubation**
   - Wait **5-10 minutes** for color development
   - Color develops progressively
   - **CRITICAL**: Do not exceed 10 minutes

5. **Measurement Window** (5-10 minutes after Reagent #2)
   - Transfer sample to clean cuvette
   - Wipe cuvette exterior
   - Insert into colorimeter
   - Read absorbance at 625 nm
   - Record reading

6. **Data Recording**
   - Note absorbance value
   - Note exact time since Reagent #2 addition
   - Compare to calibration curve

### Critical Timing Warning

⚠️ **IMPORTANT**: After approximately 10 minutes, the solution becomes cloudy and you will not get an accurate reading. The measurement MUST be taken within the 5-10 minute window.

## Automated Protocol (OpenReef System)

### System Requirements

- Calibrated colorimeter at 625 nm
- Peristaltic pumps calibrated for 6-drop equivalent volumes (bidirectional)
- Bubble mixing via pump reversal
- Temperature control (optional but recommended)

### Automated Sequence

The OpenReef system automates the entire protocol:

```
1. System Cleaning
   └─ Flush with RO water → Waste

2. Sample Loading
   └─ Fill cuvette (5 mL test water)

3. Baseline Measurement
   └─ Zero colorimeter with sample

4. Reagent #1 Addition
   ├─ Pump 6 drops equivalent
   ├─ Clear reagent line
   └─ Bubble mix (3s reverse, 5s settle)

5. Reagent #2 Addition
   ├─ Pump 6 drops equivalent
   ├─ Clear reagent line
   ├─ START TIMER
   └─ Bubble mix (3s reverse, 5s settle)

6. Incubation
   └─ Wait 7.5 minutes (mid-point of 5-10 min window)

7. Measurement
   ├─ Read absorbance @ 625 nm
   └─ Calculate concentration from calibration

8. System Cleaning
   └─ Flush with RO water → Waste

Total Time: ~12 minutes
```

### Pump Calibration for Reagents

API test kit "drops" must be converted to volume:

- Measure volume of 10 drops from each reagent bottle
- Calculate average drop volume
- Typical: 1 drop ≈ 0.05 mL
- For 6 drops: ~0.30 mL per reagent
- Calibrate peristaltic pump to dispense accurate volume

## Interpreting Results

### Calibration Curve

Plot absorbance (y-axis) vs. concentration (x-axis) for standards:
- Should be linear in 0-30 ppm range
- R² > 0.99 for good calibration
- Use linear regression: `y = mx + b`
  - y = absorbance
  - x = concentration (ppm PO₄)
  - m = slope (sensitivity)
  - b = y-intercept (blank absorbance)

### Calculating Concentration

From measured absorbance (A):

```
Concentration (ppm PO₄) = (A - b) / m
```

Where:
- A = measured absorbance
- b = y-intercept from calibration
- m = slope from calibration

### Quality Control

**Valid Result Criteria**:
- Absorbance within calibrated range
- Measurement taken at 5-10 minutes
- Blank absorbance < 0.050
- Duplicate samples within 10% RSD

**Out of Range**:
- If absorbance > calibration max: dilute sample and re-test
- If absorbance < 0.010: may be below detection limit

### Detection Limits

- **Limit of Detection (LOD)**: ~0.05 ppm PO₄
- **Limit of Quantification (LOQ)**: ~0.10 ppm PO₄
- **Optimal Range**: 0.5-25 ppm PO₄

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| No color development | Expired reagents | Replace API kit |
| | Wrong reagent order | Ensure Bottle #1 before #2 |
| | Insufficient mixing | Ensure adequate bubble mixing after each reagent |
| Weak/pale color | Low phosphate | Normal - within sensitivity |
| | Reagent degradation | Check expiration, replace if old |
| Solution cloudy before 10 min | Contamination | Use clean cuvettes/bottles |
| | Particulates in sample | Filter sample |
| Solution cloudy after 10 min | Normal reaction progress | Re-run test, read at 5-10 min |
| Color too dark to read | Concentration too high | Dilute sample (1:10 or 1:100) |
| Inconsistent results | Temperature variation | Control temperature (20-25°C) |
| | Timing inconsistency | Use automated timer |
| | Dirty cuvettes | Clean with dilute HCl, rinse well |
| Negative concentration | Blank contamination | Prepare fresh blank |
| | Calibration error | Re-calibrate system |

## Interferences

### Positive Interferences (False High)
- Silicate (> 10 ppm): can form similar blue complex
- Arsenate: reacts identically to phosphate
- High turbidity: scatters light, increases absorbance

### Negative Interferences (False Low)
- High sulfide: reduces color development
- High iron (> 100 ppm): can precipitate phosphate

### Mitigation
- Filter turbid samples
- Use sample dilution if interferences suspected
- For silicate interference: use alternative wavelength (880 nm)

## Safety

### Reagent Hazards

**Bottle #1 (Molybdate)**:
- Contains sulfuric acid (corrosive)
- Wear gloves and eye protection
- Avoid skin contact

**Bottle #2 (Ascorbic Acid)**:
- Generally safe
- Mild irritant

### Waste Disposal

- Small volumes can be neutralized and disposed of via drain
- Larger volumes: collect and dispose as chemical waste
- Follow local regulations

## References

1. APHA Standard Method 4500-P E: Standard Methods for the Examination of Water and Wastewater
2. Murphy, J. and Riley, J.P. (1962) A modified single solution method for the determination of phosphate in natural waters
3. API Phosphate Test Kit Instructions
4. IoRodeo Phosphate Protocol: https://sites.google.com/iorodeo.com/biorodeo/phosphate

## Appendix: Conversion Factors

### Phosphate Units

Different reporting conventions:

```
PO₄³⁻ (as PO₄) ÷ 3.066 = P (as P)
P (as P) × 3.066 = PO₄³⁻ (as PO₄)
```

Example:
- 1.0 ppm PO₄ = 0.33 ppm P
- 0.33 ppm P = 1.0 ppm PO₄

### Standard Preparation

To prepare 1,000 ppm PO₄ from KH₂PO₄:

```
1,000 ppm PO₄ = 1,433 mg KH₂PO₄ per liter

Calculation:
MW(KH₂PO₄) = 136.09 g/mol
MW(PO₄) = 94.97 g/mol

(1,000 mg PO₄/L) × (136.09/94.97) = 1,433 mg KH₂PO₄/L
```

Procedure:
1. Dissolve 1.433 g KH₂PO₄ in ~800 mL distilled water
2. Add 5 mL concentrated H₂SO₄ (preservative)
3. Dilute to 1 liter
4. Store in dark bottle, stable for 6 months
