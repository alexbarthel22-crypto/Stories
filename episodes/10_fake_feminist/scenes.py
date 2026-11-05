"""Visuals: Alex ist heute ein Fake-Feminist (TikTok Folge 3). Aufbau wie Pick-me-Boy.
Alles liegt in TikToks Sicherheitsbereich (SAFE_MODE "strict" in script.py).
"""
import math, random
from alexlib import *

AL = alex(top="#FFFFFF", top_style="tee", pants="#3F4A6B", shoes="#FFFFFF")
FEET, AH = 1690, 560     # Alex größer, etwas tiefer
LEA = person_spec(22, girl=True, top="#36B5C2", hair="#3B2A20", skin="#EBB894", pants="#3F4A6B", shoes="#2A2A2A")

INTRO = dict(icon="📢", bg="#7A3FA8", spec=AL, expr="smug", pose="hips", hand_prop=None,
             side_emoji="👕", burst=["📢", "👕", "🚩", "🙄", "💬", "📱", "✊", "🏆"])


def shirt_text(c, x, feet, h):
    k = h / 100.0
    c.save(); c.translate(x, feet); c.scale(k, k)
    c.select_font_face(FONT_HEAD); src(c, "#E0457B")
    for i, ln in enumerate(("THE FUTURE", "IS FEMALE")):
        c.set_font_size(3.0)
        e = c.text_extents(ln); c.move_to(-e.x_advance / 2, -44 + i * 4.2); c.show_text(ln)
    c.new_path(); c.restore()


def _sign(c, x, y, txt, col, rot, size=30, w=230, post=150):
    c.save(); c.translate(x, y); c.rotate(rot)
    c.set_line_width(10); src(c, "#8A5E3B"); c.move_to(0, 40); c.line_to(0, 40 + post); c.stroke()
    rrect(c, -w / 2, -55, w, 100, 10); fill(c, col)
    rrect(c, -w / 2, -55, w, 100, 10); c.set_line_width(4); src(c, INK); c.stroke()
    text_block(c, txt, 0, -5, size, w - 24, INK, FONT_HEAD)
    c.restore()


def intro_decor(c, t, u):
    """Haus & Garten im Fake-Feminist-Look (eher zu viel als zu wenig)."""
    s_ = clamp(u)
    # Wimpelkette zwischen Dachkanten
    for i in range(13):
        x = 200 + i * 55
        y = 840 + 30 * math.sin(math.pi * i / 12)
        c.move_to(x, y); c.line_to(x + 50, y + 4); c.line_to(x + 25, y + 45 * s_); c.close_path()
        src(c, ["#E0457B", "#7A3FA8", "#FFFFFF", "#F7C948"][i % 4]); c.fill()
    # Banner hängt an Ballons im Himmel
    def banner():
        by = 548 + math.sin(t * 2) * 6
        c.set_line_width(2); src(c, "#FFFFFF")
        for bx in (260, 820):
            c.move_to(bx, by); c.line_to(bx, by - 60); c.stroke()
            emoji(c, "🎈", bx, by - 95, 70)
        rrect(c, 230, by - 34, 620, 68, 12); fill(c, "#E0457B")
        rrect(c, 230, by - 34, 620, 68, 12); c.set_line_width(4); src(c, INK); c.stroke()
        text(c, "THE FUTURE IS FEMALE ✨", 540, by, 36, "#FFFFFF", FONT_HEAD)
    scaled(c, 540, 548, s_, banner)
    # Poster in den Fenstern
    emoji(c, "✊", 350, 955, 80 * s_); emoji(c, "♀️", 730, 955, 80 * s_)
    emoji(c, "📢", 540, 730, 60 * s_)
    # Protestschilder im Garten
    _sign(c, 190, 1620, "#ALLY ✊", "#FFE14D", -0.12, 30, 200, 90)
    _sign(c, 890, 1620, "Feminist des Jahres 🏆", "#FFFFFF", 0.1, 24, 220, 90)
    # Blumenbeet + Ballons
    for i, x in enumerate(range(240, 860, 62)):
        if abs(x - 540) > 90:
            emoji(c, "🌷" if i % 2 else "🌸", x, 1295, 46 * s_)
    for i, (x, y) in enumerate(((140, 760), (210, 690), (960, 760), (890, 690))):
        bob = math.sin(t * 2 + i) * 10
        c.set_line_width(2); src(c, "#FFFFFF"); c.move_to(x, y + 50 + bob); c.line_to(x + 10, y + 240); c.stroke()
        emoji(c, "🎈", x, y + bob, 90 * s_)


def alex_extras(c, x, feet, h, t, u):
    """Alex maximal 'Ally': Shirt-Print, Schärpe, Stirnband, Megafon, Schild, Anstecker."""
    k = h / 100.0
    shirt_text(c, x, feet, h)
    c.save(); c.translate(x, feet); c.scale(k, k)
    # Schärpe
    c.move_to(-13, -55); c.line_to(-8, -56); c.line_to(13, -27); c.line_to(8, -26); c.close_path(); fill(c, "#7A3FA8")
    c.save(); c.translate(1, -41); c.rotate(0.95)
    c.select_font_face(FONT_HEAD); c.set_font_size(2.6); src(c, "#FFFFFF")
    e = c.text_extents("ALLY 2026"); c.move_to(-e.x_advance / 2, 1); c.show_text("ALLY 2026"); c.new_path()
    c.restore()
    # Stirnband
    rrect(c, -17.5, -86, 35, 5, 2); fill(c, "#E0457B")
    c.select_font_face(FONT_HEAD); c.set_font_size(3.2); src(c, "#FFFFFF")
    e = c.text_extents("FEMINIST"); c.move_to(-e.x_advance / 2, -82.3); c.show_text("FEMINIST"); c.new_path()
    c.restore()
    # Anstecker
    for (dx, dy, e_) in ((-10, -36, "✊"), (-9, -30, "♀️"), (9, -48, "💜")):
        emoji(c, e_, x + dx * k, feet + dy * k, 4.5 * k)
    # Megafon rechts oben, Schild links oben (Pose "up")
    emoji(c, "📢", x + 23 * k, feet - 74 * k, 13 * k, rot=-0.3)
    c.save(); c.translate(x - 24 * k, feet - 84 * k); c.rotate(-0.12)
    rrect(c, -13 * k, -8 * k, 26 * k, 14 * k, 1.5 * k); fill(c, "#FFFFFF")
    rrect(c, -13 * k, -8 * k, 26 * k, 14 * k, 1.5 * k); c.set_line_width(0.6 * k); src(c, INK); c.stroke()
    text(c, "ICH BIN", 0, -3.2 * k, 3.2 * k, INK, FONT_HEAD)
    text(c, "FEMINIST! ✊", 0, 1.8 * k, 3.2 * k, "#E0457B", FONT_HEAD)
    c.restore()


INTRO["house"] = dict(sky=("#B97ADB", "#FFD1E6"), walls="#F7C6DA", roof="#7A3FA8", door="#E0457B", lawn="#6CC47A",
                      accent=("#E0457B", "#7A3FA8"))
INTRO["decor"] = intro_decor
INTRO["alex_extras"] = alex_extras
INTRO["pose"] = "up"
INTRO["expr"] = "happy"
INTRO["burst"] = ["✊", "♀️", "📢", "💜", "🌷", "🎈", "✨", "🏆"]


def draw_intro(c, t, shuffle, ticks, flash_start, reveal_t, role_text):
    draw_intro_house(c, t, shuffle, ticks, flash_start, reveal_t, role_text, INTRO)


import alexlib as _al
CONTENT_SCALE = 1.12      # Karten/Telefon/Listen größer; Alex, Lea und Sprechblasen bleiben am Platz
_BASE = [None]


def _on_base(fn):
    def wrapped(c, *a, **k):
        if _BASE[0] is None:
            return fn(c, *a, **k)
        m = c.get_matrix(); c.set_matrix(_BASE[0])
        try:
            return fn(c, *a, **k)
        finally:
            c.set_matrix(m)
    return wrapped


def big(fn):
    def wrapped(c, S):
        _BASE[0] = c.get_matrix()
        c.save()
        c.translate(W / 2, 330); c.scale(CONTENT_SCALE, CONTENT_SCALE); c.translate(-W / 2, -330)
        try:
            fn(c, S)
        finally:
            c.restore(); _BASE[0] = None
    return wrapped


bubble = _on_base(_al.bubble)


@_on_base
def alex_bottom(c, S, expr="smug", pose="idle", prop=None, x=W / 2, h=AH):
    person(c, x, FEET, h, AL, S.t, expr, pose, prop, name="Alex")
    shirt_text(c, x, FEET, h)


@_on_base
def lea(c, S, expr="neutral", x=790, h=AH * 0.97, s=1.0):
    scaled(c, x, FEET, s, lambda: person(c, x, FEET, h, LEA, S.t, expr, name="Lea", blink_seed=3))


def out_fade(t, t_end, d=0.2):
    return 1 - ease_out_cubic((t - t_end) / d) if t > t_end else 1


def row_card(c, x, y, w, h, s, label, icon=None, size=40, num=None, rot=0.0):
    def d():
        rrect(c, x - w / 2 + 6, y - h / 2 + 10, w, h, 22); src(c, "#000000", 0.2); c.fill()
        rrect(c, x - w / 2, y - h / 2, w, h, 22); fill(c, "#FFFFFF")
        rrect(c, x - w / 2, y - h / 2, w, h, 22); c.set_line_width(5); src(c, INK); c.stroke()
        lx = x - w / 2 + 40
        if num is not None:
            c.arc(x - w / 2 + 75, y, 42, 0, 2 * math.pi); fill(c, "#7A3FA8")
            text(c, str(num), x - w / 2 + 75, y, 46, "#FFFFFF", FONT_HEAD)
            lx = x - w / 2 + 140
        text(c, label, lx, y, size, INK, FONT_HEAD, anchor="l")
        if icon:
            emoji(c, icon, x + w / 2 - 60, y, 56)
    scaled(c, x, y, s, d, rot)


def bar(c, x, y, w, h, frac, col, label, value):
    rrect(c, x, y, w, h, h / 2); fill(c, "#EDEDF0")
    if frac > 0.01:
        rrect(c, x, y, max(h, w * frac), h, h / 2); fill(c, col)
    text(c, label, x, y - 34, 34, "#444444", FONT_BOLD, anchor="l")
    text(c, value, x + w, y - 34, 40, INK, FONT_HEAD, anchor="r")


# ======================================================================= SZENEN
def sc_what(c, S):
    t, a1 = S.t, S.at(1)
    s = pop(t, S.at(0, 0.0))
    def meter():
        card(c, W / 2, 680, 900, 520, 1)
        text(c, "FEMINIST-O-METER", W / 2, 480, 50, INK, FONT_HEAD)
        u = ease_out_cubic((t - S.at(0, 0.3)) / 0.9)
        bar(c, 150, 600, 780, 56, 1.0 * u, "#2FA36B", "👀 Jemand schaut zu", f"{int(100 * u)} %")
        bar(c, 150, 760, 780, 56, 0.05 * u, "#E23B3B", "🙈 Niemand schaut zu", f"{int(5 * u)} %")
    scaled(c, W / 2, 680, s, meter)
    alex_bottom(c, S, "smug", "hips")
    if t >= a1:
        bubble(c, "Ich bin der größte Feminist, den du kennst! ✊", 815, 1150, pop(t, a1), tail=(-0.5, 1), size=38, max_w=340)


def sc_post(c, S):
    t, a1 = S.t, S.at(1)
    s = pop(t, S.at(0, 0.0))
    x0, y0, w, h = phone(c, W / 2, 700, 520, 820, s, screen="#FFFFFF")
    likes = int(1204 * ease_out_cubic((t - S.at(0, 0.4)) / 2.0)) if t > S.at(0, 0.4) else 0
    def screen():
        c.save(); rrect(c, x0, y0, w, h, 42); c.clip()
        src(c, "#FDE3EE"); c.rectangle(x0, y0 + 110, w, 430); c.fill()
        person(c, W / 2, y0 + 760, 640, AL, t, "smug", "hips", bob=False)
        shirt_text(c, W / 2, y0 + 760, 640)
        c.rectangle(x0, y0 + 540, w, h); fill(c, "#FFFFFF")
        text(c, f"♥ {likes:,}".replace(",", "."), x0 + 40, y0 + 590, 34, "#E23B3B", FONT_HEAD, anchor="l")
        text(c, "The future is female ✊", x0 + 40, y0 + 645, 30, INK, FONT_BOLD, anchor="l")
        text(c, "#feminist #ally #respekt", x0 + 40, y0 + 690, 26, "#3D8BFF", FONT_BOLD, anchor="l")
        rrect(c, x0, y0, w, 110, 0); fill(c, "#F4F4F6")
        text(c, "alex.ally", x0 + 40, y0 + 65, 32, INK, FONT_HEAD, anchor="l")
        c.restore()
    scaled(c, W / 2, 700, s, screen)
    if t >= a1:
        emoji(c, "📈", 880, 460, 110 * pop(t, a1 + 0.1))
        emoji(c, "🔄", 180, 460, 90 * pop(t, a1 + 0.3), rot=t * 2)
    alex_bottom(c, S, "smug", "phone", "📱", x=880, h=AH * 0.9)


def sc_mansplain(c, S):
    t, a1 = S.t, S.at(1)
    s = pop(t, S.at(0, 0.0))
    def board():
        rrect(c, 110, 400, 860, 540, 20); fill(c, "#FFFFFF")
        rrect(c, 110, 400, 860, 540, 20); c.set_line_width(6); src(c, INK); c.stroke()
        text(c, "FEMINISMUS 101", W / 2, 470, 56, INK, FONT_HEAD)
        text(c, "erklärt von: Alex 👨‍🏫" if False else "erklärt von: Alex", W / 2, 530, 34, "#777777", FONT_BOLD)
        for i, ln in enumerate(("1. Frauen sind toll", "2. Ich auch", "3. Siehe Punkt 2")):
            if t > S.at(0, 0.25 + 0.15 * i):
                text(c, ln, 180, 620 + i * 80, 42, "#2E3A8C", FONT_HEAD, anchor="l")
    scaled(c, W / 2, 670, s, board)
    alex_bottom(c, S, "smug", "point", x=320)
    lea(c, S, "neutral" if t < a1 else "cringe", s=pop(t, S.at(0, 0.2)))
    if t >= a1:
        def badge():
            c.save(); c.translate(W / 2, 880); c.rotate(-0.08)
            rrect(c, -300, -60, 600, 120, 18); fill(c, "#FFE14D")
            rrect(c, -300, -60, 600, 120, 18); c.set_line_width(6); src(c, "#E23B3B"); c.stroke()
            text(c, "SIE IST GLEICHSTELLUNGS-", 0, -20, 36, "#C0392B", FONT_HEAD)
            text(c, "BEAUFTRAGTE 😳", 0, 26, 36, "#C0392B", FONT_HEAD)
            c.restore()
        scaled(c, W / 2, 880, pop(t, a1 + 0.05), badge)
        emoji(c, "🙄", 930, 1220, 70 * pop(t, a1 + 0.4))


def sc_work(c, S):
    t = S.t
    s = pop(t, S.at(0, 0.0))
    def table():
        rrect(c, 110, 860, 860, 50, 14); fill(c, "#B07A4F")
        rrect(c, 110, 860, 860, 50, 14); c.set_line_width(5); src(c, INK); c.stroke()
        for i, x in enumerate((230, 400, 680, 850)):
            person(c, x, 880, 300, person_spec(140 + i, girl=bool(i % 2)), t, "neutral", bob=False)
        emoji(c, "📊", W / 2, 520, 140)
    scaled(c, W / 2, 700, s, table)
    if S.at(0, 0.1) < t < S.at(0, 0.45):
        bubble(c, "Wir könnten doch … 💡", 790, 965, pop(t, S.at(0, 0.1)), tail=(0.3, 1), size=38, max_w=440)
    if t >= S.at(0, 0.45):
        bubble(c, "WIR KÖNNTEN DOCH … 💡!!", 330, 965, pop(t, S.at(0, 0.45)), tail=(-0.3, 1), size=40, max_w=480)
    if t >= S.at(0, 0.75):
        emoji(c, "🏆", 180, 1180, 100 * pop(t, S.at(0, 0.75)), rot=-0.2)
    alex_bottom(c, S, "smug" if t > S.at(0, 0.45) else "neutral", "up" if t > S.at(0, 0.75) else "idle", x=320)
    lea(c, S, "cringe" if t > S.at(0, 0.5) else "happy")


def sc_home(c, S):
    t, a1 = S.t, S.at(1)
    s = pop(t, S.at(0, 0.0))
    def kitchen():
        card(c, W / 2, 680, 900, 560, 1)
        text(c, "HAUSHALT", W / 2, 460, 48, INK, FONT_HEAD)
        tasks = ["Kochen", "Wäsche", "Bad", "Einkaufen", "Müll"]
        text(c, "Jana", 300, 530, 38, INK, FONT_HEAD); text(c, "Alex", 780, 530, 38, INK, FONT_HEAD)
        for i, tk in enumerate(tasks):
            y = 590 + i * 62
            text(c, tk, W / 2, y, 30, "#555555", FONT_BOLD)
            emoji(c, "✅", 300, y, 40)
            emoji(c, "✅" if i == 4 else "➖", 780, y, 40)
        if t > a1:
            rrect(c, 640, 870, 280, 56, 12); fill(c, "#FFE14D")
            text(c, "„geholfen“ 🗑️", 780, 898, 30, INK, FONT_HEAD)
    scaled(c, W / 2, 680, s, kitchen)
    alex_bottom(c, S, "smug", "hips")
    if t < a1 + 0.1:
        bubble(c, "Ich helfe ja im Haushalt! 😇", 815, 1150, pop(t, S.at(0, 0.3)) * out_fade(t, a1), tail=(-0.5, 1), size=40, max_w=340)


def sc_men(c, S):
    t, a1 = S.t, S.at(1)
    if t < a1 + 0.2:
        o = out_fade(t, a1)
        s = pop(t, S.at(0, 0.0)) * o
        x0, y0, w, h = phone(c, W / 2, 680, 560, 620, s, screen="#FFFFFF")
        def screen():
            c.save(); rrect(c, x0, y0, w, h, 42); c.clip()
            rrect(c, x0, y0, w, 110, 0); fill(c, "#F4F4F6")
            c.arc(x0 + 60, y0 + 62, 28, 0, 2 * math.pi); fill(c, ALEX_BASE["hair"])
            text(c, "alex.ally", x0 + 105, y0 + 62, 32, INK, FONT_HEAD, anchor="l")
            text_block(c, "Männer sind das Problem. ALLE Männer! 😤", W / 2, y0 + 270, 46, w - 70, INK, FONT_HEAD)
            text(c, "#allmen #feminist", W / 2, y0 + 420, 30, "#3D8BFF", FONT_BOLD)
            likes = int(512 * ease_out_cubic((t - S.at(0, 0.4)) / 1.2)) if t > S.at(0, 0.4) else 0
            text(c, f"♥ {likes}", x0 + 40, y0 + 520, 34, "#E23B3B", FONT_HEAD, anchor="l")
            c.restore()
        scaled(c, W / 2, 680, s, screen)
        alex_bottom(c, S, "angry", "phone", "📱")
    else:
        s = pop(t, a1 + 0.05)
        def lineup():
            card(c, W / 2, 680, 980, 560, 1)
            text(c, "ALLE MÄNNER", W / 2, 460, 52, INK, FONT_HEAD)
            for i, x in enumerate((150, 300, 450, 630, 780, 930)):
                person(c, x, 880, 300, person_spec(160 + i), t, "neutral", bob=False, blink_seed=i)
            if t > S.at(1, 0.15):
                c.set_line_width(14); src(c, "#E23B3B")
                c.move_to(110, 520); c.line_to(970, 880); c.move_to(970, 520); c.line_to(110, 880); c.stroke()
        scaled(c, W / 2, 680, s, lineup)
        # Alex mit Heiligenschein + Schild "außer mir"
        hy = FEET - AH * 1.12
        c.save(); c.translate(W / 2, hy); c.scale(1, 0.3); c.arc(0, 0, 100, 0, 2 * math.pi); c.restore()
        c.set_line_width(12); src(c, "#FFE14D", pop(t, S.at(1, 0.4)) * 0.95); c.stroke()
        alex_bottom(c, S, "smug", "hips")
        def sign():
            c.save(); c.translate(830, 1330); c.rotate(0.08)
            rrect(c, -150, -60, 300, 120, 16); fill(c, "#FFFFFF")
            rrect(c, -150, -60, 300, 120, 16); c.set_line_width(5); src(c, INK); c.stroke()
            text(c, "AUSSER MIR", 0, -16, 38, INK, FONT_HEAD)
            text(c, "ich bin anders 😇", 0, 28, 28, "#7A3FA8", FONT_HEAD)
            c.restore()
        scaled(c, 830, 1330, pop(t, S.at(1, 0.45)), sign)
        emoji(c, "👈", 680, 1420, 80 * pop(t, S.at(1, 0.45)))


def sc_signs(c, S):
    t = S.t
    items = [("Feminist nur online", "📱"), ("Erklärt Frauen Feminismus", "👨‍🏫" if False else "🗣️"),
             ("„Hilft“ im Haushalt", "🧽"), ("Gleichberechtigung à la carte", "🍽️")]
    for i, (lab, ic) in enumerate(items):
        y = 400 + i * 175
        row_card(c, W / 2, y, 1000, 160, pop(t, S.at(i + 1, 0.0)), lab, ic, 48, num=i + 1, rot=(-0.02 if i % 2 else 0.02))
    for i in range(3):
        emoji(c, "🚩", 140 + i * 400, 1150 + math.sin(t * 3 + i) * 12, 90 * pop(t, S.at(0, 0.2 + 0.15 * i)))
    alex_bottom(c, S, "smug", "shrug")


def sc_outro(c, S):
    t, a1 = S.t, S.at(1)
    q = "Kennst du auch so einen Fake-Feministen?" if t < a1 else "Was soll Alex morgen sein?"
    qs = pop(t, S.at(0, 0.0)) if t < a1 else pop(t, a1)
    card(c, W / 2, 230, 1000, 220, qs)
    scaled(c, W / 2, 230, qs, lambda: text_block(c, q, W / 2, 230, 60, 940, INK, FONT_HEAD))
    if t < a1 + 0.2:
        out = out_fade(t, a1)
        s = pop(t, S.at(0, 0.3)) * out
        def tag():
            c.arc(W / 2, 640, 210, 0, 2 * math.pi); fill(c, "#FFFFFF")
            c.arc(W / 2, 640, 210, 0, 2 * math.pi); c.set_line_width(8); src(c, INK); c.stroke()
            text(c, "@", W / 2, 625, 300, "#7A3FA8", FONT_HEAD)
            rrect(c, 160, 900, 760, 100, 50); fill(c, "#FFFFFF")
            rrect(c, 160, 900, 760, 100, 50); c.set_line_width(5); src(c, INK); c.stroke()
            typed = "@nur_online_feminist"
            n = int(clamp((t - S.at(0, 0.4)) / 1.0) * len(typed))
            cur = "|" if int(t * 3) % 2 == 0 else ""
            text(c, typed[:n] + cur, 200, 950, 40, "#3D8BFF", FONT_HEAD, anchor="l")
        scaled(c, W / 2, 700, s, tag, rot=math.sin(t * 4) * 0.02)
        emoji(c, "👇", 880, 1110 + math.sin(t * 8) * 12, 90 * pop(t, S.at(0, 0.6)) * out)
    if t >= a1:
        colors = ["#EC7FAE", "#3E5C9A", "#4A2E6B", "#7A3FA8", "#3E7BDA", "#8E5BE0", "#36B5C2", "#F07F4F", "#555A66"]
        # TikTok-Reihenfolge: 1 Pick-me-Boy, 2 Emotional abhängig, heute 3
        prev = [("🌹", "FOLGE 1"), ("🥺", "FOLGE 2"), ("📢", "HEUTE ✅")]
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
        scaled(c, W / 2, 1013, ps * (1 + 0.05 * math.sin(t * 7)), pill)
    alex_bottom(c, S, "happy", "wave")


SCENE_DRAW = dict(what=big(sc_what), post=big(sc_post), mansplain=big(sc_mansplain), work=sc_work,
                  home=big(sc_home), men=sc_men, signs=sc_signs, outro=sc_outro)
