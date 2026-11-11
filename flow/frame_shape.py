# -*- coding: utf-8 -*-
"""NOT TAKEN. The frame is not being reprinted, decided 2026-11-11.

This file is kept because the breakdown of where the length goes is worth
having if the frame is ever rebuilt, and because its one real finding stands
on its own: of "wider and shorter", WIDER is the warp fix and SHORTER is not.
Shortening takes length off the numerator and exactly as much first-layer
area off the denominator, so it does nothing for warp at all.

Nothing here is a plan. syringe_drive.FRAME_AS_BUILT pins the printed
geometry and check_drive fails if any of it moves.

Wider and shorter: what the frame's length is actually made of.

    python frame_shape.py   ->  frame-shape.png + the tables below

ABS is on the printer, and a 184 mm unbroken length is where ABS lifts its
corners. So: what can come out of the length, what does it cost, and is the
shape even the thing worth changing.

The honest headline first, because it decides how much of this matters. On an
enclosed machine at a 100 C bed with a brim, a 184 mm ABS part usually
survives. The chamber and the first layer do more for warp than the aspect
ratio does. The shape change below is worth having, it is not a rescue, and
anyone who skips the enclosure and fixes the shape instead has fixed the
wrong thing.
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

import syringe_drive as S

HERE = os.path.dirname(os.path.abspath(__file__))

# name, mm, can it come out, what it costs
PARTS = [
    ("motor wall, coupler, gap", S.X_CARR_MIN, "belt drive only",
     "needs a screw bearing at the motor end, two pulleys and a tensioner"),
    ("TRAVEL", S.TRAVEL, "yes, freely",
     "it is priming headroom. The beat uses %.2f of it" % S.BEAT_MM),
    ("carriage body", S.CARRIAGE_L, "about 6 mm",
     "the LM8UU is 24 mm and sits inside the 30"),
    ("flange gap and rib", S.X_RIB_BACK - S.X_CARR_FRONT, "no",
     "the rib takes the piston's whole reaction"),
    ("saddle for the 66 mm barrel", S.FRAME_SADDLE_L, "yes, some",
     "the collars do the gripping, the saddle only stops it rolling"),
    ("end wall", S.X_END - S.X_SADDLE_END, "no", "it is 6 mm"),
]

# label, travel, saddle, rod spacing
OPTIONS = [
    ("as built, PLA", 45.0, 56.0, 56.0),
    ("travel only", 22.0, 56.0, 56.0),
    ("travel + saddle", 22.0, 44.0, 56.0),
    ("RECOMMENDED", 22.0, 44.0, 76.0),
    ("+ belt drive", 22.0, 44.0, 76.0),
]


def shape(travel, saddle, spacing, belt=False):
    length = (S.X_CARR_MIN + travel + S.CARRIAGE_L
              + (S.X_RIB_BACK - S.X_CARR_FRONT) + saddle
              + (S.X_END - S.X_SADDLE_END))
    if belt:
        length -= S.X_CARR_MIN - 6.0          # motor face wall stays
    width = spacing + S.LM_OD + 10.0
    if belt:
        width += 42.0                          # NEMA 17 alongside
    return length, width


def main():
    A = print
    A("WHERE THE 184 mm GOES")
    A("  %-30s %8s %6s  %-16s %s"
      % ("", "mm", "share", "removable", "what it costs"))
    for nm, mm, can, cost in PARTS:
        A("  %-30s %8.1f %5.0f%%  %-16s %s"
          % (nm, mm, 100.0 * mm / S.X_END, can, cost))
    A("")
    A("  The saddle and the travel are 54 percent of it between them, and")
    A("  both are soft. The coupler stack is another 18 and only a belt")
    A("  takes it out. Everything else is structure.")
    A("")

    A("WHAT EACH OPTION GIVES")
    A("  %-18s %8s %8s %7s %10s %9s"
      % ("", "long", "wide", "aspect", "footprint", "warp idx"))
    base = None
    for lab, t, sd, sp in OPTIONS:
        belt = lab.startswith("+ belt")
        L, W = shape(t, sd, sp, belt=belt)
        area = L * W / 100.0
        idx = L / area
        if base is None:
            base = idx
        A("  %-18s %6.0f mm %6.0f mm %7.2f %7.0f cm2 %9.2f"
          % (lab, L, W, L / W, area, idx))
    A("")
    A("  WARP INDEX is longest dimension over first-layer area, and it is a")
    A("  PROXY, not a prediction. Shrink accumulates along the long axis and")
    A("  the first layer is what holds it down, so lower is better, but the")
    A("  number has no units and no calibration behind it.")
    A("")
    A("  AND IT SAYS SOMETHING I DID NOT EXPECT. The first three rows have")
    A("  the SAME index. Shortening the part takes length off the numerator")
    A("  and takes exactly as much area off the denominator, so on this")
    A("  measure cutting the length buys nothing for warp at all. Only the")
    A("  WIDER row moves it, because width adds area without adding to the")
    A("  axis the shrink accumulates along.")
    A("")
    A("  So of 'wider and shorter', the two halves are doing different jobs.")
    A("  WIDER is the warp fix. SHORTER buys bed room, print time and")
    A("  filament, which are worth having and are not the reason to do it.")
    A("")
    A("  The recommended row is %.0f percent shorter and %.0f percent wider"
      % (100.0 * (1.0 - shape(22.0, 44.0, 76.0)[0] / S.X_END),
         100.0 * (shape(22.0, 44.0, 76.0)[1] / (2 * S.HALF_W) - 1.0)))
    A("  than as built, and takes the warp index down by %.0f percent."
      % (100.0 * (1.0 - (shape(22.0, 44.0, 76.0)[0]
                         / (shape(22.0, 44.0, 76.0)[0]
                            * shape(22.0, 44.0, 76.0)[1] / 100.0))
                  / (S.X_END / (S.X_END * 2 * S.HALF_W / 100.0)))))
    A("")

    A("WHAT IT COSTS")
    A("  TRAVEL 45 to 22 mm. The stroke range goes from %.2f mL to %.2f, and"
      % (45.0 * S.BORE_A / 1000.0, 22.0 * S.BORE_A / 1000.0))
    A("  the beat needs %.3f. What goes is the ability to prime the whole"
      % S.BEAT_ML)
    A("  barrel on the rig: priming moves to filling the syringe by hand")
    A("  before it goes in, which is how it would be done anyway.")
    A("")
    A("  SADDLE 56 to 44 mm. The barrel is 66 mm and the collars grip it; the")
    A("  saddle only stops it rolling and the RIB takes the piston reaction.")
    A("  44 mm still carries two collars with room between them.")
    A("")
    A("  ROD SPACING 56 to 76 mm. Costs nothing but filament and makes the")
    A("  carriage stiffer in yaw by the square of the ratio, %.1fx. It is the"
      % ((76.0 / 56.0) ** 2))
    A("  width that buys the first-layer area.")
    A("")
    A("  AND WHAT IT REALLY COSTS: the frame on the bench is PLA and becomes")
    A("  scrap, the carriage has to be reprinted to match the new rod")
    A("  spacing, and FRAME_SADDLE_L and FRAME_FLANGE_T stop being as-built")
    A("  constants and go back to being design choices. That is four hours")
    A("  of frame plus an hour and a half of carriage.")
    A("")
    A("  THE BELT ROW is there for completeness and I would not do it now.")
    A("  It is the only thing that takes out the coupler stack, and it needs")
    A("  a screw bearing at the motor end, two pulleys and a tensioner, none")
    A("  of which are on the bench. Belt stretch itself is not the problem:")
    A("  at the %.1f N the piston actually works against, a 150 mm span of"
      % (9300.0 * S.BORE_A * 1e-6))
    A("  6 mm GT2 stretches about 2 um, which is half a microstep.")

    # -------------------------------------------------------------- figure
    fig, ax = plt.subplots(figsize=(10.4, 6.4), dpi=170)
    fig.patch.set_facecolor("white")
    cols = ["#8a8a8a", "#c9a22e", "#c9820f", "#2e6fb4", "#b4462e"]
    for (lab, t, sd, sp), c in zip(OPTIONS, cols):
        L, W = shape(t, sd, sp, belt=lab.startswith("+ belt"))
        ax.add_patch(Rectangle((0, 0), L, W, facecolor="none", edgecolor=c,
                               lw=2.2 if lab == "RECOMMENDED" else 1.4,
                               ls="-" if lab in ("as built, PLA", "RECOMMENDED")
                               else "--"))
        # Three of these share a width, so the labels go in a fixed column
        # on the right with a leader, rather than at the corner.
        k = [o[0] for o in OPTIONS].index(lab)
        ly = 150.0 - 13.0 * k
        ax.plot([L, 184.0], [W, ly], color=c, lw=0.7, alpha=0.55)
        ax.text(188.0, ly, "%s   %.0f x %.0f" % (lab, L, W), fontsize=9.5,
                color=c, va="center",
                fontweight="bold" if lab == "RECOMMENDED" else "normal")
    ax.set_xlim(0, 300)
    ax.set_ylim(0, 160)
    ax.set_aspect("equal")
    ax.set_xlabel("mm along the screw")
    ax.set_ylabel("mm across")
    ax.set_title("Frame footprint, to scale\n"
                 "shrink accumulates along the long axis, the first layer "
                 "holds it down", fontsize=11.5)
    ax.grid(alpha=0.25, lw=0.6)
    fig.text(0.5, 0.015,
             "An enclosed chamber and a 100 C bed do more for ABS warp than "
             "any of this. The shape is worth having, it is not the rescue.",
             fontsize=9, color="#555", ha="center")
    fig.tight_layout(rect=(0, 0.035, 1, 1))
    fig.savefig(os.path.join(HERE, "frame-shape.png"), facecolor="white")
    A("")
    A("wrote frame-shape.png")


if __name__ == "__main__":
    main()
