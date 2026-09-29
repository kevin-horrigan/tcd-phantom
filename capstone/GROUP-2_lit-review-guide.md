# Group 2: Reading Notes for the Literature Review

**TCD phantom capstone, pulsatile flow group** | K. Horrigan | Revised 2026-09-29

Your course sets the requirements for this assignment, not me. What follows is what I can usefully
add: which papers are worth your time, what to pull out of them, and the things that are easy to get
wrong in this corner of the literature. Take what helps and ignore the rest.

**Numbering below is unchanged from the version you worked from**, so your existing answers and table
still line up. Group 1 now has a companion set covering materials and the acoustic path.

## What this is aiming at

The useful end product is a **map of the design space** for pulsatile flow phantoms, so that when you
propose a device you can say what has been tried, what it achieved, and why yours is different. Your
feature list then falls out of it almost mechanically.

A table plus a few pages of argument goes a long way. Twenty paragraphs each summarizing one paper
does not.

## Things worth being able to answer

Not a checklist to submit. These are what the review is really about, and what I would most enjoy
talking through with you. If one cannot be answered from the literature, that is itself worth saying.

**On the target**

1. What are normal velocity values in the middle cerebral artery, peak systolic, end diastolic, and
   mean? What is a normal pulsatility index?
2. How does a cerebral velocity waveform differ in shape from a carotid or peripheral one, and why?
   The answer involves downstream resistance.
3. What heart rate range does the device need to cover, and why might the extremes matter clinically?

**On existing phantoms**

4. What drive mechanisms have been used to produce pulsatile flow on a bench, and what are the
   failure modes of each?
5. How is waveform shape controlled in existing designs? Is it imposed by the pump or produced by
   something downstream of it?
6. What velocity and pressure ranges have published phantoms actually achieved?
7. How do published designs construct the vessel, and what are the acoustic consequences of each
   approach?

**On fluids and validation**

8. What is required of a blood-mimicking fluid, and which properties matter for what reason?
9. How do published studies verify that their phantom produced the flow they intended? What is the
   independent reference in each case?

**On the gap**

10. Has anyone built a pulsatile phantom for **transcranial** Doppler specifically? If not, what is
    different about that case?

Question 10 is the one that defines your project. Spend real effort on it.

## Reading list

Start with the first three. The rest fills in around them.

### Start here

**A note on numbering.** The numbers in this list are local to this document and are *not* the same
as the numbers in `refs/REFERENCES.md`. That file is the canonical list, it carries DOIs and
open-access status, and it is the one to cite from. If a number here and a number there disagree,
`REFERENCES.md` wins. Better still, refer to papers by author and year rather than by number.

1. **Greaby R, Zderic V, Vaezy S.** Pulsatile flow phantom for ultrasound image-guided HIFU
   treatment of vascular injuries. *Ultrasound Med Biol* 2007;33(8):1269-1276.
   The closest precedent to your device, built in Dr. Zderic's prior group. Worth reading twice, and
   worth getting the velocity range right: it reaches **10 to 240 cm/s**, the only paper on this list
   that covers the range we need. Pay attention to how waveform shape is controlled, which is not
   where most people expect.

2. **Greaby R.** A pulsatile flow phantom for image-guided HIFU treatment of vascular injury.
   MS thesis, Bioengineering, University of Washington, 2005.
   The fuller build documentation behind the paper. Request through interlibrary loan early, since
   it may take time to arrive.

3. **Soloukey S, et al.** Patient-specific vascular flow phantom for MRI- and Doppler ultrasound
   imaging. *Ultrasound Med Biol* 2024;50:860-868.
   The other team's primary reference. Read it so you understand what you are plumbing into. Note
   their flow regime is nowhere near yours, and think about why that matters.

### Flow phantom design

4. **Rickey DW, Picot PA, Christopher DA, Fenster A.** A wall-less vessel phantom for Doppler
   ultrasound studies. *Ultrasound Med Biol* 1995;21:1163-1176.
5. **Peopping TL, Nikolov HN, Rankin RN, et al.** An in vitro system for Doppler ultrasound flow
   studies in the stenosed carotid artery bifurcation. *Ultrasound Med Biol* 2002;28:495-506.
6. **Law YF, Johnston KW, Routh HF, Cobbold RSC.** On the design and evaluation of a steady flow
   model for Doppler ultrasound studies. *Ultrasound Med Biol* 1989;15:505-516.
7. **Dabrowski W, Dunmore-Buyze J, Rankin RN, Holdsworth DW, Fenster A.** A real vessel phantom for
   flow imaging: 3-D Doppler ultrasound of steady flow. *Ultrasound Med Biol* 2001;27:135-141.
8. **Frayne R, Gowman LM, Rickey DW, et al.** A geometrically accurate vascular phantom for
   comparative studies of x-ray, ultrasound, and magnetic resonance vascular imaging. *Med Phys*
   1993;20:415-425.
9. **Ho CK, Chee AJY, Yiu BYS, et al.** Wall-less flow phantoms with tortuous vascular geometries.
   *IEEE Trans Ultrason Ferroelectr Freq Control* 2017;64:25-38.

19. **Rominger MB, Müller-Stuler E-M, Pinto M, Becker AS, Martini K, Frauenfelder T,
    Klingmüller V (2016).** Easy pulsatile phantom for teaching and validation of flow
    measurements in ultrasound. *Ultrasound International Open* 2:E93-E97.
    doi:10.1055/s-0042-106396.
    Numbered 19 to match the number you already assigned it. Listed here out of sequence so
    nothing else shifts. Its constant-flow pump defines mean flow structurally, which is a
    different answer to the ground-truth problem than measuring it afterward.

### Blood-mimicking fluid

10. **Ramnarine KV, Nassiri DK, Hoskins PR, Lubbers J.** Validation of a new blood-mimicking fluid
    for use in Doppler flow test objects. *Ultrasound Med Biol* 1998;24:451-459.
    Note: Greaby's printed reference list misspells the last author as "Lubvers." It is Lubbers.
11. **IEC 61685:2001**, Ultrasonics: flow measurement systems, flow test object. 36 pages.
    **Worth knowing its limits: it specifies a test object carrying steady flow.** So it governs the
    tissue-mimicking material and blood-mimicking fluid specifications, and it does **not** govern
    waveform for a pulsatile phantom. Do not lean on it for something it does not cover. Check
    library access before assuming you can read it.
12. **Lin YH, Shung KK.** Ultrasonic backscattering from porcine whole blood of varying hematocrit
    and shear rate under pulsatile flow. *Ultrasound Med Biol* 1999;25:1151-1158.

### Pump architecture and waveform shaping

13. **Westerhof N, Lankhaar JW, Westerhof BE.** The arterial Windkessel. *Med Biol Eng Comput*
    2009;47:131-141.
    The accessible canonical review of why compliance shapes an arterial waveform. Read this before
    you design anything. Verified 2026-09-22.

13b. **Stergiopulos N, Westerhof BE, Westerhof N.** Total arterial inertance as the fourth element
    of the windkessel model. *Am J Physiol Heart Circ Physiol* 1999;276(1):H81-H88.
    A different, earlier paper sharing two authors with the one above, and the copy in the Drive
    folder. Where the 2009 review explains the concept, this one adds inertance as a fourth element
    and gives healthy human parameter values in its Table 2. Read 2009 first for understanding, then
    this one when you need numbers. Both belong on your list.
14. **ISO 5840**, cardiovascular implants, prosthetic heart valves. Contains the established bench
    practice for driving physiologic pulsatile flow. You do not need the whole standard, you need
    the test loop section.
15. **Mock circulatory loop literature** for ventricular assist device testing. Search term is
    "mock circulatory loop" or "mock circulation loop." This community has been solving your exact
    problem for decades. Find two or three representative papers rather than exhaustively reading.

### Target definition, cerebral

16. **Aaslid R, Markwalder TM, Nornes H.** Noninvasive transcranial Doppler ultrasound recording of
    flow velocity in basal cerebral arteries. *J Neurosurg* 1982;57:769-774. The origin of transcranial Doppler. Establishes what the measurement is.
17. A current TCD normal values reference, for MCA velocity and pulsatility index by age. Find one
    and tell me which you chose and why. This is deliberately left open, because judging the
    quality of a normative dataset is part of the exercise.

### Validation practice

18. **Walker A, Olsson E, Wranne B, et al.** Accuracy of spectral Doppler flow and tissue velocity
    measurements in ultrasound systems. *Ultrasound Med Biol* 2004;30:127-132.

## Where these citations came from

Items 4 through 12 and 18 were transcribed from the reference lists of the Greaby and Soloukey
papers, and I have since re-checked them against those PDFs. Items 11 and 13 were written from
memory and have now been verified against the publishers. Items 1, 3, 13b, 16 and 19 I have read
directly.

Verify every citation against the actual article before it goes into your written review, and do not
cite a paper you have not opened. You have already caught one error of mine this way, which is
exactly why the habit is worth having.

## The table

You have already built this and it was the right move. Keeping the description here for reference,
one row per published phantom:

| Column | Why |
|---|---|
| Reference | |
| Target vessel | Tells you whether the design goals transfer |
| Drive mechanism | Pump type and how it is controlled |
| Compliance element | Anything that stores volume and gives it back. Is it tunable? |
| Resistance element | Anything that restricts flow and sets how fast pressure decays |
| Vessel construction | Wall-less, tubing, excised vessel, printed |
| Vessel diameter | |
| Velocity achieved | State whether peak or mean, and in what units |
| Pressure achieved | |
| Working fluid | |
| Independent validation | How did they confirm the flow was what they intended? |
| Stated limitations | Authors' own, in their discussion section |

Two columns will teach you the most. **Compliance element** will show you a pattern about where
waveform shape actually comes from. **Independent validation** will show you how many papers do not
really have one, which should inform how you treat your own numbers.

**Compliance and resistance are two different things and it is worth being strict about it.**
Compliance stores volume and releases it. Resistance restricts flow and sets the rate of pressure
decay. They are independent knobs, and the whole design depends on turning them separately. A plenum
or air chamber is compliance. A downstream constriction is resistance. Wall stiffness is compliance,
not resistance, even though the word feels right for a stiff material.

Label rows by author and year rather than by number. It is how the same paper ended up in the table
twice under two different numbers, and that was my fault, not yours.

Fill the table first and write the prose second. The argument is much easier to make once it exists.

## How this might map onto your write-up

Follow whatever structure your course asks for. But the material tends to fall out in roughly this
order:

1. The target, answering questions 1 to 3. What waveform are we trying to produce, and in what
   vessel?
2. The design space, from the table. What approaches exist and what does each buy and cost?
3. The gap, answering question 10. What has not been done, and what is different about our case?
4. Implications for our design. Which approaches are candidates, which are ruled out, and what
   remains open. This section becomes your feature list.
5. What you could not determine from the literature, and how you propose to find out.

Section 5 is not a weakness. It is the most useful part for me, because it says what we need to
measure on the bench.

## Practical notes

- Use a reference manager from day one. Zotero is free. Do not assemble a bibliography by hand in
  April.
- Keep a note of your search terms and databases. If the review concludes nobody has built a
  transcranial pulsatile phantom, that is a strong claim, and being able to say how you searched is
  what makes it credible.
- Split the reading across the team but have at least two people read the Greaby paper, since
  everything else is read in relation to it.
- Flag anything you cannot access and I will try to get it.

## Timing

Your course deadline. If you want feedback before then, send the table whenever it is updated, even
with no prose written. The table is the part I can be most useful about.
