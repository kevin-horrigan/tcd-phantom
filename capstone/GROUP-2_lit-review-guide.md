# Group 2: Reading Notes for the Literature Review

**TCD phantom capstone, pulsatile flow group** | K. Horrigan | Revised 2026-09-29

Your course sets the requirements for this assignment, not me. What follows is what I can usefully
add: which papers are worth your time, what to pull out of them, and the things that are easy to get
wrong in this corner of the literature. Take what helps and ignore the rest.

Revised after seeing your first table. A few notes below come directly from that, and Group 1 now
has a companion set covering materials and the acoustic path.

## The table

You have already built this and it was the right move. Keeping the description here for reference,
with two corrections that came out of the first version.

| Column | What goes in it |
|---|---|
| Reference | Author and year |
| Target vessel | Tells you whether the design goals transfer |
| Drive mechanism | Pump type and how it is controlled |
| Compliance element | Anything that stores volume and gives it back. Is it tunable? |
| Resistance element | Anything that restricts flow and sets how fast pressure decays |
| Vessel construction | Wall-less, tubing, excised vessel, printed |
| Vessel diameter | |
| Velocity achieved | Say whether peak or mean, and the units |
| Pressure achieved | |
| Working fluid | |
| Independent validation | How did they confirm the flow was what they intended? |
| Stated limitations | The authors' own, from the discussion |

**Compliance and resistance are two different things and it is worth being strict about it.**
Compliance stores volume and releases it. Resistance restricts flow and sets the rate of pressure
decay. They are independent knobs, and your whole design depends on being able to turn them
separately. A plenum or air chamber is compliance. A downstream constriction is resistance. Wall
stiffness is compliance, not resistance, even though the word "resistance" feels right for a stiff
material.

**Label rows by author and year, not by number.** Two documents in this repo had separately numbered
reference lists that drifted apart, which was my fault, and it is how the same paper ended up in
your table twice under two different numbers.

Two columns tend to teach the most. **Compliance element** reveals a pattern about where waveform
shape actually comes from. **Independent validation** reveals how many papers do not really have
one, which is worth knowing before you decide how much to trust your own numbers.

## Things worth being able to answer

Not a checklist to submit. These are what the review is really about, and what I would most enjoy
talking through.

**What are we trying to produce?**

- Normal MCA velocities, peak systolic, end diastolic, mean, and a normal pulsatility index. Say
  which population each number came from, because they do not all come from the same one.
- How a cerebral velocity waveform differs in shape from a carotid or peripheral one, and why. The
  answer is about downstream resistance.
- What heart rate range to build for. 40 to 180 is a sensible first-pass scope. Worth saying in the
  review that it is a scope decision rather than a physiological limit.

**What has been tried?**

- Which drive mechanisms have been used on a bench, and what is the failure mode of each? The
  failure modes are the useful half.
- How is waveform shape controlled? Imposed by the pump, or produced by something downstream of it?
- What velocity and pressure ranges have published phantoms actually reached?
- How do published designs build the vessel, and what are the acoustic consequences?

**Fluids and validation**

- What does a blood-mimicking fluid have to do, and which properties matter for which reason?
- How do published studies verify their phantom produced the flow they intended, and what is the
  independent reference in each case?

**What has nobody done?**

- Has anyone built a pulsatile phantom for **transcranial** Doppler specifically? If not, what is
  different about that case?

That last one is the question your project exists to answer, so it deserves more than a sentence.
The difference is a combination: heavy attenuation through bone, around 2 MHz rather than 5 to 10,
range-gated with no image to steer by, and a small deep vessel.

## Where to start

**A note on numbering.** Numbers below are local to this document and do not match
`refs/REFERENCES.md`, which is the canonical list and carries the DOIs. If they disagree,
`REFERENCES.md` wins. Better still, cite by author and year.

### The three to read first

1. **Greaby R, Zderic V, Vaezy S (2007).** Pulsatile flow phantom for ultrasound image-guided HIFU
   treatment of vascular injuries. *Ultrasound Med Biol* 33(8):1269-1276.
   The closest precedent to your device, built in Dr. Zderic's prior group. Worth reading twice, and
   worth getting the velocity range right: it reaches **10 to 240 cm/s**, which is the only paper on
   your list that covers the range we need. Pay attention to how waveform shape is controlled, which
   is not where most people expect.

2. **Greaby R (2005).** MS thesis, Bioengineering, University of Washington.
   The fuller build documentation behind the paper. Worth requesting through interlibrary loan early
   since it may take a while to arrive.

3. **Soloukey S, et al. (2024).** Patient-specific vascular flow phantom for MRI- and Doppler
   ultrasound imaging. *Ultrasound Med Biol* 50:860-868.
   Group 1's primary reference. Read it so you know what you are plumbing into. Their flow regime is
   nowhere near yours, and why that is matters.

### Flow phantom design

4. **Rickey DW, Picot PA, Christopher DA, Fenster A (1995).** A wall-less vessel phantom for Doppler
   ultrasound studies. *Ultrasound Med Biol* 21:1163-1176.
5. **Peopping TL, Nikolov HN, Rankin RN, et al. (2002).** An in vitro system for Doppler ultrasound
   flow studies in the stenosed carotid artery bifurcation. *Ultrasound Med Biol* 28:495-506.
6. **Law YF, Johnston KW, Routh HF, Cobbold RSC (1989).** On the design and evaluation of a steady
   flow model for Doppler ultrasound studies. *Ultrasound Med Biol* 15:505-516.
7. **Dabrowski W, Dunmore-Buyze J, Rankin RN, Holdsworth DW, Fenster A (2001).** A real vessel
   phantom for flow imaging: 3-D Doppler ultrasound of steady flow. *Ultrasound Med Biol* 27:135-141.
8. **Frayne R, Gowman LM, Rickey DW, et al. (1993).** A geometrically accurate vascular phantom for
   comparative studies of x-ray, ultrasound, and magnetic resonance vascular imaging. *Med Phys*
   20:415-425.
9. **Ho CK, Chee AJY, Yiu BYS, Tsang ACO, Chow KW, Yu ACH (2017).** Wall-less flow phantoms with
   tortuous vascular geometries. *IEEE Trans Ultrason Ferroelectr Freq Control* 64:25-38.
10. **Rominger MB, et al.** Easy pulsatile phantom for teaching and validation of flow measurements
    in ultrasound. Thieme, doi:10.1055/s-0042-106396.
    The constant-flow pump plus downstream modulator design. Note that the reference pump defines
    mean flow structurally, which is a different answer to the ground-truth problem than measuring
    it afterward.

### Blood-mimicking fluid

11. **Ramnarine KV, Nassiri DK, Hoskins PR, Lubbers J (1998).** Validation of a new blood-mimicking
    fluid for use in Doppler flow test objects. *Ultrasound Med Biol* 24:451-459.
    Note: Greaby's printed reference list misspells the last author as "Lubvers." It is Lubbers.
12. **IEC 61685:2001**, *Ultrasonics: flow measurement systems, flow test object.* 36 pages.
    **Worth knowing its limits: it specifies a test object carrying steady flow.** So it governs the
    tissue-mimicking material and blood-mimicking fluid specifications, and it does **not** govern
    waveform for a pulsatile phantom. Do not lean on it for something it does not cover. Check
    library access before assuming you can read it.
13. **Lin YH, Shung KK (1999).** Ultrasonic backscattering from porcine whole blood of varying
    hematocrit and shear rate under pulsatile flow. *Ultrasound Med Biol* 25:1151-1158.

### Pump architecture and waveform shaping

14. **Westerhof N, Lankhaar JW, Westerhof BE (2009).** The arterial Windkessel. *Med Biol Eng
    Comput* 47:131-141.
    The accessible review of why compliance shapes an arterial waveform. Read this before designing
    anything.
15. **Stergiopulos N, Westerhof BE, Westerhof N (1999).** Total arterial inertance as the fourth
    element of the windkessel model. *Am J Physiol Heart Circ Physiol* 276(1):H81-H88.
    A different, earlier paper sharing two authors with the one above, and the copy in the Drive
    folder. The 2009 review explains the concept; this one adds inertance as a fourth element and
    gives healthy human parameter values in Table 2. Read 2009 first, then this when you need
    numbers. Both belong.
16. **ISO 5840**, cardiovascular implants, prosthetic heart valves. Established bench practice for
    driving physiologic pulsatile flow. You want the test loop section, not the whole standard.
17. **Mock circulatory loop literature** for ventricular assist device testing. Search "mock
    circulatory loop" or "mock circulation loop." That community has been solving your problem for
    decades. Two or three representative papers is plenty.

### Target definition, cerebral

18. **Aaslid R, Markwalder TM, Nornes H (1982).** Noninvasive transcranial Doppler ultrasound
    recording of flow velocity in basal cerebral arteries. *J Neurosurg* 57:769-774.
    The origin of transcranial Doppler.
19. A current TCD normal values reference for MCA velocity and pulsatility index by age. Left open
    deliberately, because judging the quality of a normative dataset is part of the exercise. Tell
    me which you picked and why.

### Validation practice

20. **Walker A, Olsson E, Wranne B, et al. (2004).** Accuracy of spectral Doppler flow and tissue
    velocity measurements in ultrasound systems. *Ultrasound Med Biol* 30:127-132.

## Where these citations came from

Items 4 through 9, 11, 13 and 20 were transcribed from the reference lists of the Greaby and
Soloukey papers, and I have since re-checked them against those PDFs. Items 12 and 14 were written
from memory and have now been verified against the publishers. Items 1, 3, 10, 15 and 18 I have read
directly.

Verify every citation against the actual article before it goes into your written review, and do not
cite a paper you have not opened. You have already caught one error of mine this way, which is
exactly why the habit is worth having.

## How this might map onto your write-up

Follow whatever structure your course asks for. But the material tends to fall out in roughly this
order:

1. The target. What waveform are we trying to produce, in what vessel?
2. The design space, straight from your table
3. What nobody has done
4. What this implies for our design: candidates, what is ruled out, what stays open
5. What the literature could not tell you

Section 5 is not a weakness. It is the most useful part for me, because it says what we need to
measure on the bench.

## A few practical things

- A reference manager from day one is worth it. Zotero is free, and assembling a bibliography by
  hand in April is not fun.
- Keep a note of your search terms and databases. If the review concludes nobody has built a
  transcranial pulsatile phantom, that is a strong claim, and being able to say how you searched is
  what makes it credible.
- Split the reading, but have at least two people read Greaby, since everything else gets read in
  relation to it.
- Tell me about anything you cannot access and I will try to get it.

## One coordination item

`capstone/INTERFACE-CONTROL-DOCUMENT.md` settles who owns what between the two groups, including the
vessel question you raised. Worth reading before you finish section 4, since it affects what you can
conclude there.

## Timing

Your course deadline. If you want feedback before then, send the table whenever it is updated, even
with no prose written. The table is the part I can be most useful about.
