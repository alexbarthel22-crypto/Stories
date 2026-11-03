"""TikTok-Cover/Thumbnail: Rolle riesig lesbar, Alex im Rollen-Outfit.
Nutzung: python3 tools/thumbnail.py <episode-ordner>
Liest THUMB aus script.py und das Outfit (AL/PM) aus scenes.py, schreibt <episode>/thumbnail.png"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cairo
from alexlib import *

import importlib.util
ep = os.path.abspath(sys.argv[1])
sys.path.insert(0, ep)
def _load(n):
    sp = importlib.util.spec_from_file_location(n, os.path.join(ep, n + ".py"))
    m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
script, scenes = _load("script"), _load("scenes")
TH = getattr(script, "THUMB", dict(l1="PICK ME", l2="BOY", bg="#EC7FAE", expr="smug", pose="hips", prop="🧋",
                                  emojis=("🚩", "🚩", "🌹", "🥺")))
SPEC = getattr(scenes, "AL", None) or getattr(scenes, "PM")
out, l1, l2 = os.path.join(ep, "thumbnail.png"), TH["l1"], TH["l2"]
surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
c = cairo.Context(surf)
background(c, TH["bg"], 0.4, rays=0.12, cy=1250, nrays=20)

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
head = TH.get("head", "HEUTE IST ALEX…")
hw = text_width(c, head, 62, FONT_HEAD) + 110
rrect(c, W / 2 - hw / 2, 300, hw, 110, 55); fill(c, TH.get("pill", INK))
text(c, head, W / 2, 355, 62, TH.get("pill_text", "#FFFFFF"), FONT_HEAD)
# Rolle riesig: zwei Zeilen (l1 weiß, l2 Akzent) oder nur ein Wort (l1 leer)
if l1:
    outlined(l1, 560, 250, TH.get("color1", "#FFFFFF"))
    outlined(l2, 790, 250, TH.get("accent", "#FFE14D"))
else:
    outlined(l2, 660, 300, TH.get("accent", "#FFE14D"))
# Alex
for e, (x, y, s, r) in zip(TH["emojis"], ((150, 1020, 130, -0.3), (930, 1060, 130, 0.3), (190, 1350, 110, -0.2), (900, 1340, 110, 0.2))):
    emoji(c, e, x, y, s, r)
person(c, W / 2, 1700, 760, SPEC, 0.9, TH["expr"], TH["pose"], TH["prop"], bob=False)
surf.write_to_png(out)
