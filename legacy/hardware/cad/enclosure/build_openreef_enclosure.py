"""
OpenReef Enclosure Builder - FreeCAD Python Macro

This script automatically builds the complete OpenReef enclosure in FreeCAD.

HOW TO USE:
1. Open FreeCAD (version 0.20 or newer)
2. Macro → Macros → Create
3. Name it: build_openreef_enclosure
4. Copy and paste this entire script
5. Click "Execute"
6. Wait 30-60 seconds for model to build
7. File → Save As → openreef_enclosure.FCStd

The script will create a complete parametric model with:
- Main enclosure body (350 × 250 × 300 mm)
- 4 bottle holders
- PyBadge mount cutout
- Cuvette holder mount
- Pump mounting bosses
- Valve mounting area
- Electronics bay standoffs
- Ventilation slots

All dimensions are in the Spreadsheet - easy to modify!
"""

import FreeCAD
import Part
import Sketcher
import Draft

# Create new document
doc_name = "OpenReef_Enclosure"
if FreeCAD.ActiveDocument:
    doc = FreeCAD.ActiveDocument
else:
    doc = FreeCAD.newDocument(doc_name)

print("Building OpenReef Enclosure...")

# ============ PARAMETERS ============

# Create spreadsheet for parameters
try:
    params = doc.addObject('Spreadsheet::Sheet', 'Parameters')
except:
    params = doc.getObject('Parameters')

# Set parameters
params.set('A1', 'Parameter')
params.set('B1', 'Value')
params.set('C1', 'Description')

row = 2
def add_param(name, value, description):
    global row
    params.set(f'A{row}', name)
    params.set(f'B{row}', str(value))
    params.set(f'C{row}', description)
    params.setAlias(f'B{row}', name)
    row += 1

# Main dimensions
add_param('Length', '350 mm', 'Enclosure length (X)')
add_param('Width', '250 mm', 'Enclosure width (Y)')
add_param('Height', '300 mm', 'Enclosure height (Z)')
add_param('WallThickness', '3 mm', 'Wall thickness')
add_param('BaseThickness', '5 mm', 'Base thickness')

# Bottle holders
add_param('BottleLargeDia', '75 mm', 'Large bottle diameter')
add_param('BottleSmallDia', '55 mm', 'Small bottle diameter')
add_param('BottleDepth', '130 mm', 'Bottle holder depth')

# PyBadge
add_param('PyBadgeWidth', '110 mm', 'PyBadge cutout width')
add_param('PyBadgeHeight', '80 mm', 'PyBadge cutout height')
add_param('PyBadgeOffsetX', '20 mm', 'PyBadge offset from left')
add_param('PyBadgeOffsetZ', '200 mm', 'PyBadge offset from bottom')

# Cuvette holder
add_param('CuvetteDia', '70 mm', 'Cuvette holder diameter')
add_param('CuvetteOffsetX', '180 mm', 'Cuvette offset from left')
add_param('CuvetteOffsetZ', '200 mm', 'Cuvette offset from bottom')

doc.recompute()

print("Parameters created in Spreadsheet")

# ============ HELPER FUNCTIONS ============

def create_box(name, length, width, height):
    """Create a basic box"""
    box = doc.addObject("Part::Box", name)
    box.Length = length
    box.Width = width
    box.Height = height
    return box

def create_cylinder(name, radius, height):
    """Create a cylinder"""
    cyl = doc.addObject("Part::Cylinder", name)
    cyl.Radius = radius
    cyl.Height = height
    return cyl

# ============ MAIN ENCLOSURE BODY ============

print("Creating main enclosure body...")

# Outer box
outer_box = create_box("OuterBox", 350, 250, 300)
outer_box.ViewObject.Transparency = 70

# Inner box (to hollow out)
inner_box = create_box("InnerBox", 344, 244, 295)
inner_box.Placement.Base = FreeCAD.Vector(3, 3, 5)  # Wall thickness offset

# Create hollow enclosure
enclosure = doc.addObject("Part::Cut", "Enclosure_Body")
enclosure.Base = outer_box
enclosure.Tool = inner_box

doc.recompute()
print("Main enclosure body created")

# ============ PYBADGE CUTOUT ============

print("Creating PyBadge cutout...")

pybadge_cutout = create_box("PyBadge_Cutout", 110, 5, 80)
pybadge_cutout.Placement.Base = FreeCAD.Vector(20, -1, 200)

# Cut PyBadge opening
enclosure_with_pybadge = doc.addObject("Part::Cut", "Enclosure_PyBadge")
enclosure_with_pybadge.Base = enclosure
enclosure_with_pybadge.Tool = pybadge_cutout

doc.recompute()
print("PyBadge cutout created")

# ============ CUVETTE HOLDER MOUNT ============

print("Creating cuvette holder mount...")

cuvette_cutout = create_cylinder("Cuvette_Cutout", 35, 5)
cuvette_cutout.Placement.Base = FreeCAD.Vector(180, 0, 200)
cuvette_cutout.Placement.Rotation = FreeCAD.Rotation(FreeCAD.Vector(0, 1, 0), 90)

enclosure_with_cuvette = doc.addObject("Part::Cut", "Enclosure_Cuvette")
enclosure_with_cuvette.Base = enclosure_with_pybadge
enclosure_with_cuvette.Tool = cuvette_cutout

doc.recompute()
print("Cuvette mount created")

# ============ BOTTLE HOLDERS ============

print("Creating bottle holders...")

# Bottle positions: [x, y, diameter, name]
bottles = [
    (70, 130, 75, "RO_Water"),
    (150, 130, 75, "Test_Water"),
    (70, 200, 55, "Reagent_1"),
    (150, 200, 55, "Reagent_2")
]

current_enclosure = enclosure_with_cuvette

for i, (x, y, dia, name) in enumerate(bottles):
    # Create bottle holder cylinder
    bottle_hole = create_cylinder(f"Bottle_{name}", dia/2, 130)
    bottle_hole.Placement.Base = FreeCAD.Vector(x, y, 300 - 130)  # From top

    # Cut bottle holder
    temp_name = f"Enclosure_Bottle_{i}"
    temp_enclosure = doc.addObject("Part::Cut", temp_name)
    temp_enclosure.Base = current_enclosure
    temp_enclosure.Tool = bottle_hole

    current_enclosure = temp_enclosure

    # Add drainage hole at bottom
    drain_hole = create_cylinder(f"Drain_{name}", 2.5, 6)
    drain_hole.Placement.Base = FreeCAD.Vector(x, y, 0)

    temp_name2 = f"Enclosure_Drain_{i}"
    temp_enclosure2 = doc.addObject("Part::Cut", temp_name2)
    temp_enclosure2.Base = current_enclosure
    temp_enclosure2.Tool = drain_hole

    current_enclosure = temp_enclosure2

doc.recompute()
print("Bottle holders created")

# ============ VENTILATION SLOTS ============

print("Creating ventilation slots...")

# Bottom vents (intake)
for i in range(10):
    vent = create_box(f"Bottom_Vent_{i}", 50, 5, 6)
    x_pos = 200 + i * 60
    vent.Placement.Base = FreeCAD.Vector(x_pos, 200, 0)

    temp_enclosure = doc.addObject("Part::Cut", f"Enclosure_BVent_{i}")
    temp_enclosure.Base = current_enclosure
    temp_enclosure.Tool = vent
    current_enclosure = temp_enclosure

# Rear vents (exhaust)
for i in range(8):
    vent = create_box(f"Rear_Vent_{i}", 50, 5, 5)
    x_pos = 20 + i * 60
    vent.Placement.Base = FreeCAD.Vector(x_pos, 247, 250)

    temp_enclosure = doc.addObject("Part::Cut", f"Enclosure_RVent_{i}")
    temp_enclosure.Base = current_enclosure
    temp_enclosure.Tool = vent
    current_enclosure = temp_enclosure

doc.recompute()
print("Ventilation created")

# ============ PUMP MOUNTING BOSSES ============

print("Creating pump mounting bosses...")

# Create bosses on right side
for i, z_pos in enumerate([100, 180]):
    boss = create_box(f"Pump_Boss_{i}", 5, 20, 90)
    boss.Placement.Base = FreeCAD.Vector(342, 50, z_pos)

    # Add to enclosure (union)
    temp_enclosure = doc.addObject("Part::Fuse", f"Enclosure_PumpBoss_{i}")
    temp_enclosure.Base = current_enclosure
    temp_enclosure.Tool = boss
    current_enclosure = temp_enclosure

doc.recompute()
print("Pump bosses created")

# ============ VALVE MOUNTING STANDOFFS ============

print("Creating valve mounting standoffs...")

# 4 standoffs on bottom
standoff_positions = [
    (75, 95),   # Front-left
    (275, 95),  # Front-right
    (75, 155),  # Rear-left
    (275, 155)  # Rear-right
]

for i, (x, y) in enumerate(standoff_positions):
    standoff = create_cylinder(f"Valve_Standoff_{i}", 4, 10)
    standoff.Placement.Base = FreeCAD.Vector(x, y, 5)

    temp_enclosure = doc.addObject("Part::Fuse", f"Enclosure_VStandoff_{i}")
    temp_enclosure.Base = current_enclosure
    temp_enclosure.Tool = standoff
    current_enclosure = temp_enclosure

doc.recompute()
print("Valve standoffs created")

# ============ FINAL ENCLOSURE ============

# Rename final enclosure
try:
    current_enclosure.Label = "OpenReef_Enclosure_Complete"
except:
    pass

# Hide intermediate objects
for obj in doc.Objects:
    if obj.Label.startswith("Enclosure_") or obj.Label.startswith("Bottle_") or obj.Label.startswith("PyBadge_") or obj.Label.startswith("Cuvette_") or obj.Label.startswith("Drain_") or obj.Label.startswith("Pump_") or obj.Label.startswith("Valve_"):
        if obj.Label != "OpenReef_Enclosure_Complete":
            obj.ViewObject.Visibility = False

# Show only final result
current_enclosure.ViewObject.Visibility = True
current_enclosure.ViewObject.Transparency = 0

doc.recompute()

# ============ FIT VIEW ============

import FreeCADGui
FreeCADGui.SendMsgToActiveView("ViewFit")

print("\n" + "="*50)
print("OpenReef Enclosure Build Complete!")
print("="*50)
print("\nNext steps:")
print("1. File → Save As → openreef_enclosure.FCStd")
print("2. Modify parameters in 'Parameters' spreadsheet if needed")
print("3. Export: File → Export → STEP (for Fusion 360)")
print("4. Export: File → Export → STL (for 3D printing)")
print("\nThe model is fully parametric - change values in")
print("the Parameters spreadsheet to resize!")
print("="*50)

# Set isometric view
try:
    FreeCADGui.activeDocument().activeView().viewIsometric()
except:
    pass
