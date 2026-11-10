# Project Description: Transcranial Doppler Phantom

**GW BME senior design, AY 2026-27** | Two teams | Advisor: K. Horrigan | Host lab: V. Zderic, SEH 5100 | 2026-10-30

> **Editing note.** The authoritative formatting now lives in
> `obsidian/Work/drafts/TCD-Phantom-Project-Description-2026-10-30.docx`, which K. Horrigan edited by
> hand on 2026-10-30. This markdown has been synced to match that file's content. **Do not regenerate
> the .docx from this file**, because that would discard his formatting pass. Edit the .docx, then
> sync the text back here.

Prepared for the capstone course faculty. This is the consolidated description.

The full working detail for each team lives in `GROUP-1_materials-and-vessels.md` and
`GROUP-2_pulsatile-flow-loop.md`, and the shared seam between them lives in
`INTERFACE-CONTROL-DOCUMENT.md`. Those three files are the documents the students actually work
from, and they are kept current as numbers settle.

## What is being built

One instrument, built by two teams. A benchtop phantom that presents a **middle cerebral artery
velocity waveform behind a characterized skull window**, so that a transcranial Doppler measurement
can be checked against an independently known flow on hardware rather than only in simulation.
Operating frequency is **2 MHz**, the TCD band, and every acoustic property is reported at that
frequency.

The customer is real. The advisor needs this instrument for dissertation validation work, and the
equipment stays in the host lab after the course ends.

## Why this is a design project and not a replication exercise

Two published phantoms sit closest to the need, and each solves about half of it.

- **Soloukey et al. 2024** casts a wall-less vessel in a tissue-mimicking gel and images it cleanly,
  but runs at roughly 8 cm/s, more than an order of magnitude below peak systolic velocity in the
  M1 segment.
- **Greaby, Zderic and Vaezy 2007**, which is in-house work at GW, reaches 10 to 240 cm/s pulsatile,
  but uses an excised vessel in agarose whose attenuation is close to water, and targets a carotid
  rather than a cerebral vessel.

Neither has a skull. The acoustic window is the part with no published recipe, which is why it is
the piece this project has to solve rather than copy.

Two specific things are genuinely unproven, and both are scheduled as first-semester go/no-go tests
rather than deferred to the spring: whether a wall-less lumen survives MCA pressures, and what a
thin skull-analog window actually costs in insertion loss at 2 MHz.

## How the work divides

This is not two independent phantoms. It is one phantom split at a defined mechanical interface, so
that each team owns a complete subsystem with its own standalone deliverable and neither team stalls
when the other slips.

```
  Flow team                               |  Materials team
  ----------------------------------------+---------------------------------
  reservoir                               |
  pump / piston actuator                  |
  compliance chamber                      |
  resistance / constriction               |
  pressure instrumentation                |
  connecting tubing                       |
                   -> INLET FITTING ->    |  cast-in connector
                                          |  wall-less MCA lumen in TMM
                                          |  surrounding tissue block
                                          |  skull window plate
                   <- OUTLET FITTING <-   |  cast-in connector
  return tubing                           |
  gravimetric flow measurement            |
```

Everything left of the fittings belongs to the flow team. Everything right belongs to the materials
team. The fittings themselves are a joint deliverable and neither team may choose them alone.

---

## Team: Tissue-Mimicking Materials, Acoustic Path and Vessel

*Lily Cushman, Jillian O'Kean, Chloe Luxenberg, Colleen MacWilliams*

**Objective.** Produce and acoustically characterize three-layer transcranial path of scalp, skull
and brain, plus a wall-less 3 mm middle cerebral artery, so that a phantom can be cast whose
acoustic properties are measured.

**Responsibilities.** Tissue-mimicking formulation and casting process. Acoustic characterization
instrumentation. Skull window material and thickness set. Mold design. How the lumen is formed and
how it is terminated. The structural limit of the wall-less vessel.

### Deliverables

1. **Calibrated through-transmission bench.** Two transducers at known separation, substitution
   method against a degassed water path, yielding sound speed and, from insertion loss versus
   frequency, attenuation. This rig remains lab equipment after the project ends.
2. **Material property table.** Sound speed, attenuation coefficient in dB/cm/MHz, and density, for
   every candidate formulation, all at 2 MHz.
3. **Composition versus sound-speed calibration curve.** The reference formulation measures
   1470 m/s where brain is near 1540 to 1560, a 4 to 5 percent bias that lands directly on every
   velocity the phantom will ever report. Sweep the controls and deliver a curve rather than a
   single recipe.
4. **Skull window plate set.** Not one plate but a set spanning easy to difficult windows, with
   thin-plate insertion loss measured for each, plus insertion loss versus angle of incidence. The
   human temporal window averages about 2.5 mm and fails outright in roughly one person in five, so
   window quality is a variable to be spanned rather than a nominal value to be hit.
5. **Wall-less lumen burst result.** Pressurize a cast wall-less channel to failure. This is a
   go/no-go on the whole architecture and it is a first-semester item.
6. **Cast phantom head**, integrating the above at anatomical layer thicknesses.

### Acceptance criteria

| # | Criterion |
|---|---|
| 1 | Rig reproduces degassed water sound speed within a stated tolerance at a logged temperature |
| 2 | Cast-to-cast repeatability quantified across separate casts of one formulation (expected 2 casts for now) |
| 3 | Sound speed, attenuation and density reported together at 2 MHz for every material |
| 4 | Composition versus sound-speed curve with enough points to interpolate a target |
| 5 | Thin-plate insertion loss for each window plate against the advisor's target |
| 6 | Loss versus incidence angle on the bone plate |
| 7 | Stability re-measurement of a subset at 4 and 12 weeks |
| 8 | One named recommended brain formulation, delivered before the casting freeze |

### Principal risks

**The wall-less lumen at MCA velocity is unproven**, and it is the architectural risk. Prior work
reports that high flow rates can rupture the material around a wall-less channel.

**Bone will not match.** No printable homogeneous polymer reaches cortical bone's sound speed,
density and attenuation together, and bone supports shear waves that soft-tissue mimics do not. The
honest deliverable is a characterization of the candidates plus an explicit statement of the
residual gap. That is a finding, not a failure, and it is the single most useful thing this team can
hand the advisor.

---

## Team: Pulsatile Flow Loop

*Sidney Brutscher, Grace Zereski, Elizabeth Boelhouwer, Madeleine Carroll*

**Objective.** Build and characterize a pulsatile flow loop that delivers a physiologic MCA velocity
waveform through the cast phantom. The deliverable is explicitly **not "a pump."** It is a measured
map from the loop's compliance and resistance settings to the resulting pulsatility index and peak
systolic velocity, with the waveform instrumented and independently verified.

**Responsibilities.** Pump or actuator architecture. Compliance chamber. Resistance mechanism.
Pressure and flow instrumentation. Working fluid selection. Tubing material and routing upstream of
the fitting. A mechanical pressure ceiling protecting the cast block. The Phase 0 bench rig in its
entirety.

### Deliverables

1. **Instrumented loop** with an in-line pressure gauge. Without it, tuning is blind.
2. **Independent flow ground truth.** Timed collection and weighing at the outflow. Velocity is not
   validated with the same Doppler system that is under test.
3. **Compliance and resistance sweep.** The core result: a measured map from plenum air volume and
   constriction setting to pulsatility index and peak systolic velocity. Pulsatility here is not
   commanded, it emerges from the hardware R and C values, which is the same class of mechanism that
   produces it in a patient.
4. **Position-commanded piston actuator.** A servo or stepper rather than a crank, because a crank
   produces only a sine and the diastolic notch is the feature that matters. Stroke volume works out
   near 0.5 mL per beat, which is a 3 mL syringe bore, and peak force is under 1 N.
5. **Mechanical pressure ceiling.** A relief path teed in ahead of the block, set below the
   materials team's measured pressure.
6. **Bubble control procedure.** Air is catastrophic for Doppler, since bubbles are enormous
   scatterers, and it silently changes system compliance.

### Acceptance criteria

| # | Criterion |
|---|---|
| 1 | Stable pulse at commanded rate across 60 to 140 bpm, pressure instrumented |
| 2 | Peak systolic velocity reaches MCA range at the agreed lumen diameter |
| 3 | Pulsatility index lands in the advisor's target band, and the setting that achieves it is recorded |
| 4 | Commanded versus measured flow agreement, with an error bound, against the independent ground truth |
| 5 | Compliance and resistance sweep map delivered, repeatable across sessions |
| 6 | Loop primed and run with no detectable bubble contamination in the Doppler spectrum |

### Principal risks

**Compliance is a property of the whole system, not of the plenum.** The wall-less lumen sits in a
soft gel and is itself compliant, and so is every length of connecting tube. The consequence is that
the waveform cannot be tuned on a bench loop and then connected to the phantom. Tuning happens with
the real block in the circuit, or against a compliance-matched surrogate supplied by the materials
team.

**Scope creep into the pump.** The failure mode is spending the year building a pump and never
characterizing the waveform, ending with hardware and no data. The hedge is built into the schedule:
get the cheapest workable actuator running first, instrument the loop, measure the compliance-to-PI
map with it, and treat a refined pump as the next upgrade.

---

## The shared interface

Ten specifications are jointly owned and tracked in `INTERFACE-CONTROL-DOCUMENT.md`. Four of them
drive the schedule.

**Lumen diameter is frozen first, because everything follows from it.** At 3 mm, roughly
250 mL/min gives 60 cm/s mean and roughly 467 mL/min gives 110 cm/s peak. Change the diameter and
the flow requirement moves as the square. No pump is specified before this number is fixed.

**The cast-in connector has a hard ordering constraint, and it is the only one in the project.**
There is no way to add a fitting to a wall-less lumen after the fact. The connector has to be
embedded in the block while it is cast, with enough buried surface area that pressure cannot pull it
back out. That means the flow team must hand the materials team **the actual physical part** before
the pour, not a specification for one. This item sits on one team's schedule and in the other team's
critical path, which is exactly the coordination problem the course is meant to exercise.

**The inlet matches the lumen, 3 mm to 3 mm, with no step.** Flow leaving a sudden contraction needs
a straight run to settle back into a developed profile, roughly 80 mm at 55 cm/s and 155 mm at
110 cm/s. The M1 segment being insonated is only 22 to 27 mm long inside a head-sized block, so
there is nowhere inside the phantom to put that straight run. It has to happen upstream in tubing,
where straight length is free.

**Maximum system pressure is bounded by the burst test**, which means one team's safety limit is
unknown until the other team measures it.

## Schedule and gates

**December gate, materials team.** Characterization rig reproduces degassed water sound speed.
Wall-less burst pressure result exists. Interface items agreed.

**December gate, flow team.** Loop produces a stable instrumented pulse at target rate through a
rigid dummy channel of the agreed lumen diameter, before the real phantom exists. Interface items
agreed.

**Spring.** Integrate, then characterize the assembled phantom through the window: Doppler velocity
against gravimetric ground truth, with the window plate set swapped through to measure what window
quality costs.

## If integration slips

Each team has a complete, defensible deliverable that does not depend on the other team finishing.
The materials team has a calibrated characterization bench plus a property dataset for tissue and
skull-analog materials at 2 MHz, which is publishable-quality bench work in its own right and leaves
reusable equipment in the lab. The flow team has an instrumented pulsatile loop plus a measured
compliance-and-resistance-to-pulsatility map, validated through a rigid dummy channel.

## Mentoring and logistics

One meeting per team every two weeks with the advisor, plus email between. Work happens in the host
lab in SEH 5100, where access has been granted. Two standing constraints came with that access: stay
on the host side of the lab, and minimize time in the south research area so as not to disturb
graduate students.

Current budget, per team, is a few hundred dollars of materials (teams have the final figures).
