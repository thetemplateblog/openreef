"""Absorbance and concentration calculations for the optical cell."""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np


def absorbance(i0: float, i: float) -> float:
    """Beer-Lambert absorbance from dark-subtracted blank and sample counts."""
    if i0 <= 0 or i <= 0:
        return float("nan")
    return math.log10(i0 / i)


def channel_absorbances(blank: Dict[str, float], sample: Dict[str, float]) -> Dict[str, float]:
    return {k: absorbance(blank[k], sample[k]) for k in blank if k in sample}


def temp_correct(a: float, temp_c: float, coeff_per_c: float, ref_c: float = 25.0) -> float:
    """Normalise absorbance to 25 C: A25 = A / (1 + k*(T-25))."""
    return a / (1.0 + coeff_per_c * (temp_c - ref_c))


def concentration(a: float, coeffs: Sequence[float]) -> float:
    """conc = c0 + c1*A + c2*A^2 ..."""
    return float(sum(c * a ** n for n, c in enumerate(coeffs)))


def fit_calibration(pairs: Sequence[Tuple[float, float]], degree: int = 1,
                    through_zero: bool = False) -> Tuple[List[float], float]:
    """Fit conc = f(A) from (absorbance, known_conc) pairs. Returns (coeffs, R^2)."""
    a = np.array([p[0] for p in pairs], dtype=float)
    c = np.array([p[1] for p in pairs], dtype=float)
    need = degree if through_zero else degree + 1
    if len(a) < need:
        raise ValueError(f"not enough calibration points (need {need})")
    if through_zero:
        # least squares without intercept
        X = np.vstack([a ** n for n in range(1, degree + 1)]).T
        beta, *_ = np.linalg.lstsq(X, c, rcond=None)
        coeffs = [0.0] + list(beta)
    else:
        poly = np.polyfit(a, c, degree)       # highest power first
        coeffs = list(poly[::-1])
    pred = np.array([concentration(x, coeffs) for x in a])
    ss_res = float(np.sum((c - pred) ** 2))
    ss_tot = float(np.sum((c - c.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 1.0
    return [float(x) for x in coeffs], r2


@dataclass
class ColorResult:
    absorbance_primary: float
    absorbance_secondary: Optional[float]
    absorbance_25c: float
    concentration: float
    temp_c: float
    quality: float
    flags: List[str] = field(default_factory=list)
    channels_blank: Dict[str, float] = field(default_factory=dict)
    channels_sample: Dict[str, float] = field(default_factory=dict)


def evaluate(blank: Dict[str, float], sample: Dict[str, float], primary: str,
             secondary: Optional[str], temp_c: float, temp_coeff: float,
             coeffs: Sequence[float], abs_max: float,
             expected_ratio: Optional[float] = None) -> ColorResult:
    """Turn a blank/sample pair of channel readings into a concentration."""
    a_all = channel_absorbances(blank, sample)
    a_p = a_all[primary]
    a_s = a_all.get(secondary) if secondary else None
    flags: List[str] = []
    quality = 1.0

    if math.isnan(a_p):
        raise ValueError("invalid counts")
    if a_p < -0.02:
        flags.append("negative_absorbance")
        quality *= 0.3
    if a_p > abs_max:
        flags.append("over_range")
        quality *= 0.2
    if blank[primary] < 500:
        flags.append("low_light")      # LED failing, dirty cell or wrong gain
        quality *= 0.5
    if a_s is not None and expected_ratio and a_p > 0.05:
        ratio = a_s / a_p
        if abs(ratio - expected_ratio) / expected_ratio > 0.25:
            flags.append("spectral_shape_mismatch")   # bubbles, precipitate, wrong reagent
            quality *= 0.5

    a25 = temp_correct(max(a_p, 0.0), temp_c, temp_coeff)
    conc = max(0.0, concentration(a25, coeffs))
    return ColorResult(absorbance_primary=a_p, absorbance_secondary=a_s, absorbance_25c=a25,
                       concentration=conc, temp_c=temp_c, quality=quality, flags=flags,
                       channels_blank=dict(blank), channels_sample=dict(sample))
