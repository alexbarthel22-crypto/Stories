#!/bin/bash
# Nachbearbeitung (2 Prozesse) + Encoding
cd /home/user/Stories/sunken_pearl
N=1694
python3 src/post.py 0 847 &
python3 src/post.py 847 $N &
wait
ffmpeg -y -v error -framerate 24 -i frames/post/p%04d.png -i audio/final_mix.wav \
  -c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -profile:v high -movflags +faststart \
  -c:a aac -b:a 192k -shortest sunken_pearl.mp4
echo ASSEMBLED
