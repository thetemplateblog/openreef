# Motor Control Integration Guide

## Overview

The OpenReef colorimeter firmware now supports controlling up to 4 DC motors via the **Adafruit DC Motor + Stepper FeatherWing**. This allows you to control peristaltic pumps, mixing motors, or other motorized components directly from the PyBadge interface.

## Hardware Requirements

### Required Components

1. **Adafruit DC Motor + Stepper FeatherWing**
   - Product: https://learn.adafruit.com/adafruit-stepper-dc-motor-featherwing
   - Controls up to 4 DC motors
   - Uses TB6612 motor driver chip
   - I2C communication (default address 0x60)

2. **Any Adafruit Feather Board** (choose one):
   - Feather M0/M4 (SAMD21/51) - recommended for consistency with PyBadge
   - Feather RP2040 - great for motor control with many PWM channels
   - Feather ESP32 - if WiFi/Bluetooth needed

3. **Power Supply**
   - 4.5-13.5V DC (12V recommended to match existing pump voltage)
   - 2A minimum (depending on motor load)
   - Connected to FeatherWing terminal block

4. **DC Motors**
   - Up to 4 motors
   - 12V DC motors recommended
   - Max 1.2A per motor

5. **Connection between PyBadge and Feather**
   - I2C connection (SDA, SCL, GND)
   - OR UART connection (TX, RX, GND)

## Wiring

### FeatherWing to Feather

1. Stack FeatherWing on top of Feather board
2. Solder headers if not pre-soldered

### Power Supply to FeatherWing

1. Connect 12V power supply to FeatherWing terminal block
2. **Observe polarity!** (+ to +, - to -)
3. The FeatherWing has polarity protection

### Motors to FeatherWing

Connect motors to terminal blocks M1, M2, M3, M4:
- Each motor uses 2 wires
- Polarity determines initial direction (can be reversed in software)

### PyBadge to Feather (I2C Connection)

**Important**: The motor controller communicates with the FeatherWing via the Feather's I2C bus. The PyBadge talks to the Feather, which then controls the motors.

Current implementation assumes the FeatherWing is directly accessible from the PyBadge's I2C bus. For a two-board setup (PyBadge + Feather), you would need to modify the code to use UART communication instead.

#### Option A: Shared I2C Bus (Simple, requires custom wiring)
```
PyBadge SDA  ──────┐
                   ├──── Feather SDA ──── FeatherWing
Feather SDA  ──────┘

PyBadge SCL  ──────┐
                   ├──── Feather SCL ──── FeatherWing
Feather SCL  ──────┘

PyBadge GND  ────── Feather GND
```

#### Option B: UART Communication (Recommended for future)
Requires modifying the motor_controller.py to communicate via Serial instead of I2C.

## Software Setup

### Required CircuitPython Libraries

Copy these libraries to your PyBadge `CIRCUITPY/lib/` folder:

1. **adafruit_pca9685.mpy** - PWM driver for motor control
2. **adafruit_motor/** - Motor control library
3. **adafruit_register/** - Register access library

Download from: https://circuitpython.org/libraries

### Files Added

The motor control integration adds these files:

```
src/motor_controller.py    - Motor controller class
src/motor_screen.py         - Motor control UI screen
src/colorimeter.py          - Updated with motor control integration
```

## Usage

### Accessing Motor Control

1. Power on PyBadge
2. Press **MENU** button
3. Navigate to motor items:
   - Motor 1
   - Motor 2
   - Motor 3
   - Motor 4
4. Press **RIGHT** to select and enter motor control mode

### Motor Control Interface

Once in motor control mode, you'll see:
- Motor number (1-4)
- Current speed (0-100%)
- Status (STOPPED / FORWARD / REVERSE)
- Control instructions

#### Button Controls

| Button | Function |
|--------|----------|
| **UP** | Increase speed (+10%) |
| **DOWN** | Decrease speed (-10%) |
| **RIGHT** | Run forward (maintains current speed or starts at 50%) |
| **LEFT** | Run reverse (maintains current speed or starts at 50%) |
| **BLANK** | Stop motor (speed → 0%) |
| **MENU** | Exit motor control and return to measurement mode |

#### Example Usage Sequence

1. Enter Motor 1 control
2. Press **RIGHT** → Motor runs forward at 50%
3. Press **UP** 3 times → Speed increases to 80%
4. Press **LEFT** → Motor reverses at 80%
5. Press **DOWN** 5 times → Speed decreases to 30%
6. Press **BLANK** → Motor stops
7. Press **MENU** → Exit to main screen

## Motor Controller Architecture

### Software Components

#### motor_controller.py

Manages communication with the PCA9685 PWM chip on the FeatherWing:

```python
motor_controller = MotorController()

# Control individual motors
motor_controller.set_throttle(motor_num=1, throttle=0.5)   # 50% forward
motor_controller.set_throttle(motor_num=2, throttle=-0.75) # 75% reverse
motor_controller.stop(motor_num=3)                         # Stop motor 3
motor_controller.stop_all()                                # Emergency stop
```

**Key Parameters:**
- `motor_num`: 1-4
- `throttle`: -1.0 (full reverse) to 1.0 (full forward), 0 = stopped

#### motor_screen.py

Displays motor control interface with:
- Motor identification
- Real-time speed display
- Direction indicator
- Help text for controls

#### Mock Mode

If the FeatherWing is not detected, the controller runs in **mock mode**:
- No errors thrown
- Commands are printed to serial console
- Useful for testing UI without hardware

### I2C Addressing

Default PCA9685 address: **0x60**

The FeatherWing has address jumpers (A0-A4) allowing up to 32 boards:
- Default: 0x60
- With A0 jumper: 0x61
- With A1 jumper: 0x62
- etc.

To use a different address:
```python
motor_controller = MotorController(i2c_address=0x61)
```

## Troubleshooting

### Motor Controller Not Detected

**Symptom**: "Motor controller in mock mode" message

**Solutions**:
1. Check I2C wiring (SDA, SCL, GND)
2. Verify FeatherWing is properly stacked on Feather
3. Check power supply is connected to FeatherWing
4. Verify I2C address (default 0x60)
5. Test I2C bus with i2c scanner:
   ```python
   import board
   i2c = board.I2C()
   while not i2c.try_lock():
       pass
   print("I2C addresses found:", [hex(device_address)
         for device_address in i2c.scan()])
   i2c.unlock()
   ```

### Motor Doesn't Run

**Check**:
1. Power supply connected and turned on
2. Motor wires properly connected to terminal block
3. Motor is functional (test with different power source)
4. Current limit not exceeded (max 1.2A per motor)

### Motor Runs Backward

**Solution**: Reverse motor wires on terminal block OR use negative throttle in software

### Erratic Motor Behavior

**Possible Causes**:
1. Power supply voltage too low or unstable
2. Insufficient current capacity
3. Loose connections
4. Interference on I2C bus

**Solutions**:
- Use regulated 12V power supply with adequate current rating
- Keep I2C wires short and away from motor wires
- Add decoupling capacitors if needed

## Safety Considerations

1. **Power Supply**
   - Never exceed 13.5V DC
   - Ensure adequate current rating for your motors
   - Use fused power supply

2. **Motor Current**
   - Each motor limited to 1.2A continuous
   - TB6612 chip has thermal protection
   - Don't stall motors for extended periods

3. **Emergency Stop**
   - Press BLANK button to stop current motor
   - Press MENU to exit and stop motor
   - All motors stopped on firmware initialization

## Future Enhancements

Possible additions:
- Timed motor operation (run for X seconds)
- Speed ramping (smooth acceleration/deceleration)
- Motor sequences (automated protocols)
- Save motor presets to configuration
- PWM frequency adjustment for different motor types
- Current sensing and monitoring

## API Reference

### MotorController Class

```python
class MotorController(i2c_address=0x60)
```

**Methods**:

- `set_throttle(motor_num, throttle)` - Set motor speed/direction
  - motor_num: 1-4
  - throttle: -1.0 to 1.0

- `stop(motor_num)` - Stop specific motor
  - motor_num: 1-4

- `stop_all()` - Stop all motors

- `run_forward(motor_num, speed=0.5)` - Run motor forward
  - motor_num: 1-4
  - speed: 0.0 to 1.0

- `run_reverse(motor_num, speed=0.5)` - Run motor in reverse
  - motor_num: 1-4
  - speed: 0.0 to 1.0

**Properties**:

- `mock_mode` - Returns True if running without hardware

## Additional Resources

- [Adafruit Motor FeatherWing Guide](https://learn.adafruit.com/adafruit-stepper-dc-motor-featherwing)
- [PCA9685 Datasheet](https://www.nxp.com/docs/en/data-sheet/PCA9685.pdf)
- [TB6612FNG Motor Driver Datasheet](https://www.sparkfun.com/datasheets/Robotics/TB6612FNG.pdf)
- [CircuitPython Motor Library](https://docs.circuitpython.org/projects/motor/en/latest/)

## Support

For issues or questions:
1. Check this documentation
2. Test in mock mode to isolate hardware vs software issues
3. Verify I2C communication with scanner
4. Check physical connections and power supply
5. Review Adafruit FeatherWing documentation
