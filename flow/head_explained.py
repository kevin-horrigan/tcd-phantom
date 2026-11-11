# -*- coding: utf-8 -*-
"""What "mm of head" means, and where the 1200 mm goes.

    python head_explained.py   ->  head-explained.png + the text below

Every pressure in this project is written as a HEIGHT OF FLUID, and nothing
in these files ever said why, which makes the tables read as nonsense in one
particular place: R1 is 182 mm of tubing and it "costs 780 mm of head". A
182 mm thing cannot use up 780 mm of anything, so the reader is right to
stop. The two columns are both in millimetres and they are not the same
quantity.

  LENGTH is a length. How long the tube is.
  HEAD is a PRESSURE, written as the height of a fluid column that would
       produce it. R1's 780 mm means "the pressure drop across R1 equals the
       pressure at the bottom of a 780 mm column of this fluid". It says
       nothing about how long R1 is.

Why write pressure that way at all. Because the thing driving this loop IS a
height: a jar 1200 mm up. If the driving pressure and every loss are in the
same unit, the whole design becomes arithmetic a person can do in their head.
The jar pays in 1200. Each element spends some. R2 gets the change. Put the
losses in psi and the jar in millimetres and you cannot subtract them without
a calculator, and nobody checks what they cannot subtract.

The conversion, for this fluid only, since it depends on density:

    1 mm of BMF = rho * g * h = 1037 * 9.81 * 0.001 = 10.2 Pa
                = 0.076 mmHg = 0.00147 psi

So 1200 mm of it is 12.2 kPa, 91 mmHg, or 1.77 psi. The jar is about one and
three quarter psi. That is the entire pressure budget of this machine, which
is also why a 0-30 psi dial gauge cannot see any of it.
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

import head_budget as H

HERE = os.path.dirname(os.path.abspath(__file__))
TANK = H.TANK_MM
MMHG, PSI, KPA = 133.322, 6894.757, 1000.0


def pa(mm):
    return H.RHO * H.G * mm * 1e-3


def main():
    A = print
    one = pa(1.0)
    A("WHAT ONE MILLIMETRE OF HEAD IS")
    A("  1 mm of this fluid  =  rho g h  =  %.0f x %.2f x 0.001  =  %.2f Pa"
      % (H.RHO, H.G, one))
    A("                      =  %.4f mmHg  =  %.5f psi" % (one / MMHG, one / PSI))
    A("  so the %.0f mm jar  =  %.1f kPa  =  %.0f mmHg  =  %.2f psi"
      % (TANK, pa(TANK) / KPA, pa(TANK) / MMHG, pa(TANK) / PSI))
    A("")
    A("  It is a PRESSURE written as a height, not a length. Water towers are")
    A("  the everyday version: a tower's job is its height, and the pressure")
    A("  at the tap is that height whatever shape the tower is.")
    A("")

    # ---------------------------------------------------------- the budget
    def h(name):
        L, d = {n: (L, d) for n, L, d, _z in H.SEGMENTS}[name]
        return H.head_mm(H.r_poiseuille(L, d) * H.q_si(H.Q_MEAN))

    r1 = h("R1, fixed resistance")
    settle = h("settling run, 3 mm")
    lumen = h("phantom lumen")
    quarter = sum(h(n) for n, _L, _d, _z in H.SEGMENTS
                  if n not in ("R1, fixed resistance", "settling run, 3 mm",
                               "phantom lumen"))
    r2 = TANK - (r1 + settle + lumen + quarter)

    SLICES = [
        ("R1, the fixed resistance", r1, "#b4462e",
         "deliberate. It is what keeps the pulse from going back up to the jar"),
        ("R2, the adjustable one", r2, "#2e6fb4",
         "the change left over. This is the only knob you get"),
        ("the 3 mm settling run", settle, "#c9820f",
         "150 mm of narrow tube, and narrow tube is expensive"),
        ("the lumen itself", lumen, "#8a7452",
         "the device under test. Not negotiable"),
        ("all the 1/4 in tubing", quarter, "#6f6f6f",
         "six runs, 1.4 m of it, and it barely registers"),
    ]

    A("WHERE THE %.0f mm GOES" % TANK)
    A("  %-26s %9s %8s %8s %7s" % ("", "mm", "kPa", "mmHg", "share"))
    for nm, mm, _c, _note in SLICES:
        A("  %-26s %9.0f %8.2f %8.1f %6.0f%%"
          % (nm, mm, pa(mm) / KPA, pa(mm) / MMHG, 100.0 * mm / TANK))
    A("  %-26s %9.0f %8.2f %8.1f %6.0f%%"
      % ("THE JAR PAYS IN", TANK, pa(TANK) / KPA, pa(TANK) / MMHG, 100.0))
    A("")
    for nm, _mm, _c, note in SLICES:
        A("  %-26s %s" % (nm, note))
    A("")
    A("  Read that as money. The jar is the income, %.2f psi of it. Each row"
      % (pa(TANK) / PSI))
    A("  is a bill. R2 is what is left at the end of the month, and it is the")
    A("  only row you can change by turning something.")
    A("")
    A("  The one that looks wrong: R1 is %.0f mm of tubing and costs %.0f mm"
      % ({n: L for n, L, _d, _z in H.SEGMENTS}["R1, fixed resistance"], r1))
    A("  of head. Both numbers are in millimetres and they measure different")
    A("  things. A garden hose nozzle is 20 mm long and drops most of the")
    A("  pressure in the whole hose, for exactly the same reason: resistance")
    A("  goes as 1/bore^4, so a narrow bit does the work regardless of length.")

    # -------------------------------------------------------------- figure
    fig, ax = plt.subplots(1, 2, figsize=(12.6, 7.4), dpi=170,
                           gridspec_kw={"width_ratios": [1.0, 1.35]})
    fig.patch.set_facecolor("white")

    # left: the column of fluid IS the pressure
    a0 = ax[0]
    a0.add_patch(Rectangle((0.38, 0), 0.24, TANK, facecolor="#cfe0f0",
                           edgecolor="#2e6fb4", lw=1.8))
    a0.add_patch(FancyBboxPatch((0.20, TANK), 0.60, 90,
                                boxstyle="round,pad=0.005",
                                facecolor="#dce7f2", edgecolor="#2e6fb4",
                                lw=1.8))
    a0.text(0.50, TANK + 45, "the jar", ha="center", va="center", fontsize=9.5,
            color="#1b1b1b")
    a0.annotate("", xy=(0.14, 0), xytext=(0.14, TANK),
                arrowprops=dict(arrowstyle="<->", color="#2e6fb4", lw=1.6))
    a0.text(0.10, TANK / 2, "%.0f mm" % TANK, ha="right", va="center",
            fontsize=13, color="#2e6fb4", fontweight="semibold", rotation=90)
    a0.plot([0.30, 0.86], [0, 0], color="#1b1b1b", lw=2.2)
    a0.text(0.58, -120,
            "the pressure down here\nis %.1f kPa  =  %.0f mmHg  =  %.2f psi"
            % (pa(TANK) / KPA, pa(TANK) / MMHG, pa(TANK) / PSI),
            ha="center", va="top", fontsize=9.5, color="#1b1b1b",
            linespacing=1.6)
    a0.text(0.58, -330,
            "That is all \"mm of head\" means:\na pressure, written as the "
            "height of\nfluid that would make it.\n\n1 mm of this fluid = %.1f Pa"
            % one, ha="center", va="top", fontsize=9, color="#555",
            linespacing=1.6)
    a0.set_xlim(0.0, 1.0)
    a0.set_ylim(-620, TANK + 190)
    a0.axis("off")
    a0.set_title("A height IS a pressure", fontsize=11.5)

    # right: the same 1200 mm, spent
    a1 = ax[1]
    # Thin slices cannot be labelled at their own centre without the labels
    # landing on each other, so they get reserved rows and a leader line.
    LABEL_Y = {"the 3 mm settling run": 975.0,
               "the lumen itself": 1075.0,
               "all the 1/4 in tubing": 1175.0}
    bottom = 0.0
    for nm, mm, col, _note in SLICES:
        a1.bar(0.0, mm, bottom=bottom, width=0.5, color=col,
               edgecolor="white", lw=1.2)
        mid = bottom + mm / 2.0
        ly = LABEL_Y.get(nm, mid)
        if abs(ly - mid) > 1.0:
            a1.plot([0.26, 0.42], [mid, ly], color=col, lw=0.8, alpha=0.6)
        a1.text(0.44, ly,
                "%s\n%.0f mm   %.2f psi   %.0f %%"
                % (nm, mm, pa(mm) / PSI, 100.0 * mm / TANK),
                ha="left", va="center", fontsize=9, color=col,
                linespacing=1.5, fontweight="semibold")
        bottom += mm
    a1.plot([-0.30, 0.30], [TANK, TANK], color="#1b1b1b", lw=1.6, ls="--")
    a1.text(0.0, TANK + 112, "the jar pays in %.0f mm" % TANK, ha="center",
            va="center", fontsize=10.5, color="#1b1b1b", fontweight="semibold")
    a1.set_xlim(-0.55, 1.95)
    a1.set_ylim(-110, TANK + 215)
    a1.set_ylabel("mm of head")
    a1.set_xticks([])
    for sp in ("top", "right", "bottom"):
        a1.spines[sp].set_visible(False)
    a1.grid(axis="y", alpha=0.25, lw=0.6)
    a1.set_title("and this is where it is spent", fontsize=11.5)

    fig.suptitle("The head budget, in plain terms", fontsize=13.5, y=0.985)
    fig.text(0.5, 0.015,
             "R1 is %.0f mm of tubing and costs %.0f mm of head. Both are "
             "millimetres and they are different quantities: one is a length, "
             "the other is a pressure."
             % ({n: L for n, L, _d, _z in H.SEGMENTS}["R1, fixed resistance"],
                r1),
             fontsize=9, color="#555", ha="center")
    fig.tight_layout(rect=(0, 0.035, 1, 0.955))
    fig.savefig(os.path.join(HERE, "head-explained.png"), facecolor="white")
    A("")
    A("wrote head-explained.png")


if __name__ == "__main__":
    main()
