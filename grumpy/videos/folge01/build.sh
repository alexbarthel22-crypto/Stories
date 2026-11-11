#!/bin/bash
# Baut Folge 1 komplett: Ton (lokal, Piper) -> Bilder -> Video.  Aufruf: ./build.sh <piper-modell.onnx> <arbeitsordner>
set -e
cd "$(dirname "$0")"
# Stimme: Pfad zu einem Piper-Modell (lokal, gratis) ODER "laura-A" / "laura-D" (ElevenLabs)
VOICE=$1; WORK=$2; OUT=${3:-folge01.mp4}
case "$VOICE" in
  laura-*) python3 audio_elevenlabs.py "${VOICE#laura-}" ;;
  *) python3 audio.py "$VOICE" ;;
esac
python3 make_video.py "$WORK/fsvg"
node render.js "$WORK/fsvg" "$WORK/fjpg"
DUR=$(python3 -c "import json;print(json.load(open('timeline.json'))['duration']+1.0)")
# Meeresrauschen (synthetisch) + Stimme
ffmpeg -loglevel error -y -framerate 25 -i "$WORK/fjpg/f%05d.jpg" -i voice.wav \
  -f lavfi -i "anoisesrc=color=brown:amplitude=0.5:sample_rate=44100,lowpass=f=900,volume='0.10+0.07*sin(2*PI*t/5)':eval=frame" \
  -filter_complex "[1:a]aresample=44100,apad[v];[v][2:a]amix=inputs=2:duration=first:weights='1 1',volume=1.6,atrim=0:$DUR[a]" \
  -map 0:v -map "[a]" -c:v libx264 -preset medium -crf 19 -pix_fmt yuv420p -c:a aac -b:a 192k -t $DUR -movflags +faststart "$OUT"
echo fertig: "$OUT"
