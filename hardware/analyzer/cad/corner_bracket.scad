// OpenReef enclosure corner bracket: joins two acrylic panels at 90 degrees.
// M3 heat-set inserts (4.0 mm hole) in both faces. Print 12 (plus 4 for shelves). PETG.
$fn = 40;
len = 30; t = 6; w = 18;
difference() {
  union() { cube([len, w, t]); cube([len, t, w]); }
  for (x = [8, len - 8]) {
    translate([x, w - 6, -1]) cylinder(d = 4.0, h = t + 2);     // insert, base face
    translate([x, -1, w - 6]) rotate([-90, 0, 0]) cylinder(d = 4.0, h = t + 2);  // insert, wall face
  }
}
