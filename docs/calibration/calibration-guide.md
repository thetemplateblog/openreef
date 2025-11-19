---
layout: single
title: Calibration Guide
permalink: /docs/calibration/calibration-guide/
toc: true
---

# Calibration Guide

## Overview

Calibration is the process of establishing the relationship between colorimeter readings (absorbance) and known analyte concentrations. Accurate calibration is essential for obtaining reliable quantitative results from the OpenReef system.

## Calibration Types

The OpenReef system requires **three types of calibration**:

1. **Colorimeter Calibration**: Establish concentration vs. absorbance curves
2. **Pump Calibration**: Measure accurate flow rates for volume control
3. **System Verification**: Periodic quality control checks

## Colorimeter Calibration

### When to Calibrate

- **Initial setup**: Before first use
- **After reagent replacement**: New API test kit batches may vary slightly
- **Monthly**: Routine maintenance
- **After sensor changes**: If colorimeter sensor is replaced
- **When results drift**: If QC checks show drift > 10%

### Materials Needed

#### For Phosphate Calibration

- Phosphate standard (1,000 ppm PO₄)
- Distilled/RO water
- Volumetric flasks (25 mL, 100 mL)
- Pipettes (1 mL, 5 mL, 10 mL)
- API Phosphate test kit
- Clean cuvettes

#### For Nitrate Calibration

- Nitrate standard (4,430 ppm NO₃ or 1,000 ppm N)
- Distilled/RO water
- Volumetric flasks (25 mL, 50 mL)
- Pipettes (1 mL, 5 mL, 10 mL)
- API Nitrate test kit
- Clean cuvettes

### Phosphate Calibration Procedure

#### Step 1: Prepare Standards

From 1,000 ppm stock, prepare 37.5 ppm working stock:
- 3.75 mL of 1,000 ppm + distilled water to 100 mL

From 37.5 ppm working stock, prepare calibration series:

| Standard | Concentration (ppm) | Working Stock | Water | Total |
|----------|---------------------|---------------|-------|-------|
| S0 (Blank) | 0 | 0 mL | 25 mL | 25 mL |
| S1 | 1.0 | 0.67 mL | 24.33 mL | 25 mL |
| S2 | 2.5 | 1.67 mL | 23.33 mL | 25 mL |
| S3 | 5.0 | 3.33 mL | 21.67 mL | 25 mL |
| S4 | 10.0 | 6.67 mL | 18.33 mL | 25 mL |
| S5 | 15.0 | 10.0 mL | 15.0 mL | 25 mL |
| S6 | 20.0 | 13.33 mL | 11.67 mL | 25 mL |
| S7 | 30.0 | 20.0 mL | 5.0 mL | 25 mL |

#### Step 2: Run Standards Through Assay

For each standard (in order from lowest to highest):

1. Load 5 mL standard into system (or manual cuvette)
2. Add 6 drops Bottle #1, mix
3. Add 6 drops Bottle #2, mix, start timer
4. Wait 7.5 minutes
5. Read absorbance at 625 nm
6. Record: concentration, absorbance, time, temperature
7. Clean system/cuvette before next standard

**Important**: Run standards in duplicate (2 measurements each)

#### Step 3: Calculate Calibration Curve

Plot absorbance (y) vs. concentration (x):

```
Absorbance = m × Concentration + b
```

Perform linear regression to find:
- **m** (slope): sensitivity
- **b** (y-intercept): blank absorbance
- **R²**: correlation coefficient (should be > 0.99)

#### Step 4: Save Calibration Data

Save to `phosphate_cal.json`:

```json
{
  "assay": "phosphate",
  "date": "2025-11-14",
  "wavelength": 625,
  "units": "ppm PO4",
  "calibration": {
    "slope": 0.0456,
    "intercept": 0.012,
    "r_squared": 0.9987
  },
  "range": {
    "min": 0.0,
    "max": 30.0
  },
  "standards": [
    {"concentration": 0.0, "absorbance": 0.011, "replicate": 1},
    {"concentration": 0.0, "absorbance": 0.013, "replicate": 2},
    {"concentration": 1.0, "absorbance": 0.058, "replicate": 1},
    {"concentration": 1.0, "absorbance": 0.056, "replicate": 2},
    ...
  ],
  "reagent_lot": "API-PO4-2025-03",
  "notes": "New sensor calibration"
}
```

### Nitrate Calibration Procedure

#### Step 1: Prepare Standards

From 4,430 ppm (1,000 ppm N) stock:
- Prepare 1,000 ppm NO₃ working stock:
  - 4.51 mL of 4,430 ppm + 15.49 mL water = 20 mL

From 1,000 ppm, prepare 250 ppm intermediate:
- 6.25 mL of 1,000 ppm + water to 25 mL

From 250 ppm, prepare calibration series:

| Standard | Concentration (ppm) | 250 ppm Stock | Water | Total |
|----------|---------------------|---------------|-------|-------|
| S0 (Blank) | 0 | 0 mL | 25 mL | 25 mL |
| S1 | 5 | 0.50 mL | 24.50 mL | 25 mL |
| S2 | 10 | 1.00 mL | 24.00 mL | 25 mL |
| S3 | 20 | 2.00 mL | 23.00 mL | 25 mL |
| S4 | 40 | 4.00 mL | 21.00 mL | 25 mL |
| S5 | 60 | 6.00 mL | 19.00 mL | 25 mL |
| S6 | 80 | 8.00 mL | 17.00 mL | 25 mL |
| S7 | 90 | 9.00 mL | 16.00 mL | 25 mL |

#### Step 2: Run Standards Through Assay

For each standard:

1. **IMPORTANT**: Shake Bottle #2 vigorously for 30-60 seconds
2. Load 5 mL standard into system
3. Add 10 drops Bottle #1, mix
4. Add 10 drops Bottle #2, mix vigorously, start timer
5. Wait 5+ minutes
6. Read absorbance at 528 nm
7. Record data
8. Clean before next standard

Run in duplicate.

#### Step 3: Calculate & Save

Same process as phosphate. Save to `nitrate_cal.json`:

```json
{
  "assay": "nitrate",
  "date": "2025-11-14",
  "wavelength": 528,
  "units": "ppm NO3",
  "calibration": {
    "slope": 0.0234,
    "intercept": 0.008,
    "r_squared": 0.9992
  },
  "range": {
    "min": 0.0,
    "max": 90.0
  },
  "standards": [...],
  "reagent_lot": "API-NO3-2025-02",
  "notes": "Vigorous shaking of Bottle #2 confirmed"
}
```

## Pump Calibration

### Why Calibrate Pumps

Peristaltic pump flow rates vary with:
- Tubing size and wear
- Voltage/power supply
- Temperature
- Back pressure

Accurate calibration ensures correct reagent volumes.

### Procedure

#### Equipment Needed

- Graduated cylinder (10 mL or 25 mL)
- Stopwatch
- Distilled water
- Scale (optional, for gravimetric verification)

#### FeW Pump (Water)

**Forward Direction:**

1. Place pump outlet in graduated cylinder
2. Start with empty cylinder
3. Start pump and timer simultaneously
4. Run until ~20 mL collected
5. Stop pump and timer
6. Record volume and time

```
Flow rate (mL/s) = Volume (mL) / Time (s)
```

Repeat 3 times, average results.

**Reverse Direction:**

Same procedure (flow may differ slightly).

#### FeR Pump (Reagent)

Same as FeW pump, but use smaller volumes (10 mL) for slower reagent pump.

### Drop Volume Calibration

To convert "drops" to mL:

1. Dispense exactly 20 drops from reagent bottle
2. Collect in graduated cylinder
3. Measure volume
4. Calculate: `drop_volume = total_volume / 20`

Repeat for each reagent bottle.

### Save Calibration

Save to `pump_cal.json`:

```json
{
  "date": "2025-11-14",
  "FeW_pump": {
    "forward": {
      "flow_rate_ml_per_sec": 1.23,
      "std_dev": 0.05
    },
    "reverse": {
      "flow_rate_ml_per_sec": 1.19,
      "std_dev": 0.04
    }
  },
  "FeR_pump": {
    "forward": {
      "flow_rate_ml_per_sec": 0.41,
      "std_dev": 0.02
    },
    "reverse": {
      "flow_rate_ml_per_sec": 0.39,
      "std_dev": 0.02
    }
  },
  "drop_volumes": {
    "phosphate_bottle_1": 0.048,
    "phosphate_bottle_2": 0.050,
    "nitrate_bottle_1": 0.049,
    "nitrate_bottle_2": 0.051
  }
}
```

## Automated Calibration (Using PyBadge)

### Calibration Wizard

The firmware includes an automated calibration wizard:

```
Menu > Calibration > Run Calibration
  ├─ Phosphate Calibration
  ├─ Nitrate Calibration
  └─ Pump Calibration
```

### Automated Process

1. **Select assay type** (phosphate or nitrate)
2. **Enter number of standards** (typically 7-8)
3. **For each standard:**
   - Prompt: "Load standard X (Y.Y ppm)"
   - Wait for user confirmation
   - Run automated assay sequence
   - Record absorbance
4. **Calculate calibration curve**
   - Display slope, intercept, R²
5. **Review and save**
   - Show calibration plot
   - Save to JSON file

### Manual Entry Option

If standards were run manually, can enter data:

```
Menu > Calibration > Manual Entry
```

Enter concentration and absorbance pairs, system calculates curve.

## Quality Control

### QC Standards

Prepare mid-range QC standards:
- **Phosphate QC**: 5.0 ppm and 15.0 ppm
- **Nitrate QC**: 20 ppm and 60 ppm

Store in dark bottles at 4°C, stable for 2 weeks.

### QC Frequency

Run QC standards:
- **Daily**: If running multiple samples
- **Weekly**: For occasional use
- **Before important measurements**

### Acceptance Criteria

QC result must be within **±10%** of expected value:

```
Expected: 5.0 ppm
Measured: 4.5-5.5 ppm → PASS
Measured: 3.8 ppm → FAIL (recalibrate)
```

### QC Log

Track QC results over time:

```csv
date,assay,qc_standard,expected,measured,percent_error,status
2025-11-14,phosphate,5.0,5.0,5.1,+2%,PASS
2025-11-14,phosphate,15.0,15.0,14.7,-2%,PASS
2025-11-15,nitrate,20.0,20.0,21.5,+7.5%,PASS
```

Plot percent error over time to detect drift.

## Calibration Verification

### Independent Standard

Verify calibration using a standard from a **different source** than calibration standards:

- Purchase certified reference material (CRM)
- Prepare fresh standard from different lot of KH₂PO₄ or KNO₃
- Run through system
- Compare result to known value

Should agree within **±5%**.

### Recovery Test

Spike a known amount of analyte into a sample:

1. Measure sample: C₁ = 2.0 ppm
2. Add 5.0 ppm spike
3. Expected: C₂ = 7.0 ppm
4. Measured: C₂ = 6.8 ppm
5. Recovery = (6.8 - 2.0) / 5.0 = 96% ✓

Acceptable recovery: **90-110%**

## Troubleshooting Calibration Issues

### Poor R² (< 0.99)

**Possible causes:**
- Standards prepared incorrectly
- Inconsistent timing (phosphate)
- Dirty cuvette
- Temperature fluctuations
- Reagent #2 not shaken (nitrate)

**Solutions:**
- Prepare fresh standards carefully
- Use automated timing
- Clean/replace cuvette
- Control temperature
- Always shake Bottle #2

### Non-linear Curve

**Possible causes:**
- Concentration range too wide
- High concentrations saturate sensor
- Chemical interference at high concentrations

**Solutions:**
- Use narrower concentration range
- Limit max standard to 80% of sensor range
- Check for color saturation (absorbance > 2.0)

### Negative Intercept

**Possible causes:**
- Blank contaminated
- Baseline drift
- Sensor zero error

**Solutions:**
- Prepare fresh blank
- Re-zero sensor
- Check for light leaks

### High Blank Absorbance

**Possible causes:**
- Distilled water contaminated
- Reagent contamination
- Dirty cuvette

**Solutions:**
- Use fresh distilled/RO water
- Replace reagents
- Clean cuvette thoroughly

## Calibration Best Practices

1. **Use fresh reagents**: Check expiration dates
2. **Consistent technique**: Use same procedure for standards and samples
3. **Temperature control**: Run calibration at same temp as samples (20-25°C)
4. **Clean glassware**: Rinse with distilled water, dry thoroughly
5. **Duplicate measurements**: Always run standards in duplicate
6. **Fresh standards**: Prepare on day of calibration
7. **Record everything**: Date, lot numbers, temperatures, notes
8. **Verify**: Run QC standards immediately after calibration

## Recalibration Triggers

Recalibrate if:

- QC fails (>10% error)
- Drift trend observed (QC creeping in one direction)
- New reagent lot
- Sensor replaced
- Tubing replaced (pumps)
- Results don't make sense
- > 1 month since last calibration

## Data Management

### Calibration File Naming

```
phosphate_cal_YYYY-MM-DD.json
nitrate_cal_YYYY-MM-DD.json
pump_cal_YYYY-MM-DD.json
```

### Backup

- Keep all calibration files
- Never delete old calibrations
- Useful for tracking performance over time

### Active Calibration

System uses the most recent calibration file by default. Can manually select older calibration if needed.

## Example Calibration Data Analysis

### Calculating Concentration from Absorbance

Given calibration:
- Slope (m) = 0.0456
- Intercept (b) = 0.012

Sample absorbance = 0.240

```
Concentration = (Absorbance - b) / m
Concentration = (0.240 - 0.012) / 0.0456
Concentration = 5.0 ppm PO₄
```

### Uncertainty Estimation

Standard error of regression (Sy/x) gives uncertainty:

If Sy/x = 0.15 ppm, then:
- Measured: 5.0 ± 0.15 ppm (95% confidence)

Report as: 5.0 ppm (range: 4.85-5.15 ppm)

## Next Steps

- Review [Phosphate Assay Protocol](../assays/phosphate.md)
- Review [Nitrate Assay Protocol](../assays/nitrate.md)
- See [Firmware Documentation](../firmware/automation-sequence.md) for automated calibration code
