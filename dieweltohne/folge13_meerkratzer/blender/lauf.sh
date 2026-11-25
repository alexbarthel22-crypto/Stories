#!/bin/sh
# Rendert die Blender-Bilder fortsetzbar (überspringt vorhandene). Ein Aufruf läuft höchstens ~1h50.
# bpy stürzt gelegentlich nach vielen Bildern ab (Segfault) – dann wird einfach neu gestartet.
cd "$(dirname "$0")/.."
ende=$(( $(date +%s) + 6400 ))
while [ "$(date +%s)" -lt "$ende" ]; do
  rm -f bframes/*.tmp.png
  fehlt=0; for f in $(seq ${1:-0} $(( ${2:-1800} - 1 ))); do [ -s "$(printf 'bframes/f%05d.png' $f)" ] || { fehlt=1; break; }; done
  [ $fehlt = 0 ] && { echo ALLE_FERTIG; exit 0; }
  rest=$(( ende - $(date +%s) ))
  timeout $rest flock /tmp/dieweltohne_render.lock /home/user/bpyenv/bin/python blender/szene.py bframes ${1:-0} ${2:-1800} 1 --samples ${SAMPLES:-16} --res 540
  echo "Lauf beendet: $?"
done
