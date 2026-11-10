# -*- coding: utf-8 -*-
"""Does the syringe's own luer tip blunt the systolic upstroke?

    python piston_path.py

There are two fluid paths in this rig and they are not the same path, which
is what makes the luer question easy to get wrong.

    MEAN PATH    reservoir -> check valve -> tee -> phantom -> constriction
                 Driven by 30 cm of head, about 0.43 psi, and that is all
                 there is. Every restriction here is subtracted from a budget
                 that cannot be topped up. A luer here is a real problem and
                 that is why the check valve is specified barbed.

    PULSE PATH   syringe -> luer tip -> adapter -> short tube -> tee
                 Driven by the piston, which is a positive displacement
                 source with a motor carrying 6.5x the torque it needs. A
                 restriction here does NOT cost mean flow and does NOT eat the
                 head. It costs the sharpness of the upstroke, through the RC
                 time constant it forms with whatever compliance is in the
                 branch. Compliance here means trapped air, mostly.

So the right question for the luer is not "how much pressure does it drop",
it is "what time constant does it make". The upstroke is 100 ms and the sharp
systolic rise is the feature this phantom exists to reproduce, so we want the
branch time constant well under that.
"""
import math

RHO, MU = 1037.0, 4.1e-3         # IEC 61685 blood-mimicking fluid
V_BEAT = 0.5e-6                  # m3 per beat
UPSTROKE = 0.100                 # s
UP_FRAC = 0.70
Q_PULSE = V_BEAT * UP_FRAC / UPSTROKE      # m3/s during the upstroke
P_ATM = 101325.0

# bore mm, length mm, what it is
PATHS = [
    (1.2, 10.0, "luer tip at the ISO 7886-1 minimum"),
    (1.6, 10.0, "luer tip, typical"),
    (2.0, 10.0, "luer tip, generous"),
    (3.2, 25.0, "1/8 in barb, tip cut off and barb bonded"),
    (4.0, 25.0, "5/32 in barb"),
    (6.35, 150.0, "1/4 in tube, the rest of the branch"),
]

AIR = [(0.00, "purged, nothing but liquid"),
       (0.05, "a bubble you would not notice"),
       (0.20, "a bubble you would notice"),
       (1.00, "did not bleed the line")]


def r_tube(bore_mm, len_mm):
    d, L = bore_mm * 1e-3, len_mm * 1e-3
    return 128.0 * MU * L / (math.pi * d ** 4)


def main():
    print("PULSE PATH, %.2f mL in a %.0f ms upstroke = %.2f mL/s\n"
          % (V_BEAT * 1e6, UPSTROKE * 1e3, Q_PULSE * 1e6))

    print("%-42s %7s %8s %8s %9s" %
          ("element", "bore", "v m/s", "Re", "dP Pa"))
    total_r = 0.0
    for d, L, what in PATHS:
        R = r_tube(d, L)
        a = math.pi * (d * 1e-3 / 2.0) ** 2
        v = Q_PULSE / a
        re = RHO * v * (d * 1e-3) / MU
        # sudden contraction entry loss, which at these speeds is not small
        dp = R * Q_PULSE + 0.45 * 0.5 * RHO * v * v
        print("%-42s %5.2f mm %8.2f %8.0f %9.0f" % (what, d, v, re, dp))
    print("\n  dP includes a 0.45 entry-loss coefficient, because at a few")
    print("  metres per second the sudden contraction costs as much as the")
    print("  viscous term. Re stays under 2300 everywhere, so no turbulence.")

    # The branch a real build would have: syringe luer + adapter + short tube.
    build = [(1.6, 10.0), (4.0, 25.0), (6.35, 150.0)]
    R_branch = sum(r_tube(d, L) for d, L in build)
    print("\nAS BUILT, luer tip + adapter + 150 mm of 1/4 in tube")
    print("  branch resistance %.3g Pa.s/m3" % R_branch)

    print("\n  %-34s %10s %10s  %s" % ("trapped air", "C m3/Pa", "tau ms", ""))
    for ml, what in AIR:
        if ml == 0.0:
            print("  %-34s %10s %10s  %s"
                  % (what, "~0", "~0", "nothing to charge"))
            continue
        C = ml * 1e-6 / P_ATM          # isothermal gas compliance
        tau = R_branch * C
        frac = tau / UPSTROKE * 100.0
        verdict = ("negligible" if frac < 2 else
                   "visible rounding" if frac < 10 else
                   "RUINS THE UPSTROKE")
        print("  %-34s %10.3g %10.2f  %.0f%% of the upstroke, %s"
              % (what, C, tau * 1e3, frac, verdict))

    # Trapped air is not the only compliance, and usually not the largest.
    # A thin-walled tube stores volume as it balloons: C = pi d^3 L / (4 E t).
    print("\n  TUBING COMPLIANCE, which is the term that actually bites")
    print("  %-30s %8s %10s %10s  %s"
          % ("tube", "E MPa", "C m3/Pa", "tau ms", ""))
    for name, E, t, L in (("silicone, soft, 150 mm", 2.0e6, 1.6e-3, 0.150),
                          ("silicone, soft, 1 m", 2.0e6, 1.6e-3, 1.000),
                          ("Tygon, stiff, 150 mm", 10.0e6, 1.6e-3, 0.150),
                          ("Tygon, stiff, 1 m", 10.0e6, 1.6e-3, 1.000)):
        d = 6.35e-3
        C = math.pi * d ** 3 * L / (4.0 * E * t)
        tau = R_branch * C
        frac = tau / UPSTROKE * 100.0
        print("  %-30s %8.1f %10.3g %10.2f  %.0f%% of the upstroke, %s"
              % (name, E * 1e-6, C, tau * 1e3, frac,
                 "fine" if frac < 2 else
                 "visible rounding" if frac < 10 else "RUINS THE UPSTROKE"))
    print("  150 mm of soft silicone stores about as much as a 1 mL bubble.")
    print("  A metre of it stores seven times that, which is why the loop")
    print("  spec says stiff tubing kept short. The luer is not the lever here.")

    # How much does the luer itself contribute to that branch?
    R_luer = r_tube(1.6, 10.0)
    print("\n  Of that branch resistance, the luer tip is %.0f%%."
          % (R_luer / R_branch * 100.0))
    R_cut = sum(r_tube(d, L) for d, L in [(3.2, 25.0), (6.35, 150.0)])
    print("  Cutting the tip off and bonding a 1/8 in barb would take the")
    print("  branch to %.3g, a factor of %.1f. It changes tau on the 1 mL"
          % (R_cut, R_branch / R_cut))
    print("  air case from %.1f to %.1f ms."
          % (R_branch * 1e-6 / P_ATM * 1e3, R_cut * 1e-6 / P_ATM * 1e3))

    print("\nVERDICT")
    print("  The luer tip dominates the branch, but the branch is driven by a")
    print("  piston with torque to spare, so what it buys us is a time")
    print("  constant rather than a loss. With the line bled, there is almost")
    print("  no compliance to charge and the tip does not matter. With air in")
    print("  the line, the tip makes a bad situation worse, but the air is the")
    print("  problem and bleeding it is free.")
    print("\n  So: keep luer OUT of the mean path, where it would eat head")
    print("  that cannot be replaced. Tolerate exactly one luer joint at the")
    print("  syringe tip, where it costs a few ms. Bleed the line properly and")
    print("  mount the syringe TIP UP so gas leaves on its own.")


if __name__ == "__main__":
    main()
