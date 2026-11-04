"""Visuals: Alex ist heute ein Gaslighter (TikTok Folge 4). Aufbau wie Pick-me-Boy.
Ton: typische Sätze zeigen, nicht verharmlosen; ehrlicher Moment am Ende.
"""
import math, random
from alexlib import *

# Outfit heute: dunkelgrüne Bomberjacke-Optik, Jeans
AL = alex(top="#3F5A4A", top_style="tee", chain=None, pants="#3F4A6B", shoes="#FFFFFF")
FEET, AH = 1665, 470
LENA = person_spec(4, girl=True, top="#46B39A", hair="#6B3E26", skin="#EBB894", pants="#3F4A6B", shoes="#2A2A2A")

INTRO = dict(icon="🌀", bg="#4A2E6B", spec=AL, expr="smug", pose="shrug", hand_prop=None,
             side_emoji="🤷", burst=["🌀", "🚩", "🤷", "🙄", "❓", "💬", "🧠", "🕯️"])


def draw_intro(c, t, shuffle, ticks, flash_start, reveal_t, role_text):
    draw_intro_generic(c, t, shuffle, ticks, flash_start, reveal_t, role_text, INTRO)


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
        bubble(c, "Das hab ich nie gesagt. 🤷", W / 2, 1075, pop(t, a1), tail=(0.2, 1), size=44)
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
        bubble(c, "Du hast doch gesagt, du nimmst den Bus 🤷", W / 2, 1075, pop(t, S.at(0, 0.45)), tail=(0, 1), size=38, max_w=700)
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
        bubble(c, "Das hast du falsch verstanden 🙄", W / 2, 1075, pop(t, S.at(0, 0.6)), tail=(0, 1), size=40)
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
        text(c, "😂 „Witz“ über Lena", W / 2, 1030, 42, "#FFFFFF", FONT_HEAD)
    if t > S.at(0, 0.6):
        bubble(c, "Du bist einfach zu empfindlich 🙄", 430, 1060, pop(t, S.at(0, 0.6)), tail=(-0.4, 1), size=38, max_w=560)
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
        bubble(c, "Sorry … 😔", 790, 1075, pop(t, S.at(0, 0.7)), tail=(0.3, 1), size=44)
    duo(c, S, "smug", "hips", "sad", 0.0)
    if S.at(0, 0.35) < t < S.at(0, 0.7):
        confusion(c, t, 790, 1110, 0.8)


def sc_signs(c, S):
    t = S.t
    items = [("„Das hab ich nie gesagt.“", "🤷"), ("„Du bist zu empfindlich.“", "🙄"),
             ("„Du bildest dir das ein.“", "🌀"), ("Am Ende bist DU schuld", "🔄")]
    for i, (lab, ic) in enumerate(items):
        y = 420 + i * 175
        row_card(c, W / 2, y, 900, 140, pop(t, S.at(i + 1, 0.0)), lab, ic, 40, num=i + 1, rot=(-0.02 if i % 2 else 0.02))
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
    card(c, W / 2, 240, 940, 200, qs)
    scaled(c, W / 2, 240, qs, lambda: text_block(c, q, W / 2, 240, 42, 880, INK, FONT_HEAD))
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
        # TikTok-Reihenfolge: 1 Pick-me-Boy, 2 Emotional abhängig, 3 Merz, heute 4
        prev = [("🌹", "FOLGE 1"), ("🥺", "FOLGE 2"), ("🎙️", "FOLGE 3"), ("🌀", "HEUTE ✅")]
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
    person(c, W / 2, FEET, AH, AL, t, "happy", "wave", name="Alex")


SCENE_DRAW = dict(what=sc_what, forgot=sc_forgot, proof=sc_proof, joke=sc_joke, fight=sc_fight,
                  signs=sc_signs, real=sc_real, outro=sc_outro)
