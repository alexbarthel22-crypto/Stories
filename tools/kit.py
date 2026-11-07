"""Baukasten für neue Folgen nach bekanntem Prinzip: Helfer + generische Szenen (stage/bars/chat/signs/outro) + Haus-Intro-Deko."""
import math, random
from alexlib import *
FEET, AH = 1690, 560
def _sign(c, x, y, txt, col, rot, size=40, w=330, post=70, hh=130):
    c.save(); c.translate(x, y); c.rotate(rot)
    c.set_line_width(10); src(c, "#5A3E2A"); c.move_to(0, 40); c.line_to(0, 40 + post); c.stroke()
    rrect(c, -w / 2, -hh + 45, w, hh, 12); fill(c, col)
    rrect(c, -w / 2, -hh + 45, w, hh, 12); c.set_line_width(5); src(c, INK); c.stroke()
    text_block(c, txt, 0, 45 - hh / 2, size, w - 26, INK, FONT_HEAD)
    c.restore()





def out_fade(t, t_end, d=0.2):
    return 1 - ease_out_cubic((t - t_end) / d) if t > t_end else 1


def row_card(c, x, y, w, h, s, label, icon=None, size=40, num=None, rot=0.0):
    def d():
        rrect(c, x - w / 2 + 6, y - h / 2 + 10, w, h, 22); src(c, "#000000", 0.2); c.fill()
        rrect(c, x - w / 2, y - h / 2, w, h, 22); fill(c, "#FFFFFF")
        rrect(c, x - w / 2, y - h / 2, w, h, 22); c.set_line_width(5); src(c, INK); c.stroke()
        lx = x - w / 2 + 40
        if num is not None:
            c.arc(x - w / 2 + 75, y, 42, 0, 2 * math.pi); fill(c, "#D9762B")
            text(c, str(num), x - w / 2 + 75, y, 46, "#FFFFFF", FONT_HEAD)
            lx = x - w / 2 + 140
        text(c, label, lx, y, size, INK, FONT_HEAD, anchor="l")
        if icon:
            emoji(c, icon, x + w / 2 - 60, y, 56)
    scaled(c, x, y, s, d, rot)


def tag(c, x, y, txt, col="#E23B3B", s=1.0, size=30):
    def d():
        sz = size
        while text_width(c, txt, sz, FONT_HEAD) + 1.2 * sz > 900 and sz > 24:
            sz -= 2
        w = text_width(c, txt, sz, FONT_HEAD) + 1.2 * sz
        xx = min(max(x, 70 + w / 2), 1010 - w / 2)               # nicht über den Boxrand hinaus
        rrect(c, xx - w / 2, y - sz * 0.87, w, sz * 1.74, 14); fill(c, col)
        text(c, txt, xx, y, sz, "#FFFFFF", FONT_HEAD)
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


def box_fx(c, t, t0, x, y, w, h, kind="anger"):
    """Effekte um eine Szenen-Box: anger (rot pulsierend, 💢, Dampf), love (Herzen), shock (Blitze), party (Konfetti)."""
    if t < t0:
        return
    u = t - t0
    a = clamp(u / 0.25)
    if kind == "anger":
        pulse = 0.5 + 0.5 * math.sin(u * 12)
        for i in range(3):
            rrect(c, x - w / 2 - 10 - i * 9, y - h / 2 - 10 - i * 9, w + 20 + i * 18, h + 20 + i * 18, 30 + i * 9)
            c.set_line_width(7); src(c, "#FF3B3B", a * (0.55 - 0.15 * i) * (0.6 + 0.4 * pulse)); c.stroke()
        for (dx, dy) in ((-0.48, -0.48), (0.48, -0.5), (0.5, 0.45)):
            emoji(c, "💢", x + dx * w, y + dy * h, 70 * a * (1 + 0.15 * pulse))
        for i in range(2):
            uu = (u * 0.9 + i * 0.5) % 1
            emoji(c, "💨", x + w * 0.42, y - h * 0.5 - uu * 90, 60, rot=-0.4, alpha=a * (1 - uu))
            emoji(c, "💨", x - w * 0.42, y - h * 0.5 - uu * 90, 60, rot=0.4, alpha=a * (1 - uu))
    elif kind == "love":
        for i in range(8):
            ang = i / 8 * 2 * math.pi + u * 0.8
            rr = 1 + 0.06 * math.sin(u * 6 + i)
            emoji(c, "💘" if i % 2 else "💕", x + math.cos(ang) * w * 0.55 * rr, y + math.sin(ang) * h * 0.6 * rr, 54 * a)
    elif kind == "shock":
        for i in range(10):
            ang = i / 10 * 2 * math.pi
            r0 = max(w, h) * 0.5 + 20; r1 = r0 + 40 + 20 * math.sin(u * 20 + i)
            c.set_line_width(8); c.set_line_cap(cairo.LINE_CAP_ROUND); src(c, "#FFE14D", a)
            c.move_to(x + math.cos(ang) * r0 * w / max(w, h), y + math.sin(ang) * r0 * h / max(w, h))
            c.line_to(x + math.cos(ang) * r1 * w / max(w, h), y + math.sin(ang) * r1 * h / max(w, h)); c.stroke()
        emoji(c, "😱", x + w * 0.45, y - h * 0.5, 70 * a)
    elif kind == "party":
        rnd = random.Random(9)
        for i in range(18):
            px = x + rnd.uniform(-0.55, 0.55) * w
            py = y - h * 0.55 + ((u * rnd.uniform(120, 220) + rnd.uniform(0, h)) % (h * 1.1))
            c.save(); c.translate(px, py); c.rotate(u * 3 + i)
            rrect(c, -7, -12, 14, 24, 3); src(c, rnd.choice(["#F7C948", "#FF5CA8", "#36B5C2", "#2FA36B"]), a); c.fill()
            c.restore()


def status_dot(c, x, y, r, col="#2FD16B", t=0.0, pulse=True):
    if pulse:
        g = 0.5 + 0.5 * math.sin(t * 5)
        c.arc(x, y, r * (1.3 + 0.25 * g), 0, 2 * math.pi); src(c, col, 0.25); c.fill()
    c.arc(x, y, r, 0, 2 * math.pi); fill(c, col)
    c.arc(x, y, r, 0, 2 * math.pi); c.set_line_width(max(2, r * 0.18)); src(c, "#FFFFFF"); c.stroke()


def clock_face(c, x, y, r, hours, minutes):
    c.arc(x, y, r, 0, 2 * math.pi); fill(c, "#FFFFFF")
    c.arc(x, y, r, 0, 2 * math.pi); c.set_line_width(r * 0.08); src(c, INK); c.stroke()
    for i in range(12):
        a = i / 12 * 2 * math.pi
        c.move_to(x + math.sin(a) * r * 0.82, y - math.cos(a) * r * 0.82); c.line_to(x + math.sin(a) * r * 0.92, y - math.cos(a) * r * 0.92)
    c.set_line_width(r * 0.05); c.stroke()
    ah = (hours % 12 + minutes / 60) / 12 * 2 * math.pi; am = minutes / 60 * 2 * math.pi
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.move_to(x, y); c.line_to(x + math.sin(ah) * r * 0.5, y - math.cos(ah) * r * 0.5); c.set_line_width(r * 0.1); c.stroke()
    c.move_to(x, y); c.line_to(x + math.sin(am) * r * 0.75, y - math.cos(am) * r * 0.75); c.set_line_width(r * 0.06); c.stroke()
    c.arc(x, y, r * 0.07, 0, 2 * math.pi); c.fill()


# ---------------------------------------------------------------- Szenen
def box_move(c, cx, cy, t, kind, t0=0.0):
    """Bewegung der großen Box (vorher c.save(), danach c.restore()).
    wobble: sanftes Wackeln · rumble: Bahn-Vibration · bounce: Party-Beat · shake: hartes Rütteln ab t0 · chomp: Puls"""
    dx = dy = rot = 0.0; sc = 1.0
    if kind == "wobble":
        rot = 0.018 * math.sin(t * 3.2); sc = 1 + 0.012 * math.sin(t * 2.1)
    elif kind == "rumble":
        dx = 3 * math.sin(t * 37); dy = 4 * math.sin(t * 23) * abs(math.sin(t * 1.7))
    elif kind == "bounce":
        b = abs(math.sin(t * math.pi * 2.0)); sc = 1 + 0.025 * b; rot = 0.02 * math.sin(t * math.pi)
    elif kind == "chomp":
        sc = 1 + 0.03 * max(0, math.sin(t * 9)); rot = 0.012 * math.sin(t * 4.5)
    elif kind == "flicker":
        dx = (4 if int(t * 14) % 7 == 0 else 0)
    if kind == "shake" or (t0 and t > t0):
        u = t - t0
        if 0 <= u < 0.6:
            amp = 14 * (1 - u / 0.6); dx += amp * math.sin(u * 70); rot += 0.025 * (1 - u / 0.6) * math.sin(u * 55)
    c.translate(cx + dx, cy + dy); c.rotate(rot); c.scale(sc, sc); c.translate(-cx, -cy)


def box_flash(c, x, y, w, h, t, t0, col="#FFFFFF", d=0.35):
    """Kurzes Aufblitzen über der Box."""
    if t0 <= t < t0 + d:
        a = 0.75 * (1 - (t - t0) / d)
        rrect(c, x - w / 2, y - h / 2, w, h, 30); src(c, col, a); c.fill()


def money_rain(c, t, t0, x, y, w, n=10):
    if t < t0:
        return
    for i in range(n):
        rr = random.Random(90 + i)
        uu = ((t - t0) * rr.uniform(0.4, 0.7) + rr.random()) % 1
        emoji(c, "💸", x + rr.uniform(-w / 2, w / 2) + math.sin(uu * 7 + i) * 20, y - 60 + uu * 300, 48, rot=uu * 3, alpha=1 - uu)




# ======================================================================= generische Folge
def alex_bottom(c, S, spec, expr="smug", pose="idle", prop=None, x=W / 2, h=AH):
    person(c, x, FEET, h, spec, S.t, expr, pose, prop, name="Alex")


_ITEM_SCALE = [1.0]


def _items(c, t, S, items, li):
    """items: (emoji, x, y, size, ab_zeile[, anim]) – anim: bob/spin/pulse/shake/fly"""
    for it in items:
        e, x, y, sz, l0 = it[:5]
        an = it[5] if len(it) > 5 else "bob"
        t0 = S.at(l0, 0.15)
        if t < t0:
            continue
        p = pop(t, t0); dx = dy = rot = 0.0; k = 1.0
        if an == "bob":
            dy = math.sin(t * 3 + x) * 8
        elif an == "spin":
            rot = t * 2
        elif an == "pulse":
            k = 1 + 0.12 * max(0, math.sin(t * 6 + x))
        elif an == "shake":
            dx = math.sin(t * 40 + x) * 4; rot = math.sin(t * 30) * 0.08
        elif an == "fly":
            uu = ((t - t0) * 0.6 + (x % 7) / 7) % 1; dy = -uu * 120; k = 1 - uu * 0.5
        emoji(c, e, x + dx, y + dy, sz * p * k * _ITEM_SCALE[0], rot=rot)


def sc_stage(c, S, v, spec):
    t = S.t
    s = pop(t, S.at(0, 0.0))
    n = len(S.S.starts)
    last = S.at(n - 1, 0.3)
    bx, by, bw, bh = W / 2, 710, 940, 640
    def box():
        rrect(c, bx - bw / 2, by - bh / 2, bw, bh, 30); fill(c, v.get("box", "#FFF4E0"))
        if v.get("floor"):
            rrect(c, bx - bw / 2, by + 120, bw, bh / 2 - 120, 30); fill(c, v["floor"])
        rrect(c, bx - bw / 2, by - bh / 2, bw, bh, 30); c.set_line_width(6); src(c, INK); c.stroke()
        if v.get("head"):
            hs = v.get("head_size", 36)
            rrect(c, 110, 400, 860, 40 + hs, 14); fill(c, v.get("head_col", "#2B2F3A"))
            text(c, v["head"], W / 2, 420 + hs / 2, hs, "#FFFFFF", FONT_HEAD)
        for (sp, x, nm, ex, l_angry) in v.get("people", []):
            e = ex if (l_angry is None or t < S.at(l_angry, 0.4)) else "angry"
            person(c, x, 1000, 380, sp, t, e, bob=False, name=nm, blink_seed=int(x))
        _items(c, t, S, v.get("items", []), 0)
        for li, tg in enumerate(v.get("tags", [])):
            if tg and t > S.at(li, 0.35):
                txt, col, x, y = (tg + (W / 2, 960))[:4] if len(tg) == 2 else tg
                tag(c, x, y, txt, col, s=pop(t, S.at(li, 0.35)), size=v.get("tag_size", 30))
    _ITEM_SCALE[0] = v.get("item_scale", 1.0)
    c.save(); box_move(c, bx, by, t, v.get("move", "wobble"), last)
    scaled(c, bx, by, s, box)
    box_flash(c, bx, by, bw, bh, t, last, v.get("flash", "#FFFFFF"))
    c.restore()
    if v.get("fx"):
        box_fx(c, t, last, bx, by, bw, bh, v["fx"])
    for li, bb in enumerate(v.get("bubbles", [])):
        if bb and t > S.at(li, 0.5):
            bubble(c, bb, 830, 1190, pop(t, S.at(li, 0.5)), tail=(-0.5, 1), size=36, max_w=320)
    ex = v.get("alex", ("smug", "idle", None))
    alex_bottom(c, S, spec, *ex)
    _items(c, t, S, v.get("front", []), 0)


def sc_bars(c, S, v, spec):
    t, a1 = S.t, S.at(1)
    s = pop(t, S.at(0, 0.0))
    def card_():
        card(c, W / 2, 720, 980, 660, 1)
        text(c, v["head"], W / 2, 445, 46, INK, FONT_HEAD)
        k = clamp((t - S.at(0, 0.3)) / 1.6)
        for i, (nm, f, val, col) in enumerate(v["rows"]):
            y = 540 + i * 120
            text(c, nm, 140, y + 40, 36, INK, FONT_HEAD, anchor="l")
            rrect(c, 380, y, 560, 80, 14); fill(c, "#EEF0F4")
            if f > 0:
                rrect(c, 380, y, max(1, 560 * f * k), 80, 14); fill(c, col)
            text(c, val, 660, y + 40, 40, INK if f < 0.5 else "#FFFFFF", FONT_HEAD)
        if t > a1:
            for i, (ic, lab, col) in enumerate(v.get("pills", [])):
                yy = 520 + len(v["rows"]) * 120 + 40 + i * 82
                pl = 1 + 0.04 * math.sin(t * 6 + i * 1.5)
                def pill_(yy=yy, ic=ic, lab=lab, col=col, i=i):
                    rrect(c, 120, yy - 34, 840, 68, 34); fill(c, col)
                    rrect(c, 120, yy - 34, 840, 68, 34); c.set_line_width(4); src(c, INK); c.stroke()
                    emoji(c, ic, 175, yy, 52, rot=math.sin(t * 4 + i) * 0.2)
                    text(c, lab, 225, yy, 38, "#FFFFFF", FONT_HEAD, anchor="l")
                scaled(c, W / 2, yy, pop(t, a1 + 0.1 + i * 0.2) * pl, pill_)
    c.save(); box_move(c, W / 2, 720, t, "wobble", a1)
    scaled(c, W / 2, 720, s, card_)
    box_flash(c, W / 2, 720, 980, 660, t, a1, "#FFE14D")
    c.restore()
    alex_bottom(c, S, spec, *v.get("alex", ("smug", "hips", None)))


def sc_chat(c, S, v, spec):
    """Handy mit Chat: msgs = [(zeile, wer, text, farbe)]"""
    t = S.t
    s = pop(t, S.at(0, 0.0))
    def ph():
        rrect(c, 230, 380, 620, 680, 60); fill(c, "#17171C")
        rrect(c, 250, 400, 580, 640, 44); fill(c, "#FFFFFF")
        rrect(c, 480, 412, 120, 26, 13); fill(c, "#17171C")
        rrect(c, 250, 445, 580, 70, 0); fill(c, v.get("bar", "#2FA36B"))
        text(c, v.get("chat", "Chat"), 540, 480, 32, "#FFFFFF", FONT_HEAD)
        y = 540
        for (li, who, msg, col) in v["msgs"]:
            if t > S.at(li, 0.2):
                y += chat_msg(c, who, msg, 250, 580, y, pop(t, S.at(li, 0.2)), col) + 14
    c.save(); box_move(c, W / 2, 720, t, v.get("move", "wobble"), S.at(len(S.S.starts) - 1, 0.3))
    scaled(c, W / 2, 720, s, ph)
    c.restore()
    if v.get("fx"):
        box_fx(c, t, S.at(len(S.S.starts) - 1, 0.3), W / 2, 720, 620, 680, v["fx"])
    alex_bottom(c, S, spec, *v.get("alex", ("smug", "idle", "📱")))


def sc_signs(c, S, v, spec):
    t = S.t
    for i, (lab, ic) in enumerate(v["items"]):
        y = 400 + i * 175
        row_card(c, W / 2, y, 1000, 160, pop(t, S.at(i + 1, 0.0)), lab, ic, 38, num=i + 1,
                 rot=(-0.02 if i % 2 else 0.02) + 0.012 * math.sin(t * 3 + i))
    for i in range(3):
        emoji(c, "🚩", 140 + i * 400, 1150 + math.sin(t * 3 + i) * 12, 90 * pop(t, S.at(0, 0.2 + 0.15 * i)))
    alex_bottom(c, S, spec, "smug", "shrug")


PREV = [("🌹", "#EC7FAE"), ("🥺", "#3E5C9A"), ("🌀", "#4A2E6B"), ("🏘️", "#5E8C3A"), ("⏰", "#2F6FA8"), ("🥡", "#D9762B")]


def sc_outro(c, S, v, spec):
    t, a1 = S.t, S.at(1)
    q = v["q"] if t < a1 else "Was soll Alex morgen sein?"
    qs = pop(t, S.at(0, 0.0)) if t < a1 else pop(t, a1)
    card(c, W / 2, 230, 1000, 220, qs)
    scaled(c, W / 2, 230, qs, lambda: text_block(c, q, W / 2, 230, 52, 940, INK, FONT_HEAD))
    if t < a1 + 0.2:
        out = 1 - ease_out_cubic((t - a1) / 0.2) if t > a1 else 1
        s = pop(t, S.at(0, 0.3)) * out
        def tg():
            c.arc(W / 2, 640, 210, 0, 2 * math.pi); fill(c, "#FFFFFF")
            c.arc(W / 2, 640, 210, 0, 2 * math.pi); c.set_line_width(8); src(c, INK); c.stroke()
            text(c, "@", W / 2, 625, 300, v["col"], FONT_HEAD)
            rrect(c, 160, 900, 760, 100, 50); fill(c, "#FFFFFF")
            rrect(c, 160, 900, 760, 100, 50); c.set_line_width(5); src(c, INK); c.stroke()
            typed = v["handle"]
            n = int(clamp((t - S.at(0, 0.4)) / 1.0) * len(typed))
            cur = "|" if int(t * 3) % 2 == 0 else ""
            text(c, typed[:n] + cur, 200, 950, 40, "#3D8BFF", FONT_HEAD, anchor="l")
        scaled(c, W / 2, 700, s, tg, rot=math.sin(t * 4) * 0.02)
    if t >= a1:
        prev = PREV + [(v["icon"], v["col"])]
        for i in range(9):
            r, cc = i // 3, i % 3
            x, y = 250 + cc * 290, 445 + r * 192
            def icon(x=x, y=y, i=i):
                col = prev[i][1] if i < len(prev) else ["#36B5C2", "#F07F4F", "#555A66"][i % 3]
                c.arc(x, y, 88, 0, 2 * math.pi); fill(c, col)
                c.arc(x, y, 88, 0, 2 * math.pi); c.set_line_width(7); src(c, "#FFFFFF"); c.stroke()
                if i < len(prev):
                    emoji(c, prev[i][0], x, y, 90)
                    lab = "HEUTE ✅" if i == len(prev) - 1 else f"FOLGE {i + 1}"
                    rrect(c, x - 88, y + 58, 176, 48, 12); fill(c, "#2FA36B" if i == len(prev) - 1 else "#555A66")
                    text(c, lab, x, y + 82, 30, "#FFFFFF", FONT_HEAD)
                else:
                    text(c, "?", x, y, 100, "#FFFFFF", FONT_HEAD)
            scaled(c, x, y, pop(t, a1 + 0.1 + i * 0.07), icon)
        ps = pop(t, S.at(1, 0.45))
        def pill():
            rrect(c, 40, 950, 1000, 126, 63); fill(c, "#E23B3B")
            rrect(c, 40, 950, 1000, 126, 63); c.set_line_width(6); src(c, "#FFFFFF"); c.stroke()
            text(c, "Schreib's in die Kommentare ⬇️", W / 2, 1013, 52, "#FFFFFF", FONT_HEAD)
        scaled(c, W / 2, 1013, ps * (1 + 0.05 * math.sin(t * 7)), pill)
    alex_bottom(c, S, spec, "happy", "wave")


KINDS = dict(stage=sc_stage, bars=sc_bars, chat=sc_chat, signs=sc_signs, outro=sc_outro)


def make_scenes(scenes_def, spec):
    out = {}
    for sd in scenes_def:
        v = sd["viz"]; fn = KINDS[v["kind"]]
        out[sd["id"]] = (lambda c, S, fn=fn, v=v: fn(c, S, v, spec))
    return out


def make_intro(cfg):
    """cfg: icon,bg,spec,title_lines,house,left/right (emoji,label), door (l1,l2), neon (l1,l2,col), signs (a,b), fly, burst, extras"""
    def decor(c, t, u):
        s_ = clamp(u)
        for (wx, e, lab) in ((294, *cfg["left"]), (670, *cfg["right"])):
            rrect(c, wx, 902, 118, 106, 8); src(c, "#FFF4D6", s_); c.fill()
            emoji(c, e, wx + 59, 950 + math.sin(t * 3 + wx) * 4, 52 * s_)
            text(c, lab, wx + 59, 993, 14, INK, FONT_HEAD, alpha=s_)
        def door_sign():
            rrect(c, 455, 1100, 170, 56, 10); fill(c, "#FFFFFF")
            rrect(c, 455, 1100, 170, 56, 10); c.set_line_width(3); src(c, INK); c.stroke()
            text(c, cfg["door"][0], 540, 1118, 17, INK, FONT_HEAD)
            text(c, cfg["door"][1], 540, 1140, 14, INK, FONT_HEAD)
        scaled(c, 540, 1128, s_, door_sign)
        def neon():
            glow = 0.7 + 0.3 * (1 if int(t * 3) % 4 else 0.2)
            rrect(c, 232, 1070, 196, 80, 18); src(c, "#1C1C22", 0.92); c.fill()
            rrect(c, 232, 1070, 196, 80, 18); c.set_line_width(5); src(c, cfg["neon"][2], glow); c.stroke()
            text(c, cfg["neon"][0], 330, 1094, 28, "#FFFFFF", FONT_HEAD, alpha=glow)
            text(c, cfg["neon"][1], 330, 1128, 22, "#FFFFFF", FONT_HEAD, alpha=glow)
        scaled(c, 330, 1110, s_, neon)
        _sign(c, 230, 1640, cfg["signs"][0], "#FFFFFF", -0.1, 50, 420, 60, 170)
        _sign(c, 850, 1640, cfg["signs"][1], "#FFE1B8", 0.08, 50, 420, 60, 170)
        for i in range(5):
            u2 = (t * 0.35 + i / 5) % 1
            emoji(c, cfg["fly"][i % len(cfg["fly"])], 120 + i * 210, 1250 - u2 * 160, 46, alpha=0.8 * (1 - u2))

    def extras(c, x, feet, h, t, u):
        k = h / 100.0
        for (e, dx, dy, sz) in cfg.get("extras", []):
            emoji(c, e, x + dx * k, feet - dy * k + math.sin(t * 3 + dx) * k, sz * k)

    INTRO = dict(icon=cfg["icon"], bg=cfg["bg"], spec=cfg["spec"], expr="smug", pose="hips", hand_prop=None,
                 house=cfg["house"], umbrella=False, title_lines=cfg["title_lines"], fill="#6FB7E8", decor=decor,
                 alex_extras=extras, burst=cfg["burst"])

    def draw_intro(c, t, shuffle, ticks, flash_start, reveal_t, role_text):
        draw_intro_house(c, t, shuffle, ticks, flash_start, reveal_t, role_text, INTRO)
    return INTRO, draw_intro


# ----------------------------------------------------------------------- realistischer Messenger
def _phone_shell(c, x, y, w, h):
    rrect(c, x + 10, y + 16, w, h, 56); src(c, "#000000", 0.25); c.fill()
    for (bx, by, bh) in ((-5, 150, 50), (-5, 220, 80), (w, 200, 110)):
        rrect(c, x + bx, y + by, 6, bh, 3); fill(c, "#55565E")
    g = cairo.LinearGradient(x, y, x + w, y + h)
    g.add_color_stop_rgb(0, 0.42, 0.42, 0.46); g.add_color_stop_rgb(0.5, 0.2, 0.2, 0.23); g.add_color_stop_rgb(1, 0.38, 0.38, 0.42)
    rrect(c, x, y, w, h, 56); c.set_source(g); c.fill()
    rrect(c, x + 6, y + 6, w - 12, h - 12, 50); fill(c, "#050506")
    return x + 16, y + 16, w - 32, h - 32


def _status(c, x0, y0, w, col):
    text(c, "9:41", x0 + 50, y0 + 30, 22, col, FONT_HEAD, anchor="l")
    for i in range(4):
        hh = 7 + i * 4
        rrect(c, x0 + w - 130 + i * 8, y0 + 38 - hh, 5, hh, 1); src(c, col); c.fill()
    rrect(c, x0 + w - 74, y0 + 21, 34, 17, 5); c.set_line_width(2); src(c, col, 0.6); c.stroke()
    rrect(c, x0 + w - 71, y0 + 24, 24, 11, 3); src(c, col); c.fill()
    rrect(c, x0 + w / 2 - 60, y0 + 12, 120, 32, 16); fill(c, "#000000")


def _avatar(c, x, y, r, name, col):
    c.arc(x, y, r, 0, 2 * math.pi); fill(c, col)
    text(c, name[0].upper(), x, y, r * 1.1, "#FFFFFF", FONT_HEAD)


def _bubble(c, x0, w, y, txt, out, tm, s):
    lines = wrap(c, txt, 26, w * 0.68, FONT_BOLD)
    bw = max(text_width(c, ln, 26, FONT_BOLD) for ln in lines) + 120
    bh = len(lines) * 33 + 26
    bx = x0 + w - bw - 18 if out else x0 + 18
    def d():
        rrect(c, bx + 2, y + 3, bw, bh, 18); src(c, "#000000", 0.08); c.fill()
        rrect(c, bx, y, bw, bh, 18); fill(c, "#D9FDD3" if out else "#FFFFFF")
        for i, ln in enumerate(lines):
            text(c, ln, bx + 18, y + 28 + i * 33, 26, "#111B21", FONT_BOLD, anchor="l")
        text(c, tm + (" ✓✓" if out else ""), bx + bw - 14, y + bh - 14, 15, "#53BDEB" if out else "#667781", FONT_BOLD, anchor="r")
    scaled(c, bx + (bw if out else 0), y + bh, s, d)
    return bh


def sc_messenger(c, S, v, spec):
    """v: list=[(zeile, name, vorschau, zeit, ungelesen, farbe)], switch=zeile ab der der Chat offen ist,
    chat=dict(name, col, msgs=[(zeile, out?, text, zeit)])"""
    t = S.t
    s = pop(t, S.at(0, 0.0))
    sw_line = v.get("switch", 0)
    in_chat = sw_line is not None and t >= S.at(sw_line, 0.0)
    def ph():
        x0, y0, w, h = _phone_shell(c, 255, 370, 570, 720)
        c.save(); rrect(c, x0, y0, w, h, 42); c.clip()
        if not in_chat:
            src(c, "#FFFFFF"); c.paint()
            _status(c, x0, y0, w, "#000000")
            text(c, "Chats", x0 + 30, y0 + 100, 44, "#000000", FONT_HEAD, anchor="l")
            rrect(c, x0 + 24, y0 + 135, w - 48, 44, 12); fill(c, "#F0F2F5")
            text(c, "🔍  Suchen", x0 + 44, y0 + 157, 20, "#667781", FONT_BOLD, anchor="l")
            for i, (li, nm, prev, tm, unread, col) in enumerate(v["list"]):
                if t < S.at(li, 0.15 + i * 0.12):
                    continue
                yy = y0 + 200 + i * 108
                def row(yy=yy, nm=nm, prev=prev, tm=tm, unread=unread, col=col):
                    _avatar(c, x0 + 66, yy + 50, 36, nm, col)
                    text(c, nm, x0 + 118, yy + 32, 26, "#111B21", FONT_HEAD, anchor="l")
                    text(c, prev, x0 + 118, yy + 68, 20, "#667781", FONT_BOLD, anchor="l")
                    text(c, tm, x0 + w - 24, yy + 32, 17, "#1FA855" if unread else "#667781", FONT_BOLD, anchor="r")
                    if unread:
                        c.arc(x0 + w - 42, yy + 66, 15, 0, 2 * math.pi); fill(c, "#25D366")
                        text(c, str(unread), x0 + w - 42, yy + 66, 16, "#FFFFFF", FONT_HEAD)
                    c.move_to(x0 + 118, yy + 104); c.line_to(x0 + w, yy + 104); c.set_line_width(1); src(c, "#E9EDEF"); c.stroke()
                scaled(c, x0 + w / 2, yy + 50, pop(t, S.at(li, 0.15 + i * 0.12)), row)
        else:
            ch = v["chat"]
            src(c, "#EFEAE2"); c.paint()
            rnd = random.Random(5)
            for _ in range(40):
                emoji(c, rnd.choice(["☕", "🎈", "⭐", "🎵"]), x0 + rnd.uniform(0, w), y0 + rnd.uniform(110, h), 22, alpha=0.06)
            rrect(c, x0, y0, w, 120, 0); fill(c, "#F7F8FA")
            _status(c, x0, y0, w, "#000000")
            text(c, "‹", x0 + 24, y0 + 84, 44, "#007AFF", FONT_HEAD, anchor="l")
            _avatar(c, x0 + 86, y0 + 82, 24, ch["name"], ch["col"])
            text(c, ch["name"], x0 + 122, y0 + 72, 24, "#111B21", FONT_HEAD, anchor="l")
            text(c, "online", x0 + 122, y0 + 98, 16, "#667781", FONT_BOLD, anchor="l")
            text(c, "📞", x0 + w - 40, y0 + 82, 26, "#007AFF", FONT_HEAD)
            yy = y0 + 140
            for (li, out, msg, tm) in ch["msgs"]:
                if t > S.at(li, 0.2):
                    yy += _bubble(c, x0, w, yy, msg, out, tm, pop(t, S.at(li, 0.2))) + 14
            rrect(c, x0, y0 + h - 84, w, 84, 0); fill(c, "#F7F8FA")
            rrect(c, x0 + 20, y0 + h - 70, w - 110, 46, 23); fill(c, "#FFFFFF")
            text(c, "Nachricht", x0 + 42, y0 + h - 47, 20, "#8696A0", FONT_BOLD, anchor="l")
            c.arc(x0 + w - 48, y0 + h - 47, 26, 0, 2 * math.pi); fill(c, "#25D366")
            text(c, "🎤", x0 + w - 48, y0 + h - 47, 22, "#FFFFFF", FONT_HEAD)
        c.restore()
    last = S.at(len(S.S.starts) - 1, 0.3)
    c.save(); box_move(c, W / 2, 730, t, v.get("move", "wobble"), last)
    scaled(c, W / 2, 730, s, ph)
    c.restore()
    if v.get("fx"):
        box_fx(c, t, last, W / 2, 730, 570, 720, v["fx"])
    alex_bottom(c, S, spec, *v.get("alex", ("smug", "idle", "📱")))


KINDS["messenger"] = sc_messenger
