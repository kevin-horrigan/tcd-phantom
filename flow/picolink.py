# -*- coding: utf-8 -*-
"""Talk to the Pico over the raw REPL. Runs on the laptop, not on the Pico.

    python picolink.py info                 what firmware is on it
    python picolink.py put step_test.py     copy a file to the board
    python picolink.py ls                   list what is on the board
    python picolink.py eval "2+2"           run one expression
    python picolink.py run step_test.py     import and run it, stream output

Needs pyserial only. The port is found by VID 2E8A, or give it: --port COM15
"""
import sys
import time
import serial
from serial.tools import list_ports

CTRL_A, CTRL_B, CTRL_C, CTRL_D = b"\x01", b"\x02", b"\x03", b"\x04"


def find_port():
    for p in list_ports.comports():
        if p.vid == 0x2E8A:
            return p.device
    raise SystemExit("no Pico found. Is it plugged in and running MicroPython?")


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
        out = b""
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
        dec = lambda b: b.rstrip(CTRL_D).decode("utf-8", "replace")
        return dec(out), dec(err)

    def put(self, local, remote=None):
        remote = remote or local.replace("\\", "/").split("/")[-1]
        data = open(local, "rb").read()
        self.exec("f=open(%r,'wb')" % remote)
        for i in range(0, len(data), 256):
            self.exec("f.write(%r)" % data[i:i + 256])
        self.exec("f.close()")
        return remote, len(data)


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
            name, n = p.put(argv[2])
            out, err = p.exec("import os\nprint(%r, os.stat(%r)[6], 'bytes on board')"
                              % (name, name))
            print("sent %d bytes" % n)
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
