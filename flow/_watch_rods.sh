#!/bin/sh
# Poll until the K1C stops printing, then report. 47m32s of extrusion plus a
# full heat-up from a cold bed, so give it 90 polls and not 45.
for i in $(seq 1 90); do
  sleep 60
  out=$(timeout 30 python k1c.py status 2>&1)
  st=$(printf '%s\n' "$out" | grep -E '^state' | head -1)
  case "$st" in
    *"1 (PRINTING)"*) continue ;;
    *) printf 'ROD RETAINER PLATE ENDED after %d min\n%s\n' "$i" "$out"; exit 0 ;;
  esac
done
printf 'watcher timed out after 90 min, printer still busy\n'
timeout 30 python k1c.py status 2>&1
