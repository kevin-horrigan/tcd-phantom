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
# name, length mm, bore mm.  Bore 0 means a fixed pressure drop, given below.
SEGMENTS = [
    ("feed tube, reservoir to valve", 400.0, 6.35),   # 1/4 in ID, 1/4 in = 6.35
    ("check valve port",               15.0, 3.30),   # Qosina 0.130 in port
    ("valve to piston tee",           150.0, 6.35),
    ("tee to 3 mm transition",        150.0, 6.35),
    # The interface control document puts at least 150 mm of straight 3 mm
    # tubing ahead of the coupling, so flow arrives at the cast lumen already
    # developed: the M1 segment is 22 to 27 mm long and cannot supply its own
    # entrance length. This budget used to run 6.35 mm right up to the inlet
    # and step straight into the lumen, which left the single most expensive
    # piece of tubing on the bench out of the sum. It costs 8.4 mm of tank
    # height per 10 mm of its length. See feed_tubing.py.
    ("settling run, 3 mm",            150.0, 3.00),
    ("phantom lumen",                  80.0, 3.00),   # 3 mm, 40 mm half-run x2
    ("phantom to plenum",             150.0, 6.35),
    ("plenum to constriction",        150.0, 6.35),
    ("return to reservoir",           400.0, 6.35),
]

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
BALL_D, SEAT_D = 6.35, 3.00      # mm
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
    for name, L, d in SEGMENTS:
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
    A("  Acetal on a 3 mm seat costs %.0f mm of head against the 91050's %.0f."
      % (head_mm(ball_crack(1410.0)), head_mm(0.075 * PSI)))
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
