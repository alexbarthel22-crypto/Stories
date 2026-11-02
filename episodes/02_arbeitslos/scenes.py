"""Visuals für Folge 2 (Arbeitslos). Jede Szene: draw(c, S)
S.t = Zeit in der Szene, S.at(i, f) = Startzeit von Zeile i (+ Anteil f ihrer Dauer).
"""
import math, random
from alexlib import *

# Outfit heute: grauer Hoodie, Jogginghose, Hausschuhe
AL = alex(top="#8A8F99", top_style="hoodie", pants="#5D6270", shoes="#3C6E9E")
FEET, AH = 1665, 470
OMA = person_spec(5, girl=True, hair_style="bun", hair="#C9C9CF", skin="#F1C9A8", top="#8E5BE0",
                  pants="#4A4A5A", shoes="#5A3A2A", glasses=True)
MAMA = person_spec(6, girl=True, hair="#7A4A2A", top="#2FA36B", skin="#F1C9A8")
PAPA = person_spec(7, hair="#4A3A30", top="#3E7BDA", skin="#F1C9A8")
CLERK = person_spec(8, hair="#2B2B2B", top="#3C3C46", top_style="suit", glasses=True, skin="#E9B48A")

INTRO = dict(icon="🛋️", bg="#5FA9B8", spec=AL, expr="sad", pose="shrug", hand_prop=None,
             side_emoji="📄", burst=["📄", "☕", "💤", "📉", "🛋️", "📺", "🍕", "⏰"])


def draw_intro(c, t, shuffle, ticks, flash_start, reveal_t, role_text):
    draw_intro_generic(c, t, shuffle, ticks, flash_start, reveal_t, role_text, INTRO)


def alex_bottom(c, S, expr="happy", pose="idle", prop=None, x=W / 2, h=AH):
    person(c, x, FEET, h, AL, S.t, expr, pose, prop, name="Alex")


def out_fade(t, t_end, d=0.2):
    return 1 - ease_out_cubic((t - t_end) / d) if t > t_end else 1


def row_card(c, x, y, w, h, s, label, icon=None, size=40, num=None, check=None, rot=0.0):
    def d():
        rrect(c, x - w / 2 + 6, y - h / 2 + 10, w, h, 22); src(c, "#000000", 0.2); c.fill()
        rrect(c, x - w / 2, y - h / 2, w, h, 22); fill(c, "#FFFFFF")
        rrect(c, x - w / 2, y - h / 2, w, h, 22); c.set_line_width(5); src(c, INK); c.stroke()
        lx = x - w / 2 + 40
        if num is not None:
            c.arc(x - w / 2 + 75, y, 42, 0, 2 * math.pi); fill(c, "#E23B3B")
            text(c, str(num), x - w / 2 + 75, y, 46, "#FFFFFF", FONT_HEAD)
            lx = x - w / 2 + 140
        if check is not None:
            rrect(c, x - w / 2 + 35, y - 28, 56, 56, 10); c.set_line_width(5); src(c, INK); c.stroke()
            if check:
                emoji(c, "✅", x - w / 2 + 63, y, 52)
            lx = x - w / 2 + 120
        text(c, label, lx, y, size, INK, FONT_HEAD, anchor="l")
        if icon:
            emoji(c, icon, x + w / 2 - 60, y, 56)
    scaled(c, x, y, s, d, rot)


# ======================================================================= SZENEN
def sc_plan(c, S):
    t, a1 = S.t, S.at(1)
    if t < a1 + 0.2:
        s = pop(t, S.at(0, 0.0)) * out_fade(t, a1)
        def letter():
            c.save(); c.translate(W / 2, 720); c.rotate(-0.04)
            rrect(c, -330 + 10, -400 + 14, 660, 800, 18); src(c, "#000000", 0.2); c.fill()
            rrect(c, -330, -400, 660, 800, 18); fill(c, "#FFFFFF")
            rrect(c, -330, -400, 660, 800, 18); c.set_line_width(5); src(c, INK); c.stroke()
            text(c, "KÜNDIGUNG", 0, -300, 70, INK, FONT_HEAD)
            text(c, "Sehr geehrter Herr Alex,", -270, -200, 30, "#333333", FONT_BOLD, anchor="l")
            for i in range(6):
                rrect(c, -270, -140 + i * 50, 540 - (i % 3) * 90, 14, 7); fill(c, "#DADADA")
            c.restore()
        scaled(c, W / 2, 720, s, letter)
        red_flag_stamp(c, W / 2, 900, pop(t, S.at(0, 0.5), 0.25), "FIRMA PLEITE", rot=-0.18)
        emoji(c, "📉", 850, 470, 110 * pop(t, S.at(0, 0.3)) * out_fade(t, a1))
        alex_bottom(c, S, "sad" if t > S.at(0, 0.4) else "shock")
    if t >= a1:
        s = pop(t, a1 + 0.05)
        card(c, W / 2, 470, 760, 120, s, color="#1F1F28")
        scaled(c, W / 2, 470, s, lambda: text(c, "ALEX' PLAN 💪", W / 2, 470, 56, "#FFFFFF", FONT_HEAD))
        items = [("Früh aufstehen", "⏰", 0.3), ("Bewerbungen schreiben", "📄", 0.55), ("Sport machen", "🏃", 0.8)]
        for i, (lab, ic, f) in enumerate(items):
            row_card(c, W / 2, 650 + i * 160, 900, 130, pop(t, S.at(1, f)), lab, ic, 42, check=False,
                     rot=(0.015 if i % 2 else -0.015))
        alex_bottom(c, S, "happy", "hips")


def sc_alarm(c, S):
    t, a1 = S.t, S.at(1)
    s = pop(t, S.at(0, 0.0))
    # digitale Uhr; läuft in der Snooze-Zeile vor
    mins = 7 * 60
    if t > a1:
        mins = 7 * 60 + int(ease_in_out((t - a1) / max(0.1, S.dur - a1 - 0.3)) * (4 * 60 + 29))
    def clock():
        rrect(c, 190, 400, 700, 300, 40); fill(c, "#1F1F28")
        rrect(c, 190, 400, 700, 300, 40); c.set_line_width(6); src(c, INK); c.stroke()
        rrect(c, 230, 440, 620, 220, 24); fill(c, "#101014")
        text(c, f"{mins // 60:02d}:{mins % 60:02d}", W / 2, 550, 170, "#FF4D4D", FONT_HEAD)
    shake = math.sin(t * 60) * 8 if t < a1 else 0
    scaled(c, W / 2 + shake, 550, s, clock, rot=math.sin(t * 50) * 0.02 if t < a1 else 0)
    if t < a1:
        for i, (x, y, r) in enumerate(((220, 380, -0.3), (860, 380, 0.3))):
            emoji(c, "🔔", x + math.sin(t * 40 + i) * 10, y, 100 * pop(t, S.at(0, 0.1)), rot=r)
        text(c, "RRRING!", W / 2, 800, 90 * pop(t, S.at(0, 0.15)), "#FFFFFF", FONT_HEAD)
    else:
        for i in range(3):
            ts = S.at(1, 0.05 + i * 0.3)
            def btn(i=i):
                x = 230 + i * 310
                rrect(c, x - 130, 760, 260, 100, 50); fill(c, "#F7C948")
                rrect(c, x - 130, 760, 260, 100, 50); c.set_line_width(5); src(c, INK); c.stroke()
                text(c, "SNOOZE", x, 810, 44, INK, FONT_HEAD)
            scaled(c, 230 + i * 310, 810, pop(t, ts), btn, rot=(-0.05 + 0.05 * i))
    alex_bottom(c, S, "sleepy", "idle")
    for i in range(3):
        u = (t * 0.5 + i / 3) % 1
        emoji(c, "💤", 660 + u * 80, 1230 - u * 180, 60 + i * 8, alpha=1 - u)


def sc_breakfast(c, S):
    t = S.t
    for i, (x, e, lab, f) in enumerate(((290, "🥣", "FRÜHSTÜCK?", 0.1), (790, "🍕", "MITTAG?", 0.45))):
        s = pop(t, S.at(0, f))
        def d(x=x, e=e, lab=lab):
            card(c, x, 700, 420, 460, 1)
            emoji(c, e, x, 650, 220)
            text(c, lab, x, 860, 46, INK, FONT_HEAD)
        scaled(c, x, 700, s, d, rot=(-0.04 if i == 0 else 0.04))
    emoji(c, "🤷", W / 2, 1040, 120 * pop(t, S.at(0, 0.7)))
    alex_bottom(c, S, "neutral", "shrug")


def sc_jobcenter(c, S):
    t, a1 = S.t, S.at(1)
    s = pop(t, S.at(0, 0.0))
    called = 12 + (1 if t > a1 + 1.0 else 0)
    def board():
        rrect(c, 140, 380, 800, 260, 26); fill(c, "#1F1F28")
        rrect(c, 140, 380, 800, 260, 26); c.set_line_width(6); src(c, INK); c.stroke()
        text(c, "AUFGERUFEN", W / 2, 440, 40, "#BBBBBB", FONT_HEAD)
        text(c, f"{called:03d}", W / 2, 555, 150, "#FF4D4D", FONT_HEAD)
    scaled(c, W / 2, 510, s, board)
    # Ticket in Alex' Hand
    ts = pop(t, S.at(0, 0.4))
    def ticket():
        c.save(); c.translate(820, 1000); c.rotate(0.12)
        rrect(c, -150, -100, 300, 200, 14); fill(c, "#FFFDF0")
        rrect(c, -150, -100, 300, 200, 14); c.set_line_width(5); src(c, INK); c.stroke()
        text(c, "IHRE NUMMER", 0, -55, 30, "#555555", FONT_BOLD)
        text(c, "247", 0, 30, 110, INK, FONT_HEAD)
        c.restore()
    scaled(c, 820, 1000, ts, ticket)
    if t < a1:
        # Wartende auf Stühlen
        for i, sp in enumerate([person_spec(30 + i, girl=bool(i % 2)) for i in range(4)]):
            x = 170 + i * 120
            ps = pop(t, S.at(0, 0.15 + 0.05 * i))
            scaled(c, x, 1010, ps, lambda x=x, sp=sp, i=i: person(c, x, 1010, 250, sp, t, "sleepy" if i % 2 else "neutral", blink_seed=i))
            rrect(c, x - 50, 930, 100, 20, 6); fill(c, "#5A6B80")
    else:
        bs = pop(t, a1 + 0.05)
        def desk():
            person(c, 280, 1050, 300, CLERK, t, "neutral", bob=False)
            rrect(c, 110, 960, 360, 100, 12); fill(c, "#B07A4F")
            rrect(c, 110, 960, 360, 100, 12); c.set_line_width(5); src(c, INK); c.stroke()
            emoji(c, "🗂️", 380, 935, 70)
        scaled(c, 280, 1000, bs, desk)
        rrect(c, 120, 690, 300, 70, 35); fill(c, "#FFFFFF")
        text(c, "⏳ +3 Stunden", 270, 725, 34, INK, FONT_HEAD)
        bubble(c, "Bitte bringen Sie nächstes Mal alle Unterlagen mit.", 540, 820, pop(t, S.at(1, 0.3)),
               tail=(-0.6, 1), size=36, max_w=620)
    alex_bottom(c, S, "neutral" if t < a1 else "shock", "idle")


def sc_apply(c, S):
    t, a1 = S.t, S.at(1)
    if t < a1 + 0.2:
        s = pop(t, S.at(0, 0.0)) * out_fade(t, a1)
        def ad():
            card(c, W / 2, 720, 900, 720, 1)
            rrect(c, 90, 360, 900, 110, 0); fill(c, "#2FA36B")
            text(c, "WIR SUCHEN DICH! 🚀", W / 2, 415, 52, "#FFFFFF", FONT_HEAD)
            text(c, "Junior (m/w/d)", W / 2, 520, 56, INK, FONT_HEAD)
            reqs = ["10 Jahre Berufserfahrung", "5 Sprachen fließend", "Max. 23 Jahre alt", "Gehalt: Obstkorb 🍎"]
            for i, r in enumerate(reqs):
                y = 620 + i * 85
                if t > S.at(0, 0.35 + 0.12 * i):
                    if i == 0 and t > S.at(0, 0.6):
                        rrect(c, 150, y - 30, 700, 60, 8); src(c, "#FFE14D"); c.fill()
                    text(c, "• " + r, 160, y, 40, "#222222", FONT_BOLD, anchor="l")
        scaled(c, W / 2, 720, s, ad)
        alex_bottom(c, S, "shock" if t > S.at(0, 0.6) else "neutral", "idle", "💻")
    if t >= a1:
        s = pop(t, a1 + 0.05)
        def inbox():
            card(c, W / 2, 720, 920, 760, 1)
            text(c, "📥 Posteingang", 140, 400, 44, INK, FONT_HEAD, anchor="l")
            subs = ["Ihre Bewerbung", "Rückmeldung", "Leider…", "Absage", "Ihre Bewerbung", "Leider…"]
            for i, sb in enumerate(subs):
                ts = S.at(1, 0.1 + 0.12 * i)
                if t < ts:
                    continue
                y = 480 + i * 100
                def row(y=y, sb=sb):
                    rrect(c, 120, y, 840, 84, 14); fill(c, "#F3F3F6")
                    c.arc(170, y + 42, 26, 0, 2 * math.pi); fill(c, "#E23B3B")
                    text(c, "✉️", 170, y + 42, 28)
                    text(c, sb, 215, y + 28, 32, INK, FONT_HEAD, anchor="l")
                    text(c, "…haben uns für einen anderen Kandidaten entschieden", 215, y + 62, 22, "#666666", FONT_BOLD, anchor="l")
                scaled(c, W / 2, y + 42, pop(t, ts, 0.2), row)
        scaled(c, W / 2, 720, s, inbox)
        alex_bottom(c, S, "sad", "idle")


def sc_family(c, S):
    t, a1 = S.t, S.at(1)
    s = pop(t, S.at(0, 0.0))
    def table():
        for x, sp, ex in ((260, MAMA, "happy"), (540, OMA, "happy"), (820, PAPA, "happy")):
            if t > a1 + 0.6:
                ex = "neutral"
            person(c, x, 1000, 420, sp, t, ex, blink_seed=x % 7, name="Oma" if sp is OMA else None)
        rrect(c, 90, 860, 900, 60, 16); fill(c, "#B07A4F")
        rrect(c, 90, 860, 900, 60, 16); c.set_line_width(5); src(c, INK); c.stroke()
        for x, e in ((260, "🍗"), (540, "🥔"), (820, "🥗")):
            emoji(c, e, x, 840, 70)
    scaled(c, W / 2, 800, s, table)
    if t < a1 + 0.1:
        bubble(c, "Und, was machst du gerade beruflich? 😊", 540, 450, pop(t, S.at(0, 0.3)) * out_fade(t, a1),
               tail=(0, 1), size=40, max_w=640)
    else:
        bubble(c, "Ich bin gerade so in einer … Findungsphase 😅", 540, 1080, pop(t, a1 + 0.05),
               tail=(0, 1), size=40, max_w=640)
        if t > a1 + 0.6:
            for x in (260, 820):
                emoji(c, "🤨", x, 470, 80 * pop(t, a1 + 0.6))
    alex_bottom(c, S, "cringe" if t > S.at(0, 0.6) else "happy", "idle")
    if t > S.at(0, 0.6):
        emoji(c, "💦", 680, 1250 + math.sin(t * 6) * 6, 60)


def sc_linkedin(c, S):
    t, a1 = S.t, S.at(1)
    s = pop(t, S.at(0, 0.0))
    def post():
        card(c, W / 2, 720, 920, 700, 1)
        c.save()
        c.arc(190, 470, 70, 0, 2 * math.pi); c.clip()
        src(c, "#DCEBFF"); c.paint()
        person(c, 190, 650, 380, AL, t, "happy", bob=False)
        c.restore()
        c.arc(190, 470, 70, 0, 2 * math.pi); c.set_line_width(10); src(c, "#2FA36B"); c.stroke()
        rrect(c, 125, 520, 130, 34, 17); fill(c, "#2FA36B")
        text(c, "#OPENTOWORK", 190, 537, 15, "#FFFFFF", FONT_HEAD)
        text(c, "Alex", 290, 445, 42, INK, FONT_HEAD, anchor="l")
        text(c, "Visionär | Macher | Teamplayer", 290, 495, 28, "#666666", FONT_BOLD, anchor="l")
        text_block(c, "Ich freue mich auf neue Herausforderungen! 🚀💼 #motivation #neuanfang", W / 2, 690, 44, 800, INK, FONT_HEAD)
        rrect(c, 130, 880, 820, 4, 2); fill(c, "#DDDDDD")
        text(c, "👍 3   💬 Mama: Stolz auf dich ❤️", 140, 945, 32, "#444444", FONT_BOLD, anchor="l")
    scaled(c, W / 2, 720, s, post)
    if t >= a1:
        def note():
            c.save(); c.translate(W / 2, 1080); c.rotate(-0.06)
            rrect(c, -380 + 8, -70 + 10, 760, 140, 8); src(c, "#000000", 0.2); c.fill()
            rrect(c, -380, -70, 760, 140, 8); fill(c, "#FFE14D")
            text(c, "ÜBERSETZT:", 0, -28, 34, "#7A5A00", FONT_HEAD)
            text(c, "BITTE STELLT MICH EIN 🙏", 0, 26, 50, INK, FONT_HEAD)
            c.restore()
        scaled(c, W / 2, 1080, pop(t, a1 + 0.05), note)
    alex_bottom(c, S, "happy" if t < a1 else "puppy", "phone", "📱")


def sc_night(c, S):
    t = S.t
    emoji(c, "💡", W / 2, 520, 260 * pop(t, S.at(0, 0.1)), rot=math.sin(t * 5) * 0.05)
    s = pop(t, S.at(0, 0.35))
    def todo():
        card(c, W / 2, 900, 820, 380, 1, color="#FFFDF0")
        text(c, "AB MORGEN:", W / 2, 760, 48, INK, FONT_HEAD)
        for i, it in enumerate(["5 Uhr aufstehen", "Kalt duschen", "100 Bewerbungen", "Marathon laufen"]):
            if t > S.at(0, 0.45 + 0.1 * i):
                text(c, "→ " + it, 200, 830 + i * 55, 36, "#222222", FONT_BOLD, anchor="l")
    scaled(c, W / 2, 900, s, todo, rot=0.02)
    alex_bottom(c, S, "happy", "up")


def sc_phases(c, S):
    t = S.t
    items = [("Urlaubsgefühl", "🏖️"), ("Langeweile", "🥱"), ("Panik", "😱"), ("Sauerteigbrot", "🍞")]
    for i, (lab, ic) in enumerate(items):
        y = 420 + i * 175
        row_card(c, W / 2, y, 900, 140, pop(t, S.at(i + 1, 0.0)), lab, ic, 48, num=i + 1,
                 rot=(-0.02 if i % 2 else 0.02))
    alex_bottom(c, S, "happy" if t > S.at(4) else "neutral", "shrug", "🍞" if t > S.at(4) else None)


def sc_outro(c, S):
    t, a1 = S.t, S.at(1)
    q = "Kennst du jemanden, der gerade arbeitslos ist?" if t < a1 else "Was soll Alex morgen sein?"
    qs = pop(t, S.at(0, 0.0)) if t < a1 else pop(t, a1)
    card(c, W / 2, 230, 920, 170, qs)
    scaled(c, W / 2, 230, qs, lambda: text_block(c, q, W / 2, 230, 48, 840, INK, FONT_HEAD))
    if t < a1 + 0.2:
        out = out_fade(t, a1)
        s = pop(t, S.at(0, 0.3)) * out
        def tag():
            c.arc(W / 2, 640, 210, 0, 2 * math.pi); fill(c, "#FFFFFF")
            c.arc(W / 2, 640, 210, 0, 2 * math.pi); c.set_line_width(8); src(c, INK); c.stroke()
            text(c, "@", W / 2, 625, 300, "#5FA9B8", FONT_HEAD)
            rrect(c, 160, 900, 760, 100, 50); fill(c, "#FFFFFF")
            rrect(c, 160, 900, 760, 100, 50); c.set_line_width(5); src(c, INK); c.stroke()
            typed = "@dein_kumpel"
            n = int(clamp((t - S.at(0, 0.55)) / 1.0) * len(typed))
            cur = "|" if int(t * 3) % 2 == 0 else ""
            text(c, typed[:n] + cur, 210, 950, 44, "#3D8BFF", FONT_HEAD, anchor="l")
        scaled(c, W / 2, 700, s, tag, rot=math.sin(t * 4) * 0.02)
        emoji(c, "👇", 880, 1110 + math.sin(t * 8) * 12, 90 * pop(t, S.at(0, 0.6)) * out)
    if t >= a1:
        colors = ["#EC7FAE", "#5FA9B8", "#2FA36B", "#F2B233", "#3E7BDA", "#8E5BE0", "#36B5C2", "#F07F4F", "#555A66"]
        for i in range(9):
            r, cc = i // 3, i % 3
            x, y = 260 + cc * 280, 500 + r * 230
            def icon(x=x, y=y, i=i):
                c.arc(x, y, 95, 0, 2 * math.pi); fill(c, colors[i])
                c.arc(x, y, 95, 0, 2 * math.pi); c.set_line_width(6); src(c, "#FFFFFF"); c.stroke()
                if i < 2:
                    emoji(c, ["🌹", "🛋️"][i], x, y, 100)
                    lab, col = (["GESTERN", "HEUTE ✅"][i], ["#555A66", "#2FA36B"][i])
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


SCENE_DRAW = dict(plan=sc_plan, alarm=sc_alarm, breakfast=sc_breakfast, jobcenter=sc_jobcenter, apply=sc_apply,
                  family=sc_family, linkedin=sc_linkedin, night=sc_night, phases=sc_phases, outro=sc_outro)
