"""Visuals für Folge 1 (Pick-me-Boy). Jede Szene: draw(c, S)
S.t = Zeit in der Szene, S.at(i, f) = Startzeit von Zeile i (+ Anteil f ihrer Dauer).
"""
import math, random
from alexlib import *

PM = alex(**OUTFIT_PICKME)
FEET, AH = 1665, 470
LENA = person_spec(4, girl=True, top="#46B39A", hair="#6B3E26", skin="#EBB894", pants="#3F4A6B", shoes="#2A2A2A")


def alex_bottom(c, S, expr="happy", pose="idle", prop=None, x=W / 2, h=AH):
    person(c, x, FEET, h, PM, S.t, expr, pose, prop, name="Alex")


def boys(n, seed=10):
    return [person_spec(seed + i) for i in range(n)]


def girls(n, seed=40):
    return [person_spec(seed + i, girl=True, hair_style=random.Random(seed + i).choice(["long", "bun"])) for i in range(n)]


# ======================================================================= INTRO
ICON_PICKME = "🌹"
INTRO_BG_PICKME = "#EC7FAE"


def draw_intro(c, t, shuffle, ticks, flash_start, reveal_t, role_text):
    k = 0
    for i, tk in enumerate(ticks):
        if t >= tk:
            k = i
    revealed = t >= reveal_t
    if revealed:
        bg, top, txt, prop = INTRO_BG_PICKME, None, role_text, "🧋"
    else:
        txt, prop, top, bg = shuffle[k][0], shuffle[k][1], shuffle[k][2], shuffle[k][3]
    background(c, bg, t, rays=0.09, cy=1080, speed=0.25)
    c.save()
    safe_zone(c)

    # Kopfzeile
    text(c, "Heute ist Alex", W / 2, 112, 44, "#FFFFFF", FONT_BOLD)
    sc = 1.0
    if revealed:
        sc = pop(t, reveal_t, 0.4)
    def ttl():
        c.save(); c.translate(0, 6)
        text(c, txt, W / 2, 196, 76, "#000000", FONT_HEAD, alpha=0.25)
        c.restore()
        text(c, txt, W / 2, 196, 76, "#FFFFFF", FONT_HEAD)
    scaled(c, W / 2, 196, sc, ttl)

    # Auswahl-Leiste
    icons = [s[1] for s in shuffle] + [ICON_PICKME]
    cols = [s[3] for s in shuffle] + [INTRO_BG_PICKME]
    sel = len(shuffle) if revealed else k
    # kleine Rutsch-Animation nach jedem Tick
    last_tick = reveal_t if revealed else (ticks[k] if t >= ticks[0] else 0)
    slide = 1 - ease_out_cubic((t - last_tick) / 0.06)
    yb = 330
    rrect(c, -200, yb - 50, W + 400, 100, 0)
    src(c, "#000000", 0.55); c.fill()
    step = 96
    for j in range(-8, 9):
        idx = (sel + j) % len(icons)
        x = W / 2 + (j + slide) * step
        c.arc(x, yb, 36, 0, 2 * math.pi)
        fill(c, shade(cols[idx], 0.85))
        c.arc(x, yb, 36, 0, 2 * math.pi)
        c.set_line_width(3); src(c, "#FFFFFF", 0.35); c.stroke()
        emoji(c, icons[idx], x, yb, 38)
    c.arc(W / 2, yb, 44, 0, 2 * math.pi)
    c.set_line_width(7); src(c, "#F7C948"); c.stroke()

    # Alex groß
    if revealed:
        spec = PM
        expr = "smug"
        s = 0.9 + 0.1 * ease_out_back((t - reveal_t) / 0.35)
    else:
        spec = alex(top=top, top_style="hoodie", pants="#2F3B52")
        expr = "happy"
        s = 1.0
    def body():
        person(c, W / 2, 1520, 780, spec, t, expr, "idle", prop if revealed else None)
    scaled(c, W / 2, 1520, s, body)
    if not revealed:
        bobx = math.sin(t * 6) * 6
        emoji(c, prop, 870 + bobx, 1150, 110, rot=0.15)
    else:
        emoji(c, "🌹", 830, 1080 + math.sin(t * 3) * 10, 120, rot=0.25)
        sparkle_lines(c, t, reveal_t, W / 2, 1000, n=14, r0=260, r1=560, d=0.55)
        burst(c, t, reveal_t, ["🌹", "💌", "📖", "🥺", "✨", "🎸", "☕", "💐"], W / 2, 1000, n=18,
              seed=5, dist=620, life=1.6, size=86)

    c.restore()
    # Weißer Blitz vor dem Reveal
    if flash_start <= t < reveal_t + 0.3:
        if t < reveal_t:
            a = clamp((t - flash_start) / 0.04)
        else:
            a = 1 - ease_out_cubic((t - reveal_t) / 0.3)
        c.set_source_rgba(1, 1, 1, a)
        c.paint()
        if t < reveal_t:
            emoji(c, "🌹", W / 2, 960, 130, rot=(t - flash_start) * 9)


# ======================================================================= SZENEN
def sc_what(c, S):
    t = S.t
    a1 = S.at(1)
    # Karte mit Jungs-Auswahl
    s = pop(t, S.at(0, 0.0))
    card(c, W / 2, 700, 920, 600, s)
    def inner():
        text(c, "DIE AUSWAHL", W / 2, 470, 46, INK, FONT_HEAD)
        bs = boys(5, 21)
        for i, sp in enumerate(bs):
            x = 190 + i * 175
            ex = "neutral" if t < a1 else ("smug" if i % 2 else "neutral")
            person(c, x, 930, 330, sp, t, ex, "idle", blink_seed=i)
            if t >= a1:
                emoji(c, "🙄", x, 560, 56 * pop(t, a1 + 0.1 * i))
        # Zeiger-Hand wandert
        hx = 190 + (math.sin(t * 2.2) * 0.5 + 0.5) * 700
        emoji(c, "👆", hx, 820 + math.sin(t * 8) * 6, 80)
    scaled(c, W / 2, 700, s, inner)
    if t < a1:
        # Alex hält Schild hoch
        alex_bottom(c, S, "happy", "up")
        ss = pop(t, S.at(0, 0.35))
        def sign():
            c.set_line_width(10); src(c, "#8B5E34")
            c.move_to(W / 2, 1215); c.line_to(W / 2, 1110); c.stroke()
            rrect(c, W / 2 - 190, 1030, 380, 100, 16); fill(c, "#FFF3B0")
            rrect(c, W / 2 - 190, 1030, 380, 100, 16); c.set_line_width(5); src(c, INK); c.stroke()
            text(c, "PICK ME! 🙋", W / 2, 1080, 52, INK, FONT_HEAD)
        scaled(c, W / 2, 1080, ss, sign, rot=math.sin(t * 7) * 0.06)
    else:
        alex_bottom(c, S, "smug", "hips")
        bubble(c, "Ich bin nicht wie die anderen Jungs.", W / 2, 1075, pop(t, a1), tail=(0.25, 1), size=42)


def sc_morning(c, S):
    t = S.t
    s = pop(t, S.at(0, 0.15))
    x0, y0, w, h = phone(c, W / 2, 690, 470, 820, s, screen="#202020")
    def story():
        c.save()
        rrect(c, x0, y0, w, h, 42); c.clip()
        # Schwarz-Weiß-Sonnenaufgang
        g = cairo.LinearGradient(0, y0, 0, y0 + h)
        g.add_color_stop_rgb(0, 0.18, 0.18, 0.18)
        g.add_color_stop_rgb(0.62, 0.62, 0.62, 0.62)
        g.add_color_stop_rgb(1, 0.3, 0.3, 0.3)
        c.set_source(g); c.paint()
        sun_y = y0 + h * 0.62 - 60 * ease_out_cubic((t - S.at(0)) / 3)
        c.arc(W / 2, sun_y, 95, 0, 2 * math.pi); src(c, "#DDDDDD"); c.fill()
        c.rectangle(x0, y0 + h * 0.62, w, h); src(c, "#3A3A3A"); c.fill()
        for i in range(5):
            c.rectangle(x0 + 40 + i * 70, y0 + h * 0.66 + i * 18, 120 - i * 10, 5); src(c, "#777777"); c.fill()
        # Story-Balken
        for i in range(3):
            bw = (w - 60) / 3
            rrect(c, x0 + 20 + i * (bw + 10), y0 + 62, bw, 7, 3); src(c, "#FFFFFF", 0.4); c.fill()
        prog = clamp((t - S.at(0)) / (S.dur - S.at(0)))
        rrect(c, x0 + 20, y0 + 62, (w - 60) / 3 * prog, 7, 3); fill(c, "#FFFFFF")
        c.arc(x0 + 46, y0 + 108, 22, 0, 2 * math.pi); fill(c, ALEX_BASE["hair"])
        text(c, "alex.nicht.wie.die.anderen", x0 + 80, y0 + 108, 22, "#FFFFFF", FONT_BOLD, anchor="l")
        # Zitat
        qa = fade(t, S.at(1, 0.25), 0.3)
        if qa > 0:
            c.select_font_face("Inter Display", cairo.FONT_SLANT_ITALIC, cairo.FONT_WEIGHT_BOLD)
            c.set_font_size(40)
            lines = ["„Manche Seelen", "sind zu tief", "für diese Welt.“"]
            for i, ln in enumerate(lines):
                e = c.text_extents(ln)
                c.move_to(W / 2 - e.x_advance / 2, y0 + 200 + i * 52)
                c.set_source_rgba(1, 1, 1, qa); c.show_text(ln)
        # Gesehen von: Mama
        ma = pop(t, S.at(1, 0.8))
        def seen():
            rrect(c, W / 2 - 170, y0 + h - 100, 340, 60, 30); src(c, "#000000", 0.55); c.fill()
            text(c, "👁 Gesehen von: Mama", W / 2, y0 + h - 70, 26, "#FFFFFF", FONT_BOLD)
        scaled(c, W / 2, y0 + h - 70, ma, seen)
        c.restore()
    scaled(c, W / 2, 690, s, story)
    if t >= S.at(1, 0.1):
        tag = pop(t, S.at(1, 0.1))
        def lbl():
            rrect(c, 690, 330, 300, 64, 14); fill(c, "#FFFFFF")
            rrect(c, 690, 330, 300, 64, 14); c.set_line_width(4); src(c, INK); c.stroke()
            text(c, "Filter: traurig 🖤", 840, 362, 30, INK, FONT_HEAD)
        scaled(c, 840, 362, tag, lbl, rot=0.08)
    alex_bottom(c, S, "smug" if t > S.at(1) else "happy", "phone", "📱")


def sc_train(c, S):
    t = S.t
    a1 = S.at(1)
    # Bahnfenster
    s = pop(t, S.at(0, 0.0))
    def window():
        rrect(c, 70, 330, 940, 420, 30); fill(c, "#D9DEE5")
        rrect(c, 70, 330, 940, 420, 30); c.set_line_width(5); src(c, INK); c.stroke()
        for i in range(2):
            x = 110 + i * 440
            c.save()
            rrect(c, x, 370, 420, 260, 26); c.clip()
            src(c, "#BFE6FF"); c.paint()
            off = (t * 260) % 300
            for j in range(-1, 5):
                bx = x + j * 110 - off % 110
                bh = 60 + (j * 37 % 90)
                c.rectangle(bx, 630 - bh, 80, bh); src(c, "#7FA6C9"); c.fill()
            c.restore()
            rrect(c, x, 370, 420, 260, 26); c.set_line_width(5); src(c, INK); c.stroke()
        rrect(c, 70, 660, 940, 24, 6); fill(c, "#A9B2BF")
    scaled(c, W / 2, 540, s, window)
    # Mädchen am Handy (ignorieren ihn)
    for i, (x, sp) in enumerate(zip((150, 930), girls(2, 50))):
        gs = pop(t, S.at(0, 0.2 + 0.1 * i))
        scaled(c, x, 1180, gs, lambda x=x, sp=sp, i=i: person(c, x, 1180, 360, sp, t, "neutral", "phone", "📱", blink_seed=i))
    # Buch
    bs = pop(t, S.at(0, 0.35))
    def book():
        c.save(); c.translate(W / 2, 880); c.rotate(-0.07)
        rrect(c, -170 + 8, -230 + 12, 340, 460, 14); src(c, "#000000", 0.22); c.fill()
        rrect(c, -170, -230, 340, 460, 14); fill(c, "#2E5E4E")
        rrect(c, -170, -230, 340, 460, 14); c.set_line_width(5); src(c, INK); c.stroke()
        rrect(c, -170, -230, 26, 460, 8); fill(c, "#234A3D")
        text(c, "FRANZ KAFKA", 10, -150, 30, "#F3E7C9", FONT_BOLD)
        text(c, "DIE", 10, -60, 54, "#F3E7C9", FONT_HEAD)
        text(c, "VERWAND-", 10, 0, 54, "#F3E7C9", FONT_HEAD)
        text(c, "LUNG", 10, 60, 54, "#F3E7C9", FONT_HEAD)
        emoji(c, "🪲", 10, 150, 70)
        c.restore()
    scaled(c, W / 2, 880, bs, book)
    if t < a1:
        ar = pop(t, S.at(0, 0.6))
        for x, rot in ((300, 0.5), (780, -0.5)):
            emoji(c, "👀", x, 760, 70 * ar)
    else:
        st = pop(t, a1 + 0.15, 0.25)
        def prog():
            rrect(c, 250, 1060, 580, 80, 16); fill(c, "#FFFFFF")
            rrect(c, 250, 1060, 580, 80, 16); c.set_line_width(4); src(c, INK); c.stroke()
            text(c, "GELESEN:", 370, 1100, 32, INK, FONT_HEAD)
            rrect(c, 470, 1086, 260, 28, 14); fill(c, "#E2E2E2")
            rrect(c, 470, 1086, 260 * 0.03 + 14, 28, 14); fill(c, "#E23B3B")
            text(c, "2 %", 780, 1100, 32, "#E23B3B", FONT_HEAD)
        scaled(c, W / 2, 1100, st, prog)
        red_flag_stamp(c, W / 2, 880, pop(t, S.at(1, 0.35), 0.25), "NUR KLAPPENTEXT", rot=-0.2)
    alex_bottom(c, S, "smug", "idle", "📖", x=W / 2)


def sc_lunch(c, S):
    t = S.t
    a1 = S.at(1)
    if t < a1 + 0.25:
        out = 1 - ease_out_cubic((t - a1) / 0.25) if t > a1 else 1
        s = pop(t, S.at(0, 0.0)) * out
        def table():
            gs = girls(3, 61)
            for i, (x, sp) in enumerate(zip((290, 540, 790), gs)):
                ex = "happy" if t < S.at(0, 0.55) else ("cringe" if i == 1 else "neutral")
                person(c, x, 990, 420, sp, t, ex, "idle", blink_seed=i + 2)
            rrect(c, 90, 860, 900, 60, 16); fill(c, "#B07A4F")
            rrect(c, 90, 860, 900, 60, 16); c.set_line_width(5); src(c, INK); c.stroke()
            rrect(c, 150, 920, 30, 170, 6); fill(c, "#8A5E3B")
            rrect(c, 900, 920, 30, 170, 6); fill(c, "#8A5E3B")
            for x in (290, 540, 790):
                emoji(c, "🍝", x, 840, 70)
            if t > S.at(0, 0.55):
                emoji(c, "😬", 540, 470, 60 * pop(t, S.at(0, 0.55)))
        scaled(c, W / 2, 800, s, table)
        bubble(c, "Ich hab nur Freundinnen. Jungs sind mir zu oberflächlich.", W / 2, 1060,
               pop(t, S.at(0, 0.3)) * out, tail=(0.15, 1), size=38, max_w=700)
        alex_bottom(c, S, "smug", "hips")
    if t >= a1:
        # Wippe: andere Jungs runter, Alex hoch
        s = pop(t, a1 + 0.1)
        tilt = -0.22 * ease_in_out((t - a1 - 0.5) / 0.7)
        def seesaw():
            c.move_to(W / 2 - 60, 1010); c.line_to(W / 2 + 60, 1010); c.line_to(W / 2, 880); c.close_path()
            fill(c, "#5A4A3A")
            c.save(); c.translate(W / 2, 880); c.rotate(tilt)
            rrect(c, -440, -18, 880, 36, 14); fill(c, "#F2D16B")
            rrect(c, -440, -18, 880, 36, 14); c.set_line_width(5); src(c, INK); c.stroke()
            for i, sp in enumerate(boys(3, 70)):
                person(c, -380 + i * 95, -18, 240, sp, t, "sad" if t > a1 + 0.9 else "neutral", blink_seed=i, bob=False)
            person(c, 330, -18, 260, PM, t, "smug", "hips", bob=False)
            c.restore()
            # Labels
            text(c, "ANDERE JUNGS", 250, 640, 38, INK, FONT_HEAD)
            text(c, "ALEX", 840, 560, 38, INK, FONT_HEAD)
        scaled(c, W / 2, 900, s, seesaw)
        if t > a1 + 0.9:
            emoji(c, "⬇️", 120, 1010, 80 * pop(t, a1 + 0.9))
            emoji(c, "⬆️", 960, 640, 80 * pop(t, a1 + 1.0))
        if t >= a1 + 0.25:
            alex_bottom(c, S, "smug", "shrug")


def sc_insta(c, S):
    t = S.t
    a1 = S.at(1)
    if t < a1 + 0.2:
        out = 1 - ease_out_cubic((t - a1) / 0.2) if t > a1 else 1
        s = pop(t, S.at(0, 0.0)) * out
        def profile():
            card(c, W / 2, 680, 920, 640, 1)
            # Avatar: Alex' Kopf im Kreis
            c.save()
            c.arc(230, 520, 95, 0, 2 * math.pi); c.clip()
            src(c, "#F7D6E6"); c.paint()
            person(c, 230, 780, 520, PM, t, "smug", bob=False)
            c.restore()
            c.arc(230, 520, 95, 0, 2 * math.pi); c.set_line_width(7); src(c, "#E26AA0"); c.stroke()
            for i, (n, l) in enumerate((("312", "Beiträge"), ("847", "Follower"), ("2.140", "Gefolgt"))):
                x = 450 + i * 180
                text(c, n, x, 495, 40, INK, FONT_HEAD)
                text(c, l, x, 545, 26, "#555555", FONT_BOLD)
            text(c, "@alex.nicht.wie.die.anderen", 125, 660, 34, INK, FONT_HEAD, anchor="l")
            text(c, "🌙 tiefgründig · 📖 Bücher > Menschen", 125, 720, 30, "#333333", FONT_BOLD, anchor="l")
            hl = ease_out_cubic((t - S.at(0, 0.45)) / 0.4)
            if hl > 0:
                rrect(c, 115, 760, 560 * hl, 56, 8); src(c, "#FFE14D"); c.fill()
            text(c, "🌹 Ich respektiere Frauen.", 125, 790, 34, INK, FONT_HEAD, anchor="l")
            text(c, "🎸 Musik ist meine Therapie", 125, 850, 30, "#333333", FONT_BOLD, anchor="l")
            rrect(c, 125, 900, 830, 70, 14); fill(c, "#EFEFEF")
            text(c, "Nachricht senden", W / 2, 935, 30, INK, FONT_BOLD)
        scaled(c, W / 2, 680, s, profile)
    if t >= a1:
        s = pop(t, a1 + 0.05)
        def post():
            card(c, W / 2, 730, 940, 780, 1)
            c.save()
            rrect(c, 70 + 5, 340 + 5, 930, 340, 22); c.clip()
            src(c, "#FBD3B0"); c.paint()
            person(c, W / 2, 1000, 760, person_spec(81, girl=True, top="#F07FB0", hair="#2E1F17"), t, "happy", bob=False)
            emoji(c, "✨", 220, 420, 60); emoji(c, "☀️", 880, 420, 60)
            c.restore()
            text(c, "♡  💬  ➤", 160, 720, 40, INK, FONT_BOLD, anchor="l")
            text(c, "Kommentare", 100, 780, 28, "#777777", FONT_BOLD, anchor="l")
        scaled(c, W / 2, 730, s, post)
        comments = ["Du bist anders als die anderen 🌹", "Ich würde dich NIE so behandeln wie er 🥺", "Ohne Filter noch schöner ✨"]
        for i, cm in enumerate(comments):
            ts = S.at(1, 0.12 + 0.24 * i)
            cs = pop(t, ts)
            y = 840 + i * 78
            def row(cm=cm, y=y):
                c.arc(120, y, 24, 0, 2 * math.pi); fill(c, ALEX_BASE["hair"])
                text(c, "alex.nwda", 160, y - 14, 24, INK, FONT_HEAD, anchor="l")
                text(c, cm, 160, y + 16, 28, "#222222", FONT_BOLD, anchor="l")
            scaled(c, 120, y, cs, row)
            emoji(c, "🚩", 960, y, 52 * pop(t, ts + 0.15))
    alex_bottom(c, S, "puppy" if t > a1 else "smug", "phone", "📱")


def sc_date(c, S):
    t = S.t
    a1, a2, a3 = S.at(1), S.at(2), S.at(3)
    lena_x, alex_x = 790, 320
    if t < a2 + 0.2:
        out = 1 - ease_out_cubic((t - a2) / 0.2) if t > a2 else 1
        s = pop(t, S.at(0, 0.0)) * out
        def cafe():
            rrect(c, 140, 380, 800, 600, 20); fill(c, "#FFF4E6")
            rrect(c, 140, 380, 800, 600, 20); c.set_line_width(5); src(c, INK); c.stroke()
            for i in range(8):
                c.rectangle(140 + i * 100, 360, 100, 90); src(c, "#E23B3B" if i % 2 == 0 else "#FFFFFF"); c.fill()
            c.rectangle(140, 360, 800, 90); c.set_line_width(5); src(c, INK); c.stroke()
            rrect(c, 380, 470, 320, 70, 12); fill(c, INK)
            text(c, "CAFÉ AMORE", 540, 505, 36, "#FFFFFF", FONT_HEAD)
            rrect(c, 200, 580, 680, 330, 14); fill(c, "#BFE3F2")
            rrect(c, 200, 580, 680, 330, 14); c.set_line_width(5); src(c, INK); c.stroke()
            rrect(c, 330, 800, 420, 30, 8); fill(c, "#8A5E3B")
            emoji(c, "☕", 450, 770, 60); emoji(c, "🍰", 630, 770, 60); emoji(c, "🕯️", 540, 760, 54)
            emoji(c, "❤️", 300 + math.sin(t * 3) * 10, 650, 44); emoji(c, "💕", 790, 640 + math.sin(t * 4) * 8, 44)
        scaled(c, W / 2, 680, s, cafe)
    if a2 <= t < a3 + 0.2:
        out = 1 - ease_out_cubic((t - a3) / 0.2) if t > a3 else 1
        s = pop(t, a2 + 0.05) * out
        def others():
            card(c, W / 2, 720, 920, 560, 1)
            text(c, "ALLE ANDEREN MÄDCHEN", W / 2, 500, 44, INK, FONT_HEAD)
            for i, sp in enumerate(girls(5, 90)):
                x = 190 + i * 175
                person(c, x, 940, 330, sp, t, "cringe" if t > a2 + 0.6 else "neutral", blink_seed=i)
            if t > a2 + 0.5:
                emoji(c, "❌", W / 2, 760, 330 * pop(t, a2 + 0.5), alpha=0.85)
        scaled(c, W / 2, 720, s, others)
    if t >= a3:
        s = pop(t, a3 + 0.1)
        def song():
            card(c, W / 2, 680, 900, 440, 1, color="#1F1F28")
            text(c, "🎵 NEUER SONG", W / 2, 540, 40, "#F7C948", FONT_HEAD)
            text(c, "»LENA (DU BIST ANDERS)«", W / 2, 630, 50, "#FFFFFF", FONT_HEAD)
            text(c, "Geschrieben: nach 1 Date", W / 2, 720, 32, "#BBBBBB", FONT_BOLD)
            rrect(c, 200, 780, 680, 14, 7); src(c, "#FFFFFF", 0.25); c.fill()
            pr = clamp((t - a3) / 4)
            rrect(c, 200, 780, 680 * pr, 14, 7); fill(c, "#F7C948")
        scaled(c, W / 2, 680, s, song)
        for i in range(4):
            u = ((t - a3) * 0.6 + i * 0.25) % 1
            emoji(c, "🎶" if i % 2 else "🎵", alex_x - 120 + i * 60, 1150 - u * 200, 54, alpha=1 - u)
    # Figuren unten
    pose, prop, ex = "idle", None, "happy"
    if t >= a1:
        ex = "puppy"
    if t >= a3:
        pose, prop, ex = "guitar", "🎸", "happy"
    person(c, alex_x, FEET, AH, PM, t, ex, pose, prop, name="Alex")
    ls = pop(t, S.at(0, 0.3))
    lena_ex = "happy" if t < a1 + 0.8 else ("cringe" if t < a3 else "shock")
    scaled(c, lena_x, FEET, ls, lambda: person(c, lena_x, FEET, AH * 0.97, LENA, t, lena_ex, "idle", name="Lena", blink_seed=3))
    if a1 <= t < a2 + 0.2:
        out = 1 - ease_out_cubic((t - a2) / 0.2) if t > a2 else 1
        bubble(c, "Du bist nicht wie die anderen Mädchen 🥺", 430, 1060, pop(t, a1 + 0.05) * out,
               tail=(-0.4, 1), size=38, max_w=560)
    if t > a3 + 0.8:
        emoji(c, "😬", lena_x + 110, 1180, 70 * pop(t, a3 + 0.8))


def chat_screen(c, x0, y0, w, h, title_name, emoji_icon):
    rrect(c, x0, y0, w, 130, 0); fill(c, "#F4F4F6")
    c.arc(x0 + 70, y0 + 82, 30, 0, 2 * math.pi); fill(c, "#6B3E26")
    text(c, title_name, x0 + 115, y0 + 82, 32, INK, FONT_HEAD, anchor="l")
    emoji(c, emoji_icon, x0 + w - 60, y0 + 82, 36)


def chat_msg(c, msg, x0, w, y, mine, s, size=28):
    if s <= 0:
        return
    tw = min(text_width(c, msg, size, FONT_BOLD), w - 120)
    lines = wrap(c, msg, size, w - 140, FONT_BOLD)
    bw = max(text_width(c, ln, size, FONT_BOLD) for ln in lines) + 44
    bh = len(lines) * size * 1.25 + 26
    bx = x0 + w - 24 - bw if mine else x0 + 24
    def d():
        rrect(c, bx, y - bh, bw, bh, 22)
        fill(c, "#3D8BFF" if mine else "#E6E6EA")
        for i, ln in enumerate(lines):
            text(c, ln, bx + 22, y - bh + 13 + size * 0.62 + i * size * 1.25, size, "#FFFFFF" if mine else INK, FONT_BOLD, anchor="l")
    scaled(c, bx + (bw if mine else 0), y, s, d)
    return bh


def sc_texts(c, S):
    t = S.t
    a1 = S.at(1)
    s = pop(t, S.at(0, 0.0))
    x0, y0, w, h = phone(c, W / 2, 730, 540, 900, s, screen="#FFFFFF")
    msgs = ["Hey 🙂", "Bist du gut heimgekommen?", "Heute war magisch ✨", "Hallo?", "Du bist echt anders 🌹",
            "Hab dir einen Song geschrieben 🎸", "???", "Ich glaub, ich hab mich verliebt 🥺❤️"]
    def screen():
        c.save()
        rrect(c, x0, y0, w, h, 42); c.clip()
        chat_screen(c, x0, y0, w, h, "Lena", "📞")
        n = 0
        t0 = S.at(0, 0.1)
        span = S.at(0, 0.95) - t0
        times = [t0 + span * (i / len(msgs)) ** 0.8 for i in range(len(msgs))]
        shown = [i for i, tm in enumerate(times) if t >= tm]
        y = y0 + h - 40
        for i in reversed(shown):
            bh = chat_msg(c, msgs[i], x0, w, y, True, pop(t, times[i], 0.2))
            y -= (bh or 0) + 14
        c.restore()
        cnt = min(30, int(30 * clamp((t - t0) / span))) if t > t0 else 0
        if cnt:
            c.arc(x0 + w - 6, y0 + 6, 42, 0, 2 * math.pi); fill(c, "#E23B3B")
            text(c, str(cnt), x0 + w - 6, y0 + 6, 38, "#FFFFFF", FONT_HEAD)
    scaled(c, W / 2, 730, s, screen)
    if t >= a1:
        red_flag_stamp(c, W / 2, 640, pop(t, a1 + 0.05, 0.25), "LOVEBOMBING", rot=-0.16)
    alex_bottom(c, S, "puppy", "phone", "📱", x=860, h=AH * 0.95)


def sc_reject(c, S):
    t = S.t
    a1, a2 = S.at(1), S.at(2)
    shake = 0
    if a1 + 0.9 < t < a1 + 1.3:
        shake = math.sin(t * 70) * 10
    if t < a2 + 0.2:
        out = 1 - ease_out_cubic((t - a2) / 0.2) if t > a2 else 1
        s = pop(t, S.at(0, 0.0)) * out
        cx = W / 2 + shake
        x0, y0, w, h = phone(c, cx, 730, 540, 900, s, screen="#FFFFFF")
        def screen():
            c.save()
            rrect(c, x0, y0, w, h, 42); c.clip()
            chat_screen(c, x0, y0, w, h, "Lena", "📞")
            y = y0 + 330
            chat_msg(c, "Ich glaub, ich hab mich verliebt 🥺❤️", x0, w, y, True, 1)
            chat_msg(c, "Ich sehe dich eher als Kumpel 🙂", x0, w, y + 150, False, pop(t, S.at(0, 0.2), 0.25))
            if t > a1 + 0.9:
                chat_msg(c, "Typisch. Frauen wollen eh nur Bad Boys 😤", x0, w, y + 330, True, pop(t, a1 + 0.9, 0.25))
            c.restore()
        scaled(c, cx, 730, s, screen)
        if a1 <= t:
            emoji(c, "💔", 150, 520, 110 * pop(t, a1 + 0.1) * out, rot=-0.2)
    if t >= a2:
        s = pop(t, a2 + 0.1)
        def bill():
            card(c, W / 2, 720, 760, 720, 1, color="#FFFDF5")
            text(c, "ALEX' RECHNUNG", W / 2, 440, 46, INK, FONT_HEAD)
            rows = [("Kaffee bezahlt", "✅"), ("Song geschrieben", "✅"), ("30 Nachrichten", "✅"), ("Nett gewesen", "✅")]
            for i, (l, v) in enumerate(rows):
                y = 530 + i * 70
                if t > a2 + 0.25 + i * 0.18:
                    text(c, l, 220, y, 36, "#333333", FONT_BOLD, anchor="l")
                    text(c, v, 860, y, 40, "#2FA36B", FONT_HEAD, anchor="r")
            c.set_line_width(4); src(c, INK); c.set_dash([14, 10]); c.move_to(210, 840); c.line_to(870, 840); c.stroke(); c.set_dash([])
            if t > a2 + 1.1:
                text(c, "ERWARTET:", 220, 900, 40, INK, FONT_HEAD, anchor="l")
                text(c, "BEZIEHUNG", 860, 900, 40, "#E23B3B", FONT_HEAD, anchor="r")
        scaled(c, W / 2, 720, s, bill)
        red_flag_stamp(c, W / 2, 720, pop(t, a2 + 1.8, 0.25), "NETT ≠ ANSPRUCH", rot=-0.2)
    ex = "sad" if t < a1 + 0.8 else "angry"
    if t >= a2 + 1.8:
        ex = "shock"
    alex_bottom(c, S, ex, "idle" if t < a1 + 0.8 else "cross", x=W / 2 + shake * 0.5)
    if a1 + 0.8 < t < a2 + 1.8:
        emoji(c, "💢", W / 2 + 150, 1230, 80 * pop(t, a1 + 0.8))


def sc_flags(c, S):
    t = S.t
    items = ["Macht andere Jungs schlecht", "Macht andere Mädchen schlecht", "Nett nur mit Hintergedanken",
             "Braucht für alles Publikum"]
    icons = ["👬", "👭", "🎁", "📢"]
    for i, it in enumerate(items):
        ts = S.at(i + 1, 0.0)
        s = pop(t, ts)
        y = 420 + i * 175
        def row(it=it, y=y, i=i):
            rrect(c, 90 + 6, y - 70 + 10, 900, 140, 24); src(c, "#000000", 0.2); c.fill()
            rrect(c, 90, y - 70, 900, 140, 24); fill(c, "#FFFFFF")
            rrect(c, 90, y - 70, 900, 140, 24); c.set_line_width(5); src(c, INK); c.stroke()
            c.arc(170, y, 46, 0, 2 * math.pi); fill(c, "#E23B3B")
            text(c, str(i + 1), 170, y, 50, "#FFFFFF", FONT_HEAD)
            text(c, it, 240, y, 40, INK, FONT_HEAD, anchor="l")
            emoji(c, icons[i], 935, y, 54)
        scaled(c, W / 2, y, s, row, rot=(-0.02 if i % 2 else 0.02))
    for i in range(3):
        emoji(c, "🚩", 140 + i * 400, 1110 + math.sin(t * 3 + i) * 12, 70 * pop(t, S.at(0, 0.2 + 0.15 * i)))
    alex_bottom(c, S, "smug", "shrug")


def sc_outro(c, S):
    t = S.t
    a1 = S.at(1)
    q = "Kennst du noch einen Pick Me Boy?" if t < a1 else "Was soll Alex morgen sein?"
    qs = pop(t, S.at(0, 0.0)) if t < a1 else pop(t, a1)
    card(c, W / 2, 230, 920, 150, qs)
    scaled(c, W / 2, 230, qs, lambda: text_block(c, q, W / 2, 230, 50, 860, INK, FONT_HEAD))
    if t < a1 + 0.2:
        out = 1 - ease_out_cubic((t - a1) / 0.2) if t > a1 else 1
        s = pop(t, S.at(0, 0.3)) * out
        def tag():
            c.arc(W / 2, 640, 210, 0, 2 * math.pi); fill(c, "#FFFFFF")
            c.arc(W / 2, 640, 210, 0, 2 * math.pi); c.set_line_width(8); src(c, INK); c.stroke()
            text(c, "@", W / 2, 625, 300, "#E26AA0", FONT_HEAD)
            rrect(c, 160, 900, 760, 100, 50); fill(c, "#FFFFFF")
            rrect(c, 160, 900, 760, 100, 50); c.set_line_width(5); src(c, INK); c.stroke()
            typed = "@der_pick_me_boy"
            n = int(clamp((t - S.at(0, 0.55)) / 1.0) * len(typed))
            cur = "|" if int(t * 3) % 2 == 0 else ""
            text(c, typed[:n] + cur, 210, 950, 44, "#3D8BFF", FONT_HEAD, anchor="l")
        scaled(c, W / 2, 700, s, tag, rot=math.sin(t * 4) * 0.02)
        emoji(c, "👇", 880, 1110 + math.sin(t * 8) * 12, 90 * pop(t, S.at(0, 0.6)) * out)
    if t >= a1:
        s = pop(t, a1 + 0.1)
        colors = ["#E5534B", "#3E7BDA", "#2FA36B", "#F2B233", "#EC7FAE", "#8E5BE0", "#36B5C2", "#F07F4F", "#555A66"]
        for i in range(9):
            r, cc = i // 3, i % 3
            x, y = 260 + cc * 280, 500 + r * 230
            def icon(x=x, y=y, i=i):
                c.arc(x, y, 95, 0, 2 * math.pi); fill(c, colors[i])
                c.arc(x, y, 95, 0, 2 * math.pi); c.set_line_width(6); src(c, "#FFFFFF"); c.stroke()
                if i == 0:
                    emoji(c, "🌹", x, y, 100)
                    rrect(c, x - 80, y + 70, 160, 46, 12); fill(c, "#2FA36B")
                    text(c, "HEUTE ✅", x, y + 93, 28, "#FFFFFF", FONT_HEAD)
                else:
                    text(c, "?", x, y, 110, "#FFFFFF", FONT_HEAD)
            scaled(c, x, y, pop(t, a1 + 0.1 + i * 0.07), icon)
        ps = pop(t, S.at(1, 0.45))
        def pill():
            rrect(c, 170, 1040, 740, 96, 48); fill(c, "#E23B3B")
            text(c, "Schreib's in die Kommentare ⬇️", W / 2, 1088, 42, "#FFFFFF", FONT_HEAD)
        scaled(c, W / 2, 1088, ps * (1 + 0.04 * math.sin(t * 7)), pill)
    alex_bottom(c, S, "happy", "wave")


SCENE_DRAW = dict(what=sc_what, morning=sc_morning, train=sc_train, lunch=sc_lunch, insta=sc_insta,
                  date=sc_date, texts=sc_texts, reject=sc_reject, flags=sc_flags, outro=sc_outro)
