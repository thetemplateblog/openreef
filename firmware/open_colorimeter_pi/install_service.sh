#!/bin/bash
# Automated service installer for Open Colorimeter

set -e

echo "======================================"
echo "Open Colorimeter Service Installer"
echo "======================================"
echo ""

# Get current directory
INSTALL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "Install directory: $INSTALL_DIR"

# Get current user
CURRENT_USER=$(whoami)
echo "Running as user: $CURRENT_USER"

# Check if virtual environment exists
if [ -d "$INSTALL_DIR/venv" ]; then
    echo "✓ Virtual environment found"
    USE_VENV=true
else
    echo "⚠ No virtual environment found"
    echo "  Consider creating one: python3 -m venv venv"
    USE_VENV=false
fi

echo ""
echo "Creating systemd service file..."

# Create service file
SERVICE_FILE="/tmp/colorimeter.service"

if [ "$USE_VENV" = true ]; then
    cat > "$SERVICE_FILE" <<EOF
[Unit]
Description=Open Colorimeter Web Interface
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$INSTALL_DIR
ExecStart=/bin/bash -c 'source $INSTALL_DIR/venv/bin/activate && python app.py'
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    echo "✓ Service configured to use virtual environment"
else
    cat > "$SERVICE_FILE" <<EOF
[Unit]
Description=Open Colorimeter Web Interface
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$INSTALL_DIR
ExecStart=/usr/bin/python3 $INSTALL_DIR/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    echo "✓ Service configured to use system Python"
fi

echo ""
echo "Installing service..."
sudo cp "$SERVICE_FILE" /etc/systemd/system/colorimeter.service
sudo systemctl daemon-reload

echo ""
echo "Enabling service to start on boot..."
sudo systemctl enable colorimeter

echo ""
echo "Starting service..."
sudo systemctl start colorimeter

echo ""
echo "======================================"
echo "Installation Complete!"
echo "======================================"
echo ""
echo "Service commands:"
echo "  Status:  sudo systemctl status colorimeter"
echo "  Stop:    sudo systemctl stop colorimeter"
echo "  Restart: sudo systemctl restart colorimeter"
echo "  Logs:    sudo journalctl -u colorimeter -f"
echo ""
echo "Web interface should be available at:"
echo "  http://$(hostname).local:5000"
echo "  http://$(hostname -I | awk '{print $1}'):5000"
echo ""
