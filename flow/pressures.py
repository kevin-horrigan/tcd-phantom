# -*- coding: utf-8 -*-
"""Every pressure in the loop, in all four units, from one place.

    python pressures.py   ->  pressures.png + the table below

The numbers were scattered across head_budget, instrumentation, plenum,
feed_tubing and ball_check, each in whichever unit suited its own argument:
millimetres of fluid for the budget arithmetic, kPa for sensor ranges, psi
for ratings, mmHg for the physiology. All correct and no two comparable at a
glance.

So this file states all of them side by side and derives every one from the
model rather than restating it, which is the only way a table like this
stays true. Nothing here is a new result. The conversions, for this fluid:

    1 mm of BMF  = 10.17 Pa = 0.0763 mmHg = 0.00147 psi
    1 mmHg       = 13.11 mm of BMF
    1 psi        = 680 mm of BMF
"""
import math
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import head_budget as H
import syringe_drive as S

HERE = os.path.dirname(os.path.abspath(__file__))
MMHG, PSI, KPA = 133.322, 6894.757, 1000.0
Q = H.q_si(H.Q_MEAN)


def pa_of_mm(mm):
    return H.RHO * H.G * mm * 1e-3


def seg(name):
    L, d = {n: (L, d) for n, L, d, _z in H.SEGMENTS}[name]
    return H.head_mm(H.r_poiseuille(L, d) * Q)


def main():
    A = print
    r1 = seg("R1, fixed resistance")
    plumb = sum(seg(n) for n, _L, _d, _z in H.SEGMENTS)
    r2 = H.TANK_MM - plumb
    tee = H.TANK_MM - H.seg_head("up")
    inlet = r2 + H.seg_head("lumen") + H.seg_head("down")

    # the pulse, as instrumentation.py derives it
    r_down = pa_of_mm(H.seg_head("shape") + H.seg_head("lumen")
                      + H.seg_head("down") + r2) / Q
    # The TRUE peak, differentiated from the BEAT array the firmware plays,
    # not the mean over the upstroke. Taking the easy version here gave 340 mm
    # against instrumentation.py's 508, a 1.49x disagreement between two files
    # describing the same beat, which is the exact failure this table exists
    # to catch.
    import numpy as _np
    try:
        import pico.config as _C
        _beat = _np.asarray(_C.BEAT, dtype=float)
    except Exception:
        import assembly as _A
        _beat = _np.asarray(_A.beat(), dtype=float)
    _t = _np.linspace(0.0, 1.0, len(_beat))
    q_pk = _np.gradient(_beat * S.BEAT_MM * 1e-3, _t[1] - _t[0]).max() \
        * (S.BORE_A * 1e-6)
    pulse = H.head_mm(r_down * q_pk)

    # the piston against a blocked outlet
    tq = S.MOTOR_TH * (S.SET_I / S.MOTOR_I)
    stall_pa = 2.0 * math.pi * tq * 0.30 / (S.SCREW_LEAD * 1e-3) / (S.BORE_A * 1e-6)

    ROWS = [
        ("--- WHAT DRIVES THE LOOP", None),
        ("the jar, static, no flow", H.TANK_MM),
        ("mean at the piston junction", tee),
        ("mean at the phantom inlet", inlet),
        ("--- WHAT EATS IT, at %.0f mL/min" % H.Q_MEAN, None),
        ("R1, deliberate", r1),
        ("R2, the adjustable one", r2),
        ("the 150 mm settling run", seg("settling run, 3 mm")),
        ("the lumen itself", seg("phantom lumen")),
        ("all six trunk runs together", plumb - r1 - seg("settling run, 3 mm")
         - seg("phantom lumen")),
        ("--- THE PULSE", None),
        ("pulse at the piston, peak", pulse),
        ("peak absolute at the piston", tee + pulse),
        ("diastolic at the piston", tee - 0.0),
        ("--- LIMITS AND RATINGS", None),
        ("piston at stall, blocked outlet", H.head_mm(stall_pa)),
        ("relief valve, set above", 2.0 * H.TANK_MM),
        ("Omegaflex lifts", H.TANK_MM),
        ("Omegaflex is rated to", H.head_mm(20.0 * PSI)),
        ("--- INSTRUMENT RANGES", None),
        ("MPX5050GP full scale", H.head_mm(50.0 * KPA)),
        ("ABP2 005PG full scale", H.head_mm(5.0 * PSI)),
        ("cheap module full scale", H.head_mm(40.0 * KPA)),
        ("a 0-30 psi dial gauge", H.head_mm(30.0 * PSI)),
        ("--- CHECK VALVES, IF ONE IS EVER ADDED", None),
        ("Qosina 91050 cracking", H.head_mm(0.075 * PSI)),
        ("the printed ball check cracking", H.head_mm(0.0032 * PSI)),
        ("the luer-to-luer trap, 0.433 psi", H.head_mm(0.433 * PSI)),
        ("--- FOR COMPARISON", None),
        ("a real MCA, systolic", H.head_mm(90.0 * MMHG)),
        ("a real MCA, diastolic", H.head_mm(60.0 * MMHG)),
        ("Greaby's loop, peak", H.head_mm(250.0 * MMHG)),
        ("squeeze 1 % out of the air", H.head_mm(1.4 * 101325.0 * 0.01)),
        ("squeeze 1 % out of the fluid", H.head_mm(2.2e9 * 0.01)),
    ]

    A("EVERY PRESSURE IN THE LOOP")
    A("  1 mm of BMF = %.2f Pa = %.4f mmHg = %.5f psi"
      % (pa_of_mm(1.0), pa_of_mm(1.0) / MMHG, pa_of_mm(1.0) / PSI))
    A("")
    A("  %-34s %10s %9s %9s %9s"
      % ("", "mm fluid", "mmHg", "kPa", "psi"))
    for nm, mm in ROWS:
        if mm is None:
            A("")
            A("  %s" % nm.replace("--- ", ""))
            continue
        pa = pa_of_mm(mm)
        A("  %-34s %10.0f %9.1f %9.2f %9.3f"
          % (nm, mm, pa / MMHG, pa / KPA, pa / PSI))
    A("")
    A("  THE ONE COMPARISON WORTH MAKING. The loop runs at about %.0f mmHg"
      % (pa_of_mm(inlet) / MMHG))
    A("  mean at the block against a real MCA's %.0f, so roughly a third of"
      % 70.0)
    A("  physiological, and on purpose: it reproduces VELOCITY, and a soft")
    A("  cast gel will not hold arterial pressure. Expect the right shape at")
    A("  a third of the amplitude, and do not go chasing the difference.")
    A("")
    A("  AND THE ONE THAT KILLS MOST INSTRUMENTS. The whole machine lives")
    A("  inside %.2f psi. A 0-30 psi dial gauge resolves %.0f mmHg per"
      % (pa_of_mm(H.TANK_MM) / PSI, 30.0 * PSI / MMHG * 0.01))
    A("  percent of its scale, which is %.0f percent of the entire pulse."
      % (100.0 * (30.0 * PSI / MMHG * 0.01) / (pa_of_mm(pulse) / MMHG)))

    # -------------------------------------------------------------- figure
    fig, ax = plt.subplots(figsize=(11.6, 6.6), dpi=170)
    fig.patch.set_facecolor("white")
    SHOW = [("the fluid, 1 %", H.head_mm(2.2e9 * 0.01), "#3c3c3c"),
            ("Omegaflex rating", H.head_mm(20.0 * PSI), "#6f6f6f"),
            ("piston at stall", H.head_mm(stall_pa), "#b4462e"),
            ("0-30 psi dial gauge", H.head_mm(30.0 * PSI), "#6f6f6f"),
            ("ABP2 full scale", H.head_mm(5.0 * PSI), "#2e6fb4"),
            ("MPX5050GP full scale", H.head_mm(50.0 * KPA), "#2e6fb4"),
            ("real MCA systolic", H.head_mm(90.0 * MMHG), "#4a8f3c"),
            ("relief valve setting", 2.0 * H.TANK_MM, "#b4462e"),
            ("THE JAR", H.TANK_MM, "#c9820f"),
            ("peak at the piston", tee + pulse, "#b4462e"),
            ("pulse alone", pulse, "#b4462e"),
            ("mean at the block", inlet, "#2e6fb4"),
            ("R2", r2, "#2e6fb4"),
            ("the air, 1 %", H.head_mm(1.4 * 101325.0 * 0.01), "#4a8f3c"),
            ("ball check cracking", H.head_mm(0.0032 * PSI), "#4a8f3c")]
    SHOW.sort(key=lambda r: r[1])
    y = range(len(SHOW))
    ax.barh(list(y), [pa_of_mm(r[1]) / MMHG for r in SHOW],
            color=[r[2] for r in SHOW], height=0.64)
    ax.set_yticks(list(y))
    ax.set_yticklabels([r[0] for r in SHOW], fontsize=9.5)
    ax.set_xscale("log")
    for k, r in enumerate(SHOW):
        v = pa_of_mm(r[1]) / MMHG
        ax.text(v * 1.35, k, "%s mmHg   %s psi"
                % (("%.2f" % v) if v < 10 else "%.0f" % v,
                   ("%.3f" % (pa_of_mm(r[1]) / PSI)) if v < 100
                   else "%.1f" % (pa_of_mm(r[1]) / PSI)),
                va="center", fontsize=8.5, color=r[2])
    ax.axvspan(pa_of_mm(inlet) / MMHG, pa_of_mm(tee + pulse) / MMHG,
               color="#c9820f", alpha=0.10)
    ax.set_xlim(0.05, 4e5)
    ax.set_xlabel("mmHg, log scale")
    ax.set_title("Every pressure in the loop, on one axis\n"
                 "the shaded band is where the experiment actually happens",
                 fontsize=12)
    ax.grid(axis="x", alpha=0.25, lw=0.6)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    fig.text(0.5, 0.015,
             "Six decades from the air spring to the fluid's own stiffness, "
             "and the whole experiment sits in one of them.",
             fontsize=9, color="#555", ha="center")
    fig.tight_layout(rect=(0, 0.035, 1, 1))
    fig.savefig(os.path.join(HERE, "pressures.png"), facecolor="white")
    A("")
    A("wrote pressures.png")


if __name__ == "__main__":
    main()
