#!/bin/sh
# Fertigstellung der Blender-Fassung (fortsetzbar):
#   ./fertig.sh hd        -> bframes/ (540x960) sauber auf 1080x1920 hochskalieren -> bhd/
#   ./fertig.sh teil 450  -> Einblendungen über bhd/ legen, Teil teile/t450.mp4 (450 Bilder)
#   ./fertig.sh final     -> Teile zusammensetzen, Filmkorn, Ton, fertiges Video
cd "$(dirname "$0")"
case "$1" in
hd)
  mkdir -p bhd
  for f in bframes/f*.png; do
    n=$(basename "$f"); [ -s "bhd/$n" ] && continue
    ffmpeg -v error -y -i "$f" -vf "scale=1080:1920:flags=lanczos,unsharp=5:5:0.55:5:5:0" "bhd/$n.tmp.png" && mv "bhd/$n.tmp.png" "bhd/$n"
  done
  ls bhd | grep -c '^f.....\.png$' ;;
teil)
  a=$2; b=$((a + 450)); mkdir -p teile
  BG=bhd flock /tmp/dieweltohne_render.lock node src/render.js teile/t$a.mp4 $a $b 2>&1 | grep -v "404\|ReadPixels\|GL Driver" | tail -1
  [ "$(ffprobe -v error -count_frames -select_streams v -show_entries stream=nb_read_frames -of csv=p=0 teile/t$a.mp4)" = 450 ] && echo ok > teile/t$a.mp4.ok
  ls teile ;;
final)
  for a in 0 450 900 1350; do [ -f teile/t$a.mp4.ok ] || { echo "Teil $a fehlt"; exit 1; }; done
  for a in 0 450 900 1350; do echo "file 't$a.mp4'"; done > teile/liste.txt
  ffmpeg -v error -y -f concat -safe 0 -i teile/liste.txt -c copy video_stumm.mp4
  ffmpeg -v error -y -i video_stumm.mp4 -i mix.wav -map 0:v -map 1:a -vf "noise=c0s=5:c0f=t+u:c1s=2:c1f=t+u:c2s=2:c2f=t+u" \
    -c:v libx264 -preset slow -crf 20 -pix_fmt yuv420p -c:a aac -b:a 192k -t 60 -movflags +faststart folge13_meerkratzer.mp4
  ffprobe -v error -count_frames -select_streams v -show_entries stream=nb_read_frames -of csv=p=0 folge13_meerkratzer.mp4 ;;
esac
