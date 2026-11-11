# -*- coding: utf-8 -*-
"""Combine the small parts into one plate STL, in their print orientations.

    python make_plate.py           -> stl/plate_small.stl

Four parts at 6, 6, 9 and 14 minutes, printed one at a time, is four ABS bed
heat cycles for 35 minutes of extrusion. One plate is one heat cycle.

The orientations come from print_plate.ORIENT rather than being chosen here,
because that table is where the reasoning lives: the carriage prints on its
-X face so the nut counterbore is the first layer, the collar lies with its
bore vertical so the split does not need support, and so on. Two files
choosing orientations independently is how a part gets printed upside down.

THE CARRIAGE IS NOT ON THIS PLATE. Its LM8UU bores are drawn at 15.30 for a
15.00 bearing, which is 0.06 mm of clearance after PLA's measured shrink and
about 0.00 after ABS's estimated one. It is the one part whose fit the
coupon has not yet settled, and it is also still waiting on the nut.
"""
import os

import numpy as np
import trimesh

import syringe_drive as S
import print_plate as P

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "stl", "plate_small.stl")

GAP = 8.0                                # mm between parts and to the edge
BED = 220.0

# name, how many. Order is the print order from print_plate.
PLATES = {
    "small": [("collar", 2), ("rod_clamp", 1), ("saddle_cap", 1)],
    # Both rod retainers together. They are the same job in two directions
    # and they go on in the same five minutes of assembly, so printing them
    # apart would be two ABS heat cycles for 38 minutes of extrusion.
    "rods": [("rod_lock", 2), ("rod_stop", 2)],
}
WANT = PLATES["small"]


def main():
    import sys
    name = sys.argv[1] if len(sys.argv) > 1 else "small"
    if name not in PLATES:
        raise SystemExit("plates: %s" % ", ".join(sorted(PLATES)))
    want = PLATES[name]
    global OUT
    OUT = os.path.join(HERE, "stl", "plate_%s.stl" % name)
    orient = {n: (a, ax) for n, (a, ax), _c in P.ORIENT}
    parts = []
    for name, n in want:
        ang, axis = orient[name]
        m = P.oriented(getattr(S, name)(), ang, axis)
        for _ in range(n):
            parts.append((name, m.copy()))

    # One row along X, centred on the bed. These are all small and a single
    # row keeps every part the same distance from the chamber walls, which
    # matters more in ABS than the packing efficiency does.
    x = GAP
    placed = []
    for name, m in parts:
        e = m.extents
        m.apply_translation((x, GAP, 0.0))
        placed.append((name, m, e))
        x += e[0] + GAP

    width = x
    depth = max(e[1] for _n, _m, e in placed) + 2 * GAP
    if width > BED or depth > BED:
        raise SystemExit("plate is %.0f x %.0f mm on a %.0f mm bed"
                         % (width, depth, BED))

    # centre it
    dx, dy = (BED - width) / 2.0, (BED - depth) / 2.0
    for _n, m, _e in placed:
        m.apply_translation((dx, dy, 0.0))

    plate = trimesh.util.concatenate([m for _n, m, _e in placed])
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    plate.export(OUT)

    print("wrote %s" % OUT)
    print("  %-12s %-22s %8s" % ("part", "footprint x height", "mL"))
    for name, m, e in placed:
        print("  %-12s %5.0f x %4.0f x %4.0f mm %7.1f"
              % (name, e[0], e[1], e[2], m.volume / 1000.0))
    print("  %-12s %5.0f x %4.0f mm on a %.0f mm bed"
          % ("PLATE", width, depth, BED))
    print("  %-12s %7.1f mL, %.0f g in ABS"
          % ("total", plate.volume / 1000.0, plate.volume / 1000.0 * 1.04))
    print("")
    print("  carriage is NOT here: its LM8UU bore is 0.06 mm of clearance in")
    print("  PLA and about 0.00 in ABS, and it is the one fit the coupon has")
    print("  not settled. It is also still waiting on the nut.")


if __name__ == "__main__":
    main()
