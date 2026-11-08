"""Generate wiring.svg (block wiring diagram).
Run: python make_drawings.py  -> writes wiring.svg   (panels.svg comes from panels.py)
"""
from __future__ import annotations

from pathlib import Path

OUT = Path(__file__).resolve().parent

INK, MUTE, TEAL, CORAL, AMBER, PAPER = "#15201f", "#8a9391", "#0f8b8d", "#e4572e", "#c98a1a", "#f6f4ee"
RED, BLK, YEL, BLU, GRN = "#d33", "#222", "#d8b400", "#2d6cdf", "#2a9d3f"
FONT = "font-family='Inter,system-ui,sans-serif'"


def box(x, y, w, h, title, lines=(), fill="#fffdf8", stroke=INK, title_fill=None):
    s = [f"<rect x='{x}' y='{y}' width='{w}' height='{h}' rx='8' fill='{fill}' stroke='{stroke}' stroke-width='1.5'/>"]
    s.append(f"<text x='{x+10}' y='{y+20}' {FONT} font-size='13' font-weight='600' fill='{title_fill or INK}'>{title}</text>")
    for i, ln in enumerate(lines):
        s.append(f"<text x='{x+10}' y='{y+38+i*15}' {FONT} font-size='11' fill='{INK}'>{ln}</text>")
    return "\n".join(s)


def wire(pts, color, label=None, dash=None, w=2):
    d = " ".join(f"{'M' if i == 0 else 'L'}{x},{y}" for i, (x, y) in enumerate(pts))
    extra = f" stroke-dasharray='{dash}'" if dash else ""
    s = f"<path d='{d}' fill='none' stroke='{color}' stroke-width='{w}'{extra}/>"
    if label:
        mx, my = pts[len(pts)//2]
        s += f"<text x='{mx+4}' y='{my-4}' {FONT} font-size='10' fill='{color}'>{label}</text>"
    return s


def wiring() -> str:
    W, H = 1400, 760
    p = [f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {W} {H}' width='{W}' height='{H}'>",
         f"<rect width='{W}' height='{H}' fill='{PAPER}'/>",
         f"<text x='30' y='36' {FONT} font-size='22' font-weight='600' fill='{INK}'>OpenReef analyzer — wiring diagram</text>",
         f"<text x='30' y='56' {FONT} font-size='12' fill='{MUTE}'>Raspberry Pi 4 (BCM numbering) · 12 V 5 A brick · common ground · I²C bus 1 (3.3 V) · all 12 V loads low-side switched</text>"]

    # Power
    p.append(box(30, 90, 190, 110, "12 V 5 A PSU", ["+12 V → rail (red)", "GND → rail (black)", "Barrel jack + 5 A fuse"], title_fill=CORAL))
    p.append(box(30, 230, 190, 95, "5 V 3 A buck", ["IN: 12 V rail", "OUT: 5 V → Pi 5V (pin 2)", "GND common"]))
    # Pi
    p.append(box(300, 90, 300, 400, "Raspberry Pi 4 (BCM)", [
        "GPIO2 SDA · GPIO3 SCL  → I²C bus",
        "GPIO4  → DS18B20 data (4.7 kΩ to 3V3)",
        "GPIO17 → stepper EN (all TMC2209)",
        "GPIO27/22  SP1 STEP/DIR (acid)",
        "GPIO23/24  SP2 STEP/DIR (NP R1)",
        "GPIO25/5   SP3 STEP/DIR (NP R2)",
        "GPIO6/12   SP4 STEP/DIR (NP R3a)",
        "GPIO13/16  SP5 STEP/DIR (NP R3b)",
        "GPIO18 → heater MOSFET PWM (optional)",
        "GPIO19 → LED white · GPIO21 → LED 850 nm",
        "GPIO20 → alarm relay IN",
        "GPIO26 ← leak sensor (pull-up, low = wet)",
        "5V pin 2 ← buck · 3V3 pin 1 → sensors",
        "GND pins 6/9/14/20/25/30/34/39",
    ], title_fill=TEAL))
    # I2C devices
    p.append(box(700, 90, 230, 90, "EZO-pH on isolated carrier", ["I²C 0x63 · 3V3 · GND", "BNC → lab-grade pH probe (Cell A)"]))
    p.append(box(700, 200, 230, 90, "AS7341 spectral sensor", ["I²C 0x39 · 3V3 · GND", "Mounted in Cell B holder"]))
    p.append(box(700, 310, 230, 180, "MCP23017 I/O expander", ["I²C 0x20 · 3V3 · GND", "Port A (inputs, pull-ups):",
                                                               " A0–A4 limit switches SP1–SP5", " A5 waste float switch", " A6/A7 spare",
                                                               "Port B (outputs) → MOSFET board IN1–8"]))
    # MOSFET board
    p.append(box(1030, 310, 330, 200, "8-ch low-side MOSFET board (12 V)", [
        "IN1 FILL_A   → P1 peristaltic", "IN2 LEVEL_A  → P2 peristaltic", "IN3 DRAIN_A  → P3 peristaltic",
        "IN4 FILL_B   → P4 peristaltic", "IN5 LEVEL_B  → P5 peristaltic", "IN6 DRAIN_B  → P6 peristaltic",
        "IN7 STIR_A   → 40 mm fan + magnets", "IN8 STIR_B   → 40 mm fan + magnets",
        "V+ 12 V rail · GND common · flyback diodes"]))
    # Steppers
    p.append(box(300, 540, 640, 150, "Stepper carrier board — 5× TMC2209 StepStick", [
        "VMOT 12 V (100 µF per driver) · VIO 3V3 · GND · EN common (GPIO17) · MS1/MS2 high = 1/16 µstep",
        "STEP/DIR from Pi GPIO as listed · VREF 0.6 V (≈0.85 A RMS) for NEMA17 17HS4023",
        "SP1 → acid syringe pump (Cell A)      SP2–SP5 → Trident NP reagent syringe pumps (Cell B)",
        "Each pump: NEMA17 4-wire · micro switch at home (to MCP23017 A0–A4, COM→GND, NO→pin)"]))
    # Misc
    p.append(box(1030, 90, 330, 90, "Alarm relay (5 V module)", ["IN ← GPIO20 · VCC 5 V · GND", "COM/NO dry contact → Hydros Sense port (float-switch input)"], title_fill=AMBER))
    p.append(box(1030, 200, 330, 90, "Leak + waste sensors", ["Leak: resistive pad in drip tray → GPIO26 (pull-up)", "Waste: float switch in 2 L bottle → MCP23017 A5"]))
    p.append(box(30, 360, 190, 110, "LEDs (Cell B)", ["White: 5V→68 Ω→LED→2N7002", "  gate GPIO19", "850 nm IR: 5V→47 Ω→LED→2N7002", "  gate GPIO21"]))
    p.append(box(30, 500, 190, 95, "DS18B20 (Cell A)", ["Red 3V3 · Black GND", "Yellow → GPIO4, 4.7 kΩ to 3V3", "dtoverlay=w1-gpio,gpiopin=4"]))
    p.append(box(30, 625, 190, 95, "Fluidics note", ["6 peristaltic + 2 stir fans", "on MOSFET board (right)", "5 syringe pumps on carrier"], stroke=MUTE, title_fill=MUTE))
    p.append(box(1030, 560, 330, 150, "Optional heater (Cell B, 35 °C)", ["12 V 10 W silicone pad around holder", "IRLZ44N low-side, gate ← GPIO18 PWM", "10 kΩ NTC → ADS1115 (0x48) or use DS18B20 #2", "Needed only for slow nitrate chemistries"], stroke=MUTE, title_fill=MUTE))

    # wires
    p.append(wire([(220, 110), (260, 110), (260, 560), (300, 560)], RED, "12 V"))
    p.append(wire([(260, 520), (1100, 520), (1100, 510)], RED, dash="4 4"))
    p.append(f"<text x='700' y='533' {FONT} font-size='10' fill='{RED}'>12 V rail → MOSFET board V+</text>")
    p.append(wire([(220, 280), (280, 280), (280, 460), (300, 460)], RED, "5 V", w=1.5))
    p.append(wire([(600, 130), (700, 130)], BLU, "I²C"))
    p.append(wire([(650, 130), (650, 240), (700, 240)], BLU))
    p.append(wire([(650, 240), (650, 350), (700, 350)], BLU))
    p.append(wire([(930, 450), (1030, 450)], GRN)); p.append(f"<text x='950' y='443' {FONT} font-size='10' fill='{GRN}'>8× logic</text>")
    p.append(wire([(450, 490), (450, 540)], YEL, "STEP/DIR/EN ×11"))
    p.append(wire([(560, 90), (560, 70), (1200, 70), (1200, 90)], AMBER, "GPIO20"))
    p.append(wire([(300, 540), (280, 540), (280, 480), (300, 480)], BLK, w=0.01))
    p.append(wire([(300, 410), (220, 410)], BLK, "GPIO19/21"))
    p.append(wire([(300, 475), (270, 475), (270, 540), (220, 540)], BLK, "GPIO4"))
    p.append(wire([(940, 660), (1030, 660)], MUTE, dash="3 3")); p.append(f"<text x='945' y='675' {FONT} font-size='10' fill='{MUTE}'>GPIO18 via carrier</text>")
    p.append(f"<text x='30' y='{H-30}' {FONT} font-size='11' fill='{MUTE}'>Ground: star point at the PSU terminal. Keep the EZO carrier's isolated ground separate from the 12 V motor return; route pH BNC away from stepper cables. Leak sensor pad sits lowest in the wet bay.</text>")
    p.append("</svg>")
    return "\n".join(p)


def panels() -> str:
    """Laser-cut layout: 3 mm cast acrylic (sides/front/top/bulkhead), 6 mm (base/back). Dimensions in mm, 1 unit = 1 mm."""
    W, H = 1300, 1080
    s = [f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {W} {H}' width='{W}mm' height='{H}mm'>",
         f"<rect width='{W}' height='{H}' fill='white'/>",
         f"<text x='20' y='28' {FONT} font-size='18' fill='{INK}'>OpenReef enclosure — panel layout (mm). Red = cut, blue = engrave. Butt joints with printed corner brackets, M3 + heat-set inserts.</text>"]

    def panel(x, y, w, h, name, holes=(), cutouts=()):
        s.append(f"<rect x='{x}' y='{y}' width='{w}' height='{h}' fill='none' stroke='{RED}' stroke-width='0.5'/>")
        s.append(f"<text x='{x+6}' y='{y+16}' {FONT} font-size='11' fill='{BLU}'>{name} — {w}×{h}</text>")
        for hx, hy, d in holes:
            s.append(f"<circle cx='{x+hx}' cy='{y+hy}' r='{d/2}' fill='none' stroke='{RED}' stroke-width='0.5'/>")
        for cx, cy, cw, ch, lab in cutouts:
            s.append(f"<rect x='{x+cx}' y='{y+cy}' width='{cw}' height='{ch}' fill='none' stroke='{RED}' stroke-width='0.5'/>")
            s.append(f"<text x='{x+cx+3}' y='{y+cy+12}' {FONT} font-size='9' fill='{BLU}'>{lab}</text>")

    # Overall box: 420 W x 460 H x 200 D. Wet bay left 260 mm, dry bay right 160 mm.
    base_holes = [(x, y, 3.2) for x in (15, 210, 405) for y in (15, 185)]
    panel(20, 50, 420, 200, "BASE 6 mm (drip tray sits on it)", base_holes,
          [(30, 40, 200, 120, "drip tray recess (engrave)"), (300, 30, 100, 140, "electronics standoffs ×4 (engrave)")])
    panel(460, 50, 420, 460, "BACK 6 mm", [(x, y, 3.2) for x in (15, 405) for y in (15, 230, 445)],
          [(300, 400, 60, 30, "12 V jack + fuse"), (330, 30, 70, 40, "fan 60 mm (dry bay)"), (20, 420, 40, 40, "sample in/out, waste"), (120, 420, 120, 40, "reagent lines grommets ×5")])
    # bulkhead between wet and dry bays
    panel(900, 50, 200, 460, "BULKHEAD 3 mm (wet | dry)", [(x, y, 3.2) for x in (12, 188) for y in (20, 440)],
          [(60, 60, 80, 20, "grommet: pH BNC + DS18B20"), (60, 150, 80, 20, "grommet: pump/stepper looms"), (60, 300, 80, 20, "grommet: LED/AS7341")])
    # left side, right side
    panel(20, 280, 200, 460, "SIDE L 3 mm", [(x, y, 3.2) for x in (12, 188) for y in (20, 440)])
    panel(240, 280, 200, 460, "SIDE R 3 mm", [(x, y, 3.2) for x in (12, 188) for y in (20, 440)], [(40, 60, 120, 60, "vent slots (dry bay)")])
    # top
    panel(460, 540, 420, 200, "TOP 3 mm", [(x, y, 3.2) for x in (15, 405) for y in (15, 185)], [(290, 70, 100, 60, "vent slots")])
    # front door (clear) — covers wet bay; dry bay front is a fixed panel with status LED
    panel(900, 540, 260, 300, "FRONT DOOR clear 3 mm", [(10, 40, 3.2), (10, 260, 3.2), (250, 150, 6.5)])
    panel(1170, 540, 110, 300, "FRONT DRY 3 mm", [(12, 20, 3.2), (98, 20, 3.2), (12, 280, 3.2), (98, 280, 3.2), (55, 60, 8.2)],
          [(15, 200, 80, 25, "Pi USB/Eth access")])
    # shelves
    panel(20, 760, 260, 190, "SHELF pumps 3 mm (5 × 60 mm pitch)", [(x, y, 4.4) for x in range(30, 260, 50) for y in (40, 150)], [(10, 60, 240, 70, "syringe pump bases, M4 slots")])
    panel(300, 760, 260, 190, "SHELF cells 3 mm", [(70, 95, 26), (200, 95, 26)], [(25, 50, 90, 90, "Cell A 40 mm vial + fan"), (155, 50, 90, 90, "Cell B holder + fan")])
    panel(580, 760, 300, 190, "SHELF bottle tray 6 mm", [(x, y, 3.2) for x in (15, 285) for y in (15, 175)], [(15, 40, 230, 120, "5 × Ø60 reagent + Ø80 acid, 10 mm lip")])
    panel(900, 860, 380, 90, "CORNER BRACKETS: 12 × printed (3D), not cut", [], [(10, 30, 360, 40, "see cad/corner_bracket.scad — M3 heat-set inserts both faces")])
    s.append(f"<text x='20' y='{H-20}' {FONT} font-size='11' fill='{MUTE}'>Stack order (front view): dry bay right; wet bay left with cells shelf at 330 mm, syringe bank at 200 mm, bottle tray at 20 mm above base; peristaltic pumps on the bulkhead's wet face. Waste bottle sits outside, below.</text>")
    s.append("</svg>")
    return "\n".join(s)


if __name__ == "__main__":
    (OUT / "wiring.svg").write_text(wiring())
    print("wrote", OUT / "wiring.svg")
