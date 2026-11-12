"""Tag 2 – erzeugt pro Videobild eine SVG (Insel verändert sich durch die Kommentare).
Nutzt Figur, Insel-Grundlagen, Untertitel usw. aus Folge 1.
Aufruf: python3 make_video.py <svg-ordner>"""
import importlib.util, json, math, re, sys
from pathlib import Path

HERE = Path(__file__).parent
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "_frames_svg"
OUT.mkdir(parents=True, exist_ok=True)
_argv = sys.argv
sys.argv = ["make_video.py", str(OUT / "_unused")]
_spec = importlib.util.spec_from_file_location("base", HERE / "../folge01/make_video.py")
base = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(base)
sys.argv = _argv

TL = json.loads((HERE / "timeline.json").read_text())
ENV = json.loads((HERE / "envelope.json").read_text())
FPS = 25
DURATION = TL["duration"] + 0.6
SEG = {s["key"]: s for s in TL["segments"]}
EV = {k: s["event"] for k, s in SEG.items()}
O = "#2B2B2B"
ease = base.ease
FEET = 1452


def k_of(t, t0, dur):
    return min(max((t - t0) / dur, 0.0), 1.0)


def pop(t, t0, dur=0.35):
    """elastisches Erscheinen 0 -> 1 (mit Überschwingen)"""
    k = k_of(t, t0, dur)
    if k <= 0:
        return 0.0
    return 1 + 0.25 * math.sin(k * math.pi) * (1 - k) * 3 if k < 1 else 1.0


def line_of(seg, idx):
    return next(l for l in TL["lines"] if TL["segments"][l["seg"]]["key"] == seg and l["idx"] == idx)


def word_t(seg, prefix):
    for l in TL["lines"]:
        if TL["segments"][l["seg"]]["key"] == seg:
            for w in l["words"]:
                if w["w"].lower().startswith(prefix.lower()):
                    return w["start"]
    raise KeyError(prefix)


# ---------------------------------------------------------------- Kamera
def cy_for(s, dy=0):
    return FEET - (1170 - 960) / s + dy


HOOK_END = line_of("intro", 0)["end"]
CAM = {  # Zielbild pro Kommentar: (Zoom, x, y)
    "vulkan": (0.72, 720, 1120), "tsunami": (0.66, 560, 1150), "baum": (1.0, 420, cy_for(1.0)),
    "zigaretten": (0.85, 560, cy_for(0.85)), "haus": (1.1, 430, cy_for(1.1)), "toilette": (1.05, 330, cy_for(1.05)),
    "doener": (1.15, 700, cy_for(1.15)), "angel": (0.92, 840, cy_for(0.92)), "angeln": (0.88, 840, cy_for(0.88)),
    "bob": (1.0, 430, cy_for(1.0, 40)), "rucksack": (1.0, 600, cy_for(1.0, 30)), "krabbe": (1.2, 600, cy_for(1.2, 55)),
    "flugzeug": (0.68, 560, 1050), "villa": (0.5, 880, 1260), "outro": (0.56, 860, 1290),
}
KEYS = [(0.0, 1.0, 560, FEET - (1700 - 960)), (HOOK_END + 0.15, 1.0, 560, FEET - (1700 - 960)),
        (HOOK_END + 0.9, 0.92, 560, cy_for(0.92))]
for key, (s, x, y) in CAM.items():
    t0 = EV[key]
    KEYS.append((t0, *KEYS[-1][1:]))
    KEYS.append((t0 + 0.8, s, x, y))
KEYS.append((DURATION + 1, *KEYS[-1][1:]))
KEYS.sort(key=lambda k: k[0])


def shake_amount(t):
    a = 0.0
    if EV["vulkan"] <= t <= EV["vulkan"] + 3.0: a = max(a, 14 * (1 - k_of(t, EV["vulkan"] + 1.0, 2.0)) + 4)
    if EV["tsunami"] + 1.1 <= t <= EV["tsunami"] + 2.0: a = max(a, 18)
    if EV["baum"] + 0.7 <= t <= EV["baum"] + 1.0: a = max(a, 16)
    if EV["villa"] <= t <= EV["villa"] + 2.2: a = max(a, 8)
    if t <= HOOK_END: a = max(a, 18)
    return a


def camera(t):
    for (t0, s0, x0, y0), (t1, s1, x1, y1) in zip(KEYS, KEYS[1:]):
        if t0 <= t <= t1:
            k = ease((t - t0) / max(t1 - t0, 1e-6))
            s, x, y = s0 + (s1 - s0) * k, x0 + (x1 - x0) * k, y0 + (y1 - y0) * k
            break
    a = shake_amount(t)
    return s, x + a * math.sin(t * 61) / s, y + a * 0.8 * math.cos(t * 47) / s


# ---------------------------------------------------------------- Objekte
def volcano(t):
    ev = EV["vulkan"]
    if t < ev:
        return "", ""
    h = 300 * ease(k_of(t, ev, 1.0))
    x, y = 880, 1330
    land = f'<ellipse cx="{x}" cy="{y+8}" rx="{250*ease(k_of(t, ev, 0.8)):.0f}" ry="{105*ease(k_of(t, ev, 0.8)):.0f}" fill="#8D7B6A" stroke="{O}" stroke-width="5"/>'
    body = (f'<path d="M{x-210} {y} L{x-60} {y-h:.0f} L{x+60} {y-h:.0f} L{x+210} {y} Z" fill="#6E5A4C" stroke="{O}" stroke-width="6" stroke-linejoin="round"/>'
            f'<ellipse cx="{x}" cy="{y-h:.0f}" rx="60" ry="14" fill="#3A2A22" stroke="{O}" stroke-width="5"/>')
    lava = ""
    if t > ev + 1.15:
        k = ease(k_of(t, ev + 1.15, 1.2))
        for dx, dy in [(-40, 0.85), (10, 1.0), (45, 0.7)]:
            lava += (f'<path d="M{x+dx*0.3:.0f} {y-h+6:.0f} Q{x+dx:.0f} {y-h+h*0.5*k:.0f} {x+dx*2:.0f} {y-h+h*dy*k:.0f}" fill="none" '
                     f'stroke="#FF6A00" stroke-width="16" stroke-linecap="round"/>'
                     f'<path d="M{x+dx*0.3:.0f} {y-h+6:.0f} Q{x+dx:.0f} {y-h+h*0.5*k:.0f} {x+dx*2:.0f} {y-h+h*dy*k:.0f}" fill="none" '
                     f'stroke="#FFD23F" stroke-width="6" stroke-linecap="round"/>')
    fx = ""
    if ev + 1.0 <= t <= ev + 3.6:   # Eruption: Lavabrocken + Rauch
        r = __import__("random").Random(5)
        for i in range(36):
            t0 = ev + 1.0 + r.uniform(0, 1.4); dt = t - t0
            if 0 <= dt <= 1.6:
                vx, vy = r.uniform(-320, 320), r.uniform(-950, -650)
                px, py = x + vx * dt, y - h + vy * dt + 900 * dt * dt
                fx += f'<circle cx="{px:.0f}" cy="{py:.0f}" r="{r.uniform(9, 18):.0f}" fill="#FF7A1A" stroke="#7A1E00" stroke-width="3"/>'
        for i in range(10):
            t0 = ev + 1.0 + i * 0.22; dt = t - t0
            if dt >= 0:
                fx += (f'<circle cx="{x + 30*math.sin(i*2.1) + 25*dt:.0f}" cy="{y - h - 60 - 260*dt:.0f}" r="{40 + 55*dt:.0f}" '
                       f'fill="#5E5E66" opacity="{max(0, 0.85 - 0.3*dt):.2f}"/>')
    elif t > ev + 3.6:   # danach dampft er nur noch
        for i in range(3):
            ph = (t * 0.35 + i / 3) % 1
            fx += f'<circle cx="{x + 20*math.sin(i*2+t):.0f}" cy="{y - h - 30 - 160*ph:.0f}" r="{22 + 30*ph:.0f}" fill="#9A9AA2" opacity="{0.6*(1-ph):.2f}"/>'
    return land + body + lava, fx


def tsunami_wave(t):
    ev = EV["tsunami"] + 0.25
    k = k_of(t, ev, 1.5)
    if not (0 < k < 1):
        return ""
    X = 1700 - 2900 * ease(k)
    H = 1050 * math.sin(math.pi * min(k * 1.3, 1)) + 150
    top = 1720 - H
    return (f'<path d="M{X:.0f} 1760 C{X-60:.0f} {top+300:.0f} {X+40:.0f} {top:.0f} {X+260:.0f} {top:.0f} '
            f'C{X+420:.0f} {top:.0f} {X+430:.0f} {top+140:.0f} {X+330:.0f} {top+170:.0f} '
            f'C{X+500:.0f} {top+260:.0f} {X+900:.0f} {top+380:.0f} {X+1700:.0f} {top+420:.0f} L{X+1700:.0f} 1900 L{X:.0f} 1900 Z" '
            f'fill="#2E8FC0" stroke="{O}" stroke-width="7" stroke-linejoin="round"/>'
            f'<path d="M{X+60:.0f} {top+120:.0f} C{X+120:.0f} {top+30:.0f} {X+250:.0f} {top+20:.0f} {X+330:.0f} {top+90:.0f}" '
            f'fill="none" stroke="#FFFFFF" stroke-width="22" stroke-linecap="round"/>'
            + "".join(f'<circle cx="{X+40+60*i:.0f}" cy="{top+40-20*math.sin(i+t*9):.0f}" r="{14+6*(i%3)}" fill="#FFFFFF"/>' for i in range(6)))


def fallen_palm(t):
    ev = EV["baum"]
    k = k_of(t, ev + 0.05, 0.7)
    ang = -98 * (k ** 2.2)
    if k >= 1:
        ang = -98 + 5 * math.exp(-(t - ev - 0.75) * 6) * math.sin((t - ev) * 30)
    return f'<g transform="rotate({ang:.1f} 230 1420)">{base.palm(230, 1420, t if k == 0 else 0)}</g>'


CIGS = []
_r = __import__("random").Random(42)
for i in range(90):
    x = _r.uniform(-150, 1230); land_y = _r.uniform(1300, 1600)
    on_island = ((x - 540) / 485) ** 2 + ((land_y - 1430) / 192) ** 2 < 0.85
    if not on_island:
        land_y = _r.uniform(1700, 1900)
    CIGS.append((x, _r.uniform(-500, -100), land_y, _r.uniform(0, 1.7), _r.uniform(-180, 180), on_island))


def cigarettes(t):
    ev = EV["zigaretten"] + 0.1
    if t < ev:
        return ""
    out = ""
    for x, y0, land, delay, rot, on_isl in CIGS:
        dt = t - ev - delay
        if dt < 0:
            continue
        y = y0 + 1400 * dt
        if y >= land:
            if not on_isl:
                continue
            y, r = land, rot * 0.3
        else:
            r = rot + 360 * dt
        out += (f'<g transform="translate({x:.0f} {y:.0f}) rotate({r:.0f})"><rect x="-18" y="-4" width="36" height="8" rx="2" fill="#FFFFFF" stroke="{O}" stroke-width="2"/>'
                f'<rect x="8" y="-4" width="10" height="8" fill="#E39A4A"/></g>')
    return out


def hut(s):
    return (f'<g transform="translate(300 1300) scale({s:.3f})" stroke="{O}" stroke-width="6" stroke-linejoin="round">'
            '<rect x="-90" y="-110" width="180" height="120" fill="#C8955A"/>'
            '<path d="M-90 -80 h180 M-90 -50 h180 M-90 -20 h180" stroke="#9C6B3A" stroke-width="4"/>'
            '<path d="M-125 -105 L0 -195 L125 -105 Z" fill="#D8B05A"/>'
            '<path d="M-100 -115 l20 12 M-60 -140 l18 12 M-20 -165 l18 12" stroke="#A8823A" stroke-width="4"/>'
            '<rect x="-25" y="-60" width="50" height="70" fill="#7A4A26"/><circle cx="14" cy="-24" r="4" fill="#FFD23F"/>'
            '<rect x="40" y="-85" width="36" height="30" fill="#BFE9FA"/></g>')


def toilet(s):
    return (f'<g transform="translate(150 1455) scale({s:.3f})" stroke="{O}" stroke-width="5" stroke-linejoin="round">'
            '<rect x="-30" y="-120" width="60" height="55" rx="8" fill="#FFFFFF"/>'
            '<path d="M-42 -62 h84 q0 40 -30 52 v12 h-24 v-12 q-30 -12 -30 -52 Z" fill="#FFFFFF"/>'
            '<ellipse cx="0" cy="-62" rx="42" ry="10" fill="#E8F4FA"/><rect x="18" y="-110" width="10" height="6" fill="#B0B8C0"/></g>')


def doener(s, t):
    rot = (t * 120) % 360
    return (f'<g transform="translate(800 1480) scale({s:.3f})" stroke="{O}" stroke-width="5" stroke-linejoin="round">'
            '<rect x="-110" y="-120" width="220" height="120" fill="#F7E7C6"/>'
            '<path d="M-130 -120 L130 -120 L115 -165 L-115 -165 Z" fill="#E8102E"/>'
            '<path d="M-90 -165 L-80 -120 M-40 -165 L-35 -120 M10 -165 L10 -120 M60 -165 L55 -120" stroke="#FFFFFF" stroke-width="10"/>'
            '<rect x="-85" y="-215" width="170" height="48" rx="10" fill="#FFD23F"/>'
            '<text x="0" y="-180" text-anchor="middle" font-family="DejaVu Sans, sans-serif" font-weight="900" font-size="34" fill="#C2001A" stroke="none">DÖNER</text>'
            f'<g transform="translate(-45 -60)"><rect x="-4" y="-55" width="8" height="110" fill="#9AA0A8"/>'
            f'<path d="M-28 -45 L28 -45 L18 45 L-18 45 Z" fill="#A0602A"/>'
            f'<path d="M-24 -20 L24 -20 M-21 5 L21 5 M-19 28 L19 28" stroke="#6A3A14" stroke-width="4" transform="translate({6*math.sin(math.radians(rot)):.1f} 0)"/></g>'
            '<rect x="10" y="-80" width="85" height="50" fill="#FFFFFF"/><text x="52" y="-48" text-anchor="middle" font-family="DejaVu Sans" font-size="20" font-weight="700" fill="#333" stroke="none">5 €</text>'
            '</g>')


def jetty(s):
    return (f'<g transform="translate(985 1440) scale({s:.3f})" stroke="{O}" stroke-width="5" stroke-linejoin="round">'
            '<path d="M0 -20 L280 20 L280 60 L0 20 Z" fill="#B88550"/>'
            '<path d="M40 -14 l0 40 M90 -7 l0 40 M140 0 l0 40 M190 7 l0 40 M240 14 l0 40" stroke="#8A5A2E" stroke-width="4"/>'
            '<path d="M60 20 v60 M200 40 v60 M270 55 v55" stroke="#6A4420" stroke-width="10"/>'
            '<rect x="190" y="-30" width="50" height="40" rx="6" fill="#4C8DDB"/><path d="M190 -30 q25 -25 50 0" fill="none"/>'
            '<path d="M110 -40 L120 10 M130 -40 L120 10" stroke="#7A4A26" stroke-width="6"/>'
            '<path d="M120 -40 L60 -140" stroke="#3A3A3A" stroke-width="5"/></g>')


def turtle(x, y, s=1.0, fish=True, t=0):
    flap = 8 * math.sin(t * 8)
    return (f'<g transform="translate({x:.0f} {y:.0f}) scale({s})" stroke="{O}" stroke-width="5" stroke-linejoin="round">'
            f'<ellipse cx="-50" cy="{12+flap:.0f}" rx="22" ry="12" fill="#7DBB5A"/><ellipse cx="45" cy="{12-flap:.0f}" rx="22" ry="12" fill="#7DBB5A"/>'
            '<ellipse cx="0" cy="0" rx="60" ry="38" fill="#4E8B3A"/>'
            '<path d="M-35 -10 L-12 -25 L12 -25 L35 -10 L12 8 L-12 8 Z" fill="#6FA84E" stroke-width="3"/>'
            '<ellipse cx="78" cy="-6" rx="26" ry="20" fill="#7DBB5A"/><circle cx="86" cy="-12" r="4" fill="#111" stroke="none"/>'
            '<path d="M80 4 q8 4 16 0" fill="none" stroke-width="3"/>'
            + ('<g transform="translate(108 2) rotate(-10)"><path d="M0 0 Q20 -14 40 0 Q20 14 0 0 Z" fill="#FF9F43"/><path d="M40 0 l14 -10 v20 z" fill="#FF9F43"/></g>' if fish else "")
            + '<text x="-8" y="-46" text-anchor="middle" font-family="DejaVu Sans" font-weight="900" font-size="24" fill="#FFFFFF" stroke="#111" stroke-width="5" paint-order="stroke">BOB</text></g>')


ITEMS = {  # Wortanfang -> (x, y, Zeichnung)
    "wasser": (600, 1525, '<rect x="-12" y="-40" width="24" height="44" rx="6" fill="#5BB8F5"/><rect x="-6" y="-50" width="12" height="10" fill="#2B5D9A"/>'),
    "lampe": (690, 1533, '<rect x="-30" y="-12" width="44" height="24" rx="5" fill="#FFD23F"/><path d="M14 -16 L34 -24 L34 24 L14 16 Z" fill="#E0E0E0"/>'),
    "kompass": (770, 1511, '<circle r="22" fill="#F5F0E0"/><path d="M0 -16 L6 0 L0 16 L-6 0 Z" fill="#E8102E" stroke-width="2"/>'),
    "zelt": (420, 1335, '<path d="M-90 30 L0 -80 L90 30 Z" fill="#4CAF50"/><path d="M0 -80 L0 30 M-20 30 L0 -10 L20 30" fill="#2E7D32"/>'),
    "seil": (520, 1533, '<ellipse rx="30" ry="14" fill="#C9A26A"/><ellipse rx="18" ry="8" fill="none"/><ellipse rx="8" ry="3" fill="none"/>'),
    "erste": (860, 1489, '<rect x="-28" y="-22" width="56" height="44" rx="6" fill="#FFFFFF"/><path d="M-6 -14 h12 v8 h8 v12 h-8 v8 h-12 v-8 h-8 v-12 h8 Z" fill="#E8102E" stroke="none"/>'),
    "streichhölzer": (450, 1515, '<rect x="-24" y="-14" width="48" height="28" rx="3" fill="#E8102E"/><rect x="-24" y="-14" width="20" height="28" fill="#FFD23F"/>'),
    "messer": (920, 1533, '<path d="M-30 0 L16 -6 L30 0 L16 6 Z" fill="#D8DEE6"/><rect x="-46" y="-6" width="18" height="12" rx="3" fill="#7A4A26"/>'),
}


def backpack(t):
    ev = EV["rucksack"]
    if t < ev:
        return ""
    k = k_of(t, ev, 0.55)
    y = -300 + (1530 + 300) * (k ** 2)
    out = (f'<g transform="translate(655 {y:.0f})" stroke="{O}" stroke-width="5" stroke-linejoin="round">'
           '<rect x="-45" y="-80" width="90" height="100" rx="20" fill="#E8742E"/><rect x="-32" y="-30" width="64" height="40" rx="8" fill="#C95A1A"/>'
           '<path d="M-30 -80 q30 -30 60 0" fill="none" stroke-width="7"/></g>')
    for word, (x, yy, svg) in ITEMS.items():
        ws = WORD_ITEMS[word]
        if t >= ws:
            sc = pop(t, ws, 0.3)
            fly = 1 - ease(k_of(t, ws, 0.3))
            px, py = x + (655 - x) * fly, yy + (1480 - yy) * fly - 120 * math.sin(math.pi * (1 - fly))
            out += f'<g transform="translate({px:.0f} {py:.0f}) scale({sc:.2f})" stroke="{O}" stroke-width="4" stroke-linejoin="round">{svg}</g>'
    return out


WORD_ITEMS = {w: word_t("rucksack", w if w != "streichhölzer" else "streich") for w in ITEMS}


def plane_and_crate(t):
    ev = EV["flugzeug"]
    out = ""
    k = k_of(t, ev, 3.4)
    if 0 < k < 1:
        x = 1600 - 2300 * k
        out += (f'<g transform="translate({x:.0f} 520)" stroke="{O}" stroke-width="5" stroke-linejoin="round">'
                '<path d="M-110 0 Q-110 -26 -70 -26 L90 -20 Q120 -14 120 0 Q120 14 90 18 L-70 22 Q-110 22 -110 0 Z" fill="#FFFFFF"/>'
                '<path d="M-20 -6 L40 -80 L60 -80 L30 -6 Z M-20 8 L40 70 L60 70 L30 8 Z" fill="#E8102E"/>'
                '<path d="M80 -20 L105 -60 L118 -60 L112 -14 Z" fill="#E8102E"/>'
                '<circle cx="-70" cy="-6" r="7" fill="#7EC8F5"/><circle cx="-48" cy="-6" r="7" fill="#7EC8F5"/><circle cx="-26" cy="-6" r="7" fill="#7EC8F5"/>'
                f'<ellipse cx="-118" cy="0" rx="4" ry="{28*abs(math.sin(t*40)):.0f}" fill="#555"/></g>')
    drop0 = ev + 1.0
    if t >= drop0:
        kk = k_of(t, drop0, 1.6)
        cx, cy = 650 + (480 - 650) * kk, 560 + (1530 - 560) * ease(kk)
        if kk < 1:
            out += (f'<g transform="translate({cx:.0f} {cy-150:.0f})" stroke="{O}" stroke-width="4">'
                    '<path d="M-80 0 Q0 -90 80 0 Z" fill="#FFFFFF"/><path d="M-80 0 Q-40 -20 0 0 Q40 -20 80 0" fill="#E8102E"/>'
                    '<path d="M-78 0 L-28 120 M78 0 L28 120 M0 0 L0 120" fill="none" stroke-width="2"/></g>')
        out += (f'<g transform="translate({cx:.0f} {cy:.0f})" stroke="{O}" stroke-width="5" stroke-linejoin="round">'
                '<rect x="-45" y="-60" width="90" height="62" fill="#C8955A"/><path d="M-45 -60 L45 2 M45 -60 L-45 2" stroke="#9C6B3A" stroke-width="4"/>'
                '<rect x="-38" y="-46" width="76" height="30" fill="#FFFFFF" stroke-width="3"/>'
                '<text x="0" y="-23" text-anchor="middle" font-family="DejaVu Sans" font-weight="900" font-size="20" fill="#C2001A" stroke="none">ESSEN</text></g>')
    return out


def big_island(t):
    ev = EV["villa"]
    k = ease(k_of(t, ev, 2.0))
    if k <= 0:
        return "", ""
    cx, cy, rx, ry = 540 + 380 * k, 1430 - 30 * k, 485 + 760 * k, 192 + 330 * k
    land = (f'<ellipse cx="{cx:.0f}" cy="{cy+12:.0f}" rx="{rx+60:.0f}" ry="{ry+45:.0f}" fill="#7FDCDC" opacity="0.75"/>'
            f'<ellipse cx="{cx:.0f}" cy="{cy:.0f}" rx="{rx:.0f}" ry="{ry:.0f}" fill="#F4D58D" stroke="{O}" stroke-width="7"/>'
            f'<ellipse cx="{cx+120*k:.0f}" cy="{cy-120*k:.0f}" rx="{rx*0.55:.0f}" ry="{ry*0.45:.0f}" fill="#8CCB6A" opacity="{k:.2f}"/>')
    extra = ""
    s1 = pop(t, ev + 1.0, 0.45)
    if s1 > 0:   # Villa mit Pool
        extra += (f'<g transform="translate(1330 1120) scale({s1:.3f})" stroke="{O}" stroke-width="7" stroke-linejoin="round">'
                  '<rect x="-260" y="-150" width="520" height="160" fill="#FAFAFA"/><rect x="-200" y="-260" width="340" height="115" fill="#FFFFFF"/>'
                  '<rect x="-280" y="-160" width="560" height="18" fill="#3A3A44"/><rect x="-215" y="-272" width="370" height="16" fill="#3A3A44"/>'
                  '<rect x="-230" y="-120" width="120" height="100" fill="#8FD3F4"/><rect x="-80" y="-120" width="120" height="100" fill="#8FD3F4"/>'
                  '<rect x="70" y="-120" width="80" height="130" fill="#7A4A26"/><rect x="-170" y="-235" width="250" height="70" fill="#8FD3F4"/>'
                  '<rect x="-300" y="30" width="360" height="90" rx="20" fill="#35C2E8"/><path d="M-280 60 q30 -12 60 0 q30 12 60 0 q30 -12 60 0" fill="none" stroke="#FFFFFF" stroke-width="5"/>'
                  '<text x="10" y="-290" text-anchor="middle" font-family="DejaVu Sans" font-weight="900" font-size="44" fill="#FFD23F" stroke="#111" stroke-width="8" paint-order="stroke">VILLA CLARA</text></g>')
    s2 = pop(t, ev + 1.4, 0.45)
    if s2 > 0:   # Hafen + Boot
        bob_ = 8 * math.sin(t * 2.2)
        extra += (f'<g transform="translate(1650 1690) scale({s2:.3f})" stroke="{O}" stroke-width="6" stroke-linejoin="round">'
                  '<path d="M-60 -40 L320 60 L320 110 L-60 10 Z" fill="#B88550"/>'
                  '<path d="M0 0 v70 M110 30 v70 M220 60 v70 M310 80 v60" stroke="#6A4420" stroke-width="12"/>'
                  f'<g transform="translate(260 {150+bob_:.0f})"><path d="M-130 0 L130 0 L100 55 L-100 55 Z" fill="#FFFFFF"/>'
                  '<rect x="-50" y="-55" width="110" height="55" fill="#FFFFFF"/><rect x="-35" y="-45" width="80" height="25" fill="#8FD3F4"/>'
                  '<path d="M-100 30 h200" stroke="#2E8FC0" stroke-width="8"/></g>'
                  '<text x="120" y="-40" text-anchor="middle" font-family="DejaVu Sans" font-weight="900" font-size="40" fill="#FFFFFF" stroke="#111" stroke-width="8" paint-order="stroke">HAFEN</text></g>')
    s3 = pop(t, ev + 1.7, 0.4)
    if s3 > 0:
        for px, py in [(1080, 1240), (1620, 1260), (1880, 1480)]:
            extra += f'<g transform="translate({px} {py}) scale({0.55*s3:.3f}) translate(-230 -1420)">{base.palm(230, 1420, t + px)}</g>'
    sparkle = ""
    if ev + 0.8 <= t <= ev + 3.2:
        for i in range(14):
            ph = (t * 1.3 + i / 14) % 1
            sx, sy = 700 + (i * 137) % 1400, 900 + (i * 211) % 900
            sparkle += f'<path transform="translate({sx} {sy - 80*ph:.0f}) scale({1.4*(1-ph):.2f})" d="M0 -18 L5 -5 L18 0 L5 5 L0 18 L-5 5 L-18 0 L-5 -5 Z" fill="#FFF3A0" stroke="#111" stroke-width="2"/>'
    return land, extra + sparkle


# ---------------------------------------------------------------- Clara
SNEAKER_R = ('<g transform="translate(0 -60) translate(1118 0) scale(-1 1)" stroke="#2B2B2B" stroke-width="6" stroke-linejoin="round">'
             '<path d="M494 1484 L530 1484 L534 1520 L444 1525 C434 1525 436 1504 452 1500 Z" fill="#FFFFFF"/>'
             '<rect x="436" y="1522" width="102" height="26" rx="8" fill="#39FF6A"/>'
             '<path d="M492 1494 l20 0 M488 1506 l24 0" fill="none" stroke-width="4"/></g>')
SHOE_ON = word_t("angeln", "schuh") + 1.1


def clara(t, amp, blink, head_rot, bounce, angry):
    svg = base.character(t, amp, blink, head_rot, bounce, angry)
    if t >= SHOE_ON:   # zweiter Sneaker wieder am Fuß
        svg = re.sub(r'<!-- rechter Fuß: barfuß -->\s*<g[^>]*>.*?</g>', SNEAKER_R, svg, count=1, flags=re.S)
    return svg


def held_items(t, hand):
    """Dinge in Claras Hand: Angel, Kokosnuss (Welt-Koordinaten)."""
    hx, hy = hand
    out = ""
    a0, a_end = EV["angeln"], SEG["angeln"]["end"] + 0.3
    if a0 <= t <= a_end:
        tip = (900, 960)
        wx, wy = 1230, 1560
        out += f'<path d="M{hx} {hy} L{tip[0]} {tip[1]}" stroke="#3A3A3A" stroke-width="7" stroke-linecap="round"/>'
        ts = word_t("angeln", "schuh") - 0.6
        if t < ts:
            out += f'<path d="M{tip[0]} {tip[1]} Q{(tip[0]+wx)/2} {wy-200} {wx} {wy+6*math.sin(t*5):.0f}" fill="none" stroke="#DDD" stroke-width="2.5"/>'
        else:
            k = ease(k_of(t, ts, 0.9))
            sx, sy = wx + (tip[0] + 40 - wx) * k, wy + (tip[1] + 60 - wy) * k
            if t < SHOE_ON:
                out += (f'<path d="M{tip[0]} {tip[1]} L{sx:.0f} {sy:.0f}" stroke="#DDD" stroke-width="2.5"/>'
                        f'<g transform="translate({sx:.0f} {sy:.0f}) rotate(-20)" stroke="{O}" stroke-width="5"><path d="M-30 -10 L10 -10 L12 16 L-56 20 C-64 20 -62 4 -48 2 Z" fill="#FFFFFF"/>'
                        f'<rect x="-62" y="16" width="84" height="16" rx="6" fill="#39FF6A"/></g>')
    if EV["krabbe"] <= t <= SEG["krabbe"]["end"] + 0.3:
        out += (f'<g transform="translate({hx+8} {hy-30})" stroke="{O}" stroke-width="4">'
                '<circle r="26" fill="#7A4A26"/><path d="M6 -24 L26 -80" stroke="#FFFFFF" stroke-width="7"/>'
                '<path d="M8 -32 l7 -3 M13 -48 l7 -3 M18 -64 l7 -3" stroke="#E85D5D" stroke-width="5"/></g>')
    return out


# ---------------------------------------------------------------- Einblendungen
def live_badge(t):
    s = base.live_badge(t)
    return s.replace("TAG 1 · DIE INSEL", "TAG 2 · DIE INSEL")


def sticker(seg, t):
    """„Antwort auf Kommentar“-Sticker oben (wie bei TikTok)."""
    t0, t1 = seg["event"] - 0.3, seg["end"] + 0.25
    if not (t0 <= t <= t1):
        return ""
    sc = pop(t, t0, 0.3) * (1 - ease(k_of(t, t1 - 0.2, 0.2)))
    F = 'font-family="DejaVu Sans, Noto Color Emoji, Noto Sans CJK JP, sans-serif"'
    lines = base._wrap(seg["comment"], 40)
    if len(lines) > 2:
        lines = lines[:2]; lines[1] = lines[1].rstrip(" …") + " …"
    h = 96 + 44 * len(lines)
    user = seg["user"]
    out = (f'<defs><filter id="sk" x="-10%" y="-20%" width="120%" height="150%"><feDropShadow dx="0" dy="8" stdDeviation="8" flood-color="#000" flood-opacity="0.35"/></filter></defs>'
           f'<g transform="translate(540 {330 + h/2:.0f}) scale({sc:.3f}) translate(-450 {-h/2:.0f})" filter="url(#sk)">'
           f'<rect x="0" y="0" width="900" height="{h}" rx="26" fill="#FFFFFF"/>'
           f'<circle cx="54" cy="52" r="30" fill="#{(sum(map(ord, user)) * 2654435761) % 0xAAAAAA + 0x333333:06X}"/>'
           f'<circle cx="54" cy="44" r="11" fill="#FFFFFF"/><path d="M34 70 Q54 48 74 70 Z" fill="#FFFFFF"/>'
           f'<text x="100" y="44" font-size="25" fill="#8A8B91" {F} font-weight="600">Antwort auf den Kommentar von {user}</text>')
    for k, ln in enumerate(lines):
        out += f'<text x="100" y="{92 + k*44}" font-size="31" fill="#161823" {F} font-weight="700">{ln}</text>'
    return out + "</g>"


HOOK_LINES = ["IHR HABT", "ECHT", "KOMMENTIERT?!"]


def _hook_layout():
    from PIL import ImageFont
    x0, x1, y0, y1 = base.HOOK_BOX
    sizes = [min(100 * (x1 - x0) / ImageFont.truetype(base._FONT, 100).getlength(ln), 190) for ln in HOOK_LINES]
    caps = [0.73 * fs for fs in sizes]
    gap = 55
    ys, y = [], y0 + ((y1 - y0) - sum(caps) - gap * (len(caps) - 1)) / 2
    for c in caps:
        y += c; ys.append(y); y += gap
    return list(zip(HOOK_LINES, sizes, ys))


def hook(t):
    old = base.HOOK_LINES[:]
    base.HOOK_LINES[:] = HOOK_LINES
    base.HOOK = _hook_layout()
    l0 = line_of("intro", 0)
    base.L = lambda i: l0
    s = base.hook_text(t)
    base.HOOK_LINES[:] = old
    return s


# ---------------------------------------------------------------- Szene
def line_at(t):
    for l in TL["lines"]:
        if l["start"] - 0.05 <= t <= l["end"] + 0.25:
            return l
    return None


def scene(t):
    i = min(int(t * FPS), len(ENV) - 1)
    amp = ENV[i] if t < TL["duration"] else 0.0
    angry = t <= HOOK_END + 0.2
    blink = (t % 3.3) < 0.12 and not angry
    head_rot = 1.5 * math.sin(t * 22) if angry else 2.0 * math.sin(t * 1.7) + 3 * amp * math.sin(t * 9)
    bounce = 10 * amp + 3 * math.sin(t * 2.1)
    s, cx, cy = camera(t)

    w = ['<rect x="-1500" y="-1500" width="4200" height="2260" fill="url(#vsky)"/>']
    if EV["vulkan"] + 1.0 <= t <= EV["vulkan"] + 4.0:   # orangefarbener Himmel beim Ausbruch
        w.append(f'<rect x="-1500" y="-1500" width="4200" height="2260" fill="#FF7A1A" opacity="{0.28*math.sin(math.pi*k_of(t, EV["vulkan"]+1.0, 3.0)):.2f}"/>')
    w.append(f'<g transform="rotate({t*8:.1f} 860 250)" stroke="#FFE27A" stroke-width="10" stroke-linecap="round">' +
             "".join(f'<path d="M860 132 v-34" transform="rotate({k*30} 860 250)"/>' for k in range(12)) + "</g>")
    w.append(f'<circle cx="860" cy="250" r="88" fill="#FFD23F" stroke="{O}" stroke-width="6"/>')
    for bx, by, sc, sp in [(120, 470, 1.0, 9), (700, 560, 0.8, 6), (420, 320, 0.6, 12), (1500, 420, 1.2, 7), (-400, 520, 1.0, 8)]:
        x = (bx + t * sp + 600) % 2600 - 900
        w.append(f'<g transform="translate({x:.0f} {by}) scale({sc})" fill="#FFFFFF" opacity="0.92"><ellipse rx="95" ry="26"/>'
                 '<ellipse cx="45" cy="-20" rx="55" ry="30"/><ellipse cx="-35" cy="-12" rx="40" ry="22"/></g>')
    w.append(base.gull((t * 85) % 1500 - 200, 380 + 20 * math.sin(t), t))
    w.append(base.gull((t * 85 + 90) % 1500 - 200, 420 + 20 * math.sin(t + 1), t + 0.4, 0.8))
    w.append('<rect x="-1500" y="760" width="4200" height="3000" fill="url(#vsea)"/>')
    w.append(f'<path d="M-1500 760 H2700" stroke="{O}" stroke-width="4"/>')
    for k, y in enumerate(range(800, 3200, 70)):
        sp = 260 + (k % 3) * 40
        off = (t * (18 + k * 3) + k * 83) % sp
        d = "".join(f"M{-1500 + off + j*sp:.0f} {y} q18 -10 36 0 q18 10 36 0 " for j in range(int(4200 / sp) + 2))
        w.append(f'<path d="{d}" fill="none" stroke="#BFEFFF" stroke-width="{3 + min(k, 12)*0.15:.1f}" stroke-linecap="round" opacity="0.85"/>')
    fx = (t * 95) % 1700 - 300
    w.append(f'<g transform="translate({fx:.0f} {1820 + 6*math.sin(t*3):.0f})"><path d="M-30 0 Q0 -10 10 -70 Q28 -30 50 0 Z" fill="#5D6D7E" stroke="{O}" stroke-width="5" stroke-linejoin="round"/></g>')
    bob_ = 8 * math.sin(t * 2.4)
    w.append(f'<g transform="translate(-150 {1745-bob_:.1f}) rotate({3*math.sin(t*1.8):.1f})" stroke="{O}" stroke-width="6" stroke-linejoin="round" stroke-linecap="round">'
             f'<ellipse rx="92" ry="28" fill="#FF8FC2"/><ellipse cy="-4" rx="48" ry="11" fill="#2A8DB5"/></g>')

    land, extra = big_island(t)
    w.append(land)
    k_big = ease(k_of(t, EV["villa"], 2.0))
    foam = (t * 40) % 60
    if k_big < 0.3:
        w.append(f'<ellipse cx="540" cy="1440" rx="545" ry="235" fill="#7FDCDC" opacity="{0.75*(1-k_big/0.3):.2f}"/>')
        w.append(f'<ellipse cx="540" cy="1440" rx="500" ry="205" fill="none" stroke="#FFFFFF" stroke-width="10" stroke-dasharray="40 20" stroke-dashoffset="{foam:.0f}" opacity="{0.9*(1-k_big/0.3):.2f}"/>')
    w.append(f'<ellipse cx="540" cy="1430" rx="485" ry="192" fill="#F4D58D" stroke="{O}" stroke-width="{6*(1-k_big):.1f}"/>')
    v_land, v_fx = volcano(t)
    w.append(v_land)
    w.append(extra)
    # Strand-Details
    w.append('<g fill="#D9B46A">' + "".join(f'<circle cx="{x}" cy="{y}" r="5"/>' for x, y in [(180, 1440), (260, 1530), (700, 1580), (420, 1350), (620, 1330), (320, 1600)]) + "</g>")
    # Hintergrund-Objekte
    w.append(hut(pop(t, EV["haus"] + 0.25)) if t >= EV["haus"] + 0.25 else "")
    if t >= WORD_ITEMS["zelt"]:
        x, y, svgz = ITEMS["zelt"]
        w.append(f'<g transform="translate({x} {y}) scale({pop(t, WORD_ITEMS["zelt"], 0.3):.2f})" stroke="{O}" stroke-width="5" stroke-linejoin="round">{svgz}</g>')
    w.append(fallen_palm(t))
    w.append(f'<g stroke="{O}" stroke-width="5"><circle cx="268" cy="1430" r="20" fill="#7A4A26"/><circle cx="300" cy="1440" r="17" fill="#7A4A26"/></g>')
    w.append(toilet(pop(t, EV["toilette"] + 0.2)) if t >= EV["toilette"] + 0.2 else "")
    w.append(doener(pop(t, EV["doener"] + 0.25), t) if t >= EV["doener"] + 0.25 else "")
    w.append(jetty(pop(t, EV["angel"] + 0.2)) if t >= EV["angel"] + 0.2 else "")
    washed = t >= EV["tsunami"] + 1.2
    if not washed:   # Flaschenpost, Bassbox und Handy – werden vom Tsunami weggespült
        w.append(f'<g transform="translate(860 1455) rotate(-20) scale(0.8)" stroke="{O}" stroke-width="5"><path d="M-50 -20 h90 q20 0 20 20 q0 20 -20 20 h-90 q-14 0 -14 -20 q0 -20 14 -20 z" fill="#9FE3C9"/>'
                 f'<rect x="58" y="-10" width="34" height="20" rx="4" fill="#9FE3C9"/></g>')
    # Clara
    hand = (581, 1177)
    w.append(f'<g transform="translate(560 1452) scale(0.43) translate(-540 -1550)">{clara(t, amp, blink, head_rot, bounce, angry)}</g>')
    w.append(held_items(t, hand))
    if EV["tsunami"] + 1.4 <= t <= EV["tsunami"] + 5.0:   # nass: Tropfen
        for j in range(6):
            ph = (t * 1.8 + j / 6) % 1
            w.append(f'<path transform="translate({500 + j*24} {1000 + 260*ph:.0f})" d="M0 0 q-7 12 0 16 q7 -4 0 -16z" fill="#6FC3F5" stroke="{O}" stroke-width="2" opacity="{1-ph:.2f}"/>')
    # Vordergrund
    if not washed:
        w.append(f'<g transform="translate(370 1520) rotate(-8) scale(0.5)" stroke="{O}" stroke-width="8"><rect x="-100" y="-120" width="200" height="230" rx="14" fill="#2E2E38"/>'
                 f'<circle cx="0" cy="-60" r="34" fill="#4A4A58"/><circle cx="0" cy="40" r="52" fill="#4A4A58"/></g>'
                 f'<g transform="translate(760 1545) rotate(22) scale(0.55)" stroke="{O}" stroke-width="7"><rect x="-40" y="-70" width="80" height="140" rx="12" fill="#1F1F25"/>'
                 f'<rect x="-32" y="-58" width="64" height="116" rx="6" fill="#3A4256"/></g>')
    w.append(cigarettes(t))
    if t >= EV["bob"]:   # Bob kommt angeschwommen
        k = ease(k_of(t, EV["bob"], 1.2))
        w.append(turtle(-150 + (300 + 150) * k, 1700 - 210 * k, 0.9, fish=t < SEG["bob"]["end"] + 2, t=t))
        if EV["bob"] + 1.0 <= t <= SEG["bob"]["end"] + 0.3:
            w.append(f'<g transform="translate(300 1385)" font-family="DejaVu Sans, Noto Color Emoji" font-weight="900" text-anchor="middle">'
                     f'<rect x="-150" y="-62" width="300" height="76" rx="38" fill="#FFFFFF" stroke="{O}" stroke-width="5"/>'
                     f'<text y="-10" font-size="38" fill="#161823">2× ☀️🐟 🌙🐟</text></g>')
    w.append(backpack(t))
    w.append(plane_and_crate(t))
    crab_x, crab_y = 690 + 28 * math.sin(t * 1.6), 1480
    if EV["krabbe"] <= t <= SEG["krabbe"]["end"] + 1:
        crab_x, crab_y = 650, 1440
        for j in range(3):
            ph = (t * 1.2 + j / 3) % 1
            w.append(f'<text x="{630 + 25*j}" y="{1390 - 90*ph:.0f}" font-size="34" font-family="Noto Color Emoji" opacity="{1-ph:.2f}">❤️</text>')
    w.append(base.crab(crab_x, crab_y, 0.55, t))
    w.append(v_fx)
    w.append(tsunami_wave(t))
    world = "".join(w)

    hud = []
    if t <= HOOK_END + 0.2:
        k = 0.55 + 0.45 * abs(math.sin(t * 13))
        hud.append(f'<defs><radialGradient id="rv" cx="50%" cy="50%" r="75%"><stop offset="0.55" stop-color="#FF0000" stop-opacity="0"/>'
                   f'<stop offset="0.85" stop-color="#FF1A1A" stop-opacity="0.55"/><stop offset="1" stop-color="#D00000" stop-opacity="0.9"/></radialGradient></defs>'
                   f'<rect x="-20" y="-20" width="1120" height="1960" fill="url(#rv)" opacity="{k:.2f}"/>')
    hud.append(live_badge(t))
    if t <= HOOK_END + 0.35:
        hud.append(hook(t))
    for seg in TL["segments"]:
        if seg["comment"]:
            hud.append(sticker(seg, t))
    ln = line_at(t)
    if ln and t > HOOK_END + 0.3 and t < TL["duration"]:
        hud.append(base.caption(ln["text"], t, ln["start"], ln["end"], ln.get("words")))

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1920" width="1080" height="1920">
{base.defs}
<defs>
<linearGradient id="vsky" x1="0" x2="0" gradientUnits="userSpaceOnUse" y1="-1500" y2="760"><stop offset="0" stop-color="#2E9BE0"/><stop offset="0.75" stop-color="#BFE9FA"/><stop offset="1" stop-color="#E6F7FD"/></linearGradient>
<linearGradient id="vsea" x1="0" x2="0" gradientUnits="userSpaceOnUse" y1="760" y2="3000"><stop offset="0" stop-color="#36AACE"/><stop offset="1" stop-color="#0F5F86"/></linearGradient>
</defs>
<g transform="translate(540 960) scale({s:.4f}) translate({-cx:.1f} {-cy:.1f})">{world}</g>
{"".join(hud)}
</svg>'''


if __name__ == "__main__":
    n = int(DURATION * FPS)
    for f in range(n):
        (OUT / f"f{f:05d}.svg").write_text(scene(f / FPS))
    print(n, "Bilder,", round(DURATION, 2), "s")
