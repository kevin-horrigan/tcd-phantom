# -*- coding: utf-8 -*-
"""Read P1 and P2 on the Pico. Runs ON the Pico, next to drive.py.

    import pressure
    pressure.read()        -> (p1_kpa, p2_kpa)
    pressure.mmhg()        -> (p1_mmhg, p2_mmhg)
    pressure.check()       -> says whether each sensor is actually alive
    pressure.zero()        -> store the reading at atmosphere as the offset
    pressure.trace(secs)   -> sample both at SAMPLE_HZ and return the arrays

THE TRAP, and it will destroy a Pico: the MPX5050GP needs 4.75 to 5.25 V and
puts out up to 4.70 V at full scale. The Pico's ADC is 3.3 V. Wiring the
output straight to GP26 puts 4.7 V into a 3.3 V pin.

So every output goes through a 10k / 20k divider, which is what DIV below
is, and the firmware multiplies it back out. If someone fits the sensor
without the divider the readings will look plausible and low while the ADC
pin is being overdriven, which is the worst kind of wrong.

WIRING, per sensor:

    sensor pin 1  Vout ----[ 10k ]----+----> Pico GP26 (P1) or GP27 (P2)
                                      |
                                    [ 20k ]
                                      |
                       0.40-0.47 uF --+--- Pico GND
                                      |
                                     GND

    sensor pin 2  GND  -------------------> Pico GND
    sensor pin 3  Vs   -------------------> Pico VBUS (pin 40), 5 V
                       1 uF from pin 3 to GND, at the sensor

    Pins 4, 5 and 6 are internal connections. Leave them open: the
    datasheet says do not connect them to external circuitry OR to ground.

PIN 1 IS THE ONE BY THE NOTCH IN THE LEAD, not a notch in the side of the
package. The datasheet's wording is "pin 1 is noted by the notch in the
lead", and the distinction is not pedantry: the package has moulding
features of its own, and an NXP forum thread exists of somebody asking
whether the notched pin might be pin 6. Look at the metal legs, find the one
with the bite taken out of it, and that is pin 1. Check it against the part
before applying power, because backwards puts 5 V into the output pin and
the sensor is gone. This is recorded in GROUP-2_phase0-bench-rig.md too.

The cap across the 20k is not decoration. It is the anti-alias filter for a
250 Hz sample rate, whose Nyquist is 125 Hz, and the sensor itself answers
in 1 ms, so without it everything up to a kilohertz folds straight into the
band we care about. Against the divider's 6.7k source:

    0.47 uF film    51 Hz   the specified part
    0.40 uF         60 Hz   4 x 100 nF ceramic in parallel, which is what
                            Kevin's MOGAOPI kit can make. Fine. Still half
                            of Nyquist and the pulse lives below 20 Hz
    0.10 uF        239 Hz   NOT acceptable. A single 100 nF sits ABOVE
                            Nyquist, so it filters nothing that matters and
                            aliasing is unchanged
    0.47 uF elec    51 Hz   fallback only, + to the ADC node. An
                            electrolyte's leakage runs through 6.7k as a DC
                            offset: 1 uA is 6.7 mV, which is 8 ADC counts or
                            0.7 mmHg, and it drifts with temperature. Small
                            against the sensor's own 9.4 mmHg, but it is an
                            offset on the absolute reading, so prefer the
                            four ceramics
"""
from machine import ADC, Pin
import time

P1_PIN, P2_PIN = 26, 27           # ADC0 and ADC1. GP2/3/4 are the stepper
VS = 5.0                          # sensor supply, from VBUS
ADC_REF = 3.3                     # the Pico's own reference
DIV = 20.0 / (10.0 + 20.0)        # the divider, 10k over 20k

# MPX5050 transfer function, from the datasheet:
#     Vout = VS * (0.018 * P + 0.04)      P in kPa
# so 0 kPa is 0.20 V and 50 kPa is 4.70 V on a 5.0 V supply.
SENS = 0.018
OFFSET = 0.04
MMHG_PER_KPA = 1000.0 / 133.322

SAMPLE_HZ = 250
DEAD_V = 0.08                     # below this the sensor is not powered

_adc = {}
_zero = {P1_PIN: 0.0, P2_PIN: 0.0}


def _ch(pin):
    if pin not in _adc:
        _adc[pin] = ADC(Pin(pin))
    return _adc[pin]


def volts(pin, n=16):
    """Sensor output volts, with the divider already undone."""
    tot = 0
    for _ in range(n):
        tot += _ch(pin).read_u16()
    return (tot / n) / 65535.0 * ADC_REF / DIV


def kpa(pin):
    return (volts(pin) / VS - OFFSET) / SENS - _zero[pin]


def read():
    return kpa(P1_PIN), kpa(P2_PIN)


def mmhg():
    a, b = read()
    return a * MMHG_PER_KPA, b * MMHG_PER_KPA


def check():
    """Is each sensor actually alive. Prints rather than returns, because
    this is the thing you run when a number looks wrong.

    An unpowered or unplugged sensor reads near 0 V, and 0 V is NOT zero
    pressure: zero pressure is 0.20 V. That gap is the whole diagnostic, and
    without it a dead sensor reports a believable negative pressure forever.
    """
    ok = True
    for name, pin in (("P1", P1_PIN), ("P2", P2_PIN)):
        v = volts(pin)
        if v < DEAD_V:
            print("%s: %.3f V. NOT POWERED or not connected. Zero pressure "
                  "would be %.2f V. Check VBUS and the notched LEAD."
                  % (name, v, VS * OFFSET))
            ok = False
        elif v > VS * (SENS * 50.0 + OFFSET) + 0.2:
            print("%s: %.3f V, above full scale. Either the divider is "
                  "missing or the port is blocked." % (name, v))
            ok = False
        else:
            print("%s: %.3f V = %.2f kPa = %.1f mmHg"
                  % (name, v, kpa(pin), kpa(pin) * MMHG_PER_KPA))
    return ok


def zero():
    """Call with the loop open to atmosphere and the piston stopped.

    This removes the sensor's offset error, which is +-2.5 percent of full
    scale, or about 9 mmHg. It does NOT give you absolute accuracy: for that
    the manometer is the reference, because a ruler against a column of the
    loop's own fluid has no calibration to drift.
    """
    for pin in (P1_PIN, P2_PIN):
        _zero[pin] = 0.0
        _zero[pin] = kpa(pin)
    print("zeroed: P1 %.3f kPa, P2 %.3f kPa removed"
          % (_zero[P1_PIN], _zero[P2_PIN]))


def trace(secs=3.0, hz=SAMPLE_HZ):
    """Sample both at a fixed rate. Returns (t_ms, p1_kpa, p2_kpa)."""
    n = int(secs * hz)
    step = int(1_000_000 // hz)
    t, a, b = [], [], []
    t0 = time.ticks_us()
    nxt = t0
    for _ in range(n):
        while time.ticks_diff(time.ticks_us(), nxt) < 0:
            pass
        t.append(time.ticks_diff(time.ticks_us(), t0) // 1000)
        a.append(kpa(P1_PIN))
        b.append(kpa(P2_PIN))
        nxt = time.ticks_add(nxt, step)
    return t, a, b
