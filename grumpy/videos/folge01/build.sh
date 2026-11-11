#!/bin/bash
# Baut Folge 1 komplett: Ton (lokal, Piper) -> Bilder -> Video.  Aufruf: ./build.sh <piper-modell.onnx> <arbeitsordner>
set -e
cd "$(dirname "$0")"
# Stimme: Pfad zu einem Piper-Modell (lokal, gratis) ODER "laura-A" / "laura-D" (ElevenLabs)
VOICE=${1:-laura-A}; WORK=$2; OUT=${3:-folge01_laura_A.mp4}   # Standard: Laura A
case "$VOICE" in
  laura-*) python3 audio_elevenlabs.py "${VOICE#laura-}" ;;
  *) python3 audio.py "$VOICE" ;;
esac
python3 make_video.py "$WORK/fsvg"
node render.js "$WORK/fsvg" "$WORK/fjpg"
DUR=$(python3 -c "import json;print(json.load(open('timeline.json'))['duration']+0.8)")
# Meeresrauschen (synthetisch) + Stimme
python3 mix.py "$WORK/fjpg" "$OUT"
