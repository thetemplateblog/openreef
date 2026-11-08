#!/usr/bin/env bash
# One-shot install on Raspberry Pi OS (Bookworm, 64-bit). Run from the firmware/openreef_analyzer directory.
set -euo pipefail
sudo apt-get update
sudo apt-get install -y python3-venv python3-dev i2c-tools pigpio git
sudo raspi-config nonint do_i2c 0
grep -q '^dtoverlay=w1-gpio' /boot/firmware/config.txt 2>/dev/null || echo 'dtoverlay=w1-gpio,gpiopin=4' | sudo tee -a /boot/firmware/config.txt
sudo systemctl enable --now pigpiod
sudo mkdir -p /opt/openreef /etc/openreef
sudo chown -R "$USER" /opt/openreef
rsync -a --exclude .venv ./ /opt/openreef/
cd /opt/openreef
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -e ".[rpi,mqtt]"
[ -f /etc/openreef/config.yaml ] || sudo cp config.example.yaml /etc/openreef/config.yaml
sudo sed -i 's/^  backend: sim/  backend: rpi/' /etc/openreef/config.yaml
sudo sed -i "s/^User=pi/User=$USER/" deploy/openreef.service
sudo cp deploy/openreef.service /etc/systemd/system/openreef.service
sudo systemctl daemon-reload
sudo systemctl enable --now openreef
echo "OpenReef running: http://$(hostname -I | awk '{print $1}'):8080  (edit /etc/openreef/config.yaml, then: sudo systemctl restart openreef)"
