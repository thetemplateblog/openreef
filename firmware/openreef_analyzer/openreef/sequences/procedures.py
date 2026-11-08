"""The measurement procedures. Each is `async def proc(ctx) -> dict`.

Cell A (20 mL, pH electrode, stir bar) ....... alkalinity titration
Cell B (10 mL, 22 mm cuvette, AS7341) ........ phosphate / nitrate colorimetry
"""
from __future__ import annotations

import time
from typing import Any, Dict, List, Optional, Tuple

from ..chem import (gran_fit, standardize_acid, expected_acid_ul, evaluate, channel_absorbances,
                    DKH_PER_MEQ_L)
from ..config import ColorimetricProfile
from .engine import Context

UNITS = {"alkalinity": "dKH", "phosphate": "ppm", "nitrate": "ppm"}


# ----------------------------------------------------------------------------- fluid helpers
async def rinse_cell(ctx: Context, cell: str, times: int = 2) -> None:
    vol = ctx.cfg.hardware.cell(cell).volume_ml
    for i in range(times):
        await ctx.hw.pump_ml(f"FILL_{cell}", vol * 1.4)      # overflows a little
        await ctx.hw.pump_ml(f"DRAIN_{cell}", vol * 2.0)     # run dry
        await ctx.hw.sleep(1.0)


async def fill_cell(ctx: Context, cell: str) -> None:
    """Fill past the dip tube, then aspirate down to the tube tip = fixed volume."""
    vol = ctx.cfg.hardware.cell(cell).volume_ml
    await ctx.hw.pump_ml(f"FILL_{cell}", vol * 1.3)
    await ctx.hw.sleep(2.0)                                   # let the surface settle
    await ctx.hw.pump_ml(f"LEVEL_{cell}", vol * 0.6)         # removes the excess, then draws air
    await ctx.hw.sleep(1.0)


async def ensure_homed(ctx: Context, pumps: List[str], cell: str) -> None:
    """Home any un-homed syringe pump while `cell` is empty, then rinse the
    ~60 uL the back-off stroke expelled to waste."""
    todo = [p for p in pumps if not ctx.hw.syringes[p].homed]
    if not todo:
        return
    for p in todo:
        await ctx.hw.home(p)
    await rinse_cell(ctx, cell, 1)


async def drain_cell(ctx: Context, cell: str) -> None:
    vol = ctx.cfg.hardware.cell(cell).volume_ml
    await ctx.hw.pump_ml(f"DRAIN_{cell}", vol * 2.0)


async def park_cell(ctx: Context, cell: str) -> None:
    """Leave the cell full of tank water so the electrode / cuvette stays wet."""
    vol = ctx.cfg.hardware.cell(cell).volume_ml
    await ctx.hw.pump_ml(f"FILL_{cell}", vol * 1.0)


# ----------------------------------------------------------------------------- alkalinity
async def alkalinity(ctx: Context, *, standard_ta_meq_l: Optional[float] = None,
                     store: bool = True) -> Dict[str, Any]:
    """Gran titration. With `standard_ta_meq_l` set, the run standardises the acid
    instead of reporting alkalinity."""
    p = ctx.cfg.chemistry.alkalinity
    v0_ul = p.sample_ml * 1000.0
    normality = ctx.db.get_setting("acid_normality", p.acid_normality)

    await ctx.step("rinse", 2)
    await rinse_cell(ctx, "A", 2)
    await ensure_homed(ctx, [ctx.cfg.chemistry.reagent(p.acid_reagent).pump], "A")
    await ctx.step("fill", 10)
    await fill_cell(ctx, "A")
    await ctx.hw.dc_on("STIR_A")
    await ctx.hw.sleep(15)
    temp = await ctx.hw.read_temp_c()
    ph0, _ = await ctx.hw.wait_ph_stable(p.stable_dph_per_s, p.stable_timeout_s)
    points: List[Tuple[float, float]] = [(0.0, ph0)]
    await ctx.step("initial_dose", 18, ph=round(ph0, 3), temp_c=round(temp, 2))

    # Size the first jump from the last result so we land just past equivalence.
    last = ctx.db.latest().get("alkalinity")
    guess_dkh = last["value"] if (last and standard_ta_meq_l is None) else None
    if standard_ta_meq_l is not None:
        guess_dkh = standard_ta_meq_l * DKH_PER_MEQ_L
    if guess_dkh:
        first = 0.97 * expected_acid_ul(guess_dkh, v0_ul, normality)
    else:
        first = p.initial_dose_ul
    first = min(first, p.max_total_ul * 0.8)

    total = 0.0
    total += await ctx.dispense(p.acid_reagent, first)
    await ctx.hw.sleep(8)
    ph, _ = await ctx.hw.wait_ph_stable(p.stable_dph_per_s, p.stable_timeout_s)
    points.append((total, ph))

    # Coarse approach: 200 uL steps until pH < 4.3 (just past equivalence).
    while ph > 4.3 and total < p.max_total_ul:
        total += await ctx.dispense(p.acid_reagent, 200.0)
        await ctx.hw.sleep(4)
        ph, _ = await ctx.hw.wait_ph_stable(p.stable_dph_per_s, p.stable_timeout_s)
        points.append((total, ph))
        await ctx.step("approach", 30, ph=round(ph, 3), acid_ul=round(total))

    # Fine steps through the Gran window.
    in_window = [pt for pt in points if p.gran_ph_min <= pt[1] <= p.gran_ph_max]
    while ph > p.gran_ph_min and len(in_window) < p.max_points and total < p.max_total_ul:
        total += await ctx.dispense(p.acid_reagent, p.step_ul)
        await ctx.hw.sleep(3)
        ph, stable = await ctx.hw.wait_ph_stable(p.stable_dph_per_s, p.stable_timeout_s)
        points.append((total, ph))
        in_window = [pt for pt in points if p.gran_ph_min <= pt[1] <= p.gran_ph_max]
        await ctx.step("titrate", 30 + 50 * len(in_window) / p.max_points,
                       ph=round(ph, 3), acid_ul=round(total), points=len(in_window))

    await ctx.hw.dc_off("STIR_A")
    await ctx.step("compute", 85)
    raw = {"points": points, "v0_ul": v0_ul, "acid_normality": normality, "temp_c": temp, "ph0": ph0}

    if standard_ta_meq_l is not None:
        new_n = standardize_acid(points, v0_ul, standard_ta_meq_l, p.gran_ph_min, p.gran_ph_max)
        cal_id = ctx.db.add_calibration("alkalinity", "acid_normality",
                                        {"normality": new_n, "standard_ta_meq_l": standard_ta_meq_l, "raw": raw})
        ctx.db.set_setting("acid_normality", new_n)
        result = {"acid_normality": new_n, "calibration_id": cal_id, "points": len(points)}
        await ctx.bus.publish("calibration", test="alkalinity", kind="acid_normality", normality=new_n)
    else:
        g = gran_fit(points, v0_ul, normality, p.gran_ph_min, p.gran_ph_max, p.min_points)
        raw.update({"v_eq_ul": g.v_eq_ul, "r2": g.r2, "slope": g.slope, "intercept": g.intercept,
                    "used_points": g.used_points})
        cal = ctx.db.active_calibration("alkalinity", "acid_normality")
        result = {"test": "alkalinity", "value": round(g.dkh, 3), "unit": "dKH",
                  "ta_meq_l": round(g.ta_meq_l, 4), "quality": round(g.quality, 3), "flags": g.flags,
                  "r2": round(g.r2, 6), "temp_c": round(temp, 2), "duration_s": round(ctx.elapsed(), 1)}
        if store:
            rid = ctx.db.add_result("alkalinity", g.dkh, "dKH", g.quality, g.flags, raw, temp,
                                    ctx.elapsed(), ctx.run_id, cal["id"] if cal else None)
            result["id"] = rid
            await ctx.bus.publish("result", **result)
            await check_limits(ctx, "alkalinity", g.dkh)

    await ctx.step("drain", 92)
    await drain_cell(ctx, "A")
    await rinse_cell(ctx, "A", 1)
    await park_cell(ctx, "A")
    await ctx.step("done", 100)
    return result


# ----------------------------------------------------------------------------- colorimetry
def _profile(ctx: Context, test: str) -> ColorimetricProfile:
    return ctx.cfg.chemistry.phosphate if test == "phosphate" else ctx.cfg.chemistry.nitrate


async def colorimetric(ctx: Context, test: str, *, standard_ppm: Optional[float] = None,
                       store: bool = True, kinetics_every_s: float = 0.0) -> Dict[str, Any]:
    """Self-blanked single-cell colorimetric measurement."""
    prof = _profile(ctx, test)
    coeffs = ctx.db.get_setting(f"{test}_cal_coeffs", prof.cal_coeffs)

    await ctx.step("rinse", 3)
    await rinse_cell(ctx, "B", 2)
    pumps = [ctx.cfg.chemistry.reagent(rid).pump for d in prof.doses for rid in d]
    await ensure_homed(ctx, pumps, "B")
    await ctx.step("fill", 12)
    await fill_cell(ctx, "B")
    await ctx.hw.dc_run("STIR_B", 5)       # dislodge bubbles
    await ctx.hw.sleep(8)                  # settle before optics
    temp = await ctx.hw.read_temp_c()

    await ctx.step("blank", 18)
    blank = await ctx.hw.read_absorbance_counts(prof.led, averages=16)

    pct = 22
    for i, dose in enumerate(prof.doses):
        for rid, ul in dose.items():
            await ctx.step(f"dose_{i+1}", pct, reagent=rid, ul=ul)
            await ctx.dispense(rid, ul)
        await ctx.hw.dc_run("STIR_B", prof.mix_s / max(1, len(prof.doses)))
        pct += 6

    t_react = time.time()
    curve: List[Dict[str, Any]] = []
    waited = 0.0
    while waited < prof.develop_s:
        chunk = min(prof.develop_s - waited, kinetics_every_s if kinetics_every_s > 0 else prof.develop_s)
        await ctx.hw.sleep(chunk)
        waited += chunk
        if kinetics_every_s > 0 and waited < prof.develop_s:
            counts = await ctx.hw.read_absorbance_counts(prof.led, averages=4)
            curve.append({"t_s": round(waited), "abs": channel_absorbances(blank, counts)})
        await ctx.step("develop", 40 + 45 * waited / prof.develop_s,
                       remaining_s=round(prof.develop_s - waited))

    await ctx.step("read", 88)
    sample = await ctx.hw.read_absorbance_counts(prof.led, averages=16)
    expected_ratio = ctx.db.get_setting(f"{test}_secondary_ratio", None)
    r = evaluate(blank, sample, prof.primary_channel, prof.secondary_channel, temp,
                 prof.temp_coeff_per_c, coeffs, prof.cal_abs_max, expected_ratio)

    raw = {"blank": blank, "sample": sample,
           "channels_abs": {k: round(v, 5) for k, v in channel_absorbances(blank, sample).items()},
           "primary": prof.primary_channel, "secondary": prof.secondary_channel,
           "develop_s": prof.develop_s, "temp_c": temp, "coeffs": coeffs, "kinetics": curve}

    cal = ctx.db.active_calibration(test, "curve")
    result: Dict[str, Any] = {"test": test, "unit": "ppm", "absorbance": round(r.absorbance_primary, 5),
                              "absorbance_25c": round(r.absorbance_25c, 5), "quality": round(r.quality, 3),
                              "flags": r.flags, "temp_c": round(temp, 2), "duration_s": round(ctx.elapsed(), 1)}
    if standard_ppm is not None:
        # calibration point: remember (absorbance, known conc) for the curve fit
        pts = ctx.db.get_setting(f"{test}_cal_points", [])
        pts.append({"abs": r.absorbance_25c, "ppm": standard_ppm, "ts": time.time(),
                    "secondary_ratio": (r.absorbance_secondary / r.absorbance_primary)
                    if (r.absorbance_secondary and r.absorbance_primary > 0.05) else None})
        ctx.db.set_setting(f"{test}_cal_points", pts)
        result.update({"standard_ppm": standard_ppm, "cal_points": len(pts)})
        await ctx.bus.publish("calibration_point", test=test, absorbance=r.absorbance_25c, ppm=standard_ppm)
    else:
        result["value"] = round(r.concentration, 3)
        if store:
            rid = ctx.db.add_result(test, r.concentration, "ppm", r.quality, r.flags, raw, temp,
                                    ctx.elapsed(), ctx.run_id, cal["id"] if cal else None)
            result["id"] = rid
            await ctx.bus.publish("result", **result)
            await check_limits(ctx, test, r.concentration)

    await ctx.step("drain", 94)
    await drain_cell(ctx, "B")
    await rinse_cell(ctx, "B", 2)          # reagent residue must not reach the next blank
    await park_cell(ctx, "B")
    await ctx.step("done", 100)
    return result


async def characterize(ctx: Context, test: str, standard_ppm: float, minutes: float = 40,
                       every_s: float = 30) -> Dict[str, Any]:
    """Record all 10 channels over time after dosing a known standard, to pick
    the wavelength and development time for a reagent kit."""
    prof = _profile(ctx, test)
    saved = prof.develop_s
    prof.develop_s = minutes * 60
    try:
        res = await colorimetric(ctx, test, standard_ppm=standard_ppm, store=False, kinetics_every_s=every_s)
    finally:
        prof.develop_s = saved
    # the kinetics curve is in the last calibration_point raw; store it as its own calibration record
    cal_id = ctx.db.add_calibration(test, "characterization", {"standard_ppm": standard_ppm, "result": res})
    res["calibration_id"] = cal_id
    return res


# ----------------------------------------------------------------------------- maintenance
async def prime(ctx: Context, reagent_id: str, ul: float = 7000.0) -> Dict[str, Any]:
    """Pull reagent through the lines: dispense ~1.5 syringe volumes into the
    (empty) cell and drain it to waste."""
    reagent = ctx.cfg.chemistry.reagent(reagent_id)
    cell = ctx.cfg.hardware.stepper(reagent.pump).cell
    await ctx.step("home", 10)
    await ctx.hw.home(reagent.pump)
    await ctx.step("prime", 40, reagent=reagent_id)
    await ctx.dispense(reagent_id, ul)
    await ctx.step("drain", 80)
    await drain_cell(ctx, cell)
    await rinse_cell(ctx, cell, 2)
    await ctx.step("done", 100)
    return {"primed_ul": ul, "reagent": reagent_id}


async def home_all(ctx: Context) -> Dict[str, Any]:
    names = [s.name for s in ctx.cfg.hardware.steppers]
    for i, n in enumerate(names):
        await ctx.step(f"home_{n}", 100 * i / len(names))
        await ctx.hw.home(n)
    await ctx.step("done", 100)
    return {"homed": names}


async def flush(ctx: Context) -> Dict[str, Any]:
    """Rinse both cells with tank water (e.g. after maintenance)."""
    await ctx.step("rinse_A", 10)
    await rinse_cell(ctx, "A", 3)
    await park_cell(ctx, "A")
    await ctx.step("rinse_B", 55)
    await rinse_cell(ctx, "B", 3)
    await park_cell(ctx, "B")
    await ctx.step("done", 100)
    return {"flushed": ["A", "B"]}


async def full_cycle(ctx: Context) -> Dict[str, Any]:
    a = await alkalinity(ctx)
    p = await colorimetric(ctx, "phosphate")
    n = await colorimetric(ctx, "nitrate")
    return {"alkalinity": a, "phosphate": p, "nitrate": n}


# ----------------------------------------------------------------------------- limits
async def check_limits(ctx: Context, test: str, value: float) -> None:
    lim = ctx.cfg.limits
    lo, hi = {"alkalinity": lim.alk_dkh, "phosphate": lim.po4_ppm, "nitrate": lim.no3_ppm}[test]
    if value < lo or value > hi:
        await ctx.hw.set_alarm(True)
        await ctx.bus.publish("alert", level="warning", code=f"{test}_out_of_range", test=test,
                              value=value, low=lo, high=hi,
                              message=f"{test} {value:.3g} outside {lo}-{hi}")
    else:
        # clear the alarm only if every latest value is in range
        latest = ctx.db.latest()
        all_ok = True
        for t, r in latest.items():
            l2, h2 = {"alkalinity": lim.alk_dkh, "phosphate": lim.po4_ppm, "nitrate": lim.no3_ppm}[t]
            if not (l2 <= r["value"] <= h2):
                all_ok = False
        if all_ok:
            await ctx.hw.set_alarm(False)
