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
# Kevin is switching to the team's motor when it arrives, so this stops being
# four loose constants and becomes a table with a chooser. Swapping motors is
# then one line, and everything downstream recomputes instead of being
# inherited: torque, the 12 V speed ceiling, the phase reversal margin, and
# whether the VREF now on the pot is even legal for the new motor.
#
# That last one is the point. VREF is NOT a property of the driver. 0.556 V
# was derived for the pancake, and the same pot setting on a different motor
# can be anywhere from fine to over its rated current. A motor swap is a
# current decision, not a mechanical one, and the check below enforces it.
#
# th Ncm holding, i A/phase rated, r ohm/phase, l H/phase, body mm.
MOTORS = {
    "17HE08-1004S": dict(th=0.17, i=1.0, r=3.6, l=4.00e-3, body=23.0,
                         note="pancake. On the bench, turning, MS=8 confirmed"),
    "17HS19-2004S1": dict(th=0.59, i=2.0, r=1.4, l=3.00e-3, body=48.0,
                          note="bought. 3.5x the torque and 1.7x the back-EMF, "
                               "so it is the SLOWER motor on a 12 V supply"),
    # The team's motor. Copy its NAMEPLATE here before the swap, do not guess
    # and do not leave these at the pancake's numbers. Holding torque and
    # rated current are on the label; R and L are on the datasheet. Until
    # they are real this entry will fail its own checks, which is intended.
    "team-motor": dict(th=None, i=None, r=None, l=None, body=None,
                       note="UNKNOWN. Fill from the nameplate before fitting"),
}
MOTOR = "17HE08-1004S"

_m = MOTORS[MOTOR]
if _m["th"] is None:
    raise SystemExit(
        "MOTOR is %r and its nameplate has not been entered. Fill in "
        "MOTORS[%r] from the label before running anything: the phase "
        "current, the speed ceiling and the reversal margin all depend on it."
        % (MOTOR, MOTOR))
MOTOR_TH, MOTOR_I = _m["th"], _m["i"]
MOTOR_R, MOTOR_L = _m["r"], _m["l"]
DRIVE_V = 12.0
# Phase current, A rms. Not a free choice: it is pinned between two limits
# from opposite directions. Above roughly 0.45 A the phase cannot reverse
# inside the 1.35 ms a 446 rpm beat allows. Below 0.37 A the analog route runs
# out of road, because the TMC2209 datasheet says VREF under 0.5 V is "not
# recommended" and 0.5 V is 20% of a full scale that this board's 0.11 ohm
# sense resistors put at 1.77 A rms. So 0.375 A it is: the lowest current the
# pot can legally ask for, which still leaves a 2.4x reversal margin.
# VREF is MEASURED, not chosen. 0.53 V was the target; the pot on this board
# is coarse enough that it took six iterations to land, and where it landed is
# 0.556 V on an MDO3024 at 0.1 V/div, 1x probe, steady over five reads
# (2026-11-10). So the phase current is DERIVED from what the pot actually
# does, not asserted at the number the design asked for. 0.393 A sits inside
# the window this setting was pinned to from both sides: above about 0.45 A
# the phase reversal budget runs out at speed, below 0.37 A the TMC2209
# datasheet calls VREF "not recommended".
VREF_SET = 0.556                     # V, MEASURED at the pot wiper
SET_I = VREF_SET / 2.5 * 1.768       # 0.393 A rms, derived from the above
VREF_FLOOR = 0.5                     # datasheet: below this is not recommended
TMC_FULL_SCALE = 1.768               # A rms at VREF 2.5 V with R_sense 0.11
M3 = 3.4                             # M3 clearance
SCREW_LEAD = 8.0                     # Tr8x8
SCREW_ROOT_D = 6.2                   # for the whip calculation
BEAR_OD, BEAR_W = 22.0, 7.0          # 608
# ---------------------------------------------------------------- the T8 nut
# The nut is the joint between the screw and the carriage, so its mounting
# face is the one interface on this machine that a 98 minute print cannot get
# wrong and still be worth anything. Holes either line up or the nut cannot be
# fitted at all, and unlike the saddle bore there is no loose default to hide
# behind: a bolt circle is not a dimension you can draw generously.
#
# Two different parts are sold as "T8 anti-backlash nut". The brass one has a
# round 22 mm flange with FOUR M3 holes on a 16 mm bolt circle, and that is
# the pattern carriage() cuts. The POM spring-loaded one is a different body
# on a different flange, and the listing for the one on order (uxcell
# a24113000ux0399, ASIN B0DSZ4YYFS) never states its hole pattern. Its
# dimension block contradicts itself as well: "Nut Size: 15x14mm (L*W);
# 15x22x11mm (L*W*H)" with inch conversions that fit neither triple, and an
# attribute table calling the outside diameter 15 mm while the flange is 22.
#
# What that listing DOES settle is the number that mattered most: lead 8 mm,
# pitch 2 mm, 4 start. That is the constant the whole firmware hangs on.
#
# So the geometry below stays the brass pattern, because that is the one that
# has been checked, and the harness refuses to bless a carriage print while
# the fitted nut's interface is still unmeasured.
NUTS = {
    "brass-std": dict(flange_t=3.5, bc=16.0, holes=4, body_d=10.6,
                      body_l=15.0, spring_od=0.0,
                      note="round 22 mm flange, 4 x M3 on a 16 mm bolt "
                           "circle. What carriage() is drawn for and what "
                           "every clearance here was checked against"),
    "uxcell-pom": dict(flange_t=None, bc=None, holes=None, body_d=None,
                       body_l=None, spring_od=None,
                       note="uxcell a24113000ux0399 / B0DSZ4YYFS, POM spring "
                            "loaded, lead 8 mm CONFIRMED on the listing. A "
                            "22 mm flange is the only interface number "
                            "stated, and it happens to match the brass one, "
                            "which is encouraging and not proof. MEASURE: "
                            "flange thickness, hole count, hole spacing or "
                            "bolt circle, body diameter behind the flange, "
                            "body length, spring OD"),
}
NUT = "uxcell-pom"                   # what is on order
_nut = NUTS[NUT]
NUT_UNKNOWN = sorted(k for k, v in _nut.items() if k != "note" and v is None)

# What carriage() actually cuts. Deliberately the brass row rather than _nut,
# so an unmeasured nut cannot quietly resize a print. When the fitted nut is
# measured, fill its row in and point these four lines at _nut.
NUT_FLANGE_D, NUT_FLANGE_T, NUT_BC = 22.0, 3.5, 16.0
NUT_HOLES = 4
NUT_BODY_D = 10.6
NUT_CUT_FOR = "brass-std"

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
#
# AND IT IS A PROPERTY OF THE MATERIAL, not of the printer. The 0.24 above
# was measured in PLA. Switching to ABS changes it twice over: ABS shrinks
# roughly 0.7 percent on cooling against PLA's 0.3, so there is a term that
# scales with the hole, on top of the fixed extrusion encroachment that
# dominated in PLA. On a 15 mm LM8UU bore the extra is about 0.06 mm, which
# is a quarter of the whole PLA figure, and it lands on a SLIDING fit.
#
# Same discipline as the motor and nut tables: measured or None, never a
# plausible guess wearing a measured number's clothes.
MATERIALS = {
    "PLA": dict(fixed=0.24, per_mm=0.0, rho=1.24, nozzle=215, bed=60,
                note="MEASURED on fit coupon rev 2, 0.6 nozzle, 2026-11-09. "
                     "The frame, and everything printed before 2026-11-11"),
    "ABS": dict(fixed=None, per_mm=None, rho=1.04, nozzle=250, bed=100,
                note="UNMEASURED. Reprint fit_coupon in ABS and measure the "
                     "608 pocket and BOTH rod bores before anything fitted"),
}
MATERIAL = "ABS"                     # what is on the printer now
_mat = MATERIALS[MATERIAL]
MATERIAL_UNKNOWN = _mat["fixed"] is None

# Literature estimate, used ONLY so the coupon and the un-fitted parts can
# still be generated. Every fitted part is gated on the real measurement by
# check_drive.py, and this number is not it.
HOLE_SHRINK = _mat["fixed"] if _mat["fixed"] is not None else 0.24
HOLE_SHRINK_PER_MM = _mat["per_mm"] if _mat["per_mm"] is not None else 0.0
LM_OD, LM_L = 15.0, 24.0             # LM8UU

# ------------------------------------------------------------------- syringe
# Measured on the BH Supplies BH5LL, 5 mL luer lock, 2026-11-10.
SYR_BARREL_D = 14.0                  # barrel OD                   MEASURED
DISC_D = 16.5                        # plunger thumb disc diameter MEASURED
SYR_BARREL_L = 66.0                  # flange face to tip shoulder MEASURED
SYR_FLANGE_T = 2.0                   # finger flange thickness     MEASURED
DISC_T = 1.71                        # thumb disc thickness     MICROMETER
# Caliper read 1.9 and 2.0 on two syringes; a micrometer reads 1.71. The
# caliper was not scattering, it was overreading, which is what a caliper does
# on a thin moulded disc: the jaws span the raised rim or sit a degree out of
# square, and both errors are one-signed. The two "different" readings were
# one instrument being wrong by different amounts, not two discs differing.
# Worth recording because the old pocket was drawn from 2.0 and would have
# printed 2.16 around a 1.71 disc: 0.45 mm of slack, 54 uL, 11% of the beat.
PLUNGER_ROD_D = 12.0                 # across the cross            MEASURED

# Cross-check on the two measured numbers, because they constrain each other.
# A 120.0 mm2 bore is 12.36 mm across. Against a 14.0 mm OD that is a 0.82 mm
# barrel wall, which is exactly what a moulded polypropylene 5 mL barrel runs.
# The two measurements corroborate rather than merely coexist.

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
# itself came up for review. 16 was chosen to keep 3 mL and 5 mL both open for
# the price of 1 mm of clearance to the 608, which still leaves 1.0 mm.
# See syringe_choice.py for why 5 mL is probably the right answer.
#
# That choice is now vindicated by measurement, and by more than it was argued
# for. The 5 mL barrel was ESTIMATED at 12.5 mm when SADDLE_BORE was fixed. It
# measures 14.0. Had the saddle been sized snugly to the estimate, at 14.0 or
# even 14.5, the real syringe would not have entered the frame at all and four
# hours of printing would have been scrap. Erring large cost a thin collar.
# Erring tight would have cost the frame. That asymmetry was the whole reason
# for the rule, and this is the case that exercised it.
SADDLE_BORE = 16.0                   # frame and cap see this, never the barrel
COLLAR_L = 12.0

# 14.0 inside 16.0 leaves 1.0 mm of wall, under the 1.2 this once demanded.
# 1.2 was a guess at "two perimeters and a bit" and it fires correctly here,
# so the question is whether 1.0 is actually unprintable or merely thinner
# than the guess. It is printable, for reasons specific to this part:
#   * The collar prints standing on end, bore vertical. The wall is therefore
#     a plain vertical tube: no bridge, no overhang, no infill involved.
#   * At a 0.6 nozzle a 0.93 mm wall slices as two perimeters at 0.47 mm,
#     which is inside the extrusion width the slicer will accept. 0.78 mm,
#     which is what a generous slip fit would leave, does NOT: it lands
#     between one perimeter and two and comes out as gap fill.
#   * The load is the zip tie squeezing the collar into the saddle, so the
#     wall is in compression, where a thin printed wall is at its strongest.
# What 1.0 mm does cost is fit tolerance, and that is dealt with by splitting
# the ring rather than by thinning it further. See collar().
COLLAR_WALL_MIN = 0.9                # refuse to emit a collar thinner than this
COLLAR_GRIP = 0.10                   # printed bore this much UNDER the barrel
COLLAR_SLIT = 1.6                    # width of the split, at the top

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
FRONT_W = 2.0                        # carriage wall in front of the disc pocket
FIT = 0.35

# The thumb disc measured 2.0 on one syringe and 1.9 on another. The pocket
# that captures it used to be drawn at DISC_T + 0.4, which prints 2.16 after
# the bridge droops, so the usable window was 1.96 to 2.16: below it the disc
# rattles, above it the part will not assemble at all. Injection moulding does
# not hold a lot to 0.2 mm, so that design asked the supplier for a tolerance
# nobody promised, and 95 minutes of print rode on the answer.
#
# Worse, the slack it leaves is NOT removable by anything else in the drive.
# The anti-backlash nut takes out the screw's share. The preload spring takes
# out whatever is left between the frame and the carriage. Neither can touch
# this one, because it sits between the carriage and the PLUNGER, downstream
# of both. A spring pulling the carriage back seats the pocket's front face,
# and systole then has to cross the whole gap to get the rear face onto the
# disc, which is the worst possible place to spend it: the foot of the
# upstroke. Once the anti-backlash nut is fitted this becomes the single
# largest lost-motion term in the machine.
#
# So the pocket stops trying to be a fit. It is opened to swallow any disc in
# the range below, and the slack is removed somewhere else entirely, by
# clamping the plunger ROD to the carriage. The rod is 12 mm across and sits
# in an open slot, so it is a big accessible target. The disc offers a 1.65 mm
# annulus between the rod slot and its own rim, which is narrower than an M3
# head, so nothing can usefully bear on it.
DISC_T_MIN, DISC_T_MAX = 1.6, 2.4    # thumb discs the pocket must swallow
ROD_D_MIN = 11.0                     # smallest rod the clamp must still reach
M3_TAP = 2.6                         # self-tap pilot for M3 in PLA
CLAMP_L, CLAMP_W, CLAMP_T = 14.0, 29.0, 5.0
CLAMP_Y = 10.5                       # bolt centres, clear of the rod slot
# Tongue reaches the TOP of the smallest rod we would accept, so the bar
# always floats proud and the bolts do the clamping. Nothing is sized to a
# measurement, which is the whole point of the part.
CLAMP_TONGUE = DISC_D / 2.0 + 3.0 - ROD_D_MIN / 2.0 + 0.75
# ------------------------------------------------- the beat, and what it costs
# BH Supplies BH5LL, 5 mL luer lock, 100 pack. Bought 2026-11-09.
#
# The bore area is MEASURED, and not with calipers on the inside of a barrel,
# which has draft and is unreachable anyway. It is read between graduations,
# because that is the dimension the manufacturer actually guarantees:
#     BORE_A = (volume between two marks, in mm3) / (distance between them, mm)
# That gives the area the fluid sees, including whatever the moulding really
# is. Everything below derives from it, so this one number sets the design.
#
# Measured 2026-11-10 on the BH5LL: the 1 mL mark to the 4 mL mark is 25 mm.
#     3000 mm3 / 25 mm = 120.0 mm2,  a 12.36 mm effective bore
# That is 5% above the 114.2 nominal assumed before, which means a slightly
# shorter stroke, a slightly slower peak, and 2.1 mm less usable travel.
BORE_A = 3000.0 / 25.0               # mm2, 5 mL barrel, MEASURED

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
# As with FRAME_SADDLE_L below: the rib is printed. It was placed for a
# guessed 2.5 mm finger flange and the real flange measured 2.0, so the model
# keeps the measured truth in SYR_FLANGE_T and builds the rib where the rib
# actually is. The 0.5 mm difference is axial slack behind the flange, and it
# is slack in the safe direction. A flange THICKER than the as-built guess
# would not seat at all, which is what the check in check_drive.py asserts.
FRAME_FLANGE_T = 2.5                 # as built  <-- reprint required to change
X_RIB = X_CARR_FRONT + FRAME_FLANGE_T + 1.5
X_RIB_BACK = X_RIB + RIB_T
# The disc sits against the pocket's REAR face, which is the one that bears
# during systole, not against the front wall. With the pocket now opened to
# swallow DISC_T_MAX, that rear face is where it is regardless of how thick
# the disc turns out to be, so this no longer moves when a measurement does.
X_POCKET_BACK = X_CARR_FRONT - FRONT_W - (DISC_T_MAX + 0.3)
X_DISC = X_POCKET_BACK + DISC_T / 2                  # disc at full extension
X_TIP = X_RIB_BACK + SYR_BARREL_L

# The frame is PRINTED. It came off the bed on 2026-11-10 built to a guessed
# 56 mm barrel, and the barrel then measured 66. The model must keep telling
# the truth about the syringe, so SYR_BARREL_L is 66 and X_TIP moved with it,
# but the saddle, the strap slots and the end of the plate are features of a
# part that already exists and cannot follow. They are pinned here instead.
#
# Running the model with these free would quietly regenerate a frame 10 mm
# longer than the one on the bench and then certify it, which is the failure
# mode where a harness passes a part nobody has. Pinning them means every
# check below is run against the frame that actually exists.
#
# Changing FRAME_SADDLE_L means printing a new frame. Nothing else does.
FRAME_SADDLE_L = 56.0                # as built  <-- reprint required to change
X_SADDLE_END = X_RIB_BACK + FRAME_SADDLE_L
X_END = X_SADDLE_END + 6.0
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
    sad = box((X_RIB_BACK + 3.0, X_SADDLE_END - 6.0), (-13.0, 13.0), (0.0, SYR_H))
    sad = diff(sad, cyl_x(SADDLE_BORE / 2 + FIT,
                          (X_RIB_BACK + 2.0, X_SADDLE_END), z=SYR_H))
    sad = diff(sad, box((X_RIB_BACK + 2.0, X_SADDLE_END),
                        (-(SADDLE_BORE / 2 + FIT), SADDLE_BORE / 2 + FIT),
                        (SYR_H, SYR_H + 40)))
    for xs in (X_RIB_BACK + 8.0, X_SADDLE_END - 16.0):
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
    """Barrel adapter: SADDLE_BORE outside, the measured barrel inside.

    Split, with the slit at the top. Print two. They are what the zip-tie
    straps clamp down on, and they are the only part that knows the barrel OD.

    The split is not decoration. A solid ring at this wall has to hold a bore
    tolerance it cannot hold: 2.0 mm of diametral room has to cover BOTH the
    clearance that lets it slide on and the wall that carries the strap, and
    those two demands take the same material. Drawn loose the wall falls to
    0.78 mm and slices as gap fill; drawn tight the collar jams on a barrel
    that carries a moulding seam. Splitting it removes the trade entirely. The
    bore is drawn UNDER the barrel by COLLAR_GRIP so the collar snaps on and
    stays put while the syringe is handled, and the slit absorbs both the
    interference and whatever the real barrel does, so fit stops depending on
    print accuracy. It also means the collar comes off sideways rather than
    threading 12 mm over the luer tip, which is what you want at 2 a.m. when
    the syringe needs changing.

    Slit at the TOP because that is where the saddle is open. Pressing the
    assembly down into the channel closes the slit rather than spreading it.
    """
    wall = (SADDLE_BORE - SYR_BARREL_D) / 2.0
    if wall < COLLAR_WALL_MIN:
        raise SystemExit(
            "collar wall %.2f mm is below the %.2f mm minimum. The barrel is "
            "too close to SADDLE_BORE %.1f. Raise SADDLE_BORE and reprint the "
            "frame, or this syringe needs a different holder."
            % (wall, COLLAR_WALL_MIN, SADDLE_BORE))
    bore_r = (SYR_BARREL_D - COLLAR_GRIP + HOLE_SHRINK) / 2.0
    ring = cyl_x(SADDLE_BORE / 2.0, (0.0, COLLAR_L))
    ring = diff(ring, cyl_x(bore_r, (-1.0, COLLAR_L + 1.0)))
    ring = diff(ring, box((-1.0, COLLAR_L + 1.0),
                          (-COLLAR_SLIT / 2.0, COLLAR_SLIT / 2.0),
                          (bore_r - 1.0, SADDLE_BORE)))
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

    # Plunger capture: open-top slot for the rod, and a disc pocket sized to
    # SWALLOW the whole plausible disc range rather than to fit one reading.
    # The pocket no longer carries the waveform. The rod clamp does.
    xpf = CARRIAGE_L - FRONT_W                       # pocket front face
    xpb = xpf - (DISC_T_MAX + 0.3)                   # rear face, bears on systole
    # The slot has to drop below the axis by a full rod radius, not stop at it.
    body = diff(body, box((xpb - 20.0, x1 + 1),
                          (-(PLUNGER_ROD_D / 2 + 0.6), PLUNGER_ROD_D / 2 + 0.6),
                          (SYR_H - PLUNGER_ROD_D / 2 - 0.6, z1 + 1)))
    body = diff(body, cyl_x(DISC_D / 2 + 0.4, (xpb, xpf), z=SYR_H))
    body = diff(body, box((xpb, xpf), (-(DISC_D / 2 + 0.4), DISC_D / 2 + 0.4),
                          (SYR_H, z1 + 1)))

    # Two self-tap bolt holes for the rod clamp, outboard of the rod slot and
    # blind so the carriage keeps a solid top skin over them.
    for dy in (-CLAMP_Y, CLAMP_Y):
        body = diff(body, cyl_z(M3_TAP / 2, (z1 - 9.0, z1 + 1),
                                x=xpb - 10.0, y=dy))

    # Lighten the web between the nut and the fork, and anchor the spring.
    for dy in (-24.0, 24.0):
        body = diff(body, box((x0 + 5.0, x1 - 5.0), (dy - 6.0, dy + 6.0),
                              (SCREW_H + 11.0, SYR_H - 8.0)))
    body = union(body, cyl_z(SPRING_POST_D / 2, (z1, z1 + 8.0),
                             x=x0 + 6.0, y=HALF_W - 8.0))
    return body


def rod_clamp():
    """Pins the plunger rod to the carriage, so no disc dimension matters.

    A bar across the open rod slot with a tongue that reaches down onto the
    rod. The tongue is deliberately LONGER than the gap to the largest rod we
    would ever fit, so the bar always stands proud and the two M3 bolts do the
    clamping. Nothing here is sized to a measurement. That is the entire
    reason the part exists: the thumb disc read 1.9, then 2.0, then 1.71 on a
    micrometer, and a 95 minute print should not depend on which of those is
    right.

    Friction, not form, carries the load. Hand tight on two M3 in PLA puts
    roughly 20 N through the rod, and against polypropylene that is some 6 N
    of axial grip, comfortably over the 1.5 N of seal friction plus 0.8 N of
    hydraulic force the plunger actually sees. It also squares the rod in the
    slot, removing the 0.6 mm of lateral play the slot otherwise allows.

    Prints flat, tongue up, no supports.
    """
    xc = CARRIAGE_L - FRONT_W - (DISC_T_MAX + 0.3) - 10.0
    bar = box((xc - CLAMP_L / 2, xc + CLAMP_L / 2),
              (-CLAMP_W / 2, CLAMP_W / 2), (0.0, CLAMP_T))
    tongue = box((xc - CLAMP_L / 2, xc + CLAMP_L / 2),
                 (-(PLUNGER_ROD_D / 2 + 0.2), PLUNGER_ROD_D / 2 + 0.2),
                 (-CLAMP_TONGUE, 0.0))
    bar = union(bar, tongue)
    for dy in (-CLAMP_Y, CLAMP_Y):
        bar = diff(bar, cyl_z(M3 / 2, (-CLAMP_TONGUE - 1, CLAMP_T + 1),
                              x=xc, y=dy))
    return bar


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
            "rod_clamp": rod_clamp(),
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
