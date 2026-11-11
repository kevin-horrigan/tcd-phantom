# -*- coding: utf-8 -*-
"""Everything the waveform generator needs, and what is already on the bench.

    python bom.py

SCOPE. This is the pulse source only: the thing that turns a step train into
0.5 mL of fluid displacement per beat. It is not the flow loop. The reservoir,
the tubing, the compliance plenum, the downstream constriction and the phantom
belong to Group 2's loop list. Two loop items appear here anyway, under FLUID
INTERFACE, because the generator does not work without them and because one of
them is the single part most likely to be bought wrong.

Lengths come from syringe_drive at run time, so the screw and rod lengths here
cannot drift from the frame that was actually printed.

Status column:
    HAVE   confirmed present and, where it matters, confirmed working
    CHECK  believed present, worth laying hands on before ordering
    BUY    not here
"""
import syringe_drive as S

ROD_L = S.X_RIB_BACK + S.LOCK_T   # through the frame AND the lock
SCREW_L = S.SCREW_SPAN + 12.0

# group, qty, item, spec, status, note
BOM = [
    ("PRINTED", 1, "frame", "%.0f x %.0f x %.0f mm, 162 mL"
     % (182, 81, 59), "BUY", "plate 1, no measurement needed"),
    ("PRINTED", 1, "saddle_cap", "clamps the collars", "BUY", "plate 1"),
    ("PRINTED", 2, "collar", "%.1f mm OD, bore to the barrel" % S.SADDLE_BORE,
     "BUY", "plate 2, needs the barrel OD"),
    ("PRINTED", 1, "carriage", "LM8UU bores + T8 nut pocket", "BUY",
     "plate 2, needs the three plunger numbers"),

    ("MOTION", 1, "T8x8 lead screw", "8 mm lead, cut to %.0f mm" % SCREW_L,
     "BUY", "8 mm PER REV, not 2 mm. T8x2 is far more common and wrong here"),
    ("MOTION", 1, "anti-backlash T8 nut", "spring preloaded, flanged",
     "BUY", "a plain nut gives 0.2 mm lost motion, 2 to 5% of the beat"),
    ("PRINTED", 2, "rod_lock", "4.7 mL each, ~12 min", "PRINT",
     "Kevin's lockable collar, in the form the frame has room for. A plain "
     "collar stops ONE direction, and there is nowhere for the second: the "
     "carriage sweeps to within 4 mm of the rib. This one clamps the rod "
     "with an M3 AND bolts to the rib with two more, so the rod is fixed to "
     "the frame and cannot walk either way"),
    ("FASTENERS", 4, "M3 x 12 socket cap", "rod lock and rod stop pinch", "BUY",
     "one per rod lock and one per rod stop, pulls the C shut on the rod"),
    ("PRINTED", 2, "rod_stop", "3.2 mL each, ~9 min", "PRINT",
     "The forward stop, inboard of the rib. The rib lock alone takes travel "
     "toward the motor in compression and travel toward the syringe in "
     "thread pullout, and the carriage pushing the plunger nudges the rods "
     "the second way. This collar turns that into compression on the rib's "
     "front face. No screws into the frame: it does not need any. Goes on "
     "DURING rod insertion, the bore is closed"),
    ("FASTENERS", 4, "M3 x %.0f thread-forming" % S.LOCK_SCREW_L,
     "rod lock into the rib", "BUY",
     "two per rod lock, and the length is NOT free. 12 mm of the screw is "
     "spent crossing the lock before it reaches the rib, so an M3 x 16 "
     "leaves only 4 mm of thread in the rib and an M3 x 20 leaves 8. The "
     "rib is 9 thick, so 20 is the longest that does not come out the far "
     "side into the carriage sweep. This is the one direction the lock "
     "cannot take in compression, so it is the one to spend 4 mm on"),
    ("MOTION", 2, "8 mm smooth rod", "hardened, %.0f mm" % ROD_L, "BUY",
     "buy 300 mm and cut both from it (each now passes through the rod lock on the rib back face, hence 134 and not 122). NOT with a hacksaw: the case is "
     "60 HRC against a 64 HRC blade and it will not cut, which reads as "
     "having been sent the wrong rod. Abrasive chop saw, angle grinder or "
     "rotary tool. CHAMFER BOTH ENDS afterwards or a square burr scores the "
     "LM8UU ball tracks going in. rod_lock() retains them, so the press "
     "fit no longer has to hold on its own. See rods.py"),
    ("MOTION", 2, "LM8UU linear bearing", "15 mm OD x 24 mm", "BUY", ""),
    ("MOTION", 1, "608 bearing", "8 x 22 x 7, skate bearing", "BUY",
     "takes the screw's far end in the rib"),
    ("MOTION", 1, "flexible coupler", "5 mm to 8 mm, 19 mm OD x 25 mm",
     "BUY", "5 mm is the pancake shaft, 8 mm is the screw"),

    ("MOTOR", 1, "17HE08-1004S pancake", "NEMA 17, 23 mm, 17 Ncm, 1.0 A",
     "HAVE", "this is the one that runs the piston"),
    ("MOTOR", 1, "17HS19-2004S1", "NEMA 17, 48 mm, 59 Ncm, 2.0 A",
     "HAVE", "bought, but too slow at 12 V. Spare"),

    ("ELECTRONICS", 1, "Raspberry Pi Pico 2", "RP2350, MicroPython 1.29.0",
     "HAVE", "flashed and verified, PIO step train measured to 0.03%"),
    ("ELECTRONICS", 1, "breakout board", "for the Pico", "HAVE", ""),
    ("ELECTRONICS", 1, "BTT TMC2209 V1.3", "0.11 ohm sense, VREF 0.53 V",
     "HAVE", "wired and turning. Pot still at factory 1.2 V"),
    ("ELECTRONICS", 1, "12 V supply", "2 A or better, 5.5 x 2.5 barrel",
     "HAVE", "the motor ran off it"),
    ("ELECTRONICS", 1, "100 uF electrolytic", "25 V or better, low ESR",
     "CHECK", "across VM and GND AT the driver. Protects it on motor transients"),
    ("ELECTRONICS", 1, "barrel jack pigtail", "5.5 x 2.5 socket to flying leads",
     "CHECK", "only if the brick is not already pigtailed"),
    ("ELECTRONICS", 7, "jumper wires", "female to female, 100 mm", "CHECK",
     "5 signal plus 2 power. Motor and VM want thicker wire"),

    ("SYRINGE", 100, "BH Supplies BH5LL", "5 mL luer lock, no needle, sterile",
     "HAVE", "bought 2026-11-09. Halved the screw speed, 446 -> 230 rpm, "
             "which retired most of the motor problem"),

    ("FLUID INTERFACE", 1, "check valve", "Qosina 91050, 0.075 psi, 1/4 in barb",
     "DROP", "DO NOT FIT. With a check valve, an EMPTY plenum and R2 shut, "
             "the piston has nowhere to put its half millilitre and goes "
             "straight to its 19 psi stall, 984 mmHg at a cast gel. With R1 "
             "instead, the same fault peaks at 3.2 psi and the relief never "
             "opens, because R1 is a hole and the fluid just goes back to "
             "the jar. An empty plenum with R2 closed is a bring-up "
             "afternoon, not an exotic fault. Kept on the list because the "
             "part number history is worth not relearning: this line used "
             "to read '9105x', which is a "
            "family wildcard and not a part number, so it found nothing. The "
            "four barbed parts are 91050 (1/4 in), 91054 (3/16), 91053 (1/8) "
            "and 91055 (3/8). Qosina needs a free account to see pricing. The "
            "luer-to-luer part cracks at 0.433 psi and stops the loop dead"),
    ("FLUID INTERFACE", 1, "tee", "barbed, 1/4 in ID", "BUY",
     "piston tees in between the check valve and the phantom"),
    ("FLUID INTERFACE", 2, "barb to female luer adapter", "1/4 in barb",
     "BUY", "the syringe tip is luer, the loop is barbed"),
    ("FLUID INTERFACE", 1, "reducing barb, 1/4 to 1/8 in", "the 3 mm transition",
     "BUY", "1/8 in is 3.18 mm, so a 1/8 in barb IS the 3 mm barb. There is "
            "no such thing as a 3 mm barb and looking for one wastes an hour"),
    ("FLUID INTERFACE", 2.0, "braided PVC tubing, 1/4 in ID", "metres, stiff",
     "BUY", "NOT silicone. 150 mm of 1/4 in silicone between the tee and the "
            "phantom stores 13.5 percent of the stroke in its own wall. The "
            "same run in braided PVC stores 0.40 percent. See feed_tubing.py"),
    ("FLUID INTERFACE", 0.5, "tubing, 3 mm ID", "metres, stiff walled",
     "BUY", "the 150 mm settling run into the block, plus spares. 1/8 in ID "
            "at 3.18 mm is the commodity equivalent and fits a 1/8 in barb"),

    ("FLUID INTERFACE", 1, "R2, the adjustable resistance",
     "190 mm of the kit's 1/4 in tube + a screw clamp", "BUY",
     "THE CLAMP IS THE ONLY THING TO BUY. Hoffman screw compressor clamp, "
     "lab supply, a few dollars. 190 mm of the 4 mm tube reads 51 mm of "
     "head wide open, which is the bottom of the sweep, and the clamp takes "
     "it up from there. Clamping the 6.35 mm trunk instead starts at 8 mm, "
     "six times further from target, so the pinch is harder and it creeps "
     "more. A needle valve also works IF its full-open Cv is near 0.3: the "
     "test without a datasheet is that wide open it should cost 30 to 50 mm "
     "of head at 250 mL/min. A ball valve gives 3 mm wide open, so every "
     "setting lives in the first few degrees of handle. See head_budget.py"),

    ("FLUID INTERFACE", 1, "RO push-fit kit, 1/4 + 3/8 in",
     "25 fittings, 30 ft of each tube, NSF, about 36 USD", "BUY",
     "covers the whole loop in one box, and the two reels do two different "
     "jobs. The 3/8 in OD tube is a 6.35 mm BORE and is the trunk. The "
     "1/4 in OD tube is a 4 mm bore and is R1, about 2.9 m of it coiled. "
     "Do NOT run the trunk in the 1/4 in: at 4 mm the plumbing eats more "
     "than the jar provides and R2 goes negative. Push-fit sizes are "
     "OUTSIDE diameter, barbed tubing is INSIDE, which is the whole trap. "
     "The ball valves in the kit are isolation valves, not throttles, so "
     "R2 is still a screw clamp or needle valve"),

    ("FLUID INTERFACE", 1, "60 mL syringe, for the PLENUM",
     "stands tip down and OPEN to the loop, plunger CLAMPED", "HAVE",
     "rigid and clear and graduated, so the air volume is both the setting "
     "and the reading. Its own wall is 0.4 percent of the air's compliance, "
     "which is the margin you want. Build for 10 to 50 mL of trapped air "
     "and start at 20. A soft bulb would be 265 percent and the knob would "
     "stop working. The luer tip meets the barb-to-luer adapter already "
     "listed. At 1.8 psi the plunger sees about 7 N, the same order as its "
     "own breakout friction, so clamp the rod or it creeps. Nothing is "
     "plugged: the tip stays open, fluid rises into the barrel, air sits "
     "above it, and clamping stops the plunger SLIDING. Air dissolves into "
     "the fluid over hours, so re-read the graduations each sweep point. "
     "See plenum.py. BOUGHT 2026-11-10. Still to measure: barrel bore, "
     "plunger cross for the lock, usable stroke. None of them change the "
     "compliance, which depends on air volume alone"),

    ("INSTRUMENTS", 2, "the single-inlet modules already on the shelf",
     "gauge, check rate / range / media before trusting", "CHECK",
     "single inlet means GAUGE, which is the right reference here, and "
     "0-40 kPa is the right range. The bottleneck is the ADC: an HX710 at "
     "40 SPS puts 4 samples across a 100 ms upstroke. Good enough for PI, "
     "which is peak, trough and mean, and not good enough for the shape of "
     "systole. Use these for bring-up and the compliance sweep"),
    ("INSTRUMENTS", 2, "MPX5050GP", "0-50 kPa gauge, single port, ~1 ms",
     "HAVE",
     "P1 and P2, and the manometer does NOT replace them: it is throttled "
     "to 0.05 Hz so it cannot follow the pulse, which is what makes it a "
     "clean mean. P2 measures the waveform reaching the block, which is the "
     "deliverable. P1 is the only instrument that can tell a bad P2 from a "
     "bad PISTON, because the step counter is open loop and reports what "
     "was commanded, not what the fluid did. ALREADY SPECIFIED in "
     "GROUP-2_phase0-bench-rig.md with the "
     "reasoning attached, including buy two, one each side of the compliance "
     "chamber, which is P1 and P2 under other names. GP not DP: on the "
     "dual-port part only the P1 face carries the gel and P2 is bare "
     "silicon, so there is a wrong hole to plumb fluid into. Peak here is "
     "19 percent of its scale. Gel-protected but qualified on DRY AIR, so "
     "give it a short air dead leg"),
    ("INSTRUMENTS", 2, "Honeywell ABP2DANT005PG2A3XX",
     "0-5 psi gauge, I2C, barbed, LIQUID MEDIA", "LATER",
     "The liquid-rated alternative, only if the dead leg on the MPX5050GP "
     "is unwelcome. The 'T' in the part number is what makes it liquid "
     "media with food-grade gel: an 'N' there is dry gases only and would "
     "be destroyed. Barbless is ABP2DVNT005PG2A3XX. ~200 Hz, 3.3 V, and "
     "both land on I2C 0x28 so they need the Pico's two buses"),
    ("INSTRUMENTS", 1, "clear vinyl tube, 6.35 mm bore, 0.7 m, + a metre stick",
     "the MANOMETER, teed into the trunk at the piston junction",
     "BUY", "a tube, open at the top, with loop fluid standing in it. Its "
            "HEIGHT is the pressure. Stands at 405 mm when R1 is right, and "
            "1 - 405/1200 is the share of the pulse going forward, so it "
            "reads the design parameter directly. Tee it into the TRUNK, "
            "never the 3 mm run. 700 mm TALL with its TOP RETURNED TO THE "
            "RESERVOIR. The sweep only ever puts it between 275 and 535 mm; "
            "the 1200 mm case is a shut R2 with no flow, and with the "
            "overflow plumbed back that spills harmlessly and pins the "
            "reading at 700, which tells you at once that something is "
            "wrong. A wider tube does NOT make it shorter: h = p/(rho g) has "
            "no diameter in it. "
            "Soft tube is fine HERE and nowhere else, because it carries no "
            "flow and sits behind the needle. Zero the ruler at the "
            "RESERVOIR's surface. reads the MEAN to about a millimetre of "
            "fluid. The transducer's "
            "total error band is 1.5 percent of 5 psi, which is 4 mmHg, so "
            "the tube is the absolute reference and the sensor is the shape"),
    # The interface between the sensors and the Pico. Six passives, and
    # without the first two the Pico's 3.3 V ADC pin sees 4.70 V.
    ("INSTRUMENTS", 2, "resistor, 10k, 1%", "0.25 W, through hole", "BUY",
     "upper half of the divider on each sensor output. See wiring.py"),
    ("INSTRUMENTS", 2, "resistor, 20k, 1%", "0.25 W, through hole", "BUY",
     "lower half. 10k over 20k drops the sensor's 4.70 V full scale to "
     "3.13 V, which fits the Pico's 3.3 V ADC with room to spare and loads "
     "the sensor at only 0.16 mA"),
    ("INSTRUMENTS", 2, "capacitor, 0.47 uF film", "50 V", "BUY",
     "across the 20k. With the divider's 6.7k source this is a 51 Hz "
     "low-pass, which is the anti-alias filter for sampling at 250 Hz. The "
     "sensor answers in 1 ms, so without it a kilohertz of noise folds "
     "straight into the band we care about"),
    ("INSTRUMENTS", 2, "capacitor, 1 uF ceramic", "16 V", "BUY",
     "supply decoupling, mounted at the sensor's own pins 2 and 3, per the "
     "datasheet's application circuit"),
    ("INSTRUMENTS", 2, "blunt luer needle, 16 gauge, 25 mm",
     "the restriction in front of the manometer", "BUY",
     "PART 3 OF 3 of the manometer, not an alternative to it. Luer, so it "
     "mates the adapters already listed. Every gauge reads the mean and "
     "cannot follow the pulse, so this is about patience: 16 settles in "
     "19 s, 18 in 78 s. Without it the tube resonates at 0.89 Hz with the "
     "beat and spits out of the top"),

    ("INSTRUMENTS", 1, "kitchen scale, 1 g", "gravimetric flow catch", "BUY",
     "0.4 percent on the mean flow over a 60 s catch"),

    ("FASTENERS", 4, "M3 x 8 cap screw", "motor face to the motor plate",
     "BUY", ""),
    ("FASTENERS", 4, "M3 x 10 cap screw", "nut flange to the carriage",
     "BUY", "plus nuts, or self tap into the print"),
    ("FASTENERS", 4, "zip tie", "2.5 to 3 mm wide", "BUY",
     "through the saddle slots, clamps the collars"),
]

ORDER = ["PRINTED", "MOTION", "MOTOR", "ELECTRONICS", "SYRINGE",
         "FLUID INTERFACE", "INSTRUMENTS", "FASTENERS"]
TITLE = {"PRINTED": "PRINTED PARTS",
         "MOTION": "MOTION HARDWARE, none of it in hand",
         "MOTOR": "MOTORS",
         "ELECTRONICS": "ELECTRONICS",
         "SYRINGE": "SYRINGE",
         "FLUID INTERFACE": "FLUID INTERFACE, strictly the loop's but it "
                            "breaks without these",
         "INSTRUMENTS": "INSTRUMENTS, P1 and P2 and the two cheap references",
         "FASTENERS": "FASTENERS AND CONSUMABLES"}


def main():
    print("WAVEFORM GENERATOR, COMPLETE BILL OF MATERIALS")
    print("Screw span %.0f mm, so screw %.0f mm and rods %.0f mm.\n"
          % (S.SCREW_SPAN, SCREW_L, ROD_L))
    for g in ORDER:
        rows = [r for r in BOM if r[0] == g]
        print("%s" % TITLE[g])
        for _, qty, item, spec, status, note in rows:
            print("  [%-5s] %2d x %-24s %s" % (status, qty, item, spec))
            if note:
                print("           %s" % note)
        print("")

    for st, label in (("HAVE", "already on the bench"),
                      ("CHECK", "probably here, confirm"),
                      ("BUY", "has to be ordered or printed")):
        rows = [r for r in BOM if r[4] == st]
        print("%-5s %2d line items, %3d pieces   %s"
              % (st, len(rows), sum(r[1] for r in rows), label))

    print("\nTHE SHORT VERSION OF WHAT IS MISSING")
    print("  Every moving part. The frame, carriage, collars and cap are not")
    print("  printed yet, and not one piece of the motion hardware is here:")
    print("  no screw, no nut, no rods, no LM8UU, no 608, no coupler. The")
    print("  electronics are done and proven, the mechanism does not exist.")
    print("\n  Two items decide whether the rig works at all rather than")
    print("  merely existing, and both are easy to order wrong:")
    beat_mm = 0.5 * 1000.0 / S.BORE_A
    rpm_wrong = (0.70 * beat_mm / 2.0) / 0.100 * 60.0
    print("    T8x8 lead screw.  T8x2 looks identical and is sold far more")
    print("                      often. At a 2 mm lead the same beat needs")
    print("                      %.0f rpm, which no 12 V NEMA 17 will do."
          % rpm_wrong)
    print("    Qosina 91050 check valve.  There is no part called 9105x;")
    print("                      that was a family wildcard in these notes and")
    print("                      it is why the search came back empty. The")
    print("                      luer-to-luer alternative cracks at 0.433 psi,")
    print("                      which is the entire head.")


if __name__ == "__main__":
    main()
