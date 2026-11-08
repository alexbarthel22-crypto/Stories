"""Visuals: Alex als Alexa, ein OF-Model. Komplett jugendfrei – nur Business-/Influencer-Klischees.
Kein Plattform-Logo, keine Zahlen zu Gebühren. Endsequenz: TikTok-Folge 3.
"""
import math, random
from alexlib import *

# Alexia: gleiches Gesicht wie Alex (Augen, Sommersprossen), aber glaubwürdig weiblich gestylt
ALEXA = alex(hair_style="fem", makeup=dict(shadow="#C8708E"), lashes=True, lips="#D8346E", earrings="#F2C94C",
             top="#E8457A", top_style="tank", skirt="#1C1C22", bare_legs=True, heels=True, shoes="#E8457A")
FEET, AH = 1740, 470          # Alexia tiefer (neuer Aufbau), Inhalte darüber größer
CONTENT_SCALE = 1.12
_BASE = [None]
OMA = person_spec(5, girl=True, hair_style="bun", hair="#C9C9CF", skin="#F1C9A8", top="#8E5BE0",
                  pants="#4A4A5A", shoes="#5A3A2A", glasses=True)
MAMA = person_spec(6, girl=True, hair="#7A4A2A", top="#2FA36B", skin="#F1C9A8")
OPA = person_spec(9, hair="#DADADF", top="#7A5C45", skin="#F1C9A8", glasses=True)
KEVIN = person_spec(33, hair_style="cap", cap="#2E3A8C", top="#555A66", skin="#E9B48A")

# Verkündung vor dem Haus mit großem Titel (wie Dorfmatratze)
import kit as _kit
INTRO, draw_intro = _kit.make_intro(dict(
    icon="📸", bg="#B0307A", spec=ALEXA, title_lines=["OF-MODEL."],
    house=dict(sky=("#E26AA0", "#FFE1EE"), walls="#FFF0F6", roof="#7A1F48", door="#4A0E2A", lawn="#5DAA5E",
               accent=("#E8457A", "#F2C94C"), sun=True),
    left=("💡", "RINGLICHT"), right=("📸", "STUDIO"), door=("LINK", "IN BIO 🔗"),
    neon=("EXKLUSIV", "NUR IM ABO 💸", "#FF6FB0"), signs=("Link in Bio 🔗", "Hey Babe 😘"),
    sign_x=(190, 890), sign_w=330, sign_size=40,
    fly=["💸", "💄", "📸"], burst=["📸", "💄", "💅", "💸", "🔗", "😘", "💡", "👑"],
    extras=[("💄", -34, 40, 12), ("📱", 34, 40, 14)]))


def alexa_bottom(c, S, expr="smug", pose="idle", prop=None, x=W / 2, h=AH):
    c.save()
    if _BASE[0] is not None:
        c.set_matrix(_BASE[0])                              # Alexia unskaliert an fester Position
    person(c, x, FEET, h, ALEXA, S.t, expr, pose, prop, name="Alexia")
    c.restore()


def out_fade(t, t_end, d=0.2):
    return 1 - ease_out_cubic((t - t_end) / d) if t > t_end else 1


def chat_header(c, x0, y0, w, name, col):
    rrect(c, x0, y0, w, 130, 0); fill(c, "#F4F4F6")
    c.arc(x0 + 70, y0 + 82, 30, 0, 2 * math.pi); fill(c, col)
    text(c, name, x0 + 115, y0 + 82, 32, INK, FONT_HEAD, anchor="l")


def chat_msg(c, msg, x0, w, y, mine, s, size=30):
    if s <= 0:
        return 0
    lines = wrap(c, msg, size, w - 140, FONT_BOLD)
    bw = max(text_width(c, ln, size, FONT_BOLD) for ln in lines) + 44
    bh = len(lines) * size * 1.25 + 26
    bx = x0 + w - 24 - bw if mine else x0 + 24
    def d():
        rrect(c, bx, y - bh, bw, bh, 22)
        fill(c, "#F07FB0" if mine else "#E6E6EA")
        for i, ln in enumerate(lines):
            text(c, ln, bx + 22, y - bh + 13 + size * 0.62 + i * size * 1.25, size, "#FFFFFF" if mine else INK,
                 FONT_BOLD, anchor="l")
    scaled(c, bx + (bw if mine else 0), y, s, d)
    return bh


def row_card(c, x, y, w, h, s, label, icon=None, size=40, num=None, rot=0.0):
    def d():
        rrect(c, x - w / 2 + 6, y - h / 2 + 10, w, h, 22); src(c, "#000000", 0.2); c.fill()
        rrect(c, x - w / 2, y - h / 2, w, h, 22); fill(c, "#FFFFFF")
        rrect(c, x - w / 2, y - h / 2, w, h, 22); c.set_line_width(5); src(c, INK); c.stroke()
        lx = x - w / 2 + 40
        if num is not None:
            c.arc(x - w / 2 + 75, y, 42, 0, 2 * math.pi); fill(c, "#B0307A")
            text(c, str(num), x - w / 2 + 75, y, 46, "#FFFFFF", FONT_HEAD)
            lx = x - w / 2 + 140
        text(c, label, lx, y, size, INK, FONT_HEAD, anchor="l")
        if icon:
            emoji(c, icon, x + w / 2 - 60, y, 56)
    scaled(c, x, y, s, d, rot)


def ring_light(c, x, y, r, s=1.0, t=0.0):
    def d():
        g = cairo.RadialGradient(x, y, r * 0.6, x, y, r * 1.6)
        g.add_color_stop_rgba(0, 1, 1, 1, 0.35); g.add_color_stop_rgba(1, 1, 1, 1, 0)
        c.arc(x, y, r * 1.6, 0, 2 * math.pi); c.set_source(g); c.fill()
        c.set_line_width(r * 0.22); src(c, "#FFFFFF")
        c.arc(x, y, r, 0, 2 * math.pi); c.stroke()
        c.set_line_width(4); src(c, INK)
        c.arc(x, y, r * 1.11, 0, 2 * math.pi); c.stroke()
        c.arc(x, y, r * 0.89, 0, 2 * math.pi); c.stroke()
        c.set_line_width(10); src(c, "#2B2B2B"); c.move_to(x, y + r * 1.11); c.line_to(x, y + r * 2.2); c.stroke()
    scaled(c, x, y, s, d)


# ======================================================================= SZENEN
def sc_what(c, S):
    t, a1 = S.t, S.at(1)
    if t < a1 + 0.2:
        o = out_fade(t, a1)
        s = pop(t, S.at(0, 0.0)) * o
        x0, y0, w, h = phone(c, W / 2, 700, 480, 760, s, screen="#FDF0F6")
        def screen():
            c.save(); rrect(c, x0, y0, w, h, 42); c.clip()
            c.arc(W / 2, y0 + 160, 70, 0, 2 * math.pi); fill(c, "#F07FB0")
            text(c, "A", W / 2, y0 + 160, 70, "#FFFFFF", FONT_HEAD)
            text(c, "@alexia.exklusiv", W / 2, y0 + 270, 32, INK, FONT_HEAD)
            rrect(c, x0 + 40, y0 + 320, w - 80, 260, 20); fill(c, "#E9D5E2")
            emoji(c, "🔒", W / 2, y0 + 430, 110)
            text(c, "Exklusiv für Abonnenten", W / 2, y0 + 540, 26, "#7A4A6A", FONT_BOLD)
            rrect(c, x0 + 60, y0 + 610, w - 120, 80, 40); fill(c, "#B0307A")
            text(c, "ABONNIEREN 💸", W / 2, y0 + 650, 32, "#FFFFFF", FONT_HEAD)
            c.restore()
        scaled(c, W / 2, 700, s, screen)
        c.save()
        if _BASE[0] is not None:
            c.set_matrix(_BASE[0])
        person(c, W / 2, FEET, AH, alex(), t, "happy", "idle", name="Alex")
        c.restore()
    else:
        s = pop(t, a1 + 0.05)
        def makeover():
            card(c, W / 2, 690, 920, 620, 1)
            text(c, "VERWANDLUNG", W / 2, 440, 48, INK, FONT_HEAD)
            person(c, 270, 850, 340, alex(), t, "neutral", bob=False, name="Alex")
            emoji(c, "➡️", W / 2, 700, 100)
            person(c, 810, 850, 340, ALEXA, t, "smug", bob=False, name="Alexia")
            # Aufzählung UNTER den Figuren, überdeckt niemanden
            chips = [("Perücke", "💇", 0.35), ("Make-up", "💄", 0.55), ("Minirock", "👠", 0.75)]
            for i, (lab, ic, f) in enumerate(chips):
                if t > S.at(1, f):
                    x = 240 + i * 300
                    def chip(x=x, lab=lab, ic=ic):
                        rrect(c, x - 135, 885, 270, 74, 37); fill(c, "#B0307A")
                        text(c, ic + " " + lab + " ✅", x, 922, 32, "#FFFFFF", FONT_HEAD)
                    scaled(c, x, 922, pop(t, S.at(1, f), 0.25), chip)
        scaled(c, W / 2, 680, s, makeover)
        alexa_bottom(c, S, "smug", "hips")
        sparkle_lines(c, t, a1 + 0.1, W / 2, FEET - AH * 0.7, n=12, r0=200, r1=360, d=0.5)


def sc_morning(c, S):
    t, a1 = S.t, S.at(1)
    if t < a1 + 0.2:
        o = out_fade(t, a1)
        s = pop(t, S.at(0, 0.0)) * o
        def table():
            card(c, W / 2, 700, 900, 560, 1)
            text(c, "NATURAL LOOK ✨", W / 2, 470, 52, INK, FONT_HEAD)
            for i, e in enumerate(["💄", "💅", "🪮", "🧴", "🪞"]):
                emoji(c, e, 180 + i * 180, 640, 110 * pop(t, S.at(0, 0.15 + 0.08 * i)), rot=math.sin(t * 3 + i) * 0.1)
            mins = int(120 * clamp((t - S.at(0, 0.4)) / 1.4))
            text(c, f"⏱ {mins // 60}:{mins % 60:02d} h", W / 2, 830, 70, "#B0307A", FONT_HEAD)
        scaled(c, W / 2, 700, s * o, table)
        alexa_bottom(c, S, "neutral", "idle")
    else:
        ring_light(c, W / 2, 640, 230, pop(t, a1 + 0.05), t)
        n = int(300 * clamp((t - S.at(1, 0.2)) / 1.2)) if t > S.at(1, 0.2) else 0
        flash = (int(t * 12) % 2 == 0) and t < S.at(1, 0.75)
        if flash and t > S.at(1, 0.2):
            emoji(c, "📸", 860, 470, 90, rot=0.2)
        def counter():
            rrect(c, 220, 900, 640, 100, 50); fill(c, "#1F1F28")
            txt = f"Fotos: {n}" if t < S.at(1, 0.75) else "Gepostet: 1 ✅"
            text(c, txt, W / 2, 950, 46, "#FFFFFF", FONT_HEAD)
        scaled(c, W / 2, 950, pop(t, S.at(1, 0.15)), counter)
        if S.at(1, 0.12) < t:
            def aus():
                rrect(c, 375, 607, 330, 66, 18); fill(c, "#E8457A")
                text(c, "Ausschnitt richten ✨", 540, 640, 30, "#FFFFFF", FONT_HEAD)
            scaled(c, 540, 640, pop(t, S.at(1, 0.12)), aus, rot=-0.04 + 0.02 * math.sin(t * 5))
        alexa_bottom(c, S, "smug", "phone", "📱")


def sc_promo(c, S):
    t = S.t
    for i, (x, y, rot, col) in enumerate(((250, 620, -0.08, "#36B5C2"), (540, 700, 0.0, "#F2B233"), (830, 620, 0.08, "#2FA36B"))):
        s = pop(t, S.at(0, 0.1 + 0.15 * i))
        def post(x=x, y=y, col=col):
            rrect(c, x - 140, y - 230, 280, 460, 28); fill(c, "#17171C")
            rrect(c, x - 128, y - 218, 256, 436, 20); fill(c, col)
            person(c, x, y + 200, 300, ALEXA, t, "smug", bob=False)
            rrect(c, x - 115, y + 120, 230, 60, 30); fill(c, "#FFFFFF")
            text(c, "Link in Bio 😉", x, y + 150, 28, INK, FONT_HEAD)
        scaled(c, x, y, s, post, rot)
    for i in range(4):
        ts = S.at(0, 0.6 + 0.08 * i)
        emoji(c, "🔗", 160 + i * 250, 1020 + (i % 2) * 40, 80 * pop(t, ts), rot=i * 0.4)
    alexa_bottom(c, S, "smug", "phone", "📱")


def sc_dms(c, S):
    t, a1, a2, a3 = S.t, S.at(1), S.at(2), S.at(3)
    s = pop(t, S.at(0, 0.0))
    px = W / 2 - 120 if t > S.at(3, 0.35) else W / 2
    x0, y0, w, h = phone(c, px, 690, 520, 820, s, screen="#FFFFFF")
    def screen():
        c.save(); rrect(c, x0, y0, w, h, 42); c.clip()
        chat_header(c, x0, y0, w, "Fans 💬", "#7A8A96")
        y = y0 + 190          # Oberkante der nächsten Nachricht
        def fan(name, msg, t0):
            nonlocal y
            text(c, name, x0 + 30, y + 14, 22, "#777777", FONT_BOLD, anchor="l")
            lines = wrap(c, msg, 30, w - 140, FONT_BOLD)
            bh = len(lines) * 30 * 1.25 + 26
            chat_msg(c, msg, x0, w, y + 36 + bh, False, pop(t, t0, 0.25))
            y += 36 + bh + 24
        if t > a1:
            fan("Fan_2847", "Du bist die Einzige, die mich versteht 🥺", a1 + 0.05)
        if t > a2:
            fan("Thomas_77", "Hab dir Trinkgeld geschickt 💸 Heiratest du mich? 💍", a2 + 0.05)
        if t > a3:
            chat_msg(c, "Du auch, Babe 😘", x0, w, y + 70, True, pop(t, a3 + 0.05, 0.2))
        c.restore()
        badge = min(999, int(999 * clamp((t - S.at(0, 0.1)) / 1.5)))
        c.arc(x0 + w - 6, y0 + 6, 46, 0, 2 * math.pi); fill(c, "#E23B3B")
        text(c, str(badge), x0 + w - 6, y0 + 6, 32, "#FFFFFF", FONT_HEAD)
    scaled(c, x0 + w / 2, 690, s, screen)
    if t > S.at(3, 0.35):
        ks = pop(t, S.at(3, 0.35))
        def kevin():
            person(c, 860, 1160, 380, KEVIN, t, "neutral", bob=False)
            rrect(c, 720, 1000, 280, 30, 8); fill(c, "#B07A4F")
            emoji(c, "💻", 860, 960, 110)
            emoji(c, "🥤", 980, 960, 60)
            rrect(c, 700, 600, 320, 80, 16); fill(c, "#FFE14D")
            text(c, "KEVIN · CHATTER", 860, 640, 36, INK, FONT_HEAD)
        scaled(c, 860, 900, ks, kevin)
    alexa_bottom(c, S, "smug", "idle", x=320 if t > S.at(3, 0.35) else W / 2)


def sc_family(c, S):
    t, a1 = S.t, S.at(1)
    s = pop(t, S.at(0, 0.0))
    def table():
        for x, sp, nm in ((260, MAMA, None), (540, OMA, "Oma"), (820, OPA, "Opa")):
            ex = "happy" if t < a1 + 0.8 else ("shock" if sp is OPA else "neutral")
            person(c, x, 1000, 420, sp, t, ex, blink_seed=x % 7, name=nm)
        rrect(c, 90, 860, 900, 60, 16); fill(c, "#B07A4F")
        rrect(c, 90, 860, 900, 60, 16); c.set_line_width(5); src(c, INK); c.stroke()
        for x, e in ((260, "🍗"), (540, "🥔"), (820, "🥗")):
            emoji(c, e, x, 840, 70)
    scaled(c, W / 2, 800, s, table)
    if t < a1 + 0.1:
        bubble(c, "Und, was machst du so beruflich? 😊", 540, 450, pop(t, S.at(0, 0.3)) * out_fade(t, a1),
               tail=(0, 1), size=40, max_w=640)
    else:
        bubble(c, "Content Creatorin … im Bereich Fitness 💪😅", 540, 985, pop(t, a1 + 0.05), tail=(0, 1), size=40, max_w=640)
        if t > a1 + 0.8:
            emoji(c, "🤨", 540, 470, 80 * pop(t, a1 + 0.8))
    alexa_bottom(c, S, "cringe" if t > a1 else "happy", "idle")
    if t > a1 + 0.3:
        emoji(c, "💦", 680, 1250 + math.sin(t * 6) * 6, 60)


def sc_boss(c, S):
    t, a1 = S.t, S.at(1)
    if t < a1 + 0.2:
        o = out_fade(t, a1)
        def post():
            card(c, W / 2, 700, 900, 560, 1)
            c.arc(170, 490, 50, 0, 2 * math.pi); fill(c, "#F07FB0")
            text(c, "A", 170, 490, 50, "#FFFFFF", FONT_HEAD)
            text(c, "alexia.exklusiv", 240, 490, 34, INK, FONT_HEAD, anchor="l")
            text_block(c, "Ich bin keine Influencerin. Ich bin UNTERNEHMERIN. 👑💼", W / 2, 680, 50, 780, INK, FONT_HEAD)
            text(c, "#bossbabe #ceo #grind", W / 2, 860, 34, "#3D8BFF", FONT_BOLD)
        scaled(c, W / 2, 700, pop(t, S.at(0, 0.05)) * o, post)
    else:
        s = pop(t, a1 + 0.05)
        def office():
            card(c, W / 2, 690, 900, 560, 1, color="#FFF4F8")
            text(c, "DAS BÜRO", W / 2, 460, 48, INK, FONT_HEAD)
            emoji(c, "🛏️", 370, 720, 220)
            ring_light(c, 800, 640, 90, 1, t)
            if t > S.at(1, 0.5):
                rrect(c, 610, 850, 330, 70, 16); fill(c, "#FFE14D")
                text(c, "TEAM: 💡 × 1", 775, 885, 36, INK, FONT_HEAD)
        scaled(c, W / 2, 690, s, office)
    alexa_bottom(c, S, "smug", "hips")


def sc_signs(c, S):
    t = S.t
    items = [("Link in Bio", "🔗"), ("Nennt sich CEO", "👑"), ("Ringlicht immer dabei", "💡"), ("Jeder Fan heißt Babe", "😘")]
    for i, (lab, ic) in enumerate(items):
        y = 420 + i * 175
        row_card(c, W / 2, y, 900, 140, pop(t, S.at(i + 1, 0.0)), lab, ic, 44, num=i + 1, rot=(-0.02 if i % 2 else 0.02))
    alexa_bottom(c, S, "smug", "shrug")


def sc_outro(c, S):
    t, a1 = S.t, S.at(1)
    q = "Kennst du jemanden, der auch mit OF starten sollte?" if t < a1 else "Was soll Alex morgen sein?"
    qs = pop(t, S.at(0, 0.0)) if t < a1 else pop(t, a1)
    card(c, W / 2, 230, 920, 170, qs)
    scaled(c, W / 2, 230, qs, lambda: text_block(c, q, W / 2, 230, 46, 860, INK, FONT_HEAD))
    if t < a1 + 0.2:
        out = out_fade(t, a1)
        s = pop(t, S.at(0, 0.3)) * out
        def tag():
            c.arc(W / 2, 640, 210, 0, 2 * math.pi); fill(c, "#FFFFFF")
            c.arc(W / 2, 640, 210, 0, 2 * math.pi); c.set_line_width(8); src(c, INK); c.stroke()
            text(c, "@", W / 2, 625, 300, "#B0307A", FONT_HEAD)
            rrect(c, 160, 900, 760, 100, 50); fill(c, "#FFFFFF")
            rrect(c, 160, 900, 760, 100, 50); c.set_line_width(5); src(c, INK); c.stroke()
            typed = "@die_neue_ceo"
            n = int(clamp((t - S.at(0, 0.45)) / 1.0) * len(typed))
            cur = "|" if int(t * 3) % 2 == 0 else ""
            text(c, typed[:n] + cur, 210, 950, 44, "#3D8BFF", FONT_HEAD, anchor="l")
        scaled(c, W / 2, 700, s, tag, rot=math.sin(t * 4) * 0.02)
        emoji(c, "👇", 880, 1110 + math.sin(t * 8) * 12, 90 * pop(t, S.at(0, 0.6)) * out)
    if t >= a1:
        colors = ["#EC7FAE", "#2B2D5E", "#B0307A", "#F2B233", "#3E7BDA", "#8E5BE0", "#36B5C2", "#F07F4F", "#555A66"]
        # TikTok-Reihenfolge: Folge 1 Pick-me-Boy, Folge 2 F-Boy, heute Folge 3
        prev = [("🌹", "FOLGE 1"), ("😏", "FOLGE 2"), ("📸", "HEUTE ✅")]
        for i in range(9):
            r, cc = i // 3, i % 3
            x, y = 260 + cc * 280, 500 + r * 230
            def icon(x=x, y=y, i=i):
                c.arc(x, y, 95, 0, 2 * math.pi); fill(c, colors[i])
                c.arc(x, y, 95, 0, 2 * math.pi); c.set_line_width(6); src(c, "#FFFFFF"); c.stroke()
                if i < len(prev):
                    e, lab = prev[i]
                    emoji(c, e, x, y, 100)
                    rrect(c, x - 85, y + 70, 170, 46, 12); fill(c, "#2FA36B" if i == len(prev) - 1 else "#555A66")
                    text(c, lab, x, y + 93, 26, "#FFFFFF", FONT_HEAD)
                else:
                    text(c, "?", x, y, 110, "#FFFFFF", FONT_HEAD)
            scaled(c, x, y, pop(t, a1 + 0.1 + i * 0.07), icon)
        ps = pop(t, S.at(1, 0.45))
        def pill():
            rrect(c, 170, 1040, 740, 96, 48); fill(c, "#E23B3B")
            text(c, "Schreib's in die Kommentare ⬇️", W / 2, 1088, 42, "#FFFFFF", FONT_HEAD)
        scaled(c, W / 2, 1088, ps * (1 + 0.04 * math.sin(t * 7)), pill)
    alexa_bottom(c, S, "happy", "wave")


SCENE_DRAW = dict(what=sc_what, morning=sc_morning, promo=sc_promo, dms=sc_dms, family=sc_family,
                  boss=sc_boss, signs=sc_signs, outro=sc_outro)


_MOTION = dict(what="bounce", morning="glow", promo="bounce", dms="buzz", family="wobble", boss="bounce")
_FX = dict(what=["💄", "💅", "✨"], morning=["📸", "✨", "💡"], promo=["🔗", "💸", "✨"], dms=["💌", "💬", "❤️"],
           family=["😅", "🍗", "✨"], boss=["💼", "👑", "💸"])


def _line_t0(S):
    t0 = None
    for st in S.S.starts:
        if S.t >= st:
            t0 = st
    return t0


def _scaled_scene(fn, k=CONTENT_SCALE, dy=0, sid=""):
    def run(c, S):
        t = S.t
        _BASE[0] = c.get_matrix()
        kind = _MOTION.get(sid)
        t0 = _line_t0(S)
        u = (t - t0) / 0.5 if t0 is not None else 9
        punch = 1 + 0.06 * math.sin(clamp(u) * math.pi) if kind else 1      # Puls bei jeder neuen Zeile
        dx = rot = 0.0; sc_ = 1.0; dyy = 0.0
        if kind == "bounce":
            sc_ = 1 + 0.018 * abs(math.sin(t * math.pi * 2)); rot = 0.012 * math.sin(t * math.pi)
        elif kind == "wobble":
            rot = 0.02 * math.sin(t * 3.2)
        elif kind == "buzz":                                            # Handy vibriert bei Nachrichten
            if u < 1.2:
                dx = 7 * math.sin(t * 60) * (1 - clamp(u / 1.2)); rot = 0.02 * math.sin(t * 45) * (1 - clamp(u / 1.2))
        elif kind == "glow":
            dyy = 4 * math.sin(t * 2.5)
        if kind and u < 0.5:
            dx += 10 * math.sin(u * 30) * (1 - u / 0.5)
        cy = 430 + dy + 300
        c.save()
        c.translate(W / 2 + dx, cy + dyy); c.rotate(rot); c.scale(sc_ * punch, sc_ * punch); c.translate(-W / 2, -cy)
        c.translate(W / 2, 430 + dy); c.scale(k, k); c.translate(-W / 2, -430)
        fn(c, S)
        c.restore()
        _BASE[0] = None
        if kind and t0 is not None and 0 <= t - t0 < 1.0:                # Emojis schießen aus den Ecken
            v = (t - t0) / 1.0
            ems = _FX.get(sid, ["✨"])
            for i, (cx_, cy_, sx, sy) in enumerate(((70, 420, -1, -1), (1010, 420, 1, -1), (70, 1080, -1, 1), (1010, 1080, 1, 1))):
                for j in range(2):
                    d = 40 + 160 * ease_out_cubic(v) + j * 50
                    emoji(c, ems[(i + j) % len(ems)], cx_ + sx * d * 0.5, cy_ + sy * d * 0.35, 60 * (1 - v * 0.4),
                          rot=v * 2 * sx, alpha=1 - v)
    return run


SCENE_DRAW = {k: _scaled_scene(v, *((1.0, 45) if k == "dms" else (CONTENT_SCALE, 0)), sid=k) for k, v in SCENE_DRAW.items()}
