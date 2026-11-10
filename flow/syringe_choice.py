# -*- coding: utf-8 -*-
"""Which syringe, and what it costs us. The bore is a design knob, not a given.

    python syringe_choice.py

Everything hard about this drive traces back to one choice nobody revisited.
A 3 mL barrel is 8.66 mm across, so 0.5 mL per beat needs an 8.49 mm stroke,
so the screw turns 446 rpm at peak. That 446 is where the back-EMF problem,
the phase-reversal budget, the stealthChop problem and the whole motor
argument come from. A wider barrel moves the same volume in a shorter stroke
at a lower speed, and the speed falls as the square of the bore.

What a wider bore costs instead: resolution, in microsteps per beat, and
force, which rises with area. Both have enormous headroom here, which is why
this is worth looking at rather than assuming the first pick was right.

The bore figures below are NOMINAL. No manufacturer publishes them for
commodity syringes, and BD's own technical data sheet gives tip dimensions
only. Measure the one you buy. The point of this table is the shape of the
trade, not the third decimal place.
"""
import math

V_BEAT = 0.5             # mL per beat, the design target
UPSTROKE = 0.100         # s, systolic upstroke
UP_FRAC = 0.70           # fraction of the stroke taken during the upstroke
LEAD = 8.0               # mm per rev, T8x8
MICROSTEP = 8
STEPS_PER_REV = 200 * MICROSTEP
TRAVEL = 45.0            # mm the carriage actually has

# Motor, 17HE08-1004S pancake, same numbers as syringe_drive.
TH, I_RATED, R, L = 0.17, 1.0, 3.6, 4.00e-3
V_SUPPLY, SET_I = 12.0, 0.375

# Pressure the piston works against: 30 cm of blood-mimicking fluid plus the
# loop losses at peak, from head_budget. Small, which is the point.
P_PEAK = 6000.0          # Pa, generous
SEAL_N = 1.5             # N of plunger seal friction, measured on a dry BD 3 mL
BACKLASH_PLAIN = 0.20    # mm lost motion, plain brass T8 nut, typical
BACKLASH_ANTI = 0.02     # mm, spring-preloaded anti-backlash nut

SIZES = [
    ("1 mL",   4.70),
    ("3 mL",   8.66),
    ("5 mL",  12.06),
    ("10 mL", 14.50),
    ("20 mL", 19.13),
    ("30 mL", 21.70),
]

kt = TH / (math.sqrt(2.0) * I_RATED)


def motor_margin(rpm):
    """Phase-reversal margin at a given screw speed. Above 1.0 is survivable."""
    w = rpm * 2.0 * math.pi / 60.0
    bemf = kt * w
    head = V_SUPPLY - SET_I * R - bemf
    budget = 1.0 / (2.0 * rpm / 60.0 * 50.0)
    if head <= 0:
        return bemf, None, budget
    return bemf, 2.0 * L * SET_I / head, budget


def main():
    print("TARGET  %.1f mL per beat, %.0f%% of it in a %.0f ms upstroke"
          % (V_BEAT, UP_FRAC * 100, UPSTROKE * 1e3))
    print("SCREW   T8x8, %.0f mm per rev, 1/%d microstep = %d steps per rev\n"
          % (LEAD, MICROSTEP, STEPS_PER_REV))

    print("%-7s %6s %7s %8s %9s %8s %7s %7s  %s" %
          ("size", "bore", "area", "stroke", "peak rpm", "steps", "bemf",
           "margin", "verdict"))
    print("%-7s %6s %7s %8s %9s %8s %7s %7s" %
          ("", "mm", "mm2", "mm", "", "/beat", "V", "x"))
    for name, d in SIZES:
        a = math.pi * d * d / 4.0
        stroke = V_BEAT * 1000.0 / a
        rpm = (UP_FRAC * stroke / LEAD) / UPSTROKE * 60.0
        steps = stroke / LEAD * STEPS_PER_REV
        bemf, trev, budget = motor_margin(rpm)
        force = P_PEAK * a * 1e-6 + SEAL_N
        if trev is None:
            verdict = "IMPOSSIBLE at 12 V"
            marg = 0.0
        else:
            marg = budget / trev
            verdict = ("comfortable" if marg > 4 else
                       "workable" if marg > 2 else
                       "tight" if marg > 1.2 else "NO")
        if stroke > TRAVEL:
            verdict = "stroke exceeds travel"
        print("%-7s %6.2f %7.1f %8.2f %9.0f %8.0f %7.2f %7.1f  %s"
              % (name, d, a, stroke, rpm, steps, bemf, marg, verdict))

    print("\nWHAT A WIDER BORE COSTS")
    print("  Backlash is the real limit. The stroke shrinks as the bore grows,")
    print("  but the lost motion at each reversal does not, so it eats a")
    print("  larger share of every beat. A plain brass T8 nut gives about")
    print("  %.2f mm, an anti-backlash nut about %.2f mm."
          % (BACKLASH_PLAIN, BACKLASH_ANTI))
    print("\n%-7s %8s %9s %10s %11s  %s" %
          ("size", "peak N", "uL/step", "plain nut", "anti-bl nut", "note"))
    for name, d in SIZES:
        a = math.pi * d * d / 4.0
        stroke = V_BEAT * 1000.0 / a
        force = P_PEAK * a * 1e-6 + SEAL_N
        ul = LEAD / STEPS_PER_REV * a          # mm3 per step, and 1 mm3 = 1 uL
        e_plain = BACKLASH_PLAIN / stroke * 100.0
        e_anti = BACKLASH_ANTI / stroke * 100.0
        note = ("backlash error too big" if e_anti > 3.0 else
                "needs the anti-backlash nut" if e_plain > 5.0 else "")
        print("%-7s %8.2f %9.3f %9.1f%% %10.1f%%  %s"
              % (name, force, ul, e_plain, e_anti, note))

    print("\nREAD IT THIS WAY")
    a3 = math.pi * 8.66 ** 2 / 4.0
    a5 = math.pi * 12.06 ** 2 / 4.0
    r3 = (UP_FRAC * V_BEAT * 1000.0 / a3 / LEAD) / UPSTROKE * 60.0
    r5 = (UP_FRAC * V_BEAT * 1000.0 / a5 / LEAD) / UPSTROKE * 60.0
    print("  Going 3 mL -> 5 mL drops peak speed %.0f -> %.0f rpm, a factor of"
          % (r3, r5))
    print("  %.1f, because speed falls as the square of the bore. It costs" % (r3 / r5))
    print("  resolution: %.0f -> %.0f microsteps per beat, both far more than"
          % (V_BEAT * 1000.0 / a3 / LEAD * STEPS_PER_REV,
             V_BEAT * 1000.0 / a5 / LEAD * STEPS_PER_REV))
    print("  the waveform needs. Peak force goes %.2f -> %.2f N, and the seal"
          % (P_PEAK * a3 * 1e-6 + SEAL_N, P_PEAK * a5 * 1e-6 + SEAL_N))
    print("  friction is most of both, so the motor does not notice.")
    print("  At %.0f rpm the back-EMF problem, the phase-reversal budget and"
          % r5)
    print("  the stealthChop question all stop being interesting.")
    print("\n  The frame does not care. Barrel OD lives in the collars now, and")
    print("  a 5 mL barrel is about 12.5 mm against the 14 mm collar bore, so")
    print("  it is still a collar reprint and not a frame reprint. Stroke rises")
    print("  to %.1f mm, well inside the %.0f mm of travel."
          % (V_BEAT * 1000.0 / a5, TRAVEL))


if __name__ == "__main__":
    main()
