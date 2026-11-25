#!/bin/bash
# usage: preview.sh shot [fractions...]
V=/tmp/claude-0/-home-user-Stories/6cbad5e7-e7ab-5124-85a4-0dd8cbe1a969/scratchpad/venv/bin/python
cd /home/user/Stories/sunken_pearl_raetsel/src
SP_OUT=/home/user/Stories/sunken_pearl_raetsel/frames/test $V render_shot.py -- "$1" preview "${@:2}" 2>&1 | grep -E "DONE|Error|rror|Traceback|line [0-9]+" | grep -v CUEW
