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
DUR=$(python3 -c "import json;print(json.load(open('timeline.json'))['duration']+0.8)")
# Meeresrauschen (synthetisch) + Stimme
SFX=$(python3 -c "import json;d=json.load(open('timeline.json'));print(' '.join(f\"{x['file']}:{x['from']}:{x['to']}:{x['at']}\" for x in d.get('sfx',[])))")
INPUTS=(); FILT=""; MIX="[v][2:a]"; N=2
for e in $SFX; do IFS=: read -r F A0 A1 AT <<< "$e"; N=$((N+1))
  INPUTS+=(-i "$F")
  FILT+="[$N:a]atrim=$A0:$A1,asetpts=PTS-STARTPTS,aresample=44100,adelay=$(python3 -c "print(int($AT*1000))")|$(python3 -c "print(int($AT*1000))"),volume=1.4[s$N];"
  MIX+="[s$N]"
done
NIN=$N
ffmpeg -loglevel error -y -framerate 25 -i "$WORK/fjpg/f%05d.jpg" -i voice.wav \
  -f lavfi -i "anoisesrc=color=brown:amplitude=0.5:sample_rate=44100,lowpass=f=900,volume='0.10+0.07*sin(2*PI*t/5)':eval=frame" \
  "${INPUTS[@]}" \
  -filter_complex "[1:a]aresample=44100,apad[v];${FILT}${MIX}amix=inputs=$NIN:duration=first:normalize=0,volume=0.9,atrim=0:$DUR[a]" \
  -map 0:v -map "[a]" -c:v libx264 -preset medium -crf 19 -pix_fmt yuv420p -c:a aac -b:a 192k -t $DUR -movflags +faststart "$OUT"
echo fertig: "$OUT"
