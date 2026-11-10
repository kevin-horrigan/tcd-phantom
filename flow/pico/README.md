# Pico motor driver, laptop setup

Everything here runs on the laptop the Pico is plugged into. The repo is public, so none of it needs a login.

## 1. Get the code

```
git clone https://github.com/kevin-horrigan/tcd-phantom.git
cd tcd-phantom/flow
pip install pyserial
```

`pyserial` is the only dependency for talking to the board. The model and the checks want `numpy`, `trimesh` and `manifold3d` as well, but none of that is needed to drive a motor.

## 2. Get MicroPython onto the Pico

Skip this if the board already answers `python picolink.py info`.

A board with no firmware, or one held in BOOTSEL, shows up as a **USB drive** and not as a serial port. If `pico_install.py` says it cannot find a board, that is almost always what has happened.

1. Download the `.uf2` for the exact board from <https://micropython.org/download/>. This build is an **RP2350**, so the board is `RPI_PICO2` (or `RPI_PICO2_W` if it has wifi). An RP2040 build will not boot on it.
2. Hold BOOTSEL, plug the USB in, release. A drive called `RP2350` appears.
3. Copy the `.uf2` onto that drive. The board reboots by itself and the drive disappears.
4. `python picolink.py info` should now answer.

If the board appears as neither a drive nor a serial port, try another cable. A charge-only USB cable powers the Pico and carries no data, and it is the single most common cause of this.

## 3. Install the driver

```
python gen_pico_config.py      # writes pico/config.py from the model
python pico_install.py         # uploads it and drive.py, verifies, moves nothing
```

The install reads the constants back off the board after importing, so a pass means the firmware ran and agrees with the model, not just that two files copied.

`config.py` is **generated**. Do not edit it on the board or in the repo. Change `syringe_drive.py`, re-run the generator, re-upload. The point is that the bore area, the lead, the beat volume and the soft limit cannot drift away from the parts that were printed around them.

## 4. Before the motor turns

```
1.  motor DISCONNECTED, 12 V on, Pico USB on, meter against GND, set 0.53 V
2.  12 V off, connect the motor
3.  12 V on, THEN USB
```

**VREF needs VCC_IO, not just VM.** Measured on this board: with 12 V on and the Pico unplugged, the wiper reads 0 V, and one outer leg of the pot sits at about 3.3 V. The divider is fed from the logic supply, so there is nothing to read without it. That matters more than it sounds, because 0.00 V from a missing logic supply is indistinguishable from a pot wound fully down, and the obvious response to a reading of zero is to turn it *up*.

What makes this safe is the motor being disconnected, not the power being removed. An earlier version of this file said to measure with 12 V off; that was wrong.

**Direction, measured on this board: CW raises VREF, CCW lowers it.** An earlier version said the opposite, inherited from what is commonly said about these carriers and never measured here. Do not take a direction claim from a forum, a datasheet, or from this file. Find the end stop: a pot that reads 0.00 V and will not go lower is at minimum, and minimum is the harmless end to start from.

The pot is coarse, roughly 0.1 to 0.2 V per small nudge against a 0.67 V journey from the factory setting. Six iterations to land is normal. Meter after every adjustment and never count turns.

The TP hole is awkward to hold a probe in. The pot's middle leg is the same node and is easier to land on.

As set on 2026-11-10: **0.556 V**, measured on an MDO3024 at 0.1 V/div with a 1× probe, steady over five reads. That is 0.393 A rms, which gives 6.8× the torque the piston needs and a 6.8× phase-reversal margin. `syringe_drive.py` derives `SET_I` from this measured value rather than from the 0.53 V the design asked for.

Never unplug the motor while VM is live. The coil dumps its stored energy into the driver and kills it.

0.53 V is the datasheet floor, not a preference. The TMC2209 datasheet calls anything under 0.5 V "not recommended", and with the 0.11 Ω sense resistors on this board that floor is about 0.35 A. 0.53 V puts the phase current at 0.375 A, which is 21 percent of the 1.768 A full scale.

The board ships in **stealthChop**. That is quiet and it is not what this drive wants: the torque comes from spreadCycle. Switching modes means either the UART interface or desoldering a resistor, and it has not been done yet. StallGuard is not an option either way, because it only works in stealthChop, which is why there is no endstop on this machine and why the zero is declared by hand.

## 5. Drive it

```python
import drive
drive.selftest()            # 2 mm out and back, slowly. Watch the carriage.
drive.set_zero()            # declare where it is now. There is no endstop.
drive.goto_mm(10)
drive.beat()                # one beat
drive.run(hr=60, beats=30)
drive.off()                 # de-energise
```

Or from the laptop without opening a REPL:

```
python pico_install.py --test
python picolink.py eval "import drive; drive.run(hr=60, beats=20)"
```

### If the carriage runs the wrong way

`DIR_ADVANCE` in `config.py` is the one value the model cannot know, because it depends on how the coil pairs landed in the connector. Set it to `0`, re-run `gen_pico_config.py`, re-upload.

### If it buzzes and does not turn

The coil pairs are swapped. A stepper's two coils are A1/A2 and B1/B2; wiring them A1/B1 gives exactly this. Ring the pairs out with a multimeter: the two wires of one coil read a few ohms to each other and open to the other pair.

## 6. Wireless, on a Pico 2 W

### Firmware first

Wifi is a firmware question, not a software one. The `RPI_PICO2` build has no CYW43 driver, so `import network` raises ImportError and nothing in `net.py` can help. A non-W build runs perfectly well on W hardware, which is exactly why this presents as a software fault and is not one. This board shipped that way and was reflashed on 2026-11-10.

1. `RPI_PICO2_W` uf2 from <https://micropython.org/download/RPI_PICO2_W/>.
2. `python picolink.py --port COM6 eval "__import__('machine').bootloader()"` puts it in the bootloader without reaching for the BOOTSEL button. A drive called `RP2350` appears.
3. Copy the uf2 to that drive.

**Reflashing wipes the filesystem.** Back up anything on the board that is not in this repo first, with `python picolink.py get <name> <local>`. Then re-run `pico_install.py` and restore the rest.

Afterwards the board reports `_build='RPI_PICO2_W'` and `machine='Raspberry Pi Pico 2 W with RP2350'`.

### Credentials

```
copy pico\secrets_example.py pico\secrets.py     # then edit it
python pico_install.py --port COM6
```

`secrets.py` is gitignored. **This repo is public.** The template is committed; the real file never is.

The CYW43 is **2.4 GHz only**. A 5 GHz network never appears in a scan, which looks exactly like a wrong password.

### Run it

```
python picolink.py --port COM6 eval "__import__('net').serve()"
```

It prints a URL. Open it on anything on the same network: there is a control page with bpm, beat count, run, stop, set zero and de-energise, and a plain-text `/status`.

### What the network layer does and does not do

It **commands, it does not stream**. You ask for thirty beats and the Pico plays thirty beats. Nothing sends a waveform over wifi slice by slice, and the socket is polled between beats and never during one.

That is not an optimisation. A beat is 160 slices and at 60 bpm each slice is 6.25 ms, which is the window Python has to hand PIO the next burst. Servicing the CYW43 eats into exactly that window. Be clear about what the damage would be: PIO holds an exact pulse count and emits it whatever else the chip is doing, so jitter **cannot** put the piston in the wrong place. What it distorts is **when** those pulses arrive, which is the shape of the beat, and the shape is the entire product of this machine. `/status` reports `drive.late_us`, the worst slice lateness, so the cost is measured rather than assumed.

The price is that **stop takes effect at the end of the current beat**, up to one beat of latency. That is the right trade. A stop that lands a beat late is an annoyance; a beat whose upstroke is 8 ms late is a bad experiment that still looks like a good one.

**There is no authentication.** Anyone on the network can move this motor. That is fine on a lab bench and nowhere else. Do not port-forward it, and do not leave it serving with a syringe fitted and nobody in the room.

## What the driver guarantees

**Position is exact.** Every pulse train is generated by PIO with an exact count per burst, never by a Python loop. A dropped step is not a glitch here, it is 0.6 µL of stroke volume that never happened, and nothing downstream would show it.

**It will not pull the plunger out.** The frame allows 45 mm of travel. The 5 mL barrel allows 34.7 mm, and retracting past that drags the seal out of the open end. The frame will drive straight through that point; the firmware refuses to.

**A beat nets to zero travel.** The piston adds the pulse and the gravity head sets the mean, so the plunger has to come back to where it started every cycle. `beat()` measures its own drift and corrects it rather than assuming the arithmetic closed.

**The profile is the same one the viewer animates.** `config.BEAT` is generated by `assembly.beat()`, so the 3-D build page and the hardware play the same 160-sample displacement curve. It is displacement, not velocity.
