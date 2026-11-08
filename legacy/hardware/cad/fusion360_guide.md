# Using OpenReef CAD Files in Fusion 360

## Overview

All OpenReef CAD files can be used in Fusion 360, though some require conversion. Fusion 360 is a professional CAD tool with excellent parametric modeling capabilities.

## File Compatibility Matrix

| File Type | Direct Import | Conversion Needed | Parametric |
|-----------|---------------|-------------------|------------|
| **.step** (IoRodeo files) | ✅ Yes | No | ✅ Yes |
| **.scad** (OpenSCAD) | ❌ No | Yes → STEP/STL | ⚠️ Partial |
| **.FCStd** (FreeCAD) | ❌ No | Yes → STEP | ✅ Yes |
| **.stl** | ✅ Yes | No | ❌ No (mesh only) |

## Method 1: Import Existing STEP Files (Easiest)

### IoRodeo STEP Files

You already have these at:
```
/Users/davidchilds/Documents/Repositories/open_colorimeter_enclosure/step/v1r4/
/Users/davidchilds/Documents/Repositories/cuvette_holder/variants/3d_print/flanged_5mm_led/
```

**Steps:**

1. **Open Fusion 360**
2. **File → Open**
3. **Navigate to STEP file location**
4. **Select file** (e.g., `colorimeter_enclosure_v1r4.step`)
5. **Click "Open"**

**What you get:**
- Fully editable solid bodies
- Can modify features (extrudes, holes, etc.)
- Parametric timeline preserved (mostly)

**Files you can import directly:**
- `colorimeter_enclosure_v1r4.step` ✅
- `pybadge_cover_v1r4.step` ✅
- `cuvette_holder_led5mm_filter_rev5.step` ✅

### Editing in Fusion 360

Once imported:

1. **Timeline** (bottom) shows construction history
2. **Edit features**: Right-click feature → "Edit Feature"
3. **Add features**: Create → Extrude, Hole, etc.
4. **Sketch on faces**: Create Sketch → Select face
5. **Save**: File → Save (saves as Fusion 360 .f3d file)

## Method 2: Convert OpenSCAD Files to STEP

For the parametric OpenSCAD files we created:
- `bottle_cap_3port.scad`
- `pump_mount_bracket.scad`
- `valve_mounting_plate.scad`

### Option A: OpenSCAD → STEP → Fusion 360

**Prerequisites:**
- Install OpenSCAD (free): https://openscad.org

**Steps:**

1. **Open OpenSCAD**
   ```
   File → Open
   Select: bottle_cap_3port.scad
   ```

2. **Adjust Parameters** (optional)
   - Edit values at top of file
   - Example: Change `bottle_outer_diameter = 42;` to your size

3. **Render Model**
   - Press **F6** (or Design → Render)
   - Wait for rendering to complete (1-30 seconds)

4. **Export to STEP**
   ```
   File → Export → Export as CSG
   Or better yet:
   File → Export → Export as STEP
   ```

   **Note:** OpenSCAD may not have direct STEP export in all versions. If not available:

5. **Alternative: Export to STL first**
   ```
   File → Export → Export as STL
   Save to: hardware/cad/bottle_caps/bottle_cap_3port.stl
   ```

6. **Convert STL to STEP** (if needed)
   - Use online converter: https://www.greentoken.de/onlineconv/
   - Or use FreeCAD (File → Open STL → Export STEP)

7. **Import STEP into Fusion 360**
   ```
   Fusion 360 → File → Open
   Select: bottle_cap_3port.step
   ```

### Option B: OpenSCAD → STL → Fusion 360 (Mesh)

**Faster but loses parametric features:**

1. **Export STL from OpenSCAD** (F6 then File → Export → STL)

2. **Import STL to Fusion 360**
   ```
   File → Open → Select STL
   ```

3. **Convert Mesh to Solid** (optional)
   ```
   Mesh → Convert Mesh (requires Fusion 360 subscription)
   Or:
   Right-click mesh → Mesh to BRep
   ```

**Limitation:** STL imports as a mesh (non-editable surface), not parametric solid.

**Best for:** Quick visualization or if you don't need to edit further.

## Method 3: FreeCAD → STEP → Fusion 360

If you modify the IoRodeo FreeCAD files per our guide:

1. **Open in FreeCAD**
   ```
   File → Open
   Select: colorimeter_enclosure.FCStd (or your modified version)
   ```

2. **Export to STEP**
   ```
   File → Export
   Format: STEP with colors (*.step *.stp)
   Save to: hardware/cad/enclosure/openreef_enclosure.step
   ```

3. **Import STEP to Fusion 360**
   ```
   Fusion 360 → File → Open
   Select: openreef_enclosure.step
   ```

**Result:** Fully parametric solid bodies in Fusion 360.

## Method 4: Redesign Directly in Fusion 360 (Most Parametric)

For maximum flexibility, recreate the OpenSCAD designs natively in Fusion 360:

### Example: Bottle Cap in Fusion 360

**I'll create a Fusion 360-specific guide for you:**

1. **Create New Design**
   ```
   File → New Design
   ```

2. **Create Parameters** (like OpenSCAD)
   ```
   Modify → Change Parameters
   Add User Parameters:
     - bottle_diameter = 42 mm
     - cap_height = 20 mm
     - thread_pitch = 3 mm
     - port_1_dia = 6 mm
     - port_2_dia = 4 mm
     - port_3_dia = 2 mm
   ```

3. **Create Sketch** (top plane)
   - Draw circle: diameter = `bottle_diameter + 6`
   - Dimension using parameters

4. **Extrude**
   - Distance: `cap_height`

5. **Add Thread**
   ```
   Create → Thread
   Select inside surface
   Type: Custom
   Pitch: `thread_pitch`
   ```

6. **Add Tube Ports**
   - Create sketch on top face
   - Draw 3 circles for ports
   - Extrude upward 15mm
   - Hollow with Shell command

This gives you **fully parametric** design that auto-updates when you change parameters.

## Fusion 360 Workflow for OpenReef

### Recommended Approach

1. **Import IoRodeo STEP files** (enclosure, cuvette holder)
   - Modify in Fusion 360 using our modification guide as reference
   - Add bottle holders, pump mounts, etc.

2. **Import or recreate** mounting hardware
   - **Quick**: Convert .scad → STL → Fusion 360
   - **Better**: Recreate natively in Fusion 360 (fully parametric)

3. **Create assembly**
   ```
   File → New Design
   Use "Insert into Current Design" for each component
   Position components
   Create joints/constraints
   ```

### Advantages of Fusion 360

- **Cloud-based**: Access from anywhere
- **Collaboration**: Share designs easily
- **Rendering**: Excellent visualization
- **CAM**: Generate G-code for CNC
- **Simulation**: Stress analysis (with subscription)
- **Electronics**: PCB design integration
- **Timeline**: Easy to go back and modify

### Disadvantages vs. FreeCAD

- **Cost**: Free for hobbyists, but subscription required for advanced features
- **Cloud-required**: Must be online
- **Lock-in**: Proprietary format (.f3d)
- **Open source**: FreeCAD is open, Fusion is not

## Quick Start Guide: Import & Modify

### 1. Import IoRodeo Colorimeter Enclosure

```bash
# In Fusion 360:
File → Open
Browse to: /Users/davidchilds/Documents/Repositories/open_colorimeter_enclosure/step/v1r4/
Open: colorimeter_enclosure_v1r4.step
```

### 2. Scale Up Enclosure

```
Modify → Scale
Select: Entire body
Scale Type: Uniform
Factor: Calculate based on desired dimensions
  Original ~150mm → Target 350mm = 2.33x scale
  OR create dimensions from scratch
```

**Better approach:** Modify individual features rather than scaling.

### 3. Add Bottle Holders

```
Create → Sketch (on top face)
Sketch → Circle (75mm diameter for large bottles)
Finish Sketch
Create → Extrude
  Direction: Cut
  Depth: 130mm
Repeat for 4 bottles
```

### 4. Add Pump Mounting Bosses

```
Create → Sketch (on side panel)
Draw mounting rectangle
Extrude inward 5mm (boss)
Create holes (3.5mm, 4 holes per pump)
```

### 5. Save as Fusion 360 Project

```
File → Save
Name: OpenReef Enclosure
Location: Fusion 360 cloud or local
```

## Converting OpenSCAD Parametric to Fusion 360

Since OpenSCAD files are text-based and parametric, here's the mapping:

| OpenSCAD | Fusion 360 Equivalent |
|----------|----------------------|
| `parameter = value;` | User Parameters |
| `cylinder(h=10, d=5)` | Create → Cylinder |
| `cube([10, 20, 30])` | Create → Box |
| `translate([x, y, z])` | Move/Copy |
| `rotate([a, b, c])` | Move → Rotate |
| `difference() {}` | Boolean → Cut |
| `union() {}` | Boolean → Join |
| `intersection() {}` | Boolean → Intersect |
| `for (i = [0:n])` | Create → Pattern (Circular/Rectangular) |

### Example Translation: Bottle Cap

**OpenSCAD:**
```openscad
bottle_diameter = 42;
cap_height = 20;

cylinder(h=cap_height, d=bottle_diameter + 6);
```

**Fusion 360:**
```
User Parameters:
  bottle_diameter = 42 mm
  cap_height = 20 mm

Sketch: Circle (diameter = bottle_diameter + 6 mm)
Extrude: cap_height
```

## Batch Export from OpenSCAD

If you want to convert all .scad files at once:

### Using OpenSCAD Command Line

```bash
# Navigate to CAD directory
cd /Users/davidchilds/Documents/Repositories/openreef/hardware/cad/

# Export bottle cap to STL
openscad -o bottle_caps/bottle_cap_3port.stl bottle_caps/bottle_cap_3port.scad

# Export pump mount to STL
openscad -o mounting/pump_mount_bracket.stl mounting/pump_mount_bracket.scad

# Export valve plate to STL
openscad -o mounting/valve_mounting_plate.stl mounting/valve_mounting_plate.scad
```

Then import all STLs into Fusion 360.

## Creating a Complete Assembly in Fusion 360

### 1. Create Main Project

```
File → New Design
Save as: OpenReef_Assembly
```

### 2. Insert Components

```
Insert → Insert into Current Design
Select each STEP/STL file:
  - Enclosure body
  - PyBadge cover
  - Cuvette holder
  - Bottle caps (4×)
  - Pump brackets (2×)
  - Valve plate (1×)
```

### 3. Position Components

```
Assemble → Joint
Select faces/points to align
Type: Rigid (for fixed parts) or Revolute (for moving parts)
```

### 4. Visualize

```
View → Visual Style → Shaded with Edges
Inspect → Section Analysis (see inside)
Render → In-Canvas Render (nice visualization)
```

### 5. Generate Drawings

```
Drawing tab → Create Drawing
Add views (front, top, side, isometric)
Add dimensions
Export as PDF
```

## Tips for Fusion 360 Success

### 1. Use Parameters from Day 1
```
Modify → Change Parameters
Create all dimensions as parameters
Easy to modify later
```

### 2. Create Component Hierarchy
```
Browser (left panel):
  - Enclosure
    - Base
    - Top Panel
    - Side Panels
  - Fluidics
    - Pumps
    - Valves
    - Tubing
  - Electronics
    - PyBadge
    - Sensors
    - Drivers
```

### 3. Use Joints Properly
```
For assembly constraints:
- Rigid: Fixed components
- Revolute: Rotating parts (pumps, stirrers)
- Slider: Moving parts
- Ball: Multi-axis rotation
```

### 4. Version Control
```
File → Save Version
Add description: "v1.0 - Initial design"
Can revert to any version later
```

### 5. Collaboration
```
Share → Get Public Link
Or: Share → Invite People
Others can view/edit in browser
```

## Recommended Workflow Summary

**For your OpenReef project:**

✅ **Do this:**
1. Import IoRodeo STEP files directly into Fusion 360
2. Modify them following our guide (easier than FreeCAD for many users)
3. Recreate mounting brackets natively in Fusion 360 (fully parametric)
4. Create assembly with all components
5. Export STL for 3D printing when ready

❌ **Don't do this:**
- Don't convert everything to STL first (loses editability)
- Don't skip creating parameters (hard to modify later)
- Don't forget to save versions (easy to lose work)

## Getting Help

**Fusion 360 Resources:**
- Official Tutorials: https://www.autodesk.com/products/fusion-360/learn-training
- YouTube Channel: https://www.youtube.com/user/AutodeskFusion360
- Forums: https://forums.autodesk.com/t5/fusion-360/ct-p/1234

**OpenReef-Specific:**
- Our specifications.md has all dimensions
- Refer to OpenSCAD files for design intent
- Assembly guide has complete part list

## License Considerations

- **IoRodeo files**: CC BY 4.0 (can use in Fusion 360, must attribute)
- **OpenReef files**: MIT License (very permissive)
- **Fusion 360 exports**: You own your designs, can export freely

Would you like me to create detailed Fusion 360 parameter templates for the mounting brackets?
