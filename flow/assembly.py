# -*- coding: utf-8 -*-
"""Every part of the waveform generator, placed, named, and in build order.

    python assembly.py   ->  web/assembly.json

Writes the data behind the interactive viewer: each part as base64 float32
vertices and uint32 faces, plus a manifest giving its colour, its explode
offset, which step installs it, and the text of that step.

Three kinds of part, and the colour says which:

    tan, blue, brown, violet   printed, comes off the bed
    grey and gold              bought, comes out of a bag
    pale                       the syringe, which is neither

Geometry comes from syringe_drive at build time, so this cannot drift from
the model or from the STLs that were actually printed. The bought parts are
drawn at catalogue size, taking the same constants the frame was cut around,
which is the point: if the 608 pocket and the 608 ever disagree, they
disagree here too, visibly, instead of on the bench.

Coordinates follow the model: +X runs from the motor toward the syringe tip,
+Z is up from the baseplate, Y is across. The viewer is Y-up, so it rotates
the whole assembly once on load rather than every part having its own idea.
"""
import base64
import json
import os

import numpy as np
import trimesh

import syringe_drive as S

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "web")

# Bought parts the model does not build, at catalogue size.
COUPLER_D = 19.0                     # 5 to 8 mm flexible coupler
SHAFT_D = 5.0                        # pancake output shaft
MOTOR_L = 23.0                       # 17HE08-1004S body length
SCREW_D = 8.0                        # Tr8x8 major diameter
ZIP_T = 3.6                          # zip tie, across the flat

X_COUPLER = (S.X_MOTOR_BACK, S.X_MOTOR_BACK + S.COUPLER_L)
X_SCREW = (X_COUPLER[1] - 10.0, S.X_RIB + S.BEAR_W)
CARR_AT = S.X_CARR_MIN               # retracted, which is where you build it

STRAP_X = (S.X_RIB_BACK + 8.0, S.X_SADDLE_END - 16.0)
COLLAR_X = tuple(xs + 2.0 - S.COLLAR_L / 2.0 for xs in STRAP_X)

C_FRAME = "#cdc2b4"
C_CARRIAGE = "#4d7699"
C_COLLAR = "#8c6b4d"
C_CAP = "#a89e90"
C_CLAMP = "#75618a"
C_LOCK = "#6f8c6a"
C_STOP = "#5c8c85"
C_STEEL = "#949aa3"
C_SCREW = "#b89a40"
C_MOTOR = "#434850"
C_GLASS = "#dfe4e8"
C_ZIP = "#56606b"


def at(mesh, dx=0.0, dy=0.0, dz=0.0):
    m = mesh.copy()
    m.apply_translation((dx, dy, dz))
    return m


def both(a, b):
    return trimesh.util.concatenate([a, b])


def ring_x(od, idd, span, y=0.0, z=0.0):
    """A plain sleeve on the X axis: bearings, bushes, couplers."""
    return S.diff(S.cyl_x(od / 2.0, span, y=y, z=z),
                  S.cyl_x(idd / 2.0, (span[0] - 1.0, span[1] + 1.0), y=y, z=z))


def motor():
    body = S.box((S.X_MOTOR_FACE - MOTOR_L, S.X_MOTOR_FACE),
                 (-S.MOTOR_SQ / 2, S.MOTOR_SQ / 2),
                 (S.SCREW_H - S.MOTOR_SQ / 2, S.SCREW_H + S.MOTOR_SQ / 2))
    shaft = S.cyl_x(SHAFT_D / 2, (S.X_MOTOR_FACE, X_COUPLER[0] + 12.0),
                    z=S.SCREW_H)
    return both(body, shaft)


def t8_nut():
    """Anti-backlash T8 flange nut, drawn to the dimensions the carriage was
    counterbored for. If the one in the post does not match these, the
    carriage is the part that has to change, not the frame."""
    flange = ring_x(S.NUT_FLANGE_D, SCREW_D,
                    (CARR_AT, CARR_AT + S.NUT_FLANGE_T), z=S.SCREW_H)
    body = ring_x(S.NUT_BODY_D, SCREW_D,
                  (CARR_AT + S.NUT_FLANGE_T, CARR_AT + 18.0), z=S.SCREW_H)
    return both(flange, body)


def zip_ties():
    ties = []
    for xs in STRAP_X:
        loop = S.diff(
            S.cyl_x(S.SADDLE_BORE / 2 + 2.2, (xs, xs + ZIP_T), z=S.SYR_H),
            S.cyl_x(S.SADDLE_BORE / 2 + 0.4, (xs - 1, xs + ZIP_T + 1),
                    z=S.SYR_H))
        ties.append(loop)
    return trimesh.util.concatenate(ties)


# name, mesh, colour, explode vector, step text
def parts():
    P = S.build()
    carr = at(P["carriage"], dx=CARR_AT)
    # The rods used to stop at the rib's back face. They now run on through
    # it to 134, because that last 12 mm is what the rod lock clamps.
    rods = trimesh.util.concatenate([
        S.cyl_x(S.ROD_D / 2, (0.0, S.X_RIB_BACK + S.LOCK_T), y=dy,
                z=S.SCREW_H)
        for dy in (-S.ROD_SPACING / 2, S.ROD_SPACING / 2)])
    locks = trimesh.util.concatenate([
        P["rod_lock"],
        P["rod_lock"].copy().apply_transform(
            trimesh.transformations.scale_matrix(-1.0, [0, 0, 0], [0, 1, 0]))])
    stops = trimesh.util.concatenate([
        P["rod_stop"],
        P["rod_stop"].copy().apply_transform(
            trimesh.transformations.scale_matrix(-1.0, [0, 0, 0], [0, 1, 0]))])
    bushes = trimesh.util.concatenate([
        ring_x(S.LM_OD, S.ROD_D, (CARR_AT + 3.0, CARR_AT + 3.0 + S.LM_L),
               y=dy, z=S.SCREW_H)
        for dy in (-S.ROD_SPACING / 2, S.ROD_SPACING / 2)])
    collars = trimesh.util.concatenate(
        [at(P["collar"], dx=cx, dz=S.SYR_H) for cx in COLLAR_X])

    return [
        ("frame", P["frame"], C_FRAME, [0, 0, 0],
         "Start with the frame, motor plate to the left and the end rib to "
         "the right. It printed baseplate-down. 180.6 mL, just under four "
         "hours, and it is the one part a wrong guess could have scrapped."),

        ("608 bearing", ring_x(S.BEAR_OD, 8.0,
                               (S.X_RIB, S.X_RIB + S.BEAR_W), z=S.SCREW_H),
         C_STEEL, [0, 0, 120],
         "Press the 608 into the end rib from the OUTSIDE until it seats on "
         "the 2 mm shoulder. The pocket is drawn 22.20 and prints about "
         "21.96 on a 22.00 bearing, so it wants thumb pressure and should "
         "not fall out. If it drops in loose, stop: the rest of the screw "
         "train is built on this being tight."),

        ("LM8UU x2", bushes, C_STEEL, [0, 0, 190],
         "Press the two LM8UU bushes into the carriage bores, one each side. "
         "Same story as the 608: drawn 8.24, prints about 8.00. Do this "
         "before anything goes on the rods, because the carriage cannot be "
         "fitted to them afterwards."),

        ("T8 anti-backlash nut", t8_nut(), C_SCREW, [0, 0, 250],
         "Bolt the anti-backlash nut to the -X face of the carriage, flange "
         "into the counterbore, four M3 on a 16 mm circle. Check the nut you "
         "actually received first: 22.0 flange, 3.5 thick, 16.0 bolt circle, "
         "10.6 body. A plain brass nut will bolt up and give away 0.1 to "
         "0.3 mm at every reversal, which lands on the foot of systole."),

        ("carriage", carr, C_CARRIAGE, [0, 0, 150],
         "The carriage is now a sub-assembly: two bushes and the nut. Hold "
         "it between the rails at the motor end, roughly on the screw axis. "
         "Nothing holds it there yet."),

        ("8 mm shafts x2", rods, C_STEEL, [-150, 0, 0],
         "Slide the two hardened 8 mm shafts in from the motor end, through "
         "the carriage bushes, through the rib and out the back, where "
         "12 mm stands proud for the locks. They must be "
         "HARDENED, not 304 stainless: a recirculating ball bush brinells "
         "soft shafting and the carriage then rumbles. Teardrop bores, so "
         "they print round and the shafts press rather than rattle."),

        ("rod stop x2", stops, C_STOP, [0, 0, 210],
         "This one goes on DURING the last step, not after it. Stop pushing "
         "each shaft when its end is in the gap just before the rib, slip a "
         "stop on there, then push the shaft home. The bore is closed, so "
         "there is no adding it later without pulling a shaft back out. "
         "Pinch the M3 x 12 and slide it up against the rib's front face. "
         "It is a plain collar with no screws into the frame and it does not "
         "need any: the carriage pushing the plunger also nudges the shafts "
         "forward, and this turns that into compression against the rib "
         "instead of pull on the lock's threads. With the lock on the back "
         "face the two SANDWICH the rib, so the shafts are pinned both ways "
         "by printed walls in compression. It costs 4 mm off the forward end "
         "of the carriage sweep, which is 0.48 mL out of 5.4 mL of priming "
         "headroom on a 0.50 mL beat."),

        ("rod lock x2", locks, C_LOCK, [110, 0, 0],
         "Slide a lock onto each shaft end and bolt it to the back of the "
         "rib with two M3 x 20, then pinch the M3 x 12 down through the top "
         "lug. Nothing else holds the shafts: the frame bores are a press "
         "fit, not a fixture, and the motor is 7 mm narrower than the rod "
         "spacing so it blocks nothing. The two walking directions are NOT "
         "symmetric. A shaft creeping BACK toward the motor drives the lock "
         "into the rib's back face, which is compression on a printed wall "
         "and cannot fail. A shaft creeping FORWARD toward the syringe pulls "
         "on the two M3 instead, and that is the weaker direction: about "
         "2000 N of thread pullout against a walking force under 0.1 N, so "
         "weaker here still means four orders of magnitude of margin. The "
         "screws are x 20 and not x 16 because 12 mm of them is spent "
         "crossing the lock; x 16 would leave 4 mm in the rib, x 20 leaves "
         "8, and the rib is 9 thick. Bore prints 8.15 on an 8.00 shaft: it "
         "is meant to slide on, the screw does the holding."),

        ("Tr8x8 lead screw", S.cyl_x(SCREW_D / 2, X_SCREW, z=S.SCREW_H),
         C_SCREW, [-230, 0, 0],
         "Feed the lead screw in from the motor end, through the nut, into "
         "the 608. Verify the lead BEFORE it goes in: mark the screw, turn "
         "it exactly one revolution, and measure the carriage. It must move "
         "8 mm. If it moves 2 mm you have a Tr8x2, which needs four times "
         "the rpm and will not do the job at 12 V."),

        ("5-8 mm coupler", ring_x(COUPLER_D, SHAFT_D, X_COUPLER, z=S.SCREW_H),
         C_STEEL, [-300, 0, 0],
         "Flexible coupler onto the screw, 8 mm bore to the screw and 5 mm "
         "to the motor. Leave the motor-side grub screws loose for now."),

        ("NEMA 17 pancake", motor(), C_MOTOR, [-380, 0, 0],
         "Four M3 through the motor plate into the pancake. Slide the shaft "
         "into the coupler and tighten both grub screws. The plate is full "
         "width and takes any NEMA 17, so the 48 mm motor bolts on in the "
         "same holes if the pancake ever runs short of torque."),

        ("plunger", both(
            S.cyl_x(S.PLUNGER_ROD_D / 2, (S.X_DISC, S.X_TIP - 6.0), z=S.SYR_H),
            S.cyl_x(S.DISC_D / 2, (S.X_DISC - S.DISC_T / 2,
                                   S.X_DISC + S.DISC_T / 2), z=S.SYR_H)),
         C_GLASS, [0, 0, 340],
         "The plunger is the piston. Everything upstream of it exists to move "
         "this 12.36 mm column of water 4.17 mm per beat, 70 percent of it "
         "inside 100 ms. Leave it long for now; the clamp goes on last."),

        ("syringe barrel", both(
            S.cyl_x(S.SYR_BARREL_D / 2, (S.X_RIB_BACK, S.X_TIP), z=S.SYR_H),
            S.box((S.X_RIB - S.SYR_FLANGE_T, S.X_RIB), (-10.0, 10.0),
                  (S.SYR_H - 10.0, S.SYR_H + 10.0))),
         C_GLASS, [0, 0, 300],
         "Snap the two split collars onto the barrel first, then lay the "
         "whole thing into the saddle with the finger flange hard against "
         "the end rib. The flange measures 2.0 and the rib was printed for "
         "2.5, so there is 0.5 mm of slack: the piston's reaction pushes the "
         "barrel forward into the rib, and the straps hold it."),

        ("split collars x2", collars, C_COLLAR, [0, 0, 240],
         "The collars are the only part that knows the barrel is 14.0 mm. "
         "They are SPLIT, slit at the top, and the bore is drawn 0.10 mm "
         "under the barrel so they snap on and stay put. Slit upward, so "
         "pressing the assembly into the saddle closes it rather than "
         "spreading it. If you ever change syringe, these two are the only "
         "parts you reprint."),

        ("saddle cap + ties", both(at(P["saddle_cap"],
                                      dx=S.X_RIB_BACK + 6.0, dz=S.SYR_H),
                                   zip_ties()),
         C_CAP, [0, 0, 180],
         "Drop the cap over the collars and run a zip tie through each pair "
         "of slots, down through the frame and back. Snug, not crushing: the "
         "collar wall is 0.93 mm and it is holding a syringe, not a driveshaft."),

        ("rod clamp", at(P["rod_clamp"], dx=CARR_AT), C_CLAMP, [0, 0, 130],
         "Last. Drop the plunger disc into the carriage pocket, lay the "
         "clamp tongue into the rod slot, and run two M3 x 16 down into the "
         "carriage. The bar should still stand about 1.25 mm proud when the "
         "tongue touches the rod; the bolts close that gap and pin the rod. "
         "This is what makes the whole drive independent of the thumb disc, "
         "which read 1.9 on a caliper, 2.0 on another syringe, and 1.71 on a "
         "micrometer."),
    ]


# Parts that travel with the carriage. Everything else is bolted to the frame.
MOVING = ("carriage", "LM8UU x2", "T8 anti-backlash nut", "rod clamp",
          "plunger")


EJECT_FRAC = 0.40            # share of the beat spent pushing, the rest refills


def beat(n=160):
    """PISTON DISPLACEMENT over one beat, normalised. Not a velocity trace.

    Worth saying plainly, because anyone who works with TCD reads a pulsatile
    curve as velocity and this is not one. This is where the plunger IS. It
    starts fully retracted, advances by one beat volume while it ejects, and
    comes back to retracted while the gravity side refills through the check
    valve. Over a beat it nets to zero travel, which is what lets the mean
    flow come from the head and the pulse come from the piston.

    The shape is not a measurement and not a fit to anyone's data: it is what
    the design's own constants describe. UPSTROKE_FRAC of the stroke is
    delivered inside UPSTROKE_S, which is the sharp systolic rise this
    phantom exists to reproduce. The rest of the ejection is slower, with a
    flattening where the dicrotic notch goes. A crank would give a pure
    sinusoid here, with no sharp rise and no way to ask for the notch, which
    is the whole argument for driving this with a lead screw.
    """
    import math

    def smooth(u):
        u = max(0.0, min(1.0, u))
        return u * u * (3.0 - 2.0 * u)

    period = 60.0 / BEAT_HR
    up = S.UPSTROKE_S / (EJECT_FRAC * period)     # upstroke, as a part of ejection
    out = []
    for i in range(n):
        t = i / float(n - 1)
        if t < EJECT_FRAC:
            u = t / EJECT_FRAC
            if u < up:
                y = S.UPSTROKE_FRAC * smooth(u / up)
            else:
                v = (u - up) / (1.0 - up)
                notch = 0.055 * math.exp(-((v - 0.22) / 0.085) ** 2)
                y = S.UPSTROKE_FRAC + (1.0 - S.UPSTROKE_FRAC) * smooth(v) - notch
        else:
            y = 1.0 - smooth((t - EJECT_FRAC) / (1.0 - EJECT_FRAC))
        out.append(round(max(0.0, min(1.0, y)), 4))
    return out


BEAT_HR = 60.0                                     # bpm for the animation


def main():
    items = parts()
    blobs, manifest, off = [], [], 0
    for k, (name, mesh, color, explode, text) in enumerate(items):
        v = np.asarray(mesh.vertices, np.float32).ravel()
        f = np.asarray(mesh.faces, np.uint32).ravel()
        manifest.append(dict(
            name=name, step=k, text=text, color=color, explode=explode,
            printed=color in (C_FRAME, C_CARRIAGE, C_COLLAR, C_CAP,
                              C_CLAMP, C_LOCK, C_STOP),
            moving=name in MOVING,
            mL=round(float(mesh.volume) / 1000.0, 2),
            vOff=off, nV=len(v) // 3, fOff=off + v.nbytes, nF=len(f) // 3))
        blobs += [v.tobytes(), f.tobytes()]
        off += v.nbytes + f.nbytes

    pts = np.vstack([m.vertices for _, m, _, _, _ in items])
    lo, hi = pts.min(axis=0), pts.max(axis=0)
    facts = dict(
        bore=S.BORE_A, beat_mm=round(S.BEAT_MM, 2), rpm=round(S.PEAK_RPM),
        beat_ml=S.BEAT_ML, upstroke_ms=round(S.UPSTROKE_S * 1000),
        travel=S.TRAVEL, soft=round(S.SOFT_TRAVEL, 1),
        dead_ml=round((S.X_RIB - (S.X_DISC + S.DISC_T / 2)) * S.BORE_A / 1000.0, 2),
        step_ul=round(S.SCREW_LEAD / 1600.0 * S.BORE_A, 2),
        barrel=S.SYR_BARREL_D, lead=S.SCREW_LEAD, amps=S.SET_I,
        vref=round(S.SET_I / S.TMC_FULL_SCALE * 2.5, 2),
        bbox=[round(x, 1) for x in (hi - lo)], hr=BEAT_HR,
        eject=EJECT_FRAC)

    os.makedirs(OUT, exist_ok=True)
    data = dict(parts=manifest, facts=facts, beat=beat(),
                center=[round(x, 2) for x in (lo + hi) / 2.0],
                span=round(float((hi - lo).max()), 1),
                bin=base64.b64encode(b"".join(blobs)).decode())
    p = os.path.join(OUT, "assembly.json")
    with open(p, "w", encoding="utf-8") as fh:
        json.dump(data, fh, separators=(",", ":"))
    print("wrote %s  %.1f KB, %d parts"
          % (p, os.path.getsize(p) / 1024.0, len(items)))
    for m in manifest:
        print("  %2d  %-22s %7.1f mL  %s"
              % (m["step"] + 1, m["name"], m["mL"],
                 "printed" if m["printed"] else "bought"))


if __name__ == "__main__":
    main()
