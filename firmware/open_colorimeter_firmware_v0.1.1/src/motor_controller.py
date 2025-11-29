"""
Motor Controller Module

Controls up to 4 DC motors via Adafruit DC Motor + Stepper FeatherWing
communicating over I2C using the PCA9685 PWM driver chip.

The FeatherWing is stacked on a separate Feather board and controlled
from the PyBadge via I2C commands.
"""

import board
import busio
from adafruit_pca9685 import PCA9685
from adafruit_motor import motor

class MotorControllerError(Exception):
    pass

class MotorController:
    """
    Controls DC motors via Adafruit Motor FeatherWing

    The FeatherWing uses a PCA9685 PWM driver chip at I2C address 0x60 (default)
    """

    DEFAULT_I2C_ADDRESS = 0x60
    DEFAULT_FREQUENCY = 1600  # PWM frequency for motor control

    # Motor channel mappings on PCA9685
    MOTOR_CHANNELS = {
        1: {'pwm': 8, 'in1': 9, 'in2': 10},   # Motor 1
        2: {'pwm': 13, 'in1': 12, 'in2': 11}, # Motor 2
        3: {'pwm': 2, 'in1': 3, 'in2': 4},    # Motor 3
        4: {'pwm': 7, 'in1': 6, 'in2': 5},    # Motor 4
    }

    def __init__(self, i2c_address=DEFAULT_I2C_ADDRESS, motor_num=None):
        """
        Initialize motor controller

        Args:
            i2c_address: I2C address of PCA9685 chip (default 0x60)
            motor_num: Optional - only initialize this specific motor (1-4) to save memory
        """
        self.i2c_address = i2c_address
        self._mock_mode = False

        try:
            # Initialize I2C bus
            i2c = board.I2C()

            # Initialize PCA9685 PWM driver
            self.pca = PCA9685(i2c, address=i2c_address)
            self.pca.frequency = self.DEFAULT_FREQUENCY

            # Create motor objects (uses adafruit_motor library)
            # If motor_num specified, only create that one motor to save memory
            self.motors = {}
            motor_numbers = [motor_num] if motor_num is not None else range(1, 5)

            for num in motor_numbers:
                channels = self.MOTOR_CHANNELS[num]
                try:
                    # Create motor using PWM channels
                    self.motors[num] = motor.DCMotor(
                        self.pca.channels[channels['in1']],
                        self.pca.channels[channels['in2']]
                    )
                    # Set decay mode for better control
                    self.motors[num].decay_mode = motor.SLOW_DECAY
                except Exception as e:
                    raise MotorControllerError(f"Failed to init motor {num}: {e}")

            # Stop all initialized motors
            for num in self.motors:
                self.stop(num)

        except (ValueError, OSError) as error:
            # Motor controller not found, run in mock mode
            self._mock_mode = True
            self.pca = None
            if motor_num is not None:
                self.motors = {motor_num: None}
            else:
                self.motors = {i: None for i in range(1, 5)}
            print(f"Motor controller running in mock mode: {error}")

    @property
    def mock_mode(self):
        """Returns True if running in mock mode (no hardware detected)"""
        return self._mock_mode

    def set_throttle(self, motor_num, throttle):
        """
        Set motor speed and direction

        Args:
            motor_num: Motor number (1-4)
            throttle: Speed/direction from -1.0 (full reverse) to 1.0 (full forward)
                     0 = stopped

        Raises:
            ValueError: If motor_num is not 1-4
            MotorControllerError: If motor control fails
        """
        if motor_num not in range(1, 5):
            raise ValueError(f"Motor number must be 1-4, got {motor_num}")

        if self._mock_mode:
            print(f"[MOCK] Motor {motor_num} throttle: {throttle:.2f}")
            return

        try:
            # Clamp throttle to valid range
            throttle = max(-1.0, min(1.0, throttle))
            self.motors[motor_num].throttle = throttle
        except Exception as e:
            raise MotorControllerError(f"Failed to set motor {motor_num} throttle: {e}")

    def stop(self, motor_num):
        """
        Stop a specific motor

        Args:
            motor_num: Motor number (1-4)
        """
        self.set_throttle(motor_num, 0)

    def add_motor(self, motor_num):
        """
        Add a motor to the controller if it doesn't already exist

        Args:
            motor_num: Motor number (1-4) to add

        Raises:
            ValueError: If motor_num is not 1-4
            MotorControllerError: If motor initialization fails
        """
        if motor_num not in range(1, 5):
            raise ValueError(f"Motor number must be 1-4, got {motor_num}")

        # If motor already exists, nothing to do
        if motor_num in self.motors and self.motors[motor_num] is not None:
            return

        if self._mock_mode:
            self.motors[motor_num] = None
            return

        try:
            channels = self.MOTOR_CHANNELS[motor_num]
            self.motors[motor_num] = motor.DCMotor(
                self.pca.channels[channels['in1']],
                self.pca.channels[channels['in2']]
            )
            self.motors[motor_num].decay_mode = motor.SLOW_DECAY
            self.stop(motor_num)
        except Exception as e:
            raise MotorControllerError(f"Failed to add motor {motor_num}: {e}")

    def stop_all(self):
        """Stop all initialized motors"""
        for motor_num in self.motors:
            self.stop(motor_num)

    def run_forward(self, motor_num, speed=0.5):
        """
        Run motor forward at specified speed

        Args:
            motor_num: Motor number (1-4)
            speed: Speed from 0.0 to 1.0 (default 0.5 = half speed)
        """
        speed = max(0.0, min(1.0, abs(speed)))
        self.set_throttle(motor_num, speed)

    def run_reverse(self, motor_num, speed=0.5):
        """
        Run motor in reverse at specified speed

        Args:
            motor_num: Motor number (1-4)
            speed: Speed from 0.0 to 1.0 (default 0.5 = half speed)
        """
        speed = max(0.0, min(1.0, abs(speed)))
        self.set_throttle(motor_num, -speed)

    def deinit(self):
        """Cleanup - stop all motors and deinitialize PCA9685"""
        self.stop_all()
        if self.pca is not None:
            self.pca.deinit()
