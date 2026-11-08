---
layout: single
title: System Overview
permalink: /docs/introduction/overview/
toc: true
toc_label: "On This Page"
toc_icon: "cog"
---

# OpenReef Automated System

## Overview

The OpenReef Automated System is an open-source, Raspberry Pi-controlled platform for automated colorimetric water quality testing. The system performs automated phosphate and nitrate assays using Red Sea Pro test kits with minimal user intervention.

### Key Features

- **Fully Automated**: Automated sample handling, reagent addition, mixing, timing, and measurement
- **Dual Assay Capability**: Supports both phosphate and nitrate testing
- **Precise Control**: Automated peristaltic pumps ensure accurate reagent dosing
- **Colorimetric Detection**: Uses wavelength-specific colorimetry (880nm for phosphate, 528nm for nitrate)
- **Self-Cleaning**: Automatic RO water flush cycle between tests
- **Open Source**: Complete hardware designs, firmware, and documentation freely available

### Applications

- Aquarium water quality monitoring
- Reef tank nutrient management
- Hydroponic nutrient testing
- Environmental water testing
- Educational demonstrations

## Measurement Theory

### Colorimetric Analysis

The OpenReef system uses **colorimetric analysis** to quantify phosphate and nitrate concentrations. This method is based on the Beer-Lambert Law:

```
A = ε × c × l
```

Where:
- **A** = Absorbance (measured by colorimeter)
- **ε** = Molar extinction coefficient (specific to each compound)
- **c** = Concentration (what we're measuring)
- **l** = Path length (cuvette width)

When a sample reacts with specific reagents, colored compounds form. The intensity of the color is proportional to the analyte concentration. By measuring light absorbance at specific wavelengths, we can calculate the concentration.

### Phosphate Detection

**Chemistry**: Ascorbic acid method (APHA Standard Method 4500-P E)

Orthophosphate reacts with molybdate and antimony to form a phosphomolybdate complex. Ascorbic acid reduces this complex to form an intensely blue-colored compound.

- **Detection Wavelength**: 880nm (near-infrared)
- **Reaction Time**: 5-10 minutes (critical timing window)
- **Range**: 0-30 ppm PO₄
- **Color**: Blue (intensity increases with concentration)

### Nitrate Detection

**Chemistry**: Cadmium reduction + Griess test

Nitrate (NO₃⁻) is reduced to nitrite (NO₂⁻) using cadmium reduction. The nitrite then reacts with sulfanilamide and N-(1-naphthyl)-ethylenediamine to form a pink/purple azo dye.

- **Detection Wavelength**: 528nm (green LED)
- **Reaction Time**: Minimum 5 minutes
- **Range**: 0-90 ppm NO₃
- **Color**: Pink/purple (intensity increases with concentration)

## System Comparison

| Feature | Phosphate Assay | Nitrate Assay |
|---------|----------------|---------------|
| **Detection Method** | Ascorbic acid method | Cadmium reduction + Griess |
| **Wavelength** | 880 nm (NIR) | 528 nm (Green LED) |
| **Reagent 1 Drops** | 6 drops | 10 drops |
| **Reagent 2 Drops** | 6 drops | 10 drops |
| **Reaction Time** | 5-10 minutes* | 5+ minutes |
| **Concentration Range** | 0-30 ppm PO₄ | 0-90 ppm NO₃ |
| **Color Formed** | Blue | Pink/Purple |
| **Critical Timing** | YES - cloudy after 10 min | NO - stable after 5 min |

*The phosphate assay requires precise timing - measurements must be taken between 5-10 minutes. After 10 minutes, the solution becomes cloudy and results are inaccurate.

## System Architecture

The OpenReef system consists of:

1. **Controller**: Raspberry Pi with Flask web interface
2. **Fluidics**:
   - 4 DC motor channels (peristaltic pumps)
   - 8 solenoid valves
   - Tubing and connectors
3. **Optical System**:
   - TSL2591 light sensor
   - Cuvette holder
4. **Reagent Management**:
   - 2 reagent bottles with bubble mixing
   - Automated dispensing
5. **Sample Handling**:
   - RO water reservoir
   - Test water input
   - Waste output
   - Automatic cleaning cycle

## How It Works

The automated sequence follows these steps:

1. **System Preparation**: Flush lines with RO water, clear waste
2. **Sample Loading**: Fill cuvette with test water sample
3. **Baseline Measurement**: Zero the colorimeter with sample
4. **Reagent Addition**: Sequentially add measured amounts of Reagent #1 and #2 with stirring
5. **Incubation**: Wait for color development (timed precisely)
6. **Measurement**: Read absorbance at appropriate wavelength
7. **Calculation**: Convert absorbance to concentration using calibration curve
8. **Cleanup**: Flush system with RO water for next test

All steps are fully automated via the web interface and command sequences.
