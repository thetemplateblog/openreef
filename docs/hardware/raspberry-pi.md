# Raspberry Pi Hardware Guide

Complete parts list and assembly guide for the Raspberry Pi-based Open Colorimeter.

---

## Overview

The Raspberry Pi version provides a web-based interface accessible from any device on your network. No physical display required - control everything through your phone, tablet, or computer.

**Estimated Cost:** $200-250

---

## Required Components

### Core Controller

| Component | Description | Source | Est. Cost |
|-----------|-------------|--------|-----------|
| **Raspberry Pi 3/4/5** | Main controller | [Adafruit](https://www.adafruit.com/category/105), [Amazon](https://www.amazon.com/s?k=raspberry+pi) | $35-75 |
| **MicroSD Card** | 16GB+ for OS and data | Amazon | $8-15 |
| **USB-C Power Supply** | 5V 3A for Pi | Adafruit | $8 |

**Recommendation:** Raspberry Pi 4 (4GB RAM) or Pi 5 for best performance. Pi 3 works but may be slower.

---

## I2C Hardware

### Light Sensor

| Component | Description | Adafruit PID | Est. Cost |
|-----------|-------------|--------------|-----------|
| **TSL2591 Light Sensor** | High-sensitivity light-to-digital converter | [1980](https://www.adafruit.com/product/1980) | $6.95 |

**I2C Address:** 0x29 (default)

**Features:**
- 600M:1 dynamic range
- Programmable gain (1x, 25x, 428x, 9876x)
- Integration time: 100ms to 600ms
- IR + visible light measurement

### Motor Control

| Component | Description | Adafruit PID | Est. Cost |
|-----------|-------------|--------------|-----------|
| **DC & Stepper Motor HAT** | 4-channel DC motor controller | [2348](https://www.adafruit.com/product/2348) | $22.50 |
| **12V DC Power Supply** | 12V 2-3A for motors | [798](https://www.adafruit.com/product/798) | $12.50 |

**I2C Address:** 0x60 (PCA9685), 0x70 (auxiliary)

**Features:**
- 4 H-Bridges for DC motors
- 1.2A per channel continuous
- Stackable design
- Separate motor power supply

### Solenoid Control (Optional)

| Component | Description | Adafruit PID | Est. Cost |
|-----------|-------------|--------------|-----------|
| **I2C 8-Channel Solenoid Driver** | MCP23017-based valve controller | [6318](https://www.adafruit.com/product/6318) | $9.95 |
| **12V Solenoid Valves** | Normally closed air valves (qty varies) | [4663](https://www.adafruit.com/product/4663) | $5.95 each |

**I2C Address:** 0x20 (default, configurable)

**Features:**
- 8 independent channels
- 12V operation
- LED status indicators per channel
- Shared I2C bus with other components

---

## Motors & Actuators

### DC Motors

| Component | Description | Source | Est. Cost |
|-----------|-------------|--------|-----------|
| **Peristaltic Pump Motors** | 12V DC motors with pumps | Various | $15-30 each |
| **Small DC Motors** | 6-12V for stirring/mixing | Adafruit, Amazon | $5-10 each |

**Requirements:**
- Voltage: 4.5V - 13.5V
- Current: < 1.2A continuous per motor
- Quantity: 2-4 motors depending on application

**Typical Configuration:**
- **Motor 1:** Sample pump (fill cuvette)
- **Motor 2:** Reagent pump (dosing)
- **Motor 3:** Stirrer/mixer (optional)
- **Motor 4:** Waste pump (optional)

---

## Fluidics Components

### Tubing & Connections

| Component | Description | Adafruit PID | Est. Cost |
|-----------|-------------|--------------|-----------|
| **Silicone Tubing** | 3mm ID, food-safe | [4661](https://www.adafruit.com/product/4661) | $5.95/meter |
| **Tube Fittings** | Barb connectors, valves | Various | $10-20 |

### Cuvette & Optics

| Component | Description | Source | Est. Cost |
|-----------|-------------|--------|-----------|
| **Optical Cuvette** | 1cm path length, 3.5mL | [Amazon](https://www.amazon.com/s?k=1cm+optical+cuvette), Lab suppliers | $10-20 |
| **LED Light Source** | 525nm (green) or 625nm (red) | Adafruit | $5-10 |

**Cuvette Requirements:**
- Material: Optical-grade plastic or quartz
- Path length: 1 cm (10mm)
- Volume: 3-5 mL
- Clear/transparent walls

---

## Power Requirements

### Power Distribution

| Power Rail | Voltage | Current | Usage |
|------------|---------|---------|-------|
| **Raspberry Pi** | 5V | 2-3A | USB-C power adapter |
| **Motors** | 12V | 2-3A | Motor HAT green terminal |
| **Solenoids** | 12V | 1-2A | Solenoid driver terminal |

**Important:**
- Motor power is **separate** from Raspberry Pi power
- Never connect 12V motor power to Raspberry Pi GPIO
- Use proper polarity (+ and -)

### Recommended Power Supplies

- **Raspberry Pi:** Official USB-C 5V 3A power supply
- **Motors:** 12V 2A+ barrel jack adapter (Adafruit #798)
- **Total System:** ~15W during operation

---

## Assembly Overview

### 1. Stack the Motor HAT

1. Power off Raspberry Pi
2. Align Motor HAT with 40-pin GPIO header
3. Press firmly to seat all pins
4. HAT should sit flush on top

### 2. Connect I2C Devices

All I2C devices share the same SCL/SDA bus:

**Connections:**
- **TSL2591 Sensor:**
  - VIN → Pi 3.3V or 5V
  - GND → Pi GND
  - SCL → Pi GPIO 3 (SCL)
  - SDA → Pi GPIO 2 (SDA)

- **Solenoid Driver:**
  - VIN → Pi 3.3V or 5V
  - GND → Pi GND
  - SCL → Pi GPIO 3 (SCL)
  - SDA → Pi GPIO 2 (SDA)

**Note:** All I2C devices can connect to the same pins via breadboard or I2C hub.

### 3. Connect Motors

Connect DC motors to Motor HAT blue terminal blocks:
- **M1, M2, M3, M4** - two wires per motor
- Polarity determines direction (can swap if backwards)

### 4. Connect Motor Power

Connect 12V power supply to Motor HAT green terminal:
- **+ (positive)** to + terminal
- **- (ground)** to - terminal

**Warning:** Do NOT connect 12V to Raspberry Pi GPIO!

### 5. Connect Solenoids (Optional)

If using solenoid valves:
1. Connect 12V power to solenoid driver
2. Connect valves to channels 1-8
3. Each valve requires two wires

---

## I2C Address Reference

| Device | Address | Configurable |
|--------|---------|--------------|
| TSL2591 Sensor | 0x29 | No |
| Motor HAT (PCA9685) | 0x60 | Yes (solder jumpers) |
| Motor HAT (auxiliary) | 0x70 | No |
| Solenoid Driver (MCP23017) | 0x20 | Yes (solder jumpers) |
| Multiplexer (TCA9548A) | 0x70 | Yes (avoid conflict) |

**Verify I2C Devices:**
```bash
sudo i2cdetect -y 1
```

Should show devices at their respective addresses.

---

## Bill of Materials Summary

### Minimum System (Sensor Only)

| Component | Qty | Est. Cost |
|-----------|-----|-----------|
| Raspberry Pi 4 (4GB) | 1 | $55 |
| MicroSD Card (32GB) | 1 | $10 |
| USB-C Power Supply | 1 | $8 |
| TSL2591 Sensor | 1 | $7 |
| **Total** | | **~$80** |

### Full System (Motors + Solenoids)

| Component | Qty | Est. Cost |
|-----------|-----|-----------|
| Raspberry Pi 4 (4GB) | 1 | $55 |
| MicroSD Card (32GB) | 1 | $10 |
| USB-C Power Supply | 1 | $8 |
| TSL2591 Sensor | 1 | $7 |
| Motor HAT | 1 | $23 |
| 12V Power Supply (motors) | 1 | $13 |
| DC Motors | 2-4 | $40-80 |
| Solenoid Driver | 1 | $10 |
| Solenoid Valves | 4 | $24 |
| Tubing & Fittings | - | $20 |
| Cuvette | 1 | $15 |
| LEDs | 2 | $10 |
| **Total** | | **~$235-275** |

---

## Optional Enhancements

### Sensor Multiplexer (Multi-Sensor Support)

| Component | Description | Adafruit PID | Est. Cost |
|-----------|-------------|--------------|-----------|
| **TCA9548A Multiplexer** | 8-channel I2C switch | [2717](https://www.adafruit.com/product/2717) | $6.95 |

**Use Case:** Connect multiple TSL2591 sensors for different wavelengths or tests.

**Configuration:** Set I2C address to 0x71 or other to avoid conflict with Motor HAT auxiliary chip (0x70).

### Enclosure & Mounting

- 3D printed enclosure (STL files coming soon)
- DIN rail mounting brackets
- Acrylic or aluminum case
- Cable management and strain relief

---

## Next Steps

1. **Order Components:** Use Adafruit shopping cart with PIDs listed above
2. **Install Software:** See [Raspberry Pi Setup Guide](../getting-started/raspberry-pi-setup.md)
3. **Assemble Hardware:** Follow connection diagrams above
4. **Test I2C:** Verify all devices detected with `i2cdetect`
5. **Configure System:** Edit mappings.json for device names
6. **Calibrate:** Create calibration curves for your tests

---

## Troubleshooting

### Motor HAT Not Detected

**Check:**
- HAT properly seated on GPIO pins
- I2C enabled in raspi-config
- Run `sudo i2cdetect -y 1` to scan bus

### Motors Not Running

**Check:**
- 12V power connected to green terminal
- Polarity correct (+ and -)
- Motor wires secure in blue terminals
- Try swapping motor wires if direction is backwards

### Sensor Not Found

**Check:**
- Wiring: VIN, GND, SCL, SDA
- Voltage: 3.3V or 5V (both work)
- Address: Should appear at 0x29

---

## Resources

- [Adafruit Motor HAT Guide](https://learn.adafruit.com/adafruit-dc-and-stepper-motor-hat-for-raspberry-pi)
- [Adafruit TSL2591 Guide](https://learn.adafruit.com/adafruit-tsl2591)
- [Adafruit Solenoid Driver Guide](https://learn.adafruit.com/adafruit-i2c-to-8-channel-solenoid-driver)
- [I2C Configuration](https://learn.adafruit.com/adafruits-raspberry-pi-lesson-4-gpio-setup/configuring-i2c)
- [Full Software Documentation](../../firmware/open_colorimeter_pi/README.md)

---

**Ready to build?** Continue to [Raspberry Pi Setup Guide](../getting-started/raspberry-pi-setup.md)
