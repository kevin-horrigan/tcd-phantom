# Group 2: Literature Review Guide

**TCD phantom capstone, pulsatile flow group** | Advisor: K. Horrigan | Draft 2026-09-11

## What this review is for

Not a book report. The purpose is to produce a **map of the design space** for pulsatile flow
phantoms, so that when you propose a device you can say what has been tried, what it achieved, and
why yours is different. Your feature list should fall out of this review almost mechanically.

A good outcome is a comparison table plus five pages of argument. A bad outcome is twenty paragraphs
each summarizing one paper.

## Questions you must be able to answer at the end

Write these down and answer them explicitly in the review. If a question cannot be answered from the
literature, say so, because that is a finding.

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

1. **Greaby R, Zderic V, Vaezy S.** Pulsatile flow phantom for ultrasound image-guided HIFU
   treatment of vascular injuries. *Ultrasound Med Biol* 2007;33(8):1269-1276.
   The closest precedent to your device, built in Dr. Zderic's prior group. Read it twice. Pay
   particular attention to how waveform shape is controlled, which is not where most people expect.

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

### Blood-mimicking fluid

10. **Ramnarine KV, Nassiri DK, Hoskins PR, Lubbers J.** Validation of a new blood-mimicking fluid
    for use in Doppler flow test objects. *Ultrasound Med Biol* 1998;24:451-459.
11. **IEC 61685**, Ultrasonics: flow measurement systems, flow test object. The standard. Check
    whether the library has access before assuming you can read it.
12. **Lin YH, Shung KK.** Ultrasonic backscattering from porcine whole blood of varying hematocrit
    and shear rate under pulsatile flow. *Ultrasound Med Biol* 1999;25:1151-1158.

### Pump architecture and waveform shaping

13. **Westerhof N, Lankhaar JW, Westerhof BE.** The arterial Windkessel. *Med Biol Eng Comput*
    2009;47:131-141. *(Verify this citation before using it, I am recalling it rather than reading
    it.)* The accessible canonical review of why compliance shapes an arterial waveform. Read this
    before you design anything.
14. **ISO 5840**, cardiovascular implants, prosthetic heart valves. Contains the established bench
    practice for driving physiologic pulsatile flow. You do not need the whole standard, you need
    the test loop section.
15. **Mock circulatory loop literature** for ventricular assist device testing. Search term is
    "mock circulatory loop" or "mock circulation loop." This community has been solving your exact
    problem for decades. Find two or three representative papers rather than exhaustively reading.

### Target definition, cerebral

16. **Aaslid R, Markwalder TM, Nornes H.** Noninvasive transcranial Doppler ultrasound recording of
    flow velocity in basal cerebral arteries. *J Neurosurg* 1982;57:769-774. *(Verify the exact
    citation.)* The origin of transcranial Doppler. Establishes what the measurement is.
17. A current TCD normal values reference, for MCA velocity and pulsatility index by age. Find one
    and tell me which you chose and why. This is deliberately left open, because judging the
    quality of a normative dataset is part of the exercise.

### Validation practice

18. **Walker A, Olsson E, Wranne B, et al.** Accuracy of spectral Doppler flow and tissue velocity
    measurements in ultrasound systems. *Ultrasound Med Biol* 2004;30:127-132.

## Provenance note

Items 4 through 12 and 18 were taken from the reference lists of the Greaby and Soloukey papers, so
the citations are transcribed from a primary source and should be accurate. Items 13 and 16 are from
memory and are marked accordingly. **Verify every citation against the actual article before it goes
into your written review.** Never cite a paper you have not opened. This is a habit worth forming
now, because it is the one that protects you later.

## The deliverable: build a comparison table

The core of your review is a table, one row per published phantom, with at minimum these columns:

| Column | Why |
|---|---|
| Reference | |
| Target vessel | Tells you whether the design goals transfer |
| Drive mechanism | Pump type and how it is controlled |
| Compliance element | If any. What provides it, and is it tunable? |
| Resistance element | If any. How is it adjusted? |
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

Fill the table first. Write the prose second. The argument will be much easier to make once the
table exists.

## What to write

Roughly five pages, plus the table as an appendix.

1. The target, answering questions 1 to 3. What waveform are we trying to produce, and in what
   vessel?
2. The design space, from the table. What approaches exist and what does each buy and cost?
3. The gap, answering question 10. What has not been done, and what is different about our case?
4. Implications for our design. Which approaches are candidates, which are ruled out, and what
   remains open. This section becomes your feature list.
5. What you could not determine from the literature, and how you propose to find out.

Section 5 is not a weakness. It is the part that tells me what to measure on the bench.

## Practical notes

- Use a reference manager from day one. Zotero is free. Do not assemble a bibliography by hand in
  April.
- Track your search terms and databases as you go. If the review says "no one has built a
  transcranial pulsatile phantom," I will ask how you searched, and "we looked" is not an answer.
- Split the reading across the team but have at least two people read the Greaby paper, since
  everything else is read in relation to it.
- Flag anything you cannot access and I will try to get it.

## Timeline

Two to three weeks, as you proposed. Send the table when it is filled, even if the prose is not
written, because the table is what we will talk about.
