"""TikTok-Story: Alex im Bett mit seiner Serie, draußen viel zu kalt. 10 s, 1080x1920, ohne Sprache.
Nutzung: python3 stories/01_bett_serie/story.py"""
import os, sys, math, random, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from alexlib import *

DUR = 10.0
AL = alex(top="#7FA3D6", top_style="hoodie", pants="#5C5C66", shoes="#FFFFFF")
FEET, AH = 1560, 760
SNOW = [(random.Random(i).uniform(0, 1), random.Random(i + 99).uniform(0, 1), random.Random(i + 7).uniform(0.6, 1.4)) for i in range(40)]


def sticker(c, txt, x, y, s, rot, bg="#FFFFFF", fg=INK, size=52):
    if s <= 0:
        return
    def d():
        w = text_width(c, txt, size, FONT_HEAD) + size * 1.1
        rrect(c, x - w / 2 + 6, y - size * 0.95 + 8, w, size * 1.9, 22); src(c, "#000000", 0.25); c.fill()
        rrect(c, x - w / 2, y - size * 0.95, w, size * 1.9, 22); fill(c, bg)
        text(c, txt, x, y, size, fg, FONT_HEAD)
    scaled(c, x, y, s, d, rot)


def frame(c, t):
    # Zimmer
    g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgb(0, 0.16, 0.17, 0.30); g.add_color_stop_rgb(1, 0.24, 0.22, 0.38)
    c.rectangle(0, 0, W, H); c.set_source(g); c.fill()
    # Lichterkette
    c.move_to(0, 250)
    for i in range(13):
        c.line_to(i * 90, 250 + (25 if i % 2 else 0))
    c.set_line_width(3); src(c, "#1C1C22"); c.stroke()
    for i in range(12):
        bx, byy = 45 + i * 90, 262 + (12 if i % 2 == 0 else 12)
        on = 0.55 + 0.45 * math.sin(t * 3 + i * 1.3)
        col = ["#FFD24A", "#FF7AB6", "#7FE0FF", "#9BFF8A"][i % 4]
        c.arc(bx, byy, 26, 0, 2 * math.pi); src(c, col, 0.18 * on); c.fill()
        c.arc(bx, byy, 10, 0, 2 * math.pi); src(c, col, 0.6 + 0.4 * on); c.fill()
    # Fenster mit Schnee
    wx, wy, ww, wh = 110, 340, 340, 380
    rrect(c, wx - 18, wy - 18, ww + 36, wh + 36, 16); fill(c, "#E8E2D6")
    c.save(); rrect(c, wx, wy, ww, wh, 8); c.clip()
    g2 = cairo.LinearGradient(0, wy, 0, wy + wh); g2.add_color_stop_rgb(0, 0.07, 0.10, 0.25); g2.add_color_stop_rgb(1, 0.25, 0.32, 0.50)
    c.rectangle(wx, wy, ww, wh); c.set_source(g2); c.fill()
    c.arc(wx + 260, wy + 80, 34, 0, 2 * math.pi); src(c, "#F5F2DC", 0.9); c.fill()
    c.rectangle(wx, wy + wh - 60, ww, 60); fill(c, "#FFFFFF")
    for (fx, fy, sp) in SNOW:
        yy = wy + ((fy * wh + t * 90 * sp) % wh); xx = wx + fx * ww + math.sin(t * 2 + fy * 9) * 10
        c.arc(xx, yy, 4 * sp, 0, 2 * math.pi); src(c, "#FFFFFF", 0.9); c.fill()
    c.restore()
    c.move_to(wx + ww / 2, wy); c.line_to(wx + ww / 2, wy + wh); c.move_to(wx, wy + wh / 2); c.line_to(wx + ww, wy + wh / 2)
    c.set_line_width(10); src(c, "#E8E2D6"); c.stroke()
    c.save(); rrect(c, wx, wy, ww, wh, 8); c.clip()                                   # Eisblumen in den Ecken
    for (cx_, cy_) in ((wx, wy), (wx + ww, wy), (wx, wy + wh), (wx + ww, wy + wh)):
        g4 = cairo.RadialGradient(cx_, cy_, 0, cx_, cy_, 90)
        g4.add_color_stop_rgba(0, 0.9, 0.97, 1, 0.75); g4.add_color_stop_rgba(1, 0.9, 0.97, 1, 0)
        c.arc(cx_, cy_, 90, 0, 2 * math.pi); c.set_source(g4); c.fill()
    c.restore()
    emoji(c, "🌡️", wx + ww + 60, wy + 120, 80, rot=math.sin(t * 6) * 0.08)
    # Fitness-Ecke: Poster mit Trainingsplan
    px, py = 650, 320
    rrect(c, px, py, 320, 300, 10); fill(c, "#FFFFFF")
    rrect(c, px, py, 320, 300, 10); c.set_line_width(5); src(c, INK); c.stroke()
    text(c, "NO PAIN", px + 160, py + 40, 34, "#E23B3B", FONT_HEAD)
    text(c, "NO GAIN 💪", px + 160, py + 80, 34, "#E23B3B", FONT_HEAD)
    for i, d in enumerate(("MO", "DI", "MI", "DO", "FR")):
        yy = py + 125 + i * 33
        text(c, d, px + 70, yy, 24, INK, FONT_HEAD)
        text(c, "GYM", px + 150, yy, 22, "#555A66", FONT_BOLD)
        k = clamp((t - 1.0 - i * 0.25) / 0.2)
        if k > 0:
            text(c, "❌", px + 240, yy, 26 * (0.6 + 0.4 * k), "#E23B3B", FONT_HEAD)
    c.arc(px + 160, py + 6, 8, 0, 2 * math.pi); fill(c, "#E23B3B")             # Pinnnadel
    # Regal mit Hanteln, Shaker, Kettlebell (eingestaubt)
    sy = 740
    rrect(c, 620, sy, 380, 22, 6); fill(c, "#8A5A2B")
    rrect(c, 620, sy, 380, 22, 6); c.set_line_width(4); src(c, INK); c.stroke()
    for hx in (670, 760):                                                        # Kurzhanteln
        rrect(c, hx - 34, sy - 26, 68, 12, 5); fill(c, "#555A66")
        for ox in (-44, 28):
            rrect(c, hx + ox, sy - 54, 16, 54, 4); fill(c, "#2B2F3A")
    c.arc(880, sy - 36, 34, 0, 2 * math.pi); fill(c, "#2B2F3A")                 # Kettlebell
    c.arc(880, sy - 72, 18, math.pi, 2 * math.pi); c.set_line_width(9); src(c, "#2B2F3A"); c.stroke()
    text(c, "12kg", 880, sy - 34, 18, "#FFFFFF", FONT_HEAD)
    emoji(c, "🥤", 960, sy - 40, 60)
    for i in range(6):                                                            # Staub / Spinnweben
        r = random.Random(i + 40)
        c.arc(650 + r.uniform(0, 300), sy - 50 + r.uniform(-20, 10), 3, 0, 2 * math.pi); src(c, "#CFCFD6", 0.6); c.fill()
    emoji(c, "🕸️", 985, sy - 95, 46, alpha=0.8)
    # Klimmzugstange in der Ecke, Handtuch drüber
    rrect(c, 20, 800, 240, 14, 7); fill(c, "#B8BCC8")
    rrect(c, 60, 812, 70, 90, 8); fill(c, "#7FD0FF")
    # zusammengerollte Yogamatte am Bett
    rrect(c, 40, 990, 70, 330, 35); fill(c, "#8E5BE0")
    rrect(c, 40, 990, 70, 330, 35); c.set_line_width(5); src(c, INK); c.stroke()
    c.arc(75, 1000, 26, 0, 2 * math.pi); fill(c, "#B98CFF")
    # Bett
    rrect(c, 130, 930, 840, 420, 40); fill(c, "#6B4A2E")
    rrect(c, 130, 930, 840, 420, 40); c.set_line_width(6); src(c, INK); c.stroke()
    for px, rot in ((330, -0.06), (750, 0.06)):
        def pil(px=px):
            rrect(c, px - 170, 1030, 340, 170, 60); fill(c, "#F5F0FF")
            rrect(c, px - 170, 1030, 340, 170, 60); c.set_line_width(5); src(c, INK); c.stroke()
        scaled(c, px, 1115, 1, pil, rot)
    # Alex (sitzt, blaues Bildschirmlicht)
    blink = 1 if int(t * 1.3) % 6 != 0 else 0
    person(c, W / 2, FEET, AH, AL, t, "happy" if t < 6.5 else "smug", "idle", None, bob=True)
    glow = 0.18 + 0.08 * math.sin(t * 7) + 0.06 * math.sin(t * 13)
    g3 = cairo.RadialGradient(W / 2, 1180, 20, W / 2, 1000, 420)
    g3.add_color_stop_rgba(0, 0.95, 0.25, 0.25, glow * 1.3); g3.add_color_stop_rgba(1, 0.95, 0.25, 0.25, 0)
    c.rectangle(0, 700, W, 700); c.set_source(g3); c.fill()
    # dicke Decke
    c.move_to(-60, 1300)
    for i in range(10):
        c.curve_to(-60 + i * 120 + 40, 1260 + math.sin(t * 1.5 + i) * 6, -60 + i * 120 + 80, 1310, -60 + (i + 1) * 120, 1285)
    c.line_to(1140, H); c.line_to(-60, H); c.close_path(); fill(c, "#F2B6C8")
    c.set_line_width(6); src(c, INK)
    c.move_to(-60, 1300)
    for i in range(10):
        c.curve_to(-60 + i * 120 + 40, 1260 + math.sin(t * 1.5 + i) * 6, -60 + i * 120 + 80, 1310, -60 + (i + 1) * 120, 1285)
    c.stroke()
    for i in range(14):                                   # Herzchen-Muster
        r = random.Random(i)
        emoji(c, "🤍", r.uniform(110, 970), r.uniform(1380, 1880), 40, alpha=0.5)
    # Laptop auf der Decke (Rückseite, leuchtet)
    rrect(c, 380, 1185, 320, 200, 18); fill(c, "#C9CCD6")
    rrect(c, 380, 1185, 320, 200, 18); c.set_line_width(5); src(c, INK); c.stroke()
    c.arc(540, 1285, 26, 0, 2 * math.pi); src(c, "#FFFFFF", 0.7); c.fill()       # Logo-Punkt auf dem Deckel
    rrect(c, 350, 1380, 380, 30, 10); fill(c, "#A9ADB8")
    # Tee mit Dampf
    emoji(c, "☕", 830, 1340, 110)
    for i in range(3):
        u = (t * 0.6 + i / 3) % 1
        c.move_to(820 + i * 14, 1280 - u * 120)
        c.curve_to(800 + i * 14, 1260 - u * 120, 850 + i * 14, 1240 - u * 120, 825 + i * 14, 1220 - u * 120)
        c.set_line_width(6); src(c, "#FFFFFF", 0.5 * (1 - u)); c.stroke()
    # Story-Sticker
    sticker(c, "Draußen: 3 °C 🥶", 280, 790, pop(t, 0.5), -0.06, "#FFFFFF", INK, 44)
    sticker(c, "Gym? Morgen. 💪", 800, 810, pop(t, 2.4), 0.05, "#FFE14D", INK, 42)
    if t > 4.0:
        sticker(c, "Netflix: Folge 7 von 12 ▶", 540, 1460, pop(t, 4.0), 0.02, "#E50914", "#FFFFFF", 46)
    if t > 7.4:
        sticker(c, "Nur noch eine … 🫣", 330, 1340, pop(t, 7.4), -0.05, "#FFFFFF", INK, 38)
    if t < 0.4:                                            # Einblenden
        c.rectangle(0, 0, W, H); src(c, "#000000", 1 - t / 0.4); c.fill()


def main():
    out = os.path.join(HERE, "story_bett_serie.mp4")
    music = os.path.join(ROOT, "assets", "music", "alex_theme_marimba.wav")
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{W}x{H}", "-r", str(FPS),
                          "-i", "-", "-i", music, "-t", str(DUR), "-filter_complex",
                          f"[1:a]volume=0.55,afade=t=in:d=0.5,afade=t=out:st={DUR - 1.2}:d=1.2[a]", "-map", "0:v", "-map", "[a]",
                          "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-c:a", "aac", "-b:a", "192k", out],
                         stdin=subprocess.PIPE)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    for i in range(int(DUR * FPS)):
        c = cairo.Context(surf); frame(c, i / FPS); surf.flush()
        p.stdin.write(bytes(surf.get_data()))
        if i == int(8.0 * FPS):
            surf.write_to_png(os.path.join(HERE, "story_bett_serie.png"))
    p.stdin.close(); p.wait()
    print("fertig:", out)


if __name__ == "__main__":
    main()
