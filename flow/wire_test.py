# -*- coding: utf-8 -*-
"""Thirty seconds that prove the wiring, before the speed ladder.

Low rungs only. At 60 to 120 rpm the motor is energised for a few seconds at a
time, so this is safe at any Vref including the factory 0.9 A, which is the
whole point: run it before touching the pot. It answers the three questions
that matter first and are independent of the motor.

    does it turn at all      -> STEP reaching the driver, coils paired right
    does it reverse          -> DIR reaching the driver
    does the mark come back  -> no steps lost, so the PIO train is honest

A coil split across A and B buzzes and does not turn. That is the failure to
look for, and it looks nothing like a stall.
"""
import time
import step_test as st


def main():
    print("4 revs out, 4 revs back, twice. watch the mark.")
    st.sm.active(1)
    st.en.value(0)
    try:
        for rpm in (60, 120):
            print("  %4d rpm ..." % rpm, end="")
            st.out_and_back(rpm)
            print(" done")
            time.sleep(1.0)
    finally:
        st.en.value(1)
        st.sm.active(0)
    print("mark back where it started, both times? then the wiring is good.")


if __name__ == "__main__":
    main()
