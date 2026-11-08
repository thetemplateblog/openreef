/*
 * OpenReef Bottle Cap with 3 Tube Ports
 *
 * Parametric bottle cap design for reagent and water bottles
 * Features:
 * - Customizable thread diameter
 * - 3 tube pass-throughs (adjustable sizes)
 * - Air vent hole
 * - O-ring groove for sealing
 *
 * License: MIT
 * Based on: OpenReef project (openreef.org)
 *
 * To use:
 * 1. Open in OpenSCAD
 * 2. Adjust parameters below
 * 3. Press F5 to preview, F6 to render
 * 4. Export to STL (File → Export → STL)
 */

// ============ PARAMETERS (Adjust these) ============

// Bottle thread dimensions
bottle_outer_diameter = 42;  // Outer diameter of bottle opening (mm)
bottle_thread_pitch = 3.0;   // Thread pitch (mm)
thread_depth = 1.5;          // How deep the threads go (mm)
thread_starts = 1;           // Number of thread starts (usually 1 or 2)

// Cap dimensions
cap_height = 20;             // Total height of cap (mm)
cap_wall_thickness = 3;      // Wall thickness (mm)
top_thickness = 4;           // Thickness of top surface (mm)

// Tube ports
tube_port_1_diameter = 6;    // Port 1: large tube (mm) - e.g., water in/out
tube_port_2_diameter = 4;    // Port 2: medium tube (mm) - e.g., reagent
tube_port_3_diameter = 2;    // Port 3: small tube (mm) - e.g., air line

port_length = 15;            // How far ports extend from cap (mm)
port_wall_thickness = 1.5;   // Wall thickness of tube ports (mm)

// Air vent
air_vent_diameter = 1.5;     // Air vent hole diameter (mm)

// O-ring groove
o_ring_enabled = true;       // Set to false to disable o-ring groove
o_ring_diameter = 2;         // O-ring wire diameter (mm)
o_ring_groove_width = 2.5;   // Width of groove (mm)
o_ring_groove_depth = 1.5;   // Depth of groove (mm)

// Print settings
$fn = 100;                   // Resolution (higher = smoother, slower)

// ============ CALCULATIONS ============

cap_outer_diameter = bottle_outer_diameter + 2*cap_wall_thickness;
cap_inner_diameter = bottle_outer_diameter - 2*thread_depth;

// Port positions (evenly spaced around cap)
port_1_angle = 0;
port_2_angle = 120;
port_3_angle = 240;
port_radius = (cap_outer_diameter/2) * 0.6;  // Distance from center

// ============ MAIN MODEL ============

module bottle_cap() {
    difference() {
        union() {
            // Main cap body
            cylinder(h=cap_height, d=cap_outer_diameter);

            // Tube ports
            rotate([0, 0, port_1_angle])
                translate([port_radius, 0, top_thickness])
                    tube_port(tube_port_1_diameter, port_length);

            rotate([0, 0, port_2_angle])
                translate([port_radius, 0, top_thickness])
                    tube_port(tube_port_2_diameter, port_length);

            rotate([0, 0, port_3_angle])
                translate([port_radius, 0, top_thickness])
                    tube_port(tube_port_3_diameter, port_length);
        }

        // Hollow interior
        translate([0, 0, top_thickness])
            cylinder(h=cap_height, d=cap_inner_diameter + 0.5);

        // Internal threads
        translate([0, 0, top_thickness])
            internal_thread(
                diameter=bottle_outer_diameter,
                pitch=bottle_thread_pitch,
                length=cap_height - top_thickness,
                depth=thread_depth
            );

        // Tube port holes through top
        rotate([0, 0, port_1_angle])
            translate([port_radius, 0, 0])
                cylinder(h=top_thickness, d=tube_port_1_diameter);

        rotate([0, 0, port_2_angle])
            translate([port_radius, 0, 0])
                cylinder(h=top_thickness, d=tube_port_2_diameter);

        rotate([0, 0, port_3_angle])
            translate([port_radius, 0, 0])
                cylinder(h=top_thickness, d=tube_port_3_diameter);

        // Air vent hole
        translate([0, 0, 0])
            cylinder(h=top_thickness, d=air_vent_diameter);

        // O-ring groove
        if (o_ring_enabled) {
            translate([0, 0, cap_height - 5])
                rotate_extrude()
                    translate([bottle_outer_diameter/2 - thread_depth/2, 0, 0])
                        circle(d=o_ring_groove_width);
        }
    }

    // Gripping ridges on outside
    for (i = [0:11]) {
        rotate([0, 0, i*30])
            translate([cap_outer_diameter/2 - 1, 0, cap_height/2])
                cube([1.5, 3, cap_height - 4], center=true);
    }
}

// ============ HELPER MODULES ============

// Tube port with barbs
module tube_port(inner_dia, length) {
    outer_dia = inner_dia + 2*port_wall_thickness;

    difference() {
        union() {
            // Main tube
            cylinder(h=length, d=outer_dia);

            // Barbs (for tube retention)
            for (i = [1:3]) {
                translate([0, 0, i * (length/4)])
                    cylinder(h=1.5, d1=outer_dia, d2=outer_dia + 1);
            }
        }

        // Hollow center
        cylinder(h=length, d=inner_dia);
    }
}

// Simplified internal thread (helix approximation)
module internal_thread(diameter, pitch, length, depth) {
    thread_height = length;
    num_turns = thread_height / pitch;

    for (i = [0:num_turns*20]) {
        angle = i * 360 / 20;
        z = i * pitch / 20;

        if (z < thread_height) {
            rotate([0, 0, angle])
                translate([diameter/2 - depth/2, 0, z])
                    rotate([0, 90, 0])
                        cylinder(h=depth, d=pitch/2, $fn=4);
        }
    }
}

// ============ RENDER ============

bottle_cap();

// ============ PRINT INSTRUCTIONS ============

/*
 * PRINTING TIPS:
 *
 * 1. Orientation: Print cap upside-down (top on build plate)
 * 2. Layer height: 0.2mm
 * 3. Infill: 30%
 * 4. Supports: Not needed if printed upside-down
 * 5. Material: PETG (chemical resistant) or PLA
 * 6. Print temperature: PETG 240°C, PLA 210°C
 * 7. Bed temperature: PETG 70°C, PLA 60°C
 * 8. First layer: Slow, ensure good adhesion
 *
 * POST-PROCESSING:
 *
 * 1. Thread cleanup: Use a tap to clean threads if needed
 * 2. Port cleanup: Drill out tube ports if too tight
 * 3. O-ring: Install 2mm o-ring in groove before use
 * 4. Test fit: Verify threads mate with bottle
 *
 * CUSTOMIZATION:
 *
 * For different bottle sizes:
 * - Measure bottle opening diameter
 * - Measure thread pitch with calipers
 * - Adjust parameters at top of file
 * - Re-render and print test cap
 *
 * For different tube sizes:
 * - Measure tube outer diameter
 * - Set port diameter = tube OD + 0.5mm (snug fit)
 * - Tube should push on with friction
 */
