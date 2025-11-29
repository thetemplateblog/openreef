# Calibrations File Format

## Overview

The `calibrations.json` file contains calibration data for different assay types. Each assay has specific LED wavelengths, fit coefficients, and valid measurement ranges.

## File Structure

```json
{
  "Assay Name": {
    "units": "ppm",
    "led": "528",
    "fit_type": "polynomial",
    "fit_coef": [
      slope,
      intercept
    ],
    "range": {
      "min": 0.0,
      "max": 10.0
    }
  }
}
```

## Field Descriptions

### units
The measurement units for concentration values. Typically `"ppm"` (parts per million), which is equivalent to mg/L for dilute aqueous solutions.

### led
The LED wavelength in nanometers (nm) used for this assay:
- **"528"** - Green LED for nitrate/nitrite (Griess reaction)
- **"625"** - Red LED for phosphate API kit (molybdenum blue at 625 nm)
- **"880"** - IR LED for Red Sea Phosphate Pro (molybdenum blue optimal wavelength)

### fit_type
The type of calibration curve fit. Currently supports:
- **"polynomial"** - Polynomial fit (linear or higher order)

### fit_coef
Array of polynomial coefficients for the calibration curve.

**For linear fit (2 coefficients)**:
```
concentration = fit_coef[0] * absorbance + fit_coef[1]
```
- `fit_coef[0]` = slope
- `fit_coef[1]` = intercept

**For polynomial fit (3+ coefficients)**:
```
concentration = fit_coef[0] * absorbance² + fit_coef[1] * absorbance + fit_coef[2]
```

### range
The **calibrated absorbance range** for this specific calibration dataset.

**IMPORTANT**: These values represent the min/max absorbance values from the actual calibration standards used, NOT the theoretical instrument capability.

- **"min"**: Minimum absorbance in calibration (typically 0.0 for blank)
- **"max"**: Maximum absorbance in calibration dataset

**Example**: If you calibrated with standards from 0-10 ppm and the highest standard gave an absorbance of 2.79, then `"max": 2.79`. This doesn't mean the instrument can't measure higher values, just that you haven't calibrated beyond this range.

**Note**: The instrument's theoretical range may be wider than the calibrated range. For example:
- Nitrate API kit theoretical range: 0-90 ppm
- A specific calibration might only cover 0-10 ppm (max absorbance ~1.5)
- The `range.max` would show 1.5, not 90

## Current Assay Configurations

### Phosphate API
- **LED**: 625 nm (red)
- **Chemistry**: Molybdenum blue (ascorbic acid reduction)
- **Typical range**: 0-30 ppm PO₄

### Nitrate API
- **LED**: 528 nm (green)
- **Chemistry**: Cadmium reduction + Griess reaction
- **Typical range**: 0-90 ppm NO₃

### Nitrite API
- **LED**: 528 nm (green)
- **Chemistry**: Direct Griess reaction (no reduction step)
- **Typical range**: 0-5 ppm NO₂

## Updating Calibrations

When you perform a new calibration:

1. Run calibration standards through the assay
2. Use the `tools/calibration/analyze_calibration_simple.py` script to calculate fit coefficients
3. Update the appropriate section in `calibrations.json`
4. Ensure the `range` values match your actual calibration data

## Multiple Calibrations

You can have multiple calibrations for the same test type with different reagents:
- "Phosphate API" - Using API test kit with 625 nm LED
- "Phosphate Red Sea Pro" - Using Red Sea kit with 880 nm IR LED

The firmware can select which calibration to use based on user preference or test type.

## References

- [Calibration Guide](../../docs/calibration/calibration-guide.md)
- [Phosphate Assay Protocol](../../docs/assays/phosphate.md)
- [Nitrate Assay Protocol](../../docs/assays/nitrate.md)
- [Calibration Analysis Tools](../../tools/calibration/README.md)
