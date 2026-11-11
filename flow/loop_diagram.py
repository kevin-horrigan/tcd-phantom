# -*- coding: utf-8 -*-
"""The loop, constant-head jar to head, with bores, lengths and fittings.

    python loop_diagram.py   ->  loop-diagram.png

Topology follows the diagram sent to the teams on 2026-11-10, not the earlier
version of this file. Three things in that diagram were right and this file
was wrong:

  the PLENUM IS UPSTREAM of the phantom, because its job is to round the
    pulse before the Doppler sees it, and downstream of the lumen it would be
    shaping what happens after the measurement;
  there is NO CHECK VALVE, R1 does the blocking instead;
  NOTHING TEES INTO the straight 3 mm run or the block, so the pressure taps
    are P1 at the piston output and P2 after the plenum.

What is newer than that diagram, and deliberately so: a 5 mL barrel rather
than 3 mL, and a leadscrew rather than a crank. The wider bore halved the
screw speed for the same 0.5 mL beat, and the leadscrew makes the waveform
programmable instead of sinusoidal.

A schematic, not a scale drawing. VERTICAL is to scale in millimetres because
elevation drives the loop. HORIZONTAL is arrangement only. Line WIDTH encodes
bore. Runs are ballooned A to I and specified in the table below.

Every length and bore is read out of head_budget.SEGMENTS by name, and the
names are checked at import, so this picture cannot quietly disagree with the
budget it is drawn from.
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
TANK_MM = H.TANK_MM
Q = H.q_si(H.Q_MEAN)

SEG = {n: (L, d) for n, L, d, _z in H.SEGMENTS}

RUNS = [
    ("A", "jar to R1", "constant-head jar down to R1", "1/4 in, material free"),
    ("B", "R1, fixed resistance", "the fixed upstream resistance",
     "%.1f mm bore narrow tubing. A MEASURED LENGTH, cut long and trimmed"
     % H.R1_BORE),
    ("C", "R1 to the piston junction P1", "R1 to where the piston tees in",
     "1/4 in, material free"),
    ("D", "P1 to the plenum", "piston junction to the compliance plenum",
     "BRAIDED PVC OR TYGON, NEVER SILICONE. Carries the raw pulse"),
    ("E", "plenum to the 3 mm transition", "plenum to the reducing barb",
     "stiff walled. Carries the rounded pulse"),
    ("F", "settling run, 3 mm", "reducing barb to the inlet fitting",
     "stiff. 150 mm and no more. NO TEES: it owes the block a developed profile"),
    ("G", "phantom lumen", "inlet fitting to outlet fitting",
     "GROUP 1. Wall-less, cast in TMM. The device under test"),
    ("H", "phantom to R2", "outlet fitting to the adjustable resistance",
     "1/4 in, material free"),
    ("I", "return to reservoir", "R2 down to the reservoir",
     "1/4 in. Break it here for the gravimetric catch"),
]
missing = [n for _r, n, _w, _m in RUNS if n not in SEG]
if missing:
    raise SystemExit("head_budget.SEGMENTS no longer has: %s\n"
                     "This drawing is built from those names. Fix one or the "
                     "other, do not let them drift apart." % ", ".join(missing))

INK, MUTE, HOT, COOL, GOLD = "#1b1b1b", "#6f6f6f", "#b4462e", "#2e6fb4", "#b8790b"
PURPLE, SAND, GREEN = "#6b4aa0", "#8a7452", "#3c7a4a"

X_JAR, X_DROP = 0.30, 1.02
X_R1A, X_R1B = 1.52, 2.32
X_P1, X_PLEN = 3.10, 4.18
X_P2, X_RED = 4.86, 5.30
X_IN, X_OUT = 6.34, 7.58
X_R2, X_RES = 8.56, 9.76
Y_RES = -300.0


def lw(bore):
    return 1.6 + 1.05 * bore


def head(name):
    L, d = SEG[name]
    return H.head_mm(H.r_poiseuille(L, d) * Q)


def bore_label(d):
    return {6.35: "1/4 in", 3.00: "3.0 mm"}.get(d, "%.1f mm" % d)


def main():
    plumb = sum(head(n) for _r, n, _w, _m in RUNS)
    r2_mm = TANK_MM - plumb

    fig = plt.figure(figsize=(16.8, 14.4), dpi=150)
    fig.patch.set_facecolor("white")
    ax = fig.add_axes((0.012, 0.455, 0.976, 0.487))
    tb = fig.add_axes((0.012, 0.012, 0.976, 0.430))
    ax.axis("off")
    tb.axis("off")
    Y = 0.0

    def pipe(x0, x1, bore, y=Y, col=INK, z=3):
        ax.plot([x0, x1], [y, y], color=col, lw=lw(bore),
                solid_capstyle="butt", zorder=z)

    def vpipe(x, y0, y1, bore, col=INK, z=3):
        ax.plot([x, x], [y0, y1], color=col, lw=lw(bore),
                solid_capstyle="butt", zorder=z)

    def callout(x, y, h1, sub, col, ha="center", to=None):
        if to is not None:
            ax.plot([x, to[0]], [y - 54, to[1]], color=col, lw=0.7, alpha=0.5,
                    zorder=2)
        ax.text(x, y, h1 + "\n" + sub, ha=ha, va="top", fontsize=8.6,
                color=col, zorder=12, linespacing=1.5)

    def balloon(x, ref, y=-110):
        ax.text(x, y, ref, ha="center", va="center", fontsize=8.6, color=INK,
                fontweight="bold", zorder=12,
                bbox=dict(boxstyle="circle,pad=0.32", facecolor="white",
                          edgecolor=INK, linewidth=1.2))

    def tap(x, name, col=PURPLE, up=320):
        vpipe(x, Y, up, 1.5, col=col)
        ax.add_patch(Circle((x, up + 22), 0.062, facecolor="white",
                            edgecolor=col, lw=1.8, zorder=6))
        ax.text(x, up + 22, name, ha="center", va="center", fontsize=7.0,
                color=col, fontweight="bold", zorder=13)

    # --------------------------------------------------- Group 1 territory
    ax.add_patch(Rectangle((X_IN, -430), X_OUT - X_IN, 1860, facecolor="#f4efe6",
                           edgecolor="none", zorder=0))
    for xb in (X_IN, X_OUT):
        ax.plot([xb, xb], [-430, 1330], color="#c3b49a", lw=1.2, ls="--",
                zorder=1)
    ax.text((X_IN + X_OUT) / 2, 1340, "GROUP 1", ha="center", va="bottom",
            fontsize=11.5, color=SAND, fontweight="bold", zorder=12)
    ax.text(X_IN - 0.16, 1340, "GROUP 2", ha="right", va="bottom",
            fontsize=11.5, color="#6b7a8a", fontweight="bold", zorder=12)

    # ------------------------------------------------ constant-head jar
    ax.add_patch(FancyBboxPatch((X_JAR, TANK_MM), 0.82, 150,
                                boxstyle="round,pad=0.01", facecolor="#dce7f2",
                                edgecolor=COOL, lw=1.7, zorder=4))
    ax.plot([X_JAR + 0.04, X_JAR + 0.78], [TANK_MM + 104, TANK_MM + 104],
            color=COOL, lw=1.5, zorder=5)
    ax.text(X_JAR + 0.56, TANK_MM + 34, "CONSTANT-HEAD JAR", ha="center",
            va="center", fontsize=8.0, color=INK, zorder=12)
    # On the LEFT of the jar: the feed drop leaves from the right, and the two
    # were landing on top of each other.
    x_ovf = X_JAR + 0.06
    vpipe(x_ovf, TANK_MM - 230, TANK_MM + 118, 5.0, col=GOLD, z=6)
    ax.annotate("", xy=(x_ovf, TANK_MM - 285), xytext=(x_ovf, TANK_MM - 200),
                arrowprops=dict(arrowstyle="-|>", color=GOLD, lw=1.8))
    ax.text(x_ovf + 0.07, TANK_MM - 285, "to the reservoir", ha="left",
            va="center", fontsize=7.6, color=GOLD, zorder=12)
    callout(X_JAR + 1.26, TANK_MM + 192, "OVERFLOW STANDPIPE",
            "its rim pins the level, excess spills to the reservoir,\n"
            "so the head is constant whatever the pump does", GOLD, ha="left")

    vpipe(X_DROP, TANK_MM, Y, 6.35, col=COOL)
    pipe(X_DROP, X_R1A, 6.35, col=COOL)
    balloon(X_DROP + 0.30, "A")
    ax.annotate("", xy=(0.10, Y), xytext=(0.10, TANK_MM),
                arrowprops=dict(arrowstyle="<->", color=COOL, lw=1.4))
    ax.text(0.16, TANK_MM / 2, "%.1f m\nof head.\nIt sets the\nMEAN flow"
            % (TANK_MM / 1000.0), fontsize=9.5, color=COOL, va="center",
            zorder=12, linespacing=1.5)

    # ---------------------------------------------------------------- R1
    r1_L, r1_d = SEG["R1, fixed resistance"]
    xs = np.linspace(X_R1A, X_R1B, 200)
    ax.plot(xs, 34.0 * np.sin((xs - X_R1A) / (X_R1B - X_R1A) * 8 * np.pi),
            color=HOT, lw=lw(r1_d), solid_capstyle="round", zorder=6)
    balloon((X_R1A + X_R1B) / 2, "B")
    callout(2.58, 1130, "R1,  FIXED",
            "%.0f mm of %.1f mm bore tubing, not a valve.\n"
            "It eats %.0f mm of head, and that share IS the\n"
            "share of the pulse that goes the right way"
            % (r1_L, r1_d, head("R1, fixed resistance")), HOT,
            ha="center", to=((X_R1A + X_R1B) / 2, 54))

    # -------------------------------------------------- piston junction P1
    pipe(X_R1B, X_P1, 6.35, col=COOL)
    balloon((X_R1B + X_P1) / 2, "C")
    vpipe(X_P1, -160, Y, 6.35, col=HOT)
    ax.add_patch(Circle((X_P1, Y), 0.040, facecolor=INK, edgecolor="none",
                        zorder=7))
    tap(X_P1, "P1")
    callout(X_P1 - 0.16, 500, "P1,  piston output",
            "the raw pulse, before shaping", PURPLE, ha="right",
            to=(X_P1, 360))
    ax.add_patch(FancyBboxPatch((X_P1 - 0.84, -300), 1.68, 124,
                                boxstyle="round,pad=0.01", facecolor="#f9e8e3",
                                edgecolor=HOT, lw=1.5, zorder=4))
    ax.text(X_P1, -238, "PISTON\n5 mL syringe, %.2f mL per beat\n"
            "%.3f uL per microstep, leadscrew"
            % (S.BEAT_ML, S.SCREW_LEAD / 1600.0 * S.BORE_A),
            ha="center", va="center", fontsize=8.6, color=HOT, zorder=12,
            linespacing=1.5)

    # ------------------------------------------------------------ plenum
    pipe(X_P1, X_PLEN, 6.35, col=HOT)
    balloon((X_P1 + X_PLEN) / 2 + 0.16, "D")
    vpipe(X_PLEN, Y, 300, 6.35, col=COOL)
    ax.add_patch(Rectangle((X_PLEN - 0.085, 150), 0.17, 190, facecolor="#dce7f2",
                           edgecolor=COOL, lw=1.7, zorder=5))
    ax.plot([X_PLEN - 0.085, X_PLEN + 0.085], [226, 226], color=COOL, lw=1.4,
            zorder=6)
    ax.text(X_PLEN, 288, "air", ha="center", va="center", fontsize=7.5,
            color=MUTE, zorder=12)
    callout(X_PLEN, 790, "PLENUM,  rounds the pulse",
            "UPSTREAM of the block, because it shapes what the\n"
            "Doppler sees. Volume NOT YET SIZED, and it is what\n"
            "takes PI from 1.55 down to a normal 0.8 to 1.2", HOT,
            ha="center", to=(X_PLEN, 346))

    # ---------------------------------------------------------------- P2
    pipe(X_PLEN, X_RED, 6.35, col=COOL)
    balloon((X_PLEN + X_RED) / 2, "E")
    tap(X_P2, "P2")
    callout(X_P2 + 0.16, 500, "P2,  the waveform you are shaping",
            "0-20 kPa gauge, 11 Hz, 110 Hz sampling", PURPLE, ha="left",
            to=(X_P2, 360))

    # ---------------------------------------------------------- reducer
    ax.plot([X_RED - 0.06, X_RED + 0.06, X_RED + 0.06, X_RED - 0.06],
            [lw(6.35) * 2.6, lw(3.0) * 2.6, -lw(3.0) * 2.6, -lw(6.35) * 2.6],
            color=INK, lw=1.5, zorder=6)
    callout(X_RED, -252, "REDUCING BARB  1/4 to 1/8 in",
            "1/8 in is 3.18 mm: it IS the 3 mm barb", INK, ha="center",
            to=(X_RED, -22))

    # ----------------------------------------------------- settling run
    pipe(X_RED, X_IN, 3.00)
    balloon((X_RED + X_IN) / 2, "F")

    # --------------------------------------------------------- the head
    ax.add_patch(FancyBboxPatch((X_IN + 0.05, -96), X_OUT - X_IN - 0.10, 192,
                                boxstyle="round,pad=0.01", facecolor="#eadfc8",
                                edgecolor=SAND, lw=1.7, zorder=2))
    pipe(X_IN, X_OUT, 3.00, z=6)
    ax.text((X_IN + X_OUT) / 2, 126, "THE HEAD", ha="center", fontsize=11,
            color="#6b5636", fontweight="semibold", zorder=12)
    ax.text((X_IN + X_OUT) / 2, 100, "cast block, wall-less 3 mm lumen",
            ha="center", fontsize=8.2, color=SAND, zorder=12)
    for xb in (X_IN, X_OUT):
        ax.add_patch(Rectangle((xb - 0.030, -32), 0.060, 64, facecolor="white",
                               edgecolor=SAND, lw=1.6, zorder=7))
    balloon((X_IN + X_OUT) / 2, "G")
    ax.plot([(X_IN + X_OUT) / 2 + 0.24, (X_IN + X_OUT) / 2 + 0.56],
            [96, 330], color=GREEN, lw=2.0, zorder=8)
    callout((X_IN + X_OUT) / 2 + 0.58, 470, "DOPPLER",
            "velocity inside the lumen,\nthe only view into the block", GREEN,
            ha="left")
    ax.text((X_IN + X_OUT) / 2, -160,
            "NO TEES IN THE STRAIGHT RUN OR THE BLOCK\n"
            "inlet and outlet fittings are a joint deliverable, 3 mm to 3 mm",
            ha="center", va="top", fontsize=8.0, color=SAND, zorder=12,
            linespacing=1.5, fontweight="semibold")

    # ------------------------------------------------------------- R2
    pipe(X_OUT, X_R2, 6.35, col=COOL)
    balloon((X_OUT + X_R2) / 2, "H")
    ax.plot([X_R2 - 0.085, X_R2, X_R2 + 0.085],
            [lw(6.35) * 2.6, 6.0, lw(6.35) * 2.6], color=INK, lw=1.6, zorder=6)
    ax.plot([X_R2 - 0.085, X_R2, X_R2 + 0.085],
            [-lw(6.35) * 2.6, -6.0, -lw(6.35) * 2.6], color=INK, lw=1.6,
            zorder=6)
    callout(X_R2 + 0.14, 790, "R2,  ADJUSTABLE",
            "screw clamp or needle valve. The only knob that\n"
            "sets diastolic pressure. It has %.0f mm of the jar\n"
            "left to work with, and R1 is why it is not more"
            % r2_mm, INK, ha="left", to=(X_R2, 44))

    # ------------------------------------------------- reservoir and pump
    pipe(X_R2, X_RES, 6.35, col=COOL)
    balloon((X_R2 + X_RES) / 2, "I")
    vpipe(X_RES, Y_RES + 70, Y, 6.35, col=COOL)
    ax.add_patch(FancyBboxPatch((X_RES - 0.46, Y_RES - 86), 1.42, 156,
                                boxstyle="round,pad=0.01", facecolor="#dce7f2",
                                edgecolor=COOL, lw=1.7, zorder=4))
    ax.plot([X_RES - 0.42, X_RES + 0.92], [Y_RES + 26, Y_RES + 26],
            color=COOL, lw=1.4, zorder=5)
    ax.text(X_RES + 0.25, Y_RES - 26, "RESERVOIR", ha="center", va="center",
            fontsize=9, color=INK, zorder=12)

    # The refill leg is a pump symbol and two arrows rather than two long
    # lines across the sheet. Drawn in full it crossed everything and carried
    # no information: it is a hose from the reservoir back up to the jar.
    x_pump = X_RES - 0.92
    pipe(x_pump, X_RES - 0.46, 6.35, y=Y_RES - 60, col=GREEN, z=3)
    ax.add_patch(Circle((x_pump, Y_RES - 60), 0.19, facecolor="white",
                        edgecolor=GREEN, lw=2.0, zorder=6))
    ax.text(x_pump, Y_RES - 60, "M", ha="center", va="center", fontsize=9,
            color=GREEN, fontweight="bold", zorder=12)
    ax.annotate("", xy=(x_pump - 0.66, Y_RES - 60),
                xytext=(x_pump - 0.22, Y_RES - 60),
                arrowprops=dict(arrowstyle="-|>", color=GREEN, lw=2.0))
    ax.text(x_pump - 0.74, Y_RES - 60, "to the jar", ha="right", va="center",
            fontsize=8.2, color=GREEN, zorder=12)
    ax.annotate("", xy=(X_JAR + 0.86, TANK_MM + 108),
                xytext=(X_JAR + 1.36, TANK_MM + 108),
                arrowprops=dict(arrowstyle="-|>", color=GREEN, lw=2.0))
    ax.text(X_JAR + 1.42, TANK_MM + 108, "from the Omegaflex", ha="left",
            va="center", fontsize=8.2, color=GREEN, zorder=12)
    ax.text(x_pump + 0.26, Y_RES - 120,
            "OMEGAFLEX   lifts %.1f psi against a 20 psi rating.\n"
            "It only refills the jar and never touches the pulse.\n"
            "Discharge below the surface or it aerates the fluid."
            % (H.RHO * H.G * TANK_MM * 1e-3 / H.PSI),
            ha="left", va="top", fontsize=8.4, color=GREEN, zorder=12,
            linespacing=1.5)

    for x in (1.25, 2.72, 3.70, 5.10, 8.05, 9.20):
        ax.plot([x], [Y], marker=">", ms=7, color="white", zorder=9,
                markeredgecolor="white")

    ax.set_xlim(-0.02, 12.3)
    ax.set_ylim(-575, 1440)
    ax.set_title("Constant-head jar to head: bores, lengths and fittings\n"
                 "vertical to scale in mm, horizontal schematic, "
                 "line width proportional to bore", fontsize=13.5, pad=8)

    # -------------------------------------------------------------- table
    tb.set_xlim(0, 1)
    tb.set_ylim(0, 1)
    C_REF, C_RUN, C_WHERE, C_BORE, C_LEN, C_HEAD, C_NOTE = (
        0.010, 0.038, 0.222, 0.352, 0.410, 0.466, 0.527)
    ROW = 0.0342
    y = 0.962
    tb.text(0.0, y + 0.030, "RUNS", fontsize=10.5, color=INK, fontweight="bold")
    for cx, h in ((C_RUN, "run"), (C_WHERE, "where"), (C_BORE, "bore"),
                  (C_LEN, "length"), (C_HEAD, "head used"),
                  (C_NOTE, "material and note")):
        tb.text(cx, y, h, fontsize=8.6, color=MUTE, fontweight="semibold")
    tb.plot([0, 1], [y - 0.013, y - 0.013], color="#ccc", lw=1.0)
    y -= ROW + 0.008
    for ref, name, where, mat in RUNS:
        L, d = SEG[name]
        hot = "NEVER SILICONE" in mat or "MEASURED LENGTH" in mat
        c = HOT if hot else (SAND if ref == "G" else INK)
        tb.text(C_REF, y, ref, fontsize=8.8, color=c, fontweight="bold")
        tb.text(C_RUN, y, name, fontsize=8.4, color=c)
        tb.text(C_WHERE, y, where, fontsize=8.0, color=MUTE)
        tb.text(C_BORE, y, bore_label(d), fontsize=8.4, color=c,
                fontweight="semibold")
        tb.text(C_LEN, y, "%.0f mm" % L, fontsize=8.4, color=c)
        tb.text(C_HEAD, y, "%.0f mm" % head(name), fontsize=8.4, color=c)
        tb.text(C_NOTE, y, mat, fontsize=8.0, color=HOT if hot else MUTE)
        y -= ROW
    tb.text(C_WHERE, y + 0.004,
            "'length' is a length. 'head used' is a PRESSURE written as the "
            "height of fluid that would make it: 1 mm = 10.2 Pa = 0.076 mmHg. "
            "Both columns are millimetres and they are not the same quantity.",
            fontsize=7.6, color=MUTE, style="italic")
    y -= ROW
    tb.plot([0, 0.52], [y + 0.021, y + 0.021], color="#ccc", lw=1.0)
    for lab, val, bold in (("everything above", "%.0f mm" % plumb, False),
                           ("R2 is whatever is left", "%.0f mm" % r2_mm, False),
                           ("CONSTANT-HEAD JAR ABOVE THE PHANTOM",
                            "%.0f mm" % TANK_MM, True)):
        tb.text(C_RUN, y, lab, fontsize=8.6 if bold else 8.4,
                color=INK if bold else MUTE,
                fontweight="bold" if bold else "normal")
        tb.text(C_HEAD, y, val, fontsize=8.6 if bold else 8.4,
                color=INK if bold else MUTE,
                fontweight="bold" if bold else "normal")
        y -= ROW

    cv_gain = (TANK_MM - 50.8 - (plumb - head("R1, fixed resistance"))) / r2_mm
    ITEMS = [
        ("R1", "a measured length of %.1f mm tubing, not a valve" % H.R1_BORE,
         "its share of the head IS the share of the pulse going forward"),
        ("piston junction P1", "barbed tee, 1/4 in ID",
         "the pulse enters the loop here"),
        ("luer adapter  x2", "barb to female luer, 1/4 in",
         "the syringe tip is luer, the loop is barbed"),
        ("plenum", "trapped air over fluid, volume NOT YET SIZED",
         "sets PI. The loop reads 1.55 without it, normal is 0.8 to 1.2"),
        ("reducing barb", "1/4 to 1/8 in barb",
         "1/8 in is 3.18 mm, which IS the 3 mm barb"),
        ("P1 and P2", "0-20 kPa gauge, 11 Hz, 110 Hz sampling",
         "0-7 kPa is over range before the pulse even starts"),
        ("R2", "screw clamp or needle valve",
         "the only knob that sets diastolic pressure"),
        ("overflow standpipe", "on the jar, its rim pins the level",
         "makes the head constant whatever the Omegaflex does"),
        ("Omegaflex", "refill only, discharge below the surface",
         "lifts %.1f psi against a 20 psi rating"
         % (H.RHO * H.G * TANK_MM * 1e-3 / H.PSI)),
        ("relief valve", "cracking pressure above %.1f psi"
         % (2.0 * H.RHO * H.G * TANK_MM * 1e-3 / H.PSI),
         "the piston makes 19 psi at stall against a blocked outlet"),
        ("gravimetric catch", "beaker and a 1 g scale, 60 s catches",
         "0.4 % on the mean flow, better than any inline meter"),
        ("check valve  OPTIONAL", "Qosina 91050, 1/4 in barb, 0.075 psi",
         "could replace R1: ~100 %% forward and %.1fx the range on R2"
         % cv_gain),
    ]
    y -= 0.018
    tb.text(0.0, y, "FITTINGS AND INSTRUMENTS", fontsize=10.5, color=INK,
            fontweight="bold")
    y -= ROW + 0.008
    for nm, sp, note in ITEMS:
        flag = "NOT YET SIZED" in sp
        tb.text(C_RUN, y, nm, fontsize=8.4, color=HOT if flag else INK)
        tb.text(C_WHERE, y, sp, fontsize=8.0, color=HOT if flag else MUTE)
        tb.text(C_NOTE, y, note, fontsize=8.0, color=HOT if flag else MUTE)
        y -= ROW
    if y < -0.02:
        raise SystemExit("the table ran off the bottom: %.3f left." % y)

    fig.savefig(os.path.join(HERE, "loop-diagram.png"), facecolor="white")
    print("wrote loop-diagram.png  (%.3f of table room to spare)" % y)
    print("  %-32s %8s %7s %9s" % ("run", "len mm", "bore", "mm head"))
    for ref, n, _w, _m in RUNS:
        L, d = SEG[n]
        print("  %s %-30s %8.0f %7.2f %9.1f" % (ref, n, L, d, head(n)))
    print("  %-32s %8s %7s %9.1f" % ("everything above", "", "", plumb))
    print("  %-32s %8s %7s %9.1f" % ("R2 gets what is left", "", "", r2_mm))
    print("  %-32s %8s %7s %9.1f" % ("JAR HEIGHT", "", "", TANK_MM))


if __name__ == "__main__":
    main()
