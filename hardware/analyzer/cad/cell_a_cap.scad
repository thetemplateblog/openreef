// OpenReef Cell A cap — titration cell (60 mL borosilicate vial, 40 mm OD, GL45-style neck)
// Carries: pH electrode (12 mm), DS18B20 (6 mm), fill tube, level dip tube (sets the 20 mL volume),
// drain dip tube (to bottom), acid drip tip (above liquid), vent. Press-fit into the neck with an
// O-ring (38 x 2 mm). Print in PETG, 100 % infill for the plug section.
$fn = 72;

neck_id   = 36.0;    // inner diameter of vial neck
cap_od    = 48;      // outer flange diameter
plug_h    = 10;      // section inside the neck
flange_h  = 6;
tube_d    = 3.4;     // 1/8" OD tubing / PTFE 1/16" ID lines
level_depth = 48;    // mm from cap underside to level-tube tip -> set for 20.0 mL in your vial
drain_depth = 82;    // reaches vial bottom

module cap() {
  difference() {
    union() {
      cylinder(d = cap_od, h = flange_h);
      translate([0, 0, -plug_h]) cylinder(d = neck_id - 0.3, h = plug_h);
      // O-ring groove ridge
      translate([0, 0, -plug_h + 3]) difference() { cylinder(d = neck_id - 0.3, h = 2.4); cylinder(d = neck_id - 3.4, h = 2.4); }
    }
    // pH electrode, slightly off-centre so the stir bar vortex is not under it
    translate([-6, 0, -plug_h - 1]) cylinder(d = 12.3, h = plug_h + flange_h + 2);
    // DS18B20 stainless probe
    translate([9, 8, -plug_h - 1]) cylinder(d = 6.3, h = plug_h + flange_h + 2);
    // tubes: fill, level, drain, acid, vent
    for (p = [[9, -8], [0, -13], [12, -2], [-2, 13], [-13, -8]])
      translate([p[0], p[1], -plug_h - 1]) cylinder(d = tube_d, h = plug_h + flange_h + 2);
    // O-ring groove
    translate([0, 0, -plug_h + 3]) difference() { cylinder(d = neck_id + 1, h = 2.4); cylinder(d = neck_id - 3.6, h = 2.4); }
  }
  // tube guides below the cap so dip-tube depths are repeatable (tubes are glued into these)
  translate([0, -13, -plug_h - level_depth + plug_h]) difference() { cylinder(d = tube_d + 2.4, h = level_depth - plug_h); translate([0,0,-1]) cylinder(d = tube_d, h = level_depth); }
  translate([12, -2, -drain_depth]) difference() { cylinder(d = tube_d + 2.4, h = drain_depth - plug_h); translate([0,0,-1]) cylinder(d = tube_d, h = drain_depth); }
}

cap();

// Stir drive (separate print): a 40 mm 12 V fan with two 8x3 mm N52 magnets glued to the hub,
// mounted under the vial on the Cell A shelf. 25 mm PTFE stir bar in the vial.
