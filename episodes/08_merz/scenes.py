"""Visuals: Alex als Friedrich Merz (TikTok Folge 3). Parodie, jugendgerecht, unpolitisch.
Dauerhaftes "PARODIE"-Label. Keine Logos, keine echten Fotos.
"""
import math, random
from alexlib import *

# Kanzler-Alex: Alex' Gesicht + silbergraue Perücke, dezente Brille, dunkelblauer Anzug
AL = alex(hair="#C9CDD3", hair_dark="#9AA0A8", glasses=True, frame="#A9A9B2",
          top="#1F2A44", top_style="suit", tie="#7FB3E8", pants="#1F2A44", shoes="#2A2A2A")
FEET, AH = 1665, 470
TALL = AH * 1.12

INTRO = dict(icon="🎙️", bg="#1F3A6B", spec=AL, expr="smug", pose="hips", hand_prop=None,
             side_emoji="🛩️", burst=["🎙️", "🛩️", "⛰️", "💼", "📏", "🥐", "📜", "👔"])


def parodie_label(c):
    c.save()
    c.translate(W - 150, 1830)
    rrect(c, -110, -26, 220, 52, 14); src(c, "#000000", 0.55); c.fill()
    text(c, "PARODIE", 0, 0, 30, "#FFFFFF", FONT_HEAD)
    c.restore()


def draw_intro(c, t, shuffle, ticks, flash_start, reveal_t, role_text):
    draw_intro_generic(c, t, shuffle, ticks, flash_start, reveal_t, role_text, INTRO)
    if t >= reveal_t:
        parodie_label(c)


def alex_bottom(c, S, expr="smug", pose="idle", prop=None, x=W / 2, h=AH):
    person(c, x, FEET, h, AL, S.t, expr, pose, prop, name="Kanzler-Alex")
    parodie_label(c)


def out_fade(t, t_end, d=0.2):
    return 1 - ease_out_cubic((t - t_end) / d) if t > t_end else 1


def row_card(c, x, y, w, h, s, label, icon=None, size=40, num=None, rot=0.0):
    def d():
        rrect(c, x - w / 2 + 6, y - h / 2 + 10, w, h, 22); src(c, "#000000", 0.2); c.fill()
        rrect(c, x - w / 2, y - h / 2, w, h, 22); fill(c, "#FFFFFF")
        rrect(c, x - w / 2, y - h / 2, w, h, 22); c.set_line_width(5); src(c, INK); c.stroke()
        lx = x - w / 2 + 40
        if num is not None:
            c.arc(x - w / 2 + 75, y, 42, 0, 2 * math.pi); fill(c, "#1F3A6B")
            text(c, str(num), x - w / 2 + 75, y, 46, "#FFFFFF", FONT_HEAD)
            lx = x - w / 2 + 140
        text(c, label, lx, y, size, INK, FONT_HEAD, anchor="l")
        if icon:
            emoji(c, icon, x + w / 2 - 60, y, 56)
    scaled(c, x, y, s, d, rot)


def hills(c, t):
    for i, (col, y0, amp) in enumerate((("#4E9A5E", 820, 60), ("#3F8550", 900, 80), ("#2F6E40", 990, 70))):
        c.move_to(70, 1040)
        for x in range(70, 1011, 20):
            c.line_to(x, y0 - amp * math.sin(x * 0.006 + i * 1.7) - 20 * math.sin(x * 0.02 + i))
        c.line_to(1010, 1040); c.close_path(); fill(c, col)


# ======================================================================= SZENEN
def sc_what(c, S):
    t, a1 = S.t, S.at(1)
    s = pop(t, S.at(0, 0.0))
    def card_():
        card(c, W / 2, 660, 900, 520, 1)
        text(c, "STECKBRIEF", W / 2, 460, 50, INK, FONT_HEAD)
        rows = [("Job", "Bundeskanzler 🇩🇪" if False else "Bundeskanzler", 0.15)]
        text(c, "Job:", 160, 560, 40, "#555555", FONT_BOLD, anchor="l")
        text(c, "Bundeskanzler", 400, 560, 42, INK, FONT_HEAD, anchor="l")
        if t >= a1:
            for i, (lab, val, f) in enumerate((("Brille", "✅", 0.25), ("Anzug", "✅", 0.4), ("Größe", "ganz, ganz groß 📏", 0.6))):
                if t > S.at(1, f):
                    text(c, lab + ":", 160, 650 + i * 85, 40, "#555555", FONT_BOLD, anchor="l")
                    text(c, val, 400, 650 + i * 85, 42, INK, FONT_HEAD, anchor="l")
    scaled(c, W / 2, 660, s, card_)
    # Größenvergleich: ein normal großer Mensch neben Kanzler-Alex
    if t > S.at(1, 0.6):
        person(c, 230, FEET, AH * 0.8, person_spec(17), t, "shock", bob=False)
        emoji(c, "📏", 900, 1250, 90 * pop(t, S.at(1, 0.6)), rot=1.2)
    alex_bottom(c, S, "smug", "hips", h=TALL)


def sc_sauerland(c, S):
    t, a1 = S.t, S.at(1)
    s = pop(t, S.at(0, 0.0))
    def land():
        rrect(c, 70, 380, 940, 660, 30)
        g = cairo.LinearGradient(0, 380, 0, 1040)
        g.add_color_stop_rgb(0, *rgb("#FFD9A0")[:3]); g.add_color_stop_rgb(1, *rgb("#BFE6FF")[:3])
        c.set_source(g); c.fill()
        c.save(); rrect(c, 70, 380, 940, 660, 30); c.clip()
        c.arc(800, 560, 70, 0, 2 * math.pi); fill(c, "#FFD34D")
        hills(c, t)
        emoji(c, "🌲", 200, 900, 90); emoji(c, "🌲", 300, 960, 80); emoji(c, "🐄", 780, 940, 90)
        c.restore()
        rrect(c, 70, 380, 940, 660, 30); c.set_line_width(6); src(c, INK); c.stroke()
        # Ortsschild
        c.save(); c.translate(W / 2, 520); c.rotate(-0.03)
        rrect(c, -230, -70, 460, 140, 12); fill(c, "#F7D21B")
        rrect(c, -218, -58, 436, 116, 8); c.set_line_width(5); src(c, INK); c.stroke()
        text(c, "BRILON", 0, -12, 64, INK, FONT_HEAD)
        text(c, "Sauerland", 0, 38, 30, INK, FONT_BOLD)
        c.restore()
    scaled(c, W / 2, 710, s, land)
    if t >= a1:
        def arrow():
            c.save(); c.translate(W / 2, 1110); c.rotate(-0.04)
            rrect(c, -360, -50, 720, 100, 50); fill(c, "#FFFFFF")
            rrect(c, -360, -50, 720, 100, 50); c.set_line_width(5); src(c, INK); c.stroke()
            text(c, "Jedes Thema ➡️ Sauerland ⛰️", 0, 0, 40, INK, FONT_HEAD)
            c.restore()
        scaled(c, W / 2, 1110, pop(t, a1 + 0.2), arrow)
    alex_bottom(c, S, "happy", "idle")


def sc_jet(c, S):
    t, a1 = S.t, S.at(1)
    s = pop(t, S.at(0, 0.0))
    def sky():
        rrect(c, 70, 380, 940, 620, 30); fill(c, "#BFE6FF")
        c.save(); rrect(c, 70, 380, 940, 620, 30); c.clip()
        for i in range(4):
            x = (i * 300 - t * 80) % 1240 - 100
            emoji(c, "☁️", x, 470 + (i % 2) * 360, 130, alpha=0.9)
        # Bus unten, Flugzeug oben
        bx = 160 + (t * 40) % 80
        emoji(c, "🚌", bx, 900, 120)
        text(c, "die anderen", bx, 980, 26, INK, FONT_BOLD)
        u = clamp((t - S.at(0, 0.3)) / max(0.6, S.dur * 0.8))
        emoji(c, "🛩️", 160 + 760 * u, 640 - 140 * math.sin(u * math.pi), 170, rot=-0.15)
        if t > a1:
            c.rectangle(720, 820, 260, 160); fill(c, "#FFF1DC")
            c.rectangle(720, 820, 260, 160); c.set_line_width(4); src(c, INK); c.stroke()
            for i in range(5):
                c.rectangle(720 + i * 52, 800, 52, 30); src(c, "#E23B3B" if i % 2 == 0 else "#FFFFFF"); c.fill()
            text(c, "BÄCKER 🥐", 850, 900, 34, INK, FONT_HEAD)
        c.restore()
        rrect(c, 70, 380, 940, 620, 30); c.set_line_width(6); src(c, INK); c.stroke()
    scaled(c, W / 2, 690, s, sky)
    if t > S.at(0, 0.6):
        def lic():
            c.save(); c.translate(260, 1130); c.rotate(-0.08)
            rrect(c, -190, -55, 380, 110, 16); fill(c, "#FFFFFF")
            rrect(c, -190, -55, 380, 110, 16); c.set_line_width(4); src(c, INK); c.stroke()
            text(c, "✈️ Hobbypilot", 0, 0, 38, INK, FONT_HEAD)
            c.restore()
        scaled(c, 260, 1130, pop(t, S.at(0, 0.6)), lic)
    alex_bottom(c, S, "smug", "point" if t > a1 else "idle", x=W / 2 + 120)


def sc_mittel(c, S):
    t, a1 = S.t, S.at(1)
    s = pop(t, S.at(0, 0.0))
    steps = [("OBERSCHICHT", "#F7C948"), ("GEHOBENE MITTELSCHICHT", "#9BCB3C"), ("MITTELSCHICHT", "#6CC08B"), ("UNTERSCHICHT", "#8FA3B8")]
    def ladder():
        for i, (lab, col) in enumerate(steps):
            y = 420 + i * 150
            rrect(c, 140, y, 800, 120, 18); fill(c, col)
            rrect(c, 140, y, 800, 120, 18); c.set_line_width(5); src(c, INK); c.stroke()
            text(c, lab, 540, y + 60, 40, INK, FONT_HEAD)
        # Pfeil: "Ich" zeigt auf gehobene Mittelschicht
        if t > S.at(0, 0.4):
            emoji(c, "👈", 1000, 630, 80)
            text(c, "„ich“", 990, 700, 32, "#FFFFFF", FONT_HEAD)
    scaled(c, W / 2, 700, s, ladder)
    if t >= a1:
        def money():
            c.save(); c.translate(W / 2, 1090); c.rotate(-0.04)
            rrect(c, -380, -60, 760, 120, 60); fill(c, "#1F1F28")
            text(c, "≈ 1 Mio. € im Jahr 💰", 0, 0, 52, "#F7C948", FONT_HEAD)
            c.restore()
        scaled(c, W / 2, 1090, pop(t, S.at(1, 0.4)), money)
        if t > S.at(1, 0.6):
            emoji(c, "🤔", 180, 470, 90 * pop(t, S.at(1, 0.6)))
    alex_bottom(c, S, "smug", "shrug")


def sc_speech(c, S):
    t, a1 = S.t, S.at(1)
    s = pop(t, S.at(0, 0.0))
    asleep = t > a1 + 0.3
    def hall():
        for r in range(2):
            for i in range(5):
                x = 170 + i * 185
                y = 1010 - r * 160
                person(c, x, y, 230 - r * 20, person_spec(100 + r * 5 + i, girl=bool((i + r) % 2)), t,
                       "sleepy" if asleep else "neutral", bob=False, blink_seed=i)
        if asleep:
            for i in range(5):
                u = (t * 0.5 + i / 5) % 1
                emoji(c, "💤", 220 + i * 185 + u * 40, 650 - u * 120, 50, alpha=1 - u)
    scaled(c, W / 2, 800, s, hall)
    # Rede-Uhr
    mins = int(10 * clamp((t - S.at(0, 0.3)) / max(0.5, a1 - S.at(0, 0.3)))) if t > S.at(0, 0.3) else 0
    if t > a1:
        mins = 10 + int((t - a1) * 8)
    def clockb():
        rrect(c, W / 2 - 170, 1080, 340, 90, 45); fill(c, "#1F1F28")
        text(c, f"⏱ {mins} Min.", W / 2, 1125, 44, "#FFFFFF", FONT_HEAD)
    scaled(c, W / 2, 1125, pop(t, S.at(0, 0.3)), clockb)
    # Rednerpult vor Kanzler-Alex
    alex_bottom(c, S, "happy" if asleep else "smug", "idle")
    rrect(c, W / 2 - 170, FEET - 230, 340, 230, 14); fill(c, "#6B4A2E")
    rrect(c, W / 2 - 170, FEET - 230, 340, 230, 14); c.set_line_width(5); src(c, INK); c.stroke()
    emoji(c, "🎙️", W / 2, FEET - 270, 70)
    parodie_label(c)


def sc_burns(c, S):
    t, a1 = S.t, S.at(1)
    s = pop(t, S.at(0, 0.0))
    x0, y0, w, h = phone(c, W / 2, 680, 520, 760, s, screen="#FFFFFF")
    def screen():
        c.save(); rrect(c, x0, y0, w, h, 42); c.clip()
        rrect(c, x0, y0, w, 120, 0); fill(c, "#F4F4F6")
        text(c, "🔍 merz mr burns", x0 + 40, y0 + 75, 32, INK, FONT_BOLD, anchor="l")
        for i in range(3):
            y = y0 + 170 + i * 180
            rrect(c, x0 + 30, y, w - 60, 150, 18); fill(c, "#FFF3C4")
            emoji(c, ["😂", "💀", "🤣"][i], x0 + 100, y + 75, 70)
            text(c, ["Meme", "Vergleich", "Edit"][i], x0 + 170, y + 55, 32, INK, FONT_HEAD, anchor="l")
            text(c, f"{[812, 304, 97][i]}k Likes", x0 + 170, y + 100, 26, "#777777", FONT_BOLD, anchor="l")
        c.restore()
    scaled(c, W / 2, 680, s, screen)
    if t >= a1:
        bubble(c, "Ausgezeichnet … 😈", W / 2 + 60, 1075, pop(t, a1 + 0.1), tail=(-0.1, 1), size=46)
    alex_bottom(c, S, "smug", "cross" if t >= a1 else "idle")


def sc_signs(c, S):
    t = S.t
    items = [("Größer als alle", "📏"), ("Fliegt selbst", "🛩️"), ("Alles führt ins Sauerland", "⛰️"), ("Keine Rede ist kurz", "🎙️")]
    for i, (lab, ic) in enumerate(items):
        y = 420 + i * 175
        row_card(c, W / 2, y, 900, 140, pop(t, S.at(i + 1, 0.0)), lab, ic, 42, num=i + 1, rot=(-0.02 if i % 2 else 0.02))
    alex_bottom(c, S, "smug", "shrug")


def sc_outro(c, S):
    t, a1 = S.t, S.at(1)
    q = "Kennst du jemanden, der auch so gern lange Reden hält?" if t < a1 else "Was soll Alex morgen sein?"
    qs = pop(t, S.at(0, 0.0)) if t < a1 else pop(t, a1)
    card(c, W / 2, 240, 940, 200, qs)
    scaled(c, W / 2, 240, qs, lambda: text_block(c, q, W / 2, 240, 44, 880, INK, FONT_HEAD))
    if t < a1 + 0.2:
        out = out_fade(t, a1)
        s = pop(t, S.at(0, 0.3)) * out
        def tag():
            c.arc(W / 2, 640, 210, 0, 2 * math.pi); fill(c, "#FFFFFF")
            c.arc(W / 2, 640, 210, 0, 2 * math.pi); c.set_line_width(8); src(c, INK); c.stroke()
            text(c, "@", W / 2, 625, 300, "#1F3A6B", FONT_HEAD)
            rrect(c, 160, 900, 760, 100, 50); fill(c, "#FFFFFF")
            rrect(c, 160, 900, 760, 100, 50); c.set_line_width(5); src(c, INK); c.stroke()
            typed = "@redet_immer_lang"
            n = int(clamp((t - S.at(0, 0.4)) / 1.0) * len(typed))
            cur = "|" if int(t * 3) % 2 == 0 else ""
            text(c, typed[:n] + cur, 210, 950, 44, "#3D8BFF", FONT_HEAD, anchor="l")
        scaled(c, W / 2, 700, s, tag, rot=math.sin(t * 4) * 0.02)
        emoji(c, "👇", 880, 1110 + math.sin(t * 8) * 12, 90 * pop(t, S.at(0, 0.6)) * out)
    if t >= a1:
        colors = ["#EC7FAE", "#3E5C9A", "#1F3A6B", "#F2B233", "#3E7BDA", "#8E5BE0", "#36B5C2", "#F07F4F", "#555A66"]
        # TikTok-Reihenfolge: 1 Pick-me-Boy, 2 Emotional abhängig, heute 3
        prev = [("🌹", "FOLGE 1"), ("🥺", "FOLGE 2"), ("🎙️", "HEUTE ✅")]
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
    alex_bottom(c, S, "happy", "wave")


SCENE_DRAW = dict(what=sc_what, sauerland=sc_sauerland, jet=sc_jet, mittel=sc_mittel, speech=sc_speech,
                  burns=sc_burns, signs=sc_signs, outro=sc_outro)
