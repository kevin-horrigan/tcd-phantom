# -*- coding: utf-8 -*-
"""What goes on the bed, in the orientation it goes on in.

    python print_plate.py   ->  print-plate.png

The assembly render in check_drive.py shows how the thing works. This shows
what you actually hand the slicer, which is a different question and the one
that decides whether a part needs supports. Every part here is rotated to the
orientation named in syringe_drive's PRINT NOTES, then dropped onto z = 0, so
the footprints and heights printed are the real ones.

Why each part sits the way it does:

    frame       on its baseplate. The barrel saddle, the rib slot and the
                608 pocket all open upward or sideways, so nothing overhangs.
    carriage    on its -X face, which puts the T8 nut counterbore in the
                first layer. Any other orientation bridges that counterbore.
    saddle_cap  half-round opening UP. As modeled it opens down, which would
                print the clamping surface in mid-air.
    collar      standing on one end so the bore is vertical. A ring printed
                on its side is an unsupported arch and goes oval.

Bed is drawn at 220 x 220, the common Ender-class size. The frame is the only
part that cares, and it fits with room to spare.
"""
import os
import numpy as np
import trimesh
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.patches import Rectangle
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

import syringe_drive as S

HERE = os.path.dirname(os.path.abspath(__file__))
BED = 220.0
GAP = 16.0           # wide enough that a row's labels clear the row below
LIGHT = np.array([0.45, -0.75, 0.55])
LIGHT = LIGHT / np.linalg.norm(LIGHT)

# name, rotation as (angle_deg, axis), colour
ORIENT = [
    ("frame",      (0.0, "x"), (0.80, 0.76, 0.72)),
    ("carriage",   (90.0, "y"), (0.30, 0.46, 0.60)),
    ("saddle_cap", (180.0, "x"), (0.62, 0.58, 0.52)),
    ("collar",     (90.0, "y"), (0.55, 0.42, 0.30)),
]
AXES = {"x": (1, 0, 0), "y": (0, 1, 0), "z": (0, 0, 1)}


def oriented(mesh, angle, axis):
    """Rotate, then drop so the lowest point is exactly on the bed."""
    m = mesh.copy()
    if angle:
        m.apply_transform(trimesh.transformations.rotation_matrix(
            np.radians(angle), AXES[axis]))
    lo = m.bounds[0]
    m.apply_translation((-lo[0], -lo[1], -lo[2]))
    return m


def shade(ax, mesh, base, view):
    keep = mesh.face_normals @ view > 0.0
    tri, nrm = mesh.triangles[keep], mesh.face_normals[keep]
    lam = 0.35 + 0.65 * np.clip(nrm @ LIGHT, 0.0, 1.0)
    rgb = np.clip(np.array(base)[None, :] * lam[:, None], 0, 1)
    order = np.argsort(tri.mean(axis=1) @ view)
    ax.add_collection3d(Poly3DCollection(
        tri[order], facecolors=rgb[order], edgecolors=rgb[order],
        linewidths=0.3, shade=False))


def main():
    parts = S.build()

    # Shelf packing, tallest first by the order given. A single row overflows
    # a 220 bed as soon as the 182 mm frame is on it, so wrap.
    queue = []
    for name, (ang, axis), col in ORIENT:
        n = 2 if name == "collar" else 1          # two collars needed
        for _ in range(n):
            queue.append((name, oriented(parts[name], ang, axis), col))

    laid, x, y, row_h = [], GAP, GAP, 0.0
    for name, m, col in queue:
        w, d = m.extents[0], m.extents[1]
        if x + w + GAP > BED and laid:
            x, y, row_h = GAP, y + row_h + GAP, 0.0
        q = m.copy()
        q.apply_translation((x, y, 0.0))
        laid.append((name, q, col))
        x += w + GAP
        row_h = max(row_h, d)

    fig = plt.figure(figsize=(13.0, 7.4), dpi=170)
    fig.patch.set_facecolor("white")

    # ---------------------------------------------------------- bed plan
    ax = fig.add_subplot(1, 2, 1)
    ax.add_patch(Rectangle((0, 0), BED, BED, facecolor=(0.96, 0.96, 0.97),
                           edgecolor=(0.55, 0.55, 0.60), lw=1.2, zorder=0))
    for name, m, col in laid:
        # true silhouette, not the bounding box: the triangles projected flat
        ax.add_collection(PolyCollection(
            m.triangles[:, :, :2], facecolors=[col + (0.55,)],
            edgecolors="none", zorder=2))
        b = m.bounds
        ax.add_patch(Rectangle((b[0][0], b[0][1]), *(b[1] - b[0])[:2],
                               facecolor="none", edgecolor=(0.35, 0.35, 0.4),
                               lw=0.7, ls=(0, (3, 2)), zorder=3))
        # Name only. The sizes are on the thumbnails beside this, and
        # repeating them here is what made the collar labels run together.
        ax.text((b[0][0] + b[1][0]) / 2, b[1][1] + 2.5, name,
                ha="center", va="bottom", fontsize=7.8, zorder=4)
    ax.set_xlim(-10, BED + 10)
    ax.set_ylim(-10, BED + 10)
    ax.set_aspect("equal")
    ax.set_title("Bed plan, %.0f x %.0f mm, looking down" % (BED, BED),
                 fontsize=9.5)
    ax.set_xlabel("mm")
    ax.set_ylabel("mm")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)

    # -------------------------------------------------- per part isometrics
    e, a = np.radians(24.0), np.radians(-58.0)
    view = np.array([np.cos(e) * np.cos(a), np.cos(e) * np.sin(a), np.sin(e)])
    seen = []
    for name, (ang, axis), col in ORIENT:
        m = oriented(parts[name], ang, axis)
        seen.append((name, m, col))
    for i, (name, m, col) in enumerate(seen):
        bx = fig.add_subplot(4, 2, 2 * i + 2, projection="3d")
        shade(bx, m, col, view)
        ext = m.extents
        r = max(ext) / 2.0
        c = m.bounds.mean(axis=0)
        for setter, v in ((bx.set_xlim, c[0]), (bx.set_ylim, c[1]),
                          (bx.set_zlim, c[2])):
            setter(v - r, v + r)
        bx.set_axis_off()
        bx.view_init(elev=24, azim=-58)
        bx.set_title("%s   %.0f x %.0f x %.0f mm   %.1f mL"
                     % (name, ext[0], ext[1], ext[2], m.volume / 1000.0),
                     fontsize=8.0, pad=-2)

    fig.suptitle("Syringe drive, print orientations. Nothing here needs "
                 "supports.", fontsize=10.5, y=0.985)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    out = os.path.join(HERE, "print-plate.png")
    fig.savefig(out, facecolor="white")
    print("wrote %s" % out)

    total = sum(m.volume for _, m, _ in laid) / 1000.0
    print("\n%-12s %-22s %8s  %s" % ("part", "footprint x height", "mL", "note"))
    for name, m, _ in laid:
        ext = m.extents
        print("%-12s %5.0f x %3.0f x %3.0f mm %8.1f" %
              (name, ext[0], ext[1], ext[2], m.volume / 1000.0))
    print("%-12s %22s %8.1f  one plate, %d parts"
          % ("TOTAL", "", total, len(laid)))
    widest = max(m.bounds[1][0] for _, m, _ in laid)
    deepest = max(m.bounds[1][1] for _, m, _ in laid)
    fits = widest <= BED and deepest <= BED
    print("\nlaid out %.0f x %.0f mm on a %.0f mm bed, %s"
          % (widest, deepest, BED, "fits" if fits else "DOES NOT FIT"))
    # Split by what each part needs measured, not by what fits.
    FREE = ("frame", "saddle_cap")                 # no syringe dimension at all
    GATED = {"collar": "barrel OD",
             "carriage": "disc dia, disc thickness, plunger rod dia"}
    v = {n: parts[n].volume / 1000.0 for n in parts}
    n_free = sum(v[n] for n in FREE)
    print("\nTwo plates, split by what has to be measured first.\n")
    print("  PLATE 1, start now. Nothing here depends on the syringe.")
    for n in FREE:
        print("    %-11s x1   %6.1f mL" % (n, v[n]))
    print("    %-11s      %6.1f mL" % ("", n_free))
    print("\n  PLATE 2, after the calipers. %.1f mL total." % (total - n_free))
    for n, need in GATED.items():
        k = 2 if n == "collar" else 1
        print("    %-11s x%d   %6.1f mL   needs %s" % (n, k, v[n] * k, need))
    print("\nThe frame is %.0f%% of the filament and the long print. It is also"
          % (v["frame"] / total * 100.0))
    print("the one part that cannot be scrapped by a wrong guess, which is why")
    print("the barrel OD was moved out of it and into the collars.")


if __name__ == "__main__":
    main()
