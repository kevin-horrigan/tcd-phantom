# Interface Control Document

**TCD phantom capstone** | Both groups | 2026-09-29

Written in response to a direct question from Group 2 about who owns the vessel. If the two teams
disagree about anything in this file, that disagreement is the problem, not a detail.

## The one-sentence answer

**Group 1 owns the vessel. Group 2 owns the loop, and stops at the connector.**

The tubing Group 2 selects is plumbing. It carries fluid to and from the phantom. It is **not** the
middle cerebral artery. The MCA is a lumen inside Group 1's tissue block, and Group 2's tubing
terminates at a fitting on the outside of that block.

## Why this is confusing, and it is our fault not yours

Two things in the existing documents point the other way.

**The Phase 0 bench rig uses tubing as the vessel.** `GROUP-2_phase0-bench-rig.md` says to anchor a
section of tubing in a water bath and call it the test vessel, and to splice in a narrower segment
to raise velocity. That is correct **for the Phase 0 rig**, which is a cheap disposable instrument
for deriving requirements. It does not carry over to the phantom. Two different objects.

**The literature mostly does it the other way.** Most published flow phantoms, including the ones
in the reading list, run fluid through a tube suspended in a tank. Wall-less construction, where the
lumen is a void in the surrounding material with no tube at all, is the minority approach. It is
what we want here, and it is why the vessel belongs to the team casting the material.

## The boundary, stated precisely

```
  Group 2                                 |  Group 1
  ----------------------------------------+---------------------------------
  reservoir                               |
  pump                                    |
  compliance chamber                      |
  resistance / constriction               |
  pressure instrumentation                |
  connecting tubing                       |
                   -> INLET FITTING ->    |  cast-in connector
                                          |  wall-less MCA lumen in TMM
                                          |  surrounding tissue block
                                          |  skull window
                   <- OUTLET FITTING <-   |  cast-in connector
  return tubing                           |
  gravimetric flow measurement            |
```

Everything left of the fittings is Group 2. Everything right is Group 1. The fittings themselves are
a **joint** deliverable and neither team may choose them alone.

## The coupling, now that Group 1 is going wall-less

Group 1 is planning a wall-less 3 mm lumen. That settles a question but it creates four hard
constraints on Group 2's loop, and all four are easier to design in now than to discover later.

**Match the tubing to the lumen at the interface. 3 mm to 3 mm, no step.** This is the clean answer
to a problem that otherwise has no solution. Flow leaving a sudden contraction needs a straight run
to settle back into a developed profile, and at these velocities that is roughly 80 mm at 55 cm/s
and 155 mm at 110 cm/s. The M1 segment is only 22 to 27 mm long and the whole block is head-sized,
so **there is nowhere inside the phantom to put that straight run.** If the contraction happens at
the inlet fitting, the insonated segment is sitting in a jet. So the step-down happens upstream, in
tubing, where straight length is free: pump tubing at around 4 mm for ripple reasons, then a
transition to 3 mm ID tubing, then at least 150 mm of straight 3 mm tubing, then a flush coupling
into the cast lumen. Flow arrives at the block already developed and the block never has to supply
the entrance length.

**The phantom goes on the pressure side of the pump, never the suction side.** A wall-less lumen has
no wall. The gel holds it open and nothing resists collapse. Put it where a pump can pull it
negative and it will close. Pump discharges into the compliance chamber, through the resistance,
through the block, and out to a reservoir open to atmosphere.

**Group 2 owes a guaranteed pressure ceiling, not just a target.** A peristaltic against a
restriction will cheerfully produce its full 20 psi, roughly 1000 mmHg, which is ten times anything
this phantom needs and far above what a soft gel will hold. One blocked line destroys a block that
took Group 1 days to cast. The ceiling has to be mechanical rather than procedural: a relief path
teed off ahead of the block, either a cracking-pressure relief valve or a simple open standpipe
returning to the reservoir, set below Group 1's measured tear-out pressure.

**Prime slowly and keep gas out.** First fill of a wall-less channel at full flow can blow the
lumen out of the surrounding material. More subtly, gas trapped against a gel wall does not shear
free the way it does in smooth tubing, and you cannot flush a cast lumen aggressively to clear it.
Bubbles are enormous Doppler scatterers and they silently change loop compliance. Block orientation
should let gas sweep through rather than collect.

**One question that belongs to both teams.** The working fluid now sits in direct contact with the
tissue-mimicking material for hours at a time. If Group 1 lands on PVA cryogel, which is a hydrogel,
an aqueous blood-mimicking fluid may exchange water with the block and drift its properties over a
long run. SEBS in mineral oil is hydrophobic and should not swell. Nobody in the reading list
measures this, so treat it as a question to check rather than a settled finding, but it couples
spec 10 to Group 1's material decision and it is worth knowing before either is frozen.

## Jointly owned specifications

Neither team changes any of these without talking to the other first. Fill the values in together
once you have agreed them, and keep the file updated as they settle.

| # | Spec | Owner of the number | Value | Status |
|---|---|---|---|---|
| 1 | MCA lumen diameter | Group 1 proposes, Group 2 confirms reachable | **3 mm**, wall-less | proposed by Group 1 |
| 2 | Lumen length and insonation angle | Group 1 | `____ mm at ____ deg` | open |
| 3 | Vessel depth below window | Group 1 | `____ mm` | open |
| 4 | Required peak systolic velocity | Advisor | `____ cm/s` | open |
| 5 | Required flow at that velocity | Derived from 1 and 4 | **467 mL/min** at 3 mm and 110 cm/s | follows from 1 and 4 |
| 6 | Maximum system pressure | Group 2 proposes, Group 1 must survive it | `____ mmHg` | open, and now safety-critical |
| 7 | Connector type and bonding method | Joint | `____` | **blocking Group 1's mold** |
| 8 | Tubing inner diameter at the fitting | Joint | **3 mm, matched to the lumen** | **blocking Group 1's mold** |
| 9 | Phantom compliance, or the surrogate | Group 1 supplies to Group 2 | `____` | open |
| 10 | Working fluid | Joint | `____` | open |

**Spec 1 drives spec 5 and there is no way around it.** Velocity is flow divided by area. At 3 mm,
roughly 250 mL/min gives 60 cm/s mean and roughly 500 mL/min gives 120 cm/s peak. Change the
diameter and the pump requirement moves as the square. Nobody buys a pump before spec 1 is frozen.

**Spec 6 is bounded by Group 1's burst test.** A wall-less lumen in a soft gel has a pressure at
which it tears out of the surrounding material. Until Group 1 measures that, Group 2's maximum
pressure is unknown. If the burst pressure comes in below what is needed for target velocity, the
architecture changes: the fallback is a thin-walled compliant tube cast into the block, with the
acoustic penalty accepted and measured. **That fallback is still Group 1's vessel.** It does not
transfer ownership to Group 2, it only changes how Group 1 builds it.

**Specs 7 and 8 now gate Group 1's schedule.** There is no way to put a barb or a compression
fitting into a wall-less lumen after the fact. The connector has to be embedded in the block while
it is cast, with enough embedded length and surface area that pressure cannot pull it out. That
means **Group 2 has to hand Group 1 the actual part before Group 1 pours**, not a specification for
it. This is the one item on this list with a hard ordering constraint.

**Spec 9 is the one everyone forgets, and wall-less makes it worse.** The lumen sits in a compliant
gel and the connecting tubing is compliant too, so the phantom is part of Group 2's windkessel
whether anyone planned it or not. Group 2 cannot tune the waveform on a bench loop and then attach
the phantom and expect the same waveform. Either tune with the real head in the loop, or have
Group 1 supply a compliance-matched surrogate to tune against.

With no wall, the lumen is also the softest compliance in the loop, and it is the one element
neither team can adjust. It dilates through each cycle, which means **the 3 mm diameter is a
time-varying number, not a constant.** Any velocity derived from gravimetric flow divided by a fixed
3 mm area carries that error. Qian 2014 shows wall stiffness changing the waveform directly, so this
is a thing to measure rather than assume away. It is also the argument for treating the Doppler and
the pressure trace as the primary records and gravimetric flow as the cross-check on the mean only.

## What each team can decide alone

**Group 1, without asking Group 2:** tissue-mimicking formulation, slab characterization method,
skull window material and thickness set, mold design, casting process, how the lumen is formed.

**Group 2, without asking Group 1:** pump architecture, compliance chamber design, resistance
mechanism, instrumentation, control electronics, tubing material and routing upstream of the
fitting, the Phase 0 rig entirely.

## Keeping it current

This is a working file, not a contract. Update it as numbers settle and commit the change, so both
teams and I are always looking at the same set. If something here turns out to be wrong, change it
and say why.
