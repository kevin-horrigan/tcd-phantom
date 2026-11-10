# Transcranial Doppler Phantom: Team Summaries

**GW BME senior design, AY 2026-27** | Advisor: K. Horrigan | Host lab: V. Zderic, SEH 5100 | 2026-10-30

> **Editing note.** The authoritative formatting lives in
> `obsidian/Work/drafts/TCD-Phantom-Team-Summaries-2026-10-30.docx`, which K. Horrigan edited by hand
> on 2026-10-30. This markdown is synced to that file's content. **Do not regenerate the .docx from
> this file**, because that would discard his formatting pass. Edit the .docx, then sync the text
> back here.
>
> **One intentional divergence from the .docx.** His edit removed the second of the two reasons in
> the flow team's deliverables paragraph, which left "Two of those carry the reasoning" introducing
> one item. This file and the email draft read "One of those carries the reasoning" instead. The
> .docx still says "Two" and needs the same one-word fix before it is sent.

Two teams, one instrument. The project builds a benchtop phantom that presents a middle cerebral
artery velocity waveform behind a characterized skull window, so that a transcranial Doppler
measurement can be checked against an independently known flow on hardware rather than only in
simulation. Operating frequency is 2 MHz. The two published phantoms closest to this each solve
about half of it, and neither has a skull, which is the part with no published recipe and the reason
this is a design project rather than a replication exercise. The work is split at a defined
mechanical interface so that each team owns a complete subsystem with a standalone deliverable, and
neither team stalls when the other slips.

## Tissue-Mimicking Materials, Acoustic Path and Vessel

*Lily Cushman, Jillian O'Kean, Chloe Luxenberg, Colleen MacWilliams*

This team produces and acoustically characterizes everything the ultrasound beam has to cross,
meaning scalp, skull and brain, along with the middle cerebral artery itself as a 3 mm wall-less
lumen cast directly into tissue-mimicking material with no tube in it. They own the material
formulation, the casting process, the mold, the skull window, and how the vessel is formed and
terminated. The objective is a phantom head whose acoustic properties are measured, reported at
2 MHz.

Their deliverables are a calibrated through-transmission bench for sound speed and attenuation,
which stays in the lab as equipment afterward, a property table covering every candidate
formulation, a composition versus sound-speed calibration curve, a set of skull window plates
spanning easy to difficult windows with insertion loss measured for each, and the cast phantom head.
The calibration curve matters more than it sounds: the published recipe measures 1470 m/s where
brain is near 1540, and that gap lands directly on every velocity the finished phantom will report.
They are assessed on whether their rig reproduces the known sound speed of degassed water, on
quantified cast-to-cast repeatability, and on insertion loss through the thin window plates. Their
December gate is that the rig reproduces water and the wall-less vessel has been pressurized to
failure, since that test is a go/no-go on the whole architecture.

## Pulsatile Flow Loop

*Sidney Brutscher, Grace Zereski, Elizabeth Boelhouwer, Madeleine Carroll*

This team builds and characterizes the pulsatile flow loop that drives a physiologic middle cerebral
artery waveform through that phantom. They own the piston actuator, the compliance chamber, the
adjustable resistance, the pressure and flow instrumentation, the working fluid, and a mechanical
pressure ceiling that protects the cast block from the pump. The deliverable is deliberately not "a
pump." Pulsatility is not commanded here, it emerges from the hardware compliance and resistance
values, which is the same class of mechanism that produces it in a patient, so what the team owes is
a measured map from those settings to the resulting waveform.

Their deliverables are an instrumented loop with in-line pressure, an independent gravimetric flow
ground truth, the compliance and resistance sweep map that is the core result, a position-commanded
piston rather than a crank, and a bubble control procedure. One of those carries the reasoning: flow
is measured by timed collection and weighing rather than with the Doppler system under test, because
a measurement cannot validate itself. They are assessed on a stable pulse across 60 to 140 bpm, peak
systolic velocity reaching MCA range at the agreed 3 mm lumen, pulsatility index landing in the
target band with the setting recorded, and commanded versus measured flow agreement with a stated
error bound. Their December gate is a stable instrumented pulse through a rigid dummy channel of the
agreed diameter, before the real phantom exists.

## The seam between them

One coupling is worth knowing about, because it is the only hard ordering constraint in the project.
The fitting that carries fluid into the cast block cannot be added to a wall-less lumen after the
fact. It has to be decided before the block is poured, which means the flow team has to hand the
materials team an actual physical part before the materials team can cast. Ten shared
specifications, that one included, are tracked in a jointly owned interface document so the two
teams cannot work from different assumptions.
