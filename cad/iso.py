# -*- coding: utf-8 -*-
"""Shaded isometric of the block, with the window plate lifted out.

    python iso.py       ->  cad/phantom-block-iso.png
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import phantom_block as P

HERE = os.path.dirname(os.path.abspath(__file__))
LIGHT = np.array([0.45, -0.75, 0.55])
LIGHT = LIGHT / np.linalg.norm(LIGHT)


def eye(elev, azim):
    """Unit vector from the scene toward the camera, matplotlib convention."""
    e, a = np.radians(elev), np.radians(azim)
    return np.array([np.cos(e) * np.cos(a), np.cos(e) * np.sin(a), np.sin(e)])


def shade(ax, mesh, base, view, alpha=1.0, zbias=0.0):
    """Flat-shade a mesh by face normal, sorted back to front for this camera."""
    keep = mesh.face_normals @ view > 0.0              # cull the back faces
    tri, nrm = mesh.triangles[keep], mesh.face_normals[keep]
    lam = 0.35 + 0.65 * np.clip(nrm @ LIGHT, 0.0, 1.0)
    rgb = np.clip(np.array(base)[None, :] * lam[:, None], 0, 1)
    order = np.argsort(tri.mean(axis=1) @ view)        # far faces drawn first
    col = Poly3DCollection(tri[order], facecolors=rgb[order], alpha=alpha,
                           edgecolors=rgb[order], linewidths=0.35, shade=False)
    col.set_sort_zpos(zbias)
    ax.add_collection3d(col)


def main():
    parts = P.build()
    fig = plt.figure(figsize=(12.5, 6.6), dpi=170)
    fig.patch.set_facecolor("white")

    for i, (elev, azim, title, sub) in enumerate((
        (20, -58, "Assembled", "window plate seated, probe side toward the viewer"),
        (20, -58, "Plate lifted out", "the plate leaves straight up, so the pocket is a "
                                      "simple vertical channel"),
    )):
        ax = fig.add_subplot(1, 2, i + 1, projection="3d", computed_zorder=False)
        view = eye(elev, azim)
        shade(ax, parts["block"], (0.80, 0.73, 0.70), view, zbias=0)
        lift = 0.0 if i == 0 else 34.0
        plate = parts["plate_4mm_bone"].copy().apply_translation((0, 0, lift))
        back = parts["plate_4mm_backing"].copy().apply_translation((0, 0, lift))
        shade(ax, back, (0.62, 0.76, 0.86), view, zbias=60)
        shade(ax, plate, (0.30, 0.46, 0.60), view, zbias=61)
        lum = P.lumen(P.LUMEN_D / 2.0, overshoot=9.0)
        shade(ax, lum, (0.15, 0.62, 0.45), view, alpha=0.7, zbias=120)

        ax.set_box_aspect((P.WIDTH, P.DEPTH, P.HEIGHT + 34.0))
        ax.set_xlim(-32, 32)
        ax.set_ylim(-4, 102)
        ax.set_zlim(-30, 44)
        ax.view_init(elev=elev, azim=azim)
        ax.set_axis_off()
        ax.set_title(title, fontsize=11.5, color="#1b1b1b", fontweight="semibold",
                     y=0.985)
        ax.text2D(0.5, 0.882, sub, transform=ax.transAxes, fontsize=8.2,
                  color="#5a5a5a", ha="center")

    fig.text(0.5, 0.055,
             "Block 60 ear to eye x 40 tall x 100 deep, temporal face on R80.  "
             "Plate shown is the 4 mm bone analog with its brain-formulation backing.",
             fontsize=8.4, color="#555", ha="center")
    fig.text(0.5, 0.025,
             "The 3 mm lumen runs bottom to top at 30 deg off the beam axis and is "
             "drawn through the material.",
             fontsize=8.4, color="#555", ha="center")
    fig.subplots_adjust(left=0.0, right=1.0, top=1.0, bottom=0.08, wspace=0.0)
    fig.savefig(os.path.join(HERE, "phantom-block-iso.png"), facecolor="white")
    print("wrote phantom-block-iso.png")


if __name__ == "__main__":
    main()
