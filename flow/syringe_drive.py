# -*- coding: utf-8 -*-
"""Parametric 3D-printable syringe drive for the Group 2 pulsatile flow loop.

Converts NEMA 17 rotation into plunger travel through a Tr8x8 lead screw.
Three printed parts:

    frame.stl        motor plate, two rod seats, an end rib that carries both
                     the 608 screw bearing and the syringe flange brace,
                     and a barrel saddle
    carriage.stl     rides the rods, carries the T8 nut low, forks the
                     plunger disc high
    saddle_cap.stl   clamps the barrel into the saddle

Design decisions this part embodies, all argued out on 2026-11-08:

  * The screw is OFFSET BELOW the syringe axis. On a shared axis the screw's
    far bearing and the syringe occupy the same space past the carriage, and
    there is nowhere to put the bearing. Offset, one end rib carries the 608
    low and the barrel slot high.
  * Far-end 608 at all. A Tr8x8 screw with a free end whips at 266 rpm over
    200 mm and the piston needs 446. Supported at both ends it clears 2000.
  * Plunger disc captured in a closed pocket, not pushed by a pad. The
    carriage must pull on the retract stroke or diastole is uncontrolled.
  * Spring anchors at both ends. A plain brass T8 nut has 0.1-0.3 mm of
    backlash, 1.2-3.5 percent of the stroke, surrendered at every reversal,
    which lands on the foot of the upstroke. Seal friction (1.5 N) beats the
    hydraulic force (0.17-0.79 N) so back-pressure will NOT preload it out.
    An extension spring over 1.5 N will. Use an anti-backlash nut instead and
    the anchors are just unused bosses.
  * Linear bearings, not a printed sliding channel. Plunger stick-slip is
    already the dominant waveform risk, and printed-on-printed friction adds
    to exactly the wrong term.
  * Baseplate carries through-holes so the rig can be bolted upright with the
    syringe tip UP. The interface control document requires gas to sweep out
    rather than collect, and a tip-down syringe traps it.

MEASURE THESE BEFORE PRINTING (defaults are BD 3 mL nominal):
    SYR_BARREL_D, SYR_BARREL_L, SYR_FLANGE_T, DISC_D, DISC_T, PLUNGER_ROD_D

    python syringe_drive.py
"""
import os
import numpy as np
import math
import trimesh

# ------------------------------------------------------------- motor / screw
MOTOR_SQ, MOTOR_BC = 42.3, 31.0      # NEMA 17 body, bolt circle
MOTOR_BOSS_D, MOTOR_BOSS_DEEP = 22.5, 2.5

# Two NEMA 17 were bought: 17HE08-1004S (pancake, 23 mm, 17 Ncm, 1.0 A, 3.6 ohm,
# 4.0 mH) and 17HS19-2004S1 (48 mm, 59 Ncm, 2.0 A, 1.4 ohm, 3.0 mH). The piston
# runs the PANCAKE. Both mount the same face, but the 59 Ncm motor's own
# back-EMF reaches 9.7 V at 446 rpm and its 12 V ceiling is 549 rpm, so it
# cannot be driven at piston speed on the supply we have. See MOTOR below.
MOTOR_TH, MOTOR_I, MOTOR_R, MOTOR_L = 0.17, 1.0, 3.6, 4.00e-3
DRIVE_V = 12.0
# Phase current, A rms. Not a free choice: it is pinned between two limits
# from opposite directions. Above roughly 0.45 A the phase cannot reverse
# inside the 1.35 ms a 446 rpm beat allows. Below 0.37 A the analog route runs
# out of road, because the TMC2209 datasheet says VREF under 0.5 V is "not
# recommended" and 0.5 V is 20% of a full scale that this board's 0.11 ohm
# sense resistors put at 1.77 A rms. So 0.375 A it is: the lowest current the
# pot can legally ask for, which still leaves a 2.4x reversal margin.
SET_I = 0.375                        # phase current we actually run, A rms
VREF_FLOOR = 0.5                     # datasheet: below this is not recommended
TMC_FULL_SCALE = 1.768               # A rms at VREF 2.5 V with R_sense 0.11
M3 = 3.4                             # M3 clearance
SCREW_LEAD = 8.0                     # Tr8x8
SCREW_ROOT_D = 6.2                   # for the whip calculation
BEAR_OD, BEAR_W = 22.0, 7.0          # 608
NUT_FLANGE_D, NUT_FLANGE_T, NUT_BC = 22.0, 3.5, 16.0
NUT_BODY_D = 10.6

# ------------------------------------------------------------------ guidance
ROD_D, ROD_SPACING = 8.0, 56.0       # two 8 mm smooth rods, centre to centre

# Measured on fit coupon rev 2, 0.6 nozzle, 0.24 mm layers, 2026-11-09.
# Every horizontal hole came out 0.24 mm smaller across than drawn, in both
# axes once the teardrop removed the sag: the 8.24 mm bores measured 8.0 wide,
# the teardrop 8.2 tall. That is about 0.12 mm of extrusion encroaching per
# wall, which is normal for a nozzle this size and is a constant, not a ratio.
#
# It is deliberately NOT compensated, for two reasons. The rod bores want a
# press fit, because nothing else retains the rods, so a bore that measures
# 8.00 for an 8.00 rod is the design working rather than failing. And the
# 608 pocket depends on the same shrink: drawn at 22.20 for a 22.00 bearing it
# would be a slip fit, and it only presses because it prints at about 21.96.
# A global slicer hole compensation would fix the first and ruin the second.
HOLE_SHRINK = 0.24                   # printed hole is this much under drawn
LM_OD, LM_L = 15.0, 24.0             # LM8UU

# ------------------------------------------------------------------- syringe
SYR_BARREL_D = 10.5                  # 3 mL barrel OD        <-- MEASURE
SYR_BARREL_L = 56.0                  # flange face to tip    <-- MEASURE
SYR_FLANGE_T = 2.5                   # finger flange         <-- MEASURE
DISC_D, DISC_T = 11.0, 2.2           # plunger thumb disc    <-- MEASURE
PLUNGER_ROD_D = 7.0                  # across the cross      <-- MEASURE

# The frame does not touch the barrel. It holds a pair of collars at a fixed
# 14 mm, and the collars hold the barrel. The reason is asymmetric risk: a
# channel cut too large only lets the barrel rattle, which a shim fixes, but a
# channel cut too small is 166 mL of scrap, and the barrel OD is the one
# number that decides which. Putting that number in a 2 mL part instead means
# a wrong guess costs ten minutes. It also means the rig takes a 1 mL or a
# 5 mL syringe later for the price of two new collars rather than a new frame,
# which matters because the beat volume is exactly the kind of thing a student
# team will want to change after the frame exists.
# 16 and not 14, which is what this was first set to. 14 fits a 3 mL barrel
# with a comfortable collar wall, and that looked fine until the syringe size
# itself came up for review. A 5 mL barrel is about 12.5 mm, which leaves a
# 0.75 mm collar wall at SADDLE_BORE 14: too thin to print. So a 14 mm frame
# silently decides that this rig is a 3 mL rig forever, and a 3 mL barrel is
# what forces the screw to 446 rpm. 16 keeps 3 mL and 5 mL both open for the
# price of 1 mm of clearance to the 608, which still leaves 1.0 mm.
# See syringe_choice.py for why 5 mL is probably the right answer.
SADDLE_BORE = 16.0                   # frame and cap see this, never the barrel
COLLAR_L = 12.0
COLLAR_WALL_MIN = 1.2                # refuse to emit a collar thinner than this

# -------------------------------------------------------------------- layout
TRAVEL = 45.0                        # 8.5 mm is the beat, the rest is priming
# Screw axis has to clear MOTOR_SQ/2 plus the baseplate, or the motor body
# hangs below the table and the lower two motor bolts land in the baseplate.
SCREW_H = 26.0                       # screw and rod axis above the baseplate
SYR_H = 46.0                         # syringe and plunger axis, offset above
BASE_T, WALL_T = 6.0, 7.0

# The rib is thicker than the other walls for one reason: a 608 is 7 mm wide,
# and a 7 mm rib makes the bearing pocket a through hole with no shoulder.
# Nothing then locates the bearing axially except how tight the print came
# out, which is not a design. BEAR_W + 2 leaves a 2 mm shoulder for it to
# seat against, with the screw passing through an 11 mm hole in that shoulder.
# Costs 2 mm of frame length and 2 mm of lead screw.
RIB_T = BEAR_W + 2.0
CARRIAGE_L = 30.0
COUPLER_L = 25.0
FRONT_W = 2.5                        # carriage wall in front of the disc pocket
FIT = 0.35
# ------------------------------------------------- the beat, and what it costs
# BH Supplies BH5LL, 5 mL luer lock, 100 pack. Bought 2026-11-09.
#
# The bore area is NOMINAL until measured, and there is a better way to measure
# it than calipering the inside of a barrel. Draw to the 5 mL mark, read the
# distance from the 1 mL mark to the 5 mL mark with calipers, and divide:
#     BORE_A = 4000 mm3 / (that distance in mm)
# That gives the area the fluid actually sees, including whatever the moulding
# really is, which is the number this model wants. Everything below derives
# from it, so correcting it here corrects the whole design.
BORE_A = 114.2                       # mm2, 5 mL barrel     <-- MEASURE, see above

SYR_CAPACITY_ML = 5.0                # label volume of the barrel
BEAT_ML = 0.5                        # per beat, the pulsatile component only
UPSTROKE_S = 0.100                   # systolic upstroke
UPSTROKE_FRAC = 0.70                 # share of the stroke taken during it

BEAT_MM = BEAT_ML * 1000.0 / BORE_A                       # stroke per beat
PEAK_RPM = (UPSTROKE_FRAC * BEAT_MM / SCREW_LEAD) / UPSTROKE_S * 60.0
# 3 mL gave 8.49 mm and 446 rpm, and that 446 is where every motor difficulty
# in this build came from. Speed falls as the square of the bore, so the 5 mL
# barrel costs nothing but resolution we had in excess. Nothing downstream
# hardcodes the number any more.

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stl")


# ------------------------------------------------------------------- helpers
def box(xr, yr, zr):
    ext = [hi - lo for lo, hi in (xr, yr, zr)]
    m = trimesh.creation.box(ext)
    m.apply_translation([(lo + hi) / 2.0 for lo, hi in (xr, yr, zr)])
    return m


def cyl_x(radius, xr, y=0.0, z=0.0, sections=96):
    """Cylinder with its axis along X, spanning xr."""
    return trimesh.creation.cylinder(
        radius=radius, sections=sections,
        segment=np.array([[xr[0], y, z], [xr[1], y, z]]))


def cyl_z(radius, zr, x=0.0, y=0.0, sections=96):
    return trimesh.creation.cylinder(
        radius=radius, sections=sections,
        segment=np.array([[x, y, zr[0]], [x, y, zr[1]]]))


def teardrop_x(radius, xr, y=0.0, z=0.0):
    """A horizontal hole that prints round, with its apex pointing up.

    A plain horizontal cylinder has an unsupported arch across the top. The
    last layers before the crown have nothing under them, droop, and the hole
    comes out oval: right across the width and short in the height. Measured
    on the fit coupon 2026-11-09, where the 608 pocket and the M3 hole were
    both fine and only the 8 mm rod bore was short vertically.

    A teardrop replaces the crown with a 45 degree point, so no layer ever
    overhangs the one below it by more than a printer can bridge. The round
    part keeps its diameter, which is what locates the rod.
    """
    base = cyl_x(radius, xr, y=y, z=z)
    apex = cyl_x(0.25, xr, y=y, z=z + radius * math.sqrt(2.0))
    return trimesh.convex.convex_hull(trimesh.util.concatenate([base, apex]))


def diff(a, *b):
    return trimesh.boolean.difference([a, *b], engine="manifold")


def union(*a):
    return trimesh.boolean.union(list(a), engine="manifold")


# --------------------------------------------------------------- X stations
X_MOTOR_FACE = 0.0
X_MOTOR_BACK = X_MOTOR_FACE + WALL_T
X_CARR_MIN = X_MOTOR_BACK + COUPLER_L + 2.0          # retract hard stop
X_CARR_MAX = X_CARR_MIN + TRAVEL
X_CARR_FRONT = X_CARR_MAX + CARRIAGE_L               # front face, fully extended

# One end rib does two jobs: 608 pocket low, syringe brace high. The syringe
# finger flange butts its -X face and so hangs back by its own thickness, which
# is what the carriage front face actually has to clear.
X_RIB = X_CARR_FRONT + SYR_FLANGE_T + 1.5
X_RIB_BACK = X_RIB + RIB_T
X_DISC = X_CARR_FRONT - FRONT_W - DISC_T / 2         # disc at full extension
X_TIP = X_RIB_BACK + SYR_BARREL_L
X_END = X_TIP + 6.0
HALF_W = ROD_SPACING / 2 + LM_OD / 2 + 5.0

SPRING_POST_D = 5.0
SCREW_SPAN = X_RIB_BACK - X_MOTOR_BACK

# How far the carriage may actually be driven back, which is NOT the frame's
# mechanical travel. The frame was laid out around a 3 mL barrel, where 45 mm
# of retraction was comfortably inside the barrel. A 5 mL barrel is wider, so
# the same 45 mm withdraws 5.14 mL from a barrel that holds 5.0, and the
# plunger seal would be dragged out of the open end. The frame is still fine,
# it is simply longer than it needs to be. The limit belongs in software.
DEAD_MM = X_RIB - (X_DISC + DISC_T / 2)        # residual travel at full extension
USABLE_MM = SYR_CAPACITY_ML * 1000.0 / BORE_A  # plunger travel the barrel allows
SOFT_TRAVEL = USABLE_MM - DEAD_MM              # never retract further than this

# Electronics shelf bolt holes, on the +Y edge beyond the carriage sweep and
# staggered to miss the strap slots. They also have to miss the end rib, which
# is a full-width wall, so neither can sit between X_RIB and X_RIB_BACK.
TRAY_HOLES_X = (X_RIB_BACK + 18.0, X_END - 8.0)


# --------------------------------------------------------------------- build
def frame():
    base = box((X_MOTOR_FACE, X_END), (-HALF_W, HALF_W), (0.0, BASE_T))

    # Motor plate, full width and not just the motor face. The rods sit at
    # +/- ROD_SPACING/2 = 28, and a plate only MOTOR_SQ/2 = 21.15 wide does
    # not reach them, so for several revisions the rods were held by the end
    # rib alone and cantilevered 113 mm back toward the motor. Full width
    # makes this a proper end wall that carries both rods and the motor.
    mp = box((X_MOTOR_FACE, X_MOTOR_BACK), (-HALF_W, HALF_W),
             (0.0, SCREW_H + MOTOR_SQ / 2))
    mp = diff(mp, cyl_x(MOTOR_BOSS_D / 2 + FIT,
                        (X_MOTOR_FACE - 1, X_MOTOR_FACE + MOTOR_BOSS_DEEP), z=SCREW_H))
    mp = diff(mp, cyl_x(13.0, (X_MOTOR_FACE - 1, X_MOTOR_BACK + 1), z=SCREW_H))
    for dy in (-MOTOR_BC / 2, MOTOR_BC / 2):
        for dz in (-MOTOR_BC / 2, MOTOR_BC / 2):
            mp = diff(mp, cyl_x(M3 / 2, (X_MOTOR_FACE - 1, X_MOTOR_BACK + 1),
                                y=dy, z=SCREW_H + dz))

    # End rib: 608 pocket on the screw axis, barrel slot on the syringe axis.
    rib = box((X_RIB, X_RIB_BACK), (-HALF_W, HALF_W), (0.0, SYR_H + 13.0))
    rib = diff(rib, cyl_x(BEAR_OD / 2 + 0.1,
                          (X_RIB - 1, X_RIB + BEAR_W), z=SCREW_H))
    rib = diff(rib, cyl_x(5.5, (X_RIB - 1, X_RIB_BACK + 1), z=SCREW_H))
    rib = diff(rib, box((X_RIB - 1, X_RIB_BACK + 1),
                        (-(SADDLE_BORE / 2 + FIT), SADDLE_BORE / 2 + FIT),
                        (SYR_H - SADDLE_BORE / 2 - FIT, SYR_H + 40)))

    body = union(base, mp, rib)
    for dy in (-ROD_SPACING / 2, ROD_SPACING / 2):
        body = diff(body, teardrop_x(ROD_D / 2 + 0.12,
                                     (X_MOTOR_FACE - 1, X_RIB_BACK + 1),
                                     y=dy, z=SCREW_H))

    # Barrel saddle: a half-round channel on the syringe axis, strap slots.
    sad = box((X_RIB_BACK + 3.0, X_TIP - 6.0), (-13.0, 13.0), (0.0, SYR_H))
    sad = diff(sad, cyl_x(SADDLE_BORE / 2 + FIT,
                          (X_RIB_BACK + 2.0, X_TIP), z=SYR_H))
    sad = diff(sad, box((X_RIB_BACK + 2.0, X_TIP),
                        (-(SADDLE_BORE / 2 + FIT), SADDLE_BORE / 2 + FIT),
                        (SYR_H, SYR_H + 40)))
    for xs in (X_RIB_BACK + 8.0, X_TIP - 16.0):
        for dy in (-11.5, 11.5):
            sad = diff(sad, box((xs, xs + 4.0), (dy - 1.6, dy + 1.6), (-1, SYR_H + 10)))
    body = union(body, sad)

    # Spring anchor post, and baseplate holes for upright mounting.
    body = union(body, cyl_z(SPRING_POST_D / 2, (BASE_T, BASE_T + 10.0),
                             x=X_MOTOR_BACK + 8.0, y=HALF_W - 6.0))
    for xs in (X_MOTOR_BACK + 14.0, X_END - 16.0):
        for dy in (-HALF_W + 5.5, HALF_W - 5.5):
            body = diff(body, cyl_z(2.6, (-1, BASE_T + 1), x=xs, y=dy))

    # Two more M3 self-tap holes for a bolt-on electronics shelf. There is no
    # room for the Pico and the driver anywhere inside the footprint: the
    # carriage sweeps X 34 to 109 across the full width with only 10 mm of air
    # under it, so anything on the baseplate in that band gets hit. A shelf
    # hanging off the +Y edge is the only place left. The shelf itself is not
    # designed yet and needs the breakout measured, but the holes cost nothing
    # now and cannot be added to a printed frame, which is the whole point.
    for xs in TRAY_HOLES_X:
        body = diff(body, cyl_z(2.6, (-1, BASE_T + 1), x=xs, y=HALF_W - 5.5))
    return body


def fit_coupon():
    """A 20 minute test of the only thing left that could spoil the frame.

    Every dimension in this model is checked against every other dimension.
    What none of that can check is whether this particular printer puts a
    22.1 mm hole where the file says 22.1 mm. The frame's 608 pocket and its
    rod bores are cut along X, and the frame prints lying on its baseplate,
    so those bores come out HORIZONTAL: bridged across the top, usually a few
    tenths undersize and slightly oval. That is the classic way a part that
    verifies perfectly still does not accept a bearing.

    So this is a slice of the end rib, same wall thickness, same bore sizes,
    same orientation on the bed. Print it, push a 608 and a length of 8 mm rod
    into it, and you know before you commit 162 mL. If they are tight, scale
    the holes or tune the printer, then reprint this and not the frame.

    The carriage is not represented here on purpose. It prints on its -X face,
    which stands its LM8UU bores up vertically, and vertical holes come out
    close to nominal. Its risk is low and its reprint is cheap.
    """
    y0, y1 = -(BEAR_OD / 2 + 15.0), ROD_SPACING / 2 + LM_OD / 2
    body = box((0.0, RIB_T), (y0, y1), (0.0, SCREW_H + BEAR_OD / 2 + 3.0))
    # 608 pocket, blind to the same depth as the rib, so the 2 mm shoulder
    # that seats the bearing gets tested too and not just the bore
    body = diff(body, cyl_x(BEAR_OD / 2 + 0.1, (-1.0, BEAR_W), z=SCREW_H))
    body = diff(body, cyl_x(5.5, (-1.0, RIB_T + 1.0), z=SCREW_H))
    # Two rod bores side by side: the teardrop the frame now uses, and a plain
    # round one, so the next coupon measures the fix against the thing it
    # replaced instead of against the last print.
    body = diff(body, teardrop_x(ROD_D / 2 + 0.12, (-1.0, RIB_T + 1.0),
                                 y=ROD_SPACING / 2, z=SCREW_H))
    body = diff(body, cyl_x(ROD_D / 2 + 0.12, (-1.0, RIB_T + 1.0),
                            y=-20.0, z=SCREW_H))
    # one M3 self-tap hole, to check that too
    body = diff(body, cyl_x(2.6 / 2, (-1.0, RIB_T + 1.0),
                            y=ROD_SPACING / 2, z=8.0))
    # A 9 mm thick wall standing 40 mm tall is tippy on its own. In the frame
    # the rib is braced by the baseplate, so give the coupon the same foot.
    # It is not decoration: a coupon that falls over mid print tests nothing.
    body = union(body, box((-6.0, RIB_T + 6.0), (y0, y1), (0.0, BASE_T)))
    return body


def collar():
    """Barrel adapter. Fixed 14 mm outside, measured barrel inside.

    Slides on from the tip end, so it is a solid ring and not a split one.
    Print two. They are what the zip-tie straps clamp down on.
    """
    wall = (SADDLE_BORE - SYR_BARREL_D) / 2.0
    if wall < COLLAR_WALL_MIN:
        raise SystemExit(
            "collar wall %.2f mm is below the %.2f mm minimum. The barrel is "
            "too close to SADDLE_BORE %.1f. Raise SADDLE_BORE and reprint the "
            "frame, or this syringe needs a different holder."
            % (wall, COLLAR_WALL_MIN, SADDLE_BORE))
    ring = cyl_x(SADDLE_BORE / 2.0, (0.0, COLLAR_L))
    ring = diff(ring, cyl_x(SYR_BARREL_D / 2.0 + 0.15, (-1.0, COLLAR_L + 1.0)))
    return ring


def carriage():
    x0, x1 = 0.0, CARRIAGE_L
    z0 = SCREW_H - LM_OD / 2 - 2.5
    z1 = SYR_H + DISC_D / 2 + 3.0
    body = box((x0, x1), (-HALF_W + 2.0, HALF_W - 2.0), (z0, z1))

    # Linear bearing bores, on the screw axis.
    for dy in (-ROD_SPACING / 2, ROD_SPACING / 2):
        body = diff(body, cyl_x(LM_OD / 2 + 0.15, (x0 - 1, x1 + 1), y=dy, z=SCREW_H))

    # T8 nut: flange counterbore on the -X face, body clearance through.
    body = diff(body, cyl_x(NUT_FLANGE_D / 2 + FIT,
                            (x0 - 1, x0 + NUT_FLANGE_T + FIT), z=SCREW_H))
    body = diff(body, cyl_x(NUT_BODY_D / 2 + FIT, (x0 - 1, x1 + 1), z=SCREW_H))
    for a in np.arange(45.0, 360.0, 90.0):
        t = np.radians(a)
        body = diff(body, cyl_x(M3 / 2, (x0 - 1, x1 + 1),
                                y=NUT_BC / 2 * np.cos(t),
                                z=SCREW_H + NUT_BC / 2 * np.sin(t)))

    # Plunger capture: open-top slot for the rod, closed pocket for the disc.
    xd = CARRIAGE_L - FRONT_W - DISC_T / 2
    # The slot has to drop below the axis by a full rod radius, not stop at it.
    body = diff(body, box((xd - 20.0, x1 + 1),
                          (-(PLUNGER_ROD_D / 2 + 0.6), PLUNGER_ROD_D / 2 + 0.6),
                          (SYR_H - PLUNGER_ROD_D / 2 - 0.6, z1 + 1)))
    body = diff(body, cyl_x(DISC_D / 2 + 0.4,
                            (xd - DISC_T / 2 - 0.2, xd + DISC_T / 2 + 0.2), z=SYR_H))
    body = diff(body, box((xd - DISC_T / 2 - 0.2, xd + DISC_T / 2 + 0.2),
                          (-(DISC_D / 2 + 0.4), DISC_D / 2 + 0.4),
                          (SYR_H, z1 + 1)))

    # Lighten the web between the nut and the fork, and anchor the spring.
    for dy in (-24.0, 24.0):
        body = diff(body, box((x0 + 5.0, x1 - 5.0), (dy - 6.0, dy + 6.0),
                              (SCREW_H + 11.0, SYR_H - 8.0)))
    body = union(body, cyl_z(SPRING_POST_D / 2, (z1, z1 + 8.0),
                             x=x0 + 6.0, y=HALF_W - 8.0))
    return body


def saddle_cap():
    cap = box((0.0, 26.0), (-13.0, 13.0), (0.0, 9.0))
    cap = diff(cap, cyl_x(SADDLE_BORE / 2 + FIT, (-1, 27.0), z=0.0))
    for dy in (-11.5, 11.5):
        cap = diff(cap, box((6.0, 10.0), (dy - 1.6, dy + 1.6), (-1, 10)))
    return cap


def syringe():
    """Not printed. Drawn so collisions are visible in the render."""
    barrel = cyl_x(SYR_BARREL_D / 2, (X_RIB_BACK, X_TIP), z=SYR_H)
    flange = box((X_RIB - SYR_FLANGE_T, X_RIB), (-10.0, 10.0),
                 (SYR_H - 10.0, SYR_H + 10.0))
    rod = cyl_x(PLUNGER_ROD_D / 2, (X_DISC, X_TIP - 6.0), z=SYR_H)
    disc = cyl_x(DISC_D / 2, (X_DISC - DISC_T / 2, X_DISC + DISC_T / 2), z=SYR_H)
    return union(barrel, flange, rod, disc)


def build():
    return {"frame": frame(), "carriage": carriage(),
            "saddle_cap": saddle_cap(), "collar": collar(),
            "fit_coupon": fit_coupon()}


def report(parts):
    f, c = parts["frame"], parts["carriage"]
    L = []
    A = L.append

    def envel(m):
        return tuple(m.bounds[1] - m.bounds[0]) + (m.volume / 1000.0, m.is_watertight)

    A("SYRINGE DRIVE, rev B")
    A("  frame             %.1f x %.1f x %.1f mm   %.1f mL   watertight %s" % envel(f))
    A("  carriage          %.1f x %.1f x %.1f mm   %.1f mL   watertight %s" % envel(c))
    A("")
    A("LAYOUT")
    A("  screw axis        %.1f mm above the baseplate" % SCREW_H)
    A("  syringe axis      %.1f mm, offset %.1f mm above the screw" % (SYR_H, SYR_H - SCREW_H))
    A("  end rib           608 pocket low, barrel slot high, one wall at X %.1f" % X_RIB)
    A("")
    A("TRAVEL")
    A("  carriage stroke   %.1f mm  (X %.1f to %.1f)" % (TRAVEL, X_CARR_MIN, X_CARR_MAX))
    A("  beat stroke       %.2f mm = %.1f mL, %.0f rpm peak at the screw"
      % (BEAT_MM, BEAT_ML, PEAK_RPM))
    A("                    %.0f%% of travel is priming headroom"
      % (100 * (TRAVEL - BEAT_MM) / TRAVEL))
    A("  SOFT LIMIT        retract at most %.1f mm, NOT the %.0f mm the frame"
      % (SOFT_TRAVEL, TRAVEL))
    A("                    allows. %.0f mm would withdraw %.2f mL from a %.1f mL"
      % (TRAVEL, TRAVEL * BORE_A / 1000.0, SYR_CAPACITY_ML))
    A("                    barrel and pull the plunger seal out of the end.")
    A("  prime volume      %.2f mL at the soft limit"
      % (SOFT_TRAVEL * BORE_A / 1000.0))
    A("  dead volume       %.2f mL left at full extension"
      % ((X_RIB - (X_DISC + DISC_T / 2)) * BORE_A / 1000.0))
    A("  resolution        %.4f mm/step at 1/8 = %.2f uL/step"
      % (SCREW_LEAD / 1600.0, SCREW_LEAD / 1600.0 * BORE_A))
    A("")
    A("SCREW SUPPORT")
    nc = 4.76e6 * SCREW_ROOT_D * 1.00 / (SCREW_SPAN ** 2)
    A("  bearing span      %.1f mm, motor at one end, 608 at the other" % SCREW_SPAN)
    A("  critical speed    %.0f rpm  (piston needs %.0f)  margin %.1fx"
      % (nc, PEAK_RPM, nc / PEAK_RPM))
    A("  cut the screw to  %.0f mm" % (SCREW_SPAN + 12.0))
    A("")
    A("MOTOR  17HE08-1004S pancake, 180 g, 5 mm shaft")
    kt = MOTOR_TH / (2.0 ** 0.5 * MOTOR_I)
    w = PEAK_RPM * 2.0 * math.pi / 60.0
    bemf = kt * w
    head = DRIVE_V - SET_I * MOTOR_R - bemf
    trev = 2.0 * MOTOR_L * SET_I / head
    budget = 1.0 / (2.0 * PEAK_RPM / 60.0 * 50.0)
    vref = SET_I / TMC_FULL_SCALE * 2.5
    A("  set phase current %.3f A rms  ->  TMC2209 Vref %.2f V" % (SET_I, vref))
    A("                    factory is Vref 1.2 V = 0.9 A, far too much to")
    A("                    reverse at speed. The pot turns CLOCKWISE to reduce.")
    if vref < VREF_FLOOR - 1e-9:
        A("  *** Vref %.2f V is below the %.2f V the datasheet recommends. Set"
          % (vref, VREF_FLOOR))
        A("      the current over UART instead, or accept %.3f A at the floor."
          % (VREF_FLOOR / 2.5 * TMC_FULL_SCALE))
    else:
        A("                    this is %.0f%% of the %.2f A full scale the"
          % (vref / 2.5 * 100.0, TMC_FULL_SCALE))
        A("                    0.11 ohm sense resistors set, and sits on the")
        A("                    0.5 V floor below which the datasheet says no.")
    A("  torque at %.2f A   %.4f Nm, %.1fx the %.4f Nm the piston needs"
      % (SET_I, MOTOR_TH * SET_I / MOTOR_I, MOTOR_TH * SET_I / MOTOR_I / 0.0098, 0.0098))
    A("  back-EMF at %-5.0f %.2f V of %.0f V, leaving %.2f V to drive current"
      % (PEAK_RPM, bemf, DRIVE_V, head))
    A("  phase reversal    %.2f ms against a %.2f ms budget, margin %.1fx"
      % (trev * 1e3, budget * 1e3, budget / trev))
    A("  12 V speed ceiling %.0f rpm, where back-EMF alone equals the supply"
      % (DRIVE_V / kt * 60.0 / (2 * math.pi)))
    A("")
    A("PRINT NOTES")
    A("  frame lies on its baseplate. The barrel saddle and the rib slot are")
    A("  both open upward, so no supports are needed anywhere.")
    A("  carriage prints on its -X face so the nut counterbore is the first layer")
    A("  bolt the baseplate upright with the syringe TIP UP so gas leaves the barrel")
    A("")
    A("SYRINGE DIMENSIONS, AND WHICH PART EACH ONE CAN RUIN")
    A("  Defaults are BD 3 mL nominal. The point of the table is that no")
    A("  syringe dimension reaches the frame any more, so a wrong guess")
    A("  costs a small reprint and never the big one.")
    A("  %-16s %7s  %-11s %s" % ("", "default", "lives in", "cost if wrong"))
    for n, v, part, cost in (
            ("SYR_BARREL_D", SYR_BARREL_D, "collar", "2 mL, 10 min"),
            ("SYR_BARREL_L", SYR_BARREL_L, "frame", "length only, see below"),
            ("SYR_FLANGE_T", SYR_FLANGE_T, "frame", "travel only, see below"),
            ("DISC_D", DISC_D, "carriage", "70 mL"),
            ("DISC_T", DISC_T, "carriage", "70 mL"),
            ("PLUNGER_ROD_D", PLUNGER_ROD_D, "carriage", "70 mL")):
        A("  %-16s %5.1f mm  %-11s %s" % (n, v, part, cost))
    A("  The frame's two are both benign and one-sided. SYR_BARREL_L only sets")
    A("  how far the baseplate runs past the tip, so a short guess leaves the")
    A("  tip overhanging and a long one leaves spare plate. SYR_FLANGE_T only")
    A("  sets the rib standoff: guess thin and you get a harmless gap, guess")
    A("  thick and you lose a little of the 45 mm travel, of which 81 percent")
    A("  is headroom anyway. Neither can scrap it.")
    A("")
    A("PRINT ORDER")
    A("  1. frame     %.0f mL, needs no syringe measurement at all" % (f.volume / 1000.0))
    A("  2. collar    x2, needs the barrel OD. Print after measuring, or")
    A("               print a test ring first and check it slides on.")
    A("  3. carriage  %.0f mL, needs the three plunger numbers" % (c.volume / 1000.0))
    A("  4. saddle_cap  clamps the collars, measurement-free")
    A("  Start the frame now. It is the long print and it is the one that no")
    A("  longer depends on anything uncertain.")
    A("")
    A("BUY TO COMPLETE")
    A("  2 x 8 mm smooth rod %.0f mm   2 x LM8UU   1 x 608 bearing" % (SCREW_SPAN + 10))
    A("  1 x 5-8 mm flexible coupler   1 x anti-backlash T8 nut (or a 5 N spring)")
    A("  M3 hardware for the motor face and the nut flange")
    return "\n".join(L)


if __name__ == "__main__":
    if not os.path.isdir(OUT):
        os.makedirs(OUT)
    parts = build()
    for n, m in sorted(parts.items()):
        m.export(os.path.join(OUT, n + ".stl"))
    print(report(parts))
    print("\nwrote %d STL to %s" % (len(parts), OUT))
