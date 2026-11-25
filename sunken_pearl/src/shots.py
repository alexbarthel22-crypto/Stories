"""Alle Einstellungen (Version 2: Luxus statt Grusel). Jede Funktion baut die Szene und gibt update(t_local) zurück."""
import bpy, math
from mathutils import Vector
from lib import *
from sets import *
from sets_interior import Elevator
from sets_ext import Surface, godray, pearl_material
from sets_lux import *
from shelly import Shelly

R = math.radians
FPS = 24

# Schnittzeiten (s) passend zur Erzählung (vo_otto, Start 0.05 s)
CUTS = [0.0, 2.5, 8.2, 10.8, 14.4, 15.3, 16.4, 17.4, 21.5, 24.1, 27.4, 32.9, 35.8, 38.0, 39.7, 42.2, 46.1, 47.8,
        50.7, 55.1, 59.7, 61.3, 64.0, 69.6]
NAMES = ['surf', 'under', 'descent', 'winext', 'marble', 'crystal', 'gold', 'reef', 'door', 'envelope', 'card', 'face',
         'dress', 'capsule', 'liftup', 'display', 'doors', 'reveal', 'pearl', 'faceglow', 'reach', 'open', 'final']
UW = (0.004, 0.035, 0.05)
EXPO = -0.6  # Innenräume etwas dunkler, stimmungsvoller


def shot_range(name):
    i = NAMES.index(name)
    return CUTS[i], CUTS[i + 1]


def cam_track(cam, t, kf):
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


def expo(v=EXPO):
    bpy.context.scene.view_settings.exposure = v


def blink_at(t, times, dur=0.16):
    b = 0.0
    for tb in times:
        if tb <= t <= tb + dur:
            u = (t - tb) / dur
            b = max(b, 1 - abs(u * 2 - 1))
    return b


def sit_pose(sh, chair, extra=None, lean=-6):
    c = chair
    p = {'root_loc': (c.location.x, c.location.y, 0.0), 'root_rot': (0, 0, math.degrees(c.rotation_euler.z)),
         'hips_loc': (0, 0.06, 0.5), 'hipL': (-84, 0, -4), 'hipR': (-84, 0, 4), 'kneeL': (82, 0, 0), 'kneeR': (82, 0, 0),
         'ankleL': (-10, 0, 0), 'ankleR': (-10, 0, 0), 'spine': (lean, 0, 0), 'shoulderL': (-25, -18, 0), 'shoulderR': (-25, 18, 0),
         'elbowL': (-55, 0, 10), 'elbowR': (-55, 0, -10), 'fingers': 0.4, 'sit': 1.0}
    if extra: p.update(extra)
    sh.pose(p)


def walk_pose(t, speed=5.0, amp=1.0, base=None):
    ph = t * speed
    s = math.sin(ph)
    p = {'hipL': (s * 22 * amp - 4, 0, -2), 'hipR': (-s * 22 * amp - 4, 0, 2),
         'kneeL': (max(0, -s) * 35 * amp + 6, 0, 0), 'kneeR': (max(0, s) * 35 * amp + 6, 0, 0),
         'shoulderL': (-s * 14 * amp, -8, 0), 'shoulderR': (s * 14 * amp, 8, 0), 'elbowL': (-18, 0, 0), 'elbowR': (-18, 0, 0),
         'spine': (-2, 0, s * 3 * amp), 'neck': (2, 0, 0), 'fingers': 0.35,
         'hips_loc': (0, 0, 0.74 + 0.012 * abs(math.cos(ph)) * amp)}
    if base: p.update(base)
    return p


def held_flute(sh, A):
    wr = sh.j['wristR']
    g, ch = A._flute((0, 0, 0), None)
    for o in (g, ch):
        o.parent = wr; o.location = (0.0, -0.035, -0.13); o.rotation_euler = (R(180), 0, 0)
    return g


def apt_base(outside=True, density=1.0, outfit='home'):
    world((0.02, 0.06, 0.08), 1.0)
    A = LuxApartment(outside=outside, reef_density=density)
    sh = Shelly(outfit=outfit)
    if outside:
        fog_all(0.03, (0.01, 0.16, 0.24), skip=set(m.name for m in D.materials) - set(A.out_mats))
    expo()
    return A, sh


# ===================================================================== Shots
def s_surf():
    world((0.05, 0.08, 0.15), 1.0, top=(0.0, 0.005, 0.03), bottom=(0.03, 0.05, 0.1))
    S = Surface()
    sh = Shelly(outfit='home')
    key = add_light('AREA', 'shkey', (2.4, -14.6, 2.8), 260, (1.0, 0.85, 0.8), 1.2)
    look_at(key, (1.2, -11.8, 1.8))
    rim = add_light('AREA', 'shrim', (0.2, -7.6, 3.2), 90, (1.0, 0.65, 0.4), 1.5)
    look_at(rim, (1.2, -11.8, 1.8))
    cam = camera(lens=30)

    def up(t):
        S.update(4.0 + t)
        sh.pose({'root_loc': (1.2, -11.8, 0.6), 'root_rot': (0, 0, -12), 'neck': (-4, 0, 6), 'head': (-4, 0, 4),
                 'shoulderL': (-8, -14, 0), 'shoulderR': (-8, 14, 0), 'fingers': 0.35})
        sh.set_face('smile', lids_wide=0.3, brow=0.3, look=(0, 6), blink=blink_at(t, [1.4]))
        k = ease(t, 0.15, 2.5)
        k = k * k * (3 - 2 * k)
        p0, p1 = Vector((1.75, -14.4, 1.95)), Vector((7.0, -32.0, 2.6))
        q0, q1 = Vector((1.2, -11.8, 1.85)), Vector((0.3, 0.0, 3.6))
        cam.location = p0.lerp(p1, k)
        look_at(cam, q0.lerp(q1, k))
        cam.data.lens = lerp(40, 30, k)
        handheld(cam, t, 0.006)
    return up


def s_under():
    underwater_world(top=(0.04, 0.2, 0.25))
    M = Mats()
    build_tower(M, None, -1, -32)
    surf = prim('plane', 'uwsurf', (0, 0, 0.0), scale=(300, 300, 1))
    sm = principled('uwsurfm', (0.05, 0.2, 0.25), rough=0.1, emit=(0.2, 0.6, 0.7), emit_str=1.0, bump=(0.15, 1.0, 4, 'wave'))
    surf.data.materials.append(sm); surf.rotation_euler = (R(180), 0, 0); sm['nofog'] = 1
    neck = lathe('neck', [(TOWER_R, -3.7), (TOWER_R + 4.4, -1.3), (TOWER_R + 4.6, -0.9), (0.0, -0.9)], 96, M.hull_dark, None, False, False)
    prim('torus', 'neckrim', (0, 0, -1.1), mat=M.brass, R=TOWER_R + 4.55, r=0.12, seg=128)
    for k in range(6):
        godray(f'ray{k}', (k * 9 - 22, -6 + k * 3, 0), (k * 9 - 22 + 6, -10 + k * 3, -90), 3 + k % 3, 7, (0.5, 0.9, 1.0), 0.2)
    sch = School(None, 60, (20, -24, -18), 10, 0.55, seed=5, mat=fish_mat('f2', '#F2C230', '#FFF3C0'), speed=1.2)
    for i in range(7):
        jelly(None, f'j{i}', (rnd(i).uniform(-25, 30), rnd(i).uniform(-40, -18), -rnd(i + 3).uniform(10, 70)), rnd(i).uniform(0.8, 1.5),
              (1.0, 0.65, 0.9), 0.0, 2.5)
    add_light('SUN', 'sun', (0, 0, 0), 1.4, (0.5, 0.85, 1.0), 0.1, rot=(R(12), R(8), 0))
    fog_all(0.02, (0.006, 0.05, 0.07))
    cam = camera(lens=20)

    def up(t):
        sch.update(t + 3)
        cam_track(cam, t, [(0, (22, -36, -4), (0, 0, 2), 20), (1.5, (21, -34, -9), (0, 0, -14), 20),
                           (5.7, (17, -29, -40), (0, 0, -110), 18)])
        handheld(cam, t, 0.06)
    return up


def s_descent():
    underwater_world(top=(0.01, 0.08, 0.12), mid=(0.003, 0.03, 0.045), bottom=(0.0, 0.0, 0.006))
    M = Mats()
    build_tower(M, None, -98, -150)
    for i in range(10):
        jelly(None, f'j{i}', (rnd(i).uniform(10, 26), rnd(i).uniform(-30, -12), -rnd(i + 3).uniform(370, 520)), rnd(i).uniform(0.8, 1.4),
              (1.0, 0.6 + 0.1 * (i % 3), 0.9), 0.0, 4.0)
    sch = School(None, 50, (16, -26, -440), 7, 0.5, seed=8, mat=fish_mat('f3', '#4C9AD8', '#DCEBF8', emit=(0.2, 0.5, 0.7)))
    add_light('SUN', 'sun', (0, 0, 0), 0.3, (0.4, 0.8, 1.0), 0.1, rot=(R(10), 0, 0))
    fog_all(0.028, (0.004, 0.03, 0.045))
    cam = camera(lens=18)

    def up(t):
        sch.update(t * 2)
        z = -360 - 150 * (t / 3.4) ** 1.2
        cam.location = (14 + 2 * t, -17 - 1.5 * t, z)
        look_at(cam, (-2, 0, z - 22))
        cam.rotation_euler.rotate_axis('Z', R(-8 + 4 * t))
        cam.data.lens = 18
        handheld(cam, t, 0.1)
    return up


def s_winext():
    underwater_world(top=(0.02, 0.12, 0.16), mid=(0.004, 0.035, 0.05), bottom=(0.0, 0.0, 0.006))
    A = LuxApartment(outside=False)
    M = lux_facade(A)
    sh = Shelly()
    fl = held_flute(sh, A)
    sch = School(None, 30, (0, 9, 2), 4.5, 0.35, seed=12, mat=fish_mat('f4', '#F2C230', '#FFF3C0'))
    for i in range(4):
        jelly(None, f'j{i}', (rnd(i).uniform(-6, 6), rnd(i).uniform(7, 14), rnd(i).uniform(-2, 6)), 0.6, (1.0, 0.65, 0.9), 0.0, 3.0)
    add_light('SPOT', 'outspot', (3, 10, 6), 500, (0.4, 0.8, 1.0), 0.3, spot=R(50))
    look_at(D.objects['outspot'], (0, 4.0, 1.6))
    fog_all(0.022, (0.004, 0.03, 0.045))
    cam = camera(lens=35)

    def up(t):
        sch.update(t + 10)
        sit_pose(sh, A.chair, {'shoulderR': (-55, 25, 15), 'elbowR': (-100, 0, -40), 'neck': (6, 0, 0)})
        sh.set_face('smile', blink=blink_at(t, [1.6]), look=(0, -6))
        cam_track(cam, t, [(0, (1.6, 14.5, 0.9), (0, 3.9, 1.6), 30), (3.6, (0.6, 8.5, 1.4), (-0.6, 2.0, 1.2), 34)])
        handheld(cam, t, 0.03)
    return up


def s_marble():
    A, sh = apt_base(density=0.4)
    sh.root.location = (40, 0, 0)
    cam = camera(lens=24)
    add_light('SPOT', 'mspot', (3.0, 1.0, 3.5), 180, (1.0, 0.85, 0.6), 0.2, spot=R(40))
    look_at(D.objects['mspot'], (4.2, 3.2, 0.3))

    def up(t):
        u = t / 0.9
        cam_track(cam, t, [(0, (-2.6, -3.0, 0.1), (-0.6, 1.5, 0.55), 20), (0.9, (-2.35, -2.55, 0.13), (-0.6, 1.5, 0.65), 21)])
    return up


def s_crystal():
    A, sh = apt_base(density=0.4)
    sh.root.location = (40, 0, 0)
    cam = camera(lens=45)

    def up(t):
        A.chand.root.rotation_euler = (0, 0, R(8 * t))
        cam_track(cam, t, [(0, (2.1, -2.0, 2.05), (0.3, -0.4, 2.8), 34), (1.1, (1.95, -2.15, 2.0), (0.3, -0.4, 2.78), 37)])
    return up


def s_gold():
    A, sh = apt_base(density=0.4)
    sh.root.location = (40, 0, 0)
    cam = camera(lens=55)

    def up(t):
        a = R(-40 + 22 * t)
        c = Vector((3.6, 1.8, 1.2))
        cam.location = c + Vector((math.sin(a) * -1.3, -math.cos(a) * 1.3, 0.05))
        look_at(cam, c + Vector((0, 0, 0.02)))
        cam.data.lens = 55
    return up


def s_reef():
    A, sh = apt_base(density=1.2)
    cam = camera(lens=26)
    rim = add_light('AREA', 'rrim', (0.4, 3.3, 2.2), 60, (0.5, 0.9, 1.0), 1.0)
    look_at(rim, (0.2, 2.4, 1.4))
    kf = add_light('AREA', 'rkey', (-1.2, 1.0, 2.0), 25, (1.0, 0.8, 0.65), 0.8)
    look_at(kf, (0.2, 2.5, 1.4))

    def up(t):
        for s_ in A.schools: s_.update(t + 2)
        turn = ease(t, 2.2, 3.4)
        sh.pose({'root_loc': (0.2, 2.6, 0), 'root_rot': (0, 0, 180 - 20 * turn), 'shoulderL': (-70, -18, 0), 'elbowL': (-35, 0, 10),
                 'wristL': (-55, 0, 0), 'fingers': 0.05, 'spine': (-3, 0, 0), 'neck': (-6, 0, 12 * turn), 'head': (-4, 0, 14 * turn),
                 'hipL': (0, 0, -3), 'hipR': (-6, 0, 3), 'kneeR': (12, 0, 0)})
        sh.set_face('smile' if turn > 0.4 else 'neutral', look=(lerp(0, -25, turn), -4), blink=blink_at(t, [1.2]))
        cam_track(cam, t, [(0, (1.6, -0.6, 1.45), (0.1, 3.8, 1.5), 22), (4.1, (1.15, 0.6, 1.5), (0.05, 3.8, 1.55), 26)])
        handheld(cam, t, 0.004)
    return up


def s_door():
    A, sh = apt_base(density=0.3)
    sh.root.location = (40, 0, 0)
    env = envelope()
    env.scale = (2.0,) * 3
    sp = add_light('SPOT', 'dspot', (3.6, -1.2, 3.5), 120, (1.0, 0.82, 0.6), 0.2, spot=R(35))
    look_at(sp, (4.6, -1.8, 0.0))
    cam = camera(lens=30)

    def up(t):
        k = ease(t, 0.3, 1.5)
        env.location = (lerp(5.3, 4.45, k), -1.8 + 0.05 * k, 0.003)
        env.rotation_euler = (0, 0, R(90 + lerp(0, 14, k)))
        cam_track(cam, t, [(0, (3.0, -0.9, 0.35), (4.8, -1.8, 0.5), 28), (2.6, (3.25, -1.1, 0.28), (4.6, -1.8, 0.2), 32)])
    return up


def s_envelope():
    A, sh = apt_base(density=0.3)
    env = envelope()
    wr = sh.j['wristR']
    env.parent = wr; env.location = (0.0, -0.06, -0.19); env.rotation_euler = (R(-90), R(180), R(0))
    env.scale = (1.4,) * 3
    key = add_light('AREA', 'ekey', (3.3, -3.0, 2.3), 45, (1.0, 0.85, 0.7), 1.0)
    look_at(key, (3.6, -1.9, 1.3))
    cam = camera(lens=40)

    def up(t):
        k = ease(t, 0.0, 0.9)
        sh.pose({'root_loc': (3.6, -1.8, 0), 'root_rot': (0, 0, -30), 'shoulderR': (lerp(-25, -45, k), 22, 12), 'elbowR': (lerp(-40, -70, k), 0, -35),
                 'wristR': (-10, 0, 0), 'fingers': 0.95, 'shoulderL': (-40, -18, -10), 'elbowL': (-70, 0, 30), 'neck': (14, 0, -6),
                 'head': (8, 0, -8)})
        sh.set_face('o' if t < 1.6 else 'smile', look=(-12, -18), brow=0.6, blink=blink_at(t, [2.4]))
        hw = sh.head_world()
        cam_track(cam, t, [(0, (2.5, -2.9, 1.55), (3.55, -1.85, 1.2), 36), (3.3, (2.75, -2.6, 1.5), (3.55, -1.85, 1.15), 42)])
    return up


def s_card():
    A, sh = apt_base(density=0.3)
    cd, txt = card()
    env = envelope()
    wr = sh.j['wristR']
    cd.parent = wr; cd.location = (0.0, -0.05, -0.2); cd.rotation_euler = (R(90), 0, R(0)); cd.scale = (1.6,) * 3
    wl = sh.j['wristL']
    env.parent = wl; env.location = (0.0, -0.02, -0.14); env.rotation_euler = (R(90), 0, R(0)); env.scale = (1.4,) * 3
    key = add_light('AREA', 'ckey', (3.0, -2.6, 2.1), 30, (1.0, 0.85, 0.7), 0.8)
    look_at(key, (3.6, -2.2, 1.2))
    cam = camera(lens=50)

    def up(t):
        k = ease(t, 0.0, 0.8)
        sh.pose({'root_loc': (3.6, -1.8, 0), 'root_rot': (0, 0, -30), 'shoulderR': (-62, 22, 12), 'elbowR': (-78, 0, -35), 'fingers': 0.95,
                 'shoulderL': (-55, -10, -10), 'elbowL': (-70, 0, 30), 'neck': (16, 0, -6), 'head': (8, 0, -8)})
        sh.set_face('smile', look=(-12, -18), brow=0.4)
        bpy.context.view_layer.update()
        from mathutils import Matrix
        mw = cd.matrix_world
        rot = mw.to_quaternion().to_matrix().to_4x4()
        c = mw.translation
        n = (mw.to_quaternion() @ Vector((0, 0, 1))).normalized()
        d = lerp(0.62, 0.5, ease(t, 0.0, 5.5))
        cam.matrix_world = Matrix.Translation(c + n * d) @ rot @ Matrix.Rotation(R(-3 + 2 * t / 5.5), 4, 'Z')
        cam.data.lens = 50
    return up


def s_face():
    A, sh = apt_base(density=0.3)
    key = add_light('AREA', 'fkey', (2.7, -3.0, 2.3), 35, (1.0, 0.85, 0.7), 0.8)
    look_at(key, (3.6, -1.8, 1.5))
    cam = camera(lens=60)

    def up(t):
        k = ease(t, 0.6, 1.6)
        sh.pose({'root_loc': (3.6, -1.8, 0), 'root_rot': (0, 0, -30), 'shoulderR': (-40, 22, 12), 'elbowR': (-70, 0, -35), 'fingers': 0.55,
                 'neck': (lerp(10, -4, k), 0, lerp(-6, 4, k)), 'head': (lerp(6, -6, k), 0, lerp(-6, 8, k))})
        sh.set_face('o' if k < 0.5 else 'open', look=(lerp(-10, 16, k), lerp(-12, 10, k)), brow=lerp(0.2, 0.9, k), brow_tilt=0.5 * k,
                    blink=blink_at(t, [0.35]))
        hw = sh.head_world()
        ang = R(-30)
        fwd = Vector((math.sin(ang), -math.cos(ang), 0))
        cam.location = hw + fwd * lerp(0.75, 0.6, t / 2.9) + Vector((0.0, 0, 0.02))
        look_at(cam, hw + Vector((0, 0, -0.01)))
        cam.data.lens = 60
    return up


def s_dress():
    A, sh = apt_base(density=0.3, outfit='gown')
    key = add_light('AREA', 'dkey', (-2.6, -0.2, 2.6), 60, (1.0, 0.85, 0.75), 1.0)
    look_at(key, (-3.7, -1.6, 1.0))
    sparkle = emission('dspark', (1.0, 0.9, 0.7), 20)
    rg = rnd(3)
    sp = [prim('sphere', 'dsp', (0, 0, 0), scale=(0.012,) * 3, mat=sparkle, seg=6) for _ in range(30)]
    cam = camera(lens=32)

    def up(t):
        spin = ease(t, 0.0, 1.6)
        rot = -90 + 360 * spin
        sh.pose({'root_loc': (-3.7, -1.6, 0), 'root_rot': (0, 0, rot), 'shoulderL': (-10, -55, 0), 'shoulderR': (-10, 55, 0),
                 'elbowL': (-20, 0, 0), 'elbowR': (-20, 0, 0), 'fingers': 0.15, 'neck': (0, 0, 0), 'head': (-4, 0, 0)})
        sh.skirt.scale = (1 + 0.12 * math.sin(math.pi * spin), 1 + 0.12 * math.sin(math.pi * spin), 1)
        sh.set_face('open' if 0.2 < spin < 0.95 else 'smile', look=(0, -2), blink=blink_at(t, [1.8]))
        for i, o in enumerate(sp):
            a = i * 2.4 + t * 3
            r_ = 0.45 + 0.15 * math.sin(i)
            o.location = (-3.7 + math.cos(a) * r_, -1.6 + math.sin(a) * r_, 0.2 + (i % 10) * 0.15 + 0.1 * math.sin(t * 4 + i))
            o.hide_render = not (0.15 < spin < 1.0 or t < 2.0)
        cam_track(cam, t, [(0, (-1.2, -2.4, 1.2), (-3.9, -1.5, 1.0), 30), (2.2, (-1.4, -2.2, 1.25), (-3.9, -1.5, 1.05), 33)])
        handheld(cam, t, 0.004)
    return up


def s_capsule():
    underwater_world(top=(0.02, 0.1, 0.14), mid=(0.004, 0.03, 0.045), bottom=(0.0, 0.0, 0.006))
    M = Mats()
    build_tower(M, None, -140, -175, plates=True)
    a = R(270)
    rx, ry = math.cos(a) * (TOWER_R + 1.6), math.sin(a) * (TOWER_R + 1.6)
    gold = gold_mat('capgold')
    for s in (-1, 1):
        prim('cube', 'rail', (rx + s * 1.0, ry, -560), scale=(0.15, 0.25, 110), mat=gold, bevel=0.03)
    cap = empty('capsule', (rx, ry - 0.2, -520))
    prim('sphere', 'capglass', (0, 0, 0), scale=(1.3, 1.3, 1.6), mat=window_glass('capg', (0.95, 0.97, 1.0), 0.1), parent=cap, seg=48)
    for k in range(6):
        b = 2 * math.pi * k / 6
        pts = [(math.cos(b) * 1.32 * math.cos(th), math.sin(b) * 1.32 * math.cos(th), 1.62 * math.sin(th)) for th in [R(-90 + 180 * j / 16) for j in range(17)]]
        tube(f'caprib{k}', pts, 0.05, 8, gold, None).parent = cap
    prim('torus', 'capring', (0, 0, 0), mat=gold, R=1.32, r=0.1, seg=64, parent=cap)
    prim('cyl', 'capfloor', (0, 0, -0.9), scale=(1.1, 1.1, 0.06), mat=marble_mat('capmarble'), parent=cap)
    prim('cyl', 'capbot', (0, 0, -1.65), scale=(0.35, 0.35, 0.2), mat=gold, parent=cap)
    prim('sphere', 'caplamp', (0, 0, -1.9), scale=(0.25,) * 3, mat=emission('caplampm', (1.0, 0.85, 0.6), 14), parent=cap)
    il = add_light('POINT', 'capin', (0, 0, 0.9), 160, (1.0, 0.75, 0.55), 0.3)
    il.parent = cap; il.location = (0, 0, 0.9)
    sp = add_light('SPOT', 'capbeam', (0, 0, -2.0), 3000, (1.0, 0.85, 0.6), 0.2, spot=R(35))
    sp.parent = cap; sp.location = (0, 0, -2.0); sp.rotation_euler = (R(180), 0, 0)
    beam = godray('beam', (0, 0, -2.0), (0, 0, -30), 0.2, 9, (1.0, 0.85, 0.6), 0.45)
    beam.parent = cap; beam.location = (0, 0, -30); beam.rotation_euler = (0, 0, 0)
    sh = Shelly(outfit='gown')
    sh.root.parent = cap
    sh.pose({'root_loc': (0, 0, -0.84), 'root_rot': (0, 0, 20), 'shoulderL': (0, -10, 0), 'shoulderR': (-30, 20, 0), 'elbowR': (-60, 0, 0)})
    sh.set_face('smile', look=(0, 15))
    for i in range(6):
        jelly(None, f'j{i}', (rnd(i).uniform(-8, 8), rnd(i).uniform(-28, -18), -rnd(i + 3).uniform(510, 600)), rnd(i).uniform(0.7, 1.2), (1.0, 0.65, 0.9), 0, 3.5)
    fog_all(0.03, (0.004, 0.03, 0.045), skip={'beamm'})
    cam = camera(lens=24)

    def up(t):
        z = -523 - 9 * t - 1.5 * t * t
        cap.location = (rx, ry - 0.2, z)
        cam_track(cam, t, [(0, (rx + 4.5, ry - 7.5, -525), (rx, ry, -523.5), 26), (1.7, (rx + 4.2, ry - 7.2, -535), (rx, ry, -537), 26)])
        handheld(cam, t, 0.05)
    return up


def lux_elevator():
    E = Elevator()
    for nm, c, r, met in (('ewood', '#F2E3D3', 0.3, 0.0), ('efloor', '#EDE3DA', 0.1, 0.0)):
        m = D.materials[nm]; b = m.node_tree.nodes[m['bsdf']]
        b.inputs['Base Color'].default_value = (*hexc(c), 1); b.inputs['Roughness'].default_value = r
    set_emit(E.disp_mat, 12, color=(1.0, 0.72, 0.32))
    E.disp_light.data.color = (1.0, 0.75, 0.4)
    set_emit(D.materials['ebtnr'], 6, color=(1.0, 0.75, 0.35))
    return E


def s_liftup():
    world((0.0, 0.0, 0.0), 1.0)
    E = lux_elevator()
    sh = Shelly(outfit='gown')
    ff = add_light('AREA', 'lfill', (0.4, -0.7, 1.6), 15, (1.0, 0.85, 0.75), 0.6)
    look_at(ff, (0.05, 0.1, 1.45))
    cam = camera(lens=30)

    def up(t):
        n = -199 + (0 if t < 2.4 else 0)
        E.disp.data.body = '-199'
        sh.pose({'root_loc': (0.05, 0.1, 0), 'root_rot': (0, 0, -10), 'neck': (-12, 0, 0), 'head': (-10, 0, 0),
                 'shoulderL': (-30, -14, 0), 'elbowL': (-95, 0, 35), 'shoulderR': (-30, 14, 0), 'elbowR': (-95, 0, -35), 'fingers': 0.5,
                 'wristL': (0, 0, 20), 'wristR': (0, 0, -20)})
        sh.set_face('smile', lids_wide=0.3, brow=0.5, look=(0, 22), blink=blink_at(t, [1.4]))
        cam_track(cam, t, [(0, (0.38, -0.72, 1.12), (0.02, 0.1, 1.45), 30), (2.5, (0.3, -0.62, 1.15), (0.02, 0.1, 1.45), 34)])
    return up


def s_display():
    world((0.0, 0.0, 0.0), 1.0)
    E = lux_elevator()
    cam = camera(lens=50)

    def up(t):
        # Start 42.2: "Minus zweihundert" (42.26) ... "zweihunderteins" (44.64) -> t=2.44
        if t < 2.4:
            s = '-200'
        else:
            s = '-201'
        E.disp.data.body = s
        k = ease(t, 2.4, 2.7)
        set_emit(E.disp_mat, 12 + 14 * k * (0.7 + 0.3 * math.sin(t * 6)), color=lerp((1.0, 0.72, 0.32), (1.0, 0.88, 0.6), k))
        E.disp_light.data.energy = 8 + 20 * k
        cam_track(cam, t, [(0, (0.15, -0.2, 2.15), (0, -0.96, 2.45), 40), (3.9, (0.05, -0.32, 2.3), (0, -0.96, 2.45), 44)])
    return up


def s_doors():
    world((0.0, 0.0, 0.0), 1.0)
    E = lux_elevator()
    E.disp.data.body = '-201'
    out = prim('plane', 'outglow', (0, -6, 1.5), rot=(R(90), 0, 0), scale=(8, 6, 1), mat=emission('outglowm', (1.0, 0.72, 0.8), 2.5))
    pl = add_light('AREA', 'outl', (0, -2.0, 1.4), 500, (1.0, 0.85, 0.85), 2.0, rot=(R(-90), 0, 0))
    look_at(pl, (0, 0.5, 1.2))
    ray = godray('dray', (0, -3, 1.4), (0, 1.0, 1.0), 2.0, 0.8, (1.0, 0.9, 0.8), 0.35)
    sh = Shelly(outfit='gown')
    cam = camera(lens=30)

    def up(t):
        k = ease(t, 0.15, 1.3)
        E.set_doors(k)
        pl.data.energy = 500 * k
        ray.hide_render = k < 0.1
        sh.pose({'root_loc': (0.0, 0.15, 0), 'root_rot': (0, 0, 0), 'shoulderL': (-10, -10, 0), 'shoulderR': (-10, 10, 0),
                 'elbowL': (-40, 0, 0), 'elbowR': (-40, 0, 0), 'fingers': 0.3})
        sh.set_face('o', lids_wide=0.6)
        cam_track(cam, t, [(0, (0.55, 0.85, 2.15), (0, -1.5, 1.2), 24), (1.7, (0.5, 0.75, 2.1), (0, -1.5, 1.2), 26)])
    return up


def hall_base():
    world((0.08, 0.05, 0.07), 1.0)
    H = PearlHall()
    sh = Shelly(outfit='gown')
    expo(-0.4)
    return H, sh


def s_reveal():
    H, sh = hall_base()
    cam = camera(lens=20)

    def up(t):
        H.update(t + 50, breathe=0.6, glow=2.0)
        y = lerp(1.0, 4.6, ease(t, 0.0, 2.9))
        walk = 1 - ease(t, 2.3, 2.9)
        p = walk_pose(t, 5.0, walk, {'root_loc': (0, y, 0), 'root_rot': (0, 0, 180)})
        sh.pose(p)
        sh.set_face('o', lids_wide=0.6)
        cam_track(cam, t, [(0, (1.1, 3.0, 0.45), (0, 17, 3.0), 20), (2.9, (2.2, 4.4, 4.2), (0, 15, 1.6), 20)])
        handheld(cam, t, 0.03)
    return up


def s_pearl():
    H, sh = hall_base()
    cam = camera(lens=35)

    def up(t):
        H.update(t + 54, breathe=1.0, glow=2.2)
        sh.pose({'root_loc': (-0.6, 8.5, 0.6), 'root_rot': (0, 0, 180)})
        sh.set_face('o', lids_wide=0.5)
        cam_track(cam, t, [(0, (-2.6, 7.0, 1.0), (0, 17.4, 2.8), 32), (4.4, (-1.8, 8.6, 2.0), (0, 17.4, 2.8), 36)])
        handheld(cam, t, 0.01)
    return up


def s_faceglow():
    H, sh = hall_base()
    cam = camera(lens=45)

    def up(t):
        H.update(t + 57, breathe=1.0, glow=2.2)
        y = lerp(11.6, 12.4, ease(t, 0.5, 4.0))
        sh.pose({'root_loc': (0, y, 0.6), 'root_rot': (0, 0, 180), 'neck': (-8, 0, 0), 'head': (-6, 0, 0),
                 'shoulderL': (-10, -12, 0), 'shoulderR': (-10, 12, 0), 'fingers': 0.4})
        k = ease(t, 1.0, 2.0)
        sh.set_face('smile' if k > 0.5 else 'neutral', lids_wide=0.3, brow=0.4, look=(0, 10), blink=blink_at(t, [0.8, 3.4]))
        hz = 0.6 + 1.42
        cam.location = (0.25 - 0.05 * t / 4.6, y + lerp(1.9, 1.2, t / 4.6), hz - 0.02)
        look_at(cam, (0, y, hz))
        cam.data.lens = lerp(42, 50, t / 4.6)
    return up


def s_reach():
    H, sh = hall_base()
    cam = camera(lens=30)

    def up(t):
        th = max(0, 1 - abs(t - 0.6) / 0.25)
        H.update(t + 61, breathe=0.5, glow=2.2 + 3 * th, seam=0.3 * ease(t, 0.6, 1.4))
        reach = ease(t, 0.0, 0.6)
        sh.pose({'root_loc': (0, 14.45, 0.6), 'root_rot': (0, 0, 180), 'spine': (lerp(-2, -8, reach), 0, 0),
                 'shoulderR': (lerp(-20, -82, reach), 10, 0), 'elbowR': (lerp(-30, -10, reach), 0, 0), 'wristR': (-40, 0, 0),
                 'fingers': lerp(0.4, 0.1, reach), 'neck': (-4, 0, 0)})
        sh.set_face('smile', lids_wide=0.2, brow=0.5, look=(0, 6))
        cam_track(cam, t, [(0, (-2.1, 13.0, 2.0), (0.1, 15.4, 2.2), 26), (1.6, (-1.95, 13.2, 2.0), (0.1, 15.4, 2.2), 28)])
    return up


def s_open():
    H, sh = hall_base()
    cam = camera(lens=26)
    beams = []
    for k in range(9):
        a = R(-70 + k * 17.5)
        d = Vector((math.sin(a), -0.35, math.cos(a))).normalized()
        b = godray(f'obeam{k}', tuple(H.pc + d * 14), tuple(H.pc), 1.8 + (k % 3) * 0.4, 0.15, (1.0, 0.85, 0.55), 0.0)
        beams.append(b)

    def up(t):
        seam = ease(t, 0.0, 0.8)
        op = ease(t, 0.9, 2.7) * 0.6
        H.update(t + 62, breathe=0.3, glow=2.4, open_=op, seam=seam)
        for k, b in enumerate(beams):
            m = b.data.materials[0]
            m.node_tree.nodes[m['st']].inputs[1].default_value = 3.0 * op * (0.8 + 0.2 * math.sin(t * 5 + k))
        rec = ease(t, 0.9, 1.4)
        sh.pose({'root_loc': (0, lerp(14.45, 14.0, rec), 0.6), 'root_rot': (0, 0, 180), 'spine': (lerp(-6, 4, rec), 0, 0),
                 'shoulderR': (lerp(-80, -60, rec), 20, 0), 'elbowR': (lerp(-10, -70, rec), 0, -20), 'wristR': (-30, 0, 0),
                 'shoulderL': (lerp(-10, -50, rec), -20, 0), 'elbowL': (lerp(-20, -80, rec), 0, 20), 'fingers': 0.3})
        sh.set_face('o' if rec > 0.3 else 'smile', lids_wide=rec, brow=0.9 * rec, shell=0.15 * rec)
        cam_track(cam, t, [(0, (2.6, 9.6, 1.4), (0, 15.2, 2.4), 24), (2.7, (2.2, 10.3, 1.6), (0, 15.2, 2.6), 26)])
        handheld(cam, t, 0.01 + 0.02 * rec * (1 - ease(t, 1.4, 2.2)))
    return up


def s_final():
    H, sh = hall_base()
    cam = camera(lens=26)
    beams = []
    for k in range(9):
        a = R(-70 + k * 17.5)
        d = Vector((math.sin(a), -0.35, math.cos(a))).normalized()
        beams.append(godray(f'fbeam{k}', tuple(H.pc + d * 14), tuple(H.pc), 1.8 + (k % 3) * 0.4, 0.15, (1.0, 0.85, 0.55), 0.0))

    def up(t):
        op = 0.6 + 0.04 * ease(t, 0, 5)
        H.update(t + 65, breathe=0.3, glow=2.4, open_=op, seam=1.0)
        for k, b in enumerate(beams):
            m = b.data.materials[0]
            m.node_tree.nodes[m['st']].inputs[1].default_value = 3.0 * op * (0.8 + 0.2 * math.sin(t * 5 + k))
        sh.pose({'root_loc': (0, 14.0, 0.6), 'root_rot': (0, 0, 180), 'shoulderL': (-5, -15, 0), 'shoulderR': (-5, 15, 0)})
        sh.set_face('o', lids_wide=0.6, shell=0.1)
        cam_track(cam, t, [(0, (2.2, 8.6, 0.9), (0, 15.5, 2.5), 24), (5.6, (1.6, 7.2, 1.4), (0, 15.5, 2.7), 24)])
    return up


SHOTS = {n: globals()['s_' + n] for n in NAMES}
