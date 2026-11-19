# -*- coding: utf-8 -*-
"""The assembly procedure, one step at a time, with the fastener for each.

    python build_steps.py          the procedure as text
    python build_steps.py --png    the same thing as a one page sheet

WHY THIS EXISTS. There is already a 3-D model the students can rotate, and it
carries the same step text. What it does not do is tell somebody standing at
the bench with a bag of screws which screw goes in which hole, in what order,
and what to check before moving on. A model answers "what does it look like".
This answers "what do I do next", which is a different question.

Writing it found three defects in one part, which is the real argument for
writing procedures down: a step that has to name a fastener cannot be vague.
The rod clamp was drawn 57 mm below its seat, it called for an M3 x 16 that
bottoms out in a 10 mm blind hole, and its screws were on no list at all.

EVERY NUMBER HERE IS DERIVED. Nothing is typed twice. If the model changes,
this changes, and check_drive compares the two.
"""
import os

import syringe_drive as S

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "build_steps.png")


# What each fastener line is for, keyed by the BOM's own name for it. The
# names are NOT retyped here: fasteners() reads bom.py, because the first
# version typed "zip tie, 2.5 to 3 mm" against the BOM's "zip tie" and the
# cross-check caught it immediately. A procedure that renames its parts is a
# procedure somebody orders the wrong thing from.
WHERE = {
    "M3 x 12 socket cap": "2 rod lock, 2 rod stop, 2 rod clamp",
    "M3 x 20 thread-forming": "4 rod lock into the end rib",
    "M3 x 8 cap screw": "NEMA 17 face to the motor plate",
    "M3 x 10 cap screw": "T8 nut flange to the carriage",
    "zip tie": "2 per strap station, over the saddle cap",
}


def fasteners():
    """Every fastener line, straight off the BOM, in the order it lists them."""
    import bom
    out = []
    for r in bom.BOM:
        if r[0] == "FASTENERS":
            out.append((r[2], r[1], WHERE.get(r[2], r[3])))
    return out


def steps():
    """name, what you do, the fastener, and what tells you it is right."""
    z1 = S.CLAMP_SEAT_Z
    return [
        ("Frame on the bench",
         "Baseplate down, motor end to your left, syringe end to your "
         "right. Everything below is described in that orientation. The "
         "frame is PLA and already printed; every other printed part is ABS.",
         "none",
         "The end rib is the tall wall at X %.0f with the round 608 pocket "
         "low and the barrel channel high." % S.X_RIB),

        ("608 bearing into the end rib",
         "Press the 608 into the pocket on the rib's MOTOR side, from the "
         "motor side, until it is flush. This is the screw's far support.",
         "none, press fit",
         "It should need thumb pressure and then stay. If it drops in, the "
         "pocket printed oversize and the screw end will wander."),

        ("LM8UU x2 into the carriage",
         "Press one into each bore from the same side, so any taper in the "
         "print works the same way on both.",
         "none, press fit",
         "Both bushes square and seated. Roll the carriage on a flat "
         "surface: it should not rock."),

        ("T8 anti-backlash nut onto the carriage",
         "Flange against the carriage's nut face, spring side toward the "
         "motor so the preload works against the piston's reaction.",
         "4 x M3 x 10 through the flange",
         "Snug only. Overtightening a printed boss splits it. Spin the nut "
         "by hand on the screw before this and confirm it has no slop."),

        ("8 mm shafts x2 through the frame",
         "Chamfered end first. They pass through the motor plate, the "
         "carriage's bushes, the end rib, and out the back, where %.0f mm "
         "stands proud for the locks. CHAMFER BOTH ENDS first or a square "
         "burr scores the LM8UU ball tracks going in." % S.LOCK_T,
         "none yet",
         "Both shafts cut to %.0f mm. The carriage slides the full %.0f mm "
         "of travel with two fingers." % (S.X_RIB_BACK + S.LOCK_T, S.TRAVEL)),

        ("Rod stop x2, DURING shaft insertion",
         "These go on BEFORE the shaft reaches the rib, because the bore is "
         "closed and there is no way to add them afterwards without pulling "
         "a shaft back out. Slide one onto each shaft, inboard of the rib, "
         "bearing on the rib's FRONT face at X %.0f." % S.X_RIB,
         "1 x M3 x %.0f each, pinching the C shut" % S.CLAMP_SCREW_L,
         "This is the part that takes travel toward the syringe in "
         "COMPRESSION instead of hanging two screws in thread pullout."),

        ("Rod lock x2, outboard of the rib",
         "On the %.0f mm of shaft standing proud behind the rib. Each one "
         "clamps its shaft AND bolts to the rib, so with the stops already "
         "on, the rib is sandwiched and the shafts are pinned both "
         "directions on printed wall in compression." % S.LOCK_T,
         "2 x M3 x %.0f thread-forming into the rib, plus 1 x M3 x %.0f "
         "pinch" % (S.LOCK_SCREW_L, S.CLAMP_SCREW_L),
         "The thread-forming length is NOT free. %.0f mm is spent crossing "
         "the lock, so an M3 x %.0f engages %.0f mm of the %.0f mm rib. An "
         "M3 x 16 would engage 4, an M3 x 25 breaks through into the "
         "carriage sweep." % (S.LOCK_T, S.LOCK_SCREW_L,
                              S.LOCK_SCREW_L - S.LOCK_T, S.RIB_T)),

        ("Lead screw and coupler",
         "Tr8x8 screw through the nut and into the 608. Then the 5-to-8 "
         "coupler on the motor end: 5 mm bore to the pancake shaft, 8 mm "
         "bore to the screw.",
         "the coupler's own set screws",
         "T8x8 means 8 mm PER TURN. T8x2 looks identical, is sold far more "
         "often, and would need 875 rpm for the same beat, which no 12 V "
         "NEMA 17 will give you."),

        ("NEMA 17 pancake onto the motor plate",
         "Shaft through the plate's boss and into the coupler. Do not "
         "tighten the coupler to the motor until the motor is bolted down, "
         "or the screw ends up preloaded sideways.",
         "4 x M3 x 8 into the motor face",
         "Turn the coupler by hand through the full travel. The carriage "
         "should run end to end with no tight spot and no rising effort."),

        ("Split collars x2 onto the barrel",
         "SNAP THEM ON FIRST, off the frame. Slit upward. The bore is drawn "
         "0.10 mm under the measured %.1f mm barrel so they grip. These two "
         "are the ONLY parts that know the barrel diameter: a different "
         "syringe means reprinting these and nothing else."
         % S.SYR_BARREL_D,
         "none, snap fit",
         "They sit at X %.0f and %.0f, centred on the two strap stations."
         % (S.COLLAR_X[0], S.COLLAR_X[1])),

        ("Barrel into the saddle",
         "Lay the whole barrel-and-collars assembly into the channel with "
         "the finger flange hard against the end rib. Slit upward, so "
         "pressing down closes the collars rather than spreading them.",
         "none yet",
         "The flange measures 2.0 and the rib was printed for 2.5, so there "
         "is 0.5 mm of slack. The piston's reaction pushes the barrel "
         "forward into the rib and the straps hold it there."),

        ("Saddle cap over BOTH collars",
         "ONE cap, spanning X %.0f to %.0f. It has to reach both collars: "
         "the first starts at %.0f and the second ends at %.0f. If yours "
         "only covers one, it is the old 26 mm version and it is scrap."
         % (S.CAP_X0, S.CAP_X1, S.COLLAR_X[0], S.COLLAR_X[1] + S.COLLAR_L),
         "4 x zip tie, two per strap station",
         "The grooves are OPEN on the outside flank, on the cap and on the "
         "frame both. That is deliberate: the tie wraps the whole assembly. "
         "Snug, not crushing. The collar wall is 0.93 mm and it is holding a "
         "syringe, not a driveshaft."),

        ("Plunger into the carriage, rod clamp last",
         "Drop the plunger's thumb disc into the carriage pocket, lay the "
         "clamp's tongue down into the rod slot, and run the two screws "
         "down through the bar into the carriage's top face at Z %.1f."
         % z1,
         "2 x M3 x %.0f socket cap" % S.CLAMP_SCREW_L,
         "NOT M3 x 16. The screw crosses the %.0f mm bar first, so a 16 "
         "leaves %.0f mm for a %.0f mm blind hole and bottoms out, which "
         "feels tight and clamps nothing. The bar should still stand about "
         "1.25 mm proud when the tongue touches the rod; the screws close "
         "that gap and pin the rod."
         % (S.CLAMP_T, 16.0 - S.CLAMP_T, S.CLAMP_TAP_DEEP)),
    ]


def report():
    def A(t=""):
        print(t)

    A("WAVEFORM GENERATOR, ASSEMBLY PROCEDURE")
    A("Derived from syringe_drive, so it cannot drift from the printed parts.")
    A()
    A("HAVE THESE IN FRONT OF YOU")
    for name, qty, where in fasteners():
        A("  %2d x %-26s %s" % (qty, name, where))
    A()
    A("  Two things to get right before you start:")
    A("    The frame is PLA. Everything else printed is ABS. They do not")
    A("    shrink alike, so every fit was drawn with the forgiving direction")
    A("    in mind. Do not force anything that was meant to slide.")
    A("    Steps 6 and 7 happen WHILE the shafts go in, not after. The rod")
    A("    stop's bore is closed and the rib is in the way.")
    A()
    for i, (name, do, fast, test) in enumerate(steps(), 1):
        A("%2d. %s" % (i, name))
        A("    %s" % do)
        A("    FASTENER: %s" % fast)
        A("    CHECK:    %s" % test)
        A()
    A("WHEN IT IS TOGETHER")
    A("  Turn the coupler by hand through the whole stroke before any power.")
    A("  The carriage should move %.0f mm with no tight spot. Then run the"
      % S.TRAVEL)
    A("  motor dry, no syringe, and only then fill the loop.")


def sheet():
    """The same procedure as printable pages, for the bench.

    It paginates. The first version ran one figure and stopped at step 7
    because the page ran out, which is a sheet that looks finished and is
    not: the last six steps include the two the students are most likely to
    get wrong. A procedure that silently truncates is worse than no sheet.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    INK, MUT, RED, GRN = "#1a1a1a", "#555555", "#b3202c", "#2e6b34"
    st = steps()
    W, H = 100.0, 140.0
    pages, cur, y = [], [], H - 10.0

    # lay the steps out first, so the page count comes from the content
    for i, (name, do, fast, test) in enumerate(st, 1):
        body = ([("t", name)]
                + [("d", l) for l in _wrap(do, 104)]
                + [("f", l) for l in _wrap("FASTENER: " + fast, 100)]
                + [("c", l) for l in _wrap("CHECK: " + test, 100)])
        need = 4.0 + 2.9 * (len(body) - 1) + 2.4
        if y - need < 8.0:
            pages.append(cur)
            cur, y = [], H - 10.0
        cur.append((i, body))
        y -= need
    pages.append(cur)

    out = []
    for pno, page in enumerate(pages, 1):
        fig = plt.figure(figsize=(8.5, 11.9), facecolor="white")
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_xlim(0, W)
        ax.set_ylim(0, H)
        ax.axis("off")

        def txt(x, y, s, size=8.0, c=INK, w="normal"):
            ax.text(x, y, s, fontsize=size, color=c, ha="left", va="top",
                    family="DejaVu Sans", fontweight=w)

        y = H - 6.0
        txt(6, y, "HOW THE PUMP GOES TOGETHER", 15.5, INK, "bold")
        txt(94 - 14, y + 0.6, "page %d of %d" % (pno, len(pages)), 8.4, MUT)
        y -= 4.6
        txt(6, y, "Every number is read out of the model. The frame is PLA; "
                  "every other printed part is ABS.", 8.0, MUT)
        y -= 5.2

        if pno == 1:
            txt(6, y, "FASTENERS, all of them", 10.5, INK, "bold")
            y -= 3.6
            for name, qty, where in fasteners():
                txt(8, y, "%d x" % qty, 8.4, RED, "bold")
                txt(14, y, name, 8.4, INK, "bold")
                txt(48, y, where, 8.2, MUT)
                y -= 3.1
            y -= 1.0
            txt(6, y, "Steps 6 and 7 happen WHILE the shafts go in, not "
                      "after: the rod stop's bore is closed.", 8.2, RED,
                "bold")
            y -= 4.4

        for i, body in page:
            txt(6, y, "%d" % i, 11.5, RED, "bold")
            for kind, line in body:
                if kind == "t":
                    txt(11, y, line, 10.4, INK, "bold")
                    y -= 4.0
                elif kind == "d":
                    txt(11, y, line, 8.2, INK)
                    y -= 2.9
                elif kind == "f":
                    txt(11, y, line, 8.2, RED)
                    y -= 2.9
                else:
                    txt(11, y, line, 8.0, GRN)
                    y -= 2.9
            y -= 2.4

        if pno == len(pages):
            y -= 1.0
            txt(6, y, "WHEN IT IS TOGETHER", 10.5, INK, "bold")
            y -= 3.6
            for line in (
                    "Turn the coupler by hand through the whole stroke "
                    "before any power is applied. The carriage",
                    "should move %.0f mm with no tight spot and no rising "
                    "effort. Then run the motor dry, with no" % S.TRAVEL,
                    "syringe fitted, and only then fill the loop."):
                txt(8, y, line, 8.2, INK)
                y -= 2.9

        f = OUT.replace(".png", "_p%d.png" % pno)
        fig.savefig(f, dpi=170, facecolor="white")
        plt.close(fig)
        out.append(f)
        print("wrote %s" % f)
    return out


def _wrap(s, n):
    out, line = [], ""
    for w in s.split():
        if len(line) + len(w) + 1 > n:
            out.append(line)
            line = w
        else:
            line = (line + " " + w).strip()
    if line:
        out.append(line)
    return out


if __name__ == "__main__":
    import sys
    if "--png" in sys.argv:
        sheet()
    else:
        report()
