"""Visuals für Folge 5 (F-Boy). Aufbau wie Folge 1. TikTok-tauglich, nichts Explizites."""
import math, random
from alexlib import *

# Outfit heute: enges schwarzes Shirt, Silberkette, Jeans, weiße Sneaker
AL = alex(top="#1C1C22", top_style="tee", chain="#D9D9DE", pants="#5D7FA8", shoes="#FFFFFF")
FEET, AH = 1665, 470
MIA = person_spec(12, girl=True, top="#F2B233", hair="#3B2A20", skin="#EBB894", pants="#3F4A6B", shoes="#2A2A2A")

INTRO = dict(icon="😏", bg="#2B2D5E", spec=AL, expr="smug", pose="phone", hand_prop="📱",
             side_emoji="🌙", burst=["📱", "🌙", "💪", "👻", "🚩", "😏", "💬", "🔥"])


def draw_intro(c, t, shuffle, ticks, flash_start, reveal_t, role_text):
    draw_intro_generic(c, t, shuffle, ticks, flash_start, reveal_t, role_text, INTRO)


def alex_bottom(c, S, expr="smug", pose="idle", prop=None, x=W / 2, h=AH):
    person(c, x, FEET, h, AL, S.t, expr, pose, prop, name="Alex")


def out_fade(t, t_end, d=0.2):
    return 1 - ease_out_cubic((t - t_end) / d) if t > t_end else 1


def chat_header(c, x0, y0, w, name, col="#6B3E26"):
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
        fill(c, "#3D8BFF" if mine else "#E6E6EA")
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
            c.arc(x - w / 2 + 75, y, 42, 0, 2 * math.pi); fill(c, "#E23B3B")
            text(c, str(num), x - w / 2 + 75, y, 46, "#FFFFFF", FONT_HEAD)
            lx = x - w / 2 + 140
        text(c, label, lx, y, size, INK, FONT_HEAD, anchor="l")
        if icon:
            emoji(c, icon, x + w / 2 - 60, y, 56)
    scaled(c, x, y, s, d, rot)


# ======================================================================= SZENEN
def sc_what(c, S):
    t, a1 = S.t, S.at(1)
    s = pop(t, S.at(0, 0.0))
    def wants():
        card(c, W / 2, 690, 900, 600, 1)
        text(c, "WAS ER WILL", W / 2, 450, 52, INK, FONT_HEAD)
        rows = [("Beziehung", "❌", 0.2), ("Dates", "✅", 0.4), ("Aufmerksamkeit", "✅", 0.55), ("Verpflichtungen", "❌", 0.7)]
        for i, (lab, mark, f) in enumerate(rows):
            y = 560 + i * 100
            if t > S.at(0, f):
                text(c, lab, 170, y, 46, INK, FONT_HEAD, anchor="l")
                emoji(c, mark, 900, y, 64 * pop(t, S.at(0, f), 0.25))
    scaled(c, W / 2, 690, s, wants)
    alex_bottom(c, S, "smug", "hips")
    if t >= a1:
        bubble(c, "Ich will mich gerade auf nichts festlegen 😏", W / 2, 1075, pop(t, a1), tail=(0.2, 1), size=40, max_w=700)


def sc_seen(c, S):
    t, a1 = S.t, S.at(1)
    s = pop(t, S.at(0, 0.0))
    x0, y0, w, h = phone(c, W / 2, 720, 540, 880, s, screen="#FFFFFF")
    def screen():
        c.save(); rrect(c, x0, y0, w, h, 42); c.clip()
        chat_header(c, x0, y0, w, "Alex", ALEX_BASE["hair"])
        chat_msg(c, "Hast du heute Lust auf Kino? 🙂", x0, w, y0 + 330, True, 1)
        text(c, "Gelesen 07:02 ✓✓", x0 + w - 30, y0 + 360, 24, "#3D8BFF", FONT_BOLD, anchor="r")
        if t > a1:
            # Tippt ... und hört wieder auf
            u = (t - a1)
            if u < 1.2:
                rrect(c, x0 + 24, y0 + 430, 120, 60, 30); fill(c, "#E6E6EA")
                for k in range(3):
                    c.arc(x0 + 54 + k * 30, y0 + 460 - 6 * abs(math.sin(t * 8 + k)), 8, 0, 2 * math.pi); fill(c, "#888888")
        c.restore()
    scaled(c, W / 2, 720, s, screen)
    if t > a1 + 0.3:
        def lbl():
            c.save(); c.translate(W / 2, 1120); c.rotate(-0.04)
            rrect(c, -330, -55, 660, 110, 55); fill(c, "#1F1F28")
            text(c, "Antwort: vielleicht nachts 🌙", 0, 0, 40, "#FFFFFF", FONT_HEAD)
            c.restore()
        scaled(c, W / 2, 1120, pop(t, a1 + 0.3), lbl)
    alex_bottom(c, S, "smug", "phone", "📱", x=880, h=AH * 0.9)


def sc_gym(c, S):
    t = S.t
    s = pop(t, S.at(0, 0.0))
    def mirror():
        rrect(c, 190, 360, 700, 760, 40); fill(c, "#C9CED6")
        rrect(c, 190, 360, 700, 760, 40); c.set_line_width(6); src(c, INK); c.stroke()
        c.save(); rrect(c, 215, 385, 650, 710, 30); c.clip()
        g = cairo.LinearGradient(215, 385, 865, 1095)
        g.add_color_stop_rgb(0, 0.85, 0.93, 1.0); g.add_color_stop_rgb(1, 0.62, 0.75, 0.88)
        c.set_source(g); c.paint()
        for i in range(3):
            c.move_to(260 + i * 160, 385); c.line_to(420 + i * 160, 1095)
            c.set_line_width(24); src(c, "#FFFFFF", 0.25); c.stroke()
        person(c, W / 2, 1060, 600, AL, t, "smug", "up", bob=False)
        emoji(c, "💪", 330, 600, 90, rot=-0.3); emoji(c, "💪", 750, 600, 90, rot=0.3)
        c.restore()
    scaled(c, W / 2, 740, s, mirror)
    if t > S.at(0, 0.6):
        def cap():
            c.save(); c.translate(W / 2, 1000); c.rotate(-0.03)
            rrect(c, -330, -50, 660, 100, 16); src(c, "#000000", 0.65); c.fill()
            text(c, "Grind never stops 💪🔥", 0, 0, 44, "#FFFFFF", FONT_HEAD)
            c.restore()
        scaled(c, W / 2, 1000, pop(t, S.at(0, 0.6)), cap)
    alex_bottom(c, S, "smug", "phone", "📱")


def sc_date(c, S):
    t, a1 = S.t, S.at(1)
    alex_x, mia_x = 320, 790
    s = pop(t, S.at(0, 0.0))
    def table():
        rrect(c, 140, 420, 800, 560, 20); fill(c, "#FFF4E6")
        rrect(c, 140, 420, 800, 560, 20); c.set_line_width(5); src(c, INK); c.stroke()
        for i in range(8):
            c.rectangle(140 + i * 100, 400, 100, 80); src(c, "#3E7BDA" if i % 2 == 0 else "#FFFFFF"); c.fill()
        c.rectangle(140, 400, 800, 80); c.set_line_width(5); src(c, INK); c.stroke()
        # Redeanteil
        text(c, "REDEANTEIL", W / 2, 560, 44, INK, FONT_HEAD)
        u = ease_out_cubic((t - S.at(0, 0.3)) / 0.8)
        rrect(c, 200, 620, 680, 80, 40); fill(c, "#EDEDF0")
        rrect(c, 200, 620, max(80, 680 * 0.97 * u), 80, 40); fill(c, "#1C1C22")
        text(c, "Alex 97 %", 240, 660, 36, "#FFFFFF", FONT_HEAD, anchor="l")
        text(c, "Mia 3 %", 860, 760, 32, "#555555", FONT_HEAD, anchor="r")
        emoji(c, "📱", 300, 880, 90 * pop(t, S.at(0, 0.6)), rot=-0.2)
        emoji(c, "☕", 540, 880, 80); emoji(c, "🥤", 760, 880, 80)
    scaled(c, W / 2, 700, s, table)
    person(c, alex_x, FEET, AH, AL, t, "smug", "phone", "📱", name="Alex")
    mia_ex = "neutral" if t < a1 + 0.5 else "cringe"
    scaled(c, mia_x, FEET, pop(t, S.at(0, 0.2)), lambda: person(c, mia_x, FEET, AH * 0.97, MIA, t, mia_ex, name="Mia", blink_seed=3))
    if t >= a1:
        bubble(c, "Lass uns das nicht labeln 😏", 430, 1070, pop(t, a1 + 0.05), tail=(-0.4, 1), size=40, max_w=520)
    if t > a1 + 0.6:
        emoji(c, "🙄", mia_x + 120, 1180, 70 * pop(t, a1 + 0.6))


def sc_chats(c, S):
    t = S.t
    s = pop(t, S.at(0, 0.0))
    x0, y0, w, h = phone(c, W / 2, 720, 560, 900, s, screen="#FFFFFF")
    names = [("Mia", "#F2B233"), ("Lea", "#EC7FAE"), ("Sophie", "#2FA36B"), ("Jana", "#8E5BE0"), ("Emily", "#36B5C2")]
    def screen():
        c.save(); rrect(c, x0, y0, w, h, 42); c.clip()
        rrect(c, x0, y0, w, 130, 0); fill(c, "#F4F4F6")
        text(c, "Chats", x0 + 40, y0 + 82, 40, INK, FONT_HEAD, anchor="l")
        for i, (n, col) in enumerate(names):
            ts = S.at(0, 0.1 + 0.11 * i)
            if t < ts:
                continue
            y = y0 + 190 + i * 130
            def row(y=y, n=n, col=col):
                c.arc(x0 + 70, y, 40, 0, 2 * math.pi); fill(c, col)
                text(c, n[0], x0 + 70, y, 40, "#FFFFFF", FONT_HEAD)
                text(c, n, x0 + 130, y - 18, 34, INK, FONT_HEAD, anchor="l")
                text(c, "Du: Hey du 😏", x0 + 130, y + 22, 28, "#666666", FONT_BOLD, anchor="l")
                text(c, "22:0" + str(len(n) % 10), x0 + w - 30, y - 18, 22, "#999999", FONT_BOLD, anchor="r")
            scaled(c, x0 + w / 2, y, pop(t, ts, 0.2), row)
        c.restore()
    scaled(c, W / 2, 720, s, screen)
    if t > S.at(0, 0.75):
        emoji(c, "📋", 160, 1110, 100 * pop(t, S.at(0, 0.75)), rot=-0.2)
        text(c, "COPY + PASTE", 330, 1110, 40 * pop(t, S.at(0, 0.75)), "#FFFFFF", FONT_HEAD)
    alex_bottom(c, S, "smug", "phone", "📱", x=860, h=AH * 0.9)


def sc_snap(c, S):
    t, a1 = S.t, S.at(1)
    s = pop(t, S.at(0, 0.0))
    x0, y0, w, h = phone(c, W / 2, 720, 560, 920, s, screen="#101018")
    def screen():
        c.save(); rrect(c, x0, y0, w, h, 42); c.clip()
        # Jawline von unten: riesiges Gesicht, nur Kinn/Mund im Bild, kühles Handylicht
        # Froschperspektive: Kinn in der Bildmitte, unten etwas gestreckt
        c.save(); c.translate(W / 2, y0 + h * 0.5); c.rotate(-0.12); c.scale(1.0, 1.15)
        person(c, 0, 1483, 2600, AL, t, "smug", bob=False)
        c.restore()
        g = cairo.LinearGradient(0, y0 + h, 0, y0)
        g.add_color_stop_rgba(0, 0.3, 0.45, 1.0, 0.25); g.add_color_stop_rgba(1, 0, 0, 0.1, 0.75)
        c.set_source(g); c.paint()
        emoji(c, "👻", x0 + 60, y0 + 70, 48)
        text(c, "23:31", x0 + w - 40, y0 + 70, 28, "#FFFFFF", FONT_BOLD, anchor="r")
        if t >= a1:
            c.rectangle(x0, y0 + h * 0.42, w, 90); src(c, "#000000", 0.6); c.fill()
            text(c, "Bist du wach? 👀", W / 2, y0 + h * 0.42 + 45, 48, "#FFFFFF", FONT_BOLD)
        c.restore()
    scaled(c, W / 2, 720, s, screen)
    if t > S.at(0, 0.6):
        def tag():
            c.save(); c.translate(860, 380); c.rotate(0.12)
            rrect(c, -150, -45, 300, 90, 20); fill(c, "#F7C948")
            text(c, "JAWLINE 📐", 0, 0, 38, INK, FONT_HEAD)
            c.restore()
        scaled(c, 860, 380, pop(t, S.at(0, 0.6)), tag)
    alex_bottom(c, S, "smug", "phone", "📱", x=880, h=AH * 0.9)


def sc_crumbs(c, S):
    t, a1 = S.t, S.at(1)
    s = pop(t, S.at(0, 0.0))
    x0, y0, w, h = phone(c, W / 2, 680, 540, 780, s, screen="#FFFFFF")
    def screen():
        c.save(); rrect(c, x0, y0, w, h, 42); c.clip()
        chat_header(c, x0, y0, w, "Alex", ALEX_BASE["hair"])
        text(c, "– 6 Tage keine Nachricht –", W / 2, y0 + 200, 26, "#999999", FONT_BOLD)
        chat_msg(c, "Vermiss dich 🥺", x0, w, y0 + 330, False, pop(t, S.at(0, 0.45), 0.25))
        if t > a1:
            text(c, "– Funkstille –", W / 2, y0 + 420, 30, "#999999", FONT_HEAD)
        c.restore()
    scaled(c, W / 2, 680, s, screen)
    if t >= a1:
        # Brotkrumen-Spur
        for i in range(5):
            ts = S.at(1, 0.2 + 0.08 * i)
            emoji(c, "🍞", 140 + i * 200, 1150 - (i % 2) * 40, 70 * pop(t, ts), rot=i * 0.5)
        red_flag_stamp(c, W / 2, 660, pop(t, S.at(1, 0.55), 0.25), "BREADCRUMBING", rot=-0.16)
    alex_bottom(c, S, "puppy" if t < a1 else "smug", "phone", "📱", x=880, h=AH * 0.9)


def sc_flags(c, S):
    t = S.t
    items = [("Schreibt nur nachts", "🌙"), ("Nichts Festes, aber alles", "🤷"), ("Antwortet tagelang nicht", "⏳"),
             ("Meldet sich, wenn du ihn vergisst", "👻")]
    for i, (lab, ic) in enumerate(items):
        y = 420 + i * 175
        row_card(c, W / 2, y, 900, 140, pop(t, S.at(i + 1, 0.0)), lab, ic, 38, num=i + 1, rot=(-0.02 if i % 2 else 0.02))
    for i in range(3):
        emoji(c, "🚩", 140 + i * 400, 1110 + math.sin(t * 3 + i) * 12, 70 * pop(t, S.at(0, 0.2 + 0.15 * i)))
    alex_bottom(c, S, "smug", "shrug")


def sc_outro(c, S):
    t, a1 = S.t, S.at(1)
    q = "Kennst du einen F-Boy?" if t < a1 else "Was soll Alex morgen sein?"
    qs = pop(t, S.at(0, 0.0)) if t < a1 else pop(t, a1)
    card(c, W / 2, 230, 920, 150, qs)
    scaled(c, W / 2, 230, qs, lambda: text_block(c, q, W / 2, 230, 50, 860, INK, FONT_HEAD))
    if t < a1 + 0.2:
        out = out_fade(t, a1)
        s = pop(t, S.at(0, 0.3)) * out
        def tag():
            c.arc(W / 2, 640, 210, 0, 2 * math.pi); fill(c, "#FFFFFF")
            c.arc(W / 2, 640, 210, 0, 2 * math.pi); c.set_line_width(8); src(c, INK); c.stroke()
            text(c, "@", W / 2, 625, 300, "#2B2D5E", FONT_HEAD)
            rrect(c, 160, 900, 760, 100, 50); fill(c, "#FFFFFF")
            rrect(c, 160, 900, 760, 100, 50); c.set_line_width(5); src(c, INK); c.stroke()
            typed = "@schreibt_nur_nachts"
            n = int(clamp((t - S.at(0, 0.4)) / 1.0) * len(typed))
            cur = "|" if int(t * 3) % 2 == 0 else ""
            text(c, typed[:n] + cur, 200, 950, 40, "#3D8BFF", FONT_HEAD, anchor="l")
        scaled(c, W / 2, 700, s, tag, rot=math.sin(t * 4) * 0.02)
        emoji(c, "👇", 880, 1110 + math.sin(t * 8) * 12, 90 * pop(t, S.at(0, 0.6)) * out)
    if t >= a1:
        colors = ["#EC7FAE", "#5FA9B8", "#D9534F", "#1F6B4A", "#2B2D5E", "#8E5BE0", "#36B5C2", "#F07F4F", "#555A66"]
        prev = [("🌹", "FOLGE 1"), ("🛋️", "FOLGE 2"), ("😡", "FOLGE 3"), ("💰", "FOLGE 4"), ("😏", "HEUTE ✅")]
        for i in range(9):
            r, cc = i // 3, i % 3
            x, y = 260 + cc * 280, 500 + r * 230
            def icon(x=x, y=y, i=i):
                c.arc(x, y, 95, 0, 2 * math.pi); fill(c, colors[i])
                c.arc(x, y, 95, 0, 2 * math.pi); c.set_line_width(6); src(c, "#FFFFFF"); c.stroke()
                if i < 5:
                    e, lab = prev[i]
                    emoji(c, e, x, y, 100)
                    rrect(c, x - 85, y + 70, 170, 46, 12); fill(c, "#2FA36B" if i == 4 else "#555A66")
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


SCENE_DRAW = dict(what=sc_what, seen=sc_seen, gym=sc_gym, date=sc_date, chats=sc_chats, snap=sc_snap,
                  crumbs=sc_crumbs, flags=sc_flags, outro=sc_outro)
