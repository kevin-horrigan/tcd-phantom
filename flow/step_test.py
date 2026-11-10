# -*- coding: utf-8 -*-
"""Bench test: can the motor hold the speed the piston needs?

Run this on the PANCAKE, 17HE08-1004S (42 x 42 x 23 mm, 17 Ncm, 1.0 A, 3.6 ohm,
4.0 mH). The other motor bought, 17HS19-2004S1 (48 mm, 59 Ncm), is the WRONG
one here: its back-EMF constant is 1.7x higher. At the old 446 rpm target it
generated 9.7 V against a 12 V supply, with a ceiling of 549 rpm. The stronger
motor is the slower one. At the current 230 rpm target it would work, but the
pancake has more margin and weighs half as much.

Target comes from the phantom design, not from the motor:
    5 mL syringe, 12.06 mm bore         -> 4.38 mm stroke for 0.5 mL/beat
    T8x8 lead screw, 8 mm per rev       -> 0.55 rev per stroke
    70% of stroke in a 100 ms upstroke  -> 230 rpm peak, 767 full steps/s
    at 1/8 microstep                    -> 6132 steps/s

The syringe was 3 mL until 2026-11-09, which put the target at 446 rpm and is
where every motor difficulty in this build came from. Speed falls as the
square of the bore, so one size up halved it and bought back a great deal of
margin. The ladder below still runs past 230 on purpose: knowing where the
motor actually gives up is worth more than confirming it clears the target.

Mark the shaft with a paint pen first. The test is self-checking: at each
speed it commands a whole number of revolutions out and the same number back,
so if no steps were lost the mark returns to where it started. A mark that
drifts means steps were lost, and the speed it starts drifting at is the
answer we are looking for.

    python step_test.py        ladder, 30 rpm up to 560, stops where it fails
    LADDER = False             single run straight at TARGET_RPM

Verified on the hardware we have: Raspberry Pi Pico 2 (RP2350), MicroPython
1.29.0, CPU 150 MHz. The 1 MHz state machine clock is an exact 150:1 divide,
and the pulse train was measured on the board at 0.03% of the commanded period
at 120, 450 and 560 rpm, which also confirms the 6 cycle per step overhead
assumed below. The Pico side of this is therefore not in question. What is
still untested is the driver and the motor.

Run the ladder first on whatever motor is to hand, including the old unmarked
one. At low speed it proves the wiring, the driver and the PIO train, which is
most of what can be wrong. Do not read a high-speed FAILURE on the old motor as
a verdict: its inductance and torque constant are unknown, so a stall there
tells us about that motor and nothing about the design. A high-speed PASS on
any motor does prove the electronics.

Wiring, Pico -> BIGTREETECH TMC2209 V1.3  (pin names from the BTT manual)
    GP2        -> STEP   (J1-7)
    GP3        -> DIR    (J1-8)
    GP4        -> EN     (J1-1)   active LOW, 20k pull-up on board = off when floating
    GP5        <- DIAG   (top edge, optional, StallGuard)
    3V3(OUT)   -> VCC_IO (J2-7)   logic rail, board accepts 3-5 V
    GND        -> GND    (J2-8)
    12 V brick -> VM / GND (J2-1, J2-2) with 100 uF at the terminals
    motor      -> A1 A2 B1 B2 (J2-4, J2-3, J2-5, J2-6)

MS1 and MS2: leave both unconnected for 1/8 microstep.

Set Vref BEFORE powering the motor. Verified from the BTT manual:
    I_rms = 325mV / (R_sense + 20mohm) * (1/sqrt2) * (Vref / 2.5V)
    R_sense on this board is 0.11 ohm (schematic R2/R4 = 0R11), so
    I_rms = 0.707 * Vref      ->   Vref = 1.414 * I_rms
BTT's manual states the factory setting directly: Vref 1.2 V = 0.9 A.

    SET VREF TO 0.53 V.   That is 0.375 A rms.

Do not skip it. At the factory 0.9 A the phase cannot reverse inside the
2.61 ms a 230 rpm beat allows, and the motor stalls at speed for a reason that
has nothing to do with the motor. The potentiometer is BACKWARD from an
A4988: clockwise REDUCES current.

0.375 A rather than a rounder number because the setting is pinned from both
sides. Above about 0.45 A the reversal budget runs out. Below 0.37 A the pot
runs out: the TMC2209 datasheet (chapter 9, Motor Current Control) gives the
VREF scale as 2.5 V = 100% and 0.5 V = 20%, and says plainly "<0.5V: not
recommended". With the 0.11 ohm sense resistors on this board, 100% is
1.77 A rms, so the 0.5 V floor is 0.35 A and there is no legal way to ask the
pot for less. 0.53 V sits just above that floor and leaves a 2.3x reversal
margin with 6.5x the torque the piston needs.

An earlier version of this file said 0.40 V, which is below the datasheet
floor. If the pot is already there, bring it up.

Do NOT wire by color. The two motors use different conventions:
    17HE08-1004S  A+ black, A- BLUE,  B+ GREEN, B- red
    17HS19-2004S1 A+ black, A- GREEN, B+ RED,   B- blue
and the old unmarked motor follows neither, since nobody knows what it is.
Meter instead. The two leads that read a few ohms to each other are one coil
(3.6 ohm on the pancake, 1.4 ohm on the 48 mm, unknown on the old one, which
is itself worth writing down). The other two read open to that pair. Put one
coil on A1/A2 and the other on B1/B2. A coil split across A and B buzzes and
does not turn, which is the single most common bring-up failure.

Order of operations, every time:
    1. motor disconnected, 12 V on, meter on the VREF pin against GND
       (VREF is brought out on the board's top edge next to DIAG and INDEX,
       so there is no need to probe the pot itself)
    2. 12 V off, connect the motor
    3. 12 V on, THEN USB
Never unplug the motor while VM is live. The coil dumps its energy into the
driver and kills it.
"""
import time
import rp2
from machine import Pin

# ----------------------------------------------------------------- config
STEP_PIN, DIR_PIN, EN_PIN = 2, 3, 4
MICROSTEP = 8
STEPS_PER_REV = 200 * MICROSTEP      # 1600
SM_CLOCK = 1_000_000                 # 1 us per PIO cycle
LOOP_OVERHEAD = 5                    # PIO cycles outside the delay loop

TARGET_RPM = 230.0                   # what the piston actually needs
RAMP_MS = 800                        # steppers stall if started at speed
HOLD_S = 3.0

LADDER = True                        # False -> one run straight at TARGET_RPM
RUNGS = (30, 60, 120, 240, 360, 450, 560)
REVS = 4                             # whole revs out and back on each rung


# -------------------------------------------------------------- step train
@rp2.asm_pio(set_init=rp2.PIO.OUT_LOW)
def step_gen():
    """One STEP pulse per loop. Period comes from the TX FIFO.

    pull(noblock) on an empty FIFO copies X into OSR, so the last commanded
    period simply repeats. That lets Python update the rate every few ms
    while the pulse train itself stays hardware-timed.
    """
    pull(noblock)
    mov(x, osr)
    set(pins, 1)[1]          # STEP high, 2 us
    set(pins, 0)
    label("hold")
    jmp(x_dec, "hold")


@rp2.asm_pio(set_init=rp2.PIO.OUT_LOW)
def step_n():
    """Exactly N pulses at a fixed period. Two words per burst: N-1, then the
    delay count. PIO owns the counting, so a late or early sleep in Python
    cannot add or drop a step. That is what makes the mark test mean anything.
    """
    pull(block)              # how many, minus one
    mov(y, osr)
    pull(block)              # period, stays in OSR for the whole burst
    label("step")
    mov(x, osr)
    set(pins, 1)[1]          # STEP high, 2 us
    set(pins, 0)
    label("hold")
    jmp(x_dec, "hold")
    jmp(y_dec, "step")


def period_counts(steps_per_sec, overhead=LOOP_OVERHEAD):
    """PIO delay-loop count for a given step rate."""
    if steps_per_sec <= 0:
        return 0xFFFFFFFF
    n = int(round(SM_CLOCK / steps_per_sec)) - overhead
    return max(0, n)


def rpm_to_sps(rpm):
    return rpm * STEPS_PER_REV / 60.0


# ------------------------------------------------------------------- drive
N_OVERHEAD = 6                               # cycles per step in step_n
START_SPS = rpm_to_sps(30.0)                 # no stepper starts at speed
RAMP_STEPS = 800                             # half a rev of ramp at each end
RAMP_BURSTS = 20

en = Pin(EN_PIN, Pin.OUT, value=1)           # start disabled
dr = Pin(DIR_PIN, Pin.OUT, value=0)
sm = rp2.StateMachine(0, step_n, freq=SM_CLOCK, set_base=Pin(STEP_PIN))


def plan(total_steps, top_sps):
    """Bursts of (steps, steps_per_sec) adding to exactly total_steps."""
    if top_sps <= START_SPS:
        return [(total_steps, top_sps)]
    each = RAMP_STEPS // RAMP_BURSTS
    up, down = [], []
    for i in range(RAMP_BURSTS):
        f = START_SPS + (top_sps - START_SPS) * (i + 1) / RAMP_BURSTS
        up.append((each, f))
        down.insert(0, (each, f))
    hold = total_steps - 2 * each * RAMP_BURSTS
    if hold <= 0:                            # too few steps to ramp, just go
        return [(total_steps, START_SPS)]
    return up + [(hold, top_sps)] + down


def run(bursts, direction):
    dr.value(direction)
    time.sleep_ms(5)                          # DIR setup before the next edge
    secs = sum(s / f for s, f in bursts)
    t0 = time.ticks_ms()
    for steps, sps in bursts:
        sm.put(steps - 1)                     # put() blocks on a full FIFO,
        sm.put(period_counts(sps, N_OVERHEAD))   # so a long plan self-paces
    # The FIFO holds two bursts, so the last ones are still running when the
    # loop ends. Wait out the real remainder before DIR is allowed to move.
    left = int(secs * 1000) - time.ticks_diff(time.ticks_ms(), t0)
    if left > 0:
        time.sleep_ms(left)
    time.sleep_ms(200)
    return secs


def out_and_back(rpm):
    steps = REVS * STEPS_PER_REV
    bursts = plan(steps, rpm_to_sps(rpm))
    assert sum(b[0] for b in bursts) == steps
    t = run(bursts, 0)
    time.sleep(0.3)
    run(bursts, 1)
    return t


def main():
    print("%d revs out and back at each speed, 1/%d microstep." % (REVS, MICROSTEP))
    print("mark the shaft. the mark must come back to the same place.")
    sm.active(1)
    en.value(0)                               # active low: driver on
    try:
        for rpm in (RUNGS if LADDER else (TARGET_RPM,)):
            sps = rpm_to_sps(rpm)
            print("  %4.0f rpm  %6.0f steps/s  period %3d us  %.1f s each way"
                  % (rpm, sps, period_counts(sps, N_OVERHEAD) + N_OVERHEAD,
                     out_and_back(rpm)))
            time.sleep(1.0)
    finally:
        en.value(1)
        sm.active(0)
        print("done. the highest rung where the mark still returns is the answer.")


if __name__ == "__main__":
    main()
