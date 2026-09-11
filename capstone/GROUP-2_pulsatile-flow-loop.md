# Group 2: Pulsatile Flow Loop

**TCD phantom capstone, Group 2 of 2** | Advisor: K. Horrigan | Draft 2026-09-10

## Objective

Build and characterize a pulsatile flow loop that delivers a physiologic middle cerebral artery
velocity waveform through the phantom head built by Group 1. The deliverable is not "a pump." It is
a **measured map** from the loop's compliance and resistance settings to the resulting pulsatility
index and peak systolic velocity, with the waveform instrumented and independently verified.

## Primary references

- Greaby, Zderic, Vaezy 2007, *Ultrasound Med Biol* 33:1269. Pulsatile flow phantom. This is the
  architecture to work from, and it is in-house at GW.
- Greaby 2005, MS thesis, Bioengineering, University of Washington. Fuller build documentation.
  Worth obtaining.
- Ramnarine et al. 1998, blood-mimicking fluid validation. IEC 61685 for the standard formulation.
- Mock circulatory loop and heart valve test literature, including ISO 5840 practice. This community
  has solved these design problems already.

## Architecture

Positive-displacement piston as the ventricle, into a compliance chamber, into an adjustable
resistance, returning to a reservoir. Check valves on either side of the piston close the loop.

This is Greaby's topology and it is also a two or three element Windkessel implemented in hardware.
That is the point. Pulsatility is not commanded, it **emerges** from the compliance and resistance
values, which is the same class of mechanism that produces it in a patient. The loop's R and C are
measurable and map onto the corresponding terms in the advisor's lumped-parameter model, which makes
the phantom a test of that model layer and not only of the transducer.

Greaby's two knobs, and what each controls:

- **Compliance:** air volume trapped above the fluid in a vertical plenum. They used a 25 mL
  serologic pipette capped with a stopcock. Their characterization: no air gives short high spikes,
  6 mL gives an underdamped waveform with ringing, 20 mL resembles an arterial signal.
- **Resistance:** a constriction downstream, before return to the reservoir. Theirs was 1.6 mm ID.
  Sets diastolic pressure.

Demonstrated envelope: 50 to 500 mL/min, 62 to 138 bpm, peak pressure 100 to 250 mmHg, systolic
velocity adjustable from 10 to 240 cm/s. That covers the MCA regime, though at 3 mm lumen you sit
near the top of the flow range at peak systole rather than comfortably in the middle.

## Do not use a peristaltic pump

A peristaltic superimposes roller ripple at the roller-pass frequency, unrelated to the cardiac
frequency. Three rollers at 400 RPM is 20 Hz against a cardiac fundamental near 1.2 Hz, and 20 Hz
sits inside the band that carries the systolic upstroke. The sharp systolic upstroke is the feature
the advisor most needs this phantom to reproduce faithfully, so a pump whose artifact lives in that
same band makes model error and pump artifact indistinguishable.

Second problem: to make a cardiac waveform with a peristaltic you modulate motor speed, and rotor
inertia plus tubing viscoelasticity limit slew rate. Sharp systole is what it is worst at.
Peristaltics are good at smooth constant flow, which is why Soloukey used one and Greaby did not.

## Pump options, in order of preference

1. **Servo or stepper driven piston.** Programmable, sharp upstroke achievable, and a genuine
   mechatronics deliverable: mechanical design, driver selection, closed-loop position control.
2. **Cam-driven piston.** A DC motor turns a profiled cam, waveform shape machined into the cam,
   heart rate set by RPM. Mechanically simple, extremely repeatable, no control loop. Since cams are
   trivial to 3D print, produce a *family* of them: normal, high-PI, tachycardic. A printed cam is
   an archivable, reproducible waveform standard, which is arguably a better artifact than a servo.
3. **Commodity solenoid metering pump**, as Greaby used. Crude output, fixed by the plenum.

## Target the MCA, not the carotid

Greaby was matching a carotid, and their comparison figure is a carotid pressure and velocity trace.
That is the wrong target here. Cerebral circulation sits behind much lower downstream resistance
than a peripheral bed, so diastolic velocity stays high and the waveform is far less pulsatile.

Practical consequence: **set the constriction considerably less restrictive than a peripheral match
would call for**, in order to hold diastolic velocity up. Chasing the carotid figure in the paper
will produce a waveform that is far too pulsatile.

State the acceptance target as a pulsatility index band, not a pressure. Use the advisor's PI banding
rather than a textbook range. `PI band target: [confirm with advisor]`

## Blood-mimicking fluid

Use a properly specified BMF, either the CIRS 769DF that Soloukey used or an IEC 61685 formulation.
Not a home mixture that only targets particle content.

Viscosity is not a detail. It sets the velocity profile, the profile sets the spectral shape, and
spectral shape is what the phantom exists to reproduce. A 3 mm vessel at normal heart rate with
correctly matched fluid gives a Womersley number near 2, which is the right regime for MCA. Wrong
viscosity can hit the right peak velocity while producing an unphysiologic profile, which looks like
success on a single number and is a failure on the thing that matters.

## Deliverables

1. **Instrumented loop.** Pressure transducer in-line. Without it, tuning is blind.
2. **Independent flow ground truth.** Timed collection and weighing at the outflow is the cheap,
   honest version and requires no purchase. Do not validate velocity with the same Doppler system
   under test.
3. **Compliance and resistance sweep.** The core result. A measured map from plenum air volume and
   constriction setting to PI and peak systolic velocity.
4. **Pump**, per the options above.
5. **Bubble control procedure.** Air in the loop is catastrophic for Doppler, since bubbles are
   enormous scatterers, and it silently changes system compliance. Note the plenum deliberately
   holds air above a fluid interface, so orientation matters. Greaby's was a vertical pipette with
   the stopcock on top, letting buoyancy keep the air where it belongs. A horizontal build entrains.

## Acceptance criteria

| # | Criterion |
|---|---|
| 1 | Stable pulse at commanded rate across 60 to 140 bpm, pressure instrumented |
| 2 | Peak systolic velocity reaches MCA range in the agreed lumen diameter |
| 3 | PI lands in the advisor's target band, and the setting that achieves it is recorded |
| 4 | Commanded versus measured flow agreement, in stated units with an error bound, against the independent ground truth |
| 5 | Compliance and resistance sweep map delivered, with repeatability across sessions |
| 6 | Loop primed and run with no detectable bubble contamination in the Doppler spectrum |

## Risks

**Compliance is a property of the whole system, not of your plenum.** The wall-less lumen sits in a
soft gel and is itself compliant, the connecting tubing is compliant, and in long soft tubing that
term can dominate everything else. Soloukey needed over 8 metres of tubing to reach an MRI room,
which would have flattened any pulse completely, though they only ran constant flow so it never
showed up for them.

Consequence: **you cannot tune the waveform on a bench loop and then connect the phantom.** Tune
with the real head in the loop, or with a compliance-matched surrogate supplied by Group 1.
Corollary for plumbing: stiff tubing, kept short. Every metre of soft tube is an uncontrolled
compliance in parallel with the knob you are trying to calibrate.

**Scope creep into the pump.** The failure mode is spending the year building a pump and never
characterizing the waveform, ending with hardware and no data. Greaby's own result is the hedge:
their pump was a commodity unit that produced ugly spike trains, and the plenum did the shaping. The
waveform quality came from the windkessel, not the pump. So borrow or buy the cheapest workable pump
first, get the loop instrumented and the compliance-to-PI map measured with it, and treat the custom
pump as the second-semester upgrade. December then has a working loop regardless.

## Interface items owned jointly with Group 1

Freeze these in a signed interface document in month one.

- **Lumen diameter.** Sets your required flow. At 3 mm, roughly 250 mL/min gives 60 cm/s mean and
  roughly 500 mL/min gives 120 cm/s peak. Do this arithmetic before speccing a pump. A pump sized
  for Soloukey's regime is off by more than an order of magnitude.
- **Maximum system pressure**, bounded by Group 1's wall-less burst test.
- **Connector geometry and bonding method.** Soloukey's reported failure was leakage at the inlet
  and outlet nozzles. Do not discover in April what fitting Group 1 cast in.
- **Insonation angle and vessel depth**, so you know what velocity the phantom presents to the
  transducer rather than what is flowing in the tube.
- **Phantom compliance**, or the surrogate, delivered to you for bench tuning.

## December gate

Loop produces a stable instrumented pulse at target rate through a rigid dummy channel of the agreed
lumen diameter, before the real phantom exists. Interface document signed.
