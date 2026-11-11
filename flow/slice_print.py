# -*- coding: utf-8 -*-
"""Slice a TCD part for the K1C on Kevin's proven recipe, and optionally print it.

    python slice_print.py stl/fit_coupon.stl
    python slice_print.py stl/fit_coupon.stl --upload
    python slice_print.py stl/fit_coupon.stl --upload --start     BED MUST BE CLEAR
    python slice_print.py stl/frame.stl --set wall_loops=4 --set sparse_infill_density=25%

This does not invent a recipe. It points at the same two profiles that
lidar-locations/hardware/yoke/slice_yoke.py uses, which are the ones behind
every part Kevin has actually printed on this machine:

    process   owl_candy/out/slice_budget/override_stand06_brim10.json
    filament  owl_candy/out/slice_budget/filament_owl_pla_pro.json
              "owl PLA Pro 215 bed60": nozzle 215, first layer 220, bed 60/62

Output goes to tcd-phantom/flow/gcode, not into the lidar repo, because a TCD
part has no business in that project's out/ directory.

Things that cost time to learn, recorded so they cost it once:

  * Bed temperature lives in the FILAMENT profile. Setting it as a process
    override is silently ignored. --bed writes a patched copy of the filament.
  * OrcaSlicer's CLI does NOT resolve a filament profile's "inherits" chain.
    Hand it a profile that only inherits and you get base PLA defaults, which
    on this machine means 200 C and a 55 C bed, with no warning.
  * The K1C heats from a START_PRINT macro whose arguments are baked in at
    slice time. Editing M104/M140 in the gcode afterwards does not change what
    the machine actually does. Set it in the profile instead, which is why
    this script exists rather than a gcode post-processor.
  * Upload is POST /upload with the file named as you want it stored. A curl
    ";filename=" override fails silently on this server.
"""
import json
import os
import re
import subprocess
import sys
import zipfile

ORCA = r"C:\Program Files\OrcaSlicer\orca-slicer.exe"
SYS_DIR = os.path.join(os.environ["APPDATA"], "OrcaSlicer", "system", "Creality")
MACHINE = os.path.join(SYS_DIR, "machine", "Creality K1C 0.6 nozzle.json")
BASE = r"C:\dev\owl_candy\out\slice_budget\override_stand06_brim10.json"
FILAMENT_SRC = r"C:\dev\owl_candy\out\slice_budget\filament_owl_pla_pro.json"
# Density follows the filament, because the mass and cost readout is wrong
# otherwise and wrong quietly: ABS is 16 percent lighter than PLA, so every
# part would be overstated by that much with no sign anything had changed.
# syringe_drive.MATERIAL is the single place the material is declared.
try:
    import syringe_drive as _S
    _M = _S.MATERIALS[_S.MATERIAL]
    RHO = _M["rho"]
    MATERIAL = _S.MATERIAL
except Exception:                            # slicing without the model
    RHO, MATERIAL, _M = 1.24, "PLA", None

# ABS needs a hotter nozzle, a much hotter bed, and the chamber shut. The K1C
# is enclosed, so this is a filament profile change rather than a hardware
# problem, but FILAMENT_SRC below is a PLA Pro profile and will not be
# silently right for ABS: hand --bed and --nozzle, or point it at an ABS
# profile. The slicer does NOT warn when a profile only inherits.
if MATERIAL != "PLA":
    sys.stderr.write(
        "NOTE: material is %s. FILAMENT_SRC is a PLA Pro profile, so pass\n"
        "      --bed %d and --nozzle %d, or point FILAMENT_SRC at an %s\n"
        "      profile. Density is already %.2f g/cm3 for the mass readout.\n"
        % (MATERIAL, _M["bed"], _M["nozzle"], MATERIAL, RHO))

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "gcode")
K1C = os.environ.get("K1C_HOST", "192.168.4.62")

# What a TCD part wants that the owl recipe does not already give it. These are
# the defaults; --set overrides any of them and lands in the filename.
TCD = {
    "layer_height": "0.24",
    "initial_layer_print_height": "0.24",
    "wall_loops": "3",
    "sparse_infill_density": "15%",
    "brim_type": "outer_only",
    "brim_width": "5",
    "enable_support": "0",
}


def arg(flag, default=None):
    return sys.argv[sys.argv.index(flag) + 1] if flag in sys.argv else default


def _plate_key(o):
    """Which *_plate_temp the slicer will actually use, from the bed type."""
    return {"Textured PEI Plate": "textured_plate_temp",
            "Smooth PEI Plate": "hot_plate_temp",
            "High Temp Plate": "hot_plate_temp",
            "Cool Plate": "cool_plate_temp",
            "Engineering Plate": "eng_plate_temp"}.get(
                o.get("curr_bed_type", ""), "hot_plate_temp")


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if len(sys.argv) < 2 or sys.argv[1].startswith("--"):
        raise SystemExit(__doc__)
    stl = os.path.abspath(sys.argv[1])
    stem = os.path.splitext(os.path.basename(stl))[0]
    os.makedirs(OUT, exist_ok=True)

    o = json.load(open(BASE, encoding="utf-8"))
    o.update(TCD)
    o["name"] = "tcd06"
    name = "%s_n06_pro215" % stem

    if "--layer" in sys.argv:
        L = float(arg("--layer"))
        o["layer_height"] = "%g" % L
        o["initial_layer_print_height"] = "%g" % max(L, 0.2)
    # Apply every override FIRST, then name the file from the final values.
    # Naming as we go produced frame_..._wall3_sparse15_..._wall4_sparse25,
    # which states both the default and the override and tells you nothing.
    extra = []
    for i, a in enumerate(sys.argv):
        if a == "--set":
            k, v = sys.argv[i + 1].split("=", 1)
            o[k] = v
            if k not in ("layer_height", "wall_loops", "sparse_infill_density",
                         "brim_type", "brim_width"):
                extra.append("%s%s" % (k.split("_")[0], v.strip("%")))

    name += "_l%s" % o["layer_height"].replace(".", "")
    name += "_wall%s" % o["wall_loops"]
    name += "_sparse%s" % o["sparse_infill_density"].strip("%")
    name += "_brim%s%s" % (o["brim_type"].replace("_", ""), o["brim_width"])
    for e in extra:
        name += "_" + e

    ovr = os.path.join(OUT, "override_tcd06.json")
    json.dump(o, open(ovr, "w"), indent=1)

    # --bed and --nozzle both patch the FILAMENT, because that is where the
    # K1C's START_PRINT macro reads them from at slice time. A process
    # override is ignored silently, and so is editing the gcode afterwards.
    # --nozzle was added for ABS: bed alone gets you a 100 C plate under a
    # 215 C extrusion, which is PLA temperature on ABS filament and produces
    # a part that delaminates rather than warps.
    filament = FILAMENT_SRC
    if "--bed" in sys.argv or "--nozzle" in sys.argv:
        f = json.load(open(FILAMENT_SRC, encoding="utf-8"))
        tag = ""
        if "--bed" in sys.argv:
            T = int(arg("--bed"))
            for k in list(f):
                if k.endswith("_plate_temp"):
                    f[k] = [str(T)]
                if k.endswith("_plate_temp_initial_layer"):
                    f[k] = [str(T + 2)]
            tag += "_bed%d" % T
        if "--nozzle" in sys.argv:
            N = int(arg("--nozzle"))
            f["nozzle_temperature"] = [str(N)]
            f["nozzle_temperature_initial_layer"] = [str(N + 5)]
            # ABS wants the part fan off or nearly so, or layers peel. These
            # live in the filament profile too.
            for k, v in (("fan_max_speed", "20"), ("fan_min_speed", "0"),
                         ("overhang_fan_speed", "30"),
                         ("close_fan_the_first_x_layers", "4")):
                if k in f:
                    f[k] = [v]
            tag += "_noz%d" % N
        filament = os.path.join(OUT, "filament%s.json" % tag)
        json.dump(f, open(filament, "w"), indent=1)
        name += tag

    out3mf = os.path.join(OUT, "%s.3mf" % stem)
    gcode = os.path.join(OUT, name + ".gcode")
    if os.path.exists(out3mf):
        os.remove(out3mf)
    r = subprocess.run(
        [ORCA, "--load-settings", "%s;%s" % (MACHINE, ovr),
         "--load-filaments", filament, "--slice", "0",
         "--export-3mf", out3mf, stl],
        capture_output=True, text=True, timeout=1800)
    if not os.path.exists(out3mf):
        raise SystemExit("slice failed:\n" + r.stdout[-1500:] + r.stderr[-1500:])
    with zipfile.ZipFile(out3mf) as z:
        g = z.read("Metadata/plate_1.gcode")
    open(gcode, "wb").write(g)

    head = g[:4000].decode("utf8", "ignore")
    tail = g[-400000:].decode("utf8", "ignore")

    def find(k, txt=tail):
        m = re.search(r"; %s = (.*)" % re.escape(k), txt)
        return m.group(1).strip() if m else None

    secs = 0.0
    m = re.search(r"; estimated printing time \(normal mode\) = (.*)", tail)
    when = m.group(1).strip() if m else "?"
    cm3 = float(find("filament used [cm3]") or 0)
    macro = re.search(r"^\s*START_PRINT.*$", head, re.M)

    print("%s" % name)
    print("  %-22s %s" % ("time", when))
    print("  %-22s %.1f cm3, %.0f g" % ("filament", cm3, cm3 * RHO))
    for k in ("nozzle_diameter", "layer_height", "wall_loops",
              "sparse_infill_density", "nozzle_temperature", "brim_type"):
        print("  %-22s %s" % (k, find(k)))
    # The macro carries the FIRST LAYER temperatures, not the steady-state
    # ones, so check it against the filament profile rather than against the
    # 215 that appears everywhere else. Getting this backwards produced a
    # false alarm the first time this ran.
    fj = json.load(open(filament, encoding="utf-8"))
    want_n = int(fj["nozzle_temperature_initial_layer"][0])
    want_b = int(fj["%s_initial_layer" % _plate_key(o)][0])
    print("  %-22s %s" % ("heats via", macro.group(0).strip() if macro else "NO MACRO"))
    if not macro:
        print("  *** no START_PRINT macro. The K1C heats from it, so this")
        print("      file would print cold. Do not send it.")
    else:
        got_n = int(re.search(r"EXTRUDER_TEMP=(\d+)", macro.group(0)).group(1))
        got_b = int(re.search(r"BED_TEMP=(\d+)", macro.group(0)).group(1))
        ok = (got_n == want_n and got_b == want_b)
        print("  %-22s nozzle %d, bed %d  %s"
              % ("first layer", got_n, got_b,
                 "matches the filament profile" if ok
                 else "DOES NOT MATCH profile (%d/%d). Do not print this."
                      % (want_n, want_b)))

    if "--upload" in sys.argv:
        sys.path.insert(0, HERE)
        import k1c
        print("  upload: %s, %d bytes, HTTP %s" % k1c.put(gcode)[:3])
    if "--start" in sys.argv:
        sys.path.insert(0, HERE)
        import k1c
        d = k1c.talk()
        if d.get("state") == 1:
            raise SystemExit("REFUSING: printer is already printing.")
        k1c.talk(k1c.op("printprt", os.path.basename(gcode)), seconds=4.0)
        print("  START SENT")
        k1c.show(k1c.talk(seconds=8.0))


if __name__ == "__main__":
    main()
