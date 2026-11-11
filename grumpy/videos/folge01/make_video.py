"""Folge 1 – erzeugt pro Videobild eine SVG-Datei (Insel-Szene + Avatar + Kamera + Untertitel).
Danach: node render.js <svg-ordner> <png-ordner>  und  ffmpeg (siehe build.sh).
"""
import json, math, re, sys
from pathlib import Path

HERE = Path(__file__).parent
AVATAR = (HERE / "../../avatar/avatar.svg").read_text()
TL = json.loads((HERE / "timeline.json").read_text())
ENV = json.loads((HERE / "envelope.json").read_text())
FPS = 25
END_CARD = 0.8
DURATION = TL["duration"] + END_CARD
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "_frames_svg"
OUT.mkdir(parents=True, exist_ok=True)
O = "#2B2B2B"

# ---------------------------------------------------------------- Avatar-Teile aus avatar.svg
defs = "".join(re.findall(r"<defs>.*?</defs>", AVATAR, re.S))
char = AVATAR[AVATAR.index("  <!-- lange, wellige Haare hinten"):AVATAR.index("  <!-- Flaschenpost")]
m0 = char.index("  <!-- Mund:")
m1 = char.index('  <path d="M640 330')
CHAR_A, CHAR_B = char[:m0], char[m1:]
HEAD_T = '<g transform="translate(222.6 225.5) scale(0.62)">'
assert HEAD_T in CHAR_A


def mouth(a):
    """Mund im Kopf-Koordinatensystem; a = Öffnung 0..1."""
    if a < 0.08:
        return ('<path d="M470 630 Q490 613 505 617 Q512 613 519 617 Q534 613 554 630 Q512 622 470 630 Z" fill="#D98C84" stroke="#2B2B2B" stroke-width="5" stroke-linejoin="round"/>'
                '<path d="M472 631 Q512 623 552 631 Q541 650 512 651 Q483 650 472 631 Z" fill="#E39A90" stroke="#2B2B2B" stroke-width="5" stroke-linejoin="round"/>'
                '<path d="M467 632 l-6 9 M557 632 l6 9" stroke="#2B2B2B" stroke-width="4" stroke-linecap="round"/>')
    h = 8 + 40 * a
    w = 40 - 6 * a
    return (f'<path d="M{512-w} 628 Q512 {612} {512+w} 628 Q{512+w*0.8} {628+h} 512 {630+h} Q{512-w*0.8} {628+h} {512-w} 628 Z" fill="#5A1E22" stroke="#2B2B2B" stroke-width="5" stroke-linejoin="round"/>'
            f'<path d="M{512-w*0.7} 626 Q512 {618} {512+w*0.7} 626 L{512+w*0.6} {632} Q512 {626} {512-w*0.6} {632} Z" fill="#FFFFFF"/>'
            f'<path d="M{512-w} 628 Q512 {606} {512+w} 628" fill="none" stroke="#D98C84" stroke-width="7" stroke-linecap="round"/>'
            f'<path d="M{512-w*0.75} {632+h*0.55} Q512 {638+h*1.05} {512+w*0.75} {632+h*0.55}" fill="none" stroke="#E39A90" stroke-width="7" stroke-linecap="round"/>')


BLINK = ('<g><ellipse cx="440" cy="480" rx="50" ry="34" fill="#F2C29B"/><ellipse cx="584" cy="480" rx="50" ry="34" fill="#F2C29B"/>'
         '<path d="M394 484 Q440 498 486 484 M538 484 Q584 498 630 484" fill="none" stroke="#2B2B2B" stroke-width="6" stroke-linecap="round"/></g>')


def rage(t):
    """Extrem-Wut: roter Kopf, Zornesader, Dampf aus den Ohren (Kopf-Koordinaten)."""
    puffs = ""
    for k in range(3):
        ph = (t * 1.6 + k / 3) % 1
        for ex, dx in [(330, -1), (694, 1)]:
            x, y, r = ex + dx * (20 + 60 * ph), 470 - 150 * ph, 18 + 26 * ph
            puffs += f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.0f}" fill="#FFFFFF" stroke="#2B2B2B" stroke-width="4" opacity="{1-ph:.2f}"/>'
    vein = ('<g transform="translate(640 330) scale(1.3)" fill="none" stroke="#E0262B" stroke-width="9" stroke-linecap="round">'
            '<path d="M-28 -8 Q-10 -10 -8 -28 M8 -28 Q10 -10 28 -8 M28 8 Q10 10 8 28 M-8 28 Q-10 10 -28 8"/></g>')
    flush = '<path d="M338 436 C338 330 410 276 512 276 C614 276 686 330 686 436 C686 530 660 596 604 644 C570 672 540 682 512 682 C484 682 454 672 420 644 C364 596 338 530 338 436 Z" fill="#FF2A2A" opacity="0.28"/>'
    return puffs, vein


def character(t, amp, blink, head_rot, bounce, angry=False):
    a = CHAR_A.replace(HEAD_T, f'<g transform="rotate({head_rot:.2f} 540 640) translate(222.6 225.5) scale(0.62)">')
    # Haare hinten + Strähnen vorne drehen IMMER mit dem Kopf (eine Einheit)
    rot = f'<g transform="rotate({head_rot:.2f} 540 640)">'
    a = a.replace("  <!-- lange, wellige Haare hinten", rot + "  <!-- lange, wellige Haare hinten", 1)
    a = a.replace("  <!-- Beine mit Netzstrumpfhose", "</g>  <!-- Beine mit Netzstrumpfhose", 1)
    a = a.replace("  <!-- Strähnen vorne", rot + "  <!-- Strähnen vorne", 1)
    a = a.replace("  <!-- Kopf -->", "</g>  <!-- Kopf -->", 1)
    pre = post = ""
    if angry:
        pre, post = rage(t)
        a = a.replace('<g id="brows"', '<g transform="translate(0 12)" id="brows"')
        a = a.replace('<!-- Gesicht', pre + '<!-- Gesicht', 1)
    return f'<g transform="translate(0 {-bounce:.1f})">{a}{mouth(amp)}{"" if angry or not blink else BLINK}{post}{CHAR_B}</g>'


# ---------------------------------------------------------------- Hilfsfunktionen
def ease(x):
    x = min(max(x, 0), 1)
    return x * x * (3 - 2 * x)


def line_at(t):
    for l in TL["lines"]:
        if l["start"] - 0.05 <= t <= l["end"] + 0.25:
            return l
    return None


def L(i):
    return TL["lines"][i]


# Kamera-Keyframes: (Zeit, Zoom, Mitte x, Mitte y) – Insel bleibt immer im Bild
FEET = 1452          # Füße von Clara (Welt-Koordinate)
FEET_ON_SCREEN = 1170  # darunter liegen die Untertitel (über der unteren TikTok-Zone)


def cy_for(s, dy=0):
    return FEET - (FEET_ON_SCREEN - 960) / s + dy


HOOK_S = 1.6          # Anfang: Clara groß (Füße tief, Text darüber)
HOOK_CY = FEET - (1560 - 960) / HOOK_S

KEYS = [
    (0.00, HOOK_S, 560, HOOK_CY),
    (L(0)["end"] + 0.1, HOOK_S, 560, HOOK_CY),
    (L(2)["end"], 0.90, 540, cy_for(0.90)),
    (L(3)["end"], 1.05, 555, cy_for(1.05)),
    (L(4)["start"] + 0.2, 1.20, 350, cy_for(1.20)),
    (L(5)["end"] + 0.2, 1.20, 770, cy_for(1.20)),
    (L(6)["start"] + 0.3, 0.90, 540, cy_for(0.90)),
    (L(8)["end"], 0.96, 545, cy_for(0.96)),
    (L(9)["start"] + 0.4, 1.22, 560, cy_for(1.22)),
    (L(10)["end"] + 0.2, 1.24, 560, cy_for(1.24)),
    (L(11)["start"] + 0.3, 0.90, 540, cy_for(0.90)),
    (DURATION + 1, 0.90, 540, cy_for(0.90)),
]


def camera(t):
    for (t0, s0, x0, y0), (t1, s1, x1, y1) in zip(KEYS, KEYS[1:]):
        if t0 <= t <= t1:
            k = ease((t - t0) / max(t1 - t0, 1e-6))
            s, x, y = s0 + (s1 - s0) * k, x0 + (x1 - x0) * k, y0 + (y1 - y0) * k
            break
    # Wackeln bei „WAS GLOTZT DU SO?!“
    if L(0)["start"] <= t <= L(0)["end"]:
        x += 22 * math.sin(t * 61) / s ; y += 18 * math.cos(t * 47) / s
    return s, x, y


def wave_row(y, t, speed, spacing, phase, col="#BFEFFF", w=4):
    off = (t * speed + phase) % spacing
    xs = [-200 + off + k * spacing for k in range(int(1500 / spacing) + 2)]
    d = "".join(f"M{x:.0f} {y} q18 -10 36 0 q18 10 36 0 " for x in xs)
    return f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{w}" stroke-linecap="round" opacity="0.85"/>'


def gull(x, y, t, s=1.0):
    f = 10 * math.sin(t * 9)
    return (f'<path transform="translate({x:.0f} {y:.0f}) scale({s})" d="M-24 {f:.1f} Q-12 -12 0 0 Q12 -12 24 {f:.1f}" '
            f'fill="none" stroke="{O}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>')


def crab(x, y, s, t):
    legs = 4 * math.sin(t * 14)
    return f'''<g transform="translate({x:.1f} {y}) scale({s}) translate(-296 -848)" stroke="{O}" stroke-width="5" stroke-linejoin="round" stroke-linecap="round">
    <path d="M262 852 l-22 {-20+legs:.1f} M262 862 l-26 {-6-legs:.1f} M330 852 l22 {-20-legs:.1f} M330 862 l26 {-6+legs:.1f}" fill="none"/>
    <path d="M268 832 C250 800 230 800 228 815 C240 812 250 820 255 832 Z" fill="#E8553E"/>
    <path d="M324 832 C342 800 362 800 364 815 C352 812 342 820 337 832 Z" fill="#E8553E"/>
    <ellipse cx="296" cy="848" rx="40" ry="24" fill="#E8553E"/>
    <path d="M284 826 v-14 M308 826 v-14" fill="none"/>
    <circle cx="284" cy="810" r="6" fill="#FFFFFF"/><circle cx="308" cy="810" r="6" fill="#FFFFFF"/>
    <circle cx="281" cy="811" r="2.5" fill="{O}" stroke="none"/><circle cx="305" cy="811" r="2.5" fill="{O}" stroke="none"/>
    <path d="M286 856 q10 -6 20 0" fill="none" stroke-width="4"/></g>'''


def palm(x, y, t):
    sway = 3.5 * math.sin(t * 1.3)
    return f'''<g stroke="{O}" stroke-width="6" stroke-linejoin="round" stroke-linecap="round">
    <path d="M{x-18} {y} C{x-10} {y-200} {x+10} {y-380} {x+60} {y-520} L{x+88} {y-510} C{x+40} {y-380} {x+22} {y-200} {x+18} {y} Z" fill="#B07A45"/>
    <path d="M{x-10} {y-60} l26 4 M{x-6} {y-150} l26 5 M{x+4} {y-240} l26 6 M{x+20} {y-330} l26 7 M{x+40} {y-420} l24 8" fill="none" stroke-width="3.5"/>
    <g transform="rotate({sway:.2f} {x+74} {y-515})" fill="#3FA34D">
      <path d="M{x+74} {y-515} C{x+14} {y-560} {x-56} {y-545} {x-104} {y-485} C{x-48} {y-515} {x+14} {y-517} {x+74} {y-515} Z"/>
      <path d="M{x+74} {y-515} C{x+26} {y-605} {x-46} {y-620} {x-96} {y-590} C{x-30} {y-585} {x+26} {y-560} {x+74} {y-515} Z"/>
      <path d="M{x+74} {y-515} C{x+96} {y-605} {x+166} {y-640} {x+232} {y-628} C{x+166} {y-600} {x+116} {y-560} {x+74} {y-515} Z"/>
      <path d="M{x+74} {y-515} C{x+134} {y-545} {x+200} {y-525} {x+240} {y-462} C{x+186} {y-492} {x+134} {y-502} {x+74} {y-515} Z"/>
      <path d="M{x+74} {y-515} C{x+64} {y-585} {x+86} {y-645} {x+124} {y-675} C{x+104} {y-615} {x+94} {y-560} {x+74} {y-515} Z"/>
    </g>
    <circle cx="{x+64}" cy="{y-500}" r="15" fill="#7A4A26"/><circle cx="{x+90}" cy="{y-496}" r="15" fill="#7A4A26"/></g>'''


def caption(text, t, t0, t1, wtimes=None):
    """Untertitel unter Clara (TikTok-Sicherheitszone), ohne Hintergrund:
    dicke Kontur + harter Schatten; das gerade gesprochene Wort leuchtet gelb und größer."""
    words = text.split()
    for k in range(len(words) - 1, 0, -1):   # „…“ nie allein in eine Zeile
        if words[k] == "…":
            words[k - 1] += " …"; del words[k]
    if words and words[0] == "…" and len(words) > 1:
        words[1] = "… " + words[1]; del words[0]
    # Wort-Zeiten grob nach Länge verteilen (Satzzeichen/„…“ zählen kaum)
    weights = [max(len(w.strip("….,!?:")), 1) + 1.5 for w in words]
    tot, acc, active = sum(weights), 0.0, len(words) - 1
    for i, wgt in enumerate(weights):
        acc += wgt
        if t < t0 + (t1 - t0) * acc / tot:
            active = i
            break
    if wtimes and len(wtimes) == len(words):      # exakte Wortzeiten (ElevenLabs)
        active = 0
        for i, wt in enumerate(wtimes):
            if t >= wt["start"] - 0.03:
                active = i
    lines, cur = [], []
    for i, wd in enumerate(words):
        if cur and len(" ".join(words[j] for j in cur)) + len(wd) + 1 > 20:
            lines.append(cur); cur = [i]
        else:
            cur.append(i)
    lines.append(cur)
    fs, lh = 68, 86
    pop = 1 + 0.12 * max(0, 1 - (t - t0) / 0.15)
    out = ['<defs><filter id="ts" x="-10%" y="-30%" width="120%" height="170%"><feDropShadow dx="0" dy="7" stdDeviation="0" flood-color="#000" flood-opacity="1"/></filter></defs>',
           f'<g transform="translate(470 1262) scale({pop:.3f})" font-family="DejaVu Sans, Noto Color Emoji, sans-serif" font-weight="900" text-anchor="middle" filter="url(#ts)">']
    for k, idx in enumerate(lines):
        spans = ""
        for n, i in enumerate(idx):
            sep = " " if n else ""
            if i == active:
                spans += f'{sep}<tspan fill="#FFE600" font-size="{fs+12}">{words[i]}</tspan>'
            else:
                spans += f'{sep}<tspan fill="#FFFFFF">{words[i]}</tspan>'
        out.append(f'<text y="{k * lh}" font-size="{fs}" stroke="#000" stroke-width="15" stroke-linejoin="round" paint-order="stroke">{spans}</text>')
    out.append("</g>")
    return "".join(out)


def live_badge(t):
    """Hochwertiges LIVE-Schild oben links: pulsierender roter Punkt, Zuschauerzahl."""
    pulse = 0.55 + 0.45 * (0.5 + 0.5 * math.sin(t * 6))
    viewers = 1200 + int(t * 37) + int(40 * math.sin(t * 3))
    v = f"{viewers/1000:.1f}".replace(".", ",") + "K"
    return f'''<g transform="translate(40 225)" font-family="DejaVu Sans, sans-serif" font-weight="900">
  <defs><linearGradient id="lg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FF4B5C"/><stop offset="1" stop-color="#D5001C"/></linearGradient>
  <filter id="sh" x="-20%" y="-30%" width="140%" height="170%"><feDropShadow dx="0" dy="4" stdDeviation="5" flood-color="#000" flood-opacity="0.45"/></filter></defs>
  <g filter="url(#sh)">
    <rect x="0" y="0" width="610" height="78" rx="39" fill="#0E0E12" opacity="0.82"/>
    <rect x="8" y="8" width="150" height="62" rx="31" fill="url(#lg)"/>
    <circle cx="42" cy="39" r="17" fill="#FF6B78" opacity="{pulse*0.6:.2f}"/>
    <circle cx="42" cy="39" r="10" fill="#FFFFFF" opacity="{0.6+0.4*pulse:.2f}"/>
    <text x="100" y="52" text-anchor="middle" font-size="34" fill="#FFFFFF" letter-spacing="2">LIVE</text>
    <text x="178" y="35" font-size="27" fill="#FFFFFF">TAG 1 · DIE INSEL</text>
    <text x="178" y="64" font-size="21" fill="#FFD23F" font-weight="700">mit Clara</text>
    <g transform="translate(495 39)">
      <path d="M-18 0 Q0 -16 18 0 Q0 16 -18 0 Z" fill="none" stroke="#FFFFFF" stroke-width="3.5"/>
      <circle cx="0" cy="0" r="5.5" fill="#FFFFFF"/>
      <text x="28" y="10" font-size="26" fill="#FFFFFF" font-weight="700">{v}</text>
    </g>
  </g></g>'''


def hook_text(t):
    """„WAS GLOTZT DU SO?!“ – ab Sekunde 0 groß in der Mitte, leuchtet beim Schreien riesig auf."""
    l0 = L(0)
    speaking = l0["start"] <= t <= l0["end"] + 0.1
    if speaking:
        k = (t - l0["start"]) / (l0["end"] - l0["start"])
        sc = 1.0 + 0.27 * min(k * 4, 1) + 0.04 * math.sin(t * 40)
        glow, col = 1.0, "#FFE600"
        jx, jy = 9 * math.sin(t * 57), 7 * math.cos(t * 43)
    else:
        sc, glow, col, jx, jy = 1.0, 0.0, "#FFFFFF", 0, 0
    fade = 1 - ease((t - l0["end"] - 0.1) / 0.25) if t > l0["end"] + 0.1 else 1
    lines = [("WAS GLOTZT", 0), ("DU SO?!", 1)]
    txt = ""
    for ln, k in lines:
        y = k * 122
        txt += (f'<text y="{y}" font-size="112" fill="none" stroke="#FF2A00" stroke-width="40" stroke-linejoin="round" opacity="{0.55*glow:.2f}" filter="url(#glow)">{ln}</text>'
                f'<text y="{y}" font-size="112" fill="{col}" stroke="#111" stroke-width="16" stroke-linejoin="round" paint-order="stroke">{ln}</text>')
    return (f'<defs><filter id="glow" x="-30%" y="-60%" width="160%" height="220%"><feGaussianBlur stdDeviation="18"/></filter></defs>'
            f'<g opacity="{fade:.2f}" transform="translate({540+jx:.1f} {440+jy:.1f}) scale({sc:.3f})" font-family="DejaVu Sans, sans-serif" font-weight="900" text-anchor="middle">{txt}</g>')


def word_start(line, word):
    """Geschätzter Startzeitpunkt eines Wortes (gleiche Gewichtung wie die Untertitel)."""
    if line.get("words"):
        for wt in line["words"]:
            if wt["w"].startswith(word):
                return wt["start"]
    words = line["text"].split()
    weights = [max(len(w.strip("….,!?:")), 1) + 1.5 for w in words]
    i = next(k for k, w in enumerate(words) if w.startswith(word))
    return line["start"] + (line["end"] - line["start"]) * sum(weights[:i]) / sum(weights)


COMMENT_T0 = word_start(next(l for l in TL["lines"] if "Kommentare" in l["text"]), "Kommentare")
COMMENT = "Buddel dich ein, spuck hoch und fang die Spucke wieder auf bis es Nacht wird"


def comment_anim(dt):
    """Jemand tippt einen Kommentar und schickt ihn ab (generische Kommentar-Optik)."""
    slide_in = ease(dt / 0.3)
    slide_out = ease((dt - 3.4) / 0.3)
    y = 320 - 420 * (1 - slide_in) - 420 * slide_out
    t_type0, t_type1, t_send = 0.3, 2.3, 2.5
    n = int(len(COMMENT) * min(max((dt - t_type0) / (t_type1 - t_type0), 0), 1))
    typed = COMMENT[:n]
    posted = dt >= t_send
    lines, cur = [], ""
    for wd in typed.split(" "):
        if cur and len(cur) + len(wd) + 1 > 27:
            lines.append(cur); cur = wd
        else:
            cur = (cur + " " + wd) if cur else wd
    lines.append(cur)
    lines = lines[:3]
    cursor = "" if posted or (dt * 2.5) % 1 > 0.5 else "|"
    F = 'font-family="DejaVu Sans, Noto Color Emoji, sans-serif"'
    txt = "".join(f'<text x="150" y="{118 + k*46}" font-size="36" fill="#161616" {F} font-weight="600">{ln}{cursor if k == len(lines)-1 else ""}</text>'
                  for k, ln in enumerate(lines))
    if not posted:
        # Eingabefeld + Senden-Knopf (pulsiert, dann „Tipp“)
        tap = 1 - 0.18 * max(0, 1 - abs(dt - 2.42) / 0.1)
        body = (f'<rect x="130" y="72" width="640" height="190" rx="28" fill="#F1F1F2"/>'
                + (txt if typed else f'<text x="150" y="118" font-size="34" fill="#9A9A9F" {F}>Kommentar hinzufügen …</text>')
                + f'<g transform="translate(830 168) scale({tap:.2f})"><circle r="44" fill="#FE2C55"/>'
                  f'<path d="M-16 -18 L22 0 L-16 18 L-10 0 Z" fill="#FFFFFF"/></g>')
        header = f'<text x="450" y="46" text-anchor="middle" font-size="28" fill="#444" {F} font-weight="700">Kommentare</text>'
    else:
        k = dt - t_send
        likes = int(min(k / 0.7, 1) ** 2 * 8400) + 1
        lk = f"{likes/1000:.1f}".replace(".", ",") + "K" if likes >= 1000 else str(likes)
        heart = 1 + 0.35 * max(0, 1 - abs(k - 0.25) / 0.2)
        body = (f'<text x="150" y="80" font-size="27" fill="#8A8A90" {F} font-weight="700">mia.inselfan · gerade eben</text>'
                + txt.replace('y="118"', 'y="126"').replace('y="164"', 'y="172"').replace('y="210"', 'y="218"')
                + f'<g transform="translate(830 140) scale({heart:.2f})"><path d="M0 18 C-30 -4 -26 -30 -10 -30 C-3 -30 0 -24 0 -20 C0 -24 3 -30 10 -30 C26 -30 30 -4 0 18 Z" fill="#FE2C55"/></g>'
                + f'<text x="830" y="205" text-anchor="middle" font-size="28" fill="#555" {F} font-weight="700">{lk}</text>')
        header = f'<text x="450" y="46" text-anchor="middle" font-size="28" fill="#444" {F} font-weight="700">1 neuer Kommentar</text>'
    return (f'<defs><filter id="cs" x="-10%" y="-20%" width="120%" height="150%"><feDropShadow dx="0" dy="8" stdDeviation="10" flood-color="#000" flood-opacity="0.35"/></filter></defs>'
            f'<g transform="translate(70 {y:.0f})" filter="url(#cs)">'
            f'<rect x="0" y="0" width="900" height="290" rx="34" fill="#FFFFFF"/>'
            f'<rect x="410" y="10" width="80" height="8" rx="4" fill="#D0D0D4"/>{header}'
            f'<circle cx="70" cy="140" r="46" fill="#FF9F43"/><circle cx="70" cy="128" r="17" fill="#FFFFFF"/>'
            f'<path d="M40 172 Q70 140 100 172 Z" fill="#FFFFFF"/>{body}</g>')


# ---------------------------------------------------------------- Szene
def scene(t, profile=None):
    """profile=(zoom, x, y, größe): quadratisches Standbild ohne Einblendungen (z. B. Profilbild)."""
    i = min(int(t * FPS), len(ENV) - 1)
    amp = ENV[i] if t < TL["duration"] else 0.0
    blink = (t % 3.3) < 0.12 or (6.1 < t < 6.22)
    angry = t <= L(0)["end"] + 0.2
    head_rot = 5 * math.sin(t * 22) if angry else 2.0 * math.sin(t * 1.7) + 3 * amp * math.sin(t * 9)
    bounce = 10 * amp + 3 * math.sin(t * 2.1)
    s, cx, cy = camera(t)
    if profile:
        amp, blink, angry, head_rot, bounce = 0.0, False, False, -3.0, 0.0
        s, cx, cy, size = profile

    w = []
    # Himmel + Ferne
    w.append('<rect x="-400" y="-400" width="1880" height="1180" fill="url(#vsky)"/>')
    w.append(f'<g transform="rotate({t*8:.1f} 860 250)" stroke="#FFE27A" stroke-width="10" stroke-linecap="round">' +
             "".join(f'<path d="M860 {250-118} v-34" transform="rotate({k*30} 860 250)"/>' for k in range(12)) + "</g>")
    w.append(f'<circle cx="860" cy="250" r="88" fill="#FFD23F" stroke="{O}" stroke-width="6"/>')
    for bx, by, sc, sp in [(120, 470, 1.0, 9), (700, 560, 0.8, 6), (420, 320, 0.6, 12)]:
        x = (bx + t * sp) % 1500 - 200
        w.append(f'<g transform="translate({x:.0f} {by}) scale({sc})" fill="#FFFFFF" opacity="0.92"><ellipse cx="0" cy="0" rx="95" ry="26"/>'
                 f'<ellipse cx="45" cy="-20" rx="55" ry="30"/><ellipse cx="-35" cy="-12" rx="40" ry="22"/></g>')
    w.append(gull((t * 85) % 1500 - 200, 380 + 20 * math.sin(t), t))
    w.append(gull((t * 85 + 90) % 1500 - 200, 420 + 20 * math.sin(t + 1), t + 0.4, 0.8))
    w.append(gull(1180 - (t * 60) % 1500, 610, t + 1.3, 0.6))
    # Meer
    w.append('<rect x="-400" y="760" width="1880" height="1560" fill="url(#vsea)"/>')
    w.append(f'<path d="M-400 760 H1480" stroke="{O}" stroke-width="4"/>')
    # springende Fische (vereinzelt)
    for t0, x0, y0, dirn in [(2.2, 120, 1080, 1), (7.4, 960, 1150, -1), (12.6, 200, 1820, 1), (17.8, 880, 1000, -1)]:
        k = (t - t0) / 1.1
        if 0 <= k <= 1:
            fx, fy = x0 + dirn * 170 * k, y0 - 150 * math.sin(math.pi * k)
            ang = dirn * (-50 + 100 * k)
            w.append(f'<g transform="translate({fx:.0f} {fy:.0f}) rotate({ang:.0f}) scale({dirn} 1)" stroke="{O}" stroke-width="4" stroke-linejoin="round">'
                     f'<path d="M-34 0 Q-10 -20 22 0 Q-10 20 -34 0 Z" fill="#FF9F43"/><path d="M-30 0 l-18 -14 l2 28 z" fill="#FF9F43"/>'
                     f'<circle cx="10" cy="-4" r="3" fill="{O}" stroke="none"/></g>')
        if 0.95 <= k <= 1.4 or -0.4 <= k <= 0.05:
            sx = x0 + (dirn * 170 if k > 0.5 else 0)
            r = 20 + 60 * abs(k - (1 if k > 0.5 else 0))
            w.append(f'<ellipse cx="{sx}" cy="{y0}" rx="{r:.0f}" ry="{r*0.3:.0f}" fill="none" stroke="#FFFFFF" stroke-width="4" opacity="0.8"/>')
    # Fischschwarm im Flachwasser
    for k in range(5):
        a_ = t * 0.6 + k * 1.25
        fx, fy = 540 + 520 * math.cos(a_), 1440 + 222 * math.sin(a_)
        if math.sin(a_) > 0.2:
            w.append(f'<path transform="translate({fx:.0f} {fy:.0f}) rotate({math.degrees(a_)+90:.0f})" d="M-12 0 Q0 -7 12 0 Q0 7 -12 0 Z M-12 0 l-8 -6 v12 z" fill="#2C7A8C" opacity="0.55"/>')
    for k, y in enumerate(range(800, 1960, 70)):
        w.append(wave_row(y, t, 18 + k * 3, 260 + (k % 3) * 40, k * 83, w=3 + k * 0.15))
    # Hai-Flosse kreist
    fx = (t * 95) % 1700 - 300
    w.append(f'<g transform="translate({fx:.0f} {1800 + 6*math.sin(t*3):.0f})"><path d="M-30 0 Q0 -10 10 -70 Q28 -30 50 0 Z" fill="#5D6D7E" stroke="{O}" stroke-width="5" stroke-linejoin="round"/>'
             f'<path d="M-60 6 q20 -10 40 0 M50 6 q20 -10 40 0" fill="none" stroke="#FFFFFF" stroke-width="4" stroke-linecap="round"/></g>')
    # Treibgut: Sneaker + Flamingo
    bob = 8 * math.sin(t * 2.4)
    w.append(f'<g transform="translate(150 {1700+bob:.1f}) rotate({-12+4*math.sin(t*2):.1f})" stroke="{O}" stroke-width="5" stroke-linejoin="round">'
             f'<path d="M-20 -20 L20 -20 L22 6 L-54 10 C-62 10 -60 -6 -46 -8 Z" fill="#FFFFFF"/><rect x="-60" y="6" width="84" height="18" rx="6" fill="#39FF6A"/></g>')
    w.append(f'<g transform="translate(905 {1745-bob:.1f}) rotate({3*math.sin(t*1.8):.1f})" stroke="{O}" stroke-width="6" stroke-linejoin="round" stroke-linecap="round">'
             f'<ellipse cx="0" cy="0" rx="92" ry="28" fill="#FF8FC2"/><ellipse cx="0" cy="-4" rx="48" ry="11" fill="#2A8DB5"/>'
             f'<path d="M58 -14 C88 -54 73 -94 48 -94 C28 -94 23 -69 38 -64" fill="none" stroke="{O}" stroke-width="22"/>'
             f'<path d="M58 -14 C88 -54 73 -94 48 -94 C28 -94 23 -69 38 -64" fill="none" stroke="#FF8FC2" stroke-width="12"/>'
             f'<path d="M34 -72 l-18 10 l14 6 z" fill="{O}"/></g>')
    # Insel: Flachwasser, Schaum, Sand
    foam = (t * 40) % 60
    w.append('<ellipse cx="540" cy="1440" rx="545" ry="235" fill="#7FDCDC" opacity="0.75"/>')
    w.append(f'<ellipse cx="540" cy="1440" rx="500" ry="205" fill="none" stroke="#FFFFFF" stroke-width="10" stroke-dasharray="40 20" stroke-dashoffset="{foam:.0f}" opacity="0.9"/>')
    w.append(f'<ellipse cx="540" cy="1430" rx="485" ry="192" fill="#F4D58D" stroke="{O}" stroke-width="6"/>')
    w.append('<ellipse cx="540" cy="1442" rx="485" ry="180" fill="none" stroke="#E2BE6E" stroke-width="18" opacity="0.6"/>')
    w.append('<g fill="#D9B46A">' + "".join(f'<circle cx="{x}" cy="{y}" r="5"/>' for x, y in
             [(180, 1440), (260, 1530), (700, 1580), (860, 1500), (420, 1350), (980, 1440), (620, 1330), (320, 1600)]) + "</g>")
    # Fußspuren vom Wasser bis zu ihr
    w.append('<g fill="#D9B46A">' + "".join(
        f'<ellipse cx="{x}" cy="{y}" rx="9" ry="5" transform="rotate(-20 {x} {y})"/>' for x, y in
        [(330, 1600), (360, 1580), (392, 1566), (420, 1545), (452, 1532), (480, 1512), (508, 1500)]) + "</g>")
    # Hintergrund-Objekte auf der Insel
    w.append(f'<g stroke="{O}" stroke-width="5" stroke-linejoin="round"><ellipse cx="955" cy="1380" rx="46" ry="30" fill="#9AA6B2"/><ellipse cx="915" cy="1395" rx="28" ry="20" fill="#B5C0CA"/></g>')
    w.append(f'<g stroke="{O}" stroke-width="5" stroke-linejoin="round" fill="#4CAF50">'
             f'<path d="M800 1350 C780 1300 820 1270 845 1300 C850 1260 900 1260 905 1305 C930 1280 960 1310 940 1350 Z"/></g>')
    w.append(palm(230, 1420, t))
    w.append(f'<g stroke="{O}" stroke-width="5"><circle cx="268" cy="1430" r="20" fill="#7A4A26"/><circle cx="300" cy="1440" r="17" fill="#7A4A26"/></g>')
    # Flaschenpost
    w.append(f'<g transform="translate(860 1455) rotate(-20) scale(0.8)" stroke="{O}" stroke-width="5" stroke-linejoin="round">'
             f'<path d="M-50 -20 h90 q20 0 20 20 q0 20 -20 20 h-90 q-14 0 -14 -20 q0 -20 14 -20 z" fill="#9FE3C9"/>'
             f'<rect x="58" y="-10" width="34" height="20" rx="4" fill="#9FE3C9"/><rect x="90" y="-12" width="14" height="24" rx="3" fill="#B07A45"/>'
             f'<rect x="-38" y="-10" width="66" height="20" rx="3" fill="#FFF6DC" stroke-width="3"/></g>'
             f'<text x="0" y="6" transform="translate(860 1455) rotate(-20) scale(0.8)" text-anchor="middle" font-family="DejaVu Sans" font-weight="900" font-size="15" fill="#D64545">SOS</text>')
    # Avatar (Füße bei 1550 im Avatar-Koordinatensystem)
    w.append(f'<g transform="translate(560 1452) scale(0.43) translate(-540 -1550)">{character(t, amp, blink, head_rot, bounce, angry)}</g>')
    # Vordergrund-Objekte
    w.append(f'<g transform="translate(370 1520) rotate(-8) scale(0.5)" stroke="{O}" stroke-width="8" stroke-linejoin="round">'
             f'<rect x="-100" y="-120" width="200" height="230" rx="14" fill="#2E2E38"/>'
             f'<circle cx="0" cy="-60" r="34" fill="#4A4A58"/><circle cx="0" cy="-60" r="12" fill="{O}"/>'
             f'<circle cx="0" cy="40" r="52" fill="#4A4A58"/><circle cx="0" cy="40" r="18" fill="{O}"/>'
             f'<path d="M-80 -100 l30 40 l-10 20 l26 30" fill="none" stroke="#9AA0B5" stroke-width="5"/>'
             f'<path d="M-90 -110 C-60 -80 -70 -40 -45 -20" fill="none" stroke="#2E7D3A" stroke-width="10" stroke-linecap="round"/></g>'
             f'<path d="M300 1560 C340 1540 400 1540 440 1560 L440 1590 L300 1590 Z" fill="#F4D58D"/>'
             f'<path d="M300 1560 C340 1540 400 1540 440 1560" fill="none" stroke="{O}" stroke-width="4" stroke-linecap="round"/>')
    w.append(f'<g transform="translate(760 1545) rotate(22) scale(0.55)" stroke="{O}" stroke-width="7" stroke-linejoin="round">'
             f'<rect x="-40" y="-70" width="80" height="140" rx="12" fill="#1F1F25"/><rect x="-32" y="-58" width="64" height="116" rx="6" fill="#3A4256"/>'
             f'<path d="M-24 -50 l22 30 l-8 18 l26 22 M-2 -20 l26 -14" fill="none" stroke="#C9D3EE" stroke-width="4"/></g>')
    w.append(f'<path d="M480 1575 l34 -24" stroke="{O}" stroke-width="13" stroke-linecap="round"/><path d="M480 1575 l34 -24" stroke="#3FD2FF" stroke-width="6" stroke-linecap="round"/>')
    w.append(f'<path transform="translate(640 1590) scale(0.7)" d="M0 -40 l12 26 l28 2 l-22 18 l8 28 l-26 -16 l-26 16 l8 -28 l-22 -18 l28 -2 z" fill="#FF8A5C" stroke="{O}" stroke-width="6" stroke-linejoin="round"/>')
    w.append(f'<g fill="#F7B5C8" stroke="{O}" stroke-width="3"><path d="M200 1500 c-8 -14 6 -24 14 -16 c8 -8 22 2 14 16 z"/><path d="M930 1470 c-8 -14 6 -24 14 -16 c8 -8 22 2 14 16 z"/></g>')
    w.append(crab(705 + 28 * math.sin(t * 1.6), 1470, 0.55, t))

    world = "".join(w)
    if profile:
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" width="{size}" height="{size}">{defs}'
                '<defs><linearGradient id="vsky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4FB8EC"/><stop offset="0.7" stop-color="#BFE9FA"/><stop offset="1" stop-color="#E6F7FD"/></linearGradient>'
                '<linearGradient id="vsea" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#36AACE"/><stop offset="1" stop-color="#166F96"/></linearGradient></defs>'
                f'<g transform="translate({size/2} {size/2}) scale({s}) translate({-cx} {-cy})">{world}</g></svg>')
    cam = f'translate(540 960) scale({s:.4f}) translate({-cx:.1f} {-cy:.1f})'

    hud = []
    if angry:
        k = 0.55 + 0.45 * abs(math.sin(t * 13))
        hud.append(f'<defs><radialGradient id="rv" cx="50%" cy="50%" r="75%"><stop offset="0.55" stop-color="#FF0000" stop-opacity="0"/>'
                   f'<stop offset="0.85" stop-color="#FF1A1A" stop-opacity="0.55"/><stop offset="1" stop-color="#D00000" stop-opacity="0.9"/></radialGradient></defs>'
                   f'<rect x="-20" y="-20" width="1120" height="1960" fill="url(#rv)" opacity="{k:.2f}"/>')
    hud.append(live_badge(t))
    ln = line_at(t)
    if t <= L(0)["end"] + 0.35:
        hud.append(hook_text(t))
    elif ln and t < TL["duration"] and ln is not L(0):
        hud.append(caption(ln["text"], t, ln["start"], ln["end"], ln.get("words")))
    if COMMENT_T0 <= t <= COMMENT_T0 + 3.7:
        hud.append(comment_anim(t - COMMENT_T0))

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1920" width="1080" height="1920">
{defs}
<defs>
<linearGradient id="vsky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4FB8EC"/><stop offset="0.7" stop-color="#BFE9FA"/><stop offset="1" stop-color="#E6F7FD"/></linearGradient>
<linearGradient id="vsea" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#36AACE"/><stop offset="1" stop-color="#166F96"/></linearGradient>
</defs>
<g transform="{cam}">{world}</g>
{"".join(hud)}
</svg>'''


if __name__ == "__main__":
  n = int(DURATION * FPS)
  for f in range(n):
    (OUT / f"f{f:05d}.svg").write_text(scene(f / FPS))
  print(n, "Bilder,", round(DURATION, 2), "s")
