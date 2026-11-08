# OpenReef CAD Files

This directory contains CAD design files for the OpenReef automated assay system enclosure and mounting components.

## Design Philosophy

The OpenReef enclosure builds upon the excellent open-source designs from [IoRodeo's Open Colorimeter project](https://www.iorodeo.com/collections/colorimeter):

- **Cuvette Holder**: Reused with minor modifications
- **PyBadge Integration**: Adapted from IoRodeo design
- **Expanded Enclosure**: New design accommodating pumps, valves, and reagent bottles

## License

OpenReef CAD files: **MIT License**

Based on IoRodeo designs: **Creative Commons Attribution 4.0 International (CC BY 4.0)**
- Original designs: https://github.com/iorodeo/open_colorimeter_enclosure
- Attribution: IO Rodeo Inc.

## File Types

- **`.FCStd`**: FreeCAD source files (editable)
- **`.step`**: STEP format (CAD interchange, editable in most CAD programs)
- **`.stl`**: STL format (3D printable, non-editable)
- **`.scad`**: OpenSCAD parametric source files (text-based, editable)

## Software Requirements

### FreeCAD (Recommended for Open Source)
- **Download**: https://www.freecadweb.org
- **Version**: 0.20 or newer
- **Free**: Open-source, cross-platform

### Fusion 360 (Recommended for Ease of Use)
- **Download**: https://www.autodesk.com/products/fusion-360
- **Version**: Latest
- **Free**: For personal/hobbyist use
- **See**: `fusion360_guide.md` for detailed import/conversion instructions

### OpenSCAD (For parametric parts)
- **Download**: https://openscad.org
- **Version**: 2021.01 or newer
- **Free**: Open-source, text-based CAD

## Directory Structure

```
cad/
├── README.md (this file)
├── specifications.md
├── fusion360_guide.md
├── enclosure/
│   ├── openreef_enclosure.FCStd
│   ├── openreef_enclosure.step
│   └── openreef_enclosure.stl
├── cuvette_holder/
│   ├── cuvette_holder_dual_led.FCStd
│   ├── cuvette_holder_dual_led.step
│   └── cuvette_holder_dual_led.stl
├── bottle_caps/
│   ├── bottle_cap_3port.scad
│   └── bottle_cap_3port.stl
├── mounting/
│   ├── pump_mount.scad
│   ├── pump_mount.stl
│   ├── valve_plate.scad
│   └── valve_plate.stl
└── assembly/
    ├── assembly_guide.md
    └── assembly_diagram.svg
```

## Components Overview

### 1. Main Enclosure
- **File**: `enclosure/openreef_enclosure.FCStd`
- **Dimensions**: 350 × 250 × 300 mm (W × D × H)
- **Material**: 3D printed PLA or PETG, or laser-cut acrylic
- **Features**:
  - PyBadge front panel mount
  - 4× bottle holder recesses
  - Pump mounting brackets
  - Valve mounting plate
  - Electronics bay
  - Cable management

### 2. Cuvette Holder
- **File**: `cuvette_holder/cuvette_holder_dual_led.FCStd`
- **Based on**: IoRodeo cuvette holder with flanged 5mm LED
- **Modifications**:
  - Dual LED mounts (528nm + 625nm)
  - AS7341 sensor mount
  - Magnetic stirrer cavity
  - Light-tight design

### 3. Bottle Caps
- **File**: `bottle_caps/bottle_cap_3port.scad`
- **Type**: Parametric OpenSCAD
- **Sizes**: Adjustable for common bottle threads
- **Features**:
  - 3× tube pass-throughs (6mm, 4mm, 2mm)
  - Air vent
  - O-ring groove for seal

### 4. Mounting Brackets
- **Pump Mount**: `mounting/pump_mount.scad`
- **Valve Plate**: `mounting/valve_plate.scad`
- **Material**: 3D printed PETG or laser-cut acrylic

## Printing Guidelines

### 3D Printing Settings

**Main Enclosure:**
- Layer height: 0.2mm
- Infill: 20%
- Supports: Yes (for overhangs)
- Material: PLA or PETG
- Print time: ~24-48 hours (depending on printer)

**Cuvette Holder:**
- Layer height: 0.15mm (higher precision)
- Infill: 50%
- Supports: Yes
- Material: Black PLA/PETG (light blocking)
- Print orientation: As designed (flanged side down)

**Bottle Caps:**
- Layer height: 0.2mm
- Infill: 30%
- Supports: Minimal
- Material: PETG (chemical resistant)
- Threaded parts: Print slowly for better threads

**Mounting Brackets:**
- Layer height: 0.2mm
- Infill: 40%
- Supports: As needed
- Material: PETG (strength)

### Alternative: Laser Cutting

For enclosure panels:
- Material: 3mm acrylic or plywood
- Export: 2D DXF from FreeCAD
- Joints: Use slots/tabs or screw assembly

## Modifications Guide

### Adjusting Dimensions

**FreeCAD:**
1. Open `.FCStd` file in FreeCAD
2. Expand "Spreadsheet" in model tree
3. Modify dimensional parameters
4. Model updates automatically

**OpenSCAD:**
1. Open `.scad` file in text editor or OpenSCAD
2. Find parameter section at top of file
3. Change values (e.g., `bottle_diameter = 50;`)
4. Press F5 to preview, F6 to render

### Adding Custom Features

See `specifications.md` for detailed dimensions and mounting hole locations.

## Exporting for 3D Printing

### From FreeCAD:
1. Select part in model tree
2. File → Export → Select "STL Mesh"
3. Choose export location
4. Settings: Deviation 0.1mm, Angular deviation 20°

### From OpenSCAD:
1. Render model (F6)
2. File → Export → STL
3. Choose location and save

## Bill of Materials (Hardware)

In addition to 3D printed parts, you'll need:

| Item | Quantity | Purpose |
|------|----------|---------|
| M3 screws (10mm) | 20 | Panel assembly |
| M3 screws (20mm) | 8 | Pump mounting |
| M3 nuts | 28 | Fasteners |
| M2.5 screws (8mm) | 8 | PyBadge mount |
| Rubber feet | 4 | Bottom of enclosure |
| O-rings (various) | 4 | Bottle cap seals |

## Assembly Order

1. Print all components
2. Install cuvette holder in main enclosure
3. Mount pumps using pump brackets
4. Mount valves on valve plate
5. Install PyBadge in front panel
6. Install electronics in electronics bay
7. Route cables through cable channels
8. Install bottle holders and caps
9. Connect fluidics
10. Final testing

See `assembly/assembly_guide.md` for detailed instructions.

## Customization Examples

### Larger Bottle Holders
Edit `enclosure/openreef_enclosure.FCStd`:
- Locate "Bottle_Holder_Sketch"
- Modify diameter parameter
- Re-pocket operation

### Different PyBadge/Display
- Measure new display dimensions
- Edit front panel cutout sketch
- Adjust mounting holes

### Additional Valves
- Edit valve mounting plate
- Add mounting holes in grid pattern
- Update spacing parameter

## Troubleshooting

**3D printing issues:**
- Warping: Use heated bed, brim/raft
- Weak threads: Increase perimeters, slower print
- Support removal: Use breakaway or soluble supports

**FreeCAD issues:**
- Model not updating: Tools → "Recompute"
- Missing constraints: Sketch → Validate sketch
- Export errors: Check for degenerate faces

**OpenSCAD issues:**
- Model not appearing: Check for syntax errors
- Slow rendering: Reduce $fn parameter
- Non-manifold mesh: Use modifier `render()` or `difference()` carefully

## Contributing

Improvements welcome! If you modify the designs:
1. Document changes in comments
2. Update dimensional parameters
3. Export both STEP and STL
4. Test print if possible
5. Submit pull request

## References

- IoRodeo Open Colorimeter: https://www.iorodeo.com/collections/colorimeter
- FreeCAD Documentation: https://wiki.freecadweb.org
- OpenSCAD Manual: https://en.wikibooks.org/wiki/OpenSCAD_User_Manual
- 3D Printing Guide: https://www.simplify3d.com/support/print-quality-troubleshooting/

## Changelog

### v1.0 (2025-11-14)
- Initial design
- Based on IoRodeo Open Colorimeter v1r4
- Added automated fluidics support
- Parametric bottle caps and mounting brackets
