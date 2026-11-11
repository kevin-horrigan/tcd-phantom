# -*- coding: utf-8 -*-
"""Cutting the two 8 mm shafts, and what actually stops them walking out.

    python rods.py

TWO QUESTIONS, and the second one is the better question.

HOW DO WE CUT THEM. Not with a hacksaw. "Hardened" linear shaft is case
hardened to around 60 HRC and an HSS blade is about 64, so the blade is
barely harder than the work and gives up in a few strokes. People buy the
shaft, reach for the saw they already own, and conclude they were sent the
wrong thing. An abrasive wheel cuts it in under a minute.

DON'T THEY MOVE, SINCE NOTHING HOLDS THEM. Correct, and the model has
admitted it in a comment for weeks: "the rod bores want a press fit, because
nothing else retains the rods". The bore runs clean through both the motor
plate and the end rib, so there is no shoulder, no circlip and no collar.
The only thing holding a rod is friction in 16 mm of printed plastic, and
the bore is drawn line-to-line. That is a light press if the printer is on
song and a slip fit if it is a hair loose, which is exactly what the fit
coupon exists to find out.
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
    A("  ONE DIRECTION IS ALREADY SAFE. The motor is bolted to the front")
    A("  face of the motor plate, so a rod walking forward hits the motor")
    A("  and stops. Only the rib direction is open, and that is the one")
    A("  that matters anyway because it walks toward the syringe.")
    A("")
    A("  SO THE COUPON DECIDES IT, and this is the thing to feel for when")
    A("  it comes off the bed. Push the rod into the coupon's teardrop bore:")
    A("")
    A("    needs a tap with a mallet, will not pull out by hand")
    A("        the fit is right. Nothing else is needed.")
    A("    goes in with firm thumb pressure, comes out with a tug")
    A("        marginal. It will hold for a session and walk over a week.")
    A("    slides in and out freely")
    A("        it will walk in an afternoon. Fix it.")
    A("")
    A("  IF IT NEEDS FIXING, in the order I would try them:")
    A("    1. a drop of retaining compound or slow epoxy in each bore. The")
    A("       rods never need to come out, and this is five minutes.")
    A("    2. a printed strap across both rod ends on the rib's back face,")
    A("       held by the zip-tie slots already there. Reversible.")
    A("    3. an M3 self-tapped through the rib onto each rod. It dents the")
    A("       rod, which is harmless because that end never sees a bearing,")
    A("       but it is the least tidy of the three.")
    A("")
    A("  WHAT I WOULD NOT DO is shaft collars, which is the obvious answer")
    A("  and does not fit: there is %.0f mm between the rib's back face and"
      % 3.0)
    A("  the saddle, and a collar is about ten.")


if __name__ == "__main__":
    main()
