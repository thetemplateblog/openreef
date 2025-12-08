"""
Colorimeter hardware control using CircuitPython (Blinka)
"""

import time
import json
import numpy as np

try:
    import board
    import busio
    import adafruit_tsl2591
    from adafruit_motorkit import MotorKit
    from adafruit_mcp230xx.mcp23017 import MCP23017
    MOCK_MODE = False
except (ImportError, NotImplementedError) as e:
    print(f"Hardware libraries not available: {e}")
    print("Running in MOCK mode")
    MOCK_MODE = True


class Colorimeter:
    """Main colorimeter class for sensor and motor control"""

    NUM_BLANK_SAMPLES = 10
    BLANK_DT = 0.1  # seconds between blank samples

    def __init__(self):
        self.is_blanked = False
        self.blank_value = 1.0
        self.sensor_connected = False
        self.motor_connected = False
        self.solenoid_connected = False
        self.calibrations = {}
        self.mappings = {}
        self.sequences = {}
        self.solenoids = {}  # Track solenoid pin objects

        if not MOCK_MODE:
            self._init_hardware()
        else:
            print("Mock mode - no hardware initialization")

        self._load_calibrations()
        self._load_mappings()
        self._load_sequences()

    def _init_hardware(self):
        """Initialize I2C devices"""
        try:
            # Initialize I2C bus
            i2c = busio.I2C(board.SCL, board.SDA)

            # Initialize light sensor
            try:
                self.sensor = adafruit_tsl2591.TSL2591(i2c)
                self.sensor.gain = adafruit_tsl2591.GAIN_MED
                self.sensor.integration_time = adafruit_tsl2591.INTEGRATIONTIME_500MS
                self.sensor_connected = True
                print("TSL2591 sensor initialized")
            except Exception as e:
                print(f"Light sensor not found: {e}")
                self.sensor = None

            # Initialize motor controller
            try:
                self.kit = MotorKit()
                self.motor_connected = True
                print("Motor HAT (MotorKit) initialized")
            except Exception as e:
                print(f"Motor controller not found: {e}")
                self.kit = None

            # Initialize solenoid driver (MCP23017)
            try:
                self.mcp = MCP23017(i2c, address=0x20)
                # Initialize all 8 solenoid pins as outputs (off by default)
                for i in range(8):
                    pin = self.mcp.get_pin(i)
                    pin.switch_to_output(value=False)
                    self.solenoids[i + 1] = pin  # Solenoids numbered 1-8
                self.solenoid_connected = True
                print("Solenoid driver (MCP23017) initialized - 8 channels")
            except Exception as e:
                print(f"Solenoid driver not found: {e}")
                self.mcp = None

        except Exception as e:
            print(f"I2C initialization failed: {e}")

    def _load_calibrations(self):
        """Load calibrations from JSON file"""
        try:
            with open('calibrations.json', 'r') as f:
                self.calibrations = json.load(f)
            print(f"Loaded {len(self.calibrations)} calibrations")
        except FileNotFoundError:
            # Load from template
            try:
                with open('calibrations_templates.json', 'r') as f:
                    self.calibrations = json.load(f)
                print(f"No calibrations.json found - loaded {len(self.calibrations)} from template")
            except FileNotFoundError:
                print("No calibrations template found - using empty calibrations")
                self.calibrations = {}

    def _load_mappings(self):
        """Load device mappings (names, descriptions)"""
        try:
            with open('mappings.json', 'r') as f:
                self.mappings = json.load(f)
            print(f"Loaded mappings")
        except FileNotFoundError:
            # Load from template
            try:
                with open('mappings_templates.json', 'r') as f:
                    self.mappings = json.load(f)
                print("No mappings.json found - loaded from template")
            except FileNotFoundError:
                print("No mappings template found - using empty defaults")
                self.mappings = {}

    def _load_sequences(self):
        """Load saved sequences and merge with templates"""
        # Load templates first
        templates = {}
        try:
            with open('sequences_templates.json', 'r') as f:
                templates = json.load(f)
            print(f"Loaded {len(templates)} sequence templates")
        except FileNotFoundError:
            print("No sequences_templates.json found")

        # Load user sequences
        user_sequences = {}
        try:
            with open('sequences.json', 'r') as f:
                user_sequences = json.load(f)
            print(f"Loaded {len(user_sequences)} user sequences")
        except FileNotFoundError:
            print("No sequences.json found - creating empty file")
            user_sequences = {}

        # Merge: templates first, then user sequences (user sequences can't override templates)
        self.sequences = {**templates, **user_sequences}
        print(f"Total sequences available: {len(self.sequences)}")

    def get_raw_sensor_value(self):
        """Read raw sensor value"""
        if MOCK_MODE or not self.sensor:
            return np.random.randint(20000, 40000)

        try:
            # Read channel 0 (visible + IR)
            value = self.sensor.raw_luminosity[0]
            return value
        except Exception as e:
            raise Exception(f"Sensor read error: {e}")

    def get_transmittance(self):
        """Calculate transmittance"""
        raw = self.get_raw_sensor_value()
        return float(raw) / self.blank_value

    def get_absorbance(self):
        """Calculate absorbance"""
        transmittance = self.get_transmittance()
        absorbance = -np.log10(transmittance)
        return max(0.0, absorbance)

    def blank_sensor(self):
        """Blank the sensor by averaging multiple readings"""
        samples = []
        for _ in range(self.NUM_BLANK_SAMPLES):
            samples.append(self.get_raw_sensor_value())
            time.sleep(self.BLANK_DT)

        self.blank_value = np.median(samples)
        self.is_blanked = True
        print(f"Sensor blanked: {self.blank_value}")

    def apply_calibration(self, cal_name, absorbance):
        """Apply calibration curve to absorbance value"""
        if cal_name not in self.calibrations:
            return None

        cal = self.calibrations[cal_name]
        fit_type = cal.get('fit_type', 'polynomial')
        coef = cal.get('fit_coef', [0, 1, 0])

        if fit_type == 'polynomial':
            # polynomial: c0 + c1*x + c2*x^2
            value = coef[0] + coef[1] * absorbance + coef[2] * absorbance**2
            return value

        return None

    def get_measurement(self):
        """Get current measurement with all values"""
        try:
            raw = self.get_raw_sensor_value()
            transmittance = self.get_transmittance()
            absorbance = self.get_absorbance()

            # Apply all calibrations
            calibrated_values = {}
            for cal_name in self.calibrations:
                value = self.apply_calibration(cal_name, absorbance)
                if value is not None:
                    calibrated_values[cal_name] = {
                        'value': round(value, 4),
                        'units': self.calibrations[cal_name].get('units', '')
                    }

            return {
                'raw': raw,
                'transmittance': round(transmittance, 4),
                'absorbance': round(absorbance, 4),
                'calibrated': calibrated_values,
                'is_blanked': self.is_blanked,
                'blank_value': self.blank_value
            }
        except Exception as e:
            raise Exception(f"Measurement error: {e}")

    def get_calibrations(self):
        """Get list of available calibrations"""
        cal_list = []
        for name, cal in self.calibrations.items():
            cal_list.append({
                'name': name,
                'units': cal.get('units', ''),
                'led': cal.get('led', ''),
                'range': cal.get('range', {})
            })
        return cal_list

    def get_mappings(self):
        """Get device mappings"""
        return self.mappings

    def get_sequences(self):
        """Get saved sequences"""
        return self.sequences

    def _get_motor(self, motor_num):
        """Get motor object by number"""
        if motor_num == 1:
            return self.kit.motor1
        elif motor_num == 2:
            return self.kit.motor2
        elif motor_num == 3:
            return self.kit.motor3
        elif motor_num == 4:
            return self.kit.motor4
        else:
            raise ValueError(f"Motor number must be 1-4, got {motor_num}")

    def set_motor_throttle(self, motor_num, throttle):
        """Set motor speed (-1.0 to 1.0)"""
        if MOCK_MODE:
            print(f"Mock: Motor {motor_num} throttle = {throttle}")
            return

        if not self.kit:
            print(f"Motor controller not available")
            return

        try:
            motor = self._get_motor(motor_num)
            throttle = max(-1.0, min(1.0, throttle))
            motor.throttle = throttle
            print(f"Motor {motor_num} set to throttle {throttle}")
        except Exception as e:
            print(f"Error setting motor {motor_num} throttle: {e}")

    def stop_motor(self, motor_num):
        """Stop a motor"""
        self.set_motor_throttle(motor_num, 0)

    def set_solenoid(self, solenoid_num, state):
        """Set solenoid state (True=on, False=off)"""
        if MOCK_MODE:
            print(f"Mock: Solenoid {solenoid_num} set to {state}")
            return

        if not self.mcp:
            print(f"Solenoid driver not available")
            return

        if solenoid_num not in range(1, 9):
            print(f"Solenoid number must be 1-8, got {solenoid_num}")
            return

        try:
            self.solenoids[solenoid_num].value = state
            state_str = "ON" if state else "OFF"
            print(f"Solenoid {solenoid_num} set to {state_str}")
        except Exception as e:
            print(f"Error setting solenoid {solenoid_num}: {e}")

    def get_solenoid_state(self, solenoid_num):
        """Get current solenoid state"""
        if MOCK_MODE or not self.mcp:
            return False

        if solenoid_num not in range(1, 9):
            return False

        try:
            return self.solenoids[solenoid_num].value
        except Exception as e:
            print(f"Error reading solenoid {solenoid_num}: {e}")
            return False

    def cleanup(self):
        """Cleanup hardware"""
        if not MOCK_MODE and self.kit:
            try:
                self.kit.motor1.throttle = 0
                self.kit.motor2.throttle = 0
                self.kit.motor3.throttle = 0
                self.kit.motor4.throttle = 0
            except:
                pass

        if not MOCK_MODE and self.mcp:
            try:
                # Turn off all solenoids
                for i in range(1, 9):
                    self.set_solenoid(i, False)
            except:
                pass
