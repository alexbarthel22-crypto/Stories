#!/bin/bash
V=/tmp/claude-0/-home-user-Stories/6cbad5e7-e7ab-5124-85a4-0dd8cbe1a969/scratchpad/venv/bin/python
export SP_OUT=/home/user/Stories/sunken_pearl_raetsel/frames
cd /home/user/Stories/sunken_pearl_raetsel/src
for n in hook deep small morning station rainlift raintrain sunlift stairs why count reach umbrella end; do
  $V render_shot.py -- $n full 2>&1 | grep --line-buffered -E "FRAME|DONE|Error|rror:" | grep -v CUEW
done
echo ALL_DONE
