"""TikTok-Profilbild von Alex mit saisonalem Thema.

Das Gesicht (aus alexlib.ALEX_BASE) bleibt immer gleich und groß in der Mitte – das ist der
Wiedererkennungswert. Pro Saison wechseln nur Ring, Hintergrund, Deko und Schal/Pulli.

Nutzung:
  python3 tools/profile_pic.py <ausgabe.png> [herbst|winter|fruehling|sommer]
  python3 tools/profile_pic.py --alle <ordner>
"""
import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cairo
from alexlib import *

S = 1080
C = S / 2

THEMES = {
    "herbst": dict(
        bg=("#FFE2B8", "#F29A4A"), ring=["#E8541E", "#F28C28", "#F7C948", "#C0392B", "#8E3B1F"],
        outer="#4A1E0E", top="#C9852E", scarf="#B8322A", scarf2="#E8A33A",
        deco=["🍁", "🍂", "🌰", "🍁", "🍂", "🍄", "🍁", "🍂"], extra="🍂"),
    "winter": dict(
        bg=("#E8F4FF", "#9EC8F0"), ring=["#2E6FD0", "#7FB7FF", "#FFFFFF", "#4A90E2", "#1F4E9E"],
        outer="#12305E", top="#3B5BA8", scarf="#D63A3A", scarf2="#FFFFFF",
        deco=["❄️", "⛄", "❄️", "🎄", "❄️", "⭐", "❄️", "🎁"], extra="❄️"),
    "fruehling": dict(
        bg=("#F2FFE8", "#A8E08A"), ring=["#F07FB0", "#FFC2DD", "#7FD06A", "#F7C948", "#E26AA0"],
        outer="#3E6B48", top="#7FD06A", scarf="#F07FB0", scarf2="#FFFFFF",
        deco=["🌸", "🌷", "🐝", "🌼", "🌸", "🦋", "🌷", "🌼"], extra="🌸"),
    "sommer": dict(
        bg=("#FFF6C8", "#FFC94A"), ring=["#FF7A3D", "#FFC94A", "#36B5C2", "#FF5C8A", "#F7C948"],
        outer="#8A3A12", top="#36B5C2", scarf=None, scarf2=None,
        deco=["☀️", "🌴", "🍉", "🕶️", "☀️", "🍦", "🌊", "🍹"], extra="☀️"),
}

R_IN = 395      # Innenkreis (Bildfläche)
RING_W = 112    # Ringbreite


def lerp_col(a, b, u):
    ra, ga, ba, _ = rgb(a); rb, gb, bb, _ = rgb(b)
    return (ra + (rb - ra) * u, ga + (gb - ga) * u, ba + (bb - ba) * u)


def ring(c, cols, outer):
    """Auffälliger Verlaufsring: viele kleine Bogensegmente mit Farbübergang."""
    n = 360
    r0, r1 = R_IN, R_IN + RING_W
    for i in range(n):
        u = i / n * len(cols)
        k = int(u) % len(cols)
        col = lerp_col(cols[k], cols[(k + 1) % len(cols)], u - int(u))
        a0 = -math.pi / 2 + i / n * 2 * math.pi
        a1 = a0 + 2 * math.pi / n + 0.004
        c.arc(C, C, r1, a0, a1); c.arc_negative(C, C, r0, a1, a0); c.close_path()
        c.set_source_rgb(*col); c.fill()
    # Glanzlicht oben links
    g = cairo.LinearGradient(0, C - r1, 0, C + r1)
    g.add_color_stop_rgba(0, 1, 1, 1, 0.35); g.add_color_stop_rgba(0.5, 1, 1, 1, 0); g.add_color_stop_rgba(1, 0, 0, 0, 0.18)
    c.arc(C, C, r1, 0, 2 * math.pi); c.arc_negative(C, C, r0, 2 * math.pi, 0); c.close_path()
    c.set_source(g); c.fill()
    # Konturen
    c.set_line_width(12); src(c, outer); c.arc(C, C, r1 + 5, 0, 2 * math.pi); c.stroke()
    c.set_line_width(4); src(c, "#FFFFFF", 0.6); c.arc(C, C, r1 - 6, 0, 2 * math.pi); c.stroke()
    c.set_line_width(8); src(c, "#FFFFFF"); c.arc(C, C, R_IN - 2, 0, 2 * math.pi); c.stroke()


def scarf(c, x, feet, h, col, col2):
    """Strickschal um den Hals (gezeichnet in Figur-Einheiten)."""
    k = h / 100.0
    c.save(); c.translate(x, feet); c.scale(k, k)
    c.move_to(-14, -58); c.curve_to(-8, -52.5, 8, -52.5, 14, -58)
    c.curve_to(15, -55.5, 14, -51.5, 11, -50.2); c.curve_to(4, -47.8, -4, -47.8, -11, -50.2)
    c.curve_to(-14, -51.5, -15, -55.5, -14, -58); c.close_path()
    c.set_source_rgb(*rgb(col)[:3]); c.fill_preserve()
    c.set_line_width(0.7); src(c, shade(col, 0.65)); c.stroke()
    # Streifen
    c.save()
    c.move_to(-14, -58); c.curve_to(-8, -52.5, 8, -52.5, 14, -58)
    c.curve_to(15, -55.5, 14, -51.5, 11, -50.2); c.curve_to(4, -47.8, -4, -47.8, -11, -50.2)
    c.curve_to(-14, -51.5, -15, -55.5, -14, -58); c.close_path(); c.clip()
    for xx in range(-14, 15, 4):
        c.rectangle(xx, -60, 1.6, 14)
    src(c, col2, 0.8); c.fill()
    c.restore()
    # herunterhängendes Ende
    rrect(c, 4.5, -51.5, 6.5, 15, 2)
    c.set_source_rgb(*rgb(col)[:3]); c.fill_preserve()
    c.set_line_width(0.7); src(c, shade(col, 0.65)); c.stroke()
    for yy in (-47, -42):
        rrect(c, 4.5, yy, 6.5, 1.8, 0.5); src(c, col2, 0.85); c.fill()
    c.set_line_width(0.6); src(c, col2)
    for xx in (5.5, 7.5, 9.5):
        c.move_to(xx, -36.5); c.line_to(xx, -34.5)
    c.stroke()
    c.restore()


def render(theme_name, out):
    th = THEMES[theme_name]
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, S, S)
    c = cairo.Context(surf)
    # Außenfläche (wird von TikTok rund abgeschnitten) in Ringfarbe
    src(c, th["outer"]); c.paint()

    # Innenfläche: Verlauf + Strahlen
    c.save()
    c.arc(C, C, R_IN, 0, 2 * math.pi); c.clip()
    g = cairo.RadialGradient(C, C - 120, 40, C, C, R_IN + 40)
    g.add_color_stop_rgb(0, *rgb(th["bg"][0])[:3]); g.add_color_stop_rgb(1, *rgb(th["bg"][1])[:3])
    c.set_source(g); c.paint()
    c.save(); c.translate(C, C + 60)
    for i in range(18):
        a0, a1 = 2 * i * math.pi / 18, (2 * i + 1) * math.pi / 18
        c.move_to(0, 0); c.arc(0, 0, 900, a0, a1); c.close_path()
    c.set_source_rgba(1, 1, 1, 0.13); c.fill(); c.restore()
    # Deko im Hintergrund (fallende Blätter/Flocken)
    rnd = random.Random(11)
    for i in range(9):
        a = rnd.uniform(0, 2 * math.pi); r = rnd.uniform(280, 380)
        x, y = C + math.cos(a) * r, C + math.sin(a) * r * 0.9 - 40
        if y < C + 150:
            emoji(c, th["extra"], x, y, rnd.uniform(46, 70), rot=rnd.uniform(-0.6, 0.6), alpha=0.75)
    # Alex: großes Brustbild, Gesicht mittig
    h = 1330
    feet = C + 45 + 73 * h / 100      # Kopfmitte leicht unter der Bildmitte -> ganze Tolle sichtbar
    spec = alex(top=th["top"], top_style="hoodie", pants="#2F3B52")
    person(c, C, feet, h, spec, 0.9, "happy", "idle", bob=False)
    if th["scarf"]:
        scarf(c, C, feet, h, th["scarf"], th["scarf2"])
    c.restore()

    ring(c, th["ring"], th["outer"])
    # Saison-Deko auf dem Ring
    for i, e in enumerate(th["deco"]):
        a = -math.pi / 2 + (i + 0.5) * 2 * math.pi / len(th["deco"])
        r = R_IN + RING_W / 2
        x, y = C + math.cos(a) * r, C + math.sin(a) * r
        emoji(c, e, x, y, 92, rot=math.sin(i * 1.7) * 0.4)
    surf.write_to_png(out)


if __name__ == "__main__":
    if sys.argv[1] == "--alle":
        os.makedirs(sys.argv[2], exist_ok=True)
        for n in THEMES:
            render(n, os.path.join(sys.argv[2], f"alex_profilbild_{n}.png"))
    else:
        render(sys.argv[2] if len(sys.argv) > 2 else "herbst", sys.argv[1])
