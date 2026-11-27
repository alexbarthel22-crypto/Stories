import sys, os, cairo
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from draw import *
import queen as q
import retro
from retro import P, SLAB, TYPE
s = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H); c = cairo.Context(s)
q.hall(c, 2.0, 1.0, 1100, 'point', 'smile', pris_expr=0)
rect(c, 0, 0, W, H, alpha(hexc('#1A0E0A'), 0.12))
retro.paper_card(c, 5, 0, [('RÄTSEL', 40, TYPE, P['red']), ('NUR EIN SATZ', 64, SLAB, P['ink']),
                           ('RETTET IHN.', 64, SLAB, P['ink']), ('WELCHER?', 76, SLAB, P['red'])], 540, 420, -2)
q.rule_cards(c, 5, 0, 0, 230, 850, 1180)
retro.paper_card(c, 5, 0, [('KANNST DU ES LÖSEN?', 40, SLAB, P['ink'])], 540, 1440, 2)
s.write_to_png(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'thumbnail.png'))
