---
layout: splash
title: "OpenReef Automated System"
header:
  overlay_color: "#000"
  overlay_filter: "0.5"
  overlay_image: /assets/images/header.jpg
  actions:
    - label: "Get Started"
      url: "/docs/getting-started/raspberry-pi-setup/"
    - label: "View on GitHub"
      url: "https://github.com/thetemplateblog/openreef"
excerpt: "Open-source Raspberry Pi web-based colorimeter for phosphate and nitrate water quality testing"
intro:
  - excerpt: 'Web-controlled Raspberry Pi platform for precise automated water quality testing. Access from any device on your network. Perfect for reef aquariums, hydroponics, and environmental monitoring.'
feature_row:
  - image_path: /assets/images/phosphate.jpg
    alt: "Phosphate Testing"
    title: "Phosphate Assay"
    excerpt: "0-30 ppm range, 625nm colorimetric detection, 12-minute automated cycle"
    url: "/docs/assays/phosphate/"
    btn_label: "Learn More"
    btn_class: "btn--primary"
  - image_path: /assets/images/nitrate.jpg
    alt: "Nitrate Testing"
    title: "Nitrate Assay"
    excerpt: "0-90 ppm range, 528nm colorimetric detection, 10-minute automated cycle"
    url: "/docs/assays/nitrate/"
    btn_label: "Learn More"
    btn_class: "btn--primary"
  - image_path: /assets/images/hardware.jpg
    alt: "Open Hardware"
    title: "Open Source"
    excerpt: "Complete CAD files, firmware, and documentation. Build cost ~$300"
    url: "/docs/hardware/parts-list/"
    btn_label: "Learn More"
    btn_class: "btn--primary"
---

## Overview

**OpenReef** is an open-source Raspberry Pi-based colorimeter for automated water quality testing. The web-controlled system provides phosphate and nitrate measurements for 🐠 Reef aquarium monitoring, hydroponics, and environmental testing.

### Key Features

- **Web-Based Control**: Access from phone, tablet, or computer on your network
- **Remote Monitoring**: Check water quality from anywhere
- **Automated Sequences**: Pre-programmed test protocols with motors, valves, and timers
- **Real-Time Display**: Live sensor readings and interactive controls
- **Multi-Channel**: Support for 4 motors and 8 solenoid valves
- **Editable Calibrations**: Web-based JSON configuration for custom calibrations
- **Open Source**: Complete hardware designs, Python code, and documentation
- **Cost Effective**: ~$200-250 build cost using Raspberry Pi and Adafruit components
- **No Display Required**: Headless operation with web interface

---

## Quick Links

### 📖 Documentation

- [Raspberry Pi Setup Guide](docs/getting-started/raspberry-pi-setup.md) - Complete setup instructions
- [Full Documentation](firmware/open_colorimeter_pi/README.md) - Detailed Pi colorimeter guide
- [Introduction & Overview](docs/introduction/overview.md) - System overview and measurement theory

### 🧪 Assay Protocols

- [Phosphate Assay](docs/assays/phosphate.md) - 625nm colorimetric method (0-30 ppm)
- [Nitrate Assay](docs/assays/nitrate.md) - 528nm colorimetric method (0-90 ppm)
- [All Tests](https://airtable.com/appMpWSXr4eiez8un/shr0cEYUXC2TSvy0D/tblhy9wB2t7TJefgu)

### 🔧 Hardware

- [Raspberry Pi Hardware Guide](docs/hardware/raspberry-pi.md) - Complete parts list and assembly
- [Adafruit Components](docs/hardware/adafruit-parts-bom.md) - Motor HAT, sensors, solenoid driver
- [Control Led](https://github.com/iorodeo/i_control_led/tree/main)
- [Open Colorimeter Product Guide](https://blog.iorodeo.com/open-colorimeter-product-guide/)

### 💻 Software

- [Web Interface Documentation](firmware/open_colorimeter_pi/README.md) - Flask app, API, automation
- [Calibration Guide](docs/calibration/calibration-guide.md) - Calibration procedures
- [Configuration Files](firmware/open_colorimeter_pi/README.md#configuration) - Edit mappings, sequences, calibrations

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
| **TSL2591** | Light sensor | Absorbance measurements |
| **Motor HAT** | Motor control | 4 DC motors for pumps/stirring |
| **MCP23017** | Solenoid driver | 8-channel valve control |
| **Web UI** | User interface | Responsive web app, any device |

---

## Assay Comparison

| Feature | Phosphate | Nitrate |
|---------|-----------|---------|
| **Chemistry** | Ascorbic acid method | Cadmium reduction + Griess |
| **Wavelength** | 625 nm (Red) | 528 nm (Green) |
| **Range** | 0-30 ppm PO₄ | 0-90 ppm NO₃ |
| **Reaction Time** | 5-10 min* | 5+ min |
| **Total Time** | ~12 min | ~10 min |

*Critical timing - phosphate measurements must be taken within 5-10 minute window

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

### In Progress
- 🔨 CAD designs (3D printable enclosure and mounts)
- 🔨 Hardware assembly guide with photos
- 🔨 Assay-specific calibration protocols
- 🔨 PCB design (optional, for cleaner wiring)

### Planned
- 📋 Sensor multiplexer support (multi-sensor switching)
- 📋 Data visualization and trending
- 📋 Additional assays (ammonia, silicate)
- 📋 Mobile app (optional)

---

## Getting Started

### Build Your Raspberry Pi Colorimeter

**Estimated Cost:** $200-250

1. **Order Components**
   - [Hardware Guide](docs/hardware/raspberry-pi.md) - Complete parts list
   - [Adafruit Components](docs/hardware/adafruit-parts-bom.md) - Motor HAT, sensors, driver
   - Raspberry Pi 3/4/5
   - TSL2591 light sensor
   - Fluidics components

2. **Install Software**
   - [Setup Guide](docs/getting-started/raspberry-pi-setup.md) - Step-by-step instructions
   - Install Raspberry Pi OS or Ubuntu Server
   - Clone repository and install dependencies
   - Run automated service installer

3. **Connect Hardware**
   - Stack Motor HAT on Raspberry Pi GPIO
   - Connect TSL2591 sensor via I2C
   - Connect MCP23017 solenoid driver (optional)
   - Wire motors and valves

4. **Configure & Calibrate**
   - Access web interface at `http://raspberrypi.local:5000`
   - Edit device names in mappings.json
   - Create calibration curves
   - [Calibration Guide](docs/calibration/calibration-guide.md)

5. **Run Automated Tests!**
   - Create command sequences
   - Mix motors, solenoids, waits, blanking, measurements
   - Monitor from any device on your network
   - Save and load test protocols

---

## Contributing

This is an open-source project. Contributions welcome!

- 📝 **Documentation**: Improvements and corrections
- 💻 **Firmware**: CircuitPython code development
- 🔧 **Hardware**: Enclosure designs, PCB layouts
- 🧪 **Testing**: Validation and QC data

---

## License

This project is licensed under the **MIT License**.

**Based on:**
- [IoRodeo Open Colorimeter](https://www.iorodeo.com/collections/colorimeter) - Hardware designs (CC BY 4.0)
- [IoRodeo BioRodeo Assay Protocols](https://sites.google.com/iorodeo.com/biorodeo/) - Assay methods

---

## Acknowledgments

Built with:
- [AdaFruit](https://www.adafruit.com) - PyBadge, sensors, electronics
- [CircuitPython](https://circuitpython.org) - Embedded Python platform
- API Test Kits - Reagent chemistry

---

**Built with passion for the reef keeping and maker communities.**

🐠 🪸 🧪 🔬 🤖
