// OpenReef self-refilling syringe pump
// NEMA17 + T8x2 lead screw + 5 mL glass luer-lock syringe + 2 check valves.
// Print: PETG, 0.2 mm layers, 4 walls, 30 % infill. Parts: frame, carriage, plunger_clip.
// Hardware: 4x M3x8 (motor), 2x M3x12 + nuts (syringe clamp), 1x micro switch (12.8x5.8 mm, 2x M2),
//           T8 brass nut (4x M3 on 16 mm PCD), 5->8 mm flexible coupler, 8 mm smooth rod 120 mm, LM8UU.

$fn = 64;
part = "all";            // "frame" | "carriage" | "plunger_clip" | "all"

// ---- syringe (5 mL glass luer lock, e.g. Fortuna Optima) ----
barrel_d   = 15.0;       // outer diameter of barrel
barrel_len = 72;         // barrel length from flange to luer tip
flange_w   = 30;         // flange width
flange_t   = 3.5;
plunger_rod_d = 8;       // plunger rod diameter (glass)
thumb_d    = 22;         // plunger thumb rest diameter
thumb_t    = 4;
stroke     = 45;         // usable stroke

// ---- mechanics ----
nema       = 42.3;
nema_hole  = 31;         // hole square
nema_boss  = 22.5;
screw_d    = 8;          // T8 lead screw
rod_d      = 8;          // guide rod
rod_x      = 24;         // rod offset from screw axis
nut_pcd    = 16;         // T8 brass nut flange holes
lm8uu_d    = 15.2;
lm8uu_len  = 24;
wall       = 5;
base_t     = 6;
width      = 60;         // frame width
height     = 70;         // frame height above base (screw axis at 35)
axis_z     = 35;
frame_len  = 25 + stroke + 15 + barrel_len + 10;   // motor block + travel + carriage + syringe

module frame() {
  difference() {
    union() {
      // base
      cube([frame_len, width, base_t]);
      // motor block
      translate([0, 0, 0]) cube([wall, width, height]);
      // bearing / end block (holds the far end of the screw + rod)
      translate([25 + stroke + 15 + 12, 0, 0]) cube([wall, width, height]);
      // syringe cradle
      translate([25 + stroke + 15 + 12 + wall, 0, 0]) cube([barrel_len + 10, width, axis_z]);   // half-pipe cradle, flush with the axis
    }
    // motor shaft + bolt pattern on the motor block
    translate([-1, width/2, axis_z]) rotate([0, 90, 0]) cylinder(d = nema_boss + 0.5, h = wall + 2);
    for (a = [45, 135, 225, 315])
      translate([-1, width/2 + nema_hole/2 * sqrt(2)/2 * cos(a), axis_z + nema_hole/2 * sqrt(2)/2 * sin(a)])
        rotate([0, 90, 0]) cylinder(d = 3.3, h = wall + 2);
    // guide rod in motor block (blind) and end block
    translate([wall - 4, width/2 + rod_x, axis_z]) rotate([0, 90, 0]) cylinder(d = rod_d + 0.2, h = 10);
    translate([25 + stroke + 15 + 12 - 1, width/2 + rod_x, axis_z]) rotate([0, 90, 0]) cylinder(d = rod_d + 0.2, h = wall + 2);
    // screw clearance in end block
    translate([25 + stroke + 15 + 12 - 1, width/2, axis_z]) rotate([0, 90, 0]) cylinder(d = screw_d + 2, h = wall + 2);
    // syringe barrel cradle (half pipe) + flange slot
    translate([25 + stroke + 15 + 12 + wall + 6, width/2, axis_z]) rotate([0, 90, 0]) cylinder(d = barrel_d + 0.6, h = barrel_len + 20);
    translate([25 + stroke + 15 + 12 + wall + 2, width/2 - flange_w/2 - 0.5, axis_z - 20]) cube([flange_t + 0.6, flange_w + 1, 30]);
    // luer tip exit
    translate([frame_len - 12, width/2, axis_z]) rotate([0, 90, 0]) cylinder(d = 9, h = 20);
    // endstop (micro switch) pocket on motor block face, triggers when carriage is fully retracted
    translate([wall - 0.01, width/2 - rod_x - 10, axis_z + 10]) cube([6, 13, 6]);
    // mounting slots in base (M4) to the enclosure shelf
    for (x = [12, frame_len - 12]) for (y = [8, width - 8])
      translate([x, y, -1]) hull() { cylinder(d = 4.4, h = base_t + 2); translate([0, 0, 0]) cylinder(d = 4.4, h = base_t + 2); }
    // syringe clamp bolt holes (M3) through cradle sides
    for (y = [width/2 - 12, width/2 + 12])
      translate([25 + stroke + 15 + 12 + wall + 30, y, -1]) cylinder(d = 3.3, h = axis_z + 10);
  }
}

module carriage() {
  // slides on the guide rod via LM8UU, driven by the T8 nut, pushes the plunger thumb rest.
  len = 15;
  difference() {
    union() {
      translate([0, -width/2, -axis_z + base_t + 1]) cube([len, width, height - base_t - 1 - 8]);
    }
    // T8 nut: through hole + flange bolt holes
    rotate([0, 90, 0]) translate([0, 0, -1]) cylinder(d = 10.4, h = len + 2);
    for (a = [0, 90, 180, 270]) rotate([0, 90, 0]) translate([nut_pcd/2 * sin(a), nut_pcd/2 * cos(a), -1]) cylinder(d = 3.2, h = len + 2);
    // LM8UU pocket
    translate([-5, rod_x, 0]) rotate([0, 90, 0]) cylinder(d = lm8uu_d, h = lm8uu_len + 1);
    // plunger thumb slot (captures the glass thumb rest so the pump can pull for refill)
    translate([len - 6, -thumb_d/2 - 0.4, 2]) cube([thumb_t + 0.6, thumb_d + 0.8, 40]);
    translate([len - 8, -plunger_rod_d/2 - 0.3, 2]) cube([10, plunger_rod_d + 0.6, 40]);
    // endstop flag is the carriage body itself
  }
}

module plunger_clip() {
  // snaps over the thumb slot so the plunger cannot jump out on the pull stroke
  difference() {
    cube([thumb_t + 8, thumb_d + 8, 6]);
    translate([4, 4, -1]) cube([thumb_t + 0.6, thumb_d + 0.8, 8]);
    for (x = [2, thumb_t + 6]) translate([x, (thumb_d + 8)/2, -1]) cylinder(d = 2.2, h = 8);
  }
}

if (part == "frame" || part == "all") frame();
if (part == "carriage" || part == "all") translate([35, width/2, axis_z]) carriage();
if (part == "plunger_clip" || part == "all") translate([frame_len + 20, 0, 0]) plunger_clip();

// Resolution reminder: 200 steps/rev x 16 microsteps / 2 mm lead = 1600 steps/mm.
// 5 mL syringe bore 12.0 mm -> 113 uL/mm -> 0.071 uL/step.
