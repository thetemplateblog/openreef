#!/bin/bash
# Update script for Open Colorimeter

set -e

echo "======================================"
echo "Open Colorimeter Updater"
echo "======================================"
echo ""

# Get current directory
INSTALL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$INSTALL_DIR"

echo "Pulling latest changes from git..."
git pull

echo ""
echo "Checking for new dependencies..."
if [ -d "venv" ]; then
    echo "Using virtual environment..."
    source venv/bin/activate
    pip install -r requirements.txt
else
    echo "Using system Python..."
    pip3 install -r requirements.txt
fi

echo ""
echo "Restarting service..."
if systemctl is-active --quiet colorimeter; then
    sudo systemctl restart colorimeter
    echo "✓ Service restarted"
else
    echo "⚠ Service not running (use ./install_service.sh to install)"
fi

echo ""
echo "======================================"
echo "Update Complete!"
echo "======================================"
echo ""
echo "Check status: sudo systemctl status colorimeter"
echo "View logs:    sudo journalctl -u colorimeter -f"
echo ""
