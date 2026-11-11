# -*- coding: utf-8 -*-
"""What the plenum is made of, how big it is, and where the loop may rise.

    python plenum.py   ->  plenum.png + the text below

WHAT IT IS MADE OF. Trapped air over fluid in something RIGID and CLEAR,
standing upright. Rigid matters more than it sounds: the plenum's whole job
is to be the one soft thing in the loop, and a soft-walled vessel adds its
own compliance in parallel with the air, so the knob stops being a knob.
A polystyrene pipette wall is about two thousand times stiffer than the air
inside it, which is the margin you want. A rubber bulb would be the opposite.

Clear matters because the air volume IS the setting. You cannot set what you
cannot see, and a graduated vessel turns the setting into a reading.

Upright matters because gravity is what keeps the air on top of the fluid.
On its side the air finds the top of the bore and the interface runs the
length of the tube, so the volume stops being well defined and gas gets
dragged into the loop.

HOW BIG. Sized here from the loop's own downstream resistance rather than
copied, and it lands on top of the number Greaby measured, which is the best
corroboration available for something nobody on this bench has run yet.

DOES THE TUBING EVER NEED TO GO UP. Three places, and the reasons are
different in each. The rest should be flat, and flat is the correct answer
rather than merely the convenient one. See the last section.
"""
import math
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import head_budget as H
import syringe_drive as S

HERE = os.path.dirname(os.path.abspath(__file__))
P_ATM = 101325.0
MMHG = 133.322
EJECT_S = 0.40                  # the piston's ejection takes this long

# Candidate vessels. "rigid" is the wall's own compliance as a fraction of
# the air's, at 20 mL of air, so smaller is better and anything under a
# percent is irrelevant.
VESSELS = [
    ("60 mL syringe, plunger in", 26.5, 1.8, 2.4e9, True,
     "graduated, luer at the tip, and the plunger SETS the volume"),
    ("25 mL serologic pipette", 10.0, 1.0, 3.0e9, True,
     "Greaby's part. Graduated, needs a stopcock on top"),
    ("acrylic tube, capped", 20.0, 3.0, 3.2e9, True,
     "machine it, no graduations unless you add a scale"),
    ("glass test tube", 16.0, 1.2, 64e9, True,
     "stiffest of the lot, awkward to connect"),
    ("soft silicone bulb", 20.0, 2.0, 1.5e6, False,
     "NO. Its wall is softer than the air and swamps the setting"),
]


def seg(name):
    L, d = {n: (L, d) for n, L, d, _z in H.SEGMENTS}[name]
    return H.head_mm(H.r_poiseuille(L, d) * H.q_si(H.Q_MEAN))


def r_downstream():
    """Pa.s/m3 from the plenum tee to the reservoir, R2 included.

    This is what the plenum discharges into, so it is what sets the time
    constant. Everything upstream of the tee is irrelevant to the smoothing.
    """
    mm = (seg("settling run, 3 mm") + seg("phantom lumen")
          + seg("phantom to R2") + seg("return to reservoir"))
    r2_mm = H.TANK_MM - sum(seg(n) for n, _L, _d, _z in H.SEGMENTS)
    return H.RHO * H.G * (mm + r2_mm) * 1e-3 / H.q_si(H.Q_MEAN)


def air_for_tau(tau, r, gamma=1.0):
    """mL of trapped air giving time constant tau. C = V / (gamma * P)."""
    return tau / r * gamma * P_ATM * 1e6


def wall_fraction(bore_mm, wall_mm, e_pa, air_ml=20.0):
    """Vessel wall compliance as a fraction of the trapped air's."""
    d, h, L = bore_mm * 1e-3, wall_mm * 1e-3, 0.25
    c_wall = math.pi * d ** 3 * L / (4.0 * e_pa * h)
    c_air = air_ml * 1e-6 / P_ATM
    return c_wall / c_air


def main():
    A = print
    r = r_downstream()

    A("WHAT IT IS MADE OF")
    A("  Rigid and clear, standing upright. Wall stiffness is the whole")
    A("  question, so here it is as a number: each vessel's own wall")
    A("  compliance as a fraction of the 20 mL of air inside it.")
    A("  %-28s %7s %7s %11s  %s"
      % ("vessel", "bore", "wall", "wall/air", "note"))
    for nm, bore, wall, e, ok, note in VESSELS:
        f = wall_fraction(bore, wall, e)
        A("  %-28s %6.1f %7.1f %10.4f%%  %s"
          % (nm, bore, wall, 100.0 * f, note if ok else note))
    A("")
    A("  Anything under about one percent means the air is the compliance")
    A("  and the vessel is just a container. The silicone bulb is there to")
    A("  show what failing looks like: its wall is softer than the air, so")
    A("  turning the air volume up and down would barely change anything.")
    A("")
    A("  RECOMMENDATION: a 60 mL syringe, tip down, plunger in, clamped so")
    A("  it cannot creep. The plunger sets the air volume, the graduations")
    A("  read it out, and the luer tip meets the barb-to-luer adapter that")
    A("  is already in the bill of materials. At %.1f psi on a %.0f mm bore"
      % (H.RHO * H.G * H.TANK_MM * 1e-3 / H.PSI, 26.5))
    A("  the plunger sees about %.0f N, which is the same order as its own"
      % (H.RHO * H.G * H.TANK_MM * 1e-3 * math.pi * (26.5e-3 / 2) ** 2))
    A("  breakout friction, so it WILL creep over a long run if it is not")
    A("  held. A clamp on the rod, or a collar behind the thumb rest.")
    A("")
    A("  NOTHING IS PLUGGED. The syringe stands tip DOWN and OPEN to the")
    A("  loop: fluid rises into the barrel from the tip, air sits above it,")
    A("  and the plunger seals the top. Clamping the plunger stops it")
    A("  SLIDING, it does not close the fluid path. If the tip were blocked")
    A("  the plenum would do nothing at all, because nothing could get in")
    A("  and out of it, and that is the whole mechanism.")
    A("")
    A("  ONE THING TO WATCH over a long run: air dissolves into the fluid,")
    A("  so the level creeps up and the air volume quietly shrinks, which")
    A("  moves the compliance mid-experiment. The graduations are how you")
    A("  catch it, and the plunger is how you put it back without opening")
    A("  anything. Read it at the start and end of every sweep point."),
    A("")

    # ------------------------------------------------- why it works at all
    A("HOW FLUID GETS IN WHEN THERE IS ALREADY AIR IN THERE")
    A("  Because the AIR is the compressible one. The liquid is not. That is")
    A("  the wrong way round from how it feels, and it is the entire")
    A("  mechanism, so it is worth a number:")
    A("")
    A("  %-28s %14s %12s" % ("squeeze 1 % out of...", "needs", "psi"))
    for nm, dp in (("air at 1 atm", 1.4 * P_ATM * 0.01),
                   ("150 mm of 1/4 in silicone", 4.75e-8 / 1.257e-11),
                   ("150 mm of 1/4 in braided PVC", 4.75e-8 / 1.34e-12),
                   ("the blood-mimicking fluid", 2.2e9 * 0.01)):
        A("  %-28s %11.0f Pa %12.2f" % (nm, dp, dp / H.PSI))
    A("")
    A("  Air gives way about %.0f thousand times more easily than the fluid"
      % (2.2e9 * 0.01 / (1.4 * P_ATM * 0.01) / 1000.0))
    A("  does. So when the piston pushes, nothing happens to the liquid at")
    A("  all: the pressure rises, the trapped air shortens, and fluid climbs")
    A("  into the barrel to fill the space the air just gave up. Between")
    A("  beats the air springs back and pushes that fluid out again. The")
    A("  plenum BREATHES. The air is the spring and the liquid column is")
    A("  just the face that pushes on it.")
    A("")
    A("  How far it breathes, at 20 mL of air and a %.0f mmHg pulse:" % 39.0)
    dv = 20e-6 * (39.0 * MMHG) / (1.4 * P_ATM)
    for nm, bore in (("60 mL syringe", 26.5), ("25 mL pipette", 10.0)):
        a = math.pi * (bore * 1e-3 / 2) ** 2
        A("    %-16s %.2f mL, which is %.1f mm of level in a %.0f mm bore"
          % (nm, dv * 1e6, dv / a * 1e3, bore))
    A("  Same compliance either way, because that depends only on the air")
    A("  VOLUME. The narrow one just shows you the breathing, which is worth")
    A("  having on a rig nobody has run before.")
    A("")
    A("  And the silicone line in that table is the other warning made")
    A("  concrete: silicone tubing is only about %.0fx stiffer than the air"
      % ((4.75e-8 / 1.257e-11) / (1.4 * P_ATM * 0.01)))
    A("  itself. Plumb the loop in it and you have not avoided a plenum, you")
    A("  have built a second one, spread along the bench where you cannot")
    A("  see it, measure it or turn it down. Braided PVC is %.0fx."
      % ((4.75e-8 / 1.34e-12) / (1.4 * P_ATM * 0.01)))
    A("")
    A("  The bicycle pump is the whole thing in one image. Finger over the")
    A("  outlet, push, and the handle moves: that is the air compressing.")
    A("  Fill the barrel with water instead, finger over the outlet, push,")
    A("  and nothing moves at all. Greaby's 'no air gives short high spikes'")
    A("  IS the second case: with nothing to give, the piston's half")
    A("  millilitre goes straight into pressure.")
    A("")

    # ------------------------------------------------------------- sizing
    A("HOW BIG")
    A("  The plenum fills during systole and empties through everything")
    A("  downstream of it, so its time constant is")
    A("")
    A("      tau = R_down x C,      C = V_air / (gamma x atmospheric)")
    A("")
    A("  R_down here is %.2e Pa.s/m3, which is the settling run, the lumen," % r)
    A("  the return, and R2. Ejection takes about %.0f ms, so tau wants to be"
      % (EJECT_S * 1e3))
    A("  the same order: too short and the plenum empties before it has")
    A("  helped, too long and it never fills.")
    A("")
    A("  %-14s %14s %14s" % ("tau", "mL, isothermal", "mL, adiabatic"))
    for tau in (0.05, 0.10, 0.20, 0.40, 0.80):
        A("  %-14s %14.0f %14.0f"
          % ("%.2f s" % tau, air_for_tau(tau, r), air_for_tau(tau, r, 1.4)))
    A("")
    A("  Greaby measured this rather than calculating it: no air gave short")
    A("  high spikes, 6 mL was underdamped and rang, 20 mL resembled an")
    A("  arterial signal. On this loop 6 mL is tau %.2f s and 20 mL is tau"
      % (6e-6 / P_ATM * r))
    A("  %.2f s, so their ringing and their good result land exactly where"
      % (20e-6 / P_ATM * r))
    A("  this arithmetic says they should. Two independent routes agreeing")
    A("  is the most this can be checked before the loop exists.")
    A("")
    A("  SO: build for 10 to 50 mL of air and start at 20. A 60 mL syringe")
    A("  covers the whole range with the fluid interface still visible.")
    A("")
    A("  AND NOTE WHAT THIS MEANS FOR THE SWEEP. The air volume needed")
    A("  scales as 1/R_down, so turning R2 up means needing LESS air. The")
    A("  plenum and R2 are not independent knobs, which is exactly why the")
    A("  deliverable is a compliance-AND-resistance map rather than two")
    A("  separate calibrations.")
    A("")

    # ------------------------------------------------------------ routing
    A("DOES THE TUBING EVER NEED TO GO UP")
    A("  Three places, and only three:")
    A("")
    A("    1. DOWN from the jar. That is the one height that matters and it")
    A("       is a drop, not a rise.")
    A("    2. THE PLENUM stands up. Gravity is what holds the air above the")
    A("       fluid, so this one is not negotiable.")
    A("    3. THE PRESSURE TAP STUBS point up, if the sensors are the")
    A("       air-coupled kind. Air stays at the top of a rising stub and")
    A("       fluid cannot creep down to the die.")
    A("")
    A("  Everything else should be FLAT on the bench, and flat is the right")
    A("  answer rather than just the easy one.")
    A("")
    A("  Why it is free to be flat: the push is set by the DIFFERENCE between")
    A("  two free surfaces, the jar's and the reservoir's. The route between")
    A("  them costs nothing. A loop of tubing that climbs 300 mm and comes")
    A("  back down is worth exactly zero mm of head either way.")
    A("")
    A("  Why it should still be flat: every local high point collects air.")
    A("  Bubbles are enormous Doppler scatterers and they are also an")
    A("  uncontrolled second plenum, so a trapped bubble changes the one")
    A("  thing the compliance sweep is trying to measure. Route so that gas")
    A("  can always travel forward to somewhere it can be bled, which in")
    A("  practice means no humps.")
    A("")
    A("  THE TRAP, and it is an easy one. The head is jar surface to")
    A("  RESERVOIR surface, not jar surface to bench. Stand the reservoir on")
    A("  the floor instead of the bench and the drop grows by the height of")
    A("  the bench:")
    A("  %-26s %10s %12s %12s" % ("reservoir sits", "drop mm", "vs budget", "flow"))
    for nm, extra in (("level with the block", 0.0), ("on a low shelf", 250.0),
                      ("on the floor", 750.0)):
        drop = H.TANK_MM + extra
        A("  %-26s %10.0f %11.0f%% %11.0f%%"
          % (nm, drop, 100.0 * drop / H.TANK_MM, 100.0 * drop / H.TANK_MM))
    A("  Flow through a fixed resistance is proportional to the drop, so a")
    A("  reservoir on the floor is not a tidy choice, it is a %.0f percent"
      % (100.0 * (H.TANK_MM + 750.0) / H.TANK_MM - 100.0))
    A("  increase in flow that nothing on the drawing accounts for. Put the")
    A("  reservoir's free surface level with the block, or measure the real")
    A("  drop and put THAT number in the budget.")

    # ------------------------------------------------------------- figure
    fig, ax = plt.subplots(1, 3, figsize=(17.4, 5.0), dpi=165)
    fig.patch.set_facecolor("white")

    # The concept panel reads first, because "air is the compressible one"
    # is the thing the rest of the drawing rests on.
    a2 = ax[0]
    items = [("air at 1 atm", 1.4 * P_ATM * 0.01, "#4a8f3c"),
             ("1/4 in silicone", 4.75e-8 / 1.257e-11, "#b4462e"),
             ("1/4 in braided PVC", 4.75e-8 / 1.34e-12, "#2e6fb4"),
             ("the fluid itself", 2.2e9 * 0.01, "#3c3c3c")]
    a2.barh(range(len(items))[::-1], [i[1] / H.PSI for i in items],
            color=[i[2] for i in items], height=0.58)
    a2.set_yticks(range(len(items))[::-1])
    a2.set_yticklabels([i[0] for i in items], fontsize=9.5)
    a2.set_xscale("log")
    for k, (nm, dp, c) in enumerate(items):
        a2.text(dp / H.PSI * 1.5, len(items) - 1 - k, "%.2f psi" % (dp / H.PSI)
                if dp / H.PSI < 100 else "%.0f psi" % (dp / H.PSI),
                va="center", fontsize=9, color=c, fontweight="semibold")
    a2.set_xlim(0.08, 9e5)
    a2.set_xlabel("pressure needed to squeeze 1 % of the volume out")
    a2.set_title("Why fluid can get in at all:\nthe AIR is the soft one, "
                 "not the liquid", fontsize=10.5)

    a0 = ax[1]
    vols = np.linspace(2, 70, 300)
    a0.plot(vols, vols * 1e-6 / P_ATM * r, color="#b4462e", lw=2.2,
            label="isothermal")
    a0.plot(vols, vols * 1e-6 / (1.4 * P_ATM) * r, color="#2e6fb4", lw=2.2,
            ls="--", label="adiabatic")
    a0.axhspan(0.15, 0.45, color="#4a8f3c", alpha=0.12)
    a0.text(3, 0.30, "useful range\ntau near the\n%.0f ms ejection"
            % (EJECT_S * 1e3), fontsize=8.5, color="#3c7a4a", va="center")
    for v, nm, c in ((6.0, "Greaby: rang", "#b4462e"),
                     (20.0, "Greaby: good", "#4a8f3c")):
        a0.axvline(v, color=c, lw=1.2, ls=":")
        a0.text(v + 1.2, 0.74, nm, fontsize=8.5, color=c, rotation=90,
                va="top")
    a0.set_xlabel("trapped air, mL")
    a0.set_ylabel("time constant, s")
    a0.set_ylim(0, 0.85)
    a0.set_title("How big: sized from this loop's own\ndownstream resistance",
                 fontsize=10.5)
    a0.legend(fontsize=8.5, frameon=False, loc="lower right")

    a1 = ax[2]
    names = [v[0].split(",")[0] for v in VESSELS]
    fr = [100.0 * wall_fraction(v[1], v[2], v[3]) for v in VESSELS]
    cols = ["#2e6fb4" if v[4] else "#b4462e" for v in VESSELS]
    a1.barh(range(len(names))[::-1], fr, color=cols, height=0.6)
    a1.set_yticks(range(len(names))[::-1])
    a1.set_yticklabels(names, fontsize=9)
    a1.set_xscale("log")
    a1.axvline(1.0, color="#555", ls="--", lw=1.3)
    a1.text(1.35, 4.35, "1 % of the\nair's compliance", fontsize=8.5,
            color="#555", va="top")
    a1.set_xlabel("vessel wall compliance, % of the trapped air's")
    a1.set_title("What it is made of: the wall has to be\nirrelevant next to "
                 "the air", fontsize=10.5)

    for a in ax:
        a.grid(alpha=0.25, lw=0.6)
        for sp in ("top", "right"):
            a.spines[sp].set_visible(False)
    fig.suptitle("The plenum: an air spring with a liquid face",
                 fontsize=13, y=0.99)
    fig.text(0.5, 0.012,
             "Build for 10 to 50 mL of air and start at 20 mL. A 60 mL "
             "syringe standing tip down, plunger in and clamped, covers it.",
             fontsize=9, color="#555", ha="center")
    fig.tight_layout(rect=(0, 0.04, 1, 0.94))
    fig.savefig(os.path.join(HERE, "plenum.png"), facecolor="white")
    A("")
    A("wrote plenum.png")


if __name__ == "__main__":
    main()
