# -*- coding: utf-8 -*-
"""Characterize an unknown motor by finding the speed it gives up at.

The old motor's nameplate is gone, so its torque constant and inductance are
unknown and a high-speed failure on it would be uninterpretable. One
measurement fixes that. The speed at which an unloaded stepper stops following
is set almost entirely by how fast the driver can reverse a phase against the
motor's own back-EMF, and back-EMF is the torque constant times speed. So the
ceiling, measured, inverts to the torque constant. Run the sweep, write down
the rpm where it breaks up, and feed it to motor_id.py on the laptop.

    TEST = "sweep"   accelerate continuously and announce the speed. The one
                     to run first. A stepper losing sync is unmistakable: the
                     tone goes ragged and the shaft stops while the tone
                     continues. Note the number printed just before that.
    TEST = "hold"    ramp gently to HOLD_RPM and sit there. Separates "cannot
                     accelerate that fast" from "cannot sustain it", which are
                     different faults with different fixes.
    TEST = "creep"   5 rpm for 20 s. Checks the low end for cogging and for
                     microsteps going missing, which looks like a shaft that
                     advances in visible jerks instead of gliding.

Needs no shaft mark. The mark test in step_test.py measures lost steps, which
is a finer question. This one measures where the motor quits, which is coarser
and is the number we are missing.

Wiring and Vref are as step_test.py documents them. This file imports it, so
the pins and the state machine are configured in exactly one place.
"""
import time
import step_test as st

TEST = "sweep"

SWEEP_LO, SWEEP_HI = 30.0, 800.0     # rpm, piston needs 230
SWEEP_S = 25.0                       # seconds for the climb
BURST = 200                          # steps per burst, 9 to 70 ms of work
ANNOUNCE = 50.0                      # print every this many rpm

HOLD_RPM = 450.0
HOLD_S = 5.0

CREEP_RPM = 5.0
CREEP_S = 20.0


def sweep(lo, hi, seconds, down=True):
    """Climb from lo to hi over `seconds`, announcing as it goes.

    Rate is advanced per burst rather than per step, so the climb is a
    staircase of BURST-step treads. At 200 steps a tread that is under 1 rpm
    of jump at the top, which no motor can tell from a smooth ramp.
    """
    # steps needed: integral of rate dt, with rate linear in t
    mean_sps = st.rpm_to_sps((lo + hi) / 2.0)
    total = int(mean_sps * seconds)
    treads = max(1, total // BURST)
    next_say = lo
    for i in range(treads):
        rpm = lo + (hi - lo) * i / float(treads - 1 if treads > 1 else 1)
        st.sm.put(BURST - 1)
        st.sm.put(st.period_counts(st.rpm_to_sps(rpm), st.N_OVERHEAD))
        if rpm >= next_say:
            print("    %5.0f rpm" % rpm)
            next_say += ANNOUNCE
    if down:
        print("    coming back down")
        for i in range(treads):
            rpm = hi - (hi - lo) * i / float(treads - 1 if treads > 1 else 1)
            st.sm.put(BURST - 1)
            st.sm.put(st.period_counts(st.rpm_to_sps(rpm), st.N_OVERHEAD))
    time.sleep(1.0)                   # let the FIFO drain before EN goes high
    return treads * BURST


def flat(rpm, seconds):
    """Gentle ramp in, hold, gentle ramp out. Whole thing is step-exact."""
    sps = st.rpm_to_sps(rpm)
    ramp = st.plan(int(sps * 0.8), sps)          # 0.8 s worth of accel
    for steps, f in ramp:
        st.sm.put(steps - 1)
        st.sm.put(st.period_counts(f, st.N_OVERHEAD))
    held = int(sps * seconds)
    for i in range(0, held, 2000):               # chunked so prints get through
        n = min(2000, held - i)
        st.sm.put(n - 1)
        st.sm.put(st.period_counts(sps, st.N_OVERHEAD))
    time.sleep(1.0)
    return held


def main():
    print("test: %s" % TEST)
    st.sm.active(1)
    st.en.value(0)
    try:
        if TEST == "sweep":
            print("  %.0f to %.0f rpm over %.0f s, then back down."
                  % (SWEEP_LO, SWEEP_HI, SWEEP_S))
            print("  LISTEN. note the last number printed before the shaft")
            print("  stops while the tone keeps going. that is the ceiling.")
            n = sweep(SWEEP_LO, SWEEP_HI, SWEEP_S)
            print("  %d steps commanded, %.1f revs" % (n, n / st.STEPS_PER_REV))
        elif TEST == "hold":
            print("  ramp to %.0f rpm and hold %.0f s" % (HOLD_RPM, HOLD_S))
            n = flat(HOLD_RPM, HOLD_S)
            print("  %d steps at speed, %.1f revs" % (n, n / st.STEPS_PER_REV))
        elif TEST == "creep":
            print("  %.0f rpm for %.0f s. watch for jerk, not for noise."
                  % (CREEP_RPM, CREEP_S))
            n = flat(CREEP_RPM, CREEP_S)
            print("  %d steps, %.2f revs" % (n, n / st.STEPS_PER_REV))
        else:
            print("  unknown TEST")
    finally:
        st.en.value(1)
        st.sm.active(0)
        print("done, driver disabled.")


if __name__ == "__main__":
    main()
