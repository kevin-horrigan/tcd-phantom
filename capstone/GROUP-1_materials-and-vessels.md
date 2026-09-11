# Group 1: Tissue-Mimicking Materials and Vessel Construction

**TCD phantom capstone, Group 1 of 2** | Advisor: K. Horrigan | Draft 2026-09-10

## Objective

Produce and acoustically characterize the three-layer transcranial path (scalp, skull, brain) and a
wall-less middle cerebral artery lumen, so that a phantom head can be cast whose acoustic properties
are measured rather than assumed. Target operating frequency is **2 MHz**, the TCD band. All
properties are to be reported at that frequency.

## Primary references

- Soloukey et al. 2024, *Ultrasound Med Biol* 50:860. Wall-less patient-specific flow phantom.
  Source of the casting process and the tissue-mimicking recipe.
- Cabrelli et al., SEBS-in-mineral-oil gel materials (cited as ref 23 in Soloukey).
- Duck, *Physical Properties of Tissue*, for the target values the materials must hit.
- Transcranial HIFU phantom literature, for skull-analog materials. Scan this early.

## Deliverables

1. **Calibrated through-transmission bench.** Two transducers, known separation, substitution method
   against a degassed water path. Yields sound speed and, from insertion loss versus frequency,
   attenuation. This rig remains lab equipment after the project ends.
2. **Material property table:** sound speed, attenuation coefficient (dB/cm/MHz), and density, for
   every candidate formulation. Density by Archimedes, needed because impedance governs the
   interface reflections in the layered stack.
3. **Glycerol calibration curve.** The Soloukey formulation (10% SEBS G1650E in mineral oil, 15%
   glycerol, 0.2% TiO2, 130 C melt, 90 C pour) measures 1470 m/s. Brain is near 1540 to 1560.
   Glycerol fraction is the sound-speed lever. Sweep it and produce an interpolable curve.
4. **Skull window plate set.** Not one plate. A set spanning easy to difficult windows, so the
   finished phantom can test find-rate against window quality rather than against one nominal skull.
5. **Wall-less lumen burst result.** See risks.
6. **Cast phantom head**, integrating the above at anatomical layer thicknesses.

## Method notes that determine whether the numbers are real

- **Temperature.** Sound speed moves roughly 2.5 m/s per degree C. Log bath temperature on every
  data row. A measurement without a temperature is not a measurement.
- **Validate on water first.** Degassed water at a known temperature has a textbook sound speed
  (Marczak or Del Grosso). If the rig cannot reproduce it to within a few m/s, nothing downstream is
  trustworthy. This is the first design review gate.
- **Thickness dominates the error budget.** Sound speed is thickness over transit time. Timing by
  cross-correlation is good to nanoseconds and is negligible. On a 25 mm slab a 50 micron thickness
  error is about 3 m/s, which is fine. A half-millimeter caliper error is about 30 m/s, which smears
  the entire glycerol effect into noise. Use a micrometer, five points, report the spread.
- **Two thicknesses per formulation.** Measured insertion loss is absorption plus reflection at both
  faces. Differencing two thicknesses cancels the interface term and gives a clean attenuation
  coefficient. Sound speed needs only one thickness, attenuation needs two.
- **Coupon thickness is not anatomical thickness.** Slabs are characterization coupons sized for
  measurement quality, around 20 to 30 mm. The phantom is then built at real layer thicknesses of
  the same characterized material. Do not try to make one object do both jobs.
- **Bone needs two separate measurements.** At 2 MHz the wavelength in cortical bone is about
  1.4 mm, so an anatomically thin window plate is only a couple of wavelengths thick and the
  transmitted pulse is dominated by internal reverberation. Measure a *thick* coupon for material
  constants, and separately measure the *thin* anatomical plate for total insertion loss only, with
  no attempt to decompose it. The thin-plate insertion loss is the number the advisor needs.
- **Replicates must be separate casts.** Batch-to-batch variance in a hand-poured gel will exceed
  measurement uncertainty. Measuring one slab five times characterizes the rig. Casting three
  batches at one formulation characterizes the formulation. Matrix is formulation x 2 thicknesses
  x 3 casts.
- **Tank geometry.** A 13 mm element at 2 MHz has a near-field length near 57 mm. The sample must
  sit beyond it. Work this out before buying a tank.
- **Molds must survive 130 C.** Aluminum or high-temperature silicone. Printed PLA will deform.
  Cast between flat parallel plates so faces come out parallel, since non-parallel faces refract the
  beam and corrupt timing on top of the thickness error.
- **Bubbles read as material properties.** Degas the melt if a vacuum chamber is available. If not,
  stir slowly by hand with the spoon kept submerged, per Soloukey. Expect to lose the first casts.

## Acceptance criteria

| # | Criterion |
|---|---|
| 1 | Rig reproduces degassed water sound speed within a stated tolerance at a logged temperature |
| 2 | Repeatability quantified: separate casts, same formulation, spread reported |
| 3 | Sound speed, attenuation, and density reported together at 2 MHz for every material |
| 4 | Glycerol-fraction versus sound-speed curve with enough points to interpolate a target |
| 5 | Thin-plate insertion loss for each window plate, compared against the target insertion loss supplied by the advisor `[value TBD by advisor]` |
| 6 | Angle sweep on the bone plate: insertion loss versus incidence angle |
| 7 | Stability re-measurement of a subset at 4 and 12 weeks (Soloukey claims 6 months) |
| 8 | One named recommended brain formulation, delivered before Group 2's casting freeze |

## Risks

**Wall-less lumen at MCA velocity is unproven, and it is the architectural risk.** Soloukey's
wall-less design ran at 8 cm/s. Peak systolic in M1 is over an order of magnitude higher, and the
Greaby paper cites prior work (Peopping 2002) reporting that high flow rates can rupture the
tissue-mimicking material around a wall-less channel. Cast a wall-less channel in the candidate
formulation and pressurize it to failure **in the first semester**. This is a go/no-go on the whole
architecture. Fallback is thin-walled compliant tubing with the acoustic penalty accepted and
characterized, and that fallback must be designed early or not at all.

**Bone will not match.** No printable homogeneous polymer reaches cortical bone's sound speed,
density, or attenuation, and bone supports shear waves that soft-tissue mimics do not. Filled
composites give a tuning lever via filler loading. The honest deliverable is a characterization of
the candidates plus an explicit statement of the residual gap. That is a finding, not a failure.

**Insonation angle.** The lumen must be oriented so the beam from the temporal window makes a small
angle with the flow axis. A channel perpendicular to the window face gives a Doppler angle near 90
degrees and measures nothing. Soloukey's slanted pipe was cut at 25 degrees for this reason. State
the intended angle in the design document and confirm it in test.

## Interface items owned jointly with Group 2

Freeze these in a signed interface document in month one.

- **Lumen diameter.** Sets Group 2's required flow. At 3 mm, roughly 250 mL/min gives 60 cm/s mean
  and roughly 500 mL/min gives 120 cm/s peak. Nobody buys a pump before this is frozen.
- **Maximum system pressure.** Group 2's peak output must be survivable by the lumen. Cross-linked
  to the burst test above.
- **Connector geometry and bonding method.** Soloukey's own reported failure was leakage at the
  inlet and outlet nozzles.
- **Insonation angle and vessel depth.**
- **Compliance of the cast phantom**, or a compliance-matched surrogate supplied to Group 2 for
  bench tuning. See Group 2's brief for why this matters.

## December gate

Rig reproduces water. Wall-less burst pressure result exists. Interface document signed.
