// OpenReef Cell B — light-tight holder for a 22 mm round glass cuvette (Hanna HI731331 style)
// with AS7341 spectral sensor on one side and two 5 mm LEDs (white + 850 nm IR) on the other.
// Print in BLACK PETG, 100 % infill walls (light-tight). Two parts: body and lid (cap with ports).
$fn = 72;
part = "all";   // "body" | "lid" | "all"

cuv_d     = 22.4;     // cuvette OD + clearance
cuv_h     = 55;       // holder height (cuvette is ~95 mm tall; top sticks out through the lid)
block     = 48;       // body footprint
optic_z   = 22;       // optical axis height above the holder base (above the stir bar)
led_d     = 5.3;
led_sep   = 8;        // vertical separation of the two LEDs
sensor_win = 4;       // aperture to the sensor
pcb_w = 26.0; pcb_h = 18.5; pcb_t = 1.8;   // Adafruit AS7341 breakout pocket
stir_d = 26; stir_h = 12;                  // 40 mm fan + magnets sits below in the shelf cut-out

module body() {
  difference() {
    translate([-block/2, -block/2, 0]) cube([block, block, cuv_h]);
    // cuvette bore
    translate([0, 0, 3]) cylinder(d = cuv_d, h = cuv_h);
    // optical aperture to sensor (+X side)
    translate([0, 0, optic_z]) rotate([0, 90, 0]) cylinder(d = sensor_win, h = block);
    // sensor PCB pocket on +X face, window centred on optical axis
    translate([block/2 - pcb_t - 0.4, -pcb_w/2, optic_z - pcb_h/2]) cube([pcb_t + 1, pcb_w, pcb_h]);
    // PCB screw holes (M2.5), 20.3 mm apart on the Adafruit board
    for (y = [-10.15, 10.15]) translate([block/2 - 6, y, optic_z - pcb_h/2 + 2]) rotate([0, 90, 0]) cylinder(d = 2.2, h = 8);
    // LEDs on -X side: white above axis, IR below axis, both aimed at the bore centre
    for (dz = [led_sep/2, -led_sep/2])
      translate([-block/2 - 1, 0, optic_z + dz]) rotate([0, 90, 0]) cylinder(d = led_d, h = block/2 - cuv_d/2 + 2);
    // LED leg channels out the bottom
    translate([-block/2 + 4, -4, -1]) cube([6, 8, optic_z]);
    // stir magnet clearance under the cuvette
    translate([0, 0, -1]) cylinder(d = stir_d, h = 4.5);
    // mounting holes to shelf (M3)
    for (x = [-block/2 + 5, block/2 - 5]) for (y = [-block/2 + 5, block/2 - 5])
      translate([x, y, -1]) cylinder(d = 3.3, h = 10);
  }
}

module lid() {
  // slips over the cuvette top; carries fill, level, drain and four reagent tips + vent.
  lid_h = 14; tube_d = 3.4;
  difference() {
    union() { cylinder(d = cuv_d + 8, h = lid_h); translate([0, 0, -6]) cylinder(d = cuv_d - 0.6, h = 6.5); }
    translate([0, 0, -7]) cylinder(d = cuv_d - 4.6, h = 6);          // thin skirt inside the cuvette
    for (a = [0 : 45 : 315]) rotate([0, 0, a]) translate([6.5, 0, -8]) cylinder(d = tube_d, h = lid_h + 10);   // 8 ports
  }
}

if (part == "body" || part == "all") body();
if (part == "lid" || part == "all") translate([block + 20, 0, 0]) lid();

// Level dip tube: 10.0 mL mark is ~36 mm above the inside bottom of a HI731331 cuvette;
// trim the tube so its tip sits there, then calibrate volume with a scale.
