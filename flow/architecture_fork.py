# -*- coding: utf-8 -*-
"""Two different machines are being described, and the numbers decide it.

    python architecture_fork.py   ->  architecture-fork.png + the tables below

capstone/GROUP-2_pulsatile-flow-loop.md, which the teams have, says:

    "Positive-displacement piston as the ventricle, into a compliance
     chamber, into an adjustable resistance, returning to a reservoir.
     Check valves on either side of the piston close the loop."

That is Greaby's topology, call it B. The piston is the PUMP. It draws from a
sump through an inlet check valve and ejects through an outlet check valve,
and it supplies the mean flow and the pulse together. There is no elevated
tank and nothing for gravity to do.

The bench is being built as A. A header tank 622 mm up supplies the mean
flow, the piston tees into the line and adds only the pulse, and ONE check
valve keeps that pulse from running back up the feed. syringe_drive.py has
said so in writing the whole time:

    BEAT_ML = 0.5     # per beat, the pulsatile component only

These are not two descriptions of one machine. They differ in the number of
check valves, in whether the reservoir is elevated or a sump, in what sets
the mean flow, and by a factor of eight in what the piston has to move. This
file works out which the built hardware can actually do.

The governing arithmetic is one line. In B the piston must deliver the whole
mean flow by itself:

    stroke per beat = mean flow / heart rate

At 250 mL/min and 60 bpm that is 4.167 mL per beat. The drive is built for
0.500 mL. Everything below follows from that factor of 8.3.
"""
import math
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import syringe_drive as S

HERE = os.path.dirname(os.path.abspath(__file__))
Q_MEAN = 250.0                 # mL/min, 60 cm/s mean in a 3 mm lumen
RPM_MARGIN = 1.5               # check_drive.py's rule: ceiling over demand

# Motor ceiling, the same derivation check_drive.py uses.
_mp = S.MOTORS[S.MOTOR]
KT = _mp["th"] / (math.sqrt(2.0) * _mp["i"])
CEILING_RPM = S.DRIVE_V / KT * 60.0 / (2.0 * math.pi)

# Thrust the drive can make, from torque through the screw.
SCREW_EFF = 0.30               # trapezoidal screw, unlubricated, conservative
TORQUE = _mp["th"] * (S.SET_I / _mp["i"])
THRUST = 2.0 * math.pi * TORQUE * SCREW_EFF / (S.SCREW_LEAD * 1e-3)

MMHG = 133.322
GREABY_PEAK_MMHG = 150.0       # middle of Greaby's reported 100 to 250

# Commodity syringes. ONLY the 5 mL is measured; the rest are nominal and
# must be measured before anything is built on them. Same discipline as the
# motor table: a number nobody put calipers on is marked as such.
SYRINGES = [
    ("5 mL   (fitted)", 120.0, 14.0, True),
    ("10 mL", 199.0, 17.0, False),
    ("20 mL", 317.0, 21.5, False),
    ("30 mL", 398.0, 24.0, False),
    ("60 mL", 560.0, 28.5, False),
]
SADDLE_BORE = 16.0             # as printed. The frame exists.


def rpm_for(stroke_mm, upstroke_s=None, up_frac=None):
    """Peak screw speed to take up_frac of stroke_mm inside upstroke_s."""
    u = upstroke_s or S.UPSTROKE_S
    f = up_frac or S.UPSTROKE_FRAC
    return (f * stroke_mm / S.SCREW_LEAD) / u * 60.0


def main():
    A = print
    A("THE DRIVE AS BUILT")
    A("  motor %s at %.0f V, ceiling %.0f rpm, thrust %.1f N"
      % (S.MOTOR, S.DRIVE_V, CEILING_RPM, THRUST))
    A("  5 mL barrel, %.1f mm2 bore (MEASURED), %.1f mm saddle as printed"
      % (S.BORE_A, SADDLE_BORE))
    A("  beat %.3f mL = %.3f mm, peak %.0f rpm, margin %.1fx"
      % (S.BEAT_ML, S.BEAT_MM, S.PEAK_RPM, CEILING_RPM / S.PEAK_RPM))
    A("")

    A("WHAT ARCHITECTURE B WOULD ASK OF IT")
    A("  The piston supplies the whole %.0f mL/min, so stroke = flow / rate."
      % Q_MEAN)
    A("  Two readings of the upstroke, because the answer depends on it.")
    A("  'scaled' shortens systole with the period, 'fixed' holds it at %.0f ms."
      % (S.UPSTROKE_S * 1e3))
    A("  %-6s %9s %9s %9s %9s  %s"
      % ("bpm", "mL/beat", "stroke", "rpm scaled", "rpm fixed", "verdict"))
    for bpm in (60, 80, 100, 120, 140):
        ml = Q_MEAN / bpm
        mm = ml * 1000.0 / S.BORE_A
        rpm_s = rpm_for(mm, upstroke_s=S.UPSTROKE_S * (60.0 / bpm))
        rpm_f = rpm_for(mm)
        why = []
        if mm > S.SOFT_TRAVEL:
            why.append("stroke past the %.1f mm soft limit" % S.SOFT_TRAVEL)
        if min(rpm_s, rpm_f) * RPM_MARGIN > CEILING_RPM:
            why.append("over the motor even at best, by %.1fx"
                       % (min(rpm_s, rpm_f) * RPM_MARGIN / CEILING_RPM))
        A("  %-6d %9.3f %9.2f %9.0f %9.0f  %s"
          % (bpm, ml, mm, rpm_s, rpm_f, "; ".join(why) if why else "ok"))
    A("")
    A("  Read the 'scaled' column: it does not change with rate. In B the")
    A("  stroke falls as 1/bpm and the time to deliver it falls by the same")
    A("  factor, so they cancel exactly. Running the loop faster is not an")
    A("  escape from this, which is the one thing everybody tries first.")
    A("")
    A("  So B is not a tuning change. In the 5 mL barrel it is %.1fx the beat"
      % ((Q_MEAN / 60.0) / S.BEAT_ML))
    A("  and %.0f rpm against a %.0f rpm ceiling, with the stroke running past"
      % (rpm_for(Q_MEAN / 60.0 * 1000.0 / S.BORE_A), CEILING_RPM))
    A("  the soft limit that keeps the plunger seal inside the barrel.")
    A("")

    A("B WITH A BIGGER BARREL, WHICH IS THE REAL QUESTION")
    A("  A wider bore trades speed for thrust: stroke falls as 1/area, and the")
    A("  force to make pressure rises as area. Both at %.0f bpm, %.0f mmHg peak."
      % (60, GREABY_PEAK_MMHG))
    A("  %-18s %7s %8s %9s %9s %9s  %s"
      % ("syringe", "mm2", "stroke", "peak rpm", "thrust N", "P max", "fits frame"))
    best = []
    for nm, area, od, measured in SYRINGES:
        ml = Q_MEAN / 60.0
        mm = ml * 1000.0 / area
        rpm = rpm_for(mm)
        need_n = GREABY_PEAK_MMHG * MMHG * area * 1e-6
        p_max = THRUST / (area * 1e-6) / MMHG
        fits = od + 0.5 <= SADDLE_BORE
        okrpm = rpm * RPM_MARGIN <= CEILING_RPM
        okn = need_n <= THRUST
        A("  %-18s %7.0f %8.2f %9.0f %9.1f %9.0f  %s"
          % (nm + ("" if measured else "  nominal"), area, mm, rpm, need_n,
             p_max, "yes" if fits else "NO, %.1f mm OD" % od))
        if okrpm and okn and not measured:
            best.append(nm)
    A("")
    A("  Every barrel that can turn fast enough is too wide for the saddle.")
    A("  FRAME_SADDLE is %.1f mm and it is already printed. B therefore costs"
      % SADDLE_BORE)
    A("  a new frame, a new carriage and a new saddle cap, plus whichever of")
    A("  those barrels gets measured. Candidates on speed and thrust: %s."
      % (", ".join(best) if best else "none"))
    A("")

    A("WHAT EACH ARCHITECTURE NEEDS THAT THE OTHER DOES NOT")
    rows = [
        ("reservoir", "elevated %.0f mm" % 622.0, "a sump on the bench"),
        ("check valves", "one, above the piston tee", "TWO, either side of the piston"),
        ("what sets mean flow", "the tank height", "the piston, every beat"),
        ("piston delivers", "%.2f mL/beat" % S.BEAT_ML,
         "%.2f mL/beat" % (Q_MEAN / 60.0)),
        ("working pressure", "31 mmHg at the inlet", "100 to 250 mmHg (Greaby)"),
        ("pressure sensor", "0-20 kPa", "0-50 kPa"),
        ("standpipes", "relief and manometer", "neither applies"),
        ("head budget", "the whole design driver", "irrelevant"),
        ("frame as printed", "fits", "needs a new one"),
        ("if the piston stops", "flow continues from the tank", "flow stops dead"),
    ]
    A("  %-22s %-30s %s" % ("", "A, gravity + pulse piston", "B, Greaby piston pump"))
    for k, a, b in rows:
        A("  %-22s %-30s %s" % (k, a, b))
    A("")

    A("WHAT SURVIVES EITHER WAY, AND IS SAFE TO SEND NOW")
    for s in ("the check valve part numbers: 91050 for 1/4 in, and the fact "
              "that\n    9105x is not a part number",
              "braided PVC and not silicone on any run that carries the pulse",
              "1/4 in trunk, 3.0 mm settling run, 1/8 in barb IS the 3 mm barb",
              "the compliance plenum is unsized and it is what sets PI",
              "gravimetric catch for the mean, step count for the pulse",
              "a dial gauge cannot resolve either machine's pulse",
              "the relief valve, and that an open standpipe cannot be it"):
        A("  - %s" % s)
    A("")
    A("WHAT DOES NOT SURVIVE, AND SHOULD NOT GO OUT UNTIL THIS IS SETTLED")
    for s in ("the 622 mm tank height, which exists only in A",
              "both standpipes",
              "the 0-20 kPa transducer range",
              "the single check valve in the loop diagram",
              "the head budget as the design driver"):
        A("  - %s" % s)
    A("")

    A("A CONTRADICTION THAT WAS ALREADY THERE, INDEPENDENT OF THIS")
    A("  GROUP-2_pulsatile-flow-loop.md quotes Greaby's envelope as 100 to 250")
    A("  mmHg peak pressure. INTERFACE-CONTROL-DOCUMENT.md requires a pressure")
    A("  ceiling below Group 1's measured tear-out, on the grounds that a soft")
    A("  cast gel will not hold arterial pressure. Those two cannot both be")
    A("  satisfied by a wall-less lumen. Whoever answers the architecture")
    A("  question has to answer this one in the same breath.")

    # --------------------------------------------------------------- figure
    fig, ax = plt.subplots(1, 2, figsize=(13.2, 5.0), dpi=170)
    fig.patch.set_facecolor("white")

    a0 = ax[0]
    bpm = np.linspace(55, 145, 200)
    rpm_b = np.array([rpm_for(Q_MEAN / b * 1000.0 / S.BORE_A,
                              upstroke_s=S.UPSTROKE_S * (60.0 / b))
                      for b in bpm])
    rpm_bf = np.array([rpm_for(Q_MEAN / b * 1000.0 / S.BORE_A) for b in bpm])
    a0.plot(bpm, rpm_b, color="#b4462e", lw=2.2,
            label="B, systole scales with rate")
    a0.plot(bpm, rpm_bf, color="#b4462e", lw=1.8, ls="--",
            label="B, systole fixed at %.0f ms" % (S.UPSTROKE_S * 1e3))
    a0.axhline(S.PEAK_RPM, color="#2e6fb4", lw=2.2,
               label="A, piston adds the pulse (%.0f rpm)" % S.PEAK_RPM)
    a0.axhline(CEILING_RPM, color="#444", ls="--", lw=1.4)
    a0.axhline(CEILING_RPM / RPM_MARGIN, color="#888", ls=":", lw=1.4)
    a0.text(57, CEILING_RPM * 1.03, "motor ceiling %.0f rpm" % CEILING_RPM,
            fontsize=8, color="#444")
    a0.text(57, CEILING_RPM / RPM_MARGIN * 1.03,
            "with the 1.5x margin", fontsize=8, color="#888")
    a0.set_yscale("log")
    a0.set_xlabel("heart rate, bpm")
    a0.set_ylabel("peak screw speed, rpm")
    a0.set_title("Same 5 mL barrel, same motor:\nB asks for speed that is not there",
                 fontsize=10.5)
    a0.legend(fontsize=8, frameon=False, loc="upper right")

    a1 = ax[1]
    names = [s[0].split()[0] for s in SYRINGES]
    areas = np.array([s[1] for s in SYRINGES])
    ods = np.array([s[2] for s in SYRINGES])
    rpms = np.array([rpm_for(Q_MEAN / 60.0 * 1000.0 / a) for a in areas])
    cols = ["#2e6fb4" if o + 0.5 <= SADDLE_BORE else "#b4462e" for o in ods]
    a1.bar(names, rpms, color=cols, width=0.62)
    a1.axhline(CEILING_RPM / RPM_MARGIN, color="#888", ls=":", lw=1.4)
    a1.text(-0.42, CEILING_RPM / RPM_MARGIN * 1.04,
            "usable ceiling %.0f rpm" % (CEILING_RPM / RPM_MARGIN),
            fontsize=8, color="#888")
    for i, (r, o) in enumerate(zip(rpms, ods)):
        a1.text(i, r * 1.05, "%.0f mm OD" % o, ha="center", fontsize=7.5,
                color="#444")
    a1.set_yscale("log")
    a1.set_ylabel("peak screw speed, rpm")
    a1.set_title("B at 60 bpm, by barrel. Blue fits the printed\n"
                 "%.0f mm saddle, red does not" % SADDLE_BORE, fontsize=10.5)

    for a in ax:
        a.grid(alpha=0.25, lw=0.6)
        for sp in ("top", "right"):
            a.spines[sp].set_visible(False)
    fig.suptitle("Two architectures, one set of hardware", fontsize=12.5, y=0.99)
    fig.text(0.5, 0.012,
             "A is what the bench is built for and what syringe_drive.py has "
             "always said. B is what the teams were sent. The gap is a factor "
             "of %.1f in stroke volume." % ((Q_MEAN / 60.0) / S.BEAT_ML),
             fontsize=8.5, color="#555", ha="center")
    fig.tight_layout(rect=(0, 0.045, 1, 0.94))
    fig.savefig(os.path.join(HERE, "architecture-fork.png"), facecolor="white")
    A("")
    A("wrote architecture-fork.png")


if __name__ == "__main__":
    main()
