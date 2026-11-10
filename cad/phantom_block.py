# -*- coding: utf-8 -*-
"""Parametric solid model of the TCD phantom block (Group 1).

Block is 60 (ear to eye) x 40 (tall) x 100 (deep) mm. The 60 x 40 face is the
temporal window: it is curved on a vertical axis to approximate the temple, and
it carries a top-loading pocket that accepts an interchangeable skull window
plate. A 3 mm wall-less lumen runs bottom to top at a shallow angle to the
beam axis.

Coordinate system, origin at the crown of the window face, mid-height:
    +x  anterior, ear -> eye      (WIDTH,  60 mm)
    +y  medial, into the head     (DEPTH, 100 mm, also the beam axis)
    +z  superior, up              (HEIGHT, 40 mm)

Writes STL into cad/stl/ and prints a build report.

    python phantom_block.py
"""
import os
import numpy as np
import trimesh

# ---------------------------------------------------------------- parameters
WIDTH = 60.0          # x, ear to eye across the temple
HEIGHT = 40.0         # z, superior to inferior
DEPTH = 100.0         # y, window crown to back face

R_FACE = 80.0         # radius of the curved temple face, axis vertical
POCKET_W = 44.0       # pocket chord width in x
POCKET_T = 10.0       # pocket depth, radial, = window plate thickness
POCKET_SEAT = 4.0     # material left below the pocket, the plate seats on it
FIT = 0.3             # slide clearance, pocket is this much larger per side

LUMEN_D = 3.0         # wall-less MCA lumen diameter
LUMEN_ANGLE = 30.0    # degrees between the lumen axis and the beam axis (+y)
LUMEN_DEPTH = 55.0    # y of the lumen centre at mid-height
CONNECTOR_BURY = 15.0 # buried connector length along the lumen axis, each end

BONE_SET = [2.0, 3.0, 4.0, 6.0, 8.0, 10.0]   # bone-analog thickness per plate

SECTIONS = 256        # facets on the R80/R70 cylinders, 0.006 mm chord error
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stl")

# ------------------------------------------------------------------- helpers
def cyl_z(radius, height, center_xy, sections=SECTIONS):
    """Cylinder with a vertical axis, centred at z = 0."""
    m = trimesh.creation.cylinder(radius=radius, height=height, sections=sections)
    m.apply_translation((center_xy[0], center_xy[1], 0.0))
    return m


def box(xr, yr, zr):
    """Axis-aligned box from (lo, hi) ranges."""
    ext = [hi - lo for lo, hi in (xr, yr, zr)]
    m = trimesh.creation.box(ext)
    m.apply_translation([(lo + hi) / 2.0 for lo, hi in (xr, yr, zr)])
    return m


def diff(a, *b):
    return trimesh.boolean.difference([a, *b], engine="manifold")


def inter(a, *b):
    return trimesh.boolean.intersection([a, *b], engine="manifold")


def sagitta(radius, half_chord):
    """How far the curved face falls back from its crown at half_chord."""
    return radius - np.sqrt(radius ** 2 - half_chord ** 2)


# The face cylinder sits at y = R_FACE so its near surface passes through the
# origin: the crown of the window is at y = 0 and the face falls away in +y.
FACE_CENTER = (0.0, R_FACE)
TALL = HEIGHT * 4   # cylinders overshoot the block and get trimmed


def arc_shell(r_in, r_out, half_w, z_lo, z_hi):
    """The slab of material between two concentric face cylinders."""
    blank = inter(
        box((-half_w, half_w), (-1.0, r_out), (z_lo, z_hi)),
        cyl_z(r_out, TALL, FACE_CENTER),
    )
    return diff(blank, cyl_z(r_in, TALL, FACE_CENTER))


# --------------------------------------------------------------------- lumen
th = np.radians(LUMEN_ANGLE)
AXIS = np.array([0.0, np.cos(th), np.sin(th)])        # unit vector, bottom to top
CENTER = np.array([0.0, LUMEN_DEPTH, 0.0])
HALF_RUN = (HEIGHT / 2.0) / AXIS[2]                   # axial half length, face to face
ENTRY = CENTER - AXIS * HALF_RUN                      # pierces the bottom face
EXIT = CENTER + AXIS * HALF_RUN                       # pierces the top face


def lumen(radius, overshoot=10.0):
    return trimesh.creation.cylinder(
        radius=radius,
        segment=np.vstack([ENTRY - AXIS * overshoot, EXIT + AXIS * overshoot]),
        sections=64,
    )


# --------------------------------------------------------------------- build
def build():
    half_w, half_h = WIDTH / 2.0, HEIGHT / 2.0

    # Block blank: a box with its window face trimmed to the temple radius.
    blank = inter(
        box((-half_w, half_w), (-1.0, DEPTH), (-half_h, half_h)),
        cyl_z(R_FACE, TALL, FACE_CENTER),
    )

    # Pocket: the arc shell, oversize by the slide fit, open at the top.
    pocket = arc_shell(
        R_FACE - POCKET_T - FIT,
        R_FACE + 1.0,
        POCKET_W / 2.0 + FIT,
        -half_h + POCKET_SEAT,
        half_h + 5.0,
    )

    block = diff(blank, pocket, lumen(LUMEN_D / 2.0))

    parts = {"block": block, "lumen_mandrel": lumen(LUMEN_D / 2.0, overshoot=25.0)}

    # Window plates. Every plate has the same 10 mm envelope so the window face
    # and the probe-to-vessel distance never move. Bone analog of thickness t
    # sits on the outside, the balance is a backing of the brain formulation.
    for t in BONE_SET:
        plate = arc_shell(
            R_FACE - POCKET_T, R_FACE, POCKET_W / 2.0, -half_h + POCKET_SEAT, half_h
        )
        tag = ("%g" % t).replace(".", "p")
        parts["plate_%smm_bone" % tag] = inter(plate, diff(
            cyl_z(R_FACE + 1.0, TALL, FACE_CENTER), cyl_z(R_FACE - t, TALL, FACE_CENTER)))
        if t < POCKET_T:
            parts["plate_%smm_backing" % tag] = inter(
                plate, cyl_z(R_FACE - t, TALL, FACE_CENTER))

    return parts


def report(parts):
    block = parts["block"]
    half_w, half_h = WIDTH / 2.0, HEIGHT / 2.0
    edge_sag = sagitta(R_FACE, half_w)
    pocket_sag = sagitta(R_FACE, POCKET_W / 2.0)
    plate = parts["plate_10mm_bone"]

    lines = []
    A = lines.append
    A("BLOCK")
    A("  envelope          %.1f w x %.1f h x %.1f d mm (crown to back)" % (WIDTH, HEIGHT, DEPTH))
    A("  window face       R%.0f mm cylinder, vertical axis" % R_FACE)
    A("  face fall-off     %.2f mm at the ear and eye edges, %.2f mm at the pocket edge"
      % (edge_sag, pocket_sag))
    A("  depth at edges    %.1f mm (the 100 mm is crown to back)" % (DEPTH - edge_sag))
    A("  volume            %.1f mL   watertight %s" % (block.volume / 1000.0, block.is_watertight))
    A("  bounds            x %.1f..%.1f   y %.1f..%.1f   z %.1f..%.1f"
      % tuple(np.ravel(block.bounds.T)))
    A("")
    A("WINDOW POCKET")
    A("  plate envelope    %.1f wide x %.1f tall x %.1f thick, uniform"
      % (POCKET_W, HEIGHT - POCKET_SEAT, POCKET_T))
    A("  slide direction   vertically down from the top face, seats on %.1f mm of block"
      % POCKET_SEAT)
    A("  pocket surfaces   R%.1f floor, R%.1f mouth, concentric with the face"
      % (R_FACE - POCKET_T - FIT, R_FACE))
    A("  clearance         %.1f mm per side   plate volume %.1f mL" % (FIT, plate.volume / 1000.0))
    A("  wall each side    %.1f mm of block between pocket and the ear/eye faces"
      % (half_w - POCKET_W / 2.0 - FIT))
    A("")
    A("LUMEN")
    A("  diameter          %.1f mm, wall-less" % LUMEN_D)
    A("  axis              %.0f deg off the beam axis, in the mid-width plane x = 0" % LUMEN_ANGLE)
    A("  Doppler cosine    %.3f  (uncorrected velocity reads %.0f%% of true)"
      % (np.cos(th), 100 * np.cos(th)))
    A("  entry  (bottom)   x %.1f  y %.1f  z %.1f" % tuple(ENTRY))
    A("  exit   (top)      x %.1f  y %.1f  z %.1f" % tuple(EXIT))
    A("  run in block      %.1f mm axial, %.1f mm of that behind the connectors"
      % (2 * HALF_RUN, 2 * HALF_RUN - 2 * CONNECTOR_BURY))
    A("  clearances        %.1f mm to the pocket floor, %.1f mm to the back face"
      % (ENTRY[1] - (POCKET_T + FIT), DEPTH - EXIT[1]))

    # The stretch of lumen that lies in the clinical M1 depth window.
    for lo, hi in ((45.0, 65.0),):
        t_lo, t_hi = (lo - LUMEN_DEPTH) / AXIS[1], (hi - LUMEN_DEPTH) / AXIS[1]
        A("  depth %.0f-%.0f mm      %.1f mm of lumen, drifting %.1f mm vertically"
          % (lo, hi, t_hi - t_lo, (t_hi - t_lo) * AXIS[2]))
    return "\n".join(lines)


if __name__ == "__main__":
    if not os.path.isdir(OUT):
        os.makedirs(OUT)
    parts = build()
    for name, mesh in sorted(parts.items()):
        mesh.export(os.path.join(OUT, name + ".stl"))
    print(report(parts))
    print("\nwrote %d STL to %s" % (len(parts), OUT))
