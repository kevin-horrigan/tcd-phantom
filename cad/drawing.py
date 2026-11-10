# -*- coding: utf-8 -*-
"""Dimensioned drawing sheet for the phantom block.

    python drawing.py            ->  cad/phantom-block-drawing.png / .svg
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, Arc
import phantom_block as P

HERE = os.path.dirname(os.path.abspath(__file__))
INK = "#1b1b1b"
CUT = "#9c3b2e"      # cut material
PLATE = "#2d6a8e"    # the removable window plate
FLOW = "#1f7a5c"     # lumen and flow
THIN = 0.8

parts = P.build()
HALF_W, HALF_H = P.WIDTH / 2.0, P.HEIGHT / 2.0


# ------------------------------------------------------------------ drafting
def dim(ax, p0, p1, text, off=0.0, side=1, fs=7.5, rot=None, pad=1.6):
    """Linear dimension between two points, offset perpendicular to the run."""
    p0, p1 = np.array(p0, float), np.array(p1, float)
    v = p1 - p0
    n = np.array([-v[1], v[0]])
    n = n / (np.linalg.norm(n) or 1.0) * off * side
    a, b = p0 + n, p1 + n
    ax.annotate("", a, b, arrowprops=dict(arrowstyle="<|-|>", color=INK,
                                          lw=THIN, shrinkA=0, shrinkB=0,
                                          mutation_scale=7))
    for q, qn in ((p0, a), (p1, b)):
        ax.plot(*zip(q, qn + (qn - q) * 0.12), color=INK, lw=0.5)
    m = (a + b) / 2.0
    u = v / (np.linalg.norm(v) or 1.0)
    if rot is None:
        rot = np.degrees(np.arctan2(v[1], v[0]))
        rot = rot + 180 if abs(rot) > 90 else rot
    ax.text(*(m + np.array([-u[1], u[0]]) * pad * side), text, color=INK,
            fontsize=fs, ha="center", va="center", rotation=rot,
            rotation_mode="anchor")


def leader(ax, pt, tip, text, fs=7.5, ha="left", color=INK):
    ax.annotate(text, xy=tip, xytext=pt, color=color, fontsize=fs, ha=ha,
                va="center", arrowprops=dict(arrowstyle="-", color=color, lw=0.6))


def section(mesh, origin, normal, keep):
    """Cut the mesh and return the outline polylines in the two kept axes."""
    s = mesh.section(plane_origin=origin, plane_normal=normal)
    return [np.c_[e[:, keep[0]], e[:, keep[1]]] for e in s.discrete] if s else []


def draw_poly(ax, loops, color=INK, lw=1.4, fill=None, alpha=1.0, zorder=2):
    for e in loops:
        if fill:
            ax.fill(e[:, 0], e[:, 1], color=fill, alpha=alpha, lw=0, zorder=zorder - 1)
        ax.plot(e[:, 0], e[:, 1], color=color, lw=lw, zorder=zorder)


def face_arc(x_from, x_to, radius, n=200):
    """Points along a face cylinder of the given radius, as (x, y)."""
    x = np.linspace(x_from, x_to, n)
    return np.c_[x, P.R_FACE - np.sqrt(np.maximum(radius ** 2 - x ** 2, 0.0))]


fig = plt.figure(figsize=(15.5, 9.9), dpi=170)
fig.patch.set_facecolor("white")
gs = fig.add_gridspec(2, 2, left=0.045, right=0.985, top=0.895, bottom=0.05,
                      hspace=0.20, wspace=0.13)


def frame(ax, title, sub):
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(title, fontsize=11.5, color=INK, loc="left", pad=22,
                 fontweight="semibold")
    ax.text(0, 1.012, sub, transform=ax.transAxes, fontsize=8.2,
            color="#5a5a5a", va="bottom")


# ------------------------------------------------- A: plan section at z = 0
ax = fig.add_subplot(gs[0, 0])
frame(ax, "A   Plan section at mid height", "looking down, z = 0. Beam enters from the left.")

draw_poly(ax, section(parts["block"], [0, 0, 0], [0, 0, 1], (1, 0)),
          color=CUT, fill="#f0e3e0", zorder=3)
plate = parts["plate_10mm_bone"]
draw_poly(ax, section(plate, [0, 0, 0], [0, 0, 1], (1, 0)),
          color=PLATE, fill="#dde8ef", lw=1.2, zorder=5)

ax.plot([-9, P.DEPTH + 6], [0, 0], color="#888", lw=0.6, ls=(0, (7, 3, 1, 3)))
ax.annotate("", (-3, 0), (-13, 0),
            arrowprops=dict(arrowstyle="-|>", color="#444", lw=1.1, mutation_scale=11))
ax.text(-8, 1.6, "beam", fontsize=7.6, color="#444", ha="center", va="bottom")

dim(ax, (-17, -HALF_W), (-17, HALF_W), "60  ear to eye", off=0, rot=90, pad=2.4)
dim(ax, (0, HALF_W), (P.DEPTH, HALF_W), "100  crown to back", off=14, side=1)
dim(ax, (0, 7), (P.POCKET_T, 7), "10", off=0, side=1, pad=2.8, fs=7)
leader(ax, (76, -34), (P.DEPTH, -HALF_W + 6), "back face, flat", fs=7.5)
leader(ax, (46, 38), (5.84, HALF_W), "face falls back 5.84 at the ear and eye edges",
       fs=7.5)
leader(ax, (78, 12), (P.LUMEN_DEPTH, 0), "lumen at 55 deep, cut obliquely", fs=7.5,
       color=FLOW)
leader(ax, (32, -28), (P.POCKET_T + 0.3, -P.POCKET_W / 2 - 0.3),
       "7.7 of block each side of the pocket", fs=7.2)
ax.set_xlim(-34, 128)
ax.set_ylim(-40, 46)


# --------------------------------------------- B: window face elevation
ax = fig.add_subplot(gs[0, 1])
frame(ax, "B   Window face, looking at the temple", "the 60 x 40 face. Probe sits here.")

ax.add_patch(Rectangle((-HALF_W, -HALF_H), P.WIDTH, P.HEIGHT, fc="#f7f2f1",
                       ec=CUT, lw=1.5, zorder=2))
ax.add_patch(Rectangle((-P.POCKET_W / 2, -HALF_H + P.POCKET_SEAT), P.POCKET_W,
                       P.HEIGHT - P.POCKET_SEAT + 0.1, fc="#dde8ef", ec=PLATE,
                       lw=1.3, zorder=3))
ax.plot([0, 0], [-HALF_H - 3, HALF_H + 3], color=FLOW, lw=1.0, ls=(0, (6, 3, 1, 3)),
        zorder=4)
ax.add_patch(Circle((0, 0), 6.5, fc="none", ec="#444", lw=1.0, ls=(0, (3, 2)), zorder=5))
ax.text(8.5, -0.3, "13 mm probe footprint", fontsize=7.2, color="#444", va="center")

ax.annotate("", (-HALF_W - 6, HALF_H + 13), (-HALF_W - 6, HALF_H - 2),
            arrowprops=dict(arrowstyle="<|-", color=PLATE, lw=1.2, mutation_scale=10))
ax.text(-HALF_W - 8, HALF_H + 7, "plate drops in\nfrom the top",
        color=PLATE, fontsize=7.4, va="center", ha="right")

dim(ax, (-HALF_W, -HALF_H), (HALF_W, -HALF_H), "60", off=9, side=-1)
dim(ax, (HALF_W, -HALF_H), (HALF_W, HALF_H), "40", off=9, side=-1, rot=90)
dim(ax, (-P.POCKET_W / 2, HALF_H), (P.POCKET_W / 2, HALF_H), "44", off=9, side=1)
dim(ax, (-HALF_W - 1, -HALF_H + P.POCKET_SEAT), (-HALF_W - 1, HALF_H),
    "36  plate", off=8, side=1, rot=90)
leader(ax, (HALF_W + 3, -HALF_H + 1.5),
       (P.POCKET_W / 2 - 4, -HALF_H + P.POCKET_SEAT / 2),
       "4 seat, plate bottoms out", fs=7.2)
leader(ax, (-HALF_W + 3, -HALF_H - 6), (-0.5, -HALF_H), "lumen enters here", fs=7.2,
       color=FLOW)
leader(ax, (26, HALF_H + 3.5), (0.5, HALF_H), "and leaves here", fs=7.2, color=FLOW)
ax.set_xlim(-50, 60)
ax.set_ylim(-32, 40)


# ------------------------------------------ C: sagittal section at x = 0
ax = fig.add_subplot(gs[1, 0])
frame(ax, "C   Section on the beam axis", "x = 0, the plane the lumen lies in.")

draw_poly(ax, section(parts["block"], [0, 0, 0], [1, 0, 0], (1, 2)),
          color=CUT, fill="#f0e3e0", zorder=3)
draw_poly(ax, section(plate, [0, 0, 0], [1, 0, 0], (1, 2)),
          color=PLATE, fill="#dde8ef", lw=1.2, zorder=5)
draw_poly(ax, section(P.lumen(P.LUMEN_D / 2.0, overshoot=9.0), [0, 0, 0], [1, 0, 0],
                      (1, 2)), color=FLOW, fill="#d8ece4", lw=1.0, zorder=4)

# the stretch of lumen inside the clinical M1 depth window
for d0, d1 in ((45.0, 65.0),):
    t = (np.array([d0, d1]) - P.LUMEN_DEPTH) / P.AXIS[1]
    pts = P.CENTER + np.outer(t, P.AXIS)
    ax.plot(pts[:, 1], pts[:, 2], color=FLOW, lw=4.5, alpha=0.5, solid_capstyle="butt",
            zorder=6)
    leader(ax, (88, -13), (pts[:, 1].mean(), pts[:, 2].mean()),
           "23 mm of lumen lies between 45\nand 65 mm depth, which is the\nlength of the M1 segment",
           fs=7.2, color=FLOW)

ax.plot([-9, P.DEPTH], [0, 0], color="#888", lw=0.6, ls=(0, (7, 3, 1, 3)), zorder=1)
ax.add_patch(Rectangle((-8.5, -6.5), 8, 13, fc="#e9e9e9", ec="#444", lw=0.9, zorder=4))
ax.text(-10, 8.5, "probe", fontsize=7.4, color="#444", ha="center")
ax.add_patch(Arc((P.LUMEN_DEPTH, 0), 34, 34, theta1=0, theta2=P.LUMEN_ANGLE,
                 color=INK, lw=0.8))
ax.text(P.LUMEN_DEPTH + 20, 4.6, "30 deg", fontsize=7.6, color=INK)

dim(ax, (0, -HALF_H), (P.DEPTH, -HALF_H), "100", off=14, side=-1)
dim(ax, (P.DEPTH, -HALF_H), (P.DEPTH, HALF_H), "40", off=7, side=-1, rot=90)
dim(ax, (P.POCKET_T, HALF_H), (P.LUMEN_DEPTH, HALF_H), "55 to the lumen at mid height",
    off=5, side=1)
leader(ax, (-15, 17), (P.POCKET_T - 1, 11), "10 plate", fs=7.2)
leader(ax, (34, -26), (P.ENTRY[1], P.ENTRY[2]),
       "inlet, 10.1 clear of the pocket floor.\nFill from the bottom so gas sweeps out",
       fs=7.2, color=FLOW)
leader(ax, (52, 30), (P.EXIT[1], P.EXIT[2]), "outlet, 10.4 clear of the back face",
       fs=7.2, color=FLOW)
ax.set_xlim(-20, 132)
ax.set_ylim(-40, 34)


# ------------------------------------------------------ D: the window set
ax = fig.add_subplot(gs[1, 1])
frame(ax, "D   Window plate set, one envelope", "every plate is 10 mm thick, so the face never moves.")

x = 0.0
for t in P.BONE_SET:
    ax.add_patch(Rectangle((x, 0), 13, P.POCKET_T - t, fc="#dde8ef", ec=PLATE, lw=1.0))
    ax.add_patch(Rectangle((x, P.POCKET_T - t), 13, t, fc="#b9c9d4", ec=PLATE, lw=1.0,
                           hatch="///"))
    ax.text(x + 6.5, -1.6, "%g" % t, ha="center", va="top", fontsize=8, color=INK)
    x += 17.0
ax.text(x / 2 - 8.5, -5.4, "bone analog thickness, mm", ha="center", va="top",
        fontsize=8.2, color=INK)
ax.annotate("", (-4, 0), (-4, P.POCKET_T),
            arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=THIN, mutation_scale=7))
ax.text(-6, P.POCKET_T / 2, "10", rotation=90, ha="center", va="center", fontsize=8)
ax.text(x + 2, P.POCKET_T - 1.2, "bone analog, outer table side", fontsize=7.6,
        color=INK, va="center")
ax.text(x + 2, 2.2, "backing cast in the brain formulation,\nso the stack stays bone then brain\nwith no air and no change in depth",
        fontsize=7.6, color=PLATE, va="center")
ax.annotate("", (x - 13, 13.5), (0, 13.5),
            arrowprops=dict(arrowstyle="-", color="#888", lw=0.7))
ax.text((x - 13) / 2, 14.4, "probe side, curved on R80 to match the block face",
        fontsize=7.6, color="#555", ha="center", va="bottom")
ax.set_xlim(-14, x + 70)
ax.set_ylim(-14, 24)


fig.text(0.045, 0.975, "TCD phantom block, Group 1", fontsize=15, color=INK,
         fontweight="semibold")
fig.text(0.045, 0.952,
         "All dimensions mm.  Block 60 ear to eye x 40 tall x 100 deep, temporal face "
         "on R80, top loading window plate, 3 mm wall-less lumen at 30 deg to the beam.",
         fontsize=8.6, color="#555")
fig.text(0.985, 0.975, "2026-10-30   rev A   parametric, cad/phantom_block.py",
         fontsize=8, color="#777", ha="right")

for ext in ("png", "svg"):
    fig.savefig(os.path.join(HERE, "phantom-block-drawing." + ext),
                facecolor="white")
print("wrote phantom-block-drawing.png / .svg")
