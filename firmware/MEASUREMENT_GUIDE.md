# Open Colorimeter Measurement Guide

## Understanding Measurement Modes

### After Blanking - Expected Values

When you press the **BLANK** button, different measurement modes will show different values. This is **normal and correct**:

| Mode | Value After Blanking | Meaning |
|------|---------------------|---------|
| **Transmittance** | **1.00** | 100% light passes through (correct!) |
| **Absorbance** | **0.00** | No light absorbed (correct!) |
| **Raw Sensor** | **~9000-15000** | Actual sensor reading in counts |
| **Phosphate API** | **~3.5 ppm** | Intercept of calibration curve |
| **Nitrate API** | **~0.3 ppm** | Intercept of calibration curve |
| **Nitrite API** | **~0.1 ppm** | Intercept of calibration curve |

### Why Calibrations Don't Show Zero

Calibration curves use polynomial equations that often have a **non-zero intercept**. This is because:
- Chemical tests may have background color even at zero concentration
- The calibration is based on real-world data from API test kits
- The curve is fitted to actual measurements, not theoretical zero

**Example - Phosphate API:**
```
ppm = 3.500142 - 1.194604 × absorbance
```

When absorbance = 0 (blank), ppm = 3.5, which is normal!

---

## Measurement Modes Explained

### Basic Modes

#### Raw Sensor
- **What it shows:** Direct light sensor reading (0-65535 counts)
- **When to use:** Testing sensor, troubleshooting, maximum sensitivity
- **No blanking needed:** Shows absolute light level
- **Example reading:** 9115 counts

#### Transmittance
- **What it shows:** Percentage of light transmitted through sample (0.00-1.00 or 0%-100%)
- **Formula:** `Transmittance = Sample Reading / Blank Reading`
- **Requires blanking:** YES - must blank with reference solution
- **After blanking:** Shows 1.00 (100% transmission)
- **With sample:** Shows 0.55 (55% transmission means 45% absorbed)
- **When to use:** Comparing light transmission between samples

#### Absorbance
- **What it shows:** Amount of light absorbed by sample (0.00-3.00 typical)
- **Formula:** `Absorbance = -log10(Transmittance)`
- **Requires blanking:** YES - must blank with reference solution
- **After blanking:** Shows 0.00 (no absorption)
- **With sample:** Shows 0.26 (higher = more light absorbed)
- **When to use:** Beer-Lambert law applications, standard chemistry
- **Note:** Absorbance is additive (2x concentration = 2x absorbance)

---

## Calibrated Test Modes

### Phosphate API Test
- **What it measures:** Phosphate (PO₄³⁻) concentration in water
- **Units:** ppm (parts per million)
- **Range:** 0.0 - 2.79 ppm
- **LED Wavelength:** 625nm (red)
- **What it's for:**
  - Aquarium water testing (reef tanks, freshwater)
  - Hydroponics nutrient monitoring
  - Pond water quality
  - Wastewater analysis
- **API Test Kit Equivalent:** API Phosphate Test Kit
- **How to use:**
  1. Add API Phosphate reagent to water sample
  2. Wait for color development (5 minutes)
  3. Blank with distilled water + reagent
  4. Insert sample cuvette
  5. Read phosphate concentration in ppm

**Why measure phosphate?**
- High phosphate causes algae blooms in aquariums
- Ideal aquarium levels: < 0.05 ppm
- Plants need phosphate for growth (hydroponics)

### Nitrate API Test
- **What it measures:** Nitrate (NO₃⁻) concentration in water
- **Units:** ppm (parts per million)
- **Range:** 0.0 - 10.0 ppm
- **LED Wavelength:** 528nm (green)
- **What it's for:**
  - Aquarium nitrogen cycle monitoring
  - Freshwater and saltwater tank health
  - Fish waste accumulation tracking
  - Aquaponics system monitoring
- **API Test Kit Equivalent:** API Nitrate Test Kit
- **How to use:**
  1. Add API Nitrate reagent to water sample
  2. Shake vigorously for 1 minute
  3. Wait for color development (5 minutes)
  4. Blank with distilled water + reagent
  5. Insert sample cuvette
  6. Read nitrate concentration in ppm

**Why measure nitrate?**
- End product of beneficial bacteria breaking down fish waste
- High nitrate (>40 ppm) stresses fish
- Regular water changes reduce nitrate
- Reef tanks need very low nitrate (< 5 ppm)

### Nitrite API Test
- **What it measures:** Nitrite (NO₂⁻) concentration in water
- **Units:** ppm (parts per million)
- **Range:** 0.0 - 1.4 ppm
- **LED Wavelength:** 528nm (green)
- **What it's for:**
  - Monitoring new tank cycling (nitrogen cycle)
  - Detecting bacteria die-off events
  - Ensuring biofilter health
  - Emergency tank diagnostics
- **API Test Kit Equivalent:** API Nitrite Test Kit
- **How to use:**
  1. Add API Nitrite reagent to water sample
  2. Wait for color development (5 minutes)
  3. Blank with distilled water + reagent
  4. Insert sample cuvette
  5. Read nitrite concentration in ppm

**Why measure nitrite?**
- Toxic to fish even at low levels (>0.5 ppm dangerous)
- Indicates incomplete nitrogen cycle
- Spikes during new tank cycling
- Should be 0 ppm in established tanks

---

## The Nitrogen Cycle (Aquarium Chemistry)

Understanding why these tests matter:

```
Fish Waste → Ammonia (NH₃) → Nitrite (NO₂⁻) → Nitrate (NO₃⁻)
   [toxic]      [very toxic]    [toxic]       [less toxic]
                                               ↓
                                        Water Changes
                                               ↓
                                          Removed
```

1. **Fish produce waste** → Ammonia (very toxic)
2. **Beneficial bacteria** convert ammonia → Nitrite (toxic)
3. **Different bacteria** convert nitrite → Nitrate (less toxic)
4. **You remove nitrate** via water changes or plants

**New Tank Cycling:**
- Week 1-2: Ammonia spike (not measured by this colorimeter yet)
- Week 2-3: **Nitrite spike** ← Nitrite API Test detects this
- Week 3-4: **Nitrate appears** ← Nitrate API Test shows cycle complete
- Week 4+: Nitrite = 0, Nitrate builds up slowly

---

## General Usage Instructions

### How to Perform a Test

1. **Prepare your sample:**
   - Follow API test kit instructions for reagent mixing
   - Wait for color to develop (usually 5 minutes)
   - Transfer to clean cuvette or vial

2. **Blank the colorimeter:**
   - Select measurement mode (e.g., "Phosphate API")
   - Insert blank/reference sample (distilled water + reagent)
   - Press **BLANK** button
   - Wait for confirmation

3. **Measure your sample:**
   - Remove blank
   - Insert your test sample
   - Read the value on display
   - Note: Value updates in real-time

4. **Multiple samples:**
   - No need to re-blank between samples
   - Blank once per session (unless reagent batch changes)
   - Re-blank if ambient light changes significantly

### Tips for Accurate Readings

✅ **Do:**
- Blank before every testing session
- Use clean cuvettes (wipe with lens cloth)
- Wait for color development (follow API kit timing)
- Keep ambient light consistent
- Hold colorimeter steady while reading

❌ **Don't:**
- Touch cuvette walls (use frosted sides or rim)
- Mix different test kits/reagents
- Rush color development time
- Expose to bright sunlight during reading
- Shake sample during measurement

---

## Understanding Your Results

### Aquarium Water Quality Guidelines

#### Freshwater Aquarium
- **Nitrite:** 0 ppm (anything >0 is dangerous)
- **Nitrate:** <20 ppm (water change if >40 ppm)
- **Phosphate:** <0.5 ppm (algae control)

#### Saltwater/Reef Aquarium
- **Nitrite:** 0 ppm (very sensitive corals)
- **Nitrate:** <5 ppm (corals prefer low nitrate)
- **Phosphate:** <0.05 ppm (algae prevention)

#### New Tank Cycling
- **Week 1-2:** Nitrite rising → Don't add fish yet
- **Week 3:** Nitrite falling, Nitrate rising → Almost ready
- **Week 4+:** Nitrite = 0, Nitrate present → Tank cycled!

### Troubleshooting Readings

**Reading too high after blanking:**
- Check if you selected correct test mode
- Verify you blanked with reference (distilled water + reagent, not sample)
- Ensure cuvette is clean

**Reading negative or zero with colored sample:**
- Sample may be more transparent than blank
- Re-blank with correct reference
- Check if reagent was added

**Erratic/jumping readings:**
- Wipe cuvette clean
- Ensure sensor is not saturated (too bright)
- Check for bubbles in sample
- Steady the colorimeter

---

## Sensor Technical Details

### TSL2591 Light Sensor Specifications
- **I2C Address:** 0x29
- **Dynamic Range:** 600M:1
- **LED Support:** Multiple wavelengths via external LEDs
- **Gain Settings:** Low, Medium, High
- **Integration Time:** 100ms - 600ms

### Current Configuration
- **Gain:** Low (default)
- **Integration Time:** 500ms
- **Typical Reading:** ~9000-15000 counts (ambient/blank)
- **Overflow:** >65000 counts (too bright)

---

## Appendix: Calibration Curve Details

The colorimeter uses polynomial curve fitting based on API test kit standards.

### Phosphate API Calibration
```
Concentration (ppm) = 3.500142 - 1.194604 × Absorbance
```
- **Type:** Linear polynomial (1st order)
- **Range:** 0.0 - 2.79 ppm
- **LED:** 625nm red

### Nitrate API Calibration
```
Concentration (ppm) = 0.320 + 34.033 × Absorbance + 0.0 × Absorbance²
```
- **Type:** Linear polynomial (1st order, 2nd term = 0)
- **Range:** 0.0 - 10.0 ppm
- **LED:** 528nm green

### Nitrite API Calibration
```
Concentration (ppm) = 0.131 + 1.259 × Absorbance + 0.0 × Absorbance²
```
- **Type:** Linear polynomial (1st order, 2nd term = 0)
- **Range:** 0.0 - 1.4 ppm
- **LED:** 528nm green

**Note:** These calibrations are based on the original Open Colorimeter project's measurements using API test kits.

---

## Need Help?

- **Sensor shows "SENSOR NOT CONNECTED":** Check TSL2591 wiring (SDA→Pin 20, SCL→Pin 21, VCC→3.3V, GND→GND)
- **Calibrations missing from menu:** Ensure built-in calibrations loaded (check Serial Monitor)
- **Strange readings:** Try switching to "Raw Sensor" mode to verify sensor is working
- **Display shows zeros:** Ensure you're in correct mode and have blanked properly

For more information, see:
- `/README.md` - Hardware setup and installation
- `/README_CALIBRATIONS.md` - Calibration file format
- Serial Monitor output - Real-time debugging information
