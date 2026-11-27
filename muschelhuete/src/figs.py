"""Figuren aus dem Muschelbert-Video."""
import math
import cairo
from draw import *
from retro import P


def man(ctx, x, y, s, kind='bert', walk=None, face=1, wave=0.0, gray=0.0, smile=1, T=0.0, sit=False, arm=None, cap_on=True):
    """kind: bert (Matrosenhemd, rote Kappe mit Muschel, Schnurrbart) | officer (Zolluniform, Mütze)."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s * face, s)
    skin = hexc('#F2C6A0')
    if kind == 'bert':
        shirt, pants, cap = C['white'], hexc('#2B4A7A'), hexc('#C8322E')
        hair = hexc('#6E3820')
    else:
        shirt, pants, cap = hexc('#2A3A6A'), hexc('#22305A'), hexc('#22305A')
        hair = mixc(hexc('#3A2A20'), hexc('#D8D8D8'), gray)
    ellipse(ctx, 0, 0, 26, 5, alpha(C['shadow'], 0.22))
    lg = math.sin(walk) * 0.45 if walk is not None else 0.0
    if not sit:
        for side, l in ((-1, lg), (1, -lg)):
            fx = side * 7 + math.sin(l) * 18
            line(ctx, side * 7, -46, fx, -5, 11, pants)
            ellipse(ctx, fx + 4, -3, 11, 5, hexc('#2B2B33'))
    # Oberkörper
    ctx.save()
    rrect(ctx, -19, -102, 38, 60, 12)
    ctx.clip()
    rect(ctx, -19, -102, 38, 60, shirt)
    if kind == 'bert':
        for i in range(6):
            rect(ctx, -19, -96 + i * 10, 38, 4, hexc('#2B4A7A'))
    else:
        line(ctx, 0, -100, 0, -44, 2, alpha(C['white'], 0.3))
        for i in range(3):
            circle(ctx, 0, -88 + i * 13, 2.2, P['gold'])
        star = [(10 + 5 * math.cos(a), -84 + 5 * math.sin(a)) for a in [i * math.pi * 2 / 5 - math.pi / 2 for i in range(5)]]
        circle(ctx, 10, -84, 5, P['gold'])
    rect(ctx, 8, -102, 11, 60, alpha(C['ink'], 0.08))
    ctx.restore()
    if kind == 'officer':
        rect(ctx, -19, -50, 38, 6, hexc('#1A1A22'))
        rect(ctx, -3, -50, 6, 6, P['gold'])
    # Arme
    for side in (-1, 1):
        sx, sy = side * 16, -96
        if side == 1 and wave > 0:
            tx, ty = 26, -150 + math.sin(T * 10) * 8
        elif side == 1 and arm is not None:
            tx, ty = arm
        else:
            tx, ty = side * 22, -54 + (math.sin(walk + side) * 4 if walk is not None else 0)
        line(ctx, sx, sy, tx, ty, 9, shirt if kind == 'officer' else hexc('#2B4A7A'))
        circle(ctx, tx, ty + 2, 5, skin)
    # Kopf
    rect(ctx, -4, -110, 8, 10, mixc(skin, C['ink'], 0.12))
    circle(ctx, 2, -128, 20, skin)
    circle(ctx, 20, -126, 4, mixc(skin, C['ink'], 0.08))
    ellipse(ctx, 22, -124, 6, 5, skin)  # Nase
    circle(ctx, 22, -124, 5, mixc(skin, hexc('#E07A6A'), 0.35))
    ellipse(ctx, 10, -134, 2.4, 3.2, C['ink'])
    line(ctx, 6, -141, 13, -142, 2, mixc(hair, C['ink'], 0.2))
    # Schnurrbart
    ctx.move_to(8, -118)
    ctx.curve_to(14, -121, 22, -121, 28, -117)
    ctx.curve_to(22, -113, 14, -113, 8, -118)
    src(ctx, hair if kind == 'officer' else hexc('#6E3820'))
    ctx.fill()
    if smile:
        ctx.move_to(10, -110)
        ctx.curve_to(14, -106, 18, -106, 22, -110)
        ctx.set_line_width(1.8)
        src(ctx, hexc('#8A3B3B'))
        ctx.stroke()
    ctx.new_path()
    ctx.arc(2, -130, 21, math.radians(150), math.radians(260))
    ctx.line_to(-6, -128)
    ctx.close_path()
    src(ctx, hair)
    ctx.fill()
    # Kopfbedeckung
    if not cap_on:
        pass
    elif kind == 'bert':
        ctx.new_sub_path()
        ctx.arc(2, -136, 21, math.pi, 2 * math.pi)
        ctx.close_path()
        src(ctx, cap)
        ctx.fill()
        fill_rrect(ctx, 6, -140, 30, 7, 3, mixc(cap, C['ink'], 0.25))
        ctx.save()
        ctx.translate(0, -148)
        ctx.scale(0.35, 0.35)
        ctx.move_to(0, 10)
        for i in range(7):
            a = math.radians(200 + i * 140 / 6)
            ctx.line_to(math.cos(a) * 22, math.sin(a) * 22 + 4)
        ctx.close_path()
        src(ctx, C['pink3'])
        ctx.fill()
        ctx.restore()
    else:
        rect(ctx, -18, -152, 40, 16, cap)
        poly(ctx, [(-22, -152), (26, -152), (20, -162), (-16, -162)], cap)
        fill_rrect(ctx, 4, -140, 28, 6, 3, hexc('#111122'))
        circle(ctx, 2, -146, 4, P['gold'])
    ctx.restore()


