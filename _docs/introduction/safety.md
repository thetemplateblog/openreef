---
title: Safety
summary: Acids, toxic reagents, 12 V near salt water and a tank full of animals — read this first.
---

<div class="callout warn"><strong>Reagents.</strong> 0.1 N HCl is corrosive; the Trident NP and lab-mixed nitrate reagents contain acids and, in the VCl₃ method, vanadium compounds that are toxic. Wear gloves and eye protection when handling bottles. Keep reagents below the analyzer so a failed check valve cannot siphon them into a cell.</div>

## Waste

- All waste goes to a 2 L HDPE bottle with a float switch. The Trident NP kit ships a waste neutralizer; add it at emptying.
- Never return waste or rinse water to the tank. The sample lines are one-way: intake only.
- Dispose of neutralised waste per local rules; small hobby volumes are usually acceptable to drain with plenty of water, but check.

## Electrical

- Everything inside the wet bay is 12 V DC or lower. The 120/230 V brick stays outside the enclosure.
- Separate wet and dry bays with the bulkhead; pass cables through grommets above the highest liquid level.
- The EZO-pH carrier is electrically isolated — keep its ground separate from the motor return, or pH will jump when pumps run.
- Fuse the 12 V input at 5 A.

## Interlocks in software

| Condition | Response |
|---|---|
| Leak sensor wet | Abort run, all pumps off, alarm relay on, `alert` event |
| Waste float closed | Refuse to start a run; abort if it closes mid-run |
| Syringe not homed | Refuse to dispense (homing expels ~60 µL and must happen into an empty cell) |
| Reagent remaining < 10 % | `reagent_low` event; the run still proceeds |
| Result outside limits | Alarm relay on, `alert` event, Hydros rule evaluation |
| Service crash | `systemd` restarts it; `ExecStopPost` de-asserts the stepper enable |
| Watchdog | `check_safety()` runs before every pump action and in every `sleep()` |

## Biological

- Pull sample from a high-flow area of the sump through a 100 µm filter, not from the display.
- A stuck fill pump can only move about 1.4 mL/s and stops when the cell overflows into the drip tray, which trips the leak sensor. Keep the drain line's free end above the waste liquid level so it cannot siphon.
- Alkalinity dosing automations (via Hydros rules or your controller) should always have a maximum daily dose independent of this analyzer.
