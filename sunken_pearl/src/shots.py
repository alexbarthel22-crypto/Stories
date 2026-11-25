"""Alle Einstellungen. Jede Funktion baut die Szene und gibt update(t_local) zurück."""
import bpy, math
from mathutils import Vector
from lib import *
from sets import *
from sets_interior import *
from sets_ext import *
from shelly import Shelly

R = math.radians
FPS = 24

# Schnittzeiten (s) passend zur Erzählung
CUTS = [0.0, 2.55, 8.0, 11.4, 15.2, 18.4, 20.3, 21.65, 23.0, 24.2, 26.9, 28.65, 30.45, 32.25, 34.6, 36.55, 39.1,
        42.85, 45.5, 48.15, 49.85, 53.9, 56.6, 60.8, 63.5, 65.4, 70.6]
NAMES = ['surf', 'under', 'descent', 'winext', 'cozy', 'clock', 'startle', 'door', 'windark', 'peer', 'nixie', 'flicker',
         'gauge', 'crack', 'run', 'capsule', 'liftup', 'display', 'face', 'doors', 'reveal', 'pearl', 'faceglow', 'reach',
         'eye', 'final']
UW = (0.004, 0.035, 0.05)  # Wasserfarbe


def shot_range(name):
    i = NAMES.index(name)
    return CUTS[i], CUTS[i + 1]


def cam_track(cam, t, kf):
    """kf: Liste (t, loc, target, lens)."""
    loc = keys(t, [(k[0], k[1]) for k in kf])
    tgt = keys(t, [(k[0], k[2]) for k in kf])
    lens = keys(t, [(k[0], k[3]) for k in kf])
    cam.location = loc
    look_at(cam, tgt)
    cam.data.lens = lens


def shake(t, amp, freq=13.0, seed=0):
    return (amp * (math.sin(t * freq + seed) * 0.6 + math.sin(t * freq * 2.3 + seed * 2) * 0.4),
            amp * (math.cos(t * freq * 1.1 + seed) * 0.6 + math.sin(t * freq * 1.7 + 1 + seed) * 0.4))


def handheld(cam, t, amp=0.004):
    dx, dz = shake(t, amp, 1.3)
    cam.location.x += dx; cam.location.z += dz


def underwater_world(top=(0.03, 0.16, 0.2), mid=UW, bottom=(0.0, 0.005, 0.01)):
    world(mid, 1.0, top=top, bottom=bottom)


def sit_pose(sh, chair, extra=None, lean=-6):
    c = chair
    p = {'root_loc': (c.location.x, c.location.y, 0.0), 'root_rot': (0, 0, math.degrees(c.rotation_euler.z)),
         'hips_loc': (0, 0.02, 0.5), 'hipL': (-84, 0, -6), 'hipR': (-84, 0, 6), 'kneeL': (88, 0, 0), 'kneeR': (88, 0, 0),
         'ankleL': (-4, 0, 0), 'ankleR': (-4, 0, 0), 'spine': (lean, 0, 0), 'shoulderL': (-25, -18, 0), 'shoulderR': (-25, 18, 0),
         'elbowL': (-55, 0, 10), 'elbowR': (-55, 0, -10), 'fingers': 0.4}
    if extra: p.update(extra)
    sh.pose(p)


def held_cup(sh, M):
    """Teetasse in der rechten Hand."""
    wr = sh.j['wristR']
    cup = lathe('heldcup', [(0.0, 0.0), (0.035, 0.0), (0.045, 0.01), (0.05, 0.08), (0.046, 0.08), (0.04, 0.012), (0.0, 0.012)], 32, M['ceramic'], None, False, False)
    cup.parent = wr; cup.location = (0.0, -0.06, -0.1); cup.rotation_euler = (R(180), 0, 0)
    tea = prim('cyl', 'heldtea', (0, 0, 0.066), scale=(0.043, 0.043, 0.002), mat=M['tea'])
    tea.parent = cup
    return cup


def blink_at(t, times, dur=0.16):
    b = 0.0
    for tb in times:
        if tb <= t <= tb + dur:
            u = (t - tb) / dur
            b = max(b, 1 - abs(u * 2 - 1))
    return b


# ===================================================================== Shots
def s_surf():
    world((0.05, 0.08, 0.15), 1.0, top=(0.0, 0.005, 0.03), bottom=(0.03, 0.05, 0.1))
    S = Surface()
    cam = camera(lens=30)

    def up(t):
        S.update(4.0 + t)
        cam_track(cam, t, [(0, (9, -46, 1.4), (0, 0, 4.2), 30), (2.55, (6, -33, 2.0), (0, 0, 4.6), 30)])
        handheld(cam, t, 0.05)
    return up


def s_under():
    underwater_world()
    M = Mats()
    build_tower(M, None, -1, -32)
    # Kuppel-Unterseite / Wasseroberfläche von unten
    surf = prim('plane', 'uwsurf', (0, 0, 0.0), scale=(300, 300, 1), coll=None)
    sm = principled('uwsurfm', (0.05, 0.2, 0.25), rough=0.1, emit=(0.2, 0.6, 0.7), emit_str=1.0, bump=(0.15, 1.0, 4, 'wave'))
    surf.data.materials.append(sm)
    surf.rotation_euler = (R(180), 0, 0)
    sm['nofog'] = 1
    neck = lathe('neck', [(TOWER_R, -3.7), (TOWER_R + 4.4, -1.3), (TOWER_R + 4.6, -0.9), (0.0, -0.9)], 96, M.hull_dark, None, False, False)
    prim('torus', 'neckrim', (0, 0, -1.1), mat=M.brass, R=TOWER_R + 4.55, r=0.12, seg=128)
    for k in range(6):
        godray(f'ray{k}', (k * 9 - 22, -6 + k * 3, 0), (k * 9 - 22 + 6, -10 + k * 3, -90), 3 + k % 3, 7, (0.5, 0.9, 1.0), 0.18)
    sch = School(None, 60, (20, -24, -18), 10, 0.55, seed=5, mat=fish_mat('f2', '#5E8AA8', '#DCE8F0'), speed=1.2)
    js = [jelly(None, f'j{i}', (rnd(i).uniform(-25, 30), rnd(i).uniform(-40, -18), -rnd(i + 3).uniform(10, 70)), rnd(i).uniform(0.8, 1.5),
                (0.6, 0.8, 1.0), 0.0, 2.5) for i in range(7)]
    add_light('SUN', 'sun', (0, 0, 0), 1.2, (0.5, 0.85, 1.0), 0.1, rot=(R(12), R(8), 0))
    fog_all(0.022, UW)
    cam = camera(lens=20)

    def up(t):
        sch.update(t + 3)
        for i, j in enumerate(js):
            j.location.z += 0.01
        cam_track(cam, t, [(0, (22, -36, -4), (0, 0, 2), 20), (1.5, (21, -34, -9), (0, 0, -14), 20),
                           (5.45, (17, -29, -40), (0, 0, -110), 18)])
        handheld(cam, t, 0.06)
    return up


def s_descent():
    underwater_world(top=(0.01, 0.06, 0.09), mid=(0.002, 0.02, 0.03), bottom=(0.0, 0.0, 0.004))
    M = Mats()
    build_tower(M, None, -98, -150)
    js = [jelly(None, f'j{i}', (rnd(i).uniform(10, 26), rnd(i).uniform(-30, -12), -rnd(i + 3).uniform(370, 520)), rnd(i).uniform(0.8, 1.4),
                (0.4 + 0.1 * i % 3, 0.7, 1.0), 0.0, 4.0) for i in range(10)]
    sch = School(None, 50, (16, -26, -440), 7, 0.5, seed=8, mat=fish_mat('f3', '#4C6E88', '#C8D8E4', emit=(0.1, 0.3, 0.4)))
    add_light('SUN', 'sun', (0, 0, 0), 0.25, (0.4, 0.8, 1.0), 0.1, rot=(R(10), 0, 0))
    fog_all(0.03, (0.002, 0.02, 0.03))
    cam = camera(lens=18)

    def up(t):
        sch.update(t * 2)
        z = -360 - 150 * (t / 3.4) ** 1.2
        cam.location = (14 + 2 * t, -17 - 1.5 * t, z)
        look_at(cam, (-2, 0, z - 22))
        cam.rotation_euler.rotate_axis('Z', R(-8 + 4 * t))
        cam.data.lens = 18
        handheld(cam, t, 0.12)
    return up


def s_winext():
    underwater_world(top=(0.01, 0.06, 0.09), mid=(0.003, 0.025, 0.04), bottom=(0.0, 0.0, 0.005))
    A = Apartment(outside=False)
    A.set_gauge(0.62); A.set_depth('4000'); A.set_clock(3, 5, 0)
    M = build_facade(A)
    sh = Shelly()
    cup = held_cup(sh, A.M)
    sch = School(None, 30, (0, 9, 2), 4.5, 0.4, seed=12, mat=fish_mat('f4', '#5E8AA8', '#DCE8F0'))
    js = [jelly(None, f'j{i}', (rnd(i).uniform(-6, 6), rnd(i).uniform(6, 14), rnd(i).uniform(-3, 6)), 0.6, (0.5, 0.85, 1.0), 0.0, 3.0) for i in range(4)]
    add_light('SPOT', 'outspot', (3, 9, 6), 600, (0.4, 0.8, 1.0), 0.3, spot=R(50))
    look_at(D.objects['outspot'], (0, 3.6, 1.6))
    fog_all(0.025, (0.003, 0.025, 0.04))
    A.lamp_light.data.energy = 200
    add_light('AREA', 'inkey', (0.8, 2.5, 2.2), 120, (1.0, 0.75, 0.5), 1.0)
    look_at(D.objects['inkey'], (-0.45, 0.55, 1.1))
    cam = camera(lens=35)

    def up(t):
        sch.update(t + 10)
        sit_pose(sh, A.chair, {'shoulderR': (-55, 25, 15), 'elbowR': (-95, 0, -40), 'neck': (8, 0, 0)})
        sh.set_face('smile', blink=blink_at(t, [1.4]), look=(0, -15))
        cam_track(cam, t, [(0, (1.3, 13, 0.4), (0, 3, 1.4), 35), (3.8, (0.35, 7.2, 1.3), (-0.2, 2.5, 1.25), 40)])
        handheld(cam, t, 0.03)
    return up


def s_cozy():
    world((0.01, 0.02, 0.03), 1.0)
    A = Apartment()
    A.set_gauge(0.62); A.set_depth('4000'); A.set_clock(3, 5, 0)
    sh = Shelly()
    cup = held_cup(sh, A.M)
    fog_all(0.06, (0.01, 0.06, 0.09), skip=set(m.name for m in D.materials) - set(A.out_mats))
    js = [jelly(None, 'jw', (2.5, 11, 2.8), 0.8, (0.6, 0.85, 1.0), 0.0, 4.0)]
    add_light('AREA', 'key', (0.2, 2.6, 2.4), 90, (0.5, 0.8, 1.0), 1.5)
    look_at(D.objects['key'], (-0.4, 0.6, 1.2))
    add_light('AREA', 'warmkey', (1.3, 1.2, 1.6), 50, (1.0, 0.7, 0.45), 0.8)
    look_at(D.objects['warmkey'], (-0.45, 0.6, 1.2))
    cam = camera(lens=28)

    def up(t):
        A.school.update(t + 5)
        sip = ease(t, 0.6, 1.4) - ease(t, 2.2, 3.0)
        sit_pose(sh, A.chair, {'shoulderR': (lerp(-35, -70, sip), 25, 15), 'elbowR': (lerp(-85, -115, sip), 0, -40),
                               'neck': (lerp(5, -8, sip), 0, 0)})
        sh.set_face('smile' if sip < 0.5 else 'neutral', blink=max(blink_at(t, [0.3]), sip * 0.85), look=(0, -5))
        cam_track(cam, t, [(0, (1.1, 2.45, 1.5), (-0.45, 0.6, 1.0), 30), (3.2, (0.85, 2.2, 1.42), (-0.45, 0.6, 1.05), 34)])
        handheld(cam, t, 0.005)
    return up


def s_clock():
    world((0.01, 0.02, 0.03), 1.0)
    A = Apartment()
    A.set_depth('4000'); A.set_gauge(0.62)
    A.lamp_light.data.energy = 40; A.ceil_light.data.energy = 0; set_emit(A.M['bulb'], 4)
    add_light('SPOT', 'clockspot', (-2.0, -1.2, 3.0), 30, (1.0, 0.75, 0.5), 0.1, spot=R(30))
    look_at(D.objects['clockspot'], (-2.4, -2.95, 2.3))
    cam = camera(lens=60)

    def up(t):
        s = 52 + t * 1.0
        mm = 11 + (s // 60)
        A.set_clock(3, mm, math.floor(s % 60))
        cam_track(cam, t, [(0, (-2.25, -1.4, 2.25), (-2.4, -2.95, 2.3), 55), (1.9, (-2.32, -1.75, 2.28), (-2.4, -2.95, 2.3), 62)])
    return up


def s_startle():
    world((0.01, 0.02, 0.03), 1.0)
    A = Apartment()
    A.set_depth('4000'); A.set_gauge(0.62); A.set_clock(3, 12, 0)
    A.lamp_light.data.energy = 50; A.ceil_light.data.energy = 0; set_emit(A.M['bulb'], 4)
    sh = Shelly()
    fog_all(0.06, (0.01, 0.06, 0.09), skip=set(m.name for m in D.materials) - set(A.out_mats))
    add_light('AREA', 'key', (0.3, 2.3, 2.0), 40, (0.45, 0.75, 1.0), 1.0)
    look_at(D.objects['key'], (-0.45, 0.6, 1.2))
    cam = camera(lens=50)

    def up(t):
        A.school.update(t + 8)
        k = ease(t, 0.15, 0.35)  # bei "klopft"
        sit_pose(sh, A.chair, {'spine': (lerp(-12, 4, k), 0, 0), 'neck': (lerp(14, -4, k), lerp(0, -10, ease(t, 0.6, 1.1)), 0),
                               'head': (0, 0, lerp(0, 22, ease(t, 0.6, 1.1))), 'fingers': 0.2})
        sh.set_face('neutral' if k < 0.5 else 'o', blink=lerp(0.85, 0.0, k), look=(lerp(0, 28, ease(t, 0.5, 0.9)), 0),
                    brow=lerp(-0.2, 0.9, k), lids_wide=k, shell=0.12 * k)
        dx, dz = shake(t, 0.01 * k * (1 - ease(t, 0.5, 1.2)), 30)
        cam_track(cam, t, [(0, (-0.15, 1.95, 1.12), (-0.42, 0.5, 1.22), 50), (1.35, (-0.18, 1.85, 1.14), (-0.42, 0.5, 1.22), 54)])
        cam.location.x += dx; cam.location.z += dz
    return up


def s_door():
    world((0.01, 0.02, 0.03), 1.0)
    A = Apartment(outside=False)
    A.lamp_light.data.energy = 50; A.ceil_light.data.energy = 0; set_emit(A.M['bulb'], 4)
    A.set_depth('4000'); A.set_gauge(0.62); A.set_clock(3, 12, 0)
    add_light('SPOT', 'doorspot', (1.8, -0.6, 2.9), 260, (1.0, 0.68, 0.42), 0.2, spot=R(45))
    add_light('POINT', 'doorfill', (1.0, 0.8, 1.8), 25, (0.4, 0.7, 1.0), 0.5)
    look_at(D.objects['doorspot'], (4.0, -1.2, 1.1))
    cam = camera(lens=32)

    def up(t):
        cam_track(cam, t, [(0, (0.0, 0.9, 1.3), (4.0, -1.2, 1.2), 26), (1.35, (0.6, 0.5, 1.3), (4.0, -1.2, 1.2), 29)])
        handheld(cam, t, 0.004)
    return up


def s_windark():
    world((0.01, 0.02, 0.03), 1.0)
    A = Apartment()
    A.lamp_light.data.energy = 50; A.ceil_light.data.energy = 0; set_emit(A.M['bulb'], 4)
    A.set_depth('4000'); A.set_gauge(0.62); A.set_clock(3, 12, 0)
    for m in ('outbg',):
        set_emit(D.materials[m], 0.35)
    sh = Shelly()
    fog_all(0.08, (0.003, 0.03, 0.05), skip=set(m.name for m in D.materials) - set(A.out_mats))
    cam = camera(lens=26)

    def up(t):
        A.school.update(t + 30)
        for f, _, _, _, _ in A.school.fish:
            f.location.x += 40
        for o in D.objects:
            if o.name.startswith('farlight'): o.hide_render = True  # Fische weg: leeres Wasser
        sit_pose(sh, A.chair, {'neck': (-2, 0, 0), 'head': (0, 0, lerp(20, 0, ease(t, 0.0, 0.8))), 'spine': (4, 0, 0)})
        sh.set_face('o', look=(0, 0), lids_wide=1.0, brow=0.8, shell=0.1)
        cam_track(cam, t, [(0, (-0.3, -1.8, 1.55), (0, 3.0, 1.55), 26), (1.2, (-0.25, -1.2, 1.55), (0, 3.0, 1.6), 30)])
    return up


def s_peer():
    world((0.01, 0.02, 0.03), 1.0)
    A = Apartment()
    A.lamp_light.data.energy = 45; A.ceil_light.data.energy = 0; set_emit(A.M['bulb'], 4)
    A.set_depth('4000'); A.set_gauge(0.62); A.set_clock(3, 12, 0)
    set_emit(D.materials['outbg'], 0.25)
    sh = Shelly()
    # riesiger Schatten draußen
    set_emit(D.materials['outbg'], 1.1)
    shadow = prim('sphere', 'bigshadow', (0, 11, 2), scale=(7, 1.6, 1.9), mat=principled('shadowm', (0.0, 0.0, 0.0), 1.0))
    fin = prim('cube', 'shfin', (0, 26, 4.8), rot=(0, R(-20), 0), scale=(1.5, 0.3, 1.6), mat=D.materials['shadowm'])
    fin.parent = shadow; fin.location = (6, 0, 2.6)
    fog_all(0.06, (0.01, 0.07, 0.1), skip=set(m.name for m in D.materials) - set(A.out_mats + ['shadowm']))
    add_light('AREA', 'rim', (0, 2.4, 2.6), 25, (0.4, 0.75, 1.0), 1.0)
    look_at(D.objects['rim'], (0, 1.9, 1.3))
    cam = camera(lens=30)

    def up(t):
        A.school.update(t)
        for f, _, _, _, _ in A.school.fish:
            f.location.x += 40
        for o in D.objects:
            if o.name.startswith('farlight'): o.hide_render = True
        shadow.location = (lerp(-16, 14, t / 2.7), 10, 2.6)
        sh.pose({'root_loc': (0.15, 2.3, 0), 'root_rot': (0, 0, 180), 'shoulderL': (-75, -25, 0), 'shoulderR': (-75, 25, 0),
                 'elbowL': (-40, 0, 20), 'elbowR': (-40, 0, -20), 'wristL': (-60, 0, 0), 'wristR': (-60, 0, 0), 'fingers': 0.0,
                 'spine': (-6, 0, 0), 'neck': (0, 0, lerp(-6, 8, ease(t, 0.3, 2.4))), 'head': (-4, 0, 0)})
        sh.set_face('o', lids_wide=1.0, brow=0.7, shell=0.0)
        cam_track(cam, t, [(0, (-0.95, 0.4, 1.9), (0.4, 5.0, 1.55), 26), (2.7, (-0.8, 0.85, 1.85), (0.4, 5.0, 1.55), 28)])
    return up


def s_nixie():
    world((0.01, 0.02, 0.03), 1.0)
    A = Apartment(outside=False)
    A.lamp_light.data.energy = 30; A.ceil_light.data.energy = 0
    A.set_gauge(0.62); A.set_clock(3, 12, 0)
    cam = camera(lens=50)

    def up(t):
        # Ziffern laufen kurz hoch und rasten auf 4000 ein
        if t < 0.55:
            A.set_depth(str(3990 + int(t * 18)))
        else:
            A.set_depth('4000')
        set_emit(A.nixie_mat, 10 + 4 * math.sin(t * 40) * (1 - ease(t, 0.5, 0.8)))
        cam_track(cam, t, [(0, (-1.5, 1.6, 1.8), (-1.85, 2.96, 1.95), 40), (1.75, (-1.62, 1.95, 1.86), (-1.85, 2.96, 1.95), 46)])
    return up


def flicker(t, t0, seed=1):
    if t < t0: return 1.0
    u = t - t0
    v = 0.5 + 0.5 * math.sin(u * 37 + seed) * math.sin(u * 11.3 + seed * 2)
    on = 1.0 if v > 0.45 else 0.05
    return on * (1 - 0.6 * ease(u, 1.0, 1.6))


def s_flicker():
    world((0.01, 0.02, 0.03), 1.0)
    A = Apartment()
    A.set_depth('4000'); A.set_gauge(0.62); A.set_clock(3, 12, 30)
    set_emit(D.materials['outbg'], 0.4)
    sh = Shelly()
    fog_all(0.075, (0.004, 0.035, 0.055), skip=set(m.name for m in D.materials) - set(A.out_mats))
    cam = camera(lens=22)

    def up(t):
        A.school.update(t)
        for f, _, _, _, _ in A.school.fish:
            f.location.x += 40
        for o in D.objects:
            if o.name.startswith('farlight'): o.hide_render = True
        f = flicker(t, 0.35)
        A.lamp_light.data.energy = 120 * f; A.ceil_light.data.energy = 160 * f
        set_emit(A.M['bulb'], 30 * f); set_emit(A.M['shadein'], 6 * f)
        for fm in A.floats: set_emit(fm, 2.5 * f)
        sh.pose({'root_loc': (0.9, 2.1, 0), 'root_rot': (0, 0, lerp(180, 215, ease(t, 0.4, 1.0))), 'spine': (4, 0, 0),
                 'neck': (lerp(0, -18, ease(t, 0.4, 0.9)), 0, 0), 'head': (-8, 0, 0), 'shoulderL': (10, -14, 0), 'shoulderR': (10, 14, 0)})
        sh.set_face('o', lids_wide=1.0, brow=0.8, look=(0, lerp(0, 20, ease(t, 0.4, 0.9))), shell=0.15)
        cam_track(cam, t, [(0, (-2.6, -0.3, 1.35), (0.7, 2.1, 1.5), 22), (1.8, (-2.3, -0.1, 1.35), (0.7, 2.1, 1.5), 24)])
    return up


def s_gauge():
    world((0.01, 0.02, 0.03), 1.0)
    A = Apartment(outside=False)
    A.lamp_light.data.energy = 25; A.ceil_light.data.energy = 0; set_emit(A.M['bulb'], 3)
    A.set_depth('4000')
    add_light('SPOT', 'gspot', (1.3, 2.1, 2.5), 90, (0.5, 0.8, 1.0), 0.1, spot=R(30))
    look_at(D.objects['gspot'], (1.75, 2.98, 1.85))
    cam = camera(lens=55)

    def up(t):
        k = ease(t, 0.35, 1.5)
        jit = 0.02 * math.sin(t * 47) * (1 if 0.3 < t < 1.6 else 0.3)
        A.set_gauge(lerp(0.62, 0.08, k) + jit)
        dx, dz = shake(t, 0.003, 25)
        cam_track(cam, t, [(0, (1.62, 1.95, 1.8), (1.75, 2.93, 1.85), 42), (1.8, (1.68, 2.15, 1.83), (1.75, 2.93, 1.85), 48)])
        cam.location.x += dx; cam.location.z += dz
    return up


def s_crack():
    world((0.01, 0.02, 0.03), 1.0)
    A = Apartment()
    A.set_depth('4000'); A.set_gauge(0.1); A.set_clock(3, 12, 40)
    A.lamp_light.data.energy = 20; A.ceil_light.data.energy = 0; set_emit(A.M['bulb'], 3)
    set_emit(D.materials['outbg'], 0.4)
    sh = Shelly()
    fog_all(0.075, (0.004, 0.035, 0.055), skip=set(m.name for m in D.materials) - set(A.out_mats))
    cm = emission('crackm', (0.8, 0.95, 1.0), 1.6)
    add_light('AREA', 'cfill', (0.6, 2.9, 2.0), 30, (0.5, 0.8, 1.0), 0.8)
    look_at(D.objects['cfill'], (-0.15, 1.95, 1.4))
    state = {'obs': []}
    drops = [prim('sphere', f'drip{k}', (0, 3.27, 0), scale=(0.012, 0.008, 0.02), mat=principled('dripm', hexc('#CFEFFF'), 0.0, trans=1.0, ior=1.33)) for k in range(4)]
    cam = camera(lens=30)

    def up(t):
        A.school.update(t)
        for f, _, _, _, _ in A.school.fish:
            f.location.x += 40
        for o in D.objects:
            if o.name.startswith('farlight'): o.hide_render = True
        for o in state['obs']:
            D.objects.remove(o)
        g = ease(t, 0.05, 1.3) * 1.0
        state['obs'] = crack_mesh(None, (0.3, 1.45), 0.95, g, mat=cm)
        for k, d in enumerate(drops):
            u = max(0, t - 0.9 - k * 0.25)
            d.location = (0.35 + (k - 1.5) * 0.12, 3.27, 1.85 - u * u * 0.6 - k * 0.05)
            d.hide_render = t < 0.9 + k * 0.25
        al = 0.5 + 0.5 * math.sin(t * 9)
        set_emit(A.alarm_mat, 20 * al); A.alarm_light.data.energy = 120 * al
        sh.pose({'root_loc': (-0.15, 1.95, 0), 'root_rot': (0, 0, 180), 'spine': (lerp(0, 10, ease(t, 0.2, 0.5)), 0, 0),
                 'neck': (lerp(-4, 6, ease(t, 0.2, 0.5)), 0, 0), 'head': (0, 0, -18),
                 'shoulderL': (-30, -20, 0), 'shoulderR': (lerp(0, -70, ease(t, 0.3, 0.7)), 30, 0), 'elbowR': (-110, 0, 0), 'fingers': 0.7})
        sh.set_face('o', lids_wide=1.0, brow=1.0, brow_tilt=0.6, shell=lerp(0.0, 0.55, ease(t, 0.2, 0.45)), look=(-15, 5))
        dx, dz = shake(t, 0.012 * (1 - ease(t, 0.2, 1.0)), 32)
        cam_track(cam, t, [(0, (0.12, 3.85, 1.36), (-0.15, 1.95, 1.4), 30), (2.35, (0.1, 3.75, 1.37), (-0.15, 1.95, 1.4), 33)])
        cam.location.x += dx; cam.location.z += dz
    return up


def run_pose(t, speed=7.0, base=None):
    ph = t * speed
    s = math.sin(ph)
    p = {'hipL': (s * 40 - 10, 0, -3), 'hipR': (-s * 40 - 10, 0, 3),
         'kneeL': (max(0, -s) * 70 + 15, 0, 0), 'kneeR': (max(0, s) * 70 + 15, 0, 0),
         'shoulderL': (-s * 45, -12, 0), 'shoulderR': (s * 45, 12, 0), 'elbowL': (-75, 0, 0), 'elbowR': (-75, 0, 0),
         'spine': (-14, 0, s * 4), 'neck': (6, 0, 0), 'fingers': 0.6,
         'hips_loc': (0, 0, 0.72 + 0.04 * abs(math.cos(ph)))}
    if base: p.update(base)
    return p


def s_run():
    world((0.01, 0.0, 0.0), 1.0)
    C = Corridor()
    sh = Shelly()
    fl = add_light('POINT', 'runfill', (0, 0, 1.6), 25, (1.0, 0.6, 0.5), 0.3)
    cam = camera(lens=26)

    def up(t):
        C.update(t)
        x = -8 + t * 4.2
        p = run_pose(t, 9.0, {'root_loc': (x, 0.0, 0), 'root_rot': (0, 0, 90)})
        sh.pose(p)
        sh.set_face('o', lids_wide=1.0, brow=0.9, brow_tilt=0.6, shell=0.25 + 0.05 * math.sin(t * 18))
        cam.location = (x + 3.2 - t * 0.2, 0.35, 1.25 + 0.02 * math.sin(t * 18))
        fl.location = (x + 1.6, 0.4, 1.6)
        look_at(cam, (x, 0.0, 1.15))
        cam.data.lens = 26
    return up


def s_capsule():
    underwater_world(top=(0.01, 0.05, 0.08), mid=(0.002, 0.02, 0.03), bottom=(0.0, 0.0, 0.004))
    M = Mats()
    build_tower(M, None, -140, -175, plates=True)
    # Schienen an der Turmseite (Winkel 270°)
    a = R(270)
    rx, ry = math.cos(a) * (TOWER_R + 1.6), math.sin(a) * (TOWER_R + 1.6)
    for s in (-1, 1):
        prim('cube', 'rail', (rx + s * 1.0, ry, -560), scale=(0.15, 0.25, 110), mat=M.brass, bevel=0.03)
    cap = empty('capsule', (rx, ry - 0.2, -520))
    cg = prim('sphere', 'capglass', (0, 0, 0), scale=(1.3, 1.3, 1.6), mat=window_glass('capg', (0.85, 0.95, 1.0), 0.12), parent=cap, seg=48)
    for k in range(6):
        b = 2 * math.pi * k / 6
        pts = [(math.cos(b) * 1.32 * math.cos(th), math.sin(b) * 1.32 * math.cos(th), 1.62 * math.sin(th)) for th in [R(-90 + 180 * j / 16) for j in range(17)]]
        tube(f'caprib{k}', pts, 0.05, 8, M.brass, None).parent = cap
    prim('torus', 'capring', (0, 0, 0), mat=M.brass, R=1.32, r=0.1, seg=64, parent=cap)
    prim('cyl', 'capfloor', (0, 0, -0.9), scale=(1.1, 1.1, 0.06), mat=M.hull_dark, parent=cap)
    prim('cyl', 'capbot', (0, 0, -1.65), scale=(0.35, 0.35, 0.2), mat=M.brass, parent=cap)
    head = prim('sphere', 'caplamp', (0, 0, -1.9), scale=(0.25,) * 3, mat=M.lampc, parent=cap)
    il = add_light('POINT', 'capin', (0, 0, 0.9), 120, (1.0, 0.7, 0.4), 0.3)
    il.parent = cap; il.location = (0, 0, 0.9)
    sp = add_light('SPOT', 'capbeam', (0, 0, -2.0), 4000, (0.5, 0.9, 1.0), 0.2, spot=R(35))
    sp.parent = cap; sp.location = (0, 0, -2.0); sp.rotation_euler = (0, 0, 0)
    sp.rotation_euler = (R(180), 0, 0)
    beam = godray('beam', (0, 0, -2.0), (0, 0, -30), 0.2, 9, (0.5, 0.9, 1.0), 0.5)
    beam.parent = cap; beam.location = (0, 0, -30); beam.rotation_euler = (0, 0, 0)
    sh = Shelly()
    sh.root.parent = cap; sh.root.location = (0, 0, -0.84)
    sh.pose({'root_loc': (0, 0, -0.84), 'root_rot': (0, 0, 0), 'shoulderL': (0, -10, 0)})
    sh.set_face('o', lids_wide=1.0)
    for i in range(6):
        jelly(None, f'j{i}', (rnd(i).uniform(-8, 8), rnd(i).uniform(-28, -18), -rnd(i + 3).uniform(510, 600)), rnd(i).uniform(0.7, 1.2), (0.5, 0.8, 1.0), 0, 3.5)
    fog_all(0.032, (0.002, 0.02, 0.03), skip={'beamm'})
    cam = camera(lens=24)

    def up(t):
        z = -523 - 9 * t - 1.5 * t * t
        cap.location = (rx, ry - 0.2, z)
        cam_track(cam, t, [(0, (rx + 4.5, ry - 7.5, -525), (rx, ry, -523.5), 26), (2.55, (rx + 4.0, ry - 7.0, -539), (rx, ry, -543), 26)])
        handheld(cam, t, 0.05)
    return up


def s_liftup():
    world((0.0, 0.0, 0.0), 1.0)
    E = Elevator()
    sh = Shelly()
    cam = camera(lens=30)

    def up(t):
        n = -185 - int(t * 4)
        E.disp.data.body = str(n)
        E.ceil_light.data.energy = 70 * (0.8 + 0.2 * math.sin(t * 23) * math.sin(t * 7))
        sh.pose({'root_loc': (0.05, 0.1, 0), 'root_rot': (0, 0, -10), 'neck': (-14, 0, 0), 'head': (-12, 0, 0),
                 'shoulderL': (8, -10, 0), 'shoulderR': (-35, 20, 0), 'elbowR': (-80, 0, -20), 'fingers': 0.8})
        sh.set_face('worry', lids_wide=0.6, brow=0.6, brow_tilt=0.8, look=(0, 22), blink=blink_at(t, [2.2]))
        cam_track(cam, t, [(0, (0.38, -0.72, 1.12), (0.02, 0.1, 1.45), 30), (3.75, (0.3, -0.62, 1.15), (0.02, 0.1, 1.45), 34)])
        dx, dz = shake(t, 0.004, 20)
        cam.location.x += dx; cam.location.z += dz
    return up


def s_display():
    world((0.0, 0.0, 0.0), 1.0)
    E = Elevator()
    cam = camera(lens=50)

    def up(t):
        # 42.85 Start; "zweihunderteins" bei 44.33 -> t=1.48
        if t < 0.55: s = '-199'
        elif t < 1.45: s = '-200'
        else: s = '-201'
        glitch = 1.45 < t < 1.75 and int(t * 40) % 2 == 0
        E.disp.data.body = s if not glitch else '-2O1'
        red = ease(t, 1.45, 1.6)
        set_emit(E.disp_mat, 14 if not glitch else 25, color=lerp((1.0, 0.42, 0.08), (1.0, 0.08, 0.05), red))
        E.disp_light.data.color = lerp((1.0, 0.45, 0.1), (1.0, 0.1, 0.05), red)
        cam_track(cam, t, [(0, (0.15, -0.35, 2.15), (0, -0.96, 2.45), 45), (2.65, (0.05, -0.5, 2.3), (0, -0.96, 2.45), 50)])
        dx, dz = shake(t, 0.003 + 0.004 * red, 22)
        cam.location.x += dx; cam.location.z += dz
    return up


def s_face():
    world((0.0, 0.0, 0.0), 1.0)
    E = Elevator()
    E.disp.data.body = '-201'
    set_emit(E.disp_mat, 14, color=(1.0, 0.08, 0.05)); E.disp_light.data.color = (1.0, 0.1, 0.05); E.disp_light.data.energy = 14
    ff = add_light('AREA', 'facefill', (0.3, -1.0, 1.5), 12, (0.7, 0.85, 1.0), 0.6)
    look_at(ff, (0, 0.1, 1.42))
    sh = Shelly()
    cam = camera(lens=55)

    def up(t):
        E.ceil_light.data.energy = 50 * flicker(t, 0.0, 3) + 5
        tr = 0.6 * math.sin(t * 40)
        sh.pose({'root_loc': (0.0, 0.1, 0), 'root_rot': (0, 0, 0), 'neck': (-10, 0, tr), 'head': (-6, 0, 0),
                 'shoulderL': (-20, -10, 0), 'shoulderR': (-20, 10, 0), 'elbowL': (-90, 0, 30), 'elbowR': (-90, 0, -30), 'fingers': 0.9})
        sh.set_face('worry', lids_wide=1.0, brow=1.0, brow_tilt=0.9, look=(lerp(0, -10, ease(t, 1.2, 1.6)), 14),
                    shell=0.35 + 0.05 * math.sin(t * 30), blink=blink_at(t, [1.9]))
        cam_track(cam, t, [(0, (0.0, -0.75, 1.42), (0.0, 0.1, 1.42), 50), (2.65, (0.0, -0.55, 1.42), (0.0, 0.1, 1.42), 58)])
    return up


def s_doors():
    world((0.0, 0.0, 0.0), 1.0)
    E = Elevator()
    E.disp.data.body = '-201'
    set_emit(E.disp_mat, 14, color=(1.0, 0.08, 0.05))
    out = prim('plane', 'outglow', (0, -6, 1.5), rot=(R(90), 0, 0), scale=(8, 6, 1), mat=emission('outglowm', (0.25, 0.65, 0.9), 0.9))
    pl = add_light('AREA', 'outl', (0, -2.0, 1.4), 400, (0.55, 0.85, 1.0), 2.0, rot=(R(-90), 0, 0))
    look_at(pl, (0, 0.5, 1.2))
    ray = godray('dray', (0, -3, 1.4), (0, 1.0, 1.0), 2.0, 0.8, (0.6, 0.9, 1.0), 0.35)
    sh = Shelly()
    cam = camera(lens=28)

    def up(t):
        k = ease(t, 0.15, 1.3)
        E.set_doors(k)
        pl.data.energy = 400 * k
        ray.hide_render = k < 0.1
        sh.pose({'root_loc': (0.0, 0.15, 0), 'root_rot': (0, 0, 0), 'neck': (0, 0, 0),
                 'shoulderL': (-10, -10, 0), 'shoulderR': (-10, 10, 0), 'elbowL': (-40, 0, 0), 'elbowR': (-40, 0, 0), 'fingers': 0.7})
        sh.set_face('o', lids_wide=1.0)
        cam_track(cam, t, [(0, (0.32, 0.72, 1.75), (0, -1.5, 1.25), 24), (1.7, (0.28, 0.62, 1.72), (0, -1.5, 1.25), 26)])
    return up


def chamber_base(t_shelly_y=None):
    underwater_world(top=(0.02, 0.12, 0.16), mid=(0.0, 0.035, 0.055), bottom=(0.0, 0.01, 0.02))
    Ch = Chamber()
    sh = Shelly()
    fog_all(0.03, (0.0, 0.04, 0.065))
    return Ch, sh


def s_reveal():
    Ch, sh = chamber_base()
    cam = camera(lens=20)

    def up(t):
        Ch.update(t + 50, breathe=0.6, glow=2.0)
        y = lerp(1.2, 5.6, ease(t, 0.0, 2.6))
        walk = 1 - ease(t, 1.8, 2.4)
        p = run_pose(t, 4.0, {'root_loc': (0, y, 0), 'root_rot': (0, 0, 180)})
        for k in ('hipL', 'hipR', 'kneeL', 'kneeR', 'shoulderL', 'shoulderR'):
            p[k] = tuple(v * walk * 0.5 for v in p[k])
        p['spine'] = (0, 0, 0); p['elbowL'] = (-20, 0, 0); p['elbowR'] = (-20, 0, 0); p['hips_loc'] = (0, 0, 0.74)
        sh.pose(p)
        sh.set_face('o', lids_wide=1.0)
        cam_track(cam, t, [(0, (1.1, 3.4, 0.45), (0, 17, 2.5), 20), (4.05, (2.2, 4.6, 4.2), (0, 15, 1.2), 20)])
        handheld(cam, t, 0.03)
    return up


def s_pearl():
    Ch, sh = chamber_base()
    cam = camera(lens=35)

    def up(t):
        Ch.update(t + 54, breathe=1.0, glow=2.2)
        sh.pose({'root_loc': (-0.6, 9.5, 0), 'root_rot': (0, 0, 180)})
        sh.set_face('o', lids_wide=1.0)
        cam_track(cam, t, [(0, (-2.6, 8.0, 1.0), (0, 17.4, 2.6), 32), (2.7, (-2.0, 9.3, 1.2), (0, 17.4, 2.5), 36)])
        handheld(cam, t, 0.01)
    return up


def s_faceglow():
    Ch, sh = chamber_base()
    cam = camera(lens=45)

    def up(t):
        Ch.update(t + 57, breathe=1.0, glow=2.2)
        y = lerp(10.5, 11.6, ease(t, 0.5, 3.8))
        sh.pose({'root_loc': (0, y, 0), 'root_rot': (0, 0, 180), 'neck': (-6, 0, 0), 'head': (-4, 0, 0),
                 'shoulderL': (-10, -12, 0), 'shoulderR': (-10, 12, 0), 'fingers': 0.5})
        sh.set_face('neutral', lids_wide=0.5, brow=0.5, look=(0, 8), blink=blink_at(t, [1.0, 3.3]))
        cam_track(cam, t, [(0, (0.25, y + 1.9, 1.35), (0, y, 1.4), 42), (4.2, (0.2, y + 1.25, 1.38), (0, y, 1.4), 50)])
        cam.location = (0.25 - 0.05 * t / 4.2, y + lerp(1.9, 1.25, t / 4.2), 1.36)
        look_at(cam, (0, y, 1.38))
    return up


def s_reach():
    Ch, sh = chamber_base()
    cam = camera(lens=30)
    knocks = [0.35, 0.75, 1.5]

    def up(t):
        th = sum(max(0, 1 - abs(t - k) / 0.12) for k in knocks)
        Ch.update(t + 61, breathe=0.5, glow=2.2 + 3 * th)
        Ch.pearl.scale = tuple(v * (1 + 0.02 * th) for v in Ch.pearl.scale)
        rec = ease(t, 0.35, 0.6)
        sh.pose({'root_loc': (0, lerp(13.7, 13.4, rec), 0), 'root_rot': (0, 0, 180), 'spine': (lerp(-10, 6, rec), 0, 0),
                 'shoulderR': (lerp(-80, -40, rec), 10, 0), 'elbowR': (lerp(-10, -60, rec), 0, 0), 'wristR': (-30, 0, 0),
                 'fingers': lerp(0.1, 0.6, rec), 'neck': (-6, 0, 0)})
        sh.set_face('o', lids_wide=1.0, brow=0.9, shell=0.3 * rec)
        dx, dz = shake(t, 0.03 * th, 30)
        cam_track(cam, t, [(0, (-1.9, 11.9, 1.45), (0.1, 14.6, 1.7), 26), (2.7, (-1.7, 12.2, 1.45), (0.1, 14.6, 1.7), 28)])
        cam.location.x += dx; cam.location.z += dz
    return up


def s_eye():
    Ch, sh = chamber_base()
    cam = camera(lens=40)

    def up(t):
        o = ease(t, 0.15, 1.2)
        Ch.update(t + 63, breathe=0.4, glow=lerp(2.2, 1.4, o), eye_open=o, pupil=lerp(1.6, 0.6, ease(t, 1.0, 1.6)))
        sh.pose({'root_loc': (0, 13.4, 0), 'root_rot': (0, 0, 180)})
        cam_track(cam, t, [(0, (0.0, 12.9, 2.35), (0, 17.4, 2.3), 38), (1.9, (0.0, 13.6, 2.32), (0, 17.4, 2.3), 44)])
    return up


def s_final():
    Ch, sh = chamber_base()
    cam = camera(lens=26)

    def up(t):
        Ch.update(t + 65, breathe=0.6, glow=1.4, eye_open=1.0, pupil=0.6 + 0.1 * math.sin(t * 2))
        Ch.eye_piv.rotation_euler = (R(-6), 0, R(4 * math.sin(t * 0.8)))
        sh.pose({'root_loc': (0, 13.4, 0), 'root_rot': (0, 0, 180), 'shoulderL': (-5, -15, 0), 'shoulderR': (-5, 15, 0)})
        sh.set_face('o', lids_wide=1.0, shell=0.2)
        cam_track(cam, t, [(0, (2.8, 9.0, 0.7), (0, 15.5, 2.0), 24), (5.2, (2.0, 10.2, 1.1), (0, 15.5, 2.1), 28)])
    return up


SHOTS = {n: globals()['s_' + n] for n in NAMES}
