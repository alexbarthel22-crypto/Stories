"""Visuals für Folge 4 (Milliardär). Eigene Szenen, keine Übernahme aus dem Referenzvideo."""
import math, random
from alexlib import *

# Outfit heute: grauer Kaschmir-Pulli (3.000 €), dunkle Chino, weiße Designer-Sneaker
AL = alex(top="#9AA0A8", top_style="tee", pants="#2A2F3A", shoes="#FFFFFF")
FEET, AH = 1665, 470

INTRO = dict(icon="💰", bg="#1F6B4A", spec=AL, expr="smug", pose="hips", hand_prop=None,
             side_emoji="💎", burst=["💰", "💎", "🛥️", "🥂", "💸", "✈️", "🍾", "💵"])


def draw_intro(c, t, shuffle, ticks, flash_start, reveal_t, role_text):
    draw_intro_generic(c, t, shuffle, ticks, flash_start, reveal_t, role_text, INTRO)


def alex_bottom(c, S, expr="smug", pose="idle", prop=None, x=W / 2, h=AH):
    person(c, x, FEET, h, AL, S.t, expr, pose, prop, name="Alex")


def out_fade(t, t_end, d=0.2):
    return 1 - ease_out_cubic((t - t_end) / d) if t > t_end else 1


def fmt(n):
    return f"{int(n):,}".replace(",", ".")


def counter(t, t0, d, target):
    return target * ease_out_cubic((t - t0) / d) if t > t0 else 0


def row_card(c, x, y, w, h, s, label, icon=None, size=40, num=None, rot=0.0):
    def d():
        rrect(c, x - w / 2 + 6, y - h / 2 + 10, w, h, 22); src(c, "#000000", 0.2); c.fill()
        rrect(c, x - w / 2, y - h / 2, w, h, 22); fill(c, "#FFFFFF")
        rrect(c, x - w / 2, y - h / 2, w, h, 22); c.set_line_width(5); src(c, INK); c.stroke()
        lx = x - w / 2 + 40
        if num is not None:
            c.arc(x - w / 2 + 75, y, 42, 0, 2 * math.pi); fill(c, "#D4AF37")
            text(c, str(num), x - w / 2 + 75, y, 46, "#FFFFFF", FONT_HEAD)
            lx = x - w / 2 + 140
        text(c, label, lx, y, size, INK, FONT_HEAD, anchor="l")
        if icon:
            emoji(c, icon, x + w / 2 - 60, y, 56)
    scaled(c, x, y, s, d, rot)


def money_rain(c, t, t0, n=14, seed=4):
    if t < t0:
        return
    rnd = random.Random(seed)
    for i in range(n):
        x = rnd.uniform(60, W - 60)
        sp = rnd.uniform(180, 320)
        y = (rnd.uniform(0, 1500) + (t - t0) * sp) % 1500 + 330
        emoji(c, rnd.choice(["💵", "💶", "💸"]), x, y, 60, rot=math.sin(t * 3 + i) * 0.4, alpha=0.55)


# ======================================================================= SZENEN
def sc_what(c, S):
    t, a1 = S.t, S.at(1)
    s = pop(t, S.at(0, 0.0))
    money_rain(c, t, 0)
    def panel():
        card(c, W / 2, 560, 940, 330, 1)
        text(c, "1 MILLIARDE", W / 2, 460, 56, INK, FONT_HEAD)
        text(c, "1.000.000.000 €", W / 2, 570, 92, "#1F6B4A", FONT_HEAD)
        text(c, "= 1.000 × 1 Million", W / 2, 660, 38, "#777777", FONT_BOLD)
    scaled(c, W / 2, 560, s, panel)
    if t >= a1:
        def years():
            card(c, W / 2, 920, 820, 280, 1, color="#1F1F28")
            text(c, "1.000 € AUSGEBEN · JEDEN TAG", W / 2, 830, 34, "#BBBBBB", FONT_HEAD)
            if t > S.at(1, 0.4):
                text(c, fmt(counter(t, S.at(1, 0.4), 1.2, 2740)) + " JAHRE", W / 2, 930, 96, "#F7C948", FONT_HEAD)
            text(c, "bis das Geld weg ist", W / 2, 1010, 32, "#BBBBBB", FONT_BOLD)
        scaled(c, W / 2, 920, pop(t, a1 + 0.05), years)
    alex_bottom(c, S, "smug", "hips")


def sc_minwage(c, S):
    t = S.t
    s = pop(t, S.at(0, 0.0))
    def panel():
        card(c, W / 2, 680, 920, 640, 1)
        text(c, "MINDESTLOHN 2026", W / 2, 430, 50, INK, FONT_HEAD)
        rrect(c, W / 2 - 200, 480, 400, 90, 45); fill(c, "#2FA36B")
        text(c, "13,90 € / Std.", W / 2, 525, 48, "#FFFFFF", FONT_HEAD)
        emoji(c, "⏳", W / 2, 660, 120, rot=math.sin(t * 2) * 0.2)
        if t > S.at(0, 0.45):
            text(c, fmt(counter(t, S.at(0, 0.45), 1.4, 34000)) + "+ JAHRE", W / 2, 810, 96, "#E23B3B", FONT_HEAD)
        text(c, "Vollzeit, für 1 Milliarde (brutto)", W / 2, 900, 32, "#777777", FONT_BOLD)
    scaled(c, W / 2, 680, s, panel)
    alex_bottom(c, S, "shock" if t > S.at(0, 0.6) else "smug", "idle")


def sc_morning(c, S):
    t, a1 = S.t, S.at(1)
    if t < a1 + 0.2:
        o = out_fade(t, a1)
        for i, (e, lab, f) in enumerate((("🧊", "EISBAD", 0.15), ("🧘", "MEDITATION", 0.4), ("🥤", "SMOOTHIE", 0.65))):
            x = 200 + i * 340
            def d(x=x, e=e, lab=lab):
                card(c, x, 700, 300, 380, 1)
                emoji(c, e, x, 660, 150)
                text(c, lab, x, 820, 38, INK, FONT_HEAD)
            scaled(c, x, 700, pop(t, S.at(0, f)) * o, d, rot=(-0.04 + 0.04 * i))
    else:
        def pod():
            card(c, W / 2, 700, 880, 520, 1, color="#1F1F28")
            emoji(c, "🎙️", W / 2, 590, 170)
            text(c, "ALEX TALKS MINDSET", W / 2, 760, 54, "#F7C948", FONT_HEAD)
            text(c, "Folge 412 · Gast: Alex", W / 2, 840, 36, "#BBBBBB", FONT_BOLD)
        scaled(c, W / 2, 700, pop(t, a1 + 0.05), pod)
    alex_bottom(c, S, "happy" if t < a1 else "smug", "idle", "🥤" if t < a1 else None)


def sc_selfmade(c, S):
    t, a1 = S.t, S.at(1)
    def quote():
        card(c, W / 2, 560, 880, 300, 1)
        emoji(c, "💪", 180, 560, 90)
        text_block(c, "„Ich hab bei NULL angefangen.“", W / 2 + 50, 560, 50, 640, INK, FONT_HEAD)
    scaled(c, W / 2, 560, pop(t, S.at(0, 0.1)), quote, rot=-0.02)
    if t >= a1:
        def cheque():
            c.save(); c.translate(W / 2, 940); c.rotate(0.04)
            rrect(c, -420, -150, 840, 300, 18); fill(c, "#E9F5EC")
            rrect(c, -420, -150, 840, 300, 18); c.set_line_width(5); src(c, INK); c.stroke()
            text(c, "SCHECK", -380, -105, 32, "#1F6B4A", FONT_HEAD, anchor="l")
            text(c, "An: Alex", -380, -40, 36, INK, FONT_BOLD, anchor="l")
            text(c, "1.000.000 €", 380, 20, 76, "#1F6B4A", FONT_HEAD, anchor="r")
            text(c, "„Startkredit“  –  Papa ❤️", -380, 95, 34, "#555555", FONT_BOLD, anchor="l")
            c.restore()
        scaled(c, W / 2, 940, pop(t, S.at(1, 0.35)), cheque)
        red_flag_stamp(c, W / 2, 560, pop(t, S.at(1, 0.85), 0.25), "NICHT SELFMADE", rot=-0.16)
    alex_bottom(c, S, "smug" if t < a1 + 1.0 else "cringe", "hips")


def sc_jet(c, S):
    t = S.t
    s = pop(t, S.at(0, 0.0))
    def sky():
        rrect(c, 70, 380, 940, 620, 30); fill(c, "#BFE6FF")
        c.save(); rrect(c, 70, 380, 940, 620, 30); c.clip()
        for i in range(4):
            x = (i * 300 - t * 80) % 1240 - 100
            emoji(c, "☁️", x, 470 + (i % 2) * 380, 140, alpha=0.9)
        u = clamp((t - S.at(0, 0.1)) / max(0.5, S.dur * 0.7))
        emoji(c, "✈️", 120 + 840 * u, 700 - 120 * math.sin(u * math.pi), 170, rot=-0.15)
        c.restore()
        rrect(c, 70, 380, 940, 620, 30); c.set_line_width(6); src(c, INK); c.stroke()
        rrect(c, 680, 880, 300, 90, 20); fill(c, "#FFFFFF")
        text(c, "→ PARIS 🥐", 830, 925, 44, INK, FONT_HEAD)
    scaled(c, W / 2, 690, s, sky)
    if t > S.at(0, 0.7):
        emoji(c, "🥐", 780, 1150, 120 * pop(t, S.at(0, 0.7)), rot=0.2)
    alex_bottom(c, S, "smug", "idle")


def sc_interest(c, S):
    t, a1 = S.t, S.at(1)
    s = pop(t, S.at(0, 0.0))
    def panel():
        card(c, W / 2, 620, 920, 520, 1)
        rrect(c, W / 2 - 160, 410, 320, 90, 45); fill(c, "#2FA36B")
        text(c, "3 % ZINSEN", W / 2, 455, 46, "#FFFFFF", FONT_HEAD)
        if t > S.at(0, 0.45):
            text(c, fmt(counter(t, S.at(0, 0.45), 1.0, 30000000)) + " €", W / 2, 620, 96, "#1F6B4A", FONT_HEAD)
        text(c, "pro Jahr", W / 2, 720, 44, "#777777", FONT_BOLD)
    scaled(c, W / 2, 620, s, panel)
    if t >= a1:
        def day():
            c.save(); c.translate(W / 2, 1010); c.rotate(-0.04)
            rrect(c, -380, -75, 760, 150, 75); fill(c, "#F7C948")
            rrect(c, -380, -75, 760, 150, 75); c.set_line_width(6); src(c, INK); c.stroke()
            text(c, "≈ 82.000 € / TAG", 0, 0, 70, INK, FONT_HEAD)
            c.restore()
        scaled(c, W / 2, 1010, pop(t, a1 + 0.1), day)
        if t > S.at(1, 0.7):
            for i in range(3):
                u = (t * 0.5 + i / 3) % 1
                emoji(c, "💤", 660 + u * 80, 1230 - u * 180, 60 + i * 8, alpha=1 - u)
    alex_bottom(c, S, "sleepy" if t > S.at(1, 0.7) else "smug", "idle")


def sc_yacht(c, S):
    t, a1 = S.t, S.at(1)
    s = pop(t, S.at(0, 0.0))
    def sea():
        rrect(c, 70, 380, 940, 640, 30); fill(c, "#18213F")
        c.save(); rrect(c, 70, 380, 940, 640, 30); c.clip()
        emoji(c, "🌙", 860, 480, 110)
        for i in range(25):
            rnd = random.Random(i)
            c.arc(rnd.uniform(90, 990), rnd.uniform(400, 700), rnd.uniform(1.5, 3.5), 0, 2 * math.pi)
            src(c, "#FFFFFF", 0.4 + 0.4 * math.sin(t * 3 + i) ** 2); c.fill()
        c.rectangle(70, 800, 940, 240); src(c, "#22407A"); c.fill()
        for i in range(8):
            y = 830 + i * 26
            c.move_to(70, y)
            for x in range(70, 1011, 20):
                c.line_to(x, y + math.sin(x * 0.03 + t * 2 + i) * 5)
            c.set_line_width(2); src(c, "#FFFFFF", 0.15); c.stroke()
        emoji(c, "🛥️", W / 2, 800 + math.sin(t * 1.5) * 10, 330)
        if t > a1:
            u = clamp((t - a1) / 1.2)
            emoji(c, "🚁", 1100 - 600 * ease_out_cubic(u), 520, 150, rot=-0.1)
            if u >= 1:
                emoji(c, "🍾", 500, 600 + math.sin(t * 5) * 8, 90)
        c.restore()
        rrect(c, 70, 380, 940, 640, 30); c.set_line_width(6); src(c, INK); c.stroke()
    scaled(c, W / 2, 700, s, sea)
    if t < a1 + 0.2:
        bubble(c, "Geld macht nicht glücklich … 😔", 540, 1085, pop(t, S.at(0, 0.45)) * out_fade(t, a1),
               tail=(0, 1), size=42)
    alex_bottom(c, S, "sad" if t < a1 else "smug", "idle", "🥂")


def sc_signs(c, S):
    t = S.t
    items = [("„Geld ist mir egal.“", "🙄"), ("Grauer Pulli: 3.000 €", "👕"), ("Hat einen Podcast", "🎙️"),
             ("Nennt sich bescheiden", "😇")]
    for i, (lab, ic) in enumerate(items):
        y = 420 + i * 175
        row_card(c, W / 2, y, 900, 140, pop(t, S.at(i + 1, 0.0)), lab, ic, 44, num=i + 1, rot=(-0.02 if i % 2 else 0.02))
    alex_bottom(c, S, "smug", "shrug", None)


def sc_outro(c, S):
    t, a1 = S.t, S.at(1)
    q = "Kennst du einen Milliardär?" if t < a1 else "Was soll Alex morgen sein?"
    qs = pop(t, S.at(0, 0.0)) if t < a1 else pop(t, a1)
    card(c, W / 2, 230, 920, 150, qs)
    scaled(c, W / 2, 230, qs, lambda: text_block(c, q, W / 2, 230, 50, 860, INK, FONT_HEAD))
    if t < a1 + 0.2:
        out = out_fade(t, a1)
        s = pop(t, S.at(0, 0.3)) * out
        def tag():
            c.arc(W / 2, 640, 210, 0, 2 * math.pi); fill(c, "#FFFFFF")
            c.arc(W / 2, 640, 210, 0, 2 * math.pi); c.set_line_width(8); src(c, INK); c.stroke()
            text(c, "@", W / 2, 625, 300, "#1F6B4A", FONT_HEAD)
            rrect(c, 160, 900, 760, 100, 50); fill(c, "#FFFFFF")
            rrect(c, 160, 900, 760, 100, 50); c.set_line_width(5); src(c, INK); c.stroke()
            typed = "@leih_mir_geld"
            n = int(clamp((t - S.at(0, 0.45)) / 1.0) * len(typed))
            cur = "|" if int(t * 3) % 2 == 0 else ""
            text(c, typed[:n] + cur, 210, 950, 44, "#3D8BFF", FONT_HEAD, anchor="l")
        scaled(c, W / 2, 700, s, tag, rot=math.sin(t * 4) * 0.02)
        emoji(c, "👇", 880, 1110 + math.sin(t * 8) * 12, 90 * pop(t, S.at(0, 0.6)) * out)
    if t >= a1:
        colors = ["#EC7FAE", "#5FA9B8", "#D9534F", "#1F6B4A", "#3E7BDA", "#8E5BE0", "#36B5C2", "#F07F4F", "#555A66"]
        prev = [("🌹", "FOLGE 1", "#555A66"), ("🛋️", "FOLGE 2", "#555A66"), ("😡", "FOLGE 3", "#555A66"),
                ("💰", "HEUTE ✅", "#2FA36B")]
        for i in range(9):
            r, cc = i // 3, i % 3
            x, y = 260 + cc * 280, 500 + r * 230
            def icon(x=x, y=y, i=i):
                c.arc(x, y, 95, 0, 2 * math.pi); fill(c, colors[i])
                c.arc(x, y, 95, 0, 2 * math.pi); c.set_line_width(6); src(c, "#FFFFFF"); c.stroke()
                if i < 4:
                    e, lab, col = prev[i]
                    emoji(c, e, x, y, 100)
                    rrect(c, x - 85, y + 70, 170, 46, 12); fill(c, col)
                    text(c, lab, x, y + 93, 26, "#FFFFFF", FONT_HEAD)
                else:
                    text(c, "?", x, y, 110, "#FFFFFF", FONT_HEAD)
            scaled(c, x, y, pop(t, a1 + 0.1 + i * 0.07), icon)
        ps = pop(t, S.at(1, 0.45))
        def pill():
            rrect(c, 170, 1040, 740, 96, 48); fill(c, "#E23B3B")
            text(c, "Schreib's in die Kommentare ⬇️", W / 2, 1088, 42, "#FFFFFF", FONT_HEAD)
        scaled(c, W / 2, 1088, ps * (1 + 0.04 * math.sin(t * 7)), pill)
    alex_bottom(c, S, "happy", "wave")


SCENE_DRAW = dict(what=sc_what, minwage=sc_minwage, morning=sc_morning, selfmade=sc_selfmade, jet=sc_jet,
                  interest=sc_interest, yacht=sc_yacht, signs=sc_signs, outro=sc_outro)
