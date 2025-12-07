# Open Colorimeter - Raspberry Pi Web Version

Web-based colorimeter using Raspberry Pi with CircuitPython (Blinka) for hardware control.

## Features
- Web interface - access from any device on your network
- Real-time sensor readings
- Motor control
- Calibration management
- No physical display or keyboard required

## Hardware Requirements
- Raspberry Pi (3/4/5 recommended)
- TSL2591 light sensor (I2C)
- PCA9685 motor controller (I2C)
- LEDs for illumination

## Setup

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
```bash
pip3 install -r requirements.txt
```

### 5. Verify I2C Devices
```bash
# Check that sensor and motor controller are detected
sudo i2cdetect -y 1

# Should show:
#   0x29 (TSL2591 sensor)
#   0x60 (PCA9685 motor controller)
```

### 6. Run the Application
```bash
./start.sh
# or
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
```bash
# Upgrade pip first
pip3 install --upgrade pip

# Install project dependencies
pip3 install -r requirements.txt
```

### 5. Verify I2C Devices
```bash
# Check available I2C buses
ls /dev/i2c-*

# Scan for devices (usually bus 1 on Pi, may vary on other boards)
sudo i2cdetect -y 1

# Should show:
#   0x29 (TSL2591 sensor)
#   0x60 (PCA9685 motor controller)

# If not on bus 1, try bus 0 or other buses
sudo i2cdetect -y 0
```

### 6. Run the Application
```bash
./start.sh
# or
python3 app.py
```

### 7. Access Web Interface
Open browser to: `http://<your-server-ip>:5000`
Example: `http://192.168.1.100:5000`

---

## Optional: Auto-start on Boot

### Create systemd service (works on both Raspberry Pi OS and Ubuntu)

```bash
sudo nano /etc/systemd/system/colorimeter.service
```

Add this content:
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
# Stop service
sudo systemctl stop colorimeter

# Restart service
sudo systemctl restart colorimeter

# Disable auto-start
sudo systemctl disable colorimeter
```

## Usage
- Navigate to the web interface
- Take measurements with the "Measure" button
- Control motors from the Motors tab
- Manage calibrations in the Calibrations tab
