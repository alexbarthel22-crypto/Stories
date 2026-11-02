"""Erzeugt das TikTok-Profilbild von Alex (1080x1080, für runden Zuschnitt optimiert).
Nutzung: python3 tools/profile_pic.py <ausgabe.png>"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cairo
from alexlib import *

S = 1080
surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, S, S)
c = cairo.Context(surf)
# Verlauf Pink -> Lila
g = cairo.LinearGradient(0, 0, S, S)
g.add_color_stop_rgb(0, *rgb("#F27AAE")[:3]); g.add_color_stop_rgb(1, *rgb("#7B4FD6")[:3])
c.set_source(g); c.paint()
c.save(); c.translate(S / 2, S / 2)
for i in range(20):
    a0, a1 = 2 * i * math.pi / 20, (2 * i + 1) * math.pi / 20
    c.move_to(0, 0); c.arc(0, 0, 900, a0, a1); c.close_path()
c.set_source_rgba(1, 1, 1, 0.08); c.fill(); c.restore()
# Ring aus Rollen-Icons (zeigt: jeden Tag eine neue Rolle)
icons = ["🌹", "🚀", "🎮", "🍳", "🎧", "🏴", "🎸", "👷", "🤳", "🍎", "🏋", "👮"]
for i, e in enumerate(icons):
    a = -math.pi / 2 + i * 2 * math.pi / len(icons)
    x, y = S / 2 + math.cos(a) * 430, S / 2 + math.sin(a) * 430
    c.arc(x, y, 50, 0, 2 * math.pi); src(c, "#FFFFFF", 0.92); c.fill()
    emoji(c, e, x, y, 52)
# Alex als Brustbild, groß und mittig
c.save()
c.arc(S / 2, S / 2, 360, 0, 2 * math.pi); c.clip()
g2 = cairo.RadialGradient(S / 2, S / 2 - 60, 40, S / 2, S / 2, 360)
g2.add_color_stop_rgb(0, *rgb("#FFE9F3")[:3]); g2.add_color_stop_rgb(1, *rgb("#FFC1DD")[:3])
c.set_source(g2); c.paint()
person(c, S / 2, 1400, 1130, alex(top="#2F2F3A", top_style="hoodie", pants="#2F3B52"), 0.9, "happy", "wave", bob=False)
c.restore()
c.arc(S / 2, S / 2, 360, 0, 2 * math.pi); c.set_line_width(16); src(c, "#FFFFFF"); c.stroke()
# Fragezeichen-Badge: "Was ist Alex heute?"
bx, by = S / 2 + 250, S / 2 - 250
c.arc(bx, by, 78, 0, 2 * math.pi); fill(c, "#F7C948")
c.arc(bx, by, 78, 0, 2 * math.pi); c.set_line_width(10); src(c, "#FFFFFF"); c.stroke()
text(c, "?", bx, by + 2, 110, INK, FONT_HEAD)
surf.write_to_png(sys.argv[1])
