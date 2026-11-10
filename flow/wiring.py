# -*- coding: utf-8 -*-
"""Pin-level wiring for the piston bench test, Pico 2 to TMC2209 to motor.

    python wiring.py      ->  wiring.png

Pico pin numbers are physical header positions, which are the same on a Pico 2
as on a Pico 1. Driver pin numbers are from table 5.2 of the BIGTREETECH
TMC2209 manual. Every driver pin is silkscreened, so go by the printed label
and not by which end of the row you think is pin 1. The two rows are drawn
here on whichever side keeps the wires untangled, not in board orientation.
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch

HERE = os.path.dirname(os.path.abspath(__file__))

INK, GREY, PALE = "#1b1b1b", "#7a7a7a", "#eceff2"
SIG, PWR, GND, IO = "#2f6fb0", "#c0392b", "#2b2b2b", "#d98324"
CA, CB = "#1f8a70", "#8e44ad"

PICO = ["GP0", "GP1", "GND", "GP2", "GP3", "GP4", "GP5", "GND", "GP6", "GP7",
        "GP8", "GP9", "GND", "GP10", "GP11", "GP12", "GP13", "GND", "GP14",
        "GP15", "GP16", "GP17", "GND", "GP18", "GP19", "GP20", "GP21", "GND",
        "GP22", "RUN", "GP26", "GP27", "AGND", "GP28", "ADC_VREF", "3V3(OUT)",
        "3V3_EN", "GND", "VSYS", "VBUS"]
J1 = ["EN", "MS1", "MS2", "PDN/UART", "PDN", "CLK", "STEP", "DIR"]
J2 = ["VM", "GND", "A2", "A1", "B1", "B2", "VCC_IO", "GND"]
USED_PICO = {3: GND, 4: SIG, 5: SIG, 6: SIG, 36: IO}
USED_J1 = {1: SIG, 7: SIG, 8: SIG}
USED_J2 = {1: PWR, 2: GND, 3: CA, 4: CA, 5: CB, 6: CB, 7: IO, 8: GND}

fig, ax = plt.subplots(figsize=(15.0, 9.4), dpi=160)
fig.patch.set_facecolor("white")

# ------------------------------------------------------------------ Pico
PX, PY, PW, PH = 11.2, 0.9, 3.1, 7.4
ax.add_patch(FancyBboxPatch((PX, PY), PW, PH, boxstyle="round,pad=0.06",
                            facecolor=PALE, edgecolor=INK, lw=1.3, zorder=2))
ax.add_patch(Rectangle((PX + PW / 2 - 0.42, PY + PH - 0.30), 0.84, 0.40,
                       facecolor="#b9c0c7", edgecolor=INK, lw=0.9, zorder=3))
ax.text(PX + PW / 2, PY + PH + 0.24, "USB", ha="center", fontsize=8, color=GREY)
ax.text(PX + PW / 2, PY + PH - 0.72, "Raspberry Pi Pico 2\nRP2350   COM15",
        ha="center", va="top", fontsize=9.5, color=INK, fontweight="semibold",
        linespacing=1.5)

pico = {}
ptop = PY + PH - 1.45
for i in range(1, 41):
    left = i <= 20
    y = ptop - ((i - 1) if left else (40 - i)) * 0.295
    x = PX + 0.30 if left else PX + PW - 0.30
    c = USED_PICO.get(i)
    ax.add_patch(Circle((x, y), 0.072, facecolor=c or "white",
                        edgecolor=c or GREY, lw=1.0, zorder=4))
    ax.text(x + (0.16 if left else -0.16), y,
            ("%d  %s" % (i, PICO[i - 1])) if left else ("%s  %d" % (PICO[i - 1], i)),
            ha="left" if left else "right", va="center", fontsize=6.6,
            color=c or GREY, zorder=5, fontweight="bold" if c else "normal")
    pico[i] = (x, y)

# --------------------------------------------------------------- TMC2209
DX, DY, DW, DH = 6.3, 3.0, 2.5, 4.2
ax.add_patch(FancyBboxPatch((DX, DY), DW, DH, boxstyle="round,pad=0.06",
                            facecolor=PALE, edgecolor=INK, lw=1.3, zorder=2))
ax.text(DX + DW / 2, DY + DH + 0.50, "BIGTREETECH TMC2209", ha="center",
        fontsize=9.5, color=INK, fontweight="semibold")
ax.text(DX + DW / 2, DY + DH + 0.25, "15.2 x 20.3 mm", ha="center",
        fontsize=7.4, color=GREY)
ax.add_patch(Rectangle((DX + 0.62, DY + 1.25), DW - 1.24, 1.5,
                       facecolor="#cfd4d9", edgecolor=GREY, lw=0.8, zorder=3))
ax.text(DX + DW / 2, DY + 2.0, "TMC2209", ha="center", va="center",
        fontsize=7.2, color="#4a4a4a", zorder=4)

j1, j2 = {}, {}
jtop = DY + DH - 0.45
for i in range(1, 9):
    y = jtop - (i - 1) * 0.44
    for side, names, store, used in ((1, J1, j1, USED_J1), (0, J2, j2, USED_J2)):
        x = DX + 0.22 + side * (DW - 0.44)
        c = used.get(i)
        ax.add_patch(Rectangle((x - 0.065, y - 0.065), 0.13, 0.13,
                               facecolor=c or "white", edgecolor=c or GREY,
                               lw=1.0, zorder=4))
        # labels sit just above the pin so the incoming wire passes under them
        ax.text(x + (0.13 if side else -0.13), y + 0.10,
                ("%d %s" % (i, names[i - 1])) if side
                else ("%s %d" % (names[i - 1], i)),
                ha="left" if side else "right", va="bottom", fontsize=6.8,
                color=c or GREY, zorder=5, fontweight="bold" if c else "normal")
        store[i] = (x, y)
ax.text(DX + DW + 0.15, jtop + 0.56, "J1", fontsize=8, color=GREY)
ax.text(DX - 0.15, jtop + 0.56, "J2", fontsize=8, color=GREY, ha="right")

vref = (DX + DW / 2, DY + DH - 0.08)
ax.add_patch(Circle(vref, 0.075, facecolor="white", edgecolor=PWR, lw=1.2,
                    zorder=5))
# A window, not a point. The pot moves 0.1 to 0.2 V per nudge, so asking for
# 0.53 V exactly is asking for an afternoon. Anything from 0.50 to 0.64 V
# works: below is the datasheet floor, above is where the phase can no longer
# reverse inside the beat. Set on 2026-11-10 to 0.556 V = 0.393 A.
ax.annotate("VREF.  Anywhere from 0.50 to 0.64 V against GND.\n"
            "Below 0.50 the datasheet says not recommended;\n"
            "above 0.64 the phase cannot reverse at speed.\n"
            "Ships at 1.2 V = 0.9 A.  Needs the Pico powered:\n"
            "the pot divides VCC_IO, so 12 V alone reads 0 V.",
            vref, (DX + DW / 2, DY + DH + 1.05), fontsize=7.8, color=PWR,
            ha="center", va="bottom", linespacing=1.6, zorder=8,
            arrowprops=dict(arrowstyle="-", color=PWR, lw=0.8))

# ------------------------------------------------------- brick and motor
BX, BY, BW, BH = 0.7, 6.9, 2.2, 1.1
ax.add_patch(FancyBboxPatch((BX, BY), BW, BH, boxstyle="round,pad=0.05",
                            facecolor="white", edgecolor=INK, lw=1.2, zorder=2))
ax.text(BX + BW / 2, BY + BH - 0.20, "12 V brick", ha="center", va="top",
        fontsize=9.2, color=INK, fontweight="semibold")
ax.text(BX + BW / 2, BY + BH - 0.50, "5.5 x 2.5 barrel into\nscrew terminals",
        ha="center", va="top", fontsize=7.0, color=GREY, linespacing=1.5)

MX, MY, MW, MH = 0.7, 4.2, 2.2, 1.9
ax.add_patch(Rectangle((MX, MY), MW, MH, facecolor="#b08c3a", edgecolor=INK,
                       lw=1.2, zorder=2))
ax.text(MX + MW / 2, MY + MH - 0.35, "motor", ha="center", va="center",
        fontsize=9.5, color="white", fontweight="semibold", zorder=3)
ax.text(MX + MW / 2, MY + 0.55, "pancake, 48 mm,\nor the old one",
        ha="center", va="center", fontsize=7.2, color="white", zorder=3,
        linespacing=1.5)
ax.text(MX + MW / 2, MY - 0.22,
        "Two leads that read a few ohms to each other are ONE coil.\n"
        "Put one coil on A1 and A2, the other on B1 and B2.\n"
        "A coil split across A and B buzzes and will not turn.",
        ha="center", va="top", fontsize=7.6, color=INK, linespacing=1.6)


def route(pts, color, label, at=None, lw=1.5, off=0.10):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    ax.plot(xs, ys, color=color, lw=lw, solid_joinstyle="miter", zorder=6)
    if label:
        i = at if at is not None else 0
        mx = (xs[i] + xs[i + 1]) / 2
        my = (ys[i] + ys[i + 1]) / 2
        ax.text(mx, my + off, label, ha="center", va="bottom", fontsize=7.4,
                color=color, zorder=7, bbox=dict(fc="white", ec="none", pad=0.8))


# signals: Pico left column straight across to J1
route([pico[4], (10.3, pico[4][1]), (10.3, j1[7][1]), j1[7]], SIG,
      "GP2  pin 4   ->   STEP  J1-7", at=2)
route([pico[5], (9.95, pico[5][1]), (9.95, j1[8][1]), j1[8]], SIG,
      "GP3  pin 5   ->   DIR  J1-8", at=2)
route([pico[6], (10.65, pico[6][1]), (10.65, j1[1][1]), j1[1]], SIG,
      "GP4  pin 6   ->   EN  J1-1    active low", at=2)

# logic rail and ground, routed under everything to the J2 side
route([pico[3], (11.0, pico[3][1]), (11.0, 1.85), (5.75, 1.85),
       (5.75, j2[8][1]), j2[8]], GND, "GND  pin 3   ->   GND  J2-8", at=2)
route([pico[36], (14.55, pico[36][1]), (14.55, 0.42), (5.4, 0.42),
       (5.4, j2[7][1]), j2[7]], IO, "3V3(OUT)  pin 36   ->   VCC_IO  J2-7", at=2)

# brick down into the top of J2
route([(BX + BW, BY + 0.80), (4.75, BY + 0.80), (4.75, j2[1][1]), j2[1]], PWR,
      "12 V  ->  VM  J2-1", at=0)
route([(BX + BW, BY + 0.22), (4.25, BY + 0.22), (4.25, j2[2][1]), j2[2]], GND,
      "0 V  ->  GND  J2-2", at=0)

# motor straight across into the middle of J2
for pin, col, lab in ((3, CA, "A2"), (4, CA, "A1"), (5, CB, "B1"), (6, CB, "B2")):
    route([(MX + MW, j2[pin][1]), j2[pin]], col, None)
    ax.text(MX + MW + 0.25, j2[pin][1] + 0.08, lab, fontsize=7.4, color=col,
            zorder=7, bbox=dict(fc="white", ec="none", pad=0.6))
ax.text(4.6, j2[4][1] + 0.26, "coil A", fontsize=7.6, color=CA, ha="center",
        bbox=dict(fc="white", ec="none", pad=0.8), zorder=7)
ax.text(4.6, j2[6][1] + 0.26, "coil B", fontsize=7.6, color=CB, ha="center",
        bbox=dict(fc="white", ec="none", pad=0.8), zorder=7)

# 100 uF across VM and GND, as close to the terminals as it will go
cx = 5.55
ax.plot([cx - 0.09, cx - 0.09], [j2[2][1] + 0.02, j2[1][1] - 0.02], color=PWR,
        lw=2.2, zorder=8)
ax.plot([cx + 0.07, cx + 0.07], [j2[2][1] + 0.02, j2[1][1] - 0.02], color=GND,
        lw=2.2, zorder=8)
ax.plot([cx - 0.09, 4.75], [j2[1][1], j2[1][1]], color=PWR, lw=1.5, zorder=6)
ax.plot([cx + 0.07, 4.25], [j2[2][1], j2[2][1]], color=GND, lw=1.5, zorder=6)
ax.text(cx, j2[1][1] + 0.30, "100 uF at the terminals", fontsize=7.2,
        color=INK, ha="center", va="bottom", zorder=8,
        bbox=dict(fc="white", ec="none", pad=0.8))

ax.text(DX + DW / 2, DY - 0.28,
        "LEAVE UNCONNECTED:  MS1, MS2  (both open = 1/8 microstep)\n"
        "PDN/UART, CLK  (UART mode, not used here)",
        fontsize=7.8, color=GREY, ha="center", va="top", linespacing=1.6)

ax.text(0.4, 1.60,
        "ORDER, every time:\n"
        "motor wired first, then 12 V on, then USB.\n"
        "Never pull a motor lead with 12 V live.\n"
        "The coil dumps into the driver and kills it.",
        fontsize=8.6, color=PWR, va="top", linespacing=1.7)

ax.text(0.4, 9.35,
        "Pico pins are physical header positions, 1 at the USB end.\n"
        "3, 4, 5 and 6 are four in a row, so GND, STEP, DIR and EN\n"
        "are one short ribbon off the corner of the board.",
        fontsize=7.8, color=GREY, ha="left", va="top", linespacing=1.6)

ax.set_xlim(0, 15.0)
ax.set_ylim(0, 9.5)
ax.axis("off")
out = os.path.join(HERE, "wiring.png")
fig.savefig(out, facecolor="white", bbox_inches="tight")
print("wrote", out)
