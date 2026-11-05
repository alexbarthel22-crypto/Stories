"""Visuals: Alex ist heute eine Dorfmatratze (TikTok Folge 4). Nicht explizit – Humor: im Dorf kennt jeder jeden."""
import math, random
from alexlib import *

# Outfit: Holzfäller-Karohemd, Jeans
# Fuckboy-Look, bewusst etwas billig: schwarzes Muskelshirt, dicke Goldkette, Pump, helle Jeans
AL = alex(top="#1C1C22", top_style="tank", pump=True, chain="#D4AF37", pants="#8FB3D9", shoes="#FFFFFF")
FEET, AH = 1690, 560
JANA = person_spec(31, girl=True, top="#F2B233", hair="#C98B4A", skin="#F1C9A8")
LENA = person_spec(4, girl=True, top="#46B39A", hair="#6B3E26", skin="#EBB894", pants="#3F4A6B", shoes="#2A2A2A")
SOPHIE = person_spec(14, girl=True, top="#F07FB0", hair="#5A3A22", skin="#F1C9A8")
MUTTER = person_spec(55, girl=True, hair_style="bun", hair="#8A6A55", top="#7A5C45", skin="#F1C9A8")
ONKEL = person_spec(56, hair="#6B6B6B", top="#2E3A8C", skin="#E9B48A")


# ---------------------------------------------------------------- Intro: Dorf-Haus
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
    # Herz-Lichterkette über dem Dach (blinkt)
    for i in range(14):
        x = 205 + i * 52; y = 830 + 26 * math.sin(math.pi * i / 13)
        on = (int(t * 4) + i) % 2 == 0
        emoji(c, "❤️" if on else "🩷", x, y + 14, 34 * s_)
    # Fachwerk-Balken
    c.save(); rrect(c, 220, 820, 640, 440, 6); c.clip()
    c.set_line_width(14); src(c, "#5A3A22", s_)
    for x in (230, 420, 660, 850):
        c.move_to(x, 820); c.line_to(x, 1260)
    for y in (880, 1060):
        c.move_to(220, y); c.line_to(860, y)
    c.stroke(); c.restore()
    # Fenster: links rotes Herz-Licht, rechts Oma Hilde guckt raus
    rrect(c, 294, 904, 112, 102, 6); src(c, "#FF4D7A", (0.45 + 0.25 * math.sin(t * 3)) * s_); c.fill()
    emoji(c, "💋", 350, 955, 56 * s_)
    peek = 0.5 + 0.5 * math.sin(t * 2)
    c.save(); rrect(c, 670, 900, 120, 110, 8); c.clip()
    emoji(c, "👵", 700 + 30 * peek, 960, 80 * s_)
    src(c, "#FFFFFF", 0.95); c.rectangle(670, 900, 40 + 30 * (1 - peek), 110); c.fill()
    c.restore()
    emoji(c, "👀", 730, 870, 46 * s_)
    # Tür steht offen + Fußmatte "Komm rein"
    rrect(c, 480, 1080, 120, 180, 6); fill(c, "#2A1A20")
    c.move_to(480, 1080); c.line_to(440, 1100); c.line_to(440, 1250); c.line_to(480, 1260); c.close_path(); fill(c, "#C0392B")
    rrect(c, 455, 1250, 170, 30, 6); fill(c, "#8A3A3A")
    text(c, "KOMM REIN 😏", 540, 1265, 20, "#FFFFFF", FONT_HEAD)
    # Neon-Schild "OPEN 24/7"
    def neon():
        glow = 0.7 + 0.3 * (1 if int(t * 3) % 4 else 0.2)
        rrect(c, 232, 1110 - 40, 196, 80, 18); src(c, "#1C1C22", 0.92); c.fill()
        rrect(c, 232, 1110 - 40, 196, 80, 18); c.set_line_width(5); src(c, "#FF4DB8", glow); c.stroke()
        text(c, "OPEN", 330, 1094, 30, "#FF9FE0", FONT_HEAD, alpha=glow)
        text(c, "24/7 💘", 330, 1128, 26, "#FF9FE0", FONT_HEAD, alpha=glow)
    scaled(c, 330, 1110, s_, neon)
    # Schilder vorne
    _sign(c, 200, 1650, "Tür immer offen 🚪", "#FFFFFF", -0.1, 42, 340)
    _sign(c, 880, 1650, "Ich rammel alles 🐰", "#FFB3D9", 0.08, 42, 340)
    # Herzen fliegen
    for i in range(5):
        u2 = (t * 0.35 + i / 5) % 1
        emoji(c, "💔" if i % 2 else "💋", 120 + i * 210, 1250 - u2 * 160, 46, alpha=0.8 * (1 - u2))


def alex_extras(c, x, feet, h, t, u):
    """Fuckboy, etwas billig: Sonnenbrille im Haar, dicke Goldkette, Bierdose, Zwinkern."""
    k = h / 100.0
    # Sonnenbrille, ins Haar hochgeschoben (gezeichnet, sitzt auf der Stirn/Haaransatz)
    c.save(); c.translate(x, feet - 84.5 * k); c.rotate(-0.04)
    c.set_line_width(0.9 * k); src(c, "#111111")
    c.move_to(-16.8 * k, 1.6 * k); c.line_to(-11.6 * k, 0.2 * k); c.move_to(16.8 * k, 1.6 * k); c.line_to(11.6 * k, 0.2 * k); c.stroke()
    for sx in (-1, 1):
        rrect(c, sx * 6.2 * k - 5.6 * k, -3.4 * k, 11.2 * k, 7.0 * k, 3.0 * k)
        g = cairo.LinearGradient(0, -3.4 * k, 0, 3.6 * k)
        g.add_color_stop_rgb(0, 0.32, 0.30, 0.38); g.add_color_stop_rgb(1, 0.06, 0.06, 0.09)
        c.set_source(g); c.fill_preserve(); c.set_line_width(0.8 * k); src(c, "#111111"); c.stroke()
        c.set_line_width(0.6 * k); src(c, "#FFFFFF", 0.55)
        c.move_to(sx * 6.2 * k - 3.2 * k, -1.8 * k); c.line_to(sx * 6.2 * k - 0.6 * k, -2.6 * k); c.stroke()
    c.set_line_width(1.0 * k); src(c, "#111111")
    c.move_to(-0.9 * k, -1.2 * k); c.curve_to(-0.3 * k, -2.2 * k, 0.3 * k, -2.2 * k, 0.9 * k, -1.2 * k); c.stroke()
    c.restore()
    c.set_line_width(1.6 * k); src(c, "#D4AF37")
    c.move_to(x - 7 * k, feet - 56 * k); c.curve_to(x - 5 * k, feet - 44 * k, x + 5 * k, feet - 44 * k, x + 7 * k, feet - 56 * k); c.stroke()
    c.arc(x, feet - 45 * k, 2.2 * k, 0, 2 * math.pi); src(c, "#D4AF37"); c.fill()
    emoji(c, "🍺", x + 36 * k, feet - 30 * k, 12 * k, rot=0.1)
    emoji(c, "😉", x - 30 * k, feet - 94 * k, 12 * k)


INTRO = dict(icon="🏘️", bg="#5E8C3A", spec=AL, expr="smug", pose="hips", hand_prop=None,
             house=dict(sky=("#7A4FA0", "#FF9FB8"), walls="#F7D6E0", roof="#8A2A3A", door="#2A1A20", lawn="#5DAA5E",
                        accent=("#E0457B", "#1C1C22"), sun=False),
             umbrella=False, title_lines=["DORF-", "MATRATZE."], fill="#6FB7E8", decor=intro_decor, alex_extras=alex_extras,
             burst=["💋", "💔", "🏘️", "👵", "🍺", "😏", "👀", "💘"])


def draw_intro(c, t, shuffle, ticks, flash_start, reveal_t, role_text):
    draw_intro_house(c, t, shuffle, ticks, flash_start, reveal_t, role_text, INTRO)


# ---------------------------------------------------------------- Helfer
def alex_bottom(c, S, expr="smug", pose="idle", prop=None, x=W / 2, h=AH):
    person(c, x, FEET, h, AL, S.t, expr, pose, prop, name="Alex")


def out_fade(t, t_end, d=0.2):
    return 1 - ease_out_cubic((t - t_end) / d) if t > t_end else 1


def row_card(c, x, y, w, h, s, label, icon=None, size=40, num=None, rot=0.0):
    def d():
        rrect(c, x - w / 2 + 6, y - h / 2 + 10, w, h, 22); src(c, "#000000", 0.2); c.fill()
        rrect(c, x - w / 2, y - h / 2, w, h, 22); fill(c, "#FFFFFF")
        rrect(c, x - w / 2, y - h / 2, w, h, 22); c.set_line_width(5); src(c, INK); c.stroke()
        lx = x - w / 2 + 40
        if num is not None:
            c.arc(x - w / 2 + 75, y, 42, 0, 2 * math.pi); fill(c, "#5E8C3A")
            text(c, str(num), x - w / 2 + 75, y, 46, "#FFFFFF", FONT_HEAD)
            lx = x - w / 2 + 140
        text(c, label, lx, y, size, INK, FONT_HEAD, anchor="l")
        if icon:
            emoji(c, icon, x + w / 2 - 60, y, 56)
    scaled(c, x, y, s, d, rot)


def tag(c, x, y, txt, col="#E23B3B", s=1.0):
    def d():
        w = text_width(c, txt, 30, FONT_HEAD) + 36
        rrect(c, x - w / 2, y - 26, w, 52, 14); fill(c, col)
        text(c, txt, x, y, 30, "#FFFFFF", FONT_HEAD)
    scaled(c, x, y, s, d)


def chat_msg(c, who, msg, x0, w, y, s, col):
    if s <= 0:
        return 0
    lines = wrap(c, msg, 28, w - 150, FONT_BOLD)
    bw = max(text_width(c, ln, 28, FONT_BOLD) for ln in lines) + 44
    bh = len(lines) * 35 + 62
    def d():
        rrect(c, x0 + 24, y, bw, bh, 22); fill(c, "#E6E6EA")
        text(c, who, x0 + 46, y + 24, 22, col, FONT_HEAD, anchor="l")
        for i, ln in enumerate(lines):
            text(c, ln, x0 + 46, y + 56 + i * 35, 28, INK, FONT_BOLD, anchor="l")
    scaled(c, x0 + 24, y, s, d)
    return bh


def box_fx(c, t, t0, x, y, w, h, kind="anger"):
    """Effekte um eine Szenen-Box: anger (rot pulsierend, 💢, Dampf), love (Herzen), shock (Blitze), party (Konfetti)."""
    if t < t0:
        return
    u = t - t0
    a = clamp(u / 0.25)
    if kind == "anger":
        pulse = 0.5 + 0.5 * math.sin(u * 12)
        for i in range(3):
            rrect(c, x - w / 2 - 10 - i * 9, y - h / 2 - 10 - i * 9, w + 20 + i * 18, h + 20 + i * 18, 30 + i * 9)
            c.set_line_width(7); src(c, "#FF3B3B", a * (0.55 - 0.15 * i) * (0.6 + 0.4 * pulse)); c.stroke()
        for (dx, dy) in ((-0.48, -0.48), (0.48, -0.5), (0.5, 0.45)):
            emoji(c, "💢", x + dx * w, y + dy * h, 70 * a * (1 + 0.15 * pulse))
        for i in range(2):
            uu = (u * 0.9 + i * 0.5) % 1
            emoji(c, "💨", x + w * 0.42, y - h * 0.5 - uu * 90, 60, rot=-0.4, alpha=a * (1 - uu))
            emoji(c, "💨", x - w * 0.42, y - h * 0.5 - uu * 90, 60, rot=0.4, alpha=a * (1 - uu))
    elif kind == "love":
        for i in range(8):
            ang = i / 8 * 2 * math.pi + u * 0.8
            rr = 1 + 0.06 * math.sin(u * 6 + i)
            emoji(c, "💘" if i % 2 else "💕", x + math.cos(ang) * w * 0.55 * rr, y + math.sin(ang) * h * 0.6 * rr, 54 * a)
    elif kind == "shock":
        for i in range(10):
            ang = i / 10 * 2 * math.pi
            r0 = max(w, h) * 0.5 + 20; r1 = r0 + 40 + 20 * math.sin(u * 20 + i)
            c.set_line_width(8); c.set_line_cap(cairo.LINE_CAP_ROUND); src(c, "#FFE14D", a)
            c.move_to(x + math.cos(ang) * r0 * w / max(w, h), y + math.sin(ang) * r0 * h / max(w, h))
            c.line_to(x + math.cos(ang) * r1 * w / max(w, h), y + math.sin(ang) * r1 * h / max(w, h)); c.stroke()
        emoji(c, "😱", x + w * 0.45, y - h * 0.5, 70 * a)
    elif kind == "party":
        rnd = random.Random(9)
        for i in range(18):
            px = x + rnd.uniform(-0.55, 0.55) * w
            py = y - h * 0.55 + ((u * rnd.uniform(120, 220) + rnd.uniform(0, h)) % (h * 1.1))
            c.save(); c.translate(px, py); c.rotate(u * 3 + i)
            rrect(c, -7, -12, 14, 24, 3); src(c, rnd.choice(["#F7C948", "#FF5CA8", "#36B5C2", "#2FA36B"]), a); c.fill()
            c.restore()


# ---------------------------------------------------------------- Szenen
def sc_what(c, S):
    t, a1 = S.t, S.at(1)
    s = pop(t, S.at(0, 0.0))
    def card_():
        card(c, W / 2, 700, 980, 620, 1)
        c.save(); c.translate(W / 2, 480)
        rrect(c, -300, -60, 600, 120, 10); fill(c, "#F7D21B")
        rrect(c, -288, -48, 576, 96, 6); c.set_line_width(5); src(c, INK); c.stroke()
        text(c, "WENTORF", 0, -10, 50, INK, FONT_HEAD)
        text(c, "bei Hamburg", 0, 28, 26, INK, FONT_BOLD)
        c.restore()
        rnd = random.Random(4)
        for i in range(30):
            r, cc = i // 10, i % 10
            x, y = 155 + cc * 85, 640 + r * 105
            emoji(c, rnd.choice(["🧑", "👩", "👨", "👱", "👵"]), x, y, 62)
            if t > a1 and i < int(30 * clamp((t - a1) / 2.0)) and rnd.random() < 0.85:
                emoji(c, "💔", x + 22, y - 22, 34)
    scaled(c, W / 2, 700, s, card_)
    if t > a1:                                    # kleines Einwohner-Schild (rechts, im Sicherheitsbereich)
        def sign():
            c.rectangle(812, 1150, 16, 230); fill(c, "#8A8F98")
            rrect(c, 715, 1050, 210, 120, 12); fill(c, "#FFFFFF")
            rrect(c, 715, 1050, 210, 120, 12); c.set_line_width(5); src(c, INK); c.stroke()
            rrect(c, 727, 1062, 186, 96, 6); c.set_line_width(3); src(c, "#2E7D4F"); c.stroke()
            text(c, "Einwohner", 820, 1088, 30, INK, FONT_BOLD)
            text(c, "463", 820, 1132, 48, "#2E7D4F", FONT_HEAD)
        scaled(c, 820, 1380, pop(t, a1 + 0.2), sign)
    alex_bottom(c, S, "smug", "hips")


def sc_motto(c, S):
    t = S.t
    s = pop(t, S.at(0, 0.0))
    d0 = S.at(0, 0.0)
    span = max(0.9, S.S.durs[0] * 0.85)
    k = clamp((t - d0) / span)
    n = min(3, 1 + int(3 * k))
    sway = math.sin(t * 2.2) * 0.025 + (0.05 * math.sin(t * 18) * max(0, 1 - (t - d0 - span) / 0.6) if t > d0 + span else 0)
    def scene():
        # Himmel, Hügel, Wiese
        rrect(c, 60, 360, 960, 700, 26)
        g = cairo.LinearGradient(0, 360, 0, 1060)
        g.add_color_stop_rgb(0, 0.62, 0.84, 1.0); g.add_color_stop_rgb(1, 0.88, 0.95, 1.0)
        c.set_source(g); c.fill()
        c.save(); rrect(c, 60, 360, 960, 700, 26); c.clip()
        c.arc(860, 470, 50, 0, 2 * math.pi); src(c, "#FFE27A"); c.fill()
        c.move_to(60, 930); c.curve_to(300, 860, 600, 900, 1020, 880); c.line_to(1020, 1060); c.line_to(60, 1060); c.close_path(); src(c, "#7FC77F"); c.fill()
        c.rectangle(60, 960, 960, 100); src(c, "#5DAA5E"); c.fill()
        for i in range(60):
            rnd = random.Random(i); gx = rnd.uniform(70, 1010)
            c.move_to(gx, 975); c.line_to(gx + rnd.uniform(-6, 6) + math.sin(t * 3 + i) * 3, 955)
        c.set_line_width(3); src(c, "#3F8A47"); c.stroke()
        # Baum mit Wurzeln, Rinde, Ästen, schaukelnder Krone
        bx, by = 540, 975
        c.save(); c.translate(bx, by); c.rotate(sway); c.translate(-bx, -by)
        for dx in (-60, 60):
            c.move_to(bx + dx * 0.4, by - 30); c.curve_to(bx + dx * 0.7, by - 10, bx + dx, by - 4, bx + dx * 1.3, by); c.set_line_width(16); src(c, "#6B4226"); c.stroke()
        c.move_to(bx - 42, by); c.curve_to(bx - 34, by - 160, bx - 30, by - 250, bx - 26, by - 330)
        c.line_to(bx + 26, by - 330); c.curve_to(bx + 30, by - 250, bx + 34, by - 160, bx + 42, by); c.close_path()
        g = cairo.LinearGradient(bx - 42, 0, bx + 42, 0)
        g.add_color_stop_rgb(0, 0.36, 0.22, 0.12); g.add_color_stop_rgb(0.5, 0.52, 0.33, 0.18); g.add_color_stop_rgb(1, 0.30, 0.18, 0.10)
        c.set_source(g); c.fill()
        c.set_line_width(2.5); src(c, "#3A2414", 0.6)
        for i in range(6):
            yy = by - 40 - i * 48
            c.move_to(bx - 20 + (i % 2) * 8, yy); c.curve_to(bx - 10, yy - 14, bx + 6, yy - 10, bx + 14 - (i % 2) * 6, yy - 26); c.stroke()
        c.set_line_width(18); src(c, "#5A381F")
        c.move_to(bx - 10, by - 300); c.curve_to(bx - 80, by - 360, bx - 150, by - 380, bx - 200, by - 430); c.stroke()
        c.move_to(bx + 10, by - 290); c.curve_to(bx + 90, by - 350, bx + 160, by - 360, bx + 210, by - 420); c.stroke()
        rnd = random.Random(7)
        blobs = [(0, -470, 150), (-160, -430, 120), (170, -420, 120), (-90, -560, 120), (100, -560, 120), (0, -380, 120),
                 (-230, -360, 90), (240, -350, 90)]
        for dx, dy, r in blobs:
            c.arc(bx + dx + 6, by + dy + 10, r, 0, 2 * math.pi); src(c, "#2C6E35"); c.fill()
        for dx, dy, r in blobs:
            g = cairo.RadialGradient(bx + dx - r * 0.3, by + dy - r * 0.4, r * 0.1, bx + dx, by + dy, r)
            g.add_color_stop_rgb(0, 0.42, 0.75, 0.38); g.add_color_stop_rgb(1, 0.20, 0.52, 0.24)
            c.arc(bx + dx, by + dy, r, 0, 2 * math.pi); c.set_source(g); c.fill()
        for i in range(40):
            ang = rnd.uniform(0, 2 * math.pi); rr = rnd.uniform(40, 230)
            c.arc(bx + math.cos(ang) * rr, by - 460 + math.sin(ang) * rr * 0.6, rnd.uniform(8, 16), 0, 2 * math.pi)
            src(c, "#5FAE55", 0.6); c.fill()
        c.restore()
        # fallende Blätter
        for i in range(10):
            rnd = random.Random(30 + i)
            uu = ((t - d0) * rnd.uniform(0.25, 0.45) + rnd.random()) % 1
            lx = bx + rnd.uniform(-260, 260) + math.sin(uu * 8 + i) * 30
            emoji(c, "🍃", lx, 520 + uu * 440, 38, rot=uu * 6 + i, alpha=0.9 * (1 - uu))
        # Dorfbewohner klettern hektisch hoch (eigene Figuren, Arme hoch)
        climbers = [(person_spec(201, girl=True), -18, 0.00, 0), (person_spec(202), 22, 0.12, 1),
                    (person_spec(203, girl=True), -24, 0.24, 2), (person_spec(5, girl=True, hair_style="bun", hair="#C9C9CF", glasses=True), 18, 0.40, 3)]
        tops = [by - 560, by - 470, by - 400, by - 330]
        for sp, dx, f, j in climbers:
            kk = clamp((t - d0 - f * span) / (span * 0.75))
            y = by - (by - tops[j]) * ease_in_out(kk)
            wig = math.sin(t * 16 + j) * 6 * (1 - kk ** 3)
            person(c, bx + dx + wig + math.sin(sway) * (by - y) * 0.8, y + 40, 150, sp, t, "shock", "up", bob=False, blink_seed=j)
        # Schweißtropfen-Schreck beim Klettern
        if 0.1 < k < 1:
            emoji(c, "💦", bx + 120, 700 - 200 * k, 40)
        c.restore()
        rrect(c, 60, 360, 960, 700, 26); c.set_line_width(6); src(c, INK); c.stroke()
        # Countdown
        uu = ((t - d0) / span * 3) % 1 if k < 1 else 1
        sc_ = 1 + 0.35 * (1 - ease_out_cubic(uu))
        c.save(); c.translate(860, 470); c.scale(sc_, sc_)
        txt = f"{n}…" if k < 1 else "3!"
        text(c, txt, 0, 4, 120, "#000000", FONT_HEAD, alpha=0.25)
        text(c, txt, 0, 0, 120, "#E23B3B", FONT_HEAD)
        c.restore()
    scaled(c, W / 2, 710, s, scene)
    if k >= 1:
        box_fx(c, t, d0 + span, W / 2, 710, 960, 700, "shock")
    alex_bottom(c, S, "smug", "hips")
    if t > d0 + 0.3:
        bubble(c, "1 … 2 … 😏", 845, 1200, pop(t, d0 + 0.3), tail=(-0.5, 1), size=40, max_w=300)


def sc_bakery(c, S):
    t, a1 = S.t, S.at(1)
    s = pop(t, S.at(0, 0.0))
    def shop():
        rrect(c, 90, 380, 900, 660, 24); fill(c, "#FFF4E0")
        rrect(c, 90, 380, 900, 660, 24); c.set_line_width(6); src(c, INK); c.stroke()
        for i in range(9):
            c.rectangle(90 + i * 100, 380, 100, 80); src(c, "#C0392B" if i % 2 == 0 else "#FFFFFF"); c.fill()
        rrect(c, W / 2 - 230, 395, 460, 60, 14); fill(c, INK)
        text(c, "BÄCKEREI MÜLLER", W / 2, 425, 36, "#FFFFFF", FONT_HEAD)
        person(c, 380, 900, 380, JANA, t, "happy" if t > S.at(2) else "cringe", bob=False, name="Ex")
        if t > a1:
            person(c, 700, 900, 400, MUTTER, t, "angry", bob=False, name="ihre Mutter")
        rrect(c, 110, 880, 860, 150, 14); fill(c, "#B07A4F")
        rrect(c, 110, 880, 860, 150, 14); c.set_line_width(5); src(c, INK); c.stroke()
        for i, e in enumerate(("🥐", "🥨", "🍞", "🥯", "🍩", "🥐")):
            emoji(c, e, 190 + i * 140, 940, 70)
    shake = math.sin(t * 50) * 6 if a1 < t < a1 + 0.5 else 0
    c.save(); c.translate(shake, 0)
    scaled(c, W / 2, 710, s, shop)
    c.restore()
    a2 = S.at(2)
    if t < a2:
        box_fx(c, t, a1 + 0.1, W / 2, 710, 900, 660, "anger")
    else:
        # Geheimnis: Ex ahnt nichts, Mutter auch Ex
        tag(c, 700, 848, "AUCH EX 🤫", "#7A3FA8", s=pop(t, a2 + 0.3))
        tag(c, 380, 848, "WEISS NIX 🙈", "#2FA36B", s=pop(t, a2 + 0.6))
        box_fx(c, t, a2 + 0.3, W / 2, 710, 900, 660, "shock")
    alex_bottom(c, S, "cringe", "idle")
    if t > S.at(0, 0.6):
        emoji(c, "💦", 640, 1270, 60)


def sc_bus(c, S):
    t, a1 = S.t, S.at(1)
    s = pop(t, S.at(0, 0.0))
    def bus():
        rrect(c, 70, 460, 940, 470, 50); fill(c, "#F2B233")
        rrect(c, 70, 460, 940, 470, 50); c.set_line_width(6); src(c, INK); c.stroke()
        text(c, "LINIE 1 · DORF ↔ STADT", W / 2, 510, 34, INK, FONT_HEAD)
        for i in range(4):
            x = 110 + i * 225
            rrect(c, x, 550, 200, 220, 16); fill(c, "#BFE6FF")
            rrect(c, x, 550, 200, 220, 16); c.set_line_width(5); src(c, INK); c.stroke()
            c.save(); rrect(c, x, 550, 200, 220, 16); c.clip()
            sp = [ONKEL, JANA, LENA, SOPHIE][i]
            person(c, x + 100, 1010, 520, sp, t, "neutral" if i == 0 else "cringe", bob=False)
            c.restore()
        for x in (230, 850):
            c.arc(x, 930, 60, 0, 2 * math.pi); fill(c, "#2B2B2B"); c.arc(x, 930, 25, 0, 2 * math.pi); fill(c, "#AAAAAA")
    scaled(c, W / 2, 700, s, bus)
    for i, x in enumerate((435, 660, 885)):
        tag(c, x, 820, "EX", s=pop(t, S.at(0, 0.3 + 0.15 * i)))
    a2 = S.at(2)
    if t > a1:
        tag(c, 210, 820, "ONKEL VON EX", "#3E7BDA", s=pop(t, a1 + 0.1))
    if t > a2:
        tag(c, 210, 885, "+ AUCH EX 😳", "#E23B3B", s=pop(t, a2 + 0.1))
        box_fx(c, t, a2 + 0.1, W / 2, 700, 940, 480, "shock")
    else:
        box_fx(c, t, S.at(0, 0.3), W / 2, 700, 940, 480, "love")
    alex_bottom(c, S, "smug" if t > a2 else ("shock" if t > a1 else "cringe"), "shrug" if t > a2 else "idle")


def sc_group(c, S):
    t, a1 = S.t, S.at(1)
    s = pop(t, S.at(0, 0.0))
    x0, y0, w, h = phone(c, W / 2, 720, 600, 880, s, screen="#FFFFFF")
    def screen():
        c.save(); rrect(c, x0, y0, w, h, 42); c.clip()
        rrect(c, x0, y0, w, 130, 0); fill(c, "#2FA36B")
        text(c, "Wentorf-News 🏘️", x0 + 40, y0 + 62, 34, "#FFFFFF", FONT_HEAD, anchor="l")
        text(c, "1.204 Mitglieder", x0 + 40, y0 + 100, 22, "#E8FFE8", FONT_BOLD, anchor="l")
        y = y0 + 160
        msgs = [("Oma Hilde", "Hab den Alex gestern gesehen 👀", "#C0392B", 0.1),
                ("Gerd", "Mit wem??", "#3E7BDA", 0.45),
                ("Tina", "Nicht schon wieder 😂😂", "#8E5BE0", 0.75)]
        for who, m, col, f in msgs:
            if t > S.at(0, f):
                y += chat_msg(c, who, m, x0, w, y, pop(t, S.at(0, f), 0.2), col) + 16
        if t > a1:
            y += chat_msg(c, "Oma Hilde", "📷 Foto", x0, w, y, pop(t, a1 + 0.1, 0.2), "#C0392B") + 16
        if t > a1 + 0.9:
            y += chat_msg(c, "Gerd", "Der rammelt auch alles 😂", x0, w, y, pop(t, a1 + 0.9, 0.2), "#3E7BDA") + 16
        c.restore()
        if t > a1:
            n = min(99, int(99 * clamp((t - a1) / 1.2)))
            c.arc(x0 + w - 6, y0 + 6, 46, 0, 2 * math.pi); fill(c, "#E23B3B")
            text(c, f"{n}+", x0 + w - 6, y0 + 6, 32, "#FFFFFF", FONT_HEAD)
    scaled(c, W / 2, 720, s, screen)
    alex_bottom(c, S, "cringe", "phone", "📱", x=880, h=AH * 0.85)


def sc_fest(c, S):
    t, a1 = S.t, S.at(1)
    s = pop(t, S.at(0, 0.0))
    def tent():
        for i in range(10):
            c.move_to(90 + i * 90, 470); c.line_to(540, 380); c.line_to(90 + (i + 1) * 90, 470); c.close_path()
            src(c, "#FFFFFF" if i % 2 else "#2E3A8C"); c.fill()
        c.rectangle(90, 470, 900, 470); src(c, "#FFF4E0"); c.fill()
        c.rectangle(90, 470, 900, 470); c.set_line_width(6); src(c, INK); c.stroke()
        for i in range(14):
            x = 110 + i * 62
            c.move_to(x, 500); c.line_to(x + 31, 540); c.line_to(x + 62, 500); c.close_path()
            src(c, ["#C0392B", "#F2B233", "#2FA36B", "#3E7BDA"][i % 4]); c.fill()
        text(c, "SCHÜTZENFEST 🎉", W / 2, 590, 46, INK, FONT_HEAD)
        emoji(c, "🍺", 160, 870, 70); emoji(c, "🥨", 920, 870, 70)
        if t > a1:
            person(c, 380, 935, 250, LENA, t, "angry", bob=False, name="Lena")
            person(c, 700, 935, 250, SOPHIE, t, "angry", bob=False, name="Sophie")
    scaled(c, W / 2, 700, s, tent)
    box_fx(c, t, 0.2, W / 2, 660, 900, 560, "party")
    if t > a1:
        box_fx(c, t, a1 + 0.2, W / 2, 700, 900, 470, "anger")
    if t > a1 + 0.6:
        def cous():
            rrect(c, 270, 975, 540, 74, 37); fill(c, "#FFE14D")
            rrect(c, 270, 975, 540, 74, 37); c.set_line_width(5); src(c, INK); c.stroke()
            text(c, "ALLE DREI COUSINEN 👯", W / 2, 1012, 36, INK, FONT_HEAD)
        scaled(c, W / 2, 1012, pop(t, a1 + 0.6), cous)
    sway = math.sin(t * 4) * 15
    person(c, 380 + sway, FEET, AH * 0.95, AL, t, "happy", "wave", name="Alex")
    person(c, 720 - sway, FEET, AH * 0.92, JANA, t, "happy", "wave", name="Jana", blink_seed=2)
    emoji(c, "🎶", 550, 1180 + math.sin(t * 5) * 10, 60)


def sc_night(c, S):
    t, a1 = S.t, S.at(1)
    s = pop(t, S.at(0, 0.0))
    def street():
        rrect(c, 70, 380, 940, 680, 30); fill(c, "#1E2440")
        c.save(); rrect(c, 70, 380, 940, 680, 30); c.clip()
        emoji(c, "🌙", 880, 470, 90)
        for x0 in (90, 560):
            rrect(c, x0, 560, 420, 500, 6); fill(c, "#3A3050")
            rrect(c, x0 + 60, 640, 120, 120, 6); src(c, "#F7C66B", 0.9); c.fill()
            rrect(c, x0 + 240, 640, 120, 120, 6); src(c, "#F7C66B", 0.25); c.fill()
        wob = 0.5 + 0.5 * math.sin(t * 6)
        c.save(); rrect(c, 800, 640, 120, 120, 6); c.clip()
        src(c, "#F7C66B", 0.9); c.paint()
        emoji(c, "👵", 850, 700, 70)
        src(c, "#FFFFFF", 0.95); c.rectangle(800, 640, 28 - 18 * wob, 120); c.fill(); c.rectangle(892 + 18 * wob, 640, 28, 120); c.fill()
        c.restore()
        c.restore()
        rrect(c, 70, 380, 940, 680, 30); c.set_line_width(6); src(c, INK); c.stroke()
    scaled(c, W / 2, 720, s, street)
    if t > S.at(0, 0.5):
        emoji(c, "👀", 860, 820, 70 * pop(t, S.at(0, 0.5)))
    if t > a1:
        def notif():
            rrect(c, 120, 905, 840, 110, 26); src(c, "#FFFFFF", 0.95); c.fill()
            rrect(c, 120, 905, 840, 110, 26); c.set_line_width(4); src(c, INK); c.stroke()
            text(c, "📢 Wentorf-News: 37 neue Nachrichten", W / 2, 960, 36, INK, FONT_HEAD)
        scaled(c, W / 2, 960, pop(t, a1 + 0.1), notif)
    alex_bottom(c, S, "shock" if t > S.at(0, 0.5) else "smug", "idle", x=320, h=AH * 0.9)
    person(c, 740, FEET, AH * 0.86, JANA, t, "shock" if t > S.at(0, 0.5) else "happy", "idle", name="Jana", blink_seed=2)


def sc_signs(c, S):
    t = S.t
    items = [("Exen haben eigene WhatsApp-Gruppe", "💬"), ("Weicht auf jedem Fest jemandem aus", "🏃"),
             ("Datet schon im Nachbardorf", "🚗"), ("Rammelt alles, was Beine hat", "🦵")]
    for i, (lab, ic) in enumerate(items):
        y = 400 + i * 175
        row_card(c, W / 2, y, 1000, 160, pop(t, S.at(i + 1, 0.0)), lab, ic, 40, num=i + 1, rot=(-0.02 if i % 2 else 0.02))
    for i in range(3):
        emoji(c, "🚩", 140 + i * 400, 1150 + math.sin(t * 3 + i) * 12, 90 * pop(t, S.at(0, 0.2 + 0.15 * i)))
    alex_bottom(c, S, "smug", "shrug")


def sc_outro(c, S):
    t, a1 = S.t, S.at(1)
    q = "Kennst du auch eine Dorfmatratze?" if t < a1 else "Was soll Alex morgen sein?"
    qs = pop(t, S.at(0, 0.0)) if t < a1 else pop(t, a1)
    card(c, W / 2, 230, 1000, 220, qs)
    scaled(c, W / 2, 230, qs, lambda: text_block(c, q, W / 2, 230, 52, 940, INK, FONT_HEAD))
    if t < a1 + 0.2:
        out = out_fade(t, a1)
        s = pop(t, S.at(0, 0.3)) * out
        def tg():
            c.arc(W / 2, 640, 210, 0, 2 * math.pi); fill(c, "#FFFFFF")
            c.arc(W / 2, 640, 210, 0, 2 * math.pi); c.set_line_width(8); src(c, INK); c.stroke()
            text(c, "@", W / 2, 625, 300, "#5E8C3A", FONT_HEAD)
            rrect(c, 160, 900, 760, 100, 50); fill(c, "#FFFFFF")
            rrect(c, 160, 900, 760, 100, 50); c.set_line_width(5); src(c, INK); c.stroke()
            typed = "@dorfmatratze"
            n = int(clamp((t - S.at(0, 0.4)) / 1.0) * len(typed))
            cur = "|" if int(t * 3) % 2 == 0 else ""
            text(c, typed[:n] + cur, 200, 950, 40, "#3D8BFF", FONT_HEAD, anchor="l")
        scaled(c, W / 2, 700, s, tg, rot=math.sin(t * 4) * 0.02)
    if t >= a1:
        colors = ["#EC7FAE", "#3E5C9A", "#4A2E6B", "#7A3FA8", "#5E8C3A", "#8E5BE0", "#36B5C2", "#F07F4F", "#555A66"]
        prev = [("🌹", "FOLGE 1"), ("🥺", "FOLGE 2"), ("🌀", "FOLGE 3"), ("🏘️", "HEUTE ✅")]
        for i in range(9):
            r, cc = i // 3, i % 3
            x, y = 250 + cc * 290, 445 + r * 192
            def icon(x=x, y=y, i=i):
                c.arc(x, y, 88, 0, 2 * math.pi); fill(c, colors[i])
                c.arc(x, y, 88, 0, 2 * math.pi); c.set_line_width(7); src(c, "#FFFFFF"); c.stroke()
                if i < len(prev):
                    e, lab = prev[i]
                    emoji(c, e, x, y, 90)
                    rrect(c, x - 88, y + 58, 176, 48, 12); fill(c, "#2FA36B" if i == len(prev) - 1 else "#555A66")
                    text(c, lab, x, y + 82, 30, "#FFFFFF", FONT_HEAD)
                else:
                    text(c, "?", x, y, 100, "#FFFFFF", FONT_HEAD)
            scaled(c, x, y, pop(t, a1 + 0.1 + i * 0.07), icon)
        ps = pop(t, S.at(1, 0.45))
        def pill():
            rrect(c, 40, 950, 1000, 126, 63); fill(c, "#E23B3B")
            rrect(c, 40, 950, 1000, 126, 63); c.set_line_width(6); src(c, "#FFFFFF"); c.stroke()
            text(c, "Schreib's in die Kommentare ⬇️", W / 2, 1013, 52, "#FFFFFF", FONT_HEAD)
        scaled(c, W / 2, 1013, ps * (1 + 0.05 * math.sin(t * 7)), pill)
    alex_bottom(c, S, "happy", "wave")


SCENE_DRAW = dict(what=sc_what, motto=sc_motto, bakery=sc_bakery, bus=sc_bus, group=sc_group, fest=sc_fest, night=sc_night,
                  signs=sc_signs, outro=sc_outro)
