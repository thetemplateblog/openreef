#!/usr/bin/env python3
"""
Open Colorimeter - Raspberry Pi Web Interface
Web-based colorimeter control and monitoring
"""

from flask import Flask, render_template, jsonify, request
import json
import os
from colorimeter import Colorimeter

app = Flask(__name__)
colorimeter = Colorimeter()

@app.route('/')
def index():
    """Main web interface"""
    return render_template('index.html')

@app.route('/api/measure', methods=['GET'])
def measure():
    """Get current sensor reading"""
    try:
        data = colorimeter.get_measurement()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/blank', methods=['POST'])
def blank():
    """Blank the sensor"""
    try:
        colorimeter.blank_sensor()
        return jsonify({'success': True, 'blank_value': colorimeter.blank_value})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/calibrations', methods=['GET'])
def get_calibrations():
    """Get available calibrations"""
    try:
        cals = colorimeter.get_calibrations()
        return jsonify(cals)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/motor/<int:motor_num>/throttle', methods=['POST'])
def set_motor_throttle(motor_num):
    """Set motor speed and direction"""
    try:
        data = request.get_json()
        throttle = float(data.get('throttle', 0))
        colorimeter.set_motor_throttle(motor_num, throttle)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/motor/<int:motor_num>/stop', methods=['POST'])
def stop_motor(motor_num):
    """Stop a motor"""
    try:
        colorimeter.stop_motor(motor_num)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get system status"""
    try:
        status = {
            'is_blanked': colorimeter.is_blanked,
            'blank_value': colorimeter.blank_value,
            'sensor_connected': colorimeter.sensor_connected,
            'motor_connected': colorimeter.motor_connected
        }
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting Open Colorimeter Web Interface")
    print("Access at: http://raspberrypi.local:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
