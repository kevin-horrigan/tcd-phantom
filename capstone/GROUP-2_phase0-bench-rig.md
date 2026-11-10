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
| **Gauge pressure sensor, MPX5050GP** | ~$35. **Buy two** if the budget allows, one each side of the air chamber. See the appendix. |
| **Clear vertical tube, ~1.5 m, as a water-column manometer** | Pennies, and not a substitute for the above. Calibration standard, mean pressure, and pressure relief. |
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

**The slope is a result, not a nuisance, and you can predict it before you run.** In 3.5 mm tubing at
these speeds the Reynolds number is around 500 to 1000, comfortably laminar, so a fully developed
profile is parabolic and its centerline peak is exactly **twice** the cross-sectional mean. Your
probe is continuous-wave, with no range gate, so it reports the fastest thing in the beam, which for
a single tube lying entirely inside the beam is that centerline peak.

So: plot Doppler peak against gravimetric mean and **expect a slope near 2.0 and an intercept near
zero.** That prediction is the whole value of doing this experiment first, because each way of
missing it names its own cause:

| What you see | What it means |
|---|---|
| Slope near 2.0, intercept near 0 | Working. Laminar, developed, and your `f_0` and `c` are right. |
| Slope near 1.2 | Blunted, plug-like profile. Flow is not developed, so check for too short a straight run upstream of where you insonate. |
| Slope right but intercept well off zero | A systematic offset. Suspect AGC on the audio input, or a spectrogram noise floor being read as signal. |
| Slope off by roughly 1.5x | You have the transmit frequency wrong. This is why "2 to 3 MHz" is not an acceptable answer. |
| Scatter large and unstructured | Angle is moving between runs, or there is air in the loop. |

Write the prediction down **before** you take the data. A calibration that agrees with a number you
chose afterward has told you nothing.

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

Vary the air volume in the syringe chamber across its range. At each setting, record the Doppler
velocity envelope and compute pulsatility index from it, and record pressure at the same time.

Produce the air-volume against PI plot. Then do the thing that makes this transferable: compliance is
a ratio of volume change to pressure change, so use the pressure record to report **compliance in
mL/mmHg** at each setting, not just the syringe volume you dialed in. Syringe volume is specific to
this syringe. Compliance in real units is a specification you can hand to whoever builds the real
chamber.

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

---

## Appendix: pressure measurement

### What pressure buys you, and why two sensors beat one

The part is about **$35**, not the $15 an earlier version of this document claimed. Get it, and if
the budget stretches, **get two.**

Here is the honest accounting of what it adds. E1 and E2 do not need pressure at all: E1 calibrates
velocity gravimetrically and E2 is the cosine law. E3 and E4 work without it but are much weaker
without it, and one of them is arguably not measurable without it.

**E3 gets cleaner.** Roller ripple is a pressure phenomenon. It reaches the Doppler only after
passing through the loop and the whole audio chain, so the velocity trace is the attenuated, noisier
view of it. Measuring it in pressure measures it at the source.

**E4 needs it to produce a real number.** Compliance *is* a ratio of volume change to pressure
change. Mapping syringe air volume to pulsatility index, as the experiment is written, gives you a
useful curve that is specific to that one syringe and does not transfer to the real loop. Measure
pressure and you get compliance in mL/mmHg, which is a property you can design the real compliance
chamber against. That is the difference between a pilot result and a transferable one.

**Why two.** The single most informative measurement available on this rig is pressure on *both*
sides of the compliance chamber at once. That gives you the plenum's attenuation of the roller ripple
directly, as a ratio in one run, which is the central design question for this group. With one sensor
you have to move it and re-run, and then pump drift and setup changes are mixed into the comparison.
Two sensors turn the key question into a single measurement. The Nano has eight analog inputs, so
there is no cost beyond the part.

Buy the **MPX5050GP** rather than the `DP` if you are ordering: single-port gauge, vented internally,
and no exposed-die port to accidentally plumb fluid into. Electrically identical.

### Build the water column regardless

Not as a substitute. It does jobs the transducer does not.

A clear vertical tube teed into the loop costs almost nothing. 1 mmHg is 13.6 mm of water:

| Water column height | Pressure |
|---|---|
| 100 mm | 7.4 mmHg |
| 500 mm | 36.8 mmHg |
| 1.0 m | 73.6 mmHg |
| 1.22 m | 90 mmHg |

Three reasons it stays in the build. It is a **primary standard**, accurate to however well you read
a tape measure, so it is what you calibrate the transducer's offset and span against rather than
trusting a datasheet with 2.5% full-scale error. It reads **mean pressure** better than the
transducer does, for the same reason. And because an open vertical tube physically cannot exceed its
own height, it is the **pressure relief that protects a wall-less cast block** from a pump that can
otherwise deliver 20 psi into it.

What it will not give you is a waveform. The column is a damped resonator with its own natural
frequency, so do not read pulse pressure off how far the meniscus bounces. That is the transducer's
job, and it is why you want both.

### The trap at this price point

Searching for a cheap pressure sensor turns up $4 modules built around the **HX710B** (or HX710A).
Do not buy these for this application. They are 24-bit and well made, but they sample at **40 SPS**
(10 SPS for the A version). At 40 SPS a 1.2 Hz beat gets about four samples on the systolic upstroke,
the dicrotic notch smears away entirely, and anything above 20 Hz aliases. The roller ripple we care
about in E3 lands at 6 to 25 Hz, so the cheap module fails precisely the one experiment where
pressure would help most. Resolution is not the specification that matters here. Bandwidth is.

If the budget later argues against $35, the better cheap route is a surplus clinical arterial-line
transducer, which is purpose-built for liquid contact and has flat response far past cardiac
harmonics. It is a raw Wheatstone bridge at roughly 5 uV/V/mmHg, so it needs excitation and an
instrumentation amplifier (INA125 class) rather than connecting straight to an ADC. More build
effort, better instrument.

### Which part, and the one trap in it

The `DP` suffix means **dual port, differential**. You want gauge pressure, so leave the second port
(P2, the back side) open to room air and apply pressure only to P1. The trap: on the differential
parts, **only the P1 face has the protective gel die coat.** The P2 side is bare silicon. Get fluid
into P2 and the sensor is finished. If you are ordering rather than using one already in the lab,
the **MPX5050GP** is the better part: single port, vented internally, no wrong hole to plumb into.

Either way the electrical side below is identical.

### Pinout

Six-pin SIP, Case 867B. **Pin 1 is the one next to the notch in the side of the package.** Getting
this backwards puts 5 V into the output pin.

| Pin | Function | Connect to |
|---|---|---|
| 1 | Vout | sense line (see below) |
| 2 | GND | ground |
| 3 | Vs | +5 V |
| 4, 5, 6 | no connection | leave open |

### Circuit

Straight out of the datasheet's recommended configuration. Four passives, no amplifier.

```
  +5V ---+------------------- pin 3 (Vs)
         |
        1uF
         |
  GND ---+------------------- pin 2 (GND)

  pin 1 (Vout) ---[ 750R ]---+--- A0
                             |
                           0.01uF
                             |
                            GND
```

The 1 uF goes physically close to the sensor, not at the far end of the breadboard. The 750 ohm and
0.01 uF form a low-pass corner near 21 kHz, which is far above anything you care about and is there
to keep switching noise out of the ADC.

### Arduino, and why not the Pico

**Use the Arduino.** The sensor is a 5 V part with a ratiometric output, meaning its output is a
fixed *fraction* of its supply rather than a fixed voltage. Read it with an ADC referenced to that
same 5 V rail and the supply voltage cancels out of the arithmetic completely. You get that for free
on a 5 V board: sensor to A0, nothing in between.

A Pico's ADC tops out at 3.3 V and its pins are not 5 V tolerant, so a 4.7 V full-scale output would
damage it. You would need a divider on the output, and then the sensor runs off VBUS while the ADC
references 3.3 V, so the two no longer cancel. Every sag in USB bus voltage becomes a pressure
error. The Pico has the better ADC on paper and is the worse instrument here, and a Pico 2 does not
fix it, because this is a reference problem and not a converter problem.

**Do not use a Raspberry Pi.** It has no analog input at all, so you would be adding an external ADC
anyway, and Linux will jitter your sample timing. A Pi is the right machine for logging and plotting
the data, not for acquiring it.

### The arithmetic

The datasheet transfer function is `Vout = Vs * (0.018 * P + 0.04)` with P in kPa. Rearranged for a
10-bit `analogRead()` on the default 5 V reference, where `N` is the raw count:

```
P_kPa  = ((N / 1023.0) - 0.04) / 0.018
P_mmHg = 416.7 * ((N / 1023.0) - 0.04)
```

Sanity checks: at 0 kPa the output sits at 0.2 V, so `N` is about 41, not 0. Full scale is 4.7 V, so
`N` tops out near 962 and not 1023. If your zero reads 0 counts, something is miswired.

Resolution works out to about 0.4 mmHg per count, and `analogRead()` will give you several kHz if you
want it. Both are far better than you need for a waveform with a 1 to 3 Hz fundamental. Sample at
500 Hz or 1 kHz and you are done.

### What this sensor is actually good for

Read the accuracy spec carefully before you quote any absolute number. It is **2.5% of full scale**,
and full scale here is 375 mmHg, so the absolute error is about **9 mmHg**. Our target pulse pressure
is only 20 to 30 mmHg. Taken at face value that sounds disqualifying.

It is not, because most of that error is static offset and span, and the thing you are measuring is a
*shape*. Zero the sensor against room air at the start of every session and the offset drops out.
What remains is linearity and span error acting on a 25 mmHg swing, which is small. So treat this
sensor as a waveform and relative-change instrument, which is exactly what you need it for, and do
not report a mean pressure to three digits from it.

### One failure mode to recognize on sight

The sensor connects to the loop through a short stub of tubing, and that stub has to be **short,
stiff, and completely free of air.** An air bubble in the sense line makes a spring, which low-passes
the pressure signal. The result is a trace that still looks like a plausible pressure waveform but
with a soft upstroke and no dicrotic notch.

So: **if the notch disappears, suspect a bubble in the sensor line before you suspect the pump.**
Clinical arterial lines have exactly this problem and it fools experienced people regularly.
