# FreeCAD Modification Guide - OpenReef Enclosure

This guide explains how to adapt the IoRodeo Open Colorimeter enclosure design for the OpenReef automated assay system.

## Prerequisites

- **FreeCAD** 0.20 or newer installed
- **IoRodeo source files** from `/Users/davidchilds/Documents/Repositories/open_colorimeter_enclosure/`
- Basic FreeCAD knowledge (or willingness to learn)

## Overview of Changes

The OpenReef system requires the following modifications to the original IoRodeo design:

1. **Expand enclosure dimensions** (350 × 250 × 300 mm)
2. **Add bottle holders** (4× recesses for RO, test water, 2 reagents)
3. **Add pump mounting points** (2× peristaltic pumps)
4. **Add valve mounting** (bottom plate for 3× solenoid valves)
5. **Expand electronics bay** (larger space for motor driver, relay, solenoid driver)
6. **Add cable management** (channels and tie points)
7. **Keep PyBadge mount** (reuse existing design)
8. **Keep cuvette holder** (minor modifications for dual LED)

## Step 1: Open and Save Original Files

### 1.1 Open IoRodeo Enclosure

```
File → Open
Navigate to: /Users/davidchilds/Documents/Repositories/open_colorimeter_enclosure/
Open: colorimeter_enclosure.FCStd
```

### 1.2 Save As New Project

```
File → Save As
Name: openreef_enclosure.FCStd
Location: /Users/davidchilds/Documents/Repositories/openreef/hardware/cad/enclosure/
```

### 1.3 Open PyBadge Cover

```
File → Open
Open: pybadge_cover.FCStd
```

Save as: `openreef_pybadge_cover.FCStd`

## Step 2: Modify Enclosure Dimensions

### 2.1 Locate Spreadsheet

In the Model tree (left panel):
- Expand "colorimeter_enclosure"
- Look for "Spreadsheet" or "Parameters"
- Double-click to open

### 2.2 Update Dimensions

If there's a spreadsheet, modify these parameters:

| Parameter | Original | New (OpenReef) |
|-----------|----------|----------------|
| `length` | ~150 mm | 350 mm |
| `width` | ~120 mm | 250 mm |
| `height` | ~100 mm | 300 mm |
| `wall_thickness` | 3 mm | 3 mm (keep) |

If no spreadsheet exists, you'll need to edit individual sketches (more tedious).

### 2.3 Manual Dimension Editing (if no spreadsheet)

For each sketch defining the enclosure:
1. Double-click the sketch in the tree
2. Click a dimension
3. Enter new value
4. Press Enter
5. Click "Close" to exit sketch editing
6. Model should update automatically

If model doesn't update:
```
Tools → Recompute
```

## Step 3: Add Bottle Holders

### 3.1 Create Bottle Holder Sketch

1. Select the **base (top) face** of the enclosure
2. Click "Create Sketch" (or Sketch → New Sketch)
3. Draw 4 circles for bottle holder recesses:

| Bottle | Position (X, Y from corner) | Diameter |
|--------|----------------------------|----------|
| RO Water | (70, 130) | 75 mm |
| Test Water | (150, 130) | 75 mm |
| Reagent #1 | (70, 200) | 55 mm |
| Reagent #2 | (150, 200) | 55 mm |

**FreeCAD Steps:**
- Select Circle tool
- Click center position
- Enter radius (37.5 mm for 75mm dia, 27.5 mm for 55mm dia)
- Use constraints to position accurately:
  - Select circle center
  - Click "Constrain horizontal distance" (enter X)
  - Click "Constrain vertical distance" (enter Y)

4. Close sketch

### 3.2 Create Pocket (Recess)

1. Select the bottle holder sketch
2. Part Design → Pocket
3. Set depth: 130 mm
4. Click OK

### 3.3 Add Drainage Holes

1. Create new sketch on bottom of each pocket
2. Draw small circle (5mm diameter) in center
3. Create pocket through remaining thickness

## Step 4: Add Pump Mounting Points

### 4.1 Create Mounting Boss Sketch

On the **right side panel** (inside surface):

1. Create new sketch
2. Draw rectangles for pump mounting bosses:
   - Boss 1 (FeW): Position (100, 150), Size: 20 × 90 mm
   - Boss 2 (FeR): Position (180, 150), Size: 20 × 90 mm

### 4.2 Extrude Bosses

1. Part Design → Pad
2. Extrude inward: 5 mm
3. This creates a raised surface for mounting screws

### 4.3 Add Mounting Holes

1. Create sketch on extruded boss surface
2. Draw 4 circles per boss (M3 mounting holes, 3.5mm diameter)
3. Spacing matches `pump_mount_bracket.scad` design
4. Part Design → Hole (or Pocket through all)

## Step 5: Modify Cuvette Holder (Dual LED)

### 5.1 Open Cuvette Holder

```
File → Open
Navigate to: /Users/davidchilds/Documents/Repositories/cuvette_holder/variants/3d_print/flanged_5mm_led/
Open: cuvette_holder.FCStd
```

### 5.2 Add Second LED Mount

The original has 1 LED mount. We need 2 (528nm and 625nm).

1. Locate the LED hole feature in the model tree
2. Right-click → "Duplicate selection"
3. Edit the duplicate:
   - Rotate 180° (position opposite side)
   - Ensure alignment with sensor

**Alternative:** Use Circular Pattern
1. Select LED hole feature
2. Part Design → Circular Pattern
3. Axis: Z-axis (vertical through cuvette center)
4. Occurrences: 2
5. Angle: 180°

### 5.3 Add Magnetic Stirrer Cavity

On the **bottom face** of cuvette holder:

1. Create sketch
2. Draw circle (25mm diameter) centered
3. Pocket: 15 mm deep

### 5.4 Save Modified Cuvette Holder

```
File → Save As
Name: cuvette_holder_dual_led.FCStd
Location: /Users/davidchilds/Documents/Repositories/openreef/hardware/cad/cuvette_holder/
```

## Step 6: Add Electronics Bay

### 6.1 Create Bay Volume

On **right side panel** (top section):

1. Create sketch showing electronics bay outline
   - Width: 80 mm
   - Height: 100 mm
2. Pocket inward to create recess
3. Depth: Match wall thickness (to inside surface)

### 6.2 Add Mounting Standoffs

For each electronics board mount:

1. Create cylindrical boss (8mm diameter, 15mm height)
2. Position according to board mounting holes
3. Add center hole (2.7mm diameter for M2.5 threaded insert)

**Board Positions:**
- Motor FeatherWing: 4 standoffs in rectangle (60 × 25 mm)
- Solenoid Driver: 4 standoffs in rectangle (50 × 30 mm)

## Step 7: Add Cable Management

### 7.1 Cable Channels

Create grooves along enclosure walls:

1. Select surface where cable will run
2. Create sketch: draw path (15mm wide line)
3. Pocket: 5mm deep
4. This creates a channel for wires

### 7.2 Cable Tie Points

Along each channel, add small holes:

1. Sketch: 5mm diameter circles every 50mm
2. Pocket: 3mm deep
3. Use for zip tie anchoring

### 7.3 Pass-Through Holes

Rear panel:

1. Power cable: 12mm diameter grommet hole
2. USB (PyBadge): 10 × 5 mm slot
3. Waste tube: 10mm grommet hole

## Step 8: Add Valve Mounting Area

### 8.1 Bottom Panel Mounting Points

On **bottom panel** (inside):

1. Create sketch with 4 mounting holes for valve plate
   - Spacing matches `valve_mounting_plate.scad`
   - Diameter: 3.5 mm (M3 screws)
2. Add cylindrical bosses (8mm dia, 10mm height)
3. Pocket center holes

### 8.2 Tube Pass-Throughs

Bottom panel needs holes for tubing to enter enclosure:

1. Sketch: 8-10 small holes (10mm diameter) near valve mounting area
2. Pocket through panel thickness
3. Optional: Add grommets (not modeled, purchased separately)

## Step 9: Ventilation

### 9.1 Bottom Vents (Intake)

On bottom panel, rear section:

1. Create sketch: 10 slots (50 × 5 mm each)
2. Space evenly
3. Pocket through thickness

### 9.2 Rear Vents (Exhaust)

On rear panel, top section:

1. Create sketch: 8 slots (50 × 5 mm each)
2. Space evenly
3. Pocket through thickness

## Step 10: Assembly and Verification

### 10.1 Create Assembly

```
File → New
Select: Assembly (A2plus workbench if installed)
```

Import all components:
- Enclosure body
- PyBadge cover
- Cuvette holder
- Bottle caps (from OpenSCAD)
- Pump brackets (from OpenSCAD)
- Valve plate (from OpenSCAD)

Position parts in their mounted locations.

### 10.2 Verify Clearances

Check that:
- Bottles fit in holders
- Pumps don't interfere with bottles
- Valves have tubing clearance
- Cables can route properly
- Cuvette holder aligns with front panel
- PyBadge cover fits opening

### 10.3 Interference Check

Tools → Measure → Distance
- Check critical dimensions
- Ensure no component interference

## Step 11: Export for Manufacturing

### 11.1 Export STL for 3D Printing

For each part:
```
Select part in tree
File → Export
Format: STL Mesh (*.stl)
Settings:
  - Deviation: 0.1 mm
  - Angular Deviation: 20°
Save to: hardware/cad/enclosure/
```

### 11.2 Export STEP for Editing

```
Select part
File → Export
Format: STEP (*.step, *.stp)
Save to: hardware/cad/enclosure/
```

This allows opening in other CAD programs.

### 11.3 Export 2D Drawings (Optional)

For laser cutting panels:
```
Select face
TechDraw → Insert View
Add dimensions
Export as PDF or DXF
```

## Troubleshooting

### Model Turns Yellow/Red (Errors)

**Cause:** Feature dependencies broken

**Fix:**
1. Tools → Dependency Graph
2. Identify broken feature
3. Edit feature to fix error
4. Tools → Recompute

### Changes Don't Update Model

**Fix:**
```
Tools → Recompute
or
Edit → Refresh
```

If still broken, rebuild feature from scratch.

### Slow Performance

**Cause:** Complex model with many features

**Fix:**
- Part → Bounding box (hide complex features temporarily)
- Edit → Preferences → Display → Reduce rendering quality
- Save often, restart FreeCAD

### Export Fails

**Check:**
- No degenerate faces (zero-area surfaces)
- No self-intersecting geometry
- All features computed successfully (green in tree)

**Fix:**
- Part → Check Geometry
- Part → Refine Shape

## Tips for Success

1. **Save frequently** - FreeCAD can crash
2. **Use constraints** - Don't just place points arbitrarily
3. **Name your features** - Makes finding things easier later
4. **Use spreadsheets** - Parametric design is powerful
5. **Version control** - Save dated versions (v1, v2, v3)
6. **Test print small** - Print one corner/section to verify dimensions
7. **Check units** - Ensure all dimensions in mm
8. **Leverage symmetry** - Mirror features when possible

## Learning Resources

### FreeCAD Documentation
- Official Wiki: https://wiki.freecadweb.org
- Video Tutorials: https://www.youtube.com/c/MangoJellySolutions

### Part Design Workbench
- https://wiki.freecadweb.org/PartDesign_Workbench

### Common Operations
- Pad (extrude): Add material
- Pocket: Remove material
- Pattern: Repeat features
- Mirror: Reflect features
- Boolean: Combine parts

## Next Steps

After completing the FreeCAD modifications:

1. Export STL files
2. Slice in your slicer software (Cura, PrusaSlicer, etc.)
3. Print test components
4. Verify fit with actual hardware
5. Iterate as needed
6. Print final components
7. Assemble OpenReef system

See `../assembly/assembly_guide.md` for assembly instructions.
