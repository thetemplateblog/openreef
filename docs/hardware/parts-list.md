---
layout: single
title: Hardware Parts List
permalink: /docs/hardware/parts-list/
toc: true
---

# Hardware Components & Parts List

## Complete Bill of Materials (BOM)

### Core Components

| Component | Quantity | Specification | Notes |
|-----------|----------|---------------|-------|
| **AdaFruit PyBadge** | 1 | ATSAMD51J19, 120MHz ARM Cortex-M4, 1.8" TFT display | Main controller |
| **Colorimeter Sensor** | 1 | RGB or multi-wavelength (528nm, 625nm) | AS7341 or TCS34725 recommended |
| **Cuvette** | 1+ | Standard 1cm path length, glass or plastic | 3.5 mL minimum volume |
| **Peristaltic Pump (Water)** | 1 | 12V DC, flow rate 50-100 mL/min | FeW Pump - water handling |
| **Peristaltic Pump (Reagent)** | 1 | 12V DC, flow rate 10-50 mL/min | FeR Pump - reagent dispensing |
| **Solenoid Valve** | 3 | 12V DC, 2-way or 3-way | ReV, WtV, WaV |
| **Air Pump** | 1 | 12V DC, small aquarium pump (optional) | Alternative to pump bubbling |
| **Power Supply** | 1 | 12V DC, 2A minimum | Powers pumps and valves |

### Fluidic Components

| Component | Quantity | Specification | Notes |
|-----------|----------|---------------|-------|
| **Silicone Tubing (Large)** | 3m | 6mm OD, 4mm ID | Water lines |
| **Silicone Tubing (Small)** | 2m | 3mm OD, 1.5mm ID | Reagent lines |
| **Tube Connectors** | 10 | Barbed, various sizes | Y-connectors, T-connectors |
| **Check Valves** | 3 | One-way, 4mm ID | Prevent backflow |
| **Bottle Caps (Custom)** | 4 | With tube fittings | RO, test water, 2 reagents |
| **Waste Container** | 1 | 500 mL or larger | Collect waste |

### Reagents & Consumables

| Component | Quantity | Specification | Notes |
|-----------|----------|---------------|-------|
| **API Phosphate Test Kit** | 1 | 2-bottle system | Reagents for ~150 tests |
| **API Nitrate Test Kit** | 1 | 2-bottle system | Reagents for ~90 tests |
| **Phosphate Standard** | 1 | 1,000 ppm PO₄ | For calibration |
| **Nitrate Standard** | 1 | 4,430 ppm NO₃ | For calibration |
| **RO/Distilled Water** | - | Continuous supply | Blank & cleaning |

### Electronics & Control

| Component | Quantity | Specification | Notes |
|-----------|----------|---------------|-------|
| **Relay Module** | 1 | 4-channel, 12V/10A | Control pumps & valves |
| **Breadboard/PCB** | 1 | For connections | Or custom PCB |
| **Jumper Wires** | - | M-M, M-F, F-F | Connections |
| **Power Distribution** | 1 | Terminal block | 12V distribution |

### Enclosure & Mechanical

| Component | Quantity | Specification | Notes |
|-----------|----------|---------------|-------|
| **Console Enclosure** | 1 | Custom 3D printed or acrylic | Houses all components |
| **Cuvette Holder** | 1 | 3D printed, light-tight | Precise alignment |
| **Mounting Brackets** | - | Various | Pumps, valves, bottles |

## Detailed Component Specifications

### 1. AdaFruit PyBadge

**Specifications:**
- Microcontroller: ATSAMD51J19 ARM Cortex-M4 @ 120 MHz
- RAM: 192 KB
- Flash: 512 KB
- Display: 1.8" color TFT (160x128 pixels)
- I/O: 17 GPIO pins, I2C, SPI, UART
- Power: USB-C or JST battery connector
- Programming: CircuitPython or Arduino

**Why PyBadge:**
- Built-in color display for user interface
- Sufficient processing power for control & calculations
- Native CircuitPython support (easy programming)
- Plenty of GPIO for pumps, valves, sensors
- Low power consumption
- Compact form factor

**Purchase:** https://www.adafruit.com/product/4277

### 2. Colorimeter Sensor Options

#### Option A: AS7341 (Recommended)

**Specifications:**
- 11-channel spectral sensor
- Wavelength range: 350-1000 nm
- Channels: 8 visible + NIR + clear + flicker
- Interface: I2C
- Supply: 3.3V

**Channels Relevant to Assays:**
- F4 (528 nm) - Nitrate detection
- F7 (630 nm) - Close to phosphate 625 nm

**Advantages:**
- Multiple discrete wavelengths
- High sensitivity
- Direct I2C interface to PyBadge
- Single sensor for both assays

**Purchase:** Adafruit AS7341 Breakout - https://www.adafruit.com/product/4698

#### Option B: TCS34725

**Specifications:**
- RGB + Clear channels
- Interface: I2C
- Supply: 3.3V
- IR blocking filter

**Advantages:**
- Simple, well-documented
- Lower cost than AS7341
- Good for single-wavelength work

**Disadvantages:**
- Broad RGB channels (less specific than AS7341)
- May require external LED filters

**Purchase:** Adafruit TCS34725 - https://www.adafruit.com/product/1334

### 3. LED Light Sources

For optimal colorimetry, use discrete LEDs matching assay wavelengths:

| Assay | Wavelength | LED Part Number | Notes |
|-------|------------|-----------------|-------|
| Phosphate | 625 nm | Red LED | High brightness |
| Nitrate | 528 nm | Green LED | High brightness |

**Recommended:** High-brightness 5mm LEDs
- Forward voltage: 2-3V
- Current: 20 mA
- Viewing angle: 15-30° (narrow for focused beam)

### 4. Peristaltic Pumps

#### Water Pump (FeW)

**Specifications:**
- Voltage: 12V DC
- Flow rate: 50-100 mL/min
- Tubing size: 4-6 mm ID
- Reversible motor
- Self-priming

**Example:** Kamoer KCS mini peristaltic pump

#### Reagent Pump (FeR)

**Specifications:**
- Voltage: 12V DC
- Flow rate: 10-50 mL/min (lower than water pump)
- Tubing size: 2-3 mm ID
- Reversible motor
- Precise dosing

**Calibration Required:**
- Measure mL/second for each pump
- Convert "drops" to volume (1 drop ≈ 0.05 mL)
- Program pump run time for exact volumes

### 5. Solenoid Valves

**Specifications (all 3 valves):**
- Voltage: 12V DC
- Type: 2-way normally closed OR 3-way
- Port size: 4-6 mm barbed
- Material: PP or PTFE (chemical compatible)
- Response time: < 50 ms

**Valve Assignments:**

| Valve | Name | Function | Positions |
|-------|------|----------|-----------|
| ReV | Reagent Valve | Switches between Reagent #1 & #2 | 3-way |
| WtV | Water Test Valve | Switches between RO & Test water | 3-way |
| WaV | Waste Valve | Switches between Waste & Test (cuvette) | 3-way |

**3-Way Valve Configuration:**
- Common port: to pump
- Port A: Source 1 (e.g., RO water)
- Port B: Source 2 (e.g., Test water)

### 6. Mixing Method

#### Air Bubbling via Pump Reversal

**Method:**
- **Cuvette mixing**: Reverse FeW pump briefly to create air bubbles
- **Reagent bottle mixing**: Reverse FeR pump to agitate reagents
- No mechanical stirrers required

**Advantages:**
- Simplified hardware (no stirrer motors or stir bars)
- Fewer moving parts
- Effective mixing for both cuvette and reagent bottles
- Critical for Reagent #2 (nitrate): bubbling keeps cadmium suspension mixed

**Alternative:** Air pump (PID 4699) available for dedicated bubbling system if needed

**Technique:**
1. Reverse pump direction for 2-5 seconds
2. Creates air bubbles that rise through liquid
3. Provides thorough mixing without mechanical parts

### 7. Relay Module

**Specifications:**
- Channels: 4 (minimum 3 needed for valves)
- Coil voltage: 5V (matches PyBadge GPIO)
- Contact rating: 10A @ 12V DC
- Isolation: Optocoupled
- Interface: Active high or active low

**Connections:**
- Channel 1: ReV (Reagent Valve)
- Channel 2: WtV (Water Test Valve)
- Channel 3: WaV (Waste Valve)
- Channel 4: Spare (air pump or additional valve)

**Example:** SainSmart 4-channel relay module

### 8. Motor Driver (H-Bridge)

**Specifications:**
- Type: Dual H-bridge (for reversible pump control)
- Channels: 2 (for 2 pumps)
- Voltage: Up to 12V
- Current: 1A per channel (minimum)

**Recommended ICs:**
- L293D: Simple, dual H-bridge
- TB6612FNG: Higher efficiency, better thermal performance

**Purpose:**
- Enables bidirectional pump control for bubble mixing
- Forward: Normal pumping
- Reverse: Creates air bubbles for mixing

**Connections:**
- Motor A: FeW Pump (water) - forward/reverse for cuvette bubbling
- Motor B: FeR Pump (reagent) - forward/reverse for reagent bottle bubbling

### 9. Power Supply

**Specifications:**
- Output: 12V DC
- Current: 2A minimum (3A recommended)
- Connector: Barrel jack (5.5mm x 2.1mm)
- Regulation: < 5% ripple

**Power Budget:**
| Component | Current | Notes |
|-----------|---------|-------|
| Peristaltic pumps (2x) | 0.5A each | 1A total |
| Solenoid valves (3x) | 0.2A each | 0.6A total (not simultaneous) |
| PyBadge | 0.1A | Via USB or regulator |
| Air pump (optional) | 0.3A | If using instead of pump bubbling |
| Margin | 0.4A | Safety factor |
| **Total** | **~2A** | Recommend 2-3A supply |

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        PyBadge Controller                    │
│  ┌────────────┐  ┌──────────┐  ┌─────────┐  ┌────────────┐ │
│  │   Display  │  │  I2C to  │  │  GPIO   │  │   Timer    │ │
│  │   (TFT)    │  │  AS7341  │  │ Control │  │  Control   │ │
│  └────────────┘  └──────────┘  └─────────┘  └────────────┘ │
└──────────┬──────────────┬───────────┬────────────┬──────────┘
           │              │           │            │
     User Interface   Colorimeter  Relays    Motor Driver
                          │           │            │
                     ┌────▼────┐  ┌───▼─────┐  ┌──▼───────┐
                     │ AS7341  │  │  4-Ch   │  │ L293D or │
                     │ Sensor  │  │ Relay   │  │ TB6612   │
                     │+ LED    │  │ Module  │  │          │
                     └────┬────┘  └───┬─────┘  └──┬───────┘
                          │           │            │
                     ┌────▼────┐  ┌───▼──────┐ ┌──▼──────┐
                     │ Cuvette │  │ Valves:  │ │ Pumps:  │
                     │         │  │ ReV,WtV, │ │ FeW,FeR │
                     │         │  │ WaV      │ │         │
                     └─────────┘  └──────────┘ └─────────┘
```

## Fluidic System Diagram

```
                    Fluidic Flow Paths

    RO Water ───┐                      ┌─── Reagent #1
                │                      │
    Test Water ─┤─► WtV ──┐            ├─► ReV ──┐
                │    (3-way)           │    (3-way)
                          │            │          │
                          ▼            ▼          │
                       FeW Pump    FeR Pump      │
                          │            │          │
                          ▼            ▼          │
                    ┌─────────────────────┐      │
                    │      Cuvette        │◄─────┘
                    │  (bubble mixing)    │
                    └──────────┬──────────┘
                               │
                        WaV ───┤─► Waste Container
                      (3-way)  │
                               └─► Back to cuvette (recirculate)

Legend:
  WtV = Water Test Valve (selects RO or Test water)
  ReV = Reagent Valve (selects Reagent #1 or #2)
  WaV = Waste Valve (directs to waste or recirculates)
  FeW = Fill/Empty Water Pump (bidirectional)
  FeR = Fill/Empty Reagent Pump (bidirectional)
```

## Wiring Diagram

### PyBadge GPIO Assignments

| PyBadge Pin | Connection | Purpose |
|-------------|------------|---------|
| SDA | AS7341 SDA | I2C data |
| SCL | AS7341 SCL | I2C clock |
| D0 | Relay Ch1 | ReV valve control |
| D1 | Relay Ch2 | WtV valve control |
| D2 | Relay Ch3 | WaV valve control |
| D3 | Motor Driver IN1 | FeW pump forward |
| D4 | Motor Driver IN2 | FeW pump reverse (bubbling) |
| D5 | Motor Driver IN3 | FeR pump forward |
| D6 | Motor Driver IN4 | FeR pump reverse (bubbling) |
| D7 | Relay Ch4 (optional) | Air pump control |
| 3.3V | Sensor power | AS7341 |
| GND | Common ground | All components |

### Power Distribution

```
12V Power Supply
    │
    ├─► Relay Module (12V coil)
    │       └─► Solenoid Valves (3x)
    │
    ├─► Motor Driver (12V motor supply)
    │       └─► Peristaltic Pumps (2x) - bidirectional for bubbling
    │
    ├─► Air Pump (optional, via relay)
    │
    └─► 5V Regulator ──► PyBadge (if not USB powered)
            └─► Relay Module (5V logic)
            └─► AS7341 (3.3V via PyBadge)
```

## Enclosure Design

### Console Dimensions (Suggested)

- Width: 350 mm
- Depth: 250 mm
- Height: 300 mm

### Component Layout

```
┌─────────────────────────────────────┐  ◄─ Top View
│                                     │
│  [PyBadge Display]        [Cuvette] │
│                            Holder   │
│  ┌──────┐  ┌──────┐               │
│  │ RO   │  │ Test │                │
│  │Water │  │Water │                │
│  └──────┘  └──────┘                │
│                                     │
│  ┌──────┐  ┌──────┐     [Pumps]   │
│  │Reag 1│  │Reag 2│     [Valves]  │
│  └──────┘  └──────┘                │
│                                     │
│            [Waste]                  │
│                                     │
└─────────────────────────────────────┘

Side panels: Electronics, power supply, motor driver
```

### 3D Printable Components

1. **Cuvette Holder**
   - Light-tight chamber
   - Precise positioning (±0.5mm)
   - LED mount opposite sensor
   - Tube access for bubble mixing

2. **Bottle Caps** (4 needed)
   - Threaded to fit reagent/water bottles
   - 2-3 tube pass-throughs
   - Air vent
   - Seal gasket

3. **Pump Mounts**
   - Secure peristaltic pump motors
   - Aligned with tubing

4. **Valve Bracket**
   - Mount 3 solenoid valves
   - Organized tubing routing

## Assembly Notes

### Critical Alignments

1. **Colorimeter Optical Path**
   - LED, cuvette, sensor must be perfectly aligned
   - No ambient light leakage
   - Consistent cuvette positioning

2. **Tubing Connections**
   - No air bubbles in lines
   - Check valves oriented correctly (flow direction)
   - Secure all barbed connections

3. **Electrical Isolation**
   - Keep 12V circuits separate from 3.3V/5V logic
   - Use optocoupled relays
   - Common ground, but isolated power rails

### Testing Before First Use

1. Test each valve individually (click sound, flow verification)
2. Calibrate pump flow rates (mL/second)
3. Verify colorimeter readings (stable baseline)
4. Check for leaks in fluidic system
5. Test bubble mixing (visual confirmation - pump reversal creates bubbles)

## Optional Enhancements

### Temperature Control

- Add DS18B20 temperature sensor
- Monitor reaction temperature
- Heater/cooler for temperature control (20-25°C optimal)

### Data Logging

- Add SD card to PyBadge
- Log all test results
- Store calibration data

### WiFi Connectivity

- Add ESP32 or AirLift FeatherWing
- Upload results to cloud
- Remote monitoring

### Automatic Calibration

- Store multiple standard solutions
- Automated calibration runs
- QC checks before each test

## Purchasing Guide

### Recommended Suppliers

- **Adafruit**: PyBadge, sensors, electronics
- **Amazon**: Pumps, valves, tubing
- **DigiKey/Mouser**: Electronic components
- **McMaster-Carr**: Mechanical parts, tubing
- **API**: Test kit reagents (pet stores or online)

### Estimated Total Cost

| Category | Cost (USD) |
|----------|------------|
| PyBadge + Sensor | $50-80 |
| Pumps (2x) | $40-80 |
| Valves (3x) | $30-60 |
| Electronics | $30-50 |
| Fluidics | $20-40 |
| Enclosure/3D printing | $30-60 |
| Reagents & consumables | $40-60 |
| **Total** | **$240-430** |

## Next Steps

- Review [Firmware & Automation Sequence](../firmware/automation-sequence.md)
- See [Calibration Guide](../calibration/calibration-guide.md)
- Check [Assembly Instructions](assembly.md) (coming soon)
