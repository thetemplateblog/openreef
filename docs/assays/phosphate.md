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

### Comparison of Test Kits

| Parameter | API Phosphate Kit | Red Sea Phosphate Pro |
|-----------|-------------------|----------------------|
| **Detection Method** | Colorimetric (ascorbic acid) | Colorimetric (ascorbic acid) |
| **Optimal Wavelength** | 880 nm (measured at 625 nm) | 880 nm (IR LED) |
| **Measurement Range** | 0-30 ppm PO₄ | 0-5 ppm PO₄ |
| **Optimal Range** | 0.5-25 ppm | 0-1 ppm |
| **Accuracy** | ±1 ppm | ±0.02 ppm |
| **Precision** | ~0.5 ppm | 0.01 ppm |
| **LOD** | ~0.05 ppm | ~0.02 ppm |
| **LOQ** | ~0.10 ppm | ~0.05 ppm |
| **Reaction Time** | 5-10 minutes | Per kit instructions |
| **Color** | Blue (molybdenum blue) | Light blue (molybdenum blue) |
| **Tests per Kit** | ~150 | 100 |
| **Best Use** | General aquarium (0-10 ppm) | Ultra-low reef (0-1 ppm) |

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

---

## Red Sea Phosphate Pro Protocol

### Overview

The **Red Sea Phosphate Pro** test kit is designed for ultra-low phosphate measurements in reef aquariums, providing exceptional accuracy (±0.02 ppm) in the 0-1 ppm range where reef systems typically operate.

### Hardware Requirements

#### LED Configuration
- **Optimal**: **880 nm infrared LED** (maximum sensitivity)
- Alternative: 710-720 nm (95% sensitivity)
- Not recommended: 625 nm red LED (only 30-40% sensitivity)

#### Sensor Setup (TSL2591)
- Use **Channel 1** (IR photodiode) for 880 nm LED
- IR channel has good response in 650-950 nm range
- Peak sensitivity: 800-850 nm

### Preparing Reference Standards (0-1 ppm range)

#### Stock Solution (100 ppm PO₄)

**Materials**:
- Potassium phosphate monobasic (KH₂PO₄, anhydrous, ACS grade)
- Distilled or RO/DI water
- 1000 mL volumetric flask
- Analytical balance (0.0001 g precision)

**Preparation**:
1. Weigh **0.1433 g** KH₂PO₄ (anhydrous)
   - MW KH₂PO₄ = 136.09 g/mol
   - MW PO₄³⁻ = 94.97 g/mol
   - Conversion: 136.09 / 94.97 = 1.433
2. Dissolve in ~500 mL distilled water
3. Dilute to 1000 mL mark
4. Mix thoroughly (invert 20 times)
5. Store refrigerated at 4°C (stable 6 months)

#### Intermediate Solution (10 ppm PO₄) - Recommended

1. Pipette 10.00 mL of 100 ppm stock
2. Transfer to 100 mL volumetric flask
3. Fill to mark with distilled water
4. Mix thoroughly
5. Store refrigerated (stable 1 month)

#### Working Standards (0-1 ppm)

From 10 ppm intermediate solution:

| Concentration | 10 ppm Stock | Distilled Water | Total Volume |
|---------------|--------------|-----------------|--------------|
| 0.00 ppm      | 0.0 mL       | 100 mL          | 100 mL       |
| 0.10 ppm      | 1.0 mL       | 99.0 mL         | 100 mL       |
| 0.25 ppm      | 2.5 mL       | 97.5 mL         | 100 mL       |
| 0.50 ppm      | 5.0 mL       | 95.0 mL         | 100 mL       |
| 0.75 ppm      | 7.5 mL       | 92.5 mL         | 100 mL       |
| 1.00 ppm      | 10.0 mL      | 90.0 mL         | 100 mL       |

**Storage**: Prepare fresh daily for best accuracy. If stored, refrigerate and use within 1 week.

### Calibration Procedure

1. **Blank the colorimeter** with distilled water
2. **Measure each standard** (3-6 replicates per concentration)
   - Add Red Sea Pro reagents per kit instructions
   - Wait for color development
   - Record absorbance value
3. **Calculate fit coefficients** using linear regression
   - Plot concentration (ppm) vs absorbance
   - Should be linear with R² > 0.995
4. **Update calibration file** with new coefficients

#### Expected Performance

With 880 nm LED:
- **Linearity**: R² > 0.995
- **Precision**: 2-5% RSD
- **Sensitivity**: ~3x better than 625 nm LED
- **Detection limit**: 0.02 ppm PO₄

### Software Configuration

#### Modify `src/light_sensor.py`

Change to use IR channel for 880 nm LED:

```python
self.channel = 1  # Use IR channel (1) for 880nm LED
```

#### Update `calibrations.json`

```json
{
  "Phosphate Red Sea Pro": {
    "units": "ppm",
    "led": "880",
    "fit_type": "polynomial",
    "fit_coef": [
      3.521845,
      -0.012456
    ],
    "range": {
      "min": 0.00,
      "max": 0.65
    }
  }
}
```

**Note**: `fit_coef` values shown are examples. Perform calibration to determine actual coefficients for your system.

### Quality Control

**Method Blank**:
- Distilled water processed with reagents
- Should read 0.00 ± 0.01 ppm

**Continuing Calibration Verification (CCV)**:
- Run 0.50 ppm standard every 10 samples
- Should be within ±10% of expected value

**Duplicate Samples**:
- Run 1 duplicate per 10 samples
- RPD < 10%

### Commercial Reference Standards (Alternative)

If preparing standards is impractical:

**Hanna Phosphate Standards**:
- HI774-11: 0.00 ppm (blank)
- HI774-12: 0.25 ppm
- HI774-13: 0.50 ppm

**NIST Traceable Standards**:
- Available from scientific suppliers
- Certified accuracy
- Typical: 0.1, 0.5, 1.0, 5.0 ppm PO₄

### Troubleshooting Red Sea Pro

| Issue | Cause | Solution |
|-------|-------|----------|
| Readings negative | Calibration intercept too high | Re-calibrate with fresh standards |
| Poor repeatability (>10% RSD) | Inconsistent mixing/timing | Control temperature, use timer |
| Non-linear curve | Reagent issues, LED saturation | Fresh reagents, reduce integration time |
| Drift over time | Reagent degradation | Re-calibrate monthly |
| Doesn't match comparator | Different timing | Ensure exact same reaction time |

### Best Practices

- Always blank before measurements
- Control temperature (20-25°C)
- Follow exact reaction timing
- Filter turbid samples
- Store reagents cool and dark
- Check expiration dates
- Re-calibrate monthly

---

## Manual Protocol (API Kit)

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
- **For silicate interference**: Use 880 nm IR LED instead of 625 nm
  - 880 nm is optimal wavelength for molybdenum blue method
  - Provides 3x better sensitivity than 625 nm
  - Reduces silicate interference
  - Required for ultra-low range (0-1 ppm) measurements

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

### Standards and Methods
1. APHA Standard Method 4500-P E: Standard Methods for the Examination of Water and Wastewater
2. Murphy, J. and Riley, J.P. (1962) A modified single solution method for the determination of phosphate in natural waters
3. EPA Method 365.3: Phosphorous, All Forms (Colorimetric, Ascorbic Acid)

### Test Kit Documentation
4. API Phosphate Test Kit Instructions
5. Red Sea Phosphate Pro Manual: https://g1.redseafish.com/support/manuals/products/phosphate-pro/
6. IoRodeo Phosphate Protocol: https://sites.google.com/iorodeo.com/biorodeo/phosphate

### Sensor Documentation
7. TSL2591 High Dynamic Range Digital Light Sensor Datasheet: https://cdn-shop.adafruit.com/datasheets/TSL25911_Datasheet_EN_v1.pdf
8. AMS TSL25911 Product Page: https://ams-osram.com/products/sensor-solutions/ambient-light-color-spectral-proximity-sensors/ams-tsl25911-ambient-light-sensor

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
