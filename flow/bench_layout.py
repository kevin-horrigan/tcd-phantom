# -*- coding: utf-8 -*-
"""The whole piston station on one sheet: what sits where, and what wires to what.

    python bench_layout.py      ->  bench-layout.png

Top panel is a true side elevation, every coordinate taken from syringe_drive so
it cannot drift from the model. Bottom panel is the electrical setup, not to
scale. Footprints that are known are drawn; the two that are not are marked
nominal rather than guessed.
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch, Circle
import syringe_drive as S

HERE = os.path.dirname(os.path.abspath(__file__))

PRINTED = "#4a6d8c"      # the three printed parts
METAL = "#8d8f93"        # rod, screw, bearing
MOTOR = "#b08c3a"
SYR = "#cfd6dc"
FLUID = "#1f8a70"
PWR = "#c0392b"
GND = "#2b2b2b"
SIG = "#2f6fb0"
INK = "#1b1b1b"
GREY = "#6c6c6c"


def rect(ax, x0, x1, z0, z1, fc, ec=None, lw=0.9, z=2, alpha=1.0):
    ax.add_patch(Rectangle((x0, z0), x1 - x0, z1 - z0, facecolor=fc,
                           edgecolor=ec or INK, linewidth=lw, zorder=z,
                           alpha=alpha))


def dim(ax, x0, x1, z, text):
    ax.annotate("", (x0, z), (x1, z),
                arrowprops=dict(arrowstyle="<->", color=GREY, lw=0.8), zorder=6)
    ax.text((x0 + x1) / 2, z + 1.8, text, ha="center", va="bottom",
            fontsize=7.4, color=GREY, zorder=6)


def tag(ax, x, z, text, tx, tz, color=GREY, size=7.6, ha="left"):
    ax.annotate(text, (x, z), (tx, tz), fontsize=size, color=color, ha=ha,
                va="center", zorder=8, linespacing=1.4,
                arrowprops=dict(arrowstyle="-", color=color, lw=0.6,
                                shrinkA=0, shrinkB=2))


# --------------------------------------------------------------- elevation
def elevation(ax):
    half = S.MOTOR_SQ / 2
    rib_top = 57.0

    ax.plot([-170, S.X_END + 74], [0, 0], color=GREY, lw=1.0, zorder=1)
    ax.text(-170, -7.0, "bench", fontsize=7.2, color=GREY)

    # the loose kit, same bench, to scale where the size is known
    rect(ax, -162, -67, 0, 30, "white", ec=GREY, lw=1.0, z=1)
    ax.text(-114.5, 15, "12 V brick\nnominal, measure yours", ha="center",
            va="center", fontsize=7.2, color=GREY, zorder=3)
    rect(ax, -62, -28, 0, 25, "white", ec=GREY, lw=1.0, z=1)
    tag(ax, -45, 25, "Pico + TMC2209 on the breakout.\n"
                     "Shelf holes are now in the frame,\n"
                     "the shelf itself is not drawn yet.",
        -168, 52)

    # printed frame: baseplate, motor plate, end rib
    rect(ax, S.X_MOTOR_FACE, S.X_END, 0, S.BASE_T, PRINTED)
    rect(ax, S.X_MOTOR_FACE, S.X_MOTOR_BACK, 0, S.SCREW_H + half, PRINTED)
    rect(ax, S.X_RIB, S.X_RIB_BACK, 0, rib_top, PRINTED)

    # pancake motor, hanging off the back of the plate in free air
    rect(ax, -23.0, S.X_MOTOR_FACE, S.SCREW_H - half, S.SCREW_H + half, MOTOR)
    ax.text(-11.5, S.SCREW_H, "17HE08\n1004S", ha="center", va="center",
            fontsize=6.6, color="white", zorder=5, fontweight="bold")

    # coupler, screw, 608
    rect(ax, S.X_MOTOR_BACK, S.X_MOTOR_BACK + S.COUPLER_L,
         S.SCREW_H - 9.5, S.SCREW_H + 9.5, "#5a5a5a")
    rect(ax, S.X_MOTOR_BACK, S.X_RIB_BACK, S.SCREW_H - 4, S.SCREW_H + 4, METAL)
    ax.add_patch(Circle((S.X_RIB + S.WALL_T / 2, S.SCREW_H), S.BEAR_OD / 2,
                        facecolor="#c8cbcf", edgecolor=INK, lw=0.9, zorder=4))

    # carriage: solid retracted, ghosted at full extension
    for x0, a, lbl in ((S.X_CARR_MIN, 1.0, "carriage, retracted"),
                       (S.X_CARR_MAX, 0.22, "fully extended")):
        rect(ax, x0, x0 + S.CARRIAGE_L, S.BASE_T, S.SYR_H + 8.0,
             PRINTED, z=5, alpha=a)
        ax.text(x0 + S.CARRIAGE_L / 2, S.BASE_T + 2.5, lbl, ha="center",
                va="bottom", fontsize=6.6, zorder=9,
                color="white" if a == 1.0 else GREY)

    # syringe: flange butts the rib, barrel through the slot, tip past the end
    rect(ax, S.X_RIB - S.SYR_FLANGE_T, S.X_RIB, S.SYR_H - 10, S.SYR_H + 10, SYR, z=6)
    rect(ax, S.X_RIB - S.SYR_FLANGE_T, S.X_TIP,
         S.SYR_H - S.SYR_BARREL_D / 2, S.SYR_H + S.SYR_BARREL_D / 2, SYR, z=6)
    rect(ax, S.X_TIP, S.X_TIP + 6, S.SYR_H - 2.2, S.SYR_H + 2.2, SYR, z=6)

    # plunger: disc held in the carriage pocket, rod back into the barrel
    xd = S.X_CARR_MIN + S.CARRIAGE_L - S.FRONT_W - S.DISC_T / 2
    rect(ax, xd, S.X_RIB - S.SYR_FLANGE_T, S.SYR_H - S.PLUNGER_ROD_D / 2,
         S.SYR_H + S.PLUNGER_ROD_D / 2, "#9aa6b1", z=7)
    rect(ax, xd - S.DISC_T / 2, xd + S.DISC_T / 2,
         S.SYR_H - S.DISC_D / 2, S.SYR_H + S.DISC_D / 2, "#7f8c99", z=8)

    # fluid: tip to a tee, up to the phantom, down to the gravity feed
    tx, tz = S.X_TIP + 6, S.SYR_H
    ax.plot([tx, tx + 22], [tz, tz], color=FLUID, lw=2.2, zorder=6)
    ax.plot([tx + 22, tx + 22], [tz - 16, tz + 22], color=FLUID, lw=2.2, zorder=6)
    ax.plot([tx + 22, tx + 36], [tz + 22, tz + 22], color=FLUID, lw=2.2, zorder=6)
    ax.plot([tx + 22, tx + 36], [tz - 16, tz - 16], color=FLUID, lw=2.2, zorder=6)
    ax.add_patch(Circle((tx + 22, tz), 2.8, facecolor="white", edgecolor=FLUID,
                        lw=1.6, zorder=7))
    ax.text(tx + 39, tz + 22, "to the phantom", fontsize=7.6, color=FLUID,
            va="center")
    ax.text(tx + 39, tz - 16, "gravity feed\nCHECK VALVE HERE", fontsize=7.6,
            color=FLUID, va="center", linespacing=1.4)

    tag(ax, 0, S.SCREW_H - half, "23 mm body, 180 g,\nhangs in free air",
        -8, -24, ha="right")
    tag(ax, S.X_MOTOR_BACK + 12, S.SCREW_H + 9.5, "5-8 mm flexible coupler",
        -20, 68)
    tag(ax, xd, S.SYR_H + S.DISC_D / 2,
        "closed pocket, so the carriage\npulls as well as pushes", 34, 80)
    tag(ax, S.X_RIB + S.WALL_T / 2, S.SCREW_H + 11, "608 low in the rib", 132, 58)
    tag(ax, S.X_RIB + 3, S.SYR_H + 10, "barrel slot high in the same rib",
        132, 76)

    dim(ax, S.X_CARR_MIN, S.X_CARR_MAX, -12,
        "%.0f mm travel, soft limit %.0f mm, beat uses %.1f mm"
        % (S.TRAVEL, S.SOFT_TRAVEL, S.BEAT_MM))
    dim(ax, S.X_MOTOR_FACE, S.X_END, -30, "printed frame %.0f mm" % S.X_END)

    ax.set_xlim(-172, S.X_END + 100)
    ax.set_ylim(-40, 90)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Side elevation, to scale.  Screw low at %.0f mm, syringe %.0f mm "
                 "above it, one rib carrying both."
                 % (S.SCREW_H, S.SYR_H - S.SCREW_H),
                 fontsize=10.5, color=INK, fontweight="semibold", loc="left")


# ---------------------------------------------------------------- electrical
def wiring(ax):
    def box(x, z, w, h, title, sub):
        ax.add_patch(Rectangle((x, z), w, h, facecolor="white", edgecolor=INK,
                               linewidth=1.1, zorder=3))
        ax.text(x + w / 2, z + h - 0.30, title, ha="center", va="top",
                fontsize=8.6, color=INK, fontweight="semibold", zorder=4)
        ax.text(x + w / 2, z + h - 0.80, sub, ha="center", va="top",
                fontsize=7.0, color=GREY, zorder=4, linespacing=1.5)

    def wire(p0, p1, color, label, off=0.10):
        ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=9,
                                     color=color, lw=1.4, shrinkA=1, shrinkB=1,
                                     zorder=5))
        ax.text((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2 + off, label,
                ha="center", va="bottom" if off >= 0 else "top", fontsize=7.0,
                color=color, zorder=6, linespacing=1.4,
                bbox=dict(fc="white", ec="none", pad=0.6))

    box(0.2, 5.9, 3.0, 1.4, "laptop", "runs the beat profile")
    box(0.2, 2.8, 3.0, 2.0, "Pico", "PIO makes the step train\n11,884 steps/s at 1/8")
    box(0.2, 0.0, 3.0, 1.7, "12 V brick", "5.5 x 2.5 barrel jack\n100 uF at the driver")
    box(5.3, 1.5, 3.3, 3.3, "TMC2209",
        "BTT V1.3, 15.2 x 20.3 mm\nVref 0.53 V = 0.375 A rms\n"
        "MS1 and MS2 open = 1/8")
    box(10.5, 2.8, 2.8, 2.0, "pancake", "17HE08-1004S\n17 Ncm, 4.0 mH")
    box(10.5, 0.0, 2.8, 1.8, "syringe", "0.5 mL per beat\n0.29 uL per step")

    wire((1.7, 5.9), (1.7, 4.8), SIG, "USB")
    wire((3.2, 4.1), (5.3, 4.1), SIG, "GP2 STEP, GP3 DIR, GP4 EN")
    wire((3.2, 3.2), (5.3, 2.9), GND, "3V3 to VCC_IO\nGND to GND")
    wire((3.2, 0.9), (5.3, 1.9), PWR, "VM 12 V", -0.12)
    wire((8.6, 3.6), (10.5, 3.6), PWR, "1A 1B / 2A 2B")
    ax.add_patch(FancyArrowPatch((11.9, 2.8), (11.9, 1.8), arrowstyle="-|>",
                                 mutation_scale=9, color=INK, lw=1.4, zorder=5))
    ax.text(12.1, 2.3, "coupler, screw,\ncarriage, plunger", fontsize=7.0,
            color=INK, va="center", linespacing=1.4)

    ax.text(5.3, 1.15,
            "Meter the coils, do not wire by color: the two motors you bought\n"
            "use different conventions. The two leads reading 3.6 ohm to each\n"
            "other are one coil. One coil on 1A/1B, the other on 2A/2B.",
            fontsize=7.2, color=PWR, va="top", linespacing=1.55)
    ax.text(0.2, 7.8,
            "One ground. The brick negative, the driver GND and the Pico GND are "
            "the same node, or the step pulses ride on a floating reference.",
            fontsize=7.6, color=INK, va="bottom")
    ax.text(10.5, 6.3,
            "The frame now carries two M3 holes\non its +Y edge for a shelf. The\n"
            "shelf needs the breakout measured.",
            fontsize=7.4, color=GREY, va="bottom", linespacing=1.55)

    ax.set_xlim(-0.2, 15.6)
    ax.set_ylim(-0.5, 8.6)
    ax.axis("off")
    ax.set_title("Electrical, not to scale.", fontsize=10.5, color=INK,
                 fontweight="semibold", loc="left")


fig = plt.figure(figsize=(13.4, 9.0), dpi=165)
fig.patch.set_facecolor("white")
elevation(fig.add_axes([0.01, 0.52, 0.98, 0.44]))
wiring(fig.add_axes([0.01, 0.04, 0.98, 0.44]))
fig.text(0.01, 0.004,
         "Elevation coordinates come straight from syringe_drive.py, so the "
         "drawing cannot drift from the model. Brick and breakout footprints "
         "are nominal: measure them before any tray is designed.",
         fontsize=7.6, color=GREY)
out = os.path.join(HERE, "bench-layout.png")
fig.savefig(out, facecolor="white")
print("wrote", out)
