#!/bin/bash
V=${BLENDER_PY:-/tmp/claude-0/-home-user-Stories/6cbad5e7-e7ab-5124-85a4-0dd8cbe1a969/scratchpad/venv/bin/python}
cd /home/user/Stories/sunken_pearl/src
for n in surf under descent winext cozy clock startle door windark peer nixie flicker gauge crack run capsule liftup display face doors reveal pearl faceglow reach eye final; do
  $V render_shot.py -- $n full 2>&1 | grep -E "FRAME|DONE|Error|rror:" | grep -v CUEW
done
echo ALL_DONE
