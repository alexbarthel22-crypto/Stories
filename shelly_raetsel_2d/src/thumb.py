import sys, os, cairo, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from draw import *
import scenes
from chars import shelly
s = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H); c = cairo.Context(s)
scenes.exterior(c, 1200, 0.56, 2.0, 'day', hl=1.0)
scenes.vignette(c, 0.35)
rect(c, 0, 0, W, H, alpha(C['navy'], 0.25))
shelly(c, 760, 1320, 2.6, arms={'R': (8, -112)}, expr='think', look=(-4, -6), face=-0.3)
for i in range(3):
    circle(c, 640 - i * 55, 840 - i * 50, 14 + i * 8, alpha(C['white'], 0.95))
sticker(c, 'RÄTSEL', 510, 380, 130, 'yellow', rot=-4)
sticker(c, 'WARUM FÄHRT SHELLY', 510, 590, 60, 'cream', rot=2)
sticker(c, 'NUR BIS ZUM 10. UG?', 510, 700, 64, 'cream', rot=-2)
sticker(c, 'KANNST DU ES LÖSEN?', 510, 1440, 54, 'blue', rot=-2)
s.write_to_png(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'thumbnail.png'))
