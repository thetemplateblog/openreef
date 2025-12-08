#!/bin/bash
# Uninstaller for Open Colorimeter service

set -e

echo "======================================"
echo "Open Colorimeter Service Uninstaller"
echo "======================================"
echo ""

# Check if service exists
if [ ! -f "/etc/systemd/system/colorimeter.service" ]; then
    echo "⚠ Service not installed"
    exit 0
fi

echo "Stopping service..."
sudo systemctl stop colorimeter

echo "Disabling service..."
sudo systemctl disable colorimeter

echo "Removing service file..."
sudo rm /etc/systemd/system/colorimeter.service

echo "Reloading systemd..."
sudo systemctl daemon-reload

echo ""
echo "======================================"
echo "Service Uninstalled Successfully"
echo "======================================"
echo ""
echo "The application files are still in:"
echo "  $(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo ""
echo "To run manually: python3 app.py"
echo ""
