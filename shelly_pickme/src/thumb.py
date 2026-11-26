import sys, os, cairo, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from draw import *
import pm
s = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H); c = cairo.Context(s)
pm.sunburst(c, 1.0, '#E95C9C', '#F27BB0')
import random
r = random.Random(5)
for i in range(22):
    x, y = r.uniform(60, 1020), r.uniform(200, 1750)
    k = i % 3
    if k == 0: pm.heart(c, x, y, r.uniform(1.0, 1.7), C['red'])
    elif k == 1: pm.sparkle(c, x, y, r.uniform(14, 24), C['yellow'])
    else: pm.shell_icon(c, x, y, r.uniform(0.8, 1.2), C['pink3'])
pm.outlined(c, 'Heute ist Shelly', 540, 330, 58, C['white'], sw=10)
tw = text_size(c, 'PICK-ME-GIRL', 118)[0]
c.save(); c.translate(540, 500); c.rotate(-0.05)
fill_rrect(c, -tw / 2 - 48, -83, tw + 96, 190, 40, alpha(C['shadow'], 0.3))
fill_rrect(c, -tw / 2 - 40, -95, tw + 80, 190, 40, C['yellow'])
rrect(c, -tw / 2 - 40, -95, tw + 80, 190, 40); c.set_line_width(8); src(c, C['ink']); c.stroke()
text(c, 'PICK-ME-GIRL', 0, 0, 118, C['ink'])
c.restore()
sticker(c, 'ERKENNST DU SIE?', 510, 700, 58, 'white', rot=2)
pm.shelly_main(c, 1.0, 'hair', 'smile', feet=1440, s=2.4, name=False)
for i, (x, y) in enumerate([(250, 1050), (830, 1000), (230, 1330), (860, 1310)]):
    pm.red_flag(c, x, y, 2.0)
sticker(c, '4 RED FLAGS', 510, 1430, 62, 'red', rot=-2)
s.write_to_png(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'thumbnail.png'))
