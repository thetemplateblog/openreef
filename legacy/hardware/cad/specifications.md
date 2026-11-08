# OpenReef Enclosure - Detailed Specifications

## Overall Dimensions

### Main Enclosure

```
Width (X):  350 mm
Depth (Y):  250 mm
Height (Z): 300 mm

Wall Thickness: 3 mm
Base Thickness: 5 mm
```

### Component Zones

```
┌─────────────────────────────────────────────────┐
│                   TOP VIEW                      │
│  ┌────────────────────────────────────────────┐ │
│  │                 FRONT                      │ │
│  │  ┌──────────┐                              │ │
│  │  │ PyBadge  │        Cuvette                │ │
│  │  │  Cover   │        Holder                 │ │
│  │  └──────────┘                              │ │
│  │                                            │ │
│  │   ┌─────┐  ┌─────┐                        │ │
│  │   │ RO  │  │Test │    Electronics          │ │
│  │   │Water│  │Water│       Bay                │ │
│  │   └─────┘  └─────┘                        │ │
│  │                                            │ │
│  │   ┌─────┐  ┌─────┐    ┌────────┐         │ │
│  │   │Reag │  │Reag │    │ Pumps  │         │ │
│  │   │  1  │  │  2  │    │ x2     │         │ │
│  │   └─────┘  └─────┘    └────────┘         │ │
│  │                                            │ │
│  │                     Valves                 │ │
│  │                      x3                    │ │
│  │                    [Waste]                 │ │
│  │                                            │ │
│  └────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
```

## PyBadge Front Panel Mount

### Based on IoRodeo Design

- **Location**: Front panel, top left
- **Opening**: 110 × 80 mm rectangular cutout
- **Mounting Holes**: 4× M2.5 (diameter 2.7mm)
  - Hole spacing: 100 × 70 mm (center to center)
  - Corner radius: 5 mm

### PyBadge Dimensions (Reference)
```
PyBadge PCB: 88 × 60 × 8 mm
Display area: 36 × 28 mm
Button overhang: Consider when designing cover
```

## Cuvette Holder

### Based on IoRodeo Flanged 5mm LED Design

**Base Dimensions:**
- Outer diameter: 60 mm
- Height: 50 mm
- Flange diameter: 70 mm
- Flange thickness: 5 mm

**Cuvette Cavity:**
- Square cutout: 12.5 × 12.5 mm (for standard 10mm cuvette)
- Depth: 45 mm
- Tolerance: +0.2mm for easy insertion

**LED Mounts (Dual):**
- **Green LED (528nm)**:
  - Position: 0° (front)
  - Hole diameter: 5.2 mm (for 5mm LED)
  - Depth: 10 mm
  - Distance to cuvette center: 25 mm

- **Red LED (625nm)**:
  - Position: 180° (opposite)
  - Hole diameter: 5.2 mm
  - Depth: 10 mm
  - Distance to cuvette center: 25 mm

**AS7341 Sensor Mount:**
- Position: Opposite to active LED
- Mounting holes: 2× M2 (30mm spacing)
- Sensor window aligned with cuvette center
- Light path: 50mm (LED → cuvette → sensor)

**Magnetic Stirrer Cavity:**
- Location: Bottom center, beneath cuvette
- Diameter: 25 mm
- Depth: 15 mm
- Clearance for 10mm stir bar + motor

**Mounting to Enclosure:**
- 4× M3 mounting holes on flange
- Hole spacing: 60 mm diameter bolt circle
- Countersunk for flush mounting

## Bottle Holders

### Dimensions for Standard Reagent Bottles

**Bottle Specifications:**
- API Reagent Bottle: ~50mm diameter, 120mm tall
- Typical water bottle: ~70mm diameter

**Holder Recesses (4× total):**

1. **RO Water** (larger):
   - Diameter: 75 mm
   - Depth: 130 mm
   - Location: X=70, Y=130 (from front-left corner)

2. **Test Water** (larger):
   - Diameter: 75 mm
   - Depth: 130 mm
   - Location: X=150, Y=130

3. **Reagent #1**:
   - Diameter: 55 mm
   - Depth: 130 mm
   - Location: X=70, Y=200

4. **Reagent #2**:
   - Diameter: 55 mm
   - Depth: 130 mm
   - Location: X=150, Y=200

**Features:**
- Bottom drain holes: 5mm diameter (in case of spills)
- Lip height: 10mm (holds bottle in place)
- Tolerance: +2mm for easy bottle insertion

## Pump Mounting Brackets

### Peristaltic Pump Dimensions (Typical)

```
Length: 100 mm
Width: 50 mm
Height: 45 mm
Mounting holes: 2× M4 (80mm spacing)
```

### Bracket Specifications

**Location:** Right side panel

**FeW Pump (Water):**
- Position: X=280, Y=100, Z=150
- Mounting: L-bracket
- Orientation: Vertical
- Motor shaft: Horizontal

**FeR Pump (Reagent):**
- Position: X=280, Y=180, Z=150
- Mounting: L-bracket
- Orientation: Vertical
- Motor shaft: Horizontal

**Bracket Design:**
- Material: 3mm PETG or acrylic
- Base: 60 × 110 mm
- Height: 55 mm
- Mounting to enclosure: 4× M3 screws
- Pump mounting: 2× M4 screws (80mm spacing)
- Cable pass-through: 10mm diameter hole

## Valve Mounting Plate

### Solenoid Valve Specifications

**Adafruit 6V Air Valve (PID 4663):**
```
Body: 38 × 28 × 20 mm
Ports: 3× barbed (6mm)
Mounting: 2× M3 (32mm spacing)
```

### Mounting Plate

**Location:** Bottom of enclosure, accessible from rear

**Dimensions:**
- Length: 200 mm
- Width: 60 mm
- Thickness: 3 mm

**Valve Positions (3× valves):**

1. **ReV (Reagent Valve)**:
   - Position: X=30, Y=30
   - Mounting: 2× M3, 32mm vertical spacing

2. **WtV (Water Test Valve)**:
   - Position: X=90, Y=30
   - Mounting: 2× M3, 32mm vertical spacing

3. **WaV (Waste Valve)**:
   - Position: X=150, Y=30
   - Mounting: 2× M3, 32mm vertical spacing

**Plate Mounting to Enclosure:**
- 4× M3 screws at corners
- Standoffs: 10mm height (clearance for tubing)

## Electronics Bay

### Location
Right side panel, top section

### Dimensions
```
Width: 80 mm
Depth: 150 mm
Height: 100 mm
```

### Component Mounting

**DC Motor FeatherWing:**
- Size: 60 × 25 mm
- Mounting: 4× M2.5 standoffs (15mm)
- Location: X=270, Y=50, Z=200

**Solenoid Driver Board:**
- Size: 50 × 30 mm
- Mounting: 4× M2.5 standoffs (15mm)
- Location: X=270, Y=90, Z=200

**Power Distribution Block:**
- Size: 40 × 30 mm
- Location: X=270, Y=130, Z=200
- DIN rail mount (optional)

### Cable Management

**Channels:**
- Width: 15 mm
- Depth: 10 mm
- Routes from electronics bay to:
  - Pumps (right side)
  - Valves (bottom)
  - PyBadge (front)
  - Sensor (cuvette holder)

**Cable Tie Points:**
- Every 50mm along channels
- 5mm diameter holes for zip ties

## Waste Container

### Mounting

**Location:** Rear panel, external

**Opening:**
- Diameter: 30 mm
- Height from base: 50 mm
- Grommet: Rubber, 32mm OD

**Container Hook:**
- Type: S-hook or bracket
- Capacity: 500mL bottle

## Ventilation

### Air Flow

**Intake:** Bottom panel, rear
- 10× slots, each 50 × 5 mm
- Dust filter mount (optional)

**Exhaust:** Rear panel, top
- 8× slots, each 50 × 5 mm

**Purpose:**
- Cool electronics
- Ventilate any reagent fumes
- Passive convection (no fan needed)

## Access Panels

### Top Panel (Removable)

**Dimensions:** 340 × 240 mm

**Mounting:**
- 6× M3 screws with knurled knobs (tool-free)
- Captive nuts in enclosure walls

**Features:**
- Access to bottles, pumps, electronics
- Transparent acrylic option (see inside during operation)

### Rear Panel

**Features:**
- Cable pass-throughs:
  - Power: 12mm diameter grommet
  - USB (PyBadge): 10mm × 5mm slot
  - Data/expansion: 20mm diameter knockout
- Waste tube pass-through: 10mm grommet

## Material Specifications

### 3D Printing

**Enclosure Body:**
- Material: PLA or PETG
- Color: Black or dark gray (light blocking)
- Print orientation: Walls vertical
- Layer adhesion: Critical (use high bed temp)

**Cuvette Holder:**
- Material: Black PETG (opaque, chemical resistant)
- Infill: 50% (structural)
- Print orientation: Flange down

**Bottle Caps:**
- Material: PETG (chemical resistant)
- Thread pitch: 0.4mm layers recommended
- Post-processing: Thread with tap if needed

### Alternative: Laser Cutting

**Panels (if using laser cutter instead of 3D printing):**
- Material: 3mm black acrylic or plywood
- Joints: Finger joints or tab/slot
- Assembly: M3 screws + nuts
- Estimated sheets: 600 × 400 mm (2-3 sheets)

## Tolerances

### Clearances

```
Sliding fit (bottles): +1.0mm to +2.0mm
Snap fit: +0.2mm to +0.5mm
Press fit: -0.1mm to +0.1mm
Threaded parts: +0.3mm for printed threads
```

### Critical Dimensions

**Cuvette positioning:** ±0.5mm (affects optical alignment)
**Mounting holes:** ±0.2mm
**Bottle holders:** ±2mm (not critical)

## Weight Estimate

```
Enclosure (printed): ~1.2 kg
Cuvette holder: ~100 g
Mounting brackets: ~200 g
Electronics: ~300 g
Pumps: ~400 g (2×)
Bottles (full): ~2 kg (4×)
Total: ~4.2 kg
```

## Center of Gravity

With all bottles full:
- X: 175 mm (centered)
- Y: 160 mm (slightly rear)
- Z: 140 mm (lower half)

**Stability:** Rubber feet prevent tipping, low CG ensures stability

## Modifications for Future Versions

### Multi-Sample Carousel

**Expansion space available:**
- Left side panel: 100mm × 200mm area
- Can fit 6-position carousel
- Requires motor and indexing mechanism

### Additional Sensors

**Spare sensor bay:**
- Bottom front corner: 60 × 60 mm
- pH probe, temperature, conductivity, etc.

### WiFi Module

**ESP32 mount location:**
- Electronics bay has space
- Antenna position: top panel for best signal

## Assembly Hardware BOM

| Item | Size | Quantity | Purpose |
|------|------|----------|---------|
| M3 × 10mm screws | Phillips/hex | 20 | Panel assembly |
| M3 × 20mm screws | Phillips/hex | 8 | Pump mounts |
| M3 nuts | Hex | 28 | Fasteners |
| M3 washers | Flat | 28 | Load distribution |
| M2.5 × 8mm screws | Phillips | 12 | PyBadge, electronics |
| M2.5 standoffs | 15mm | 8 | Electronics mounting |
| M4 × 16mm screws | Phillips/hex | 4 | Pump mounting |
| M4 nuts | Hex | 4 | Pump fasteners |
| Rubber feet | 12mm dia, adhesive | 4 | Bottom of enclosure |
| Cable ties | 100mm | 20 | Cable management |
| O-rings | Various sizes | 4 | Bottle cap seals |
| Grommets | 10-30mm | 5 | Cable/tube pass-throughs |

## Design Files Generated

### FreeCAD Files (to be created)
- `openreef_enclosure.FCStd` - Main enclosure body
- `cuvette_holder_dual_led.FCStd` - Modified IoRodeo design

### OpenSCAD Files (parametric, included)
- `bottle_cap_3port.scad` - Customizable bottle caps
- `pump_mount.scad` - L-bracket for pumps
- `valve_plate.scad` - Valve mounting plate

### Export Formats
- STEP (.step) - For editing in other CAD programs
- STL (.stl) - For 3D printing
- DXF (.dxf) - For laser cutting (2D panels)

## Next Steps

1. Modify IoRodeo colorimeter enclosure in FreeCAD (see enclosure_modifications.md)
2. Generate OpenSCAD parametric parts
3. Export STL files for 3D printing
4. Create assembly diagrams
5. Test fit with actual components
