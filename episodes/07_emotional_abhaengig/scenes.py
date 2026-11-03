"""Visuals: Alex ist heute emotional abhängig (TikTok Folge 4). Aufbau wie Pick-me-Boy.
Ton: nachvollziehbar-lustig, nicht herablassend; am Ende ein kurzer ehrlicher Moment.
"""
import math, random
from alexlib import *

# Outfit heute: übergroßer Kuschel-Hoodie, Jogger
AL = alex(top="#7FA3D6", top_style="hoodie", pants="#4A5570", shoes="#FFFFFF")
FEET, AH = 1665, 470
SOPHIE = person_spec(14, girl=True, top="#F07FB0", hair="#5A3A22", skin="#F1C9A8", pants="#3F4A6B", shoes="#FFFFFF")

INTRO = dict(icon="🥺", bg="#3E5C9A", spec=AL, expr="puppy", pose="phone", hand_prop="📱",
             side_emoji="💬", burst=["🥺", "💬", "📱", "⏳", "💔", "❓", "🫠", "👀"])


def draw_intro(c, t, shuffle, ticks, flash_start, reveal_t, role_text):
    draw_intro_generic(c, t, shuffle, ticks, flash_start, reveal_t, role_text, INTRO)


def alex_bottom(c, S, expr="puppy", pose="phone", prop="📱", x=W / 2, h=AH):
    person(c, x, FEET, h, AL, S.t, expr, pose, prop, name="Alex")


def out_fade(t, t_end, d=0.2):
    return 1 - ease_out_cubic((t - t_end) / d) if t > t_end else 1


def chat_header(c, x0, y0, w, name, sub=None, col="#5A3A22"):
    rrect(c, x0, y0, w, 140, 0); fill(c, "#F4F4F6")
    c.arc(x0 + 70, y0 + 82, 30, 0, 2 * math.pi); fill(c, col)
    text(c, name, x0 + 115, y0 + (70 if sub else 82), 32, INK, FONT_HEAD, anchor="l")
    if sub:
        text(c, sub, x0 + 115, y0 + 108, 22, "#2FA36B", FONT_BOLD, anchor="l")


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
            c.arc(x - w / 2 + 75, y, 42, 0, 2 * math.pi); fill(c, "#3E5C9A")
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
    def baro():
        card(c, W / 2, 680, 900, 520, 1)
        text(c, "ALEX' LAUNE", W / 2, 480, 50, INK, FONT_HEAD)
        rrect(c, 160, 640, 760, 60, 30)
        g = cairo.LinearGradient(160, 0, 920, 0)
        g.add_color_stop_rgb(0, *rgb("#3E5C9A")[:3]); g.add_color_stop_rgb(1, *rgb("#FF9EC4")[:3])
        c.set_source(g); c.fill()
        emoji(c, "😭", 150, 760, 80); emoji(c, "😍", 930, 760, 80)
        # Zeiger springt hin und her – je nachdem, ob sie antwortet
        u = 0.5 + 0.48 * math.sin(t * 3.2)
        x = 160 + 760 * u
        c.move_to(x - 26, 610); c.line_to(x + 26, 610); c.line_to(x, 650); c.close_path(); fill(c, INK)
        text(c, "gesteuert von: Sophies Antworten 📱", W / 2, 860, 32, "#555555", FONT_BOLD)
    scaled(c, W / 2, 680, s, baro)
    alex_bottom(c, S, "puppy" if t > a1 else "neutral")
    if t >= a1:
        bubble(c, "Ohne dich bin ich nichts 🥺", W / 2, 1075, pop(t, a1), tail=(0.2, 1), size=42, max_w=640)


def sc_morning(c, S):
    t, a1 = S.t, S.at(1)
    if t < a1 + 0.2:
        o = out_fade(t, a1)
        s = pop(t, S.at(0, 0.0)) * o
        x0, y0, w, h = phone(c, W / 2, 700, 520, 780, s, screen="#FFFFFF")
        def screen():
            c.save(); rrect(c, x0, y0, w, h, 42); c.clip()
            chat_header(c, x0, y0, w, "Sophie ❤️")
            chat_msg(c, "Guten Morgen! Gut geschlafen? 🥰☀️", x0, w, y0 + 300, True, 1)
            chat_msg(c, "ok", x0, w, y0 + 420, False, pop(t, S.at(0, 0.25), 0.25))
            c.restore()
        scaled(c, W / 2, 700, s, screen)
        if t > S.at(0, 0.6):
            text(c, "„ok“ ≠ „okay“ 😳", W / 2, 1110, 60 * pop(t, S.at(0, 0.6)), "#FFFFFF", FONT_HEAD)
    else:
        s = pop(t, a1 + 0.05)
        def board():
            rrect(c, 100, 380, 880, 680, 20); fill(c, "#B07A4F")
            rrect(c, 100, 380, 880, 680, 20); c.set_line_width(6); src(c, INK); c.stroke()
            rrect(c, 130, 410, 820, 620, 10); fill(c, "#D9B98E")
            notes = [(300, 540, "„ok“ statt „okay“?!", -0.06), (760, 520, "Kein Emoji 😱", 0.05),
                     (300, 860, "Kein Punkt.", 0.04), (760, 880, "Sauer auf mich??", -0.05)]
            pts = []
            for i, (x, y, txt, r) in enumerate(notes):
                if t > S.at(1, 0.1 + 0.15 * i):
                    c.save(); c.translate(x, y); c.rotate(r)
                    rrect(c, -170, -70, 340, 140, 6); fill(c, "#FFF7A8")
                    text_block(c, txt, 0, 0, 34, 300, INK, FONT_HEAD)
                    c.restore()
                    c.arc(x, y - 62, 10, 0, 2 * math.pi); fill(c, "#E23B3B")
                    pts.append((x, y - 62))
            c.set_line_width(4); src(c, "#E23B3B")
            for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
                c.move_to(xa, ya); c.line_to(xb, yb)
            c.stroke()
            emoji(c, "🔎", W / 2, 700, 130, rot=math.sin(t * 2) * 0.2)
        scaled(c, W / 2, 720, s, board)
    alex_bottom(c, S, "puppy" if t > S.at(0, 0.3) else "happy")


def sc_online(c, S):
    t, a1 = S.t, S.at(1)
    s = pop(t, S.at(0, 0.0))
    x0, y0, w, h = phone(c, W / 2, 720, 540, 880, s, screen="#FFFFFF")
    def screen():
        c.save(); rrect(c, x0, y0, w, h, 42); c.clip()
        chat_header(c, x0, y0, w, "Sophie ❤️", "zuletzt online vor 2 Min.")
        chat_msg(c, "Was machst du heute? 🥰", x0, w, y0 + 300, True, 1)
        text(c, "Gelesen ✓✓", x0 + w - 30, y0 + 330, 22, "#3D8BFF", FONT_BOLD, anchor="r")
        if t > a1:
            y = y0 + 440
            for i, m in enumerate(["?", "??", "Alles gut? 🥺"]):
                ts = S.at(1, 0.2 + 0.25 * i)
                if t > ts:
                    bh = chat_msg(c, m, x0, w, y, True, pop(t, ts, 0.2))
                    y += bh + 16
        c.restore()
    scaled(c, W / 2, 720, s, screen)
    if t > S.at(0, 0.4):
        emoji(c, "👀", 860, 400, 90 * pop(t, S.at(0, 0.4)))
    alex_bottom(c, S, "shock" if t < a1 else "puppy", x=880, h=AH * 0.9)


def sc_friends(c, S):
    t, a1 = S.t, S.at(1)
    out = 1 - clamp((t - S.at(1, 0.6)) / 0.8)
    s = pop(t, S.at(0, 0.0))
    def kumpels():
        for i, x in enumerate((250, 540, 830)):
            sp = person_spec(70 + i)
            dx = (1 - out) * (600 + i * 80)
            person(c, x + dx, 1000, 420, sp, t, "happy" if t < a1 + 0.4 else "neutral", blink_seed=i)
        emoji(c, "⚽", 540 + (1 - out) * 700, 1000, 90, rot=t * 3)
    scaled(c, W / 2, 800, s, kumpels)
    if t < a1 + 0.2:
        bubble(c, "Kommst du mit zum Fußball? ⚽", 540, 470, pop(t, S.at(0, 0.2)) * out_fade(t, a1), tail=(0, 1), size=40)
    if t >= a1:
        bubble(c, "Nee … vielleicht meldet sie sich ja 📱", 540, 1075, pop(t, a1 + 0.05), tail=(0, 1), size=40, max_w=660)
    alex_bottom(c, S, "puppy" if t > a1 else "neutral")


def sc_party(c, S):
    t, a1 = S.t, S.at(1)
    s = pop(t, S.at(0, 0.0))
    def party():
        card(c, 300, 560, 480, 400, 1, color="#2B1A3A")
        for i in range(10):
            rnd = random.Random(i)
            c.arc(rnd.uniform(80, 520), rnd.uniform(380, 740), rnd.uniform(6, 14), 0, 2 * math.pi)
            src(c, rnd.choice(["#F7C948", "#FF5CA8", "#36B5C2"]), 0.4 + 0.4 * math.sin(t * 5 + i) ** 2); c.fill()
        person(c, 230, 740, 260, SOPHIE, t, "happy", bob=False, name="Sophie")
        person(c, 380, 740, 250, person_spec(91, girl=True, top="#36B5C2"), t, "happy", bob=False)
        emoji(c, "🎉", 160, 430, 70); emoji(c, "🍹", 460, 450, 60)
    scaled(c, 300, 560, s, party)
    x0, y0, w, h = phone(c, 790, 760, 420, 760, pop(t, S.at(0, 0.3)), screen="#FFFFFF")
    def screen():
        c.save(); rrect(c, x0, y0, w, h, 42); c.clip()
        chat_header(c, x0, y0, w, "Sophie ❤️")
        if t > a1:
            msgs = ["Hast du Spaß?", "Ohne mich? 🥺", "Denkst du an mich?", "Hallo??", "Schreib mal 🥺"]
            span = S.dur - a1 - 0.5
            shown = [m for i, m in enumerate(msgs) if t > a1 + span * i / len(msgs) * 0.9]
            y = y0 + h - 30
            for m in reversed(shown):
                bh = chat_msg(c, m, x0, w, y, True, 1, size=26)
                y -= bh + 12
        c.restore()
        n = min(20, int(20 * clamp((t - a1) / max(0.5, S.dur - a1 - 0.6)))) if t > a1 else 0
        if n:
            c.arc(x0 + w - 6, y0 + 6, 42, 0, 2 * math.pi); fill(c, "#E23B3B")
            text(c, str(n), x0 + w - 6, y0 + 6, 36, "#FFFFFF", FONT_HEAD)
    scaled(c, 790, 760, pop(t, S.at(0, 0.3)), screen)
    alex_bottom(c, S, "puppy", x=300, h=AH * 0.9)


def sc_google(c, S):
    t, a1 = S.t, S.at(1)
    if t < a1 + 0.2:
        o = out_fade(t, a1)
        def search():
            card(c, W / 2, 640, 920, 420, 1)
            text(c, "Suche", 140, 500, 40, "#4A6FD0", FONT_HEAD, anchor="l")
            rrect(c, 120, 560, 840, 100, 50); fill(c, "#F1F3F6")
            rrect(c, 120, 560, 840, 100, 50); c.set_line_width(3); src(c, "#CCCCCC"); c.stroke()
            q = "wie lange darf eine antwort dauern"
            n = int(clamp((t - S.at(0, 0.3)) / 1.6) * len(q))
            text(c, "🔍 " + q[:n] + ("|" if int(t * 3) % 2 == 0 else ""), 150, 610, 32, INK, FONT_BOLD, anchor="l")
            if n == len(q):
                text(c, "Ähnliche Suchen: „warum antwortet sie nicht“", 150, 730, 28, "#777777", FONT_BOLD, anchor="l")
        scaled(c, W / 2, 640, pop(t, S.at(0, 0.0)) * o, search)
    else:
        s = pop(t, a1 + 0.05)
        x0, y0, w, h = phone(c, W / 2, 700, 520, 800, s, screen="#FFFFFF")
        def screen():
            c.save(); rrect(c, x0, y0, w, h, 42); c.clip()
            chat_header(c, x0, y0, w, "Sophie ❤️", "schreibt …" if t > S.at(1, 0.6) else "online")
            if t > S.at(1, 0.6):
                rrect(c, x0 + 24, y0 + 220, 130, 64, 32); fill(c, "#E6E6EA")
                for k in range(3):
                    c.arc(x0 + 56 + k * 32, y0 + 252 - 6 * abs(math.sin(t * 8 + k)), 9, 0, 2 * math.pi); fill(c, "#888888")
            c.restore()
        scaled(c, W / 2, 700, s, screen)
        emoji(c, "👀", 860, 1140, 90 * pop(t, a1 + 0.2))
    alex_bottom(c, S, "puppy" if t < a1 else "shock")


def sc_signs(c, S):
    t = S.t
    items = [("Tag hängt an einer Antwort", "⏳"), ("Sagt Freunde & Hobbys ab", "🚫"),
             ("Braucht ständig Bestätigung", "👍"), ("Alleinsein = Panik", "😰")]
    for i, (lab, ic) in enumerate(items):
        y = 420 + i * 175
        row_card(c, W / 2, y, 900, 140, pop(t, S.at(i + 1, 0.0)), lab, ic, 40, num=i + 1, rot=(-0.02 if i % 2 else 0.02))
    alex_bottom(c, S, "puppy", "shrug", None)


def sc_real(c, S):
    t = S.t
    s = pop(t, S.at(0, 0.0), 0.45)
    def heart():
        card(c, W / 2, 680, 880, 560, 1, color="#FFF7FA")
        emoji(c, "🫂", 330, 620, 170)
        emoji(c, "🤍", 750, 620, 170)
        text_block(c, "Du bist auch allein wertvoll.", W / 2, 840, 52, 780, INK, FONT_HEAD)
    scaled(c, W / 2, 680, s, heart)
    alex_bottom(c, S, "happy", "idle", None)


def sc_outro(c, S):
    t, a1 = S.t, S.at(1)
    q = "Kennst du jemanden, der gerade emotional abhängig ist – aber auch alleine wertvoll? 🤍" if t < a1 else "Was soll Alex morgen sein?"
    qs = pop(t, S.at(0, 0.0)) if t < a1 else pop(t, a1)
    card(c, W / 2, 240, 940, 200, qs)
    scaled(c, W / 2, 240, qs, lambda: text_block(c, q, W / 2, 240, 42, 880, INK, FONT_HEAD))
    if t < a1 + 0.2:
        out = out_fade(t, a1)
        s = pop(t, S.at(0, 0.3)) * out
        def tag():
            c.arc(W / 2, 640, 210, 0, 2 * math.pi); fill(c, "#FFFFFF")
            c.arc(W / 2, 640, 210, 0, 2 * math.pi); c.set_line_width(8); src(c, INK); c.stroke()
            text(c, "@", W / 2, 625, 300, "#3E5C9A", FONT_HEAD)
            rrect(c, 160, 900, 760, 100, 50); fill(c, "#FFFFFF")
            rrect(c, 160, 900, 760, 100, 50); c.set_line_width(5); src(c, INK); c.stroke()
            typed = "@du_bist_wertvoll"
            n = int(clamp((t - S.at(0, 0.4)) / 1.0) * len(typed))
            cur = "|" if int(t * 3) % 2 == 0 else ""
            text(c, typed[:n] + cur, 200, 950, 40, "#3D8BFF", FONT_HEAD, anchor="l")
        scaled(c, W / 2, 700, s, tag, rot=math.sin(t * 4) * 0.02)
        emoji(c, "👇", 880, 1110 + math.sin(t * 8) * 12, 90 * pop(t, S.at(0, 0.6)) * out)
    if t >= a1:
        colors = ["#EC7FAE", "#2B2D5E", "#B0307A", "#3E5C9A", "#3E7BDA", "#8E5BE0", "#36B5C2", "#F07F4F", "#555A66"]
        # TikTok-Reihenfolge: 1 Pick-me-Boy, 2 F-Boy, 3 OF-Model, heute 4
        prev = [("🌹", "FOLGE 1"), ("😏", "FOLGE 2"), ("📸", "FOLGE 3"), ("🥺", "HEUTE ✅")]
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
    alex_bottom(c, S, "happy", "wave", None)


SCENE_DRAW = dict(what=sc_what, morning=sc_morning, online=sc_online, friends=sc_friends, party=sc_party,
                  google=sc_google, signs=sc_signs, real=sc_real, outro=sc_outro)
