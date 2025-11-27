# Calibration Analysis Tools

This folder contains tools for analyzing colorimeter calibration data.

## analyze_calibration_simple.py

A Python script that performs linear regression on calibration data and outputs fit coefficients and absorbance range.

### Usage

```bash
# Use the included sample data
python3 analyze_calibration_simple.py

# Or specify your own data file
python3 analyze_calibration_simple.py your_data.txt
```

### Input Format

The input file should contain space-separated concentration and absorbance values, one pair per line:

```
0.0  0.00
1.25  0.72
2.5  1.23
3.75  1.68
5.0  1.97
...
```

The script will automatically average multiple readings at the same concentration.

### Output Format

The script outputs JSON-formatted calibration coefficients and range:

```json
"fit_coef": [
  3.500142,
  -1.194604
],
"range": {
  "min": 0.00,
  "max": 2.79
}
```

These values can be directly inserted into your `calibrations.json` file in the firmware.

### How It Works

1. Reads calibration data from file
2. Averages multiple readings at the same concentration
3. Performs linear regression: `concentration = slope * absorbance + intercept`
4. Outputs the slope and intercept as fit coefficients
5. Calculates the min/max absorbance range

## Sample Data

`calibrations.txt` contains sample calibration data for testing the script.
