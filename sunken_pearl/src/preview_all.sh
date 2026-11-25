#!/bin/bash
V=${BLENDER_PY:-/tmp/claude-0/-home-user-Stories/6cbad5e7-e7ab-5124-85a4-0dd8cbe1a969/scratchpad/venv/bin/python}
cd /home/user/Stories/sunken_pearl/src
for n in "$@"; do
  $V render_shot.py -- $n preview 2>&1 | grep -E "Error|rror:|Traceback|line [0-9]+" | head -8 | sed "s/^/[$n] /"
done
echo PREVIEW_DONE
