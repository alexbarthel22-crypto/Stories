import sys, os, cairo
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from draw import *
import safe as s_
import retro
from retro import P, SLAB, TYPE
s = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H); c = cairo.Context(s)
c.save(); c.translate(540, 1300); c.scale(1.4, 1.4); c.translate(-540, -1300)
s_.room(c, 2.0, 'night'); s_.bed(c); s_.desk(c)
s_.safe(c, 300, 1240, 1.0, 1.0, 'open', [lambda cc: s_.shoe(cc, 0, 50, 1.4)])
s_.shoe(c, 600, 1480, 1.6)
s_.shelly_x(c, 0.5, 470, 1480, 1.9, mirror=True, shoes=(False, False), expr='think', arms={'R': (8, -112)})
c.restore()
rect(c, 0, 0, W, H, alpha(hexc('#0B0E24'), 0.12))
retro.paper_card(c, 5, 0, [('RÄTSEL', 40, TYPE, P['red']), ('WARUM SCHLIESST', 54, SLAB, P['ink']),
                           ('SHELLY 1 SCHUH', 54, SLAB, P['ink']), ('IM SAFE EIN?', 66, SLAB, P['red'])], 540, 560, -2)
retro.paper_card(c, 5, 0, [('KANNST DU ES LÖSEN?', 40, SLAB, P['ink'])], 560, 830, 2)
s.write_to_png(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'thumbnail.png'))
