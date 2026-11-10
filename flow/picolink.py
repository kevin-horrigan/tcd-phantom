# -*- coding: utf-8 -*-
"""Talk to the Pico over the raw REPL. Runs on the laptop, not on the Pico.

    python picolink.py info                 what firmware is on it
    python picolink.py put step_test.py     copy a file to the board
    python picolink.py ls                   list what is on the board
    python picolink.py eval "2+2"           run one expression
    python picolink.py run step_test.py     import and run it, stream output
    python picolink.py put a.py main.py    copy, renaming it on the board
    python picolink.py get drive.py        read a file back, verified by length
    python picolink.py call drive.diag     reload, then run it

Use "call", not "eval", to run code on the board. MicroPython caches imports
for the life of the board session, so a module imported before an upload
stays imported after it, and eval will happily run the version you replaced.
"call" drops the cache first. This bit us on drive.selftest().

Uploads are verified by a sha256 computed ON the board, because the link has
no flow control and a file that lands short still imports and then misbehaves
somewhere that looks unrelated.

Needs pyserial only. The port is found by VID 2E8A, or give it: --port COM15
"""
import hashlib
import sys
import time
import serial
from serial.tools import list_ports

CTRL_A, CTRL_B, CTRL_C, CTRL_D = b"\x01", b"\x02", b"\x03", b"\x04"


PICO_VID = 0x2E8A

# Boards on this bench that all answer to VID 2E8A. Auto-detect used to take
# the first match, which is fine with one board plugged in and is a way to
# flash the wrong hardware with two. Serial numbers are the only thing that
# tells them apart, so they are recorded here. Add to this as boards appear.
KNOWN = {
    "EFD8105DF76537C4": "motor Pico 2, TMC2209 driver",
    "6B565B5B2DC9D43D": "Sentinel",
    "2FE1876C8E855B9C": "XY-9 stage",
}


def pico_ports():
    """Every VID 2E8A device, as (device, serial, label)."""
    out = []
    for p in list_ports.comports():
        if p.vid == PICO_VID:
            sn = (p.serial_number or "").upper()
            out.append((p.device, sn, KNOWN.get(sn, "unknown board")))
    return out


def find_port(want=None):
    """The one Pico to talk to. Refuses to guess between several.

    Three boards on this bench share VID 2E8A: the motor Pico, the Sentinel
    and the XY-9 stage. Taking the first match would eventually upload the
    motor driver onto the Sentinel, so ambiguity is an error here, not a
    coin flip. Pass a serial number, or --port, to settle it.
    """
    found = pico_ports()
    if not found:
        raise SystemExit(
            "no Pico found.\n"
            "  * is it plugged in, and is the cable a DATA cable? A charge-only\n"
            "    lead powers the board and carries nothing.\n"
            "  * a board with no firmware, or one held in BOOTSEL, appears as a\n"
            "    USB DRIVE and not as a serial port. See pico/README.md.")
    if want:
        for dev, sn, label in found:
            if sn == want.upper():
                return dev
        raise SystemExit("no board with serial %s. Present: %s"
                         % (want, ", ".join(s for _, s, _ in found)))
    if len(found) == 1:
        return found[0][0]
    lines = ["  %-6s %-18s %s" % (d, s, l) for d, s, l in found]
    raise SystemExit(
        "%d boards share VID 2E8A and I will not guess between them:\n%s\n"
        "Pick one with --port, or by serial number."
        % (len(found), "\n".join(lines)))


class Pico:
    def __init__(self, port=None, timeout=2.0):
        self.port = port or find_port()
        self.s = serial.Serial(self.port, 115200, timeout=timeout)
        time.sleep(0.1)

    def close(self):
        self.s.write(CTRL_B)          # back to the friendly REPL
        self.s.close()

    def enter_raw(self):
        self.s.write(CTRL_C + CTRL_C)  # stop whatever is running
        time.sleep(0.1)
        self.s.reset_input_buffer()
        self.s.write(CTRL_A)
        if b"raw REPL" not in self.s.read_until(b">"):
            raise SystemExit("could not get a raw REPL on " + self.port)

    # A single exec that prints more than about 8 KB LOSES DATA, silently.
    # MicroPython's USB CDC has no flow control: when the board outruns the
    # host it drops what it cannot buffer, and the host has no way to know.
    # Measured on 2026-11-10 reading a 12 KB file back in one print(): the
    # result was exactly 32 bytes short, all of it missing from offset 8192.
    #
    # Nothing on this side can recover dropped bytes, so the rule is a
    # protocol one: never ask the board to emit a large blob in one go. get()
    # reads in bounded chunks and checks the length. put() verifies by a hash
    # computed ON the board, which is 64 characters however big the file is,
    # so it cannot be truncated into looking correct.
    SAFE_OUT = 4096

    def exec(self, code, stream=False, wait=600.0):
        """Run code on the board. Returns (stdout, stderr) as text.

        A quiet serial line is not the end of the output. The step tests go
        many seconds between prints while a burst runs, so an empty read means
        "still working", not "done". Only CTRL_D ends the stream, or the
        deadline, which is there so a genuinely hung board does not hang us.
        """
        self.s.write(code.encode() + CTRL_D)
        if self.s.read(2) != b"OK":
            raise SystemExit("board rejected the code")
        out = bytearray()
        deadline = time.time() + wait
        while True:
            chunk = self.s.read_until(CTRL_D)
            if chunk:
                out += chunk
                if stream:
                    sys.stdout.write(chunk.rstrip(CTRL_D).decode("utf-8", "replace"))
                    sys.stdout.flush()
            if chunk.endswith(CTRL_D):
                break
            if time.time() > deadline:
                raise SystemExit("board still running after %.0f s, gave up" % wait)
        err = self.s.read_until(CTRL_D)
        self.s.read_until(b">")
        dec = lambda b: bytes(b).rstrip(CTRL_D).decode("utf-8", "replace")
        if len(out) > self.SAFE_OUT and not stream:
            sys.stderr.write(
                "picolink: %d bytes from one exec, over the %d byte point "
                "where USB CDC starts dropping output silently. Read it in "
                "chunks instead.\n" % (len(out), self.SAFE_OUT))
        return dec(out), dec(err)

    # Uploading a file does NOT change what is already running. MicroPython
    # caches imports in sys.modules for the life of the board session, so a
    # module imported once before an upload stays imported after it. Measured
    # at the bench 2026-11-10: a fresh drive.py went up, verified by hash,
    # and the board then ran the PREVIOUS version's selftest because an
    # earlier eval had already imported it.
    #
    # On a file full of motion limits that is not an inconvenience. You can
    # tighten a soft travel limit, watch the upload verify, and have the
    # board keep enforcing the old one. So every path here that imports
    # uploaded code drops the cache first, and the convenient way to call
    # something on the board is the one that does it.
    CACHED = ("config", "drive", "net", "secrets")

    def fresh(self, names=None):
        """Drop uploaded modules from sys.modules so the next import reloads."""
        names = names or self.CACHED
        self.exec("import sys\n" + "\n".join(
            "sys.modules.pop(%r, None)" % n for n in names))

    def sha(self, remote):
        """sha256 of a file ON the board. 64 characters, so it cannot be
        truncated into looking right the way a file dump can."""
        out, err = self.exec(
            "import hashlib, binascii\n"
            "h = hashlib.sha256()\n"
            "f = open(%r, 'rb')\n"
            "while True:\n"
            "    b = f.read(512)\n"
            "    if not b: break\n"
            "    h.update(b)\n"
            "f.close()\n"
            "print(binascii.hexlify(h.digest()).decode())" % remote)
        if err.strip():
            raise SystemExit("could not hash %s on the board:\n%s" % (remote, err))
        return out.strip()

    def put(self, local, remote=None, verify=True):
        """Copy a file to the board and PROVE it arrived intact.

        Verification is not ceremony here. The upload path is thousands of
        small writes over a link with no flow control, and a file that lands
        short still imports, still runs, and misbehaves later in a way that
        looks like a logic bug. Comparing hashes costs one round trip.
        """
        remote = remote or local.replace("\\", "/").split("/")[-1]
        data = open(local, "rb").read()
        self.exec("f=open(%r,'wb')" % remote)
        for i in range(0, len(data), 256):
            self.exec("f.write(%r)" % data[i:i + 256])
        self.exec("f.close()")
        if verify:
            want = hashlib.sha256(data).hexdigest()
            got = self.sha(remote)
            if got != want:
                raise SystemExit(
                    "%s did not arrive intact.\n  local  %s\n  board  %s\n"
                    "Nothing on the board should be trusted until this passes."
                    % (remote, want, got))
        return remote, len(data)

    def get(self, remote, local=None, chunk=1024):
        """Read a file off the board in bounded pieces, and check the length.

        One big print() would be simpler and would silently lose bytes past
        about 8 KB. This asks for a slice at a time and compares what came
        back against os.stat, so a short read is an error rather than a file.
        """
        out, err = self.exec("import os\nprint(os.stat(%r)[6])" % remote)
        if err.strip():
            raise SystemExit("no such file on the board: %s" % remote)
        size = int(out.strip())
        buf = bytearray()
        while len(buf) < size:
            o, e = self.exec(
                "f=open(%r,'rb')\nf.seek(%d)\n"
                "import binascii\nprint(binascii.hexlify(f.read(%d)).decode())\n"
                "f.close()" % (remote, len(buf), chunk))
            if e.strip():
                raise SystemExit("read failed at offset %d:\n%s" % (len(buf), e))
            piece = bytes.fromhex(o.strip())
            if not piece:
                break
            buf += piece
        if len(buf) != size:
            raise SystemExit("read %d of %d bytes from %s, the link dropped data"
                             % (len(buf), size, remote))
        if local:
            open(local, "wb").write(buf)
        return bytes(buf)


def main(argv):
    port = None
    if "--port" in argv:
        i = argv.index("--port")
        port = argv[i + 1]
        del argv[i:i + 2]
    cmd = argv[1] if len(argv) > 1 else "info"
    p = Pico(port)
    print("# %s" % p.port)
    p.enter_raw()
    try:
        if cmd == "info":
            out, err = p.exec(
                "import sys, os, machine, rp2\n"
                "print(sys.implementation)\n"
                "print('cpu', machine.freq(), 'Hz')\n"
                "print('files', os.listdir())\n")
        elif cmd == "ls":
            out, err = p.exec("import os\nfor f in os.listdir():"
                              " print(f, os.stat(f)[6])")
        elif cmd == "eval":
            out, err = p.exec("print(%s)" % argv[2])
        elif cmd == "put":
            # argv[3] is the name ON THE BOARD. It used to be ignored, so
            # "put pico/drive.py main.py" quietly wrote drive.py instead.
            name, n = p.put(argv[2], argv[3] if len(argv) > 3 else None)
            out, err = p.exec("import os\nprint(%r, os.stat(%r)[6], 'bytes on board')"
                              % (name, name))
            print("sent %d bytes" % n)
        elif cmd == "call":
            # The safe way to run something on the board: drop the module
            # cache first, so what runs is what was last uploaded. "eval"
            # does NOT do this, which is how stale code gets run.
            mod, _, fn = argv[2].partition(".")
            p.fresh()
            code = "import {0}\n{0}.{1}()".format(mod, fn or "main")
            out, err = p.exec(code, stream=True)
            out = ""
        elif cmd == "get":
            data = p.get(argv[2], argv[3] if len(argv) > 3 else None)
            out, err = "%s: %d bytes read back intact" % (argv[2], len(data)), ""
        elif cmd == "run":
            # fresh import every time, so editing a file and re-running does
            # not silently re-execute the cached module
            name = argv[2].replace("\\", "/").split("/")[-1].replace(".py", "")
            out, err = p.exec("import sys\nsys.modules.pop(%r, None)\n"
                              "import %s\n%s.main()" % (name, name, name),
                              stream=True)
            out = ""                       # already streamed
        else:
            raise SystemExit("unknown command: " + cmd)
        if out:
            print(out, end="" if out.endswith("\n") else "\n")
        if err:
            print("--- board error ---\n" + err, file=sys.stderr)
    finally:
        p.close()


if __name__ == "__main__":
    main(sys.argv)
