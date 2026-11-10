# -*- coding: utf-8 -*-
"""Put the motor driver onto a connected Pico. Runs on whatever laptop the
board is plugged into, not on the Pico.

    python pico_install.py                 find the board, upload, verify
    python pico_install.py --port COM15    if auto-detect picks the wrong one
    python pico_install.py --test          upload, then move the motor 2 mm

Uploads pico/config.py and pico/drive.py, then imports drive on the board and
reads its constants back, so "installed" means the firmware actually ran and
agreed with the model rather than two files having landed.

It does NOT move the motor unless you pass --test, because the board may be
wired to a driver with no motor on it, or to a motor with a syringe already
in the carriage. Moving a stepper is never the safe default.
"""
import os
import sys

import picolink

HERE = os.path.dirname(os.path.abspath(__file__))
FILES = ("config.py", "drive.py")

CHECK = """
import drive, config as C
print("OK|%d|%.5f|%.5f|%.3f|%d|%d|%d|%d" % (
    C.STEPS_PER_MM, C.UL_PER_STEP, C.BEAT_MM, C.SOFT_TRAVEL_MM,
    len(C.BEAT), C.STEP_PIN, C.DIR_PIN, C.EN_PIN))
drive.off()
"""


def arg(flag, default=None):
    return sys.argv[sys.argv.index(flag) + 1] if flag in sys.argv else default


def main():
    for f in FILES:
        p = os.path.join(HERE, "pico", f)
        if not os.path.exists(p):
            raise SystemExit(
                "missing %s. Run: python gen_pico_config.py" % p)

    port = arg("--port")
    if port is None:
        port = picolink.find_port()
        if port is None:
            raise SystemExit(
                "no Pico found.\n"
                "  * is it plugged in, and is the cable a DATA cable?\n"
                "  * does it have MicroPython on it? A board in BOOTSEL mode\n"
                "    shows up as a USB DRIVE, not a serial port, and has to be\n"
                "    flashed first. See pico/README.md.\n"
                "  * if you know the port: --port COM15")
    print("board on %s" % port)

    pico = picolink.Pico(port)
    try:
        pico.enter_raw()
        out, err = pico.exec("import sys\nprint(sys.implementation)")
        if err.strip():
            raise SystemExit("board refused a plain print:\n" + err)
        ver = out.strip()
        print("firmware %s" % ver)
        if "micropython" not in ver.lower():
            raise SystemExit("that is not MicroPython. See pico/README.md.")

        for f in FILES:
            name, n = pico.put(os.path.join(HERE, "pico", f), f)
            print("  uploaded %s, %d bytes" % (name, n))

        out, err = pico.exec(CHECK)
        if err.strip():
            raise SystemExit("drive.py did not import cleanly:\n" + err)
        lines = out.strip().splitlines()
        line = [l for l in lines if l.startswith("OK|")]
        if not line:
            raise SystemExit("drive.py imported but said nothing:\n" +
                             "\n".join(lines))
        _, spmm, ulst, beat, soft, n, st, dr, en = line[0].split("|")
        print("")
        print("drive imported and answered:")
        print("  %s steps/mm, %s uL/step" % (spmm, ulst))
        print("  beat %s mm = %d steps" % (beat, round(float(beat) * float(spmm))))
        print("  soft limit %s mm, beat profile %s samples" % (soft, n))
        print("  pins STEP=%s DIR=%s EN=%s" % (st, dr, en))

        if "--test" in sys.argv:
            print("\n--- moving 2 mm and back, slowly. WATCH THE CARRIAGE ---")
            pico.exec("import drive; drive.selftest()", stream=True)
        else:
            print("\nNothing has moved. When the motor is connected and VREF is")
            print("set to 0.53 V, run this again with --test, or on the board:")
            print("    import drive; drive.selftest()")
    finally:
        pico.close()


if __name__ == "__main__":
    main()
