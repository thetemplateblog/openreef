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

@app.route('/api/mappings', methods=['GET'])
def get_mappings():
    """Get device mappings (names, descriptions)"""
    try:
        mappings = colorimeter.get_mappings()
        return jsonify(mappings)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sequences', methods=['GET'])
def get_sequences():
    """Get saved sequences"""
    try:
        sequences = colorimeter.get_sequences()
        return jsonify(sequences)
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
            'motor_connected': colorimeter.motor_connected,
            'solenoid_connected': colorimeter.solenoid_connected
        }
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/solenoid/<int:solenoid_num>/set', methods=['POST'])
def set_solenoid(solenoid_num):
    """Set solenoid state (on/off)"""
    try:
        data = request.get_json()
        state = bool(data.get('state', False))
        colorimeter.set_solenoid(solenoid_num, state)
        return jsonify({'success': True, 'state': state})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/solenoid/<int:solenoid_num>/state', methods=['GET'])
def get_solenoid_state(solenoid_num):
    """Get current solenoid state"""
    try:
        state = colorimeter.get_solenoid_state(solenoid_num)
        return jsonify({'solenoid': solenoid_num, 'state': state})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/config/load', methods=['GET'])
def load_config_files():
    """Load all configuration files"""
    try:
        # Load mappings.json
        mappings_data = {}
        try:
            with open('mappings.json', 'r') as f:
                mappings_data = json.load(f)
        except FileNotFoundError:
            mappings_data = {}

        # Load sequences.json
        sequences_data = {}
        try:
            with open('sequences.json', 'r') as f:
                sequences_data = json.load(f)
        except FileNotFoundError:
            sequences_data = {}

        # Load calibrations.json
        calibrations_data = {}
        try:
            with open('calibrations.json', 'r') as f:
                calibrations_data = json.load(f)
        except FileNotFoundError:
            calibrations_data = {}

        return jsonify({
            'mappings': mappings_data,
            'sequences': sequences_data,
            'calibrations': calibrations_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/mappings/save', methods=['POST'])
def save_mappings_file():
    """Save mappings.json"""
    try:
        data = request.get_json()
        mappings_content = data.get('content', {})

        # Write to file with pretty printing
        with open('mappings.json', 'w') as f:
            json.dump(mappings_content, f, indent=2)

        # Reload mappings in colorimeter
        colorimeter._load_mappings()

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sequences/save', methods=['POST'])
def save_sequences_file():
    """Save sequences.json"""
    try:
        data = request.get_json()
        sequences_content = data.get('content', {})

        # Write to file with pretty printing
        with open('sequences.json', 'w') as f:
            json.dump(sequences_content, f, indent=2)

        # Reload sequences in colorimeter
        colorimeter._load_sequences()

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/calibrations/save', methods=['POST'])
def save_calibrations_file():
    """Save calibrations.json"""
    try:
        data = request.get_json()
        calibrations_content = data.get('content', {})

        # Write to file with pretty printing
        with open('calibrations.json', 'w') as f:
            json.dump(calibrations_content, f, indent=2)

        # Reload calibrations in colorimeter
        colorimeter._load_calibrations()

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting Open Colorimeter Web Interface")
    print("Access at: http://raspberrypi.local:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
