import time
import ulab
import board
import analogio
import digitalio
import gamepadshift
import constants
import adafruit_itertools
import gc

from light_sensor import LightSensor
from light_sensor import LightSensorOverflow
from light_sensor import LightSensorIOError

from battery_monitor import BatteryMonitor

from configuration import Configuration
from configuration import ConfigurationError

from calibrations import Calibrations
from calibrations import CalibrationsError

from menu_screen import MenuScreen
from message_screen import MessageScreen
from measure_screen import MeasureScreen

# Motor imports - lazy load to save memory
# from motor_screen import MotorScreen
# from motor_controller import MotorController
# from motor_controller import MotorControllerError

class Mode:
    MEASURE = 0
    MENU    = 1
    MESSAGE = 2
    ABORT   = 3
    MOTOR_CONTROL = 4

class Colorimeter:

    ABOUT_STR = 'About'
    RAW_SENSOR_STR = 'Raw Sensor'
    ABSORBANCE_STR = 'Absorbance'
    TRANSMITTANCE_STR = 'Transmittance'
    MOTOR_1_STR = 'Motor 1'
    MOTOR_2_STR = 'Motor 2'
    MOTOR_3_STR = 'Motor 3'
    MOTOR_4_STR = 'Motor 4'
    DEFAULT_MEASUREMENTS = [ABSORBANCE_STR, TRANSMITTANCE_STR, RAW_SENSOR_STR]
    MOTOR_ITEMS = [MOTOR_1_STR, MOTOR_2_STR, MOTOR_3_STR, MOTOR_4_STR]

    def __init__(self):

        self.menu_items = list(self.DEFAULT_MEASUREMENTS)
        self.menu_view_pos = 0
        self.menu_item_pos = 0
        self.mode = Mode.MEASURE
        self.is_blanked = False
        self.blank_value = 1.0
        self.current_motor_num = 1
        self.motor_throttle = 0.0  # Current motor speed/direction
        self.motor_enabled = True  # Set to False to disable motor features
        self.motor_controller = None  # Lazy load when needed


        # Create screens
        board.DISPLAY.brightness = 1.0
        self.measure_screen = MeasureScreen()
        self.message_screen = MessageScreen()
        self.menu_screen = MenuScreen()
        self.motor_screen = None  # Lazy load when needed

        # Setup gamepad inputs - change this (Keypad shift??)
        self.last_button_press = time.monotonic()
        self.pad = gamepadshift.GamePadShift(
                digitalio.DigitalInOut(board.BUTTON_CLOCK), 
                digitalio.DigitalInOut(board.BUTTON_OUT),
                digitalio.DigitalInOut(board.BUTTON_LATCH),
                )

        # Load Configuration
        self.configuration = Configuration()
        try:
            self.configuration.load()
        except ConfigurationError as error:
            # Unable to load configuration file or not a dict after loading
            self.message_screen.set_message(error)
            self.message_screen.set_to_error()
            self.mode = Mode.MESSAGE

        # Load calibrations and populate menu items
        self.calibrations = Calibrations()
        try:
            self.calibrations.load()
        except CalibrationsError as error: 
            # Unable to load calibrations file or not a dict after loading
            self.message_screen.set_message(error) 
            self.message_screen.set_to_error()
            self.mode = Mode.MESSAGE
        else:
            # We can load calibration, but detected errors in some calibrations
            if self.calibrations.has_errors:
                error_msg = f'errors found in calibrations file'
                self.message_screen.set_message(error_msg)
                self.message_screen.set_to_error()
                self.mode = Mode.MESSAGE

        self.menu_items.extend([k for k in self.calibrations.data])
        if self.motor_enabled:
            self.menu_items.extend(self.MOTOR_ITEMS)
        self.menu_items.append(self.ABOUT_STR)

        # Set default/startup measurement
        if self.configuration.startup in self.menu_items:
            self.measurement_name = self.configuration.startup
        else:
            if self.configuration.startup is not None:
                error_msg = f'startup measurement {self.configuration.startup} not found'
                self.message_screen.set_message(error_msg)
                self.message_screen.set_to_error()
                self.mode = Mode.MESSAGE
            self.measurement_name = self.menu_items[0] 

        # Setup light sensor and preliminary blanking 
        try:
            self.light_sensor = LightSensor()
        except LightSensorIOError as error:
            error_msg = f'missing sensor? {error}'
            self.message_screen.set_message(error_msg,ok_to_continue=False)
            self.message_screen.set_to_abort()
            self.mode = Mode.ABORT
        else:
            if self.configuration.gain is not None:
                self.light_sensor.gain = self.configuration.gain
            if self.configuration.integration_time is not None:
                self.light_sensor.integration_time = self.configuration.integration_time
            self.blank_sensor(set_blanked=False)
            self.measure_screen.set_not_blanked()

        # Setup up battery monitoring settings cycles
        self.battery_monitor = BatteryMonitor()
        self.setup_gain_and_itime_cycles()

        # Print memory info at startup
        gc.collect()
        print(f"Startup free memory: {gc.mem_free()} bytes")

    def _init_motor_controller(self, motor_num):
        """
        Lazy load motor controller and screen only when needed

        Args:
            motor_num: Motor number (1-4) to initialize - only initializes this motor to save memory
        """
        if self.motor_controller is not None:
            return  # Already initialized

        try:
            # Free up memory before loading heavy motor modules
            gc.collect()
            print(f"Free memory before motor init: {gc.mem_free()} bytes")

            # Import motor modules only when needed
            from motor_screen import MotorScreen
            from motor_controller import MotorController

            # Initialize motor screen
            self.motor_screen = MotorScreen()

            # Run GC again after screen initialization
            gc.collect()
            print(f"Free memory after screen init: {gc.mem_free()} bytes")

            # Initialize motor controller - only create the one motor we need
            self.motor_controller = MotorController(motor_num=motor_num)
            if self.motor_controller.mock_mode:
                print("Motor controller in mock mode - no hardware detected")

            gc.collect()
            print(f"Free memory after motor init: {gc.mem_free()} bytes")

        except MemoryError as error:
            print(f"Memory allocation failed during motor init: {error}")
            print(f"Free memory: {gc.mem_free()} bytes")
            self.motor_controller = None
            self.motor_screen = None
            raise  # Re-raise to be caught by caller
        except Exception as error:
            print(f"Motor init error: {error}")
            self.motor_controller = None
            self.motor_screen = None

    def setup_gain_and_itime_cycles(self):
        self.gain_cycle = adafruit_itertools.cycle(constants.GAIN_TO_STR)
        if self.configuration.gain is not None:
            while next(self.gain_cycle) != self.configuration.gain:
                continue

        self.itime_cycle = adafruit_itertools.cycle(constants.INTEGRATION_TIME_TO_STR)
        if self.configuration.integration_time is not None:
            while next(self.itime_cycle) != self.configuration.integration_time:
                continue

    @property
    def num_menu_items(self):
        return len(self.menu_items)

    def incr_menu_item_pos(self):
        if self.menu_item_pos < self.num_menu_items-1:
            self.menu_item_pos += 1
        diff_pos = self.menu_item_pos - self.menu_view_pos
        if diff_pos > self.menu_screen.items_per_screen-1:
            self.menu_view_pos += 1

    def decr_menu_item_pos(self):
        if self.menu_item_pos > 0:
            self.menu_item_pos -= 1
        if self.menu_item_pos < self.menu_view_pos:
            self.menu_view_pos -= 1

    def update_menu_screen(self):
        n0 = self.menu_view_pos
        n1 = n0 + self.menu_screen.items_per_screen
        view_items = []
        for i, item in enumerate(self.menu_items[n0:n1]):
            led = self.calibrations.led(item)
            if led is None:
                item_text = f'{n0+i} {item}' 
            else:
                item_text = f'{n0+i} {item} ({led})' 
            view_items.append(item_text)
        self.menu_screen.set_menu_items(view_items)
        pos = self.menu_item_pos - self.menu_view_pos
        self.menu_screen.set_curr_item(pos)

    @property
    def is_absorbance(self):
        return self.measurement_name == self.ABSORBANCE_STR

    @property
    def is_transmittance(self):
        return self.measurement_name == self.TRANSMITTANCE_STR

    @property
    def is_raw_sensor(self):
        return self.measurement_name == self.RAW_SENSOR_STR

    @property
    def is_motor_control(self):
        return self.measurement_name in self.MOTOR_ITEMS

    def get_motor_number_from_name(self, name):
        """Extract motor number (1-4) from motor menu item name"""
        if name == self.MOTOR_1_STR:
            return 1
        elif name == self.MOTOR_2_STR:
            return 2
        elif name == self.MOTOR_3_STR:
            return 3
        elif name == self.MOTOR_4_STR:
            return 4
        return None

    @property
    def measurement_units(self):
        if self.measurement_name in self.DEFAULT_MEASUREMENTS: 
            units = None 
        else:
            units = self.calibrations.units(self.measurement_name)
        return units

    @property
    def raw_sensor_value(self):
        return self.light_sensor.value

    @property
    def transmittance(self):
        transmittance = float(self.raw_sensor_value)/self.blank_value
        return transmittance

    @property
    def absorbance(self):
        absorbance = -ulab.numpy.log10(self.transmittance)
        absorbance = absorbance if absorbance > 0.0 else 0.0
        return absorbance

    @property
    def measurement_value(self):
        if self.is_absorbance: 
            value = self.absorbance
        elif self.is_transmittance:
            value = self.transmittance
        elif self.is_raw_sensor:
            value = self.raw_sensor_value
        else:
            try:
                value = self.calibrations.apply( 
                        self.measurement_name, 
                        self.absorbance
                        )
            except CalibrationsError as error:
                self.message_screen.set_message(error_message)
                self.message_screen.set_to_error()
                self.measurement_name = 'Absorbance'
                self.mode = Mode.MESSAGE
        return value

    def blank_sensor(self, set_blanked=True):
        blank_samples = ulab.numpy.zeros((constants.NUM_BLANK_SAMPLES,))
        for i in range(constants.NUM_BLANK_SAMPLES):
            try:
                value = self.raw_sensor_value
            except LightSensorOverflow:
                value = self.light_sensor.max_counts
            blank_samples[i] = value
            time.sleep(constants.BLANK_DT)
        self.blank_value = ulab.numpy.median(blank_samples)
        if set_blanked:
            self.is_blanked = True

    def blank_button_pressed(self, buttons):  
        if self.is_raw_sensor:
            return False
        else:
            return buttons & constants.BUTTON['blank']

    def menu_button_pressed(self, buttons): 
        return buttons & constants.BUTTON['menu']

    def up_button_pressed(self, buttons):
        return buttons & constants.BUTTON['up']

    def down_button_pressed(self, buttons):
        return buttons & constants.BUTTON['down']

    def right_button_pressed(self, buttons):
        return buttons & constants.BUTTON['right']

    def gain_button_pressed(self, buttons):
        if self.is_raw_sensor:
            return buttons & constants.BUTTON['gain']
        else:
            return False

    def itime_button_pressed(self, buttons):
        if self.is_raw_sensor:
            return buttons & constants.BUTTON['itime']
        else:
            return False

    def handle_button_press(self):
        buttons = self.pad.get_pressed()
        if not buttons:
            # No buttons pressed
            return 
        if not self.check_debounce():
            # Still within debounce timeout
            return  

        # Get time of last button press for debounce check
        self.last_button_press = time.monotonic()

        # Update state of system based on buttons pressed.
        # This is different for each operating mode. 
        if self.mode == Mode.MEASURE:
            if self.blank_button_pressed(buttons):
                self.measure_screen.set_blanking()
                self.blank_sensor()
            elif self.menu_button_pressed(buttons):
                self.mode = Mode.MENU
                self.menu_view_pos = 0
                self.menu_item_pos = 0
                self.update_menu_screen()
            elif self.gain_button_pressed(buttons):
                self.light_sensor.gain = next(self.gain_cycle)
                self.is_blanked = False
            elif self.itime_button_pressed(buttons):
                self.light_sensor.integration_time = next(self.itime_cycle)
                self.is_blanked = False

        elif self.mode == Mode.MENU:
            if self.menu_button_pressed(buttons):
                self.mode = Mode.MEASURE
            elif self.up_button_pressed(buttons): 
                self.decr_menu_item_pos()
            elif self.down_button_pressed(buttons): 
                self.incr_menu_item_pos()
            elif self.right_button_pressed(buttons):
                selected_item = self.menu_items[self.menu_item_pos]
                if selected_item == self.ABOUT_STR:
                    about_msg = f'firmware version {constants.__version__}'
                    self.message_screen.set_message(about_msg)
                    self.message_screen.set_to_about()
                    self.mode = Mode.MESSAGE
                elif selected_item in self.MOTOR_ITEMS:
                    # Entering motor control mode - lazy load motor modules
                    try:
                        # Determine which motor number before initializing
                        motor_num = self.get_motor_number_from_name(selected_item)

                        # Initialize controller if first time, or add motor if switching
                        if self.motor_controller is None:
                            self._init_motor_controller(motor_num)
                        else:
                            # Controller exists, add this motor if it doesn't exist yet
                            gc.collect()
                            self.motor_controller.add_motor(motor_num)

                        if self.motor_controller is not None:
                            self.measurement_name = selected_item
                            self.current_motor_num = motor_num
                            self.motor_throttle = 0.0
                            self.mode = Mode.MOTOR_CONTROL
                            self.motor_controller.stop(self.current_motor_num)
                        else:
                            error_msg = 'Motor controller init failed'
                            self.message_screen.set_message(error_msg)
                            self.message_screen.set_to_error()
                            self.mode = Mode.MESSAGE
                    except MemoryError:
                        error_msg = 'Not enough memory for motors. Disable motor_enabled in code or remove calibrations'
                        self.message_screen.set_message(error_msg)
                        self.message_screen.set_to_error()
                        self.mode = Mode.MESSAGE
                else:
                    self.measurement_name = self.menu_items[self.menu_item_pos]
                    self.mode = Mode.MEASURE
            self.update_menu_screen()

        elif self.mode == Mode.MOTOR_CONTROL:
            if self.menu_button_pressed(buttons):
                # Exit motor control, stop motor
                if self.motor_controller:
                    self.motor_controller.stop(self.current_motor_num)
                self.motor_throttle = 0.0
                self.mode = Mode.MEASURE
            elif self.up_button_pressed(buttons):
                # Increase speed (keep same direction)
                if abs(self.motor_throttle) < 1.0:
                    if self.motor_throttle >= 0:
                        self.motor_throttle = min(1.0, self.motor_throttle + 0.1)
                    else:
                        self.motor_throttle = max(-1.0, self.motor_throttle - 0.1)
                if self.motor_controller:
                    self.motor_controller.set_throttle(self.current_motor_num, self.motor_throttle)
            elif self.down_button_pressed(buttons):
                # Decrease speed (keep same direction)
                if abs(self.motor_throttle) > 0:
                    if self.motor_throttle > 0:
                        self.motor_throttle = max(0.0, self.motor_throttle - 0.1)
                    else:
                        self.motor_throttle = min(0.0, self.motor_throttle + 0.1)
                if self.motor_controller:
                    self.motor_controller.set_throttle(self.current_motor_num, self.motor_throttle)
            elif self.right_button_pressed(buttons):
                # Forward direction - maintain current speed
                speed = abs(self.motor_throttle)
                self.motor_throttle = speed if speed > 0 else 0.5
                if self.motor_controller:
                    self.motor_controller.set_throttle(self.current_motor_num, self.motor_throttle)
            elif buttons & constants.BUTTON['left']:
                # Reverse direction - maintain current speed
                speed = abs(self.motor_throttle)
                self.motor_throttle = -speed if speed > 0 else -0.5
                if self.motor_controller:
                    self.motor_controller.set_throttle(self.current_motor_num, self.motor_throttle)
            elif self.blank_button_pressed(buttons):
                # Stop motor
                self.motor_throttle = 0.0
                if self.motor_controller:
                    self.motor_controller.stop(self.current_motor_num)

        elif self.mode == Mode.MESSAGE:
            if self.calibrations.has_errors:
                error_msg = self.calibrations.pop_error()
                self.message_screen.set_message(error_msg)
                self.message_screen.set_to_error()
                self.mode = Mode.MESSAGE
            else:
                self.mode = Mode.MEASURE

    def check_debounce(self):
        button_dt = time.monotonic() - self.last_button_press
        if button_dt < constants.DEBOUNCE_DT: 
            return False
        else:
            return True

    def run(self):

        while True:

            # Deal with any button presses
            self.handle_button_press()

            # Update display based on the current operating mode
            if self.mode == Mode.MEASURE:

                # Get measurement and result to measurment screen
                try:
                    self.measure_screen.set_measurement(
                            self.measurement_name, 
                            self.measurement_units, 
                            self.measurement_value,
                            self.configuration.precision
                            )
                except LightSensorOverflow:
                    self.measure_screen.set_overflow(self.measurement_name)

                # Display whether or not we have blanking data. Not relevant
                # when device is displaying raw sensor data
                if self.is_raw_sensor:
                    self.measure_screen.set_blanked()
                    gain = self.light_sensor.gain
                    itime = self.light_sensor.integration_time
                    self.measure_screen.set_gain(gain)
                    self.measure_screen.set_integration_time(itime)
                else:
                    if self.is_blanked:
                        self.measure_screen.set_blanked()
                    else:
                        self.measure_screen.set_not_blanked()
                    self.measure_screen.clear_gain()
                    self.measure_screen.clear_integration_time()

                # Update and display measurement of battery voltage
                self.battery_monitor.update()
                battery_voltage = self.battery_monitor.voltage_lowpass
                self.measure_screen.set_bat(battery_voltage)

                self.measure_screen.show()

            elif self.mode == Mode.MENU:
                self.menu_screen.show()

            elif self.mode == Mode.MOTOR_CONTROL:
                # Update motor control screen
                if self.motor_screen is not None:
                    self.motor_screen.set_motor_number(self.current_motor_num)
                    self.motor_screen.update(self.motor_throttle)
                    self.motor_screen.show()

            elif self.mode in (Mode.MESSAGE, Mode.ABORT):
                self.message_screen.show()

            time.sleep(constants.LOOP_DT)



