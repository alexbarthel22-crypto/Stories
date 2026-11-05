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
    # Ortsschild-Banner
    def banner():
        by = 790
        rrect(c, 230, by - 44, 620, 88, 10); fill(c, "#F7D21B")
        rrect(c, 240, by - 34, 600, 68, 6); c.set_line_width(5); src(c, INK); c.stroke()
        text(c, "WENTORF", 540, by - 6, 42, INK, FONT_HEAD)
        text(c, "bei Hamburg · alle kennen Alex", 540, by + 26, 22, INK, FONT_BOLD)
    scaled(c, 540, 790, s_, banner)
    # Schilder vorne
    _sign(c, 200, 1650, "Tür immer offen 🚪", "#FFFFFF", -0.1, 42, 340)
    _sign(c, 880, 1650, "Schon wieder Besuch 👀", "#FFB3D9", 0.08, 40, 340)
    # Herzen fliegen
    for i in range(5):
        u2 = (t * 0.35 + i / 5) % 1
        emoji(c, "💔" if i % 2 else "💋", 120 + i * 210, 1250 - u2 * 160, 46, alpha=0.8 * (1 - u2))


def alex_extras(c, x, feet, h, t, u):
    """Fuckboy, etwas billig: Sonnenbrille im Haar, dicke Goldkette, Bierdose, Zwinkern."""
    k = h / 100.0
    emoji(c, "🕶️", x + 2 * k, feet - 90 * k, 16 * k, rot=-0.08)
    c.set_line_width(1.6 * k); src(c, "#D4AF37")
    c.move_to(x - 7 * k, feet - 56 * k); c.curve_to(x - 5 * k, feet - 44 * k, x + 5 * k, feet - 44 * k, x + 7 * k, feet - 56 * k); c.stroke()
    c.arc(x, feet - 45 * k, 2.2 * k, 0, 2 * math.pi); src(c, "#D4AF37"); c.fill()
    emoji(c, "🍺", x + 36 * k, feet - 30 * k, 12 * k, rot=0.1)
    emoji(c, "😉", x - 30 * k, feet - 94 * k, 12 * k)


INTRO = dict(icon="🏘️", bg="#5E8C3A", spec=AL, expr="smug", pose="hips", hand_prop=None,
             house=dict(sky=("#7A4FA0", "#FF9FB8"), walls="#F7D6E0", roof="#8A2A3A", door="#2A1A20", lawn="#5DAA5E",
                        accent=("#E0457B", "#1C1C22"), sun=False),
             umbrella=False, fill="#6FB7E8", decor=intro_decor, alex_extras=alex_extras,
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
    alex_bottom(c, S, "smug", "hips")


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
        person(c, 380, 900, 380, JANA, t, "cringe", bob=False, name="Ex")
        if t > a1:
            person(c, 700, 900, 400, MUTTER, t, "angry", bob=False, name="ihre Mutter")
            emoji(c, "👁️", 700, 560, 60 + 6 * math.sin(t * 8))
        rrect(c, 110, 880, 860, 150, 14); fill(c, "#B07A4F")
        rrect(c, 110, 880, 860, 150, 14); c.set_line_width(5); src(c, INK); c.stroke()
        for i, e in enumerate(("🥐", "🥨", "🍞", "🥯", "🍩", "🥐")):
            emoji(c, e, 190 + i * 140, 940, 70)
    scaled(c, W / 2, 710, s, shop)
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
    if t > a1:
        tag(c, 210, 820, "ONKEL VON EX", "#3E7BDA", s=pop(t, a1 + 0.1))
    alex_bottom(c, S, "shock" if t > a1 else "cringe", "idle")


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


def sc_signs(c, S):
    t = S.t
    items = [("Exen haben eigene WhatsApp-Gruppe", "💬"), ("Weicht auf jedem Fest jemandem aus", "🏃"),
             ("Datet schon im Nachbardorf", "🚗"), ("Oma Hilde weiß alles", "👵")]
    for i, (lab, ic) in enumerate(items):
        y = 400 + i * 175
        row_card(c, W / 2, y, 1000, 160, pop(t, S.at(i + 1, 0.0)), lab, ic, 40, num=i + 1, rot=(-0.02 if i % 2 else 0.02))
    for i in range(3):
        emoji(c, "🚩", 140 + i * 400, 1150 + math.sin(t * 3 + i) * 12, 90 * pop(t, S.at(0, 0.2 + 0.15 * i)))
    alex_bottom(c, S, "smug", "shrug")


def sc_outro(c, S):
    t, a1 = S.t, S.at(1)
    q = "Kennst du auch so ein Dorf, wo jeder jeden kennt?" if t < a1 else "Was soll Alex morgen sein?"
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
            typed = "@kennt_jeden_im_dorf"
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
            rrect(c, 100, 955, 880, 116, 58); fill(c, "#E23B3B")
            rrect(c, 100, 955, 880, 116, 58); c.set_line_width(6); src(c, "#FFFFFF"); c.stroke()
            text(c, "Schreib's in die Kommentare ⬇️", W / 2, 1013, 54, "#FFFFFF", FONT_HEAD)
        scaled(c, W / 2, 1013, ps * (1 + 0.05 * math.sin(t * 7)), pill)
    alex_bottom(c, S, "happy", "wave")


SCENE_DRAW = dict(what=sc_what, bakery=sc_bakery, bus=sc_bus, group=sc_group, fest=sc_fest, night=sc_night,
                  signs=sc_signs, outro=sc_outro)
