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

ROD_L = S.SCREW_SPAN + 10.0
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
    ("MOTION", 2, "8 mm smooth rod", "hardened, %.0f mm" % ROD_L, "BUY", ""),
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
     "BUY", "THE ONE TO GET RIGHT. This line used to read '9105x', which is a "
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

    ("FASTENERS", 4, "M3 x 8 cap screw", "motor face to the motor plate",
     "BUY", ""),
    ("FASTENERS", 4, "M3 x 10 cap screw", "nut flange to the carriage",
     "BUY", "plus nuts, or self tap into the print"),
    ("FASTENERS", 4, "zip tie", "2.5 to 3 mm wide", "BUY",
     "through the saddle slots, clamps the collars"),
]

ORDER = ["PRINTED", "MOTION", "MOTOR", "ELECTRONICS", "SYRINGE",
         "FLUID INTERFACE", "FASTENERS"]
TITLE = {"PRINTED": "PRINTED PARTS",
         "MOTION": "MOTION HARDWARE, none of it in hand",
         "MOTOR": "MOTORS",
         "ELECTRONICS": "ELECTRONICS",
         "SYRINGE": "SYRINGE",
         "FLUID INTERFACE": "FLUID INTERFACE, strictly the loop's but it "
                            "breaks without these",
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
