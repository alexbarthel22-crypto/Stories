#!/bin/bash
V=${BLENDER_PY:-/tmp/claude-0/-home-user-Stories/6cbad5e7-e7ab-5124-85a4-0dd8cbe1a969/scratchpad/venv/bin/python}
export SP_OUT=${SP_OUT:-/home/user/Stories/sunken_pearl/frames/v2}
cd /home/user/Stories/sunken_pearl/src
for n in surf under descent winext marble crystal gold reef door envelope card face dress capsule liftup display doors reveal pearl faceglow reach open final; do
  $V render_shot.py -- $n full 2>&1 | grep --line-buffered -E "FRAME|DONE|Error|rror:" | grep -v CUEW
done
echo ALL_DONE
