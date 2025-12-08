# Open Colorimeter - Raspberry Pi Web Version

Web-based colorimeter using Raspberry Pi with CircuitPython (Blinka) for hardware control.

## Table of Contents
- [Quick Start Workflow](#quick-start-workflow)
- [Features](#features)
- [Hardware Requirements](#hardware-requirements)
- [Hardware Setup](#hardware-setup)
- [Software Setup](#software-setup)
  - [Raspberry Pi OS Setup](#raspberry-pi-os-setup)
  - [Ubuntu Server Setup](#ubuntu-server-setup)
- [Auto-start on Boot](#optional-auto-start-on-boot)
- [Updating the Application](#updating-the-application)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Command Sequences](#command-sequences)
- [Project Files](#project-files)
- [Troubleshooting](#troubleshooting)
- [Quick Reference](#quick-reference)
- [Support](#support)

---

## Quick Start Workflow

**Initial Setup (one time):**
1. Clone repository to Raspberry Pi
2. Install dependencies: `pip install -r requirements.txt`
3. Install service: `./install_service.sh`

**Development Workflow:**
1. Make changes on your development machine
2. Commit and push: `git commit -am "message" && git push`
3. On Raspberry Pi: `./update.sh`

Done! The service automatically restarts with your changes.

---

## Features

**Hardware Control:**
- 4-channel DC motor control (Adafruit Motor HAT)
- 8-channel solenoid valve control (MCP23017)
- TSL2591 light sensor for absorbance measurements
- Multiplexer support for multiple sensors (future)

**Web Interface:**
- Access from any device on your network
- Real-time sensor readings (raw, transmittance, absorbance)
- Interactive motor and solenoid controls
- Visual status indicators for all hardware
- Built-in JSON editors for configuration files
- No SSH required for configuration changes

**Automation:**
- Command sequences for automated testing
- Mix motors, solenoids, waits, blanking, and measurements
- Save and load multiple named sequences
- Real-time progress monitoring
- Named tests with sensor/calibration mapping
- Share sequences via JSON configuration

**Calibration & Testing:**
- Multiple calibration curves support
- Named test configurations (e.g., Phosphate, Nitrate)
- Automatic sensor switching via multiplexer (when configured)
- JSON-based calibration storage

**Deployment:**
- Automated service installation scripts
- One-command updates via git pull
- Virtual environment support
- Auto-restart on boot
- No physical display or keyboard required

## Hardware Requirements
- Raspberry Pi (3/4/5 recommended)
- TSL2591 light sensor (I2C)
- Adafruit DC & Stepper Motor HAT for Raspberry Pi (Product #2348)
- 2-4 DC motors (4.5V-13.5V, <1.2A continuous)
- 12V power supply for motors
- Adafruit I2C 8-Channel Solenoid Driver (MCP23017, optional)
- Solenoid valves (12V recommended, optional)
- LEDs for illumination

## Hardware Setup

### Motor HAT Installation

1. **Stack the Motor HAT**
   - Power off your Raspberry Pi
   - Align the Motor HAT with the 40-pin GPIO header
   - Press firmly to seat all pins
   - The HAT should sit flush on top of the Pi

2. **Connect Power**
   - Connect your 12V power supply to the green terminal block on the Motor HAT
   - **Polarity**: + (positive) and - (negative/ground)
   - **Important**: Motor power is separate from Pi power - don't connect 12V to Pi!

3. **Connect Motors**
   - Connect your DC motors to the blue terminal blocks:
     - **M1**: Motor 1 (appears as "Motor 1" in web interface)
     - **M2**: Motor 2 (appears as "Motor 2" in web interface)
     - **M3**: Motor 3 (optional)
     - **M4**: Motor 4 (optional)
   - Motor wire polarity determines direction (can swap if backwards)

4. **Connect Sensor (Optional)**
   - TSL2591 light sensor connects via I2C:
     - **VIN** → Pi 3.3V or 5V
     - **GND** → Pi GND
     - **SCL** → Pi SCL (GPIO 3)
     - **SDA** → Pi SDA (GPIO 2)
   - Can use breadboard or direct wiring

5. **Connect Solenoid Driver (Optional)**
   - Adafruit I2C 8-Channel Solenoid Driver connects via I2C:
     - **VIN** → Pi 3.3V or 5V
     - **GND** → Pi GND
     - **SCL** → Pi SCL (GPIO 3)
     - **SDA** → Pi SDA (GPIO 2)
   - Connect 12V power supply to driver's power input
   - Connect solenoid valves to channels 1-8
   - All I2C devices share the same SCL/SDA bus

6. **Connect Sensor Multiplexer (Optional)**
   - For multiple sensors, connect I2C multiplexer (e.g., TCA9548A)
   - Each sensor gets its own multiplexer channel
   - Configure test-to-sensor mapping in `mappings.json`
   - System will automatically switch sensors based on test being run

### I2C Addresses
- **Motor HAT (PCA9685)**: 0x60 (default)
- **Motor HAT (PWM)**: 0x70 (auxiliary chip)
- **TSL2591 Sensor**: 0x29 (default)
- **Solenoid Driver (MCP23017)**: 0x20 (default)
- **Sensor Multiplexer (TCA9548A)**: 0x70 (configurable to avoid conflicts)

---

## Software Setup

Choose your platform:
- [Raspberry Pi OS Setup](#raspberry-pi-os-setup)
- [Ubuntu Server Setup](#ubuntu-server-setup)

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
# Navigate to: Interface Options → I2C → Enable
# Reboot
sudo reboot
```

### 3. Clone/Copy Project Files
```bash
# Option A: Clone from git
git clone <your-repo-url>
cd open_colorimeter_pi

# Option B: Copy files manually
# scp -r /path/to/open_colorimeter_pi pi@raspberrypi.local:~/
```

### 4. Install Python Dependencies

**Option A: Using Virtual Environment (Recommended)**
```bash
# Install venv support
sudo apt install python3-venv

# Create virtual environment
cd ~/open_colorimeter_pi
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Option B: System-wide Installation**
```bash
pip3 install -r requirements.txt
```

### 5. Verify I2C Devices
```bash
# Check that sensor and motor controller are detected
sudo i2cdetect -y 1

# Should show:
#   0x20 (Solenoid driver - MCP23017) - if connected
#   0x29 (TSL2591 sensor) - if connected
#   0x60 (Motor HAT - PCA9685)
#   0x70 (Motor HAT - additional chip)
#
# Example output with all devices:
#      0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
# 00:          -- -- -- -- -- -- -- -- -- -- -- -- --
# 10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
# 20: 20 -- -- -- -- -- -- -- -- 29 -- -- -- -- -- --
# 30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
# 40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
# 50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
# 60: 60 -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
# 70: 70 -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
```

### 6. Run the Application

**If using virtual environment:**
```bash
# The start.sh script will automatically activate venv if it exists
./start.sh

# Or manually:
source venv/bin/activate
python app.py
```

**If installed system-wide:**
```bash
python3 app.py
```

### 7. Access Web Interface
Open browser to: `http://raspberrypi.local:5000`
Or use the Pi's IP address: `http://192.168.1.XXX:5000`

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
# Load I2C kernel modules
sudo modprobe i2c-dev

# Make I2C load on boot
echo "i2c-dev" | sudo tee -a /etc/modules

# Add user to i2c group for permissions
sudo usermod -aG i2c $USER

# If i2c group doesn't exist, create it
sudo groupadd -f i2c

# Set I2C device permissions
echo 'KERNEL=="i2c-[0-9]*", GROUP="i2c", MODE="0660"' | sudo tee /etc/udev/rules.d/99-i2c.rules

# Reload udev rules
sudo udevadm control --reload-rules
sudo udevadm trigger

# Reboot to apply changes
sudo reboot
```

### 3. Clone/Copy Project Files
```bash
# Clone from git
git clone <your-repo-url>
cd open_colorimeter_pi

# Or copy files via scp, etc.
```

### 4. Install Python Dependencies

**Option A: Using Virtual Environment (Recommended for Ubuntu 24.04+)**
```bash
# Install venv support
sudo apt install python3-venv python3-full

# Create virtual environment
cd ~/open_colorimeter_pi
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

**Option B: System-wide Installation (may require --break-system-packages on newer Ubuntu)**
```bash
# Upgrade pip first
pip3 install --upgrade pip

# Install project dependencies
pip3 install -r requirements.txt
```

**Note:** Ubuntu 24.04+ uses Python 3.13 which enforces PEP 668 (externally managed environments). Virtual environments are strongly recommended.

### 5. Verify I2C Devices
```bash
# Check available I2C buses
ls /dev/i2c-*

# Scan for devices (usually bus 1 on Pi, may vary on other boards)
sudo i2cdetect -y 1

# Should show:
#   0x20 (Solenoid driver - MCP23017) - if connected
#   0x29 (TSL2591 sensor) - if connected
#   0x60 (Motor HAT - PCA9685)
#   0x70 (Motor HAT - additional chip)
#
# Example output with all devices:
#      0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
# 00:          -- -- -- -- -- -- -- -- -- -- -- -- --
# 10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
# 20: 20 -- -- -- -- -- -- -- -- 29 -- -- -- -- -- --
# 30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
# 40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
# 50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
# 60: 60 -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
# 70: 70 -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

# If not on bus 1, try bus 0 or other buses
sudo i2cdetect -y 0
```

### 6. Run the Application

**If using virtual environment:**
```bash
# The start.sh script will automatically activate venv if it exists
./start.sh

# Or manually:
source venv/bin/activate
python app.py
```

**If installed system-wide:**
```bash
python3 app.py
```

### 7. Access Web Interface
Open browser to: `http://<your-server-ip>:5000`
Example: `http://192.168.1.100:5000`

---

## Optional: Auto-start on Boot

### Automated Installation (Recommended)

Use the provided installation script to automatically set up the service:

```bash
cd ~/open_colorimeter_pi
./install_service.sh
```

The script will:
- Detect if you're using a virtual environment
- Create the systemd service file with correct paths
- Enable and start the service automatically
- Show you the web interface URLs

**That's it!** The service is now running and will start automatically on boot.

---

### Manual Installation (Alternative)

If you prefer to set up the service manually:

#### Create systemd service (works on both Raspberry Pi OS and Ubuntu)

```bash
sudo nano /etc/systemd/system/colorimeter.service
```

Add this content:

**If using virtual environment:**
```ini
[Unit]
Description=Open Colorimeter Web Interface
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/open_colorimeter_pi
ExecStart=/bin/bash -c 'source /home/pi/open_colorimeter_pi/venv/bin/activate && python app.py'
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**If using system Python:**
```ini
[Unit]
Description=Open Colorimeter Web Interface
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/open_colorimeter_pi
ExecStart=/usr/bin/python3 /home/pi/open_colorimeter_pi/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Note:** Change `User=pi` and paths if your username or install location is different.

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable colorimeter
sudo systemctl start colorimeter

# Check status
sudo systemctl status colorimeter

# View logs
sudo journalctl -u colorimeter -f
```

### Service Management Commands
```bash
# Check status
sudo systemctl status colorimeter

# View logs
sudo journalctl -u colorimeter -f

# Stop service
sudo systemctl stop colorimeter

# Restart service
sudo systemctl restart colorimeter

# Disable auto-start
sudo systemctl disable colorimeter

# Uninstall service (automated)
./uninstall_service.sh

# Or manually remove service
sudo systemctl stop colorimeter
sudo systemctl disable colorimeter
sudo rm /etc/systemd/system/colorimeter.service
sudo systemctl daemon-reload
```

## Updating the Application

### Automated Update (Recommended)

When you push new changes to the repository, update your Raspberry Pi with:

```bash
cd ~/open_colorimeter_pi
./update.sh
```

The update script will:
- Pull latest changes from git
- Install any new dependencies
- Restart the service automatically

### Manual Update (Alternative)

```bash
cd ~/open_colorimeter_pi
git pull
pip install -r requirements.txt  # or: source venv/bin/activate && pip install -r requirements.txt
sudo systemctl restart colorimeter
```

---

## Configuration

### Device Names and Descriptions

You can customize the names and descriptions of motors, solenoids, and tests by editing `mappings.json`:

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
    },
    "Nitrate": {
      "sensor": 2,
      "calibration": "Nitrate"
    }
  }
}
```

**Test Configuration:**
- Each test maps to a sensor number (for multiplexer support)
- Specifies which calibration curve to use
- Test names can be used in sequences with `measure TestName`

### Web-Based Config Editor

You can edit all three configuration files directly from the web interface:

1. Go to the **Config** tab
2. Edit `mappings.json`, `sequences.json`, or `calibrations.json` in the text editors
3. Click the corresponding **Save** button for each file
4. The system validates JSON syntax before saving
5. Changes are applied immediately (device names may require page reload)

**Benefits:**
- No need to SSH into the Raspberry Pi
- Syntax validation prevents errors
- Edit all three files in one place
- Auto-formatted JSON with proper indentation
- Separate files for better organization

## Usage
- Navigate to the web interface
- Take measurements with the "Measure" button
- Control motors from the Motors tab
- Control solenoids from the Solenoids tab (8 channels)
- Create and save automated sequences in the Sequences tab
- Load saved sequences from the dropdown menu
- Manage calibrations in the Calibrations tab
- Edit configuration files in the Config tab (web-based JSON editor)
- Customize device names, test definitions, sequences, and calibration curves

### Command Sequences

The Sequences tab allows you to automate multiple device operations. Enter commands one per line:

**Motor Commands:**
```
Sample, 30        # Run Sample motor forward for 30 seconds
Reagent, -15      # Run Reagent motor reverse for 15 seconds
```

**Solenoid Commands:**
```
Solenoid 1, on    # Turn on Solenoid 1
Solenoid 1, off   # Turn off Solenoid 1
```

**Wait Commands:**
```
wait, 5           # Wait 5 seconds before next command
```

**Sensor Commands:**
```
blank                 # Blank the sensor (takes ~1 second)
measure Phosphate     # Take a measurement for specific test
measure Nitrate       # Measure different test (switches to configured sensor)
measure               # Measure all calibrations on current sensor
```

**Complete Example:**
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

**Multiple Tests Example:**
```
blank
measure Phosphate
wait, 5
blank
measure Nitrate
```

The sequence will execute each command in order, showing progress in real-time. When using `measure TestName`, the system will automatically use the sensor and calibration configured for that test (useful when you have a multiplexer with multiple sensors). Measurement results (absorbance and calibrated values) are displayed in the status log. Use the Stop button to cancel execution.

### Saved Sequences

Save frequently-used sequences for quick access:

1. **Create a sequence** - Type commands in the editor
2. **Click "Save As..."** - Give it a name and description
3. **Load anytime** - Select from dropdown and click "Load"
4. **Delete** - Select and click "Delete" to remove

**Saved sequences are stored in `sequences.json`:**
```json
{
  "sequences": {
    "Phosphate Test": {
      "description": "Full phosphate measurement cycle",
      "commands": [
        "Sample, 30",
        "Solenoid 1, on",
        "wait, 5",
        "Solenoid 1, off",
        "Reagent, -15",
        "wait, 10",
        "blank",
        "wait, 2",
        "measure Phosphate"
      ]
    },
    "Nitrate Test": {
      "description": "Nitrate test sequence",
      "commands": [
        "Sample, 25",
        "blank",
        "measure Nitrate"
      ]
    }
  }
}
```

This allows you to:
- Build a library of standard operating procedures
- Share sequences between team members
- Quickly switch between different test protocols
- Backup sequences in version control

---

## Project Files

**Core Application:**
- `app.py` - Flask web server and REST API endpoints
- `colorimeter.py` - Hardware control (sensor, motors, solenoids)
- `requirements.txt` - Python dependencies

**Configuration:**
- `mappings.json` - Device names, test definitions, sensor mappings
- `sequences.json` - Saved command sequences
- `calibrations.json` - Calibration curves for each test

**Web Interface:**
- `templates/index.html` - Main web page with tabs
- `static/style.css` - Styling (ocean blue theme)
- `static/script.js` - Interactive controls and sequence execution

**Automation Scripts:**
- `install_service.sh` - Automated systemd service installation
- `uninstall_service.sh` - Remove service
- `update.sh` - Pull changes and restart service
- `start.sh` - Manual start with venv support

**Example Configuration:**
```
open_colorimeter_pi/
├── app.py                    # Flask server
├── colorimeter.py            # Hardware control
├── mappings.json             # Device names & test mappings
├── sequences.json            # Saved command sequences
├── calibrations.json         # Calibration curves
├── requirements.txt          # Dependencies
├── install_service.sh        # Service installer
├── update.sh                 # Update script
├── templates/
│   └── index.html           # Web UI
└── static/
    ├── style.css            # Styles
    └── script.js            # Frontend logic
```

---

## Troubleshooting

### Motor HAT Not Detected (No 0x60 in i2cdetect)

**Check Physical Connection:**
```bash
# Power off Pi
sudo shutdown -h now

# Check that Motor HAT is properly seated on GPIO pins
# Reseat the HAT if necessary
# Power back on
```

**Check I2C is Enabled:**
```bash
# Raspberry Pi OS
sudo raspi-config
# Interface Options → I2C → Enable

# Ubuntu - check if i2c-dev module is loaded
lsmod | grep i2c
```

### Motors Not Running

**Check Power:**
- Verify 12V power supply is connected to Motor HAT green terminal
- Check polarity (+ and -)
- Motor power is separate from Pi power

**Check Motor Connections:**
- Motors connected to blue terminal blocks (M1, M2, etc.)
- Terminals are screw terminals - make sure wires are secure

**Test in Web Interface:**
- Go to Motors tab
- Move slider for Motor 1
- If motor doesn't move, try swapping motor wires (reverses direction)

### Web Interface Not Accessible

**Check Flask is Running:**
```bash
# Check if app is running
ps aux | grep python

# Check what's using port 5000
sudo netstat -tulpn | grep 5000
```

**Check Firewall (Ubuntu):**
```bash
sudo ufw status
sudo ufw allow 5000
```

**Access from Same Network:**
- Make sure your device is on the same WiFi/network as the Pi
- Try using Pi's IP address: `http://192.168.1.XXX:5000`
- Check Pi's IP: `hostname -I`

### Motor Direction is Backwards

Simply **swap the two motor wires** on the terminal block - this reverses the direction.

### Python Package Errors

**If using Ubuntu 24.04+ and getting externally-managed-environment error:**
```bash
# Use virtual environment (recommended)
cd ~/open_colorimeter_pi
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Quick Reference

**Common Commands:**
```bash
# First-time setup
./install_service.sh

# Update application
./update.sh

# Service management
sudo systemctl status colorimeter
sudo systemctl restart colorimeter
sudo journalctl -u colorimeter -f

# Manual run
source venv/bin/activate
python app.py
```

**Web Interface:**
- Local: `http://raspberrypi.local:5000`
- Network: `http://[PI_IP_ADDRESS]:5000`
- Find IP: `hostname -I`

**API Endpoints:**
- `GET /api/status` - System status
- `GET /api/measure` - Current measurement
- `POST /api/blank` - Blank sensor
- `GET /api/configuration` - Device configuration
- `GET /api/calibrations` - Available calibrations
- `GET /api/config/load` - Load config files for editing
- `POST /api/mappings/save` - Save mappings.json
- `POST /api/sequences/save` - Save sequences.json
- `POST /api/calibrations/save` - Save calibrations.json
- `POST /api/motor/<num>/throttle` - Control motor
- `POST /api/solenoid/<num>/set` - Control solenoid

**Configuration Files:**
- `mappings.json` - Device names and test definitions
- `sequences.json` - Saved command sequences
- `calibrations.json` - Calibration curves

---

## Support

For issues or questions:
- Check the [GitHub Issues](https://github.com/thetemplateblog/openreef/issues)
- Review the [Adafruit Motor HAT Guide](https://learn.adafruit.com/adafruit-dc-and-stepper-motor-hat-for-raspberry-pi)
- Review the [Adafruit Solenoid Driver Guide](https://learn.adafruit.com/adafruit-i2c-to-8-channel-solenoid-driver)
