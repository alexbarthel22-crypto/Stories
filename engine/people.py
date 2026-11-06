"""Detailed, naturally moving flat-vector characters (v2).

Skeleton with elbows and knees, 2-bone IK for hands, procedural breathing / weight shift / head bob,
walk cycle with knee bend (lowest foot stays on the ground), expressive faces and detailed clothes/hair.

    g = draw_char(cv, x, y, look, h, f=1, t=t, arm_f=("ik", (tx, ty)), talk=0.6, mood="smile")
returns geometry (head centre, radius, eye line, hands, chest, ...) for props.
"""
import math
from toolkit import hexc, mix, clamp

INK = (34, 30, 52)


def sh(c, f):
    return mix(c, (24, 18, 44), f)


def hl(c, f):
    return mix(c, (255, 255, 255), f)


class Look:
    def __init__(self, skin, hair, top, pants, shoes, hair_style="short", top_style="tee", under="#ffffff",
                 trim=None, glasses=False, eyes="#3b2a20", sole="#f2f2f2", shoe_trim=None, lips=None, lashes=False,
                 beard=False):
        self.skin, self.hair, self.top, self.pants, self.shoes = (hexc(c) for c in (skin, hair, top, pants, shoes))
        self.hair_style, self.top_style, self.under = hair_style, top_style, hexc(under)
        self.trim = hexc(trim) if trim else sh(self.top, 0.25)
        self.glasses, self.eyes, self.sole = glasses, hexc(eyes), hexc(sole)
        self.shoe_trim = hexc(shoe_trim) if shoe_trim else None
        self.lips = hexc(lips) if lips else sh(self.skin, 0.35)
        self.lashes, self.beard = lashes, beard


def _ik(sx, sy, tx, ty, l1, l2, f):
    dx, dy = tx - sx, ty - sy
    d = clamp(math.hypot(dx, dy), abs(l1 - l2) + 1e-3, l1 + l2 - 1e-3)
    base = math.atan2(dy, dx)
    a = math.acos(clamp((l1 * l1 + d * d - l2 * l2) / (2 * l1 * d), -1, 1))
    best = None
    for s in (1, -1):
        ex, ey = sx + math.cos(base + s * a) * l1, sy + math.sin(base + s * a) * l1
        # prefer the elbow that is lower and slightly behind (natural)
        score = ey - 0.3 * f * (ex - sx)
        if best is None or score > best[0]:
            best = (score, ex, ey)
    _, ex, ey = best
    ux, uy = tx - ex, ty - ey
    n = math.hypot(ux, uy) or 1
    return (ex, ey), (ex + ux / n * l2, ey + uy / n * l2)


def _chain(sx, sy, a1, a2, l1, l2, f):
    """angles from straight down; positive = forward (towards f)"""
    ex, ey = sx + f * math.sin(a1) * l1, sy + math.cos(a1) * l1
    b = a1 + a2
    return (ex, ey), (ex + f * math.sin(b) * l2, ey + math.cos(b) * l2)


def walk_pose(ph, amount=1.0):
    """returns thigh/shin angles for (back, front) legs and arm swing for a walk phase"""
    s = math.sin(ph)
    legs = []
    for k in (0, 1):
        p = ph + k * math.pi
        th = 0.32 * math.sin(p) * amount
        kn = (0.1 + 0.6 * max(0.0, math.cos(p))) * amount   # knee bends while the leg swings forward
        legs.append((th, -kn))
    arms = (("ang", 0.45 * s * amount - 0.18, 0.3 + 0.15 * s), ("ang", -0.45 * s * amount, 0.35 - 0.15 * s))
    return legs, arms


def _cap(cv, a, b, w, col):
    cv.line([a, b], col, w)


def draw_hand(cv, wrist, d, f, u, skin, pose="relaxed", point=None, outline=True):
    """detailed hand with a soft contour (so it reads in front of the face)"""
    if outline:
        _hand(cv, wrist, d, f, u, sh(skin, 0.38), sh(skin, 0.38), pose, point, 0.16 * u)
    return _hand(cv, wrist, d, f, u, skin, sh(skin, 0.18), pose, point, 0.0)


def _hand(cv, wrist, d, f, u, skin, skin_d, pose, point, g):
    dx, dy = d
    nx, ny = -dy * f, dx * f
    P = (wrist[0] + dx * u * 0.75, wrist[1] + dy * u * 0.75)
    det = g == 0

    def at(a, b):
        return (P[0] + dx * a * u + nx * b * u, P[1] + dy * a * u + ny * b * u)
    pts = [at(0.75 * math.cos(k * math.pi / 10) * (1 + g / u * 0.7), 0.62 * math.sin(k * math.pi / 10) * (1 + g / u * 0.9))
           for k in range(20)]
    if pose == "open":
        for b, ln, sp in ((0.42, 1.05, 0.16), (0.14, 1.2, 0.05), (-0.14, 1.12, -0.05), (-0.42, 0.92, -0.16)):
            base = at(0.55, b)
            tip = (base[0] + (dx + nx * sp) * ln * u, base[1] + (dy + ny * sp) * ln * u)
            _cap(cv, base, tip, 0.3 * u + g, skin)
    elif pose == "relaxed":
        for b in (0.36, 0.12, -0.12, -0.36):
            cv.line([at(0.55, b), at(1.05, b * 0.9), at(1.0, b * 0.8 - 0.25)], skin, 0.3 * u + g)
    cv.poly(pts, fill=skin)
    if pose in ("fist", "point", "pinch"):
        for k, b in enumerate((0.36, 0.12, -0.12, -0.36)):
            if pose in ("point", "pinch") and k == 0:
                continue
            c = at(0.68, b)
            cv.circle(c[0], c[1], 0.19 * u + g / 2, fill=skin)
        if det:
            for b in (0.24, 0.0, -0.24):
                cv.line([at(0.5, b), at(0.82, b)], skin_d, 0.05 * u)
    if pose in ("point", "pinch"):
        base = at(0.6, 0.36)
        ln = 1.7
        if point is not None and point[0] == "to":
            vx, vy = point[1][0] - base[0], point[1][1] - base[1]
            dd = math.hypot(vx, vy) or 1
            pd = (vx / dd, vy / dd)
            ln = clamp(dd / u, 1.1, 2.2)
        else:
            pd = point if point is not None else (dx, dy)
        tip = (base[0] + pd[0] * ln * u, base[1] + pd[1] * ln * u)
        _cap(cv, base, tip, 0.3 * u + g, skin)
        if det:
            mx, my = (base[0] + tip[0]) / 2, (base[1] + tip[1]) / 2
            cv.line([(mx - pd[1] * 0.1 * u, my + pd[0] * 0.1 * u), (mx + pd[1] * 0.1 * u, my - pd[0] * 0.1 * u)], skin_d, 0.05 * u)
            cv.circle(tip[0] - pd[0] * 0.06 * u, tip[1] - pd[1] * 0.06 * u, 0.09 * u, fill=hl(skin, 0.35))
    if pose == "open" and det:
        for b, ln, sp in ((0.42, 1.05, 0.16), (0.14, 1.2, 0.05), (-0.14, 1.12, -0.05), (-0.42, 0.92, -0.16)):
            base = at(0.55, b)
            m = (base[0] + (dx + nx * sp) * ln * u * 0.55, base[1] + (dy + ny * sp) * ln * u * 0.55)
            cv.line([(m[0] - nx * 0.1 * u, m[1] - ny * 0.1 * u), (m[0] + nx * 0.1 * u, m[1] + ny * 0.1 * u)], skin_d, 0.05 * u)
    tb = at(0.0, 0.5)
    if pose == "open":
        tt = (tb[0] + (dx * 0.5 + nx * 0.85) * u, tb[1] + (dy * 0.5 + ny * 0.85) * u)
    elif pose in ("fist", "point"):
        tt = at(0.6, 0.12)
    elif pose == "pinch":
        tip_i = tip
        tt = (tip_i[0] - pd[0] * 0.25 * u + nx * 0.28 * u, tip_i[1] - pd[1] * 0.25 * u + ny * 0.28 * u)
    else:
        tt = (tb[0] + (dx * 0.75 + nx * 0.3) * u, tb[1] + (dy * 0.75 + ny * 0.3) * u)
    _cap(cv, tb, tt, 0.32 * u + g, skin)
    if det:
        cv.line([at(-0.1, 0.35), at(0.45, 0.2)], skin_d, 0.05 * u)
    return P


def draw_char(cv, x, y, L, h, f=1, t=0.0, arm_b=None, arm_f=None, walk=None, walk_amt=1.0, lean=0.0, talk=0.0,
              mood="smile", blink=None, look=(0.0, 0.0), brows=0.0, breathe=1.0, sway=1.0, bounce=0.0, squash=0.0,
              head_tilt=0.0, stance=1.0, hold=None, hand_f="relaxed", hand_b="relaxed",
              point_f=None, glasses_dy=0.0, shrug=0.0):
    ink = INK
    r = 0.084 * h
    # ---- procedural life
    br = math.sin(t * 2.1) * breathe
    sw = math.sin(t * 0.8 + x * 0.01) * sway
    if blink is None:
        blink = (t + x * 0.003) % 3.3 < 0.11
    legs = None
    if walk is not None:
        legs, arms = walk_pose(walk, walk_amt)
        arm_b = arm_b or arms[0]
        arm_f = arm_f or arms[1]
    hip_y = y - 0.47 * h - bounce
    hip_x = x + 0.012 * h * sw
    l_th, l_sh = 0.22 * h, 0.215 * h
    # ---- legs (compute first, then lift body so the lowest foot touches the ground)
    feet = []
    if legs is None:
        spread = 0.035 * h * stance
        for k, side in ((0, -1), (1, 1)):
            hx = hip_x + side * 0.03 * h
            fx = x + side * spread + (0.006 * h * sw if side > 0 else 0)
            # knee slightly bent towards the front, IK to a planted foot
            feet.append((hx, fx, y))
        knees = []
        for hx, fx, fy in feet:
            kn, _ = _ik(hx, hip_y, fx, fy - 0.045 * h, l_th, l_sh, -f)
            knees.append(kn)
        leg_pts = [((hx, hip_y), kn, (fx, fy - 0.045 * h)) for (hx, fx, fy), kn in zip(feet, knees)]
    else:
        tmp = []
        for k, (th, kn) in enumerate(legs):
            hx = hip_x + (k * 2 - 1) * 0.02 * h
            knee, ank = _chain(hx, hip_y, th, kn, l_th, l_sh, f)
            tmp.append(((hx, hip_y), knee, ank))
        low = max(p[2][1] for p in tmp)
        dy = (y - 0.045 * h) - low
        hip_y += dy
        leg_pts = [((a[0], a[1] + dy), (b[0], b[1] + dy), (c[0], c[1] + dy)) for a, b, c in tmp]
    # ---- torso frame
    lean_a = lean + 0.015 * sw
    sh_y = hip_y - 0.30 * h - 0.004 * h * br - squash * 0.04 * h - shrug * 0.025 * h
    sh_x = hip_x + f * math.sin(lean_a) * 0.29 * h
    neck = (sh_x + f * 0.01 * h, sh_y - 0.01 * h)
    hb = math.sin(t * 9) * 0.012 * h * clamp(talk)               # head bob while talking
    hcx = neck[0] + f * 0.012 * h + f * math.sin(lean_a) * 0.05 * h
    hcy = sh_y - 0.105 * h - hb
    sx_b, sx_f = sh_x - f * 0.088 * h, sh_x + f * 0.082 * h
    sy_ = sh_y + 0.025 * h
    la1, la2 = 0.16 * h, 0.145 * h
    aw = 0.058 * h

    def arm_pts(spec, sx, side):
        if spec is None:
            spec = ("ang", (0.08 if side > 0 else -0.26) + 0.05 * math.sin(t * 1.3 + side), (0.22 if side > 0 else 0.12) + 0.04 * br)
        if spec[0] == "ik":
            return _ik(sx, sy_, spec[1][0], spec[1][1], la1, la2, f)
        return _chain(sx, sy_, spec[1], spec[2], la1, la2, f)

    hand_b_pose = hand_b
    eb, hand_b = arm_pts(arm_b, sx_b, -1)
    ef, hand_f_pt = arm_pts(arm_f, sx_f, 1)
    top, top_d = L.top, sh(L.top, 0.22)
    skin, skin_d = L.skin, sh(L.skin, 0.16)
    pants, pants_d = L.pants, sh(L.pants, 0.25)

    def draw_leg(pts, back):
        hip, knee, ank = pts
        col = pants_d if back else pants
        cv.line([hip, knee, ank], col, 0.078 * h)
        cv.line([(knee[0] - f * 0.012 * h, knee[1] - 0.01 * h), (knee[0] + f * 0.006 * h, knee[1] + 0.02 * h)],
                sh(col, 0.15), 0.008 * h)                         # knee fold
        cv.line([(ank[0] - 0.034 * h, ank[1] - 0.012 * h), (ank[0] + 0.034 * h, ank[1] - 0.012 * h)], sh(col, 0.2),
                0.012 * h, cap=False)                               # hem
        # sneaker
        sl = 0.095 * h
        fx0, fx1 = (ank[0] - 0.03 * h, ank[0] + sl) if f > 0 else (ank[0] - sl, ank[0] + 0.03 * h)
        shoe = sh(L.shoes, 0.12) if back else L.shoes
        cv.rect(fx0, ank[1] - 0.012 * h, fx1, ank[1] + 0.04 * h, fill=shoe, r=0.022 * h)
        cv.rect(fx0 - 0.003 * h, ank[1] + 0.028 * h, fx1 + 0.004 * h, ank[1] + 0.045 * h, fill=L.sole, r=0.008 * h)
        if L.shoe_trim:
            mx = (fx0 + fx1) / 2
            cv.line([(mx - 0.02 * h, ank[1] + 0.018 * h), (mx + 0.025 * h, ank[1] + 0.005 * h)], L.shoe_trim, 0.009 * h)
        for k in range(2):
            lx = ank[0] + f * (0.012 + k * 0.016) * h
            cv.line([(lx - 0.008 * h, ank[1] + 0.0 * h), (lx + 0.008 * h, ank[1] + 0.006 * h)], hl(shoe, 0.5), 0.004 * h)

    def draw_arm(sh_pt, el, hand, back, pose="relaxed", point=None):
        col = top_d if back else top
        cv.line([sh_pt, el], col, aw)
        dx, dy = hand[0] - el[0], hand[1] - el[1]
        n = math.hypot(dx, dy) or 1
        d = (dx / n, dy / n)
        if pose == "pocket":
            cv.line([el, hand], col, aw * 0.92)
            cv.line([(hand[0] - 0.02 * h, hand[1] + 0.005 * h), (hand[0] + 0.025 * h, hand[1] - 0.01 * h)],
                    sh(pants, 0.35), 0.008 * h)
            return hand
        sleeve_end = (el[0] + dx * 0.78, el[1] + dy * 0.78)
        cv.line([el, sleeve_end], col, aw * 0.92)
        if L.top_style in ("bomber", "hoodie"):
            cv.line([(el[0] + dx * 0.66, el[1] + dy * 0.66), sleeve_end], sh(L.trim, 0.1 if not back else 0.3), aw * 0.9,
                    cap=False)
        cv.line([(el[0] - 0.01 * h, el[1] - 0.01 * h), (el[0] + 0.008 * h, el[1] + 0.012 * h)], sh(col, 0.18), 0.006 * h)
        cv.line([sleeve_end, hand], skin_d if back else skin, aw * 0.5)
        return draw_hand(cv, hand, d, f if not back else -f, 0.034 * h, skin_d if back else skin, pose, point)

    # ---- back hair (long styles) behind everything of the head
    if L.hair_style in ("long", "ponytail"):
        hair_d = sh(L.hair, 0.12)
        if L.hair_style == "long":
            cv.rect(hcx - f * 0.15 * r - r * 1.05, hcy - r * 0.6, hcx - f * 0.15 * r + r * 0.95, hcy + r * 2.1,
                    fill=hair_d, r=r * 0.8)
            for k in range(5):
                xx = hcx - f * 0.15 * r - r * 0.85 + k * r * 0.42
                cv.line([(xx, hcy + r * 0.6), (xx + 0.05 * r * math.sin(t * 2 + k), hcy + r * 2.0)], sh(hair_d, 0.12),
                        0.04 * r)
        else:
            px, py = hcx - f * r * 0.95, hcy - r * 0.3
            swing = 0.25 * math.sin(t * 2.4)
            cv.line([(px, py), (px - f * r * 0.5, py + r * 0.9), (px - f * r * (0.45 - swing), py + r * 1.9)], hair_d,
                    r * 0.55)
    # ---- draw order: back arm, back leg, front leg, torso, head, front arm
    draw_arm((sx_b, sy_), eb, hand_b, True, hand_b_pose)
    draw_leg(leg_pts[0], True)
    draw_leg(leg_pts[1], False)
    # hips / pants block
    hw = 0.072 * h
    cv.rect(hip_x - hw, hip_y - 0.03 * h, hip_x + hw, hip_y + 0.05 * h, fill=pants, r=0.02 * h)
    cv.rect(hip_x - hw, hip_y - 0.035 * h, hip_x + hw, hip_y - 0.018 * h, fill=sh(pants, 0.35), r=0.006 * h)   # belt
    # torso
    tw_s, tw_h = 0.095 * h, 0.08 * h
    pts = [(sh_x - tw_s, sh_y + 0.01 * h), (sh_x + tw_s, sh_y + 0.01 * h), (hip_x + tw_h, hip_y + 0.005 * h),
           (hip_x - tw_h, hip_y + 0.005 * h)]
    if L.top_style == "hoodie":   # hood behind the neck
        cv.ellipse(neck[0] - f * 0.06 * h - 0.06 * h, sh_y - 0.035 * h, neck[0] - f * 0.06 * h + 0.06 * h, sh_y + 0.05 * h,
                   fill=top_d)
    cv.poly(pts, fill=top)
    cv.circle(sh_x - tw_s + 0.02 * h, sh_y + 0.03 * h, 0.03 * h, fill=top)
    cv.circle(sh_x + tw_s - 0.02 * h, sh_y + 0.03 * h, 0.03 * h, fill=top)
    # back-side shading
    bx0 = sh_x - f * tw_s
    cv.poly([(bx0, sh_y + 0.02 * h), (bx0 + f * 0.04 * h, sh_y + 0.02 * h), (hip_x - f * tw_h + f * 0.035 * h, hip_y),
             (hip_x - f * tw_h, hip_y)], fill=top_d)
    cx_ = (sh_x + hip_x) / 2 + f * 0.025 * h
    if L.top_style == "bomber":
        cv.poly([(sh_x + f * 0.005 * h - 0.022 * h, sh_y + 0.008 * h), (sh_x + f * 0.005 * h + 0.022 * h, sh_y + 0.008 * h),
                 (hip_x + f * 0.03 * h + 0.018 * h, hip_y - 0.03 * h), (hip_x + f * 0.03 * h - 0.018 * h, hip_y - 0.03 * h)],
                fill=L.under)                                          # open jacket, tee visible
        cv.rect(hip_x - tw_h, hip_y - 0.035 * h, hip_x + tw_h, hip_y + 0.008 * h, fill=L.trim, r=0.01 * h)   # ribbed hem
        for k in range(6):
            xx = hip_x - tw_h + (k + 0.5) * tw_h * 2 / 6
            cv.line([(xx, hip_y - 0.03 * h), (xx, hip_y + 0.004 * h)], sh(L.trim, 0.2), 0.003 * h, cap=False)
        cv.line([(sh_x - 0.03 * h, sh_y + 0.012 * h), (sh_x + f * 0.01 * h, sh_y + 0.05 * h), (sh_x + 0.035 * h, sh_y + 0.012 * h)],
                L.trim, 0.016 * h)                                    # collar
    elif L.top_style == "hoodie":
        cv.rect(hip_x - tw_h * 0.7 + f * 0.01 * h, hip_y - 0.1 * h, hip_x + tw_h * 0.75 + f * 0.01 * h, hip_y - 0.03 * h,
                fill=top_d, r=0.02 * h)                                # kangaroo pocket
        cv.rect(hip_x - tw_h, hip_y - 0.03 * h, hip_x + tw_h, hip_y + 0.008 * h, fill=L.trim, r=0.01 * h)
        for k in (-1, 1):
            sx = sh_x + f * 0.012 * h + k * 0.018 * h
            cv.line([(sx, sh_y + 0.02 * h), (sx + 0.003 * h * math.sin(t * 2 + k), sh_y + 0.1 * h)], hl(top, 0.5), 0.006 * h)
            cv.circle(sx, sh_y + 0.103 * h, 0.006 * h, fill=hl(top, 0.6))
        cv.ellipse(sh_x - 0.045 * h + f * 0.01 * h, sh_y - 0.01 * h, sh_x + 0.045 * h + f * 0.01 * h, sh_y + 0.03 * h,
                   fill=top_d)                                         # neckline
    else:
        cv.ellipse(sh_x - 0.03 * h + f * 0.01 * h, sh_y - 0.005 * h, sh_x + 0.03 * h + f * 0.01 * h, sh_y + 0.025 * h,
                   fill=sh(top, 0.3))
    chest = (cx_, sh_y + 0.08 * h)
    # ---- neck + head
    cv.rect(neck[0] - 0.022 * h, sh_y - 0.05 * h, neck[0] + 0.022 * h, sh_y + 0.012 * h, fill=skin_d, r=0.008 * h)
    hx = hcx + f * 0.005 * h
    # ear
    ex_ = hx - f * r * 0.62
    cv.ellipse(ex_ - r * 0.18, hcy - r * 0.12, ex_ + r * 0.18, hcy + r * 0.32, fill=skin_d)
    # skull + face
    cv.ellipse(hx - r * 0.95, hcy - r * 1.02, hx + r * 0.95, hcy + r * 1.0, fill=skin)
    cv.ellipse(hx - r * 0.86 + f * r * 0.1, hcy - r * 0.2, hx + r * 0.86 + f * r * 0.1, hcy + r * 1.05, fill=skin)  # jaw
    cv.arc(ex_ - r * 0.1, hcy - r * 0.02, ex_ + r * 0.1, hcy + r * 0.22, 0, 360, sh(skin_d, 0.15), 0.03 * r)
    if L.beard:
        cv.pieslice(hx - r * 0.9 + f * r * 0.2, hcy - r * 0.3, hx + r * 0.85 + f * r * 0.2, hcy + r * 1.08, 0, 180,
                    fill=sh(L.hair, 0.05))
    hair, hair_d = L.hair, sh(L.hair, 0.18)
    # ---- face features
    fx = hx + f * r * 0.3 + look[0] * r * 0.06
    ey = hcy + r * 0.05 + look[1] * r * 0.04
    for k, exx in enumerate((fx - r * 0.33, fx + r * 0.33)):
        far = (exx < fx) == (f > 0)
        s = 0.82 if far else 1.0
        if blink:
            cv.arc(exx - r * 0.17 * s, ey - r * 0.12, exx + r * 0.17 * s, ey + r * 0.1, 20, 160, ink, 0.05 * r)
        else:
            cv.ellipse(exx - r * 0.17 * s, ey - r * 0.2, exx + r * 0.17 * s, ey + r * 0.18, fill=(255, 255, 255, 255))
            ix, iy = exx + f * r * 0.04 + look[0] * r * 0.06, ey + r * 0.01 + look[1] * r * 0.05
            cv.circle(ix, iy, r * 0.115 * s, fill=L.eyes)
            cv.circle(ix, iy, r * 0.06 * s, fill=(20, 16, 30, 255))
            cv.circle(ix + r * 0.04, iy - r * 0.05, r * 0.035, fill=(255, 255, 255, 255))
            cv.arc(exx - r * 0.18 * s, ey - r * 0.22, exx + r * 0.18 * s, ey + r * 0.18, 200, 340, ink, 0.035 * r)
            if L.lashes:
                cv.line([(exx + f * r * 0.15 * s, ey - r * 0.14), (exx + f * r * 0.24 * s, ey - r * 0.2)], ink, 0.03 * r)
        bry = ey - r * (0.36 + 0.1 * brows) - (0.03 * r if mood == "smirk" and not far else 0)
        tilt = (0.05 if mood == "angry" else -0.02) * r * (1 if exx < fx else -1)
        cv.line([(exx - r * 0.17, bry + tilt), (exx + r * 0.16, bry - r * 0.04 - tilt)], hair_d, 0.075 * r)
        if L.glasses:
            gy = ey - glasses_dy * r
            cv.circle(exx, gy, r * 0.27 * s, outline=ink, width=0.05 * r)
            cv.arc(exx - r * 0.2 * s, gy - r * 0.2, exx + r * 0.05, gy + r * 0.05, 200, 260, (255, 255, 255, 200), 0.04 * r)
    if L.glasses:
        gy = ey - glasses_dy * r
        cv.line([(fx - r * 0.07, gy - r * 0.02), (fx + r * 0.07, gy - r * 0.02)], ink, 0.05 * r)
        cv.line([(fx - f * r * 0.6, gy - r * 0.03), (hx - f * r * 0.65, gy - r * 0.05)], ink, 0.045 * r)
    # nose
    nx = fx + f * r * 0.1
    cv.line([(nx, ey + r * 0.05), (nx + f * r * 0.1, ey + r * 0.32), (nx - f * r * 0.02, ey + r * 0.36)], skin_d, 0.07 * r)
    # mouth
    my = ey + r * 0.58
    mo = clamp(talk) * (0.5 + 0.5 * abs(math.sin(t * 13)))
    if mood == "laugh":
        cv.pieslice(fx - r * 0.3, my - r * 0.18, fx + r * 0.34, my + r * 0.36, 0, 180, fill=hexc("#7a2b33"))
        cv.rect(fx - r * 0.22, my - r * 0.02, fx + r * 0.26, my + r * 0.06, fill=(255, 255, 255, 255))
        cv.ellipse(fx - r * 0.1, my + r * 0.14, fx + r * 0.16, my + r * 0.3, fill=hexc("#e5737f"))
    elif mood == "o":
        cv.ellipse(fx - r * 0.1, my - r * 0.08, fx + r * 0.14, my + r * 0.2, fill=hexc("#7a2b33"))
    elif mo > 0.08:
        cv.ellipse(fx - r * 0.2, my - r * 0.06, fx + r * 0.24, my + r * (0.06 + 0.26 * mo), fill=hexc("#7a2b33"))
        cv.rect(fx - r * 0.14, my - r * 0.05, fx + r * 0.18, my + r * 0.01, fill=(255, 255, 255, 255))
        cv.ellipse(fx - r * 0.08, my + r * 0.08 * mo + r * 0.02, fx + r * 0.12, my + r * (0.06 + 0.2 * mo), fill=hexc("#e5737f"))
    elif mood == "smirk":
        cv.line([(fx - r * 0.18, my + r * 0.04), (fx + r * 0.08, my + r * 0.06), (fx + r * 0.24, my - r * 0.06)], L.lips, 0.06 * r)
    elif mood == "worried":
        cv.arc(fx - r * 0.18, my + r * 0.02, fx + r * 0.22, my + r * 0.24, 200, 340, L.lips, 0.06 * r)
    else:
        cv.arc(fx - r * 0.22, my - r * 0.2, fx + r * 0.26, my + r * 0.14, 20, 160, L.lips, 0.065 * r)
    cv.circle(fx - f * r * 0.5, ey + r * 0.38, r * 0.14, fill=(255, 120, 110, 60))
    cv.circle(fx + f * r * 0.42, ey + r * 0.38, r * 0.1, fill=(255, 120, 110, 45))
    # ---- hair (front)
    st_ = L.hair_style
    if st_ == "quiff":
        cv.pieslice(hx - r * 1.0, hcy - r * 1.08, hx + r * 1.0, hcy + r * 0.5, 180, 360, fill=hair)
        cv.ellipse(hx - f * r * 0.62 - r * 0.38, hcy - r * 0.55, hx - f * r * 0.62 + r * 0.38, hcy + r * 0.2, fill=hair_d)  # faded side
        cv.ellipse(hx - f * r * 0.98 - r * 0.06, hcy - r * 0.35, hx - f * r * 0.98 + r * 0.06, hcy + r * 0.25, fill=hair_d)
        q = [(hx - f * r * 0.9, hcy - r * 0.75), (hx - f * r * 0.2, hcy - r * 1.42), (hx + f * r * 0.7, hcy - r * 1.36),
             (hx + f * r * 1.12, hcy - r * 0.9), (hx + f * r * 0.85, hcy - r * 0.62), (hx + f * r * 0.1, hcy - r * 0.72)]
        cv.poly(q, fill=hair)
        for k in range(4):
            a0 = hx - f * r * (0.6 - k * 0.35)
            cv.line([(a0, hcy - r * (0.8 + 0.1 * k)), (a0 + f * r * 0.45, hcy - r * (1.25 - 0.02 * k))], hl(hair, 0.35), 0.05 * r)
    elif st_ in ("long", "ponytail"):
        cv.pieslice(hx - r * 1.04, hcy - r * 1.1, hx + r * 1.04, hcy + r * 0.6, 180, 360, fill=hair)
        part = hx + f * r * 0.15
        cv.poly([(part, hcy - r * 1.02), (hx + f * r * 1.05, hcy - r * 0.55), (hx + f * r * 0.95, hcy - r * 0.15),
                 (part + f * r * 0.15, hcy - r * 0.55)], fill=hair)
        cv.poly([(part, hcy - r * 1.02), (hx - f * r * 1.05, hcy - r * 0.45), (hx - f * r * 1.02, hcy + r * 0.6),
                 (hx - f * r * 0.7, hcy + r * 0.2), (part - f * r * 0.3, hcy - r * 0.5)], fill=hair)
        for k in range(4):
            cv.line([(part - f * r * (0.1 + k * 0.2), hcy - r * 0.98), (part - f * r * (0.35 + k * 0.2), hcy - r * 0.4)],
                    hl(hair, 0.2), 0.04 * r)
        if st_ == "long":
            cv.line([(hx + f * r * 0.95, hcy - r * 0.5), (hx + f * r * 1.02, hcy + r * 0.4), (hx + f * r * 0.92, hcy + r * 1.3)], hair, 0.3 * r)
    elif st_ == "curly":
        for k in range(11):
            a = math.pi + k * math.pi / 10
            cv.circle(hx + math.cos(a) * r * 0.95, hcy - r * 0.2 + math.sin(a) * r * 0.95, r * 0.32, fill=hair)
        cv.circle(hx, hcy - r * 0.9, r * 0.4, fill=hair)
    elif st_ == "bun":
        cv.pieslice(hx - r * 1.02, hcy - r * 1.08, hx + r * 1.02, hcy + r * 0.5, 180, 360, fill=hair)
        cv.circle(hx - f * r * 0.3, hcy - r * 1.25, r * 0.42, fill=hair)
    else:   # short
        cv.pieslice(hx - r * 1.0, hcy - r * 1.06, hx + r * 1.0, hcy + r * 0.45, 180, 360, fill=hair)
        cv.poly([(hx - f * r * 0.2, hcy - r * 1.0), (hx + f * r * 0.95, hcy - r * 0.6), (hx + f * r * 0.55, hcy - r * 0.62)],
                fill=hair)
    # ---- front arm (+ held prop under the hand)
    if hold:
        hold(cv, hand_f_pt)
    draw_arm((sx_f, sy_), ef, hand_f_pt, False, hand_f, point_f)
    return dict(head=(hx, hcy), r=r, fx=fx, ey=ey, hand_f=hand_f_pt, hand_b=hand_b, chest=chest, sh_y=sh_y, sh_x=sh_x,
                hip=(hip_x, hip_y), neck=neck, top=hcy - r * 1.4)


def talk_arm(t, k=1.0, seed=0.0):
    """conversational hand gesture for the front arm"""
    return ("ang", 0.25 + 0.3 * k * (0.5 + 0.5 * math.sin(t * 2.6 + seed)), 1.1 + 0.35 * k * math.sin(t * 3.4 + seed))
