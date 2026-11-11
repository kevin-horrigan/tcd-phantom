# -*- coding: utf-8 -*-
"""One page the team can build from, with the numbers in units people use.

    python one_pager.py   ->  loop-one-pager.png

loop-diagram.png is the working drawing: every run ballooned, every length
and bore and pressure drop in a table under it. It is correct and it is a lot
to hand someone.

This is the same loop said simply, and the simplification is mostly one
decision: STOP WRITING PRESSURE AS MILLIMETRES OF HEAD. That unit is right
for the budget arithmetic and wrong for a reader, because the drawing then
has two columns of millimetres that are different quantities. Here:

    pressures are mmHg, because anyone who has seen a blood pressure
      can read them
    lengths are mm or m, and they are only ever lengths
    shares of the budget are percentages, with no unit at all

Nothing is rounded in a way that changes a decision. R1 is "about 180 mm,
cut long and trim" because that is honestly what it is: a measured length
trimmed on the bench, not a dimension held to a tenth.
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle

import head_budget as H
import syringe_drive as S

HERE = os.path.dirname(os.path.abspath(__file__))
MMHG = 133.322
TANK = H.TANK_MM


def mmhg(mm):
    return H.RHO * H.G * mm * 1e-3 / MMHG


def seg(name):
    L, d = {n: (L, d) for n, L, d, _z in H.SEGMENTS}[name]
    return L, d, H.head_mm(H.r_poiseuille(L, d) * H.q_si(H.Q_MEAN))


INK, MUTE, HOT, COOL, GOLD = "#1b1b1b", "#6f6f6f", "#b4462e", "#2e6fb4", "#b8790b"
PURPLE, SAND, GREEN = "#6b4aa0", "#8a7452", "#3c7a4a"


def main():
    r1_L, r1_d, r1_h = seg("R1, fixed resistance")
    set_L, set_d, set_h = seg("settling run, 3 mm")
    lum_L, lum_d, lum_h = seg("phantom lumen")
    quarter = sum(seg(n)[2] for n, _L, _d, _z in H.SEGMENTS
                  if n not in ("R1, fixed resistance", "settling run, 3 mm",
                               "phantom lumen"))
    r2_h = TANK - (r1_h + set_h + lum_h + quarter)

    # the operating point, in units a reader already owns
    mean_tee = TANK - r1_h - (quarter - seg("phantom to R2")[2]
                              - seg("return to reservoir")[2])
    pulse_mm = 508.0            # from instrumentation.py's first-order estimate
    peak_mmhg = mmhg(mean_tee + pulse_mm)

    fig = plt.figure(figsize=(16.0, 12.4), dpi=150)
    fig.patch.set_facecolor("white")
    ax = fig.add_axes((0.015, 0.560, 0.970, 0.375))
    ax.set_xlim(0, 10.6)
    ax.set_ylim(-3.6, 6.4)
    ax.axis("off")

    def pipe(x0, x1, y=0.0, w=7.0, col=COOL, z=3):
        ax.plot([x0, x1], [y, y], color=col, lw=w, solid_capstyle="butt",
                zorder=z)

    def vpipe(x, y0, y1, w=7.0, col=COOL, z=3):
        ax.plot([x, x], [y0, y1], color=col, lw=w, solid_capstyle="butt",
                zorder=z)

    def lab(x, y, text, col=INK, size=10.5, ha="center", va="bottom",
            weight="normal"):
        ax.text(x, y, text, ha=ha, va=va, fontsize=size, color=col,
                zorder=12, linespacing=1.6, fontweight=weight)

    def bore(x, y, text, col=INK, rot=0):
        """A size label sitting on the run it describes.

        On the pipe rather than in the legend, because a buy list that says
        "1/4 inch for everything but two places" leaves the reader to find
        the two places, and finding them is the part that goes wrong.
        """
        ax.text(x, y, text, ha="center", va="center", fontsize=8.0,
                color=col, zorder=14, linespacing=1.35, rotation=rot,
                bbox=dict(boxstyle="round,pad=0.28", facecolor="white",
                          edgecolor=col, linewidth=0.9))

    # Labelled by BORE, with both ways to buy that bore underneath, because
    # the number on the bag means inside diameter in one aisle and outside
    # diameter in the other.
    QTR = "6.35 mm bore\n1/4 barb or 3/8 push"
    SML = "4 mm bore\n1/4 in push"
    LUM = "3 mm\n1/8 in barb"

    X_JAR, X_DROP = 0.55, 1.05
    X_R1A, X_R1B = 1.60, 2.45
    X_P1, X_PLEN = 3.30, 4.50
    X_P2, X_RED = 5.10, 5.55
    X_IN, X_OUT = 6.35, 7.80
    X_R2, X_RES = 8.75, 9.90

    # ------------------------------------------------------------- the jar
    ax.add_patch(FancyBboxPatch((X_JAR - 0.42, 4.10), 0.92, 0.85,
                                boxstyle="round,pad=0.02", facecolor="#dce7f2",
                                edgecolor=COOL, lw=2.0, zorder=4))
    ax.plot([X_JAR - 0.38, X_JAR + 0.46], [4.70, 4.70], color=COOL, lw=1.6,
            zorder=5)
    lab(X_JAR + 0.04, 5.15, "JAR", COOL, 12, weight="bold")
    lab(X_JAR + 0.04, 3.70, "kept full and\noverflowing", MUTE, 9, va="top")
    vpipe(X_DROP, 4.10, 0.0)
    ax.annotate("", xy=(0.12, 0.0), xytext=(0.12, 4.10),
                arrowprops=dict(arrowstyle="<->", color=COOL, lw=1.8))
    lab(0.24, 2.05, "1.2 m", COOL, 14, ha="left", va="center", weight="bold")
    lab(0.10, -0.70, "that height is\nthe whole push:\n%.0f mmHg\n%.2f psi"
        % (mmhg(TANK), H.RHO * H.G * TANK * 1e-3 / 6894.757),
        COOL, 10, ha="left", va="top")
    pipe(X_DROP, X_R1A)
    # No badge on the vertical drop: the horizontal run right below it
    # carries the same one, and the wider label made this a collision with
    # the 1.2 m dimension. Ten labels, not eleven.
    bore((X_DROP + X_R1A) / 2, 0.30, QTR, COOL)

    # ---------------------------------------------------------------- R1
    xs = np.linspace(X_R1A, X_R1B, 200)
    ax.plot(xs, 0.22 * np.sin((xs - X_R1A) / (X_R1B - X_R1A) * 8 * np.pi),
            color=HOT, lw=5.0, solid_capstyle="round", zorder=6)
    lab((X_R1A + X_R1B) / 2, 0.78, "R1", HOT, 12, weight="bold")
    bore((X_R1A + X_R1B) / 2, 0.38, SML, HOT)
    lab((X_R1A + X_R1B) / 2 - 0.12, -0.55,
        "about %.1f m of the\nkit's 1/4 inch tube\ncoiled. Cut long, trim"
        % (round(r1_L / 100.0) / 10.0), HOT, 9.5, va="top")

    # ------------------------------------------------------ the manometer
    # It had fallen off this drawing entirely during the rewrite, while the
    # head budget kept saying "trim it against the manometer". A tube nobody
    # has drawn is a tube nobody will build.
    X_MANO = X_R1B + 0.22
    H_MANO = 4.10 * 405.0 / 1200.0          # 405 mm on the jar's own scale
    pipe(X_R1B, X_P1)
    vpipe(X_MANO, 0.0, H_MANO + 0.26, w=4.0, col=GOLD)
    ax.plot([X_MANO - 0.085, X_MANO + 0.085], [H_MANO, H_MANO], color=GOLD,
            lw=3.0, zorder=7)
    lab(X_MANO - 0.42, 3.05, "MANOMETER", GOLD, 11.5, weight="bold")
    lab(X_MANO - 0.42, 2.92,
        "a clear tube, open at the top.\n"
        "Stands at 405 mm when R1 is right.\n"
        "700 mm tall, top returned to the\n"
        "reservoir so a shut R2 spills there.",
        MUTE, 9.5, va="top")
    bore((X_R1B + X_P1) / 2 + 0.28, 0.30, QTR, COOL)
    vpipe(X_P1, -1.35, 0.0, col=HOT)
    bore(X_P1 + 0.40, -0.85, QTR, HOT)
    ax.add_patch(Circle((X_P1, 0.0), 0.075, facecolor=INK, edgecolor="none",
                        zorder=7))
    ax.add_patch(FancyBboxPatch((X_P1 - 0.84, -2.95), 1.68, 1.50,
                                boxstyle="round,pad=0.02", facecolor="#f9e8e3",
                                edgecolor=HOT, lw=1.8, zorder=4))
    lab(X_P1, -2.20, "PISTON\nhalf a millilitre\nper heartbeat", HOT, 10.5,
        va="center")

    # ------------------------------------------------------------ plenum
    pipe(X_P1, X_PLEN, col=HOT)
    bore((X_P1 + X_PLEN) / 2 + 0.05, 0.30, QTR, HOT)
    vpipe(X_PLEN, 0.0, 1.30)
    bore(X_PLEN - 0.50, 1.02, QTR, COOL)
    ax.add_patch(Rectangle((X_PLEN - 0.17, 0.95), 0.34, 1.15,
                           facecolor="#dce7f2", edgecolor=COOL, lw=1.8,
                           zorder=5))
    ax.plot([X_PLEN - 0.17, X_PLEN + 0.17], [1.42, 1.42], color=COOL, lw=1.5,
            zorder=6)
    ax.text(X_PLEN, 1.72, "air", ha="center", va="center", fontsize=8.5,
            color=MUTE, zorder=13)
    lab(X_PLEN, 2.56, "PLENUM", COOL, 12, weight="bold")
    lab(X_PLEN, 2.46, "rounds the pulse", MUTE, 9.5, va="top")

    # ---------------------------------------------------- taps and reducer
    for x, nm in ((X_P1, "P1"), (X_P2, "P2")):
        vpipe(x, 0.0, 2.85, w=2.0, col=PURPLE)
        ax.add_patch(Circle((x, 3.00), 0.145, facecolor="white",
                            edgecolor=PURPLE, lw=2.0, zorder=6))
        ax.text(x, 3.00, nm, ha="center", va="center", fontsize=9.5,
                color=PURPLE, fontweight="bold", zorder=13)
    lab(X_P1, 3.25, "before", PURPLE, 9.5)
    lab(X_P2, 3.25, "after", PURPLE, 9.5)
    lab((X_P1 + X_P2) / 2, 3.95, "TWO PRESSURE TAPS", PURPLE, 11,
        weight="bold")
    lab((X_P1 + X_P2) / 2, 3.78,
        "the difference between them is\nwhat the plenum is doing",
        MUTE, 9.5, va="top")

    pipe(X_PLEN, X_RED)
    bore(X_PLEN + 0.36, 0.30, QTR, COOL)
    ax.plot([X_RED - 0.07, X_RED + 0.07, X_RED + 0.07, X_RED - 0.07],
            [0.13, 0.055, -0.055, -0.13], color=INK, lw=1.8, zorder=6)

    # ------------------------------------------------------ settling run
    pipe(X_RED, X_IN, w=3.4, col=INK)
    bore((X_RED + X_IN) / 2, 0.34, LUM, INK)
    lab((X_RED + X_IN) / 2 - 0.26, -0.50,
        "%.0f mm of straight\n3 mm tubing\nNO TEES HERE" % set_L, INK, 9.5,
        va="top")

    # -------------------------------------------------------------- head
    ax.add_patch(FancyBboxPatch((X_IN, -0.78), X_OUT - X_IN, 1.56,
                                boxstyle="round,pad=0.02", facecolor="#eadfc8",
                                edgecolor=SAND, lw=2.0, zorder=2))
    pipe(X_IN, X_OUT, w=3.4, col=INK, z=6)
    bore((X_IN + X_OUT) / 2, 0.34, "3 mm\ncast lumen", SAND)
    lab((X_IN + X_OUT) / 2, 0.98, "THE HEAD", "#6b5636", 12.5, weight="bold")
    lab((X_IN + X_OUT) / 2, -0.96, "Group 1's block,\n3 mm lumen", SAND, 9.5,
        va="top")
    ax.plot([(X_IN + X_OUT) / 2 + 0.30, (X_IN + X_OUT) / 2 + 0.62],
            [0.80, 2.60], color=GREEN, lw=2.4, zorder=8)
    lab((X_IN + X_OUT) / 2 + 0.66, 2.70, "DOPPLER", GREEN, 11.5, ha="left",
        weight="bold")
    lab((X_IN + X_OUT) / 2 + 0.66, 2.55,
        "the only view\ninto the block", MUTE, 9.5, ha="left", va="top")

    # ---------------------------------------------------------------- R2
    pipe(X_OUT, X_R2)
    bore((X_OUT + X_R2) / 2, 0.30, QTR, COOL)
    ax.plot([X_R2 - 0.16, X_R2, X_R2 + 0.16], [0.28, 0.05, 0.28],
            color=INK, lw=2.2, zorder=6)
    ax.plot([X_R2 - 0.16, X_R2, X_R2 + 0.16], [-0.28, -0.05, -0.28],
            color=INK, lw=2.2, zorder=6)
    lab(X_R2, 0.55, "R2", INK, 12, weight="bold")
    lab(X_R2, -0.55, "190 mm of the kit's 1/4 in\ntube with a screw clamp.\n"
        "THE ONLY KNOB you turn.\ndrops 13 mmHg, 0.25 psi",
        INK, 9.5, va="top")

    # ------------------------------------------------- reservoir and pump
    pipe(X_R2, X_RES)
    bore((X_R2 + X_RES) / 2, 0.30, QTR, COOL)
    vpipe(X_RES, -1.55, 0.0)
    ax.add_patch(FancyBboxPatch((X_RES - 0.62, -2.35), 1.24, 0.82,
                                boxstyle="round,pad=0.02", facecolor="#dce7f2",
                                edgecolor=COOL, lw=1.8, zorder=4))
    ax.plot([X_RES - 0.58, X_RES + 0.58], [-1.78, -1.78], color=COOL, lw=1.5,
            zorder=5)
    lab(X_RES, -2.25, "RESERVOIR", COOL, 10, va="center")
    ax.add_patch(Circle((X_RES - 1.45, -2.90), 0.20, facecolor="white",
                        edgecolor=GREEN, lw=2.2, zorder=6))
    ax.text(X_RES - 1.45, -2.90, "M", ha="center", va="center", fontsize=10,
            color=GREEN, fontweight="bold", zorder=12)
    ax.plot([X_RES - 1.25, X_RES - 0.62], [-2.90, -2.90], color=GREEN, lw=5,
            solid_capstyle="butt", zorder=3)
    ax.annotate("", xy=(X_RES - 2.25, -2.90), xytext=(X_RES - 1.70, -2.90),
                arrowprops=dict(arrowstyle="-|>", color=GREEN, lw=2.4))
    lab(X_RES - 2.35, -2.90, "pump, back up to the jar", GREEN, 10,
        ha="right", va="center")

    for x in (1.35, 2.85, 5.00, 8.30, 9.45):
        ax.plot([x], [0.0], marker=">", ms=8, color="white", zorder=9,
                markeredgecolor="white")

    # ------------------------------------------------- the pressure profile
    # Every station labelled in both units, on its own strip rather than on
    # the pipe. The runs already carry a bore badge each and a second badge
    # on the same line would make the drawing unreadable.
    pp = fig.add_axes((0.015, 0.462, 0.970, 0.088), sharex=ax)
    STATIONS = [
        (X_DROP, 1200.0, "the jar"),
        (X_R1A, 1191.6, ""),
        (X_R1B, 411.6, "after R1"),
        (X_P1, 405.3, "P1"),
        (X_PLEN, 399.0, ""),
        (X_P2, 396.0, "P2"),
        (X_RED, 392.6, ""),
        (X_IN, 265.9, "into the block"),
        (X_OUT, 198.3, "out of it"),
        (X_R2, 189.9, ""),
        (X_R2 + 0.12, 21.0, "after R2"),
        (X_RES, 0.0, "reservoir"),
    ]
    xs = [s[0] for s in STATIONS]
    ys = [s[1] for s in STATIONS]
    pp.fill_between(xs, 0, ys, color="#2e6fb4", alpha=0.13)
    pp.plot(xs, ys, color=COOL, lw=2.4, solid_capstyle="round")
    for x, y, lab in STATIONS:
        pp.plot([x], [y], "o", ms=4.5, color=COOL, zorder=6)
        if not lab:
            continue
        pa = y * 1e-3 * 1037.0 * 9.80665
        up = lab in ("the jar", "P1", "into the block", "after R2")
        pp.text(x, y + (115 if up else -115),
                "%s\n%.0f mm   %.0f mmHg   %.2f psi"
                % (lab, y, pa / 133.322, pa / 6894.757),
                ha="center", va="bottom" if up else "top", fontsize=8.0,
                color=INK, linespacing=1.4)
    pp.set_ylim(-640, 1560)
    pp.set_yticks([])
    pp.set_xticks([])
    for sp in ("top", "right", "bottom", "left"):
        pp.spines[sp].set_visible(False)
    # Heading below the curve on the left, where the profile has already
    # fallen away. At the top it landed on the jar's own label.
    pp.text(0.02, -300, "PRESSURE ALONG THE LOOP", fontsize=10,
            color=COOL, fontweight="bold", va="center")
    pp.text(0.02, -510, "mm of fluid, mmHg and psi, against the reservoir",
            fontsize=8.5, color=MUTE, va="center")

    fig.text(0.5, 0.950,
             "The flow loop on one page", fontsize=19, ha="center",
             color=INK, fontweight="semibold")
    fig.text(0.5, 0.929,
             "The jar pushes the steady flow. The piston adds the heartbeat. "
             "R1 and R2 decide how much of each reaches the block.",
             fontsize=11.5, ha="center", color=MUTE)

    # ------------------------------------------------------- bottom panels
    # One shared top edge and one shared line pitch, so the three columns
    # read as a row rather than three things that happen to be near each
    # other. The pitch is counted in lines, not in entries.
    PANEL_TOP, LINE, GAP = 0.435, 0.0255, 0.006
    _ends = []

    def panel(x0, title, lines, col=INK, top=PANEL_TOP):
        fig.text(x0, top, title, fontsize=12.5, color=col, fontweight="bold")
        y = top - 0.040
        for t, c in lines:
            fig.text(x0, y, t, fontsize=10.5, color=c, linespacing=1.5,
                     va="top")
            y -= LINE * (1 + t.count("\n")) + GAP
        _ends.append(y)
        return y

    # Every imperial size carries its millimetres. Three bores on one page,
    # two of them named in inches, is exactly the setup for reading "1/4 in"
    # and "3 mm" as the same thing.
    panel(0.030, "WHAT TO BUY", [
        ("THREE BORES, and only three:\n"
         "6.35 mm    the trunk. 3/8 in push-fit tube\n"
         "4.0 mm     R1 only. 1/4 in push-fit tube\n"
         "3.0 mm     the last 150 mm into the block", INK),
        ("Barbed tube is sold by INSIDE diameter, push-fit by\n"
         "OUTSIDE. The 6.35 mm trunk is 3/8 in PUSH-FIT, not\n"
         "1/4. The 1/4 in reel is 4 mm, and that one is R1.", HOT),
        ("Push-fit is the better buy: rigid, hand-assembled\n"
         "for the sweep, LLDPE 5x stiffer than braided PVC.\n"
         "Never silicone, it soaks up the heartbeat.", HOT),
        ("A screw clamp or needle valve for R2, not a ball\n"
         "valve. Two MPX5050GP sensors. A scale.", INK),
    ])

    panel(0.385, "WHERE THE PUSH GOES", [
        ("All of it comes from the jar being 1.2 m up.", MUTE),
    ])
    bar = fig.add_axes((0.385, 0.300, 0.235, 0.055))
    bar.set_xlim(0, 100)
    bar.set_ylim(0, 1)
    bar.axis("off")
    left = 0.0
    for nm, h, c in (("R1", r1_h, HOT), ("R2", r2_h, COOL),
                     ("3 mm run", set_h, GOLD), ("lumen", lum_h, SAND),
                     ("tubing", quarter, MUTE)):
        pct = 100.0 * h / TANK
        bar.barh(0.55, pct, left=left, height=0.52, color=c,
                 edgecolor="white", lw=1.4)
        if pct > 8:
            bar.text(left + pct / 2, 0.55, "%.0f%%" % pct, ha="center",
                     va="center", fontsize=10.5, color="white",
                     fontweight="bold")
        left += pct
    fig.text(0.385, 0.286,
             "R1 65 %    R2 14 %    the 3 mm run 11 %\n"
             "the lumen 6 %    all the rest together 5 %",
             fontsize=10, color=MUTE, va="top", linespacing=1.5)
    fig.text(0.385, 0.222,
             "R1 is big on purpose. It is what stops the\n"
             "heartbeat running back up to the jar. Every\n"
             "point it gives back is a point R2 can use,\n"
             "and R2 is the only thing you can adjust.",
             fontsize=10.5, color=HOT, va="top", linespacing=1.5)

    panel(0.700, "WHAT IT SHOULD DO", [
        ("250 mL a minute through the block, which is\n"
         "60 cm/s in a 3 mm lumen.", INK),
        ("At the piston: 70 mmHg / 1.35 psi at peak,\n"
         "30 mmHg / 0.60 psi between beats.", INK),
        ("60 beats a minute, half a millilitre each.", INK),
    ])
    fig.text(0.700, 0.212, "THE PLENUM IS THE EXPERIMENT", fontsize=12.5,
             color=HOT, fontweight="bold")
    fig.text(0.700, 0.190,
             "A 60 mL syringe standing tip down, open to the\n"
             "loop, with air trapped above the fluid. The\n"
             "plunger stays in and gets CLAMPED so it cannot\n"
             "slide. Move it to set the air: 10 to 50 mL, start\n"
             "at 20, where Greaby landed. Sweeping it against\n"
             "R2 is the deliverable.",
             fontsize=10.5, color=HOT, va="top", linespacing=1.5)

    fig.text(0.5, 0.056,
             "FOUR RULES THAT ARE EASY TO BREAK BY ACCIDENT",
             fontsize=10.5, color=INK, ha="center", fontweight="bold")
    fig.text(0.5, 0.040, va="top",
             s="Nothing tees into the straight 3 mm run or the block.    "
             "The pump only refills the jar and never touches the loop.    "
             "The pump discharges below the surface, or it whips air into "
             "the fluid and air ruins the Doppler.\n"
             "The reservoir's water line sits LEVEL WITH THE BLOCK. The push "
             "is jar surface to reservoir surface, so a bucket on the floor "
             "is not tidying up, it is 60 percent more flow than the drawing "
             "says.",
             fontsize=10, color=MUTE, ha="center", linespacing=1.6)

    # A column that outgrows the page should say so rather than run off it.
    # Adding the bore conversions pushed the buy list past the footer and
    # nothing complained, which is how a drawing ends up with a line nobody
    # can read.
    if min(_ends) < 0.050:
        raise SystemExit("a bottom column ran down to %.3f and the footer is "
                         "at 0.030. Cut a line or two." % min(_ends))

    out = os.path.join(HERE, "loop-one-pager.png")
    fig.savefig(out, facecolor="white")
    print("wrote loop-one-pager.png")
    print("  jar %.0f mm = %.0f mmHg" % (TANK, mmhg(TANK)))
    print("  peak at the piston %.0f mmHg, between beats %.0f mmHg"
          % (peak_mmhg, mmhg(mean_tee)))
    print("  shares: R1 %.0f%%  R2 %.0f%%  3 mm run %.0f%%  lumen %.0f%%  "
          "rest %.0f%%"
          % (100 * r1_h / TANK, 100 * r2_h / TANK, 100 * set_h / TANK,
             100 * lum_h / TANK, 100 * quarter / TANK))


if __name__ == "__main__":
    main()
