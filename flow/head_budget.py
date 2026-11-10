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
    ("tee to phantom inlet",          200.0, 6.35),
    ("phantom lumen",                  80.0, 3.00),   # 3 mm, 40 mm half-run x2
    ("phantom to plenum",             150.0, 6.35),
    ("plenum to constriction",        150.0, 6.35),
    ("return to reservoir",           400.0, 6.35),
]

# Cracking pressures actually on the market, psi, from the vendors' own pages.
VALVES = [
    ("Qosina 9105x high-flow barbed",      0.072, "barb 1/8 to 3/8 in ID. THE ONE"),
    ("Qosina 11584 / 80057 duckbill",      0.112, "0.130 in OD port, too small"),
    ("Qosina 80065 duckbill",              0.433, "FEMALE + MALE LUER LOCK, the trap"),
    ("Qosina 80089 / 80091 duckbill",      0.433, "barb"),
    ("typical inline luer check valve",    1.500, "luer, what a search returns"),
    ("ITW BOLUSSAFE diaphragm",            1.500, "luer, 1.5 to 5 psi"),
]

# Qosina quotes the 9105x family at 0.029 psi on the product page and 0.072 psi
# in the same page's technical features. 0.072 is used above because a budget
# built on the kinder of two conflicting vendor numbers is not a budget. Ask
# Qosina which is current before the drawing says so.

PSI = 6894.757           # Pa per psi


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
    A("  The %.3f psi valve adds %.0f mm. At a 300 mm reservoir that leaves"
      % (best, best_mm))
    A("  %.0f mm for the constriction, which is the only knob that sets"
      % (300.0 - plumb_mm - best_mm))
    A("  diastolic pressure, so it wants to be the largest term, not a remainder.")
    A("  Put the reservoir at %.0f mm above the phantom and it is."
      % (2.0 * (plumb_mm + best_mm)))
    A("  Raising the reservoir is free. Buying a lower-cracking valve is not,")
    A("  and below about 0.03 psi the parts stop existing. Fix the head.")
    A("")
    A("  The trap: the 0.433 psi part is the only luer-to-luer check valve in")
    A("  the catalog, so it is the one a search for a luer check valve finds")
    A("  first. It consumes %.0f mm on its own, more than a 300 mm reservoir"
      % head_mm(0.433 * PSI))
    A("  provides, and the loop would simply sit there. A barbed valve plus a")
    A("  barb-to-luer adapter costs a few dollars and works.")
    A("")
    A("  Specify the barb to the loop tubing, not the other way round. The")
    A("  9105x family covers 1/8 through 3/8 in ID, so whatever the team buys")
    A("  for the loop has a matching valve in the same family.")


if __name__ == "__main__":
    report()
