#!/bin/bash
# Start the Open Colorimeter web interface

# Check if virtual environment exists, activate if it does
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

echo "Starting Open Colorimeter Web Interface..."
echo ""
echo "Access the interface at:"
echo "  http://raspberrypi.local:5000"
echo "  or http://$(hostname -I | awk '{print $1}'):5000"
echo ""

python3 app.py
