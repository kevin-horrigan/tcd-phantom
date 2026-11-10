# -*- coding: utf-8 -*-
"""Talk to the Creality K1C on the bench. Upload, list, delete, start, watch.

    python k1c.py status                  live state, temps, job
    python k1c.py ls [match]              gcode files on the printer
    python k1c.py put FILE.gcode          upload (HTTP multipart)
    python k1c.py rm NAME.gcode           delete one file
    python k1c.py start NAME.gcode        START A PRINT. Asks nothing. Be sure.
    python k1c.py stop                    cancel the running print
    python k1c.py watch [seconds]         poll progress

The printer is a K1C on stock firmware. Two interfaces, and you need both:

    HTTP  port 80    /info, and POST /upload for files
    WS    port 9999  status pushes and every command, Creality's own protocol

Notes that cost time to find:

  * The file list arrives as retGcodeFileInfo2 only after you ASK, by sending
    {"method":"get","params":{"reqGcodeFile":1}}. Status pushes do not carry it.
  * Commands are {"method":"set","params":{"opGcodeFile":"<verb>:<path>"}}
    where verb is printprt or deleteprt and path is the full
    /usr/data/printer_data/gcodes/NAME.gcode.
  * curl -F with a ";filename=" override silently fails on this server. Upload
    the file under the name you want it to have.
  * state 1 is printing. The machine reports the PREVIOUS job's filename and
    100% progress while idle, so "printProgress 100" does not mean busy.
"""
import asyncio
import json
import os
import sys
import urllib.request

import websockets

HOST = os.environ.get("K1C_HOST", "192.168.4.62")
WS = "ws://%s:9999" % HOST
GCODE_DIR = "/usr/data/printer_data/gcodes"

STATE = {0: "idle", 1: "PRINTING", 2: "complete", 3: "failed", 4: "paused"}


async def _talk(send=None, seconds=6.0, want=None):
    """Send zero or one command, collect pushes for a while, return merged."""
    merged = {}
    async with websockets.connect(WS, open_timeout=10, ping_interval=None) as ws:
        if send:
            await ws.send(json.dumps(send))
        end = asyncio.get_event_loop().time() + seconds
        while asyncio.get_event_loop().time() < end:
            try:
                raw = await asyncio.wait_for(ws.recv(), timeout=2.5)
            except asyncio.TimeoutError:
                continue
            try:
                d = json.loads(raw)
            except Exception:
                continue
            if isinstance(d, dict):
                merged.update(d)
                if want and want in d:
                    break
    return merged


def talk(send=None, seconds=6.0, want=None):
    return asyncio.run(_talk(send, seconds, want))


def op(verb, name):
    path = name if name.startswith("/") else "%s/%s" % (GCODE_DIR, name)
    return {"method": "set", "params": {"opGcodeFile": "%s:%s" % (verb, path)}}


def files(match=None):
    d = talk({"method": "get", "params": {"reqGcodeFile": 1}},
             seconds=8.0, want="retGcodeFileInfo2")
    out = d.get("retGcodeFileInfo2") or []
    if match:
        out = [f for f in out if match.lower() in (f.get("name") or "").lower()]
    return out


def put(local):
    name = os.path.basename(local)
    body = open(local, "rb").read()
    b = "----k1c%d" % len(body)
    pre = ("--%s\r\nContent-Disposition: form-data; name=\"file\"; "
           "filename=\"%s\"\r\nContent-Type: application/octet-stream\r\n\r\n"
           % (b, name)).encode()
    post = ("\r\n--%s--\r\n" % b).encode()
    req = urllib.request.Request(
        "http://%s/upload" % HOST, data=pre + body + post,
        headers={"Content-Type": "multipart/form-data; boundary=%s" % b})
    with urllib.request.urlopen(req, timeout=180) as r:
        return name, len(body), r.status, r.read(200).decode("utf-8", "replace")


def show(d):
    st = d.get("state")
    print("%-18s %s" % ("printer", "%s  %s" % (d.get("model"), d.get("hostname"))))
    print("%-18s %s (%s)" % ("state", st, STATE.get(st, "?")))
    print("%-18s %.1f / %s C" % ("nozzle", float(d.get("nozzleTemp", 0)),
                                 d.get("targetNozzleTemp")))
    print("%-18s %.1f / %s C" % ("bed", float(d.get("bedTemp0", 0)),
                                 d.get("targetBedTemp0")))
    print("%-18s %s" % ("job", os.path.basename(str(d.get("printFileName", "")))))
    print("%-18s %s%%  layer %s of %s" % ("progress", d.get("printProgress"),
                                          d.get("layer"), d.get("TotalLayer")))
    left = d.get("printLeftTime")
    if left:
        print("%-18s %d min" % ("remaining", int(left) // 60))


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    arg = sys.argv[2] if len(sys.argv) > 2 else None
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    if cmd == "status":
        show(talk())
    elif cmd == "ls":
        fs = files(arg)
        print("%d file(s)" % len(fs))
        for f in fs[:40]:
            print("  %s" % f.get("name"))
    elif cmd == "put":
        print("uploaded %s, %d bytes, HTTP %s %s" % put(arg))
    elif cmd == "rm":
        talk(op("deleteprt", arg), seconds=3.0)
        print("delete sent: %s" % arg)
    elif cmd == "start":
        d = talk()
        if d.get("state") == 1:
            raise SystemExit("REFUSING: printer is already printing.")
        names = [f.get("name") for f in files()]
        if arg not in names:
            raise SystemExit("REFUSING: %s is not on the printer." % arg)
        talk(op("printprt", arg), seconds=4.0)
        print("start sent: %s" % arg)
        show(talk(seconds=8.0))
    elif cmd == "stop":
        talk({"method": "set", "params": {"stop": 1}}, seconds=3.0)
        print("stop sent")
    elif cmd == "watch":
        import time
        for _ in range(int(arg or 5)):
            d = talk(seconds=4.0)
            print("state %s  layer %s/%s  %s%%  nozzle %.0f bed %.0f"
                  % (d.get("state"), d.get("layer"), d.get("TotalLayer"),
                     d.get("printProgress"), float(d.get("nozzleTemp", 0)),
                     float(d.get("bedTemp0", 0))))
            time.sleep(10)
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
