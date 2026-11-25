"""Innen-Sets: Wohnung Etage -147, Flur, Aufzug."""
import bpy, bmesh, math
from mathutils import Vector, Matrix
from lib import *
from sets import fog_all, fish_mat, fish_mesh, School, jelly, hull_mat, window_mat

R = math.radians


def planks_mat(name='planks', c1='#7A4A2E', c2='#A86C43'):
    mat = principled(name, hexc(c1), rough=0.45, coat=0.25)
    nt = mat.node_tree
    b = nt.nodes[mat['bsdf']]
    tc = nt.nodes.new('ShaderNodeTexCoord')
    br = nt.nodes.new('ShaderNodeTexBrick')
    br.inputs['Color1'].default_value = (*hexc(c1), 1)
    br.inputs['Color2'].default_value = (*hexc(c2), 1)
    br.inputs['Mortar'].default_value = (*hexc('#2A170D'), 1)
    br.inputs['Scale'].default_value = 1.0
    br.inputs['Mortar Size'].default_value = 0.006
    br.inputs['Brick Width'].default_value = 1.6
    br.inputs['Row Height'].default_value = 0.16
    br.offset = 0.37
    nt.links.new(tc.outputs['Object'], br.inputs['Vector'])
    wv = nt.nodes.new('ShaderNodeTexWave'); wv.inputs['Scale'].default_value = 3; wv.inputs['Distortion'].default_value = 6
    wv.inputs['Detail'].default_value = 4
    nt.links.new(tc.outputs['Object'], wv.inputs['Vector'])
    mx = nt.nodes.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'; mx.inputs['Factor'].default_value = 0.35
    nt.links.new(br.outputs['Color'], mx.inputs['A']); nt.links.new(wv.outputs['Color'], mx.inputs['B'])
    nt.links.new(mx.outputs['Result'], b.inputs['Base Color'])
    bp = nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.3
    nt.links.new(br.outputs['Fac'], bp.inputs['Height'])
    nt.links.new(bp.outputs[0], b.inputs['Normal'])
    return mat


def panel_mat(name, c1, c2, scale=1.2):
    """Wandpaneele mit Fugen (Brick-Textur als Raster)."""
    mat = principled(name, hexc(c1), rough=0.55, metal=0.3)
    nt = mat.node_tree
    b = nt.nodes[mat['bsdf']]
    tc = nt.nodes.new('ShaderNodeTexCoord')
    br = nt.nodes.new('ShaderNodeTexBrick')
    br.inputs['Color1'].default_value = (*hexc(c1), 1)
    br.inputs['Color2'].default_value = (*hexc(c2), 1)
    br.inputs['Mortar'].default_value = (*[x * 0.4 for x in hexc(c1)], 1)
    br.inputs['Scale'].default_value = scale
    br.inputs['Mortar Size'].default_value = 0.008
    br.inputs['Brick Width'].default_value = 1.0
    br.inputs['Row Height'].default_value = 0.5
    br.offset = 0.0
    nt.links.new(tc.outputs['Object'], br.inputs['Vector'])
    nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 4
    nt.links.new(tc.outputs['Object'], nz.inputs['Vector'])
    mx = nt.nodes.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.blend_type = 'OVERLAY'; mx.inputs['Factor'].default_value = 0.25
    nt.links.new(br.outputs['Color'], mx.inputs['A']); nt.links.new(nz.outputs['Color'], mx.inputs['B'])
    nt.links.new(mx.outputs['Result'], b.inputs['Base Color'])
    bp = nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.4; bp.invert = True
    nt.links.new(br.outputs['Fac'], bp.inputs['Height'])
    nt.links.new(bp.outputs[0], b.inputs['Normal'])
    return mat


def wallpaper_mat(name='wallp', c1='#1F4D57', c2='#2C6670'):
    """Tapete mit Wellenmuster."""
    mat = principled(name, hexc(c1), rough=0.75)
    nt = mat.node_tree
    b = nt.nodes[mat['bsdf']]
    tc = nt.nodes.new('ShaderNodeTexCoord')
    wv = nt.nodes.new('ShaderNodeTexWave'); wv.wave_type = 'BANDS'; wv.bands_direction = 'Z'
    wv.wave_profile = 'SIN'
    wv.inputs['Scale'].default_value = 4.0; wv.inputs['Distortion'].default_value = 1.2
    wv.inputs['Detail Scale'].default_value = 1.0
    nt.links.new(tc.outputs['Object'], wv.inputs['Vector'])
    cr = nt.nodes.new('ShaderNodeValToRGB')
    el = cr.color_ramp.elements
    el[0].position = 0.45; el[0].color = (*hexc(c1), 1)
    el[1].position = 0.55; el[1].color = (*hexc(c2), 1)
    nt.links.new(wv.outputs['Fac'], cr.inputs[0])
    nt.links.new(cr.outputs[0], b.inputs['Base Color'])
    return mat


def cut(ob, cutter):
    m = ob.modifiers.new('cut', 'BOOLEAN'); m.object = cutter; m.operation = 'DIFFERENCE'; m.solver = 'EXACT'
    cutter.hide_render = True; cutter.hide_viewport = True
    cutter.display_type = 'WIRE'


def books(coll, x0, y, z, width, rg, depth=0.22, axis='x', mats=None):
    """Bücherreihe auf Brett."""
    x = x0
    obs = []
    while x < x0 + width - 0.03:
        w = rg.uniform(0.025, 0.055); h = rg.uniform(0.18, 0.28)
        m = rg.choice(mats)
        lean = R(rg.uniform(-4, 4)) if rg.random() < 0.15 else 0
        o = prim('cube', 'book', (x + w / 2, y, z + h / 2), rot=(0, lean, 0), scale=(w / 2, depth / 2 * rg.uniform(0.8, 1), h / 2), mat=m, bevel=0.004, coll=coll)
        obs.append(o)
        # Buchrücken-Band
        if rg.random() < 0.6:
            bb = prim('cube', 'bookband', (0, -depth / 2 * 0.98, h * rg.uniform(0.1, 0.35)), scale=(w / 2 * 1.01, 0.003, 0.008),
                 mat=mats[-1], coll=coll)
            bb.parent = o
        x += w + 0.002
    return obs


class Apartment:
    """Wohnung von Shelly. Fensterwand bei y=+3, Boden z=0, Raum x∈[-4,4], y∈[-3,3], Höhe 3.2."""

    def __init__(self, coll=None, outside=True, t=0.0):
        self.coll = co = coll
        rg = rnd(11)
        self.M = M = {}
        M['planks'] = planks_mat()
        M['wall'] = wallpaper_mat()
        M['wainscot'] = panel_mat('wains', '#5B3424', '#6A3D2A', 2.5)
        M['brass'] = principled('brass', hexc('#C8923A'), rough=0.25, metal=1.0, bump=(80, 0.03))
        M['brass_dark'] = principled('brass2', hexc('#8A5F25'), rough=0.4, metal=1.0)
        M['copper'] = principled('copper', hexc('#B4643C'), rough=0.35, metal=1.0, bump=(40, 0.05))
        M['hull'] = hull_mat('hullin', '#2A4E50', '#3D6A5A')
        M['wood'] = principled('wood', hexc('#6B3A22'), rough=0.4, coat=0.4, bump=(6, 0.1, 4, 'wave'))
        M['velvet'] = principled('velvet', hexc('#C9772F'), rough=0.85, sheen=1.0, bump=(200, 0.08))
        M['cushion'] = principled('cushion', hexc('#E0B547'), rough=0.85, sheen=0.8, bump=(55, 0.3, 0, 'knit'))
        M['rug1'] = principled('rug1', hexc('#9E3B3B'), rough=0.95, sheen=0.6, bump=(300, 0.3))
        M['ceramic'] = principled('ceramic', hexc('#F1ECE2'), rough=0.15, coat=0.6)
        M['tea'] = principled('tea', hexc('#5A2A10'), rough=0.05)
        M['shade'] = principled('shade', hexc('#F2C98A'), rough=0.7, sss=0.0, trans=0.0)
        M['shadein'] = emission('shadein', (1.0, 0.72, 0.4), 6.0)
        M['bulb'] = emission('bulb', (1.0, 0.8, 0.5), 30.0)
        M['dial'] = principled('dial', hexc('#F3E9D2'), rough=0.35)
        M['black'] = principled('blk', hexc('#141414'), rough=0.4)
        M['red'] = principled('redp', hexc('#C0262C'), rough=0.4)
        M['glass'] = window_glass('winglass', (0.85, 0.95, 1.0), 0.06)
        M['plant'] = principled('plant', hexc('#3E8E5A'), rough=0.5, sss=0.3, sss_r=(0.3, 1, 0.3))
        M['pot'] = principled('pot', hexc('#C66B4A'), rough=0.7, bump=(60, 0.2))
        M['frame'] = principled('frame', hexc('#3B2616'), rough=0.5, coat=0.4)
        M['paper'] = principled('paper', hexc('#E8DCC0'), rough=0.8)
        bookmats = [principled(f'bk{i}', hexc(c), rough=0.6) for i, c in
                    enumerate(['#8C2F39', '#2F5D8C', '#D9A441', '#3E7C59', '#6A4C93', '#C4623A', '#1F3B4D', '#E8D8B0'])]
        bookmats.append(principled('bkgold', hexc('#D4A017'), rough=0.3, metal=1.0))
        H = 3.2
        # Boden
        prim('cube', 'floor', (0, 0, -0.05), scale=(4.2, 3.2, 0.05), mat=M['planks'], coll=co)
        # Decke mit Holzbalken
        prim('cube', 'ceil', (0, 0, H + 0.05), scale=(4.2, 3.2, 0.05), mat=M['hull'], coll=co)
        for i in range(5):
            prim('cube', f'beam{i}', (-3.2 + i * 1.6, 0, H - 0.08), scale=(0.08, 3.1, 0.1), mat=M['wood'], bevel=0.015, coll=co)
        # Fensterwand (y=3) mit Bullauge
        ww = prim('cube', 'winwall', (0, 3.25, H / 2), scale=(4.2, 0.25, H / 2 + 0.1), mat=M['hull'], coll=co)
        cutter = prim('cyl', 'wincut', (0, 3.25, 1.6), rot=(R(90), 0, 0), scale=(1.15, 1.15, 0.6), seg=64, coll=co)
        cut(ww, cutter)
        # Innenwände
        prim('cube', 'wallL', (-4.15, 0, H / 2), scale=(0.15, 3.2, H / 2), mat=M['wall'], coll=co)
        prim('cube', 'wallR', (4.15, 0, H / 2), scale=(0.15, 3.2, H / 2), mat=M['wall'], coll=co)
        prim('cube', 'wallB', (0, -3.15, H / 2), scale=(4.2, 0.15, H / 2), mat=M['wall'], coll=co)
        # Holzvertäfelung unten + Leisten
        for nm, loc, sc in [('wsL', (-3.98, 0, 0.5), (0.03, 3.0, 0.5)), ('wsR', (3.98, 0, 0.5), (0.03, 3.0, 0.5)),
                            ('wsB', (0, -2.98, 0.5), (4.0, 0.03, 0.5))]:
            prim('cube', nm, loc, scale=sc, mat=M['wainscot'], coll=co)
            prim('cube', nm + 'cap', (loc[0], loc[1], 1.02), scale=(sc[0] + 0.015, sc[1] + 0.015 if sc[1] > 1 else sc[1] + 0.015, 0.025),
                 mat=M['wood'], bevel=0.008, coll=co)
        # Bullauge: Messingrahmen, Nieten, Glas, Tunnel
        self.win_c = Vector((0, 3.0, 1.6))
        prim('torus', 'winframe', (0, 2.98, 1.6), rot=(R(90), 0, 0), mat=M['brass'], R=1.22, r=0.12, seg=96, seg2=16, coll=co)
        prim('torus', 'winframe2', (0, 3.04, 1.6), rot=(R(90), 0, 0), mat=M['brass_dark'], R=1.12, r=0.06, seg=96, seg2=12, coll=co)
        tunnel = lathe('wintunnel', [(1.15, 0), (1.15, 0.55)], 64, M['hull'], co, False, False)
        tunnel.rotation_euler = (R(-90), 0, 0); tunnel.location = (0, 3.0, 1.6)
        for k in range(24):
            a = 2 * math.pi * k / 24
            prim('sphere', f'winriv{k}', (math.cos(a) * 1.38, 2.95, 1.6 + math.sin(a) * 1.38), scale=(0.035, 0.03, 0.035), mat=M['brass'], seg=10, coll=co)
        # Kreuzstreben im Fenster
        prim('cube', 'winbar', (0, 3.3, 1.6), scale=(1.15, 0.025, 0.025), mat=M['brass_dark'], coll=co)
        self.glass = prim('cyl', 'winglass', (0, 3.32, 1.6), rot=(R(90), 0, 0), scale=(1.14, 1.14, 0.01), mat=M['glass'], seg=64, coll=co)
        # Fensterbank
        prim('cube', 'sill', (0, 2.78, 0.38), scale=(1.3, 0.22, 0.04), mat=M['wood'], bevel=0.015, coll=co)
        # --- Messgeräte links/rechts vom Fenster
        self.gauge = self._gauge((1.75, 2.98, 1.85), 0.28)
        self.depth = self._depth_counter((-1.85, 2.96, 1.95))
        # Rohre unter der Decke
        pm = M['copper']
        tube('pipe1', [(-4, 2.8, 2.9), (4, 2.8, 2.9)], 0.07, 16, pm, co)
        tube('pipe2', [(-4, 2.6, 3.0), (2.2, 2.6, 3.0), (2.4, 2.6, 2.8), (2.4, 2.9, 2.8), (2.4, 2.9, 0.2)], 0.05, 16, M['brass_dark'], co)
        for x in (-3, -1.5, 0.5, 2.0, 3.5):
            prim('cyl', 'pipeclamp', (x, 2.8, 2.9), rot=(0, R(90), 0), scale=(0.09, 0.09, 0.04), mat=M['brass'], coll=co)
        # Ventilrad
        vw = prim('torus', 'valve', (2.4, 2.78, 1.2), rot=(R(90), 0, 0), mat=M['red'], R=0.14, r=0.02, seg=32, coll=co)
        for k in range(4):
            prim('cube', f'spoke{k}', (2.4, 2.78, 1.2), rot=(0, R(45 * k), 0), scale=(0.14, 0.012, 0.012), mat=M['red'], coll=co)
        # --- Sessel
        self._armchair((-0.45, 0.55, 0), R(168))
        # Teppich
        rug = lathe('rug', [(0, 0.01), (1.6, 0.01), (1.62, 0.0)], 64, None, co, False, True)
        rug.scale = (1, 0.7, 1); rug.location = (-0.2, 0.7, 0.0)
        rug.data.materials.append(self._rug_mat())
        # Beistelltisch mit Lampe und Tee
        tbl = (0.75, 1.05, 0)
        lathe('tabletop', [(0, 0.62), (0.38, 0.62), (0.4, 0.64), (0.38, 0.66), (0, 0.66)], 48, M['wood'], co).location = tbl
        lathe('tableleg', [(0.18, 0.0), (0.05, 0.06), (0.035, 0.3), (0.05, 0.55), (0.1, 0.62)], 32, M['wood'], co).location = tbl
        self.lamp_pos = Vector((tbl[0] - 0.12, tbl[1] + 0.1, 0.66))
        lb = lathe('lampbase', [(0.0, 0.0), (0.09, 0.0), (0.1, 0.02), (0.06, 0.08), (0.02, 0.1), (0.012, 0.42)], 32, M['brass'], co)
        lb.location = self.lamp_pos
        self.shade = lathe('lampshade', [(0.22, 0.36), (0.13, 0.6)], 48, M['shade'], co, False, False)
        self.shade.location = self.lamp_pos
        sm = self.shade.modifiers.new('sol', 'SOLIDIFY'); sm.thickness = 0.008
        self.shade.data.materials.append(M['shadein'])
        sm.material_offset = 1
        prim('sphere', 'bulb', tuple(self.lamp_pos + Vector((0, 0, 0.45))), scale=(0.045,) * 3, mat=M['bulb'], coll=co)
        self.lamp_light = add_light('POINT', 'lamplight', tuple(self.lamp_pos + Vector((0, 0, 0.47))), 120, (1.0, 0.7, 0.4), 0.08, coll=co)
        # Tasse
        cp = Vector((tbl[0] + 0.15, tbl[1] - 0.12, 0.66))
        cup = lathe('cup', [(0.0, 0.0), (0.035, 0.0), (0.045, 0.01), (0.05, 0.08), (0.046, 0.08), (0.04, 0.012), (0.0, 0.012)], 32, M['ceramic'], co, False, False)
        cup.location = cp
        prim('cyl', 'teasurf', tuple(cp + Vector((0, 0, 0.065))), scale=(0.043, 0.043, 0.002), mat=M['tea'], coll=co)
        prim('torus', 'cuphandle', tuple(cp + Vector((0.055, 0, 0.045))), rot=(R(90), 0, 0), scale=(0.7, 1, 1), mat=M['ceramic'], R=0.022, r=0.006, seg=24, coll=co)
        lathe('saucer', [(0, 0), (0.07, 0.0), (0.085, 0.012), (0.08, 0.014), (0, 0.006)], 32, M['ceramic'], co).location = cp - Vector((0, 0, 0.002))
        self.cup_pos = cp
        # Buch auf Tisch
        prim('cube', 'tbook', (tbl[0] - 0.12, tbl[1] - 0.15, 0.68), rot=(0, 0, R(20)), scale=(0.1, 0.07, 0.015), mat=bookmats[1], bevel=0.004, coll=co)
        # --- Regal an linker Wand
        sx = -3.85
        for k, z in enumerate((1.3, 1.75, 2.2)):
            prim('cube', f'shelf{k}', (sx + 0.12, -0.6, z), scale=(0.14, 1.1, 0.02), mat=M['wood'], bevel=0.006, coll=co)
            for bx in (-1.65, 0.45):
                pass
        # Bücher entlang y: Regal parallel zur Wand -> Bücher drehen
        for k, z in enumerate((1.32, 1.77, 2.22)):
            grp = books(co, -1.6, 0, z, 1.6 if k != 1 else 1.0, rg, 0.2, mats=bookmats)
            for b in grp:
                p = b.location.copy()
                b.location = (sx + 0.12, p.x, p.z)
                b.rotation_euler = (b.rotation_euler.y, 0, R(90))
        # Deko auf Regal: Muscheln, Flaschenschiff, Pflanze
        self._bottle_ship((sx + 0.12, -0.55 + 0.45, 1.79 + 0.0))
        self._pot_plant((sx + 0.15, 0.25, 2.22), 0.6)
        self._pot_plant((3.4, 2.4, 0.0), 1.4, big=True)
        for k in range(4):
            sh = lathe(f'deco_shell{k}', [(0, 0), (0.05, 0.01), (0.04, 0.05), (0.01, 0.08), (0, 0.085)], 12, M['ceramic'], co)
            sh.location = (sx + 0.12, -1.55 + k * 0.08, 1.32); sh.rotation_euler = (R(-70), 0, R(20 * k)); sh.scale = (0.8, 0.8, 0.8)
        # Bilderrahmen an Rückwand / rechts
        self._frames()
        # Wanduhr über Regal (links an der Rückwand)
        self.clock = self._clock((-2.4, -2.95, 2.3), 0.32)
        # Deckenlampe
        lathe('ceillamp', [(0.0, 3.2), (0.03, 3.2), (0.01, 2.9), (0.2, 2.75), (0.28, 2.62), (0, 2.6)], 32, M['brass'], co)
        prim('sphere', 'ceilbulb', (0, 0, 2.58), scale=(0.08, 0.08, 0.05), mat=M['bulb'], coll=co)
        self.ceil_light = add_light('POINT', 'ceillight', (0, 0, 2.45), 160, (1.0, 0.75, 0.5), 0.2, coll=co)
        # Tür rechts
        self._door((4.0, -1.2, 0))
        # Hängende Glaskugel-Lampen (Fischernetz-Bojen)
        self.floats = []
        for k, (x, y, c) in enumerate([(-3.2, -2.3, (0.3, 0.85, 1.0)), (-2.6, -1.7, (1.0, 0.55, 0.3)), (-3.4, -1.2, (0.5, 1.0, 0.7))]):
            tube(f'cord{k}', [(x, y, 3.2), (x, y, 2.35 - k * 0.15)], 0.006, 6, M['black'], co)
            fm = emission(f'floatm{k}', c, 2.5)
            prim('sphere', f'float{k}', (x, y, 2.25 - k * 0.15), scale=(0.1,) * 3, mat=fm, coll=co)
            prim('torus', f'floatnet{k}', (x, y, 2.25 - k * 0.15), mat=principled(f'net{k}', hexc('#8B6A3E'), 0.8), R=0.1, r=0.008, seg=24, coll=co)
            self.floats.append(fm)
        # Rotes Alarmlicht (aus)
        self.alarm_mat = emission('alarm', (1.0, 0.08, 0.04), 0.0)
        lathe('alarmbase', [(0.1, 0), (0.1, 0.03), (0, 0.03)], 24, M['brass'], co).location = (3.0, 2.98, 2.7)
        a = prim('sphere', 'alarmglass', (3.0, 2.9, 2.75), scale=(0.08, 0.08, 0.1), mat=self.alarm_mat, coll=co)
        self.alarm_light = add_light('SPOT', 'alarmlight', (3.0, 2.8, 2.75), 0, (1, 0.1, 0.05), 0.05, spot=R(120), coll=co)
        look_at(self.alarm_light, (0, 0, 0.5))
        # Außenwelt
        if outside:
            self._outside(t)
        # Kreide-Riss (unsichtbar bis gebraucht)
        self.crack = None

    # -------------------------------------------------------------
    def _rug_mat(self):
        mat = principled('rugm', hexc('#9E3B3B'), rough=0.95, sheen=0.7, bump=(250, 0.35))
        nt = mat.node_tree; b = nt.nodes[mat['bsdf']]
        tc = nt.nodes.new('ShaderNodeTexCoord')
        ln = nt.nodes.new('ShaderNodeVectorMath'); ln.operation = 'LENGTH'
        nt.links.new(tc.outputs['Object'], ln.inputs[0])
        m = nt.nodes.new('ShaderNodeMath'); m.operation = 'MULTIPLY'; m.inputs[1].default_value = 9
        nt.links.new(ln.outputs['Value'], m.inputs[0])
        fr = nt.nodes.new('ShaderNodeMath'); fr.operation = 'FRACT'
        nt.links.new(m.outputs[0], fr.inputs[0])
        cr = nt.nodes.new('ShaderNodeValToRGB'); el = cr.color_ramp.elements
        el[0].position = 0.0; el[0].color = (*hexc('#9E3B3B'), 1)
        el[1].position = 0.75; el[1].color = (*hexc('#E0B547'), 1)
        e = el.new(0.5); e.color = (*hexc('#9E3B3B'), 1)
        e = el.new(0.85); e.color = (*hexc('#1E6E6C'), 1)
        cr.color_ramp.interpolation = 'CONSTANT'
        nt.links.new(fr.outputs[0], cr.inputs[0])
        nt.links.new(cr.outputs[0], b.inputs['Base Color'])
        return mat

    def _armchair(self, loc, rot):
        co = self.coll; M = self.M
        p = empty('chair', loc, (0, 0, rot), coll=co)
        prim('cube', 'ch_seat', (0, 0, 0.42), scale=(0.45, 0.42, 0.1), mat=M['velvet'], bevel=0.07, parent=p, coll=co, subsurf=1)
        prim('cube', 'ch_base', (0, 0, 0.22), scale=(0.47, 0.44, 0.12), mat=M['velvet'], bevel=0.05, parent=p, coll=co)
        prim('cube', 'ch_back', (0, 0.38, 0.85), rot=(R(-10), 0, 0), scale=(0.47, 0.1, 0.42), mat=M['velvet'], bevel=0.08, parent=p, coll=co, subsurf=1)
        for s in (-1, 1):
            prim('cube', f'ch_arm{s}', (s * 0.5, 0.0, 0.55), scale=(0.1, 0.45, 0.18), mat=M['velvet'], bevel=0.08, parent=p, coll=co, subsurf=1)
            for fy in (-0.35, 0.35):
                lathe(f'ch_leg{s}{fy}', [(0.03, 0), (0.025, 0.1), (0.04, 0.12)], 16, M['wood'], co).parent = p
                D.objects[f'ch_leg{s}{fy}'].location = (s * 0.42, fy, 0)
        # Knöpfe (Chesterfield)
        for i in range(3):
            for j in range(2):
                prim('sphere', 'ch_btn', (-0.3 + i * 0.3, 0.27 - 0.0, 0.72 + j * 0.25), scale=(0.018, 0.012, 0.018), mat=M['brass'], parent=p, coll=co)
        # Kissen + Decke
        prim('cube', 'ch_cush', (0.25, 0.22, 0.68), rot=(R(-20), R(15), R(-10)), scale=(0.17, 0.07, 0.15), mat=M['cushion'], bevel=0.06, parent=p, coll=co, subsurf=2)
        self.chair = p

    def _gauge(self, loc, r):
        co = self.coll; M = self.M
        p = empty('gauge', loc, (R(-90), 0, 0), coll=co)
        prim('cyl', 'g_body', (0, 0, 0.0), scale=(r, r, 0.05), mat=M['brass'], bevel=0.02, parent=p, coll=co)
        prim('torus', 'g_bezel', (0, 0, -0.05), mat=M['brass'], R=r, r=0.025, seg=64, parent=p, coll=co)
        prim('cyl', 'g_face', (0, 0, -0.052), scale=(r * 0.92, r * 0.92, 0.002), mat=M['dial'], parent=p, coll=co)
        # Skala-Striche + roter Bereich
        for k in range(41):
            a = R(-135 + 270 * k / 40)
            L = 0.05 if k % 5 == 0 else 0.025
            prim('cube', 'g_tick', (math.sin(a) * (r * 0.8 - L / 2), -math.cos(a) * (r * 0.8 - L / 2), -0.056),
                 rot=(0, 0, a), scale=(0.004 if k % 5 else 0.007, L / 2, 0.001), mat=M['red'] if k > 32 else M['black'], parent=p, coll=co)
        for k, v in enumerate(['0', '100', '200', '300', '400', '500', '600', '700', '800']):
            a = R(-135 + 270 * k / 8)
            t = text_obj('g_num', v, 0.045, M['black'], coll=co)
            t.parent = p; t.location = (math.sin(a) * r * 0.6, -math.cos(a) * r * 0.6, -0.057); t.rotation_euler = (R(180), 0, 0)
        t = text_obj('g_lbl', 'BAR', 0.04, M['red'], coll=co); t.parent = p; t.location = (0, r * 0.35, -0.057); t.rotation_euler = (R(180), 0, 0)
        t = text_obj('g_lbl2', 'DRUCK', 0.035, M['black'], coll=co); t.parent = p; t.location = (0, -r * 0.3, -0.057); t.rotation_euler = (R(180), 0, 0)
        needle_p = empty('g_needlep', (0, 0, -0.065), parent=p, coll=co)
        needle_p.rotation_mode = 'XYZ'
        prim('cube', 'g_needle', (0, -r * 0.35, 0), scale=(0.008, r * 0.45, 0.003), mat=M['red'], parent=needle_p, coll=co)
        prim('cyl', 'g_cap', (0, 0, -0.004), scale=(0.022, 0.022, 0.008), mat=M['brass'], parent=needle_p, coll=co)
        prim('cyl', 'g_glass', (0, 0, -0.07), scale=(r * 0.95, r * 0.95, 0.003), mat=window_glass('gglass', (0.95, 0.97, 1.0), 0.1), parent=p, coll=co)
        # Rohr in die Wand
        tube('g_pipe', [(loc[0], loc[1] + 0.05, loc[2] - r), (loc[0], loc[1] + 0.05, loc[2] - r - 0.4), (loc[0], loc[1] + 0.3, loc[2] - r - 0.4)], 0.025, 12, M['brass_dark'], co)
        self.needle = needle_p
        return p

    def set_gauge(self, val):  # 0..1
        a = -135 + 270 * val
        self.needle.rotation_euler = (0, 0, R(a))

    def _depth_counter(self, loc):
        """Nixie-Röhren-Tiefenanzeige 4000 m."""
        co = self.coll; M = self.M
        p = empty('depth', loc, coll=co)
        prim('cube', 'dc_box', (0, 0.05, 0), scale=(0.42, 0.08, 0.17), mat=M['wood'], bevel=0.02, parent=p, coll=co)
        prim('cube', 'dc_plate', (0, -0.035, -0.22), scale=(0.25, 0.01, 0.04), mat=M['brass'], bevel=0.005, parent=p, coll=co)
        t = text_obj('dc_lbl', 'TIEFE  ·  METER', 0.04, M['black'], coll=co); t.parent = p; t.location = (0, -0.047, -0.22); t.rotation_euler = (R(90), 0, 0)
        nix = emission('nixie', (1.0, 0.32, 0.04), 4.5)
        self.nixie_mat = nix
        gm = window_glass('nixglass', (0.95, 0.9, 0.85), 0.12)
        self.nix_digits = []
        for k in range(4):
            x = -0.27 + k * 0.18
            lathe(f'dc_tube{k}', [(0.0, 0.0), (0.07, 0.0), (0.07, 0.26), (0.05, 0.31), (0.0, 0.33)], 24, gm, co).parent = p
            D.objects[f'dc_tube{k}'].location = (x, -0.02, -0.15)
            lathe(f'dc_sock{k}', [(0.075, 0.0), (0.075, 0.05), (0, 0.05)], 24, M['black'], co).parent = p
            D.objects[f'dc_sock{k}'].location = (x, -0.02, -0.16)
            t = text_obj(f'dc_d{k}', '0', 0.2, nix, coll=co, bevel=0.002)
            t.parent = p; t.location = (x, -0.03, -0.01); t.rotation_euler = (R(90), 0, 0)
            t.data.extrude = 0.001
            # Gitter
            for g in range(5):
                prim('cube', 'dc_grid', (x, -0.07, -0.12 + g * 0.06), scale=(0.06, 0.0008, 0.0008), mat=M['brass_dark'], parent=p, coll=co)
            self.nix_digits.append(t)
        self.nix_glow = add_light('POINT', 'nixlight', (loc[0], loc[1] - 0.25, loc[2]), 6, (1.0, 0.45, 0.1), 0.2, coll=co)
        return p

    def set_depth(self, s):
        for d, ch in zip(self.nix_digits, s.rjust(4)):
            d.data.body = ch

    def _clock(self, loc, r):
        co = self.coll; M = self.M
        p = empty('clock', loc, (R(90), 0, 0), coll=co)
        prim('cyl', 'c_body', (0, 0, 0), scale=(r, r, 0.04), mat=M['brass'], bevel=0.015, parent=p, coll=co)
        prim('torus', 'c_bezel', (0, 0, -0.045), mat=M['brass'], R=r, r=0.03, seg=64, parent=p, coll=co)
        prim('cyl', 'c_face', (0, 0, -0.046), scale=(r * 0.9, r * 0.9, 0.002), mat=M['dial'], parent=p, coll=co)
        for k in range(60):
            a = R(k * 6)
            L = 0.04 if k % 5 == 0 else 0.015
            prim('cube', 'c_tick', (math.sin(a) * (r * 0.84 - L / 2), math.cos(a) * (r * 0.84 - L / 2), -0.05), rot=(0, 0, -a),
                 scale=(0.006 if k % 5 == 0 else 0.002, L / 2, 0.001), mat=M['black'], parent=p, coll=co)
        rom = ['XII', 'I', 'II', 'III', 'IIII', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI']
        for k in range(12):
            a = R(k * 30)
            t = text_obj('c_num', rom[k], 0.045, M['black'], coll=co)
            t.parent = p; t.location = (math.sin(a) * r * 0.66, math.cos(a) * r * 0.66, -0.051); t.rotation_euler = (R(180), 0, R(180))
            t.location.x *= -1
        t = text_obj('c_brand', 'SUNKEN PEARL', 0.022, M['red'], coll=co); t.parent = p; t.location = (0, r * 0.32, -0.051); t.rotation_euler = (R(180), 0, R(180))
        self.hands = {}
        for nm, L, w, z, m in (('h', 0.5, 0.012, -0.056, M['black']), ('m', 0.75, 0.008, -0.06, M['black']), ('s', 0.82, 0.003, -0.064, M['red'])):
            hp = empty('c_' + nm, (0, 0, z), parent=p, coll=co); hp.rotation_mode = 'XYZ'
            prim('cube', 'c_hand' + nm, (0, r * L / 2 - 0.02, 0), scale=(w, r * L / 2 + 0.02, 0.002), mat=m, parent=hp, coll=co)
            if nm == 'h':
                prim('sphere', 'c_hknob', (0, r * L * 0.85, 0), scale=(0.02, 0.025, 0.002), mat=m, parent=hp, coll=co)
            self.hands[nm] = hp
        prim('cyl', 'c_pin', (0, 0, -0.067), scale=(0.012, 0.012, 0.006), mat=M['brass'], parent=p, coll=co)
        prim('cyl', 'c_glass', (0, 0, -0.07), scale=(r * 0.93, r * 0.93, 0.003), mat=window_glass('cglass', (0.95, 0.97, 1.0), 0.1), parent=p, coll=co)
        return p

    def set_clock(self, h, m, s):
        # Uhr ist um X um 90° gedreht, Zifferblatt zeigt nach -Y; Drehung um lokale Z (im Uhrzeigersinn von vorn = +)
        self.hands['h'].rotation_euler = (0, 0, R((h % 12 + m / 60) * 30))
        self.hands['m'].rotation_euler = (0, 0, R((m + s / 60) * 6))
        self.hands['s'].rotation_euler = (0, 0, R(s * 6))

    def _frames(self):
        co = self.coll; M = self.M
        rg = rnd(4)
        pics = [('#1D5C7A', '#F2C14E'), ('#C4623A', '#F4E3B5'), ('#2F4858', '#86BBD8'), ('#6A4C93', '#FFCA3A')]
        spots = [(-0.6, -2.97, 2.1, 0.28, 0.36), (0.2, -2.97, 2.25, 0.22, 0.22), (0.9, -2.97, 2.05, 0.3, 0.24), (3.97, 1.0, 2.0, 0.35, 0.28)]
        for k, (x, y, z, w, h) in enumerate(spots):
            rot = (R(90), 0, R(90) if x > 3 else 0)
            p = empty(f'pic{k}', (x, y, z), rot, coll=co)
            if x > 3: p.rotation_euler = (R(90), 0, R(90))
            prim('cube', f'pf{k}', (0, 0, 0), scale=(w, h, 0.02), mat=M['frame'], bevel=0.01, parent=p, coll=co)
            c1, c2 = pics[k]
            pm = color_ramp_mat(f'pic{k}m', [(0.0, hexc(c1)), (0.55, hexc(c1)), (0.6, hexc(c2)), (1.0, hexc(c2))], coord='Y', lo=-h, hi=h, rough=0.6)
            prim('cube', f'pp{k}', (0, 0, -0.022), scale=(w * 0.82, h * 0.82, 0.002), mat=pm, parent=p, coll=co)
            # kleines Motiv: Fisch/Kreis
            prim('sphere', f'pm{k}', (rg.uniform(-w, w) * 0.4, rg.uniform(-h, h) * 0.3, -0.026), scale=(w * 0.18, w * 0.12, 0.002), mat=M['ceramic'], parent=p, coll=co)

    def _door(self, loc):
        co = self.coll; M = self.M
        p = empty('door', loc, (0, 0, R(90)), coll=co)
        self.door = p
        prim('cube', 'd_frame', (0, 0.0, 1.1), scale=(0.62, 0.12, 1.15), mat=M['brass_dark'], bevel=0.03, parent=p, coll=co)
        d = prim('cube', 'd_leaf', (0, 0.05, 1.07), scale=(0.52, 0.1, 1.07), mat=M['wood'], bevel=0.02, parent=p, coll=co)
        for zz in (0.55, 1.5):
            prim('cube', 'd_panel', (0, -0.055, zz), scale=(0.38, 0.01, 0.32 if zz < 1 else 0.22), mat=M['wainscot'], bevel=0.01, parent=p, coll=co)
        prim('torus', 'd_port', (0, -0.06, 1.85), rot=(R(90), 0, 0), mat=M['brass'], R=0.14, r=0.025, seg=32, parent=p, coll=co)
        prim('cyl', 'd_portg', (0, -0.05, 1.85), rot=(R(90), 0, 0), scale=(0.13, 0.13, 0.005), mat=emission('corrglow', (1.0, 0.6, 0.3), 5.0), parent=p, coll=co)
        prim('sphere', 'd_knob', (-0.4, -0.12, 1.0), scale=(0.045,) * 3, mat=M['brass'], parent=p, coll=co)
        prim('cyl', 'd_rose', (-0.4, -0.065, 1.0), rot=(R(90), 0, 0), scale=(0.05, 0.05, 0.01), mat=M['brass'], parent=p, coll=co)
        t = text_obj('d_num', '-147', 0.12, M['brass'], extrude=0.005, coll=co); t.parent = p; t.location = (0, -0.07, 1.55); t.rotation_euler = (R(90), 0, 0)
        prim('cube', 'd_mail', (0, -0.06, 0.95), scale=(0.15, 0.01, 0.025), mat=M['brass'], bevel=0.005, parent=p, coll=co)
        # Fußmatte
        prim('cube', 'd_mat', (loc[0] - 0.5, loc[1], 0.01), scale=(0.3, 0.5, 0.01), mat=principled('mat', hexc('#7A5A3A'), 0.95, bump=(300, 0.5)), coll=co)

    def _bottle_ship(self, loc):
        co = self.coll; M = self.M
        p = empty('bottle', loc, (0, 0, R(90)), coll=co)
        b = lathe('bt_glass', [(0, 0), (0.07, 0), (0.075, 0.01), (0.075, 0.2), (0.03, 0.26), (0.025, 0.32), (0, 0.32)], 24, window_glass('btg', (0.8, 1, 0.85), 0.15), co)
        b.parent = p; b.rotation_euler = (0, R(90), 0); b.location = (-0.16, 0, 0.075)
        prim('cube', 'bt_hull', (0, 0, 0.03), scale=(0.09, 0.025, 0.018), mat=M['wood'], bevel=0.01, parent=p, coll=co)
        prim('cyl', 'bt_mast', (0, 0, 0.09), scale=(0.004, 0.004, 0.06), mat=M['wood'], parent=p, coll=co)
        prim('cube', 'bt_sail', (0.0, 0, 0.1), scale=(0.035, 0.002, 0.04), mat=M['paper'], parent=p, coll=co)
        prim('cyl', 'bt_cork', (0.17, 0, 0.075), rot=(0, R(90), 0), scale=(0.022, 0.022, 0.02), mat=M['pot'], parent=p, coll=co)

    def _pot_plant(self, loc, h, big=False):
        co = self.coll; M = self.M
        rg = rnd(int(loc[0] * 100))
        pot = lathe('pot', [(0, 0), (0.1, 0), (0.13, 0.15), (0.14, 0.16), (0, 0.16)], 24, M['pot'], co)
        pot.location = loc
        s = 1.6 if big else 0.7
        pot.scale = (s, s, s)
        n = 14 if big else 7
        for k in range(n):
            a = 2 * math.pi * k / n + rg.uniform(-0.3, 0.3)
            L = h * rg.uniform(0.5, 1.0)
            pts = []
            for j in range(8):
                u = j / 7
                pts.append((loc[0] + math.cos(a) * u * L * 0.35, loc[1] + math.sin(a) * u * L * 0.35, loc[2] + 0.15 * s + u * L - (u ** 2) * L * 0.3))
            tube(f'leaf{k}', pts, 0.02, 6, M['plant'], co, radii=[0.03 * s * (1 - 0.5 * (j / 7)) + 0.01 for j in range(8)])

    def _outside(self, t):
        """Meer vor dem Fenster: Dunkelheit, Fische, Qualle, entfernte Lichter."""
        co = self.coll
        self.out_mats = []
        bg = emission('outbg', (0.01, 0.06, 0.09), 1.0)
        bgp = prim('plane', 'outbg', (0, 30, 1.6), rot=(R(90), 0, 0), scale=(40, 30, 1), mat=bg, coll=co)
        # Lichtstrahl von oben (sehr schwach) – entfernte Fenster
        dots = emission('farwin', (1.0, 0.6, 0.25), 3.0)
        rg = rnd(9)
        for k in range(30):
            prim('sphere', 'farlight', (rg.uniform(-25, 25), rg.uniform(18, 28), rg.uniform(-15, 18)), scale=(0.15,) * 3, mat=dots, seg=8, coll=co)
        fm = fish_mat('fishout', '#6F8FA8', '#D8E4EC')
        self.school = School(co, 26, (2, 9, 1.8), 5, 0.35, seed=21, mat=fm, speed=0.8)
        self.jelly_t = t
        self.out_mats = ['outbg', 'farwin', 'fishout']


class Corridor:
    """Flur entlang -X..+X bei y∈[-1.3,1.3], Höhe 2.8; Aufzugtür am Ende bei x=+14."""

    def __init__(self, coll=None):
        co = self.coll = coll
        M = self.M = {}
        M['grate'] = principled('grate', hexc('#3A3F40'), rough=0.35, metal=0.9, bump=(30, 0.2))
        M['panel'] = panel_mat('cpanel', '#2D5650', '#326058', 1.4)
        M['brass'] = principled('cbrass', hexc('#C8923A'), rough=0.3, metal=1.0)
        M['copper'] = principled('ccopper', hexc('#B4643C'), rough=0.35, metal=1.0)
        M['dark'] = principled('cdark', hexc('#1A2A2A'), rough=0.6, metal=0.5)
        M['water'] = principled('cwater', hexc('#0A1A1E'), rough=0.02, ior=1.33)
        M['red'] = emission('credlamp', (1.0, 0.1, 0.05), 25.0)
        M['sign'] = emission('csign', (0.4, 1.0, 0.7), 8.0)
        M['door'] = principled('cdoor', hexc('#5B3424'), rough=0.45, coat=0.3)
        L = 16
        prim('cube', 'c_floor', (0, 0, -0.05), scale=(L, 1.4, 0.05), mat=M['grate'], coll=co)
        # Pfützen
        for k, x in enumerate((-6, -1, 3.5, 8)):
            prim('cyl', 'c_puddle', (x, 0.2 * (-1) ** k, 0.003), scale=(1.2, 0.6, 0.003), mat=M['water'], coll=co)
        prim('cube', 'c_ceil', (0, 0, 2.85), scale=(L, 1.4, 0.05), mat=M['dark'], coll=co)
        for s in (-1, 1):
            prim('cube', f'c_wall{s}', (0, s * 1.35, 1.4), scale=(L, 0.05, 1.45), mat=M['panel'], coll=co)
            # Rohre
            tube(f'c_pipe{s}a', [(-L, s * 1.15, 2.55), (L, s * 1.15, 2.55)], 0.07, 14, M['copper'], co)
            tube(f'c_pipe{s}b', [(-L, s * 1.2, 2.35), (L, s * 1.2, 2.35)], 0.045, 12, M['brass'], co)
            tube(f'c_pipe{s}c', [(-L, s * 1.22, 0.25), (L, s * 1.22, 0.25)], 0.05, 12, M['dark'], co)
            for x in range(-L + 1, L, 2):
                prim('cyl', 'c_clamp', (x, s * 1.15, 2.55), rot=(0, R(90), 0), scale=(0.09, 0.09, 0.04), mat=M['brass'], coll=co)
                prim('cube', 'c_rib', (x, s * 1.3, 1.4), scale=(0.06, 0.04, 1.45), mat=M['dark'], bevel=0.02, coll=co)
        # Rippen an der Decke + Lampen
        self.reds = []
        for k, x in enumerate(range(-L + 2, L, 4)):
            prim('cube', 'c_cb', (x, 0, 2.78), scale=(0.08, 1.35, 0.06), mat=M['dark'], coll=co)
            lp = prim('sphere', 'c_lamp', (x, 0, 2.7), scale=(0.12, 0.12, 0.08), mat=M['red'], coll=co)
            prim('torus', 'c_lampcage', (x, 0, 2.7), mat=M['brass'], R=0.13, r=0.012, seg=24, coll=co)
            l = add_light('POINT', f'c_redl{k}', (x, 0, 2.5), 120, (1.0, 0.12, 0.06), 0.15, coll=co)
            self.reds.append(l)
        # Türen mit Nummern
        for k, x in enumerate(range(-L + 3, L - 3, 5)):
            for s in (-1, 1):
                p = empty('c_dp', (x, s * 1.29, 0), (0, 0, R(180) if s > 0 else 0), coll=co)
                prim('cube', 'c_dleaf', (0, 0, 1.0), scale=(0.45, 0.04, 1.0), mat=M['door'], bevel=0.02, parent=p, coll=co)
                prim('cube', 'c_dfr', (0, 0.02, 1.02), scale=(0.52, 0.03, 1.06), mat=M['brass'], bevel=0.02, parent=p, coll=co)
                prim('sphere', 'c_knob', (0.33, -0.07, 1.0), scale=(0.04,) * 3, mat=M['brass'], parent=p, coll=co)
                num = f'-147-{k * 2 + (s > 0) + 1:02d}'
                t = text_obj('c_dn', num, 0.09, M['brass'], extrude=0.004, coll=co); t.parent = p
                t.location = (0, -0.05, 1.65); t.rotation_euler = (R(90), 0, 0)
        # Aufzugtür am Ende
        ex = L - 0.3
        p = empty('c_lift', (ex, 0, 0), (0, 0, R(90)), coll=co)
        prim('cube', 'c_lfr', (0, 0, 1.25), scale=(0.95, 0.1, 1.3), mat=M['brass'], bevel=0.03, parent=p, coll=co)
        for s in (-1, 1):
            prim('cube', 'c_ldoor', (s * 0.4, -0.06, 1.15), scale=(0.39, 0.05, 1.12), mat=principled('liftd', hexc('#B8863A'), 0.3, 1.0, bump=(14, 0.08, 4, 'wave')), bevel=0.01, parent=p, coll=co)
        prim('cube', 'c_lsign', (0, -0.11, 2.45), scale=(0.5, 0.01, 0.1), mat=M['dark'], parent=p, coll=co)
        t = text_obj('c_lst', 'AUFZUG  ▼', 0.11, M['sign'], coll=co); t.parent = p; t.location = (0, -0.125, 2.45); t.rotation_euler = (R(90), 0, 0)
        add_light('POINT', 'c_signl', (ex - 0.5, 0, 2.4), 15, (0.4, 1.0, 0.7), 0.2, coll=co)
        prim('cube', 'c_endwall', (L + 0.1, 0, 1.4), scale=(0.05, 1.4, 1.45), mat=M['panel'], coll=co)
        prim('cube', 'c_startwall', (-L - 0.1, 0, 1.4), scale=(0.05, 1.4, 1.45), mat=M['panel'], coll=co)
        # Wasser tropft: Tropfen-Objekte
        self.drops = []
        wm = principled('drop', hexc('#BFE8FF'), rough=0.0, trans=1.0, ior=1.33)
        for k in range(10):
            d = prim('sphere', 'c_drop', (0, 0, -5), scale=(0.012, 0.012, 0.02), mat=wm, seg=10, coll=co)
            self.drops.append((d, rnd(k).uniform(-12, 12), rnd(k + 50).uniform(-0.8, 0.8), rnd(k + 9).uniform(0, 1)))

    def update(self, t):
        for k, l in enumerate(self.reds):
            l.data.energy = 60 + 90 * (0.5 + 0.5 * math.sin(t * 6 + k * 0.6))
        for d, x, y, ph in self.drops:
            u = (t * 1.2 + ph) % 1.0
            d.location = (x, y, 2.75 - u * u * 2.75 * 1.0)


class Elevator:
    """Kabine (Zylinder r=1), Tür bei -Y. Boden z=0."""

    def __init__(self, coll=None):
        co = self.coll = coll
        M = self.M = {}
        M['wood'] = principled('ewood', hexc('#6B3A22'), rough=0.35, coat=0.6, bump=(5, 0.08, 4, 'wave'))
        M['brass'] = principled('ebrass', hexc('#C8923A'), rough=0.22, metal=1.0, bump=(80, 0.03))
        M['floor'] = principled('efloor', hexc('#2A2422'), rough=0.6, bump=(40, 0.2))
        M['mirror'] = principled('emirror', hexc('#B9C4C8'), rough=0.05, metal=1.0)
        M['black'] = principled('eblk', hexc('#101010'), rough=0.3)
        M['btn'] = emission('ebtn', (1.0, 0.65, 0.3), 4.0)
        M['btnr'] = emission('ebtnr', (1.0, 0.15, 0.1), 6.0)
        self.disp_mat = emission('edisp', (1.0, 0.42, 0.08), 12.0)
        H = 2.6
        wall = lathe('e_wall', [(1.05, 0), (1.05, H)], 64, M['wood'], co, False, False)
        wall.modifiers.new('sol', 'SOLIDIFY').thickness = 0.05
        cutter = prim('cube', 'e_doorcut', (0, -1.05, 1.15), scale=(0.55, 0.3, 1.15), coll=co)
        cut(wall, cutter)
        prim('cyl', 'e_floor', (0, 0, -0.02), scale=(1.1, 1.1, 0.02), mat=M['floor'], coll=co)
        prim('cyl', 'e_ceil', (0, 0, H + 0.02), scale=(1.1, 1.1, 0.02), mat=M['wood'], coll=co)
        # Messing-Leisten
        for z in (0.05, 0.95, 1.0, 2.3, 2.55):
            prim('torus', 'e_rail', (0, 0, z), mat=M['brass'], R=1.03, r=0.018, seg=96, coll=co)
        prim('torus', 'e_handrail', (0, 0, 0.95), mat=M['brass'], R=0.96, r=0.025, seg=96, coll=co)
        # Spiegelpaneele
        for k in range(5):
            a = R(90 + 50 * (k - 2))
            prim('cube', 'e_mirror', (math.cos(a) * 1.0, math.sin(a) * 1.0, 1.65), rot=(0, 0, a), scale=(0.01, 0.28, 0.5), mat=M['mirror'], coll=co)
        # Deckenleuchte (Ring)
        self.ceil_mat = emission('eceil', (1.0, 0.8, 0.55), 2.5)
        prim('torus', 'e_ceilring', (0, 0, H - 0.03), mat=self.ceil_mat, R=0.5, r=0.04, seg=64, coll=co)
        self.ceil_light = add_light('POINT', 'e_light', (0, 0, H - 0.2), 70, (1.0, 0.8, 0.55), 0.4, coll=co)
        # Türen (zwei Hälften)
        dm = principled('edoor', hexc('#B8863A'), 0.28, 1.0, bump=(14, 0.06, 4, 'wave'))
        self.doors = []
        for s in (-1, 1):
            d = prim('cube', 'e_door', (s * 0.27, -1.02, 1.1), scale=(0.27, 0.025, 1.1), mat=dm, bevel=0.008, coll=co)
            prim('cyl', 'e_dport', (-s * 0.12, -0.03, 0.45), rot=(R(90), 0, 0), scale=(0.08, 0.08, 0.01), mat=window_glass('edg', (0.7, 0.9, 1), 0.1), parent=d, coll=co)
            self.doors.append((d, s))
        prim('cube', 'e_dframe', (0, -1.05, 2.33), scale=(0.62, 0.05, 0.05), mat=M['brass'], coll=co)
        # Anzeige über der Tür (Nixie)
        p = empty('e_disp', (0, -0.96, 2.45), coll=co)
        prim('cube', 'e_dbox', (0, 0.02, 0), scale=(0.32, 0.04, 0.09), mat=M['black'], bevel=0.01, parent=p, coll=co)
        prim('cube', 'e_dbez', (0, 0.03, 0), scale=(0.34, 0.035, 0.11), mat=M['brass'], bevel=0.015, parent=p, coll=co)
        self.disp = text_obj('e_dtxt', '-147', 0.13, self.disp_mat, coll=co)
        self.disp.parent = p; self.disp.location = (0, 0.072, -0.0); self.disp.rotation_euler = (R(90), 0, R(180))
        self.disp_light = add_light('POINT', 'e_dl', (0, -0.8, 2.35), 8, (1.0, 0.45, 0.1), 0.1, coll=co)
        # Pfeil
        arr = mesh_obj('e_arrow', [(-0.04, 0, 0.02), (0.04, 0, 0.02), (0, 0, -0.03)], [(0, 1, 2)], M['btnr'], coll=co)
        arr.parent = p; arr.location = (0.27, 0.07, 0); arr.rotation_euler = (0, 0, R(180))
        # Bedienfeld rechts neben Tür (innen)
        a = R(-90 + 42)
        bp = empty('e_panel', (math.cos(a) * 0.99, math.sin(a) * 0.99, 1.25), (0, 0, a + R(90)), coll=co)
        prim('cube', 'e_pplate', (0, 0, 0), scale=(0.11, 0.01, 0.3), mat=M['brass'], bevel=0.01, parent=bp, coll=co)
        self.buttons = []
        for i in range(6):
            for j in range(2):
                b = prim('cyl', 'e_btn', (-0.045 + j * 0.09, -0.015, 0.22 - i * 0.075), rot=(R(90), 0, 0), scale=(0.025, 0.025, 0.01),
                         mat=M['btn'] if (i, j) != (5, 1) else M['btnr'], parent=bp, coll=co)
                self.buttons.append(b)
        self.panel = bp
        # Kabinenboden Muster: Messingstern
        star = lathe('e_star', [(0, 0.001), (0.5, 0.001), (0.5, 0.0)], 8, M['brass'], co)

    def set_doors(self, k):  # 0 zu .. 1 offen
        for d, s in self.doors:
            d.location.x = s * (0.27 + 0.52 * k)


def build_facade(A, M=None):
    """Außenfassade vor der Fensterwand (y=3.5), mit weiteren leuchtenden Bullaugen."""
    from sets import Mats
    co = A.coll
    M = M or Mats()
    fac = prim('cube', 'facade', (0, 3.62, 1.6), scale=(30, 0.12, 22), mat=M.hull, coll=co)
    cutter = prim('cyl', 'facut', (0, 3.6, 1.6), rot=(R(90), 0, 0), scale=(1.15, 1.15, 0.5), seg=64, coll=co)
    cut(fac, cutter)
    prim('torus', 'fa_ring', (0, 3.78, 1.6), rot=(R(90), 0, 0), mat=M.brass, R=1.28, r=0.16, seg=96, seg2=16, coll=co)
    for k in range(20):
        a = 2 * math.pi * k / 20
        prim('sphere', 'fa_rv', (math.cos(a) * 1.55, 3.76, 1.6 + math.sin(a) * 1.55), scale=(0.06,) * 3, mat=M.brass, seg=8, coll=co)
    # weitere Fenster (emissiv) im Raster
    for i in range(-4, 5):
        for j in range(-3, 4):
            if i == 0 and j == 0:
                continue
            x, z = i * 3.3, 1.6 + j * 3.6
            prim('torus', 'fa_fr', (x, 3.76, z), rot=(R(90), 0, 0), mat=M.brass, R=0.85, r=0.13, seg=28, seg2=10, coll=co)
            g = prim('cyl', 'fa_gl', (x, 3.72, z), rot=(R(90), 0, 0), scale=(0.8, 0.8, 0.02), mat=M.winobj, seg=28, coll=co)
    # Gesimse
    for j in range(-3, 4):
        prim('cube', 'fa_trim', (0, 3.78, 1.6 + j * 3.6 - 1.8), scale=(30, 0.12, 0.12), mat=M.hull_dark, bevel=0.03, coll=co)
    # Schild -147
    prim('cube', 'fa_plate', (0, 3.8, 3.35), scale=(0.9, 0.06, 0.32), mat=M.hull_dark, bevel=0.03, coll=co)
    t = text_obj('fa_num', '-147', 0.42, M.neon, extrude=0.02, coll=co)
    t.location = (0, 3.87, 3.35); t.rotation_euler = (R(90), 0, R(180))
    # Seepocken + Algen
    rg = rnd(12)
    for k in range(260):
        x = rg.uniform(-14, 14); z = rg.uniform(-10, 12)
        if (x * x + (z - 1.6) ** 2) < 2.2:
            continue
        s = rg.uniform(0.04, 0.16)
        prim('sphere', 'fa_barn', (x, 3.74, z), scale=(s, s * 0.6, s), mat=M.barn, seg=8, coll=co)
    for k in range(8):
        x = rg.uniform(-6, 6)
        pts = [(x + 0.2 * math.sin(j), 3.85 + 0.1 * j, -6 + j * 0.9) for j in range(10)]
        tube('fa_kelp', pts, 0.05, 6, M.kelp, co)
    return M


def crack_mesh(coll, center, radius, grow, seed=5, mat=None, plane_y=3.28):
    """Verzweigter Riss im Glas (Linien als dünne Röhren), grow 0..1."""
    rg = rnd(seed)
    obs = []
    if grow <= 0:
        return obs
    mat = mat or emission('crackm', (0.85, 0.95, 1.0), 2.5)
    branches = []
    def walk(p, ang, length, depth, t0):
        pts = [p]
        steps = 7
        for k in range(steps):
            ang += rg.uniform(-0.5, 0.5)
            p = (p[0] + math.cos(ang) * length / steps, p[1] + math.sin(ang) * length / steps)
            pts.append(p)
        branches.append((pts, t0, depth))
        if depth < 3:
            for _ in range(rg.randint(1, 2)):
                k = rg.randint(2, steps - 1)
                walk(pts[k], ang + rg.choice([-1, 1]) * rg.uniform(0.5, 1.1), length * 0.55, depth + 1, t0 + 0.3 * (k / steps) + 0.1)
    for i in range(7):
        a = 2 * math.pi * i / 7 + rg.uniform(-0.3, 0.3)
        walk((0.0, 0.0), a, radius * rg.uniform(0.6, 1.0), 0, rg.uniform(0, 0.15))
    for bi, (pts, t0, depth) in enumerate(branches):
        k = (grow - t0) / 0.45
        if k <= 0:
            continue
        n = max(2, int(len(pts) * min(1, k)))
        P = [(center[0] + x, plane_y, center[1] + z) for x, z in pts[:n]]
        obs.append(tube(f'crack{bi}', P, 0.0018 / (1 + 0.6 * depth), 5, mat, coll))
    # Einschlagstern
    obs.append(prim('sphere', 'impact', (center[0], plane_y, center[1]), scale=(0.035, 0.005, 0.035), mat=mat, coll=coll))
    return obs
