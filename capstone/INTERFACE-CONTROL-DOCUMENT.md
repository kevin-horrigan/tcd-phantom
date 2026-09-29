# Interface Control Document

**TCD phantom capstone** | Both groups | Draft 2026-09-29, unsigned

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

## Jointly owned specifications

Neither team changes any of these without the other agreeing in writing. Fill in the values and both
teams sign.

| # | Spec | Owner of the number | Value | Status |
|---|---|---|---|---|
| 1 | MCA lumen diameter | Group 1 proposes, Group 2 confirms reachable | `____ mm` | open |
| 2 | Lumen length and insonation angle | Group 1 | `____ mm at ____ deg` | open |
| 3 | Vessel depth below window | Group 1 | `____ mm` | open |
| 4 | Required peak systolic velocity | Advisor | `____ cm/s` | open |
| 5 | Required flow at that velocity | Derived from 1 and 4 | `____ mL/min` | open |
| 6 | Maximum system pressure | Group 2 proposes, Group 1 must survive it | `____ mmHg` | open |
| 7 | Connector type and bonding method | Joint | `____` | open |
| 8 | Tubing inner diameter at the fitting | Joint | `____ mm` | open |
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

**Spec 9 is the one everyone forgets.** The lumen sits in a compliant gel and the connecting tubing
is compliant too, so the phantom is part of Group 2's windkessel whether anyone planned it or not.
Group 2 cannot tune the waveform on a bench loop and then attach the phantom and expect the same
waveform. Either tune with the real head in the loop, or have Group 1 supply a compliance-matched
surrogate to tune against.

## What each team can decide alone

**Group 1, without asking Group 2:** tissue-mimicking formulation, slab characterization method,
skull window material and thickness set, mold design, casting process, how the lumen is formed.

**Group 2, without asking Group 1:** pump architecture, compliance chamber design, resistance
mechanism, instrumentation, control electronics, tubing material and routing upstream of the
fitting, the Phase 0 rig entirely.

## Signature

This document is not in force until both teams have signed it. Print it, sign it, scan it, commit
the scan.

| Team | Name | Date |
|---|---|---|
| Group 1 | | |
| Group 2 | | |
| Advisor | | |
