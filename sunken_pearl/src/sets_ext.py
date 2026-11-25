"""Meeresoberfläche (Turmspitze) und Perlenkammer am Grund."""
import bpy, bmesh, math
from mathutils import Vector, Matrix
from lib import *
from sets import Mats, fog_all, fish_mat, School, jelly, hull_mat, TOWER_R, window_mat
from shelly import scallop

R = math.radians


def godray(name, top, bottom, r_top, r_bot, color=(0.6, 0.9, 1.0), strength=0.6, coll=None):
    """Lichtschacht: Kegel mit Emission, transparent, Fresnel-weich."""
    mat = D.materials.get(name + 'm')
    if mat is None:
        mat = D.materials.new(name + 'm')
        mat.use_nodes = True
        nt = mat.node_tree
        for n in list(nt.nodes): nt.nodes.remove(n)
        out = nt.nodes.new('ShaderNodeOutputMaterial')
        lw = nt.nodes.new('ShaderNodeLayerWeight'); lw.inputs[0].default_value = 0.5
        inv = nt.nodes.new('ShaderNodeMath'); inv.operation = 'SUBTRACT'; inv.inputs[0].default_value = 1.0
        nt.links.new(lw.outputs['Facing'], inv.inputs[1])
        pw = nt.nodes.new('ShaderNodeMath'); pw.operation = 'POWER'; pw.inputs[1].default_value = 2.5
        nt.links.new(inv.outputs[0], pw.inputs[0])
        # Verlauf entlang Höhe (Generated Z)
        tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ')
        nt.links.new(tc.outputs['Generated'], sep.inputs[0])
        mz = nt.nodes.new('ShaderNodeMath'); mz.operation = 'POWER'; mz.inputs[1].default_value = 1.5
        nt.links.new(sep.outputs['Z'], mz.inputs[0])
        mul = nt.nodes.new('ShaderNodeMath'); mul.operation = 'MULTIPLY'
        nt.links.new(pw.outputs[0], mul.inputs[0]); nt.links.new(mz.outputs[0], mul.inputs[1])
        st = nt.nodes.new('ShaderNodeMath'); st.operation = 'MULTIPLY'; st.inputs[1].default_value = strength
        nt.links.new(mul.outputs[0], st.inputs[0])
        em = nt.nodes.new('ShaderNodeEmission'); em.inputs[0].default_value = (*color, 1)
        nt.links.new(st.outputs[0], em.inputs[1])
        tr = nt.nodes.new('ShaderNodeBsdfTransparent')
        ad = nt.nodes.new('ShaderNodeAddShader')
        nt.links.new(em.outputs[0], ad.inputs[0]); nt.links.new(tr.outputs[0], ad.inputs[1])
        nt.links.new(ad.outputs[0], out.inputs[0])
        mat['nofog'] = 1
        mat['st'] = st.name
    h = (Vector(top) - Vector(bottom)).length
    ob = lathe(name, [(r_bot, 0), (r_top, h)], 32, mat, coll, False, False)
    ob.location = bottom
    d = (Vector(top) - Vector(bottom)).normalized()
    ob.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    ob.visible_shadow = False
    ob.visible_diffuse = False
    ob.visible_glossy = False
    return ob


def rock_mat(name='rock', c1='#3B4A4A', c2='#5E6B5F'):
    mat = principled(name, hexc(c1), rough=0.85, bump=(3, 0.8, 10))
    nt = mat.node_tree; b = nt.nodes[mat['bsdf']]
    tc = nt.nodes.new('ShaderNodeTexCoord')
    nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 1.5; nz.inputs['Detail'].default_value = 10
    nt.links.new(tc.outputs['Object'], nz.inputs['Vector'])
    cr = nt.nodes.new('ShaderNodeValToRGB'); el = cr.color_ramp.elements
    el[0].position = 0.35; el[0].color = (*hexc(c1), 1); el[1].position = 0.7; el[1].color = (*hexc(c2), 1)
    nt.links.new(nz.outputs['Fac'], cr.inputs[0]); nt.links.new(cr.outputs[0], b.inputs['Base Color'])
    return mat


def rock(name, loc, size, mat, seed, coll=None, squash=1.0):
    ob = prim('sphere', name, loc, scale=(size, size * 0.9, size * squash), mat=mat, seg=24, coll=coll)
    tex = D.textures.new(name + 'tx', 'CLOUDS'); tex.noise_scale = 0.6 * size; tex.noise_depth = 4
    m = ob.modifiers.new('disp', 'DISPLACE'); m.texture = tex; m.strength = size * 0.45; m.texture_coords = 'OBJECT'
    sub = ob.modifiers.new('sub', 'SUBSURF'); sub.levels = 1; sub.render_levels = 2
    m2 = ob.modifiers.new('disp2', 'DISPLACE'); tex2 = D.textures.new(name + 'tx2', 'CLOUDS'); tex2.noise_scale = 0.12 * size
    m2.texture = tex2; m2.strength = size * 0.06
    ob.rotation_euler = (rnd(seed).uniform(0, 6), rnd(seed + 1).uniform(0, 6), rnd(seed + 2).uniform(0, 6))
    return ob


def sand_mat():
    mat = principled('sand', hexc('#8C8270'), rough=0.95, bump=(25, 0.4, 6))
    nt = mat.node_tree; b = nt.nodes[mat['bsdf']]
    tc = nt.nodes.new('ShaderNodeTexCoord')
    wv = nt.nodes.new('ShaderNodeTexWave'); wv.inputs['Scale'].default_value = 0.6; wv.inputs['Distortion'].default_value = 4
    nt.links.new(tc.outputs['Object'], wv.inputs['Vector'])
    bp = nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.35
    nt.links.new(wv.outputs['Fac'], bp.inputs['Height'])
    old = b.inputs['Normal'].links[0].from_socket
    nt.links.new(old, bp.inputs['Normal'])
    nt.links.new(bp.outputs[0], b.inputs['Normal'])
    return mat


def pearl_material(name='giantpearl'):
    """Perlmutt mit innerem Leuchten (Emission über invertiertem Fresnel), pulsierbar."""
    mat = D.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    for n in list(nt.nodes): nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    b = nt.nodes.new('ShaderNodeBsdfPrincipled')
    b.inputs['Base Color'].default_value = (*hexc('#E6D8E2'), 1)
    b.inputs['Roughness'].default_value = 0.08
    b.inputs['Coat Weight'].default_value = 1.0
    b.inputs['Thin Film Thickness'].default_value = 520
    b.inputs['Thin Film IOR'].default_value = 1.55
    b.inputs['Subsurface Weight'].default_value = 0.3
    b.inputs['Subsurface Radius'].default_value = (1.0, 0.9, 0.85)
    b.inputs['Subsurface Scale'].default_value = 0.3
    tc = nt.nodes.new('ShaderNodeTexCoord')
    nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 3; nz.inputs['Detail'].default_value = 6
    nt.links.new(tc.outputs['Object'], nz.inputs['Vector'])
    bp = nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.05
    nt.links.new(nz.outputs['Fac'], bp.inputs['Height']); nt.links.new(bp.outputs[0], b.inputs['Normal'])
    lw = nt.nodes.new('ShaderNodeLayerWeight'); lw.inputs[0].default_value = 0.35
    cr = nt.nodes.new('ShaderNodeValToRGB'); el = cr.color_ramp.elements
    el[0].position = 0.0; el[0].color = (1.0, 0.97, 0.9, 1)
    el[1].position = 1.0; el[1].color = (0.35, 0.75, 1.0, 1)
    e = el.new(0.6); e.color = (0.95, 0.85, 1.0, 1)
    nt.links.new(lw.outputs['Facing'], cr.inputs[0])
    em = nt.nodes.new('ShaderNodeEmission')
    nt.links.new(cr.outputs[0], em.inputs[0])
    em.inputs[1].default_value = 2.0
    ad = nt.nodes.new('ShaderNodeAddShader')
    nt.links.new(b.outputs[0], ad.inputs[0]); nt.links.new(em.outputs[0], ad.inputs[1])
    nt.links.new(ad.outputs[0], out.inputs[0])
    mat['emit'] = em.name
    mat['nofog'] = 1
    return mat


def iris_material():
    """Riesiges Auge: goldene Iris mit senkrechter Schlitzpupille (Objektkoordinaten Einheitskugel, Blick -Y)."""
    mat = D.materials.new('bigeye')
    mat.use_nodes = True
    nt = mat.node_tree
    for n in list(nt.nodes): nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    nt.links.new(tc.outputs['Object'], sep.inputs[0])
    # radialer Abstand in XZ-Ebene
    cx = nt.nodes.new('ShaderNodeCombineXYZ')
    nt.links.new(sep.outputs['X'], cx.inputs[0]); nt.links.new(sep.outputs['Z'], cx.inputs[2])
    ln = nt.nodes.new('ShaderNodeVectorMath'); ln.operation = 'LENGTH'
    nt.links.new(cx.outputs[0], ln.inputs[0])
    cr = nt.nodes.new('ShaderNodeValToRGB'); el = cr.color_ramp.elements
    el[0].position = 0.0; el[0].color = (1.0, 0.95, 0.4, 1)
    el[1].position = 1.0; el[1].color = (0.15, 0.02, 0.0, 1)
    e = el.new(0.45); e.color = (1.0, 0.55, 0.05, 1)
    e = el.new(0.85); e.color = (0.6, 0.12, 0.0, 1)
    nt.links.new(ln.outputs['Value'], cr.inputs[0])
    # Strahlen
    at = nt.nodes.new('ShaderNodeMath'); at.operation = 'ARCTAN2'
    nt.links.new(sep.outputs['X'], at.inputs[0]); nt.links.new(sep.outputs['Z'], at.inputs[1])
    nz = nt.nodes.new('ShaderNodeTexNoise'); nz.noise_dimensions = '1D'; nz.inputs['Scale'].default_value = 9
    nt.links.new(at.outputs[0], nz.inputs['W'])
    mxr = nt.nodes.new('ShaderNodeMix'); mxr.data_type = 'RGBA'; mxr.blend_type = 'MULTIPLY'; mxr.inputs['Factor'].default_value = 0.5
    nt.links.new(cr.outputs[0], mxr.inputs['A']); nt.links.new(nz.outputs['Color'], mxr.inputs['B'])
    # Pupille: |x| < 0.12*(1-z^2)
    ax = nt.nodes.new('ShaderNodeMath'); ax.operation = 'ABSOLUTE'
    nt.links.new(sep.outputs['X'], ax.inputs[0])
    z2 = nt.nodes.new('ShaderNodeMath'); z2.operation = 'MULTIPLY'
    nt.links.new(sep.outputs['Z'], z2.inputs[0]); nt.links.new(sep.outputs['Z'], z2.inputs[1])
    w = nt.nodes.new('ShaderNodeMath'); w.operation = 'MULTIPLY_ADD'; w.inputs[1].default_value = -0.16; w.inputs[2].default_value = 0.16
    nt.links.new(z2.outputs[0], w.inputs[0])
    self_w = w
    lt = nt.nodes.new('ShaderNodeMath'); lt.operation = 'LESS_THAN'
    nt.links.new(ax.outputs[0], lt.inputs[0]); nt.links.new(w.outputs[0], lt.inputs[1])
    mx = nt.nodes.new('ShaderNodeMix'); mx.data_type = 'RGBA'
    nt.links.new(lt.outputs[0], mx.inputs['Factor'])
    nt.links.new(mxr.outputs['Result'], mx.inputs['A'])
    mx.inputs['B'].default_value = (0.0, 0.0, 0.0, 1)
    em = nt.nodes.new('ShaderNodeEmission'); em.inputs[1].default_value = 2.5
    nt.links.new(mx.outputs['Result'], em.inputs[0])
    gl = nt.nodes.new('ShaderNodeBsdfGlossy'); gl.inputs['Roughness'].default_value = 0.25
    gl.inputs[0].default_value = (0.15, 0.15, 0.15, 1)
    ad = nt.nodes.new('ShaderNodeAddShader')
    nt.links.new(em.outputs[0], ad.inputs[0]); nt.links.new(gl.outputs[0], ad.inputs[1])
    nt.links.new(ad.outputs[0], out.inputs[0])
    mat['emit'] = em.name
    mat['pupil'] = w.name
    mat['nofog'] = 1
    return mat


class Surface:
    """Nacht-Ozean mit Kuppel der Turmspitze bei (0,0,0)."""

    def __init__(self, coll=None, t=0.0):
        co = self.coll = coll
        M = self.M = Mats()
        # Ozean
        pl = prim('plane', 'ocean', (0, 0, 0), scale=(1, 1, 1), coll=co)
        oc = pl.modifiers.new('ocean', 'OCEAN')
        oc.geometry_mode = 'GENERATE'; oc.size = 6.0; oc.spatial_size = 60; oc.resolution = 14
        oc.repeat_x = 6; oc.repeat_y = 6
        oc.wave_scale = 1.6; oc.choppiness = 1.2; oc.wind_velocity = 14; oc.time = t
        oc.random_seed = 3
        self.ocean = oc
        pl.location = (-180, -180, 0)
        wm = principled('sea', hexc('#082030'), rough=0.1, ior=1.33, spec=0.6)
        pl.data.materials.append(wm)
        for p in pl.data.polygons: p.use_smooth = True
        # Kuppel: Glas-Halbkugel mit innerem Garten und warmem Licht
        r = 9.0
        dome = prim('sphere', 'dome', (0, 0, -1.0), scale=(r, r, r * 0.9), mat=M.glassdome, seg=64, coll=co)
        # Rippen (Messing-Meridiane)
        for k in range(16):
            a = 2 * math.pi * k / 16
            pts = []
            for j in range(20):
                th = R(90) * j / 19
                pts.append((math.cos(a) * r * 1.005 * math.cos(th), math.sin(a) * r * 1.005 * math.cos(th), -1 + r * 0.9 * 1.005 * math.sin(th)))
            tube(f'domerib{k}', pts, 0.09, 8, M.brass, co)
        for z, rr in ((2.0, 0.97), (5.0, 0.82)):
            th = math.asin((z + 1) / (r * 0.9))
            prim('torus', 'domering', (0, 0, z), mat=M.brass, R=r * math.cos(th) * 1.005, r=0.08, seg=96, coll=co)
        # Ring-Plattform auf dem Wasser
        plat = lathe('platform', [(r - 0.3, -1.0), (r + 3.5, -1.0), (r + 3.8, -0.4), (r + 3.6, 0.6), (r + 0.2, 0.6)], 96, M.hull_dark, co, False, False)
        prim('torus', 'platrim', (0, 0, 0.62), mat=M.brass, R=r + 3.6, r=0.1, seg=128, coll=co)
        # Geländer + Lampen
        for k in range(40):
            a = 2 * math.pi * k / 40
            x, y = math.cos(a) * (r + 3.3), math.sin(a) * (r + 3.3)
            prim('cyl', 'post', (x, y, 1.1), scale=(0.04, 0.04, 0.5), mat=M.brass, coll=co)
            if k % 4 == 0:
                prim('sphere', 'postlamp', (x, y, 1.7), scale=(0.13,) * 3, mat=M.lamp, seg=12, coll=co)
        prim('torus', 'rail', (0, 0, 1.6), mat=M.brass, R=r + 3.3, r=0.035, seg=128, coll=co)
        add_light('POINT', 'platl1', (r + 5, -r, 3), 2500, (1.0, 0.7, 0.4), 1.0, coll=co)
        # Innen: warmes Licht, Pflanzen-Silhouetten
        inner = emission('domeinner', (1.0, 0.5, 0.2), 0.6)
        add_light('POINT', 'domel', (0, 0, 3), 3500, (1.0, 0.7, 0.4), 3.0, coll=co)
        rg = rnd(5)
        for k in range(9):
            a = rg.uniform(0, 6.28); d = rg.uniform(2, 6)
            prim('sphere', 'tree', (math.cos(a) * d, math.sin(a) * d, rg.uniform(0.5, 2.0)), scale=(rg.uniform(0.8, 1.6),) * 3,
                 mat=principled('treem', hexc('#1E3B22'), 0.8), seg=16, coll=co)
        # Spitze: Perle auf Antenne
        prim('cyl', 'spire', (0, 0, r * 0.9 - 1 + 1.5), scale=(0.12, 0.12, 1.6), mat=M.brass, coll=co)
        self.top_pearl = prim('sphere', 'toppearl', (0, 0, r * 0.9 - 1 + 3.4), scale=(0.6,) * 3, mat=pearl_material('toppearlm'), seg=32, coll=co)
        set_emit(self.top_pearl.data.materials[0], 6.0)
        # Neon-Schriftzug auf Bogen
        neon = emission('neonsign', (1.0, 0.62, 0.25), 7.0)
        self.neon = neon
        fp = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
        import os
        font = bpy.data.fonts.load(fp) if os.path.exists(fp) else None
        txt = 'SUNKEN PEARL'
        n = len(txt)
        for i, ch in enumerate(txt):
            if ch == ' ':
                continue
            a = R(-90 - 40 + 80 * i / (n - 1))
            t_ = text_obj('ltr', ch, 1.5, neon, extrude=0.12, coll=co, font=font)
            t_.location = (math.cos(a) * (r + 0.5), math.sin(a) * (r + 0.5), 5.3)
            t_.rotation_euler = (R(90), 0, a + R(90))
        # Bojen mit roten Lichtern
        self.buoys = []
        for k, (x, y) in enumerate([(-22, -30), (18, -40), (-40, -10), (30, -15)]):
            b = prim('cyl', 'buoy', (x, y, 0.3), scale=(0.5, 0.5, 0.8), mat=principled('buoym', hexc('#B33A2A'), 0.5), coll=co)
            prim('sphere', 'buoyl', (x, y, 1.3), scale=(0.2,) * 3, mat=M.red, coll=co)
            self.buoys.append(b)
        # Himmel: Mond + Sterne
        moon = prim('sphere', 'moon', (-260, 700, 230), scale=(28,) * 3, mat=emission('moonm', (0.85, 0.92, 1.0), 6.0), coll=co)
        stars = emission('starm', (0.9, 0.95, 1.0), 20.0)
        rg = rnd(77)
        for k in range(160):
            a = rg.uniform(R(40), R(140)); el_ = rg.uniform(R(5), R(60))
            d = 900
            prim('sphere', 'star', (math.cos(a) * d * math.cos(el_), math.sin(a) * d * math.cos(el_), d * math.sin(el_)),
                 scale=(rg.uniform(0.3, 1.0),) * 3, mat=stars, seg=6, coll=co)
        ml = add_light('SUN', 'moonlight', (-260, 700, 230), 1.2, (0.6, 0.75, 1.0), 0.03, coll=co)
        look_at(ml, (0, 0, 0))

    def update(self, t):
        self.ocean.time = t
        for k, b in enumerate(self.buoys):
            b.rotation_euler = (math.sin(t * 1.3 + k) * 0.12, math.cos(t + k) * 0.1, 0)


class Chamber:
    """Perlenkammer. Aufzugtür bei (0,0,0) Blick +Y; Muschel bei (0,16,0)."""

    def __init__(self, coll=None, t=0.0):
        co = self.coll = coll
        M = self.M = Mats()
        rm = rock_mat()
        rm2 = rock_mat('rock2', '#2A3436', '#405048')
        sand = sand_mat()
        g = prim('plane', 'ground', (0, 15, 0), scale=(60, 60, 1), mat=sand, coll=co)
        sub = g.modifiers.new('sub', 'SUBSURF'); sub.subdivision_type = 'SIMPLE'; sub.levels = 6; sub.render_levels = 6
        tx = D.textures.new('dunes', 'CLOUDS'); tx.noise_scale = 6
        dm = g.modifiers.new('disp', 'DISPLACE'); dm.texture = tx; dm.strength = 0.8; dm.texture_coords = 'GLOBAL'
        g.location.z = -0.4
        # Rückwand mit Aufzugtür (Felswand)
        rg = rnd(3)
        for k in range(14):
            x = -16 + k * 2.5 + rg.uniform(-0.6, 0.6)
            if abs(x) < 2.2:
                continue
            rock(f'wall{k}', (x, -1.2 + rg.uniform(-0.5, 0.5), rg.uniform(0, 6)), rg.uniform(2.2, 3.5), rm2, k, co)
        # Torbogen aus Messing + Fels darüber
        arch = empty('arch', (0, -0.3, 0), coll=co)
        for s in (-1, 1):
            prim('cube', 'archpost', (s * 1.1, 0, 1.4), scale=(0.18, 0.3, 1.4), mat=M.brass, bevel=0.04, parent=arch, coll=co)
        prim('cube', 'archtop', (0, 0, 2.9), scale=(1.3, 0.32, 0.18), mat=M.brass, bevel=0.04, parent=arch, coll=co)
        rock('archrock', (0, -1.5, 4.8), 3.2, rm2, 99, co)
        rock('archrock2', (-2.4, -1.0, 2.5), 1.6, rm2, 98, co)
        rock('archrock3', (2.5, -1.2, 2.2), 1.5, rm2, 97, co)
        t_ = text_obj('archnum', '-201', 0.28, emission('archnumm', (1.0, 0.3, 0.12), 10), extrude=0.02, coll=co)
        t_.location = (0, -0.65, 2.9); t_.rotation_euler = (R(90), 0, R(180))
        t_.location = (0, 0.0, 2.9); t_.rotation_euler = (R(90), 0, 0)
        t_.location.y = 0.33
        t_.rotation_euler = (R(90), 0, R(180))
        # Aufzugtüren (offen) + warmes Licht aus Kabine
        self.ldoors = []
        dmat = principled('ldoor', hexc('#B8863A'), 0.28, 1.0)
        for s in (-1, 1):
            d = prim('cube', 'liftdoor', (s * 1.35, -0.35, 1.3), scale=(0.27, 0.05, 1.25), mat=dmat, bevel=0.01, coll=co)
            self.ldoors.append((d, s))
        self.cabin_glow = emission('cabinglow', (1.0, 0.7, 0.4), 3.0)
        prim('cube', 'cabin', (0, -1.6, 1.3), scale=(1.0, 0.05, 1.3), mat=self.cabin_glow, coll=co)
        self.cabin_light = add_light('AREA', 'cabinl', (0, -0.8, 1.6), 120, (1.0, 0.7, 0.4), 1.0, rot=(R(-90), 0, 0), coll=co)
        # Riesenmuschel
        self.clam_c = Vector((0, 17, 0))
        shout = color_ramp_mat('clamout', [(0.0, hexc('#5E2A3A')), (0.5, hexc('#9C4A5A')), (1.0, hexc('#E0A090'))], coord='Z',
                               lo=0, hi=6, rough=0.5, coat=0.3, film=200, bump=(4, 0.3, 6))
        nac = principled('clamnacre', hexc('#E8E4F0'), rough=0.12, coat=1.0, film=450, film_ior=1.6, bump=(2, 0.1, 3, 'wave'))
        low = scallop('clamlow', radius=6.0, spread=78, ribs=15, depth=1.8, rib_amp=0.18, mat=shout, edge_wave=0.03, coll=co)
        low.data.materials.append(nac)
        low.modifiers['sol'].thickness = 0.25
        low.location = self.clam_c + Vector((0, 3.0, 0.3)); low.rotation_euler = (R(-90 + 12), 0, R(180))
        up = scallop('clamup', radius=6.0, spread=78, ribs=15, depth=1.8, rib_amp=0.18, mat=shout, edge_wave=0.03, coll=co)
        up.data.materials.append(nac)
        up.modifiers['sol'].thickness = 0.25
        up.location = self.clam_c + Vector((0, 3.0, 0.6)); up.rotation_euler = (R(-90 + 12 + 70 + 30), 0, R(180))
        self.clam_up = up
        # Perle
        self.pearl_r = 2.0
        self.pearl_mat = pearl_material()
        self.pearl = prim('sphere', 'pearl', tuple(self.clam_c + Vector((0, 0.4, 2.3))), scale=(self.pearl_r,) * 3, mat=self.pearl_mat, seg=64, coll=co, bake=False)
        self.pearl_lights = [add_light('POINT', 'pearll1', tuple(self.clam_c + Vector((0, -2.6, 2.5))), 900, (0.75, 0.9, 1.0), 1.2, coll=co),
                             add_light('POINT', 'pearll2', tuple(self.clam_c + Vector((0, 0.4, 5.0))), 600, (0.9, 0.8, 1.0), 1.0, coll=co)]
        for l in self.pearl_lights:
            l.visible_glossy = False
        # Auge (startet geschlossen)
        self.eye_mat = iris_material()
        piv = empty('eyepiv', tuple(self.pearl.location), coll=co)
        self.eye = prim('sphere', 'bigeye', (0, -self.pearl_r * 0.9, 0.0), scale=(0.9, 0.35, 0.75), mat=self.eye_mat, parent=piv, seg=48, coll=co, bake=False)
        self.eye_piv = piv
        # Felsen, Säulen, Korallen, Anemonen, Kelp
        for k in range(18):
            a = rg.uniform(0, 6.28); d = rg.uniform(9, 22)
            p = (math.cos(a) * d, 17 + math.sin(a) * d, -0.2)
            if p[1] < 2: continue
            rock(f'r{k}', p, rg.uniform(0.6, 2.6), rm if k % 2 else rm2, 200 + k, co, squash=0.6)
        col = principled('marble', hexc('#B9B2A0'), rough=0.6, bump=(10, 0.4, 6))
        for k, (x, y, h, tilt) in enumerate([(-7, 9, 6, 0), (7, 10, 4.5, 8), (-9, 21, 7, -5), (9, 23, 3, 0), (-4.5, 27, 5, 12), (5, 28, 8, 0)]):
            p = empty('col', (x, y, 0), (R(tilt), 0, 0), coll=co)
            prim('cyl', 'colshaft', (0, 0, h / 2), scale=(0.55, 0.55, h / 2), mat=col, seg=24, parent=p, coll=co)
            for f in range(12):
                a = 2 * math.pi * f / 12
                prim('cube', 'flute', (math.cos(a) * 0.55, math.sin(a) * 0.55, h / 2), rot=(0, 0, a), scale=(0.05, 0.06, h / 2 * 0.98), mat=col, parent=p, coll=co)
            prim('cube', 'colbase', (0, 0, 0.15), scale=(0.8, 0.8, 0.15), mat=col, bevel=0.03, parent=p, coll=co)
            if k % 2 == 0:
                prim('cube', 'colcap', (0, 0, h + 0.15), scale=(0.8, 0.8, 0.15), mat=col, bevel=0.03, parent=p, coll=co)
            # Algenbewuchs
            for j in range(6):
                prim('sphere', 'colmoss', (rg.uniform(-0.5, 0.5), rg.uniform(-0.5, 0.5), rg.uniform(0, h)), scale=(0.25, 0.25, 0.15), mat=M.kelp, parent=p, coll=co)
        # Korallenfächer
        fanm = principled('fan', hexc('#D94F5C'), rough=0.6, sss=0.4, sss_r=(1, 0.3, 0.3))
        for k in range(10):
            a = rg.uniform(0, 6.28); d = rg.uniform(6, 14)
            f = scallop(f'fan{k}', radius=rg.uniform(0.8, 1.6), spread=60, ribs=24, depth=0.05, rib_amp=0.02, mat=fanm, coll=co)
            f.location = (math.cos(a) * d, 17 + math.sin(a) * d, 0)
            f.rotation_euler = (0, 0, rg.uniform(0, 6.28))
        # Anemonen mit leuchtenden Spitzen
        self.anem = []
        anm = principled('anem', hexc('#E07AA0'), rough=0.5, sss=0.5, sss_r=(1, 0.4, 0.6))
        tipm = emission('aneTip', (0.4, 1.0, 0.9), 1.5)
        for k in range(14):
            a = rg.uniform(0, 6.28); d = rg.uniform(4.5, 12)
            c = Vector((math.cos(a) * d, 17 + math.sin(a) * d, 0))
            if c.y < 4: continue
            for j in range(16):
                b = 2 * math.pi * j / 16
                pts = [tuple(c + Vector((math.cos(b) * 0.1, math.sin(b) * 0.1, 0))),
                       tuple(c + Vector((math.cos(b) * 0.3, math.sin(b) * 0.3, 0.4))),
                       tuple(c + Vector((math.cos(b) * 0.45, math.sin(b) * 0.45, 0.6)))]
                tube('anet', pts, 0.03, 6, anm, co)
                prim('sphere', 'anetip', pts[-1], scale=(0.045,) * 3, mat=tipm, seg=8, coll=co)
        # Kelp-Wald hinten
        self.kelp = []
        for k in range(26):
            a = rg.uniform(R(20), R(160)); d = rg.uniform(14, 26)
            self.kelp.append(((math.cos(a) * d, 17 + math.sin(a) * d, -0.2), rg.uniform(6, 14), rg.uniform(0, 6)))
        self.kelp_obs = []
        # Leuchtpartikel / Bio-Lumineszenz
        bio = emission('bio', (0.3, 1.0, 0.85), 12.0)
        for k in range(90):
            prim('sphere', 'bio', (rg.uniform(-14, 14), rg.uniform(2, 30), rg.uniform(0.2, 9)), scale=(rg.uniform(0.02, 0.05),) * 3, mat=bio, seg=6, coll=co)
        # Lichtschächte von oben
        for k, (x, y) in enumerate([(-3, 14), (2.5, 19), (0, 17), (-6, 22), (6, 12)]):
            godray(f'ray{k}', (x * 1.6, y + 3, 40), (x, y, -0.3), 3.5 + k * 0.3, 1.2 + k * 0.2, (0.55, 0.85, 1.0), 0.25 if k != 2 else 0.45, co)
        add_light('SUN', 'csun', (0, 0, 0), 0.35, (0.4, 0.75, 1.0), 0.1, rot=(R(8), R(-6), 0), coll=co)
        add_light('AREA', 'crim', (0, 34, 8), 3000, (0.3, 0.7, 1.0), 10, rot=(R(-70), 0, R(180)), coll=co)
        # Fischschwärme
        self.school = School(co, 40, (0, 20, 7), 9, 0.3, seed=31, mat=fish_mat('fishc', '#7FA6C0', '#E8F2F8'), speed=0.6)
        self.jellies = []
        self.t = t

    def update(self, t, breathe=1.0, eye_open=0.0, pupil=1.0, glow=2.0):
        for o in self.kelp_obs:
            bpy.data.objects.remove(o)
        self.kelp_obs = []
        for k, (b, h, ph) in enumerate(self.kelp):
            from sets import kelp_strand
            self.kelp_obs.append(kelp_strand(f'kelp{k}', self.M, b, h, ph, self.coll, t))
        self.school.update(t)
        s = self.pearl_r * (1 + 0.025 * breathe * math.sin(t * 2.2))
        self.pearl.scale = (s,) * 3
        set_emit(self.pearl_mat, 0.32 * glow * (1 + 0.45 * breathe * (0.5 + 0.5 * math.sin(t * 2.2))))
        for l, e in zip(self.pearl_lights, (320, 220)):
            l.data.energy = e * (glow / 2.0) * (1 + 0.35 * breathe * (0.5 + 0.5 * math.sin(t * 2.2)))
        self.eye.scale = (0.9, 0.35, max(0.002, 0.75 * eye_open))
        self.eye.location = (0, -self.pearl_r * 0.92 * s / self.pearl_r, 0)
        self.eye.hide_render = eye_open <= 0.001
        self.eye_mat.node_tree.nodes[self.eye_mat['pupil']].inputs[1].default_value = -0.16 * pupil
        self.eye_mat.node_tree.nodes[self.eye_mat['pupil']].inputs[2].default_value = 0.16 * pupil
