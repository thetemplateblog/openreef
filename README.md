# OpenReef Automated System

Open-source Raspberry Pi web-based colorimeter for water quality testing.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Status](https://img.shields.io/badge/status-ready%20to%20build-green.svg)
![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![Platform](https://img.shields.io/badge/platform-Raspberry%20Pi-red.svg)

---

## Overview

**OpenReef** is an open-source Raspberry Pi-based colorimeter with web interface for automated water quality testing. Access measurements and controls from any device on your network. Perfect for reef aquariums, hydroponics, and environmental monitoring.

### Key Features

- **Web-Based Control**: Access from phone, tablet, or computer on your network
- **Remote Monitoring**: Check water quality from anywhere
- **Automated Sequences**: Pre-programmed test protocols with motors, valves, and timers
- **Real-Time Display**: Live sensor readings and interactive controls
- **Multi-Channel**: Support for 4 motors and 8 solenoid valves
- **Editable Calibrations**: Web-based JSON configuration
- **Open Source**: Complete hardware designs, Python code, and documentation
- **Cost Effective**: ~$200-250 build cost using Raspberry Pi and Adafruit components

---

## Quick Links

### 📖 Documentation

- **[Full Pi Documentation](firmware/open_colorimeter_pi/README.md)** - Detailed guide with all features
- [Introduction & Overview](docs/introduction/overview.md) - System overview

### 🧪 Assay Protocols

- [Phosphate Assay](docs/assays/phosphate.md) - 880nm colorimetric method
- [Nitrate Assay](docs/assays/nitrate.md) - 528nm colorimetric method
- [All Tests Database](https://airtable.com/appMpWSXr4eiez8un/shr0cEYUXC2TSvy0D/tblhy9wB2t7TJefgu)

### 🔧 Hardware

- [Raspberry Pi Hardware Guide](docs/hardware/raspberry-pi.md) - Complete parts list
- [Adafruit Components](docs/hardware/adafruit-parts-bom.md) - Motor HAT, sensors, driver

### 💻 Software

- [Web Interface](firmware/open_colorimeter_pi/README.md) - Flask app documentation
- [Calibration Guide](docs/calibration/calibration-guide.md) - Calibration procedures
- [Configuration](firmware/open_colorimeter_pi/README.md#configuration) - Mappings, sequences, calibrations

### 🔗 Related Projects

- [Control Led](https://github.com/iorodeo/i_control_led/tree/main)
- [Open Colorimeter Product Guide](https://blog.iorodeo.com/open-colorimeter-product-guide/)

---

## System Architecture

```
┌──────────────────────────────────────────┐
│      Raspberry Pi + Flask Server         │
│  ┌────────────┐  ┌──────────────────┐   │
│  │  TSL2591   │  │  Motor HAT       │   │
│  │  Sensor    │  │  Solenoid Driver │   │
│  └────────────┘  └──────────────────┘   │
└────────┬───────────────┬──────────────────┘
         │               │
    Measurement     Hardware Control
         │               │
         │          ┌────▼─────────┐
         │          │  Motors (4×) │
    ┌────▼────┐    │  Solenoids(8×)│
    │ Cuvette │    │  Reagents    │
    └─────────┘    └──────────────┘
         ▲
         │
    ┌────┴────────────────┐
    │   Web Browser UI    │
    │  (Phone/Tablet/PC)  │
    └─────────────────────┘
```

### Component Summary

| Component | Function | Details |
|-----------|----------|---------|
| **Raspberry Pi** | Main controller | Web server, automation, remote access |
| **TSL2591** | Light sensor | Absorbance measurements (I2C) |
| **Motor HAT** | Motor control | 4 DC motors for pumps/stirring |
| **MCP23017** | Solenoid driver | 8-channel valve control (I2C) |
| **Web UI** | User interface | Responsive Flask app, any device |

---

## Assay Comparison

| Feature | Phosphate | Nitrate |
|---------|-----------|---------|
| **Chemistry** | Ascorbic acid method | Cadmium reduction + Griess |
| **Wavelength** | 880 nm (NIR) | 528 nm (Green) |
| **Range** | 0-30 ppm PO₄ | 0-90 ppm NO₃ |
| **Reagent Drops** | 6 + 6 | 10 + 10 |
| **Reaction Time** | 5-10 min* | 5+ min |
| **Total Time** | ~12 min | ~10 min |
| **Critical Timing** | YES* | NO |

*Phosphate measurements must be taken within 5-10 minute window before solution becomes cloudy.

---

## Automated Sequence

1. **System Preparation** - Flush with RO water, clear waste
2. **Sample Loading** - Fill cuvette with test water (5 mL)
3. **Baseline** - Zero colorimeter with sample
4. **Reagent #1** - Automated dosing + mixing
5. **Reagent #2** - Automated dosing + mixing + timer start
6. **Incubation** - Timed color development
7. **Measurement** - Read absorbance, calculate concentration
8. **Cleanup** - Automatic RO water flush

All steps fully automated. Total hands-off time: 10-12 minutes.

---

## Getting Started

### 1. Hardware Assembly

**Estimated Cost:** $200-250

Components needed:
- Raspberry Pi 3/4/5
- Adafruit DC & Stepper Motor HAT
- TSL2591 light sensor
- MCP23017 solenoid driver
- DC motors, solenoid valves, power supply

Detailed guides:
- **[Raspberry Pi Hardware Guide](docs/hardware/raspberry-pi.md)** - Complete parts list
- **[Adafruit Components BOM](docs/hardware/adafruit-parts-bom.md)** - Specific part numbers

### 2. Software Installation

See **[Raspberry Pi Setup Guide](docs/getting-started/raspberry-pi-setup.md)** for complete instructions:

```bash
# Clone repository
git clone https://github.com/thetemplateblog/openreef.git
cd openreef/firmware/open_colorimeter_pi

# Install dependencies
pip install -r requirements.txt

# Run automated service installer
./install_service.sh
```

Access web interface at: `http://raspberrypi.local:5000`

### 3. Configuration & Calibration

- Edit device names in web Config tab (mappings.json)
- Create command sequences for automation
- Set up calibration curves
- Follow [Calibration Guide](docs/calibration/calibration-guide.md)

### 4. Run Your First Test

- Access web interface from any device
- Use Sequences tab to create automated protocols
- Monitor real-time measurements
- Save and load test configurations

---

## Documentation Structure

```
openreef/
├── README.md (this file)
├── docs/
│   ├── introduction/
│   │   └── overview.md
│   ├── getting-started/
│   │   └── raspberry-pi-setup.md
│   ├── assays/
│   │   ├── phosphate.md
│   │   └── nitrate.md
│   ├── hardware/
│   │   ├── raspberry-pi.md
│   │   └── adafruit-parts-bom.md
│   └── calibration/
│       └── calibration-guide.md
├── firmware/
│   └── open_colorimeter_pi/
│       ├── README.md (complete Pi guide)
│       ├── app.py (Flask web server)
│       ├── colorimeter.py (hardware control)
│       ├── templates/ (web UI)
│       └── static/ (CSS, JavaScript)
└── hardware/
    └── (CAD files, schematics - coming soon)
```

---

## Technical Specifications

### Measurement Capabilities

**Phosphate (PO₄)**
- Method: APHA 4500-P E (Ascorbic Acid)
- Range: 0-30 ppm PO₄
- LOD: 0.05 ppm
- LOQ: 0.10 ppm
- Wavelength: 880 nm

**Nitrate (NO₃)**
- Method: Cadmium Reduction + Griess
- Range: 0-90 ppm NO₃
- LOD: 0.2 ppm
- LOQ: 0.5 ppm
- Wavelength: 528 nm

### Performance

- **Precision**: < 5% RSD (relative standard deviation)
- **Accuracy**: ± 10% of known standards
- **Sample Volume**: 5 mL
- **Throughput**: 5-6 samples/hour
- **Automation Level**: 100% (sample to result)

---

## Applications

### Reef Aquarium

Monitor nutrient levels for optimal coral health:
- Ultra-low phosphate (< 0.03 ppm) for SPS corals
- Nitrate control (5-10 ppm) for mixed reefs
- Track water change effectiveness

### Hydroponics

Maintain nutrient solution balance:
- Ensure adequate phosphate for plant growth
- Monitor nitrate uptake
- Optimize fertilizer dosing

### Environmental Testing

Field water quality analysis:
- Stream/river nutrient monitoring
- Eutrophication assessment
- Agricultural runoff testing

### Education

Chemistry and instrumentation demonstrations:
- Colorimetric analysis principles
- Beer-Lambert law
- Automation and robotics

---

## Hardware Details

### Electronics

- **Controller**: Raspberry Pi 3/4/5
- **Sensor**: TSL2591 light sensor (I2C address 0x29)
- **Motor Control**: Adafruit DC & Stepper Motor HAT (I2C address 0x60)
- **Valve Control**: Adafruit I2C 8-Channel Solenoid Driver MCP23017 (I2C address 0x20)
- **Motors**: 4× DC motors (4.5-13.5V, <1.2A)
- **Solenoids**: 8× 12V solenoid valves

### Fluidics

- **Tubing**: 3mm ID silicone
- **Cuvette**: 1 cm path length for colorimetric measurements
- **Reservoirs**: RO water, test water, waste, reagents

### Power

- **Motor Power**: 12V DC, 2-3A (green terminal on Motor HAT)
- **Raspberry Pi**: 5V USB-C (separate from motor power)
- **Consumption**: ~15W during operation

---

## Software

### Web Interface

- **Language**: Python 3.x
- **Framework**: Flask (web server)
- **Platform**: Raspberry Pi (Raspberry Pi OS or Ubuntu Server)
- **Libraries**:
  - `adafruit-circuitpython-tsl2591` - Light sensor
  - `adafruit-circuitpython-motorkit` - Motor HAT control
  - `adafruit-circuitpython-mcp230xx` - Solenoid driver
  - `flask` - Web server
  - `numpy` - Data processing

### Features

- **Web-Based Interface**: Access from any device on network
- **Real-Time Measurements**: Live sensor data display
- **Automated Sequences**: Command-based automation (motors, valves, waits, blanking, measurements)
- **Editable Configurations**: Web-based JSON editors for mappings, sequences, and calibrations
- **Multi-Tab UI**: Measure, Motors, Solenoids, Sequences, Calibrations, Config
- **Auto-Start Service**: Systemd service for boot automation
- **Remote Access**: Network-accessible from phone, tablet, or computer

---

## Project Status

✅ **Raspberry Pi Version - Ready to Build!**

### Completed
- ✅ Raspberry Pi web interface (Flask)
- ✅ Hardware control (motors, solenoids, sensor)
- ✅ Automated command sequences
- ✅ Web-based configuration editors
- ✅ Calibration system
- ✅ Real-time measurements and display
- ✅ Systemd service automation
- ✅ Comprehensive documentation
- ✅ Assay protocol documentation

### In Progress
- 🔨 CAD designs (3D printable enclosure and mounts)
- 🔨 Hardware assembly guide with photos
- 🔨 Assay-specific calibration protocols
- 🔨 PCB design (optional, for cleaner wiring)

### Planned
- 📋 Sensor multiplexer support (multi-sensor switching)
- 📋 Data visualization and trending
- 📋 Additional assays (ammonia, silicate)
- 📋 Multi-sample carousel

---

## Contributing

This is an open-source project. Contributions welcome!

- **Documentation**: Improvements and corrections
- **Firmware**: CircuitPython code development
- **Hardware**: Enclosure designs, PCB layouts
- **Testing**: Validation and QC data

---

## Safety & Compliance

### Chemical Safety

⚠️ **Reagent Hazards**:
- Phosphate Bottle #1: Contains sulfuric acid (corrosive)
- Nitrate Bottle #2: Contains cadmium metal (toxic)

**Precautions**:
- Wear gloves and eye protection
- Work in ventilated area
- Dispose of nitrate waste properly (hazardous waste)
- Follow Red Sea Pro test kit MSDS

### Electrical Safety

- Use certified power supplies
- Ensure proper grounding
- Keep electronics away from liquids
- Follow local electrical codes

---

## License

This project is licensed under the **MIT License**.

```
Copyright (c) 2025 OpenReef Project

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## Acknowledgments

### Based on Methods From:
- [IoRodeo BioRodeo Assay Protocols](https://sites.google.com/iorodeo.com/biorodeo/)
- [Open Colorimeter Project](https://blog.iorodeo.com/open-colorimeter-product-guide/)
- APHA Standard Methods for Water Analysis

### Built With:
- [Raspberry Pi Foundation](https://www.raspberrypi.org) - Raspberry Pi platform
- [AdaFruit](https://www.adafruit.com) - Motor HAT, sensors, solenoid driver, electronics
- [CircuitPython (Blinka)](https://circuitpython.org) - Python hardware libraries
- [Flask](https://flask.palletsprojects.com/) - Web framework
- Red Sea Pro Test Kits - Reagent chemistry

---

## Contact & Support

- **Documentation**: See `/docs` folder
- **Issues**: [GitHub Issues](https://github.com/yourusername/openreef/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/openreef/discussions)

---

## Roadmap

### Version 1.0 (Released)
- ✅ Raspberry Pi web interface
- ✅ Core hardware control (motors, solenoids, sensor)
- ✅ Automated sequences
- ✅ Web-based configuration
- ✅ Manual calibration
- ✅ JSON data storage

### Version 1.1 (In Progress)
- 🔨 CAD designs for enclosure
- 🔨 Hardware assembly documentation
- 🔨 Assay-specific protocols

### Version 2.0 (Future)
- Sensor multiplexer support
- Data visualization and trending
- Historical data storage (SQLite)
- Additional assays (ammonia, alkalinity, calcium)
- Sample carousel automation
- Mobile-optimized UI

---

## Related Projects

- [Open Colorimeter](https://www.iorodeo.com/collections/colorimeter) - General purpose colorimeter
- [Atlas Scientific](https://atlas-scientific.com) - Water quality sensors
- [Reef-Pi](https://reef-pi.github.io) - Reef aquarium controller

---

**Built with passion for the reef keeping and maker communities.**

🐠 🪸 🧪 🔬 🤖
