---
layout: single
title: Automation Sequence
permalink: /docs/firmware/automation-sequence/
toc: true
---

# Firmware & Automation Sequence

## Overview

The OpenReef firmware controls the entire automated assay process, from sample preparation through measurement and cleanup. The firmware is written in **CircuitPython** for the AdaFruit PyBadge and manages pumps, valves, colorimeter, timing, and user interface.

## System Components Controlled

### Pumps (Bidirectional)
- **FeW Pump**: Fill/Empty Water pump (handles RO water, test water, waste)
  - Forward: Normal pumping
  - Reverse: Creates air bubbles for cuvette mixing
- **FeR Pump**: Fill/Empty Reagent pump (dispenses reagents #1 and #2)
  - Forward: Normal pumping
  - Reverse: Creates air bubbles for reagent bottle mixing

### Valves (3-way solenoid)
- **ReV**: Reagent Valve (selects Reagent #1 or Reagent #2)
- **WtV**: Water Test Valve (selects RO water or Test water)
- **WaV**: Waste Valve (directs to Waste or back to Test/cuvette)

### Sensors & Actuators
- **AS7341 Colorimeter**: Measures absorbance at 528nm (nitrate) or 625nm (phosphate)
- **LEDs**: 528nm (green) for nitrate, 625nm (red) for phosphate
- **PyBadge Display**: User interface and results

### Mixing Method
- **Bubble Mixing**: Achieved by reversing pumps to introduce air bubbles
- **No mechanical stirrers** - simplified hardware design
- **Air Pump**: Optional alternative for dedicated bubbling system

## Automation Sequence Overview

```
┌─────────────────────────────────────────┐
│          System Preparation             │
│  - Clean lines with RO water            │
│  - Verify pumps and valves functional   │
└────────────┬────────────────────────────┘
             ▼
┌─────────────────────────────────────────┐
│          Sample Loading                  │
│  - Fill cuvette with test water         │
│  - Verify fill level                    │
└────────────┬────────────────────────────┘
             ▼
┌─────────────────────────────────────────┐
│       Baseline Measurement               │
│  - Zero colorimeter with sample         │
│  - Record blank absorbance              │
└────────────┬────────────────────────────┘
             ▼
┌─────────────────────────────────────────┐
│        Reagent Addition                  │
│  - Add Reagent #1 (measured volume)     │
│  - Stir and mix                         │
│  - Add Reagent #2 (measured volume)     │
│  - Stir and START TIMER                 │
└────────────┬────────────────────────────┘
             ▼
┌─────────────────────────────────────────┐
│       Timed Incubation                   │
│  - Wait for color development           │
│  - Display countdown                    │
└────────────┬────────────────────────────┘
             ▼
┌─────────────────────────────────────────┐
│         Measurement                      │
│  - Read absorbance at wavelength        │
│  - Calculate concentration              │
│  - Display result                       │
└────────────┬────────────────────────────┘
             ▼
┌─────────────────────────────────────────┐
│          System Cleanup                  │
│  - Flush cuvette with RO water          │
│  - Clear all lines                      │
│  - Ready for next test                  │
└─────────────────────────────────────────┘
```

## Detailed Automation Sequence

### Phosphate Assay Sequence

```python
# Pseudocode for automated phosphate assay

def run_phosphate_assay():
    """
    Complete automated phosphate assay
    Total time: ~12 minutes
    """

    # ========== STEP 1: SYSTEM PREPARATION ==========
    display_message("Preparing system...")

    # Clear waste line
    set_valve(WaV, WASTE)
    run_pump(FeW, REVERSE, duration=3.0)  # 3 seconds reverse

    # Flush with RO water
    set_valve(WtV, RO_WATER)
    set_valve(WaV, TEST)  # Direct to cuvette
    run_pump(FeW, FORWARD, volume=5.0)  # Fill cuvette with RO

    # Empty to waste
    set_valve(WaV, WASTE)
    run_pump(FeW, REVERSE, duration=5.0)

    # ========== STEP 2: SAMPLE LOADING ==========
    display_message("Loading sample...")

    # Fill cuvette with test water
    set_valve(WtV, TEST_WATER)
    set_valve(WaV, TEST)
    run_pump(FeW, FORWARD, volume=5.0)  # 5 mL test water

    wait(2.0)  # Let sample settle

    # ========== STEP 3: BASELINE MEASUREMENT ==========
    display_message("Zeroing colorimeter...")

    set_led(RED_625nm, ON)
    wait(1.0)  # LED warm-up

    baseline_absorbance = read_colorimeter(wavelength=625)
    display_value("Baseline", baseline_absorbance)

    # ========== STEP 4: REAGENT #1 ADDITION ==========
    display_message("Adding Reagent #1...")

    # Dispense 6 drops (~0.30 mL) of Reagent #1
    set_valve(ReV, REAGENT_1)
    run_pump(FeR, FORWARD, volume=0.30)  # 6 drops

    # Clear reagent line (reverse pump, possibly with air)
    run_pump(FeR, REVERSE, duration=1.0)
    # Optional: pulse air pump to clear line

    # Mix via bubbling
    mix_by_bubbling(FeW, duration=3.0)  # Reverse pump to create bubbles
    wait(5.0)  # Allow bubbles to mix solution

    # ========== STEP 5: REAGENT #2 ADDITION ==========
    display_message("Adding Reagent #2...")

    # Dispense 6 drops (~0.30 mL) of Reagent #2
    set_valve(ReV, REAGENT_2)
    run_pump(FeR, FORWARD, volume=0.30)  # 6 drops

    # Clear reagent line
    run_pump(FeR, REVERSE, duration=1.0)

    # Mix and START TIMER
    mix_by_bubbling(FeW, duration=3.0)  # Reverse pump to create bubbles
    wait(5.0)  # Allow bubbles to mix solution

    start_time = time.now()

    # ========== STEP 6: INCUBATION ==========
    display_message("Incubating...")

    # Wait 7.5 minutes (mid-point of 5-10 min window)
    target_time = 7.5 * 60  # 450 seconds

    while (time.now() - start_time) < target_time:
        elapsed = time.now() - start_time
        remaining = target_time - elapsed
        display_countdown(remaining)
        wait(1.0)

    # ========== STEP 7: MEASUREMENT ==========
    display_message("Measuring...")

    # Ensure LED is on
    set_led(RED_625nm, ON)
    wait(1.0)  # Stabilize

    # Read absorbance
    sample_absorbance = read_colorimeter(wavelength=625)

    # Calculate concentration from calibration curve
    # concentration = (absorbance - b) / m
    concentration = calculate_concentration(
        absorbance=sample_absorbance,
        baseline=baseline_absorbance,
        calibration_file="phosphate_cal.json"
    )

    # Display result
    display_result("Phosphate", concentration, "ppm PO4")

    # Log data
    log_result(timestamp=time.now(),
               assay="phosphate",
               absorbance=sample_absorbance,
               concentration=concentration)

    set_led(RED_625nm, OFF)

    # ========== STEP 8: CLEANUP ==========
    display_message("Cleaning system...")

    # Empty cuvette to waste
    set_valve(WaV, WASTE)
    run_pump(FeW, REVERSE, duration=5.0)

    # Flush with RO water
    set_valve(WtV, RO_WATER)
    set_valve(WaV, TEST)
    run_pump(FeW, FORWARD, volume=5.0)

    # Final waste
    set_valve(WaV, WASTE)
    run_pump(FeW, REVERSE, duration=5.0)

    display_message("Test complete!")
    beep()

    return concentration
```

### Nitrate Assay Sequence

```python
# Pseudocode for automated nitrate assay

def run_nitrate_assay():
    """
    Complete automated nitrate assay
    Total time: ~10 minutes
    """

    # ========== STEP 1-3: SAME AS PHOSPHATE ==========
    # (System prep, sample loading, baseline measurement)

    # ... (identical to phosphate steps 1-3)

    # Key difference: Use GREEN 528nm LED
    set_led(GREEN_528nm, ON)
    baseline_absorbance = read_colorimeter(wavelength=528)

    # ========== STEP 4: REAGENT #2 PREPARATION ==========
    display_message("Preparing Reagent #2...")

    # CRITICAL: Mix Reagent #2 bottle to suspend cadmium particles
    # Bubble vigorously by reversing reagent pump
    mix_by_bubbling(FeR, duration=5.0)  # Reverse pump into bottle
    wait(10.0)  # Allow bubbles to suspend cadmium particles

    # ========== STEP 5: REAGENT #1 ADDITION ==========
    display_message("Adding Reagent #1...")

    # Dispense 10 drops (~0.50 mL) of Reagent #1
    set_valve(ReV, REAGENT_1)
    run_pump(FeR, FORWARD, volume=0.50)  # 10 drops

    run_pump(FeR, REVERSE, duration=1.0)

    # Mix via bubbling
    mix_by_bubbling(FeW, duration=3.0)
    wait(5.0)

    # ========== STEP 6: REAGENT #2 ADDITION ==========
    display_message("Adding Reagent #2...")

    # Dispense 10 drops (~0.50 mL) of Reagent #2
    set_valve(ReV, REAGENT_2)
    run_pump(FeR, FORWARD, volume=0.50)  # 10 drops

    run_pump(FeR, REVERSE, duration=1.0)

    # VIGOROUS mixing for nitrate
    mix_by_bubbling(FeW, duration=5.0)  # Longer duration for more bubbles
    wait(10.0)  # Allow vigorous mixing

    start_time = time.now()

    # ========== STEP 7: INCUBATION ==========
    # Minimum 5 minutes (no upper limit, but use 5 min for consistency)
    target_time = 5.0 * 60  # 300 seconds

    while (time.now() - start_time) < target_time:
        elapsed = time.now() - start_time
        remaining = target_time - elapsed
        display_countdown(remaining)
        wait(1.0)

    # ========== STEP 8: MEASUREMENT ==========
    set_led(GREEN_528nm, ON)
    wait(1.0)

    sample_absorbance = read_colorimeter(wavelength=528)

    concentration = calculate_concentration(
        absorbance=sample_absorbance,
        baseline=baseline_absorbance,
        calibration_file="nitrate_cal.json"
    )

    display_result("Nitrate", concentration, "ppm NO3")

    log_result(timestamp=time.now(),
               assay="nitrate",
               absorbance=sample_absorbance,
               concentration=concentration)

    set_led(GREEN_528nm, OFF)

    # ========== STEP 9: CLEANUP ==========
    # (Same as phosphate cleanup)

    return concentration
```

## Timing Summary

### Phosphate Assay

| Step | Duration | Notes |
|------|----------|-------|
| System prep | 30 sec | Clean & flush |
| Sample loading | 15 sec | Fill cuvette |
| Baseline | 5 sec | Zero colorimeter |
| Reagent #1 | 20 sec | Dispense & mix |
| Reagent #2 | 20 sec | Dispense & mix |
| Incubation | 7.5 min | **CRITICAL TIMING** |
| Measurement | 10 sec | Read & calculate |
| Cleanup | 30 sec | Flush system |
| **Total** | **~10-12 min** | |

### Nitrate Assay

| Step | Duration | Notes |
|------|----------|-------|
| System prep | 30 sec | Clean & flush |
| Sample loading | 15 sec | Fill cuvette |
| Baseline | 5 sec | Zero colorimeter |
| Reagent #2 prep | 30 sec | **Stir bottle** |
| Reagent #1 | 20 sec | Dispense & mix |
| Reagent #2 | 25 sec | Dispense & vigorous mix |
| Incubation | 5 min | Minimum time |
| Measurement | 10 sec | Read & calculate |
| Cleanup | 30 sec | Flush system |
| **Total** | **~8-10 min** | |

## Pump Calibration

### Measuring Flow Rates

To ensure accurate reagent dispensing, pumps must be calibrated:

```python
def calibrate_pump(pump_id, direction):
    """
    Measure pump flow rate
    Returns: mL per second
    """
    # Collect 10 mL in graduated cylinder
    target_volume = 10.0  # mL

    display_message(f"Calibrating {pump_id}...")
    display_message("Place tube in graduated cylinder")
    wait_for_button()

    start_time = time.now()
    run_pump(pump_id, direction, volume=target_volume)
    end_time = time.now()

    duration = end_time - start_time

    display_message("Measure volume in cylinder")
    measured_volume = get_user_input("Volume (mL): ")

    flow_rate = measured_volume / duration  # mL/s

    save_calibration(pump_id, direction, flow_rate)

    display_message(f"Flow rate: {flow_rate:.3f} mL/s")

    return flow_rate
```

### Calibration Data Storage

```json
{
  "pump_calibration": {
    "FeW": {
      "forward": 1.25,  // mL/s
      "reverse": 1.18   // mL/s (may differ slightly)
    },
    "FeR": {
      "forward": 0.42,
      "reverse": 0.39
    }
  },
  "drop_volume": {
    "reagent_1": 0.048,  // mL per drop
    "reagent_2": 0.052
  }
}
```

## Volume Conversion

### Drops to mL

API test kits specify "drops" but pumps dispense volume:

```python
def drops_to_volume(reagent_id, num_drops):
    """
    Convert drops to mL for pump control
    """
    drop_volume = load_calibration("drop_volume", reagent_id)
    volume_ml = num_drops * drop_volume
    return volume_ml

# Example:
# Phosphate: 6 drops × 0.05 mL/drop = 0.30 mL
# Nitrate: 10 drops × 0.05 mL/drop = 0.50 mL
```

### Pump Run Time

```python
def volume_to_pump_time(pump_id, direction, volume_ml):
    """
    Calculate pump run time for desired volume
    """
    flow_rate = load_calibration("pump", pump_id, direction)
    run_time = volume_ml / flow_rate  # seconds
    return run_time

# Example:
# FeR pump: 0.30 mL ÷ 0.42 mL/s = 0.71 seconds
```

## Colorimeter Control

### AS7341 Integration

```python
import adafruit_as7341

# Initialize sensor
i2c = board.I2C()
sensor = adafruit_as7341.AS7341(i2c)

# Configure sensor
sensor.atime = 100  # Integration time
sensor.astep = 999  # Step size
sensor.gain = adafruit_as7341.Gain.GAIN_128X

def read_colorimeter(wavelength):
    """
    Read absorbance at specific wavelength

    wavelength: 528 (nitrate) or 625 (phosphate)
    Returns: absorbance (unitless)
    """
    # Read all channels
    channels = sensor.all_channels

    if wavelength == 528:
        # Use F4 channel (527 nm center)
        intensity = channels[3]  # F4
    elif wavelength == 625:
        # Use F7 channel (630 nm center)
        intensity = channels[6]  # F7
    else:
        raise ValueError("Invalid wavelength")

    # Convert intensity to absorbance
    # A = -log10(I/I0)
    # I0 = reference intensity (measured during baseline)
    absorbance = -math.log10(intensity / reference_intensity[wavelength])

    return absorbance

def zero_colorimeter(wavelength):
    """
    Set baseline (I0) with blank or sample
    """
    global reference_intensity

    channels = sensor.all_channels

    if wavelength == 528:
        reference_intensity[528] = channels[3]
    elif wavelength == 625:
        reference_intensity[625] = channels[6]
```

### LED Control

```python
import board
import digitalio

# Setup LEDs
led_green = digitalio.DigitalInOut(board.D11)
led_green.direction = digitalio.Direction.OUTPUT

led_red = digitalio.DigitalInOut(board.D12)
led_red.direction = digitalio.Direction.OUTPUT

def set_led(led_id, state):
    """
    Control colorimeter LEDs
    """
    if led_id == "GREEN_528nm":
        led_green.value = (state == "ON")
    elif led_id == "RED_625nm":
        led_red.value = (state == "ON")
```

### Bubble Mixing Control

```python
import time

def mix_by_bubbling(pump, duration=3.0):
    """
    Mix solution by reversing pump to create air bubbles

    Args:
        pump: FeW (for cuvette) or FeR (for reagent bottles)
        duration: How long to reverse pump (seconds)

    Creates air bubbles that rise through liquid for mixing.
    Replaces mechanical stirrers with simplified pump reversal.
    """
    # Reverse pump direction to pull air into line
    if pump == "FeW":
        # Cuvette mixing
        set_pump_direction(FeW, REVERSE)
        time.sleep(duration)
        set_pump_direction(FeW, STOP)
    elif pump == "FeR":
        # Reagent bottle mixing
        set_pump_direction(FeR, REVERSE)
        time.sleep(duration)
        set_pump_direction(FeR, STOP)

def set_pump_direction(pump, direction):
    """
    Control H-bridge for bidirectional pump operation

    Args:
        pump: FeW or FeR
        direction: FORWARD, REVERSE, or STOP
    """
    if pump == "FeW":
        if direction == FORWARD:
            pump_few_in1.value = True
            pump_few_in2.value = False
        elif direction == REVERSE:
            pump_few_in1.value = False
            pump_few_in2.value = True
        else:  # STOP
            pump_few_in1.value = False
            pump_few_in2.value = False

    elif pump == "FeR":
        if direction == FORWARD:
            pump_fer_in1.value = True
            pump_fer_in2.value = False
        elif direction == REVERSE:
            pump_fer_in1.value = False
            pump_fer_in2.value = True
        else:  # STOP
            pump_fer_in1.value = False
            pump_fer_in2.value = False
```

## User Interface

### Menu System

```
┌─────────────────────────┐
│     OpenReef v1.0       │
│                         │
│  ► Run Test             │
│    Calibration          │
│    System               │
│    Settings             │
│                         │
│  [A] Select  [B] Back   │
└─────────────────────────┘
```

### Display During Test

```
┌─────────────────────────┐
│   Phosphate Assay       │
│                         │
│  Step: Incubating       │
│  Time: 3:45 remaining   │
│                         │
│  ████████░░░░░░  50%    │
│                         │
│  [B] Abort              │
└─────────────────────────┘
```

### Result Display

```
┌─────────────────────────┐
│   Phosphate Result      │
│ ━━━━━━━━━━━━━━━━━━━━━  │
│                         │
│  0.25 ppm PO₄           │
│                         │
│  Absorbance: 0.142      │
│  Status: ✓ Valid        │
│  Time: 14:23:45         │
│                         │
│  [A] Save  [B] Discard  │
└─────────────────────────┘
```

## Error Handling

### Common Errors

```python
class AssayError(Exception):
    pass

# Pump timeout
if pump_running_time > max_time:
    raise AssayError("Pump timeout - check for air in lines")

# Absorbance out of range
if absorbance < 0:
    raise AssayError("Negative absorbance - check baseline")
if absorbance > max_calibration:
    raise AssayError("Absorbance too high - dilute sample")

# Valve failure
if not valve_actuated():
    raise AssayError("Valve failure - check connections")
```

### Error Recovery

1. **Pump Timeout**: Stop pump, notify user, offer to retry or abort
2. **High Absorbance**: Suggest dilution, offer to re-run with diluted sample
3. **Sensor Error**: Re-initialize I2C, check connections
4. **Low Battery**: Save state, prompt to connect power

## Firmware Architecture

### Main Loop

```python
def main():
    """
    Main firmware loop
    """
    # Initialize hardware
    init_display()
    init_pumps()  # Includes H-bridge for bidirectional control
    init_valves()
    init_colorimeter()

    # Load calibration data
    load_calibrations()

    while True:
        # Display main menu
        choice = show_main_menu()

        if choice == "RUN_PHOSPHATE":
            try:
                result = run_phosphate_assay()
                save_result(result)
            except AssayError as e:
                display_error(str(e))

        elif choice == "RUN_NITRATE":
            try:
                result = run_nitrate_assay()
                save_result(result)
            except AssayError as e:
                display_error(str(e))

        elif choice == "CALIBRATION":
            run_calibration_wizard()

        elif choice == "SYSTEM":
            system_diagnostics()

        elif choice == "SETTINGS":
            settings_menu()
```

### File Structure

```
/firmware/
├── code.py                 # Main entry point
├── lib/
│   ├── adafruit_as7341.py  # Colorimeter driver
│   ├── display_ui.py       # PyBadge display functions
│   └── pump_control.py     # Pump/valve control
├── assays/
│   ├── phosphate.py        # Phosphate assay sequence
│   └── nitrate.py          # Nitrate assay sequence
├── calibration/
│   ├── phosphate_cal.json  # Phosphate calibration data
│   ├── nitrate_cal.json    # Nitrate calibration data
│   └── pump_cal.json       # Pump calibration data
└── config.py               # System configuration
```

## Configuration File

```python
# config.py

# Pump GPIO pins
PUMP_FEW_IN1 = board.D3
PUMP_FEW_IN2 = board.D4
PUMP_FER_IN1 = board.D5
PUMP_FER_IN2 = board.D6

# Valve GPIO pins (relay channels)
VALVE_REV = board.D0
VALVE_WTV = board.D1
VALVE_WAV = board.D2

# LED pins
LED_GREEN_528 = board.D11
LED_RED_625 = board.D12

# Assay timing (seconds)
PHOSPHATE_INCUBATION_TIME = 450  # 7.5 minutes
NITRATE_INCUBATION_TIME = 300    # 5 minutes

# Safety limits
MAX_PUMP_RUN_TIME = 30  # seconds
MAX_ABSORBANCE = 3.0
MIN_ABSORBANCE = -0.1

# Data logging
SD_CARD_ENABLED = True
LOG_FILE_PATH = "/sd/data/"
```

## Next Steps

- Review [Calibration Guide](../calibration/calibration-guide.md) for calibration procedures
- See [Hardware Documentation](../hardware/parts-list.md) for wiring details
- Check example CircuitPython code in `/firmware/` directory (coming soon)
