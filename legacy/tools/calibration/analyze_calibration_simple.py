#!/usr/bin/env python3
import sys

# Read calibration data from file
if len(sys.argv) > 1:
    filename = sys.argv[1]
else:
    filename = "calibrations.txt"

try:
    with open(filename, 'r') as f:
        data = f.read()
except FileNotFoundError:
    print(f"Error: File '{filename}' not found", file=sys.stderr)
    sys.exit(1)

lines = data.strip().split('\n')
concentration = []
absorbance = []

for line in lines:
    parts = line.split()
    concentration.append(float(parts[0]))
    absorbance.append(float(parts[1]))

# Average the replicates
from collections import defaultdict
conc_abs_dict = defaultdict(list)
for c, a in zip(concentration, absorbance):
    conc_abs_dict[c].append(a)

avg_data = []
for conc in sorted(conc_abs_dict.keys()):
    abs_list = conc_abs_dict[conc]
    avg_abs = sum(abs_list) / len(abs_list)
    avg_data.append((conc, avg_abs))

concentrations = [x[0] for x in avg_data]
absorbances = [x[1] for x in avg_data]

# Simple linear regression (y = mx + b where y=concentration, x=absorbance)
n = len(absorbances)
sum_x = sum(absorbances)
sum_y = sum(concentrations)
sum_xy = sum(a * c for a, c in zip(absorbances, concentrations))
sum_x2 = sum(a * a for a in absorbances)

slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
intercept = (sum_y - slope * sum_x) / n

# Output only fit coefficients and range
print(f""""fit_coef": [
  {slope:.6f},
  {intercept:.6f}
],
"range": {{
  "min": {min(absorbances):.2f},
  "max": {max(absorbances):.2f}
}}""")
