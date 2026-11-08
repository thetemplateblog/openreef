/*
 * OpenReef Complete Enclosure - Full Assembly
 *
 * Complete parametric model of the OpenReef automated assay system
 * Includes: Main enclosure, bottle holders, mounting points, panels
 *
 * To view:
 * 1. Open in OpenSCAD (free: https://openscad.org)
 * 2. Press F5 for preview (fast)
 * 3. Press F6 for full render (slower but better quality)
 * 4. Export to STEP or STL: File → Export
 * 5. Import into Fusion 360: File → Open
 *
 * License: MIT
 */

// ============ PARAMETERS ============

// Main enclosure dimensions
enclosure_length = 350;          // X-axis (mm)
enclosure_width = 250;           // Y-axis (mm)
enclosure_height = 300;          // Z-axis (mm)
wall_thickness = 3;              // Wall thickness (mm)
base_thickness = 5;              // Bottom panel thickness (mm)

// Bottle holder dimensions
bottle_large_diameter = 75;      // RO and test water bottles (mm)
bottle_small_diameter = 55;      // Reagent bottles (mm)
bottle_holder_depth = 130;       // Depth of bottle recesses (mm)

// PyBadge cutout (front panel)
pybadge_width = 110;
pybadge_height = 80;
pybadge_offset_x = 20;           // From left edge
pybadge_offset_z = 200;          // From bottom

// Cuvette holder mount (front panel)
cuvette_holder_diameter = 70;    // Flange diameter
cuvette_offset_x = 180;          // From left edge
cuvette_offset_z = 200;          // From bottom

// Pump mounting (right side panel)
pump_mount_width = 20;
pump_mount_height = 90;
pump_spacing = 80;               // Vertical spacing between pumps

// Valve mounting (bottom panel)
valve_plate_length = 200;
valve_plate_width = 60;
valve_spacing = 60;              // Spacing between valves

// Ventilation
vent_slot_width = 50;
vent_slot_height = 5;
vent_slot_spacing = 10;

// Rendering quality
$fn = 100;  // Circle resolution (higher = smoother, slower)
            // Use 50 for preview (F5), 100 for final render (F6)

// Display options - set to true/false to show/hide parts
show_enclosure_body = true;
show_top_panel = true;
show_bottle_holders = true;
show_pybadge_cutout = true;
show_cuvette_mount = true;
show_pump_mounts = true;
show_valve_mounting = true;
show_electronics_bay = true;
show_ventilation = true;
show_cable_channels = true;

// Transparency for visualization (0=solid, 1=invisible)
enclosure_alpha = 0.7;  // Set to 1.0 for solid, 0.3 for see-through

// ============ MAIN ASSEMBLY ============

module openreef_complete_assembly() {

    // Main enclosure body
    if (show_enclosure_body) {
        color("DarkSlateGray", enclosure_alpha)
            enclosure_body();
    }

    // Top panel (removable)
    if (show_top_panel) {
        color("DarkSlateGray", 0.5)
            translate([0, 0, enclosure_height - wall_thickness])
                top_panel();
    }

    // Internal features
    if (show_bottle_holders) {
        // Visualize bottle holder positions
        color("LightBlue", 0.3)
            bottle_holders();
    }

    if (show_pump_mounts) {
        color("Gray", 0.8)
            pump_mounting_bosses();
    }

    if (show_valve_mounting) {
        color("Silver", 0.8)
            valve_mounting_plate_area();
    }

    if (show_electronics_bay) {
        color("Green", 0.6)
            electronics_bay_standoffs();
    }
}

// ============ ENCLOSURE BODY ============

module enclosure_body() {
    difference() {
        // Outer shell
        cube([enclosure_length, enclosure_width, enclosure_height]);

        // Hollow interior (remove top)
        translate([wall_thickness, wall_thickness, base_thickness])
            cube([
                enclosure_length - 2*wall_thickness,
                enclosure_width - 2*wall_thickness,
                enclosure_height - base_thickness
            ]);

        // PyBadge cutout (front panel)
        if (show_pybadge_cutout) {
            translate([pybadge_offset_x, -1, pybadge_offset_z])
                cube([pybadge_width, wall_thickness + 2, pybadge_height]);

            // PyBadge mounting holes
            pybadge_mount_holes();
        }

        // Cuvette holder mount cutout
        if (show_cuvette_mount) {
            translate([cuvette_offset_x, -1, cuvette_offset_z])
                cylinder(h=wall_thickness + 2, d=cuvette_holder_diameter);

            // Cuvette mounting holes
            cuvette_mount_holes();
        }

        // Bottle holder recesses (top)
        if (show_bottle_holders) {
            bottle_holder_cutouts();
        }

        // Ventilation slots
        if (show_ventilation) {
            ventilation_slots();
        }

        // Cable pass-throughs
        if (show_cable_channels) {
            cable_passthroughs();
        }
    }

    // Add internal features (bosses, standoffs)
    pump_mounting_bosses();
    electronics_bay_standoffs();
    valve_mounting_plate_area();
}

// ============ TOP PANEL ============

module top_panel() {
    difference() {
        // Main panel
        cube([
            enclosure_length - 2*wall_thickness,
            enclosure_width - 2*wall_thickness,
            wall_thickness
        ]);

        // Mounting screw holes (6 positions)
        for (x = [20, enclosure_length/2, enclosure_length - 40]) {
            for (y = [20, enclosure_width - 40]) {
                translate([x, y, -1])
                    cylinder(h=wall_thickness + 2, d=3.5);
            }
        }
    }
}

// ============ BOTTLE HOLDERS ============

module bottle_holder_cutouts() {
    // Positions: [x, y, diameter]
    bottle_positions = [
        [70, 130, bottle_large_diameter],   // RO water
        [150, 130, bottle_large_diameter],  // Test water
        [70, 200, bottle_small_diameter],   // Reagent 1
        [150, 200, bottle_small_diameter]   // Reagent 2
    ];

    for (pos = bottle_positions) {
        translate([pos[0], pos[1], enclosure_height - bottle_holder_depth])
            cylinder(h=bottle_holder_depth + 1, d=pos[2]);

        // Drainage hole at bottom
        translate([pos[0], pos[1], base_thickness - 1])
            cylinder(h=base_thickness + 2, d=5);
    }
}

module bottle_holders() {
    // Visual representation of bottles (for preview)
    bottle_positions = [
        [70, 130, bottle_large_diameter, "RO Water"],
        [150, 130, bottle_large_diameter, "Test Water"],
        [70, 200, bottle_small_diameter, "Reagent 1"],
        [150, 200, bottle_small_diameter, "Reagent 2"]
    ];

    for (pos = bottle_positions) {
        translate([pos[0], pos[1], enclosure_height - bottle_holder_depth])
            cylinder(h=100, d=pos[2] - 5);  // Bottle visualization
    }
}

// ============ PYBADGE MOUNT ============

module pybadge_mount_holes() {
    // 4 mounting holes in corners
    hole_spacing_x = 100;
    hole_spacing_y = 70;
    base_x = pybadge_offset_x + (pybadge_width - hole_spacing_x) / 2;
    base_z = pybadge_offset_z + (pybadge_height - hole_spacing_y) / 2;

    for (x = [0, hole_spacing_x]) {
        for (z = [0, hole_spacing_y]) {
            translate([base_x + x, -1, base_z + z])
                rotate([-90, 0, 0])
                    cylinder(h=wall_thickness + 2, d=2.7);  // M2.5 holes
        }
    }
}

// ============ CUVETTE HOLDER MOUNT ============

module cuvette_mount_holes() {
    // 4 mounting holes on flange (60mm bolt circle)
    bolt_circle_dia = 60;

    for (angle = [45, 135, 225, 315]) {
        rotate([0, 0, angle])
            translate([
                cuvette_offset_x + bolt_circle_dia/2 * cos(angle),
                -1,
                cuvette_offset_z + bolt_circle_dia/2 * sin(angle)
            ])
                rotate([-90, 0, 0])
                    cylinder(h=wall_thickness + 2, d=3.5);  // M3 holes
    }
}

// ============ PUMP MOUNTING BOSSES ============

module pump_mounting_bosses() {
    // Right side panel, interior surface
    boss_x = enclosure_length - wall_thickness - 5;

    // FeW pump (water)
    translate([boss_x, 0, 100])
        pump_mounting_boss();

    // FeR pump (reagent)
    translate([boss_x, 0, 180])
        pump_mounting_boss();
}

module pump_mounting_boss() {
    difference() {
        // Boss body
        translate([0, 50, 0])
            cube([5, pump_mount_width, pump_mount_height]);

        // Mounting holes (4 per pump)
        hole_spacing = 80;  // Vertical spacing
        hole_positions = [10, 10 + hole_spacing];

        for (z = hole_positions) {
            for (y = [55, 65]) {
                translate([-1, y, z])
                    rotate([0, 90, 0])
                        cylinder(h=7, d=3.5);  // M3 holes
            }
        }
    }
}

// ============ VALVE MOUNTING AREA ============

module valve_mounting_plate_area() {
    // Bottom interior - standoffs for valve mounting plate
    standoff_positions = [
        [enclosure_length/2 - valve_plate_length/2, enclosure_width/2 - valve_plate_width/2],
        [enclosure_length/2 + valve_plate_length/2, enclosure_width/2 - valve_plate_width/2],
        [enclosure_length/2 - valve_plate_length/2, enclosure_width/2 + valve_plate_width/2],
        [enclosure_length/2 + valve_plate_length/2, enclosure_width/2 + valve_plate_width/2]
    ];

    for (pos = standoff_positions) {
        translate([pos[0], pos[1], base_thickness])
            standoff(height=10, diameter=8, hole_diameter=3.5);
    }
}

module standoff(height, diameter, hole_diameter) {
    difference() {
        cylinder(h=height, d=diameter);
        translate([0, 0, -1])
            cylinder(h=height + 2, d=hole_diameter);
    }
}

// ============ ELECTRONICS BAY ============

module electronics_bay_standoffs() {
    // Right side panel - standoffs for electronics boards
    bay_x = enclosure_length - wall_thickness - 20;
    bay_y = 50;
    bay_z = 200;

    // Motor FeatherWing standoffs (4 in rectangle)
    standoff_spacing = [[0, 0], [60, 0], [0, 25], [60, 25]];

    for (offset = standoff_spacing) {
        translate([bay_x, bay_y + offset[0], bay_z + offset[1]])
            rotate([0, 90, 0])
                standoff(height=15, diameter=6, hole_diameter=2.7);  // M2.5
    }

    // Solenoid driver standoffs (offset below)
    for (offset = standoff_spacing) {
        translate([bay_x, bay_y + offset[0], bay_z + offset[1] - 50])
            rotate([0, 90, 0])
                standoff(height=15, diameter=6, hole_diameter=2.7);
    }
}

// ============ VENTILATION ============

module ventilation_slots() {
    // Bottom panel - intake vents (rear)
    for (i = [0:9]) {
        translate([
            enclosure_length - 150 + i * (vent_slot_width + vent_slot_spacing),
            enclosure_width - 50,
            -1
        ])
            cube([vent_slot_width, vent_slot_height, base_thickness + 2]);
    }

    // Rear panel - exhaust vents (top)
    for (i = [0:7]) {
        translate([
            20 + i * (vent_slot_width + vent_slot_spacing),
            enclosure_width - wall_thickness - 1,
            enclosure_height - 50
        ])
            cube([vent_slot_width, wall_thickness + 2, vent_slot_height]);
    }
}

// ============ CABLE MANAGEMENT ============

module cable_passthroughs() {
    // Rear panel pass-throughs

    // Power cable (12V)
    translate([enclosure_length/2 - 50, enclosure_width - wall_thickness - 1, 50])
        rotate([-90, 0, 0])
            cylinder(h=wall_thickness + 2, d=12);

    // USB (PyBadge)
    translate([enclosure_length/2, enclosure_width - wall_thickness - 1, 100])
        cube([10, wall_thickness + 2, 5]);

    // Waste tube
    translate([enclosure_length/2 + 50, enclosure_width - wall_thickness - 1, 50])
        rotate([-90, 0, 0])
            cylinder(h=wall_thickness + 2, d=10);
}

// ============ LABELS (optional) ============

module add_labels() {
    // Embossed text labels (requires render, slow)
    label_depth = 0.5;

    // Front panel
    translate([20, 1, 180])
        rotate([90, 0, 0])
            linear_extrude(height=label_depth)
                text("PyBadge", size=6);

    translate([180, 1, 180])
        rotate([90, 0, 0])
            linear_extrude(height=label_depth)
                text("Cuvette", size=6);
}

// ============ RENDER ============

// Main assembly
openreef_complete_assembly();

// Uncomment to add labels (slow to render)
// add_labels();

// ============ INSTRUCTIONS ============

/*
 * VIEWING IN OPENSCAD:
 *
 * 1. Press F5 for quick preview (use $fn=50 for speed)
 * 2. Press F6 for full render (use $fn=100 for quality)
 * 3. Use mouse to orbit (left drag), pan (right drag), zoom (scroll)
 *
 * CUSTOMIZATION:
 *
 * Change parameters at top of file:
 * - enclosure_length = 350;  // Make larger/smaller
 * - bottle_large_diameter = 75;  // Fit your bottles
 * - $fn = 50;  // Lower for preview, 100 for final
 *
 * TRANSPARENCY:
 *
 * See inside the enclosure:
 * - enclosure_alpha = 0.3;  // More transparent
 * - enclosure_alpha = 1.0;  // Solid
 *
 * EXPORT:
 *
 * After rendering (F6):
 * 1. File → Export → Export as STL
 *    Save to: openreef_enclosure.stl
 *
 * 2. OR better: File → Export → Export as CSG
 *    Then use FreeCAD to convert CSG → STEP:
 *    - FreeCAD → File → Open (CSG)
 *    - File → Export → STEP
 *
 * 3. Import STEP into Fusion 360:
 *    Fusion 360 → File → Open → openreef_enclosure.step
 *
 * PRINT PREPARATION:
 *
 * 1. Open STL in your slicer (Cura, PrusaSlicer, etc.)
 * 2. Orient for optimal printing
 * 3. Add supports if needed
 * 4. Slice and print
 *
 * Estimated print time: 30-40 hours (depending on printer)
 * Estimated material: ~1.5 kg PLA/PETG
 *
 * MODULAR PRINTING:
 *
 * Too big for your printer? Split into panels:
 * - Uncomment individual parts
 * - Print each panel separately
 * - Assemble with screws/glue
 */
