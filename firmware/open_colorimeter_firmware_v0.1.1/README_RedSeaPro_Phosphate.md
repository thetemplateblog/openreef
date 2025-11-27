# Red Sea Phosphate Pro Test Kit - Colorimeter Setup Guide

## Overview

The Red Sea Phosphate Pro test kit is a high-precision colorimetric reagent optimized for ultra-low phosphate measurements in reef aquariums. This guide explains how to configure the open colorimeter for use with this reagent.

## Specifications

### Red Sea Pro Test Kit
- **Method**: Molybdenum blue (ascorbic acid reduction)
- **Accuracy**: ±0.02 ppm (some sources: 0.014 ppm)
- **Precision**: 0.01 ppm resolution
- **Range**: 0-5 ppm (optimal for 0-1 ppm)
- **Tests per Kit**: 100 tests
- **Color Development**: Light blue (molybdenum blue complex)

### Chemistry
1. Phosphate + molybdate → phosphomolybdate complex
2. Ascorbic acid reduces complex → molybdenum blue (blue color)
3. Color intensity proportional to phosphate concentration

## Hardware Requirements

### LED Configuration
**Optimal**: 880 nm infrared LED
- Maximum absorption of molybdenum blue complex
- Industry standard for phosphate analysis
- 3x better sensitivity than visible red LEDs

**Alternative Wavelengths**:
- 710-720 nm: Excellent (95% sensitivity)
- 625-630 nm: Acceptable (30-40% sensitivity)
- 520 nm: Poor (not recommended)

### Sensor Configuration
**TSL2591 Light Sensor**:
- Use **Channel 1** (IR photodiode) for 880 nm LED
- IR channel has good response at 880 nm (within 650-950 nm range)
- Peak sensitivity: 800-850 nm

## Software Configuration

### 1. Modify `src/light_sensor.py`

Change the channel selection for IR LED:

```python
def __init__(self):
    # Set up light sensor
    i2c = busio.I2C(board.SCL, board.SDA)
    try:
        self._device = adafruit_tsl2591.TSL2591(i2c)
        self._mock_mode = False
    except (ValueError, OSError) as error:
        # Sensor not found, run in mock mode
        self._device = None
        self._mock_mode = True
        print(f"Running in mock mode - sensor not detected: {error}")
    self.gain = self.DEFAULT_GAIN
    self.integration_time = self.DEFAULT_INTEGRATION_TIME
    self.channel = 1  # Use IR channel (1) for 880nm LED, use 0 for visible LEDs
```

### 2. Update `calibrations.json`

Add or modify the phosphate entry:

```json
{
  "Phosphate Red Sea Pro": {
    "units": "ppm",
    "led": "880",
    "fit_type": "polynomial",
    "fit_coef": [
      0.0,
      0.0
    ],
    "range": {
      "min": 0.0,
      "max": 1.0
    }
  }
}
```

**Note**: The `fit_coef` values shown are placeholders. You must perform calibration to determine actual coefficients.

## Calibration Procedure

### Materials Needed
- Red Sea Phosphate Pro test kit
- Phosphate standards: 0, 0.25, 0.5, 0.75, 1.0 ppm (mg/L)
- Distilled/RO water for blanking
- Standard solution (KH₂PO₄) or certified reference materials

### Preparing Reference Standards

#### Materials Required
- **Potassium phosphate monobasic** (KH₂PO₄, anhydrous, ACS grade)
- **Distilled or RO/DI water** (low phosphate)
- **Volumetric flasks**: 1000 mL, 100 mL, 50 mL
- **Pipettes**: 1 mL, 5 mL, 10 mL (calibrated)
- **Analytical balance** (0.0001 g precision recommended)
- **Storage bottles** (amber glass, HDPE)

#### Stock Solution (100 ppm PO₄³⁻)

**Calculation**:
- Molecular weight KH₂PO₄ = 136.09 g/mol
- Molecular weight PO₄³⁻ = 94.97 g/mol
- Conversion factor: 136.09 / 94.97 = 1.433

**Preparation**:
1. Weigh **0.1433 g** of KH₂PO₄ (anhydrous) on analytical balance
   - For 100.0 ppm PO₄: exactly 0.14330 g in 1000 mL
2. Transfer to clean 1000 mL volumetric flask
3. Add ~500 mL distilled water, swirl to dissolve completely
4. Fill to 1000 mL mark with distilled water
5. Mix thoroughly by inverting 20 times
6. Transfer to amber glass bottle
7. Label: "100 ppm PO₄ Stock, Date: [date], Expires: [+6 months]"
8. Store refrigerated at 4°C

**Stability**: 6 months refrigerated, 3 months at room temperature

#### Intermediate Solution (10 ppm PO₄³⁻) - Optional

For easier dilutions:
1. Pipette **10.00 mL** of 100 ppm stock
2. Transfer to 100 mL volumetric flask
3. Fill to mark with distilled water
4. Mix thoroughly
5. Store refrigerated, stable 1 month

#### Working Standards (0-1 ppm range)

**Method 1: From 100 ppm Stock** (more precise for high concentrations)

| Target Conc. | Stock Volume | Total Volume | Preparation |
|--------------|--------------|--------------|-------------|
| 0.00 ppm     | 0.0 mL       | 100 mL       | Distilled water only |
| 0.10 ppm     | 0.10 mL      | 100 mL       | Use micropipette |
| 0.25 ppm     | 0.25 mL      | 100 mL       | 250 μL stock + water to 100 mL |
| 0.50 ppm     | 0.50 mL      | 100 mL       | 500 μL stock + water to 100 mL |
| 0.75 ppm     | 0.75 mL      | 100 mL       | 750 μL stock + water to 100 mL |
| 1.00 ppm     | 1.00 mL      | 100 mL       | 1.0 mL stock + water to 100 mL |

**Method 2: From 10 ppm Intermediate** (easier, recommended)

| Target Conc. | Intermediate Vol. | Total Volume | Preparation |
|--------------|-------------------|--------------|-------------|
| 0.00 ppm     | 0.0 mL           | 100 mL       | Distilled water only |
| 0.10 ppm     | 1.0 mL           | 100 mL       | 1.0 mL intermediate + water to 100 mL |
| 0.25 ppm     | 2.5 mL           | 100 mL       | 2.5 mL intermediate + water to 100 mL |
| 0.50 ppm     | 5.0 mL           | 100 mL       | 5.0 mL intermediate + water to 100 mL |
| 0.75 ppm     | 7.5 mL           | 100 mL       | 7.5 mL intermediate + water to 100 mL |
| 1.00 ppm     | 10.0 mL          | 100 mL       | 10.0 mL intermediate + water to 100 mL |

#### Standard Preparation Protocol

**For each standard**:
1. Rinse volumetric flask 3x with distilled water
2. Pipette required volume of stock/intermediate solution
3. Add distilled water to ~75% of final volume
4. Swirl to mix
5. Fill to final volume mark
6. Cap and invert 20 times to mix thoroughly
7. Label with concentration and date
8. Use within 24 hours for best accuracy

**Storage**:
- Working standards: Use fresh daily (prepare same day)
- If storing: Refrigerate in sealed containers, use within 1 week
- Warm to room temperature before use

#### Quality Control Standards

**Method Blank**:
- Distilled/RO water processed with reagents
- Should read 0.00 ± 0.01 ppm
- Run with every batch

**Continuing Calibration Verification (CCV)**:
- Mid-range standard (e.g., 0.50 ppm)
- Run every 10 samples
- Should be within ±10% of expected value

**Duplicate Samples**:
- Run 1 duplicate per 10 samples
- RPD (Relative Percent Difference) should be <10%
- Formula: RPD = |A-B| / ((A+B)/2) × 100%

#### Alternative: Commercial Reference Materials

If preparing standards is impractical:

**Option 1: Hanna Phosphate Standards**
- HI774-11: 0.00 ppm (blank)
- HI774-12: 0.25 ppm
- HI774-13: 0.50 ppm
- Pre-made, certified, ready to use

**Option 2: NIST Traceable Standards**
- Purchase from scientific supply companies
- More expensive but certified accuracy
- Typical concentrations: 0.1, 0.5, 1.0, 5.0 ppm PO₄

**Option 3: Aquarium Test Kit Standards**
- Some manufacturers sell calibration solutions
- Check certification and traceability
- May be less precise than lab-grade

#### Verification of Stock Solution

**Method 1: ICP-MS or ICP-OES Analysis**
- Send sample to commercial lab
- Most accurate verification
- Cost: ~$20-50 per sample

**Method 2: Comparison with Certified Reference**
- Purchase NIST-traceable 100 ppm PO₄ standard
- Run both through colorimeter
- Should agree within 5%

**Method 3: Gravimetric Check**
- Re-weigh KH₂PO₄ batch
- Verify final volume with calibrated flask
- Calculate theoretical vs. actual concentration

### Calibration Steps

1. **Blank the Colorimeter**
   - Fill sample vial with distilled water
   - Blank the sensor (press Blank button)

2. **Measure Each Standard** (in triplicate minimum)
   - Add Red Sea Pro reagents per kit instructions
   - Wait for color development (timing per kit)
   - Record absorbance value from colorimeter
   - Repeat 3-6 times per concentration

3. **Record Data**
   ```
   Concentration (ppm) | Absorbance (replicate 1, 2, 3...)
   0.00                | 0.000, 0.000, 0.000
   0.25                | 0.150, 0.152, 0.151
   0.50                | 0.301, 0.298, 0.302
   0.75                | 0.450, 0.448, 0.451
   1.00                | 0.598, 0.601, 0.599
   ```

4. **Calculate Fit Coefficients**

   Use the provided calibration script:
   ```bash
   python3 analyze_calibration_simple.py
   ```

   Enter your data when prompted. The script will output:
   - Linear fit coefficients (slope and intercept)
   - Absorbance range (min/max)
   - JSON-formatted calibration entry

5. **Update calibrations.json**

   Replace the placeholder `fit_coef` values with calculated coefficients:
   ```json
   "fit_coef": [
     3.521845,    // slope (example)
     -0.012456    // intercept (example)
   ],
   "range": {
     "min": 0.00,
     "max": 0.60  // max absorbance from calibration
   }
   ```

### Quality Checks

**Good Calibration Indicators**:
- R² > 0.995 (linearity)
- Replicate RSD < 5% (precision)
- Intercept close to 0 (±0.1)
- Residuals randomly distributed

**Poor Calibration Indicators**:
- R² < 0.99
- Large replicate variation (RSD > 10%)
- Non-linear curve
- Systematic drift

## Usage Instructions

### Running a Sample Test

1. **Blank the colorimeter** with distilled water
2. **Prepare sample** according to Red Sea Pro instructions:
   - Add sample to test vial
   - Add Reagent A (molybdate/acid)
   - Add Reagent B (ascorbic acid reducer)
   - Mix and wait for color development
3. **Read measurement** in colorimeter
4. Device displays concentration in ppm

### Best Practices

- **Always blank** before each measurement session
- **Temperature**: Keep reagents and samples at consistent temperature (20-25°C)
- **Timing**: Follow Red Sea Pro reaction time exactly
- **Sample clarity**: Filter turbid samples before testing
- **Storage**: Store reagents in cool, dark place
- **Expiration**: Check reagent expiration dates

## Troubleshooting

### Problem: Readings are negative or zero for known phosphate samples
**Cause**: Calibration intercept too high, or sensor not detecting light
**Solution**:
- Re-calibrate with fresh standards
- Check LED is working (880 nm IR LED may not be visible to eye)
- Verify channel = 1 in light_sensor.py

### Problem: Poor repeatability (>10% RSD)
**Cause**: Inconsistent reagent mixing, temperature variation, or timing
**Solution**:
- Mix samples thoroughly and consistently
- Control sample temperature
- Use timer for consistent reaction time
- Check reagent expiration

### Problem: Non-linear calibration curve
**Cause**: Reagent concentration issues, interfering substances, or LED saturation
**Solution**:
- Prepare fresh reagent solutions
- Filter samples to remove turbidity
- Reduce integration time if readings saturate
- Check for salt/organics interference

### Problem: Calibration drift over time
**Cause**: Reagent degradation, LED output drift, or sensor aging
**Solution**:
- Re-calibrate monthly or when drift detected
- Store reagents properly (cool, dark)
- Check LED stability with reference standard

### Problem: Readings don't match Red Sea Pro comparator
**Cause**: Different color development time or calibration differences
**Solution**:
- Ensure exact same timing as manual method
- Calibrate against certified reference standards
- Consider differences in optical path length

## Expected Performance

With proper calibration and technique:

- **Detection Limit**: ~0.02 ppm (Red Sea Pro specification)
- **Quantitation Limit**: ~0.05 ppm
- **Linear Range**: 0-1.0 ppm (can extend to 5 ppm)
- **Precision**: 2-5% RSD
- **Accuracy**: ±0.02-0.05 ppm
- **Analysis Time**: 3-5 minutes per sample

## Comparison: 880nm vs Other Wavelengths

| LED Wavelength | Sensitivity | Linearity | Recommended |
|----------------|-------------|-----------|-------------|
| 880 nm (IR)    | 100% (optimal) | Excellent | ⭐⭐⭐ Yes |
| 710 nm (red)   | ~95%        | Excellent | ⭐⭐⭐ Yes |
| 625 nm (red)   | ~30-40%     | Good      | ⭐⭐ Acceptable |
| 520 nm (green) | ~5-10%      | Poor      | ❌ Not recommended |

## Technical References

### Molybdenum Blue Method
- Maximum absorption: 880 nm (primary), 710-720 nm (secondary)
- Absorption range: 650-900 nm
- Molar absorptivity: High (ε > 10,000 L·mol⁻¹·cm⁻¹)
- Color stability: 10-60 minutes (method dependent)

### Interferences
- **Positive**: Silicate (if present > 10 ppm), arsenate
- **Negative**: High salinity (>40 ppt), organic matter
- **Minimize**: Use blank correction, filter samples

### Chemical Reactions

**Step 1** - Complex formation:
```
PO₄³⁻ + 12 MoO₄²⁻ + 24 H⁺ → H₃[P(Mo₁₂O₄₀)] + 12 H₂O
```

**Step 2** - Reduction to molybdenum blue:
```
H₃[P(Mo₁₂O₄₀)] + Ascorbic Acid → Mo-blue complex (reduced)
```

## Maintenance Schedule

### Daily (when in use)
- Blank calibration before use
- Check zero/reference reading

### Weekly
- Clean sample vials
- Check LED operation
- Verify readings with control sample

### Monthly
- Full re-calibration
- Check reagent expiration
- Clean sensor window

### Quarterly
- Verify with certified reference materials
- Document calibration history
- Check for drift trends

## Safety Notes

- **Sulfuric acid**: Red Sea Pro Reagent A contains 25% H₂SO₄ - handle carefully
- **Proper disposal**: Dispose of reagent waste per local regulations
- **Skin contact**: Rinse immediately with water
- **Ventilation**: Use in well-ventilated area

## File Locations

- Calibration data: `calibrations.json`
- Configuration: `configuration.json`
- Sensor code: `src/light_sensor.py`
- Main application: `src/colorimeter.py`
- Calibration script: `analyze_calibration_simple.py`

## Additional Resources

- Red Sea Phosphate Pro Manual: https://g1.redseafish.com/support/manuals/products/phosphate-pro/
- TSL2591 Datasheet: https://cdn-shop.adafruit.com/datasheets/TSL25911_Datasheet_EN_v1.pdf
- Molybdenum Blue Method: EPA Method 365.3

## Version History

- v1.0 (2025-01-26): Initial documentation for Red Sea Pro with 880 nm LED configuration

---

**For questions or issues, refer to the main colorimeter documentation or Red Sea technical support.**
