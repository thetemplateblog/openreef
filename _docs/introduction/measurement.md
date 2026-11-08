---
title: How it measures
summary: The three methods in one page; each has its own chapter under Chemistry.
---

## Alkalinity: Gran titration

Acid is added to a stirred 20.0 mL sample in small increments while the electrode records pH. Past the equivalence point every drop of acid adds free H⁺, so the Gran function

<div class="math">F(v) = (V₀ + v) · 10^(−pH)</div>

is a straight line in acid volume *v*, and its x-intercept is the equivalence volume. Total alkalinity is `TA = c_HCl · v_eq / V₀`, and `dKH = 2.80 × TA (meq/L)`. Only the slope of the line matters, so the electrode's absolute offset drops out. OpenReef adds a dissolved-inorganic-carbon correction (see [Alkalinity](/docs/chemistry/alkalinity/)) that removes the 2–5 % low bias the plain extrapolation has in seawater when the window reaches pH 3.8.

## Phosphate: molybdenum blue

Orthophosphate + molybdate + antimony in acid → phosphomolybdate, reduced by ascorbic acid to an intense blue (APHA 4500-P E). Molar absorptivity is about 22 000 L·mol⁻¹·cm⁻¹ at 880 nm; in a 22 mm cuvette 0.01 ppm PO₄ is an absorbance of ≈0.005, which the AS7341 resolves after dark subtraction and averaging.

## Nitrate: reduction + Griess

Nitrate is reduced to nitrite, which couples with sulfanilamide and NEDD into a pink azo dye read at 540 nm. The Trident NP kit does this as a liquid, automation-ready reagent set; the open-literature equivalent is the vanadium(III) chloride method (Schnetger & Lehners 2014, *Marine Chemistry* 160:91–98). Reef nitrite is negligible, so NO₃ + NO₂ is reported as nitrate.

## Self-blanking

Cell B is filled with sample and read (I₀) **before** reagent is added, then read again (I) after development. Absorbance `A = log₁₀((I₀−D)/(I−D))` with D the dark reading. Turbidity, yellow dissolved organics and cuvette scratches cancel, and no DI-water blank is needed between tests.

## Why an 11-channel sensor

One AS7341 covers 540 nm, 680 nm and NIR with programmable gain (0.5×–512×) and integration time. Each test reads a primary and a secondary channel; their ratio is a spectral-shape check that flags bubbles, precipitate or a wrong reagent. It also makes **reagent characterisation** possible: dose a known standard and record all channels every 30 s to find where absorbance plateaus, with no spectrophotometer.

## Volume metering without precision pumps

Cells are overfilled by a cheap peristaltic pump, then a second pump aspirates from a dip tube whose tip sits at the 20 mL (Cell A) or 10 mL (Cell B) mark until it draws air. The tube tip sets the volume to about ±1 %, and the calibration against a reference standard absorbs the rest. Only the five syringe pumps need to be precise: 0.07 µL per microstep.
