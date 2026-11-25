"""Neue Bausteine fürs Rätsel-Video: Wetter, Bahnhof + Zug, Regenschirm, Knopfleiste, Treppenhaus."""
import bpy, math
from mathutils import Vector, Matrix
from lib import *
from sets import *
from sets_lux import marble_mat, gold_mat, font

R = math.radians
D = bpy.data


# ------------------------------------------------------------------ Wetter an der Oberfläche
def weather(mode):
    """mode 'sun' (heller Morgen) oder 'rain' (grau, nass)."""
    for o in D.objects:
        if o.name.startswith('star') or o.name.startswith('moon'):
            if o.type == 'MESH':
                o.hide_render = True
    ml = D.objects.get('moonlight')
    if mode == 'sun':
        world((0.3, 0.55, 0.95), 1.0, top=(0.1, 0.32, 0.85), bottom=(0.7, 0.8, 0.92))
        if ml:
            ml.data.energy = 4.5; ml.data.color = (1.0, 0.9, 0.75)
            ml.location = (-30, 40, 50); look_at(ml, (0, -16, 0))
        sea = D.materials.get('sea')
        if sea:
            b = sea.node_tree.nodes[sea['bsdf']]; b.inputs['Base Color'].default_value = (*hexc('#0F5C78'), 1)
        sun = prim('sphere', 'daysun', (-300, 600, 330), scale=(26,) * 3, mat=emission('daysunm', (1.0, 0.95, 0.8), 30.0))
        neon = D.materials.get('neonsign')
        if neon: set_emit(neon, 2.0)
    else:
        world((0.3, 0.33, 0.38), 1.0, top=(0.2, 0.22, 0.26), bottom=(0.4, 0.43, 0.47))
        if ml:
            ml.data.energy = 1.2; ml.data.color = (0.75, 0.82, 0.95)
            ml.location = (20, 30, 40); look_at(ml, (0, -16, 0))
        sea = D.materials.get('sea')
        if sea:
            b = sea.node_tree.nodes[sea['bsdf']]; b.inputs['Base Color'].default_value = (*hexc('#14262E'), 1)
            b.inputs['Roughness'].default_value = 0.25
        # Wolkendecke
        cm = principled('cloudm', (0.28, 0.3, 0.33), rough=1.0)
        rg = rnd(4)
        for k in range(26):
            a = rg.uniform(R(20), R(160)); d = rg.uniform(250, 500)
            prim('sphere', 'cloud', (math.cos(a) * d, math.sin(a) * d, rg.uniform(60, 120)), scale=(rg.uniform(60, 120), rg.uniform(40, 80), rg.uniform(15, 30)), mat=cm, seg=16)


# ------------------------------------------------------------------ Bahnhof + Zug
TRACK_Y = -18.6


class Station:
    def __init__(self):
        mar = marble_mat('stmarble', '#F3EFEA', '#A79C94')
        gold = gold_mat('stgold')
        pink = principled('stpink', hexc('#F4A9BE'), rough=0.3, coat=0.5)
        steel = principled('ststeel', hexc('#D6D8DA'), rough=0.3, metal=0.8)
        # Bahnsteig
        prim('cube', 'stdeck', (0, -14.6, 0.1), scale=(11, 2.2, 0.5), mat=mar, bevel=0.03)
        prim('cube', 'stedge', (0, -16.78, 0.61), scale=(11, 0.04, 0.012), mat=emission('stedgem', (1.0, 0.85, 0.4), 4.0))
        prim('cube', 'stgoldedge', (0, -16.8, 0.45), scale=(11.02, 0.05, 0.17), mat=gold)
        # Stützen ins Meer
        for x in (-9, -3, 3, 9):
            prim('cyl', 'stleg', (x, -14.6, -3), scale=(0.45, 0.45, 3.2), mat=mar)
        for x in (-1.9, 1.9):
            prim('cyl', 'stpost', (x, -16.9, 1.8), scale=(0.06, 0.06, 1.2), mat=gold)
        for x in range(-9, 10, 3):
            prim('cyl', 'stlpost', (x, -16.5, 1.6), scale=(0.035, 0.035, 1.0), mat=gold)
            prim('sphere', 'stlamp', (x, -16.5, 2.65), scale=(0.11,) * 3, mat=emission('stlampm', (1.0, 0.85, 0.6), 8.0), seg=12)
        # Schild
        sg = prim('cube', 'stsign', (0, -16.9, 3.05), scale=(1.7, 0.05, 0.28), mat=principled('stsignb', hexc('#141018'), 0.4), bevel=0.02)
        prim('cube', 'stsignf', (0, -16.88, 3.05), scale=(1.78, 0.04, 0.34), mat=gold, bevel=0.02)
        tx = text_obj('stsigntx', 'SUNKEN PEARL  ·  ETAGE 0', 0.22, emission('stsigntxm', (1.0, 0.82, 0.45), 6.0), font=font('FreeSerifBold.ttf'))
        tx.location = (0, -16.96, 3.0); tx.rotation_euler = (R(90), 0, 0)
        # Aufzug-Portal am Dom
        prim('cube', 'stportal', (0, -12.4, 1.75), scale=(1.0, 0.35, 1.15), mat=mar, bevel=0.05)
        self.pdoor = []
        dm = principled('stpdoor', hexc('#E1B45A'), 0.22, 1.0)
        for s in (-1, 1):
            self.pdoor.append((prim('cube', 'stpd', (s * 0.35, -12.77, 1.55), scale=(0.35, 0.03, 0.95), mat=dm, bevel=0.01), s))
        tx0 = text_obj('stp0', '0', 0.35, emission('stp0m', (1.0, 0.82, 0.45), 8.0), font=font('FreeSerifBold.ttf'))
        tx0.location = (0, -12.78, 2.7); tx0.rotation_euler = (R(90), 0, 0)
        # Gleis (Monorail-Balken)
        prim('cube', 'track', (0, TRACK_Y, -0.35), scale=(260, 0.55, 0.35), mat=steel, bevel=0.05)
        prim('cube', 'trackg', (0, TRACK_Y, -0.02), scale=(260, 0.6, 0.03), mat=gold)
        for x in range(-240, 241, 24):
            prim('cyl', 'trleg', (x, TRACK_Y, -4), scale=(0.45, 0.45, 3.8), mat=steel)
        add_light('AREA', 'stlight', (0, -15.0, 3.3), 300, (1.0, 0.85, 0.65), 6.0, rot=(0, 0, 0))

    def set_portal(self, k):
        for d, s in self.pdoor:
            d.location.x = s * (0.35 + 0.66 * k)


class Train:
    """3 Wagen, Fahrtrichtung -X, Türen auf +Y-Seite (zum Bahnsteig)."""

    def __init__(self, ncar=3):
        self.root = empty('train', (0, TRACK_Y, 0))
        body = principled('trbody', hexc('#F7F2EE'), rough=0.18, coat=1.0, film=420, film_ior=1.4)
        gold = gold_mat('trgold')
        pink = principled('trpink', hexc('#F09AB3'), rough=0.25, coat=0.6)
        win = principled('trwin', hexc('#1A2A33'), rough=0.05, coat=1.0, emit=(1.0, 0.78, 0.5), emit_str=0.6)
        L, Wd, Hh = 8.2, 1.4, 1.5
        self.doors = []
        for c in range(ncar):
            x = c * (2 * L + 0.4)
            car = empty(f'car{c}', (x, 0, 0), parent=self.root)
            prim('cube', 'trb', (0, 0, 1.72), scale=(L, Wd, Hh), mat=body, bevel=0.55, seg=6, parent=car)
            # Fensterband
            prim('cube', 'trw', (0, Wd - 0.03, 2.25), scale=(L - 0.7, 0.04, 0.42), mat=win, bevel=0.05, parent=car)
            prim('cube', 'trw2', (0, -Wd + 0.03, 2.25), scale=(L - 0.7, 0.04, 0.42), mat=win, bevel=0.05, parent=car)
            # Goldstreifen
            for s in (-1, 1):
                prim('cube', 'trs', (0, s * (Wd + 0.005), 1.35), scale=(L - 0.3, 0.02, 0.06), mat=gold, parent=car)
                prim('cube', 'trs2', (0, s * (Wd + 0.005), 0.55), scale=(L - 0.4, 0.02, 0.18), mat=pink, parent=car)
            # Türen (+Y) bei x = -4 und +4
            for dx in (-4.0, 4.0):
                for s in (-1, 1):
                    d = prim('cube', 'trd', (dx + s * 0.42, Wd + 0.03, 1.6), scale=(0.42, 0.03, 1.02), mat=pink, bevel=0.03, parent=car)
                    prim('cube', 'trdw', (0, 0.035, 0.35), scale=(0.25, 0.01, 0.4), mat=win, parent=d)
                    self.doors.append((d, s, dx))
            # Innenlicht
            il = add_light('POINT', 'trin', (0, 0, 2.6), 120, (1.0, 0.8, 0.55), 1.0)
            il.parent = car; il.location = (0, 0, 2.6)
            # Fahrwerk
            prim('cube', 'trbogie', (0, 0, 0.18), scale=(L - 1.2, 0.7, 0.2), mat=principled('trbog', hexc('#2A2A30'), 0.4, 0.6), parent=car)
        # Nase vorne (-X)
        nose = prim('sphere', 'trnose', (-L - 0.6, 0, 1.72), scale=(2.4, Wd, Hh), mat=body, seg=40, parent=self.root)
        prim('sphere', 'trnosew', (-L - 1.6, 0, 2.15), scale=(1.45, Wd * 0.82, 0.55), mat=win, seg=32, parent=self.root)
        prim('sphere', 'trlampL', (-L - 2.75, 0.6, 1.3), scale=(0.12,) * 3, mat=emission('trlampm', (1.0, 0.95, 0.8), 30), parent=self.root)
        prim('sphere', 'trlampR', (-L - 2.75, -0.6, 1.3), scale=(0.12,) * 3, mat=D.materials['trlampm'], parent=self.root)
        xe = (ncar - 1) * (2 * L + 0.4)
        prim('sphere', 'trtail', (xe + L + 0.6, 0, 1.72), scale=(2.0, Wd, Hh), mat=body, seg=40, parent=self.root)

    def set_doors(self, k):
        for d, s, dx in self.doors:
            d.location.x = dx + s * (0.42 + 0.8 * k)


# ------------------------------------------------------------------ Regenschirm
class Umbrella:
    """Ursprung = Griff. Schaft entlang +Z. open_ 0 (zu) .. 1 (offen)."""

    def __init__(self, name='umb', size=1.0):
        s = size
        self.root = empty(name)
        self.root['size'] = size
        pink = principled(name + 'pink', hexc('#F27FA3'), rough=0.35, sheen=0.5)
        pink2 = principled(name + 'pink2', hexc('#FFD3DF'), rough=0.35)
        gold = gold_mat(name + 'gold')
        self.mats = (pink, pink2, gold)
        # Griff (J-Haken) + Schaft
        hook = [(0, 0, 0.12 * s), (0, 0, 0), (0, 0.02 * s, -0.06 * s), (0, 0.07 * s, -0.085 * s), (0, 0.11 * s, -0.06 * s), (0, 0.115 * s, -0.03 * s)]
        tube(name + 'hook', hook, 0.016 * s, 10, gold, None).parent = self.root
        sh = prim('cyl', name + 'shaft', (0, 0, 0.5 * s), scale=(0.009 * s, 0.009 * s, 0.4 * s), mat=gold, parent=self.root)
        prim('cyl', name + 'tip', (0, 0, 0.94 * s), scale=(0.006 * s, 0.006 * s, 0.05 * s), mat=gold, parent=self.root)
        prim('sphere', name + 'tipb', (0, 0, 0.99 * s), scale=(0.012 * s,) * 3, mat=gold, parent=self.root)
        # Offener Schirm: 8 Bahnen, gewellter Rand
        verts, faces = [], []
        nr, na = 8, 64
        Rr, Hc = 0.55 * s, 0.24 * s
        verts.append((0, 0, 0.9 * s))
        for i in range(1, nr + 1):
            u = i / nr
            for j in range(na):
                a = 2 * math.pi * j / na
                scal = 1 - 0.08 * u * abs(math.cos(4 * a)) ** 0.5 * 0
                rr = Rr * u * (1 - 0.06 * u * (1 - abs(math.cos(4 * a))))
                z = 0.9 * s - Hc * u ** 1.6 + 0.03 * s * u * (1 - abs(math.cos(4 * a)))
                verts.append((rr * math.cos(a), rr * math.sin(a), z))
        for j in range(na):
            faces.append((0, 1 + j, 1 + (j + 1) % na))
        for i in range(nr - 1):
            for j in range(na):
                a0 = 1 + i * na + j; a1 = 1 + i * na + (j + 1) % na
                faces.append((a0, a0 + na, a1 + na, a1))
        cm = color_ramp_mat(name + 'canm', [(0.0, hexc('#FFD3DF')), (0.55, hexc('#F7A1BA')), (1.0, hexc('#E85C8A'))], coord='Z',
                            lo=0.66 * s, hi=0.9 * s, rough=0.35, coat=0.3)
        self.canopy = mesh_obj(name + 'canopy', verts, faces, cm)
        sol = self.canopy.modifiers.new('sol', 'SOLIDIFY'); sol.thickness = 0.006 * s
        self.canopy.parent = self.root
        # Rippen-Spitzen
        self.tips = []
        for k in range(8):
            a = 2 * math.pi * k / 8
            p = prim('sphere', name + 'rtip', (Rr * math.cos(a) * 0.95, Rr * math.sin(a) * 0.95, 0.9 * s - Hc + 0.01 * s), scale=(0.012 * s,) * 3, mat=gold, parent=self.root)
            self.tips.append(p)
        # Zugeklappt: schlanke Hülle
        self.furled = lathe(name + 'furl', [(0.0, 0.3 * s), (0.035 * s, 0.38 * s), (0.045 * s, 0.6 * s), (0.02 * s, 0.86 * s), (0.0, 0.9 * s)], 24, pink)
        self.furled.parent = self.root
        prim('torus', name + 'band', (0, 0, 0.55 * s), mat=gold, R=0.045 * s, r=0.006 * s, seg=24, parent=self.root)
        self.band = D.objects[name + 'band']
        self.set_open(0)

    def set_open(self, k):
        op = k > 0.02
        self.canopy.hide_render = not op
        for p in self.tips: p.hide_render = not op
        self.furled.hide_render = op
        self.band.hide_render = op
        if op:
            sc = 0.15 + 0.85 * k
            self.canopy.scale = (sc, sc, 1.0 + 1.4 * (1 - k))
            self.canopy.location = (0, 0, 0.9 * (1 - (1.0 + 1.4 * (1 - k))) * 0)
            for i, p in enumerate(self.tips):
                a = 2 * math.pi * i / 8
                p.location = (0.52 * sc * math.cos(a), 0.52 * sc * math.sin(a), p.location.z)

    def hold_upright(self, sh, side='R', lift=0.0):
        bpy.context.view_layer.update()
        w = sh.j['wrist' + side].matrix_world
        p = w @ Vector((0, 0, -0.05))
        self.root.matrix_world = Matrix.Translation(p + Vector((0, 0, lift))) @ Matrix.Rotation(R(0), 4, 'X')

    def hold_along_arm(self, sh, side='R'):
        bpy.context.view_layer.update()
        w = sh.j['wrist' + side].matrix_world
        p = w @ Vector((0, 0, -0.05))
        rot = w.to_3x3().normalized().to_4x4() @ Matrix.Rotation(R(180), 4, 'X')
        sc = sh.root.scale.x
        self.root.matrix_world = Matrix.Translation(p) @ rot @ Matrix.Translation((0, 0, -0.1 * sc))

    def hold_cane(self, sh, side='R', fwd=Vector((0.25, -1, 0))):
        bpy.context.view_layer.update()
        w = sh.j['wrist' + side].matrix_world
        p = w @ Vector((0, 0, -0.05))
        L = 0.99 * self.root.get('size', 0.85)
        h = max(0.05, p.z - (sh.root.location.z))
        horiz = math.sqrt(max(0.0, L * L - h * h))
        f = fwd.normalized()
        tip = Vector((p.x + f.x * horiz, p.y + f.y * horiz, sh.root.location.z))
        d = (tip - p).normalized()
        q = d.to_track_quat('Z', 'Y')
        self.root.matrix_world = Matrix.Translation(p) @ q.to_matrix().to_4x4()

    def hold_aim(self, sh, target, k, side='R', fwd=Vector((0.3, -1, 0))):
        """k 0: wie Gehstock, 1: Spitze zeigt auf target."""
        self.hold_cane(sh, side, fwd)
        bpy.context.view_layer.update()
        p = self.root.matrix_world.translation.copy()
        d0 = (self.root.matrix_world.to_3x3() @ Vector((0, 0, 1))).normalized()
        d1 = (target - p).normalized()
        d = d0.lerp(d1, k).normalized()
        L = 0.99 * self.root.get('size', 0.85)
        if k > 0.99:
            p = target - d1 * L
        self.root.matrix_world = Matrix.Translation(p) @ d.to_track_quat('Z', 'Y').to_matrix().to_4x4()

    def tip_world(self):
        bpy.context.view_layer.update()
        return self.root.matrix_world @ Vector((0, 0, 0.99))


# ------------------------------------------------------------------ Knopfleiste im Aufzug
def big_panel(E):
    """Ersetzt das Bedienfeld: hohe Leiste mit 0 ... -200 (21 Knöpfe)."""
    for o in [E.panel] + list(E.panel.children_recursive):
        o.hide_render = True
    a = R(-90 + 42)
    bp = empty('bigpanel', (math.cos(a) * 0.985, math.sin(a) * 0.985, 0), (0, 0, a + R(90)))
    gold = gold_mat('bpgold', '#E9B84C', 0.18)
    prim('cube', 'bpplate', (0, 0, 1.22), scale=(0.15, 0.012, 0.86), mat=gold, bevel=0.012, parent=bp)
    prim('cube', 'bpinner', (0, 0.013, 1.22), scale=(0.13, 0.004, 0.83), mat=principled('bpblk', hexc('#1A1418'), 0.3, coat=0.8), parent=bp)
    fnt = font('FreeSerifBold.ttf')
    lblm = emission('bplbl', (1.0, 0.9, 0.7), 3.0)
    off = principled('bpoff', hexc('#F4EBDD'), rough=0.2, coat=0.8)
    self_btn = {}
    zs = {}
    for i in range(21):
        z = 1.98 - i * 0.074
        n = -10 * i
        m = off
        if i in (0, 10):
            m = emission(f'bpon{i}', (1.0, 0.75, 0.35), 0.0)
            mm = m
        b = prim('cyl', f'bpbtn{i}', (-0.04, 0.02, z), rot=(R(90), 0, 0), scale=(0.024, 0.024, 0.008), mat=m, parent=bp)
        prim('torus', f'bpring{i}', (-0.04, 0.02, z), rot=(R(90), 0, 0), mat=gold, R=0.026, r=0.004, seg=24, parent=bp)
        lab = text_obj(f'bplab{i}', '0' if n == 0 else f'−{abs(n)}', 0.032 if i else 0.04, lblm, font=fnt, align='RIGHT')
        lab.parent = bp; lab.location = (-0.005, 0.019, z); lab.rotation_euler = (R(90), 0, R(180))
        self_btn[i] = b; zs[i] = z
    # Stern über der 0
    st = text_obj('bpstar', '★', 0.04, emission('bpstarm', (1.0, 0.8, 0.4), 5.0), font=font('FreeSerif.ttf'))
    st.parent = bp; st.location = (-0.04, 0.019, 2.04); st.rotation_euler = (R(90), 0, R(180))
    bp['zs'] = [zs[i] for i in range(21)]
    return bp, self_btn


def panel_world(bp, i, push=0.0):
    bpy.context.view_layer.update()
    return bp.matrix_world @ Vector((-0.04, 0.03 + push, bp['zs'][i]))


# ------------------------------------------------------------------ Treppenhaus
class Stairs:
    """Gerade Treppe entlang +X, Stufe 0 bei x=0. Laufrichtung +X."""
    RISE, RUN, N = 0.17, 0.3, 18

    def __init__(self):
        mar = marble_mat('stmar', '#EFE9E2', '#9A8F86')
        wall = marble_mat('stwall', '#E7DCD2', '#B3A69B', scale=0.9)
        gold = gold_mat('stgold2')
        for i in range(self.N):
            prim('cube', 'step', (i * self.RUN + self.RUN / 2, 0, i * self.RISE + self.RISE / 2 - 0.0), scale=(self.RUN / 2 + 0.01, 0.8, self.RISE / 2), mat=mar, bevel=0.008)
            prim('cube', 'nose', (i * self.RUN + self.RUN, -0.0, (i + 1) * self.RISE - 0.006), scale=(0.012, 0.8, 0.006), mat=gold)
        top = self.N * self.RISE
        prim('cube', 'landing', (self.N * self.RUN + 1.2, 0, top - 0.5), scale=(1.2, 0.8, 0.5), mat=mar)
        prim('cube', 'botfloor', (-2.0, 0, -0.1), scale=(2.0, 0.8, 0.1), mat=mar)
        # Wände
        prim('cube', 'wback', (2.5, 0.9, 3), scale=(7, 0.1, 5), mat=wall)
        # Geländer
        rail = [(-0.2 + i * 0.6, -0.72, 0.95 + max(0, (-0.2 + i * 0.6)) / self.RUN * self.RISE) for i in range(11)]
        tube('handrail', rail, 0.025, 10, gold, None)
        for i in range(0, self.N, 2):
            x = i * self.RUN + 0.15
            prim('cyl', 'baluster', (x, -0.72, (i + 1) * self.RISE + 0.45), scale=(0.012, 0.012, 0.47), mat=gold)
        # Wandschilder
        self.signs = []
        for k, (x, n) in enumerate(((-1.6, '−100'), (5.9, '−99'))):
            z = (max(0, x) / self.RUN) * self.RISE + 1.9 if x > 0 else 1.9
            prim('cube', 'signb', (x, 0.79, z), scale=(0.55, 0.02, 0.3), mat=gold, bevel=0.02)
            prim('cube', 'signi', (x, 0.77, z), scale=(0.5, 0.01, 0.25), mat=principled('signin', hexc('#1A1418'), 0.4))
            tx = text_obj('signtx', n, 0.32, emission('signtxm', (1.0, 0.82, 0.45), 6.0), font=font('FreeSerifBold.ttf'))
            tx.location = (x, 0.755, z - 0.02); tx.rotation_euler = (R(90), 0, 0)
        # Wandleuchten
        for x in (-1.0, 2.0, 5.0):
            z = max(0, x) / self.RUN * self.RISE + 2.4
            prim('sphere', 'sconce', (x, 0.75, z), scale=(0.09, 0.05, 0.12), mat=emission('sconcem', (1.0, 0.8, 0.55), 10), seg=16)
            add_light('POINT', 'sconl', (x, 0.5, z), 40, (1.0, 0.78, 0.5), 0.2)

    def height_at(self, x):
        if x <= 0: return 0.0
        return min(self.N, x / self.RUN) * self.RISE
