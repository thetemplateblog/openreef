# Open Colorimeter for Arduino Giga R1 WiFi

This is a port of the Open Colorimeter firmware from CircuitPython (PyBadge) to Arduino C++ for the **Arduino Giga R1 WiFi** with **Giga Display Shield**.

## Features

- **800x480 Touchscreen Display** - Large, beautiful UI with LVGL graphics
- **TSL2591 Light Sensor** - High-sensitivity luminosity sensor
- **Multiple Measurements** - Absorbance, Transmittance, Raw Sensor, and custom calibrations
- **Motor Control** - Control up to 4 DC motors via PCA9685
- **Solenoid Control** - Control up to 4 solenoid valves
- **Calibration System** - Polynomial curve fitting for custom tests
- **9 MB RAM** - No more memory constraints!

## Hardware Requirements

### Required
- **Arduino Giga R1 WiFi** (ABX00063)
- **Arduino Giga Display Shield** (800x480 touchscreen)
- **TSL2591 Light Sensor** (I2C address 0x29)
- **Micro SD Card** (for storing calibrations and config)

### Optional
- **Adafruit PCA9685 Motor FeatherWing** (I2C address 0x60) for motor control
- **Adafruit PCA9685 PWM Driver** (I2C address 0x61) for solenoid control
- **DC Motors** (up to 4)
- **Solenoid Valves** (up to 4)

## Arduino Libraries Required

Install these libraries via Arduino Library Manager:

1. **Arduino_GigaDisplay_GFX** - Display driver for Giga Display Shield
2. **ArduinoJson** (v6.x) - JSON parsing for calibrations
3. **Wire** (built-in) - I2C communication

## Project Structure

```
arduino_giga_colorimeter/
├── arduino_giga_colorimeter.ino  # Main sketch
├── src/
│   ├── Config.h                   # Constants and configuration
│   ├── LightSensor.h/.cpp         # TSL2591 sensor driver
│   ├── Calibrations.h/.cpp        # Calibration management
│   ├── UI_Manager.h/.cpp          # Display and UI management
│   ├── MotorController.h/.cpp     # DC motor control
│   └── SolenoidController.h/.cpp  # Solenoid valve control
└── data/
    ├── calibrations.json          # Calibration data
    └── configuration.json         # Device configuration
```

## Setup Instructions

### 1. Install Arduino IDE

Download and install the latest Arduino IDE 2.x from https://www.arduino.cc/en/software

### 2. Install Arduino Giga R1 Board Support

1. Open Arduino IDE
2. Go to **Tools > Board > Boards Manager**
3. Search for "Arduino Mbed OS Giga Boards"
4. Install the board package

### 3. Install Required Libraries

Go to **Sketch > Include Library > Manage Libraries** and install:
- Arduino_GigaDisplay_GFX
- ArduinoJson (version 6.x)

### 4. Prepare SD Card

1. Format a micro SD card as FAT32
2. Copy `calibrations.json` and `configuration.json` to the root of the SD card
3. Insert SD card into Giga Display Shield

### 5. Hardware Connections

#### TSL2591 Light Sensor (Required)
```
TSL2591 VIN  → Giga 3.3V
TSL2591 GND  → Giga GND
TSL2591 SDA  → Giga SDA (I2C)
TSL2591 SCL  → Giga SCL (I2C)
```

#### PCA9685 Motor Driver (Optional)
```
PCA9685 VCC  → Giga 5V
PCA9685 GND  → Giga GND
PCA9685 SDA  → Giga SDA (I2C)
PCA9685 SCL  → Giga SCL (I2C)
PCA9685 V+   → Motor power supply (6-12V)
```

#### Solenoid Driver (Optional)
Use a second PCA9685 at address 0x61, or configure GPIO pins

### 6. Upload Firmware

1. Connect Arduino Giga R1 via USB-C
2. Select **Tools > Board > Arduino Mbed OS Giga Boards > Arduino Giga R1 WiFi**
3. Select the correct **Port**
4. Click **Upload**

### 7. Serial Monitor

Open Serial Monitor at 115200 baud to see debug output:
- Free RAM at startup
- Sensor initialization status
- Calibration loading status
- Motor/solenoid mock mode warnings

## Configuration

### calibrations.json

Defines test calibrations with polynomial curve fitting:

```json
{
  "Phosphate API": {
    "units": "ppm",
    "led": "625",
    "fit_type": "polynomial",
    "fit_coef": [3.500142, -1.194604],
    "range": {"min": 0.0, "max": 2.79}
  }
}
```

- **units**: Measurement units (e.g., "ppm", "mg/L")
- **led**: LED wavelength in nm
- **fit_type**: Currently supports "polynomial"
- **fit_coef**: Polynomial coefficients [a0, a1, a2, ...] for y = a0 + a1*x + a2*x^2 + ...
- **range**: Valid measurement range

### configuration.json

Device settings:

```json
{
  "gain": "low",
  "integration_time": "500ms",
  "startup": "Absorbance",
  "precision": 2
}
```

## Usage

### Basic Operation

1. **Power On** - System initializes and shows measurement screen
2. **Blank** - Tap BLANK button to capture blank reference
3. **Measure** - Insert sample and read value
4. **Menu** - Access different measurement modes and controls

### Measurement Modes

- **Absorbance** - Standard absorbance measurement
- **Transmittance** - Percentage of light transmitted
- **Raw Sensor** - Direct sensor reading
- **Custom Tests** - Any calibrations loaded from JSON

### Motor Control

1. Tap **MENU** → **Motors**
2. Select motor number (1-4)
3. Use touch controls for:
   - **Forward/Reverse** - Direction
   - **Speed** - Throttle level (0-100%)
   - **Stop** - Emergency stop

### Solenoid Control

1. Tap **MENU** → **Solenoids**
2. Select solenoid number (1-4)
3. Tap to **Open** or **Close**
4. Optional: Set pulse duration for timed operation

## Memory Advantages

**Arduino Giga R1**: 9 MB RAM (1 MB SRAM + 8 MB SDRAM)
**PyBadge**: 192 KB RAM

This gives you **47x more memory**, eliminating all the memory optimization workarounds from the CircuitPython version!

## Troubleshooting

### "TSL2591 not found"
- Check I2C connections
- Verify sensor address (0x29)
- Try I2C scanner sketch

### "SD card initialization failed"
- Ensure SD card is formatted as FAT32
- Check SD card is properly inserted
- Try different SD card

### "PCA9685 not found - running in mock mode"
- Normal if motor controller not connected
- System will log commands but not control actual hardware
- Connect PCA9685 to enable motor/solenoid control

### Display issues
- Ensure Giga Display Shield is properly seated
- Check Arduino_GigaDisplay_GFX library is installed
- Try display examples from library

## Future Enhancements

- [ ] Full LVGL UI implementation with animations
- [ ] Touch calibration
- [ ] Wi-Fi data logging
- [ ] Bluetooth control from phone app
- [ ] Real-time graphing
- [ ] Camera integration for sample detection
- [ ] Multi-language support

## Differences from PyBadge Version

| Feature | PyBadge | Giga R1 |
|---------|---------|---------|
| RAM | 192 KB | 9 MB |
| Display | 160x128 | 800x480 |
| Input | Buttons | Touchscreen |
| Language | CircuitPython | C++ |
| Speed | 120 MHz | 480 MHz |
| Motors | Memory constrained | No limits |
| Solenoids | Not supported | Supported |

## Credits

- Original firmware: Open Colorimeter Project
- Ported to Arduino C++ for Giga R1
- TSL2591 driver based on Adafruit library
- UI framework using Arduino_GigaDisplay_GFX

## License

Same as original Open Colorimeter firmware

## Support

For issues specific to this Arduino port, please check:
1. Hardware connections
2. Library versions
3. Serial monitor output
4. SD card contents

Original CircuitPython version: `/open_colorimeter_firmware_v0.1.1/`
