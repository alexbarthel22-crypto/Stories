"""TikTok-Cover/Thumbnail: Rolle riesig lesbar, Alex im Rollen-Outfit.
Nutzung: python3 tools/thumbnail.py <ausgabe.png> "PICK ME" "BOY" """
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cairo
from alexlib import *

out, l1, l2 = sys.argv[1], sys.argv[2], sys.argv[3]
surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
c = cairo.Context(surf)
background(c, "#EC7FAE", 0.4, rays=0.12, cy=1250, nrays=20)

def outlined(s, y, size, fill_col, rot=-0.04):
    c.save(); c.translate(W / 2, y); c.rotate(rot)
    c.select_font_face(FONT_HEAD); c.set_font_size(size)
    w = c.text_extents(s).x_advance
    if w > 980:
        size *= 980 / w; c.set_font_size(size); w = c.text_extents(s).x_advance
    for dx, dy, col, lw in ((10, 14, "#000000", 0), (0, 0, INK, size * 0.16)):
        c.move_to(-w / 2 + dx, size * 0.36 + dy); c.text_path(s)
        if lw:
            c.set_line_width(lw); c.set_line_join(cairo.LINE_JOIN_ROUND); src(c, col); c.stroke_preserve()
            src(c, fill_col); c.fill()
        else:
            src(c, col, 0.3); c.fill()
    c.restore()

# Kopfzeile (unterhalb der TikTok-Leiste, im 3:4-Ausschnitt)
rrect(c, W / 2 - 330, 300, 660, 110, 55); fill(c, INK)
text(c, "HEUTE IST ALEX…", W / 2, 355, 62, "#FFFFFF", FONT_HEAD)
# Rolle riesig
outlined(l1, 560, 250, "#FFFFFF")
outlined(l2, 790, 250, "#FFE14D")
# Alex
for e, x, y, s, r in (("🚩", 150, 1020, 130, -0.3), ("🚩", 930, 1060, 130, 0.3), ("🌹", 190, 1350, 110, -0.2), ("🥺", 900, 1340, 110, 0.2)):
    emoji(c, e, x, y, s, r)
person(c, W / 2, 1700, 760, alex(**OUTFIT_PICKME), 0.9, "smug", "hips", "🧋", bob=False)
surf.write_to_png(out)
