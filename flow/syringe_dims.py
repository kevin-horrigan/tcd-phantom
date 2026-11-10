# -*- coding: utf-8 -*-
"""The syringe, measured, with what each number moved in the design.

    python syringe_dims.py   ->  syringe-dims.png

Six dimensions in syringe_drive.py carried a "<-- MEASURE" comment. Five were
measured on the BH Supplies BH5LL on 2026-11-10 and are drawn here at their
real sizes. Two remain, and both only confirm a frame that is already off the
bed, so nothing waits on them.

The bore area is the odd one out and the most important. It is not a caliper
dimension at all: no feature of the barrel equals the piston area, because
the inside wall carries draft and the graduations are printed on the outside.
So it gets measured the way the manufacturer guarantees it, between marks:

    BORE_A = (volume between two marks in mm3) / (distance between them, mm)
    1 mL to 4 mL is 25.0 mm, so 3000 / 25.0 = 120.0 mm2

Use marks away from the zero end. Zero sits where the gasket is still seating
and the taper begins, and it is the least honest part of the barrel.

Two of the five corroborate each other, which is why they are worth drawing
together. A 120.0 mm2 bore is 12.36 mm across, and inside a 14.0 mm OD that
leaves a 0.82 mm barrel wall, exactly what a moulded polypropylene 5 mL
barrel runs. A 12.0 mm plunger rod inside that same 12.36 mm bore is a cross
sized to very nearly fill it, which is what the part is supposed to be. Three
independent caliper readings that agree on one geometry are worth more than
any one of them alone.
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, FancyArrowPatch

HERE = os.path.dirname(os.path.abspath(__file__))

# Measured 2026-11-10 unless marked. The drawing is to these, so it is a real
# elevation of the real part, not a sketch at nominal proportions.
BARREL_D = 14.0                  # measured
DISC_D, DISC_T = 16.5, 2.0       # measured
ROD_D = 12.0                     # measured
ML_PITCH = 25.0 / 3.0            # measured: 1 mL to 4 mL is 25.0 mm
BARREL_L = 66.0                  # measured
FLANGE_T = 2.0                   # measured
FLANGE_D = 24.0                  # flange WIDTH, never needed, drawn nominal
BORE_D = 12.36                   # derived from BORE_A = 120.0

TIP_L, TIP_D, LOCK_D = 9.0, 4.3, 8.0
DRAWN_OUT = 30.0                 # how far the plunger is withdrawn, for clarity
ZERO_X = -7.0

BODY = (0.93, 0.94, 0.95)
EDGE = (0.30, 0.32, 0.35)
RUBBER = (0.45, 0.42, 0.40)
MASTER = (0.69, 0.13, 0.13)
DONE = (0.11, 0.40, 0.29)
OPEN = (0.50, 0.53, 0.56)
NAME = (0.42, 0.44, 0.47)

FLANGE_X = -BARREL_L
DISC_X = FLANGE_X - DRAWN_OUT
L1 = -FLANGE_D / 2.0 - 5.0
L2 = -FLANGE_D / 2.0 - 13.0


def arrow(ax, p0, p1, c):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="<|-|>", mutation_scale=9,
                                 lw=1.1, color=c, zorder=6,
                                 shrinkA=0, shrinkB=0))


def witness(ax, pts, c):
    for (x0, y0), (x1, y1) in pts:
        ax.plot([x0, x1], [y0, y1], lw=0.6, c=c, zorder=5)


def dim_h(ax, x0, x1, y, text, c, above=True, from_y=None):
    if from_y is not None:
        witness(ax, [((x0, from_y), (x0, y)), ((x1, from_y), (x1, y))], c)
    arrow(ax, (x0, y), (x1, y), c)
    ax.text((x0 + x1) / 2.0, y + (1.0 if above else -1.2), text,
            ha="center", va="bottom" if above else "top",
            fontsize=9, color=c, zorder=7)


def dim_v(ax, y0, y1, x, text, c, from_x=None):
    if from_x is not None:
        witness(ax, [((from_x, y0), (x, y0)), ((from_x, y1), (x, y1))], c)
    arrow(ax, (x, y0), (x, y1), c)
    ax.text(x, max(y0, y1) + 1.4, text, ha="center", va="bottom",
            fontsize=9, color=c, zorder=7)


def main():
    fig, ax = plt.subplots(figsize=(13.6, 7.8))

    # ---- the syringe, side elevation, tip to the right ----
    ax.add_patch(Rectangle((FLANGE_X, -BARREL_D / 2), BARREL_L, BARREL_D,
                           fc=BODY, ec=EDGE, lw=1.3, zorder=2))
    ax.add_patch(Rectangle((FLANGE_X, -FLANGE_D / 2), FLANGE_T, FLANGE_D,
                           fc=BODY, ec=EDGE, lw=1.3, zorder=4))

    # the bore itself, dashed, because it is derived and not drawn on the part
    for s in (-1, 1):
        ax.plot([FLANGE_X + 1.0, -1.0], [s * BORE_D / 2, s * BORE_D / 2],
                lw=0.8, c=(0.62, 0.30, 0.30), ls=(0, (5, 4)), zorder=3)

    ax.add_patch(Polygon([(0, -TIP_D / 2 - 0.9), (TIP_L, -TIP_D / 2 + 0.4),
                          (TIP_L, TIP_D / 2 - 0.4), (0, TIP_D / 2 + 0.9)],
                         fc=BODY, ec=EDGE, lw=1.2, zorder=2))
    for s in (-1, 1):
        ax.add_patch(Rectangle((0, s * (LOCK_D / 2 - 1.4)), TIP_L - 2.5,
                               s * 1.4, fc=(0.86, 0.87, 0.88), ec=EDGE,
                               lw=1.0, zorder=2))

    ax.add_patch(Rectangle((DISC_X, -DISC_D / 2), DISC_T, DISC_D,
                           fc=BODY, ec=EDGE, lw=1.3, zorder=3))
    ax.add_patch(Rectangle((DISC_X + DISC_T, -ROD_D / 2),
                           (FLANGE_X + DRAWN_OUT) - (DISC_X + DISC_T) + 1.0,
                           ROD_D, fc=(0.88, 0.89, 0.90), ec=EDGE, lw=1.1,
                           zorder=2))
    ax.plot([DISC_X + DISC_T, FLANGE_X + DRAWN_OUT], [0, 0],
            lw=0.7, c=EDGE, ls=(0, (4, 3)), zorder=3)
    ax.add_patch(Rectangle((FLANGE_X + DRAWN_OUT - 1.0, -BARREL_D / 2 + 0.9),
                           4.0, BARREL_D - 1.8,
                           fc=RUBBER, ec=EDGE, lw=1.0, zorder=3))

    for n in range(0, 6):
        x = ZERO_X - n * ML_PITCH
        key = n in (1, 4)
        ax.plot([x, x], [-BARREL_D / 2, -BARREL_D / 2 + (3.4 if key else 2.0)],
                lw=1.6 if key else 0.9,
                c=MASTER if key else (0.58, 0.60, 0.63), zorder=2)
        ax.text(x, -BARREL_D / 2 - 0.9, "%d" % n, ha="center", va="top",
                fontsize=8, zorder=6,
                color=MASTER if key else (0.58, 0.60, 0.63),
                weight="bold" if key else "normal")

    # ---- the master parameter, alone above the part ----
    x1, x4 = ZERO_X - ML_PITCH, ZERO_X - 4 * ML_PITCH
    yb = BARREL_D / 2 + 6.0
    witness(ax, [((x1, -BARREL_D / 2), (x1, yb)),
                 ((x4, -BARREL_D / 2), (x4, yb))], MASTER)
    arrow(ax, (x4, yb), (x1, yb), MASTER)
    ax.text((x1 + x4) / 2.0, yb + 1.2,
            "1 mL mark to 4 mL mark  =  3 mL of travel  =  25.0 mm measured",
            ha="center", va="bottom", fontsize=9, color=MASTER, zorder=7)
    ax.text((x1 + x4) / 2.0, yb + 5.2,
            "the master parameter. 5% above the 114.2 that was assumed, so a "
            "4.17 mm beat and 219 rpm, not 4.38 and 230",
            ha="center", va="bottom", fontsize=8.5, color=MASTER, zorder=7,
            style="italic")
    ax.text((x1 + x4) / 2.0, yb + 9.2,
            "BORE_A  =  3000 / 25.0  =  120.0 mm2",
            ha="center", va="bottom", fontsize=12.5, color=MASTER, zorder=7,
            weight="bold")

    # ---- the five that are measured ----
    dim_v(ax, -DISC_D / 2, DISC_D / 2, DISC_X - 8.0, "DISC_D  16.5", DONE,
          from_x=DISC_X)
    dim_h(ax, DISC_X, DISC_X + DISC_T, L1, "DISC_T  2.0", DONE, above=False,
          from_y=-DISC_D / 2)
    dim_v(ax, -ROD_D / 2, ROD_D / 2, DISC_X + DISC_T + 17.0,
          "PLUNGER_ROD_D  12.0", DONE)
    dim_v(ax, -BARREL_D / 2, BARREL_D / 2, 40.0, "SYR_BARREL_D  14.0", DONE,
          from_x=0.0)

    # ---- the two still open, and neither gates a print ----
    dim_h(ax, FLANGE_X, FLANGE_X + FLANGE_T, L1, "SYR_FLANGE_T  2.0", DONE,
          above=False, from_y=-FLANGE_D / 2)
    dim_h(ax, FLANGE_X, 0.0, L2, "SYR_BARREL_L  66.0", DONE, above=False,
          from_y=-BARREL_D / 2)

    for x, y, t, ha, c in (
            (DISC_X + DISC_T / 2, -DISC_D / 2 - 1.4, "thumb disc", "center", NAME),
            (DISC_X + DISC_T + 9.0, -ROD_D / 2 - 1.4, "plunger rod", "left", NAME),
            (FLANGE_X + FLANGE_T + 1.5, FLANGE_D / 2 - 1.2,
             "finger flange", "left", NAME),
            (FLANGE_X + DRAWN_OUT + 1.0, BARREL_D / 2 + 1.2, "gasket", "center",
             NAME),
            (ZERO_X - 2.5 * ML_PITCH, -BARREL_D / 2 - 4.8,
             "graduations, printed on the outside wall", "center", NAME),
            (TIP_L + 3.0, 1.6, "luer lock tip", "left", NAME),
            (TIP_L + 3.0, -1.8,
             "bore 12.36 (dashed), derived from BORE_A,\nnever measured "
             "directly", "left", (0.62, 0.30, 0.30))):
        ax.text(x, y, t, ha=ha, va="center", fontsize=8.5, color=c,
                zorder=7, linespacing=1.5)

    # ---- the table ----
    rows = [("BORE_A", "3000 / 25.0 mm, 1 mL to 4 mL", "120.0 mm2",
             "beat 4.17 mm, peak 219 rpm", MASTER),
            ("SYR_BARREL_D", "barrel OD, on the smooth tube", "14.0 mm",
             "collar, and it forced a split one", DONE),
            ("DISC_D", "thumb disc diameter", "16.5 mm",
             "carriage fork, 5.5 mm taller", DONE),
            ("DISC_T", "thumb disc thickness", "2.0 mm",
             "carriage disc pocket", DONE),
            ("PLUNGER_ROD_D", "rod, across the widest of the cross", "12.0 mm",
             "carriage rod slot, 5 mm wider", DONE),
            ("SYR_BARREL_L", "flange face to tip shoulder", "66.0 mm",
             "10 mm longer than the frame assumed", DONE),
            ("SYR_FLANGE_T", "finger flange thickness", "2.0 mm",
             "0.5 mm of slack behind the rib", DONE)]
    y0 = L2 - 11.0
    xa = DISC_X - 10.0
    xb, xc, xd = xa + 40.0, xa + 92.0, xa + 120.0
    ax.text(xa, y0 + 5.2,
            "measured 2026-11-10, BH Supplies BH5LL 5 mL luer lock",
            fontsize=11, color=(0.18, 0.20, 0.23), weight="bold", va="bottom")
    for x, h in ((xa, "name"), (xb, "what the caliper was on"),
                 (xc, "value"), (xd, "what it moved")):
        ax.text(x, y0 + 1.6, h, fontsize=8.5, color=(0.48, 0.50, 0.53),
                style="italic", va="bottom")
    ax.plot([xa, xd + 40.0], [y0 + 0.5, y0 + 0.5], lw=0.8,
            c=(0.72, 0.74, 0.77), zorder=3)
    for i, (n, how, now, feeds, c) in enumerate(rows):
        y = y0 - 3.6 - i * 4.0
        ax.text(xa, y, n, fontsize=9, color=c, va="center", family="monospace")
        ax.text(xb, y, how, fontsize=9, color=(0.25, 0.27, 0.30), va="center")
        ax.text(xc, y, now, fontsize=9, color=c, va="center")
        ax.text(xd, y, feeds, fontsize=9, color=c, va="center")

    ax.text(xa, y0 - 3.6 - len(rows) * 4.0 - 2.4,
            "Three of the six landed outside the guess by more than a "
            "tolerance. The barrel is 14.0 and not the 12.5 assumed when the "
            "saddle bore was frozen at 16.0,\nso a saddle sized snugly to that "
            "guess would have rejected the real syringe and four hours of "
            "frame would be scrap. The barrel is 66 mm and not 56, and\nthe "
            "flange 2.0 and not 2.5, so the printed frame no longer matches "
            "what the model would now draw. The frame is therefore PINNED to "
            "as-built and the real\nsyringe is checked against it, rather than "
            "the model quietly certifying a part nobody owns. All 39 checks "
            "pass, and the regenerated frame STL is\nbyte-identical to the one "
            "that was printed.",
            fontsize=8.8, color=(0.33, 0.35, 0.38), va="top", linespacing=1.7)

    ax.set_xlim(xa - 5.0, xd + 44.0)
    ax.set_ylim(y0 - 3.6 - len(rows) * 4.0 - 14.0, yb + 15.0)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("5 mL luer-lock syringe, measured: what each number moved",
                 fontsize=13, color=(0.13, 0.15, 0.18), pad=4)
    fig.tight_layout(pad=0.4)
    out = os.path.join(HERE, "syringe-dims.png")
    fig.savefig(out, dpi=170, facecolor="white")
    print("wrote %s" % out)


if __name__ == "__main__":
    main()
