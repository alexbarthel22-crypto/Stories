#!/bin/bash
# Nachbearbeitung (2 Prozesse) + Encoding
cd /home/user/Stories/sunken_pearl
N=1670
python3 src/post.py 0 835 &
python3 src/post.py 835 $N &
wait
ffmpeg -y -v error -framerate 24 -i frames/v2/post/p%04d.png -i audio/final_mix.wav \
  -c:v libx264 -preset slow -b:v 9000k -maxrate 14M -bufsize 18M -pix_fmt yuv420p -profile:v high -movflags +faststart \
  -c:a aac -b:a 192k -shortest sunken_pearl.mp4
echo ASSEMBLED
