"""Visuals: Alex ist heute ein Gaslighter (TikTok Folge 3). Aufbau wie Pick-me-Boy.
Ton: typische Sätze zeigen, nicht verharmlosen; ehrlicher Moment am Ende.
"""
import math, random
from alexlib import *

# Outfit heute: dunkelgrüne Bomberjacke-Optik, Jeans
AL = alex(top="#3F5A4A", top_style="tee", chain=None, pants="#3F4A6B", shoes="#FFFFFF")
FEET, AH = 1690, 560     # größer wie bei Fake-Feminist
LENA = person_spec(4, girl=True, top="#46B39A", hair="#6B3E26", skin="#EBB894", pants="#3F4A6B", shoes="#2A2A2A")

INTRO = dict(icon="🌀", bg="#4A2E6B", spec=AL, expr="smug", pose="shrug", hand_prop=None,
             side_emoji="🤷", burst=["🌀", "🚩", "🤷", "🙄", "❓", "💬", "🧠", "🕯️"])


def _spiral(c, x, y, r, t, col, lw=5):
    c.save(); c.translate(x, y); c.rotate(t * 2.5)
    c.set_line_width(lw); c.set_line_cap(cairo.LINE_CAP_ROUND); src(c, col)
    for i in range(120):
        a = i * 0.16; rr = r * i / 120
        (c.move_to if i == 0 else c.line_to)(math.cos(a) * rr, math.sin(a) * rr)
    c.stroke(); c.restore()


def gas_lamp(c, x, base, t, glow, seed=0):
    """Viktorianische Gaslaterne mit Flackern."""
    c.set_line_width(14); src(c, "#1E1B24"); c.move_to(x, base); c.line_to(x, base - 520); c.stroke()
    rrect(c, x - 30, base - 30, 60, 30, 6); fill(c, "#1E1B24")
    c.set_line_width(6); c.move_to(x - 40, base - 480); c.line_to(x + 40, base - 480); c.stroke()
    fl = 0.75 + 0.25 * math.sin(t * 17 + seed) * math.sin(t * 7.3 + seed * 2)
    g = cairo.RadialGradient(x, base - 580, 10, x, base - 580, 260)
    g.add_color_stop_rgba(0, 1, 0.82, 0.45, 0.55 * glow * fl); g.add_color_stop_rgba(1, 1, 0.82, 0.45, 0)
    c.arc(x, base - 580, 260, 0, 2 * math.pi); c.set_source(g); c.fill()
    c.move_to(x - 34, base - 520); c.line_to(x + 34, base - 520); c.line_to(x + 46, base - 640); c.line_to(x - 46, base - 640); c.close_path()
    src(c, "#FFD98A", 0.55 + 0.45 * fl * glow); c.fill_preserve(); c.set_line_width(6); src(c, "#1E1B24"); c.stroke()
    c.move_to(x - 56, base - 640); c.line_to(x, base - 690); c.line_to(x + 56, base - 640); c.close_path(); fill(c, "#1E1B24")
    c.arc(x, base - 584, 12 + 3 * fl, 0, 2 * math.pi); src(c, "#FFF4D0", fl * glow); c.fill()


def gas_scene(c, t, revealed, tint):
    """Altes Stadthaus bei Dämmerung, Kopfsteinpflaster, Nebel, Gaslaternen (Gaslight-Anspielung)."""
    top = "#2A1F45" if revealed else mix_col("#2A1F45", tint, 0.35)
    bot = "#8A5A8F" if revealed else mix_col("#8A5A8F", tint, 0.3)
    g = cairo.LinearGradient(0, 0, 0, 1240)
    g.add_color_stop_rgb(0, *rgb(top)[:3]); g.add_color_stop_rgb(1, *rgb(bot)[:3])
    c.rectangle(-400, -400, W + 800, 1640); c.set_source(g); c.fill()
    rnd = random.Random(2)
    for i in range(30):
        c.arc(rnd.uniform(-100, 1180), rnd.uniform(380, 900), rnd.uniform(1.5, 3), 0, 2 * math.pi); src(c, "#FFFFFF", 0.5); c.fill()
    c.arc(880, 480, 60, 0, 2 * math.pi); src(c, "#F2EBD9"); c.fill()
    c.arc(905, 465, 52, 0, 2 * math.pi); src(c, top); c.fill()           # Sichel
    # Nachbarhäuser-Silhouette
    for x, hgt in ((-120, 520), (900, 560)):
        c.rectangle(x, 1240 - hgt, 300, hgt); src(c, "#1E1730"); c.fill()
    # Stadthaus (dunkler Backstein)
    rrect(c, 220, 820, 640, 440, 4); fill(c, "#5A3238")
    c.save(); rrect(c, 220, 820, 640, 440, 4); c.clip()
    for row in range(22):
        y = 820 + row * 20
        off = 0 if row % 2 else 30
        for col in range(12):
            c.rectangle(220 + col * 60 + off, y, 56, 16); src(c, "#6B3B42" if (row + col) % 3 else "#633740"); c.fill()
    c.restore()
    rrect(c, 220, 820, 640, 440, 4); c.set_line_width(6); src(c, INK); c.stroke()
    c.move_to(540, 590); c.line_to(880, 840); c.line_to(200, 840); c.close_path(); fill(c, "#2F2A3A")
    c.move_to(540, 590); c.line_to(880, 840); c.line_to(200, 840); c.close_path(); c.set_line_width(6); src(c, INK); c.stroke()
    for i in range(6):                                                     # Schieferlinien
        y = 640 + i * 35; hw = (y - 590) / 250 * 340
        c.move_to(540 - hw, y); c.line_to(540 + hw, y)
    c.set_line_width(2); src(c, "#46405A"); c.stroke()
    lit = 0.55 + 0.45 * (0.5 + 0.5 * math.sin(t * 9) * math.sin(t * 3.1)) if revealed else 1.0
    for x in (290, 670):
        rrect(c, x, 900, 120, 110, 8); src(c, "#F7C66B", 0.35 + 0.55 * lit); c.fill()
        rrect(c, x, 900, 120, 110, 8); c.set_line_width(5); src(c, INK); c.stroke()
        c.move_to(x + 60, 900); c.line_to(x + 60, 1010); c.move_to(x, 955); c.line_to(x + 120, 955); c.set_line_width(3); c.stroke()
        rrect(c, x - 8, 1010, 136, 14, 3); fill(c, "#2B2B2B")
    c.arc(540, 730, 42, 0, 2 * math.pi); src(c, "#F7C66B", 0.4 + 0.5 * lit); c.fill()
    c.arc(540, 730, 42, 0, 2 * math.pi); c.set_line_width(5); src(c, INK); c.stroke()
    rrect(c, 480, 1080, 120, 180, 6); fill(c, "#1F3A2E")
    c.arc(540, 1080, 60, math.pi, 0); fill(c, "#1F3A2E")
    c.arc(580, 1175, 7, 0, 2 * math.pi); fill(c, "#C9A227")
    # Kopfsteinpflaster
    c.rectangle(-400, 1240, W + 800, 2400); src(c, "#4A4458"); c.fill()
    for row in range(30):
        y = 1250 + row * 34
        for col in range(-6, 30):
            x = col * 52 + (26 if row % 2 else 0)
            rrect(c, x, y, 46, 28, 10); src(c, "#5A5468" if (row + col) % 2 else "#545066"); c.fill()
    # schmiedeeiserner Zaun
    c.set_line_width(5); src(c, "#16141C")
    for x in list(range(-40, 410, 32)) + list(range(690, 1140, 32)):
        c.move_to(x, 1420); c.line_to(x, 1310); c.stroke()
        c.move_to(x - 7, 1318); c.line_to(x, 1300); c.line_to(x + 7, 1318); c.close_path(); fill(c, "#16141C")
    c.set_line_width(6)
    for y in (1330, 1400):
        c.move_to(-40, y); c.line_to(410, y); c.move_to(690, y); c.line_to(1140, y)
    c.stroke()
    # schmiedeeiserne Parkbank links, Bistrotisch rechts
    c.set_line_width(6); src(c, "#16141C")
    for x in (135, 320):
        c.move_to(x, 1470); c.line_to(x, 1540); c.stroke()
    for i in range(3):
        rrect(c, 120, 1395 + i * 22, 220, 12, 4); fill(c, "#7A5638")
    rrect(c, 115, 1460, 230, 16, 5); fill(c, "#7A5638")
    c.arc(940, 1455, 70, math.pi, 2 * math.pi); c.close_path(); fill(c, "#16141C")
    c.set_line_width(8); src(c, "#16141C"); c.move_to(940, 1455); c.line_to(940, 1540); c.move_to(900, 1540); c.line_to(980, 1540); c.stroke()
    # Gaslaternen
    gas_lamp(c, 70, 1460, t, 1.0 if revealed else 0.8, 0)
    gas_lamp(c, 1010, 1460, t, 1.0 if revealed else 0.8, 3)
    # Nebel
    for i in range(3):
        y = 1230 + i * 60; x = (t * 40 * (1 + i * 0.3)) % 600 - 300
        for k in range(4):
            c.save(); c.translate(x + k * 420, y); c.scale(1, 0.25); c.arc(0, 0, 260, 0, 2 * math.pi); c.restore()
            src(c, "#E8E0F0", 0.08 + 0.03 * i); c.fill()


def _sign(c, x, y, txt, col, rot, size=40, w=330, post=70):
    c.save(); c.translate(x, y); c.rotate(rot)
    c.set_line_width(10); src(c, "#5A3E2A"); c.move_to(0, 40); c.line_to(0, 40 + post); c.stroke()
    hh = 130
    rrect(c, -w / 2, -hh + 45, w, hh, 12); fill(c, col)
    rrect(c, -w / 2, -hh + 45, w, hh, 12); c.set_line_width(5); src(c, INK); c.stroke()
    text_block(c, txt, 0, 45 - hh / 2, size, w - 26, INK, FONT_HEAD)
    c.restore()


def intro_decor(c, t, u):
    s_ = clamp(u)
    # Spiralen in den Fenstern + schiefe Bilderrahmen
    for x in (350, 730):
        _spiral(c, x, 955, 46 * s_, t, "#4A2E6B", 5)
    _spiral(c, 540, 730, 32 * s_, -t, "#4A2E6B", 4)
    for x, r in ((260, 0.35), (820, -0.4)):
        c.save(); c.translate(x, 860); c.rotate(r * s_)
        rrect(c, -34, -26, 68, 52, 4); fill(c, "#C9A227"); rrect(c, -26, -18, 52, 36, 3); fill(c, "#BFE6FF")
        c.restore()
    # Banner am Dach
    def banner():
        rrect(c, 230, 756, 620, 68, 12); fill(c, "#FFB547")
        rrect(c, 230, 756, 620, 68, 12); c.set_line_width(4); src(c, INK); c.stroke()
        text(c, "„DAS HAB ICH NIE GESAGT“", 540, 790, 34, INK, FONT_HEAD)
    scaled(c, 540, 790, s_, banner, rot=0.02 * math.sin(t * 3))
    # Schilder vorne
    _sign(c, 200, 1650, "Du bildest dir das ein 🌀", "#E9D9FF", -0.1, 40, 340)
    _sign(c, 880, 1650, "Du bist zu empfindlich 🙄", "#FFFFFF", 0.08, 40, 340)
    # Fragezeichen im Nebel
    for i in range(5):
        u2 = (t * 0.4 + i / 5) % 1
        text(c, "?", 120 + i * 210, 1250 - u2 * 120, 60, "#FFFFFF", FONT_HEAD, alpha=0.5 * (1 - u2))


def alex_extras(c, x, feet, h, t, u):
    """Gaslighter-Alex: Gaslaterne in der Hand, 'Ich hab immer recht'-Anstecker, Unschuldsblick."""
    k = h / 100.0
    # Laterne an der rechten Hand (Pose shrug)
    hx, hy = x + 34.5 * k, feet - 61 * k
    c.save(); c.translate(hx, hy)
    c.set_line_width(0.8 * k); src(c, "#1E1B24"); c.move_to(0, 2 * k); c.line_to(0, 6 * k); c.stroke()
    fl = 0.7 + 0.3 * math.sin(t * 15)
    g = cairo.RadialGradient(0, 13 * k, 1, 0, 13 * k, 22 * k)
    g.add_color_stop_rgba(0, 1, 0.85, 0.5, 0.6 * fl); g.add_color_stop_rgba(1, 1, 0.85, 0.5, 0)
    c.arc(0, 13 * k, 22 * k, 0, 2 * math.pi); c.set_source(g); c.fill()
    c.move_to(-4 * k, 7 * k); c.line_to(4 * k, 7 * k); c.line_to(5 * k, 19 * k); c.line_to(-5 * k, 19 * k); c.close_path()
    src(c, "#FFD98A", 0.7 + 0.3 * fl); c.fill_preserve(); c.set_line_width(0.7 * k); src(c, "#1E1B24"); c.stroke()
    c.move_to(-6 * k, 7 * k); c.line_to(0, 4 * k); c.line_to(6 * k, 7 * k); c.close_path(); fill(c, "#1E1B24")
    rrect(c, -6 * k, 19 * k, 12 * k, 2 * k, 0.5 * k); fill(c, "#1E1B24")
    c.restore()
    # Anstecker auf der Brust
    c.save(); c.translate(x - 7 * k, feet - 42 * k)
    c.arc(0, 0, 5.5 * k, 0, 2 * math.pi); fill(c, "#FFB547")
    c.arc(0, 0, 5.5 * k, 0, 2 * math.pi); c.set_line_width(0.5 * k); src(c, INK); c.stroke()
    c.select_font_face(FONT_HEAD); c.set_font_size(1.7 * k); src(c, INK)
    for i, ln in enumerate(("ICH HAB", "IMMER", "RECHT")):
        e = c.text_extents(ln); c.move_to(-e.x_advance / 2, (-1.6 + i * 2.0) * k); c.show_text(ln)
    c.new_path(); c.restore()
    emoji(c, "😇", x - 30 * k, feet - 92 * k, 12 * k)


def intro_decor_house(c, t, u):
    """Gaslighting-Deko auf dem Haus aus der Fake-Feminist-Folge."""
    s_ = clamp(u)
    # flackerndes Licht in den Fenstern (Gaslight)
    lit = 0.5 + 0.5 * math.sin(t * 9) * math.sin(t * 3.1)
    for x in (290, 670):
        rrect(c, x + 4, 904, 112, 102, 6); src(c, "#F7C66B", (0.35 + 0.5 * lit) * s_); c.fill()
    c.arc(540, 730, 38, 0, 2 * math.pi); src(c, "#F7C66B", (0.35 + 0.5 * lit) * s_); c.fill()
    # flackernde Gaslampe vorne rechts im Garten
    g_ = gas_lamp
    c.save(); c.translate(1000, 1460); c.scale(0.75, 0.75); c.translate(-1000, -1460)
    g_(c, 1000, 1460, t, s_, 3)
    c.restore()
    intro_decor(c, t, u)
    # Nebel über dem Rasen
    for i in range(3):
        y = 1270 + i * 55; x = (t * 40 * (1 + i * 0.3)) % 600 - 300
        for k in range(4):
            c.save(); c.translate(x + k * 420, y); c.scale(1, 0.25); c.arc(0, 0, 260, 0, 2 * math.pi); c.restore()
            src(c, "#E8E0F0", (0.10 + 0.03 * i) * s_); c.fill()


INTRO.update(house=dict(sky=("#2E2350", "#A27CC0"), walls="#CFC3DD", roof="#3A2A55", door="#2E2440", lawn="#4F8A5A",
                        accent=("#4A2E6B", "#FFB547"), sun=False),
             umbrella=False, fill="#2E2350", decor=intro_decor_house,
             alex_extras=alex_extras, pose="shrug", expr="smug",
             burst=["🌀", "❓", "🤷", "🕯️", "🙄", "💭", "🚩", "😇"])


def draw_intro(c, t, shuffle, ticks, flash_start, reveal_t, role_text):
    draw_intro_house(c, t, shuffle, ticks, flash_start, reveal_t, role_text, INTRO)


def duo(c, S, alex_expr="smug", alex_pose="idle", lena_expr="neutral", lena_pop=0.2):
    t = S.t
    person(c, 320, FEET, AH, AL, t, alex_expr, alex_pose, name="Alex")
    scaled(c, 790, FEET, pop(t, S.at(0, lena_pop)),
           lambda: person(c, 790, FEET, AH * 0.97, LENA, t, lena_expr, name="Lena", blink_seed=3))


def confusion(c, t, x, y, s=1.0):
    for i in range(3):
        a = t * 2 + i * 2.1
        emoji(c, "🌀" if i != 1 else "❓", x + math.cos(a) * 60, y + math.sin(a) * 25, 60 * s, rot=t * 2)


def row_card(c, x, y, w, h, s, label, icon=None, size=40, num=None, rot=0.0):
    def d():
        rrect(c, x - w / 2 + 6, y - h / 2 + 10, w, h, 22); src(c, "#000000", 0.2); c.fill()
        rrect(c, x - w / 2, y - h / 2, w, h, 22); fill(c, "#FFFFFF")
        rrect(c, x - w / 2, y - h / 2, w, h, 22); c.set_line_width(5); src(c, INK); c.stroke()
        lx = x - w / 2 + 40
        if num is not None:
            c.arc(x - w / 2 + 75, y, 42, 0, 2 * math.pi); fill(c, "#4A2E6B")
            text(c, str(num), x - w / 2 + 75, y, 46, "#FFFFFF", FONT_HEAD)
            lx = x - w / 2 + 140
        text(c, label, lx, y, size, INK, FONT_HEAD, anchor="l")
        if icon:
            emoji(c, icon, x + w / 2 - 60, y, 56)
    scaled(c, x, y, s, d, rot)


def chat_msg(c, msg, x0, w, y, mine, s, size=30):
    if s <= 0:
        return 0
    lines = wrap(c, msg, size, w - 140, FONT_BOLD)
    bw = max(text_width(c, ln, size, FONT_BOLD) for ln in lines) + 44
    bh = len(lines) * size * 1.25 + 26
    bx = x0 + w - 24 - bw if mine else x0 + 24
    def d():
        rrect(c, bx, y - bh, bw, bh, 22)
        fill(c, "#3D8BFF" if mine else "#E6E6EA")
        for i, ln in enumerate(lines):
            text(c, ln, bx + 22, y - bh + 13 + size * 0.62 + i * size * 1.25, size, "#FFFFFF" if mine else INK,
                 FONT_BOLD, anchor="l")
    scaled(c, bx + (bw if mine else 0), y, s, d)
    return bh


# ======================================================================= SZENEN
def sc_what(c, S):
    t, a1 = S.t, S.at(1)
    s = pop(t, S.at(0, 0.0))
    def card_():
        card(c, W / 2, 680, 900, 560, 1)
        emoji(c, "🕯️", 200, 520, 110)
        text_block(c, "Du zweifelst an dem, was du selbst gesehen und gehört hast.", W / 2 + 60, 560, 40, 640, INK, FONT_HEAD)
        # Wahrnehmungs-Balken, der von "sicher" zu "unsicher" kippt
        u = ease_in_out((t - S.at(0, 0.4)) / 1.5)
        rrect(c, 160, 760, 760, 54, 27); fill(c, "#EDEDF0")
        rrect(c, 160, 760, max(54, 760 * (1 - 0.8 * u)), 54, 27); fill(c, "#2FA36B" if u < 0.5 else "#E23B3B")
        text(c, "Vertrauen in dich selbst", 160, 730, 30, "#555555", FONT_BOLD, anchor="l")
    scaled(c, W / 2, 680, s, card_)
    if t >= a1:
        bubble(c, "Das hab ich nie gesagt. 🤷", 845, 1200, pop(t, a1), tail=(-0.5, 1), size=40, max_w=330)
    person(c, W / 2, FEET, AH, AL, t, "smug", "shrug" if t >= a1 else "idle", name="Alex")


def sc_forgot(c, S):
    t = S.t
    s = pop(t, S.at(0, 0.0))
    def stop():
        rrect(c, 70, 380, 940, 620, 30); fill(c, "#9FB7C9")
        c.save(); rrect(c, 70, 380, 940, 620, 30); c.clip()
        for i in range(40):
            rnd = random.Random(i)
            x = rnd.uniform(70, 1010); y = (rnd.uniform(380, 1000) + t * 500) % 620 + 380
            c.move_to(x, y); c.line_to(x - 8, y + 26)
        c.set_line_width(3); src(c, "#FFFFFF", 0.6); c.stroke()
        emoji(c, "🚏", 260, 760, 200)
        person(c, 560, 960, 380, LENA, t, "sad", bob=False, name="Lena")
        emoji(c, "⌚", 700, 780, 70)
        c.restore()
        rrect(c, 70, 380, 940, 620, 30); c.set_line_width(6); src(c, INK); c.stroke()
        rrect(c, 640, 410, 340, 80, 16); fill(c, "#1F1F28")
        text(c, "08:45 … kein Alex", 810, 450, 32, "#FFFFFF", FONT_HEAD)
    scaled(c, W / 2, 690, s, stop)
    if t > S.at(0, 0.45):
        bubble(c, "Du hast doch gesagt, du nimmst den Bus 🤷", 845, 1215, pop(t, S.at(0, 0.45)), tail=(-0.5, 1), size=36, max_w=330)
    person(c, W / 2, FEET, AH, AL, t, "smug", "shrug" if t > S.at(0, 0.45) else "idle", name="Alex")


def sc_proof(c, S):
    t = S.t
    s = pop(t, S.at(0, 0.0))
    x0, y0, w, h = phone(c, W / 2, 690, 520, 780, s, screen="#FFFFFF")
    def screen():
        c.save(); rrect(c, x0, y0, w, h, 42); c.clip()
        rrect(c, x0, y0, w, 130, 0); fill(c, "#F4F4F6")
        c.arc(x0 + 70, y0 + 82, 30, 0, 2 * math.pi); fill(c, ALEX_BASE["hair"])
        text(c, "Alex", x0 + 115, y0 + 82, 32, INK, FONT_HEAD, anchor="l")
        chat_msg(c, "Ich hol dich morgen um 8 ab 😘", x0, w, y0 + 320, False, 1)
        if t > S.at(0, 0.2):
            hl = ease_out_cubic((t - S.at(0, 0.2)) / 0.4)
            c.set_line_width(8); src(c, "#FFD34D")
            rrect(c, x0 + 14, y0 + 220, (w - 60) * hl, 112, 26); c.stroke()
        text(c, "Gestern, 21:14", W / 2, y0 + 380, 24, "#999999", FONT_BOLD)
        c.restore()
    scaled(c, W / 2, 690, s, screen)
    emoji(c, "🔍", 860, 520, 120 * pop(t, S.at(0, 0.2)), rot=0.3)
    if t > S.at(0, 0.6):
        bubble(c, "Das hast du falsch verstanden 🙄", 845, 1205, pop(t, S.at(0, 0.6)), tail=(-0.5, 1), size=38, max_w=330)
    person(c, W / 2, FEET, AH, AL, t, "smug", "idle", name="Alex")


def sc_joke(c, S):
    t = S.t
    hurt = t > S.at(0, 0.35)
    def table():
        rrect(c, 140, 420, 800, 520, 20); fill(c, "#FFF4E6")
        rrect(c, 140, 420, 800, 520, 20); c.set_line_width(5); src(c, INK); c.stroke()
        for i, x in enumerate((300, 540, 780)):
            person(c, x, 880, 330, person_spec(120 + i, girl=bool(i % 2)), t, "cringe" if hurt else "happy", bob=False)
        rrect(c, 180, 830, 720, 40, 10); fill(c, "#B07A4F")
        emoji(c, "🍕", 540, 810, 70)
        text(c, "Freunde", W / 2, 470, 36, "#777777", FONT_HEAD)
    scaled(c, W / 2, 680, pop(t, S.at(0, 0.0)), table)
    if t > S.at(0, 0.15) and t < S.at(0, 0.6):
        text(c, "😂 „Witz“ über Lena", W / 2, 985, 44, "#FFFFFF", FONT_HEAD)
    if t > S.at(0, 0.6):
        bubble(c, "Du bist einfach zu empfindlich 🙄", 430, 990, pop(t, S.at(0, 0.6)), tail=(-0.4, 1), size=36, max_w=520)
    duo(c, S, "smug", "idle", "sad" if hurt else "happy", 0.0)
    if hurt:
        emoji(c, "💧", 860, 1250, 50)


def sc_fight(c, S):
    t = S.t
    u = ease_in_out((t - S.at(0, 0.25)) / 1.6)
    def scale_():
        card(c, W / 2, 690, 900, 560, 1)
        text(c, "WER IST SCHULD?", W / 2, 460, 50, INK, FONT_HEAD)
        # Schuld-Pfeil wandert von Alex zu Lena
        rrect(c, 160, 640, 760, 20, 10); fill(c, "#DDDDDD")
        text(c, "Alex", 200, 720, 40, INK, FONT_HEAD)
        text(c, "Lena", 880, 720, 40, INK, FONT_HEAD)
        x = 200 + 680 * u
        c.move_to(x - 30, 600); c.line_to(x + 30, 600); c.line_to(x, 640); c.close_path(); fill(c, "#E23B3B")
        text(c, "SCHULD", x, 575, 30, "#E23B3B", FONT_HEAD)
        if u > 0.95:
            text(c, "🔄 umgedreht", W / 2, 840, 40, "#4A2E6B", FONT_HEAD)
    scaled(c, W / 2, 690, pop(t, S.at(0, 0.0)), scale_)
    if t > S.at(0, 0.7):
        bubble(c, "Sorry … 😔", 790, 975, pop(t, S.at(0, 0.7)), tail=(0.3, 1), size=40)
    duo(c, S, "smug", "hips", "sad", 0.0)
    if S.at(0, 0.35) < t < S.at(0, 0.7):
        confusion(c, t, 790, 1110, 0.8)


def sc_signs(c, S):
    t = S.t
    items = [("„Das hab ich nie gesagt.“", "🤷"), ("„Du bist zu empfindlich.“", "🙄"),
             ("„Du bildest dir das ein.“", "🌀"), ("Am Ende bist DU schuld", "🔄")]
    for i, (lab, ic) in enumerate(items):
        y = 400 + i * 175
        row_card(c, W / 2, y, 1000, 160, pop(t, S.at(i + 1, 0.0)), lab, ic, 46, num=i + 1, rot=(-0.02 if i % 2 else 0.02))
    for i in range(3):
        emoji(c, "🚩", 140 + i * 400, 1110 + math.sin(t * 3 + i) * 12, 70 * pop(t, S.at(0, 0.2 + 0.15 * i)))
    person(c, W / 2, FEET, AH, AL, t, "smug", "shrug", name="Alex")


def sc_real(c, S):
    t = S.t
    s = pop(t, S.at(0, 0.0), 0.45)
    def heart():
        card(c, W / 2, 680, 880, 560, 1, color="#FFF7FA")
        emoji(c, "🧠", 330, 610, 160)
        emoji(c, "🫂", 750, 610, 160)
        text_block(c, "Vertrau deiner Wahrnehmung. 🤍", W / 2, 830, 50, 780, INK, FONT_HEAD)
    scaled(c, W / 2, 680, s, heart)
    scaled(c, 790, FEET, 1, lambda: person(c, 790, FEET, AH * 0.97, LENA, t, "happy", name="Lena", blink_seed=3))
    emoji(c, "💪", 920, 1250, 70 * pop(t, S.at(0, 0.4)))


def sc_outro(c, S):
    t, a1 = S.t, S.at(1)
    q = "Kennst du jemanden, der auch immer sagt: „Das hab ich nie gesagt“?" if t < a1 else "Was soll Alex morgen sein?"
    qs = pop(t, S.at(0, 0.0)) if t < a1 else pop(t, a1)
    card(c, W / 2, 230, 1000, 220, qs)
    scaled(c, W / 2, 230, qs, lambda: text_block(c, q, W / 2, 230, 52, 940, INK, FONT_HEAD))
    if t < a1 + 0.2:
        out = 1 - ease_out_cubic((t - a1) / 0.2) if t > a1 else 1
        s = pop(t, S.at(0, 0.3)) * out
        def tag():
            c.arc(W / 2, 640, 210, 0, 2 * math.pi); fill(c, "#FFFFFF")
            c.arc(W / 2, 640, 210, 0, 2 * math.pi); c.set_line_width(8); src(c, INK); c.stroke()
            text(c, "@", W / 2, 625, 300, "#4A2E6B", FONT_HEAD)
            rrect(c, 160, 900, 760, 100, 50); fill(c, "#FFFFFF")
            rrect(c, 160, 900, 760, 100, 50); c.set_line_width(5); src(c, INK); c.stroke()
            typed = "@hab_ich_nie_gesagt"
            n = int(clamp((t - S.at(0, 0.4)) / 1.0) * len(typed))
            cur = "|" if int(t * 3) % 2 == 0 else ""
            text(c, typed[:n] + cur, 200, 950, 40, "#3D8BFF", FONT_HEAD, anchor="l")
        scaled(c, W / 2, 700, s, tag, rot=math.sin(t * 4) * 0.02)
        emoji(c, "👇", 880, 1110 + math.sin(t * 8) * 12, 90 * pop(t, S.at(0, 0.6)) * out)
    if t >= a1:
        colors = ["#EC7FAE", "#3E5C9A", "#1F3A6B", "#4A2E6B", "#3E7BDA", "#8E5BE0", "#36B5C2", "#F07F4F", "#555A66"]
        # TikTok-Reihenfolge: 1 Pick-me-Boy, 2 Emotional abhängig, heute 3
        prev = [("🌹", "FOLGE 1"), ("🥺", "FOLGE 2"), ("🌀", "HEUTE ✅")]
        for i in range(9):
            r, cc = i // 3, i % 3
            x, y = 250 + cc * 290, 445 + r * 192
            def icon(x=x, y=y, i=i):
                c.arc(x, y, 88, 0, 2 * math.pi); fill(c, colors[i])
                c.arc(x, y, 88, 0, 2 * math.pi); c.set_line_width(7); src(c, "#FFFFFF"); c.stroke()
                if i < len(prev):
                    e, lab = prev[i]
                    emoji(c, e, x, y, 100)
                    rrect(c, x - 88, y + 58, 176, 48, 12); fill(c, "#2FA36B" if i == len(prev) - 1 else "#555A66")
                    text(c, lab, x, y + 82, 30, "#FFFFFF", FONT_HEAD)
                else:
                    text(c, "?", x, y, 110, "#FFFFFF", FONT_HEAD)
            scaled(c, x, y, pop(t, a1 + 0.1 + i * 0.07), icon)
        ps = pop(t, S.at(1, 0.45))
        def pill():
            rrect(c, 100, 955, 880, 116, 58); fill(c, "#E23B3B")
            rrect(c, 100, 955, 880, 116, 58); c.set_line_width(6); src(c, "#FFFFFF"); c.stroke()
            text(c, "Schreib's in die Kommentare ⬇️", W / 2, 1013, 54, "#FFFFFF", FONT_HEAD)
        scaled(c, W / 2, 1013, ps * (1 + 0.04 * math.sin(t * 7)), pill)
    person(c, W / 2, FEET, AH, AL, t, "happy", "wave", name="Alex")


SCENE_DRAW = dict(what=sc_what, forgot=sc_forgot, proof=sc_proof, joke=sc_joke, fight=sc_fight,
                  signs=sc_signs, real=sc_real, outro=sc_outro)
