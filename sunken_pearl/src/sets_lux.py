"""Luxus-Sets: Apartment Etage -147 mit Riff-Panorama, Kristallleuchter, Umschlag/Karte, Perlmutt-Saal."""
import bpy, bmesh, math, os
from mathutils import Vector
from lib import *
from sets import fog_all, fish_mat, School, jelly, kelp_strand, Mats
from sets_ext import godray, rock_mat, rock, sand_mat, pearl_material
from sets_interior import cut
from shelly import scallop

R = math.radians
FONT_DIR = '/usr/share/fonts/truetype/freefont/'


def font(name):
    p = FONT_DIR + name
    if os.path.exists(p):
        return D.fonts.load(p, check_existing=True)
    return None


# ------------------------------------------------------------------ Materialien
def marble_mat(name='marble', base='#F4F0EA', vein='#8F857E', gold=False, rough=0.07, scale=0.6):
    mat = principled(name, hexc(base), rough=rough, coat=0.5)
    nt = mat.node_tree; b = nt.nodes[mat['bsdf']]
    tc = nt.nodes.new('ShaderNodeTexCoord')
    nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 2.0; nz.inputs['Detail'].default_value = 8
    nt.links.new(tc.outputs['Object'], nz.inputs['Vector'])
    mp = nt.nodes.new('ShaderNodeVectorMath'); mp.operation = 'ADD'
    sc = nt.nodes.new('ShaderNodeVectorMath'); sc.operation = 'SCALE'; sc.inputs['Scale'].default_value = 1.3
    nt.links.new(nz.outputs['Color'], sc.inputs[0])
    nt.links.new(tc.outputs['Object'], mp.inputs[0]); nt.links.new(sc.outputs[0], mp.inputs[1])
    wv = nt.nodes.new('ShaderNodeTexWave'); wv.inputs['Scale'].default_value = scale; wv.inputs['Distortion'].default_value = 9
    wv.inputs['Detail'].default_value = 6; wv.inputs['Detail Roughness'].default_value = 0.7
    wv.bands_direction = 'DIAGONAL'
    nt.links.new(mp.outputs[0], wv.inputs['Vector'])
    cr = nt.nodes.new('ShaderNodeValToRGB'); el = cr.color_ramp.elements
    vc = hexc('#C9A24A') if gold else hexc(vein)
    el[0].position = 0.0; el[0].color = (*vc, 1)
    el[1].position = 0.08; el[1].color = (*hexc(base), 1)
    e = el.new(0.03); e.color = (*[0.5 * a + 0.5 * c for a, c in zip(vc, hexc(base))], 1)
    nt.links.new(wv.outputs['Fac'], cr.inputs[0])
    # leichte Wolkigkeit
    nz2 = nt.nodes.new('ShaderNodeTexNoise'); nz2.inputs['Scale'].default_value = 0.8
    nt.links.new(tc.outputs['Object'], nz2.inputs['Vector'])
    mx = nt.nodes.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'; mx.inputs['Factor'].default_value = 0.12
    nt.links.new(cr.outputs[0], mx.inputs['A']); nt.links.new(nz2.outputs['Color'], mx.inputs['B'])
    nt.links.new(mx.outputs['Result'], b.inputs['Base Color'])
    if gold:
        mt = nt.nodes.new('ShaderNodeMath'); mt.operation = 'LESS_THAN'; mt.inputs[1].default_value = 0.02
        nt.links.new(wv.outputs['Fac'], mt.inputs[0])
        nt.links.new(mt.outputs[0], b.inputs['Metallic'])
    return mat


def velvet(name, c):
    return principled(name, hexc(c), rough=0.75, sheen=1.0, coat=0.0, bump=(240, 0.06))


def crystal_mat(name='crystal'):
    m = principled(name, (1, 1, 1), rough=0.0, trans=1.0, ior=1.65, film=180, film_ior=1.3)
    b = m.node_tree.nodes[m['bsdf']]
    if 'Dispersion' in b.inputs:
        b.inputs['Dispersion'].default_value = 0.6
    return m


def gold_mat(name='gold', c='#E9B84C', rough=0.16):
    return principled(name, hexc(c), rough=rough, metal=1.0, bump=(90, 0.02))


def nacre_mat(name='hallnacre', base='#F6E9EE', film=520, rough=0.1, tile=None):
    m = principled(name, hexc(base), rough=rough, coat=1.0, film=film, film_ior=1.7, sss=0.05,
                   bump=(3, 0.15, 4, 'wave'))
    return m


# ------------------------------------------------------------------ Kristallleuchter
class Chandelier:
    def __init__(self, loc, size=1.0, coll=None, n_drop=1.0):
        co = self.coll = coll
        self.root = empty('chand', loc, coll=co)
        g = gold_mat('chgold')
        cr = crystal_mat('chcrys')
        self.bulb = emission('chbulb', (1.0, 0.82, 0.58), 22.0)
        s = size
        # Mittelstab
        tube('ch_rod', [(0, 0, 0), (0, 0, -0.5 * s)], 0.02 * s, 12, g, co).parent = self.root
        lathe('ch_hub', [(0, -0.45 * s), (0.08 * s, -0.5 * s), (0.12 * s, -0.62 * s), (0.06 * s, -0.75 * s), (0, -0.78 * s)], 32, g, co).parent = self.root
        rg = rnd(4)
        tiers = [(0.95, -0.95, 18), (0.68, -1.25, 14), (0.4, -1.5, 10)]
        self.drops = []
        for ti, (r, z, nb) in enumerate(tiers):
            r *= s; z *= s
            prim('torus', f'ch_ring{ti}', (0, 0, z), mat=g, R=r, r=0.018 * s, seg=96, parent=self.root, coll=co)
            # Arme + Kerzen
            for k in range(nb if ti == 0 else 0):
                a = 2 * math.pi * k / nb
                x, y = math.cos(a) * r, math.sin(a) * r
                tube('ch_arm', [(0, 0, -0.7 * s), (x * 0.5, y * 0.5, -0.85 * s), (x, y, z - 0.05 * s), (x, y, z + 0.05 * s)], 0.012 * s, 8, g, co).parent = self.root
                cup = lathe('ch_cup', [(0, 0), (0.04 * s, 0.0), (0.05 * s, 0.03 * s), (0.03 * s, 0.035 * s)], 16, g, co)
                cup.parent = self.root; cup.location = (x, y, z + 0.05 * s)
                c = prim('cyl', 'ch_candle', (x, y, z + 0.12 * s), scale=(0.018 * s, 0.018 * s, 0.07 * s), mat=principled('chwax', hexc('#FFF6E8'), 0.4, sss=0.4), parent=self.root, coll=co)
                prim('sphere', 'ch_flame', (x, y, z + 0.215 * s), scale=(0.02 * s, 0.02 * s, 0.035 * s), mat=self.bulb, parent=self.root, coll=co)
            # Kristall-Girlanden (Bögen) zwischen Punkten
            nsw = nb
            for k in range(nsw):
                a0 = 2 * math.pi * k / nsw; a1 = 2 * math.pi * (k + 1) / nsw
                for j in range(1, 7):
                    u = j / 7
                    a = a0 + (a1 - a0) * u
                    sag = 0.12 * s * math.sin(math.pi * u)
                    p = (math.cos(a) * r, math.sin(a) * r, z - sag)
                    d = prim('sphere', 'ch_bead', p, scale=(0.016 * s,) * 3, mat=cr, seg=8, parent=self.root, coll=co)
                # hängender Prisma-Tropfen
                a = a0
                for j in range(3):
                    p = (math.cos(a) * r, math.sin(a) * r, z - 0.06 * s - j * 0.055 * s)
                    prim('sphere', 'ch_bead2', p, scale=(0.014 * s,) * 3, mat=cr, seg=8, parent=self.root, coll=co)
                prim('sphere', 'ch_drop', (math.cos(a) * r, math.sin(a) * r, z - 0.27 * s), scale=(0.035 * s, 0.035 * s, 0.075 * s), mat=cr, seg=6,
                     parent=self.root, coll=co)
        # großer Abschluss-Tropfen
        for j in range(5):
            prim('sphere', 'ch_cb', (0, 0, -0.8 * s - j * 0.06 * s), scale=(0.02 * s,) * 3, mat=cr, seg=8, parent=self.root, coll=co)
        prim('sphere', 'ch_final', (0, 0, -1.22 * s), scale=(0.07 * s, 0.07 * s, 0.13 * s), mat=cr, seg=8, parent=self.root, coll=co)
        # Krone oben
        prim('torus', 'ch_crown', (0, 0, -0.35 * s), mat=g, R=0.3 * s, r=0.012 * s, seg=48, parent=self.root, coll=co)
        for k in range(12):
            a = 2 * math.pi * k / 12
            prim('sphere', 'ch_cr', (math.cos(a) * 0.3 * s, math.sin(a) * 0.3 * s, -0.33 * s), scale=(0.018 * s,) * 3, mat=cr, seg=8, parent=self.root, coll=co)
        self.light = add_light('POINT', 'chlight', tuple(Vector(loc) + Vector((0, 0, -1.0 * s))), 120, (1.0, 0.78, 0.52), 0.6, coll=co)


# ------------------------------------------------------------------ Riff draußen
def reef(coll, y0=6.0, z0=-0.6, width=30, depth=26, seed=3, density=1.0):
    """Leuchtendes Korallenriff ab y0 (Blickrichtung +Y). Gibt (school_list, mats) zurück."""
    co = coll
    rg = rnd(seed)
    mats = []
    sand = sand_mat(); mats.append('sand')
    sand.node_tree.nodes[sand['bsdf']].inputs['Base Color'].default_value = (*hexc('#C9B79A'), 1)
    g = prim('plane', 'reefground', (0, y0 + depth / 2, z0 - 1.5), scale=(width, depth, 1), mat=sand, coll=co)
    sub = g.modifiers.new('sub', 'SUBSURF'); sub.subdivision_type = 'SIMPLE'; sub.levels = 5; sub.render_levels = 5
    tx = D.textures.new('reefd', 'CLOUDS'); tx.noise_scale = 4
    dm = g.modifiers.new('disp', 'DISPLACE'); dm.texture = tx; dm.strength = 1.6; dm.texture_coords = 'GLOBAL'
    # Hintergrund-Wasser: Verlauf
    bg = color_ramp_mat('reefbg', [(0.0, (0.0, 0.05, 0.12)), (0.5, (0.02, 0.3, 0.45)), (1.0, (0.25, 0.75, 0.85))], coord='Z', lo=-12, hi=18)
    bgn = bg.node_tree.nodes[bg['bsdf']]
    bgn.inputs['Emission Strength'].default_value = 1.0
    bg.node_tree.links.new(bgn.inputs['Base Color'].links[0].from_socket, bgn.inputs['Emission Color'])
    bgn.inputs['Base Color'].default_value = (0, 0, 0, 1)
    bg['nofog'] = 1
    prim('plane', 'reefbgp', (0, y0 + depth + 4, 2), rot=(R(90), 0, 0), scale=(width * 2.2, 22, 1), mat=bg, coll=co)
    rm = rock_mat('reefrock', '#6E5A66', '#9A7E7A'); mats.append('reefrock')
    # Korallen-Paletten
    cols = ['#FF6F91', '#FF9671', '#FFC75F', '#C34A9C', '#F9F871', '#7FE0C8', '#FF5E78', '#B98CF0']
    cmats = [principled(f'coral{i}', hexc(c), rough=0.55, sss=0.5, sss_r=(1, 0.5, 0.5), bump=(40, 0.4)) for i, c in enumerate(cols)]
    glow = [emission(f'coralglow{i}', hexc(c), 3.0) for i, c in enumerate(['#7FFFE8', '#FF8FD0', '#FFE38A', '#8FB4FF'])]
    mats += [m.name for m in cmats] + [m.name for m in glow]
    n = int(60 * density)
    for k in range(n):
        x = rg.uniform(-width * 0.8, width * 0.8); y = y0 + rg.uniform(0.5, depth)
        z = z0 - 1.2
        kind = rg.random()
        m = rg.choice(cmats)
        if kind < 0.3:
            rock(f'rr{k}', (x, y, z - 0.3), rg.uniform(0.6, 1.8), rm, 400 + k, co, squash=0.55)
        elif kind < 0.55:  # Fächerkoralle
            f = scallop(f'rfan{k}', radius=rg.uniform(0.7, 1.7), spread=62, ribs=26, depth=0.04, rib_amp=0.02, mat=m, coll=co)
            f.location = (x, y, z); f.rotation_euler = (0, 0, rg.uniform(-0.6, 0.6))
        elif kind < 0.75:  # Geweihkoralle
            def branch(p, d, L, depth_):
                q = p + d * L
                tube('rbr', [tuple(p), tuple(p + d * L * 0.5 + Vector((0, 0, L * 0.1))), tuple(q)], 0.06 * L, 6, m, co, radii=[0.07 * L, 0.06 * L, 0.04 * L])
                if depth_ > 0:
                    for s_ in (-1, 1):
                        nd = (d + Vector((rg.uniform(-0.6, 0.6), rg.uniform(-0.6, 0.6), 0.4 * s_ + 0.5))).normalized()
                        branch(q, nd, L * 0.7, depth_ - 1)
                else:
                    prim('sphere', 'rtip', tuple(q), scale=(0.05 * L + 0.02,) * 3, mat=rg.choice(glow), seg=8, coll=co)
            branch(Vector((x, y, z)), Vector((0, 0, 1)), rg.uniform(0.5, 0.9), 2)
        elif kind < 0.88:  # Hirnkoralle
            o = prim('sphere', f'rbrain{k}', (x, y, z), scale=(rg.uniform(0.5, 1.0),) * 2 + (0.5,), mat=principled(f'brain{k}', hexc(rg.choice(cols)), 0.6, sss=0.3, bump=(6, 1.0, 2, 'wave')), seg=24, coll=co)
        else:  # Anemone mit Leuchtspitzen
            c = Vector((x, y, z))
            gm = rg.choice(glow)
            for j in range(12):
                b = 2 * math.pi * j / 12
                pts = [tuple(c + Vector((math.cos(b) * 0.08, math.sin(b) * 0.08, 0))),
                       tuple(c + Vector((math.cos(b) * 0.25, math.sin(b) * 0.25, 0.35))),
                       tuple(c + Vector((math.cos(b) * 0.38, math.sin(b) * 0.38, 0.55)))]
                tube('ranet', pts, 0.03, 6, m, co)
                prim('sphere', 'ranetip', pts[-1], scale=(0.045,) * 3, mat=gm, seg=8, coll=co)
    # Kelp hinten
    km = principled('reefkelp', hexc('#6C9A3A'), rough=0.6, sss=0.4, sss_r=(0.4, 1, 0.2)); mats.append('reefkelp')
    for k in range(int(16 * density)):
        x = rg.uniform(-width * 0.7, width * 0.7); y = y0 + rg.uniform(depth * 0.5, depth)
        h = rg.uniform(5, 11)
        pts = [(x + 0.4 * math.sin(j * 0.6 + k), y, z0 - 1.5 + h * j / 12) for j in range(13)]
        tube('rkelp', pts, 0.07, 6, km, co)
    # Fische: bunte Schwärme
    schools = []
    for i, (c1, c2, n_, cen, rad, sz) in enumerate([('#F2C230', '#FFF3C0', 26, (-3, y0 + 4, z0 + 1.8), 3.5, 0.28),
                                                     ('#2A7BD6', '#BFE3FF', 34, (4, y0 + 7, z0 + 2.6), 4.5, 0.22),
                                                     ('#FF7A59', '#FFE1D6', 14, (0, y0 + 3, z0 + 0.8), 2.5, 0.3)]):
        fm = fish_mat(f'rfish{i}', c1, c2); mats.append(fm.name)
        schools.append(School(co, n_, cen, rad, sz, seed=40 + i, mat=fm, speed=0.7))
    # Quallen (rosa, sanft)
    for i in range(5):
        jelly(co, f'rj{i}', (rg.uniform(-8, 8), y0 + rg.uniform(4, 14), z0 + rg.uniform(2, 6)), rg.uniform(0.4, 0.8), (1.0, 0.6, 0.85), 0.0, 3.0)
        mats.append(f'rj{i}m')
    # Lichtstrahlen
    for k in range(5):
        x = -8 + k * 4
        godray(f'rray{k}', (x + 3, y0 + 10, 25), (x, y0 + 6 + k, z0 - 1.5), 2.5, 1.0, (0.6, 0.95, 1.0), 0.22, co)
        mats.append(f'rray{k}m')
    sun = add_light('SUN', 'reefsun', (0, 0, 0), 2.0, (0.55, 0.9, 1.0), 0.08, rot=(R(15), R(-8), 0), coll=co)
    # Plankton-Funkeln
    pm = emission('plankton', (0.7, 1.0, 0.95), 8.0); mats.append('plankton')
    for k in range(int(70 * density)):
        prim('sphere', 'plk', (rg.uniform(-10, 10), y0 + rg.uniform(0.5, 12), z0 + rg.uniform(-1, 5)), scale=(rg.uniform(0.012, 0.03),) * 3, mat=pm, seg=6, coll=co)
    return schools, mats


# ------------------------------------------------------------------ Apartment
class LuxApartment:
    """Penthouse Etage -147. Halbkreis-Panoramafenster (Muschelmotiv) bei y=3.5, Boden z=0,
    Raum x∈[-5,5], y∈[-4,3.5], Höhe 3.8. Tür rechts (x=+5)."""

    def __init__(self, coll=None, outside=True, reef_density=1.0):
        self.coll = co = coll
        M = self.M = {}
        M['floor'] = marble_mat('lfloor', '#F5F1EB', '#A39385', gold=True)
        M['marble2'] = marble_mat('lmarble2', '#EDE3DA', '#9C8576', rough=0.15)
        M['wall'] = principled('lwall', hexc('#E8D3C6'), rough=0.6, bump=(8, 0.05))
        M['panel'] = principled('lpanel', hexc('#EEDFD2'), rough=0.45, coat=0.2)
        M['gold'] = gold_mat('lgold')
        M['gold2'] = gold_mat('lgold2', '#D9A441', 0.3)
        M['velvet'] = velvet('lvelvet', '#1E7C83')
        M['velvet2'] = velvet('lvelvet2', '#E9A3B5')
        M['cushion'] = velvet('lcushion', '#F2C6CF')
        M['crystal'] = crystal_mat('lcrystal')
        M['glass'] = window_glass('lwinglass', (0.9, 0.97, 1.0), 0.05)
        M['ceil'] = principled('lceil', hexc('#E9DCCF'), rough=0.5)
        M['rug'] = self._rug_mat()
        M['champ'] = principled('champ', hexc('#F3D98A'), rough=0.0, trans=1.0, ior=1.34)
        M['bottle'] = principled('bottle', hexc('#1F3A22'), rough=0.05, trans=0.6, ior=1.5, coat=1.0)
        M['label'] = gold_mat('label', '#E8C46A', 0.25)
        M['silver'] = principled('silver', hexc('#D8DDE2'), rough=0.1, metal=1.0)
        M['flower'] = principled('peony', hexc('#F59AB8'), rough=0.55, sss=0.5, sss_r=(1, 0.4, 0.5), bump=(30, 0.6))
        M['flower2'] = principled('peony2', hexc('#FFF1F3'), rough=0.55, sss=0.5, bump=(30, 0.6))
        M['leaf'] = principled('leaf', hexc('#3E7B4E'), rough=0.5, sss=0.3, sss_r=(0.3, 1, 0.3))
        M['mirror'] = principled('lmirror', hexc('#E6ECEF'), rough=0.02, metal=1.0)
        M['door'] = principled('ldoor', hexc('#FBF6EF'), rough=0.35, coat=0.4)
        M['shade'] = emission('lshade', (1.0, 0.85, 0.65), 6.0)
        H = self.H = 3.8
        # Boden mit eingelegtem Goldstern
        prim('cube', 'l_floor', (0, -0.25, -0.05), scale=(5.2, 4.0, 0.05), mat=M['floor'], coll=co)
        star = []
        for k in range(16):
            a = 2 * math.pi * k / 16
            rr = 1.5 if k % 2 == 0 else 0.55
            star.append((math.cos(a) * rr, math.sin(a) * rr, 0.002))
        st = mesh_obj('l_star', star + [(0, 0, 0.002)], [(k, (k + 1) % 16, 16) for k in range(16)], M['gold'], coll=co)
        st.location = (0.6, -1.6, 0); st.data.polygons.foreach_set('use_smooth', [False] * 16)
        prim('torus', 'l_starring', (0.6, -1.6, 0.0), mat=M['gold'], R=1.7, r=0.012, seg=96, coll=co)
        # Decke mit Kassetten
        prim('cube', 'l_ceil', (0, -0.25, H + 0.05), scale=(5.2, 4.0, 0.05), mat=M['ceil'], coll=co)
        for i in range(-4, 5, 2):
            prim('cube', 'l_cbx', (i, -0.25, H - 0.06), scale=(0.05, 3.9, 0.06), mat=M['panel'], bevel=0.01, coll=co)
            prim('cube', 'l_cbxg', (i, -0.25, H - 0.125), scale=(0.055, 3.9, 0.006), mat=M['gold'], coll=co)
        for j in range(-3, 4, 2):
            prim('cube', 'l_cby', (0, j, H - 0.06), scale=(5.1, 0.05, 0.06), mat=M['panel'], bevel=0.01, coll=co)
            prim('cube', 'l_cbyg', (0, j, H - 0.125), scale=(5.1, 0.055, 0.006), mat=M['gold'], coll=co)
        # Fensterwand: Halbkreis-Fenster mit Muschelrippen
        ww = prim('cube', 'l_winwall', (0, 3.75, H / 2), scale=(5.2, 0.25, H / 2 + 0.1), mat=M['wall'], coll=co)
        self.win_r = WR = 3.35
        self.win_c = Vector((0, 3.5, 0.12))
        cutter = prim('cyl', 'l_wincut', (0, 3.75, 0.12), rot=(R(90), 0, 0), scale=(WR, WR, 0.6), seg=128, coll=co)
        cut(ww, cutter)
        # Rahmen + Rippen
        rim = []
        for k in range(97):
            a = math.pi * k / 96
            rim.append((math.cos(a) * WR, 3.52, 0.12 + math.sin(a) * WR))
        tube('l_winrim', rim, 0.09, 16, M['gold'], co)
        tube('l_winrim2', [(x * 0.965, 3.56, 0.12 + (z - 0.12) * 0.965) for x, _, z in rim], 0.03, 10, M['gold2'], co)
        for k in range(1, 9):
            a = math.pi * k / 9
            tube('l_rib', [(math.cos(a) * 0.5, 3.6, 0.12 + math.sin(a) * 0.5), (math.cos(a) * WR, 3.6, 0.12 + math.sin(a) * WR)], 0.035, 10, M['gold'], co)
        for rr in (0.5, 1.6):
            arc = [(math.cos(math.pi * k / 48) * rr, 3.6, 0.12 + math.sin(math.pi * k / 48) * rr) for k in range(49)]
            tube('l_arc', arc, 0.035 if rr < 1 else 0.025, 10, M['gold'], co)
        # Fächer-Zentrum (Muschel)
        hub = scallop('l_hub', radius=0.5, spread=88, ribs=9, depth=0.06, rib_amp=0.01, mat=M['gold'], coll=co)
        hub.location = (0, 3.62, 0.12); hub.rotation_euler = (R(-90), 0, R(180))
        hub.rotation_euler = (R(90), 0, 0)
        self.glass = prim('cube', 'l_glass', (0, 3.65, 1.8), scale=(WR, 0.01, 1.8), mat=M['glass'], coll=co)
        # Fensterbank aus Marmor mit Kissen (Sitzbank)
        prim('cube', 'l_bench', (0, 3.25, 0.22), scale=(3.0, 0.3, 0.22), mat=M['marble2'], bevel=0.02, coll=co)
        # Wände
        prim('cube', 'l_wallL', (-5.15, -0.25, H / 2), scale=(0.15, 4.0, H / 2), mat=M['wall'], coll=co)
        prim('cube', 'l_wallR', (5.15, -0.25, H / 2), scale=(0.15, 4.0, H / 2), mat=M['wall'], coll=co)
        prim('cube', 'l_wallB', (0, -4.15, H / 2), scale=(5.2, 0.15, H / 2), mat=M['wall'], coll=co)
        # Paneele mit Goldleisten
        for side, (cx, cy, rot, L) in {'L': (-4.99, -0.25, R(90), 8.0), 'R': (4.99, -0.25, R(-90), 8.0), 'B': (0, -3.99, 0, 10.4)}.items():
            n = 4 if side != 'B' else 5
            for i in range(n):
                u = (i + 0.5) / n - 0.5
                w = L / n * 0.38
                for zc, hh in ((0.55, 0.32), (2.15, 1.05)):
                    p = empty('l_pnl', (cx, cy, 0), (0, 0, rot), coll=co)
                    off = u * L
                    fr = [(off - w, 0, zc - hh), (off + w, 0, zc - hh), (off + w, 0, zc + hh), (off - w, 0, zc + hh), (off - w, 0, zc - hh)]
                    tube('l_frm', fr, 0.012, 6, M['gold'], co).parent = p
        # Sockel + Kranzgesims
        for nm, loc, sc in [('bL', (-4.98, -0.25, 0.08), (0.03, 4.0, 0.08)), ('bR', (4.98, -0.25, 0.08), (0.03, 4.0, 0.08)), ('bB', (0, -3.98, 0.08), (5.2, 0.03, 0.08))]:
            prim('cube', 'l_' + nm, loc, scale=sc, mat=M['panel'], bevel=0.01, coll=co)
            prim('cube', 'l_' + nm + 'c', (loc[0], loc[1], H - 0.1), scale=(sc[0] + 0.04, sc[1] + 0.04 if sc[1] > 1 else sc[1] + 0.04, 0.1), mat=M['panel'], bevel=0.03, coll=co)
            prim('cube', 'l_' + nm + 'g', (loc[0], loc[1], H - 0.21), scale=(sc[0] + 0.045, sc[1] + 0.045 if sc[1] > 1 else sc[1] + 0.045, 0.01), mat=M['gold'], coll=co)
        # kannelierte Marmorsäulen neben dem Fenster
        for s in (-1, 1):
            self._column((s * 4.2, 3.2, 0), H)
        # Kristallleuchter
        self.chand = Chandelier((0.3, -0.4, H), 1.0, co)
        # Muschel-Sofa
        self.chair = self._sofa((-1.35, 0.9, 0), R(150))
        # Beistelltisch mit Champagner
        self._side_table((-0.15, 1.95, 0))
        # Goldene Muschel-Skulptur auf Podest
        self._sculpture((3.6, 1.8, 0))
        # Spiegel an der linken Wand
        self._mirror((-4.95, -1.6, 0))
        # Blumen
        self._vase((-3.9, 2.6, 0), 1.0)
        self._vase((2.5, -3.5, 0), 0.8)
        # Stehlampen
        for p in [(-4.3, -3.3), (4.3, -3.3)]:
            self._floor_lamp((p[0], p[1], 0))
        # Teppich
        rug = lathe('l_rug', [(0, 0.012), (1.8, 0.012), (1.82, 0.0)], 96, M['rug'], co, False, True)
        rug.location = (-0.9, 1.0, 0.0); rug.scale = (1.0, 0.8, 1)
        # Tür rechts
        self._door((5.0, -1.8, 0))
        # Licht
        self.win_light = add_light('AREA', 'l_winl', (0, 3.2, 1.8), 110, (0.5, 0.9, 1.0), 4.0, rot=(R(90), 0, 0), coll=co)
        look_at(self.win_light, (0, -2, 0.8))
        self.fill = add_light('AREA', 'l_fill', (2.5, -3.0, 3.2), 35, (1.0, 0.85, 0.7), 3.0, coll=co)
        look_at(self.fill, (-1, 1.5, 0.8))
        self.out_mats = []
        self.schools = []
        if outside:
            self.schools, self.out_mats = reef(co, 4.2, 1.0, 20, 22, 3, reef_density)

    # ------------------------------------------------------------------
    def _rug_mat(self):
        mat = principled('lrug', hexc('#F4EADF'), rough=0.95, sheen=0.8, bump=(260, 0.3))
        nt = mat.node_tree; b = nt.nodes[mat['bsdf']]
        tc = nt.nodes.new('ShaderNodeTexCoord')
        ln = nt.nodes.new('ShaderNodeVectorMath'); ln.operation = 'LENGTH'
        nt.links.new(tc.outputs['Object'], ln.inputs[0])
        cr = nt.nodes.new('ShaderNodeValToRGB'); el = cr.color_ramp.elements; cr.color_ramp.interpolation = 'CONSTANT'
        el[0].position = 0.0; el[0].color = (*hexc('#F4EADF'), 1)
        el[1].position = 0.97; el[1].color = (*hexc('#F4EADF'), 1)
        for p_, c in [(0.84, '#D9A441'), (0.87, '#F4EADF'), (0.9, '#E9A3B5'), (0.94, '#D9A441')]:
            e = el.new(p_); e.color = (*hexc(c), 1)
        mr = nt.nodes.new('ShaderNodeMapRange'); mr.inputs['From Max'].default_value = 1.8
        nt.links.new(ln.outputs['Value'], mr.inputs[0]); nt.links.new(mr.outputs[0], cr.inputs[0])
        nt.links.new(cr.outputs[0], b.inputs['Base Color'])
        return mat

    def _column(self, loc, H):
        co = self.coll; M = self.M
        p = empty('l_col', loc, coll=co)
        prim('cyl', 'l_colshaft', (0, 0, H / 2), scale=(0.2, 0.2, H / 2 - 0.25), mat=M['marble2'], seg=32, parent=p, coll=co)
        for f in range(16):
            a = 2 * math.pi * f / 16
            prim('cube', 'l_flute', (math.cos(a) * 0.2, math.sin(a) * 0.2, H / 2), rot=(0, 0, a), scale=(0.02, 0.025, H / 2 - 0.3), mat=M['marble2'], parent=p, coll=co)
        for z, s_ in ((0.12, 1.0), (H - 0.12, 1.0)):
            prim('cube', 'l_colb', (0, 0, z), scale=(0.3, 0.3, 0.12), mat=M['marble2'], bevel=0.03, parent=p, coll=co)
            prim('torus', 'l_colg', (0, 0, z + (0.14 if z < 1 else -0.14)), mat=M['gold'], R=0.215, r=0.022, seg=48, parent=p, coll=co)

    def _sofa(self, loc, rot):
        co = self.coll; M = self.M
        p = empty('l_sofa', loc, (0, 0, rot), coll=co)
        back = scallop('l_sofaback', radius=1.15, spread=72, ribs=7, depth=0.28, rib_amp=0.05, mat=M['velvet'], edge_wave=0.05, coll=co)
        back.data.materials.append(M['velvet'])
        back.modifiers['sol'].thickness = 0.12
        back.parent = p; back.location = (0, 0.35, 0.38); back.rotation_euler = (R(-12), 0, 0)
        seat = prim('cyl', 'l_seat', (0, 0.05, 0.36), scale=(0.95, 0.5, 0.1), mat=M['velvet'], seg=64, bevel=0.06, parent=p, coll=co)
        prim('cyl', 'l_seatb', (0, 0.05, 0.2), scale=(0.97, 0.52, 0.08), mat=M['gold'], seg=64, bevel=0.02, parent=p, coll=co)
        for s in (-1, 1):
            for fy in (-0.3, 0.35):
                lg = lathe('l_sleg', [(0.035, 0), (0.025, 0.06), (0.04, 0.12)], 16, M['gold'], co)
                lg.parent = p; lg.location = (s * 0.7, fy, 0)
        # Kissen
        prim('cube', 'l_cush1', (0.48, 0.25, 0.62), rot=(R(-18), R(10), R(-12)), scale=(0.17, 0.07, 0.15), mat=M['cushion'], bevel=0.06, parent=p, coll=co, subsurf=2)
        prim('cube', 'l_cush2', (-0.5, 0.25, 0.6), rot=(R(-15), R(-12), R(14)), scale=(0.15, 0.06, 0.13), mat=M['velvet2'], bevel=0.06, parent=p, coll=co, subsurf=2)
        return p

    def _side_table(self, loc):
        co = self.coll; M = self.M
        x, y, _ = loc
        lathe('l_ttop', [(0, 0.6), (0.34, 0.6), (0.36, 0.62), (0.34, 0.645), (0, 0.645)], 48, M['marble2'], co).location = loc
        lathe('l_tleg', [(0.2, 0.0), (0.2, 0.02), (0.05, 0.08), (0.03, 0.3), (0.06, 0.56), (0.12, 0.6)], 32, M['gold'], co).location = loc
        top = 0.645
        # Sektkühler mit Flasche
        bx = (x - 0.1, y + 0.08, top)
        lathe('l_bucket', [(0.0, 0.0), (0.09, 0.0), (0.12, 0.2), (0.125, 0.21), (0.0, 0.21)], 32, M['silver'], co, True, False).location = bx
        bt = lathe('l_bottle', [(0, 0.05), (0.06, 0.05), (0.062, 0.25), (0.05, 0.31), (0.02, 0.36), (0.018, 0.42), (0.0, 0.42)], 24, M['bottle'], co)
        bt.location = bx; bt.rotation_euler = (R(-12), R(8), 0)
        foil = lathe('l_foil', [(0.021, 0.36), (0.02, 0.43), (0.0, 0.43)], 16, M['label'], co); foil.location = bx; foil.rotation_euler = bt.rotation_euler
        # Eiswürfel
        rg = rnd(5)
        for k in range(10):
            a = 2 * math.pi * k / 10
            prim('cube', 'l_ice', (bx[0] + math.cos(a) * 0.085, bx[1] + math.sin(a) * 0.085, top + 0.2), rot=(rg.uniform(0, 1), rg.uniform(0, 1), 0),
                 scale=(0.022,) * 3, mat=M['crystal'], bevel=0.006, coll=co)
        # Sektglas
        for k, (dx, dy) in enumerate(((0.14, -0.12),)):
            self._flute((x + dx, y + dy, top), co)
        # Perlen-Schale
        lathe('l_dish', [(0, 0), (0.06, 0.0), (0.09, 0.025), (0.085, 0.027), (0.0, 0.01)], 24, M['gold'], co).location = (x + 0.15, y + 0.15, top)

    def _flute(self, loc, co, parent=None):
        M = self.M
        g = lathe('l_flute', [(0.0, 0.0), (0.035, 0.0), (0.035, 0.004), (0.004, 0.01), (0.004, 0.1), (0.012, 0.11), (0.025, 0.16), (0.027, 0.24), (0.025, 0.24),
                               (0.022, 0.16), (0.0, 0.115)], 24, M['crystal'], co, False, False)
        g.location = loc
        ch = lathe('l_champ', [(0.0, 0.118), (0.02, 0.15), (0.023, 0.2), (0.0, 0.2)], 24, M['champ'], co)
        ch.location = loc
        if parent:
            g.parent = parent; ch.parent = parent
        return g, ch

    def _sculpture(self, loc):
        co = self.coll; M = self.M
        x, y, _ = loc
        prim('cyl', 'l_ped', (x, y, 0.5), scale=(0.28, 0.28, 0.5), mat=M['marble2'], seg=48, bevel=0.02, coll=co)
        prim('cyl', 'l_pedtop', (x, y, 1.02), scale=(0.33, 0.33, 0.03), mat=M['gold'], seg=48, bevel=0.01, coll=co)
        sh = scallop('l_goldshell', radius=0.5, spread=78, ribs=13, depth=0.12, rib_amp=0.025, mat=M['gold'], coll=co)
        sh.data.materials.append(M['gold2'])
        sh.location = (x, y, 1.08); sh.rotation_euler = (R(-8), 0, R(200))
        pe = prim('sphere', 'l_goldpearl', (x, y - 0.12, 1.15), scale=(0.07,) * 3, mat=principled('lpearl', hexc('#FBF4EE'), 0.06, coat=1.0, film=520, film_ior=1.5), coll=co)
        sp = add_light('SPOT', 'l_sculspot', (x - 0.5, y - 1.2, 3.6), 80, (1.0, 0.85, 0.6), 0.1, spot=R(25), coll=co)
        look_at(sp, (x, y, 1.2))

    def _mirror(self, loc):
        co = self.coll; M = self.M
        p = empty('l_mirr', loc, (0, 0, R(-90)), coll=co)
        # ovaler Spiegel mit Goldrahmen + Muschelkrone
        prim('sphere', 'l_mglass', (0, 0.03, 1.55), scale=(0.62, 0.02, 1.0), mat=M['mirror'], seg=64, parent=p, coll=co)
        ring = [(0.66 * math.cos(2 * math.pi * k / 64), 0, 1.55 + 1.05 * math.sin(2 * math.pi * k / 64)) for k in range(65)]
        tube('l_mframe', ring, 0.05, 12, M['gold'], co).parent = p
        cr = scallop('l_mcrown', radius=0.32, spread=80, ribs=9, depth=0.05, rib_amp=0.015, mat=M['gold'], coll=co)
        cr.parent = p; cr.location = (0, -0.02, 2.5); cr.rotation_euler = (R(90), 0, R(180))
        cr.rotation_euler = (R(-90), R(180), 0)
        self.mirror = p

    def _vase(self, loc, s):
        co = self.coll; M = self.M
        x, y, _ = loc
        lathe('l_vase', [(0, 0), (0.12 * s, 0), (0.2 * s, 0.25 * s), (0.17 * s, 0.6 * s), (0.1 * s, 0.75 * s), (0.13 * s, 0.82 * s), (0.11 * s, 0.82 * s), (0, 0.6 * s)],
              32, M['gold'] if s > 0.9 else M['marble2'], co, False, True).location = loc
        rg = rnd(int(x * 10 + y * 7) % 97)
        for k in range(14):
            a = rg.uniform(0, 6.28); r_ = rg.uniform(0.05, 0.3) * s
            p = Vector((x + math.cos(a) * r_, y + math.sin(a) * r_, (0.95 + rg.uniform(0, 0.35)) * s))
            tube('l_stem', [(x, y, 0.7 * s), tuple(p)], 0.008, 6, M['leaf'], co)
            m = M['flower'] if k % 3 else M['flower2']
            prim('sphere', 'l_bloom', tuple(p), scale=(0.08 * s, 0.08 * s, 0.065 * s), mat=m, seg=16, coll=co, subsurf=1)
            for j in range(5):
                b = 2 * math.pi * j / 5 + rg.uniform(0, 1)
                prim('sphere', 'l_petal', tuple(p + Vector((math.cos(b) * 0.06 * s, math.sin(b) * 0.06 * s, -0.01))), rot=(rg.uniform(0, 1), rg.uniform(0, 1), b),
                     scale=(0.05 * s, 0.03 * s, 0.012 * s), mat=m, seg=10, coll=co)
            if k % 2 == 0:
                prim('sphere', 'l_leaf', tuple(p + Vector((0.05, 0.03, -0.12)) * 1.0), rot=(0.4, 0.3, a), scale=(0.09 * s, 0.03 * s, 0.006), mat=M['leaf'], seg=10, coll=co)

    def _floor_lamp(self, loc):
        co = self.coll; M = self.M
        lathe('l_flbase', [(0, 0), (0.18, 0), (0.18, 0.03), (0.03, 0.06), (0.018, 1.55)], 32, M['gold'], co).location = loc
        sh = lathe('l_flshade', [(0.26, 1.45), (0.15, 1.8)], 48, M['shade'], co, False, False)
        sh.location = loc
        sh.modifiers.new('sol', 'SOLIDIFY').thickness = 0.01
        add_light('POINT', 'l_fll', (loc[0], loc[1], 1.6), 60, (1.0, 0.75, 0.5), 0.2, coll=co)

    def _door(self, loc):
        co = self.coll; M = self.M
        p = empty('l_doorp', loc, (0, 0, R(-90)), coll=co)
        for s in (-1, 1):
            prim('cube', 'l_dleaf', (s * 0.5, -0.01, 1.3), scale=(0.49, 0.05, 1.3), mat=M['door'], bevel=0.015, parent=p, coll=co)
            for zc, hh in ((0.55, 0.35), (1.75, 0.6)):
                fr = [(s * 0.5 - 0.33, -0.055, zc - hh), (s * 0.5 + 0.33, -0.055, zc - hh), (s * 0.5 + 0.33, -0.055, zc + hh), (s * 0.5 - 0.33, -0.055, zc + hh), (s * 0.5 - 0.33, -0.055, zc - hh)]
                tube('l_dfrm', fr, 0.012, 6, M['gold'], co).parent = p
            prim('cube', 'l_dhandle', (s * 0.08, -0.09, 1.15), scale=(0.012, 0.02, 0.18), mat=M['gold'], bevel=0.008, parent=p, coll=co)
        prim('cube', 'l_dframe', (0, 0.09, 1.32), scale=(1.1, 0.07, 1.4), mat=M['panel'], bevel=0.02, parent=p, coll=co)
        # Lichtspalt unter der Tür (Flur)
        prim('cube', 'l_dgap', (0, 0.0, 0.004), scale=(0.98, 0.06, 0.004), mat=emission('l_gapm', (1.0, 0.8, 0.55), 6.0), parent=p, coll=co)
        self.door = p


# ------------------------------------------------------------------ Umschlag + Karte
def envelope(coll=None):
    """Schwarzer Umschlag mit goldenem Muschel-Siegel. Ursprung = Mitte, liegt in XY-Ebene, Vorderseite +Z."""
    co = coll
    p = empty('env', coll=co)
    em = principled('envm', hexc('#141216'), rough=0.45, sheen=0.3, bump=(120, 0.05))
    prim('cube', 'env_body', (0, 0, 0.002), scale=(0.11, 0.075, 0.002), mat=em, bevel=0.001, parent=p, coll=co)
    flap = mesh_obj('env_flap', [(-0.11, 0.075, 0.0045), (0.11, 0.075, 0.0045), (0, -0.01, 0.0045)], [(0, 2, 1)], em, coll=co)
    flap.parent = p
    gm = gold_mat('envgold', '#E3B24A', 0.22)
    # Goldkante
    tube('env_edge', [(-0.108, 0.073, 0.0048), (0, -0.008, 0.0048), (0.108, 0.073, 0.0048)], 0.0012, 6, gm, co).parent = p
    seal = prim('cyl', 'env_seal', (0, -0.006, 0.007), scale=(0.022, 0.022, 0.0035), mat=gm, seg=32, bevel=0.002, parent=p, coll=co)
    # Siegelrand gewellt
    for k in range(14):
        a = 2 * math.pi * k / 14
        prim('sphere', 'env_sealb', (math.cos(a) * 0.022, -0.006 + math.sin(a) * 0.022, 0.006), scale=(0.006, 0.006, 0.0035), mat=gm, seg=8, parent=p, coll=co)
    sh = scallop('env_shell', radius=0.016, spread=80, ribs=7, depth=0.004, rib_amp=0.001, mat=gm, coll=co)
    sh.modifiers['sol'].thickness = 0.001
    sh.parent = p; sh.location = (0, -0.013, 0.0105); sh.rotation_euler = (R(-90) + R(90), 0, 0)
    sh.rotation_euler = (R(0), 0, 0)
    sh.rotation_euler = (R(90), 0, R(180))
    sh.rotation_euler = (R(-90 + 180), 0, 0)
    sh.location = (0, -0.018, 0.0105)
    sh.rotation_euler = (R(90), R(180), R(180))
    return p


def card(coll=None):
    """Cremefarbene Karte mit Goldschrift. Ursprung = Mitte, Vorderseite +Z, Text liest entlang +X."""
    co = coll
    p = empty('card', coll=co)
    cm = principled('cardm', hexc('#F7EFE2'), rough=0.6, bump=(300, 0.04))
    prim('cube', 'card_body', (0, 0, 0.0008), scale=(0.1, 0.07, 0.0008), mat=cm, bevel=0.0006, parent=p, coll=co)
    gm = gold_mat('cardgold', '#D9A441', 0.2)
    fr = [(-0.092, -0.062, 0.0018), (0.092, -0.062, 0.0018), (0.092, 0.062, 0.0018), (-0.092, 0.062, 0.0018), (-0.092, -0.062, 0.0018)]
    tube('card_frm', fr, 0.0006, 6, gm, co).parent = p
    fr2 = [(x * 0.95, y * 0.93, z) for x, y, z in fr]
    tube('card_frm2', fr2, 0.0003, 6, gm, co).parent = p
    serif = font('FreeSerifBold.ttf') or font('FreeSerif.ttf')
    ital = font('FreeSerifItalic.ttf') or serif
    t1 = text_obj('card_t1', 'ETAGE  −201', 0.024, gm, extrude=0.0003, font=serif, coll=co)
    t1.parent = p; t1.location = (0, 0.012, 0.0018)
    t2 = text_obj('card_t2', 'Mitternacht', 0.02, gm, extrude=0.0003, font=ital, coll=co)
    t2.parent = p; t2.location = (0, -0.022, 0.0018)
    # kleine Muschel oben
    sh = scallop('card_shell', radius=0.011, spread=80, ribs=7, depth=0.002, rib_amp=0.0008, mat=gm, coll=co)
    sh.modifiers['sol'].thickness = 0.0005
    sh.parent = p; sh.location = (0, 0.036, 0.0018); sh.rotation_euler = (R(90), 0, 0)
    sh.rotation_euler = (0, 0, 0)
    # Shell liegt in XZ; für Karte (XY) um X -90 drehen
    sh.rotation_euler = (R(-90), 0, 0)
    sh.location = (0, 0.03, 0.002)
    return p, (t1, t2)


# ------------------------------------------------------------------ Perlmutt-Saal
class PearlHall:
    """Saal aus Perlmutt. Aufzugtür bei (0,0,0) Blick +Y; Perle bei (0,17,~2.3)."""

    def __init__(self, coll=None):
        co = self.coll = coll
        self.clam_c = Vector((0, 17, 0))
        nac = nacre_mat('hallnacre', '#C9B3CF', 560)
        floor = principled('hallfloor', hexc('#D8BFCB'), rough=0.06, coat=1.0, film=480, film_ior=1.6)
        # Fliesenmuster (Ringe) im Boden
        nt = floor.node_tree; b = nt.nodes[floor['bsdf']]
        tc = nt.nodes.new('ShaderNodeTexCoord')
        ln = nt.nodes.new('ShaderNodeVectorMath'); ln.operation = 'DISTANCE'; ln.inputs[1].default_value = (0, 17, 0)
        nt.links.new(tc.outputs['Generated'] if False else tc.outputs['Object'], ln.inputs[0])
        m_ = nt.nodes.new('ShaderNodeMath'); m_.operation = 'MULTIPLY'; m_.inputs[1].default_value = 0.8
        nt.links.new(ln.outputs['Value'], m_.inputs[0])
        fr = nt.nodes.new('ShaderNodeMath'); fr.operation = 'FRACT'
        nt.links.new(m_.outputs[0], fr.inputs[0])
        lt = nt.nodes.new('ShaderNodeMath'); lt.operation = 'LESS_THAN'; lt.inputs[1].default_value = 0.035
        nt.links.new(fr.outputs[0], lt.inputs[0])
        nt.links.new(lt.outputs[0], b.inputs['Metallic'])
        mx = nt.nodes.new('ShaderNodeMix'); mx.data_type = 'RGBA'
        mx.inputs['A'].default_value = (*hexc('#D8BFCB'), 1); mx.inputs['B'].default_value = (*hexc('#E2B04A'), 1)
        nt.links.new(lt.outputs[0], mx.inputs['Factor'])
        nt.links.new(mx.outputs['Result'], b.inputs['Base Color'])
        g = prim('cyl', 'hallfloor', (0, 17, -0.05), scale=(22, 22, 0.05), mat=floor, seg=128, coll=co)
        gold = gold_mat('hallgold', '#E9B84C', 0.18)
        self.gold = gold
        # Kuppel: Muschelrippen innen
        dome = lathe('halldome', [(22, 0), (21.5, 6), (19, 11), (14, 15), (8, 17.5), (0.0, 18.5)], 96, nac, co, False, False)
        dome.location = (0, 17, 0)
        dm = dome.modifiers.new('sol', 'SOLIDIFY'); dm.thickness = 0.4
        for k in range(24):
            a = 2 * math.pi * k / 24
            pts = [(math.cos(a) * r, 17 + math.sin(a) * r, z) for r, z in [(21.3, 0), (20.8, 6), (18.4, 11), (13.5, 14.6), (7.7, 17.0), (0.5, 18.0)]]
            tube('domerib', pts, 0.18, 10, gold, co)
        # Säulenring
        colm = nacre_mat('colnacre', '#F7EEF1', 420, 0.15)
        for k in range(14):
            a = 2 * math.pi * (k + 0.5) / 14
            x, y = math.cos(a) * 12, 17 + math.sin(a) * 12
            if y < 3:
                continue
            p = empty('hcol', (x, y, 0), coll=co)
            prim('cyl', 'hcolshaft', (0, 0, 4), scale=(0.55, 0.55, 3.7), mat=colm, seg=32, parent=p, coll=co)
            for f in range(14):
                b_ = 2 * math.pi * f / 14
                prim('cube', 'hflute', (math.cos(b_) * 0.55, math.sin(b_) * 0.55, 4), rot=(0, 0, b_), scale=(0.05, 0.06, 3.5), mat=colm, parent=p, coll=co)
            prim('cube', 'hcolbase', (0, 0, 0.2), scale=(0.8, 0.8, 0.2), mat=colm, bevel=0.04, parent=p, coll=co)
            prim('torus', 'hcolg', (0, 0, 0.45), mat=gold, R=0.58, r=0.06, seg=48, parent=p, coll=co)
            cap = scallop('hcap', radius=1.0, spread=80, ribs=9, depth=0.18, rib_amp=0.03, mat=gold, coll=co)
            cap.parent = p; cap.location = (0, 0, 7.4); cap.rotation_euler = (R(-100), 0, a + R(90))
            prim('sphere', 'hcolpearl', (0, 0, 7.9), scale=(0.25,) * 3, mat=pearl_material(f'hcp{k}'), seg=24, parent=p, coll=co)
        # Muschel-Thron (Riesenmuschel)
        shout = color_ramp_mat('hclamout', [(0.0, hexc('#C9688A')), (0.5, hexc('#F2A7BC')), (1.0, hexc('#FFF0E8'))], coord='Z',
                               lo=0, hi=6, rough=0.3, coat=0.6, film=300, bump=(4, 0.2, 6))
        cn = principled('hclamnacre', hexc('#F7EAF2'), rough=0.1, coat=1.0, film=500, film_ior=1.65, bump=(2, 0.08, 3, 'wave'))
        low = scallop('hclamlow', radius=6.0, spread=78, ribs=15, depth=1.8, rib_amp=0.18, mat=shout, edge_wave=0.03, coll=co)
        low.data.materials.append(cn); low.modifiers['sol'].thickness = 0.25
        low.location = self.clam_c + Vector((0, 3.0, 0.3)); low.rotation_euler = (R(-90 + 12), 0, R(180))
        up = scallop('hclamup', radius=6.0, spread=78, ribs=15, depth=1.8, rib_amp=0.18, mat=shout, edge_wave=0.03, coll=co)
        up.data.materials.append(cn); up.modifiers['sol'].thickness = 0.25
        up.location = self.clam_c + Vector((0, 3.0, 0.6)); up.rotation_euler = (R(-90 + 12 + 100), 0, R(180))
        # Podest-Stufen
        for i in range(3):
            prim('cyl', 'hstep', (0, 17, 0.1 + i * 0.2), scale=(9 - i * 1.4, 9 - i * 1.4, 0.1), mat=colm, seg=96, bevel=0.03, coll=co)
            prim('torus', 'hstepg', (0, 17, 0.2 + i * 0.2), mat=gold, R=9 - i * 1.4, r=0.035, seg=128, coll=co)
        # Perle: zwei Hälften (oben kippt beim Öffnen nach hinten)
        self.pearl_r = Rp = 2.0
        self.pc = self.clam_c + Vector((0, 0.4, 2.3 + 0.4))
        self.pearl_mat = pearl_material('hallpearl')
        self.core_mat = emission('pearlcore', (1.0, 0.85, 0.55), 0.0)
        self.pearl_root = empty('pearlroot', tuple(self.pc), coll=co)
        lo = prim('sphere', 'pearllow', (0, 0, 0), scale=(Rp,) * 3, mat=self.pearl_mat, seg=96, parent=self.pearl_root, coll=co)
        self._halve(lo, keep_top=False)
        self.hinge = empty('pearlhinge', (0, Rp * 0.98, 0), parent=self.pearl_root, coll=co)
        self.hinge.rotation_mode = 'XYZ'
        hi = prim('sphere', 'pearlhigh', (0, -Rp * 0.98, 0), scale=(Rp,) * 3, mat=self.pearl_mat, seg=96, parent=self.hinge, coll=co)
        self._halve(hi, keep_top=True)
        for o in (lo, hi):
            so = o.modifiers.new('sol', 'SOLIDIFY'); so.thickness = 0.06; so.offset = -1
            so.material_offset = 1
            o.data.materials.append(self.core_mat)
        self.core = prim('sphere', 'pearlcorein', (0, 0, 0), scale=(Rp * 0.9,) * 3, mat=self.core_mat, seg=48, parent=self.pearl_root, coll=co)
        self.seam_mat = emission('pearlseam', (1.0, 0.85, 0.5), 0.0)
        self.seam = prim('torus', 'pearlseam', (0, 0, 0), mat=self.seam_mat, R=Rp * 1.0, r=0.03, seg=128, parent=self.pearl_root, coll=co)
        self.core_light = add_light('POINT', 'pearlcorel', tuple(self.pc), 0, (1.0, 0.8, 0.5), 0.8, coll=co)
        self.pearl_lights = [add_light('POINT', 'hpearll1', tuple(self.clam_c + Vector((0, -2.8, 2.8))), 500, (1.0, 0.88, 0.95), 1.2, coll=co),
                             add_light('POINT', 'hpearll2', tuple(self.clam_c + Vector((0, 0.4, 5.6))), 300, (0.9, 0.85, 1.0), 1.0, coll=co)]
        for l in self.pearl_lights:
            l.visible_glossy = False
        # Lichtstrahlen (gold-rosa) von der Kuppel
        self.rays = []
        for k, (x, y) in enumerate([(-3, 14), (2.5, 19), (0, 17), (-6, 22), (6, 12)]):
            self.rays.append(godray(f'hray{k}', (x * 1.4, y + 2, 18), (x, y, 0), 2.6 + k * 0.3, 1.2 + k * 0.2, (1.0, 0.85, 0.75), 0.18 if k != 2 else 0.3, co))
        # schwebende Goldfunken
        sp = emission('hspark', (1.0, 0.82, 0.5), 14.0)
        self.sparks = []
        rg = rnd(8)
        for k in range(140):
            o = prim('sphere', 'hsp', (rg.uniform(-11, 11), rg.uniform(2, 30), rg.uniform(0.3, 9)), scale=(rg.uniform(0.015, 0.045),) * 3, mat=sp, seg=6, coll=co)
            self.sparks.append((o, Vector(o.location), rg.uniform(0, 6)))
        # Quallen-Lampen schweben im Saal
        for i in range(7):
            a = rg.uniform(0, 6.28); d = rg.uniform(6, 10)
            jelly(co, f'hj{i}', (math.cos(a) * d, 17 + math.sin(a) * d, rg.uniform(4, 8)), rg.uniform(0.5, 0.9), (1.0, 0.7, 0.9), 0.0, 3.5)
        # Aufzug-Portal (offen) + Etagennummer
        arch = empty('harch', (0, -0.3, 0), coll=co)
        for s in (-1, 1):
            prim('cube', 'harchpost', (s * 1.1, 0, 1.4), scale=(0.18, 0.3, 1.4), mat=gold, bevel=0.04, parent=arch, coll=co)
        prim('cube', 'harchtop', (0, 0, 2.9), scale=(1.3, 0.32, 0.18), mat=gold, bevel=0.04, parent=arch, coll=co)
        sh = scallop('harchshell', radius=0.9, spread=82, ribs=11, depth=0.15, rib_amp=0.03, mat=gold, coll=co)
        sh.parent = arch; sh.location = (0, 0, 3.05); sh.rotation_euler = (R(90), 0, 0)
        sh.rotation_euler = (R(-90), R(180), 0)
        self.cabin_glow = emission('hcabin', (1.0, 0.8, 0.6), 3.0)
        prim('cube', 'hcabin', (0, -1.6, 1.3), scale=(1.0, 0.05, 1.3), mat=self.cabin_glow, coll=co)
        wb = prim('cube', 'hwallback', (0, -0.6, 4), scale=(22, 0.2, 8), mat=nac, coll=co)
        cutter = prim('cube', 'hwallcut', (0, -0.6, 1.3), scale=(1.0, 0.5, 1.3), coll=co)
        cut(wb, cutter)
        add_light('AREA', 'hcabinl', (0, -0.9, 1.6), 150, (1.0, 0.8, 0.6), 1.0, rot=(R(-90), 0, 0), coll=co)
        add_light('AREA', 'hambient', (0, 12, 14), 700, (0.75, 0.62, 0.95), 14, coll=co)
        add_light('AREA', 'hrim', (0, 30, 6), 900, (0.55, 0.7, 1.0), 10, rot=(R(-80), 0, R(180)), coll=co)

    def _halve(self, ob, keep_top):
        bm = bmesh.new(); bm.from_mesh(ob.data)
        kill = [v for v in bm.verts if (v.co.z < -1e-4 if keep_top else v.co.z > 1e-4)]
        bmesh.ops.delete(bm, geom=kill, context='VERTS')
        bm.to_mesh(ob.data); bm.free()

    def update(self, t, breathe=1.0, glow=2.0, open_=0.0, seam=0.0):
        s = 1 + 0.02 * breathe * math.sin(t * 2.2)
        self.pearl_root.scale = (s,) * 3
        pulse = 1 + 0.45 * breathe * (0.5 + 0.5 * math.sin(t * 2.2))
        nd = self.pearl_mat.node_tree.nodes[self.pearl_mat['emit']]
        nd.inputs[1].default_value = 0.16 * glow * pulse
        for l, e in zip(self.pearl_lights, (900, 500)):
            l.data.energy = e * (glow / 2.0) * pulse
        self.hinge.rotation_euler = (R(-28 * open_), 0, 0)
        set_emit(self.seam_mat, 40 * seam)
        self.seam.hide_render = seam < 0.01
        set_emit(self.core_mat, 25 * max(seam, open_))
        self.core_light.data.energy = 3000 * open_ + 400 * seam
        for o, p0, ph in self.sparks:
            o.location = (p0.x + 0.3 * math.sin(t * 0.5 + ph), p0.y + 0.2 * math.cos(t * 0.4 + ph), p0.z + 0.4 * math.sin(t * 0.3 + ph))


def lux_facade(A, M=None):
    """Außenfassade um das Halbkreis-Fenster (für Außenansicht)."""
    co = A.coll
    M = M or Mats()
    gold = gold_mat('fgold')
    fac = prim('cube', 'lfacade', (0, 3.95, 1.6), scale=(30, 0.08, 22), mat=M.hull, coll=co)
    cutter = prim('cyl', 'lfacut', (0, 3.95, 0.12), rot=(R(90), 0, 0), scale=(A.win_r, A.win_r, 0.5), seg=128, coll=co)
    cut(fac, cutter)
    rim = [(math.cos(math.pi * k / 96) * (A.win_r + 0.15), 4.06, 0.12 + math.sin(math.pi * k / 96) * (A.win_r + 0.15)) for k in range(97)]
    tube('lf_rim', rim, 0.16, 14, gold, co)
    prim('cube', 'lf_sill', (0, 4.1, 0.0), scale=(A.win_r + 0.4, 0.15, 0.12), mat=gold, bevel=0.03, coll=co)
    # Nachbarfenster (kleiner, warm leuchtend)
    for i in (-2, -1, 1, 2):
        for j in (-1, 0, 1):
            if j == 0 and abs(i) < 2:
                continue
            x, z = i * 7.5, 0.12 + j * 5.2
            prim('cyl', 'lf_win', (x, 4.0, z + 1.2), rot=(R(90), 0, 0), scale=(1.6, 1.6, 0.03), mat=M.winobj, seg=48, coll=co)
            rr = [(x + math.cos(math.pi * k / 48) * 1.7, 4.06, z + 1.2 + math.sin(math.pi * k / 48) * 1.7) for k in range(-48, 49)]
            tube('lf_wr', rr, 0.1, 10, gold, co)
    for j in range(-3, 4):
        prim('cube', 'lf_trim', (0, 4.08, 0.12 + j * 5.2 - 1.0), scale=(30, 0.1, 0.1), mat=gold, bevel=0.03, coll=co)
    t = text_obj('lf_num', '−147', 0.5, M.neon, extrude=0.03, font=font('FreeSerifBold.ttf'), coll=co)
    t.location = (0, 4.12, A.win_r + 0.8); t.rotation_euler = (R(90), 0, R(180))
    return M
