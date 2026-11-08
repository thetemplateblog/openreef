"""OpenReef enclosure — finger-jointed (tab-and-slot) laser-cut panels.

Generates `panels.svg` (1 user unit = 1 mm; red = cut, blue = engrave) with:
  * finger joints on every box edge, tab depth = mating panel thickness,
  * through-slots for the bulkhead and the three wet-bay shelves,
  * kerf compensation and a small press-fit interference so panels click together,
  * optional T-slot pockets (M3 bolt + captive nut) on the long joints for a permanent hold.

Run:  python panels.py [--kerf 0.18] [--fit 0.10] [--no-tslot] [--out panels.svg]

Box: 420 W x 460 H x 200 D mm outside. Sides are 3 mm and receive tabs from base (6), back (6),
top (3) and the dry-bay front (3). The bulkhead (3) and shelves (3) tab through slots.
Acrylic note: a pure interference snap cracks cast acrylic over months; keep --fit <= 0.10 and use
the T-slots (or a bead of Weld-On 4) for the permanent joint.
"""
from __future__ import annotations

import argparse
import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from shapely.geometry import Polygon, box
from shapely.ops import unary_union

# ----------------------------------------------------------------------------- parameters
W, H, D = 420.0, 460.0, 200.0        # outside dimensions (x, z, y)
T3, T6 = 3.0, 6.0                    # sheet thicknesses
BULK_X = 260.0                       # bulkhead centre from the outer left face
SHELF_Z = [20.0, 200.0, 330.0]       # shelf top surfaces above the inside of the base (wet bay)
SHELF_DEPTH = 190.0                  # shelves stop 4 mm short of the door
FINGER = 18.0                        # target finger width
TSLOT_BOLT, TSLOT_NUT_W, TSLOT_NUT_T, TSLOT_LEN = 3.4, 5.6, 2.6, 12.0   # M3 nut 5.5 x 2.4

INK, RED, BLU, MUTE = "#15201f", "#d33", "#2d6cdf", "#8a9391"


def fingers(length: float, inset0: float, inset1: float, target: float = FINGER) -> List[Tuple[float, float]]:
    """Return (start, end) of the tab/notch segments along an edge, laid out on
    [inset0, length - inset1] as an odd number of equal segments; tabs sit on the ODD
    segments so every edge starts and ends with material on the female panel and a gap on
    the male one. That keeps the female panel's corners attached and lets the third panel
    at each corner fill the cube. The same call on both mating panels guarantees a match."""
    L = length - inset0 - inset1
    n = max(3, int(round(L / target)))
    if n % 2 == 0:
        n += 1
    w = L / n
    return [(inset0 + i * w, inset0 + (i + 1) * w) for i in range(1, n, 2)]


@dataclass
class Panel:
    name: str
    w: float                     # flat width  (x on the sheet)
    h: float                     # flat height (y on the sheet)
    t: float
    shape: Optional[Polygon] = None
    holes: List[Polygon] = field(default_factory=list)      # through-slots, T-slot pockets, bolt holes
    engrave: List[Tuple[float, float, float, float, str]] = field(default_factory=list)
    labels: List[Tuple[float, float, str]] = field(default_factory=list)

    def core(self, male: Dict[str, float]) -> None:
        """Start from the outer rectangle shrunk by the mating thickness on male edges."""
        x0 = male.get("left", 0.0); x1 = self.w - male.get("right", 0.0)
        y0 = male.get("bottom", 0.0); y1 = self.h - male.get("top", 0.0)
        self.shape = box(x0, y0, x1, y1)

    # edge helpers: edges are 'bottom' (y=0), 'top' (y=h), 'left' (x=0), 'right' (x=w)
    def tabs(self, edge: str, segs: List[Tuple[float, float]], depth: float, fit: float) -> None:
        """Male: add tabs protruding `depth` beyond the core, widened by `fit` for a press fit."""
        rects = []
        for a, b in segs:
            a -= fit / 2; b += fit / 2
            if edge == "bottom":
                rects.append(box(a, 0, b, depth + 0.01))
            elif edge == "top":
                rects.append(box(a, self.h - depth - 0.01, b, self.h))
            elif edge == "left":
                rects.append(box(0, a, depth + 0.01, b))
            else:
                rects.append(box(self.w - depth - 0.01, a, self.w, b))
        self.shape = unary_union([self.shape] + rects)

    def notches(self, edge: str, segs: List[Tuple[float, float]], depth: float, fit: float) -> None:
        """Female: cut notches `depth` deep into the edge, narrowed by `fit`."""
        for a, b in segs:
            a += fit / 2; b -= fit / 2
            if edge == "bottom":
                r = box(a, -1, b, depth)
            elif edge == "top":
                r = box(a, self.h - depth, b, self.h + 1)
            elif edge == "left":
                r = box(-1, a, depth, b)
            else:
                r = box(self.w - depth, a, self.w + 1, b)
            self.shape = self.shape.difference(r)

    def slots(self, along: str, pos: float, segs: List[Tuple[float, float]], t_mate: float, fit: float) -> None:
        """Through-slots for an internal panel: a row at `pos` (y for a horizontal row,
        x for a vertical row), each slot t_mate thick (narrowed by fit)."""
        for a, b in segs:
            a += fit / 2; b -= fit / 2
            if along == "x":
                self.holes.append(box(a, pos - t_mate / 2 + fit / 2, b, pos + t_mate / 2 - fit / 2))
            else:
                self.holes.append(box(pos - t_mate / 2 + fit / 2, a, pos + t_mate / 2 - fit / 2, b))

    def tslots(self, edge: str, segs: List[Tuple[float, float]], depth: float) -> None:
        """T-slot pocket in the middle of every *odd* gap of a male edge (between tabs):
        a bolt channel from the edge plus a nut pocket; the mating female panel gets a bolt hole."""
        gaps = [(segs[i][1], segs[i + 1][0]) for i in range(len(segs) - 1)]
        for a, b in gaps:
            c = (a + b) / 2
            bolt_len = TSLOT_LEN + depth
            if edge in ("bottom", "top"):
                y0 = 0 if edge == "bottom" else self.h
                s = 1 if edge == "bottom" else -1
                chan = box(c - TSLOT_BOLT / 2, min(y0, y0 + s * bolt_len), c + TSLOT_BOLT / 2, max(y0, y0 + s * bolt_len))
                nut = box(c - TSLOT_NUT_W / 2, min(y0 + s * (depth + 5), y0 + s * (depth + 5 + TSLOT_NUT_T)),
                          c + TSLOT_NUT_W / 2, max(y0 + s * (depth + 5), y0 + s * (depth + 5 + TSLOT_NUT_T)))
            else:
                x0 = 0 if edge == "left" else self.w
                s = 1 if edge == "left" else -1
                chan = box(min(x0, x0 + s * bolt_len), c - TSLOT_BOLT / 2, max(x0, x0 + s * bolt_len), c + TSLOT_BOLT / 2)
                nut = box(min(x0 + s * (depth + 5), x0 + s * (depth + 5 + TSLOT_NUT_T)), c - TSLOT_NUT_W / 2,
                          max(x0 + s * (depth + 5), x0 + s * (depth + 5 + TSLOT_NUT_T)), c + TSLOT_NUT_W / 2)
            self.shape = self.shape.difference(unary_union([chan, nut]))

    def bolt_holes(self, along: str, pos: float, segs: List[Tuple[float, float]]) -> None:
        """Clearance holes in a female panel matching a male edge's T-slot bolts."""
        gaps = [(segs[i][1], segs[i + 1][0]) for i in range(len(segs) - 1)]
        for a, b in gaps:
            c = (a + b) / 2
            if along == "x":
                self.holes.append(circle(c, pos, TSLOT_BOLT / 2))
            else:
                self.holes.append(circle(pos, c, TSLOT_BOLT / 2))


def circle(cx: float, cy: float, r: float) -> Polygon:
    return Polygon([(cx + r * math.cos(a), cy + r * math.sin(a)) for a in [i * 2 * math.pi / 36 for i in range(36)]])


def build(kerf: float, fit: float, tslot: bool) -> List[Panel]:
    # Press-fit: tabs grow and slots shrink by `fit` *after* the laser removes `kerf`.
    # A laser cut removes kerf/2 from each side of a line, so outlines (tabs) lose kerf and
    # holes (slots) gain kerf. Compensate so the as-cut interference equals `fit`.
    f_out = fit + kerf          # applied to tabs (widen)
    f_in = fit - kerf           # applied to notches/slots (narrow; may be negative = widen less)

    P: Dict[str, Panel] = {}

    # ---- shared finger patterns (same call on both mating panels) ----
    # side <-> base/top along D (front edge plain, back edge has the back panel): inset back by T6
    side_base = fingers(D, T6, 0)
    side_top = fingers(D, T6, 0)
    side_back = fingers(H, T6, T3)            # along H; base at bottom (T6), top at top (T3)
    side_front_dry = fingers(H, T6, T3)
    back_base = fingers(W, T3, T3)            # along W between the two sides
    back_top = fingers(W, T3, T3)
    front_base = fingers(W - BULK_X - T3 / 2, T3 / 2, T3)   # dry front along its own width
    front_top = fingers(W - BULK_X - T3 / 2, T3 / 2, T3)
    bulk_base = fingers(D - T6, 0, 4)         # bulkhead along depth (inside back to 4 mm from door)
    bulk_back = fingers(H - T6 - T3, 0, 0)    # bulkhead along height between base and top
    bulk_top = fingers(D - T6, 0, 4)
    shelf_side = fingers(SHELF_DEPTH, 0, 0)   # shelf along depth into side / bulkhead
    shelf_width = BULK_X - T3 / 2 - T3        # inside left side to bulkhead face
    shelf_back = fingers(shelf_width, 0, 0)

    # ---- SIDE L (x = depth 0..D, back at x=0 side? we draw front at x=D) ----
    # Flat coords: x = depth from the back face (0) to the front (D); y = height from bottom (0).
    for name, dry in (("SIDE_L", False), ("SIDE_R", True)):
        p = Panel(name, D, H, T3)
        p.core({})                                           # female on every edge
        p.notches("bottom", side_base, T6, f_in)             # base tabs
        p.notches("top", side_top, T3, f_in)                 # top tabs
        p.notches("left", side_back, T6, f_in)               # back tabs
        if dry:
            p.notches("right", side_front_dry, T3, f_in)     # dry-bay front tabs
        # shelf and (for the right side) nothing; for the left side, shelf through-slots:
        if not dry:
            for z in SHELF_Z:
                p.slots("x", T6 + z + T3 / 2, [(T6 + a, T6 + b) for a, b in shelf_side], T3, f_in)
                p.engrave.append((T6, T6 + z - 1, SHELF_DEPTH, 2, f"shelf z={z:g}"))
        if tslot:
            p.bolt_holes("x", T6 / 2, side_base); p.bolt_holes("x", H - T3 / 2, side_top)
            p.bolt_holes("y", T6 / 2, side_back)
        if dry:
            p.engrave.append((60, 60, 100, 60, "vent slots"))
        p.labels.append((D / 2, H / 2, name + (" (hinge, door)" if not dry else "")))
        P[name] = p

    # ---- BASE (x = width, y = depth; back at y=0) ----
    p = Panel("BASE", W, D, T6)
    p.core({"left": T3, "right": T3})                        # male into the sides
    p.tabs("left", side_base, T3, f_out); p.tabs("right", side_base, T3, f_out)
    p.notches("bottom", back_base, T6, f_in)                 # female to the back panel
    for a, b in bulk_base:                                   # bulkhead through-slots
        p.holes.append(box(BULK_X - T3 / 2 + f_in / 2, T6 + a + f_in / 2, BULK_X + T3 / 2 - f_in / 2, T6 + b - f_in / 2))
    # dry-bay front tabs land in the base
    for a, b in front_base:
        p.holes.append(box(BULK_X + T3 / 2 + a + f_in / 2, D - T3 + f_in / 2, BULK_X + T3 / 2 + b - f_in / 2, D - f_in / 2))
    if tslot:
        p.tslots("left", side_base, T3); p.tslots("right", side_base, T3)
    p.engrave.append((T3 + 6, T6 + 6, BULK_X - T3 - 12, D - T6 - 10, "drip tray (wet bay)"))
    p.engrave.append((BULK_X + 30, 30, 110, 140, "Pi + carrier standoffs"))
    p.labels.append((W / 2, D / 2, "BASE 6 mm")); P["BASE"] = p

    # ---- BACK (x = width, y = height) ----
    p = Panel("BACK", W, H, T6)
    p.core({"left": T3, "right": T3, "bottom": T6, "top": T3})   # male everywhere
    p.tabs("left", side_back, T3, f_out); p.tabs("right", side_back, T3, f_out)
    p.tabs("bottom", back_base, T6, f_out); p.tabs("top", back_top, T3, f_out)
    for a, b in bulk_back:                                   # bulkhead through-slots
        p.holes.append(box(BULK_X - T3 / 2 + f_in / 2, T6 + a + f_in / 2, BULK_X + T3 / 2 - f_in / 2, T6 + b - f_in / 2))
    for z in SHELF_Z:                                        # shelf through-slots
        for a, b in shelf_back:
            p.holes.append(box(T3 + a + f_in / 2, T6 + z + f_in / 2, T3 + b - f_in / 2, T6 + z + T3 - f_in / 2))
    if tslot:
        p.tslots("left", side_back, T3); p.tslots("right", side_back, T3)
    p.holes.append(box(BULK_X + 50, 30, BULK_X + 110, 60)); p.labels.append((BULK_X + 80, 45, "12 V jack + fuse"))
    p.holes.append(circle(BULK_X + 80, 400, 29)); p.labels.append((BULK_X + 80, 440, "60 mm fan"))
    for i in range(5):
        p.holes.append(circle(40 + i * 40, 40, 5)); p.labels.append((40 + i * 40, 60, "Ø10 grommet"))
    p.holes.append(circle(40, 100, 8)); p.labels.append((40, 120, "sample in / waste Ø16"))
    p.labels.append((W / 2, H / 2, "BACK 6 mm")); P["BACK"] = p

    # ---- TOP (x = width, y = depth; back at y=0) ----
    p = Panel("TOP", W, D, T3)
    p.core({"left": T3, "right": T3})
    p.tabs("left", side_top, T3, f_out); p.tabs("right", side_top, T3, f_out)
    p.notches("bottom", back_top, T6, f_in)
    for a, b in bulk_top:
        p.holes.append(box(BULK_X - T3 / 2 + f_in / 2, T6 + a + f_in / 2, BULK_X + T3 / 2 - f_in / 2, T6 + b - f_in / 2))
    for a, b in front_top:
        p.holes.append(box(BULK_X + T3 / 2 + a + f_in / 2, D - T3 + f_in / 2, BULK_X + T3 / 2 + b - f_in / 2, D - f_in / 2))
    if tslot:
        p.tslots("left", side_top, T3); p.tslots("right", side_top, T3)
    p.engrave.append((BULK_X + 40, 60, 100, 70, "vent slots"))
    p.labels.append((W / 2, D / 2, "TOP 3 mm")); P["TOP"] = p

    # ---- BULKHEAD (x = depth, y = height), internal ----
    bw, bh = D - T6, H - T6 - T3
    p = Panel("BULKHEAD", bw, bh, T3)
    p.core({"left": T6, "bottom": T6, "top": T3})
    p.tabs("left", bulk_back, T6, f_out); p.tabs("bottom", bulk_base, T6, f_out); p.tabs("top", bulk_top, T3, f_out)
    for z in SHELF_Z:                                        # shelves land on the wet face
        p.slots("x", z + T3 / 2, shelf_side, T3, f_in)
    for y, lab in ((60, "pH BNC + DS18B20"), (150, "pump / stepper looms"), (300, "LED / AS7341")):
        p.holes.append(box(bw / 2 - 40, y, bw / 2 + 40, y + 20)); p.labels.append((bw / 2, y + 32, "grommet: " + lab))
    p.labels.append((bw / 2, bh / 2, "BULKHEAD 3 mm (wet | dry)")); P["BULKHEAD"] = p

    # ---- SHELVES (x = width, y = depth; back at y=0), 3 identical blanks + features ----
    for i, z in enumerate(SHELF_Z):
        p = Panel(f"SHELF_{i+1}", shelf_width, SHELF_DEPTH, T3)
        p.core({"left": T3, "right": T3, "bottom": T6})
        p.tabs("left", shelf_side, T3, f_out); p.tabs("right", shelf_side, T3, f_out); p.tabs("bottom", shelf_back, T6, f_out)
        if i == 0:
            # bottle collars: 4 x Trident NP bottles (~55 mm) in two rows + the 500 mL acid bottle (~78 mm)
            for cx, cy, r in ((45, 52, 29), (125, 52, 29), (205, 52, 29), (178, 135, 29), (70, 135, 41)):
                p.holes.append(circle(cx, cy, r)); p.labels.append((cx, cy + 4, f"Ø{2*r}"))
            p.labels.append((shelf_width / 2, 14, "SHELF 1 bottle tray z=20 (bottles stand on the base)"))
        elif i == 1:
            for k in range(5):
                for yy in (40, 150):
                    p.holes.append(circle(30 + k * 50, yy, 2.2))
            p.labels.append((shelf_width / 2, SHELF_DEPTH / 2, "SHELF 2 syringe bank z=200 (M4 slots)"))
        else:
            p.holes.append(circle(70, SHELF_DEPTH / 2, 13)); p.holes.append(circle(190, SHELF_DEPTH / 2, 13))
            p.labels.append((shelf_width / 2, 20, "SHELF 3 cells z=330 (Ø26 stir drives)"))
        P[p.name] = p

    # ---- FRONT DRY (x = width of dry bay, y = height) ----
    fw = W - BULK_X - T3 / 2
    p = Panel("FRONT_DRY", fw, H, T3)
    p.core({"right": T3, "bottom": T6, "top": T3})
    p.tabs("right", side_front_dry, T3, f_out); p.tabs("bottom", front_base, T6, f_out); p.tabs("top", front_top, T3, f_out)
    p.holes.append(box(fw / 2 - 40, 200, fw / 2 + 40, 225)); p.labels.append((fw / 2, 240, "Pi USB / Ethernet"))
    p.holes.append(circle(fw / 2, 60, 4.1)); p.labels.append((fw / 2, 80, "status LED"))
    p.labels.append((fw / 2, H / 2, "FRONT DRY 3 mm")); P["FRONT_DRY"] = p

    # ---- DOOR (clear 3 mm, overlaps the wet bay opening, hinges on side L) ----
    p = Panel("DOOR", BULK_X - T3 / 2 - 1, H - T6 - T3 - 2, T3)
    p.core({})
    for y in (40, p.h - 40):
        p.holes.append(circle(8, y, 1.6)); p.holes.append(circle(8, y + 20, 1.6))
    p.holes.append(circle(p.w - 12, p.h / 2, 3.3)); p.labels.append((p.w - 12, p.h / 2 + 16, "Ø6.5 magnet"))
    p.labels.append((p.w / 2, p.h / 2, "DOOR clear 3 mm (not jointed)")); P["DOOR"] = p

    return list(P.values())


def poly_path(poly: Polygon, ox: float, oy: float) -> str:
    def ring(coords):
        pts = [f"{ox + x:.2f},{oy + y:.2f}" for x, y in coords]
        return "M" + " L".join(pts) + " Z"
    d = ring(poly.exterior.coords)
    for interior in poly.interiors:
        d += " " + ring(interior.coords)
    return d


def layout(panels: List[Panel], sheet_w: float = 1300.0, gap: float = 12.0) -> List[Tuple[Panel, float, float]]:
    """Simple shelf packing left-to-right, top-to-bottom."""
    x, y, row_h = gap, 40.0, 0.0
    out = []
    for p in sorted(panels, key=lambda q: -q.h):
        if x + p.w + gap > sheet_w:
            x = gap; y += row_h + gap + 14; row_h = 0
        out.append((p, x, y))
        x += p.w + gap; row_h = max(row_h, p.h)
    return out


def render(panels: List[Panel], kerf: float, fit: float, tslot: bool) -> str:
    placed = layout(panels)
    total_h = max(y + p.h for p, _, y in placed) + 60
    F = "font-family='Inter,system-ui,sans-serif'"
    s = [f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1300 {total_h:.0f}' width='1300mm' height='{total_h:.0f}mm'>",
         "<rect width='1300' height='100%' fill='white'/>",
         f"<text x='12' y='22' {F} font-size='14' fill='{INK}'>OpenReef enclosure — finger-jointed panels (mm). Red = cut, blue = engrave. "
         f"kerf {kerf} mm, press-fit {fit} mm, T-slots {'on' if tslot else 'off'}. 3 mm: sides, top, bulkhead, shelves, front, door · 6 mm: base, back.</text>"]
    for p, ox, oy in placed:
        s.append(f"<path d='{poly_path(p.shape, ox, oy)}' fill='none' stroke='{RED}' stroke-width='0.35'/>")
        for h in p.holes:
            s.append(f"<path d='{poly_path(h, ox, oy)}' fill='none' stroke='{RED}' stroke-width='0.35'/>")
        for ex, ey, ew, eh, lab in p.engrave:
            s.append(f"<rect x='{ox+ex:.1f}' y='{oy+ey:.1f}' width='{ew:.1f}' height='{eh:.1f}' fill='none' stroke='{BLU}' stroke-width='0.35'/>")
            s.append(f"<text x='{ox+ex+2:.1f}' y='{oy+ey+9:.1f}' {F} font-size='7' fill='{BLU}'>{lab}</text>")
        for lx, ly, lab in p.labels:
            s.append(f"<text x='{ox+lx:.1f}' y='{oy+ly:.1f}' {F} font-size='8' fill='{BLU}' text-anchor='middle'>{lab}</text>")
        s.append(f"<text x='{ox+4:.1f}' y='{oy-3:.1f}' {F} font-size='9' fill='{MUTE}'>{p.name} {p.w:.1f}×{p.h:.1f} t{p.t:g}</text>")
    s.append("</svg>")
    return "\n".join(s)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--kerf", type=float, default=0.18, help="laser kerf for your machine on 3 mm cast acrylic")
    ap.add_argument("--fit", type=float, default=0.10, help="press-fit interference after kerf (0 = slip fit)")
    ap.add_argument("--no-tslot", action="store_true")
    ap.add_argument("--out", default="panels.svg")
    a = ap.parse_args()
    panels = build(a.kerf, a.fit, not a.no_tslot)
    open(a.out, "w").write(render(panels, a.kerf, a.fit, not a.no_tslot))
    print(f"wrote {a.out}: {len(panels)} panels")


if __name__ == "__main__":
    main()
