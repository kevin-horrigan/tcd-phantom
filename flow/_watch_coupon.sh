#!/bin/sh
# Poll until the K1C stops printing, then report. Capped so it cannot hang
# forever if the machine goes unreachable.
for i in $(seq 1 110); do
  sleep 60
  out=$(timeout 30 python k1c.py status 2>&1)
  st=$(printf '%s\n' "$out" | grep -E '^state' | head -1)
  case "$st" in
    *"1 (PRINTING)"*) continue ;;
    *) printf 'CARRIAGE PRINT ENDED after %d min\n%s\n' "$i" "$out"; exit 0 ;;
  esac
done
printf 'watcher timed out after 45 min, printer still busy\n'
timeout 30 python k1c.py status 2>&1
