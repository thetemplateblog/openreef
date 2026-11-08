"""Gran-function evaluation of an alkalinity titration.

Given (acid volume, pH) pairs in the excess-acid region, the Gran function
    F = (V0 + v) * 10**(-pH)
is linear in v and crosses zero at the equivalence volume v_eq.
Total alkalinity TA = c_acid * v_eq / V0.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Sequence, Tuple

import numpy as np

DKH_PER_MEQ_L = 2.8   # 1 meq/L = 2.8 dKH (50 ppm CaCO3)
PK1_SEAWATER = 5.86   # first carbonic acid constant, S=35, 25 C (free scale), Millero 2010


@dataclass
class GranResult:
    v_eq_ul: float
    ta_meq_l: float               # DIC-corrected (primary)
    dkh: float
    slope: float
    intercept: float
    r2: float
    n_points: int
    residual_rms: float
    used_points: List[Tuple[float, float]] = field(default_factory=list)
    quality: float = 0.0          # 0..1
    flags: List[str] = field(default_factory=list)
    ta_classic_meq_l: float = 0.0 # plain Gran extrapolation, for comparison
    dic_est_mmol_l: float = 0.0   # by-product of the correction


def gran_fit(points: Sequence[Tuple[float, float]], v0_ul: float, acid_normality: float,
             ph_min: float = 3.0, ph_max: float = 3.8, min_points: int = 5,
             pk1: float = PK1_SEAWATER) -> GranResult:
    """points: [(acid_ul, pH), ...] cumulative acid volume and measured pH.

    Two estimates are produced:
    * classic Gran: straight line through F = (V0+v)*10^-pH, x-intercept = v_eq.
    * DIC-corrected: below pH 4 the charge balance is
          [H+] = CT_v*K1/[H+] - TA_remaining,
      so  (V0+v)[H+] - c*v = -TA0*V0 + CT0 * (V0*K1/[H+]),
      a straight line in x = V0*K1/[H+] whose intercept gives TA0 directly and
      whose slope is the DIC.  This removes the 2-5 % low bias the classic
      extrapolation has in seawater when the window reaches pH 3.8.
    """
    pts = [(v, ph) for v, ph in points if ph_min <= ph <= ph_max]
    flags: List[str] = []
    if len(pts) < min_points:
        raise ValueError(f"only {len(pts)} points in Gran window {ph_min}-{ph_max} (need {min_points})")

    v = np.array([p[0] for p in pts], dtype=float)
    ph = np.array([p[1] for p in pts], dtype=float)
    f = (v0_ul + v) * 10.0 ** (-ph)

    slope, intercept = np.polyfit(v, f, 1)
    if slope <= 0:
        raise ValueError("Gran slope not positive; titration did not pass equivalence")
    pred = slope * v + intercept
    ss_res = float(np.sum((f - pred) ** 2))
    ss_tot = float(np.sum((f - f.mean()) ** 2)) or 1e-30
    r2 = 1.0 - ss_res / ss_tot
    rms = float(np.sqrt(ss_res / len(v))) / float(np.max(f))   # relative rms

    v_eq_classic = -intercept / slope
    ta_classic = acid_normality * v_eq_classic / v0_ul * 1000.0   # (eq/L * uL/uL) -> meq/L

    # DIC-corrected estimate (see docstring). Units: v, V0 in uL; H in mol/L; c in eq/L.
    h = 10.0 ** (-ph)
    k1 = 10.0 ** (-pk1)
    y = (v0_ul + v) * h - acid_normality * v
    x = v0_ul * k1 / h
    b, a = np.polyfit(x, y, 1)              # y = a + b*x
    ta0 = -a / v0_ul                         # eq/L
    ct0 = b                                  # mol/L
    ta = ta0 * 1000.0
    v_eq = ta0 * v0_ul / acid_normality
    if ct0 < 0 or ct0 > 2.0 * ta0:
        flags.append("dic_estimate_implausible")
    if v_eq <= 0 or v_eq >= v.min():
        flags.append("v_eq_outside_expected")
    dkh = ta * DKH_PER_MEQ_L

    quality = max(0.0, min(1.0, (r2 - 0.995) / 0.005)) if r2 > 0.995 else 0.0
    if rms > 0.01:
        quality *= 0.5
        flags.append("noisy_fit")
    if r2 < 0.999:
        flags.append("low_r2")

    return GranResult(v_eq_ul=float(v_eq), ta_meq_l=float(ta), dkh=float(dkh), slope=float(slope),
                      intercept=float(intercept), r2=float(r2), n_points=len(v), residual_rms=rms,
                      used_points=[(float(p), float(q)) for p, q in zip(v, ph)], quality=quality,
                      flags=flags, ta_classic_meq_l=float(ta_classic), dic_est_mmol_l=float(ct0 * 1000.0))


def standardize_acid(points: Sequence[Tuple[float, float]], v0_ul: float, known_ta_meq_l: float,
                     ph_min: float = 3.0, ph_max: float = 3.8) -> float:
    """Return the acid normality (eq/L) that makes the Gran fit reproduce a
    reference standard of known alkalinity (e.g. 1.887 meq/L Na2CO3)."""
    # The DIC-corrected estimate depends on the assumed normality, so solve
    # TA(c) = known by bisection (TA is monotonic in c).
    lo, hi = 0.001, 0.5
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        ta = gran_fit(points, v0_ul, acid_normality=mid, ph_min=ph_min, ph_max=ph_max).ta_meq_l
        if ta < known_ta_meq_l:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def expected_acid_ul(dkh: float, v0_ul: float, acid_normality: float) -> float:
    """Acid volume to reach equivalence for a guessed alkalinity; used to size the first dose."""
    ta_eq_l = dkh / DKH_PER_MEQ_L / 1000.0
    return ta_eq_l * v0_ul / acid_normality
