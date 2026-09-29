# Group 1: Literature Review Guide

**TCD phantom capstone, materials and vessels group** | Advisor: K. Horrigan | Draft 2026-09-29

Counterpart to `GROUP-2_lit-review-guide.md`. Same format and same deliverable shape, so the two
reviews can sit side by side. The subject matter is different: Group 2 is reviewing flow loops, you
are reviewing **materials and the acoustic path**.

## What this review is for

Not a book report. The purpose is a **map of the materials design space**, so that when you propose
a formulation you can say what has been tried, what it measured, and why yours is different.

A good outcome is a comparison table plus about five pages of argument. A bad outcome is twenty
paragraphs each summarizing one paper.

**A note on numbering.** Cite by author and year, never by list number. Numbers are local to whatever
document you are reading and they drift. `refs/REFERENCES.md` is the canonical list and carries DOIs.
Ask Group 2 how much trouble numbering caused them.

## Questions you must be able to answer

Write these down and answer them explicitly. If a question cannot be answered from the literature,
say so, because that is a finding.

**On the target: what has to be matched**

1. What are the acoustic properties of the three tissues in the transcranial path, scalp, skull and
   brain? For each: speed of sound, attenuation coefficient, density. Give ranges, not single
   numbers, and say which source each came from.
2. Why do published values for skull disagree so much more than values for soft tissue? The answer
   involves what bone actually is.
3. What does the temporal acoustic window look like anatomically? Thickness, how much it varies
   between people, and what fraction of the population has an inadequate one.
4. How much signal is lost passing through the temporal bone at around 2 MHz, and what else happens
   to the beam besides attenuation?

**On existing materials**

5. What tissue-mimicking material families exist for ultrasound, and what are their measured
   properties? Gels, oil-based gels, cryogels, silicones, others.
6. For each family, what composition variable tunes sound speed, and over what range?
7. What has been used as a skull analog, and how well does any of it actually match bone?
8. How are wall-less vessels made, what is the smallest lumen anyone has achieved, and what pressure
   have they been shown to hold?

**On measurement**

9. How is speed of sound measured in a sample? How is attenuation measured? What are the dominant
   error sources in each?
10. How do published studies verify that their material is what they claim? What is the independent
    reference in each case, and how many do not really have one?

**On the gap**

11. Has anyone built and acoustically characterized a tissue-mimicking head phantom **at TCD
    frequencies through a skull analog**? If not, what is different about that case?

Question 11 defines your project the way question 10 defines Group 2's. Spend real effort on it.

## Reading list

Items marked **[Drive]** are in the shared folder. The rest you find yourself, which is part of the
exercise.

### Start here

1. **Soloukey et al. (2024)**, *Ultrasound Med Biol* 50:860. **[Drive]**
   The wall-less casting process and a full tissue-mimicking recipe. Read it twice. Note what they
   measured their material's sound speed to be, and think about what that means for a device that
   reports velocity in absolute units.
2. **Qian et al. (2014)**, *IEEE Trans Biomed Eng* 61(9):2444. **[Drive]**
   PVA cryogel, with sound speed, attenuation and stiffness all measured across freeze-thaw cycles.
   The direct competitor to the Soloukey formulation. Compare them carefully.
3. **Roldan & Kyriacou (2023)**, *Photonics* 10:504. **[Drive]**
   Skull plus brain plus circulation plus controllable intracranial pressure. The closest published
   object to the whole phantom. It is optical rather than acoustic, so ask yourself which parts of
   it transfer and which do not.

### Tissue-mimicking materials

4. **Duck FA.** *Physical Properties of Tissue: A Comprehensive Reference Book.* The standard
   compendium for the target values in question 1. Find it through the library.
5. **Cabrelli et al.**, the SEBS and glycerol-in-oil gel papers. These are the compositional basis
   for the Soloukey recipe and are listed in that paper's reference list. Chase them from there.
   They are where the answer to question 6 lives for that material family.
6. **Greaby, Zderic & Vaezy (2007)**, *Ultrasound Med Biol* 33(8):1269. **[Drive]**
   Group 2's primary paper, and you should read it too, but read it for the material rather than the
   pump. They used agarose and say plainly in their discussion why it was the wrong choice
   acoustically. That admission is one of the most useful sentences in your reading list.

### Skull analogs

7. **Transcranial HIFU phantom literature.** Search terms: "3D printed skull phantom", "skull
   mimicking material ultrasound", "transcranial HIFU phantom". This community has spent years on
   exactly the problem in question 7, and has published what does and does not work. Find three or
   four representative papers rather than reading exhaustively. This is the least mapped part of
   your list and potentially the most valuable.
8. **Roldan & Kyriacou (2023)** again, for how they justified their printed calvaria. Look closely
   at what property they matched it on. It is not the one you need.

### Wall-less vessel construction

9. **Rickey, Picot, Christopher & Fenster (1995)**, *Ultrasound Med Biol* 21:1163. The original
   wall-less vessel phantom.
10. **Ho, Chee, Yiu et al. (2017)**, *IEEE Trans Ultrason Ferroelectr Freq Control* 64:25. Wall-less
    phantoms with tortuous geometry, design principles.
11. **Nikitichev et al. (2016)**, *J Ultrasound Med* 35:1333. 3D printed phantoms with wall-less
    vessels.

### Measurement method

12. **IEC 61685**, ultrasonics flow test object. Check library access before assuming you can read
    it.
13. Find a primary source on the **through-transmission substitution method** for measuring sound
    speed and attenuation. This is the method you will use, and you should cite where it comes from
    rather than learning it from a lab manual.

### Geometry you have to reproduce

14. **Leotta et al. (2024)**, *J Clin Monit Comput*. **[Drive]** Doppler insonation angles and depths
    for the basal cerebral arteries, measured from CT angiography. This gives you the depth and
    angle your vessel has to sit at, from real anatomy rather than a guess.
15. **Aaslid, Markwalder & Nornes (1982)**, *J Neurosurg* 57:769. **[Drive]** The origin of TCD.
    Read it for what the measurement is and where the window is.

### Shared with Group 2

16. **Ramnarine et al. (1998)**, *Ultrasound Med Biol* 24:451. Blood-mimicking fluid. Coordinate with
    Group 2 rather than both reviewing it.

## The deliverable: build a comparison table

One row per material or phantom, with at least these columns:

| Column | Why |
|---|---|
| Reference | Author and year |
| Material family | Gel, oil gel, cryogel, silicone, printed polymer |
| Composition | Actual proportions if given |
| Speed of sound | With units, and say whether measured or quoted |
| Attenuation | **With the frequency it was measured at.** Useless without it |
| Density | Needed for impedance |
| What tunes it | Which variable moves sound speed, and over what range |
| Stability | Shelf life, storage conditions, any reported degradation |
| Vessel method | Wall-less, tube, excised, printed, or not applicable |
| Measurement method | How they determined the acoustic properties |
| Independent validation | Did they check against anything, or just report? |
| Stated limitations | The authors' own, from the discussion section |

Two columns will teach you the most. **What tunes it** is the answer to your design problem. **Stated
limitations** is where authors admit what their material cannot do, and the Greaby agarose sentence
is the model for what to look for.

Fill the table first, write the prose second.

## What to write

About five pages plus the table as an appendix.

1. The target, from questions 1 to 4. What are we trying to match, and how well is it even known?
2. The materials design space, from your table. What exists, what does each buy and cost?
3. The skull problem, from question 7. Treat this separately because it is the hardest part.
4. The gap, from question 11.
5. Implications for our design. Candidate formulations, what is ruled out, what stays open. This
   becomes your specification.
6. What you could not determine from the literature, and how you propose to measure it.

Section 6 is not a weakness. It tells me what to put on the bench.

## Coordinate with Group 2

Two things are jointly owned and you should not decide them alone. The vessel diameter sets their
pump requirement, and your maximum survivable pressure bounds what they can drive. Both are in
`capstone/INTERFACE-CONTROL-DOCUMENT.md`, which both teams need to fill in and sign.

Read that document before you finish this review. It will change what you conclude in section 5.

## Timeline

Two to three weeks. Send me the table as soon as it is filled, even if the prose is not written. The
table is what we will talk about.
