"""Rätsel-Video: Shelly, der Aufzug und der Regenschirm."""
import bpy, math
from mathutils import Vector, Matrix
from lib import *
from sets import *
from sets_ext import Surface
from sets_lux import *
from shelly import Shelly
import shots as S1
from shots import cam_track, handheld, blink_at, walk_pose, expo, lux_elevator, apt_base
from sets_r import *

R = math.radians
FPS = 24
SC = 0.62  # Shelly ist klein

CUTS = [0.0, 5.05, 8.45, 10.35, 13.25, 16.35, 20.6, 22.45, 26.8, 31.35, 34.7, 38.1, 44.0, 49.6, 52.4]
NAMES = ['hook', 'deep', 'small', 'morning', 'station', 'rainlift', 'raintrain', 'sunlift', 'stairs', 'why', 'count',
         'reach', 'umbrella', 'end']


def shot_range(name):
    i = NAMES.index(name)
    return CUTS[i], CUTS[i + 1]


def surface_base(mode, train_x=4.0):
    world((0.05, 0.08, 0.15), 1.0)
    Su = Surface()
    Su.ocean.wave_scale = 0.45; Su.ocean.choppiness = 0.8
    D.objects['ocean'].location.z = -0.45
    weather(mode)
    St = Station()
    T = Train()
    T.root.location.x = train_x
    return Su, St, T


def handbag(sh, side='L'):
    wr = sh.j['wrist' + side]
    m = principled('bagm', hexc('#F27FA3'), rough=0.3, coat=0.8)
    g = gold_mat('baggold')
    b = empty('bag', parent=wr)
    b.location = (0, 0, -0.16)
    prim('cube', 'bagbody', (0, 0, -0.06), scale=(0.035, 0.09, 0.065), mat=m, bevel=0.02, parent=b)
    tube('baghandle', [(0, -0.05, -0.0), (0, -0.03, 0.06), (0, 0.03, 0.06), (0, 0.05, 0.0)], 0.006, 8, g, None).parent = b
    prim('sphere', 'bagclasp', (0.036, 0, -0.03), scale=(0.012,) * 3, mat=g, parent=b)
    return b


# ===================================================================== Shots
def s_hook():
    Su, St, T = surface_base('sun', 70)
    cam = camera(lens=30)

    def up(t):
        Su.update(2 + t)
        T.root.location.x = 70 - 16 * t
        k = ease(t, 0, 5.05)
        cam.location = Vector((34, -58, 14)).lerp(Vector((16, -36, 4.5)), k)
        look_at(cam, Vector((0, -8, 3)).lerp(Vector((0, -10, 3.5)), k))
        cam.data.lens = lerp(28, 30, k)
        handheld(cam, t, 0.03)
    return up


def s_deep():
    return S1.s_descent()


def s_small():
    A, sh = apt_base(density=0.8)
    sh.root.scale = (SC,) * 3
    cam = camera(lens=22)

    def up(t):
        sh.pose({'root_loc': (0.4, 2.0, 0), 'root_rot': (0, 0, 15), 'neck': (14, 0, -6), 'head': (10, 0, 0),
                 'shoulderL': (-6, -12, 0), 'shoulderR': (-6, 12, 0), 'fingers': 0.3})
        sh.set_face('smile', lids_wide=0.5, brow=0.5, look=(0, 18), blink=blink_at(t, [1.1]))
        cam_track(cam, t, [(0, (1.6, -2.8, 0.35), (0.2, 3.0, 1.9), 22), (1.9, (1.4, -2.4, 0.38), (0.2, 3.0, 1.9), 22)])
    return up


def s_morning():
    A, sh = apt_base(density=0.6)
    sh.root.scale = (SC,) * 3
    bag = handbag(sh)
    cam = camera(lens=32)

    def up(t):
        y = 1.6 - 0.62 * t
        p = walk_pose(t, 7.0, 0.9, {'root_loc': (0.6, y, 0), 'root_rot': (0, 0, 0), 'elbowL': (-60, 0, 0), 'shoulderL': (-10, -10, 0)})
        sh.pose(p)
        sh.set_face('smile', look=(0, 4), blink=blink_at(t, [1.7]))
        cam.location = (1.25, y - 2.4, 0.75)
        look_at(cam, (0.55, y, 0.62))
        handheld(cam, t, 0.004)
    return up


def s_station():
    Su, St, T = surface_base('sun', 60)
    cam = camera(lens=26)

    def up(t):
        Su.update(10 + t)
        k = ease(t, 0, 2.8)
        T.root.location.x = 4 + 56 * (1 - k) ** 2
        T.set_doors(ease(t, 2.75, 3.1))
        cam_track(cam, t, [(0, (-6.0, -14.2, 1.5), (8, -17.6, 1.9), 24), (3.1, (-5.6, -14.0, 1.6), (2, -17.6, 1.9), 26)])
        handheld(cam, t, 0.01)
    return up


def elevator_base(sun=False):
    world((0.0, 0.0, 0.0), 1.0)
    E = lux_elevator()
    bp, btn = big_panel(E)
    sh = Shelly()
    sh.root.scale = (SC,) * 3
    ff = add_light('AREA', 'lfill', (0.4, -0.7, 1.6), 12, (1.0, 0.85, 0.75), 0.6)
    look_at(ff, (0.05, 0.1, 0.9))
    return E, bp, btn, sh


def s_rainlift():
    E, bp, btn, sh = elevator_base()
    U = Umbrella('umb', 0.85)
    cam = camera(lens=28)

    def up(t):
        sh.pose({'root_loc': (-0.15, 0.15, 0), 'root_rot': (0, 0, -8), 'shoulderR': (-10, 18, 0), 'elbowR': (-35, 0, 0), 'wristR': (0, 0, 0),
                 'shoulderL': (-10, -10, 0), 'fingers': 0.85, 'neck': (12, 0, 0), 'head': (8, 0, 0)})
        sh.set_face('smile', look=(0, 22), lids_wide=0.3, blink=blink_at(t, [2.0]))
        U.set_open(0)
        U.hold_cane(sh, fwd=Vector((0.35, -1, 0)))
        cam_track(cam, t, [(0, (0.45, -0.88, 0.62), (-0.22, 0.15, 0.6), 20), (4.25, (0.4, -0.8, 0.66), (-0.22, 0.15, 0.62), 22)])
        handheld(cam, t, 0.003)
    return up


def s_raintrain():
    Su, St, T = surface_base('rain', 4.0)
    T.set_doors(1.0)
    sh = Shelly()
    sh.root.scale = (SC,) * 3
    U = Umbrella('umb', 0.95)
    key = add_light('AREA', 'rkey', (2.0, -13.6, 2.2), 80, (1.0, 0.85, 0.75), 1.0)
    look_at(key, (0.2, -15.6, 1.0))
    cam = camera(lens=30)

    def up(t):
        Su.update(20 + t)
        y = -14.9 - 0.75 * t
        sh.pose(walk_pose(t, 7.0, 0.9, {'root_loc': (0.15, y, 0.6), 'root_rot': (0, 0, -8), 'shoulderR': (-35, 14, 0), 'elbowR': (-80, 0, -30),
                                         'fingers': 0.9}))
        sh.set_face('smile', look=(0, 0))
        U.set_open(1.0)
        U.hold_upright(sh)
        cam_track(cam, t, [(0, (2.6, -13.4, 1.1), (0.1, -16.4, 1.3), 28), (1.85, (2.3, -13.8, 1.15), (0.1, -16.9, 1.3), 30)])
        handheld(cam, t, 0.006)
    return up


def s_sunlift():
    E, bp, btn, sh = elevator_base()
    cam = camera(lens=28)

    def up(t):
        stop = ease(t, 3.4, 3.9)
        sh.pose({'root_loc': (-0.15, 0.15, 0), 'root_rot': (0, 0, -8), 'shoulderR': (-6, 14, 0), 'shoulderL': (-6, -14, 0),
                 'elbowL': (-14 - 60 * stop, 0, 20 * stop), 'elbowR': (-14 - 60 * stop, 0, -20 * stop), 'fingers': 0.3,
                 'neck': (12 - 16 * stop, 0, 0), 'head': (8 - 8 * stop, 0, 0), 'spine': (4 * stop, 0, 0)})
        sh.set_face('worry' if t > 3.5 else 'smile', look=(0, 22 - 22 * stop), brow=0.4 * stop, brow_tilt=0.7 * stop, blink=blink_at(t, [1.6, 3.95]))
        cam_track(cam, t, [(0, (0.42, -0.78, 0.7), (-0.1, 0.2, 0.85), 26), (4.35, (0.32, -0.6, 0.76), (-0.1, 0.2, 0.8), 32)])
        handheld(cam, t, 0.003)
    return up


def stairs_base():
    world((0.05, 0.04, 0.04), 1.0)
    St = Stairs()
    sh = Shelly()
    sh.root.scale = (SC,) * 3
    add_light('AREA', 'skey', (1.5, -3.0, 4.0), 200, (1.0, 0.88, 0.78), 3.0)
    look_at(D.objects['skey'], (1.5, 0, 0.8))
    expo(-0.3)
    return St, sh


def s_stairs():
    St, sh = stairs_base()
    cam = camera(lens=30)

    def up(t):
        x = -0.8 + 0.92 * t
        z = St.height_at(x + 0.05)
        sh.pose(walk_pose(t, 6.0, 1.0, {'root_loc': (x, -0.05, z), 'root_rot': (0, 0, 90), 'spine': (10, 0, 0), 'neck': (-4, 0, 0),
                                       'kneeL': (max(0, -math.sin(t * 6)) * 50 + 14, 0, 0), 'kneeR': (max(0, math.sin(t * 6)) * 50 + 14, 0, 0)}))
        sh.set_face('worry', brow=0.3, brow_tilt=0.8, look=(0, -4), blink=blink_at(t, [2.2]))
        cam.location = (x + 0.7, -1.9, z + 0.75)
        look_at(cam, (x + 0.25, 0, z + 0.62))
        cam.data.lens = 30
        handheld(cam, t, 0.01)
    return up


def s_why():
    St, sh = stairs_base()
    cam = camera(lens=40)
    x = St.N * St.RUN + 0.5
    z = St.N * St.RISE

    def up(t):
        k = ease(t, 0.0, 0.5)
        sh.pose({'root_loc': (x, -0.1, z), 'root_rot': (0, 0, -10), 'shoulderL': (-10, -30 * k, -20 * k), 'shoulderR': (-10, 30 * k, 20 * k),
                 'elbowL': (-70 * k, 0, 40 * k), 'elbowR': (-70 * k, 0, -40 * k), 'wristL': (0, 0, 30 * k), 'wristR': (0, 0, -30 * k),
                 'fingers': 0.1, 'neck': (0, 0, -8 * k), 'head': (0, 12 * k, 0), 'spine': (4 * math.sin(t * 5) * (1 - k * 0.5), 0, 0)})
        sh.set_face('o' if t < 1.6 else 'worry', lids_wide=0.4, brow=0.8, brow_tilt=0.6, look=(0, 4), blink=blink_at(t, [2.4]))
        hw = sh.head_world()
        cam.location = hw + Vector((0.15, -1.6 + 0.2 * t / 3.35, -0.25))
        look_at(cam, hw + Vector((0, 0, -0.18)))
    return up


def s_count():
    E, bp, btn, sh = elevator_base()
    sh.root.location = (0, 0, -20)
    cam = camera(lens=35)

    def up(t):
        sh.root.location = (0, 0, -20)
        c = panel_world(bp, 10)
        nrm = (bp.matrix_world.to_3x3() @ Vector((0, 1, 0))).normalized()
        d = lerp(1.05, 0.7, t / 3.4)
        cam.location = c + nrm * d + Vector((-0.15, 0, -0.1))
        look_at(cam, c + Vector((0, 0, 0.08)))
        cam.data.lens = 30
    return up


def panel_pose(bp, side_off=0.36):
    c = panel_world(bp, 10)
    nrm = (bp.matrix_world.to_3x3() @ Vector((0, 1, 0))).normalized()
    p = c + nrm * side_off
    # Shelly blickt entgegen der Normalen
    face = -nrm
    rot = math.degrees(math.atan2(face.x, -face.y))
    return Vector((p.x, p.y, 0)), rot, nrm


def s_reach():
    E, bp, btn, sh = elevator_base()
    pos, rot, nrm = panel_pose(bp)
    cam = camera(lens=26)
    on = D.materials['bpon10']

    def up(t):
        # 0-3.4 streckt sich zur 0 (Zehenspitzen), dann drückt -100
        a = ease(t, 0.2, 1.0) * (1 - ease(t, 3.0, 3.6))
        b = ease(t, 3.4, 4.0)
        tiptoe = 0.05 * a * (0.8 + 0.2 * math.sin(t * 9))
        sh.pose({'root_loc': (pos.x, pos.y, 0), 'root_rot': (0, 0, rot - 55), 'hips_loc': (0, 0, 0.74 + tiptoe),
                 'shoulderR': (lerp(lerp(-6, -128, a), -95, b), 14, lerp(-25 * a, 0, b)), 'elbowR': (lerp(-14, -2, a) - 10 * b, 0, 0), 'wristR': (-20 * a, 0, 0),
                 'ankleL': (40 * a, 0, 0), 'ankleR': (40 * a, 0, 0),
                 'spine': (-6 * a, 0, -6 * a), 'neck': (24 * a + 8 * b, 0, 0), 'head': (12 * a, 0, 0), 'fingers': lerp(0.3, 0.05, a) + 0.4 * b})
        sh.set_face('worry' if a > 0.5 else 'smile', look=(0, 30 * a + 10 * b), brow=0.6 * a, brow_tilt=0.6 * a, blink=blink_at(t, [2.5, 5.2]))
        set_emit(on, 12 * ease(t, 3.9, 4.05))
        c = panel_world(bp, 8)
        cam.location = c + nrm * 1.35 + Vector((0, 0, -0.4)) + (bp.matrix_world.to_3x3() @ Vector((-0.5, 0, 0)))
        look_at(cam, c + nrm * 0.3 + Vector((0, 0, -0.25)))
        cam.data.lens = 17
        handheld(cam, t, 0.003)
    return up


def s_umbrella():
    E, bp, btn, sh = elevator_base()
    pos, rot, nrm = panel_pose(bp, 0.42)
    U = Umbrella('umb', 0.85)
    cam = camera(lens=26)
    on0 = D.materials['bpon0']

    def up(t):
        a = ease(t, 1.2, 3.0)
        push = ease(t, 3.7, 3.9) * (1 - ease(t, 4.2, 4.5))
        sh.pose({'root_loc': (pos.x, pos.y, 0), 'root_rot': (0, 0, rot - 50), 'shoulderR': (lerp(-30, -150 - 6 * push, a), lerp(16, 4, a), 0),
                 'elbowR': (lerp(-70, -4, a), 0, lerp(-20, 0, a)), 'wristR': (lerp(0, -26, a), 0, 0), 'fingers': 0.9,
                 'neck': (20 * a, 0, 0), 'head': (10 * a, 0, 0), 'spine': (-4 * a, 0, 0)})
        sh.set_face('smile' if t < 1.0 or t > 4.0 else 'neutral', look=(0, 28 * a), brow=0.3 + 0.4 * ease(t, 4.0, 4.3), blink=blink_at(t, [0.7, 5.0]))
        U.set_open(0)
        U.hold_aim(sh, panel_world(bp, 0, -0.01 + 0.02 * (1 - push)), ease(t, 1.0, 3.2))
        set_emit(on0, 14 * ease(t, 3.85, 4.0))
        c = panel_world(bp, 8)
        cam.location = c + nrm * 1.35 + Vector((0, 0, -0.4)) + (bp.matrix_world.to_3x3() @ Vector((-0.5, 0, 0)))
        look_at(cam, c + nrm * 0.3 + Vector((0, 0, -0.25)))
        cam.data.lens = 17
        handheld(cam, t, 0.003)
    return up


def s_end():
    Su, St, T = surface_base('rain', 4.0)
    T.set_doors(1.0)
    sh = Shelly()
    sh.root.scale = (SC,) * 3
    U = Umbrella('umb', 0.95)
    key = add_light('AREA', 'rkey', (0.8, -13.0, 1.8), 90, (1.0, 0.85, 0.75), 1.0)
    look_at(key, (0.0, -15.8, 1.0))
    cam = camera(lens=34)

    def up(t):
        Su.update(30 + t)
        k = ease(t, 0.0, 0.8)
        sh.pose({'root_loc': (0.0, -16.2, 0.6), 'root_rot': (0, 0, 180 * k), 'shoulderR': (-35, 14, 0), 'elbowR': (-80, 0, -30),
                 'shoulderL': (-20 - 120 * ease(t, 0.9, 1.3), -20, 0), 'elbowL': (-30, 0, 20 + 25 * math.sin(t * 9) * ease(t, 1.2, 1.4)), 'fingers': 0.9})
        sh.set_face('smile', look=(0, 6), lids_wide=0.2, blink=blink_at(t, [2.2]))
        U.set_open(1.0)
        U.hold_upright(sh)
        hw = sh.head_world()
        cam.location = Vector((0.35, -13.6, 1.05)) + Vector((0, 0.25 * t / 2.8, 0))
        look_at(cam, Vector((0.0, -16.2, 1.05)))
        handheld(cam, t, 0.005)
    return up


SHOTS = {n: globals()['s_' + n] for n in NAMES}
