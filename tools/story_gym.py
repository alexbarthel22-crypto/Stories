"""Story: Heute ist Alex ... im Gym gewesen (1080x1920). Abends auf dem Heimweg, Pump, weiße Energy-Dose.
Nutzung: python3 tools/story_gym.py <ausgabe.png>"""
import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cairo
from alexlib import *

out = sys.argv[1]
surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
c = cairo.Context(surf)

# Abendhimmel
g = cairo.LinearGradient(0, 0, 0, H)
g.add_color_stop_rgb(0, *rgb("#2B2D5E")[:3]); g.add_color_stop_rgb(0.55, *rgb("#C9607A")[:3]); g.add_color_stop_rgb(1, *rgb("#F2A65A")[:3])
c.set_source(g); c.paint()
rnd = random.Random(3)
for i in range(40):
    c.arc(rnd.uniform(0, W), rnd.uniform(0, 700), rnd.uniform(1.5, 3.5), 0, 2 * math.pi); src(c, "#FFFFFF", rnd.uniform(0.3, 0.8)); c.fill()
emoji(c, "🌙", 150, 800, 100)
# Häuser-Silhouette
for i in range(8):
    x = i * 150 - 30; hh = 260 + (i * 97 % 220)
    c.rectangle(x, 1380 - hh, 140, hh); src(c, "#1E1F3A"); c.fill()
    for wy in range(int(1380 - hh + 30), 1360, 60):
        for wx in (x + 25, x + 85):
            if rnd.random() < 0.55:
                c.rectangle(wx, wy, 30, 34); src(c, "#FFD98A", 0.85); c.fill()
# Straße + Gehweg
c.rectangle(0, 1380, W, 540); src(c, "#3A3A48"); c.fill()
c.rectangle(0, 1380, W, 90); src(c, "#6B6B7A"); c.fill()
for i in range(6):
    rrect(c, 40 + i * 190, 1700, 110, 16, 8); src(c, "#E8E8E8"); c.fill()
# Laterne mit Lichtkegel
c.set_line_width(14); src(c, "#22222E"); c.move_to(170, 1420); c.line_to(170, 980); c.line_to(240, 960); c.stroke()
g2 = cairo.RadialGradient(250, 980, 10, 250, 1250, 420)
g2.add_color_stop_rgba(0, 1, 0.9, 0.6, 0.55); g2.add_color_stop_rgba(1, 1, 0.9, 0.6, 0)
c.move_to(230, 990); c.line_to(80, 1430); c.line_to(520, 1430); c.close_path(); c.set_source(g2); c.fill()
c.arc(250, 975, 22, 0, 2 * math.pi); fill(c, "#FFE9A8")


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

head = "HEUTE IST ALEX…"
hw = text_width(c, head, 60, FONT_HEAD) + 110
rrect(c, W / 2 - hw / 2, 290, hw, 110, 55); fill(c, INK)
text(c, head, W / 2, 345, 60, "#FFFFFF", FONT_HEAD)
outlined("IM GYM GEWESEN", 520, 130, "#FFFFFF")
emoji(c, "💪", 540, 690, 150, rot=-0.1)

# Alex: Muskelshirt, Pump, Sporttasche, Handtuch, winkt mit rechts, Dose links
AL = alex(top="#F4F4F2", top_style="tank", pump=True, pants="#3C3C46", shoes="#FFFFFF")
fx, fy, hgt = W / 2 + 40, 1720, 760
k = hgt / 100.0
# Sporttasche (hinter der Figur, Gurt über die Schulter)
c.save(); c.translate(fx, fy); c.scale(k, k)
c.set_line_width(1.6); src(c, "#1F1F28")
c.move_to(12, -52); c.curve_to(2, -46, -16, -40, -24, -37); c.stroke()
rrect(c, -40, -38, 22, 14, 4); fill(c, "#2E3A8C")
rrect(c, -40, -38, 22, 14, 4); c.set_line_width(0.7); src(c, "#141A4A"); c.stroke()
rrect(c, -37, -33, 16, 2, 1); fill(c, "#FFFFFF")
c.restore()
person(c, fx, fy, hgt, AL, 0.42, "happy", "wave", bob=False, name="Alex")
# Handtuch über der linken Schulter
c.save(); c.translate(fx, fy); c.scale(k, k)
rrect(c, -16.5, -57, 7, 15, 2.5); fill(c, "#36B5C2")
for yy in (-53, -48):
    rrect(c, -16.5, yy, 7, 1.2, 0.5); fill(c, "#FFFFFF")
c.restore()
# Schweißtropfen + Pump-Linien
for (dx, dy) in ((-215, -690), (215, -650)):
    emoji(c, "💦", fx + dx, fy + dy, 55)
c.set_line_width(6); src(c, "#FFFFFF", 0.8)
for a in (-0.4, 0, 0.4):
    c.move_to(fx - 260 + math.cos(a + math.pi) * 10, fy - 330 + math.sin(a) * 30)
    c.line_to(fx - 290 + math.cos(a + math.pi) * 10, fy - 330 + math.sin(a) * 50)
c.stroke()

# weiße Energy-Dose in der linken Hand (Hand bei ca. (-18.4, -28.6) Figur-Einheiten)
hx, hy = fx - 18.4 * k, fy - 28.6 * k
c.save(); c.translate(hx - 4, hy - 55); c.rotate(-0.08); c.scale(1.45, 1.45)
cw, ch = 64, 128
rrect(c, -cw / 2, -ch / 2, cw, ch, 10)
g3 = cairo.LinearGradient(-cw / 2, 0, cw / 2, 0)
g3.add_color_stop_rgb(0, 0.82, 0.83, 0.86); g3.add_color_stop_rgb(0.45, 1, 1, 1); g3.add_color_stop_rgb(1, 0.78, 0.79, 0.82)
c.set_source(g3); c.fill_preserve(); c.set_line_width(3); src(c, "#9A9AA2"); c.stroke()
rrect(c, -cw / 2 + 4, -ch / 2 - 6, cw - 8, 10, 4); fill(c, "#B8B8C0")
# drei Kratz-Streifen
src(c, "#2A2A30")
for i, x0 in enumerate((-18, -2, 14)):
    c.move_to(x0 - 4, -40); c.line_to(x0 + 3, -40); c.line_to(x0 + 1, 18 - i * 6); c.line_to(x0 - 2, 22 - i * 6); c.close_path(); c.fill()
c.select_font_face(FONT_HEAD); c.set_font_size(11); src(c, "#1F1F28")
e = c.text_extents("ZERO ZUCKER"); c.move_to(-e.x_advance / 2, -46); c.show_text("ZERO ZUCKER")
c.set_font_size(12); src(c, "#36B5C2")
e = c.text_extents("ULTRA"); c.move_to(-e.x_advance / 2, 46); c.show_text("ULTRA")
c.new_path()
c.restore()
# Hand vor der Dose
c.arc(hx, hy, 3.7 * k, 0, 2 * math.pi); fill(c, ALEX_BASE["skin"])
c.arc(hx, hy, 3.7 * k, 0, 2 * math.pi); c.set_line_width(0.6 * k); src(c, shade(ALEX_BASE["skin"], 0.72)); c.stroke()

bubble(c, "Bis morgen! 💪🔥", 700, 870, 1.0, tail=(-0.25, 1), size=66, max_w=520, font=FONT_HEAD)
surf.write_to_png(out)
