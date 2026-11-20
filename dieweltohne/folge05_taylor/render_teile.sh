#!/bin/sh
# Rendert das Video in Teilen (bricht nichts ab, wenn ein Lauf unterbrochen wird) und setzt es zusammen.
cd "$(dirname "$0")"
mkdir -p teile
for a in 0 450 900 1350 1800 2250; do
  b=$((a + 450)); f=teile/t$a.mp4
  [ -s $f.ok ] && continue
  flock /tmp/dieweltohne_render.lock node src/render.js $f $a $b && echo ok > $f.ok
done
for a in 0 450 900 1350 1800 2250; do echo "file 't$a.mp4'"; done > teile/liste.txt
ffmpeg -y -v error -f concat -safe 0 -i teile/liste.txt -c copy video_stumm.mp4
