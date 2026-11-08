/*
 * OpenReef Peristaltic Pump L-Bracket Mount
 *
 * Parametric mounting bracket for peristaltic pumps
 * Features:
 * - L-shaped bracket for vertical pump mounting
 * - Adjustable dimensions for different pump sizes
 * - Mounting holes for pump and enclosure
 * - Cable management slot
 *
 * License: MIT
 * Based on: OpenReef project (openreef.org)
 */

// ============ PARAMETERS (Adjust these) ============

// Pump mounting holes
pump_mounting_hole_spacing = 80;   // Distance between pump mounting holes (mm)
pump_mounting_hole_diameter = 4.5; // M4 screws (mm)
pump_width = 50;                   // Width of pump body (mm)
pump_length = 100;                 // Length of pump body (mm)
pump_height = 45;                  // Height of pump (mm)

// Bracket dimensions
bracket_base_width = 60;           // Width of base plate (mm)
bracket_base_length = 110;         // Length of base plate (mm)
bracket_vertical_height = 55;      // Height of vertical plate (mm)
bracket_thickness = 3;             // Thickness of bracket material (mm)

// Enclosure mounting holes
enclosure_mounting_holes = 4;      // Number of holes to mount to enclosure
enclosure_hole_diameter = 3.5;     // M3 screws (mm)
enclosure_hole_spacing_x = 50;     // Spacing between holes horizontally (mm)
enclosure_hole_spacing_y = 100;    // Spacing between holes vertically (mm)

// Cable management
cable_slot_width = 10;             // Width of cable slot (mm)
cable_slot_height = 5;             // Height of cable slot (mm)

// Reinforcement
add_gusset = true;                 // Add triangular gusset for strength
gusset_height = 30;                // Height of gusset triangle (mm)

// Print settings
$fn = 50;                          // Resolution

// ============ CALCULATIONS ============

total_width = max(bracket_base_width, pump_width + 10);
total_length = max(bracket_base_length, pump_length + 10);

// ============ MAIN MODEL ============

module pump_mount_bracket() {
    difference() {
        union() {
            // Base plate (horizontal)
            cube([total_length, total_width, bracket_thickness]);

            // Vertical plate
            translate([0, 0, 0])
                cube([total_length, bracket_thickness, bracket_vertical_height]);

            // Gusset reinforcement
            if (add_gusset) {
                translate([total_length/2 - gusset_height/2, bracket_thickness, 0])
                    rotate([90, 0, 0])
                        linear_extrude(height=bracket_thickness)
                            polygon(points=[
                                [0, 0],
                                [gusset_height, 0],
                                [gusset_height/2, gusset_height]
                            ]);
            }

            // Corner reinforcement blocks
            for (x = [0, total_length - 10]) {
                translate([x, 0, 0])
                    cube([10, 10, 10]);
            }
        }

        // Pump mounting holes (vertical plate)
        pump_hole_offset_z = bracket_vertical_height / 2;
        pump_hole_offset_x1 = (total_length - pump_mounting_hole_spacing) / 2;
        pump_hole_offset_x2 = pump_hole_offset_x1 + pump_mounting_hole_spacing;

        translate([pump_hole_offset_x1, -1, pump_hole_offset_z])
            rotate([-90, 0, 0])
                cylinder(h=bracket_thickness + 2, d=pump_mounting_hole_diameter);

        translate([pump_hole_offset_x2, -1, pump_hole_offset_z])
            rotate([-90, 0, 0])
                cylinder(h=bracket_thickness + 2, d=pump_mounting_hole_diameter);

        // Countersink for pump mounting holes (optional)
        translate([pump_hole_offset_x1, bracket_thickness, pump_hole_offset_z])
            rotate([-90, 0, 0])
                cylinder(h=2, d1=pump_mounting_hole_diameter, d2=pump_mounting_hole_diameter + 2);

        translate([pump_hole_offset_x2, bracket_thickness, pump_hole_offset_z])
            rotate([-90, 0, 0])
                cylinder(h=2, d1=pump_mounting_hole_diameter, d2=pump_mounting_hole_diameter + 2);

        // Enclosure mounting holes (base plate)
        enclosure_hole_x1 = (total_length - enclosure_hole_spacing_x) / 2;
        enclosure_hole_x2 = enclosure_hole_x1 + enclosure_hole_spacing_x;
        enclosure_hole_y1 = (total_width - enclosure_hole_spacing_y) / 2;
        enclosure_hole_y2 = enclosure_hole_y1 + enclosure_hole_spacing_y;

        for (x = [enclosure_hole_x1, enclosure_hole_x2]) {
            for (y = [enclosure_hole_y1, enclosure_hole_y2]) {
                translate([x, y, -1])
                    cylinder(h=bracket_thickness + 2, d=enclosure_hole_diameter);

                // Countersink for flush mounting
                translate([x, y, bracket_thickness - 1.5])
                    cylinder(h=2, d1=enclosure_hole_diameter, d2=enclosure_hole_diameter + 3);
            }
        }

        // Cable management slot
        translate([total_length - 20, total_width/2 - cable_slot_width/2, bracket_thickness - cable_slot_height])
            cube([20, cable_slot_width, cable_slot_height + 1]);

        // Cable pass-through hole
        translate([total_length - 10, total_width/2, -1])
            cylinder(h=bracket_thickness + 2, d=8);
    }
}

// ============ RENDER ============

pump_mount_bracket();

// ============ PRINT INSTRUCTIONS ============

/*
 * PRINTING TIPS:
 *
 * 1. Orientation: Print with base plate flat on bed
 * 2. Layer height: 0.2mm
 * 3. Infill: 40% (needs strength)
 * 4. Supports: None needed with this orientation
 * 5. Material: PETG (strong, heat resistant) or PLA
 * 6. Perimeters: 4 perimeters for extra strength
 * 7. First layer: Critical - ensure good adhesion
 *
 * ASSEMBLY:
 *
 * 1. Mount bracket to enclosure using 4× M3 screws
 * 2. Verify bracket is level and secure
 * 3. Mount pump to bracket using 2× M4 screws
 * 4. Route cables through cable slot and pass-through hole
 * 5. Connect pump to motor driver
 *
 * CUSTOMIZATION:
 *
 * For different pump sizes:
 * - Measure pump mounting hole spacing with calipers
 * - Measure pump body dimensions
 * - Adjust parameters at top of file
 * - Ensure holes align before printing full size
 * - Consider printing small test piece first
 *
 * MATERIALS:
 *
 * Alternative to 3D printing:
 * - Laser cut from 3mm acrylic or plywood
 * - Bend aluminum sheet (1.5-2mm thickness)
 * - Export top view and side view as DXF
 *
 * HARDWARE REQUIRED:
 *
 * - 4× M3 × 10mm screws (enclosure mounting)
 * - 4× M3 nuts or threaded inserts
 * - 2× M4 × 16mm screws (pump mounting)
 * - 2× M4 nuts or threaded inserts
 * - Cable ties for cable management
 */
