# Quick Motor Testing Guide

## What You Need to Test

### Hardware
1. ✅ Adafruit DC Motor + Stepper FeatherWing
2. ✅ Adafruit Feather board (any model)
3. ✅ 12V power supply (4.5-13.5V, 2A min)
4. ✅ 1-4 DC motors (12V, max 1.2A each)
5. ✅ PyBadge running this firmware

### Software Libraries

Install these to `CIRCUITPY/lib/` on your PyBadge:

```
lib/
├── adafruit_pca9685.mpy
├── adafruit_motor/
│   ├── __init__.py
│   ├── motor.py
│   └── ...
└── adafruit_register/
    ├── __init__.py
    └── ...
```

Download from: https://circuitpython.org/libraries

## Quick Test Without Hardware (Mock Mode)

The firmware will run in **mock mode** if no FeatherWing is detected:

1. Upload firmware to PyBadge
2. Connect USB for serial console
3. Press MENU → Select "Motor 1" → Press RIGHT
4. Try controls - commands will print to serial console

Example console output:
```
Motor controller running in mock mode: [Errno 19] No such device
[MOCK] Motor 1 throttle: 0.50
[MOCK] Motor 1 throttle: 0.60
[MOCK] Motor 1 throttle: -0.50
[MOCK] Motor 1 throttle: 0.00
```

## Quick Test With Hardware

### 1. Assembly
```
1. Solder headers on FeatherWing (if needed)
2. Stack FeatherWing onto Feather
3. Connect 12V power to FeatherWing terminal block
4. Connect motor to M1 terminal (doesn't matter which wire goes where)
5. Wire PyBadge to Feather via I2C:
   PyBadge SDA → Feather SDA
   PyBadge SCL → Feather SCL
   PyBadge GND → Feather GND
```

### 2. Test Motor 1

1. Power on PyBadge
2. Press **MENU** button
3. Navigate down to "Motor 1"
4. Press **RIGHT** to select

You should see:
```
Motor 1
  50%
FORWARD

UP/DN: Speed
LEFT: Rev
RIGHT: Fwd
BLANK: Stop
```

5. Try each button:
   - **RIGHT** → Motor spins forward
   - **LEFT** → Motor reverses
   - **UP** → Speed increases
   - **DOWN** → Speed decreases
   - **BLANK** → Motor stops
   - **MENU** → Exit to main screen

### 3. Test All Motors

Repeat steps for Motor 2, Motor 3, Motor 4

## Troubleshooting Quick Checks

### "Mock mode" message but hardware is connected

Run I2C scanner:
```python
import board
i2c = board.I2C()
while not i2c.try_lock():
    pass
print("I2C devices:", [hex(addr) for addr in i2c.scan()])
i2c.unlock()
```

Should see: `['0x60']` (FeatherWing default address)

### Motor doesn't spin

1. ✅ Power supply turned on?
2. ✅ Green LED on FeatherWing lit?
3. ✅ Motor wires properly in terminal block?
4. ✅ Try different motor to rule out bad motor
5. ✅ Try reversing motor wires

### Motor runs wrong direction

- Swap motor wires in terminal block
- OR use LEFT button instead of RIGHT

## Expected Behavior Summary

| Action | Result |
|--------|--------|
| Select Motor 1 from menu | Enter motor control, motor stopped |
| Press RIGHT | Motor runs forward at 50% |
| Press UP (3x) | Speed increases to 80% |
| Press LEFT | Motor reverses at same speed |
| Press DOWN (8x) | Speed decreases to 0% |
| Press BLANK | Motor stops immediately |
| Press MENU | Exit to measurement screen, motor stops |

## Control Ranges

- **Speed**: 0-100% in 10% increments
- **Throttle**: -1.0 (full reverse) to +1.0 (full forward)
- **Throttle = 0**: Motor stopped

## Safety

- Motors stop automatically when:
  - Pressing BLANK button
  - Pressing MENU to exit
  - Firmware starts/restarts
  - Switching between motor channels

- Emergency stop: Press BLANK or MENU

## Next Steps

Once basic testing works:

1. ✅ Test all 4 motors individually
2. ✅ Verify speed control (UP/DOWN buttons)
3. ✅ Test direction changes (LEFT/RIGHT buttons)
4. ✅ Confirm motor stops on exit (MENU button)
5. ✅ Test with your actual pump motors
6. ✅ Integrate into your fluidic control sequences

## Files Changed

New files:
- `src/motor_controller.py` - Motor control logic
- `src/motor_screen.py` - Motor UI display
- `README_MOTOR_CONTROL.md` - Full documentation

Modified files:
- `src/colorimeter.py` - Integration and menu items

## Code Integration Points

To use motors in your own code:

```python
from motor_controller import MotorController

# Initialize
motor = MotorController()

# Run pump forward at 75%
motor.set_throttle(1, 0.75)

# Wait...
import time
time.sleep(5)

# Stop
motor.stop(1)
```

## Questions?

See `README_MOTOR_CONTROL.md` for complete documentation.
