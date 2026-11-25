#!/bin/sh
# Rendert die Blender-Bilder fortsetzbar (überspringt vorhandene). Ein Aufruf läuft höchstens ~1h50.
cd "$(dirname "$0")/.."
exec timeout 6600 flock /tmp/dieweltohne_render.lock /home/user/bpyenv/bin/python blender/szene.py bframes ${1:-0} ${2:-1800} 1 --samples ${SAMPLES:-16} --res 540
