#!/bin/sh
# Rendert einen Teil (450 Bilder) und markiert ihn als fertig: ./teil.sh 450
cd "$(dirname "$0")"; a=$1; b=$((a + 450)); mkdir -p teile
flock /tmp/dieweltohne_render.lock node src/render.js teile/t$a.mp4 $a $b 2>&1 | grep -v "404\|ReadPixels\|GL Driver" | tail -1
[ "$(ffprobe -v error -count_frames -select_streams v -show_entries stream=nb_read_frames -of csv=p=0 teile/t$a.mp4)" = 450 ] && echo ok > teile/t$a.mp4.ok
ls teile
