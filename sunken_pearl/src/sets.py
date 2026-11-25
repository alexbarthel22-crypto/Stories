"""Sets: Unterwasser-Turm, Meeresoberfläche, Fische, Quallen, Nebel."""
import bpy, bmesh, math
from mathutils import Vector
from lib import *

R = math.radians
FLOOR_H = 3.6
TOWER_R = 12.0


def fog_all(density, color, skip=()):
    """Unterwasser-Dunst in jedes Material einmischen (Kamera-Distanz)."""
    for mat in D.materials:
        if not mat.use_nodes or mat.name in skip or mat.get('nofog'):
            continue
        nt = mat.node_tree
        out = [n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL']
        if not out or not out[0].inputs[0].links:
            continue
        out = out[0]
        src = out.inputs[0].links[0].from_socket
        cd = nt.nodes.new('ShaderNodeCameraData')
        m1 = nt.nodes.new('ShaderNodeMath'); m1.operation = 'MULTIPLY'; m1.inputs[1].default_value = -density
        nt.links.new(cd.outputs['View Distance'], m1.inputs[0])
        m2 = nt.nodes.new('ShaderNodeMath'); m2.operation = 'EXPONENT'
        nt.links.new(m1.outputs[0], m2.inputs[0])
        m3 = nt.nodes.new('ShaderNodeMath'); m3.operation = 'SUBTRACT'; m3.inputs[0].default_value = 1.0
        nt.links.new(m2.outputs[0], m3.inputs[1])
        em = nt.nodes.new('ShaderNodeEmission'); em.inputs[0].default_value = (*color, 1); em.inputs[1].default_value = 1.0
        mx = nt.nodes.new('ShaderNodeMixShader')
        nt.links.new(m3.outputs[0], mx.inputs[0])
        nt.links.new(src, mx.inputs[1]); nt.links.new(em.outputs[0], mx.inputs[2])
        nt.links.new(mx.outputs[0], out.inputs[0])
        mat['fog_m1'] = m1.name
        mat['fog_em'] = em.name


def set_fog(density=None, color=None):
    for mat in D.materials:
        if 'fog_m1' in mat:
            nt = mat.node_tree
            if density is not None: nt.nodes[mat['fog_m1']].inputs[1].default_value = -density
            if color is not None: nt.nodes[mat['fog_em']].inputs[0].default_value = (*color, 1)


def window_mat(name='winlit', warm=(1.0, 0.42, 0.12), strength=1.8, onrate=0.6, seed_scale=16.0):
    """Leuchtende Fensterscheibe, pro Fenster (Winkel-Index + Objekt-Zufall) an/aus und Farbvariation."""
    mat = D.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    for n in list(nt.nodes): nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    tc = nt.nodes.new('ShaderNodeTexCoord')
    sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    nt.links.new(tc.outputs['Object'], sep.inputs[0])
    at = nt.nodes.new('ShaderNodeMath'); at.operation = 'ARCTAN2'
    nt.links.new(sep.outputs['Y'], at.inputs[0]); nt.links.new(sep.outputs['X'], at.inputs[1])
    mm = nt.nodes.new('ShaderNodeMath'); mm.operation = 'MULTIPLY'; mm.inputs[1].default_value = seed_scale / (2 * math.pi)
    nt.links.new(at.outputs[0], mm.inputs[0])
    fl = nt.nodes.new('ShaderNodeMath'); fl.operation = 'FLOOR'
    nt.links.new(mm.outputs[0], fl.inputs[0])
    zq = nt.nodes.new('ShaderNodeMath'); zq.operation = 'ROUND'
    nt.links.new(sep.outputs['Z'], zq.inputs[0])
    oi = nt.nodes.new('ShaderNodeObjectInfo')
    cmb = nt.nodes.new('ShaderNodeCombineXYZ')
    nt.links.new(fl.outputs[0], cmb.inputs[0]); nt.links.new(oi.outputs['Random'], cmb.inputs[1])
    wn = nt.nodes.new('ShaderNodeTexWhiteNoise'); wn.noise_dimensions = '3D'
    nt.links.new(cmb.outputs[0], wn.inputs['Vector'])
    sepc = nt.nodes.new('ShaderNodeSeparateColor')
    nt.links.new(wn.outputs['Color'], sepc.inputs[0])
    gt = nt.nodes.new('ShaderNodeMath'); gt.operation = 'LESS_THAN'; gt.inputs[1].default_value = onrate
    nt.links.new(sepc.outputs[0], gt.inputs[0])
    # Farbe: warm bis leicht türkis
    cr = nt.nodes.new('ShaderNodeValToRGB')
    el = cr.color_ramp.elements
    el[0].position = 0.0; el[0].color = (1.0, 0.3, 0.06, 1)
    el[1].position = 1.0; el[1].color = (0.3, 0.8, 1.0, 1)
    e = el.new(0.6); e.color = (1.0, 0.5, 0.15, 1)
    e = el.new(0.9); e.color = (1.0, 0.6, 0.22, 1)
    nt.links.new(sepc.outputs[1], cr.inputs[0])
    st = nt.nodes.new('ShaderNodeMath'); st.operation = 'MULTIPLY'; st.inputs[1].default_value = strength
    br = nt.nodes.new('ShaderNodeMath'); br.operation = 'MULTIPLY_ADD'; br.inputs[1].default_value = 0.7; br.inputs[2].default_value = 0.5
    nt.links.new(sepc.outputs[2], br.inputs[0])
    m4 = nt.nodes.new('ShaderNodeMath'); m4.operation = 'MULTIPLY'
    nt.links.new(gt.outputs[0], m4.inputs[0]); nt.links.new(br.outputs[0], m4.inputs[1])
    nt.links.new(m4.outputs[0], st.inputs[0])
    em = nt.nodes.new('ShaderNodeEmission')
    nt.links.new(cr.outputs[0], em.inputs[0]); nt.links.new(st.outputs[0], em.inputs[1])
    gl = nt.nodes.new('ShaderNodeBsdfGlossy'); gl.inputs['Roughness'].default_value = 0.05
    gl.inputs[0].default_value = (0.05, 0.08, 0.1, 1)
    ad = nt.nodes.new('ShaderNodeAddShader')
    nt.links.new(em.outputs[0], ad.inputs[0]); nt.links.new(gl.outputs[0], ad.inputs[1])
    nt.links.new(ad.outputs[0], out.inputs[0])
    mat['strength_node'] = st.name
    return mat


def hull_mat(name='hull', col='#2F5A5A', col2='#4A7A66'):
    """Gealtertes Metall mit Patina-Flecken."""
    mat = principled(name, hexc(col), rough=0.5, metal=0.35, bump=(8, 0.25, 8))
    nt = mat.node_tree
    b = nt.nodes[mat['bsdf']]
    tc = nt.nodes.new('ShaderNodeTexCoord')
    nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 0.35; nz.inputs['Detail'].default_value = 8
    nt.links.new(tc.outputs['Object'], nz.inputs['Vector'])
    cr = nt.nodes.new('ShaderNodeValToRGB')
    el = cr.color_ramp.elements
    el[0].position = 0.4; el[0].color = (*hexc(col), 1)
    el[1].position = 0.65; el[1].color = (*hexc(col2), 1)
    nt.links.new(nz.outputs['Fac'], cr.inputs[0])
    nt.links.new(cr.outputs[0], b.inputs['Base Color'])
    return mat


class Mats:
    def __init__(self):
        self.hull = hull_mat()
        self.hull_dark = hull_mat('hull2', '#16302F', '#22433A')
        self.brass = principled('brass', hexc('#C8923A'), rough=0.28, metal=1.0, bump=(60, 0.05))
        self.copper = principled('copper', hexc('#B4643C'), rough=0.35, metal=1.0)
        self.patina = principled('patina', hexc('#4FA38E'), rough=0.7, metal=0.2, bump=(30, 0.3))
        self.winlit = window_mat()
        self.winobj = window_mat('winobj', seed_scale=0.0)
        self.lamp = emission('lampw', (1.0, 0.75, 0.45), 18.0)
        self.lampc = emission('lampc', (0.35, 0.9, 1.0), 14.0)
        self.red = emission('lampr', (1.0, 0.15, 0.08), 20.0)
        self.neon = emission('neon', (1.0, 0.86, 0.6), 22.0)
        self.barn = principled('barn', hexc('#D8D2C2'), rough=0.8, bump=(80, 0.4))
        self.kelp = principled('kelp', hexc('#5E7A22'), rough=0.6, sss=0.4, sss_r=(0.4, 1, 0.2))
        self.glassdome = window_glass('domeglass', (0.75, 0.95, 1.0), 0.12)


def floor_module(M, coll, nwin=16):
    """Ein Stockwerk (Höhe FLOOR_H) als wiederverwendbare Mesh-Daten. Gibt Liste (data, mods) zurück."""
    parts = []
    # Wand
    w = prim('cyl', 'mod_wall', (0, 0, FLOOR_H / 2), scale=(TOWER_R, TOWER_R, FLOOR_H / 2), mat=M.hull, seg=96, coll=coll)
    parts.append(w)
    # Fenster: Messingring + Scheibe
    for i in range(nwin):
        a = 2 * math.pi * (i + 0.5) / nwin
        x, y = math.cos(a) * TOWER_R, math.sin(a) * TOWER_R
        fr = prim('torus', f'mod_fr{i}', (x * 1.01, y * 1.01, FLOOR_H * 0.52), rot=(0, R(90), a), mat=M.brass, R=0.85, r=0.13, seg=28, seg2=10, coll=coll)
        gl = prim('cyl', f'mod_gl{i}', (x * 1.004, y * 1.004, FLOOR_H * 0.52), rot=(0, R(90), a), scale=(0.8, 0.8, 0.04), mat=M.winlit, seg=28, coll=coll)
        parts += [fr, gl]
        # Nieten um Fenster
        for k in range(8):
            b = 2 * math.pi * k / 8
            off = Vector((0, math.cos(b) * 1.08, math.sin(b) * 1.08))
            rv = Vector((x, y, 0)).normalized()
            tang = Vector((-math.sin(a), math.cos(a), 0))
            p = Vector((x * 1.006, y * 1.006, FLOOR_H * 0.52)) + tang * off.y + Vector((0, 0, off.z))
            parts.append(prim('sphere', f'mod_rv{i}_{k}', tuple(p), scale=(0.07,) * 3, mat=M.brass, seg=8, coll=coll))
    # Gesims unten
    parts.append(prim('torus', 'mod_trim', (0, 0, 0.05), mat=M.hull_dark, R=TOWER_R + 0.12, r=0.16, seg=96, seg2=8, coll=coll))
    for p in parts:
        for m in p.modifiers:
            pass
    # Join zu einem Objekt
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = w
    with bpy.context.temp_override(active_object=w, selected_editable_objects=parts, selected_objects=parts):
        bpy.ops.object.join()
    from mathutils import Matrix
    w.data.transform(w.matrix_basis)
    w.matrix_basis = Matrix.Identity(4)
    w.modifiers.clear()
    w.name = 'floor_module'
    return w


def ring_deck(M, coll, idx):
    """Alle 10 Stockwerke: ausladender Ring mit Lampen."""
    obs = []
    d = lathe('deck', [(TOWER_R, -0.5), (TOWER_R + 1.6, -0.2), (TOWER_R + 1.8, 0.0), (TOWER_R + 1.6, 0.25), (TOWER_R, 0.4)], 96, M.hull_dark, coll, False, False)
    obs.append(d)
    obs.append(prim('torus', 'deckrim', (0, 0, 0.0), mat=M.brass, R=TOWER_R + 1.8, r=0.09, seg=96, seg2=8, coll=coll))
    for i in range(6):
        a = 2 * math.pi * (i + 0.5) / 6
        l = add_light('POINT', 'decklight', ((TOWER_R + 2.4) * math.cos(a), (TOWER_R + 2.4) * math.sin(a), -0.6), 900,
                      (0.4, 0.85, 1.0) if idx % 2 else (1.0, 0.7, 0.4), 0.3, coll=coll)
        obs.append(l)
    for i in range(24):
        a = 2 * math.pi * i / 24
        obs.append(prim('sphere', f'decklamp{i}', ((TOWER_R + 1.75) * math.cos(a), (TOWER_R + 1.75) * math.sin(a), -0.18),
                        scale=(0.14,) * 3, mat=M.lampc if idx % 2 else M.lamp, seg=10, coll=coll))
    return obs


def number_plate(M, coll, txt, ang, z, mat=None):
    """Etagenschild an der Fassade."""
    a = R(ang)
    x, y = math.cos(a) * (TOWER_R + 0.05), math.sin(a) * (TOWER_R + 0.05)
    pl = prim('cube', 'plate', (x, y, z), rot=(0, 0, a), scale=(0.08, 1.7, 0.75), mat=M.hull_dark, bevel=0.05, coll=coll)
    fr = prim('cube', 'platefr', (x * 1.002, y * 1.002, z), rot=(0, 0, a), scale=(0.06, 1.8, 0.85), mat=M.brass, bevel=0.04, coll=coll)
    t = text_obj('platet', txt, 1.0, mat or M.neon, extrude=0.02, coll=coll)
    t.location = (x * 1.012 + math.cos(a) * 0.05, y * 1.012 + math.sin(a) * 0.05, z)
    t.rotation_euler = (R(90), 0, a + R(90))
    return [pl, fr, t]


def build_tower(M, coll, f_top, f_bot, plates=True, rails=True, seed=1):
    """Stockwerke f_top..f_bot (negativ, f_top > f_bot). Etage -k liegt bei z=-k*FLOOR_H."""
    mod = floor_module(M, coll)
    mod.hide_render = True; mod.hide_viewport = True
    obs = []
    rg = rnd(seed)
    for f in range(f_top, f_bot - 1, -1):
        z = f * FLOOR_H
        o = D.objects.new(f'floor{f}', mod.data)
        link(o, coll)
        o.location = (0, 0, z)
        o.rotation_euler = (0, 0, R((f % 3) * 7.5))
        obs.append(o)
        if f % 10 == 0:
            for d in ring_deck(M, coll, f // 10):
                d.location.z += z
        if plates and f % 5 == 0:
            for p in number_plate(M, coll, f'{f}', 90 - 11.25 + (f % 3) * 7.5 + 180, z + FLOOR_H * 0.52):
                pass
    # vertikale Rippen
    zt, zb = f_top * FLOOR_H + FLOOR_H, f_bot * FLOOR_H
    for i in range(8):
        a = 2 * math.pi * i / 8 + R(11.25)
        prim('cube', f'rib{i}', (math.cos(a) * (TOWER_R + 0.25), math.sin(a) * (TOWER_R + 0.25), (zt + zb) / 2), rot=(0, 0, a),
             scale=(0.35, 0.28, (zt - zb) / 2), mat=M.hull_dark, bevel=0.08, coll=coll)
    # Seepocken + Algen an der Fassade
    barn = prim('sphere', 'barnsrc', scale=(1, 1, 0.6), mat=M.barn, seg=10, coll=coll)
    barn.hide_render = True
    for k in range(int((zt - zb) * 6)):
        a = rg.uniform(0, 2 * math.pi); z = rg.uniform(zb, zt)
        s = rg.uniform(0.05, 0.18)
        o = D.objects.new('barn', barn.data); link(o, coll)
        o.location = (math.cos(a) * (TOWER_R + 0.02), math.sin(a) * (TOWER_R + 0.02), z)
        o.rotation_euler = (0, R(90), a); o.scale = (s, s, s * 0.6)
    return obs


def kelp_strand(name, M, base, height, phase, coll, t=0.0, mat=None):
    pts = []
    n = 14
    for k in range(n):
        u = k / (n - 1)
        sway = math.sin(t * 0.9 + phase + u * 2.5) * 0.25 * u * height * 0.15
        pts.append((base[0] + sway, base[1] + sway * 0.4, base[2] + u * height))
    ob = tube(name, pts, 0.06, 6, mat or M.kelp, coll, radii=[0.08 * (1 - 0.6 * k / (n - 1)) for k in range(n)])
    return ob


def fish_mesh(coll, mat, name='fishsrc'):
    """Fisch als ein Mesh, Länge entlang +X (Kopf bei +X)."""
    from mathutils import Matrix
    prof = [(0.0, -0.5), (0.06, -0.44), (0.15, -0.22), (0.19, 0.0), (0.16, 0.2), (0.09, 0.36), (0.05, 0.43), (0.0, 0.48)]
    body = lathe(name, prof, 16, mat, coll)
    me = body.data
    bm = bmesh.new(); bm.from_mesh(me)
    # Schwanzflosse
    v = [bm.verts.new(p) for p in [(0, 0, -0.42), (0, 0.17, -0.66), (0, 0, -0.58), (0, -0.17, -0.66)]]
    bm.faces.new((v[0], v[1], v[2])); bm.faces.new((v[0], v[2], v[3]))
    # Rückenflosse
    v = [bm.verts.new(p) for p in [(0.0, 0.17, -0.1), (0.0, 0.3, -0.2), (0.0, 0.17, 0.15)]]
    bm.faces.new(v)
    bmesh.ops.scale(bm, vec=(0.55, 1.0, 1.0), verts=bm.verts)
    bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(R(90), 3, 'Y'), verts=bm.verts)
    bm.to_mesh(me); bm.free()
    return body


def fish_mat(name='fishm', col='#9FB8C8', col2='#E8EEF2', emit=None):
    mat = color_ramp_mat(name, [(0.0, hexc(col2)), (0.5, hexc(col2)), (0.55, hexc(col)), (1.0, hexc(col))], coord='X',
                         lo=-0.18, hi=0.18, rough=0.25, metal=0.5, film=300)
    if emit:
        b = mat.node_tree.nodes[mat['bsdf']]
        b.inputs['Emission Color'].default_value = (*emit, 1)
        b.inputs['Emission Strength'].default_value = 2.0
    return mat


class School:
    """Fischschwarm: Instanzen mit Boid-artiger Bahn (deterministisch über t)."""
    def __init__(self, coll, n, center, radius, size=0.5, seed=3, mat=None, speed=1.0, src=None):
        self.rg = rnd(seed)
        mat = mat or fish_mat()
        if src is None:
            src = fish_mesh(coll, mat, f'fishsrc{seed}')
        src.hide_render = True
        self.src = src
        self.fish = []
        self.center = Vector(center); self.radius = radius; self.speed = speed
        for i in range(n):
            o = D.objects.new(f'fish{seed}_{i}', src.data)
            link(o, coll)
            s = size * self.rg.uniform(0.7, 1.2)
            o.scale = (s, s, s)
            o.rotation_mode = 'XYZ'
            self.fish.append((o, self.rg.uniform(0, 6.28), self.rg.uniform(-1, 1), self.rg.uniform(0.6, 1.0), self.rg.uniform(0, 6.28)))

    def update(self, t):
        for o, ph, h, r, wob in self.fish:
            a = ph + t * 0.25 * self.speed / max(self.radius * 0.1, 0.3)
            rr = self.radius * r
            p = self.center + Vector((math.cos(a) * rr, math.sin(a) * rr * 0.6, h * self.radius * 0.3 + math.sin(t * 1.3 + wob) * 0.2))
            o.location = p
            vx, vy = -math.sin(a) * rr, math.cos(a) * rr * 0.6
            o.rotation_euler = (0, 0, math.atan2(vy, vx) + 0.12 * math.sin(t * 9 + wob))


def jelly(coll, name, loc, size=1.0, col=(0.5, 0.8, 1.0), t=0.0, strength=3.0):
    pulse = 1 + 0.08 * math.sin(t * 3)
    prof = [(0.0, 0.5), (0.25, 0.47), (0.42, 0.35), (0.5, 0.15), (0.52, 0.0), (0.45, 0.02), (0.3, 0.2), (0.0, 0.25)]
    m = D.materials.get(name + 'm') or emission(name + 'm', col, strength, alpha=0.55)
    m['nofog'] = 0
    b = lathe(name, [(r * pulse, z) for r, z in prof], 32, m, coll)
    b.location = loc; b.scale = (size,) * 3
    for k in range(8):
        a = 2 * math.pi * k / 8
        pts = [(math.cos(a) * 0.35, math.sin(a) * 0.35, 0)]
        for j in range(1, 10):
            u = j / 9
            pts.append((math.cos(a) * 0.35 * (1 - u * 0.3) + 0.08 * math.sin(t * 2 + j * 0.7 + k), math.sin(a) * 0.35 * (1 - u * 0.3), -u * 1.6))
        tt = tube(name + f't{k}', pts, 0.015, 5, m, coll)
        tt.parent = b
    return b
