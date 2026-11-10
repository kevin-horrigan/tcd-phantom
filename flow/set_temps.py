# -*- coding: utf-8 -*-
"""Rewrite the nozzle and bed temperatures in a sliced gcode file.

    python set_temps.py IN.gcode OUT.gcode 215 65

OrcaSlicer's CLI does not resolve a filament profile's inheritance chain, so
asking it for PolyLite PLA Pro silently produced the base PLA defaults instead
of that filament's own 220 C. Rather than fight the CLI, slice with the
profile that comes out structurally correct and set the two numbers here.

215 / 65 are not guesses. They are what Kevin's own successful prints on this
machine used, recorded in his filenames: _pro215_ and _bed65. The generic
Creality PLA profile asks for 200 / 55, which is cool for a 0.6 nozzle moving
this much plastic and gives less first layer grip than a 40 mm tall part on a
small footprint wants.

Every M104/M109 (nozzle) and M140/M190 (bed) is rewritten, and the header
comments are updated so the file does not lie about itself afterwards.
"""
import re
import sys


def main():
    src, dst = sys.argv[1], sys.argv[2]
    nozzle, bed = int(sys.argv[3]), int(sys.argv[4])

    noz_cmd = re.compile(r"^(M10[49])(\s.*?)S(\d+(?:\.\d+)?)", re.I)
    bed_cmd = re.compile(r"^(M1[49]0)(\s.*?)S(\d+(?:\.\d+)?)", re.I)
    noz_hdr = re.compile(
        r"^(; (?:first_layer_temperature|nozzle_temperature"
        r"|nozzle_temperature_initial_layer)\s*=\s*).*$")
    bed_hdr = re.compile(
        r"^(; (?:first_layer_bed_temperature|bed_temperature|hot_plate_temp"
        r"|hot_plate_temp_initial_layer|textured_plate_temp"
        r"|cool_plate_temp|eng_plate_temp)\s*=\s*).*$")

    # The K1 does its real heating inside a START_PRINT macro whose arguments
    # are baked in at slice time. Patching only M104/M140 leaves that call
    # saying 200/55, and the macro is what actually runs. Miss this and the
    # bed quietly comes up to the wrong temperature.
    macro = re.compile(r"^(\s*START_PRINT\b.*)$", re.I)

    counts = {"nozzle": 0, "bed": 0, "header": 0, "macro": 0}
    out = []
    for line in open(src, encoding="utf-8", errors="replace"):
        s = line.rstrip("\n")
        if macro.match(s):
            s2 = re.sub(r"(EXTRUDER_TEMP=)\d+", r"\g<1>%d" % nozzle, s)
            s2 = re.sub(r"(BED_TEMP=)\d+", r"\g<1>%d" % bed, s2)
            if s2 != s:
                counts["macro"] += 1
            out.append(s2)
            continue
        m = noz_cmd.match(s)
        if m and float(m.group(3)) > 0:
            s = noz_cmd.sub(lambda g: "%s%sS%d" % (g.group(1), g.group(2), nozzle), s, 1)
            counts["nozzle"] += 1
        else:
            m = bed_cmd.match(s)
            if m and float(m.group(3)) > 0:
                s = bed_cmd.sub(lambda g: "%s%sS%d" % (g.group(1), g.group(2), bed), s, 1)
                counts["bed"] += 1
            elif noz_hdr.match(s):
                s = noz_hdr.sub(lambda g: g.group(1) + str(nozzle), s, 1)
                counts["header"] += 1
            elif bed_hdr.match(s):
                s = bed_hdr.sub(lambda g: g.group(1) + str(bed), s, 1)
                counts["header"] += 1
        out.append(s)

    with open(dst, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out) + "\n")

    print("nozzle -> %d C in %d commands" % (nozzle, counts["nozzle"]))
    print("bed    -> %d C in %d commands" % (bed, counts["bed"]))
    print("START_PRINT macro calls patched: %d" % counts["macro"])
    print("header lines corrected: %d" % counts["header"])
    if counts["macro"] == 0:
        print("WARNING: no START_PRINT call found. On a K1 that macro is what")
        print("         heats the machine. Check the start gcode before using.")
    # Nothing anywhere may still name the old temperatures.
    bad = [s for s in out
           if re.search(r"(EXTRUDER_TEMP|BED_TEMP)=\d+", s)
           and not re.search(r"EXTRUDER_TEMP=%d\b" % nozzle, s)]
    print("macro calls still on an old temperature: %d" % len(bad))
    # Prove it: no heater command outside the targets survives.
    left = []
    for i, s in enumerate(out, 1):
        m = noz_cmd.match(s) or bed_cmd.match(s)
        if m and float(m.group(3)) not in (0.0, float(nozzle), float(bed)):
            left.append("%d: %s" % (i, s))
    print("stray heater settings remaining: %d" % len(left))
    for s in left[:5]:
        print("   " + s)


if __name__ == "__main__":
    main()
