---
title: Enclosure
summary: A laser-cut acrylic box with a wet bay and a dry bay, plus the printed parts that live inside it.
---

## Layout

Outer size 420 W × 460 H × 200 D mm. A full-height bulkhead splits a 260 mm **wet bay** (left) from a 160 mm **dry bay** (right). Electronics never share air with liquids; cables pass through grommets in the bulkhead above the highest liquid level.

```
 front view                                 side view
 ┌──────────────────────────┬────────────┐  ┌──────────────┐
 │ cells shelf   z=330      │ Pi + carrier│  │  door  │     │
 │  [Cell A] [Cell B]       │ MCP · MOSFET│  │        │ dry │
 ├──────────────────────────┤ relay       │  │  wet   │     │
 │ syringe pump bank z=200  │             │  │  bay   │ bay │
 │  [SP1][SP2][SP3][SP4][SP5]│ PSU in      │  │        │     │
 ├──────────────────────────┤ fan         │  │drip tray│    │
 │ bottle tray   z=20       │             │  └──────────────┘
 │  ○ ○ ○ ○ ○ (acid)        │             │
 └──────────────────────────┴────────────┘
    waste bottle below, outside
```

Peristaltic pumps mount on the wet face of the bulkhead so tube runs to both cells are short. The drip tray covers the whole wet-bay floor with the leak sensor at its low corner.

## Panels

![Panel layout](/assets/img/panels.svg)

`hardware/analyzer/cad/panels.svg` is the cut file: red = cut, blue = engrave, dimensions in millimetres (1 user unit = 1 mm; import at 100 % scale). Base, back and bottle tray are 6 mm; everything else 3 mm. Joints are butt joints with 16 printed corner brackets (`corner_bracket.scad`) and M3 heat-set inserts — no tab-and-slot, so panel thickness tolerance does not matter. The front door is clear acrylic on two hinges with a magnet catch.

## Printed parts

| Part | File | Qty | Material | Notes |
|---|---|---|---|---|
| Syringe pump frame, carriage, plunger clip | `syringe_pump.scad` | 5 sets | PETG | 4 walls, 30 % infill |
| Cell A cap | `cell_a_cap.scad` | 1 | PETG | 100 % infill plug; 38 × 2 mm O-ring |
| Cell B holder body | `cell_b_holder.scad` (part="body") | 1 | **black** PETG | 100 % infill walls for light-tightness |
| Cell B lid | `cell_b_holder.scad` (part="lid") | 1 | PETG | |
| Corner bracket | `corner_bracket.scad` | 16 | PETG | |
| Stir drive mount | included in cell holder shelf cut-out | 2 | — | 40 mm fan + 2 magnets |

Set `part` at the top of each SCAD file to export individual STLs. The OpenSCAD files are parametric: syringe diameter, stroke, lead-screw pitch, cuvette diameter and tube diameters are variables at the top.

## Assembly notes

- Dry-fit the panels with brackets before inserting the heat-set inserts; mark the bracket positions.
- Mount the bottle tray 20 mm above the base so spilled reagent runs into the drip tray, not under the tray.
- Route all tubing so that free ends are above liquid levels — no siphons.
- Put the 60 mm fan in the dry bay back panel blowing out; intake slots in the right side panel. The TMC2209 drivers barely warm up, but the PSU brick should stay outside.
- Label every tube at both ends before you close the door. Future you will thank you.
