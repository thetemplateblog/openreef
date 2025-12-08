# Raspberry Pi Setup Guide

Complete step-by-step guide to set up your Raspberry Pi-based Open Colorimeter with web interface.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Raspberry Pi OS Setup](#raspberry-pi-os-setup)
3. [Ubuntu Server Setup](#ubuntu-server-setup)
4. [Software Installation](#software-installation)
5. [Hardware Connection](#hardware-connection)
6. [First Run](#first-run)
7. [Configuration](#configuration)
8. [Auto-Start on Boot](#auto-start-on-boot)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Hardware Required

- Raspberry Pi 3, 4, or 5
- MicroSD card (16GB+) with OS installed
- TSL2591 light sensor
- Adafruit DC & Stepper Motor HAT
- (Optional) MCP23017 solenoid driver
- 12V power supply for motors
- USB-C power supply for Pi

See [Hardware Guide](../hardware/raspberry-pi.md) for complete parts list.

### Skills Required

- Basic Linux command line
- SSH access to Raspberry Pi
- Basic understanding of I2C hardware

---

## Choose Your Platform

This guide supports two operating systems:

- **Raspberry Pi OS** - Recommended for beginners
- **Ubuntu Server** - Recommended for headless deployments

Both work equally well. Choose based on your preference.

---

## Raspberry Pi OS Setup

### 1. Prepare System

```bash
# Update system
sudo apt update
sudo apt upgrade -y

# Install required packages
sudo apt install -y python3-pip python3-dev i2c-tools git
```

### 2. Enable I2C

```bash
sudo raspi-config
```

Navigate to:
- **Interface Options** → **I2C** → **Enable**

Reboot:
```bash
sudo reboot
```

### 3. Verify I2C

After reboot, check that I2C is working:

```bash
sudo i2cdetect -y 1
```

**Expected output** (with devices connected):
```
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:          -- -- -- -- -- -- -- -- -- -- -- -- --
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
20: 20 -- -- -- -- -- -- -- -- 29 -- -- -- -- -- --
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
60: 60 -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
70: 70 -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
```

**Addresses:**
- **0x20** - Solenoid driver (MCP23017)
- **0x29** - TSL2591 sensor
- **0x60** - Motor HAT (PCA9685)
- **0x70** - Motor HAT (auxiliary)

---

## Ubuntu Server Setup

### 1. Prepare System

```bash
# Update system
sudo apt update
sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-pip python3-dev i2c-tools git build-essential
```

### 2. Enable I2C

```bash
# Load I2C kernel module
sudo modprobe i2c-dev

# Make I2C load on boot
echo "i2c-dev" | sudo tee -a /etc/modules

# Add user to i2c group
sudo usermod -aG i2c $USER

# Create i2c group if it doesn't exist
sudo groupadd -f i2c

# Set I2C device permissions
echo 'KERNEL=="i2c-[0-9]*", GROUP="i2c", MODE="0660"' | sudo tee /etc/udev/rules.d/99-i2c.rules

# Reload udev rules
sudo udevadm control --reload-rules
sudo udevadm trigger

# Reboot
sudo reboot
```

### 3. Verify I2C

Check available I2C buses:
```bash
ls /dev/i2c-*
```

Scan for devices (usually bus 1):
```bash
sudo i2cdetect -y 1
```

If not on bus 1, try bus 0:
```bash
sudo i2cdetect -y 0
```

---

## Software Installation

### Option A: Using Virtual Environment (Recommended)

**For Raspberry Pi OS:**
```bash
# Install venv support
sudo apt install python3-venv

# Clone repository
cd ~
git clone https://github.com/thetemplateblog/openreef.git
cd openreef/firmware/open_colorimeter_pi

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**For Ubuntu Server (24.04+):**
```bash
# Install venv support
sudo apt install python3-venv python3-full

# Clone repository
cd ~
git clone https://github.com/thetemplateblog/openreef.git
cd openreef/firmware/open_colorimeter_pi

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### Option B: System-wide Installation

**Raspberry Pi OS:**
```bash
# Clone repository
cd ~
git clone https://github.com/thetemplateblog/openreef.git
cd openreef/firmware/open_colorimeter_pi

# Install dependencies
pip3 install -r requirements.txt
```

**Ubuntu (may require --break-system-packages):**
```bash
cd ~
git clone https://github.com/thetemplateblog/openreef.git
cd openreef/firmware/open_colorimeter_pi

pip3 install -r requirements.txt
```

**Note:** Ubuntu 24.04+ enforces PEP 668. Virtual environments are strongly recommended.

---

## Hardware Connection

### Before Powering On

1. **Power OFF** Raspberry Pi
2. **Stack Motor HAT** on GPIO pins
3. **Connect TSL2591** sensor:
   - VIN → Pi 3.3V or 5V
   - GND → Pi GND
   - SCL → GPIO 3
   - SDA → GPIO 2

4. **Connect Solenoid Driver** (optional):
   - VIN → Pi 3.3V or 5V
   - GND → Pi GND
   - SCL → GPIO 3
   - SDA → GPIO 2

5. **Connect Motors** to M1, M2, M3, M4 terminals
6. **Connect 12V power** to Motor HAT green terminal
7. **Power ON** Raspberry Pi

### Verify Connections

```bash
sudo i2cdetect -y 1
```

All devices should appear at their addresses.

---

## First Run

### Manual Test Run

**If using virtual environment:**
```bash
cd ~/openreef/firmware/open_colorimeter_pi
source venv/bin/activate
python app.py
```

**If using system Python:**
```bash
cd ~/openreef/firmware/open_colorimeter_pi
python3 app.py
```

**Expected output:**
```
Starting Open Colorimeter Web Interface
Access at: http://raspberrypi.local:5000
 * Running on http://0.0.0.0:5000
```

### Access Web Interface

Open browser to:
- **Local:** `http://raspberrypi.local:5000`
- **Network:** `http://[PI_IP_ADDRESS]:5000`

**Find IP address:**
```bash
hostname -I
```

### Test Hardware

1. **Sensor Tab:**
   - Click "Measure" - should see raw values
   - Click "Blank Sensor" - should see blank value updated

2. **Motors Tab:**
   - Move slider for Motor 1
   - Motor should spin (or pump should activate)
   - Test all motors

3. **Solenoids Tab:**
   - Toggle solenoid switches
   - Should hear click (valves opening/closing)

**If everything works, proceed to auto-start setup!**

---

## Configuration

### Device Names

Edit device names in the web interface:

1. Go to **Config** tab
2. Edit `mappings.json`:

```json
{
  "motors": {
    "1": {
      "name": "Sample",
      "description": "Sample pump"
    },
    "2": {
      "name": "Reagent",
      "description": "Reagent pump"
    }
  },
  "solenoids": {
    "1": {
      "name": "Inlet Valve",
      "description": "Sample inlet"
    }
  },
  "tests": {
    "Phosphate": {
      "sensor": 1,
      "calibration": "Phosphate"
    }
  }
}
```

3. Click **Save Mappings**
4. Reload page to see changes

### Calibration Curves

Go to **Calibrations** tab:

1. View existing calibrations
2. Click **Edit Calibrations** section
3. Modify `calibrations.json`:

```json
{
  "Phosphate": {
    "units": "ppm",
    "led": "525",
    "fit_type": "polynomial",
    "fit_coef": [0.0, 2.709, 0.0],
    "range": {
      "min": 0.0,
      "max": 1.0
    }
  }
}
```

4. Click **Save Calibrations**

### Command Sequences

Go to **Sequences** tab:

1. Create automated test protocols
2. Example sequence:

```
Sample, 30
Solenoid 1, on
wait, 5
Solenoid 1, off
Reagent, -15
wait, 10
blank
wait, 2
measure Phosphate
```

3. Click **Save As...** to save sequence
4. Click **Execute Sequence** to run

---

## Auto-Start on Boot

### Automated Installation (Recommended)

```bash
cd ~/openreef/firmware/open_colorimeter_pi
./install_service.sh
```

The script will:
- Detect virtual environment automatically
- Create systemd service
- Enable auto-start on boot
- Start service immediately
- Show web interface URLs

**That's it!** Service is now running.

### Verify Service

```bash
# Check status
sudo systemctl status colorimeter

# View logs
sudo journalctl -u colorimeter -f

# Restart service
sudo systemctl restart colorimeter

# Stop service
sudo systemctl stop colorimeter
```

### Uninstall Service

```bash
cd ~/openreef/firmware/open_colorimeter_pi
./uninstall_service.sh
```

---

## Updating the Application

### Automated Update

```bash
cd ~/openreef/firmware/open_colorimeter_pi
./update.sh
```

The update script:
- Pulls latest code from git
- Installs new dependencies
- Restarts service automatically

### Manual Update

```bash
cd ~/openreef/firmware/open_colorimeter_pi
git pull

# If using venv:
source venv/bin/activate
pip install -r requirements.txt

# If using system Python:
pip3 install -r requirements.txt

# Restart service
sudo systemctl restart colorimeter
```

---

## Troubleshooting

### Web Interface Not Accessible

**Check Flask is running:**
```bash
ps aux | grep python
```

**Check port 5000:**
```bash
sudo netstat -tulpn | grep 5000
```

**Check firewall (Ubuntu):**
```bash
sudo ufw status
sudo ufw allow 5000
```

**Try IP address instead:**
```bash
hostname -I
# Use: http://192.168.1.XXX:5000
```

### Motor HAT Not Detected

**Check physical connection:**
- Power off Pi
- Reseat Motor HAT on GPIO pins
- Power back on

**Check I2C enabled:**
```bash
# Raspberry Pi OS
sudo raspi-config
# Interface Options → I2C → Enable

# Ubuntu
lsmod | grep i2c
```

**Scan I2C bus:**
```bash
sudo i2cdetect -y 1
```

Should show 0x60 and 0x70.

### Motors Not Running

**Check power:**
- 12V supply connected to Motor HAT green terminal
- Polarity correct (+ and -)
- Motor power is separate from Pi power

**Check motor connections:**
- Wires secure in blue terminal blocks
- Try swapping motor wires if direction backwards

**Test in web interface:**
- Go to Motors tab
- Move Motor 1 slider
- Should see/hear motor respond

### Sensor Not Found

**Check wiring:**
- VIN → Pi 3.3V or 5V
- GND → Pi GND
- SCL → GPIO 3
- SDA → GPIO 2

**Check I2C scan:**
```bash
sudo i2cdetect -y 1
```

Should show device at 0x29.

**Try mock mode:**
If sensor not connected, app runs in mock mode with simulated values.

### Python Package Errors

**Ubuntu 24.04+ externally-managed-environment error:**
```bash
# Use virtual environment
cd ~/openreef/firmware/open_colorimeter_pi
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Service Won't Start

**Check service status:**
```bash
sudo systemctl status colorimeter
```

**View error logs:**
```bash
sudo journalctl -u colorimeter -n 50
```

**Common issues:**
- Wrong Python path in service file
- Virtual environment not activated
- Missing dependencies
- Permission errors

**Reinstall service:**
```bash
./uninstall_service.sh
./install_service.sh
```

---

## Next Steps

1. **Calibrate System:**
   - See [Calibration Guide](../calibration/calibration-guide.md)
   - Create standards
   - Build calibration curves

2. **Create Sequences:**
   - Design automated test protocols
   - Save frequently-used sequences
   - Share with team

3. **Run Tests:**
   - Use web interface for measurements
   - Monitor from any device
   - Log data

---

## Additional Resources

- **[Full Documentation](../../firmware/open_colorimeter_pi/README.md)** - Complete Pi guide
- **[Hardware Guide](../hardware/raspberry-pi.md)** - Parts list and assembly
- **[API Documentation](../../firmware/open_colorimeter_pi/README.md#api-endpoints)** - REST API reference
- **[GitHub Issues](https://github.com/thetemplateblog/openreef/issues)** - Report problems

---

## Quick Reference

### Common Commands

```bash
# First-time setup
./install_service.sh

# Update application
./update.sh

# Service management
sudo systemctl status colorimeter
sudo systemctl restart colorimeter
sudo journalctl -u colorimeter -f

# Manual run (with venv)
source venv/bin/activate
python app.py

# Check I2C devices
sudo i2cdetect -y 1

# Find Pi IP address
hostname -I
```

### Web Interface

- **URL:** `http://raspberrypi.local:5000` or `http://[IP]:5000`
- **Tabs:** Measure, Motors, Solenoids, Sequences, Calibrations, Config
- **Config Files:** Edit mappings, sequences, calibrations via web UI

---

**Setup complete!** Your Raspberry Pi colorimeter is ready to use. 🎉
