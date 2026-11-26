import sys, os, cairo
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from draw import *
import hotel2 as h
s = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H); c = cairo.Context(s)
cam = h.Cam(540, -640, 0.66)
def act(ctx):
    h.shelly_boss(ctx, 2.0, 330, h.GROUND + 40, 1.3, 'present', 'smile')
h.draw_facade_scene(c, cam, 2.0, [act], belegt=1.0)
rect(c, 0, 0, W, H, alpha(hexc('#0B0E24'), 0.18))
h.paper_card(c, 5, 0, [('RÄTSEL', 40, h.TYPE, h.P['red']), ('AUSGEBUCHT –', 60, h.SLAB, h.P['ink']),
                       ('UND TROTZDEM', 60, h.SLAB, h.P['ink']), ('∞ NEUE GÄSTE?', 66, h.SLAB, h.P['red'])], 540, 560, -2)
h.paper_card(c, 5, 0, [('KANNST DU ES LÖSEN?', 40, h.SLAB, h.P['ink'])], 540, 1420, 2)
s.write_to_png(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'thumbnail.png'))
