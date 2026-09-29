# Group 1: Reading Notes for the Literature Review

**TCD phantom capstone, materials and vessels group** | K. Horrigan | 2026-09-29

Your course sets the requirements for this assignment, not me. What follows is what I can usefully
add: which papers are worth your time, what to pull out of them, and the handful of things that are
easy to get wrong in this particular corner of the literature. Take what helps and ignore the rest.

Group 2 has a companion set of notes. They are reading flow loops and pumps. You are reading
materials and the acoustic path.

## A suggestion that will save you time

Before writing anything, put the papers in a table, one row per material or phantom. Everyone who
has done this tells me the same thing afterward: the prose gets much easier once the table exists,
because the comparisons write themselves.

Columns worth having:

| Column | Why it earns its place |
|---|---|
| Reference | Author and year |
| Material family | Gel, oil gel, cryogel, silicone, printed polymer |
| Composition | Actual proportions where given |
| Speed of sound | With units, and note whether they measured it or quoted someone else |
| Attenuation | **With the frequency it was measured at.** See below |
| Density | You need it for impedance |
| What tunes it | Which variable moves the properties, and over what range |
| Stability | Shelf life, storage, any reported degradation |
| Vessel method | Wall-less, tube, excised, printed, not applicable |
| How measured | The method they used to get the acoustic numbers |
| Independent check | Did they verify against anything, or only report? |
| Stated limitations | The authors' own words, from the discussion |

Two of those columns tend to be the most useful. **What tunes it** is effectively the answer to your
design problem. **Stated limitations** is where authors admit what their material cannot do, and it
is usually the most honest paragraph in any paper.

Group 2 built theirs in a spreadsheet and it worked well. Ask them for the file if it helps.

## Things worth being able to answer

Not a checklist to submit. These are the questions I think the review is really about, and the ones
I would most enjoy talking through with you.

**What are we trying to match?**

- What are the acoustic properties of the three tissues in the path, scalp, skull and brain? Speed
  of sound, attenuation, density. Ranges rather than single numbers, with sources.
- Why do published skull values scatter so much more than soft tissue values? The answer is about
  what bone actually is, and it is worth understanding rather than just noting.
- What does the temporal window look like anatomically, how much does it vary between people, and
  what fraction of the population has an inadequate one? That last number is more interesting than
  it sounds.
- How much signal is lost through the temporal bone around 2 MHz, and what happens to the beam
  besides attenuation?

**What has been tried?**

- Which tissue-mimicking material families exist, and what did they measure?
- For each family, what composition variable moves the speed of sound, and how far?
- What has been used as a skull analog, and how well does any of it really match bone?
- How are wall-less vessels made? What is the smallest lumen anyone has managed, and what pressure
  has one been shown to hold?

**How do you know a material is what you say it is?**

- How is speed of sound measured? How is attenuation measured? Where does the error come from?
- How do published studies verify their material? You may notice that a fair number do not really
  verify it at all, which is worth saying out loud.

**What has nobody done?**

- Has anyone built and acoustically characterized a tissue-mimicking head phantom at TCD frequencies
  through a skull analog?

That last one is the question your project exists to answer, so it is worth more than a sentence.

## Where to start

Items marked **[Drive]** should be in the shared folder. If one is missing, tell me rather than
assuming you lost it.

**The three to read first**

- **Soloukey et al. (2024)**, *Ultrasound Med Biol* 50:860. **[Drive]** The wall-less casting process
  and a complete material recipe. Worth reading twice. Note what they measured their material's
  speed of sound to be, and think about what that implies for a device reporting velocity in
  absolute units.
- **Qian et al. (2014)**, *IEEE Trans Biomed Eng* 61(9):2444. **[Drive]** PVA cryogel, with speed of
  sound, attenuation and stiffness all measured across freeze-thaw cycles. The direct competitor to
  the Soloukey formulation, and the comparison between the two is most of your section 2.
- **Roldan & Kyriacou (2023)**, *Photonics* 10:504. **[Drive]** Skull, brain, circulation and
  controllable intracranial pressure. The closest published thing to the whole phantom. It is
  optical rather than acoustic, so the interesting question is which parts transfer.

**Materials**

- **Duck FA (1990).** *Physical Properties of Tissue: A Comprehensive Reference Book.* Academic
  Press. The standard compendium, 138 tables covering acoustic, thermal, mechanical and other
  properties for soft tissue and bone. This is where the target numbers come from. Long out of
  print, though IPEM reissued it print-on-demand (ISBN 1903613507), and the library may have the
  original. Archive.org has a lending copy.
- **Cabrelli et al.**, the SEBS and glycerol-in-oil gel papers, three of them, all listed in
  Soloukey's reference list. These are the compositional basis for that recipe and are where the
  tuning answer lives for that material family.
- **Greaby, Zderic & Vaezy (2007)**, *Ultrasound Med Biol* 33(8):1269. **[Drive]** Group 2's main
  paper, but read it for the material rather than the pump. They used agarose and say plainly in the
  discussion why it was the wrong acoustic choice. That admission is one of the more useful
  sentences you will read.

**Skull analogs**

This is the least mapped part of your reading and probably where you can add the most. Search the
transcranial HIFU phantom literature: try "3D printed skull phantom", "skull mimicking material
ultrasound", "transcranial HIFU phantom". That community has worked on exactly this problem for
years. Three or four representative papers is plenty.

Also look again at how Roldan justified their printed calvaria, and notice which property they
matched it on. It is not the one you need.

**Wall-less vessels**

- **Rickey, Picot, Christopher & Fenster (1995)**, *Ultrasound Med Biol* 21:1163. The original
  wall-less vessel phantom.
- **Ho, Chee, Yiu, Tsang, Chow & Yu (2017)**, *IEEE Trans Ultrason Ferroelectr Freq Control*
  64:25-38. Wall-less phantoms with tortuous geometry, design principles.
- **Nikitichev, Barburas, McPherson, Mari, West & Desjardins (2016)**, *J Ultrasound Med*
  35:1333-1339. 3D printed phantoms with wall-less vessels.

**Method and standards**

- **IEC 61685:2001**, *Ultrasonics: Flow measurement systems, flow test object.* 36 pages. Worth
  knowing about, and worth knowing its limits: it specifies a test object carrying **steady** flow,
  so it does not directly govern a pulsatile phantom. Useful for the tissue-mimicking material and
  blood-mimicking fluid specifications, not for waveform. Check library access before assuming you
  can read it.
- A primary source on the **through-transmission substitution method**, since that is likely the
  technique you will use for sound speed and attenuation. Worth citing where it comes from rather
  than picking it up from a lab handout.

**Geometry you have to reproduce**

- **Leotta et al. (2024)**, *J Clin Monit Comput*. **[Drive]** Doppler angles and depths for the
  basal cerebral arteries, measured from CT angiography. Real anatomy instead of a guess.
- **Aaslid, Markwalder & Nornes (1982)**, *J Neurosurg* 57:769. **[Drive]** The origin of TCD. Read
  it for what the measurement is and where the window sits.

**Shared with Group 2**

- **Ramnarine et al. (1998)**, *Ultrasound Med Biol* 24:451. Blood-mimicking fluid. Coordinate
  rather than both doing it.

## Three things that are easy to get wrong

**Always record attenuation with its frequency.** An attenuation number alone is not usable, and we
care about roughly 2 MHz, which is lower than most convenient lab equipment runs at. If a paper
reports at 5 or 10 MHz, note it, because it does not transfer directly.

**Cite by author and year, not by list number.** Two documents in the repo had independently
numbered reference lists that drifted apart, which was my fault, and Group 2 ended up entering the
same paper twice under two different numbers before anyone noticed. Author and year travel between
documents; numbers do not.

**No printable homogeneous material matches real bone well.** If you conclude that, you are probably
right, and it is a finding rather than a failure. Say it clearly and show the numbers.

## How this might map onto your write-up

Your course may want a different structure, in which case follow theirs. But the material tends to
fall out in roughly this order:

1. What we are trying to match, and how well it is even known
2. The materials design space, straight from your table
3. The skull problem, separately, because it is the hardest part
4. What nobody has done
5. What this implies for our design: candidates, what is ruled out, what stays open
6. What the literature could not tell you

Section 6 is not a weakness. It is the most useful section for me, because it tells me what we need
to measure on the bench.

## One coordination item

`capstone/INTERFACE-CONTROL-DOCUMENT.md` settles who owns what between the two groups. Short version:
your group owns the vessel, and Group 2's tubing stops at a fitting on the outside of your block.
There was real confusion about that, traceable to something ambiguous I wrote.

Worth reading before you finish section 5, because it affects what you can conclude there.

## Timing

Whatever your course deadline is. If you want feedback before then, send me the table as soon as it
is filled, even with no prose written. The table is the part I can be most useful about.
