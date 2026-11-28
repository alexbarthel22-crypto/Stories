import sys, os, cairo, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from draw import *
import lt3 as L
import retro
from retro import P, SLAB, TYPE
from chars import shelly
s = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H); c = cairo.Context(s)
T = 3.0
L.FLASHES[:] = []
cam = L.Cam(60, -1560, 0.62)


def fg(k):
    L.hair_braid(k, [(208, L.TOPY - 64), (216, L.TOPY + 30), (216, L.TOPY + 90 * L.M)], 24)
    L.shelly_braided(k, T, 30, L.TOPY - 26, 0.95, 'o', {'R': (40, -150)}, 0.6, [(70, L.TOPY - 30), (120, L.TOPY - 40)] + L.WIN_OUT[:2])
    L.measure(k, -600, 0, L.TOPY, '120 M', fs=80)
    L.measure(k, 480, L.TOPY, L.TOPY + 90 * L.M, '90 M', L.HAIR(), fs=80)
    k.set_dash([18, 14])
    line(k, 216, L.TOPY + 90 * L.M, 216, -20, 9, P['red'])
    k.set_dash([])
    L.bolt(k, 560, L.TOPY - 900, -400, 7, 1.0)
    L.witch(k, -330, L.TOPY + 330, 1.5, 0.4, 1)


L.world(c, cam, T, 'night', [fg])
retro.paper_card(c, 5, 0, [('RÄTSEL', 40, TYPE, P['red']), ('120 M TURM', 70, SLAB, P['ink']), ('90 M ZOPF', 70, SLAB, hexc('#8A5A2E'))],
                 540, 330, -2)
retro.paper_card(c, 5, 0, [('WIE KOMMT', 56, SLAB, P['ink']), ('SIE RUNTER?', 70, SLAB, P['red'])], 540, 1480, 2)
s.write_to_png(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'thumbnail.png'))
