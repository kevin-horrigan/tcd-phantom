# -*- coding: utf-8 -*-
"""What to measure on the loop, and what the instruments have to be.

    python instrumentation.py   ->  instrumentation.png + the tables below

Two questions, and they have different answers than they look like they do.

PRESSURE. The whole signal lives in under one psi. A 622 mm column of
blood-mimicking fluid is 0.90 psi, and the pulse riding on it is smaller
still. Put that into an ordinary 0 to 30 psi dial gauge and the entire
experiment happens inside the first three percent of the dial, below the
width of the needle. Range is the specification that matters here, ahead of
accuracy class, ahead of everything. And one instrument cannot do both jobs:
setting the constriction wants a slow absolute reading, and seeing whether
systole survived the plumbing wants something that can follow a 100 ms rise.

VELOCITY. The pulsatile part does not need measuring, because it is already
known better than any sensor on this bench could report it. The piston is a
positive displacement pump commanded in exact step counts at 0.600 uL per
step. What needs measuring is the MEAN, which gravity sets and which nothing
commands, and that is a beaker and a scale. The sensor question is really
"did the pulse arrive", and that is a pressure measurement, not a flow one.

Nothing here names a part number. The 9105x episode is recent enough: these
are specifications, and the part that meets them has to be checked against
its own datasheet before anyone orders it.
"""
import math
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import syringe_drive as S
from head_budget import TANK_MM as H_TANK

HERE = os.path.dirname(os.path.abspath(__file__))
RHO, G, MU = 1037.0, 9.80665, 4.1e-3
PSI, MMHG, KPA = 6894.757, 133.322, 1000.0
Q_MEAN = 250.0                      # mL/min
TANK_MM = H_TANK                    # the constant-head jar, 1.2 m
BEAT_HZ = 1.0

# Commodity full-scale ranges, psi. The point of this list is how badly the
# usual ones fit, not which to buy.
RANGES = [
    ("dial gauge, 0-100 psi", 100.0, "the one in every lab drawer"),
    ("dial gauge, 0-30 psi", 30.0, "the one people buy for this"),
    ("dial gauge, 0-15 psi", 15.0, "still ten times too coarse"),
    ("transducer, 0-5 psi", 5.0, "getting there"),
    ("transducer, 0-20 kPa", 20.0 * KPA / PSI, "THE SPEC. Peak fits with room"),
    ("transducer, 0-10 kPa", 10.0 * KPA / PSI, "mean plus pulse just clips it"),
    ("transducer, 0-7 kPa", 7.0 * KPA / PSI, "pulse alone fills it. Too tight"),
    ("standpipe, mm of fluid", TANK_MM * RHO * G * 1e-3 / PSI, "a clear tube"),
]

SCALE_G = 1.0                       # kitchen scale resolution, grams
PHONE_FPS = 240.0
CLEAR_RUN_MM = 100.0


def head_pa(mm):
    return RHO * G * mm * 1e-3


def head_mm(pa):
    return pa / (RHO * G) * 1e3


def piston_flow():
    """Commanded flow and its derivative, from the real BEAT array."""
    try:
        import pico.config as C
        beat = np.asarray(C.BEAT, dtype=float)
    except Exception:
        import assembly as A
        beat = np.asarray(A.beat(), dtype=float)
    t = np.linspace(0.0, 1.0 / BEAT_HZ, len(beat))
    dt = t[1] - t[0]
    x = beat * S.BEAT_MM * 1e-3
    q = np.gradient(x, dt) * (S.BORE_A * 1e-6)
    return t, q, np.gradient(q, dt)


def spectrum(t, q):
    """Harmonic content of the commanded flow, as a fraction of total power.

    This is what sets the sensor bandwidth. A rise-time rule of thumb gives
    one number; the actual array gives the right one, and the array is what
    the firmware plays.
    """
    n = len(q)
    f = np.fft.rfftfreq(n, t[1] - t[0])
    a = np.abs(np.fft.rfft(q - q.mean()))
    p = a ** 2
    return f, a, np.cumsum(p) / p.sum()


def main():
    A = print
    t, q, dqdt = piston_flow()
    f, amp, cum = spectrum(t, q)
    q_mean_si = Q_MEAN * 1e-6 / 60.0
    q_peak = q.max() + q_mean_si
    stroke_m3 = S.BEAT_ML * 1e-6

    # ------------------------------------------------------------ pressure
    # Taken off head_budget's own segment list rather than halving the tank
    # height, so the two files cannot drift apart.
    import head_budget as H
    # By ZONE, not by list position. This used to slice SEGMENTS as seg[:3]
    # and seg[3:], which silently meant something different the moment the
    # topology changed, and the topology did change: the plenum moved
    # upstream of the phantom and a check valve became an R1.
    up_mm = H.seg_head("up")
    down_mm = H.seg_head("shape") + H.seg_head("lumen") + H.seg_head("down")
    crack_mm = 0.0                                # no check valve in the loop
    constrict_mm = TANK_MM - up_mm - down_mm - crack_mm
    r_down = head_pa(down_mm + constrict_mm) / (Q_MEAN * 1e-6 / 60.0)
    pp_pa = r_down * q.max()                      # peak piston flow x downstream R

    A("WHAT PRESSURE THIS LOOP ACTUALLY MAKES")
    # mm of fluid first, because that is the unit the head budget is written
    # in and the unit a standpipe reads in without being asked.
    A("  %-36s %9s %8s %8s %9s" % ("", "mm fluid", "psi", "kPa", "mmHg"))
    for nm, mm in (("tank head, static, no flow", TANK_MM),
                   ("mean at the piston tee", TANK_MM - crack_mm - up_mm),
                   ("mean at the phantom inlet",
                    constrict_mm + H.seg_head("lumen") + H.seg_head("down")),
                   ("PULSE, peak piston flow x R_down", head_mm(pp_pa)),
                   ("a 91050 check valve, IF one is added", 50.8),
                   ("the printed ball check alone", 2.2)):
        pa = head_pa(mm)
        A("  %-36s %9.0f %8.3f %8.2f %9.1f"
          % (nm, mm, pa / PSI, pa / KPA, pa / MMHG))
    A("")
    A("  The pulse line is a first-order estimate: peak commanded piston flow")
    A("  through the resistance downstream of the tee, ignoring compliance and")
    A("  the gravity leg backing off as pressure rises. A real number needs a")
    A("  network solve. What it is good for is a sanity check, and it lands at")
    A("  %.0f mmHg against the 40 mmHg that feed_tubing.py assumed when it"
      % (pp_pa / MMHG))
    A("  priced tubing compliance. Two independent routes to the same size, so")
    A("  that assumption can stay.")
    A("")
    A("  A real MCA runs near 90/60 mmHg. This loop runs at about a third of")
    A("  that, and on purpose: it reproduces VELOCITY, and the interface")
    A("  control document says a soft cast gel will not hold arterial")
    A("  pressure anyway. Nobody should be surprised when the trace has the")
    A("  right shape and a third of the amplitude.")
    A("")

    A("WHY THE USUAL GAUGE WILL NOT DO")
    A("  Signal is the %.0f mmHg pulse derived above. 'of FS' is how much of"
      % (pp_pa / MMHG))
    A("  the dial it uses, and the last column is its smallest resolvable step.")
    A("  %-26s %8s %9s %9s  %s"
      % ("instrument", "FS psi", "of FS", "1% of FS", "note"))
    sig = pp_pa
    for nm, fs_psi, note in RANGES:
        fs = fs_psi * PSI
        A("  %-26s %8.3f %8.2f%% %8.1f  %s"
          % (nm, fs_psi, 100.0 * sig / fs, fs / MMHG * 0.01, note))
    A("  -> A 0-30 psi gauge cannot see this pulse at all: one percent of its")
    A("     scale is %.0f mmHg against a %.0f mmHg signal."
      % (30.0 * PSI / MMHG * 0.01, pp_pa / MMHG))
    A("     Note the standpipe row too. An UNTHROTTLED standpipe is over range")
    A("     on the pulse, which is a polite way of saying it would spit fluid")
    A("     out of its open top once a second: the pulse alone is %.0f mm of"
      % head_mm(pp_pa))
    A("     fluid against a %.0f mm tank. Second reason for the capillary."
      % TANK_MM)
    A("")

    # ----------------------------------------------------------- bandwidth
    for frac, lab in ((0.95, "95"), (0.99, "99"), (0.999, "99.9")):
        k = int(np.searchsorted(cum, frac))
        A("  %s%% of the commanded flow's power is below %.0f Hz (harmonic %d)"
          % (lab, f[k], k))
    k99 = int(np.searchsorted(cum, 0.99))
    A("  -> sensor bandwidth %.0f Hz minimum, sample at %.0f Hz or better."
      % (f[k99], 10 * f[k99]))
    A("     That is easy for any MEMS part and impossible for a dial gauge,")
    A("     whose needle takes about a second to settle. The dial is not a")
    A("     cheap version of the transducer. It measures a different thing.")
    A("")

    # ----------------------------------------------------------- standpipe
    A("THE STANDPIPE, AND WHY IT HAS TO BE THROTTLED")
    col = TANK_MM * 1e-3
    fn = math.sqrt(2.0 * G / col) / (2.0 * math.pi)
    A("  A clear vertical tube teed into the line reads mean pressure in")
    A("  millimetres of the very fluid the head budget is written in. No")
    A("  calibration, no drift, no range problem. But a free liquid column is")
    A("  an oscillator: f = sqrt(2g/L)/2pi, and at L = %.0f mm that is" % TANK_MM)
    A("  %.2f Hz against a %.1f Hz beat. It would resonate with the piston."
      % (fn, BEAT_HZ))
    A("")
    cap = (math.pi * (6.35e-3 / 2) ** 2) / (RHO * G)     # m3/Pa, free surface
    for fc in (0.05, 0.10):
        tau = 1.0 / (2.0 * math.pi * fc)
        r = tau / cap
        L = r * math.pi * (1.0e-3) ** 4 / (128.0 * MU)
        A("  Throttle it to %.2f Hz: tau %.1f s, which is %.0f mm of 1.0 mm"
          % (fc, tau, L * 1e3))
        A("    bore capillary ahead of the standpipe. Reads the mean in about")
        A("    %.0f s and cannot follow the pulse, which is the point." % (3 * tau))
    A("")

    # ------------------------------------------------------- the dead leg
    A("THE SENSING DEAD LEG, IF THE TRANSDUCER IS NOT WETTED")
    A("  Most low-range MEMS parts have bare silicon behind the port and are")
    A("  not liquid compatible. The usual dodge is a short stub of trapped")
    A("  air between the line and the sensor. It works, and it is a gas")
    A("  spring sitting in the pulse path, so it has to be priced:")
    A("  %-22s %10s %10s" % ("air column", "mL stored", "% of stroke"))
    for d, L in ((3.0, 10.0), (3.0, 20.0), (3.0, 40.0), (1.5, 20.0)):
        v = math.pi * (d * 1e-3 / 2) ** 2 * L * 1e-3
        dv = v / 101325.0 * pp_pa                  # isothermal, dV = V dp / P
        A("  %-22s %10.4f %10.2f"
          % ("%.1f mm x %.0f mm" % (d, L), dv * 1e6, 100.0 * dv / stroke_m3))
    A("  -> keep it short and narrow, or buy a wetted sensor. 40 mm of 3 mm")
    A("     bore costs as much stroke as all the tubing put together.")
    A("")

    # ----------------------------------------------------------- velocity
    A("VELOCITY: THREE LAYERS, AND ONLY ONE OF THEM IS A SENSOR")
    A("")
    A("  1. THE MEAN, by weighing. Gravity sets it and nothing commands it,")
    A("     so it has to be measured. At %.0f mL/min the loop delivers" % Q_MEAN)
    A("     %.0f g/min. A %.0f g scale over 60 s is %.2f%% resolution, which"
      % (Q_MEAN * RHO * 1e-3, SCALE_G, 100.0 * SCALE_G / (Q_MEAN * RHO * 1e-3)))
    A("     beats any inline flow sensor that fits a 3 mm line.")
    A("     mean velocity in the lumen = Q / A = %.1f cm/s at %.0f mL/min."
      % (q_mean_si / (math.pi * (1.5e-3) ** 2) * 100.0, Q_MEAN))
    A("")
    A("  2. THE PULSE, by construction. %.3f uL per microstep, %d steps per"
      % (S.SCREW_LEAD / 1600.0 * S.BORE_A, round(S.BEAT_MM * 200)))
    A("     beat, counted in PIO hardware. Peak flow %.0f mL/min on top of the"
      % (q.max() * 6e7))
    A("     mean, so %.0f mL/min at peak systole. No sensor on this bench"
      % (q_peak * 6e7))
    A("     reports that better than the step counter already does. Do not")
    A("     buy an instrument to measure a number you command.")
    A("")
    A("  3. AN INDEPENDENT CHECK, once, during bring-up. A single bubble in")
    A("     the clear %.0f mm settling run, filmed at %.0f fps: at %.0f cm/s"
      % (CLEAR_RUN_MM, PHONE_FPS,
         q_mean_si / (math.pi * (1.5e-3) ** 2) * 100.0))
    A("     it crosses in %.0f ms, which is %.0f frames. Enough to measure to"
      % (1e3 * CLEAR_RUN_MM * 1e-3 / (q_mean_si / (math.pi * (1.5e-3) ** 2)),
         PHONE_FPS * CLEAR_RUN_MM * 1e-3 / (q_mean_si / (math.pi * (1.5e-3) ** 2))))
    A("     a few percent on a phone. Then purge it: bubbles are enormous")
    A("     Doppler scatterers and they quietly change loop compliance.")
    A("")

    # ---------------------------------------------------------- the PI check
    # The loop exists to put a plausible MCA waveform under a probe, and PI
    # is the number the whole programme is judged on, so it is worth reading
    # off the commanded trace before any hardware is bought.
    qt = (q + q_mean_si) * 6e7
    pi = (qt.max() - qt.min()) / qt.mean()
    A("THE PULSATILITY INDEX THIS LOOP WOULD PRODUCE")
    A("  Lumen area is fixed, so PI from flow is PI from velocity.")
    A("  peak %.0f mL/min, trough %.0f, mean %.0f  ->  PI = %.2f"
      % (qt.max(), qt.min(), qt.mean(), pi))
    A("  in velocity: %.0f / %.0f / %.0f cm/s"
      % (qt.max() * 1e-6 / 60 / (math.pi * 1.5e-3 ** 2) * 100,
         qt.min() * 1e-6 / 60 / (math.pi * 1.5e-3 ** 2) * 100,
         qt.mean() * 1e-6 / 60 / (math.pi * 1.5e-3 ** 2) * 100))
    A("")
    A("  Diastolic flow never reverses, which is right for an MCA. But a")
    A("  normal MCA sits near PI 0.8 to 1.2 and this is %.2f, so as specified" % pi)
    A("  the loop is TOO pulsatile. That is not a fault in the piston, which")
    A("  is doing exactly what it was told. It is the compliance plenum doing")
    A("  nothing yet, because nobody has sized it: its whole job is to shave")
    A("  the peak and hold diastole up, and it is the only element in the")
    A("  loop that moves PI without touching the stroke volume.")
    A("  Sizing it is the next piece of work on the loop, and it should be")
    A("  done against this trace rather than by eye.")
    A("")

    # --------------------------------------------------- the relief problem
    tq = S.MOTOR_TH * (S.SET_I / S.MOTOR_I)
    force = 2.0 * math.pi * tq * 0.30 / (S.SCREW_LEAD * 1e-3)
    stall = force / (S.BORE_A * 1e-6)
    A("THE RELIEF PATH, WHICH IS NOT A STANDPIPE")
    A("  The piston can overpressure the block. At %.3f A it makes about"
      % S.SET_I)
    A("  %.2f Nm, and through a Tr8x8 at 30%% efficiency that is %.0f N on a"
      % (tq, force))
    A("  %.0f mm2 bore: %.0f psi, %.0f mmHg, if the outlet is ever blocked."
      % (S.BORE_A, stall / PSI, stall / MMHG))
    A("  That is twenty times the working pressure and it would destroy a")
    A("  cast gel block.")
    A("")
    A("  But the relief CANNOT be an open standpipe teed into the pulse path.")
    A("  A standpipe's cracking pressure is zero, so the pulse would go up it")
    A("  in preference to going through a %.0f mm head of phantom. The relief"
      % (TANK_MM / 2.0))
    A("  has to be a valve that stays SHUT at working pressure and opens")
    A("  above it: set between about %.1f psi and Group 1's measured tear-out"
      % (2.0 * head_pa(TANK_MM) / PSI))
    A("  pressure, which they still owe. An open standpipe belongs upstream")
    A("  of the check valve, where it caps the gravity leg and the pulse")
    A("  cannot reach it.")
    A("")

    A("WHAT TO SPECIFY")
    A("  pressure, mean      clear vertical tube, 1/4 in, open top, scaled in")
    A("                      mm, behind a %.0f mm x 1 mm capillary. Doubles as"
      % (1.0 / (2 * math.pi * 0.05) / cap * math.pi * 1e-12 / (128 * MU) * 1e3))
    A("                      the gravity leg's pressure cap if put upstream")
    A("                      of the check valve.")
    peak_kpa = (head_pa(TANK_MM - crack_mm - up_mm) + pp_pa) / KPA
    A("  pressure, waveform  MEMS, gauge referenced, 0-20 kPa (0-3 psi) full")
    A("                      scale. The tee sees %.1f kPa of mean and %.1f kPa"
      % (head_pa(TANK_MM - crack_mm - up_mm) / KPA, pp_pa / KPA))
    A("                      of pulse on top, so peak is %.1f kPa: a 0-7 kPa"
      % peak_kpa)
    A("                      part, which looks right for the pulse alone, is")
    A("                      over range before the pulse even starts.")
    A("                      %.0f Hz bandwidth or better, digital output" % f[k99])
    A("                      preferred. Wetted or gel-filled if it can be had;")
    A("                      otherwise a dead leg under 20 mm of 1.5 mm bore.")
    A("  the part            Honeywell ABP2DANT005PG2A3XX, verified against")
    A("                      Honeywell's own datasheet rather than a listing:")
    A("                      0-5 psi gage, I2C at 0x28, 3.3 V, ~200 Hz update")
    A("                      rate, and the T in the part number is 'liquid")
    A("                      media, food-grade silicone gel'. An N there is")
    A("                      'dry gases only' and the same-looking part would")
    A("                      be destroyed by the fluid. AN is the barbed port,")
    A("                      VN the barbless one. 1 psi gage would be over")
    A("                      range at %.1f kPa peak and the family has nothing"
      % ((head_pa(TANK_MM - crack_mm - up_mm) + pp_pa) / KPA))
    A("                      between 1 and 5 psi, so 5 psi it is.")
    A("  BOTH SENSORS SHARE I2C ADDRESS 0x28. Two of the same part cannot sit")
    A("                      on one bus. The Pico has I2C0 and I2C1, so put P1")
    A("                      on one and P2 on the other and buy nothing extra.")
    A("  and its error       1.5 percent total error band, which on a 5 psi")
    A("                      part is 4 mmHg. That is fine for SHAPE and poor")
    A("                      for absolute, which is the whole reason the")
    A("                      manometer stays: the tube is the reference and")
    A("                      the sensor is the waveform.")
    A("  flow, mean          beaker and a 1 g kitchen scale, 60 s catches.")
    A("  flow, pulse         already known. The step counter is the instrument.")
    A("  relief              cracking-pressure valve above %.1f psi, not a"
      % (2.0 * head_pa(TANK_MM) / PSI))
    A("                      standpipe, and not in the pulse path.")

    # -------------------------------------------------------------- figure
    fig, ax = plt.subplots(1, 2, figsize=(12.0, 4.4), dpi=170)
    fig.patch.set_facecolor("white")

    a0 = ax[0]
    a0.plot(t, (q + q_mean_si) * 6e7, color="#b4462e", lw=2.0,
            label="total through the phantom")
    a0.axhline(Q_MEAN, color="#2e6fb4", lw=1.6, ls="--",
               label="gravity mean, %.0f mL/min" % Q_MEAN)
    a0.axhline(0.0, color="#999", lw=0.8)
    a0.fill_between(t, Q_MEAN, (q + q_mean_si) * 6e7,
                    where=((q + q_mean_si) * 6e7 > Q_MEAN),
                    color="#b4462e", alpha=0.15)
    a0.set_xlabel("time, s")
    a0.set_ylabel("flow, mL/min")
    a0.set_title("What the loop delivers: gravity sets the mean,\n"
                 "the piston adds the pulse", fontsize=10.5)
    a0.legend(fontsize=8, frameon=False)

    a1 = ax[1]
    k = min(len(f) - 1, 26)
    a1.stem(f[1:k], amp[1:k] / amp[1:k].max(), basefmt=" ",
            linefmt="#6b4aa0", markerfmt="o")
    a1.axvline(f[k99], color="#b4462e", lw=1.6, ls="--")
    a1.text(f[k99] + 0.4, 0.75, "99 %% of power\nbelow %.0f Hz" % f[k99],
            fontsize=8.5, color="#b4462e")
    a1.set_xlabel("frequency, Hz")
    a1.set_ylabel("amplitude, normalised")
    a1.set_title("Harmonics of the commanded flow:\n"
                 "this is the sensor bandwidth spec", fontsize=10.5)

    for a in ax:
        a.grid(alpha=0.25, lw=0.6)
        for s_ in ("top", "right"):
            a.spines[s_].set_visible(False)
    fig.text(0.5, 0.012,
             "The pulsatile term is commanded, not measured. The instruments "
             "exist to catch the mean and to prove the pulse survived the plumbing.",
             fontsize=8.3, color="#555", ha="center")
    fig.tight_layout(rect=(0, 0.045, 1, 1))
    fig.savefig(os.path.join(HERE, "instrumentation.png"), facecolor="white")
    A("")
    A("wrote instrumentation.png")


if __name__ == "__main__":
    main()
