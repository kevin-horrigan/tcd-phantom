# Group 2, Phase 0: Low-Cost Doppler Bench Rig

**TCD phantom capstone** | Advisor: K. Horrigan | Draft 2026-09-11
Adapted from a high school build. The hardware is nearly the same. The purpose is not.

## What this is

A roughly $100 rig you can build in a weekend, running **during** your literature review rather than
after it. It is not a small version of your capstone device. It is the instrument you use to decide
what your capstone device should be.

By the end of it you will have measured, on your own bench, the three numbers that size your real
design: how much flow you need, how much pressure that costs, and what a peristaltic pump actually
does to a waveform. Those are requirements you can defend in a design review, rather than numbers
taken from a paper written for a different vessel.

Secondary benefit, and not a small one: your measurement chain will have worked once, in September.
The December gate stops being the first time anything is plugged in.

## What this rig decides

1. **Pump architecture.** You are going to build this with a hobby peristaltic pump. Characterize
   what it produces. Then decide, with data, whether that architecture belongs in the final device.
   I have an opinion. I am deliberately not giving it to you until you have the spectrogram.
2. **Flow and pressure requirements** for the real pump, derived from measured velocity in a known
   bore rather than estimated.
3. **Whether a compliance chamber is optional.** Build it, remove it, look at the difference.

## Parts

Same core as the high school build, with four additions and one subtraction.

| Item | Note |
|---|---|
| FD-200B pocket fetal Doppler (or similar) | ~$40. **Find its actual transmit frequency.** See below. |
| Peristaltic pump, 5-6 V DC (Adafruit #3910 or similar) | ~$25. This is the device under test, not just the drive. |
| Silicone tubing, 3.5 mm ID | Plus a short narrower segment for the test vessel |
| Arduino + motor driver (L293D or TIP120) | As the original build |
| **Syringe body, 20-60 mL, for the air chamber** | Moved into the build. Not optional. |
| **Gauge pressure sensor (MPX5050DP or similar)** | ~$15. You need P and v together. |
| **Digital kitchen scale, 1 g resolution** | Gravimetric flow ground truth |
| **USB audio interface or line input** | See the AGC warning below |
| Plastic container, reservoir, gel, clamps | As the original build |
| Whole milk as working fluid | Replaces cornstarch. See below. |
| ~~Audacity as the analysis tool~~ | Use Python. See below. |

## Build

Follow the original build with four changes.

**1. The air chamber goes in now.** Tee a vertical, partly air-filled syringe body into the line
downstream of the pump, open end up so buoyancy keeps the air where you put it. In the high school
version this was an optional final experiment. It is in the build here because without it the
waveform is dominated by roller ripple and there is very little to look at.

**2. Slant the vessel, not the probe.** Anchor the test-vessel section at a fixed angle in the bath,
30 to 45 degrees to the water surface, and rest the probe face flat on the surface or against the
container wall. Do not try to hold the probe at an angle. The Doppler angle becomes a measured,
fixed property of the build instead of something your hand is doing differently each time, and
every velocity number you compute depends on knowing it.

Measure that angle and write it down. A protractor photograph is fine.

**3. Narrow the test vessel.** Velocity, not flow rate, is what Doppler measures, and velocity is
flow over area. A narrower segment at the insonation point buys you signal for free. Halving
diameter quadruples velocity.

**4. Instrument the pressure.** Tee the sensor in near the test vessel. You need simultaneous
pressure and velocity to say anything about compliance later, and you need pressure to size the real
pump.

**Working fluid:** whole milk, or milk diluted in water. Cornstarch is a suspension and settles
within minutes, which will drift your signal mid-run and look exactly like a real effect. Milk is an
emulsion and stays put. If you want to compare scatterers, do it first, then use the winner for
everything else.

## Measurement chain, and three ways to get it wrong

**Ignore the BPM readout.** It is a black box with an undocumented beat detector, and your capstone
is not about a $40 device's firmware. Work from the raw audio out of the headphone jack.

**Find the probe's actual transmit frequency.** Specifications for these units say "2 to 3 MHz,"
which is not a number. Velocity scales inversely with it, so a unit that is actually 3 MHz read as
2 MHz gives you a 50% velocity error that is completely invisible in the data. Check the label, the
manual, the probe housing, or measure it. Do not proceed on "2 to 3."

**Disable automatic gain control.** Laptop microphone inputs usually apply AGC, which will flatten
exactly the amplitude variation you need for the angle experiment. Use a line input or a USB audio
interface, and turn off any "automatic" level option. Verify by recording a known-varying signal and
confirming the amplitude actually varies.

**Use the right speed of sound.** Your bath is water at roughly 1480 m/s, not tissue at 1540. Using
the tissue value introduces about a 4% error. It is small, but it is the same class of error the
materials team is spending their semester characterizing, so get it right on principle.

Velocity from the spectrogram:

```
v = c * f_doppler / (2 * f_0 * cos(theta))
```

Move the analysis to Python (`scipy.signal.spectrogram`). Audacity is fine for looking, but you
need to compute velocity traces, extract envelopes, and produce maps, and you will need that code
for the capstone anyway.

**Three different quantities, and never confuse them:**

| | What it is |
|---|---|
| **Commanded** | The Arduino BPM variable, or pump PWM setting |
| **Actual** | What the phantom really did, measured gravimetrically or counted from audio |
| **Measured** | What the Doppler reports |

Your calibration compares **measured** against **actual**. Never against **commanded**. If the pump
stalls or the tubing damps, commanded and actual diverge, and you will blame the instrument for the
phantom's error. This is the single most transferable idea in the exercise and it applies unchanged
to everything you build after it.

## Experiments

### E1. Velocity calibration against a gravimetric ground truth

Run at several pump settings. At each one, catch the outflow in a tared container for a timed
interval and weigh it. That gives you volumetric flow, and flow over the measured bore area gives
you true mean velocity.

Separately, compute velocity from the Doppler spectrogram.

Plot Doppler-derived velocity against gravimetric velocity. Report slope, intercept, and scatter.
This is your calibration, and it is the first honest thing the rig produces.

Expect the flow-derived value to be a mean over the cross-section while the spectrogram shows a
distribution up to a peak. Think about which number you are comparing to which, and say so in the
writeup. That distinction does not go away at the capstone scale.

### E2. Angle and the cosine law

Vary the insonation angle from roughly 30 to 90 degrees at constant pump setting. Extract the
Doppler frequency at each angle and fit against the predicted cosine dependence.

Report the fit and the residual. At 90 degrees you should measure essentially nothing, and
confirming that is worth doing because it is the failure mode most likely to waste a week later.

### E3. Roller ripple characterization

**This is the experiment that decides your architecture.**

Run the pump at several steady speeds with no cardiac modulation. In each spectrogram, find the
periodic ripple. Determine its frequency, and check it against what you would predict from motor
speed and roller count.

Then run with the cardiac modulation on, at a normal heart rate, and look at where the ripple sits
relative to the cardiac fundamental and the systolic upstroke.

Answer three questions in writing:

1. What is the ripple frequency, and does it track pump speed rather than commanded heart rate?
2. Does it overlap the frequency content of the systolic upstroke?
3. With the air chamber in and out, how much of it survives?

Then tell me whether a peristaltic pump belongs in the final device, and show me the figure that
makes the case. I will tell you what I think after you have told me what you think.

### E4. Compliance sweep, pilot version

Vary the air volume in the syringe chamber across its range. At each setting, record pressure and
the Doppler velocity envelope, and compute pulsatility index from the envelope.

Produce a plot of air volume against PI.

This is a small version of the map that is your actual capstone deliverable. Building it once at
$100 scale, with a pump you do not care about, is much cheaper than discovering the method problems
at full scale in March.

## Deriving your real requirements

Work this out from your own measurements rather than from mine, but here is the shape of it.

A hobby peristaltic at 6 V moves on the order of 100 mL/min. Through 3.5 mm bore, that is an area
near 9.6 mm², giving roughly 17 cm/s. At 2 MHz and a 50 degree angle in water, that is a Doppler
shift near 300 Hz, comfortably audible.

The middle cerebral artery is a different regime. A 3 mm lumen has an area near 7.1 mm², and 120
cm/s peak systolic through it requires on the order of 500 mL/min.

So the real device needs roughly **five times the flow through a smaller bore**, which also means
substantially more pressure. That ratio, computed from your own bench numbers, is your pump
requirement, and it is defensible in a way that a number copied from the Greaby paper is not.

Note also what does **not** need to scale. At 120 cm/s the Doppler shift is around 2 kHz, still
ordinary audio. Your measurement chain already reaches MCA velocities unchanged. The pump is the
only thing that has to grow. That tells you where the money goes.

## Safety and scope

The Doppler is used on the phantom only, never on a person. Two reasons, and the second is the one
that will actually affect you: pointing it at a human being makes this human subjects research and
brings IRB review into a project that currently needs none. Keep it on the bench.

Low voltage throughout. Keep electronics away from the water bath. Normal supervision for soldering.

## Deliverable

A short characterization memo, five pages or so, covering:

- Calibration result from E1 with slope, intercept, and scatter
- Cosine fit and residual from E2
- Roller ripple finding from E3, **with your architecture recommendation**
- Compliance versus PI map from E4
- Derived flow and pressure requirements for the real pump
- Your analysis code, in the repo

Due alongside the feature list and sketch you already proposed, so that the sketch is informed by
measurements rather than only by literature. This should run in parallel with the literature review,
not after it.
