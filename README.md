# tcd-phantom

A bench phantom for transcranial Doppler validation, and the working repository for the GW BME
senior design build behind it (two groups, AY 2026-27).

## What is being built

A phantom that presents an **MCA-realistic pulsatile waveform behind a characterized skull window**,
so that Doppler measurements can be checked against a known flow on hardware rather than only in
simulation.

Two published phantoms sit closest to this, and each solves about half of it:

- **Soloukey et al. (2024)** casts wall-less vessels in a tissue-mimicking gel and images them
  cleanly, but runs at roughly 8 cm/s, over an order of magnitude below the middle cerebral artery.
- **Greaby, Zderic & Vaezy (2007)** reaches 10 to 240 cm/s with a pulsatile loop, but uses an
  excised vessel in agarose whose attenuation is close to water, and targets a carotid.

Neither has a skull. That is the part with no published recipe, and it is why the acoustic window is
the piece this project has to solve rather than copy.

## Repository layout

```
INDEX.md              annotated index: the literature and what each item is for
capstone/             project briefs, one per student group
refs/REFERENCES.md    DOI list with open-access status (PDFs are not committed)
```

## The two groups

| Group | Scope | Primary reference |
|---|---|---|
| 1, materials | Skin / bone / brain slabs, acoustic characterization rig, wall-less MCA vessel | Soloukey 2024 |
| 2, plumbing | Pulsatile loop, compliance and resistance tuning, pump | Greaby 2007 |

Each group has a brief in `capstone/` covering deliverables, method notes, acceptance criteria and
risks. The shared interface items and the December gate appear **verbatim in both briefs**, so the
two teams cannot be working from different assumptions about the seam between them.

Group 2 also has a literature review guide and a Phase 0 bench rig, the second of which is a roughly
$100 build used to derive requirements from measurement rather than from the literature alone.

## A note on the literature PDFs

`refs/` holds no PDFs in this repository. Most of these papers are under publisher copyright and a
public repo is not the place to redistribute them. `refs/REFERENCES.md` lists every item with its
DOI and its open-access status, so anyone can obtain their own copy. Several are open access and free
to download, including both of the papers this build rests on most heavily.

**Project members** can get the PDFs from the shared Drive folder, which is restricted to GWU
accounts: https://drive.google.com/drive/folders/1BS4GFaekAu13mgtEKKH5-q6HEAU1PLzF

If you clone this and drop your own PDFs into `refs/`, `.gitignore` will keep them out of commits.

## Contributing

Two things worth knowing before you open a pull request.

**Verify citations.** Check every citation against the actual article before it goes into written
work, and do not cite a paper you have not opened. Entries in `REFERENCES.md` marked *(verify)* were
transcribed from other papers' reference lists and have not been confirmed against the source.

**Keep unpublished results out.** This repository is public. Target values that come from
unpublished work are written as placeholders such as `[value TBD by advisor]` and should stay that
way. Raw measurement data also stays out of git; `.gitignore` covers the usual formats.

## Status

Early. The briefs are drafted, the literature is indexed, and the build has not started.

Open questions that need answers before anyone cuts material are listed at the end of `INDEX.md`.
The one with the shortest fuse is whether an intracranial pressure compartment is in scope, because
it cannot be retrofitted into a solid cast block after the fact.
