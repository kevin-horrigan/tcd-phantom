# -*- coding: utf-8 -*-
"""Checks on the phantom block model that a volume number alone will not catch.

    python verify.py
"""
import numpy as np
import trimesh
import phantom_block as P

fails = []


def check(name, ok, detail=""):
    print("%-4s %-46s %s" % ("PASS" if ok else "FAIL", name, detail))
    if not ok:
        fails.append(name)


parts = P.build()
block = parts["block"]
plate = parts["plate_10mm_bone"]

for name, mesh in sorted(parts.items()):
    check("watertight: %s" % name, mesh.is_watertight and mesh.volume > 0,
          "%.2f mL" % (mesh.volume / 1000.0))

# Seated plate must not fight the block anywhere.
clash = trimesh.boolean.intersection([block, plate], engine="manifold")
check("seated plate does not interfere with block", clash.volume < 1.0,
      "overlap %.4f mm3" % clash.volume)

# Withdrawing it is pure +z translation, so sweep the plate up and re-check.
sweep = trimesh.util.concatenate([
    plate.copy().apply_translation((0, 0, dz)) for dz in np.linspace(0, 60, 40)])
sweep = trimesh.boolean.union([sweep], engine="manifold")
clash = trimesh.boolean.intersection([block, sweep], engine="manifold")
check("plate slides out the top without binding", clash.volume < 5.0,
      "swept overlap %.3f mm3" % clash.volume)

# Outer face of the plate has to land on the block's own face, not inside it.
check("plate outer face is flush with the window face",
      abs(plate.bounds[0][1] - 0.0) < 1e-6, "plate y_min = %.6f" % plate.bounds[0][1])
check("plate seats at the pocket floor height",
      abs(plate.bounds[0][2] - (-P.HEIGHT / 2 + P.POCKET_SEAT)) < 1e-6,
      "plate z_min = %.3f" % plate.bounds[0][2])

# Uniform thickness is the whole point of a curved plate; sample it radially.
ctr = np.array([P.FACE_CENTER[0], P.FACE_CENTER[1], 0.0])
v = plate.vertices - ctr
r = np.hypot(v[:, 0], v[:, 1])
inner, outer = r[r < P.R_FACE - P.POCKET_T / 2], r[r > P.R_FACE - P.POCKET_T / 2]
check("plate thickness uniform across the arc",
      abs((outer.mean() - inner.mean()) - P.POCKET_T) < 0.02,
      "%.3f mm, spread %.3f" % (outer.mean() - inner.mean(), np.ptp(outer) + np.ptp(inner)))

# Bone pane plus backing must refill the envelope exactly, with no air gap.
for t in P.BONE_SET:
    tag = ("%g" % t).replace(".", "p")
    bone = parts["plate_%smm_bone" % tag]
    back = parts.get("plate_%smm_backing" % tag)
    tot = bone.volume + (back.volume if back else 0.0)
    check("plate %g mm: bone + backing = full envelope" % t,
          abs(tot - plate.volume) < 1.0, "%.1f vs %.1f mm3" % (tot, plate.volume))

# The lumen must stay clear of the pocket and of the probe's acoustic path.
d_pocket = P.ENTRY[1] - (P.POCKET_T + P.FIT)
check("lumen clears the pocket floor", d_pocket > 5.0, "%.1f mm" % d_pocket)
check("lumen clears the back face", P.DEPTH - P.EXIT[1] > 5.0,
      "%.1f mm" % (P.DEPTH - P.EXIT[1]))

# Does a beam straight through the centre of the window cross the lumen?
# Closest approach between the beam line and the lumen axis, solved directly.
beam_o, beam_d = np.zeros(3), np.array([0.0, 1.0, 0.0])
w = beam_o - P.CENTER
a, b, c = beam_d @ beam_d, beam_d @ P.AXIS, P.AXIS @ P.AXIS
d, e = beam_d @ w, P.AXIS @ w
den = a * c - b * b
s, t = ((b * e - c * d) / den, (a * e - b * d) / den) if abs(den) > 1e-9 else (0.0, 0.0)
miss = np.linalg.norm((beam_o + s * beam_d) - (P.CENTER + t * P.AXIS))
check("beam through the window centre crosses the lumen", miss < P.LUMEN_D / 2,
      "misses the axis by %.3f mm at %.1f mm depth" % (miss, s))

# Connector burial: the embedded length must sit entirely inside the block.
for end, step in ((P.ENTRY, +1), (P.EXIT, -1)):
    tip = end + step * P.AXIS * P.CONNECTOR_BURY
    d = min(tip[1] - (P.POCKET_T + P.FIT), P.DEPTH - tip[1], P.HEIGHT / 2 - abs(tip[2]))
    check("connector tip at %.0f mm burial has material around it" % P.CONNECTOR_BURY,
          d > 2.0, "nearest surface %.1f mm" % d)

print("\n%d check(s) failed" % len(fails) if fails else "\nall checks passed")
