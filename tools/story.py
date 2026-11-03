"""TikTok-Story-Bild (1080x1920) im Serien-Stil.
Nutzung: python3 tools/story.py <ausgabe.png>
"""
import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cairo
from alexlib import *

out = sys.argv[1]
surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
c = cairo.Context(surf)
background(c, "#7B4FD6", 0.3, rays=0.11, cy=1180, nrays=20)
# zweite Farbebene für Verlauf Lila -> Pink
g = cairo.LinearGradient(0, 0, 0, H)
g.add_color_stop_rgba(0, 0.93, 0.5, 0.7, 0.0); g.add_color_stop_rgba(1, 0.93, 0.5, 0.7, 0.45)
c.set_source(g); c.paint()


def outlined(s, y, size, fill_col, rot=-0.04):
    c.save(); c.translate(W / 2, y); c.rotate(rot)
    c.select_font_face(FONT_HEAD); c.set_font_size(size)
    w = c.text_extents(s).x_advance
    if w > 960:
        size *= 960 / w; c.set_font_size(size); w = c.text_extents(s).x_advance
    c.move_to(-w / 2 + 9, size * 0.36 + 12); c.text_path(s); src(c, "#000000", 0.3); c.fill()
    c.move_to(-w / 2, size * 0.36); c.text_path(s)
    c.set_line_width(size * 0.16); c.set_line_join(cairo.LINE_JOIN_ROUND); src(c, INK); c.stroke_preserve()
    src(c, fill_col); c.fill()
    c.restore()

# Konfetti
rnd = random.Random(8)
for i in range(26):
    x, y = rnd.uniform(40, W - 40), rnd.uniform(260, 1700)
    if 200 < x < 880 and 1050 < y < 1700:
        continue
    c.save(); c.translate(x, y); c.rotate(rnd.uniform(0, 3.14))
    rrect(c, -9, -16, 18, 32, 4); src(c, rnd.choice(["#F7C948", "#FF5CA8", "#36B5C2", "#FFFFFF", "#2FA36B"]), 0.85); c.fill()
    c.restore()

# Kopfzeile + Text (unterhalb der Story-Leiste oben)
head = "HEUTE IST ALEX:"
hw = text_width(c, head, 60, FONT_HEAD) + 110
rrect(c, W / 2 - hw / 2, 290, hw, 110, 55); fill(c, INK)
text(c, head, W / 2, 345, 60, "#FFFFFF", FONT_HEAD)
outlined("DEN ERSTEN TAG", 520, 130, "#FFFFFF")
outlined("AUF TIKTOK", 670, 150, "#FFE14D", rot=-0.03)
# Sprechblase "was geht? 😁"
bubble(c, "was geht? 😁", W / 2, 850, 1.0, tail=(-0.15, 1), size=78, max_w=700, font=FONT_HEAD)

# Alex, groß und freundlich winkend (t so gewählt, dass die Hand oben ist)
person(c, W / 2 - 30, 1690, 700, alex(top="#5B8DEF", top_style="hoodie", pants="#2F3B52"), 0.42, "happy", "wave", bob=False)
emoji(c, "👋", 820, 1080, 100, rot=0.3)
emoji(c, "🎉", 170, 1150, 110, rot=-0.3)
emoji(c, "✨", 930, 1300, 80)
surf.write_to_png(out)
