---
layout: single
title: Adafruit Components
permalink: /docs/hardware/adafruit-parts-bom/
toc: true
---

# Adafruit Specific Parts - Bill of Materials

## Confirmed Components

This is the confirmed bill of materials using specific Adafruit products for the OpenReef automated system.

### Core Controller & Display

| Component | Adafruit PID | Quantity | Unit Price | Total | Link |
|-----------|--------------|----------|------------|-------|------|
| **AdaFruit PyBadge** | TBD | 1 | ~$40 | $40.00 | [Adafruit PyBadge](https://www.adafruit.com/product/4277) |

### Motor & Pump Control

| Component | Adafruit PID | Quantity | Unit Price | Total | Link |
|-----------|--------------|----------|------------|-------|------|
| **DC Motor + Stepper FeatherWing** | 3243 | 1 | $21.50 | $21.50 | [Product Link](https://www.adafruit.com/product/3243) |
| **8-Channel PWM or Servo FeatherWing** | 2928 | 1 | $9.95 | $9.95 | [Product Link](https://www.adafruit.com/product/2928) |

**Notes:**
- DC Motor FeatherWing controls the two peristaltic pumps (FeW and FeR)
- Can drive 4 DC motors or 2 stepper motors
- TB6612 MOSFET driver with 1.2A per channel
- Suitable for 4.5-13.5V DC motors

### Valve Control

| Component | Adafruit PID | Quantity | Unit Price | Total | Link |
|-----------|--------------|----------|------------|-------|------|
| **I2C to 8 Channel Solenoid Driver** | 6318 | 1 | ~$15 | $15.00 | [Product Link](https://www.adafruit.com/product/6318) |
| **6V Air Valve with 2-pin JST** | 4663 | 3 | $2.95 | $8.85 | [Product Link](https://www.adafruit.com/product/4663) |

**Valve Assignments:**
1. **ReV** (Reagent Valve): Switches between Reagent #1 and Reagent #2
2. **WtV** (Water Test Valve): Switches between RO water and Test water
3. **WaV** (Waste Valve): Switches between Waste and Test (cuvette)

**Notes:**
- Solenoid driver uses I2C (STEMMA QT / Qwiic compatible)
- 8 channels (need 3, have 5 spare for future expansion)
- Each valve operates at 6V DC
- 2-pin JST connectors for easy attachment

### Air Pump & Fluidics

| Component | Adafruit PID | Quantity | Unit Price | Total | Link |
|-----------|--------------|----------|------------|-------|------|
| **Air Pump and Vacuum DC Motor** | 4699 | 1 | $7.95 | $7.95 | [Product Link](https://www.adafruit.com/product/4699) |
| **Silicone Tubing (3mm ID)** | 4661 | 2 | $2.50 | $5.00 | [Product Link](https://www.adafruit.com/product/4661) |

**Air Pump Specs:**
- Model: ZR370-02PM
- Voltage: 4.5V DC
- Flow rate: 2.5 LPM (liters per minute)
- Use: Optional line clearing with air pulses

**Tubing:**
- Inner diameter: 3mm
- 1 meter long per unit (2 meters total)
- Compatible with air valves and pump
- Silicone material (chemical resistant)

### Colorimeter Sensor (Recommended)

| Component | Adafruit PID | Quantity | Unit Price | Total | Link |
|-----------|--------------|----------|------------|-------|------|
| **AS7341 11-Channel Spectral Sensor** | 4698 | 1 | $14.95 | $14.95 | [Product Link](https://www.adafruit.com/product/4698) |

**Specifications:**
- 11-channel spectral color sensor
- Wavelengths: 350-1000nm
- Channels include:
  - **F4 (528nm)**: Perfect for nitrate detection (green)
  - **F7 (630nm)**: Close to phosphate 625nm (red)
- I2C interface (STEMMA QT)
- 3.3V operation

### LEDs for Colorimetry

| Component | Specification | Quantity | Unit Price | Total | Source |
|-----------|---------------|----------|------------|-------|--------|
| **Green LED (528nm)** | High brightness, 5mm | 1 | $0.50 | $0.50 | Adafruit/DigiKey |
| **Red LED (625nm)** | High brightness, 5mm | 1 | $0.50 | $0.50 | Adafruit/DigiKey |

**LED Requirements:**
- Narrow viewing angle (15-30°) for focused beam
- High brightness (1000+ mcd)
- Wavelength tolerance: ±10nm

### Additional Components Needed

| Component | Quantity | Notes | Source |
|-----------|----------|-------|--------|
| **Peristaltic Pumps (DC Motor)** | 2 | 6-12V DC, reversible | Amazon/AliExpress |
| **Cuvettes (1cm path)** | 2+ | Glass or plastic, 3.5mL | Lab supply |
| **Power Supply (12V, 2-3A)** | 1 | Barrel jack | Adafruit #352 |
| **Jumper Wires** | Set | M-M, M-F, F-F | Adafruit |
| **STEMMA QT Cables** | 2-3 | I2C connections | Adafruit |

### Reagents & Consumables

| Component | Quantity | Notes | Source |
|-----------|----------|-------|--------|
| **API Phosphate Test Kit** | 1 | ~150 tests | Pet store/Amazon |
| **API Nitrate Test Kit** | 1 | ~90 tests | Pet store/Amazon |
| **Phosphate Standard (1000ppm PO₄)** | 1 bottle | Certified | Lab supply |
| **Nitrate Standard (1000ppm N)** | 1 bottle | Certified | Lab supply |

## Total Cost Summary (Adafruit Components)

| Category | Cost |
|----------|------|
| **PyBadge Controller** | $40.00 |
| **Motor/Servo Control** | $31.45 |
| **Valve Control** | $23.85 |
| **Air Pump & Tubing** | $12.95 |
| **Colorimeter Sensor** | $14.95 |
| **LEDs** | $1.00 |
| **Subtotal (Adafruit)** | **$124.20** |
| **Additional Components** | ~$100-150 |
| **Reagents** | ~$60-80 |
| **Grand Total (Estimated)** | **$284-354** |

## FeatherWing Stacking

The PyBadge is **not** a Feather board, so direct FeatherWing stacking won't work. Instead, use the following approach:

### Option 1: External Feather + I2C Communication

Use a separate **Feather M4 Express** as a motor/valve controller:

```
PyBadge (Main Controller)
    │
    ├─ I2C ──► AS7341 Colorimeter
    │
    └─ I2C ──► Feather M4 (Motor Controller)
              │
              ├─ DC Motor FeatherWing (PID 3243)
              │   └─ FeW Pump, FeR Pump
              │
              └─ Solenoid Driver (PID 6318)
                  └─ ReV, WtV, WaV valves
```

**Additional Required:**
- Feather M4 Express (Adafruit #3857) - $22.95

### Option 2: Direct GPIO Control from PyBadge

Use the Solenoid Driver and Motor FeatherWing as standalone I2C modules:

```
PyBadge
    │
    ├─ I2C ──► AS7341 Colorimeter
    ├─ I2C ──► Solenoid Driver (PID 6318) ──► Valves
    └─ I2C ──► Motor FeatherWing (via breakout) ──► Pumps (bidirectional for bubbling)
```

**Notes:**
- Motor FeatherWing can be used as standalone I2C module
- Requires I2C address configuration
- STEMMA QT cables simplify wiring

### Recommended: Option 2 (Direct Control)

Simpler architecture, fewer components, lower cost.

## Wiring Diagram (with Adafruit Parts)

```
                    PyBadge Controller
                          │
            ┌─────────────┼─────────────┐
            │             │             │
        (I2C/SDA)     (I2C/SCL)      (Power)
            │             │             │
            ▼             ▼             ▼
    ┌───────────────────────────────────────┐
    │      STEMMA QT I2C Bus (3.3V)         │
    └───┬──────────┬────────────┬───────────┘
        │          │            │
        ▼          ▼            ▼
   ┌────────┐  ┌─────────┐  ┌──────────────┐
   │ AS7341 │  │Solenoid │  │ Motor/Servo  │
   │ Sensor │  │ Driver  │  │ Controller   │
   └────────┘  └────┬────┘  └──────┬───────┘
                    │               │
            ┌───────┼───────┐       ├─────────┐
            ▼       ▼       ▼       ▼         ▼
         [ReV]   [WtV]   [WaV]  [FeW    [FeR Pump]
         Valve   Valve   Valve   Pump]  (bidirectional)
```

## CircuitPython Libraries Required

```python
# Install these libraries to PyBadge:
adafruit_as7341          # Colorimeter sensor
adafruit_motor           # DC motor control
adafruit_seesaw          # Motor FeatherWing I2C control
adafruit_pypixelbuf      # Display support
```

## Power Distribution

```
12V 2A Power Supply
    │
    ├─► Solenoid Driver (12V input, regulates to 6V for valves)
    │       └─► 3× 6V Air Valves
    │
    ├─► DC Motor FeatherWing (12V motor power)
    │       └─► 2× Peristaltic Pumps (bidirectional for bubble mixing)
    │
    └─► Air Pump (optional, via relay for alternative mixing method)

PyBadge: Separate USB-C power (5V) or battery

**Note:** Mixing is achieved by reversing pumps to create air bubbles, eliminating
the need for separate stirrer motors.
```

## Assembly Notes

1. **STEMMA QT Advantage**: All I2C devices use standardized STEMMA QT connectors
   - No breadboard required for I2C connections
   - Plug-and-play with cables
   - Daisy-chain multiple devices

2. **Motor FeatherWing Setup**:
   - Terminal blocks for motor connections
   - Supports 4 DC motors (we use 2 for pumps)
   - Reversible control for bidirectional pumps

3. **Solenoid Driver**:
   - 8 channels (use 3, have 5 spare)
   - Built-in flyback diodes
   - I2C address selectable (0x40 default)

4. **3D Printed Enclosure**:
   - Mount PyBadge on front panel
   - Motor FeatherWing + Solenoid Driver on side panel
   - Pumps, valves, and bottles in main chamber

## Next Steps

1. Order components from Adafruit
2. Test individual modules (pumps, valves, sensor)
3. Assemble and wire system
4. Load CircuitPython firmware
5. Calibrate pumps and colorimeter
6. Run test assays

## Purchase Links

- **Adafruit**: https://www.adafruit.com
- **Search by PID**: https://www.adafruit.com/product/{PID}

For complete assembly instructions, see [Assembly Guide](assembly.md) (coming soon).
