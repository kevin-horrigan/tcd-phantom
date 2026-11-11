# -*- coding: utf-8 -*-
"""Cutting the two 8 mm shafts, and what actually stops them walking out.

    python rods.py

TWO QUESTIONS, and the second one is the better question.

HOW DO WE CUT THEM. Not with a hacksaw. "Hardened" linear shaft is case
hardened to around 60 HRC and an HSS blade is about 64, so the blade is
barely harder than the work and gives up in a few strokes. People buy the
shaft, reach for the saw they already own, and conclude they were sent the
wrong thing. An abrasive wheel cuts it in under a minute.

DON'T THEY MOVE, SINCE NOTHING HOLDS THEM. They did, and now they do not:
rod_lock() clamps each rod and bolts to the rib. The section below is kept
because the reasoning that got there is worth having, including the part I
got wrong.
"""
import os

import syringe_drive as S

HERE = os.path.dirname(os.path.abspath(__file__))

CUTS = [
    ("abrasive chop saw", "YES, best", "square cut, under a minute, no heat "
     "in the part that matters"),
    ("angle grinder, thin cutoff wheel", "YES", "fast and fine. Expect to "
     "square the end up afterwards"),
    ("rotary tool, cutoff disc", "yes, slowly", "several discs for 8 mm, but "
     "it works and most benches have one"),
    ("bimetal hacksaw", "barely", "minutes of effort per cut and it eats the "
     "blade. Last resort"),
    ("HSS hacksaw", "NO", "the case is 60 HRC against a 64 HRC blade. It "
     "will not cut and you will think the rod is wrong"),
    ("tube cutter", "NO", "the wheel skates on hardened steel and work "
     "hardens the surface where it rides"),
]


def main():
    A = print
    L = S.X_RIB_BACK - S.X_MOTOR_FACE
    A("THE CUT")
    A("  Two rods, %.0f mm each. Buy 300 mm of 8 mm hardened shaft and you"
      % L)
    A("  get both out of one piece with %.0f mm spare for the coupon."
      % (300.0 - 2 * L))
    A("")
    A("  %-34s %-12s %s" % ("tool", "verdict", "why"))
    for nm, verdict, why in CUTS:
        A("  %-34s %-12s %s" % (nm, verdict, why))
    A("")
    A("  AND THEN CHAMFER BOTH ENDS, which is not optional and is the step")
    A("  that gets skipped. An LM8UU is a cage of ball tracks with a thin")
    A("  steel sleeve, and a square-cut burr dragged through it will score")
    A("  the tracks on the way in. A few seconds on a file or a grinder,")
    A("  turning the rod, until the edge is visibly broken all round.")
    A("")
    A("  Measure after cutting, not before. %.0f mm is the span from the"
      % L)
    A("  motor plate's front face to the rib's back face, and the rod is")
    A("  meant to sit flush at both. Long is recoverable, short is scrap.")
    A("")

    A("WHAT HOLDS THEM")
    A("  Nothing but the press fit, and the bore is line-to-line:")
    A("    bore drawn        %.2f mm" % (S.ROD_D + 0.24))
    A("    prints            %.2f mm after the %.2f shrink"
      % (S.ROD_D + 0.24 - S.HOLE_SHRINK, S.HOLE_SHRINK))
    A("    rod               %.2f mm" % S.ROD_D)
    A("    grip length       %.0f mm, %.0f in the motor plate and %.0f in the rib"
      % (S.WALL_T + S.RIB_T, S.WALL_T, S.RIB_T))
    A("")
    A("  WHAT WOULD MAKE THEM WALK. The carriage runs four LM8UUs at 1 Hz")
    A("  for hours. Each stroke drags the rods one way and then the other,")
    A("  and the two directions are never quite equal, so a loose rod")
    A("  ratchets. Tens of thousands of cycles in an afternoon.")
    A("")
    A("  I SAID THE MOTOR BLOCKED ONE DIRECTION. IT DOES NOT. The rods sit")
    A("  at y = +/- %.0f and a NEMA17 is %.1f square, so each rod passes"
      % (S.ROD_SPACING / 2, S.MOTOR_SQ))
    A("  %.2f mm OUTSIDE the motor body and sails straight past it. Both"
      % (S.ROD_SPACING / 2 - S.MOTOR_SQ / 2))
    A("  ends were open the whole time, which makes a lock necessary rather")
    A("  than tidy.")
    A("")
    A("  AND A PLAIN COLLAR CANNOT DO IT. A collar clamped to a rod stops")
    A("  ONE direction: it jams against a fixed face when the rod moves")
    A("  toward it and lifts straight off when the rod moves the other way.")
    A("  Both directions would take two collars per rod, and there is")
    A("  nowhere for the second. The carriage sweeps X %.0f to %.0f, which"
      % (S.X_CARR_MIN, S.X_CARR_MIN + S.TRAVEL + S.CARRIAGE_L))
    A("  leaves %.0f mm of rod free inboard of the rib against a collar's ten."
      % (S.X_RIB - (S.X_CARR_MIN + S.TRAVEL + S.CARRIAGE_L)))
    A("")
    A("  SO THE LOCK BOLTS TO THE RIB. rod_lock() clamps the rod with one")
    A("  M3 and screws to the rib's back face with two more. Once the rod")
    A("  is fixed to the frame it cannot travel either way, and one part")
    A("  per rod replaces the four collars that would not have fitted.")
    A("")
    A("  It goes on the rib's BACK face because that face is free: the")
    A("  saddle starts %.0f mm behind the rib but spans only y +/- 13, and"
      % 3.0)
    A("  the rods are at y +/- %.0f. The lock's inner edge is at y = %.0f."
      % (S.ROD_SPACING / 2, S.ROD_SPACING / 2 - S.LOCK_HALF))
    A("")
    A("  ITS BORE IS A CLAMP FIT, NOT A PRESS FIT, which is the opposite of")
    A("  the frame's bores and easy to get backwards. It prints %.2f on an"
      % (S.ROD_D + 0.15))
    A("  %.2f rod so it SLIDES on, and then the screw does the holding."
      % S.ROD_D)
    A("  A press fit here would make it impossible to position.")


if __name__ == "__main__":
    main()
