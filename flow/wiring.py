# -*- coding: utf-8 -*-
"""How P1 and P2 wire to the Pico, and what they can and cannot tell you.

    python wiring.py          -> wiring.png, plus the numbers

ASSUMES THE MPX5050GP, which is what bom.py and GROUP-2_phase0-bench-rig.md
specify. If the part that arrived is a different MPX5xxx the wiring is
identical and only SENS and the full scale change, both of which live in
pico/pressure.py.

THE ONE THING THAT WILL BREAK A PICO. The sensor wants 4.75 to 5.25 V and
swings its output to 4.70 V at full scale. The Pico's ADC pin is 3.3 V. Wire
the output straight to GP26 and you are putting 4.7 V into a 3.3 V pin.

Running the sensor at 3.3 V instead looks like the easy way out and is not:
the datasheet specifies 4.75 V minimum and calls the device ratiometric only
"within this specified excitation range". Below that you are off the
characterised curve with no way to know by how much. Supply it properly and
divide the output.
"""
import math
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

import pressures as PR

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "wiring.png")

VS = 5.0
R_TOP, R_BOT = 10.0e3, 20.0e3
CAP = 0.47e-6            # the specified film part. 0.40e-6 from four
                         # 100 nF ceramics in parallel is also fine, see the
                         # table in pico/pressure.py. A single 100 nF is not
ADC_REF, ADC_BITS = 3.3, 12
SENS, OFFSET = 0.018, 0.04          # Vout = VS * (SENS * P_kPa + OFFSET)
FS_KPA = 50.0
MMHG_PER_KPA = 1000.0 / 133.322

INK = "#1a1a1a"
RED = "#b3202c"
BLU = "#1f4e79"
GRN = "#2e6b34"
PAPER = "#ffffff"


def numbers():
    div = R_BOT / (R_TOP + R_BOT)
    v0 = VS * OFFSET
    vfs = VS * (SENS * FS_KPA + OFFSET)
    rsrc = R_TOP * R_BOT / (R_TOP + R_BOT)
    fc = 1.0 / (2.0 * 3.14159265 * rsrc * CAP)
    counts = 2 ** ADC_BITS
    lsb_v = ADC_REF / counts
    lsb_kpa = lsb_v / div / VS / SENS
    load_ma = vfs / (R_TOP + R_BOT) * 1000.0
    return dict(div=div, v0=v0, vfs=vfs, v0d=v0 * div, vfsd=vfs * div,
                rsrc=rsrc, fc=fc, lsb_v=lsb_v, lsb_kpa=lsb_kpa,
                lsb_mmhg=lsb_kpa * MMHG_PER_KPA, load_ma=load_ma,
                fs_mmhg=FS_KPA * MMHG_PER_KPA)


def report():
    n = numbers()
    A = print
    A("THE PART")
    A("  MPX5050GP, 6-pin SIP. From the datasheet:")
    A("    supply          4.75 / 5.00 / 5.25 V. NOT 3.3 V")
    A("    supply current  7 mA typical, 10 mA max, so 20 mA for the pair")
    A("    transfer        Vout = VS x (0.018 x P + 0.04), P in kPa")
    A("    full scale      50 kPa = %.0f mmHg, at %.2f V" % (n["fs_mmhg"], n["vfs"]))
    A("    zero            %.2f V, which is NOT 0 V. That gap is a diagnostic"
      % n["v0"])
    A("    accuracy        +-2.5%% of full scale = +-%.1f mmHg"
      % (0.025 * n["fs_mmhg"]))
    A("    response        1.0 ms")
    A("    pins 4, 5, 6    internal. Not to external circuitry and NOT to")
    A("                    ground either, which is what the datasheet says")
    A("")
    A("  PIN 1 IS THE LEAD WITH THE NOTCH IN IT, not a notch in the side of")
    A("  the package. The datasheet's words are 'pin 1 is noted by the notch")
    A("  in the lead'. Look at the metal legs, find the one with a bite out")
    A("  of it, and count from there. The package has moulding marks of its")
    A("  own, and there is an NXP forum thread of somebody asking whether")
    A("  the notched pin might be pin 6, so this is worth half a minute:")
    A("  backwards puts 5 V into the output pin and the part is gone.")
    A("")

    A("THE DIVIDER, and why it is not optional")
    A("  Sensor swings to %.2f V. The Pico ADC tops out at %.1f V."
      % (n["vfs"], ADC_REF))
    A("    %.0fk over %.0fk       ratio %.3f" % (R_TOP / 1e3, R_BOT / 1e3, n["div"]))
    A("    zero reads         %.3f V at the pin" % n["v0d"])
    A("    full scale reads   %.3f V at the pin, under %.1f with room to spare"
      % (n["vfsd"], ADC_REF))
    A("    loads the sensor   %.2f mA" % n["load_ma"])
    A("")
    A("  The cap across the lower resistor is the anti-alias filter, not")
    A("  decoration. Source impedance is %.1fk, so it rolls off at %.0f Hz."
      % (n["rsrc"] / 1e3, n["fc"]))
    A("  The sensor answers in 1 ms, which is 1 kHz of bandwidth, and")
    A("  sampling that at 250 Hz without a filter folds every bit of it back")
    A("  into the band we care about. It also gives the ADC a low impedance")
    A("  to charge from, which a bare %.1fk divider would not."
      % (n["rsrc"] / 1e3))
    A("")
    A("  WHICH CAP. The spec is one 0.47 uF film per sensor, 51 Hz. Kevin's")
    A("  MOGAOPI kit has no film part, so the filter is four 100 nF ceramics")
    A("  in parallel: 0.40 uF, %.0f Hz, which is fine. Sampling is 250 Hz,"
      % (1.0 / (2.0 * math.pi * n["rsrc"] * 0.40e-6)))
    A("  Nyquist is 125 and the pulse lives below 20, so the filter still")
    A("  sits between the signal and the fold-back.")
    A("    4 x 100 nF    %3.0f Hz   use this" % (
        1.0 / (2.0 * math.pi * n["rsrc"] * 0.40e-6)))
    A("    0.47 uF film  %3.0f Hz   the spec, if you have one" % (
        1.0 / (2.0 * math.pi * n["rsrc"] * 0.47e-6)))
    A("    1 x 100 nF    %3.0f Hz   NO. Above Nyquist, so it filters" % (
        1.0 / (2.0 * math.pi * n["rsrc"] * 0.10e-6)))
    A("                           nothing that matters")
    A("    0.47 uF elec  %3.0f Hz   fallback, + to the ADC node. Leakage" % (
        1.0 / (2.0 * math.pi * n["rsrc"] * 0.47e-6)))
    A("                           through %.1fk is a DC offset: 1 uA is"
      % (n["rsrc"] / 1e3))
    A("                           %.1f mV, %.0f counts, %.2f mmHg, and it"
      % (1e-6 * n["rsrc"] * 1e3, 1e-6 * n["rsrc"] / n["lsb_v"],
         1e-6 * n["rsrc"] / n["lsb_v"] * n["lsb_mmhg"]))
    A("                           drifts with temperature")
    A("")

    A("WHAT YOU GET")
    A("  one ADC count      %.3f mV = %.4f kPa = %.3f mmHg"
      % (n["lsb_v"] * 1000, n["lsb_kpa"], n["lsb_mmhg"]))
    A("  sensor's own error +-%.1f mmHg" % (0.025 * n["fs_mmhg"]))
    A("")
    A("  So the ADC is %.0f times finer than the sensor. The divider costs"
      % (0.025 * n["fs_mmhg"] / n["lsb_mmhg"]))
    A("  nothing and resolution is not the limit. The SENSOR is.")
    A("")

    A("AND HERE IS THE HONEST PART")
    peak = 69.6
    A("  P1 peaks at about %.0f mmHg and full scale is %.0f. We are using"
      % (peak, n["fs_mmhg"]))
    A("  %.0f%% of the range, so the +-%.1f mmHg sits at +-%.0f%% of the"
      % (100 * peak / n["fs_mmhg"], 0.025 * n["fs_mmhg"],
         100 * 0.025 * n["fs_mmhg"] / peak))
    A("  actual peak. That is a lot, and it is not fixable in firmware.")
    A("")
    A("  It matters much less than it looks, because of WHAT these are for:")
    A("    the shape of the pulse   offset error is a constant and cancels,")
    A("                             span error is one scale factor")
    A("    P1 minus P2              both sensors see the same offset drift")
    A("    is the piston working    a seal leak or trapped air is obvious")
    A("    absolute mean pressure   NOT this. The manometer does that, and")
    A("                             a ruler against a column of the loop's")
    A("                             own fluid has no calibration to drift")
    A("")
    A("  Which is the division of labour the loop was already built around:")
    A("  the manometer is the reference and P1 and P2 are the fast channel.")
    A("  Zero them against the manometer at rest and the offset goes away.")
    A("")

    A("WIRING, per sensor")
    A("  pin 1  Vout -> 10k -> ADC pin, 20k from there to GND, and the")
    A("         filter cap across that 20k")
    A("  pin 2  GND  -> Pico GND")
    A("  pin 3  Vs   -> Pico VBUS, physical pin 40. 1 uF to GND at the part.")
    A("         The kit's 1 uF is an ELECTROLYTIC, so + goes to pin 3 and -")
    A("         to pin 2. Backwards it conducts and then vents")
    A("  P1 -> GP26 (ADC0), P2 -> GP27 (ADC1). GP2/3/4 are the stepper")
    A("")
    A("  VBUS IS ONLY LIVE ON USB. If the Pico is ever run from VSYS the")
    A("  sensors go dark and read about 0 V, and 0 V is not zero pressure,")
    A("  it is %.2f V below it. pressure.check() catches exactly this."
      % n["v0"])
    A("")
    A("  Ground the sensors back to the Pico, not to the stepper supply.")
    A("  One ADC count is %.1f mV and a stepper's ground bounce is larger"
      % (n["lsb_v"] * 1000))
    A("  than that, so a shared return path puts the motor in your signal.")


def draw():
    n = numbers()
    fig = plt.figure(figsize=(13.5, 8.6), facecolor=PAPER)
    ax = fig.add_axes((0.0, 0.0, 1.0, 1.0))
    ax.set_xlim(0, 135)
    ax.set_ylim(0, 86)
    ax.axis("off")

    def txt(x, y, s, size=8.4, c=INK, ha="left", va="center", w=None, st=None):
        ax.text(x, y, s, fontsize=size, color=c, ha=ha, va=va,
                fontweight=w, style=st, family="DejaVu Sans")

    def wire(pts, c=INK, lw=1.5, ls="-"):
        ax.plot([p[0] for p in pts], [p[1] for p in pts],
                color=c, lw=lw, ls=ls, solid_capstyle="round", zorder=2)

    def dot(x, y, c=INK, r=0.7):
        ax.add_patch(plt.Circle((x, y), r, color=c, zorder=4))

    txt(3, 82.5, "P1 and P2 to the Pico", 17, INK, w="bold")
    txt(3, 78.4, "MPX5050GP.  The divider is not optional: the sensor swings to "
                 "%.2f V and the ADC pin is %.1f V." % (n["vfs"], ADC_REF),
        9.6, RED)

    # ---------------------------------------------------------- the sensor
    for idx, (name, ycen, col) in enumerate((("P1", 57.0, BLU),
                                             ("P2", 26.0, GRN))):
        sx, sy = 6.0, ycen - 9.0
        ax.add_patch(FancyBboxPatch((sx, sy), 20, 18,
                                    boxstyle="round,pad=0.5", fc="#f4f4f6",
                                    ec=col, lw=1.8, zorder=3))
        txt(sx + 10, sy + 15.0, name, 13, col, ha="center", w="bold")
        txt(sx + 10, sy + 11.6, "MPX5050GP", 8.0, INK, ha="center")
        # the notch, drawn where it really is
        ax.add_patch(Rectangle((sx - 0.5, sy + 6.6), 1.0, 2.0, fc=RED,
                               ec=RED, zorder=5))
        txt(sx - 1.4, sy + 7.6, "notch", 7.2, RED, ha="right")
        txt(sx + 10, sy + 4.2, "pin 1 is the lead\nwith the notch", 7.6, RED,
            ha="center")
        txt(sx + 10, sy + 0.6, "pins 4 5 6 = N/C", 7.2, "#777", ha="center")

        p1y, p2y, p3y = sy + 13.0, sy + 9.0, sy + 5.0
        for py, lab in ((p1y, "1 Vout"), (p2y, "2 GND"), (p3y, "3 Vs")):
            txt(sx + 20.6, py, lab, 7.4, INK)

        # ------------------------------------------------ Vout -> divider
        jx = 62.0                       # the divider tap
        wire([(sx + 20, p1y), (44, p1y)], col, 1.8)
        # R top
        ax.add_patch(Rectangle((44, p1y - 1.6), 9, 3.2, fc="#fff", ec=INK,
                               lw=1.4, zorder=3))
        txt(48.5, p1y + 0.1, "10k", 7.6, INK, ha="center")
        wire([(53, p1y), (jx, p1y)], col, 1.8)
        dot(jx, p1y, col)
        wire([(jx, p1y), (88, p1y)], col, 1.8)

        # R bottom
        wire([(jx, p1y), (jx, p1y - 9)], INK, 1.4)
        ax.add_patch(Rectangle((jx - 1.6, p1y - 13), 3.2, 4, fc="#fff",
                               ec=INK, lw=1.4, zorder=3))
        txt(jx + 2.6, p1y - 11, "20k", 7.6, INK)
        wire([(jx, p1y - 13), (jx, p1y - 16)], INK, 1.4)

        # the cap, in parallel
        cx = jx + 11
        wire([(jx, p1y - 4.5), (cx, p1y - 4.5), (cx, p1y - 9.4)], INK, 1.4)
        wire([(cx - 2.4, p1y - 9.4), (cx + 2.4, p1y - 9.4)], INK, 1.6)
        wire([(cx - 2.4, p1y - 10.9), (cx + 2.4, p1y - 10.9)], INK, 1.6)
        txt(cx + 3.4, p1y - 10.1, "0.47 uF", 7.6, INK)
        wire([(cx, p1y - 10.9), (cx, p1y - 16), (jx, p1y - 16)], INK, 1.4)
        dot(jx, p1y - 4.5, INK, 0.55)

        # ground symbol
        gy = p1y - 16
        for k, half in enumerate((3.0, 2.0, 1.0)):
            wire([(jx - half, gy - k * 1.1), (jx + half, gy - k * 1.1)],
                 INK, 1.4)

        # GND and Vs runs
        wire([(sx + 20, p2y), (34, p2y), (34, gy - 1.1)], INK, 1.4)
        dot(34, gy - 1.1, INK, 0.55)
        wire([(34, gy - 1.1), (jx - 3.0, gy - 1.1)], INK, 1.4)
        wire([(sx + 20, p3y), (30, p3y), (30, 66.0), (88, 66.0)], RED, 1.8)

        txt(70, p1y + 2.4, "%s to %s" % (name, "GP26" if idx == 0 else "GP27"),
            8.6, col, w="bold")

    # 1 uF decoupling note on the 5 V rail
    txt(31, 63.4, "1 uF to GND at each sensor", 7.6, RED)

    # ------------------------------------------------------------ the Pico
    px, py, pw, ph = 88.0, 12.0, 20.0, 64.0
    ax.add_patch(FancyBboxPatch((px, py), pw, ph, boxstyle="round,pad=0.6",
                                fc="#f7f5ef", ec=INK, lw=2.0, zorder=3))
    txt(px + pw / 2, 72.8, "Pico", 14, INK, ha="center", w="bold")
    txt(px + pw / 2, 69.4, "ADC pin is 3.3 V", 8.2, RED, ha="center")

    for yy, lab, c in ((66.0, "VBUS  pin 40", RED),
                       (61.0, "GP26  ADC0", BLU),
                       (30.0, "GP27  ADC1", GRN),
                       (20.0, "GND", INK),
                       (16.0, "GP2 3 4  stepper", "#888")):
        txt(px + 1.6, yy, lab, 7.8, c)

    # tie the grounds in
    wire([(65.0, 14.0), (84, 14.0), (84, 20.0), (px, 20.0)], INK, 1.4)
    wire([(65.0, 45.0), (84, 45.0), (84, 20.0)], INK, 1.4)
    dot(84, 20.0, INK, 0.55)

    # ------------------------------------------------------ the right rail
    rx = 112.0
    txt(rx, 73.0, "WHAT THESE ARE FOR", 9.4, INK, w="bold")
    yy = 68.6
    for lab, verdict, c in (
            ("the shape of the pulse", "yes. offset cancels", GRN),
            ("P1 minus P2", "yes. both drift together", GRN),
            ("is the piston working", "yes. a leak shows", GRN),
            ("absolute mean pressure", "NO. the manometer", RED)):
        txt(rx, yy, lab, 8.0, INK)
        txt(rx, yy - 3.0, verdict, 8.0, c, w="bold")
        yy -= 7.6

    yy = 36.0
    txt(rx, yy, "THE NUMBERS", 9.4, INK, w="bold")
    yy -= 4.6
    for lab, val in (("full scale", "%.0f mmHg" % n["fs_mmhg"]),
                     ("P1 peak", "70 mmHg"),
                     ("range used", "19%"),
                     ("sensor error", "+-%.0f mmHg" % (0.025 * n["fs_mmhg"])),
                     ("one ADC count", "%.2f mmHg" % n["lsb_mmhg"]),
                     ("filter", "%.0f Hz" % n["fc"]),
                     ("sample at", "250 Hz")):
        txt(rx, yy, lab, 7.8, "#555")
        txt(rx + 18.5, yy, val, 7.8, INK, ha="right", w="bold")
        yy -= 3.8

    txt(3, 7.6, "VBUS is live only on USB. If the Pico ever runs from VSYS the "
                "sensors go dark and read about 0 V,", 8.6, RED)
    txt(3, 4.6, "and 0 V is not zero pressure, it is %.2f V below it. "
                "pressure.check() is written to catch exactly that."
        % n["v0"], 8.6, RED)
    txt(3, 1.6, "flow/wiring.py  and  flow/pico/pressure.py", 7.4, "#888")

    fig.savefig(OUT, dpi=150, facecolor=PAPER)
    plt.close(fig)
    print("\nwrote %s" % OUT)


if __name__ == "__main__":
    report()
    draw()
