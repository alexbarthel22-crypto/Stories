#!/bin/bash
# Baut Tag 2: Ton (Laura, gecacht) -> Soundeffekte -> Bilder -> Video mit Musik.  Aufruf: ./build.sh <arbeitsordner>
set -e
cd "$(dirname "$0")"
WORK=$1; OUT=${2:-tag02.mp4}
python3 audio_elevenlabs.py
python3 ../../sounds/make_sfx.py >/dev/null
rm -rf "${WORK:?}/f2svg" "${WORK:?}/f2jpg"
python3 make_video.py "$WORK/f2svg"
node ../folge01/render.js "$WORK/f2svg" "$WORK/f2jpg"
python3 mix.py "$WORK/f2jpg" "$OUT"
