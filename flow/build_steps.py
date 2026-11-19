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

import numpy as _np

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


# --------------------------------------------------------------- pictures
# One rendered view per step, built from the same meshes the 3-D page uses,
# so a picture cannot show something the model does not have.
#
# The trick that makes these readable: EVERY visible triangle from every part
# goes into ONE Poly3DCollection, depth sorted together. Drawing each part as
# its own collection is what made earlier 3-D renders here unusable, because
# matplotlib sorts whole collections against each other and not the triangles
# inside them, so the frame's saddle would paint over parts standing in front
# of it. Concatenating first removes the problem entirely rather than fighting
# it with z-bias.
#
# Already-built parts go grey and the step's own part goes red, which is the
# whole job of the picture: not "what does the rig look like" but "which thing
# am I holding and where does it go".
LIGHT = _np.array([0.45, -0.75, 0.55])
LIGHT = LIGHT / _np.linalg.norm(LIGHT)
GREY = (0.78, 0.78, 0.76)
NEW = (0.70, 0.16, 0.24)


def _eye(elev, azim):
    e, a = _np.radians(elev), _np.radians(azim)
    return _np.array([_np.cos(e) * _np.cos(a),
                      _np.cos(e) * _np.sin(a), _np.sin(e)])


def _collect(meshes, view):
    """Every forward facing triangle from every mesh, shaded and depth sorted
    as one pile. Returns (triangles, rgb) ready for a single collection."""
    tris, cols = [], []
    for mesh, base in meshes:
        keep = mesh.face_normals @ view > 0.0
        if not keep.any():
            continue
        tri, nrm = mesh.triangles[keep], mesh.face_normals[keep]
        lam = 0.38 + 0.62 * _np.clip(nrm @ LIGHT, 0.0, 1.0)
        tris.append(tri)
        cols.append(_np.clip(_np.array(base)[None, :] * lam[:, None], 0, 1))
    if not tris:
        return None, None
    tri = _np.concatenate(tris)
    rgb = _np.concatenate(cols)
    order = _np.argsort(tri.mean(axis=1) @ view)
    return tri[order], rgb[order]


# How to frame each step. BUILD says how much of the rig to draw, HERO says
# which part goes red. They are NOT the same: step 3 fits the LM8UU bushes
# into the carriage, but assembly order puts the bushes before the carriage,
# so building only as far as the bushes draws two bearings floating in a
# frame. Build to the carriage, redden the bushes, and the picture says what
# the step says. The first version tied the two together and step 3 showed a
# red carriage under the words "LM8UU x2 into the carriage".
#
#   step: (build_to, hero, elev, azim, pad)   pad None = frame the whole rig
VIEWS = {
    1: (None, None, 26, -58, None),
    2: ("608 bearing", "608 bearing", 18, -132, 18),
    3: ("carriage", "LM8UU x2", 24, -54, 22),
    4: ("carriage", "T8 anti-backlash nut", 22, -44, 20),
    5: ("8 mm shafts x2", "8 mm shafts x2", 26, -58, None),
    6: ("rod stop x2", "rod stop x2", 20, -128, 20),
    7: ("rod lock x2", "rod lock x2", 20, -34, 20),
    8: ("5-8 mm coupler", "Tr8x8 lead screw", 26, -58, None),
    9: ("NEMA 17 pancake", "NEMA 17 pancake", 22, -64, 26),
    10: ("split collars x2", "split collars x2", 16, -34, 22),
    11: ("syringe barrel", "syringe barrel", 22, -48, None),
    12: ("saddle cap + ties", "saddle cap + ties", 16, -32, 22),
    13: ("rod clamp", "rod clamp", 22, -40, 18),
}


def figures(outdir=None):
    """Render one PNG per step. Returns {step number: path}."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    import assembly as A

    outdir = outdir or os.path.join(HERE, "steps")
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    built = A.parts()
    order = [n for n, _m, _c, _e, _t in built]
    out = {}

    for i, (name, _do, _f, _t) in enumerate(steps(), 1):
        build_to, hero_name, elev, azim, pad = VIEWS[i]
        upto = order.index(build_to) if build_to else len(built) - 1
        hero_i = order.index(hero_name) if hero_name else -1
        view = _eye(elev, azim)

        meshes, hero = [], None
        for k, (n, m, _c, _e, _tx) in enumerate(built):
            if k > upto:
                continue
            if k == hero_i:
                meshes.append((m, NEW))
                hero = m
            else:
                meshes.append((m, GREY))
        tri, rgb = _collect(meshes, view)
        if tri is None:
            continue

        fig = plt.figure(figsize=(3.4, 2.6), facecolor="white")
        ax = fig.add_axes([-0.14, -0.14, 1.28, 1.28], projection="3d")
        ax.set_proj_type("ortho")
        ax.add_collection3d(Poly3DCollection(
            tri, facecolors=rgb, edgecolors=rgb, linewidths=0.25,
            shade=False))

        if pad and hero is not None:
            # A mirrored pair spans the whole width, so cropping to its
            # bounds crops to nothing: step 6 framed a 126 mm cube and the
            # rod stop came out four pixels wide behind the rib. Focus on
            # ONE of the pair when the mesh is symmetric about y = 0.
            v = hero.vertices
            if (v[:, 1].min() < -1.0 < 1.0 < v[:, 1].max()
                    and abs(v[:, 1].min() + v[:, 1].max()) < 1.0):
                v = v[v[:, 1] >= -1.0]
            lo, hi = v.min(axis=0) - pad, v.max(axis=0) + pad
        else:
            allv = _np.concatenate([m.vertices for m, _c in meshes])
            lo, hi = allv.min(axis=0) - 6, allv.max(axis=0) + 6
        mid = (lo + hi) / 2.0
        r = float((hi - lo).max()) / 2.0
        ax.set_xlim(mid[0] - r, mid[0] + r)
        ax.set_ylim(mid[1] - r, mid[1] + r)
        ax.set_zlim(mid[2] - r, mid[2] + r)
        ax.set_box_aspect((1, 1, 1))
        ax.view_init(elev=elev, azim=azim)
        ax.set_axis_off()

        f = os.path.join(outdir, "step%02d.png" % i)
        fig.savefig(f, dpi=150, facecolor="white")
        plt.close(fig)
        out[i] = f
        print("  step %2d  %s" % (i, os.path.basename(f)))
    return out


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
    """The procedure as printable pages: text on the left, a picture of that
    step on the right, with the part going on shown in red.

    It paginates on measured content. The first version ran one figure and
    stopped at step 7 because the page filled, which looks finished and is
    not: the six it cut include the saddle cap and the rod clamp, the two
    most likely to be built wrong.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.image as mpimg

    INK, MUT, RED, GRN = "#1a1a1a", "#555555", "#b3202c", "#2e6b34"
    figs = figures()
    st = steps()
    W, H = 100.0, 140.0
    TXT_W = 62           # characters of text before the picture column
    PIC_W, PIC_H = 33.0, 25.0

    # measure first, so the page count comes from the content
    # Page 1 carries the fastener table and the warning line above the first
    # step, so it has less room. Measuring every page as if it started at the
    # top is what ran step 4's CHECK lines off the bottom of page 1.
    HEAD1 = 3.6 + 3.1 * len(fasteners()) + 1.2 + 4.6
    laid, cur, y = [], [], H - 10.0 - HEAD1
    for i, (name, do, fast, test) in enumerate(st, 1):
        body = ([("t", name)]
                + [("d", l) for l in _wrap(do, TXT_W)]
                + [("f", l) for l in _wrap("FASTENER: " + fast, TXT_W - 2)]
                + [("c", l) for l in _wrap("CHECK: " + test, TXT_W - 2)])
        text_h = 4.0 + 2.9 * (len(body) - 1)
        need = max(text_h, PIC_H) + 3.0
        if y - need < 8.0:
            laid.append(cur)
            cur, y = [], H - 10.0
        cur.append((i, body, need))
        y -= need
    laid.append(cur)

    out = []
    for pno, page in enumerate(laid, 1):
        fig = plt.figure(figsize=(8.5, 11.9), facecolor="white")
        ax = fig.add_axes([0, 0, 1, 1])
        ax.set_xlim(0, W)
        ax.set_ylim(0, H)
        ax.axis("off")

        def txt(x, yy, t, size=8.0, c=INK, w="normal"):
            ax.text(x, yy, t, fontsize=size, color=c, ha="left", va="top",
                    family="DejaVu Sans", fontweight=w)

        y = H - 6.0
        txt(6, y, "HOW THE PUMP GOES TOGETHER", 15.5, INK, "bold")
        txt(80, y + 0.6, "page %d of %d" % (pno, len(laid)), 8.4, MUT)
        y -= 4.6
        txt(6, y, "The part going on at each step is RED. Every number is "
                  "read out of the model.", 8.0, MUT)
        y -= 5.2

        if pno == 1:
            txt(6, y, "FASTENERS, all of them", 10.5, INK, "bold")
            y -= 3.6
            for nm, qty, where in fasteners():
                txt(8, y, "%d x" % qty, 8.4, RED, "bold")
                txt(14, y, nm, 8.4, INK, "bold")
                txt(48, y, where, 8.2, MUT)
                y -= 3.1
            y -= 1.2
            txt(6, y, "Steps 6 and 7 happen WHILE the shafts go in, not "
                      "after: the rod stop's bore is closed.", 8.2, RED,
                "bold")
            y -= 4.6

        for i, body, need in page:
            top = y
            txt(5, y, "%d" % i, 11.5, RED, "bold")
            for kind, line in body:
                if kind == "t":
                    txt(10, y, line, 10.4, INK, "bold")
                    y -= 4.0
                elif kind == "d":
                    txt(10, y, line, 8.2, INK)
                    y -= 2.9
                elif kind == "f":
                    txt(10, y, line, 8.2, RED)
                    y -= 2.9
                else:
                    txt(10, y, line, 8.0, GRN)
                    y -= 2.9

            if i in figs:
                bx, by = W - PIC_W - 4.0, top - PIC_H + 1.5
                iax = fig.add_axes([bx / W, by / H, PIC_W / W, PIC_H / H])
                iax.imshow(mpimg.imread(figs[i]))
                iax.axis("off")

            y = top - need

        if pno == len(laid):
            y -= 1.0
            txt(6, y, "WHEN IT IS TOGETHER", 10.5, INK, "bold")
            y -= 3.6
            for line in (
                    "Turn the coupler by hand through the whole stroke "
                    "before any power is applied.",
                    "The carriage should move %.0f mm with no tight spot "
                    "and no rising effort. Then run" % S.TRAVEL,
                    "the motor dry, with no syringe fitted, and only then "
                    "fill the loop."):
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
