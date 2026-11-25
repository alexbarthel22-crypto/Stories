"""Shelly – Frau mit Muschelkopf. Aufbau aus Primitiven mit Gelenk-Hierarchie (Blick nach -Y)."""
import bpy, math
from mathutils import Vector
from lib import *

R = math.radians


def scallop(name, radius=0.42, spread=82, ribs=19, depth=0.12, rib_amp=0.012, nr=34, nt=140, mat=None,
            edge_wave=0.035, coll=None):
    """Jakobsmuschel-Schale: Fächer in XZ-Ebene, Scharnier im Ursprung, Wölbung nach +Y."""
    vs, fs = [], []
    a0 = R(spread)
    for i in range(nr + 1):
        u = i / nr
        for j in range(nt + 1):
            v = j / nt
            th = -a0 + 2 * a0 * v
            # Rand gewellt (Rippen enden in Bögen)
            rib = math.cos(ribs * math.pi * v * 2 - math.pi)  # -1..1
            rr = radius * u * (1 + edge_wave * rib * u ** 3)
            x = rr * math.sin(th)
            z = rr * math.cos(th)
            # Wölbung: Kuppel, an Seiten flacher
            dome = depth * math.sin(math.pi * min(u * 1.05, 1.0)) ** 0.8 * (1 - 0.55 * (abs(th) / a0) ** 2)
            dome += depth * 0.35 * u
            y = dome + rib_amp * rib * (0.3 + u)
            vs.append((x, y, z))
    W = nt + 1
    for i in range(nr):
        for j in range(nt):
            a = i * W + j
            fs.append((a, a + 1, a + W + 1, a + W))
    ob = mesh_obj(name, vs, fs, mat, coll=coll)
    so = ob.modifiers.new('sol', 'SOLIDIFY'); so.thickness = 0.012; so.offset = 0; so.use_rim = True
    so.material_offset = 1
    sub = ob.modifiers.new('sub', 'SUBSURF'); sub.levels = 1; sub.render_levels = 1
    return ob


def ellipsoid_point(a, b, c, x, z, push=0.0):
    k = 1 - (x / a) ** 2 - (z / c) ** 2
    y = -b * math.sqrt(max(k, 0.0))
    n = Vector((x / a ** 2, y / b ** 2, z / c ** 2)).normalized()
    return Vector((x, y, z)) + n * push


def partial_sphere(name, r, th_max=95, seg=32, rings=16, mat=None, coll=None):
    """Kugelkappe um +Z-Achse … hier: obere Lidhälfte. th von 0 (oben) bis th_max."""
    vs, fs = [], []
    for i in range(rings + 1):
        th = R(th_max) * i / rings
        for j in range(seg):
            ph = 2 * math.pi * j / seg
            vs.append((r * math.sin(th) * math.cos(ph), r * math.sin(th) * math.sin(ph), r * math.cos(th)))
    for i in range(rings):
        for j in range(seg):
            a = i * seg + j; b = i * seg + (j + 1) % seg
            fs.append((a, b, b + seg, a + seg))
    ob = mesh_obj(name, vs, fs, mat, coll=coll)
    so = ob.modifiers.new('sol', 'SOLIDIFY'); so.thickness = r * 0.12
    return ob


def eye_material(name, iris=(0.05, 0.42, 0.45), iris2=(0.35, 0.85, 0.75)):
    mat = principled(name, (1, 1, 1), rough=0.08, coat=1.0, sss=0.05)
    nt = mat.node_tree
    b = nt.nodes[mat['bsdf']]
    tc = nt.nodes.new('ShaderNodeTexCoord')
    sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    nt.links.new(tc.outputs['Object'], sep.inputs[0])
    # Iris-Struktur: radiale Streifen über Winkel um Y-Achse
    noise = nt.nodes.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value = 18
    nt.links.new(tc.outputs['Object'], noise.inputs['Vector'])
    cr = nt.nodes.new('ShaderNodeValToRGB')
    el = cr.color_ramp.elements
    el[0].position = 0.0; el[0].color = (0.015, 0.012, 0.012, 1)   # Pupille (y=-1)
    el[1].position = 1.0; el[1].color = (0.92, 0.9, 0.88, 1)        # Sklera
    for p, c in [(0.075, (0.015, 0.012, 0.012)), (0.085, (*iris, )), (0.16, (*iris2,)), (0.2, (*iris,)),
                 (0.225, (0.02, 0.06, 0.07)), (0.245, (0.93, 0.91, 0.9))]:
        e = el.new(p); e.color = (*c, 1)
    mr = nt.nodes.new('ShaderNodeMapRange')
    mr.inputs['From Min'].default_value = -1.0; mr.inputs['From Max'].default_value = 1.0
    nt.links.new(sep.outputs['Y'], mr.inputs[0])
    cr2 = nt.nodes.new('ShaderNodeMixRGB'); cr2.blend_type = 'MULTIPLY'; cr2.inputs[0].default_value = 0.25
    nt.links.new(cr.outputs[0], cr2.inputs[1]); nt.links.new(noise.outputs['Color'], cr2.inputs[2])
    nt.links.new(mr.outputs[0], cr.inputs[0])
    nt.links.new(cr2.outputs[0], b.inputs['Base Color'])
    return mat


class Shelly:
    def __init__(self, coll=None, scale=1.0):
        self.coll = coll
        self.build()
        self.root.scale = (scale,) * 3

    def J(self, name, loc, parent):
        e = empty('sh_' + name, loc, parent=parent, coll=self.coll)
        e.rotation_mode = 'XYZ'
        self.j[name] = e
        return e

    def build(self):
        co = self.coll
        self.j = {}
        skin = principled('sh_skin', hexc('#F4AE92'), rough=0.42, sss=0.25, sss_r=(1.0, 0.45, 0.3), film=180,
                          film_ior=1.3, bump=(120, 0.02))
        self.skin = skin
        self.cheekmat = principled('sh_cheekm', hexc('#F49A8C'), rough=0.45, sss=0.25, sss_r=(1.0, 0.45, 0.3))
        self.lidmat = principled('sh_lidm', hexc('#D98FA0'), rough=0.35, sss=0.2, film=300, film_ior=1.4)
        sweater = principled('sh_sweater', hexc('#1E8C8A'), rough=0.85, sheen=0.6, bump=(55, 0.35, 0, 'knit'))
        cuff = principled('sh_cuff', hexc('#166E6C'), rough=0.9, sheen=0.5, bump=(140, 0.3, 0, 'wave'))
        pants = principled('sh_pants', hexc('#3A3560'), rough=0.6, sheen=0.3, bump=(200, 0.05))
        shoe = principled('sh_shoe', hexc('#E8775F'), rough=0.55, coat=0.3)
        sole = principled('sh_sole', hexc('#F3EBDD'), rough=0.6)
        shell_out = color_ramp_mat('sh_shell_out', [(0.0, hexc('#9E2A44')), (0.3, hexc('#E2525A')),
                                                    (0.7, hexc('#F7977A')), (1.0, hexc('#FFD9B8'))],
                                   coord='Z', lo=0.0, hi=0.45, rough=0.32, coat=0.6, film=260, film_ior=1.35,
                                   bump=(260, 0.08, 4, 'noise'))
        # Rippen-Streifen in die Schalenfarbe
        self._rib_stripes(shell_out)
        nacre = principled('sh_nacre', hexc('#F7C9C2'), rough=0.15, coat=1.0, film=420, film_ior=1.6,
                           bump=(30, 0.06, 3, 'wave'))
        self.nacre = nacre
        dark = principled('sh_mouth', hexc('#5A1E2A'), rough=0.5)
        brow = principled('sh_brow', hexc('#A8404C'), rough=0.6)
        blush = principled('sh_blush', hexc('#F59A92'), rough=0.5, sss=0.3, alpha=1.0)
        white = principled('sh_teeth', hexc('#FFFDF8'), rough=0.3)

        pearl = principled('sh_pearl', hexc('#FBF6F1'), rough=0.07, coat=1.0, film=500, film_ior=1.5)
        self.pearl_mat = pearl
        self.root = empty('sh_root', coll=co)
        hips = self.J('hips', (0, 0, 0.74), self.root)
        spine = self.J('spine', (0, 0, 0.06), hips)
        # Oberkörper (Pullover) als Drehkörper
        prof = [(0.0, 0.0), (0.14, 0.0), (0.155, 0.04), (0.16, 0.12), (0.168, 0.22), (0.178, 0.3), (0.17, 0.36),
                (0.13, 0.42), (0.075, 0.45), (0.0, 0.452)]
        torso = lathe('sh_torso', prof, 48, sweater, co)
        torso.parent = spine; torso.location = (0, 0, -0.08); torso.scale = (1.0, 0.72, 1.0)
        sub = torso.modifiers.new('s', 'SUBSURF'); sub.levels = 1; sub.render_levels = 2
        # Bündchen unten + Rollkragen
        band = prim('torus', 'sh_band', (0, 0, -0.075), scale=(1, 0.72, 1), mat=cuff, parent=spine, R=0.147, r=0.024, seg=48, coll=co)
        neck = self.J('neck', (0, 0, 0.37), spine)
        collar = prim('torus', 'sh_collar', (0, 0, 0.0), scale=(1, 0.95, 1.6), mat=cuff, parent=neck, R=0.062, r=0.03, seg=40, coll=co)
        neckm = prim('cyl', 'sh_neckm', (0, 0, 0.03), scale=(0.045, 0.045, 0.045), mat=skin, parent=neck, coll=co)
        # Hüfte / Hose
        pelvis = prim('sphere', 'sh_pelvis', (0, 0, -0.02), scale=(0.14, 0.105, 0.1), mat=pants, parent=hips, coll=co)
        skirtm = principled('sh_skirt', hexc('#E8A33A'), rough=0.7, sheen=0.4, bump=(160, 0.08, 4, 'wave'))
        vs, fs = [], []
        NS, NZ = 96, 10
        for i in range(NZ + 1):
            u = i / NZ
            z = 0.04 - 0.3 * u
            r0 = 0.15 + 0.1 * u ** 1.2
            for k in range(NS):
                a_ = 2 * math.pi * k / NS
                rr = r0 * (1 + 0.035 * u * math.sin(16 * a_) ** 1)
                vs.append((rr * math.cos(a_), rr * math.sin(a_) * 0.8, z))
        for i in range(NZ):
            for k in range(NS):
                a_ = i * NS + k; b_ = i * NS + (k + 1) % NS
                fs.append((a_, b_, b_ + NS, a_ + NS))
        skirt = mesh_obj('sh_skirt', vs, fs, skirtm, coll=co)
        skirt.parent = hips
        so = skirt.modifiers.new('sol', 'SOLIDIFY'); so.thickness = 0.01
        sb = skirt.modifiers.new('s', 'SUBSURF'); sb.render_levels = 1
        self.skirt = skirt
        prim('torus', 'sh_belt', (0, 0, 0.04), scale=(1, 0.8, 1), mat=principled('sh_beltm', hexc('#7A3B2E'), 0.5), parent=hips, R=0.152, r=0.014, seg=48, coll=co)
        prim('sphere', 'sh_buckle', (0, -0.125, 0.04), scale=(0.022, 0.012, 0.018), mat=pearl, parent=hips, coll=co)
        # Kopf
        head = self.J('head', (0, 0, 0.045), neck)
        a, b, c = 0.145, 0.13, 0.155
        self.face_abc = (a, b, c)
        face = prim('sphere', 'sh_face', (0, 0, 0.13), scale=(a, b, c), mat=skin, parent=head, seg=48, coll=co)
        self.face_c = Vector((0, 0, 0.13))
        # Kinn/Wangen
        for s in (-1, 1):
            prim('sphere', f'sh_cheek{s}', (s * 0.075, -0.075, 0.075), scale=(0.055, 0.045, 0.045), mat=self.cheekmat,
                 parent=head, coll=co)
        # Nase
        prim('sphere', 'sh_nose', (0, -0.138, 0.115), scale=(0.018, 0.016, 0.016), mat=skin, parent=head, coll=co)
        # Augen
        em = eye_material('sh_eye')
        hl = emission('sh_eyehl', (1, 1, 1), 6.0)
        self.eyes, self.lids, self.lowlids, self.brows = [], [], [], []
        for s in (-1, 1):
            ex, ez = s * 0.055, 0.155
            p = ellipsoid_point(a, b, c, ex, ez - 0.13, -0.022) + self.face_c
            piv = empty(f'sh_eyepiv{s}', tuple(p), parent=head, coll=co)
            eye = prim('sphere', f'sh_eye{s}', (0, 0, 0), scale=(0.042, 0.042, 0.048), mat=em, parent=piv, seg=40, coll=co, bake=False)
            eye.rotation_mode = 'XYZ'
            self.eyes.append(eye)
            # Glanzpunkt (dreht nicht mit Auge)
            prim('sphere', f'sh_hl{s}', (p.x + 0.013, p.y - 0.044, p.z + 0.017), scale=(0.0042,) * 3, mat=hl,
                 parent=head, seg=12, coll=co)
            # Oberlid
            lp = empty(f'sh_lidpiv{s}', tuple(p), parent=head, coll=co)
            lid = partial_sphere(f'sh_lid{s}', 0.0475, 100, 32, 14, self.lidmat, co)
            lid.parent = lp; lid.scale = (1.0, 1.0, 1.08)
            lid.rotation_mode = 'XYZ'
            self.lids.append(lid)
            # Wimpernkante
            lash = prim('torus', f'sh_lash{s}', (0, 0, 0), mat=dark, parent=lid, R=0.0475, r=0.0035, seg=32, coll=co)
            lash.rotation_euler = (R(90 - 100 + 90), 0, 0)
            lash.location = (0, 0, 0.0475 * math.cos(R(100)))
            lash.scale = (1, 1, 1)
            lash.rotation_euler = (0, 0, 0)
            lash.location = (0, 0, -0.0475 * 0.17)
            lash.scale = (0.985, 0.985, 1)
            for k in range(0):  # drei Wimpern außen
                ang = R(-60 - k * 22) if s > 0 else R(-120 + k * 22)
                x0, y0 = 0.047 * math.cos(ang), 0.047 * math.sin(ang)
                tube(f'sh_lashh{s}{k}', [(x0, y0, -0.008), (x0 * 1.25 + s * 0.006, y0 * 1.25, 0.006 + k * 0.004)],
                     0.0025, 6, dark, co).parent = lid
            # Unterlid
            ll = partial_sphere(f'sh_low{s}', 0.0465, 60, 32, 8, skin, co)
            ll.parent = lp; ll.rotation_euler = (R(180), 0, 0); ll.rotation_mode = 'XYZ'
            self.lowlids.append(ll)
            # Braue
            bp = empty(f'sh_browp{s}', (s * 0.058, -0.11, 0.235), parent=head, coll=co)
            pts = []
            for k in range(7):
                u = k / 6 - 0.5
                pts.append((u * 0.065, 0.006 * (1 - (2 * u) ** 2) * -1 + abs(u) * 0.01, 0.012 * (1 - (2 * u) ** 2)))
            br = tube(f'sh_brow{s}', pts, 0.0065, 8, brow, co, radii=[0.004, 0.006, 0.0075, 0.0078, 0.007, 0.0055, 0.0035][::s])
            br.parent = bp
            bp.rotation_mode = 'XYZ'
            self.brows.append(bp)
        # Münder (je Ausdruck ein Objekt)
        self.mouths = {}
        def mouth_curve(nm, fn, rad, n=13):
            pts = []
            for k in range(n):
                u = k / (n - 1) * 2 - 1
                x, dz = fn(u)
                pts.append(tuple(ellipsoid_point(a, b, c, x, -0.055 + dz, 0.002) + self.face_c))
            ob = tube('sh_m_' + nm, pts, rad, 8, dark, co, radii=[rad * (0.55 + 0.45 * (1 - abs(k / (n - 1) * 2 - 1) ** 2)) for k in range(n)])
            ob.parent = head
            self.mouths[nm] = ob
            return ob
        mouth_curve('smile', lambda u: (u * 0.04, 0.012 * (u * u - 1) + 0.004), 0.0055)
        mouth_curve('neutral', lambda u: (u * 0.03, 0.003 * (u * u - 1)), 0.0045)
        mouth_curve('worry', lambda u: (u * 0.032, -0.008 * (u * u - 1) - 0.008 + 0.003 * math.sin(u * 9)), 0.0045)
        # offener Mund "O" (Schreck): dunkle Scheibe
        p = ellipsoid_point(a, b, c, 0, -0.06, -0.004) + self.face_c
        om = prim('sphere', 'sh_m_o', tuple(p), scale=(0.021, 0.012, 0.028), mat=dark, parent=head, coll=co)
        self.mouths['o'] = om
        pb = ellipsoid_point(a, b, c, 0, -0.05, 0.0) + self.face_c
        sm = prim('sphere', 'sh_m_open', tuple(pb), scale=(0.03, 0.012, 0.018), mat=dark, parent=head, coll=co)
        prim('sphere', 'sh_teeth', (0, -0.006, 0.008), scale=(0.022, 0.005, 0.006), mat=white, parent=sm, coll=co)
        self.mouths['open'] = sm
        # --- Muschelkopf: große Schale hinten (Fächer), kleine Schale unten als Kragen
        shell_piv = empty('sh_shellpiv', (0, 0.06, -0.01), parent=head, coll=co)
        shell_piv.rotation_mode = 'XYZ'
        self.shell_piv = shell_piv
        sh = scallop('sh_shell', radius=0.41, spread=86, ribs=17, depth=0.15, rib_amp=0.013, mat=nacre, coll=co)
        sh.data.materials.append(shell_out)
        sh.parent = shell_piv
        sh.rotation_euler = (R(-8), 0, 0)
        # Ohren (Schalenflügel am Scharnier) + Perlenohrringe
        for s in (-1, 1):
            wv = [(0, 0, 0), (s * 0.085, 0.0, 0.0), (s * 0.075, 0.0, 0.05), (0, 0, 0.065)]
            w = mesh_obj(f'sh_wing{s}', wv, [(0, 1, 2, 3)] if s > 0 else [(3, 2, 1, 0)], shell_out, coll=co)
            w.parent = shell_piv; w.location = (0, 0.01, -0.01)
            so = w.modifiers.new('sol', 'SOLIDIFY'); so.thickness = 0.014
            bv = w.modifiers.new('bv', 'BEVEL'); bv.width = 0.008; bv.segments = 3
            tube(f'sh_earhook{s}', [(s * 0.142, -0.02, 0.06), (s * 0.15, -0.02, 0.035)], 0.0025, 6,
                 principled('gold', hexc('#D9A441'), 0.25, 1.0), co).parent = head
            prim('sphere', f'sh_earpearl{s}', (s * 0.15, -0.02, 0.022), scale=(0.016,) * 3, mat=pearl, parent=head, coll=co)
        # Haarsträhnen-artige Algen? -> kleine Seepocken / Muschel-Details auf der Schale
        rg = rnd(7)
        for k in range(5):
            th = R(rg.uniform(-60, 60)); rr = rg.uniform(0.2, 0.33)
            x, z = rr * math.sin(th), rr * math.cos(th)
            prim('sphere', f'sh_barn{k}', (x, 0.16 + 0.02, z), scale=(0.011, 0.006, 0.011), mat=pearl, parent=shell_piv, coll=co)
        # Haarband-Perlenkette über Schale
        for k in range(15):
            th = R(-70 + k * 10)
            prim('sphere', f'sh_tiara{k}', (0.205 * math.sin(th), 0.035, 0.0 + 0.205 * math.cos(th) + 0.01),
                 scale=(0.0125,) * 3, mat=pearl, parent=shell_piv, seg=16, coll=co)
        # Arme
        self.hands = []
        for s, nm in ((-1, 'R'), (1, 'L')):
            sh_ = self.J('shoulder' + nm, (s * 0.15, 0, 0.3), spine)
            prim('sphere', f'sh_shball{nm}', (0, 0, -0.01), scale=(0.056, 0.053, 0.06), mat=sweater, parent=sh_, coll=co)
            up = prim('cyl', f'sh_uarm{nm}', (0, 0, -0.12), scale=(0.048, 0.046, 0.12), r1=0.85, r2=1.0, mat=sweater, parent=sh_, coll=co)
            up.modifiers.new('s', 'SUBSURF').render_levels = 1
            el = self.J('elbow' + nm, (0, 0, -0.245), sh_)
            prim('sphere', f'sh_elb{nm}', (0, 0, 0), scale=(0.043,) * 3, mat=sweater, parent=el, coll=co)
            fo = prim('cyl', f'sh_farm{nm}', (0, 0, -0.1), scale=(0.042, 0.04, 0.11), r1=0.8, r2=1.0, mat=sweater, parent=el, coll=co)
            prim('torus', f'sh_cuff{nm}', (0, 0, -0.2), mat=cuff, parent=el, R=0.034, r=0.014, seg=24, coll=co)
            wr = self.J('wrist' + nm, (0, 0, -0.215), el)
            self._hand(wr, s, skin, co)
        # Beine
        for s, nm in ((-1, 'R'), (1, 'L')):
            hp = self.J('hip' + nm, (s * 0.075, 0, -0.03), hips)
            prim('cyl', f'sh_thigh{nm}', (0, 0, -0.17), scale=(0.062, 0.062, 0.18), r1=0.85, r2=1.0, mat=pants, parent=hp, coll=co).modifiers.new('s', 'SUBSURF').render_levels = 1
            kn = self.J('knee' + nm, (0, 0, -0.33), hp)
            prim('sphere', f'sh_knee{nm}', (0, 0, 0), scale=(0.052,) * 3, mat=pants, parent=kn, coll=co)
            prim('cyl', f'sh_shin{nm}', (0, 0, -0.16), scale=(0.052, 0.052, 0.17), r1=0.8, r2=1.0, mat=pants, parent=kn, coll=co).modifiers.new('s', 'SUBSURF').render_levels = 1
            an = self.J('ankle' + nm, (0, 0, -0.33), kn)
            prim('cyl', f'sh_sock{nm}', (0, 0, 0.0), scale=(0.046, 0.046, 0.03), mat=cuff, parent=an, coll=co)
            sh2 = prim('sphere', f'sh_shoe{nm}', (0, -0.04, -0.03), scale=(0.062, 0.115, 0.05), mat=shoe, parent=an, coll=co)
            prim('cube', f'sh_sole{nm}', (0, -0.04, -0.068), scale=(0.058, 0.108, 0.012), mat=sole, parent=an, bevel=0.01, coll=co)
            prim('sphere', f'sh_pom{nm}', (0, -0.13, -0.005), scale=(0.03,) * 3, mat=principled('pom', hexc('#FFE3D6'), 0.95, sheen=1.0, bump=(300, 0.6)), parent=an, coll=co)
        self.set_face('smile')
        self.pose({})

    def _rib_stripes(self, mat):
        nt = mat.node_tree
        b = nt.nodes[mat['bsdf']]
        base = b.inputs['Base Color'].links[0].from_socket
        tc = nt.nodes.new('ShaderNodeTexCoord')
        sep = nt.nodes.new('ShaderNodeSeparateXYZ')
        nt.links.new(tc.outputs['Object'], sep.inputs[0])
        at = nt.nodes.new('ShaderNodeMath'); at.operation = 'ARCTAN2'
        nt.links.new(sep.outputs['X'], at.inputs[0]); nt.links.new(sep.outputs['Z'], at.inputs[1])
        m = nt.nodes.new('ShaderNodeMath'); m.operation = 'MULTIPLY'; m.inputs[1].default_value = 17 * 2 / 2.93 * math.pi
        nt.links.new(at.outputs[0], m.inputs[0])
        s = nt.nodes.new('ShaderNodeMath'); s.operation = 'SINE'
        nt.links.new(m.outputs[0], s.inputs[0])
        mr = nt.nodes.new('ShaderNodeMapRange')
        mr.inputs['From Min'].default_value = -1; mr.inputs['From Max'].default_value = 1
        mr.inputs['To Min'].default_value = 0.72; mr.inputs['To Max'].default_value = 1.0
        nt.links.new(s.outputs[0], mr.inputs[0])
        # Wachstumsringe
        ln = nt.nodes.new('ShaderNodeVectorMath'); ln.operation = 'LENGTH'
        nt.links.new(tc.outputs['Object'], ln.inputs[0])
        m2 = nt.nodes.new('ShaderNodeMath'); m2.operation = 'MULTIPLY'; m2.inputs[1].default_value = 140
        nt.links.new(ln.outputs['Value'], m2.inputs[0])
        s2 = nt.nodes.new('ShaderNodeMath'); s2.operation = 'SINE'
        nt.links.new(m2.outputs[0], s2.inputs[0])
        mr2 = nt.nodes.new('ShaderNodeMapRange')
        mr2.inputs['From Min'].default_value = -1; mr2.inputs['From Max'].default_value = 1
        mr2.inputs['To Min'].default_value = 0.9; mr2.inputs['To Max'].default_value = 1.0
        nt.links.new(s2.outputs[0], mr2.inputs[0])
        mul = nt.nodes.new('ShaderNodeMix'); mul.data_type = 'RGBA'; mul.blend_type = 'MULTIPLY'
        mul.inputs['Factor'].default_value = 1.0
        nt.links.new(base, mul.inputs['A'])
        cmb = nt.nodes.new('ShaderNodeMath'); cmb.operation = 'MULTIPLY'
        nt.links.new(mr.outputs[0], cmb.inputs[0]); nt.links.new(mr2.outputs[0], cmb.inputs[1])
        nt.links.new(cmb.outputs[0], mul.inputs['B'])
        nt.links.new(mul.outputs['Result'], b.inputs['Base Color'])

    def _hand(self, wr, s, skin, co):
        palm = prim('sphere', f'sh_palm{s}', (0, 0, -0.045), scale=(0.022, 0.04, 0.05), mat=skin, parent=wr, coll=co)
        palm.rotation_euler = (0, 0, R(90))
        fingers = []
        for k in range(4):
            y = -0.027 + k * 0.018
            ln = [0.055, 0.062, 0.058, 0.047][k]
            f = tube(f'sh_fing{s}{k}', [(0, 0, 0), (0, 0, -ln * 0.5), (0, 0.003 * s, -ln)], 0.0095, 10, skin, co,
                     radii=[0.0105, 0.0095, 0.0075])
            fp = empty(f'sh_fpiv{s}{k}', (0.0, y, -0.085), parent=wr, coll=co)
            fp.rotation_mode = 'XYZ'
            f.parent = fp
            fingers.append(fp)
        th = tube(f'sh_thumb{s}', [(0, 0, 0), (0, 0, -0.025), (0, 0, -0.045)], 0.011, 10, skin, co, radii=[0.012, 0.011, 0.008])
        tp = empty(f'sh_tpiv{s}', (-0.012, -0.035, -0.035), parent=wr, coll=co)
        tp.rotation_mode = 'XYZ'
        tp.rotation_euler = (R(30), R(-30), 0)
        th.parent = tp
        self.hands.append((fingers, tp))

    # --------------------------------------------------------- Animation
    def set_face(self, mouth='smile', blink=0.0, look=(0, 0), brow=0.0, brow_tilt=0.0, shell=0.0, lids_wide=0.0):
        """blink 0..1; look (yaw,pitch) Grad; brow: hoch (+)/runter(-); shell: 0 offen .. 1 zu."""
        for k, ob in self.mouths.items():
            ob.hide_render = (k != mouth)
            ob.hide_viewport = (k != mouth)
            for ch in ob.children:
                ch.hide_render = ob.hide_render
        for e in self.eyes:
            e.rotation_euler = (R(-look[1]), 0, R(look[0]))
        # Oberlid: offen bei ~ -35° (nach hinten gekippt), zu bei +62°
        op = -38 - 14 * lids_wide
        for l in self.lids:
            l.rotation_euler = (R(lerp(op, 66, blink)), 0, 0)
        for l in self.lowlids:
            l.rotation_euler = (R(180 + 40 - 12 * blink - 6 * lids_wide), 0, 0)
        for i, bp in enumerate(self.brows):
            s = -1 if i == 0 else 1
            bp.location.z = 0.235 + 0.018 * brow
            bp.rotation_euler = (0, R(s * brow_tilt * 18), 0)
        self.shell_piv.rotation_euler = (R(-shell * 62), 0, 0)

    def pose(self, p):
        """p: dict Gelenkname -> (rx,ry,rz) in Grad; Rest neutral. 'root_loc', 'root_rot', 'fingers' (0..1)."""
        neutral = {'shoulderL': (0, -12, 0), 'shoulderR': (0, 12, 0), 'elbowL': (-14, 0, 0), 'elbowR': (-14, 0, 0),
                   'wristL': (0, 0, 0), 'wristR': (0, 0, 0)}
        for n, e in self.j.items():
            v = p.get(n, neutral.get(n, (0, 0, 0)))
            e.rotation_euler = tuple(R(x) for x in v)
        if 'root_loc' in p: self.root.location = p['root_loc']
        if 'root_rot' in p: self.root.rotation_euler = tuple(R(x) for x in p['root_rot'])
        if 'hips_loc' in p: self.j['hips'].location = p['hips_loc']
        else: self.j['hips'].location = (0, 0, 0.74)
        curl = p.get('fingers', 0.25)
        for fingers, tp in self.hands:
            for f in fingers:
                f.rotation_euler = (R(-70 * curl), 0, 0)
            tp.rotation_euler = (R(30 + 30 * curl), R(-30), 0)

    def head_world(self):
        return self.j['head'].matrix_world @ Vector((0, 0, 0.13))
