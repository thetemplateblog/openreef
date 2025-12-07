#!/bin/bash
# Start the Open Colorimeter web interface

echo "Starting Open Colorimeter Web Interface..."
echo ""
echo "Make sure you have installed dependencies:"
echo "  pip3 install -r requirements.txt"
echo ""
echo "Access the interface at:"
echo "  http://raspberrypi.local:5000"
echo "  or http://$(hostname -I | awk '{print $1}'):5000"
echo ""

python3 app.py
