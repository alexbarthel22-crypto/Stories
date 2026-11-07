#!/bin/bash
# Vorschau mit Ersatzstimme (Piper) – kein Gemini-Kontingent. Nutzung: tools/preview.sh episodes/<ordner>
set -e
EP=$1; N=$(basename $EP); M=/tmp/claude-0/-home-user-Stories/a66d8103-8728-5ec7-a9d5-052ce7dc835c/scratchpad/tts/hi/de_DE-thorsten-high.onnx
python3 tools/tts.py $EP $M 0.85 | tail -1
cp episodes/01_pick_me_boy/build/tts/intro_pre.orig.wav $EP/build/tts/intro_pre.wav
python3 - "$EP" <<'P'
import json,sys,soundfile as sf
P=sys.argv[1]; j=json.load(open(f"{P}/build/tts.json")); j["intro"]["pre"]=sf.info(f"{P}/build/tts/intro_pre.wav").duration
json.dump(j,open(f"{P}/build/tts.json","w"),indent=1,ensure_ascii=False)
P
python3 tools/tighten.py $EP 1.08 0.22 | tail -1
python3 tools/match_level.py $EP > /dev/null
python3 tools/build.py $EP | tail -1
mkdir -p $EP/vorschau; mv $EP/$N.mp4 $EP/vorschau/vorschau_mit_ersatzstimme.mp4
