import sys, os, cairo
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from draw import *
import mb
import retro
from retro import P, SLAB, TYPE
s = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H); c = cairo.Context(s)
T = 2.0
c.save(); c.translate(540, 1540); c.scale(1.22, 1.22); c.translate(-520, -mb.ROAD)
mb.border_scene(c, T, 'day', sand=1.0)
mb.bert_on_bike(c, T, 240, moving=False)
mb.money_bag(c, 80, mb.ROAD + 10, 1.0)
c.restore()
mb.magnifier(c, 300, 1000, 150, 1.0, cross=1.0, T=T)
retro.paper_card(c, 5, 0, [('RÄTSEL', 40, TYPE, P['red']), ('20 JAHRE KONTROLLIERT –', 44, SLAB, P['ink']),
                           ('NIE WAS GEFUNDEN.', 50, SLAB, P['ink']), ('TROTZDEM MILLIONÄR?', 54, SLAB, P['red'])], 540, 460, -2)
retro.paper_card(c, 5, 0, [('KANNST DU ES LÖSEN?', 40, SLAB, P['ink'])], 620, 720, 2)
s.write_to_png(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'thumbnail.png'))
