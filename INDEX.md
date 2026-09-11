# tcd-phantom — index

Bench phantom for TCD validation. Home for the GW BME senior-design build (two groups, AY 2026-27) and
for the phantom literature behind it.

Created 2026-09-11.

**On `refs/`:** the PDFs are **not committed to this repository.** Most are under publisher copyright
and cannot be redistributed. `refs/REFERENCES.md` lists every item with its DOI and open-access status
so anyone can obtain it through their own library. Collaborators working from a local clone will have
an empty `refs/` directory; drop your own copies in and git will ignore them.

---

## Why this exists

The device needs a bench fixture that can hold an MCA-realistic pulsatile waveform behind a
characterized skull window, so that synthesized TCD can be compared against measured TCD **in absolute
cm/s** on hardware rather than only in simulation. No published phantom does this. The two closest
each solve half of it and neither has a skull.

Two student groups, split along that seam:

| Group | Scope | Primary reference |
|---|---|---|
| 1 (materials) | Skin / bone / brain slabs, characterization rig, wall-less MCA vessel | Soloukey 2024 |
| 2 (plumbing) | Pulsatile loop, compliance and resistance tuning, pump | Greaby 2007 |

Team 7a is Group 2.

---

## Contents

```
tcd-phantom/
  INDEX.md              this file
  capstone/             project briefs, one per group
  refs/REFERENCES.md    DOI list + open-access status (PDFs are gitignored)
```

### capstone/

| File | For | What it is |
|---|---|---|
| `GROUP-1_materials-and-vessels.md` | Group 1 | Deliverables, method notes, acceptance criteria, risks, interface items |
| `GROUP-2_pulsatile-flow-loop.md` | Group 2 | Same shape, for the loop |
| `GROUP-2_lit-review-guide.md` | Group 2 | Reading list, the questions to answer, the comparison-table format |
| `GROUP-2_phase0-bench-rig.md` | Group 2 | ~$100 rig built during the lit review, to derive requirements from their own bench |

Shared interface items and the December gate are mirrored verbatim in both group briefs, so neither
team can be told something different. Not yet written: the standalone interface control document both
teams sign.

---

## The literature, and what each item is for

### The two the whole build rests on

| File | Paper | Why |
|---|---|---|
| `1-s2.0-S0301562907001032.pdf` | **Greaby, Zderic & Vaezy 2007**, UMB 33(8):1269 | The pulsatile loop, and it is in-house (Zderic, GW). Waveform is shaped by an air-filled **plenum**, not by the pump. Reaches **10-240 cm/s**, 50-500 mL/min, 62-138 bpm. Agarose gel has water-like attenuation, by their own admission. Target was a carotid. |
| `Soloukey-2024-Patient-specific-vascular-flow-phan.pdf` | **Soloukey et al. 2024**, UMB 50:860 | Wall-less casting via sacrificial water-soluble resin. Full TMM recipe. **Measures 1470 m/s**, against ~1540 assumed — a ~4.5% velocity bias for absolute-cm/s work. Slanted pipe at 25 deg is the insonation-angle answer. Flow regime far too low for MCA. |

### The two found 2026-09-11 that change decisions

| File | Paper | Why |
|---|---|---|
| `Roldan-2023-Head-phantom-for-the-acquisition-of.pdf` | **Roldan & Kyriacou 2023**, Photonics 10:504 | Skull + brain + pulsatile cerebral circulation + **ICP controllable 5-30 mmHg** via an artificial-CSF loop. Optical, so the skull is matched at 660-900 nm and **not** at 2 MHz. States its waveform **"does not have a clear dicrotic notch."** Raises the scope question of whether an ICP compartment belongs in the capstone, which cannot be retrofitted to a solid cast block. |
| `Qian-2014-Pulsatile-flow-characterization-in-.pdf` | **Qian et al. 2014**, IEEE TBME 61(9):2444 | **PVA cryogel measures 1536.5-1552.1 m/s** across 1-8 freeze-thaw cycles, with attenuation 0.96-1.70 dB/cm at 5 MHz and modulus 60.9-310.3 kPa. One lever moves stiffness and sound speed together, and it lands on target with no compositional tuning, unlike SEBS at 1470. Also shows **vessel wall stiffness changes the waveform**, so compliance is not only in the plenum. |

### Loop topology and secondary phantoms

| File | Paper | Why |
|---|---|---|
| `10-1055-s-0042-106396.pdf` | **Rominger et al.**, Thieme | Explicitly a teaching phantom. Constant-flow syringe pump **as the reference standard** plus a separate modulator, so ground truth is structural. Microbubble BMF and 0.5 mm tube are both wrong for quantitative MCA work. |
| `s41598-021-88420-3.pdf` | **Vanrossomme et al. 2021**, Sci Rep | Test bench reproducing ICA-like pulsatile waveforms. The bench transfers, the aneurysm and CT focus does not. |
| `JBO-030-117001.pdf` | **Boonya-ananta et al.**, JBO | Pulsatile radial-artery phantom with skin tone and obesity as variables. **Belongs to a separate wearable-PPG effort, not to this project.** Filed for cross-reference. |
| `Gorina-2025-Design-of-brain-vessel-phantom-mode.pdf` | **Gorina et al. 2025**, IEEE STDH | Aneurysm phantom, fabrication methods only. Low priority. |
| `2512.13477v1.pdf` | **Brumfiel et al.**, arXiv 2512.13477 | Guidewire robotics; the phantom is incidental. Lowest priority. |

### What waveform to aim at

| File | Paper | Why |
|---|---|---|
| `bok%3A978-3-030-48202-2.pdf` | **Robba & Citerio (eds) 2021**, *Echography and Doppler of the Brain* | **Ch 7 (Fedriga & Czosnyka)** covers flow velocity, PI, autoregulation and critical closing pressure in one chapter. The single best "why does the cerebral waveform look like that" reading. |
| `Journal of Neuroimaging - 2012 - Tegeler - ...pdf` | **Tegeler et al. 2013**, J Neuroimaging 23(3):466 | TCD velocities in a large healthy population. The normal-values reference. Note other sources in the library disagree on mean velocity (Robba/ESICM gives PSV 114 / MFV 73 / EDV 50 / PI 0.87; Neurosonology in Critical Care gives MFV ~49-53, PI ~0.8). |
| `j-neurosurg-article-p769.pdf` | **Aaslid, Markwalder & Nornes 1982**, J Neurosurg 57:769 | The origin of TCD. Establishes what the measurement is. |

### Why the waveform has that shape

| File | Paper | Why |
|---|---|---|
| `stergiopulos-et-al-1999-...windkessel-model.pdf` | **Stergiopulos, Westerhof & Westerhof 1999**, Am J Physiol 276(1):H81 | Canonical 4-element windkessel, Table 2 healthy human values. The theory the plenum implements in hardware. |
| `shoemaker-et-al-2025-...cerebral-arteries...pdf` | **Shoemaker et al. 2025**, Am J Physiol | Direct aorta-to-MCA pressure. **PP attenuates 68 aortic, 59 CCA, 43 distal ICA, 25 at M1.** The cerebral bed does not see aortic pressure, which moves the loop's target well below Greaby's 100-250 mmHg. n=5, so a direction not a specification. |
| `permutt-riley-1963-...vascular-waterfall.pdf` | **Permutt & Riley 1963**, J Appl Physiol 18:924 | Critical closing pressure. Why diastolic velocity behaves as it does in the cerebral bed, and why the loop's resistance should be set less restrictive than a peripheral match. |

### Measurement caveats that govern every comparison

| File | Paper | Why |
|---|---|---|
| `1-s2.0-S0301562921003811.pdf` | **Ambrogio, ... Ramnarine 2022**, UMB | PW Doppler **overestimates max velocity by 12-50% typically, up to 75%** at small sample volumes, across 51 probes and 4 manufacturers. Without this, a systematic overread gets blamed on the phantom. Same Ramnarine as the BMF validation work. |
| `Finding_the_peak_velocity_in_a_flow_from_its_doppler_spectrum.pdf` | **Vilkomerson, Ricci & Tortoli 2013**, IEEE TUFFC | The observed envelope is not the true peak velocity. Companion to the above. |
| `Leotta-2024-Measurement-of-transcranial-doppler.pdf` | **Leotta et al. 2024**, J Clin Monit Comput | MCA-M1 Doppler angle **median 24.6 deg (IQR 16.4-35.4)**, depth **median 51.5 mm**. Velocity underestimation 6% at 20 deg, 23% at 40, over 50% at 60. Sets the phantom geometry with measured numbers. |

---

## Not held, and worth acquiring

- **Greaby R (2005)**, MS thesis, Bioengineering, Univ. Washington. The fuller build documentation
  behind the 2007 paper. Interlibrary loan.
- **Bottan S**, *In-Vitro Model of Intracranial Pressure and Cerebrospinal Fluid Dynamics*, PhD thesis,
  ETH Zurich. The ICP-pulsation reference Roldan validates against.
- **IEC 61685**, flow test object standard. Cited everywhere in this literature, never held. Check
  institutional access before assuming it is readable.
- **Ramnarine KV et al. (1998)**, UMB 24:451-459. Blood-mimicking fluid validation. Needed by any
  quantitative velocity work here.

---

## Open decisions

1. **ICP compartment in scope or not.** Roldan shows it is buildable at this level. It cannot be
   retrofitted to a solid cast block, so the answer has to precede Group 1's mold design.
2. **SEBS versus PVA cryogel** for the brain block. SEBS is stable uncovered for over 6 months but
   measures 1470 and needs a glycerol sweep. PVA-C lands at 1536-1552 natively and gives tunable
   stiffness, but is water-based and needs 8 days of freeze-thaw cycling for the stiff end.
3. **Wall-less versus walled vessel**, pending Group 1's burst test at MCA pressures. Nobody in this
   literature has demonstrated wall-less at those velocities.
4. **Skull analog material.** No printable homogeneous polymer reaches cortical bone. Roldan's resin
   was justified mechanically and never acoustically.
