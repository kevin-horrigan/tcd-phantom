# -*- coding: utf-8 -*-
"""How high does the reservoir have to be, and what check valve can we afford?

The gravity leg sets the mean flow. The piston only adds the pulse on top of
it. So the mean flow has to be driven entirely by the reservoir height, and
every element between the reservoir and the return eats part of that height.
A check valve's cracking pressure is subtracted from the budget before any
flow happens at all, which is why it is not a detail.

The number that makes this urgent: a 30 cm head is 0.43 psi, and the only
luer-to-luer duckbill check valve Qosina sells cracks at 0.433 psi. It would
consume the entire driving pressure and the loop would not flow. Meanwhile the
check valves that turn up first in a search for "luer check valve" crack at
1 to 3 psi, which is three to seven times the whole budget.

    python head_budget.py

Fluid is IEC 61685 blood-mimicking fluid per Ramnarine 1998: 1037 kg/m3,
4.1 mPa.s. Water would be four times thinner and so four times kinder, which
is exactly why the budget must be run on the fluid we intend to use.
"""
import math

# ----------------------------------------------------------------- the fluid
RHO = 1037.0             # kg/m3, Ramnarine 1998 BMF
MU = 4.1e-3              # Pa.s
G = 9.80665

# ------------------------------------------------------------- the operating point
Q_MEAN = 250.0           # mL/min, gives 60 cm/s mean in a 3 mm lumen
Q_PEAK = 500.0           # mL/min at peak systole

# ------------------------------------------------------------------ the loop
# TOPOLOGY, from the diagram that went to the teams 2026-11-10:
#
#   constant-head jar -> R1 -> [P1, piston tees in] -> plenum -> 3 mm run
#     -> phantom -> R2 -> reservoir -> Omegaflex -> back up to the jar
#
# Three things in that diagram are not what this file used to assume, and all
# three were the diagram being right:
#
#  1. THE PLENUM IS UPSTREAM OF THE PHANTOM. It has to be. Its job is to round
#     the pulse before the Doppler sees it, and downstream of the lumen it
#     would be shaping what happens after the measurement.
#  2. THERE IS NO CHECK VALVE. R1, a measured length of narrow tubing, does
#     the blocking instead, and the trade that makes is worked out below.
#  3. THE JAR IS AT 1.2 m, not the 622 mm this file had computed. The extra
#     head is what pays for R1.
#
# name, length mm, bore mm, zone.  Zones, so nothing has to slice this list by
# position again: "up" is between the jar and the piston junction, "shape"
# carries the pulse to the block, "lumen" is Group 1, "down" is after it.
TANK_MM = 1200.0         # constant-head jar above the phantom centreline
# 4.0 mm, which is the bore of the 1/4 in OD tube in the RO kit. That kit was
# bought for its 3/8 in tube, which is the 6.35 mm trunk, and the 1/4 in reel
# in the same box turns out to be a better R1 than the 2.0 mm this file
# specified before it existed:
#
#   trim resolution   2.9 m of it instead of 182 mm, so 29 mm of length per
#                     1 % of head instead of 1.8. Sixteen times easier to cut
#                     to a number against the manometer.
#   AC blocking       wL/R is w*rho*d^2/(32*mu), which does not depend on
#                     length, so a wider bore carries more inertance per unit
#                     of resistance. At 1 Hz this one blocks 28 % harder than
#                     its DC resistance alone, against 2 % for the 2.0 mm.
#                     Better pulse rejection for the same head spent.
#
# It costs 37 mL of extra fluid sitting in the coil, and bench space for a
# 2.9 m coil. Both cheap. Coiling raises the resistance a few percent through
# Dean flow at Re 335, which is inside the trimming anyway.
R1_BORE = 4.0
FORWARD_FRAC = 0.65      # share of the piston's output that goes toward the block

SEGMENTS = [
    ("jar to R1",                     200.0, 6.35, "up"),
    ("R1, fixed resistance",            0.0, R1_BORE, "up"),   # length set below
    ("R1 to the piston junction P1",  150.0, 6.35, "up"),
    ("P1 to the plenum",              150.0, 6.35, "shape"),
    ("plenum to the 3 mm transition", 150.0, 6.35, "shape"),
    # The interface control document puts at least 150 mm of straight 3 mm
    # tubing ahead of the coupling, so flow arrives at the cast lumen already
    # developed: the M1 segment is 22 to 27 mm long and cannot supply its own
    # entrance length. It costs 8.4 mm of jar height per 10 mm of its length.
    # The diagram's "no tees in the straight run or the block" applies here:
    # nothing taps this segment, which is why P2 sits before it.
    ("settling run, 3 mm",            150.0, 3.00, "shape"),
    ("phantom lumen",                  80.0, 3.00, "lumen"),
    ("phantom to R2",                 200.0, 6.35, "down"),
    ("return to reservoir",           500.0, 6.35, "down"),
]


def seg_head(zone=None):
    """mm of head eaten at the mean flow, optionally for one zone only."""
    return sum(head_mm(r_poiseuille(L, d) * q_si(Q_MEAN))
               for _n, L, d, z in SEGMENTS if zone is None or z == zone)


def r1_length(bore=None, forward=None):
    """Length of narrow tubing that sends `forward` of the pulse downstream.

    The split is simpler than it looks. The piston injects at P1. Backward it
    sees R1 to a jar whose level is pinned by an overflow, so a fixed
    pressure. Forward it sees everything else to a reservoir, also fixed. Two
    resistances to two fixed pressures, so the flow divides as

        forward fraction = R1 / (R1 + R_down)

    and because the MEAN flow passes through both in series at the same rate,
    that ratio is also their share of the head:

        forward fraction = (head across R1) / (total head)

    So R1's job and R1's cost are the same number. Wanting more of the pulse
    to go the right way means spending more of the jar on R1, and the jar is
    the only place that money comes from.
    """
    d = bore or R1_BORE
    f = forward if forward is not None else FORWARD_FRAC
    target_pa = RHO * G * (f * TANK_MM) * 1e-3
    r_per_m = 128.0 * MU / (math.pi * (d * 1e-3) ** 4)
    return target_pa / q_si(Q_MEAN) / r_per_m * 1e3      # mm


def _set_r1():
    for i, (n, L, d, z) in enumerate(SEGMENTS):
        if n.startswith("R1,"):
            SEGMENTS[i] = (n, r1_length(), d, z)

# Cracking pressures actually on the market, psi, from the vendors' own pages.
VALVES = [
    ("Qosina 91050 barbed, 1/4 in ID",     0.075, "THE ONE. Matches the trunk"),
    ("Qosina 91054 barbed, 3/16 in ID",    0.055, "lowest of the barbed four"),
    ("Qosina 91053 barbed, 1/8 in ID",     0.061, "barb for a 3 mm run"),
    ("Qosina 91055 barbed, 3/8 in ID",     0.072, "if the trunk goes wider"),
    ("Qosina 91052 port, 1/8 in OD tube",  0.029, "NOT barbed. Push-on OD port"),
    ("industrialspec CVN/CVP/CVK",         0.217, "1/4 in barb, see note below"),
    ("Qosina 11584 / 80057 duckbill",      0.112, "0.130 in OD port, too small"),
    ("Qosina 80065 duckbill",              0.433, "FEMALE + MALE LUER LOCK, the trap"),
    ("Qosina 80089 / 80091 duckbill",      0.433, "barb"),
    ("typical inline luer check valve",    1.500, "luer, what a search returns"),
    ("ITW BOLUSSAFE diaphragm",            1.500, "luer, 1.5 to 5 psi"),
]

# This table used to carry "Qosina 9105x" as a family wildcard, with a note
# that Qosina quoted both 0.029 and 0.072 psi for it. Both of those were my
# problem, not Qosina's.
#
# There is no part called 9105x. The barbed high-flow family is four separate
# parts, 91050 / 91053 / 91054 / 91055, and a search for the wildcard returns
# nothing, which is exactly what it did to the person trying to buy one. The
# part that matches a 1/4 in trunk is 91050.
#
# The 0.029 figure was not a contradiction either. It belongs to 91052, which
# is a different valve: a push-on port for 1/8 in OD tubing, not a barb. Two
# numbers for two parts, read as two numbers for one part.
#
# The CVN/CVP/CVK entry is NOT the vendor's psi figure. industrialspec states
# "a very low cracking pressure: 6 inches H2O (water). This is equal to only
# 0.015 psi or 1.49 kPa". Two of those three agree and one does not: 6 inches
# of water IS 1.49 kPa, and 1.49 kPa is 0.217 psi, not 0.015. The psi number
# is low by a factor of fourteen. 0.217 is used above, because the two
# self-consistent units outvote the one that is not, and because a check valve
# chosen on a number that cheap would have been chosen for nothing. Worth
# confirming with them, but not worth designing around until they do.

PSI = 6894.757           # Pa per psi

# A ball resting on a seat, for the case where the catalog part cannot be
# bought. Densities in kg/m3 for balls sold by the bag.
# The seat is the O-ring the ball lands on, not a bare printed hole. These
# started out as 6.35 on a 3.00 mm seat, which is a bad pairing: cracking
# pressure is ball weight over SEAT area, so a small seat raises it, and a
# small seat also throttles the flow. Opening it to an AS568-009 at 5.28 mm
# improves both terms at once. ball_check.py draws the part.
BALL_D, SEAT_D = 6.35, 5.28      # mm
BALLS = [
    ("nylon", 1140.0), ("acetal / Delrin", 1410.0), ("PTFE", 2160.0),
    ("soda-lime glass", 2500.0), ("316 stainless", 7980.0),
]


def ball_crack(rho_ball, ball_d=None, seat_d=None):
    """Pa. Net buoyant weight of the ball over the seat orifice area.

    Statics, and that is the point: no vendor number, no tolerance stack, and
    nothing that can be wrong by a factor of fourteen the way a conversion on
    a product page can.
    """
    bd = (ball_d or BALL_D) * 1e-3
    sd = (seat_d or SEAT_D) * 1e-3
    vol = math.pi / 6.0 * bd ** 3
    return vol * (rho_ball - RHO) * G / (math.pi * (sd / 2.0) ** 2)



def q_si(ml_per_min):
    return ml_per_min * 1e-6 / 60.0


def r_poiseuille(length_mm, bore_mm):
    """Pa.s/m3 for laminar flow in a round tube."""
    L, d = length_mm * 1e-3, bore_mm * 1e-3
    return 128.0 * MU * L / (math.pi * d ** 4)


def reynolds(ml_per_min, bore_mm):
    d = bore_mm * 1e-3
    v = q_si(ml_per_min) / (math.pi * (d / 2.0) ** 2)
    return RHO * v * d / MU


def head_mm(pa):
    return pa / (RHO * G) * 1e3


# R1 has no length until the fluid properties and the flow are known, so it is
# filled in here, once, at import. Everything downstream of this line sees a
# complete SEGMENTS list.
_set_r1()


def report():
    A = print
    A("BLOOD-MIMICKING FLUID   %.0f kg/m3, %.1f mPa.s  (Ramnarine 1998 / IEC 61685)"
      % (RHO, MU * 1e3))
    A("  1 cm of this fluid is %.4f psi, so 30 cm is %.3f psi" %
      (RHO * G * 0.01 / PSI, RHO * G * 0.30 / PSI))
    A("")

    A("LOSSES AT %.0f mL/min MEAN  (Poiseuille, laminar, no fitting losses)" % Q_MEAN)
    A("  %-32s %7s %6s %10s %9s %7s" %
      ("segment", "len mm", "bore", "Pa", "mm head", "Re"))
    total = 0.0
    for name, L, d, _z in SEGMENTS:
        dp = r_poiseuille(L, d) * q_si(Q_MEAN)
        total += dp
        A("  %-32s %7.0f %6.2f %10.1f %9.1f %7.0f"
          % (name, L, d, dp, head_mm(dp), reynolds(Q_MEAN, d)))
    A("  %-32s %7s %6s %10.1f %9.1f" % ("PLUMBING TOTAL", "", "", total, head_mm(total)))

    peak = total * Q_PEAK / Q_MEAN
    re_peak = reynolds(Q_PEAK, 3.0)
    A("  at %.0f mL/min peak the same plumbing costs %.0f Pa (%.0f mm head), "
      "Re %.0f in the lumen" % (Q_PEAK, peak, head_mm(peak), re_peak))
    if re_peak > 2300:
        A("  -> TURBULENT at peak in the 3 mm lumen, so the peak figure is optimistic")
    A("")

    # -------------------------------------------------- R1 or a check valve
    down_mm = seg_head("shape") + seg_head("lumen") + seg_head("down")
    up_fixed = seg_head("up") - head_mm(
        r_poiseuille([L for n, L, d, z in SEGMENTS if n.startswith("R1,")][0],
                     R1_BORE) * q_si(Q_MEAN))
    A("R1, AND WHAT IT COSTS THE OTHER KNOB")
    A("  R1 blocks the pulse from running back up to the jar by being a big")
    A("  resistance. The split works out simply: looking back from P1 the")
    A("  piston sees R1 into a jar pinned by its overflow, looking forward it")
    A("  sees everything else into a reservoir, and both are fixed pressures.")
    A("  So the pulse divides as R1 / (R1 + R_down), and because the mean flow")
    A("  passes through both in series at the same rate, that ratio is also")
    A("  their share of the head. R1's JOB and R1's COST are one number.")
    A("")
    A("  %-9s %10s %10s %11s  %s" %
      ("forward", "R1 head", "R1 length", "left for R2", "note"))
    base = None
    for f in (0.50, 0.60, 0.65, 0.70, 0.80):
        h1 = f * TANK_MM
        L1 = r1_length(forward=f)
        left = TANK_MM - h1 - up_fixed - down_mm
        if base is None and abs(f - FORWARD_FRAC) < 1e-9:
            base = left
        A("  %-9s %7.0f mm %7.0f mm %8.0f mm  %s"
          % ("%.0f%%" % (100 * f), h1, L1, left,
             "fitted" if abs(f - FORWARD_FRAC) < 1e-9
             else ("R2 has nothing left" if left < 0 else "")))
    left_now = TANK_MM - FORWARD_FRAC * TANK_MM - up_fixed - down_mm
    A("")
    A("  Every point of pulse sent the right way is paid for out of R2, and")
    A("  R2 is the only knob that sets diastolic pressure. At the fitted %.0f%%"
      % (100 * FORWARD_FRAC))
    A("  it has %.0f mm of authority out of a %.0f mm jar." % (left_now, TANK_MM))
    A("")
    crack = head_mm(VALVES[0][1] * PSI)
    left_cv = TANK_MM - crack - up_fixed - down_mm
    A("  A CHECK VALVE BREAKS THE TRADE, and this is the argument for one that")
    A("  neither version of this design had made. A valve blocks backflow")
    A("  outright instead of dividing it, so R1 can go to nearly nothing:")
    A("    no valve, R1 at %.0f%%    %.0f%% of the stroke goes forward, "
      "R2 gets %.0f mm" % (100 * FORWARD_FRAC, 100 * FORWARD_FRAC, left_now))
    A("    %s" % VALVES[0][0])
    A("      R1 removed, valve costs %.0f mm   ~100%% forward, R2 gets %.0f mm"
      % (crack, left_cv))
    A("  That is %.0f%% more stroke delivered AND %.1fx the tuning range on the"
      % (100 * (1.0 - FORWARD_FRAC) / FORWARD_FRAC, left_cv / left_now))
    A("  one adjustable element in the loop, for a part that costs %.0f mm of"
      % crack)
    A("  head. R1's %.0f mm was never doing anything except blocking." % (FORWARD_FRAC * TANK_MM))
    A("")
    A("  WHAT BORE TO CUT R1 FROM, if it stays. Length goes as d^4, so the")
    A("  bore decides how finely the length can be trimmed by hand.")
    A("  %-10s %11s %13s %9s" % ("bore mm", "length mm", "mm per 1% head", "Re"))
    for d in (1.0, 1.6, 2.0, 2.5, 3.0):
        L1 = r1_length(bore=d)
        A("  %-10.1f %11.0f %13.1f %9.0f"
          % (d, L1, L1 / 100.0, reynolds(Q_MEAN, d)))
    A("  -> 1.0 mm is %.0f mm long and a millimetre of trim moves it %.0f%%."
      % (r1_length(bore=1.0), 100.0 / r1_length(bore=1.0)))
    A("     2.0 mm is %.0f mm and trims ten times finer. Cut long and shorten"
      % r1_length(bore=2.0))
    A("     it against the manometer, which is what 'a measured length' means.")
    A("")

    # -------------------------------------------------------- what R2 is
    import math as _m
    q_gpm = Q_MEAN * 1e-3 / 3.785412 * 60.0 / 60.0
    sg = RHO / 1000.0
    A("R2: WHAT TO BUY, AND WHY THE OBVIOUS PARTS ARE THE WRONG SIZE")
    A("  R2 has to sit around %.0f mm of head at %.0f mL/min and sweep either"
      % (left_now if False else 169.0, Q_MEAN))
    A("  side of it. In valve terms that is a flow coefficient:")
    A("  %-16s %9s %10s" % ("R2 at", "psi", "Cv wanted"))
    for mm in (50.0, 169.0, 300.0, 400.0):
        psi = RHO * G * mm * 1e-3 / PSI
        A("  %-16s %9.3f %10.3f"
          % ("%.0f mm of head" % mm, psi, q_gpm * _m.sqrt(sg / psi)))
    A("")
    A("  So R2 wants a Cv of roughly 0.09 to 0.25. Now the same list read")
    A("  backwards, which is the part that decides it:")
    A("  %-32s %8s %12s" % ("a valve whose full-open Cv is", "Cv", "gives"))
    for cv, what in ((0.03, "fine metering valve"), (0.1, "small needle valve"),
                     (0.3, "ordinary needle valve"), (1.0, "1/4 in ball valve"),
                     (4.0, "3/8 in ball valve")):
        mm = sg * (q_gpm / cv) ** 2 * PSI / (RHO * G) * 1e3
        A("  %-32s %8.2f %9.0f mm" % (what, cv, mm))
    A("")
    A("  A ball valve wide open gives nothing, so every setting you care")
    A("  about lives in the first few degrees of handle. That is not an")
    A("  opinion about ball valves, it is the %.0f mm in that row."
      % (sg * (q_gpm / 1.0) ** 2 * PSI / (RHO * G) * 1e3))
    A("  A fine metering valve is the opposite error: %.0f mm WIDE OPEN,"
      % (sg * (q_gpm / 0.03) ** 2 * PSI / (RHO * G) * 1e3))
    A("  which is more than the jar has, so the loop never runs.")
    A("  An ordinary needle valve at Cv 0.3 gives %.0f mm wide open and"
      % (sg * (q_gpm / 0.3) ** 2 * PSI / (RHO * G) * 1e3))
    A("  closes into the range. That is the right size.")
    A("")
    A("  THE PROBLEM: cheap needle valves do not publish Cv. So here is the")
    A("  test that needs no datasheet. Plumb it in WIDE OPEN and read the")
    A("  manometer. It should cost 30 to 50 mm of head at the working flow.")
    A("  Near zero and it is a ball valve in disguise. Hundreds and it is a")
    A("  metering valve and will not pass the flow.")
    A("")
    A("  AND THE OPTION THAT NEEDS NO VALVE AT ALL. R1 is a measured length")
    A("  of the kit's 1/4 in tube, and R2 can be the same thing with a screw")
    A("  clamp on it:")
    A("  %-12s %16s %16s" % ("R2 head", "of 4.0 mm tube", "of 6.35 mm tube"))
    for mm in (50.0, 169.0, 400.0):
        A("  %-12s %13.0f mm %13.0f mm"
          % ("%.0f mm" % mm, r1_length(bore=4.0, forward=mm / TANK_MM),
             r1_length(bore=6.35, forward=mm / TANK_MM)))
    A("  Cut about 190 mm of the 4 mm tube and it reads %.0f mm wide open,"
      % (190.0 / r1_length(bore=4.0, forward=1.0 / TANK_MM)))
    A("  which is the bottom of the sweep, and the clamp takes it up from")
    A("  there. Clamp the 6.35 mm trunk instead and the same 190 mm starts at")
    A("  %.0f mm, six times further from the target, so the pinch has to be"
      % (190.0 / r1_length(bore=6.35, forward=1.0 / TANK_MM)))
    A("  that much harder and it creeps that much more.")
    A("")
    A("  AND THE REASON THE CHEAP OPTION IS NOT A COMPROMISE: a sweep does")
    A("  not need a repeatable DIAL, it needs a known RESISTANCE at each")
    A("  point. The manometer gives the pressure and the gravimetric catch")
    A("  gives the flow, so R2 is measured every time it is moved. The axis")
    A("  of the map is measured resistance, not turns of a screw, and a")
    A("  clamp that drifts between points does not matter because the point")
    A("  is remeasured.")
    A("")

    # --------------------------------------------- how to set R1 and R2
    tee_mm = TANK_MM - seg_head("up")
    A("SETTING R1 AND R2: TWO READINGS, TWO KNOBS, AND THEY CLOSE")
    A("  The manometer is a clear tube teed into the trunk at the piston")
    A("  junction, open at the top, with the loop fluid standing in it. Its")
    A("  height IS the pressure there. And it happens to read the design")
    A("  parameter directly, which is worth seeing:")
    A("")
    A("      pressure at the tee = jar x R_down / (R_up + R_down)")
    A("      forward fraction    = R_up / (R_up + R_down)")
    A("                          = 1 - (manometer reading) / jar")
    A("")
    A("  So a manometer standing at %.0f mm out of %.0f means %.0f percent of"
      % (tee_mm, TANK_MM, 100.0 * (1.0 - tee_mm / TANK_MM)))
    A("  the pulse goes toward the block. The tube is not just a pressure")
    A("  gauge here, it is a direct readout of the split R1 exists to set.")
    A("  Lower reading means more goes forward.")
    A("")
    A("  Which closes the bring-up into two measurements against two knobs:")
    A("")
    A("    1. THE BEAKER sets the TOTAL. Catch the return for 60 s and trim")
    A("       R1 and R2 together until it gives %.0f mL/min. That fixes"
      % Q_MEAN)
    A("       R_up + R_down and nothing else.")
    A("    2. THE MANOMETER sets the SPLIT. Trim R1 against R2, keeping the")
    A("       flow where step 1 put it, until the tube reads %.0f mm."
      % tee_mm)
    A("")
    A("  They interact, so it takes a couple of passes, but each reading")
    A("  belongs to one quantity and the pair converges. Neither step needs")
    A("  a calibrated instrument: a beaker, a kitchen scale, a ruler.")
    A("")
    A("  And this is what makes the cheap R2 fine. The sweep records the")
    A("  MEASURED resistance at every point, from these same two readings,")
    A("  so a clamp that drifts between points costs nothing.")
    A("")

    A("WHAT EACH CANDIDATE VALVE COSTS, AND THE RESERVOIR HEIGHT IT FORCES")
    A("  The constriction is the only knob that sets diastolic pressure, so it")
    A("  needs to be the biggest term in the budget, not the leftovers. Below,")
    A("  'needs' is the height at which the constriction still owns half the head.")
    A("")
    A("  %-34s %6s %8s %9s %9s" %
      ("valve", "psi", "mm head", "needs mm", "at 300 mm"))
    for name, psi, note in VALVES:
        crack_pa = psi * PSI
        crack_mm = head_mm(crack_pa)
        # constriction gets half the head:  H = 2*(crack + plumbing)
        need = 2.0 * (crack_mm + head_mm(total))
        left = 300.0 - crack_mm - head_mm(total)
        flag = "%.0f mm left" % left if left > 0 else "WILL NOT FLOW"
        A("  %-34s %6.3f %8.1f %9.0f %9s" % (name, psi, crack_mm, need, flag))
    A("")
    for name, psi, note in VALVES:
        A("  %-34s %s" % (name, note))
    A("")

    A("CONCLUSION")
    plumb_mm = head_mm(total)
    best, best_mm = VALVES[0][1], head_mm(VALVES[0][1] * PSI)
    lumen_mm = head_mm(r_poiseuille(80.0, 3.0) * q_si(Q_MEAN))
    A("  Plumbing costs %.0f mm of head at the mean flow, and %.0f mm of that is"
      % (plumb_mm, lumen_mm))
    A("  the 3 mm lumen itself, which is the device under test and not")
    A("  negotiable. The budget is therefore mostly fixed cost.")
    left = 300.0 - plumb_mm - best_mm
    A("  The %.3f psi valve adds %.0f mm. A 300 mm reservoir then %s"
      % (best, best_mm,
         "leaves %.0f mm for the constriction," % left if left > 0 else
         "is %.0f mm SHORT of flowing at all, before" % -left))
    A("  the constriction, which is the only knob that sets diastolic")
    A("  pressure, so it wants to be the largest term, not a remainder.")
    A("  Put the reservoir at %.0f mm above the phantom and it is."
      % (2.0 * (plumb_mm + best_mm)))
    A("  Raising the reservoir is free. Buying a lower-cracking valve is not:")
    A("  the one part below 0.03 psi, Qosina 91052, is a push-on port for")
    A("  1/8 in OD tubing rather than a barb, so it does not fit this loop.")
    A("  Fix the head, not the valve.")
    A("")
    A("  The trap: the 0.433 psi part is the only luer-to-luer check valve in")
    A("  the catalog, so it is the one a search for a luer check valve finds")
    A("  first. It consumes %.0f mm on its own, more than a 300 mm reservoir"
      % head_mm(0.433 * PSI))
    A("  provides, and the loop would simply sit there. A barbed valve plus a")
    A("  barb-to-luer adapter costs a few dollars and works.")
    A("")
    A("IF THE PART CANNOT BE SOURCED: A GRAVITY BALL CHECK")
    A("  Worth pricing because the cracking pressure of a ball resting on a")
    A("  seat is pure statics, and it beats every valve above.")
    A("")
    A("      P = V_ball x (rho_ball - rho_fluid) x g / A_seat")
    A("")
    A("  The fluid is doing most of the work: it is 1037 kg/m3, so a plastic")
    A("  ball is nearly neutrally buoyant in it and weighs almost nothing.")
    A("  Mounted vertically with flow upward, the ball lifts off the seat on")
    A("  forward flow and drops back on reverse. %0.1f mm ball, %0.1f mm seat:"
      % (BALL_D, SEAT_D))
    A("  %-18s %8s %9s %9s %9s" % ("ball", "kg/m3", "psi", "mm head", "vs 91050"))
    for name, rho in BALLS:
        pa = ball_crack(rho)
        A("  %-18s %8.0f %9.4f %9.1f %8.1fx"
          % (name, rho, pa / PSI, head_mm(pa),
             head_mm(0.075 * PSI) / max(head_mm(pa), 1e-9)))
    A("")
    A("  Acetal on a %.2f mm seat costs %.1f mm of head against the 91050's %.0f."
      % (SEAT_D, head_mm(ball_crack(1410.0)), head_mm(0.075 * PSI)))
    A("  Stainless is the one to avoid: steel is eight times the fluid density")
    A("  and lands back among the catalog valves.")
    A("")
    A("  What this does NOT tell you is whether it reseats fast enough. That")
    A("  is a ball falling through a confined annulus, where the fluid it has")
    A("  to displace past itself dominates, and it is not worth modelling. In")
    A("  free fall a %0.1f mm acetal ball crosses a 3 mm lift in %.0f ms, so the"
      % (BALL_D, 1e3 * (2 * 0.003 / (G * (1 - RHO / 1410.0))) ** 0.5))
    A("  real figure is somewhere above that against a %.0f ms ejection. Reverse"
      % (0.40 * 1000.0))
    A("  flow helps it shut. Measure it, do not calculate it: put the valve on")
    A("  the bench, run the piston, and watch whether the return stroke pulls")
    A("  fluid back through it.")
    A("")
    A("  Specify the barb to the loop tubing, not the other way round. The")
    A("  91050/3/4/5 family covers 1/8 through 3/8 in ID, so whatever is bought")
    A("  for the loop has a matching valve in the same family.")


if __name__ == "__main__":
    report()
