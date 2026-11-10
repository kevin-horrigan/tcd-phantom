# -*- coding: utf-8 -*-
"""One labelled picture of the whole drive, with every part named.

    python drive_parts.py   ->  drive-parts.png

The check_drive.py render exists to catch interference, and it draws only
what the model builds: the printed parts, the screw and the rods. That left
the two things a person actually looks for, the motor and the syringe,
either absent or unlabelled. This file draws the bought parts too, in their
real sizes and positions, and puts a name on everything.

Colour carries the only distinction that matters when you are standing at the
bench holding a box of parts:

    tan and blue    printed, comes off the bed
    grey and gold   bought, comes out of a bag
    white           the syringe, the one thing that is neither

Geometry comes from syringe_drive at draw time, so this cannot drift from
the model. Nothing here is a separate drawing of the design, it is the design.
"""
import os
import numpy as np
import trimesh
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from mpl_toolkits.mplot3d import proj3d

import syringe_drive as S

HERE = os.path.dirname(os.path.abspath(__file__))
ELEV, AZIM = 20.0, -58.0
LIGHT = np.array([0.45, -0.75, 0.55])
LIGHT = LIGHT / np.linalg.norm(LIGHT)

PRINTED = (0.80, 0.76, 0.72)
CARRIAGE = (0.30, 0.46, 0.60)
COLLAR = (0.55, 0.42, 0.30)
BOUGHT = (0.58, 0.60, 0.64)
SCREW = (0.72, 0.60, 0.25)
GLASS = (0.90, 0.92, 0.94)

# Bought parts the model does not build, drawn here at catalogue size.
COUPLER_D = 19.0                     # 5 to 8 mm flexible coupler, typical OD
SHAFT_D = 5.0                        # pancake output shaft
MOTOR_L = 23.0                       # 17HE08-1004S body length

X_COUPLER = (S.X_MOTOR_BACK, S.X_MOTOR_BACK + S.COUPLER_L)
X_SCREW = (X_COUPLER[1], S.X_RIB + S.BEAR_W)
CARR_AT = S.X_CARR_MIN                       # retracted, leaves the screw visible


def eye(elev, azim):
    e, a = np.radians(elev), np.radians(azim)
    return np.array([np.cos(e) * np.cos(a), np.cos(e) * np.sin(a), np.sin(e)])


def shade(ax, mesh, base, view, alpha=1.0, zbias=0.0):
    keep = mesh.face_normals @ view > 0.0
    tri, nrm = mesh.triangles[keep], mesh.face_normals[keep]
    lam = 0.35 + 0.65 * np.clip(nrm @ LIGHT, 0.0, 1.0)
    rgb = np.clip(np.array(base)[None, :] * lam[:, None], 0, 1)
    order = np.argsort(tri.mean(axis=1) @ view)
    col = Poly3DCollection(tri[order], facecolors=rgb[order], alpha=alpha,
                           edgecolors=rgb[order], linewidths=0.3, shade=False)
    col.set_sort_zpos(zbias)
    ax.add_collection3d(col)


def motor():
    """Pancake body hanging off the -X face of the motor plate, plus shaft."""
    body = S.box((-MOTOR_L, 0.0), (-S.MOTOR_SQ / 2, S.MOTOR_SQ / 2),
                 (S.SCREW_H - S.MOTOR_SQ / 2, S.SCREW_H + S.MOTOR_SQ / 2))
    shaft = S.cyl_x(SHAFT_D / 2, (0.0, X_COUPLER[0] + 10.0), z=S.SCREW_H)
    return body, shaft


def main():
    parts = S.build()
    frame, carr = parts["frame"], parts["carriage"]
    syr = S.syringe()
    body, shaft = motor()

    coupler = S.cyl_x(COUPLER_D / 2, X_COUPLER, z=S.SCREW_H)
    screw = S.cyl_x(4.0, X_SCREW, z=S.SCREW_H)
    rods = [S.cyl_x(S.ROD_D / 2, (0.0, S.X_RIB_BACK), y=dy, z=S.SCREW_H)
            for dy in (-S.ROD_SPACING / 2, S.ROD_SPACING / 2)]

    strap_x = (S.X_RIB_BACK + 8.0, S.X_TIP - 16.0)
    collars = []
    for xs in strap_x:
        c = parts["collar"].copy()
        c.apply_translation((xs + 2.0 - S.COLLAR_L / 2.0, 0.0, S.SYR_H))
        collars.append(c)

    cap = parts["saddle_cap"].copy()
    cap.apply_translation((S.X_RIB_BACK + 6.0, 0.0, S.SYR_H))

    carr_at = carr.copy()
    carr_at.apply_translation((CARR_AT, 0, 0))

    fig = plt.figure(figsize=(14.5, 8.2), dpi=170)
    fig.patch.set_facecolor("white")
    ax = fig.add_subplot(111, projection="3d", computed_zorder=False)
    view = eye(ELEV, AZIM)

    shade(ax, frame, PRINTED, view, zbias=0)
    for r in rods:
        shade(ax, r, BOUGHT, view, zbias=10)
    shade(ax, screw, SCREW, view, zbias=12)
    shade(ax, body, (0.26, 0.28, 0.31), view, zbias=14)
    shade(ax, shaft, BOUGHT, view, zbias=16)
    shade(ax, coupler, (0.45, 0.47, 0.50), view, zbias=18)
    # The carriage and the cap are drawn see-through on purpose. Solid, they
    # hide the two things this picture exists to show: the screw runs through
    # the carriage, and the barrel runs under the cap.
    shade(ax, carr_at, CARRIAGE, view, alpha=0.58, zbias=30)
    shade(ax, syr, GLASS, view, alpha=0.95, zbias=40)
    for c in collars:
        shade(ax, c, COLLAR, view, zbias=50)
    shade(ax, cap, (0.66, 0.62, 0.56), view, alpha=0.45, zbias=55)

    allpts = np.vstack([frame.vertices, syr.vertices, body.vertices,
                        carr_at.vertices])
    lo, hi = allpts.min(axis=0), allpts.max(axis=0)
    c = (lo + hi) / 2.0
    r = (hi - lo).max() / 2.0
    ax.set_xlim(c[0] - r, c[0] + r)
    ax.set_ylim(c[1] - r, c[1] + r)
    ax.set_zlim(c[2] - r * 0.62, c[2] + r * 0.62)
    ax.set_axis_off()
    ax.view_init(elev=ELEV, azim=AZIM)

    # --------------------------------------------------------------- labels
    # Callout slots, not hand-tuned offsets. Every label is parked in a fixed
    # position down one side of the figure and reaches its part with a leader.
    # Hand-placed offsets collided three times in a row while this picture was
    # being built, because moving one part of the model moves every anchor.
    # Slots cannot collide no matter what the geometry does.
    LEFT = [
        ((-MOTOR_L / 2, -S.MOTOR_SQ / 2, S.SCREW_H),
         "NEMA 17 pancake, bought\n17HE08-1004S, 23 mm body"),
        ((S.X_MOTOR_BACK / 2, 0, S.SCREW_H + S.MOTOR_SQ / 2 - 3),
         "motor plate, printed"),
        ((np.mean(X_COUPLER), 0, S.SCREW_H + COUPLER_D / 2),
         "5 to 8 mm flexible coupler, bought"),
        ((np.mean(X_SCREW), 0, S.SCREW_H - 4.0),
         "T8x8 lead screw, bought\nturns, does not slide"),
        ((70.0, -S.ROD_SPACING / 2, S.SCREW_H),
         "8 mm smooth rod x2, bought\nLM8UU bearings inside the carriage"),
    ]
    RIGHT = [
        ((CARR_AT + S.CARRIAGE_L / 2, 0, S.SYR_H + 8.0),
         "carriage, printed\nT8 nut in its back face. This is\n"
         "the part the screw pushes."),
        ((S.X_RIB + S.WALL_T / 2, 0, S.SCREW_H - 12.0),
         "end rib, printed\nholds the 608 bearing"),
        ((S.X_RIB_BACK + 16.0, 0, S.SYR_H + 7.0),
         "saddle cap, printed\nzip ties through the slots"),
        ((S.X_TIP - 10.0, 0, S.SYR_H + S.SYR_BARREL_D / 2),
         "3 mL SYRINGE, bought\nplunger points left, into the carriage"),
        ((strap_x[1] + 2.0, 0, S.SYR_H - S.SADDLE_BORE / 2),
         "collar x2, printed\nthe only part touching the barrel"),
        ((S.X_END - 8.0, S.HALF_W - 5.5, S.BASE_T),
         "shelf holes for the Pico\nand the driver"),
    ]
    proj = ax.get_proj()

    def callout(items, fx, ha, y_hi, y_lo):
        n = len(items)
        for i, ((x, y, z), text) in enumerate(items):
            fy = y_hi - (y_hi - y_lo) * i / float(n - 1 if n > 1 else 1)
            x2, y2, _ = proj3d.proj_transform(x, y, z, proj)
            ax.annotate(text, xy=(x2, y2), xytext=(fx, fy),
                        textcoords="axes fraction",
                        fontsize=8.2, color=(0.15, 0.15, 0.18),
                        linespacing=1.5, ha=ha, va="center",
                        bbox=dict(boxstyle="round,pad=0.3", fc="white",
                                  ec=(0.72, 0.72, 0.76), lw=0.6),
                        arrowprops=dict(arrowstyle="-", lw=0.8,
                                        color=(0.40, 0.40, 0.46),
                                        shrinkA=3, shrinkB=3,
                                        connectionstyle="arc3,rad=0.06"))

    callout(LEFT, -0.02, "right", 0.90, 0.12)
    callout(RIGHT, 1.02, "left", 0.93, 0.09)

    ax.set_title("Syringe drive, every part named.  Tan, blue and brown are "
                 "printed. Everything else is bought.\nMotor turns the screw, "
                 "the screw drives the carriage, the carriage pushes the "
                 "plunger.", fontsize=10.4, pad=-6)
    out = os.path.join(HERE, "drive-parts.png")
    fig.savefig(out, facecolor="white", bbox_inches="tight")
    print("wrote %s" % out)

    print("\nWHAT IS WHAT, left to right along the screw axis")
    for name, x0, x1, src in (
            ("NEMA 17 pancake body", -MOTOR_L, 0.0, "bought"),
            ("motor plate", S.X_MOTOR_FACE, S.X_MOTOR_BACK, "printed"),
            ("flexible coupler", X_COUPLER[0], X_COUPLER[1], "bought"),
            ("lead screw", X_SCREW[0], X_SCREW[1], "bought"),
            ("carriage travel", S.X_CARR_MIN, S.X_CARR_MAX + S.CARRIAGE_L,
             "printed"),
            ("end rib and 608", S.X_RIB, S.X_RIB_BACK, "rib printed"),
            ("syringe barrel", S.X_RIB_BACK, S.X_TIP, "bought"),
            ("collars", strap_x[0], strap_x[1] + S.COLLAR_L, "printed")):
        print("  %-22s X %6.1f to %6.1f   %s" % (name, x0, x1, src))


if __name__ == "__main__":
    main()
