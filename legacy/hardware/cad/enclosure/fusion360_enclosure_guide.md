# OpenReef Enclosure in Fusion 360 - Step-by-Step Guide

## Quick Start: View the Existing Enclosure

### Step 1: Open the IoRodeo Enclosure

**You already have the STEP file here:**
```
/Users/davidchilds/Documents/Repositories/open_colorimeter_enclosure/step/v1r4/colorimeter_enclosure_v1r4.step
```

**In Fusion 360:**

1. Launch Fusion 360
2. **File → Open**
3. **Browse to:** `/Users/davidchilds/Documents/Repositories/open_colorimeter_enclosure/step/v1r4/`
4. **Select:** `colorimeter_enclosure_v1r4.step`
5. **Click "Open"**

**What you'll see:**
- The original IoRodeo colorimeter enclosure
- Compact design (~150 × 120 × 100 mm)
- PyBadge mount on front panel
- Cuvette holder mount
- Battery compartment

### Step 2: Orbit and Inspect

**Navigation:**
- **Orbit**: Shift + Middle Mouse (or two-finger drag on trackpad)
- **Pan**: Middle Mouse (or Option + two-finger drag)
- **Zoom**: Scroll wheel (or pinch on trackpad)

**View the inside:**
```
Inspect → Section Analysis
Drag section plane to see internal features
```

**Measure dimensions:**
```
Inspect → Measure
Click two faces/edges to see distance
```

## Current IoRodeo Design Overview

### What's Already There

```
Original Enclosure (IoRodeo):
┌─────────────────────────────┐
│  [PyBadge]    [Cuvette]     │  ← Front Panel
│                             │
│  Electronics                │
│  Bay                        │
│                             │
│  [Battery]                  │
│                             │
└─────────────────────────────┘

Dimensions: ~150 × 120 × 100 mm
```

### What We Need for OpenReef

```
OpenReef Enclosure (Expanded):
┌─────────────────────────────────────────┐
│  [PyBadge]         [Cuvette]            │  ← Front Panel
│                                         │
│  ┌──┐  ┌──┐    Electronics              │
│  │RO│  │TW│      Bay                    │
│  └──┘  └──┘                             │
│                                         │
│  ┌──┐  ┌──┐    ┌─────┐                │
│  │R1│  │R2│    │Pumps│                 │
│  └──┘  └──┘    │ ×2  │                │
│                └─────┘                 │
│                                         │
│               [Valves ×3]               │
└─────────────────────────────────────────┘

Dimensions: 350 × 250 × 300 mm (2.3× larger)
```

## Modification Plan: IoRodeo → OpenReef

### Changes Summary

| Feature | Original | OpenReef | Change Type |
|---------|----------|----------|-------------|
| Length | 150 mm | 350 mm | +133% |
| Width | 120 mm | 250 mm | +108% |
| Height | 100 mm | 300 mm | +200% |
| PyBadge mount | ✅ Keep | ✅ Keep | No change |
| Cuvette holder | ✅ Single LED | ✅ Dual LED | Minor mod |
| Bottle holders | ❌ None | ✅ 4× | Add new |
| Pump mounts | ❌ None | ✅ 2× | Add new |
| Valve mounting | ❌ None | ✅ 3× | Add new |
| Electronics bay | Small | Large | Expand |

## Step-by-Step Modification in Fusion 360

### Method 1: Parametric Modification (Recommended)

#### Step 1: Check for Parameters

After importing the STEP file:

1. **Look at Timeline** (bottom of screen)
   - Shows construction history
   - Each feature should be visible

2. **Check for Parameters**
   ```
   Modify → Change Parameters
   ```
   - If parameters exist: You're in luck! Change dimensions directly
   - If no parameters: Need to modify features individually

#### Step 2: Expand Base Dimensions

**If there's a base sketch:**

1. **Find the base sketch** in timeline/browser
2. **Right-click** → "Edit Sketch"
3. **Click dimensions** and change:
   - Length: 150 → 350 mm
   - Width: 120 → 250 mm
4. **Finish Sketch** (checkmark)
5. **Find extrude feature** for walls
6. **Edit extrude**: Change height 100 → 300 mm

**Model should update automatically!**

#### Step 3: Add Bottle Holder Recesses

**Create new sketch on top surface:**

1. **Create → Create Sketch**
2. **Select** top face of enclosure
3. **Sketch → Circle**
   - Draw circle for RO water bottle
   - **Diameter: 75 mm**
   - **Position: 70mm from left, 130mm from front**
4. **Dimension** the circle and position:
   ```
   Sketch → Sketch Dimension
   Click circle → Enter 75
   Click center point → Dimension X = 70
   Click center point → Dimension Y = 130
   ```

5. **Repeat for other 3 bottles:**
   - Test Water: 75mm dia @ (150, 130)
   - Reagent 1: 55mm dia @ (70, 200)
   - Reagent 2: 55mm dia @ (150, 200)

6. **Finish Sketch**

**Create pockets (recesses):**

1. **Create → Extrude**
2. **Select** all 4 circles
3. **Direction:** Cut (negative)
4. **Distance:** 130 mm
5. **OK**

**You now have bottle holders!**

#### Step 4: Add Drainage Holes

1. **Create sketch** on bottom of each pocket
2. **Draw small circle** (5mm diameter) in center
3. **Extrude → Cut** through remaining thickness

### Method 2: Direct Solid Modeling (If No Parameters)

If the STEP import doesn't have editable features:

#### Expand Enclosure - Scaling Method

**Quick but less precise:**

1. **Select** entire enclosure body
2. **Modify → Scale**
3. **Scale Type:** Non-uniform
4. **X-Factor:** 350/150 = 2.33
5. **Y-Factor:** 250/120 = 2.08
6. **Z-Factor:** 300/100 = 3.0
7. **OK**

**Issue:** This scales EVERYTHING including wall thickness and holes.

**Better:** Scale, then fix wall thickness and holes individually.

#### Add Features to Scaled Enclosure

Follow same steps as Method 1 (sketches and extrudes) but on scaled body.

### Method 3: Recreate from Scratch (Most Control)

**For a fully parametric design:**

#### Create User Parameters First

```
Modify → Change Parameters → Add User Parameter

Add these parameters:
- enclosure_length = 350 mm
- enclosure_width = 250 mm
- enclosure_height = 300 mm
- wall_thickness = 3 mm
- bottle_large_dia = 75 mm
- bottle_small_dia = 55 mm
- bottle_depth = 130 mm
```

#### Create Base Sketch

1. **Create → Create Sketch** (Top plane)
2. **Rectangle:** Use `enclosure_length` × `enclosure_width`
3. **Finish Sketch**

#### Extrude Walls

1. **Create → Extrude** (the rectangle)
2. **Distance:** `enclosure_height`
3. **OK**

#### Shell (Hollow Out)

1. **Modify → Shell**
2. **Select top face** (remove it)
3. **Thickness:** `wall_thickness`
4. **OK**

**Now you have a hollow box!**

#### Add PyBadge Mount (Front Panel)

1. **Create Sketch** on front face
2. **Rectangle:** 110 × 80 mm (PyBadge opening)
3. **Position:** Top-left corner, ~20mm from edges
4. **Finish Sketch**
5. **Extrude → Cut** through wall thickness

**Add mounting holes:**

1. **Sketch** on same face
2. **4 circles:** 2.7mm diameter
3. **Positions:**
   - Corners of 100 × 70 mm rectangle
   - Centered around PyBadge opening
4. **Extrude → Cut** (countersunk optional)

#### Add Cuvette Holder Mount

**Import existing cuvette holder:**

1. **Insert → Insert into Current Design**
2. **Select:** `cuvette_holder_led5mm_filter_rev5.step`
3. **Position** on front panel

**Create mounting points:**

1. Project cuvette mounting holes onto enclosure
2. Create matching holes for M3 screws

#### Add Bottle Holders

(Follow Step 3 from Method 1 above)

#### Add Pump Mounting Bosses

**On right interior wall:**

1. **Create Sketch** (on inner side panel surface)
2. **Rectangle:** 20 × 90 mm (boss for pump mount)
3. **Position:** X=280, Y=100 (for FeW pump)
4. **Repeat** for FeR pump at Y=180
5. **Finish Sketch**

**Extrude inward:**

1. **Create → Extrude** (the rectangles)
2. **Distance:** 5 mm (inward from wall)
3. **OK**

**Add mounting holes in bosses:**

1. **Sketch** on boss surface
2. **4 circles per boss:** 3.5mm diameter (M3)
3. **Pattern:** Matches pump mount bracket hole spacing
4. **Extrude → Cut** through boss

#### Add Valve Mounting Plate Area

**On bottom panel (inside):**

1. **Create Sketch**
2. **4 circles:** 3.5mm diameter (M3)
3. **Rectangular pattern:** 200 × 60 mm spacing
4. **Finish Sketch**

**Create standoff bosses:**

1. **Extrude** around each hole: 8mm diameter × 10mm height
2. **Create → Circular Pattern** or do individually

**Add tube pass-throughs:**

1. **Sketch:** 8-10 circles (10mm diameter) near valve area
2. **Extrude → Cut** through bottom panel

#### Add Electronics Bay

**Right side panel, top section:**

1. **Create Sketch** (on inner wall)
2. **Rectangle:** 80 × 100 mm
3. **Position:** Top-right corner
4. **Extrude → Cut** inward to create recess

**Add board standoffs:**

1. **Create cylindrical bosses** (8mm dia × 15mm)
2. **Pattern** based on board mounting holes:
   - Motor FeatherWing: 60 × 25 mm rectangle
   - Solenoid Driver: 50 × 30 mm rectangle
3. **Center hole:** 2.7mm diameter (M2.5)

#### Add Ventilation

**Bottom panel (exterior):**

1. **Sketch:** Rectangular slots (50 × 5 mm)
2. **Pattern:** 10 slots evenly spaced
3. **Extrude → Cut** through panel

**Rear panel (top):**

1. **Sketch:** Rectangular slots (50 × 5 mm)
2. **Pattern:** 8 slots evenly spaced
3. **Extrude → Cut** through panel

#### Add Cable Channels

**Along interior walls:**

1. **Sketch:** Spline or polyline showing cable path
2. **Offset** path by 7.5mm each side (15mm total width)
3. **Extrude → Cut:** 5mm deep
4. **Result:** Groove for cable routing

**Add cable tie points:**

1. **Sketch:** Small circles (5mm dia) every 50mm along channel
2. **Extrude → Cut:** 3mm deep

## Viewing & Presenting the Design

### Create Section View

To see inside:

```
Inspect → Section Analysis
- Drag section plane to desired position
- Toggle plane visibility
- Rotate view to see interior features
```

### Create Exploded View

**Show assembly components separated:**

1. **Design → Create Exploded View**
2. **Drag components** away from each other
3. **Create animation** of assembly/disassembly

### Render for Visualization

**Make it look pretty:**

1. **Render → Render Workspace**
2. **Apply appearances:**
   - Enclosure: Black plastic
   - Electronics: Metallic
   - Bottles: Translucent blue
3. **Set up lighting**
4. **Render → Start Rendering**

**Saves as image for presentation**

### Create Technical Drawings

**For fabrication/documentation:**

1. **Design → Create Drawing**
2. **From Design:** Select enclosure
3. **Add views:**
   - Front view
   - Top view
   - Right side view
   - Isometric view
4. **Add dimensions**
5. **Export:** PDF or DWG

## Assembly with All Components

### Create Full Assembly

1. **File → New Design**
2. **Save as:** "OpenReef_Complete_Assembly"

**Insert all components:**

```
Insert → Insert into Current Design

Add in order:
1. Enclosure body
2. Enclosure top panel
3. PyBadge cover
4. Cuvette holder (dual LED)
5. Bottle caps ×4
6. Pump brackets ×2
7. Valve mounting plate
8. Electronics (FeatherWing, solenoid driver)
```

**Position components:**

```
Assemble → Joint

For each component:
- Select component origin
- Select enclosure mount point
- Type: Rigid
- OK

Result: Components snap into position
```

**Visualize complete system:**

```
View → Visual Style → Shaded with Edges
Inspect → Interference Detection (check for collisions)
```

## Export for Manufacturing

### For 3D Printing (STL)

**Each component separately:**

1. **Right-click** component in browser
2. **Save as STL**
3. **Options:**
   - Format: Binary
   - Refinement: High
   - Preview mesh (should look smooth)
4. **OK**

**Save to:**
```
/Users/davidchilds/Documents/Repositories/openreef/hardware/cad/enclosure/
```

**Files to export:**
- `openreef_enclosure_body.stl`
- `openreef_enclosure_top.stl`
- `openreef_pybadge_cover.stl`

### For Laser Cutting (DXF)

**If cutting panels from acrylic:**

1. **Create Sketch** from component face
2. **Project edges** onto sketch plane
3. **Finish Sketch**
4. **Right-click sketch** → "Save as DXF"

**Export each panel:**
- Front panel
- Back panel
- Side panels (×2)
- Top panel
- Bottom panel

### For CNC/Professional (STEP)

```
File → Export
Format: STEP (*.step, *.stp)
Save as: openreef_enclosure.step
```

**Can be opened in:**
- Other CAD programs (SolidWorks, Inventor, etc.)
- CAM software (for CNC machining)
- Sent to machine shops

## Quick Reference: Fusion 360 Commands

### Essential Commands for This Project

| Task | Command | Shortcut |
|------|---------|----------|
| **Create Sketch** | Create → Sketch | S |
| **Extrude** | Create → Extrude | E |
| **Cut** | Modify → Press Pull | Q |
| **Hole** | Create → Hole | H |
| **Fillet** | Modify → Fillet | F |
| **Pattern** | Create → Pattern | - |
| **Mirror** | Create → Mirror | - |
| **Shell** | Modify → Shell | - |
| **Measure** | Inspect → Measure | I |
| **Section** | Inspect → Section | - |

### Sketch Commands

| Task | Command | Shortcut |
|------|---------|----------|
| **Rectangle** | Sketch → Rectangle | R |
| **Circle** | Sketch → Circle | C |
| **Line** | Sketch → Line | L |
| **Dimension** | Sketch → Dimension | D |
| **Offset** | Sketch → Offset | O |

## Tips for Success

### 1. Save Versions Frequently

```
File → Save Version
Description: "v1 - Base enclosure"
```

Can revert to any version later.

### 2. Use Parameters for Everything

```
Modify → Change Parameters

Instead of: 350
Use parameter: enclosure_length = 350 mm
```

Easy to change dimensions later.

### 3. Name Your Features

In browser (left panel):
- Right-click feature → Rename
- "Bottle Holder Pockets" instead of "Extrude7"

### 4. Create Components

Organize complex designs:

```
New Component for:
- Enclosure
- Fluidics
- Electronics
```

Easy to show/hide groups.

### 5. Use Construction Planes

For complex geometry:

```
Construct → Offset Plane
Construct → Plane at Angle
```

Create reference planes for sketching.

## Troubleshooting

### Import Shows Mesh (Not Solid)

**Problem:** STEP imported as surface/mesh

**Fix:**
```
Mesh → Convert Mesh
Or: Mesh → Mesh to BRep
```

Converts to editable solid.

### Can't Edit Features

**Problem:** STEP has no parametric history

**Fix:**
- Use direct modeling (push/pull faces)
- Or: Recreate from scratch using STEP as reference
- Modify → Press Pull (Q) to push/pull faces

### Model Updates Slowly

**Problem:** Complex model lags

**Fix:**
```
Preferences → Display → Reduce quality
Turn off shadows temporarily
```

### Dimensions Won't Change

**Problem:** Over-constrained sketch

**Fix:**
```
Right-click dimension → Delete
Sketch → Show Constraints
Remove conflicting constraints
```

## Next Steps

1. **Open the existing IoRodeo enclosure** in Fusion 360 (see Step 1)
2. **Experiment** with modifications on a copy
3. **Create parameters** for key dimensions
4. **Add bottle holders** following Step 3
5. **Export STL** when satisfied
6. **Test print** a small section first

## Get Help

**Stuck?**

- Fusion 360 Tutorials: https://www.autodesk.com/products/fusion-360/learn
- Our specs: `../specifications.md` (has all dimensions)
- Assembly guide: `../assembly/assembly_guide.md`

Ready to build your OpenReef enclosure! 🚀
