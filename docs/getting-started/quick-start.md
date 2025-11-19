---
layout: single
title: Quick Start Guide
permalink: /docs/getting-started/quick-start/
toc: true
---

# Getting Started with OpenReef

## Quick Start Guide

### Prerequisites

Before running your first test, ensure you have:

- [ ] OpenReef system fully assembled and powered
- [ ] RO (reverse osmosis) water reservoir filled
- [ ] Reagent bottles filled (API Phosphate or Nitrate test kit)
- [ ] Waste container connected
- [ ] Colorimeter calibrated for your assay type
- [ ] PyBadge firmware loaded

### First Time Setup

1. **Power On**
   - Connect power to PyBadge
   - System will boot and display OpenReef logo
   - Main menu will appear

2. **Prime the System**
   - Select `System > Prime Pumps`
   - Follow on-screen prompts to prime water and reagent lines
   - Ensure no air bubbles in tubing

3. **Install Cuvette**
   - Insert clean cuvette into holder
   - Ensure proper alignment with light path

4. **Load Calibration**
   - Select `Settings > Load Calibration`
   - Choose phosphate or nitrate calibration file
   - Confirm calibration loaded successfully

### Running Your First Test

#### Phosphate Test

1. **Select Assay**
   - From main menu: `Run Test > Phosphate`

2. **Prepare Sample**
   - Connect test water input
   - System will prompt when ready

3. **Start Test**
   - Press `Start` button
   - System will automatically:
     - Clean cuvette with RO water
     - Load test sample
     - Zero colorimeter
     - Add reagents with stirring
     - Wait 5-10 minutes
     - Read absorbance
     - Calculate concentration

4. **View Results**
   - Results displayed on PyBadge screen
   - Data logged to SD card (if installed)

5. **Cleanup**
   - System automatically flushes with RO water
   - Remove waste when prompted

**Total Test Time**: ~15 minutes

#### Nitrate Test

1. **Select Assay**
   - From main menu: `Run Test > Nitrate`

2. **Prepare Sample**
   - Connect test water input
   - System will prompt when ready

3. **Start Test**
   - Press `Start` button
   - System will automatically:
     - Clean cuvette with RO water
     - Load test sample
     - Zero colorimeter
     - Add reagents with stirring
     - Wait 5+ minutes
     - Read absorbance
     - Calculate concentration

4. **View Results**
   - Results displayed on PyBadge screen
   - Data logged to SD card (if installed)

5. **Cleanup**
   - System automatically flushes with RO water
   - Remove waste when prompted

**Total Test Time**: ~12 minutes

## Understanding the PyBadge Menu

### Main Menu Structure

```
OpenReef Main Menu
├── Run Test
│   ├── Phosphate
│   └── Nitrate
├── Calibration
│   ├── Run Calibration
│   ├── View Curves
│   └── Load Calibration
├── System
│   ├── Prime Pumps
│   ├── Clean System
│   └── Diagnostics
└── Settings
    ├── Pump Calibration
    ├── Timing Settings
    └── About
```

### Navigation

- **D-Pad**: Navigate menu items (up/down/left/right)
- **A Button**: Select/Confirm
- **B Button**: Back/Cancel
- **Start Button**: Main menu (from anywhere)
- **Select Button**: Quick start last test

### Status Icons

| Icon | Meaning |
|------|---------|
| 💧 | Water system active |
| 🧪 | Reagent dispensing |
| ⏱️ | Timing/waiting |
| 📊 | Measuring |
| ✓ | Test complete |
| ⚠️ | Warning/Error |

## Understanding Results

### Display Format

```
Phosphate Result
━━━━━━━━━━━━━━━
Concentration: 0.25 ppm
Absorbance: 0.142
Status: ✓ Valid
Time: 14:23:45
━━━━━━━━━━━━━━━
[A] Save  [B] Discard
```

### Result Interpretation

#### Phosphate (PO₄)

| Concentration | Interpretation | Reef Tank Action |
|---------------|----------------|------------------|
| 0.00-0.03 ppm | Ultra-low | Ideal for SPS corals |
| 0.03-0.10 ppm | Low | Good for most reef tanks |
| 0.10-0.25 ppm | Moderate | Acceptable, monitor |
| 0.25-1.00 ppm | Elevated | Increase water changes |
| > 1.00 ppm | High | Use phosphate remover |

#### Nitrate (NO₃)

| Concentration | Interpretation | Reef Tank Action |
|---------------|----------------|------------------|
| 0-5 ppm | Very low | Ideal for SPS corals |
| 5-10 ppm | Low | Good for mixed reefs |
| 10-20 ppm | Moderate | Acceptable for most tanks |
| 20-40 ppm | Elevated | Increase water changes |
| > 40 ppm | High | Check bioload/feeding |

### Data Logging

If an SD card is installed, all test results are saved to:
```
/data/YYYY-MM-DD_tests.csv
```

CSV format:
```
timestamp,assay_type,concentration,absorbance,status
2025-11-14 14:23:45,phosphate,0.25,0.142,valid
```

## Troubleshooting

### Common Issues

| Issue | Possible Cause | Solution |
|-------|---------------|----------|
| No color development | Expired reagents | Replace API test kit |
| Weak/faint color | Low concentration | Normal - check calibration curve |
| Cloudy solution | Phosphate read too late | Re-run test, read at 5-10 min |
| Error: Pump timeout | Air in lines | Prime pumps again |
| Error: Absorbance out of range | Concentration too high | Dilute sample and re-test |
| Inconsistent results | Cuvette dirty | Clean cuvette with RO water |

### System Diagnostics

1. **Check Pump Function**
   - `System > Diagnostics > Test Pumps`
   - Verify both FeW and FeR pumps working
   - Check flow rate matches calibration

2. **Check Valve Operation**
   - `System > Diagnostics > Test Valves`
   - Cycle each valve (ReV, WtV, WaV)
   - Listen for click, verify flow path

3. **Check Colorimeter**
   - `System > Diagnostics > Light Test`
   - Verify LED illumination
   - Check sensor readings

4. **View Logs**
   - `System > Diagnostics > View Logs`
   - Check for error messages
   - Note any warnings

## Maintenance

### Daily (if running multiple tests)
- Empty waste container
- Refill RO water reservoir
- Check reagent levels

### Weekly
- Clean cuvette with dilute acid, rinse thoroughly
- Wipe colorimeter optical surfaces
- Check tubing for wear/cracks

### Monthly
- Replace tubing
- Clean all valves
- Run calibration verification
- Update firmware (if available)

### As Needed
- Replace reagents when expired
- Replace cuvette if scratched
- Recalibrate system

## Next Steps

- Learn about [Phosphate Assay Protocol](../assays/phosphate.md)
- Learn about [Nitrate Assay Protocol](../assays/nitrate.md)
- Review [Hardware Details](../hardware/parts-list.md)
- Understand [Calibration Process](../calibration/calibration-guide.md)
- Explore [Firmware Customization](../firmware/automation-sequence.md)
