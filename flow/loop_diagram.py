# -*- coding: utf-8 -*-
"""The whole loop, header tank to head, with bores, lengths and fittings.

    python loop_diagram.py   ->  loop-diagram.png

A schematic, not a scale drawing: 622 mm of elevation and a 3 mm bore cannot
share one scale. VERTICAL is to scale in millimetres, because elevation is
what drives the loop and the standpipe heights mean nothing without it.
HORIZONTAL is arrangement only. Line WIDTH encodes bore, so the step down
into the phantom is visible rather than merely stated.

Runs are ballooned A to I on the drawing and specified in the table below it.
Callouts on the drawing are two lines each and the prose lives in the table,
because the first two attempts put every spec inline and the labels ate each
other. A drawing that needs a magnifying glass has not been drawn yet.

Every length and bore is read out of head_budget.SEGMENTS by name, and the
names are checked at import, so this picture cannot quietly disagree with the
budget it is drawn from.
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle

import head_budget as H
import syringe_drive as S

HERE = os.path.dirname(os.path.abspath(__file__))
TANK_MM = 622.0
CRACK_MM = 50.8                       # Qosina 91050
Q = H.q_si(H.Q_MEAN)

SEG = {n: (L, d) for n, L, d in H.SEGMENTS}

RUNS = [
    ("A", "feed tube, reservoir to valve", "header tank to check valve",
     "material free. The check valve keeps the pulse out of this leg"),
    ("B", "check valve port", "through the check valve",
     "Qosina 91050 internal port. Its cracking pressure is the real cost"),
    ("C", "valve to piston tee", "check valve to piston tee",
     "material free, still upstream of the pulse"),
    ("D", "tee to 3 mm transition", "piston tee to reducing barb",
     "BRAIDED PVC OR TYGON, NEVER SILICONE. Route it as short as you can"),
    ("E", "settling run, 3 mm", "reducing barb to inlet fitting",
     "stiff walled. 150 mm and no more: 8.4 mm of tank height per 10 mm"),
    ("F", "phantom lumen", "inlet fitting to outlet fitting",
     "GROUP 1. Wall-less, cast in TMM. The device under test"),
    ("G", "phantom to plenum", "outlet fitting to compliance plenum",
     "material free, downstream of everything that matters"),
    ("H", "plenum to constriction", "plenum to the constriction",
     "material free"),
    ("I", "return to reservoir", "constriction back to the tank",
     "material free. Break it here for the gravimetric catch"),
]
missing = [n for _r, n, _w, _m in RUNS if n not in SEG]
if missing:
    raise SystemExit("head_budget.SEGMENTS no longer has: %s\n"
                     "This drawing is built from those names. Fix one or the "
                     "other, do not let them drift apart." % ", ".join(missing))

INK, MUTE, HOT, COOL, GOLD = "#1b1b1b", "#6f6f6f", "#b4462e", "#2e6fb4", "#b8790b"
PURPLE, SAND = "#6b4aa0", "#8a7452"

X_TANK, X_DROP = 0.26, 0.80
X_RELIEF, X_CV0, X_CV1 = 1.34, 1.72, 2.20
X_TEE, X_RED = 3.20, 4.38
X_TAP, X_MANO = 4.80, 5.24
X_IN, X_OUT = 5.68, 6.94
X_PLEN, X_CON, X_RET = 7.94, 8.94, 9.72


def lw(bore):
    return 1.6 + 1.05 * bore


def head(name):
    L, d = SEG[name]
    return H.head_mm(H.r_poiseuille(L, d) * Q)


def bore_label(d):
    return {6.35: "1/4 in", 3.30: "0.13 in", 3.00: "3.0 mm"}.get(
        d, "%.2f mm" % d)


def main():
    plumb = sum(head(n) for _r, n, _w, _m in RUNS)
    con_mm = TANK_MM - CRACK_MM - plumb

    fig = plt.figure(figsize=(16.8, 13.6), dpi=155)
    fig.patch.set_facecolor("white")
    ax = fig.add_axes((0.012, 0.472, 0.976, 0.470))
    tb = fig.add_axes((0.012, 0.012, 0.976, 0.448))
    ax.axis("off")
    tb.axis("off")
    Y = 0.0

    def pipe(x0, x1, bore, y=Y, col=INK, z=3):
        ax.plot([x0, x1], [y, y], color=col, lw=lw(bore),
                solid_capstyle="butt", zorder=z)

    def vpipe(x, y0, y1, bore, col=INK, z=3):
        ax.plot([x, x], [y0, y1], color=col, lw=lw(bore),
                solid_capstyle="butt", zorder=z)

    def callout(x, y, head_line, sub, col, ha="center", to=None):
        """Two lines, always. Anything longer belongs in the table."""
        if to is not None:
            ax.plot([x, to[0]], [y - 30, to[1]], color=col, lw=0.7, alpha=0.5,
                    zorder=2)
        ax.text(x, y, head_line + "\n" + sub, ha=ha, va="top", fontsize=8.6,
                color=col, zorder=12, linespacing=1.5)

    def balloon(x, ref, y=-62):
        # A Circle patch goes elliptical here because the axes aspect is not
        # equal, so the marker is drawn by the text's own bbox instead.
        ax.text(x, y, ref, ha="center", va="center", fontsize=8.6, color=INK,
                fontweight="bold", zorder=12,
                bbox=dict(boxstyle="circle,pad=0.32", facecolor="white",
                          edgecolor=INK, linewidth=1.2))

    # --------------------------------------------------- Group 1 territory
    ax.add_patch(Rectangle((X_IN, -250), X_OUT - X_IN, 1030, facecolor="#f4efe6",
                           edgecolor="none", zorder=0))
    for xb in (X_IN, X_OUT):
        ax.plot([xb, xb], [-250, 756], color="#c3b49a", lw=1.2, ls="--", zorder=1)
    ax.text((X_IN + X_OUT) / 2, 762, "GROUP 1", ha="center", va="bottom",
            fontsize=11.5, color=SAND, fontweight="bold", zorder=12)
    ax.text(X_IN - 0.16, 762, "GROUP 2", ha="right", va="bottom", fontsize=11.5,
            color="#6b7a8a", fontweight="bold", zorder=12)

    # ------------------------------------------------------------- tank
    ax.add_patch(FancyBboxPatch((X_TANK, TANK_MM), 0.76, 86,
                                boxstyle="round,pad=0.01", facecolor="#dce7f2",
                                edgecolor=COOL, lw=1.6, zorder=4))
    ax.plot([X_TANK + 0.04, X_TANK + 0.72], [TANK_MM + 62, TANK_MM + 62],
            color=COOL, lw=1.4, zorder=5)
    ax.text(X_TANK + 0.38, TANK_MM + 30, "HEADER TANK\nopen to air",
            ha="center", va="center", fontsize=9, color=INK, zorder=12)

    vpipe(X_DROP, TANK_MM, Y, 6.35, col=COOL)
    pipe(X_DROP, X_CV0, 6.35, col=COOL)
    balloon(X_DROP + 0.32, "A")
    ax.annotate("", xy=(0.11, Y), xytext=(0.11, TANK_MM),
                arrowprops=dict(arrowstyle="<->", color=COOL, lw=1.4))
    ax.text(0.17, TANK_MM / 2, "%.0f mm\nof head.\nIt sets the\nMEAN flow"
            % TANK_MM, fontsize=9.5, color=COOL, va="center", zorder=12,
            linespacing=1.5)

    # -------------------------------------------------- relief standpipe
    vpipe(X_RELIEF, Y, 700, 6.35, col=GOLD)
    ax.plot([X_RELIEF - 0.06, X_RELIEF + 0.06], [700, 700], color=GOLD, lw=2.2)
    callout(X_RELIEF + 0.13, 700, "OPEN STANDPIPE  (relief)",
            "upstream of the check valve", GOLD, ha="left")

    # ------------------------------------------------------- check valve
    ax.add_patch(Rectangle((X_CV0, -26), X_CV1 - X_CV0, 52, facecolor="white",
                           edgecolor=HOT, lw=1.8, zorder=5))
    ax.plot([X_CV0 + 0.07, X_CV1 - 0.07, X_CV0 + 0.07], [-19, 0, 19],
            color=HOT, lw=1.6, zorder=6)
    ax.plot([X_CV1 - 0.07, X_CV1 - 0.07], [-19, 19], color=HOT, lw=2.4, zorder=6)
    balloon((X_CV0 + X_CV1) / 2, "B", y=72)
    callout(1.42, 545, "CHECK VALVE", "Qosina 91050, 0.075 psi", HOT,
            ha="left", to=((X_CV0 + X_CV1) / 2, 104))

    # ------------------------------------------------------ piston branch
    pipe(X_CV1, X_TEE, 6.35)
    balloon((X_CV1 + X_TEE) / 2, "C")
    vpipe(X_TEE, -120, Y, 6.35, col=HOT)
    ax.add_patch(Circle((X_TEE, Y), 0.040, facecolor=INK, edgecolor="none",
                        zorder=7))
    ax.add_patch(FancyBboxPatch((X_TEE - 0.76, -230), 1.52, 100,
                                boxstyle="round,pad=0.01", facecolor="#f9e8e3",
                                edgecolor=HOT, lw=1.5, zorder=4))
    ax.text(X_TEE, -180, "PISTON\n5 mL syringe, %.2f mL stroke\n"
            "%.3f uL per microstep, 60 bpm"
            % (S.BEAT_ML, S.SCREW_LEAD / 1600.0 * S.BORE_A),
            ha="center", va="center", fontsize=8.6, color=HOT, zorder=12,
            linespacing=1.5)
    # Left of the drop, not right: balloon D sits on the right at this height.
    ax.text(X_TEE - 0.12, -100, "barb to female luer, 1/4 in", ha="right",
            va="center", fontsize=7.8, color=MUTE, zorder=12)
    callout(X_TEE, 150, "PISTON TEE", "barbed, 1/4 in", INK)

    # ------------------------------------------------ the one stiff stretch
    pipe(X_TEE, X_RED, 6.35, col=HOT)
    balloon((X_TEE + X_RED) / 2 + 0.18, "D")

    # ---------------------------------------------------------- reducer
    ax.plot([X_RED - 0.06, X_RED + 0.06, X_RED + 0.06, X_RED - 0.06],
            [lw(6.35) * 0.9, lw(3.0) * 0.9, -lw(3.0) * 0.9, -lw(6.35) * 0.9],
            color=INK, lw=1.5, zorder=6)
    callout(4.06, 405, "REDUCING BARB  1/4 to 1/8 in",
            "1/8 in is 3.18 mm: it IS the 3 mm barb", INK, ha="center",
            to=(X_RED, 26))

    # ----------------------------------------------------- settling run
    pipe(X_RED, X_IN, 3.00)
    balloon((X_RED + X_IN) / 2 + 0.24, "E")

    # ------------------------------------------------------- transducer
    vpipe(X_TAP, Y, 150, 1.5, col=PURPLE)
    ax.add_patch(Circle((X_TAP, 168), 0.062, facecolor="white",
                        edgecolor=PURPLE, lw=1.8, zorder=6))
    callout(X_TAP - 0.16, 282, "PRESSURE TRANSDUCER",
            "0-20 kPa gauge, 11 Hz", PURPLE, ha="right", to=(X_TAP, 182))

    # -------------------------------------------------------- manometer
    vpipe(X_MANO, Y, 406, 6.35, col=GOLD)
    ax.plot([X_MANO - 0.06, X_MANO + 0.06], [406, 406], color=GOLD, lw=2.2)
    ax.add_patch(Rectangle((X_MANO - 0.030, 30), 0.060, 36, facecolor="white",
                           edgecolor=GOLD, lw=1.5, zorder=6))
    callout(X_MANO + 0.13, 700, "MANOMETER STANDPIPE",
            "fluid stands at 406 mm. Read it with a ruler", GOLD, ha="left",
            to=(X_MANO, 418))

    # --------------------------------------------------------- the head
    ax.add_patch(FancyBboxPatch((X_IN + 0.05, -96), X_OUT - X_IN - 0.10, 192,
                                boxstyle="round,pad=0.01", facecolor="#eadfc8",
                                edgecolor=SAND, lw=1.7, zorder=2))
    pipe(X_IN, X_OUT, 3.00, z=6)
    ax.text((X_IN + X_OUT) / 2, 126, "THE HEAD", ha="center", fontsize=11,
            color="#6b5636", fontweight="semibold", zorder=12)
    ax.text((X_IN + X_OUT) / 2, 102, "cast block, wall-less lumen",
            ha="center", fontsize=8.4, color=SAND, zorder=12)
    for xb in (X_IN, X_OUT):
        ax.add_patch(Rectangle((xb - 0.030, -32), 0.060, 64, facecolor="white",
                               edgecolor=SAND, lw=1.6, zorder=7))
    balloon((X_IN + X_OUT) / 2, "F")
    ax.text((X_IN + X_OUT) / 2, -140,
            "INLET and OUTLET FITTINGS: a joint deliverable.\n"
            "3 mm to 3 mm, no step. Neither team picks them alone.",
            ha="center", va="top", fontsize=8.0, color=SAND, zorder=12,
            linespacing=1.5)

    # -------------------------------------------------------- downstream
    pipe(X_OUT, X_PLEN, 6.35, col=COOL)
    balloon((X_OUT + X_PLEN) / 2, "G")

    vpipe(X_PLEN, Y, 300, 6.35, col=COOL)
    ax.add_patch(Rectangle((X_PLEN - 0.080, 150), 0.16, 164, facecolor="#dce7f2",
                           edgecolor=COOL, lw=1.7, zorder=5))
    ax.plot([X_PLEN - 0.080, X_PLEN + 0.080], [206, 206], color=COOL, lw=1.4,
            zorder=6)
    callout(X_PLEN + 0.16, 700, "COMPLIANCE PLENUM",
            "trapped air over fluid. NOT YET SIZED", HOT, ha="left",
            to=(X_PLEN, 318))

    pipe(X_PLEN, X_CON, 6.35, col=COOL)
    balloon((X_PLEN + X_CON) / 2, "H")

    # ------------------------------------------------------ constriction
    ax.plot([X_CON - 0.080, X_CON, X_CON + 0.080],
            [lw(6.35) * 0.9, 2.0, lw(6.35) * 0.9], color=INK, lw=1.6, zorder=6)
    ax.plot([X_CON - 0.080, X_CON, X_CON + 0.080],
            [-lw(6.35) * 0.9, -2.0, -lw(6.35) * 0.9], color=INK, lw=1.6, zorder=6)
    # Below the line. Either side of it at this height crosses a riser: the
    # plenum's to the left, the return's to the right.
    callout(X_CON, -120, "CONSTRICTION",
            "owns %.0f mm of head" % con_mm, INK, ha="center")

    # ------------------------------------------------------------ return
    pipe(X_CON, X_RET, 6.35, col=COOL)
    balloon((X_CON + X_RET) / 2 + 0.04, "I")
    vpipe(X_RET, Y, 500, 6.35, col=COOL)
    ax.annotate("", xy=(X_RET, 560), xytext=(X_RET, 480),
                arrowprops=dict(arrowstyle="-|>", color=COOL, lw=2.4))
    callout(X_RET + 0.14, 560, "back to the HEADER TANK",
            "break it here for the gravimetric catch", COOL, ha="left")
    callout(X_RET + 0.14, 405, "GRAVIMETRIC CATCH",
            "beaker on a 1 g scale, 60 s = 0.4 %", COOL, ha="left",
            to=(X_RET, 300))

    for x in (1.05, 2.72, 3.90, 5.05, 7.45, 9.30):
        ax.plot([x], [Y], marker=">", ms=7, color="white", zorder=9,
                markeredgecolor="white")

    ax.set_xlim(-0.02, 11.8)
    ax.set_ylim(-250, 790)
    ax.set_title("Header tank to head: bores, lengths and fittings\n"
                 "vertical to scale in mm, horizontal schematic, "
                 "line width proportional to bore", fontsize=13.5, pad=8)

    # -------------------------------------------------------------- table
    tb.set_xlim(0, 1)
    tb.set_ylim(0, 1)
    C_REF, C_RUN, C_WHERE, C_BORE, C_LEN, C_HEAD, C_NOTE = (
        0.010, 0.038, 0.200, 0.330, 0.392, 0.452, 0.515)
    ROW = 0.0355
    y = 0.962
    tb.text(0.0, y + 0.030, "RUNS", fontsize=10.5, color=INK, fontweight="bold")
    for cx, h in ((C_RUN, "run"), (C_WHERE, "where"), (C_BORE, "bore"),
                  (C_LEN, "length"), (C_HEAD, "head"),
                  (C_NOTE, "material and note")):
        tb.text(cx, y, h, fontsize=8.6, color=MUTE, fontweight="semibold")
    tb.plot([0, 1], [y - 0.013, y - 0.013], color="#ccc", lw=1.0)
    y -= ROW + 0.008
    for ref, name, where, mat in RUNS:
        L, d = SEG[name]
        hot = "NEVER SILICONE" in mat
        c = HOT if hot else (SAND if ref == "F" else INK)
        tb.text(C_REF, y, ref, fontsize=8.8, color=c, fontweight="bold")
        tb.text(C_RUN, y, name, fontsize=8.4, color=c)
        tb.text(C_WHERE, y, where, fontsize=8.0, color=MUTE)
        tb.text(C_BORE, y, bore_label(d), fontsize=8.4, color=c,
                fontweight="semibold")
        tb.text(C_LEN, y, "%.0f mm" % L, fontsize=8.4, color=c)
        tb.text(C_HEAD, y, "%.0f mm" % head(name), fontsize=8.4, color=c)
        tb.text(C_NOTE, y, mat, fontsize=8.0, color=HOT if hot else MUTE)
        y -= ROW
    tb.plot([0, 0.50], [y + 0.021, y + 0.021], color="#ccc", lw=1.0)
    for lab, val, bold in (("plumbing total", "%.0f mm" % plumb, False),
                           ("check valve, Qosina 91050", "%.0f mm" % CRACK_MM,
                            False),
                           ("constriction keeps", "%.0f mm" % con_mm, False),
                           ("HEADER TANK ABOVE THE PHANTOM",
                            "%.0f mm" % TANK_MM, True)):
        tb.text(C_RUN, y, lab, fontsize=8.6 if bold else 8.4,
                color=INK if bold else MUTE,
                fontweight="bold" if bold else "normal")
        tb.text(C_HEAD, y, val, fontsize=8.6 if bold else 8.4,
                color=INK if bold else MUTE,
                fontweight="bold" if bold else "normal")
        y -= ROW

    ITEMS = [
        ("check valve", "Qosina 91050, 1/4 in barb, 0.075 psi",
         "or the printed ball check at 2 mm of head, vertical only"),
        ("piston tee", "barbed tee, 1/4 in ID",
         "the pulse enters the loop here"),
        ("luer adapter  x2", "barb to female luer, 1/4 in",
         "the syringe tip is luer, the loop is barbed"),
        ("reducing barb", "1/4 to 1/8 in barb",
         "1/8 in is 3.18 mm, which IS the 3 mm barb"),
        ("relief standpipe", "open tube, upstream of the check valve",
         "a standpipe cannot be the relief inside the pulse path"),
        ("manometer standpipe", "open tube behind 6 mm of 1.0 mm capillary",
         "unthrottled it resonates at 0.89 Hz with the beat"),
        ("pressure transducer", "0-20 kPa gauge, 11 Hz, 110 Hz sampling",
         "0-7 kPa is over range before the pulse even starts"),
        ("compliance plenum", "trapped air over fluid, volume NOT YET SIZED",
         "sets PI. The loop reads 1.55 without it, normal is 0.8 to 1.2"),
        ("constriction", "adjustable, owns %.0f mm of head" % con_mm,
         "the only knob that sets diastolic pressure"),
        ("relief valve", "cracking pressure above 1.8 psi",
         "the piston makes 19 psi at stall against a blocked outlet"),
        ("gravimetric catch", "beaker and a 1 g scale, 60 s catches",
         "0.4 % on the mean flow, better than any inline meter"),
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
        raise SystemExit("the table ran off the bottom: %.3f left. Shrink ROW "
                         "or grow the figure." % y)

    fig.savefig(os.path.join(HERE, "loop-diagram.png"), facecolor="white")
    print("wrote loop-diagram.png  (table ended with %.3f of room to spare)" % y)
    print("  %-34s %8s %7s %9s" % ("segment", "len mm", "bore", "mm head"))
    for ref, n, _w, _m in RUNS:
        L, d = SEG[n]
        print("  %s %-32s %8.0f %7.2f %9.1f" % (ref, n, L, d, head(n)))
    print("  %-34s %8s %7s %9.1f" % ("PLUMBING TOTAL", "", "", plumb))
    print("  %-34s %8s %7s %9.1f" % ("constriction keeps", "", "", con_mm))
    print("  %-34s %8s %7s %9.1f" % ("TANK HEIGHT", "", "", TANK_MM))


if __name__ == "__main__":
    main()
