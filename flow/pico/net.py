# -*- coding: utf-8 -*-
"""Wireless control for the piston. Runs ON a Pico 2 W.

    import net
    net.serve()                 connect, print the URL, then listen

Needs the RPI_PICO2_W firmware. The plain RPI_PICO2 build has no CYW43
driver, so `import network` fails there and nothing in this file can help.
A non-W build runs perfectly well on W hardware, which is why that mistake
looks like a software problem and is not one.

THE ARCHITECTURE EXISTS FOR ONE REASON, SO IT IS WORTH STATING PLAINLY.

This server COMMANDS, it does not stream. You ask for thirty beats and the
Pico plays thirty beats; nothing sends a waveform over wifi slice by slice.
That is not laziness, it is the only arrangement that survives contact with
the radio.

A beat is 160 slices and at 60 bpm each slice is 6.25 ms. Python has to hand
PIO the next burst inside that window. Servicing the CYW43 is exactly the
kind of work that eats into it. If the network were in the loop, a retry on
a dropped frame would land as a stretched slice in the middle of the
systolic upstroke.

Note carefully what that can and cannot break. PIO was handed an exact pulse
count and will emit it whatever else the chip is doing, so the piston cannot
end up in the wrong place: position stays arithmetic. What jitter distorts is
WHEN those pulses arrive, which is the shape of the beat, and the shape is
the entire product of this machine. So the socket is polled BETWEEN beats and
never during one, and drive.late_us is reported on every status so the cost
is measured rather than assumed.

The price is that stop takes effect at the end of the current beat, up to one
beat of latency. That is the right trade: a stop that lands a beat late is a
minor annoyance, and a beat whose upstroke is 8 ms late is a bad experiment
that still looks like a good one.

NOT SECURE, AND NOT PRETENDING TO BE. There is no authentication. Anyone on
the same network can move this motor. That is acceptable on a lab bench and
nowhere else: do not port-forward it, do not put it on a network you do not
control, and do not leave it running with a syringe fitted and nobody there.
"""
import socket
import time

import network

import config as C
import drive

try:
    import secrets
except ImportError:
    raise SystemExit(
        "no secrets.py on the board. Copy pico/secrets_example.py to\n"
        "pico/secrets.py, fill in SSID and PASSWORD, then:\n"
        "    python picolink.py --port COM6 put pico/secrets.py")

PORT = 80
hr = 60.0
beats_left = 0
worst_late = 0
beats_done = 0


def connect(timeout=20):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if getattr(secrets, "STATIC", None):
        wlan.ifconfig(secrets.STATIC)
    if not wlan.isconnected():
        wlan.connect(secrets.SSID, secrets.PASSWORD)
        t0 = time.ticks_ms()
        while not wlan.isconnected():
            if time.ticks_diff(time.ticks_ms(), t0) > timeout * 1000:
                st = wlan.status()
                wlan.active(False)
                raise OSError(
                    "wifi timed out, status %d. The CYW43 is 2.4 GHz ONLY, so "
                    "a 5 GHz network never appears in a scan and looks exactly "
                    "like a wrong password." % st)
            time.sleep_ms(200)
    return wlan.ifconfig()[0]


PAGE = """<!doctype html><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>Piston</title><style>
body{margin:0;padding:18px;font:16px system-ui;background:#14181d;color:#e3e8ee}
h1{font-size:1.1rem;margin:0 0 14px}
button{font:inherit;padding:10px 14px;margin:0 6px 8px 0;border-radius:6px;
border:1px solid #2c343d;background:#1b2026;color:#e3e8ee}
button.go{background:#a3253c;border-color:#a3253c;color:#fff}
input{font:inherit;width:5em;padding:8px;border-radius:6px;border:1px solid #2c343d;
background:#1b2026;color:#e3e8ee}
pre{background:#1b2026;padding:12px;border-radius:6px;overflow-x:auto;font-size:.85rem}
label{display:inline-block;margin:0 14px 10px 0}
</style><h1>Pulsatile piston</h1>
<div><label>bpm <input id=hr value=60></label>
<label>beats <input id=n value=30></label></div>
<div><button class=go onclick="go('/run?hr='+hr.value+'&beats='+n.value)">Run</button>
<button onclick="go('/stop')">Stop</button>
<button onclick="go('/zero')">Set zero here</button>
<button onclick="go('/off')">De-energise</button></div>
<pre id=s>...</pre>
<script>
function go(u){fetch(u).then(r=>r.text()).then(t=>s.textContent=t)}
setInterval(()=>{if(!document.hidden)fetch('/status').then(r=>r.text())
.then(t=>s.textContent=t)},1000);go('/status')
</script>"""


def _status():
    return ("position   %+.3f mm  %+.1f uL\n"
            "zero       %s\n"
            "beats      %d queued, %d done at %.0f bpm\n"
            "worst slice %d us late  (budget %d us)\n"
            "limits     %.1f mm soft, %.0f mm frame\n"
            "beat       %.3f mm = %d steps, %.3f uL/step"
            % (drive.mm(), drive.ul(),
               "declared" if drive.is_zeroed() else "NOT DECLARED",
               beats_left, beats_done, hr,
               worst_late, int(60.0 / hr / (len(C.BEAT) - 1) * 1e6),
               C.SOFT_TRAVEL_MM, C.TRAVEL_MM,
               C.BEAT_MM, round(C.BEAT_MM * C.STEPS_PER_MM), C.UL_PER_STEP))


def _query(path):
    if "?" not in path:
        return path, {}
    p, q = path.split("?", 1)
    out = {}
    for kv in q.split("&"):
        if "=" in kv:
            k, v = kv.split("=", 1)
            out[k] = v
    return p, out


def _handle(path):
    """Returns (content_type, body). Never moves the motor itself."""
    global hr, beats_left, beats_done, worst_late
    p, q = _query(path)
    if p == "/":
        return "text/html", PAGE
    if p == "/status":
        return "text/plain", _status()
    if p == "/zero":
        drive.set_zero()
        return "text/plain", "zero declared\n" + _status()
    if p == "/stop":
        beats_left = 0
        return "text/plain", "stopping at the end of this beat\n" + _status()
    if p == "/off":
        beats_left = 0
        drive.off()
        return "text/plain", "de-energised\n" + _status()
    if p == "/goto":
        if not drive.is_zeroed():
            return "text/plain", "refused: no zero declared. Press Set zero."
        try:
            drive.goto_mm(float(q.get("mm", "0")))
        except Exception as e:
            return "text/plain", "refused: %s" % e
        return "text/plain", _status()
    if p == "/run":
        if not drive.is_zeroed():
            return "text/plain", "refused: no zero declared. Press Set zero."
        try:
            hr = max(20.0, min(200.0, float(q.get("hr", "60"))))
            beats_left = max(0, min(100000, int(q.get("beats", "30"))))
        except ValueError:
            return "text/plain", "refused: hr and beats must be numbers"
        beats_done, worst_late = 0, 0
        return "text/plain", "queued %d beats at %.0f bpm\n%s" % (
            beats_left, hr, _status())
    return "text/plain", "no such endpoint: " + p


def serve(port=PORT):
    global beats_left, beats_done, worst_late
    ip = connect()
    print("piston at  http://%s/" % ip)
    print("status     http://%s/status" % ip)
    print("")
    print("No authentication. Anyone on this network can move the motor.")
    print("Ctrl-C stops the server and de-energises.")

    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("0.0.0.0", port))
    s.listen(2)
    s.settimeout(0)                      # non-blocking: beats come first

    try:
        while True:
            try:
                cl, _ = s.accept()
            except OSError:
                cl = None
            if cl:
                try:
                    cl.settimeout(2)
                    req = cl.recv(512).decode()
                    path = req.split(" ")[1] if " " in req else "/"
                    ct, body = _handle(path)
                    cl.send("HTTP/1.0 200 OK\r\nContent-Type: %s\r\n"
                            "Connection: close\r\n\r\n" % ct)
                    cl.send(body)
                except Exception as e:
                    print("request failed:", e)
                finally:
                    cl.close()

            # A beat runs to completion with the socket untouched. This is the
            # whole point of the design: the radio does not get a say in the
            # timing of a systolic upstroke.
            if beats_left > 0:
                drive.beat(hr)
                beats_left -= 1
                beats_done += 1
                if drive.late_us > worst_late:
                    worst_late = drive.late_us
            else:
                time.sleep_ms(20)
    except KeyboardInterrupt:
        pass
    finally:
        beats_left = 0
        drive.off()
        s.close()
        print("stopped, motor de-energised")
