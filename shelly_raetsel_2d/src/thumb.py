import sys, os, cairo, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from draw import *
import scenes
s = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H); c = cairo.Context(s)
scenes.question_bg(c, 3.0)
from chars import shelly
shelly(c, 540, 1560, 3.6, arms={'R': (8, -112)}, expr='think', look=(4, -6))
for i in range(3):
    circle(c, 690 + i * 62, 790 - i * 58, 15 + i * 8, alpha(C['white'], 0.9))
sticker(c, 'RÄTSEL', 540, 250, 130, 'yellow', rot=-3)
sticker(c, 'WARUM FÄHRT SHELLY', 540, 440, 62, 'cream', rot=2)
sticker(c, 'BEI SONNE NUR BIS −10?', 540, 550, 62, 'cream', rot=-2)
sticker(c, 'KANNST DU ES LÖSEN?', 540, 1730, 56, 'blue', rot=-2)
s.write_to_png(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'thumbnail.png'))
