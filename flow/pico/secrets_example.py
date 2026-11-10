# -*- coding: utf-8 -*-
"""Copy to secrets.py, fill in, upload. secrets.py is gitignored on purpose.

    python picolink.py --port COM6 put pico/secrets.py

This repo is PUBLIC. Do not put a real SSID or password in this file, and do
not rename this file in place: the gitignore rule names secrets.py exactly.

Use the lab's 2.4 GHz network. The CYW43 on a Pico 2 W has no 5 GHz radio, so
a network that is 5 GHz only will simply never appear in a scan, which looks
identical to a wrong password.
"""
SSID = "your-2.4GHz-network"
PASSWORD = "your-password"

# Optional. Leave as None for DHCP. A fixed address is worth setting once the
# rig lives on a bench, because then the control page is at a known URL
# instead of wherever the router felt like putting it that morning.
STATIC = None          # ("192.168.4.70", "255.255.255.0", "192.168.4.1", "192.168.4.1")
