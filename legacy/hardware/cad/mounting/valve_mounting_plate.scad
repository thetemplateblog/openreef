/*
 * OpenReef Solenoid Valve Mounting Plate
 *
 * Parametric mounting plate for 3 solenoid valves
 * Features:
 * - Mounts 3× Adafruit 6V Air Valves (PID 4663)
 * - Standoffs for tubing clearance
 * - Cable management features
 * - Modular design for easy expansion
 *
 * License: MIT
 * Based on: OpenReef project (openreef.org)
 */

// ============ PARAMETERS (Adjust these) ============

// Plate dimensions
plate_length = 200;                // Length of plate (mm)
plate_width = 60;                  // Width of plate (mm)
plate_thickness = 3;               // Thickness of plate (mm)

// Valve specifications (Adafruit 6V Air Valve PID 4663)
valve_mounting_hole_spacing = 32;  // Distance between valve mounting holes (mm)
valve_mounting_hole_diameter = 3.5; // M3 screws (mm)
valve_body_width = 28;             // Width of valve body (mm)
valve_body_length = 38;            // Length of valve body (mm)
num_valves = 3;                    // Number of valves

// Valve spacing
valve_spacing = 60;                // Distance between valve centers (mm)

// Enclosure mounting
enclosure_mount_holes = 4;         // Corners
enclosure_hole_diameter = 3.5;     // M3 screws (mm)
enclosure_hole_inset = 10;         // Distance from edge (mm)

// Standoffs (raise plate above enclosure for tubing)
add_standoffs = true;
standoff_height = 10;              // Height of standoffs (mm)
standoff_diameter = 8;             // Diameter of standoff (mm)

// Cable routing
cable_channel_width = 8;           // Width of cable channel (mm)
cable_channel_depth = 2;           // Depth of cable channel (mm)

// Print settings
$fn = 50;                          // Resolution

// ============ CALCULATIONS ============

// Position valves evenly
valve_start_x = (plate_length - (num_valves - 1) * valve_spacing) / 2;

// ============ MAIN MODEL ============

module valve_mounting_plate() {
    difference() {
        union() {
            // Main plate
            cube([plate_length, plate_width, plate_thickness]);

            // Standoffs at corners (if enabled)
            if (add_standoffs) {
                for (x = [enclosure_hole_inset, plate_length - enclosure_hole_inset]) {
                    for (y = [enclosure_hole_inset, plate_width - enclosure_hole_inset]) {
                        translate([x, y, 0])
                            standoff(standoff_height, standoff_diameter, enclosure_hole_diameter);
                    }
                }
            }

            // Valve mounting bosses (raised areas around valve holes)
            for (i = [0 : num_valves - 1]) {
                valve_x = valve_start_x + i * valve_spacing;
                valve_y = plate_width / 2;

                translate([valve_x, valve_y, plate_thickness])
                    valve_mounting_boss();
            }
        }

        // Valve mounting holes
        for (i = [0 : num_valves - 1]) {
            valve_x = valve_start_x + i * valve_spacing;
            valve_y = plate_width / 2;

            // Two mounting holes per valve (vertical spacing)
            translate([valve_x, valve_y - valve_mounting_hole_spacing/2, -1])
                cylinder(h=plate_thickness + 10, d=valve_mounting_hole_diameter);

            translate([valve_x, valve_y + valve_mounting_hole_spacing/2, -1])
                cylinder(h=plate_thickness + 10, d=valve_mounting_hole_diameter);

            // Countersink for flush mounting
            translate([valve_x, valve_y - valve_mounting_hole_spacing/2, plate_thickness - 1])
                cylinder(h=2, d1=valve_mounting_hole_diameter, d2=valve_mounting_hole_diameter + 3);

            translate([valve_x, valve_y + valve_mounting_hole_spacing/2, plate_thickness - 1])
                cylinder(h=2, d1=valve_mounting_hole_diameter, d2=valve_mounting_hole_diameter + 3);

            // Valve body clearance (cutout for valve)
            translate([valve_x - valve_body_length/2, valve_y - valve_body_width/2, -1])
                cube([valve_body_length, valve_body_width, plate_thickness + 2]);
        }

        // Enclosure mounting holes (corners)
        for (x = [enclosure_hole_inset, plate_length - enclosure_hole_inset]) {
            for (y = [enclosure_hole_inset, plate_width - enclosure_hole_inset]) {
                translate([x, y, -1])
                    cylinder(h=plate_thickness + standoff_height + 2, d=enclosure_hole_diameter);
            }
        }

        // Cable channel (runs along bottom edge)
        translate([enclosure_hole_inset + 10, plate_width/2 - cable_channel_width/2, plate_thickness - cable_channel_depth])
            cube([plate_length - 2*(enclosure_hole_inset + 10), cable_channel_width, cable_channel_depth + 1]);

        // Cable pass-through holes (between valves)
        for (i = [0 : num_valves - 2]) {
            wire_hole_x = valve_start_x + (i + 0.5) * valve_spacing;

            translate([wire_hole_x, plate_width/2, -1])
                cylinder(h=plate_thickness + 2, d=5);
        }

        // Label engraving (valve numbers)
        for (i = [0 : num_valves - 1]) {
            valve_x = valve_start_x + i * valve_spacing;

            translate([valve_x, plate_width - 8, plate_thickness - 0.5])
                linear_extrude(height=0.6)
                    text(str(i + 1), size=5, halign="center", font="Liberation Sans:style=Bold");
        }
    }
}

// ============ HELPER MODULES ============

// Standoff cylinder with mounting hole
module standoff(height, diameter, hole_dia) {
    difference() {
        cylinder(h=height, d=diameter);
        translate([0, 0, -1])
            cylinder(h=height + 2, d=hole_dia);
    }
}

// Raised boss around valve mounting area
module valve_mounting_boss() {
    boss_height = 2;
    boss_width = valve_body_width + 6;
    boss_length = valve_body_length + 6;

    difference() {
        // Raised platform
        translate([-boss_length/2, -boss_width/2, 0])
            cube([boss_length, boss_width, boss_height]);

        // Chamfer edges for smoother transition
        translate([-boss_length/2, -boss_width/2, 0])
            rotate([0, 0, 0])
                chamfer_edge(boss_length, 1);

        translate([boss_length/2, -boss_width/2, 0])
            rotate([0, 0, 90])
                chamfer_edge(boss_width, 1);

        translate([boss_length/2, boss_width/2, 0])
            rotate([0, 0, 180])
                chamfer_edge(boss_length, 1);

        translate([-boss_length/2, boss_width/2, 0])
            rotate([0, 0, 270])
                chamfer_edge(boss_width, 1);
    }
}

// Chamfer edge for smooth transition
module chamfer_edge(length, size) {
    translate([0, 0, 0])
        rotate([0, 90, 0])
            linear_extrude(height=length)
                polygon(points=[[0, 0], [0, size], [size, 0]]);
}

// ============ RENDER ============

valve_mounting_plate();

// ============ ALTERNATE VIEWS ============

// Uncomment to see with valves positioned (for visualization)
/*
module valve_body_visualization() {
    // Simplified valve body representation
    color("gray", 0.7) {
        cube([valve_body_length, valve_body_width, 20], center=true);

        // Port stubs
        for (angle = [0, 120, 240]) {
            rotate([0, 0, angle])
                translate([valve_body_width/2 + 5, 0, 0])
                    rotate([0, 90, 0])
                        cylinder(h=10, d=6);
        }
    }
}

// Show valves positioned on plate
for (i = [0 : num_valves - 1]) {
    valve_x = valve_start_x + i * valve_spacing;
    valve_y = plate_width / 2;

    translate([valve_x, valve_y, plate_thickness + 5])
        valve_body_visualization();
}
*/

// ============ PRINT INSTRUCTIONS ============

/*
 * PRINTING TIPS:
 *
 * 1. Orientation: Print flat on bed
 * 2. Layer height: 0.2mm
 * 3. Infill: 30%
 * 4. Supports: None needed (standoffs print without support)
 * 5. Material: PETG (heat resistant) or PLA
 * 6. First layer: Critical for flatness
 * 7. Bed adhesion: Use brim if warping occurs
 *
 * POST-PROCESSING:
 *
 * 1. Remove any stringing between standoffs
 * 2. Clean mounting holes with drill if needed (3.0mm or 3.2mm)
 * 3. Test fit valves before final assembly
 * 4. Check that standoffs are uniform height
 *
 * ASSEMBLY:
 *
 * 1. Install M3 threaded inserts in standoffs (optional but recommended)
 * 2. Mount plate to enclosure bottom using 4× M3 × 20mm screws
 *    - Screws go through standoffs into enclosure
 *    - Standoffs create 10mm clearance for tubing
 * 3. Mount valves using 2× M3 × 10mm screws each (6 screws total)
 * 4. Route wires through cable channel and pass-through holes
 * 5. Connect tubing to valve ports
 * 6. Secure cables with small cable ties
 *
 * CUSTOMIZATION:
 *
 * For different valve models:
 * - Measure valve mounting hole spacing
 * - Measure valve body dimensions
 * - Adjust parameters at top of file
 * - Test fit before drilling/printing final version
 *
 * For more than 3 valves:
 * - Increase num_valves parameter
 * - Increase plate_length accordingly
 * - May need to adjust valve_spacing
 *
 * For different mounting:
 * - Disable standoffs: add_standoffs = false
 * - Use flat mounting directly to surface
 * - Adjust standoff_height for more/less clearance
 *
 * HARDWARE REQUIRED:
 *
 * - 4× M3 × 20mm screws (plate to enclosure)
 * - 4× M3 nuts or threaded inserts
 * - 6× M3 × 10mm screws (valves to plate)
 * - 6× M3 nuts or threaded inserts
 * - 3× Adafruit 6V Air Valves (PID 4663)
 * - Silicone tubing (3mm ID)
 * - Wire for valve control
 * - Cable ties (small)
 *
 * ALTERNATIVE MATERIALS:
 *
 * - Laser cut from 3mm acrylic (export 2D DXF)
 * - Aluminum sheet (1.5-2mm, bend standoffs separately)
 * - Plywood (3mm, for non-critical applications)
 */
