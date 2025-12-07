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
    from adafruit_pca9685 import PCA9685
    from adafruit_motor import motor
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
        self.calibrations = {}

        if not MOCK_MODE:
            self._init_hardware()
        else:
            print("Mock mode - no hardware initialization")

        self._load_calibrations()

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
                self.pca = PCA9685(i2c, address=0x60)
                self.pca.frequency = 1600
                self.motors = {}
                self.motor_connected = True
                print("PCA9685 motor controller initialized")
            except Exception as e:
                print(f"Motor controller not found: {e}")
                self.pca = None

        except Exception as e:
            print(f"I2C initialization failed: {e}")

    def _load_calibrations(self):
        """Load calibrations from JSON file"""
        try:
            with open('calibrations.json', 'r') as f:
                self.calibrations = json.load(f)
            print(f"Loaded {len(self.calibrations)} calibrations")
        except FileNotFoundError:
            print("No calibrations.json found - using empty calibrations")
            self.calibrations = {}

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

    def _init_motor(self, motor_num):
        """Initialize a specific motor"""
        if MOCK_MODE or not self.pca:
            return None

        if motor_num in self.motors:
            return self.motors[motor_num]

        # Motor channel mappings on PCA9685
        channels = {
            1: {'pwm': 8, 'in1': 9, 'in2': 10},
            2: {'pwm': 13, 'in1': 12, 'in2': 11},
            3: {'pwm': 2, 'in1': 3, 'in2': 4},
            4: {'pwm': 7, 'in1': 6, 'in2': 5},
        }

        if motor_num not in channels:
            raise ValueError(f"Motor number must be 1-4, got {motor_num}")

        ch = channels[motor_num]
        self.motors[motor_num] = motor.DCMotor(
            self.pca.channels[ch['in1']],
            self.pca.channels[ch['in2']]
        )
        return self.motors[motor_num]

    def set_motor_throttle(self, motor_num, throttle):
        """Set motor speed (-1.0 to 1.0)"""
        if MOCK_MODE:
            print(f"Mock: Motor {motor_num} throttle = {throttle}")
            return

        m = self._init_motor(motor_num)
        if m:
            throttle = max(-1.0, min(1.0, throttle))
            m.throttle = throttle

    def stop_motor(self, motor_num):
        """Stop a motor"""
        self.set_motor_throttle(motor_num, 0)

    def cleanup(self):
        """Cleanup hardware"""
        if not MOCK_MODE and self.pca:
            for motor_num in self.motors:
                self.stop_motor(motor_num)
            self.pca.deinit()
