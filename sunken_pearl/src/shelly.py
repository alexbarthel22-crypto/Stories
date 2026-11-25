"""Shelly – elegante Frau mit Muschelkopf. Aufbau aus Primitiven mit Gelenk-Hierarchie (Blick nach -Y).
outfit: 'home' (Seidenkleid, knielang) oder 'gown' (Pailletten-Abendkleid, bodenlang)."""
import bpy, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
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
            rib = math.cos(ribs * math.pi * v * 2 - math.pi)
            rr = radius * u * (1 + edge_wave * rib * u ** 3)
            x = rr * math.sin(th)
            z = rr * math.cos(th)
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


def partial_sphere(name, r, th_max=95, seg=32, rings=16, mat=None, coll=None, thick=0.12):
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
    so = ob.modifiers.new('sol', 'SOLIDIFY'); so.thickness = r * thick
    return ob


def eye_material(name, iris=(0.03, 0.30, 0.42), iris2=(0.40, 0.86, 0.88)):
    mat = principled(name, (1, 1, 1), rough=0.06, coat=1.0, sss=0.05)
    nt = mat.node_tree
    b = nt.nodes[mat['bsdf']]
    tc = nt.nodes.new('ShaderNodeTexCoord')
    sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    nt.links.new(tc.outputs['Object'], sep.inputs[0])
    noise = nt.nodes.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value = 22
    nt.links.new(tc.outputs['Object'], noise.inputs['Vector'])
    cr = nt.nodes.new('ShaderNodeValToRGB')
    el = cr.color_ramp.elements
    el[0].position = 0.0; el[0].color = (0.012, 0.01, 0.012, 1)
    el[1].position = 1.0; el[1].color = (0.95, 0.93, 0.92, 1)
    for p, c in [(0.042, (0.012, 0.01, 0.012)), (0.056, iris), (0.17, iris2), (0.215, (0.85, 0.75, 0.35)),
                 (0.235, iris), (0.255, (0.02, 0.05, 0.08)), (0.27, (0.95, 0.93, 0.92))]:
        e = el.new(p); e.color = (*c, 1)
    mr = nt.nodes.new('ShaderNodeMapRange')
    mr.inputs['From Min'].default_value = -1.0; mr.inputs['From Max'].default_value = 1.0
    nt.links.new(sep.outputs['Y'], mr.inputs[0])
    cr2 = nt.nodes.new('ShaderNodeMixRGB'); cr2.blend_type = 'MULTIPLY'; cr2.inputs[0].default_value = 0.22
    nt.links.new(cr.outputs[0], cr2.inputs[1]); nt.links.new(noise.outputs['Color'], cr2.inputs[2])
    nt.links.new(mr.outputs[0], cr.inputs[0])
    nt.links.new(cr2.outputs[0], b.inputs['Base Color'])
    return mat


def _blush(mat, centers, radius, color, amt=0.55):
    """Weiches Rouge in Objektkoordinaten."""
    nt = mat.node_tree
    b = nt.nodes[mat['bsdf']]
    tc = nt.nodes.new('ShaderNodeTexCoord')
    acc = None
    for c in centers:
        d = nt.nodes.new('ShaderNodeVectorMath'); d.operation = 'DISTANCE'
        d.inputs[1].default_value = c
        nt.links.new(tc.outputs['Object'], d.inputs[0])
        mr = nt.nodes.new('ShaderNodeMapRange'); mr.interpolation_type = 'SMOOTHSTEP'
        mr.inputs['From Min'].default_value = radius; mr.inputs['From Max'].default_value = radius * 0.15
        nt.links.new(d.outputs['Value'], mr.inputs[0])
        if acc is None:
            acc = mr.outputs[0]
        else:
            mx = nt.nodes.new('ShaderNodeMath'); mx.operation = 'MAXIMUM'
            nt.links.new(acc, mx.inputs[0]); nt.links.new(mr.outputs[0], mx.inputs[1]); acc = mx.outputs[0]
    k = nt.nodes.new('ShaderNodeMath'); k.operation = 'MULTIPLY'; k.inputs[1].default_value = amt
    nt.links.new(acc, k.inputs[0])
    mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'
    mix.inputs['A'].default_value = tuple(b.inputs['Base Color'].default_value)
    mix.inputs['B'].default_value = (*color, 1)
    nt.links.new(k.outputs[0], mix.inputs['Factor'])
    nt.links.new(mix.outputs['Result'], b.inputs['Base Color'])


def sequin_mat(name, c1, c2):
    """Pailletten: metallisch, Voronoi-Zellen mit wechselnder Helligkeit und Normalen."""
    mat = principled(name, hexc(c1), rough=0.22, metal=0.75, coat=0.3)
    nt = mat.node_tree
    b = nt.nodes[mat['bsdf']]
    tc = nt.nodes.new('ShaderNodeTexCoord')
    vo = nt.nodes.new('ShaderNodeTexVoronoi'); vo.inputs['Scale'].default_value = 420
    nt.links.new(tc.outputs['Object'], vo.inputs['Vector'])
    mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'
    mix.inputs['A'].default_value = (*hexc(c1), 1); mix.inputs['B'].default_value = (*hexc(c2), 1)
    sep = nt.nodes.new('ShaderNodeSeparateColor')
    nt.links.new(vo.outputs['Color'], sep.inputs[0])
    nt.links.new(sep.outputs[0], mix.inputs['Factor'])
    nt.links.new(mix.outputs['Result'], b.inputs['Base Color'])
    # Paillettennormalen: zufällige Farbe als Normalstörung
    bp = nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.6
    nt.links.new(vo.outputs['Distance'], bp.inputs['Height'])
    nt.links.new(bp.outputs[0], b.inputs['Normal'])
    return mat


def satin_mat(name, c, sheen_tint=None):
    m = principled(name, hexc(c), rough=0.32, sheen=0.8, coat=0.15, aniso=0.6, bump=(18, 0.08, 3, 'wave'))
    return m


class Shelly:
    def __init__(self, coll=None, scale=1.0, outfit='home'):
        self.coll = coll
        self.outfit = outfit
        self.build()
        self.root.scale = (scale,) * 3

    def J(self, name, loc, parent):
        e = empty('sh_' + name, loc, parent=parent, coll=self.coll)
        e.rotation_mode = 'XYZ'
        self.j[name] = e
        return e

    # Oberflächenpunkt auf Gesicht (Kopf-Koordinaten)
    def surf(self, x, z, push=0.0):
        o = Vector((x, -1.0, z - self.face_c.z))
        hit, nrm, idx, dist = self.bvh.ray_cast(o, Vector((0, 1, 0)))
        if hit is None:
            return Vector((x, 0, z))
        return hit + nrm * push + self.face_c

    def build(self):
        co = self.coll
        self.j = {}
        gown = self.outfit == 'gown'
        skin = principled('sh_skin', hexc('#F8C6AE'), rough=0.4, sss=0.3, sss_r=(1.0, 0.5, 0.35), bump=(160, 0.015))
        self.skin = skin
        facem = principled('sh_facem', hexc('#F8C6AE'), rough=0.38, sss=0.3, sss_r=(1.0, 0.5, 0.35), bump=(160, 0.01))
        self.lidmat = principled('sh_lidm', hexc('#E8A9B4'), rough=0.3, sss=0.25, sss_r=(1.0, 0.5, 0.35), film=300, film_ior=1.35)
        liner = principled('sh_liner', hexc('#2A1420'), rough=0.4)
        lipm = principled('sh_lips', hexc('#D9536F'), rough=0.22, coat=0.6, sss=0.25, sss_r=(1, 0.3, 0.3))
        dark = principled('sh_mouth', hexc('#4A1626'), rough=0.5)
        brow = principled('sh_brow', hexc('#5C2F2E'), rough=0.6)
        white = principled('sh_teeth', hexc('#FFFDF8'), rough=0.25)
        nail = principled('sh_nail', hexc('#E25A7E'), rough=0.15, coat=1.0)
        gold = principled('sh_gold', hexc('#E2B04A'), 0.2, 1.0)
        pearl = principled('sh_pearl', hexc('#FBF4EE'), rough=0.06, coat=1.0, film=520, film_ior=1.5, sss=0.1)
        self.pearl_mat = pearl
        if gown:
            dress = sequin_mat('sh_dress', '#13306E', '#3E7FD0')
            dress2 = principled('sh_dress2', hexc('#0E2350'), rough=0.3, sheen=0.6, coat=0.2, aniso=0.5)
            shoe = principled('sh_shoe', hexc('#C9D7E8'), rough=0.1, metal=0.9)
        else:
            dress = satin_mat('sh_dress', '#F3A6B9')
            dress2 = satin_mat('sh_dress2', '#F7BCCB')
            shoe = principled('sh_shoe', hexc('#E7B866'), rough=0.2, metal=0.85)
        self.dress = dress
        shell_out = color_ramp_mat('sh_shell_out', [(0.0, hexc('#B84A72')), (0.3, hexc('#E7789B')),
                                                    (0.7, hexc('#F8B5C4')), (1.0, hexc('#FFF0E6'))],
                                   coord='Z', lo=0.0, hi=0.45, rough=0.25, coat=0.8, film=300, film_ior=1.4,
                                   bump=(260, 0.05, 4, 'noise'))
        self._rib_stripes(shell_out)
        nacre = principled('sh_nacre', hexc('#F7CCD8'), rough=0.12, coat=1.0, film=520, film_ior=1.7,
                           bump=(30, 0.05, 3, 'wave'))
        self.nacre = nacre

        self.root = empty('sh_root', coll=co)
        hips = self.J('hips', (0, 0, 0.74), self.root)
        spine = self.J('spine', (0, 0, 0.06), hips)
        # Oberkörper: Sanduhr, Ausschnitt mit Haut
        prof = [(0.0, 0.0), (0.128, 0.0), (0.122, 0.05), (0.1, 0.14), (0.104, 0.2), (0.126, 0.26), (0.13, 0.3),
                (0.128, 0.34), (0.12, 0.37), (0.09, 0.4), (0.05, 0.425), (0.0, 0.43)]
        torso = lathe('sh_torso', prof, 56, None, co)
        torso.parent = spine; torso.location = (0, 0, -0.08); torso.scale = (1.0, 0.7, 1.0)
        torso.data.materials.append(self._bodice(dress, skin))
        sub = torso.modifiers.new('s', 'SUBSURF'); sub.levels = 1; sub.render_levels = 2
        # dezente Brust
        for s in (-1, 1):
            b_ = prim('sphere', f'sh_bust{s}', (s * 0.05, -0.062, 0.18), scale=(0.058, 0.045, 0.052), mat=dress, parent=spine, coll=co)
        neck = self.J('neck', (0, 0, 0.345), spine)
        prim('cyl', 'sh_neckm', (0, 0, 0.04), scale=(0.04, 0.038, 0.065), r1=1.2, r2=1.0, mat=skin, parent=neck, coll=co)
        # Perlenkette
        for k in range(26):
            a = 2 * math.pi * k / 26
            prim('sphere', f'sh_neckl{k}', (0.05 * math.sin(a), -0.044 * math.cos(a), 0.012 - 0.012 * math.cos(a)),
                 scale=(0.0085,) * 3, mat=pearl, parent=neck, seg=12, coll=co)
        prim('sphere', 'sh_pendant', (0, -0.05, -0.025), scale=(0.013, 0.011, 0.016), mat=pearl, parent=neck, seg=16, coll=co)
        # Hüfte + Rock
        prim('sphere', 'sh_pelvis', (0, 0, -0.01), scale=(0.13, 0.095, 0.1), mat=dress2 if gown else dress, parent=hips, coll=co)
        if gown:
            self._skirt(hips, dress, z0=0.04, length=0.74, prof=lambda u: 0.13 + 0.01 * u if u < 0.5 else 0.135 + 0.42 * (u - 0.5) ** 1.5,
                        folds=14, fold_amp=0.06)
        else:
            self._skirt(hips, dress, z0=0.04, length=0.36, prof=lambda u: 0.13 + 0.15 * u ** 1.1, folds=12, fold_amp=0.05)
        # Taillengürtel mit Perlen
        prim('torus', 'sh_belt', (0, 0, 0.06), scale=(1, 0.72, 1), mat=gold if gown else dress2, R=0.105, r=0.01, seg=48, parent=spine, coll=co)
        prim('sphere', 'sh_buckle', (0, -0.077, 0.06), scale=(0.018, 0.01, 0.018), mat=pearl, parent=spine, coll=co)
        # ---------------------------------------------------------------- Kopf
        head = self.J('head', (0, 0, 0.062), neck)
        a, b, c = 0.142, 0.13, 0.16
        self.face_c = Vector((0, 0, 0.13))
        face = prim('sphere', 'sh_face', (0, 0, 0.13), scale=(a, b, c), mat=facem, parent=head, seg=64, coll=co)
        # Herzform: Kinn schmaler
        for v in face.data.vertices:
            z = v.co.z
            if z < 0:
                u = (-z / c)
                v.co.x *= 1 - 0.3 * u ** 1.7
                v.co.y *= 1 - 0.08 * u ** 2
            else:
                u = z / c
                v.co.x *= 1 + 0.03 * math.sin(u * math.pi)
        face.data.update()
        self.bvh = BVHTree.FromPolygons([v.co.copy() for v in face.data.vertices], [p.vertices[:] for p in face.data.polygons])
        _blush(facem, [(-0.078, -0.1, -0.035), (0.078, -0.1, -0.035)], 0.05, hexc('#F28A9A'), 0.5)
        self._hair(head, face, a, b, c)
        # Nase (klein, Stupsnase)
        p = self.surf(0, 0.105, -0.002)
        prim('sphere', 'sh_nose', tuple(p), scale=(0.014, 0.012, 0.011), mat=facem, parent=head, coll=co)
        # Augen
        em = eye_material('sh_eye')
        hl = emission('sh_eyehl', (1, 1, 1), 6.0)
        self.eyes, self.lids, self.lowlids, self.brows = [], [], [], []
        ER = 0.044
        for s in (-1, 1):
            p = self.surf(s * 0.06, 0.15, -0.024)
            piv = empty(f'sh_eyepiv{s}', tuple(p), parent=head, coll=co)
            eye = prim('sphere', f'sh_eye{s}', (0, 0, 0), scale=(ER, ER, ER * 1.12), mat=em, parent=piv, seg=40, coll=co, bake=False)
            eye.rotation_mode = 'XYZ'
            self.eyes.append(eye)
            lp = empty(f'sh_lidpiv{s}', tuple(p), parent=head, coll=co)
            LR = ER * 1.04
            lid = partial_sphere(f'sh_lid{s}', LR, 100, 36, 14, self.lidmat, co)
            lid.parent = lp; lid.scale = (1.0, 1.0, 1.1)
            lid.rotation_mode = 'XYZ'
            self.lids.append(lid)
            # Lidstrich
            lash = prim('torus', f'sh_liner{s}', (0, 0, -LR * 0.17), mat=liner, parent=lid, R=LR * 0.99, r=0.0042, seg=36, coll=co)
            lash.scale = (1, 1, 1)
            # Wimpern (geschwungen, außen länger)
            for k in range(8):
                ph = R(-90 + s * (-30 + k * 13))
                outer = k / 7
                L = 0.011 + 0.013 * outer
                rr = LR * math.sin(R(100))
                p0 = Vector((rr * math.cos(ph), rr * math.sin(ph), LR * math.cos(R(100))))
                n = Vector((math.cos(ph), math.sin(ph), 0)) + Vector((s * 0.35 * outer, 0, 0))
                n.normalize()
                z = Vector((0, 0, 1))
                pts = [p0, p0 + n * L * 0.5 - z * L * 0.2, p0 + n * L * 0.85 + z * L * 0.1, p0 + n * L * 0.95 + z * L * 0.55]
                tube(f'sh_lashh{s}{k}', [tuple(q) for q in pts], 0.0012, 6, liner, co,
                     radii=[0.0015, 0.0012, 0.0008, 0.0003]).parent = lid
            ll = partial_sphere(f'sh_low{s}', ER * 1.02, 60, 36, 8, facem, co)
            ll.parent = lp; ll.rotation_euler = (R(180), 0, 0); ll.rotation_mode = 'XYZ'
            self.lowlids.append(ll)
            # Braue: schmal, geschwungen
            bz = 0.222
            bp = empty(f'sh_browp{s}', tuple(self.surf(s * 0.064, bz, 0.002)), parent=head, coll=co)
            c0 = bp.location.copy()
            pts = []
            for k in range(9):
                u = k / 8 - 0.5
                arch = 0.013 * (1 - ((2 * u - 0.3 * s) / 1.3) ** 2) - 0.004
                pts.append(tuple(self.surf(s * 0.064 + u * 0.074, bz + arch, 0.003) - c0))
            br = tube(f'sh_brow{s}', pts, 0.003, 8, brow, co,
                      radii=[r_ * 0.72 for r_ in ([0.0042, 0.0046, 0.0046, 0.0042, 0.0037, 0.0031, 0.0025, 0.0018, 0.0009][::-1] if s < 0 else
                      [0.0042, 0.0046, 0.0046, 0.0042, 0.0037, 0.0031, 0.0025, 0.0018, 0.0009])])
            br.parent = bp
            bp.rotation_mode = 'XYZ'
            bp['z0'] = bp.location.z
            self.brows.append(bp)
        # ----------------------------------------------------------- Lippen / Münder
        self.mouths = {}
        MZ = 0.062  # Mundhöhe in Kopfkoordinaten

        def lipcurve(fn_z, w, n=15):
            return [(u, (u * w, MZ + fn_z(u))) for u in [k / (n - 1) * 2 - 1 for k in range(n)]]

        def lip(nm, curve, rmax, push, profile):
            pts = [tuple(self.surf(x, z, push * rmax)) for u, (x, z) in curve]
            radii = [rmax * profile(u) for u, _ in curve]
            return tube(nm, pts, rmax, 10, lipm, co, radii=radii)

        def upper_prof(u):
            return (0.3 + 0.7 * (1 - u * u) ** 0.6) * (1 - 0.3 * math.exp(-(u / 0.13) ** 2))

        def lower_prof(u):
            return 0.28 + 0.72 * (1 - u * u) ** 0.8

        def closed_mouth(nm, curve_up, w, rup=0.0058, rlo=0.0075, gap=0.0065):
            root = empty('sh_m_' + nm, parent=head, coll=co)
            bow = lambda u: 0.0025 * math.exp(-((abs(u) - 0.28) / 0.14) ** 2)
            up_ = lip(f'sh_lipu_{nm}', lipcurve(lambda u: curve_up(u) + gap * 0.5 + bow(u), w), rup, 0.25, upper_prof)
            lo_ = lip(f'sh_lipl_{nm}', lipcurve(lambda u: curve_up(u) * 0.8 - gap, w * 0.86), rlo, 0.25, lower_prof)
            ln = tube(f'sh_lipline_{nm}', [tuple(self.surf(x, z, 0.0008)) for u, (x, z) in lipcurve(lambda u: curve_up(u) - 0.0008, w * 1.02)],
                      0.0017, 6, dark, co)
            for o in (up_, lo_, ln):
                o.parent = root
            self.mouths[nm] = root
            return root

        closed_mouth('smile', lambda u: 0.009 * u ** 2 - 0.002, 0.033)
        closed_mouth('neutral', lambda u: 0.002 * u ** 2, 0.028)
        closed_mouth('worry', lambda u: -0.003 * u ** 2 + 0.0015 * math.sin(u * 4), 0.026)
        # "o": Kussmund / staunend
        root = empty('sh_m_o', parent=head, coll=co)
        ring = []
        for k in range(25):
            ang = 2 * math.pi * k / 24
            ring.append(tuple(self.surf(0.0145 * math.cos(ang), MZ - 0.004 + 0.0165 * math.sin(ang), 0.003)))
        tube('sh_lipo', ring, 0.0058, 10, lipm, co, radii=[0.0058 * (1.0 + 0.25 * max(0, -math.sin(2 * math.pi * k / 24))) for k in range(25)]).parent = root
        pc = self.surf(0, MZ - 0.004, -0.004)
        prim('sphere', 'sh_m_odark', tuple(pc), scale=(0.014, 0.006, 0.0165), mat=dark, parent=root, coll=co)
        self.mouths['o'] = root
        # "open": strahlendes Lachen
        root = empty('sh_m_open', parent=head, coll=co)
        w = 0.034
        up_c = lambda u: 0.01 * u ** 2 + 0.002 + 0.0022 * math.exp(-((abs(u) - 0.28) / 0.14) ** 2)
        lo_c = lambda u: -0.021 * (1 - u ** 2) ** 0.8 + 0.01 * u ** 2 + 0.002
        lip('sh_lipu_open', lipcurve(up_c, w), 0.0052, 0.25, upper_prof).parent = root
        lip('sh_lipl_open', lipcurve(lo_c, w * 0.97), 0.0068, 0.25, lower_prof).parent = root
        pc = self.surf(0, MZ - 0.007, -0.006)
        prim('sphere', 'sh_m_opendark', tuple(pc), scale=(0.03, 0.008, 0.012), mat=dark, parent=root, coll=co)
        prim('sphere', 'sh_teeth', tuple(self.surf(0, MZ - 0.0015, -0.0035)), scale=(0.022, 0.006, 0.0045), mat=white, parent=root, coll=co)
        self.mouths['open'] = root
        # ----------------------------------------------------------- Muschelkopf
        shell_piv = empty('sh_shellpiv', (0, 0.06, -0.01), parent=head, coll=co)
        shell_piv.rotation_mode = 'XYZ'
        self.shell_piv = shell_piv
        sh = scallop('sh_shell', radius=0.43, spread=86, ribs=17, depth=0.15, rib_amp=0.012, mat=nacre, coll=co)
        sh.data.materials.append(shell_out)
        sh.parent = shell_piv
        sh.rotation_euler = (R(-8), 0, 0)
        for s in (-1, 1):
            wv = [(0, 0, 0), (s * 0.085, 0.0, 0.0), (s * 0.075, 0.0, 0.05), (0, 0, 0.065)]
            wg = mesh_obj(f'sh_wing{s}', wv, [(0, 1, 2, 3)] if s > 0 else [(3, 2, 1, 0)], shell_out, coll=co)
            wg.parent = shell_piv; wg.location = (0, 0.01, -0.01)
            so = wg.modifiers.new('sol', 'SOLIDIFY'); so.thickness = 0.014
            bv = wg.modifiers.new('bv', 'BEVEL'); bv.width = 0.008; bv.segments = 3
            # Tropfen-Ohrringe
            tube(f'sh_earhook{s}', [(s * 0.142, -0.02, 0.06), (s * 0.148, -0.02, 0.04)], 0.0022, 6, gold, co).parent = head
            prim('sphere', f'sh_eargold{s}', (s * 0.148, -0.02, 0.038), scale=(0.006,) * 3, mat=gold, parent=head, coll=co)
            prim('sphere', f'sh_earpearl{s}', (s * 0.148, -0.02, 0.018), scale=(0.013, 0.013, 0.017), mat=pearl, parent=head, coll=co)
        # Perlen-Diadem
        for k in range(17):
            th = R(-72 + k * 9)
            big = 1.35 if k == 8 else (1.0 if k % 2 == 0 else 0.75)
            prim('sphere', f'sh_tiara{k}', (0.205 * math.sin(th), 0.035, 0.0 + 0.205 * math.cos(th) + 0.01),
                 scale=(0.0115 * big,) * 3, mat=pearl, parent=shell_piv, seg=16, coll=co)
        tube('sh_tiarawire', [(0.205 * math.sin(R(a_)), 0.04, 0.205 * math.cos(R(a_)) + 0.01) for a_ in range(-74, 75, 6)],
             0.0022, 6, gold, co).parent = shell_piv
        # Perlen auf der Schale
        rg = rnd(7)
        for k in range(7):
            th = R(rg.uniform(-60, 60)); rr = rg.uniform(0.24, 0.36)
            x, z = rr * math.sin(th), rr * math.cos(th)
            prim('sphere', f'sh_barn{k}', (x, 0.17, z), scale=(0.008,) * 3, mat=pearl, parent=shell_piv, coll=co)
        def limb(nm, parent, z0, z1, radii, back=0.0):
            n = len(radii)
            pts = [(0, back * math.sin(math.pi * k / (n - 1)) ** 2 if k < n - 2 else 0, z0 + (z1 - z0) * k / (n - 1)) for k in range(n)]
            ob = tube(nm, pts, radii[0], 20, skin, co, radii=radii)
            ob.parent = parent
            return ob

        # ----------------------------------------------------------- Arme
        self.hands = []
        for s, nm in ((-1, 'R'), (1, 'L')):
            sh_ = self.J('shoulder' + nm, (s * 0.112, 0, 0.295), spine)
            prim('sphere', f'sh_shball{nm}', (0, 0, -0.012), scale=(0.038, 0.036, 0.042), mat=skin, parent=sh_, coll=co)
            pf = prim('sphere', f'sh_puff{nm}', (s * 0.008, 0, -0.03), scale=(0.056, 0.052, 0.05), mat=dress, parent=sh_, coll=co, subsurf=1)
            prim('torus', f'sh_puffband{nm}', (s * 0.004, 0, -0.066), mat=self.pearl_mat, R=0.04, r=0.0055, seg=32, parent=sh_, coll=co)
            limb(f'sh_uarm{nm}', sh_, -0.01, -0.245, [0.037, 0.036, 0.034, 0.03, 0.027, 0.025, 0.0235])
            el = self.J('elbow' + nm, (0, 0, -0.245), sh_)
            prim('sphere', f'sh_elb{nm}', (0, 0, 0), scale=(0.0235,) * 3, mat=skin, parent=el, coll=co)
            limb(f'sh_farm{nm}', el, 0.0, -0.215, [0.0235, 0.025, 0.024, 0.021, 0.018, 0.0165, 0.016])
            # Perlenarmband
            for k in range(14):
                a_ = 2 * math.pi * k / 14
                prim('sphere', f'sh_brace{nm}{k}', (0.026 * math.cos(a_), 0.026 * math.sin(a_), -0.195), scale=(0.0065,) * 3,
                     mat=pearl, parent=el, seg=10, coll=co)
            wr = self.J('wrist' + nm, (0, 0, -0.215), el)
            self._hand(wr, s, skin, nail, co)
        # ----------------------------------------------------------- Beine
        for s, nm in ((-1, 'R'), (1, 'L')):
            hp = self.J('hip' + nm, (s * 0.068, 0, -0.03), hips)
            limb(f'sh_thigh{nm}', hp, 0.03, -0.33, [0.062, 0.06, 0.056, 0.05, 0.045, 0.04, 0.037, 0.035])
            kn = self.J('knee' + nm, (0, 0, -0.33), hp)
            prim('sphere', f'sh_knee{nm}', (0, 0, 0), scale=(0.035,) * 3, mat=skin, parent=kn, coll=co)
            limb(f'sh_shin{nm}', kn, 0.0, -0.33, [0.035, 0.037, 0.038, 0.034, 0.028, 0.022, 0.019, 0.018], back=0.008)
            an = self.J('ankle' + nm, (0, 0, -0.33), kn)
            prim('sphere', f'sh_ank{nm}', (0, 0, 0), scale=(0.019,) * 3, mat=skin, parent=an, coll=co)
            prim('sphere', f'sh_foot{nm}', (0, -0.04, -0.03), rot=(R(24), 0, 0), scale=(0.024, 0.07, 0.022), mat=skin, parent=an, coll=co)
            prim('sphere', f'sh_shoe{nm}', (0, -0.055, -0.042), rot=(R(24), 0, 0), scale=(0.028, 0.068, 0.02), mat=shoe, parent=an, coll=co)
            prim('sphere', f'sh_shoeb{nm}', (0, 0.012, -0.018), scale=(0.026, 0.03, 0.026), mat=shoe, parent=an, coll=co)
            prim('cyl', f'sh_heel{nm}', (0, 0.028, -0.05), scale=(0.007, 0.007, 0.028), r1=0.6, r2=1.0, mat=shoe, parent=an, coll=co)
            prim('sphere', f'sh_bow{nm}', (0, -0.085, -0.045), scale=(0.014, 0.008, 0.009), mat=pearl, parent=an, coll=co)
        self.set_face('smile')
        self.pose({})

    def _hair(self, head, face, a, b, c):
        """Frisur: Haarkappe mit Seitenscheitel + Wellen, die das Gesicht einrahmen."""
        co = self.coll
        hm = principled('sh_hair', hexc('#7E3326'), rough=0.34, sheen=0.4, coat=0.25, aniso=0.8, bump=(26, 0.35, 2, 'wave'))
        self.hairmat = hm
        cap = prim('sphere', 'sh_haircap', (0, 0, 0.13), scale=(a * 1.06, b * 1.07, c * 1.05), mat=hm, parent=head, seg=128, coll=co)
        import bmesh
        bm = bmesh.new(); bm.from_mesh(cap.data)
        kill = []
        for v in bm.verts:
            x, y, z = v.co
            ax = min(1.0, abs(x) / (a * 1.06))
            if y < 0:
                front = -y / (b * 1.07)
                zt = 0.098 - 0.11 * ax ** 1.6 + 0.022 * (x / a)
                zt = zt * front + (-0.06) * (1 - front)
            else:
                zt = -0.07 - 0.03 * (y / b)
            if z < zt:
                kill.append(v)
        bmesh.ops.delete(bm, geom=kill, context='VERTS')
        bm.to_mesh(cap.data); bm.free()
        so = cap.modifiers.new('sol', 'SOLIDIFY'); so.thickness = 0.01; so.offset = -1
        sb = cap.modifiers.new('sub', 'SUBSURF'); sb.render_levels = 2
        # Wellen-Locken, die das Gesicht rahmen
        for s in (-1, 1):
            for k in range(3):
                ph0 = 0.7 + 0.25 * k
                pts, radii = [], []
                for i in range(14):
                    u = i / 13
                    zz = 0.06 - 0.17 * u - 0.01 * k
                    rr = a * (1.02 + 0.06 * u) - 0.004 * k
                    yy = -0.04 + 0.05 * k + 0.012 * math.sin(u * 7 + ph0)
                    xx = s * (rr + 0.012 * math.sin(u * 9 + ph0 * 2))
                    pts.append((xx, yy, 0.13 + zz))
                    radii.append(0.02 * (1 - 0.75 * u) * (0.9 + 0.1 * k))
                tube(f'sh_lock{s}{k}', pts, 0.02, 12, hm, co, radii=radii).parent = head
        # Schwungvoller Pony vom Seitenscheitel: mehrere Strähnen
        for j in range(5):
            pts = []
            for i in range(12):
                u = i / 11
                x = 0.045 - (0.16 + 0.008 * j) * u
                z = 0.13 + 0.125 - 0.007 * j - (0.018 + 0.004 * j) * u - 0.014 * u * u
                zz = (z - 0.13) / c
                k_ = max(0.05, 1 - (x / (a * 1.06)) ** 2 - zz ** 2)
                y = -b * 1.07 * math.sqrt(k_) - 0.006
                pts.append((x, y, z))
            tube(f'sh_fringe{j}', pts, 0.01, 10, hm, co, radii=[0.004 + 0.009 * math.sin(math.pi * (0.15 + 0.85 * i / 11)) for i in range(12)]).parent = head

    def _bodice(self, dress, skin):
        """Torso-Material: Kleid unten, Haut über einem Herz-Ausschnitt."""
        mat = dress.copy(); mat.name = 'sh_bodice'
        nt = mat.node_tree
        out = [n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL'][0]
        dsh = out.inputs[0].links[0].from_socket
        sk = nt.nodes.new('ShaderNodeBsdfPrincipled')
        sk.inputs['Base Color'].default_value = (*hexc('#F8C6AE'), 1)
        sk.inputs['Roughness'].default_value = 0.4
        sk.inputs['Subsurface Weight'].default_value = 0.3
        sk.inputs['Subsurface Radius'].default_value = (1.0, 0.5, 0.35)
        sk.inputs['Subsurface Scale'].default_value = 0.05
        tc = nt.nodes.new('ShaderNodeTexCoord')
        sep = nt.nodes.new('ShaderNodeSeparateXYZ')
        nt.links.new(tc.outputs['Object'], sep.inputs[0])
        ax = nt.nodes.new('ShaderNodeMath'); ax.operation = 'ABSOLUTE'
        nt.links.new(sep.outputs['X'], ax.inputs[0])
        # Herzausschnitt: Schwelle = 0.31 + 0.25*|x| - 0.03*exp(...)  (vorne tiefer)
        k = nt.nodes.new('ShaderNodeMath'); k.operation = 'MULTIPLY_ADD'
        k.inputs[1].default_value = 0.22; k.inputs[2].default_value = 0.305
        nt.links.new(ax.outputs[0], k.inputs[0])
        # vorne (y<0) zählt, hinten Schwelle höher
        yb = nt.nodes.new('ShaderNodeMath'); yb.operation = 'MULTIPLY_ADD'
        yb.inputs[1].default_value = 0.35; yb.inputs[2].default_value = 0.0
        nt.links.new(sep.outputs['Y'], yb.inputs[0])
        cl = nt.nodes.new('ShaderNodeMath'); cl.operation = 'MAXIMUM'; cl.inputs[1].default_value = 0.0
        nt.links.new(yb.outputs[0], cl.inputs[0])
        thr = nt.nodes.new('ShaderNodeMath'); thr.operation = 'ADD'
        nt.links.new(k.outputs[0], thr.inputs[0]); nt.links.new(cl.outputs[0], thr.inputs[1])
        st = nt.nodes.new('ShaderNodeMath'); st.operation = 'GREATER_THAN'
        nt.links.new(sep.outputs['Z'], st.inputs[0]); nt.links.new(thr.outputs[0], st.inputs[1])
        mx = nt.nodes.new('ShaderNodeMixShader')
        nt.links.new(st.outputs[0], mx.inputs[0])
        nt.links.new(dsh, mx.inputs[1]); nt.links.new(sk.outputs[0], mx.inputs[2])
        nt.links.new(mx.outputs[0], out.inputs[0])
        return mat

    def _skirt(self, hips, mat, z0, length, prof, folds, fold_amp):
        co = self.coll
        vs, fs = [], []
        NS, NZ = 128, 16
        for i in range(NZ + 1):
            u = i / NZ
            z = z0 - length * u
            r0 = prof(u)
            for k in range(NS):
                a_ = 2 * math.pi * k / NS
                rr = r0 * (1 + fold_amp * u ** 1.3 * math.sin(folds * a_ + 0.6 * math.sin(3 * a_)))
                vs.append((rr * math.cos(a_), rr * math.sin(a_) * 0.82, z))
        for i in range(NZ):
            for k in range(NS):
                a_ = i * NS + k; b_ = i * NS + (k + 1) % NS
                fs.append((a_, b_, b_ + NS, a_ + NS))
        skirt = mesh_obj('sh_skirt', vs, fs, mat, coll=co)
        skirt.parent = hips
        so = skirt.modifiers.new('sol', 'SOLIDIFY'); so.thickness = 0.008
        sb = skirt.modifiers.new('s', 'SUBSURF'); sb.render_levels = 1
        self.skirt = skirt

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
        mr.inputs['To Min'].default_value = 0.8; mr.inputs['To Max'].default_value = 1.0
        nt.links.new(s.outputs[0], mr.inputs[0])
        ln = nt.nodes.new('ShaderNodeVectorMath'); ln.operation = 'LENGTH'
        nt.links.new(tc.outputs['Object'], ln.inputs[0])
        m2 = nt.nodes.new('ShaderNodeMath'); m2.operation = 'MULTIPLY'; m2.inputs[1].default_value = 140
        nt.links.new(ln.outputs['Value'], m2.inputs[0])
        s2 = nt.nodes.new('ShaderNodeMath'); s2.operation = 'SINE'
        nt.links.new(m2.outputs[0], s2.inputs[0])
        mr2 = nt.nodes.new('ShaderNodeMapRange')
        mr2.inputs['From Min'].default_value = -1; mr2.inputs['From Max'].default_value = 1
        mr2.inputs['To Min'].default_value = 0.93; mr2.inputs['To Max'].default_value = 1.0
        nt.links.new(s2.outputs[0], mr2.inputs[0])
        mul = nt.nodes.new('ShaderNodeMix'); mul.data_type = 'RGBA'; mul.blend_type = 'MULTIPLY'
        mul.inputs['Factor'].default_value = 1.0
        nt.links.new(base, mul.inputs['A'])
        cmb = nt.nodes.new('ShaderNodeMath'); cmb.operation = 'MULTIPLY'
        nt.links.new(mr.outputs[0], cmb.inputs[0]); nt.links.new(mr2.outputs[0], cmb.inputs[1])
        nt.links.new(cmb.outputs[0], mul.inputs['B'])
        nt.links.new(mul.outputs['Result'], b.inputs['Base Color'])

    def _hand(self, wr, s, skin, nail, co):
        palm = prim('sphere', f'sh_palm{s}', (0, 0, -0.042), scale=(0.017, 0.032, 0.044), mat=skin, parent=wr, coll=co)
        palm.rotation_euler = (0, 0, R(90))
        fingers = []
        for k in range(4):
            y = -0.022 + k * 0.0145
            ln = [0.058, 0.066, 0.062, 0.05][k]
            f = tube(f'sh_fing{s}{k}', [(0, 0, 0), (0, 0, -ln * 0.5), (0, 0.002 * s, -ln)], 0.0072, 10, skin, co,
                     radii=[0.0078, 0.007, 0.0055])
            fp = empty(f'sh_fpiv{s}{k}', (0.0, y, -0.078), parent=wr, coll=co)
            fp.rotation_mode = 'XYZ'
            f.parent = fp
            nl = prim('sphere', f'sh_nail{s}{k}', (-0.0035, 0.002 * s, -ln + 0.008), scale=(0.0035, 0.005, 0.008), mat=nail, parent=fp, coll=co)
            fingers.append(fp)
        th = tube(f'sh_thumb{s}', [(0, 0, 0), (0, 0, -0.024), (0, 0, -0.042)], 0.0085, 10, skin, co, radii=[0.009, 0.0082, 0.006])
        tp = empty(f'sh_tpiv{s}', (-0.01, -0.03, -0.032), parent=wr, coll=co)
        tp.rotation_mode = 'XYZ'
        tp.rotation_euler = (R(30), R(-30), 0)
        th.parent = tp
        self.hands.append((fingers, tp))

    # --------------------------------------------------------- Animation
    def set_face(self, mouth='smile', blink=0.0, look=(0, 0), brow=0.0, brow_tilt=0.0, shell=0.0, lids_wide=0.0):
        """blink 0..1; look (yaw,pitch) Grad; brow: hoch (+)/runter(-); shell: 0 offen .. 1 zu."""
        for k, ob in self.mouths.items():
            hide = (k != mouth)
            for o in [ob] + list(ob.children_recursive):
                o.hide_render = hide
                o.hide_viewport = hide
        for e in self.eyes:
            e.rotation_euler = (R(-look[1]), 0, R(look[0]))
        op = -54 - 8 * lids_wide
        for l in self.lids:
            l.rotation_euler = (R(lerp(op, 66, blink)), 0, 0)
        for l in self.lowlids:
            l.rotation_euler = (R(180 + 44 - 12 * blink - 6 * lids_wide), 0, 0)
        for i, bp in enumerate(self.brows):
            s = -1 if i == 0 else 1
            bp.location.z = bp['z0'] + 0.016 * brow
            bp.rotation_euler = (0, R(s * brow_tilt * 16), 0)
        self.shell_piv.rotation_euler = (R(-shell * 62), 0, 0)

    def pose(self, p):
        """p: dict Gelenkname -> (rx,ry,rz) in Grad; Rest neutral. 'root_loc', 'root_rot', 'fingers' (0..1)."""
        neutral = {'shoulderL': (0, -8, 0), 'shoulderR': (0, 8, 0), 'elbowL': (-14, 0, 0), 'elbowR': (-14, 0, 0),
                   'wristL': (0, 0, 0), 'wristR': (0, 0, 0)}
        for n, e in self.j.items():
            v = p.get(n, neutral.get(n, (0, 0, 0)))
            e.rotation_euler = tuple(R(x) for x in v)
        if 'root_loc' in p: self.root.location = p['root_loc']
        if 'root_rot' in p: self.root.rotation_euler = tuple(R(x) for x in p['root_rot'])
        if 'hips_loc' in p: self.j['hips'].location = p['hips_loc']
        else: self.j['hips'].location = (0, 0, 0.74)
        if hasattr(self, 'skirt'):
            sit = p.get('sit', 0.0)
            self.skirt.rotation_euler = (R(-62 * sit), 0, 0)
            self.skirt.scale = (1.0, 1.0, 1.0 - 0.35 * sit)
            self.skirt.location = (0, -0.03 * sit, 0.0)
        curl = p.get('fingers', 0.25)
        for fingers, tp in self.hands:
            for f in fingers:
                f.rotation_euler = (R(-70 * curl), 0, 0)
            tp.rotation_euler = (R(30 + 30 * curl), R(-30), 0)

    def head_world(self):
        bpy.context.view_layer.update()
        return self.j['head'].matrix_world @ Vector((0, 0, 0.13))
