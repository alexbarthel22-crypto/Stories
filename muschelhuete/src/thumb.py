import sys, os, cairo
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from draw import *
import hats2 as h
import retro
from retro import P, SLAB, TYPE
s = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H); c = cairo.Context(s)
T = 3.0
h.CAM[0] = h.Cam(760, -230, 0.8)
h.setup(c, T, hat_q={i: 1.0 for i in range(1, 5)})
for i in range(1, 5):
    hx, hy = h.hat_pt(i)
    circle(c, hx + 46, hy - 46, 26, C['yellow'])
    text(c, '?', hx + 46, hy - 46, 34, C['ink'], font=SLAB)
retro.paper_card(c, 5, 0, [('RÄTSEL', 40, TYPE, P['red']), ('4 FREUNDE', 64, SLAB, P['ink']), ('4 MUSCHELHÜTE', 64, SLAB, P['ink'])],
                 540, 330, -2)
h.hat_card(c, 5, 0, 540, 1190)
retro.paper_card(c, 5, 0, [('WER KENNT', 56, SLAB, P['ink']), ('SEINE FARBE?', 70, SLAB, P['red'])], 540, 1500, 2)
s.write_to_png(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'thumbnail.png'))
