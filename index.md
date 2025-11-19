---
layout: splash
title: "OpenReef Automated System"
header:
  overlay_color: "#000"
  overlay_filter: "0.5"
  overlay_image: /assets/images/header.jpg
  actions:
    - label: "Get Started"
      url: "/docs/getting-started/quick-start/"
    - label: "View on GitHub"
      url: "https://github.com/thetemplateblog/openreef"
excerpt: "Open-source automated colorimetric water quality testing for phosphate and nitrate analysis"
intro:
  - excerpt: 'Fully automated, PyBadge-controlled platform for precise water quality testing. Perfect for reef aquariums, hydroponics, and environmental monitoring.'
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

**OpenReef** is a fully automated, PyBadge-controlled platform for colorimetric water quality testing. The system automates the entire assay process from sample preparation through measurement and cleanup, providing accurate phosphate and nitrate measurements for:

- 🐠 Reef aquarium monitoring
- 🌱 Hydroponic nutrient management
- 🌊 Environmental water testing
- 🎓 Educational demonstrations

### Key Features

- **Fully Automated**: Hands-off operation from sample to result
- **Dual Assay Support**: Phosphate (625nm) and Nitrate (528nm) testing
- **Precision Control**: Automated pumps, valves, and timing
- **Open Source**: Complete hardware designs, firmware, and documentation
- **Cost Effective**: ~$300 total build cost using off-the-shelf components
- **PyBadge Display**: Interactive menu and real-time results

---

## Quick Links

### 📖 Documentation

- [Introduction & Overview](docs/introduction/overview.md) - System overview and measurement theory
- [Quick Start Guide](docs/getting-started/quick-start.md) - Get up and running quickly

### 🧪 Assay Protocols

- [Phosphate Assay](docs/assays/phosphate.md) - 625nm colorimetric method (0-30 ppm)
- [Nitrate Assay](docs/assays/nitrate.md) - 528nm colorimetric method (0-90 ppm)

### 🔧 Hardware

- [Parts List & BOM](docs/hardware/parts-list.md) - Complete bill of materials
- [Adafruit Components](docs/hardware/adafruit-parts-bom.md) - Specific Adafruit parts
- [CAD Files (Coming Soon)](docs/hardware/cad-files.md) - 3D printable designs

### 💻 Software

- [Automation Sequence](docs/firmware/automation-sequence.md) - Complete automation workflow
- [Calibration Guide](docs/calibration/calibration-guide.md) - Calibration procedures

---

## System Architecture

```
┌─────────────────────────────────────────┐
│          PyBadge Controller             │
│  ┌──────────┐  ┌────────────────────┐  │
│  │ Display  │  │  AS7341 Sensor     │  │
│  │ & UI     │  │  I2C Control       │  │
│  └──────────┘  └────────────────────┘  │
└────────┬──────────────┬─────────────────┘
         │              │
    User Interface  Measurement & Control
         │              │
    ┌────▼────┐    ┌────▼─────────┐
    │ Cuvette │    │  Pumps (2×)  │
    │(bubbling│    │  Valves (3×) │
    └─────────┘    │  Reagents    │
                   └──────────────┘
```

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

🚧 **In Development**

### Completed
- ✅ System architecture design
- ✅ Hardware component selection
- ✅ Assay protocol documentation
- ✅ Automation sequence design

### In Progress
- 🔨 CAD designs (3D printable enclosure and mounts)
- 🔨 Calibration procedures documentation
- 🔨 CircuitPython firmware development
- 🔨 Hardware assembly guide
- 🔨 PCB design (optional)

### Planned
- 📋 Web interface for data visualization
- 📋 WiFi connectivity (ESP32)
- 📋 Additional assays (ammonia, silicate)

---

## Getting Started

### Build Your Own

**Estimated Cost:** $280-350

1. **Review Documentation**
   - [Introduction](docs/introduction/overview.md)
   - [Parts List](docs/hardware/parts-list.md)

2. **Order Components**
   - [Adafruit Parts BOM](docs/hardware/adafruit-parts-bom.md)

3. **3D Print Enclosure**
   - [CAD Files (Coming Soon)](docs/hardware/cad-files.md)

4. **Assemble Hardware**
   - Assembly guide coming soon

5. **Calibrate System**
   - [Calibration Guide](docs/calibration/calibration-guide.md)

6. **Run Tests!**
   - [Quick Start](docs/getting-started/quick-start.md)

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
