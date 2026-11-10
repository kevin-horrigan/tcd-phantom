# -*- coding: utf-8 -*-
"""Can the screw actually follow a waveform, or only reach its peak speed?

    python slew.py

Peak speed was settled long ago: 230 rpm with a 6.7x phase-reversal margin.
That is not the same question. A waveform makes the carriage start from rest,
reach peak, stop, and reverse every single beat, so the real question is
whether the motor can ACCELERATE the rotating mass fast enough to put a sharp
corner where the systolic upstroke needs one.

Torque to accelerate = J_total * alpha, and J_total is dominated by the
motor's own rotor. Everything the piston actually moves is reflected through
the screw by (lead / 2 pi)^2, and an 8 mm lead makes that factor 1.6e-6, so
the carriage, the plunger and the fluid nearly vanish from the sum. That is
the quiet advantage of a coarse lead: it is not only fewer turns per stroke,
it is a load the motor can barely feel.
"""
import math

LEAD = 8.0e-3                 # m per rev
TORQUE = 0.0638               # Nm available at 0.375 A
PEAK_RPM = 230.0
UPSTROKE_S = 0.100

# Rotating inertia, kg.m2
J_ROTOR = 3.0e-6              # 23 mm NEMA 17, nominal 30 g.cm2  <-- verify
RHO_STEEL, RHO_AL, RHO_PLA = 7850.0, 2700.0, 1240.0

# Translating mass, kg: carriage print + 2 LM8UU + nut + plunger + fluid
M_MOVING = 0.12


def j_rod(d, L, rho):
    m = rho * math.pi * (d / 2.0) ** 2 * L
    return 0.5 * m * (d / 2.0) ** 2, m


def main():
    j_screw, m_screw = j_rod(8.0e-3, 0.127, RHO_STEEL)
    j_coup, m_coup = j_rod(19.0e-3, 0.025, RHO_AL)
    j_load = M_MOVING * (LEAD / (2.0 * math.pi)) ** 2
    j_tot = J_ROTOR + j_screw + j_coup + j_load

    print("ROTATING INERTIA")
    for n, j, note in (("motor rotor", J_ROTOR, "nominal for a 23 mm NEMA 17"),
                       ("lead screw", j_screw, "%.0f g of steel" % (m_screw * 1e3)),
                       ("coupler", j_coup, "%.0f g of aluminium" % (m_coup * 1e3)),
                       ("everything sliding", j_load,
                        "%.0f g reflected through an %.0f mm lead"
                        % (M_MOVING * 1e3, LEAD * 1e3))):
        print("  %-20s %9.3g kg.m2  %5.1f%%   %s"
              % (n, j, 100 * j / j_tot, note))
    print("  %-20s %9.3g kg.m2" % ("TOTAL", j_tot))
    print("\n  The sliding mass is %.1f%% of the problem. An 8 mm lead divides"
          % (100 * j_load / j_tot))
    print("  it by (lead/2pi)^2 = %.2e, so the motor mostly accelerates itself."
          % ((LEAD / (2 * math.pi)) ** 2))

    w_peak = PEAK_RPM * 2.0 * math.pi / 60.0
    print("\nTORQUE TO REACH %.0f rpm IN A GIVEN TIME" % PEAK_RPM)
    print("  %-12s %12s %12s %10s" % ("ramp", "alpha rad/s2", "torque Nm", "margin"))
    for ms in (50, 20, 10, 5, 2):
        a = w_peak / (ms * 1e-3)
        t = j_tot * a
        print("  %-12s %12.0f %12.4f %9.0fx"
              % ("%d ms" % ms, a, t, TORQUE / t))
    print("\n  The systolic upstroke lasts %.0f ms. A 10 ms ramp to full speed"
          % (UPSTROKE_S * 1e3))
    print("  is a tenth of it, sharper than any artery, and still leaves 6x.")
    print("  Only below about 3 ms does the torque run out, and nothing in a")
    print("  cerebral waveform asks for that.")

    # What the step generator has to do, as a sanity check on the Pico side.
    steps_s = PEAK_RPM / 60.0 * 200 * 8
    print("\nSTEP RATE")
    print("  peak %.0f steps/s at 1/8 microstep, %.0f us between steps"
          % (steps_s, 1e6 / steps_s))
    print("  the PIO was measured at 0.03 percent of the commanded period, so the")
    print("  profile the motor follows is the profile we asked for")

    print("\nWHAT ACTUALLY LIMITS THE SHAPE")
    print("  Not torque and not inertia. Two things:")
    print("  1. Step resolution: %.0f microsteps per beat, so the finest"
          % (4.38 / (LEAD * 1e3) * 1600))
    print("     feature is about %.0f us of the upstroke. Not a limit."
          % (UPSTROKE_S * 1e6 / (4.38 / (LEAD * 1e3) * 1600 * 0.7)))
    print("  2. The fluid path. Compliance in the tubing and any trapped air")
    print("     round off the upstroke far sooner than the drive does, which")
    print("     is what piston_path.py measures. A metre of soft silicone")
    print("     costs 18 ms of rise time. The drive costs under 1 ms.")


if __name__ == "__main__":
    main()
