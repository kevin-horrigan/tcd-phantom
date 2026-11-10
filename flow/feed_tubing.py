# -*- coding: utf-8 -*-
"""What bore of tubing runs from the head tank to the phantom, and why.

    python feed_tubing.py      ->  feed-tubing.png + the tables below

head_budget.py asks how high the tank has to be. This asks the next question
down: given that height, what should the tubing actually be. They are not the
same question, and the second one is not answered by "as big as convenient".

The feed side has THREE zones with three different jobs, and the check valve
is what separates them:

    tank ---- A ----> [check valve] ---- B ----> [piston tee] ---- C ---->
                                                          ---- D ----> phantom

  A  tank to the check valve.      Carries the MEAN flow only.
  B  valve to the piston tee.      Carries the MEAN flow only.
  C  tee to the 3 mm transition.   Carries the mean AND the pulse.
  D  the settling run, 3 mm.       Carries the mean AND the pulse.

That split is the whole trick, and it is worth saying out loud because it is
not obvious: the check valve blocks the pulse from travelling back up toward
the tank, so the compliance of A and B is charged to nothing. Only C and D
can steal stroke volume. A and B are picked on head loss alone, and head loss
on that stretch turns out to be almost free.

Three physical effects compete, and they do not all point the same way:

  RESISTANCE   goes as 1/d^4.  Wants big bore. Costs tank height, which is
               the one currency on this bench that is genuinely cheap.
  COMPLIANCE   goes as d^3/(E*h).  Wants small bore and a stiff wall. Steals
               stroke volume outright, and no amount of tank height buys it
               back. This is the term that rounds off systole.
  INERTANCE    goes as 1/d^2.  Wants big bore. Delays the pulse rather than
               shrinking it, and is reactive, so it does not eat the mean
               budget at all.

Compliance is the only one of the three that destroys information. So it gets
first claim on the design, and it is beaten by MATERIAL by a factor of ten
before bore is even considered.

Fluid is IEC 61685 blood-mimicking fluid per Ramnarine 1998.
"""
import math
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import syringe_drive as S

HERE = os.path.dirname(os.path.abspath(__file__))

RHO = 1037.0             # kg/m3, Ramnarine 1998 BMF
MU = 4.1e-3              # Pa.s
G = 9.80665
PSI = 6894.757
MMHG = 133.322

Q_MEAN = 250.0           # mL/min, 60 cm/s mean in a 3 mm lumen
BEAT_HZ = 1.0

# Pulse pressure the compliant section sees. The loop is velocity-targeted,
# not pressure-targeted, so this is an assumption and it is stated as one.
# 40 mmHg is an ordinary arterial pulse pressure and the compliance numbers
# below scale linearly with it, so halving it halves every stolen volume.
PP_MMHG = 40.0

# Commodity tubing, by inner diameter. These are the sizes actually stocked
# and the sizes the Qosina barbed check valve family covers: 91053 at 1/8 in,
# 91054 at 3/16, 91050 at 1/4 and 91055 at 3/8. That is why the list stops
# where it does. These notes used to say "9105x", which is a wildcard and not
# a part number, and a search for it returns nothing.
BORES = [
    ("1/8 in",  3.18),
    ("3/16 in", 4.76),
    ("1/4 in",  6.35),
    ("5/16 in", 7.94),
    ("3/8 in",  9.53),
]

# Wall thickness. Nearly all of this tubing is sold at 1/16 in wall in the
# small sizes, so holding it fixed compares like with like. A thicker wall is
# stiffer in exactly the proportion the formula says.
WALL = 1.59              # mm

# Young's modulus, Pa. The spread here is the point: it is three orders of
# magnitude, and it costs nothing to move along it.
MATERIALS = [
    ("silicone",      1.5e6, "what a flow loop reaches for first"),
    ("Tygon / PVC",    15e6, "clear, barbs fine, 10x stiffer than silicone"),
    ("braided PVC",    50e6, "reinforced, the practical stiff choice"),
    ("nylon / PTFE",  500e6, "effectively rigid at these pressures"),
]

# Zone lengths, mm. A and B are routing and can be whatever the bench needs.
# C is the one to fight for, because it is compliant AND carries the pulse.
# D is set by the interface control document at 150 mm minimum.
LEN_A, LEN_B, LEN_C, LEN_D = 400.0, 150.0, 150.0, 150.0
BORE_D = 3.00            # the settling run matches the lumen, by agreement
LUMEN_L = 80.0


def q_si(ml_per_min):
    return ml_per_min * 1e-6 / 60.0


def r_pois(length_mm, bore_mm):
    """Pa.s/m3, laminar flow in a round tube."""
    return 128.0 * MU * (length_mm * 1e-3) / (math.pi * (bore_mm * 1e-3) ** 4)


def inertance(length_mm, bore_mm):
    """Pa per (m3/s2). Pressure needed to accelerate the slug of fluid."""
    a = math.pi * (bore_mm * 1e-3 / 2.0) ** 2
    return RHO * (length_mm * 1e-3) / a


def compliance(length_mm, bore_mm, e_pa, wall_mm=WALL):
    """m3/Pa for a thin-walled tube.  dV/dp = pi d^3 L / (4 E h).

    From Laplace: hoop stress p*r/h, strain p*r/(E*h), so dr = p*r^2/(E*h)
    and dV = 2*pi*r*L*dr. The d^3 is why bore matters here at all, and the
    1/E is why material matters more.
    """
    d, L, h = bore_mm * 1e-3, length_mm * 1e-3, wall_mm * 1e-3
    return math.pi * d ** 3 * L / (4.0 * e_pa * h)


def velocity(ml_per_min, bore_mm):
    return q_si(ml_per_min) / (math.pi * (bore_mm * 1e-3 / 2.0) ** 2)


def reynolds(ml_per_min, bore_mm):
    d = bore_mm * 1e-3
    return RHO * velocity(ml_per_min, bore_mm) * d / MU


def womersley(bore_mm, hz=BEAT_HZ):
    """alpha = r * sqrt(w*rho/mu). Above about 4 the profile stops being
    quasi-steady and the core starts moving as a plug."""
    w = 2.0 * math.pi * hz
    return (bore_mm * 1e-3 / 2.0) * math.sqrt(w * RHO / MU)


def head_mm(pa):
    return pa / (RHO * G) * 1e3


def piston_flow():
    """Flow and flow-rate-of-change the piston actually commands.

    Differentiating the real BEAT array rather than assuming a shape, because
    the array is what the firmware plays. BEAT is normalised DISPLACEMENT over
    one period, so Q is its first derivative and dQ/dt its second.
    """
    try:
        import pico.config as C
        beat = np.asarray(C.BEAT, dtype=float)
    except Exception:
        import assembly as A
        beat = np.asarray(A.beat(), dtype=float)
    period = 60.0 / 60.0                       # 1 s at 60 bpm
    t = np.linspace(0.0, period, len(beat))
    dt = t[1] - t[0]
    x = beat * S.BEAT_MM * 1e-3                # m of piston travel
    q = np.gradient(x, dt) * (S.BORE_A * 1e-6)  # m3/s
    dqdt = np.gradient(q, dt)
    return t, q, dqdt


def main():
    A = print
    t, q, dqdt = piston_flow()
    q_pk = q.max()
    dq_pk = dqdt.max()
    pp_pa = PP_MMHG * MMHG
    stroke_m3 = S.BEAT_ML * 1e-6

    A("FLUID AND BEAT")
    A("  BMF %.0f kg/m3, %.1f mPa.s. 1 cm of it is %.4f psi."
      % (RHO, MU * 1e3, RHO * G * 0.01 / PSI))
    A("  stroke %.2f mL, %.3f mm of a %.1f mm2 bore, %.0f bpm"
      % (S.BEAT_ML, S.BEAT_MM, S.BORE_A, 60.0))
    A("  piston peak flow %.2f mL/s (%.0f mL/min) on top of a %.0f mL/min mean"
      % (q_pk * 1e6, q_pk * 6e7, Q_MEAN))
    A("  piston peak dQ/dt %.3e m3/s2, differentiated from the BEAT array"
      % dq_pk)
    A("  compliance volumes below assume a %.0f mmHg pulse and scale linearly"
      % PP_MMHG)
    A("")

    A("ZONE A+B, TANK TO THE PISTON TEE  (%.0f mm of run, MEAN flow only)"
      % (LEN_A + LEN_B))
    A("  The check valve sits inside this stretch, so none of its compliance")
    A("  is charged against the stroke. Head loss is the only cost.")
    A("  %-9s %6s %8s %8s %7s %8s %9s"
      % ("bore", "mm", "mm head", "cm/s", "Re", "alpha", "mL held"))
    for name, d in BORES:
        dp = r_pois(LEN_A + LEN_B, d) * q_si(Q_MEAN)
        vol = math.pi * (d / 2.0) ** 2 * (LEN_A + LEN_B) * 1e-3
        A("  %-9s %6.2f %8.1f %8.1f %7.0f %8.2f %9.1f"
          % (name, d, head_mm(dp), velocity(Q_MEAN, d) * 100.0,
             reynolds(Q_MEAN, d), womersley(d), vol))
    A("  -> 1/4 in costs %.0f mm of tank height over %.0f mm of run. That is"
      % (head_mm(r_pois(LEN_A + LEN_B, 6.35) * q_si(Q_MEAN)), LEN_A + LEN_B))
    A("     noise next to the %.0f mm the 3 mm lumen itself costs, so there is"
      % head_mm(r_pois(LUMEN_L, 3.0) * q_si(Q_MEAN)))
    A("     nothing here to buy by going wider.")
    A("")

    A("ZONE C, PISTON TEE TO THE 3 mm TRANSITION  (%.0f mm, MEAN + PULSE)"
      % LEN_C)
    A("  This is the stretch that matters. Everything it stores in its wall")
    A("  is stroke volume that never reaches the phantom.")
    A("  %-9s %8s %8s %8s   %s"
      % ("bore", "mm head", "inert mm", "", "stolen stroke volume, %"))
    A("  %-9s %8s %8s %8s   %s"
      % ("", "mean", "at dQ/dt", "",
         "  ".join("%-12s" % m[0] for m in MATERIALS)))
    for name, d in BORES:
        dp = head_mm(r_pois(LEN_C, d) * q_si(Q_MEAN))
        iner = head_mm(inertance(LEN_C, d) * dq_pk)
        pcts = []
        for _, e, _n in MATERIALS:
            dv = compliance(LEN_C, d, e) * pp_pa
            pcts.append("%-12.2f" % (100.0 * dv / stroke_m3))
        A("  %-9s %8.1f %8.1f %8s   %s"
          % (name, dp, iner, "", "  ".join(pcts)))
    A("")
    A("  Read that table across, not down. Moving 1/4 in from silicone to")
    A("  braided PVC takes %.1f%% of the stroke down to %.1f%%, and costs"
      % (100.0 * compliance(LEN_C, 6.35, 1.5e6) * pp_pa / stroke_m3,
         100.0 * compliance(LEN_C, 6.35, 50e6) * pp_pa / stroke_m3))
    A("  nothing but ordering the other reel. Moving 1/4 in down to 1/8 in to")
    A("  chase the same effect costs %.0f mm of tank height and %.0f mm of"
      % (head_mm(r_pois(LEN_C, 3.18) * q_si(Q_MEAN))
         - head_mm(r_pois(LEN_C, 6.35) * q_si(Q_MEAN)),
         head_mm(inertance(LEN_C, 3.18) * dq_pk)
         - head_mm(inertance(LEN_C, 6.35) * dq_pk)))
    A("  inertial lag, and still lands above braided 1/4 in. Material first.")
    A("")

    A("ZONE D, THE 3 mm SETTLING RUN  (what each 10 mm of it costs)")
    A("  The interface control document sets 150 mm so flow arrives at the")
    A("  cast lumen already developed, because the M1 segment is 22 to 27 mm")
    A("  long and cannot supply its own entrance length. Fine. But it is the")
    A("  most expensive tubing on the bench, so it should be 150 and not 300.")
    A("  %-10s %9s %9s %10s"
      % ("length mm", "per 10 mm", "total", "stolen %, braided"))
    for L in (50.0, 100.0, 150.0, 200.0, 300.0):
        dp = head_mm(r_pois(L, BORE_D) * q_si(Q_MEAN))
        dv = compliance(L, BORE_D, 50e6) * pp_pa
        A("  %-10.0f %9.1f %9.1f %10.2f"
          % (L, head_mm(r_pois(10.0, BORE_D) * q_si(Q_MEAN)), dp,
             100.0 * dv / stroke_m3))
    A("  -> %.1f mm of tank height per 10 mm of 3 mm tube. Compliance there is"
      % head_mm(r_pois(10.0, BORE_D) * q_si(Q_MEAN)))
    A("     almost nothing, because compliance goes as d^3 and this is the")
    A("     narrowest tube in the loop. Narrow tube: cheap to stretch,")
    A("     expensive to push through. Exactly the opposite of the trunk.")
    A("")

    # ------------------------------------------------- the corrected budget
    A("THE BUDGET head_budget.py IS MISSING")
    A("  head_budget.py runs 6.35 mm all the way to the phantom inlet and then")
    A("  steps straight into the lumen. The interface control document does")
    A("  not: it puts 150 mm of 3 mm tubing ahead of the coupling. That run is")
    A("  absent from the budget, and it is not a rounding error.")
    old = sum(head_mm(r_pois(L, d) * q_si(Q_MEAN)) for L, d in
              ((LEN_A, 6.35), (15.0, 3.30), (LEN_B, 6.35), (200.0, 6.35),
               (LUMEN_L, 3.0), (150.0, 6.35), (150.0, 6.35), (400.0, 6.35)))
    new = sum(head_mm(r_pois(L, d) * q_si(Q_MEAN)) for L, d in
              ((LEN_A, 6.35), (15.0, 3.30), (LEN_B, 6.35), (LEN_C, 6.35),
               (LEN_D, BORE_D), (LUMEN_L, 3.0), (150.0, 6.35), (150.0, 6.35),
               (400.0, 6.35)))
    crack = head_mm(0.075 * PSI)   # Qosina 91050, the 1/4 in ID barbed part
    A("  plumbing as budgeted            %6.0f mm of head" % old)
    A("  plumbing with the settling run  %6.0f mm of head" % new)
    A("  Qosina 91050 cracking pressure  %6.0f mm" % crack)
    A("  tank height for the constriction to own half the head:")
    A("    as budgeted  %.0f mm      with the settling run  %.0f mm"
      % (2.0 * (old + crack), 2.0 * (new + crack)))
    A("  So the 370 mm figure in the notes is for a loop that does not have")
    A("  the agreed interface in it. With the settling run the tank wants to")
    A("  be about %.0f mm above the phantom, or %.0f mm if the constriction is"
      % (2.0 * (new + crack), 1.5 * (new + crack)))
    A("  allowed to own a third of the head instead of half.")
    A("")

    A("WHAT TO BUY")
    A("  A  tank to check valve    1/4 in ID. Material free, nothing is")
    A("                            charged against the pulse upstream of the")
    A("                            valve. Use whatever is clear and cheap.")
    A("  B  valve to piston tee    1/4 in ID, same reasoning.")
    A("  C  tee to transition      1/4 in ID in BRAIDED PVC or Tygon, and as")
    A("                            short as the bench can be routed. Not")
    A("                            silicone. This is the only stretch where")
    A("                            the wall competes with the piston.")
    A("  D  settling run           3.0 mm ID, stiff, 150 mm and no more.")
    A("  return side               1/4 in or wider, material free.")
    A("  All of A through C are inside the barbed family's range, so the")
    A("  check valve matches the trunk with no adapters: 91050 for a 1/4 in")
    A("  trunk, 0.075 psi, which is %.0f mm of the head budget." % crack)
    A("")
    A("  The one number to hold: C and D together should steal under 3 percent")
    A("  of the stroke. Braided 1/4 in at %.0f mm plus 3 mm at %.0f mm gives"
      % (LEN_C, LEN_D))
    A("  %.2f percent. The same routing in silicone gives %.2f percent, and"
      % (100.0 * (compliance(LEN_C, 6.35, 50e6)
                  + compliance(LEN_D, BORE_D, 50e6)) * pp_pa / stroke_m3,
         100.0 * (compliance(LEN_C, 6.35, 1.5e6)
                  + compliance(LEN_D, BORE_D, 1.5e6)) * pp_pa / stroke_m3))
    A("  that loss lands on the sharp part of systole, which is the single")
    A("  feature this phantom exists to reproduce.")

    # ------------------------------------------------------------- figure
    fig, ax = plt.subplots(1, 3, figsize=(13.4, 4.3), dpi=170)
    fig.patch.set_facecolor("white")
    dd = np.linspace(2.5, 10.0, 200)

    a0 = ax[0]
    a0.plot(dd, [head_mm(r_pois(LEN_C, d) * q_si(Q_MEAN)) for d in dd],
            color="#b4462e", lw=2.0, label="zone C, %.0f mm" % LEN_C)
    a0.plot(dd, [head_mm(r_pois(LEN_A + LEN_B, d) * q_si(Q_MEAN)) for d in dd],
            color="#2e6fb4", lw=2.0, label="zone A+B, %.0f mm" % (LEN_A + LEN_B))
    a0.axhline(head_mm(r_pois(LUMEN_L, 3.0) * q_si(Q_MEAN)), color="#555",
               ls="--", lw=1.2)
    a0.text(6.3, head_mm(r_pois(LUMEN_L, 3.0) * q_si(Q_MEAN)) + 4,
            "the 3 mm lumen itself", fontsize=8, color="#555")
    a0.set_yscale("log")
    a0.set_title("Resistance: wants big bore", fontsize=10.5)
    a0.set_xlabel("tubing ID, mm")
    a0.set_ylabel("head loss at 250 mL/min, mm")
    a0.legend(fontsize=8, frameon=False)

    a1 = ax[1]
    for (name, e, _n), col in zip(MATERIALS,
                                  ("#b4462e", "#c98a2e", "#4a8f3c", "#2e6fb4")):
        a1.plot(dd, [100.0 * compliance(LEN_C, d, e) * pp_pa / stroke_m3
                     for d in dd], lw=2.0, color=col, label=name)
    a1.axhline(3.0, color="#555", ls="--", lw=1.2)
    a1.text(2.7, 3.4, "3 % of stroke", fontsize=8, color="#555")
    a1.set_yscale("log")
    a1.set_title("Compliance: wants small bore, stiff wall", fontsize=10.5)
    a1.set_xlabel("tubing ID, mm")
    a1.set_ylabel("stroke volume stolen by %.0f mm of zone C, %%" % LEN_C)
    a1.legend(fontsize=8, frameon=False)

    a2 = ax[2]
    for name, d in BORES:
        a2.plot([], [])
    a2.plot(dd, [head_mm(inertance(LEN_C, d) * dq_pk) for d in dd],
            color="#6b4aa0", lw=2.0)
    for name, d in BORES:
        a2.plot([d], [head_mm(inertance(LEN_C, d) * dq_pk)], "o",
                color="#6b4aa0", ms=5)
        a2.annotate(name, (d, head_mm(inertance(LEN_C, d) * dq_pk)),
                    textcoords="offset points", xytext=(5, 5), fontsize=7.5,
                    color="#444")
    a2.set_title("Inertance: wants big bore, but only delays", fontsize=10.5)
    a2.set_xlabel("tubing ID, mm")
    a2.set_ylabel("mm head to accelerate zone C at peak dQ/dt")

    for a in ax:
        a.grid(alpha=0.25, lw=0.6)
        for s in ("top", "right"):
            a.spines[s].set_visible(False)
    fig.suptitle("Tank to phantom: the three effects that pick a tubing bore, "
                 "and the one that destroys information",
                 fontsize=11.5, y=0.99)
    fig.text(0.5, 0.005,
             "Compliance is the only term a taller tank cannot buy back. It is "
             "beaten by material by 30x before bore is considered.",
             fontsize=8.3, color="#555", ha="center")
    fig.tight_layout(rect=(0, 0.03, 1, 0.94))
    out = os.path.join(HERE, "feed-tubing.png")
    fig.savefig(out, facecolor="white")
    print("")
    print("wrote feed-tubing.png")


if __name__ == "__main__":
    main()
