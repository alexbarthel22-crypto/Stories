# Folge 13 – fotorealistische Fassung in Blender/Cycles.
# Aufruf:  bpyenv/bin/python blender/szene.py <ausgabeordner> <von> <bis> [schritt] [--samples N] [--res 720]
# Rendert die 3D-Bilder (ohne Schrift); die Einblendungen kommen danach im Browser (src/page.html?bg=...) darüber.
import sys, os, math, time, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, bmesh
from mathutils import Vector, Matrix, Euler, Color, noise
from lib_b import *
import creatures_b as CR

FPS = 30
SHOTS = [
    dict(id='surface', t0=0, t1=5, d0=0, d1=0), dict(id='panel', t0=5, t1=9, d0=0, d1=0),
    dict(id='shallow', t0=9, t1=15, d0=0, d1=24), dict(id='whale', t0=15, t1=21, d0=300, d1=312),
    dict(id='squid', t0=21, t1=27, d0=690, d1=700), dict(id='dark', t0=27, t1=33.5, d0=1450, d1=1462),
    dict(id='vent', t0=33.5, t1=39.5, d0=2790, d1=2800), dict(id='crack', t0=39.5, t1=46.5, d0=6000, d1=6012),
    dict(id='snail', t0=46.5, t1=51, d0=8326, d1=8336), dict(id='bottom', t0=51, t1=60, d0=10880, d1=10920)]
PRESS, START, NO_NET, SHADOW, WHALE_FLEE, LIGHTS_OUT = 7.9, 9.0, 11.4, 13.2, 18.6, 26.3
LURE, LIGHTS_ON, CRACK, ARRIVE, KNOCK, SUB, BOX, DELIVERED = 29.2, 31.8, 42.0, 52.0, 53.3, 54.4, 55.5, 56.2

def depth_at(T, s):
    if s['id'] == 'bottom': return min(s['d1'], s['d0'] + (s['d1'] - s['d0']) * min(1, (T - s['t0']) / (ARRIVE - s['t0'])))
    if s['id'] == 'shallow': k = max(0, (T - START) / (s['t1'] - START)); return s['d0'] + (s['d1'] - s['d0']) * k ** 1.3
    k = (T - s['t0']) / (s['t1'] - s['t0']); return s['d0'] + (s['d1'] - s['d0']) * k
def shot_at(T):
    for s in SHOTS:
        if s['t0'] <= T < s['t1']: return s
    return SHOTS[-1]

def hexc(h): h = h.lstrip('#'); return Color(tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))).from_srgb_to_scene_linear()
FOG = [(0, '#1d97b8'), (30, '#127aa1'), (150, '#0a4c78'), (330, '#062c52'), (720, '#02152a'), (1000, '#01070f'), (2500, '#000306'), (11000, '#000204')]
def fog_col(d):
    for i in range(1, len(FOG)):
        if d <= FOG[i][0]:
            a, ca = FOG[i - 1]; b, cb = FOG[i]; k = (d - a) / (b - a); x, y = hexc(ca), hexc(cb)
            return Vector((lerp(x.r, y.r, k), lerp(x.g, y.g, k), lerp(x.b, y.b, k)))
    c = hexc(FOG[-1][1]); return Vector((c.r, c.g, c.b))

# ---------------------------------------------------------------- Grundeinstellungen
def setup(samples, res):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene; sc.render.engine = 'CYCLES'; cy = sc.cycles
    cy.device = 'CPU'; cy.samples = samples; cy.use_adaptive_sampling = True; cy.adaptive_threshold = 0.02
    cy.use_denoising = True; cy.denoiser = 'OPENIMAGEDENOISE'
    try: cy.denoising_prefilter = 'ACCURATE'
    except Exception: pass
    cy.max_bounces = 6; cy.diffuse_bounces = 2; cy.glossy_bounces = 3; cy.transmission_bounces = 6; cy.volume_bounces = 1; cy.transparent_max_bounces = 12
    cy.caustics_reflective = False; cy.caustics_refractive = False; cy.blur_glossy = 1.0
    cy.volume_step_rate = 2.0; cy.volume_max_steps = 256
    sc.render.resolution_x = res; sc.render.resolution_y = res * 16 // 9; sc.render.resolution_percentage = 100
    sc.render.threads_mode = 'FIXED'; sc.render.threads = 4
    sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_mode = 'RGB'
    sc.view_settings.view_transform = 'AgX'
    try: sc.view_settings.look = 'AgX - Medium High Contrast'
    except Exception: pass
    sc.render.film_transparent = False
    coll('SEA'); coll('SURF'); coll('LIB').hide_render = True
    cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); sc.collection.objects.link(cam); sc.camera = cam
    cam.data.sensor_fit = 'VERTICAL'; cam.data.sensor_height = 24; cam.data.clip_start = 0.01; cam.data.clip_end = 2000
    cam.data.dof.use_dof = True
    return sc, cam

def set_cam(cam, cp3, lk3, fov, focus=None, fstop=2.8):
    p, l = P(*cp3), P(*lk3); cam.location = p
    cam.rotation_euler = (l - p).to_track_quat('-Z', 'Y').to_euler()
    cam.data.lens = 12 / math.tan(math.radians(fov) / 2)
    cam.data.dof.focus_distance = focus if focus else (l - p).length
    cam.data.dof.aperture_fstop = fstop

# ---------------------------------------------------------------- Materialien (Umgebung)
def mat_steel():
    m, nb, out = new_mat('steel'); o = coords(nb, 'Object')
    vm = nb.n('ShaderNodeVectorMath', operation='MULTIPLY'); nb.l(o, vm.inputs[0]); vm.inputs[1].default_value = (3, 3, 260)
    n = noise_tex(nb, vm.outputs[0], 4, 3)
    r = mr(nb, n.outputs['Fac'], 0.3, 0.7, 0.18, 0.3)
    bsdf(nb, out, (0.62, 0.63, 0.64), rough=r, metal=1.0, Anisotropic=0.5)
    return m

def mat_floor():
    m, nb, out = new_mat('cabfloor'); o = coords(nb, 'Object')
    br = nb.n('ShaderNodeTexBrick'); nb.l(o, br.inputs['Vector']); br.inputs['Scale'].default_value = 1.6; br.inputs['Mortar Size'].default_value = 0.004
    br.inputs['Color1'].default_value = (0.05, 0.05, 0.052, 1); br.inputs['Color2'].default_value = (0.065, 0.064, 0.066, 1); br.inputs['Mortar'].default_value = (0.01, 0.01, 0.01, 1)
    br.offset = 0.0
    vor = nb.n('ShaderNodeTexVoronoi'); nb.l(o, vor.inputs['Vector']); vor.inputs['Scale'].default_value = 90
    col = nb.mix(nb.math('MULTIPLY', nb.math('LESS_THAN', vor.outputs['Distance'], 0.12), 0.5), br.outputs['Color'], (0.35, 0.34, 0.33, 1))
    sm = noise_tex(nb, o, 6, 4)
    bsdf(nb, out, col, rough=mr(nb, sm.outputs['Fac'], 0.3, 0.7, 0.12, 0.35), normal=bump(nb, br.outputs['Fac'], 0.3, 0.002))
    return m

def mat_facade(name='facade'):
    m, nb, out = new_mat(name); o = coords(nb, 'Object'); x, y, z = sep(nb, o)
    scroll = nb.n('ShaderNodeValue', label='scroll'); scroll.name = 'scroll'; scroll.outputs[0].default_value = 0
    lit = nb.n('ShaderNodeValue'); lit.name = 'lit'; lit.outputs[0].default_value = 1.0
    hz = nb.math('ADD', y, x)  # waagerecht (eine der beiden Achsen ist auf jeder Seite konstant)
    u = nb.math('DIVIDE', hz, 3.25); v = nb.math('DIVIDE', nb.math('ADD', z, scroll.outputs[0]), 3.0)
    fu = nb.math('FRACT', u); fv = nb.math('FRACT', v)
    win = nb.math('MULTIPLY', nb.math('MULTIPLY', nb.math('GREATER_THAN', fu, 0.1), nb.math('LESS_THAN', fu, 0.9)), nb.math('MULTIPLY', nb.math('GREATER_THAN', fv, 0.2), nb.math('LESS_THAN', fv, 0.86)))
    mull = nb.math('LESS_THAN', nb.math('ABSOLUTE', nb.math('SUBTRACT', fu, 0.5)), 0.012)
    win = nb.math('MULTIPLY', win, nb.math('SUBTRACT', 1.0, mull))
    cell = nb.math('ADD', nb.math('FLOOR', u), nb.math('MULTIPLY', nb.math('FLOOR', v), 37.13))
    wn = nb.n('ShaderNodeTexWhiteNoise', noise_dimensions='1D'); nb.l(cell, wn.inputs['W'])
    r = wn.outputs['Value']
    on = nb.math('MULTIPLY', nb.math('LESS_THAN', r, 0.42), win)
    wcol = nb.mix(nb.math('LESS_THAN', r, 0.3), (0.55, 0.75, 1.0, 1), (1.0, 0.62, 0.32, 1))
    # Vorhänge / Innenleben: leichte Helligkeitsvariation im Fenster
    grad = mr(nb, fv, 0.2, 0.86, 1.0, 0.55, False)
    estr = nb.math('MULTIPLY', nb.math('MULTIPLY', on, nb.math('MULTIPLY', grad, nb.math('ADD', 2.5, nb.math('MULTIPLY', r, 5.0)))), lit.outputs[0])
    foul = noise_tex(nb, o, 0.45, 6, 0.6)
    conc = nb.mix(mr(nb, foul.outputs['Fac'], 0.45, 0.62), (0.3, 0.31, 0.3, 1), (0.06, 0.075, 0.05, 1))
    col = nb.mix(win, conc, (0.008, 0.01, 0.012, 1))
    gr = noise_tex(nb, o, 25, 6)
    p = bsdf(nb, out, col, rough=nb.mixf(win, 0.85, 0.05), normal=bump(nb, nb.math('ADD', gr.outputs['Fac'], nb.math('MULTIPLY', win, -0.6)), 0.4, 0.02))
    nb.l(wcol, p.inputs['Emission Color']); nb.l(estr, p.inputs['Emission Strength'])
    return m

def mat_water_volume(name='water'):
    m, nb, out = new_mat(name)
    ab = nb.n('ShaderNodeVolumeAbsorption'); ab.name = 'abs'; ab.inputs['Color'].default_value = (0.12, 0.55, 0.7, 1); ab.inputs['Density'].default_value = 0.05
    sc = nb.n('ShaderNodeVolumeScatter'); sc.name = 'sca'; sc.inputs['Color'].default_value = (0.5, 0.82, 0.92, 1); sc.inputs['Density'].default_value = 0.025; sc.inputs['Anisotropy'].default_value = 0.6
    ad = nb.n('ShaderNodeAddShader'); nb.l(ab.outputs[0], ad.inputs[0]); nb.l(sc.outputs[0], ad.inputs[1])
    nb.l(ad.outputs[0], out.inputs['Volume']); return m

def mat_rock(name, base=(0.05, 0.045, 0.04), sed=(0.32, 0.29, 0.25), sed_amt=1.0, scale=1.0):
    m, nb, out = new_mat(name); o = coords(nb, 'Object')
    n1 = noise_tex(nb, o, 0.8 * scale, 8, 0.65)
    vor = nb.n('ShaderNodeTexVoronoi'); nb.l(o, vor.inputs['Vector']); vor.inputs['Scale'].default_value = 3 * scale
    h = nb.math('ADD', nb.math('MULTIPLY', n1.outputs['Fac'], 1.0), nb.math('MULTIPLY', vor.outputs['Distance'], 0.5))
    fine = noise_tex(nb, o, 30 * scale, 6)
    h = nb.math('ADD', h, nb.math('MULTIPLY', fine.outputs['Fac'], 0.25))
    col = nb.mix(n1.outputs['Fac'], base, tuple(c * 1.9 for c in base) + (1,))
    nz = sep(nb, nb.n('ShaderNodeNewGeometry').outputs['Normal'])[2]
    sd = nb.math('MULTIPLY', mr(nb, nz, 0.35, 0.8), sed_amt)
    sd = nb.math('MULTIPLY', sd, mr(nb, noise_tex(nb, o, 2.5 * scale, 4).outputs['Fac'], 0.35, 0.6, 0.4, 1.0))
    col = nb.mix(sd, col, (*sed, 1))
    bsdf(nb, out, col, rough=0.92, normal=bump(nb, h, 0.6, 0.15))
    return m

def mat_sediment():
    m, nb, out = new_mat('sediment'); o = coords(nb, 'Object')
    n1 = noise_tex(nb, o, 0.3, 6); n2 = noise_tex(nb, o, 9, 8, 0.7)
    col = nb.mix(n1.outputs['Fac'], (0.2, 0.19, 0.165, 1), (0.3, 0.28, 0.245, 1))
    vor = nb.n('ShaderNodeTexVoronoi'); nb.l(o, vor.inputs['Vector']); vor.inputs['Scale'].default_value = 1.2
    pits = nb.math('LESS_THAN', vor.outputs['Distance'], 0.05)
    col = nb.mix(nb.math('MULTIPLY', pits, 0.6), col, (0.08, 0.075, 0.065, 1))
    wv = nb.n('ShaderNodeTexWave', wave_type='RINGS'); nb.l(o, wv.inputs['Vector']); wv.inputs['Scale'].default_value = 0.4; wv.inputs['Distortion'].default_value = 12; wv.inputs['Detail'].default_value = 3
    h = nb.math('ADD', n2.outputs['Fac'], nb.math('ADD', nb.math('MULTIPLY', wv.outputs['Fac'], 0.25), nb.math('MULTIPLY', pits, -0.8)))
    bsdf(nb, out, col, rough=1.0, normal=bump(nb, h, 0.5, 0.05))
    return m

# ---------------------------------------------------------------- Kabine
def build_cabin(R):
    steel = mat_steel(); dark = principled('framedark', (0.025, 0.028, 0.03), 0.35, 0.7)
    chrome = principled('chrome', (0.9, 0.9, 0.9), 0.08, 1.0)
    white = principled('ceiling', (0.035, 0.036, 0.038), 0.6)
    glass = glass_mat('cabglass', (0.93, 0.98, 0.97), 0.0, 1.5)
    box('cab_floor', -1.4, 1.4, -0.1, 0.0, -1.35, 1.35, mat_floor())
    box('cab_ceiling', -1.4, 1.4, 2.75, 2.85, -1.35, 1.35, white)
    lamp = emission('lamp', (1.0, 0.9, 0.76), 3.0)
    lp = box('cab_lamp', -0.5, 0.5, 2.74, 2.75, 0.2, 0.45, lamp); R['lamp'] = lamp
    R['inlight'] = light('cab_light', 'AREA', P(0, 2.73, 0), 160, (1.0, 0.86, 0.7), shape='RECTANGLE', size=1.7, size_y=1.2)
    R['inlight'].rotation_euler = (0, 0, 0); R['inlight'].visible_camera = False; R['inlight'].visible_glossy = False; R['inlight'].visible_transmission = False
    box('cab_glass_front', -1.35, 1.35, 0.0, 2.75, -1.33, -1.30, glass)
    box('cab_glass_right', 1.35, 1.38, 0.0, 2.75, -1.3, 1.3, glass)
    for x, z in ((-1.35, -1.3), (1.35, -1.3), (1.35, 1.3)): box('cab_post', x - 0.045, x + 0.045, -0.02, 2.82, z - 0.045, z + 0.045, dark, bevel=0.01)
    box('cab_sill_f', -1.4, 1.4, 0.0, 0.14, -1.34, -1.26, dark, bevel=0.01); box('cab_head_f', -1.4, 1.4, 2.66, 2.78, -1.34, -1.26, dark, bevel=0.01)
    box('cab_sill_r', 1.31, 1.39, 0.0, 0.12, -1.35, 1.35, dark, bevel=0.01); box('cab_head_r', 1.31, 1.39, 2.66, 2.78, -1.35, 1.35, dark, bevel=0.01)
    box('cab_wall_l', -1.42, -1.36, -0.02, 2.82, -1.35, 1.35, steel)
    box('cab_wall_b', -1.4, 1.4, -0.02, 2.82, 1.33, 1.39, steel)
    for x0, x1 in ((-0.62, -0.005), (0.005, 0.62)): box('cab_door', x0, x1, 0.0, 2.2, 1.315, 1.33, principled('door', (0.55, 0.56, 0.57), 0.22, 1.0))
    box('cab_doorframe', -0.68, 0.68, 2.2, 2.28, 1.31, 1.33, dark)
    for (a, b, c, d) in (((0, 0.95, -1.18), 2.5, 'x', 0.022), ((1.23, 0.95, 0), 2.4, 'z', 0.022)):
        m = Matrix.Translation(a) @ (Euler((0, math.pi / 2, 0)) if c == 'x' else Euler((0, 0, 0))).to_matrix().to_4x4()
        mesh_obj('cab_rail', cyl_bm(d, d, b, 24, mat=m), chrome)
    # Bedienfeld
    pm, nb, out = new_mat('panel')
    t0 = nb.n('ShaderNodeTexImage'); t0.image = bpy.data.images.load(os.path.join(CR.TEX, 'panel_off.png'))
    t1 = nb.n('ShaderNodeTexImage'); t1.image = bpy.data.images.load(os.path.join(CR.TEX, 'panel_on.png'))
    e0 = nb.n('ShaderNodeTexImage'); e0.image = bpy.data.images.load(os.path.join(CR.TEX, 'panel_off_emit.png')); e0.image.colorspace_settings.name = 'Non-Color'
    e1 = nb.n('ShaderNodeTexImage'); e1.image = bpy.data.images.load(os.path.join(CR.TEX, 'panel_on_emit.png')); e1.image.colorspace_settings.name = 'Non-Color'
    pr = nb.n('ShaderNodeValue'); pr.name = 'pressed'; pr.outputs[0].default_value = 0
    col = nb.mix(pr.outputs[0], t0.outputs['Color'], t1.outputs['Color'])
    em = nb.mixf(pr.outputs[0], e0.outputs['Color'], e1.outputs['Color'])
    p = bsdf(nb, out, col, rough=0.3, metal=0.6)
    p.inputs['Emission Color'].default_value = (1.0, 0.55, 0.15, 1); nb.l(nb.math('MULTIPLY', em, 4.0), p.inputs['Emission Strength'])
    bm = bmesh.new(); vs = [bm.verts.new(Vector(c)) for c in ((-1.355, 0.795, -0.53), (-1.355, 0.795, -0.87), (-1.355, 1.645, -0.87), (-1.355, 1.645, -0.53))]
    f = bm.faces.new(vs); uvl = bm.loops.layers.uv.new()
    for lo, uv in zip(f.loops, ((0, 0), (1, 0), (1, 1), (0, 1))): lo[uvl].uv = uv
    po = mesh_obj('panel', bm, pm, smooth_shade=False); R['panelmat'] = pm
    box('panel_frame', -1.362, -1.357, 0.775, 1.665, -0.89, -0.51, dark)
    # Außenscheinwerfer
    R['floods'] = []
    for x, tx in ((-0.9, -1.5), (0.9, 2.8)):
        box('flood_h', x - 0.14, x + 0.14, 2.88, 3.02, -1.56, -1.36, dark, bevel=0.01)
        s = light('flood', 'SPOT', P(x, 2.95, -1.58), 0, (0.86, 0.93, 1.0), spot_size=math.radians(62), spot_blend=0.45, shadow_soft_size=0.08)
        s['tgt'] = (tx, -3.5, -15); aim(s, P(tx, -3.5, -15)); R['floods'].append(s)
    R['nearL'] = light('nearL', 'POINT', P(0.7, 2.95, -1.8), 0, (0.85, 0.92, 1.0), shadow_soft_size=0.1)

def build_tower(R):
    R['facade'] = mat_facade()
    box('tower', -14.6, -1.6, -70, 70, -3, 10, R['facade'])
    rail = principled('rail', (0.2, 0.22, 0.23), 0.4, 0.8)
    for z in (-1.05, 1.05): box('guide', -1.58, -1.43, -70, 70, z - 0.08, z + 0.08, rail)
    bm = bmesh.new()
    for k in range(-14, 15):
        for z in (-1.05, 1.05): box_bm(-1.6, -1.4, k * 3.5 - 0.06, k * 3.5 + 0.06, z - 0.25, z + 0.25, bm)
    R['brk'] = mesh_obj('brackets', bm, rail, smooth_shade=False)

def build_water(R):
    wm = mat_water_volume(); R['water'] = wm
    bm = box_bm(-70, 70, -70, 1, -110, 45)
    dom = mesh_obj('domain', bm, wm, smooth_shade=False); R['domain'] = dom
    hb = box_bm(-1.40, 1.385, -0.12, 2.86, -1.335, 1.37)
    hole = mesh_obj('hole', hb, None, smooth_shade=False); hole.hide_render = True; hole.hide_viewport = False
    md = dom.modifiers.new('cut', 'BOOLEAN'); md.operation = 'DIFFERENCE'; md.object = hole; md.solver = 'EXACT'
    R['dom_top'] = [i for i, v in enumerate(dom.data.vertices) if v.co.z > 0.5]
    # Lichtmuster der Wellen (Kaustik-Schablone, wirft nur Schatten)
    gm, nb, out = new_mat('gobo')
    o = coords(nb, 'Object'); tv = nb.n('ShaderNodeValue'); tv.name = 'T'
    vor = nb.n('ShaderNodeTexVoronoi', voronoi_dimensions='4D', feature='DISTANCE_TO_EDGE'); nb.l(o, vor.inputs['Vector']); nb.l(nb.math('MULTIPLY', tv.outputs[0], 0.35), vor.inputs['W'])
    vor.inputs['Scale'].default_value = 0.55
    lines = mr(nb, vor.outputs['Distance'], 0.0, 0.07, 1.0, 0.0)
    pas = nb.math('ADD', 0.08, nb.math('MULTIPLY', lines, 0.92))
    tr = nb.n('ShaderNodeBsdfTransparent'); dif = nb.n('ShaderNodeBsdfDiffuse'); dif.inputs[0].default_value = (0, 0, 0, 1)
    mx = nb.n('ShaderNodeMixShader'); nb.l(pas, mx.inputs[0]); nb.l(dif.outputs[0], mx.inputs[1]); nb.l(tr.outputs[0], mx.inputs[2]); nb.l(mx.outputs[0], out.inputs['Surface'])
    gb = bmesh.new(); bmesh.ops.create_grid(gb, x_segments=1, y_segments=1, size=60, matrix=Euler((math.pi / 2, 0, 0)).to_matrix().to_4x4())
    gob = mesh_obj('gobo', gb, gm, smooth_shade=False); ray_vis(gob, camera=False, diffuse=False, glossy=False, transmission=False, scatter=False, shadow=True)
    R['gobo'] = gob; R['gobomat'] = gm
    R['sun'] = light('sun', 'SUN', (0, 0, 50), 4.0, (1.0, 0.97, 0.9), angle=math.radians(1.0))
    R['sun'].rotation_euler = Euler((math.radians(14), math.radians(-8), 0))

def build_particles(R):
    # Meeresschnee: periodisch in 40 m, drei Lagen übereinander
    snow_m = principled('snow', (0.75, 0.75, 0.72), 0.6, Transmission_Weight=0.35, Subsurface_Weight=0.2)
    bm = bmesh.new(); r = random.Random(9); base = []
    for i in range(1500): base.append((lerp(-1.3, 16, r.random()), r.random() * 40, lerp(-28, -1.42, r.random()), 0.003 + r.random() ** 3 * 0.006))
    for i in range(350): base.append((lerp(1.42, 13, r.random()), r.random() * 40, lerp(-1.3, 7, r.random()), 0.003 + r.random() ** 3 * 0.006))
    for i in range(900): base.append((lerp(-1.3, 2.5, r.random()), r.random() * 40, lerp(-4.5, -1.4, r.random()), 0.002 + r.random() ** 2 * 0.004))
    for off in (-40, 0, 40):
        for x, y, z, s in base:
            if z > -1.38 and x < 1.4: continue
            bmesh.ops.create_icosphere(bm, subdivisions=1, radius=s, matrix=Matrix.Translation((x, y + off - 20, z)) @ Matrix.Diagonal((1, 1 + r.random(), 1, 1)))
    R['snow'] = mesh_obj('snow', bm, snow_m); R['snowmat'] = snow_m
    # Biolumineszenz: Lichtpünktchen mit eigenem Blinktakt (Attribut)
    bmm, nb, out = new_mat('bio')
    at = nb.n('ShaderNodeAttribute'); at.attribute_name = 'ph'; at2 = nb.n('ShaderNodeAttribute'); at2.attribute_name = 'col'
    tv = nb.n('ShaderNodeValue'); tv.name = 'T'; amt = nb.n('ShaderNodeValue'); amt.name = 'amt'
    xx = sep(nb, at.outputs['Vector'])
    s = nb.math('SINE', nb.math('ADD', nb.math('MULTIPLY', tv.outputs[0], nb.math('ADD', 0.7, nb.math('MULTIPLY', xx[1], 2.5))), nb.math('MULTIPLY', xx[0], 18.0)))
    b = nb.math('POWER', nb.math('MAXIMUM', s, 0.0), 3.0)
    e = nb.n('ShaderNodeEmission'); nb.l(at2.outputs['Color'], e.inputs['Color']); nb.l(nb.math('MULTIPLY', nb.math('MULTIPLY', b, amt.outputs[0]), 30.0), e.inputs['Strength'])
    nb.l(e.outputs[0], out.inputs['Surface'])
    bm = bmesh.new(); r = random.Random(17); recs = []
    ph = bm.verts.layers.float_vector.new('ph'); cl = bm.verts.layers.float_color.new('col')
    for i in range(700):
        x, y, z = lerp(-1.3, 10, r.random()), lerp(-4, 7, r.random()), lerp(-18, -1.5, r.random())
        k = r.random(); col = (0.25, 0.7, 1.0) if k < 0.7 else ((0.3, 1.0, 0.65) if k < 0.85 else (0.6, 0.5, 1.0))
        res = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=0.0025 + r.random() * 0.004, matrix=Matrix.Translation((x, y, z)))
        p = (r.random(), r.random(), 0)
        for v in res['verts']: v[ph] = p; v[cl] = (*col, 1)
    R['bio'] = mesh_obj('bio', bm, bmm); R['biomat'] = bmm

def build_school(R):
    fm, fin = CR.fish_mats(); variants = [CR.fish_variant(i, fm, fin, i / 6 * math.tau) for i in range(6)]
    r = random.Random(12); R['fish'] = []
    for i in range(420):
        ob = bpy.data.objects.new('fish', variants[i % 6]); coll('SEA').objects.link(ob)
        R['fish'].append((ob, dict(R=1.5 + r.random() * 3.4, y=(r.random() - 0.5) * 3.6, ph=r.random() * 6.28, sp=0.55 + r.random() * 0.25, wob=r.random() * 6, s=0.8 + r.random() * 0.5, v=i % 6)))
    R['fishvar'] = variants

def update_school(R, T, center, scare):
    for ob, f in R['fish']:
        a = f['ph'] + T * f['sp'] * (1 + scare * 1.6); Rr = f['R'] * (1 - scare * 0.45)
        p = (center.x + math.cos(a) * Rr, center.y + f['y'] * (1 - scare * 0.3) + math.sin(T * 1.3 + f['wob']) * 0.15 - scare * 1.5, center.z + math.sin(a) * Rr * 0.8 - scare * 2.5)
        yaw = -a - math.pi
        ob.matrix_basis = M3(p, (0, yaw, 0.15 * math.sin(T * 2 + f['wob'])), f['s'])
        ob.data = R['fishvar'][(f['v'] + int(T * 14 * (1 + scare))) % 6]

# ---------------------------------------------------------------- Schwarze Raucher, Felsen, Boden
def rock_bm(seed, detail=4, amp=0.25):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=detail, radius=1.0); r = random.Random(seed); o = Vector((r.random() * 50, r.random() * 50, r.random() * 50))
    for v in bm.verts:
        n = noise.fractal(v.co * 1.3 + o, 0.6, 2.2, 6); v.co *= 1 + amp * n
    return bm

def build_vent(R):
    grp = bpy.data.objects.new('vent', None); coll('SEA').objects.link(grp); R['vent'] = grp; parts = []
    basalt = mat_rock('basalt', (0.035, 0.03, 0.028), (0.22, 0.2, 0.17), 0.8, 1.2)
    lb = rock_bm(3, 5, 0.3); bmesh.ops.transform(lb, matrix=Matrix.Translation((4, -9, -17)) @ Matrix.Diagonal((11, 5, 8, 1)), verts=lb.verts)
    parts.append(mesh_obj('ledge', lb, basalt))
    # Schornsteine: Mineralkrusten (schwarz, ocker, schwefelgelb)
    cm, nb, out = new_mat('chimney'); o = coords(nb, 'Object')
    n1 = noise_tex(nb, o, 1.5, 6, 0.6); n2 = noise_tex(nb, o, 6, 4)
    c1 = nb.ramp(n1.outputs['Fac'], [(0.0, (0.012, 0.01, 0.009, 1)), (0.48, (0.03, 0.024, 0.02, 1)), (0.6, (0.16, 0.07, 0.02, 1)), (0.7, (0.3, 0.16, 0.05, 1)), (0.78, (0.03, 0.025, 0.02, 1))])
    yel = nb.math('MULTIPLY', mr(nb, n2.outputs['Fac'], 0.62, 0.72), mr(nb, sep(nb, o)[2], 0.3, 0.9))
    col = nb.mix(yel, c1, (0.45, 0.36, 0.08, 1))
    vor = nb.n('ShaderNodeTexVoronoi'); nb.l(o, vor.inputs['Vector']); vor.inputs['Scale'].default_value = 7
    h = nb.math('ADD', n1.outputs['Fac'], nb.math('MULTIPLY', vor.outputs['Distance'], 0.8))
    bsdf(nb, out, col, rough=0.85, normal=bump(nb, h, 0.8, 0.08))
    R['chimneys'] = []
    smoke_m, nb, out = new_mat('smoke'); o = coords(nb, 'Object'); tv = nb.n('ShaderNodeValue'); tv.name = 'T'
    x, y, z = sep(nb, o)
    rad = nb.math('SQRT', nb.math('ADD', nb.math('MULTIPLY', x, x), nb.math('MULTIPLY', y, y)))
    width = nb.math('ADD', 0.18, nb.math('MULTIPLY', z, 0.17))
    fall = mr(nb, nb.math('DIVIDE', rad, width), 0.4, 1.0, 1.0, 0.0)
    vm = nb.n('ShaderNodeCombineXYZ'); nb.l(x, vm.inputs[0]); nb.l(y, vm.inputs[1]); nb.l(nb.math('SUBTRACT', z, nb.math('MULTIPLY', tv.outputs[0], 1.6)), vm.inputs[2])
    nz = noise_tex(nb, vm.outputs[0], 1.8, 6, 0.6, dist=0.6)
    den = nb.math('MULTIPLY', fall, mr(nb, nz.outputs['Fac'], 0.38, 0.7, 0.0, 1.0))
    den = nb.math('MULTIPLY', den, mr(nb, z, 0.0, 0.4))
    den = nb.math('MULTIPLY', den, mr(nb, z, 9.0, 4.0))
    pv = nb.n('ShaderNodeVolumePrincipled'); pv.inputs['Color'].default_value = (0.09, 0.075, 0.06, 1); pv.inputs['Absorption Color'].default_value = (0.02, 0.02, 0.02, 1)
    nb.l(nb.math('MULTIPLY', den, 45.0), pv.inputs['Density']); pv.inputs['Anisotropy'].default_value = 0.3
    nb.l(pv.outputs[0], out.inputs['Volume']); R['smokemat'] = smoke_m
    for (x0, y0, z0, hgt, s) in ((0.8, -5.2, -12.5, 5.5, 1), (3.8, -4.8, -15.5, 7.5, 2), (6.5, -5.8, -19, 4.2, 3), (-0.6, -5.6, -16, 3.2, 4)):
        bm = bmesh.new(); r = random.Random(s * 13); rings = []
        for i in range(41):
            u = i / 40; rr = lerp(0.85, 0.24, u ** 0.7) * (0.85 + 0.3 * r.random()); ring = []
            for j in range(32):
                a = j / 32 * math.tau; p = Vector((math.cos(a) * rr, u * hgt, math.sin(a) * rr))
                nn = noise.fractal(Vector((p.x * 1.6, p.y * 1.1, p.z * 1.6)) + Vector((s * 10, 0, 0)), 0.6, 2.1, 5)
                p.x *= 1 + 0.32 * nn; p.z *= 1 + 0.32 * nn
                if 0.3 < u < 0.9 and noise.noise(Vector((a * 2, u * 9, s))) > 0.45: p.x *= 1.25; p.z *= 1.25  # Krusten / Seitenäste
                ring.append(bm.verts.new(p + Vector((x0, y0, z0))))
            rings.append(ring)
        for i in range(40):
            for j in range(32): bm.faces.new((rings[i][j], rings[i + 1][j], rings[i + 1][(j + 1) % 32], rings[i][(j + 1) % 32]))
        ch = mesh_obj('chimney', bm, cm, subsurf=1); parts.append(ch)
        top = Vector((x0, y0 + hgt, z0)); R['chimneys'].append(top)
        sb = bmesh.new(); cyl_bm(2.4, 2.4, 10.0, 24, sb, Matrix.Translation((0, 0, 5.0)))
        sm = mesh_obj('smoke', sb, smoke_m, smooth_shade=False, three=False)
        sm.matrix_basis = Matrix.Translation(P(*top) - Vector((0, 0, 0.1))); parts.append(sm)
    # Röhrenwürmer, weiße Krebse
    tw = principled('tubeworm', (0.75, 0.72, 0.66), 0.6); plume = principled('plume', (0.55, 0.02, 0.03), 0.4, Subsurface_Weight=0.6, Subsurface_Radius=(0.02, 0.004, 0.004))
    wb, pb = bmesh.new(), bmesh.new(); r = random.Random(44)
    for i in range(110):
        c = R['chimneys'][i % 4]; a = r.random() * 6.28; dd = 0.9 + r.random() * 1.2; x, z = c.x + math.cos(a) * dd, c.z + math.sin(a) * dd; L = 0.3 + r.random() * 0.6
        m = Matrix.Translation((x, -5.35 + r.random() * 0.3, z)) @ Euler(((r.random() - 0.5) * 0.4, 0, (r.random() - 0.5) * 0.4)).to_matrix().to_4x4()
        cyl_bm(0.025, 0.03, L, 10, wb, m @ Matrix.Translation((0, L / 2, 0)) @ Euler((math.pi / 2, 0, 0)).to_matrix().to_4x4())
        sphere_bm(0.045, 10, 8, pb, m @ Matrix.Translation((0, L + 0.03, 0)) @ Matrix.Diagonal((1, 1.6, 1, 1)))
    parts.append(mesh_obj('worms', wb, tw)); parts.append(mesh_obj('plumes', pb, plume, subsurf=1))
    crab = principled('crab', (0.8, 0.78, 0.72), 0.5, Subsurface_Weight=0.3)
    cb = bmesh.new()
    for i in range(14):
        c = R['chimneys'][i % 4]; a = r.random() * 6.28; dd = 1.1 + r.random() * 1.8; x, z = c.x + math.cos(a) * dd, c.z + math.sin(a) * dd
        m = Matrix.Translation((x, -5.25, z)) @ Euler((0, r.random() * 6, 0)).to_matrix().to_4x4()
        sphere_bm(0.06, 12, 8, cb, m @ Matrix.Diagonal((1.2, 0.5, 1, 1)))
        for k in range(8):
            ang = (k / 8) * math.tau; cyl_bm(0.008, 0.004, 0.11, 6, cb, m @ Euler((0, ang, 0)).to_matrix().to_4x4() @ Matrix.Translation((0.08, -0.02, 0)) @ Euler((0, 0, -0.9)).to_matrix().to_4x4() @ Euler((0, math.pi / 2, 0)).to_matrix().to_4x4())
    parts.append(mesh_obj('crabs', cb, crab))
    for p in parts: p.parent = grp

def grid_bm(w, h, nx, ny, height):
    bm = bmesh.new(); vs = []
    for j in range(ny + 1):
        row = []
        for i in range(nx + 1):
            x, y = (i / nx - 0.5) * w, (j / ny - 0.5) * h
            row.append(bm.verts.new(Vector((x, y, height(x, y)))))
        vs.append(row)
    for j in range(ny):
        for i in range(nx): bm.faces.new((vs[j][i], vs[j][i + 1], vs[j + 1][i + 1], vs[j + 1][i]))
    return bm

def build_walls(R):
    wallm = mat_rock('wall', (0.03, 0.027, 0.024), (0.15, 0.14, 0.12), 0.45, 1.6)
    def rockh(o, amp):
        return lambda x, y: amp * (noise.fractal(Vector((x * 0.045 + o, y * 0.045, 0.3)), 0.62, 2.1, 7) + 0.6 * abs(noise.noise(Vector((x * 0.11, y * 0.11 + o, 1.7)))))
    # Grabenwand rechts (zeigt zur Kabine, -x) und hinten
    b = grid_bm(140, 140, 220, 220, rockh(2.0, 4.0))
    bmesh.ops.transform(b, matrix=Matrix.Translation((13, 0, -20)) @ Euler((0, -math.pi / 2, 0)).to_matrix().to_4x4(), verts=b.verts)
    R['wallR'] = mesh_obj('wallR', b, wallm)
    b = grid_bm(160, 140, 240, 210, rockh(7.0, 5.0))
    bmesh.ops.transform(b, matrix=Matrix.Translation((0, 0, -48)), verts=b.verts)
    R['wallB'] = mesh_obj('wallB', b, wallm)
    # Meeresboden
    sed = mat_sediment()
    fl = grid_bm(160, 160, 260, 260, lambda x, y: 0.35 * noise.fractal(Vector((x * 0.06, y * 0.06, 0.0)), 0.6, 2.0, 5) + 0.06 * noise.noise(Vector((x * 0.9, y * 0.9, 3))))
    bmesh.ops.transform(fl, matrix=Matrix.Translation((0, -1.3, -40)) @ Euler((-math.pi / 2, 0, 0)).to_matrix().to_4x4(), verts=fl.verts)
    R['floor'] = mesh_obj('seafloor', fl, sed)
    ck = principled('cuke', (0.85, 0.45, 0.42), 0.3, Subsurface_Weight=0.8, Subsurface_Radius=(0.04, 0.012, 0.01), Transmission_Weight=0.2, Coat_Weight=0.6)
    R['cukes'] = []
    for x, z, s in ((1.2, -4.2, 1), (-0.4, -6.5, 0.8), (2.8, -8, 1.1), (-1.6, -9.5, 0.9)):
        bm = CR.hull_bm(0.38 * s, lambda u, s=s: (0.07 * s * math.sin(math.pi * clamp(u * 1.05)) ** 0.8 + 0.008, 0.08 * s * math.sin(math.pi * clamp(u * 1.05)) ** 0.8 + 0.008, 2, 0), 24, 16)
        for k in range(10):  # Füßchen / Papillen
            u = (k + 0.5) / 10; sphere_bm(0.012 * s, 8, 6, bm, Matrix.Translation((u * 0.38 * s, 0.06 * s * math.sin(math.pi * u), 0.03 * s * (1 if k % 2 else -1))) @ Matrix.Diagonal((1, 2.5, 1, 1)))
        c = mesh_obj('cuke', bm, ck, subsurf=1); c['x'] = x; c['z'] = z; c['rot'] = x; R['cukes'].append(c)

# ---------------------------------------------------------------- Sprung in der Scheibe (echte Bruchflächen im Glas)
def build_crack(R):
    r = random.Random(77); segs = []; ox, oy = 0.62, 1.78
    def grow(x, y, ang, ln, depth, t0):
        px, py = x, y; n = 5 + int(r.random() * 4)
        for i in range(n):
            a = ang + (r.random() - 0.5) * 0.7; l = ln / n * (0.6 + r.random() * 0.8); nx, ny = px + math.cos(a) * l, py + math.sin(a) * l
            segs.append((px, py, nx, ny, t0 + (i / n) * 0.22 * (depth + 1), depth, (r.random() - 0.5) * 0.9))
            if depth < 2 and r.random() < 0.4: grow(nx, ny, a + (0.7 if r.random() < 0.5 else -0.7), ln * 0.45, depth + 1, t0 + (i / n) * 0.2)
            px, py = nx, ny
    for i in range(9): grow(ox, oy, i / 9 * math.tau + r.random() * 0.4, 0.38 + r.random() * 0.4, 0, 0)
    rings = []
    for k in (1, 2, 3):
        pts = []
        for i in range(25):
            a = i / 24 * math.tau; rr = k * 0.028 + r.random() * 0.01; pts.append((ox + math.cos(a) * rr, oy + math.sin(a) * rr))
        rings.append(pts)
    R['crack'] = dict(segs=segs, rings=rings, ox=ox, oy=oy)
    cm = principled('crackface', (0.9, 0.95, 1.0), 0.18, 0.6, Emission_Color=(0.75, 0.88, 1.0), Emission_Strength=0.1)
    ob = bpy.data.objects.new('crack', bpy.data.meshes.new('crack')); coll('SEA').objects.link(ob); ob.data.materials.append(cm)
    pw = principled('powder', (0.9, 0.93, 0.95), 0.5, Transmission_Weight=0.4)
    ob.data.materials.append(pw); R['crackob'] = ob

def update_crack(R, T):
    ob = R['crackob']; t = T - CRACK; cr = R['crack']
    if t < 0: ob.hide_render = True; return
    ob.hide_render = False; verts, faces, mi = [], [], []
    z0, z1 = -1.3295, -1.3005
    def quad(x0, y0, x1, y1, tilt, m=0):
        o = len(verts); dx, dy = (y1 - y0) * tilt * 0.03, -(x1 - x0) * tilt * 0.03
        for (x, y, z) in ((x0, y0, z0), (x1, y1, z0), (x1 + dx, y1 + dy, z1), (x0 + dx, y0 + dy, z1)): verts.append(P(x, y, z))
        faces.append((o, o + 1, o + 2, o + 3)); mi.append(m)
    for (x0, y0, x1, y1, t0, dp, tilt) in cr['segs']:
        k = clamp((t - t0) / 0.06)
        if k <= 0: continue
        quad(x0, y0, lerp(x0, x1, k), lerp(y0, y1, k), tilt * (0.9 - dp * 0.25))
    rk = clamp(t / 0.3)
    if rk > 0:
        for pts in cr['rings']:
            n = max(2, int(len(pts) * rk))
            for i in range(n - 1): quad(*pts[i], *pts[i + 1], 0.6)
    # zertrümmerte Mitte
    r = random.Random(5)
    if t > 0:
        for i in range(60):
            a, rr = r.random() * math.tau, r.random() ** 2 * 0.03; x, y = cr['ox'] + math.cos(a) * rr, cr['oy'] + math.sin(a) * rr; b = r.random() * math.tau; l = 0.004 + r.random() * 0.008
            quad(x, y, x + math.cos(b) * l, y + math.sin(b) * l, r.random() - 0.5, 1)
    me = ob.data; me.clear_geometry(); me.from_pydata(verts, [], faces)
    for p, m in zip(me.polygons, mi): p.material_index = m
    me.update()

# ---------------------------------------------------------------- Hand am Bedienfeld
def build_hand(R):
    skin, nbs, outs = new_mat('skin'); os_ = coords(nbs, 'Object')
    bsdf(nbs, outs, nbs.mix(noise_tex(nbs, os_, 60, 3).outputs['Fac'], (0.55, 0.34, 0.26, 1), (0.66, 0.42, 0.33, 1)), rough=0.45, normal=bump(nbs, noise_tex(nbs, os_, 900, 6).outputs['Fac'], 0.12, 0.0004),
         Subsurface_Weight=0.7, Subsurface_Radius=(0.012, 0.004, 0.0025), Subsurface_Scale=1.0, Coat_Weight=0.1)
    me = bpy.data.meshes.new('hand'); ob = bpy.data.objects.new('hand', me); coll('SEA').objects.link(ob)
    V, E, RAD = [], [], []
    def chain(pts, radii, start=None):
        idx = []
        for p, rr in zip(pts, radii): V.append(p); RAD.append(rr); idx.append(len(V) - 1)
        if start is not None: E.append((start, idx[0]))
        for a, b in zip(idx, idx[1:]): E.append((a, b))
        return idx
    palm = chain([(0.17, -0.01, 0.005), (0.12, -0.008, 0.005), (0.075, -0.004, 0.004)], [0.03, 0.031, 0.03])
    chain([(0.045, 0.004, 0.012), (0.022, 0.007, 0.012), (0.002, 0.008, 0.012), (-0.016, 0.007, 0.012)], [0.0105, 0.0095, 0.0088, 0.008], palm[-1])  # Zeigefinger
    for z, s in ((-0.006, 1.0), (-0.022, 0.95), (-0.036, 0.85)):
        chain([(0.05, -0.002, z), (0.03, -0.018, z), (0.042, -0.036, z), (0.06, -0.034, z)], [0.0105 * s, 0.0095 * s, 0.0088 * s, 0.008 * s], palm[-1])
    chain([(0.11, -0.022, 0.03), (0.085, -0.03, 0.04), (0.062, -0.034, 0.036), (0.05, -0.03, 0.028)], [0.014, 0.012, 0.0105, 0.0095], palm[1])
    me.from_pydata([P(*v) for v in V], E, []); me.update()
    md = ob.modifiers.new('skin', 'SKIN')
    if len(me.skin_vertices) == 0: me.skin_vertices.new()
    for i, rr in enumerate(RAD): me.skin_vertices[0].data[i].radius = (rr, rr * (0.7 if i in palm else 1.0))
    me.skin_vertices[0].data[0].use_root = True
    sd = ob.modifiers.new('sub', 'SUBSURF'); sd.levels = 2; sd.render_levels = 2
    me.materials.append(skin)
    for p in me.polygons: p.use_smooth = True
    nail = principled('nail', (0.85, 0.62, 0.55), 0.15, Coat_Weight=0.8, Subsurface_Weight=0.3)
    nb = bmesh.new(); sphere_bm(1, 16, 10, nb, Matrix.Translation((-0.012, 0.0145, 0.012)) @ Matrix.Diagonal((0.009, 0.0022, 0.0068, 1)))
    n = mesh_obj('nail', nb, nail); n.parent = ob
    cloth, nb2, out = new_mat('hoodie'); o = coords(nb2, 'Object')
    wv = nb2.n('ShaderNodeTexWave', wave_type='BANDS', bands_direction='Y'); nb2.l(o, wv.inputs['Vector']); wv.inputs['Scale'].default_value = 120
    fz = noise_tex(nb2, o, 400, 4)
    bsdf(nb2, out, (0.035, 0.05, 0.08), rough=0.95, normal=bump(nb2, nb2.math('ADD', wv.outputs['Fac'], nb2.math('MULTIPLY', fz.outputs['Fac'], 0.5)), 0.3, 0.002), Sheen_Weight=0.8, Sheen_Roughness=0.5)
    sb = bmesh.new(); cyl_bm(0.042, 0.05, 0.32, 32, sb, Matrix.Translation((0.33, -0.012, 0.005)) @ Euler((0, math.pi / 2, 0)).to_matrix().to_4x4())
    s = mesh_obj('sleeve', sb, cloth, subsurf=1); s.parent = ob
    R['hand'] = ob

# ---------------------------------------------------------------- Oberfläche (Hook)
def build_surface(R):
    c = 'SURF'
    # Himmel
    w = bpy.data.worlds.new('sky'); w.use_nodes = True; nt = w.node_tree; nt.nodes.clear(); nb = NB(nt)
    out = nb.n('ShaderNodeOutputWorld'); bg = nb.n('ShaderNodeBackground'); sky = nb.n('ShaderNodeTexSky')
    for t in ('MULTIPLE_SCATTERING', 'SINGLE_SCATTERING', 'NISHITA'):
        try: sky.sky_type = t; break
        except Exception: pass
    try: sky.sun_elevation = math.radians(38); sky.sun_rotation = math.radians(120); sky.altitude = 20; sky.air_density = 1.2; sky.aerosol_density = 1.6
    except Exception: pass
    nb.l(sky.outputs[0], bg.inputs[0]); bg.inputs[1].default_value = 0.14; nb.l(bg.outputs[0], out.inputs['Surface']); R['skyworld'] = w
    R['sunS'] = light('sunS', 'SUN', (0, 0, 50), 2.2, (1.0, 0.95, 0.86), c=c, angle=math.radians(0.6))
    R['sunS'].rotation_euler = Euler((math.radians(52), 0, math.radians(120 + 90)))
    # Meer: Ocean-Modifier + Volumen darunter (Solidify)
    sea_m, nb, out = new_mat('seasurf')
    bsdf(nb, out, (0.8, 0.95, 1.0), rough=0.03, Transmission_Weight=1.0, IOR=1.333)
    ab = nb.n('ShaderNodeVolumeAbsorption'); ab.inputs['Color'].default_value = (0.12, 0.6, 0.72, 1); ab.inputs['Density'].default_value = 0.04
    sc = nb.n('ShaderNodeVolumeScatter'); sc.inputs['Color'].default_value = (0.3, 0.72, 0.95, 1); sc.inputs['Density'].default_value = 0.065; sc.inputs['Anisotropy'].default_value = 0.55
    ad = nb.n('ShaderNodeAddShader'); nb.l(ab.outputs[0], ad.inputs[0]); nb.l(sc.outputs[0], ad.inputs[1]); nb.l(ad.outputs[0], out.inputs['Volume'])
    bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=1)
    sea = mesh_obj('sea', bm, sea_m, c=c, three=False)
    try:
        oc = sea.modifiers.new('ocean', 'OCEAN'); oc.geometry_mode = 'GENERATE'; oc.resolution = 18; oc.spatial_size = 40; oc.repeat_x = 9; oc.repeat_y = 9; oc.use_normals = True
        oc.wave_scale = 1.1; oc.choppiness = 1.1; oc.wind_velocity = 11; oc.random_seed = 3; oc.wave_alignment = 0.3
        sea.location = (-180, -180, 0); R['ocean'] = oc
    except Exception as e:
        print('Ocean fehlt', e); R['ocean'] = None
    so = sea.modifiers.new('sol', 'SOLIDIFY'); so.thickness = 420; so.offset = -1; so.use_even_offset = False
    R['sea'] = sea
    # ferne Meeresfläche bis zum Horizont
    fm, nb, out = new_mat('farsea'); o = coords(nb, 'Object')
    n1 = noise_tex(nb, o, 0.08, 8, 0.6); n2 = noise_tex(nb, o, 0.6, 6, 0.6)
    bsdf(nb, out, (0.004, 0.03, 0.045), rough=0.06, normal=bump(nb, nb.math('ADD', n1.outputs['Fac'], nb.math('MULTIPLY', n2.outputs['Fac'], 0.3)), 0.5, 0.6))
    fb = bmesh.new(); a = bmesh.ops.create_circle(fb, segments=96, radius=6000)['verts']; b = bmesh.ops.create_circle(fb, segments=96, radius=172)['verts']
    for i in range(96): fb.faces.new((b[i], b[(i + 1) % 96], a[(i + 1) % 96], a[i]))
    far = mesh_obj('farsea', fb, fm, c=c, three=False, smooth_shade=False); far.location = (0, 0, -0.3)
    # Turm mitten im Meer (geht 300 m nach unten)
    fac = mat_facade('facade_s'); R['facade_s'] = fac
    box('towerS', -6.5, 6.5, -320, 0.2, -6.5, 6.5, fac, c=c)
    conc, nb, out = new_mat('concrete'); o = coords(nb, 'Object'); n1 = noise_tex(nb, o, 2, 8)
    bsdf(nb, out, nb.mix(n1.outputs['Fac'], (0.16, 0.155, 0.145, 1), (0.25, 0.24, 0.225, 1)), rough=0.85, normal=bump(nb, noise_tex(nb, o, 40, 6).outputs['Fac'], 0.3, 0.01))
    mesh_obj('deck', cyl_bm(9.4, 9.0, 3.2, 96, mat=Matrix.Translation((0, -1.0, 0)) @ Euler((math.pi / 2, 0, 0)).to_matrix().to_4x4()), conc, c=c, smooth_shade=False)
    steelS = principled('steelS', (0.85, 0.86, 0.87), 0.25, 1.0)
    rb = bmesh.new()
    bmesh.ops.create_circle(rb, segments=96, radius=9.0, matrix=Matrix.Translation((0, 1.6, 0)) @ Euler((math.pi / 2, 0, 0)).to_matrix().to_4x4())
    rail = mesh_obj('railS', rb, steelS, c=c); rail.modifiers.new('sk', 'SKIN')
    if len(rail.data.skin_vertices) == 0: rail.data.skin_vertices.new()
    for sv in rail.data.skin_vertices[0].data: sv.radius = (0.035, 0.035)
    for i in range(36):
        a = i / 36 * math.tau; mesh_obj('postS', cyl_bm(0.035, 0.035, 1.0, 8, mat=Matrix.Translation((math.cos(a) * 9.0, 1.1, math.sin(a) * 9.0)) @ Euler((math.pi / 2, 0, 0)).to_matrix().to_4x4()), steelS, c=c)
    gl = glass_mat('pavglass', (0.9, 0.96, 0.98), 0.02)
    pb = bmesh.new(); bmesh.ops.create_cone(pb, cap_ends=False, segments=64, radius1=3.0, radius2=3.0, depth=2.8, matrix=Matrix.Translation((0, 2.0, 0)) @ Euler((math.pi / 2, 0, 0)).to_matrix().to_4x4())
    pav = mesh_obj('pavilion', pb, gl, c=c); md = pav.modifiers.new('sol', 'SOLIDIFY'); md.thickness = 0.03
    mesh_obj('roof', cyl_bm(3.3, 3.3, 0.18, 64, mat=Matrix.Translation((0, 3.45, 0)) @ Euler((math.pi / 2, 0, 0)).to_matrix().to_4x4()), principled('roofS', (0.9, 0.9, 0.88), 0.4), c=c)
    mesh_obj('liftdoor', box_bm(-0.9, 0.9, 0.6, 2.8, 0.9, 1.1), principled('ldoor', (0.55, 0.56, 0.57), 0.2, 1.0), c=c, smooth_shade=False)
    light('pavlight', 'POINT', P(0, 2.9, 0), 300, (1.0, 0.82, 0.6), c=c, shadow_soft_size=0.5)
    # Steg und Boot
    wood = principled('wood', (0.24, 0.16, 0.1), 0.7)
    mesh_obj('pier', box_bm(-0.9, 0.9, 0.35, 0.5, 8.8, 15), wood, c=c, smooth_shade=False)
    hb = CR.hull_bm(5.5, lambda u: (lerp(0.55, 0.7, u) if u > 0.2 else lerp(0.2, 0.55, u / 0.2), (math.sin(math.pi * min(1, u * 0.9 + 0.1)) ** 0.5) * 1.0, 2.0 + 2 * u, 0))
    bmesh.ops.bisect_plane(hb, geom=hb.verts[:] + hb.edges[:] + hb.faces[:], plane_co=(0, 0.25, 0), plane_no=(0, 1, 0), clear_outer=True)
    boat = mesh_obj('boat', hb, principled('boatwhite', (0.85, 0.85, 0.83), 0.3, Coat_Weight=0.5), c=c)
    cb = box_bm(1.5, 3.4, 0.2, 1.3, -0.65, 0.65); bc = mesh_obj('boatcab', cb, principled('boatcab', (0.82, 0.82, 0.8), 0.35), c=c, smooth_shade=False); bc.parent = boat
    R['boat'] = boat
    # Gläserner Aufzug am Turm (fährt runter)
    cab = bpy.data.objects.new('cabS', None); coll(c).objects.link(cab); R['cabS'] = cab
    o = mesh_obj('cabS_glass', box_bm(-1.4, 1.4, 0, 2.8, 6.55, 9.3), gl, c=c, smooth_shade=False); o.parent = cab
    o = mesh_obj('cabS_floor', box_bm(-1.45, 1.45, -0.15, 0.0, 6.5, 9.35), principled('cabSf', (0.05, 0.05, 0.05), 0.4), c=c, smooth_shade=False); o.parent = cab
    li = light('cabS_light', 'POINT', P(0, 2.2, 7.9), 220, (1.0, 0.8, 0.55), c=c, shadow_soft_size=0.4); li.parent = cab
    # Blasen beim Eintauchen
    bub = glass_mat('bubble', (1, 1, 1), 0.0, 0.75)
    R['bubbles'] = bpy.data.objects.new('bubbles', bpy.data.meshes.new('bubbles')); coll(c).objects.link(R['bubbles']); R['bubbles'].data.materials.append(bub)
    # Schwebeteilchen unter Wasser
    bm = bmesh.new(); r = random.Random(5); snow = principled('snowS', (0.8, 0.85, 0.85), 0.6, Transmission_Weight=0.3)
    for i in range(1500):
        bmesh.ops.create_icosphere(bm, subdivisions=1, radius=0.004 + r.random() * 0.008, matrix=Matrix.Translation(((r.random() - 0.5) * 40, -r.random() * 80 - 1, (r.random() - 0.5) * 40 + 15)))
    mesh_obj('snowS', bm, snow, c=c)

def update_surface(R, T, cam):
    if R.get('ocean'): R['ocean'].time = T * 1.0
    R['boat'].matrix_basis = M3((-0.2, 0.0, 15.5), (0, 0.1, 0.05 * math.sin(T * 1.3)))
    R['cabS'].matrix_basis = M3((0, -14 - max(0, T - 2.5) * 2.2, 0))
    if T < 1.9:
        k = ease_out(T / 1.9); pos = (lerp(-30, -16, k), lerp(14, 4.5, k), lerp(34, 24, k)); look = (0, lerp(2.5, 0.5, k), 0)
    elif T < 2.9:
        k = (T - 1.9) / 1.0; pos = (lerp(-16, -14, k), lerp(4.5, -5, ease_in(k)), lerp(24, 21, k)); look = (0, lerp(0.5, -8, k), 0)
    else:
        k = smooth(2.9, 5.0, T); pos = (lerp(-14, -9, k), lerp(-5, -26, k), lerp(21, 18, k)); look = (0, lerp(-8, -70, k), lerp(0, 4, k))
    pos = (pos[0] + noise1(T, 2) * 0.12, pos[1] + noise1(T, 5) * 0.08, pos[2])
    set_cam(cam, pos, look, 50, fstop=11)
    # Blasen
    d = T - 2.25; me = R['bubbles'].data; me.clear_geometry()
    if 0 < d < 2.6:
        bm = bmesh.new(); r = random.Random(11); cp = Vector(pos)
        for i in range(160):
            s = (r.random() * 2 - 1, r.random(), r.random() * 2 - 1, 0.5 + r.random())
            p = (cp.x + s[0] * 1.6 + math.sin(T * 6 + i) * 0.05, cp.y - 1.5 + s[1] * 3 + d * d * s[3] * 3.5, cp.z + s[2] * 1.6 - 1.2)
            sphere_bm(0.006 + r.random() * 0.02, 10, 6, bm, Matrix.Translation(P(*p)) @ Matrix.Diagonal((1, 1, 0.75, 1)))
        bm.to_mesh(me); bm.free()
    me.update()

# ---------------------------------------------------------------- Aufbau
def build_all():
    R = {}
    w = bpy.data.worlds.new('deep'); w.use_nodes = True; nt = w.node_tree; nt.nodes.clear(); nb = NB(nt)
    out = nb.n('ShaderNodeOutputWorld'); bg = nb.n('ShaderNodeBackground'); bg.name = 'bg'; nb.l(bg.outputs[0], out.inputs['Surface']); R['deepworld'] = w
    build_cabin(R); build_tower(R); build_water(R); build_particles(R); build_school(R)
    R['whale'] = CR.whale(); R['squid'] = CR.squid(); R['angler'] = CR.angler(); R['snail'] = CR.snailfish(); R['sub'] = CR.submersible()
    build_vent(R); build_walls(R); build_crack(R); build_hand(R); build_surface(R)
    return R

# ---------------------------------------------------------------- Aktualisierung pro Bild
def squid_arms(R, T, k, eyeK):
    sq = R['squid']
    head = Vector((lerp(2.4, 1.15, eyeK) + 0.05 * math.sin(T * 0.8), lerp(3.6, 2.0, eyeK), lerp(-4.2, -2.45, eyeK)))
    rot = (0, -0.2, 1.15 + 0.05 * math.sin(T * 0.6))
    sq['ob'].matrix_basis = M3(head, rot)
    rm = Euler(rot, 'XYZ').to_matrix()
    base = rm @ Vector((-0.35, 0, 0)) + head
    r = random.Random(5); items = []
    for i, arm in enumerate(sq['arms']):
        pts = []
        if i == 0:  # Arm gleitet über die Scheibe
            c0 = Vector((lerp(1.15, -0.5, k), lerp(2.45, 1.15, k), -1.43)); dr = Vector((-0.75, -0.66, 0)).normalized()
            for j in range(65):
                u = j / 64
                if u < 0.42:
                    w = u / 0.42; ctrl = Vector(((base.x + c0.x) / 2 + 0.4, (base.y + c0.y) / 2 + 0.3, (base.z + c0.z) / 2 - 0.5))
                    pts.append(base * ((1 - w) ** 2) + ctrl * (2 * w * (1 - w)) + c0 * (w * w))
                else:
                    w = (u - 0.42) / 0.58; p = c0 + dr * (w * 1.3); p.x += 0.06 * math.sin(w * 7 + T * 2) * w; p.y += 0.04 * math.sin(w * 5 + T * 2.4) * w
                    if w > 0.85: cc = (w - 0.85) / 0.15; p += Vector((0.6, -0.2, -0.3)) * (cc * cc * 0.25)
                    pts.append(p)
            rad = lambda ii, u: (0.085 * (1 - u) ** 0.8 + 0.006)
            bpts = [P(*p) for p in pts]
            tube_set(arm, bpts, rad, up=Vector((0, -1, 0)), flat=0.85)
            # Saugnäpfe zur Scheibe gedrückt (Blender: Scheibe bei y=+1.33, Normale -y)
            for j in range(28, 63, 1):
                u = j / 64; t = (bpts[j + 1] - bpts[j - 1]).normalized(); side = t.cross(Vector((0, 1, 0))).normalized()
                rr = rad(j, u)
                for sgn in (-1, 1):
                    p = bpts[j] + side * (sgn * rr * 0.42) + Vector((0, -rr * 0.72, 0))
                    p.y = min(p.y, 1.345); items.append((p, Vector((0, -1, 0)), rr * 0.34))
        else:
            ln = 2.0 + r.random() * 0.8 if i < 8 else 5.0; az = r.random() * 6.28; el = -0.4 - r.random() * 0.8; ph = r.random() * 6
            d0 = Vector((math.cos(az) * 0.6 - 0.5, el, math.sin(az) * 0.5 + 0.25)).normalized()
            for j in range(65):
                u = j / 64; p = base + d0 * (u * ln)
                p.x += 0.35 * u * math.sin(T * 0.9 + ph + u * 3); p.y += 0.25 * u * math.sin(T * 0.7 + ph * 2 + u * 4) - u * u * 0.6; p.z += 0.25 * u * math.cos(T * 0.8 + ph + u * 2)
                if p.z > -1.45: p.z = -1.45
                pts.append(p)
            if i < 8: rad = lambda ii, u: 0.075 * (1 - u) ** 0.85 + 0.004
            else: rad = lambda ii, u: 0.04 * (1 - u) ** 0.6 + 0.004 + (0.03 * math.sin(math.pi * clamp((u - 0.78) / 0.18)) if u > 0.78 else 0)
            bpts = [P(*p) for p in pts]
            nrm = tube_set(arm, bpts, rad, up=Vector((0, 0, -1)))
            for j in range(4, 62, 3):
                u = j / 64; t = (bpts[j + 1] - bpts[j - 1]).normalized(); dn = Vector((0, 0, -1)); dn = (dn - t * dn.dot(t)).normalized()
                if i >= 8 and u < 0.78: continue
                side = t.cross(dn); rr = rad(j, u)
                for sgn in (-1, 1): items.append((bpts[j] + dn * rr * 0.75 + side * sgn * rr * 0.4, dn, rr * 0.3))
    CR.suckers_set(sq, items)

def lights(R, inside, outside, d):
    R['inlight'].data.energy = 160 * inside; R['lamp'].node_tree.nodes['Emission'].inputs[1].default_value = 3.0 * inside + 0.02
    for f in R['floods']: f.data.energy = (2600 if d < 2000 else 4200) * outside
    R['nearL'].data.energy = 25 * outside
    R['facade'].node_tree.nodes['lit'].outputs[0].default_value = clamp(inside + 0.2)

def set_env(R, d, T):
    fc = fog_col(d); bg = R['deepworld'].node_tree.nodes['bg']
    bright = 2.2 if d < 100 else 1.0
    bg.inputs[0].default_value = (fc.x * bright, fc.y * bright, fc.z * bright, 1); bg.inputs[1].default_value = 1.0
    nt = R['water'].node_tree; k = smooth(0, 1200, d)
    nt.nodes['abs'].inputs['Density'].default_value = lerp(0.045, 0.03, k)
    nt.nodes['abs'].inputs['Color'].default_value = (lerp(0.12, 0.05, k), lerp(0.58, 0.32, k), lerp(0.72, 0.62, k), 1)
    nt.nodes['sca'].inputs['Density'].default_value = lerp(0.022, 0.045, k)
    nt.nodes['sca'].inputs['Color'].default_value = (lerp(0.45, 0.55, k), lerp(0.82, 0.72, k), lerp(0.92, 0.85, k), 1)
    R['sun'].data.energy = 14.0 * math.exp(-d / 40)
    top = clamp(max(3.5, d), 0, 60)
    me = R['domain'].data
    for i in R['dom_top']: me.vertices[i].co.z = top
    me.update()
    R['gobo'].hide_render = d > 80; R['gobo'].location = (0, 0, top - 0.3)
    R['gobomat'].node_tree.nodes['T'].outputs[0].default_value = T
    R['sun'].hide_render = d > 600

def scroll(R, d):
    R['facade'].node_tree.nodes['scroll'].outputs[0].default_value = d
    R['brk'].matrix_basis = M3((0, (d % 3.5), 0))

def snow_at(R, d, T, k=1.0):
    R['snow'].matrix_basis = M3((0.15 * math.sin(T * 0.4), ((d * k) % 40), 0.12 * math.cos(T * 0.3)))

SEA_ALWAYS = None
def update(R, cam, f):
    T = f / FPS; s = shot_at(T); id_ = s['id']; d = depth_at(T, s); t = T - s['t0']
    sc = bpy.context.scene
    surf = id_ == 'surface'
    for ob in coll('SURF').all_objects: ob.hide_render = not surf
    for ob in coll('SEA').all_objects: ob.hide_render = surf or ob.name.startswith('hole')
    R['hand'].hide_render = True; R['bubbles'].hide_render = not surf
    if surf:
        sc.world = R['skyworld']; update_surface(R, T, cam); sc.view_settings.exposure = -0.6 if T < 2.25 else 0.3; R['facade_s'].node_tree.nodes['lit'].outputs[0].default_value = 0.35; return
    sc.world = R['deepworld']
    set_env(R, d, T); scroll(R, d)
    hideall = [R['whale']['ob'], R['squid']['ob'], R['squid']['suck'], R['angler']['ob'], R['snail']['ob'], R['vent'], R['wallR'], R['wallB'], R['floor'], R['bio']] + R['squid']['arms'] + R['cukes'] + [o for o, _ in R['fish']]
    for o in hideall:
        o.hide_render = True
        for ch in o.children_recursive: ch.hide_render = True
    for o in [R['sub']['root']] + R['sub']['root'].children_recursive: o.hide_render = True
    inside, outside = 1.0, 0.0
    cp, lk, fov, fst, focus = Vector((0.15, 1.55, 0.85)), Vector((0.25, 1.35, -5)), 52, 2.8, None
    pm = R['panelmat'].node_tree.nodes['pressed'].outputs[0]; pm.default_value = 1.0 if T >= PRESS else 0.0
    def show(o, v=True):
        o.hide_render = not v
        for ch in o.children_recursive: ch.hide_render = not v
    exp = 0.0
    if id_ == 'panel':
        show(R['hand']); pk = smooth(PRESS - 0.6, PRESS, T) - smooth(PRESS + 0.25, PRESS + 0.8, T)
        bx, by, bz = -1.322, 0.901, -0.7
        hy = by + lerp(-0.08, 0, smooth(PRESS - 1.4, PRESS - 0.5, T)) - (1 - smooth(6.2, 6.9, T)) * 0.25
        R['hand'].matrix_basis = M3((bx + 0.018 + lerp(0.25, 0.0, pk), hy - 0.007, bz - 0.012), (0, 0, 0))
        R['hand'].hide_render = T <= 6.2
        for ch in R['hand'].children_recursive: ch.hide_render = T <= 6.2
        cp = Vector((-0.68, 1.12 + 0.02 * math.sin(T), -0.42)); lk = Vector((-1.32, 1.0 - smooth(5, 8.5, T) * 0.1, -0.72)); fov = lerp(44, 36, smooth(5, 9, T)); fst = 2.0
        focus = (Vector((-1.33, 0.95, -0.7)) - cp).length
    if id_ in ('shallow', 'panel'):
        for o, _ in R['fish']: o.hide_render = False
        scare = smooth(SHADOW - 0.1, SHADOW + 0.6, T)
        update_school(R, T, Vector((2.2, 1.6 + (d - 6) * 0.4, -6.5)), scare)
        if T > SHADOW - 0.5:
            show(R['whale']['ob']); R['whale']['ob'].matrix_basis = M3((lerp(13, -12, (T - SHADOW + 0.5) / 2.3), 4.6, -12), (0, 0.1, 0.05)); CR.whale_swim(R['whale'], T, 0.18)
        dim = smooth(SHADOW, SHADOW + 0.5, T) * (1 - smooth(SHADOW + 1.2, SHADOW + 1.9, T))
        R['sun'].data.energy *= 1 - 0.75 * dim
        if id_ == 'shallow': lk = Vector((0.6 + 0.4 * smooth(SHADOW, SHADOW + 0.8, T), 1.4 + 0.9 * smooth(SHADOW - 0.3, SHADOW + 0.7, T), -5)); focus = 5.5
    if id_ == 'whale':
        show(R['whale']['ob']); outside = 1
        flee = max(0, T - WHALE_FLEE); look = smooth(17.9, 18.5, T) * (1 - smooth(WHALE_FLEE, WHALE_FLEE + 0.5, T))
        nx = 6 - 4.1 * t - 6 * flee * flee; pos = (nx, 2.1 + 2.6 * flee * flee + 0.15 * math.sin(T * 0.7), -8.6 - 1.5 * flee * flee)
        rot = (0, -0.38 - 0.25 * smooth(WHALE_FLEE, WHALE_FLEE + 1.5, T), -0.18 * look - 0.55 * smooth(WHALE_FLEE, WHALE_FLEE + 1.2, T))
        R['whale']['ob'].matrix_basis = M3(pos, rot)
        CR.whale_swim(R['whale'], T * (1 + 1.8 * smooth(WHALE_FLEE, WHALE_FLEE + 0.6, T)), 0.12 + 0.12 * smooth(WHALE_FLEE, WHALE_FLEE + 0.5, T))
        eye = Euler(rot, 'XYZ').to_matrix() @ Vector((4.9, -0.78, 1.06)) + Vector(pos)
        lk = Vector((lerp(clamp(eye.x, -0.4, 1.4), 0.6, smooth(18.8, 20.5, T)), lerp(eye.y, 2.6, smooth(18.8, 20.5, T)), eye.z)); fov = lerp(50, 56, smooth(18.6, 20.5, T))
        cp = Vector((0.1, 1.55, 0.6)); focus = (eye - cp).length; fst = 4
    if id_ == 'squid':
        outside = 1; show(R['squid']['ob']); show(R['squid']['suck'])
        for a in R['squid']['arms']: a.hide_render = False
        squid_arms(R, T, smooth(21.2, 25.2, T), smooth(23.6, 25.6, T))
        lk = Vector((lerp(0.55, 0.95, smooth(23.5, 25.5, T)), lerp(1.85, 1.9, smooth(23.5, 25.5, T)), -3)); fov = lerp(50, 42, smooth(21, 26, T)); focus = 2.3; fst = 2.8
        if T > LIGHTS_OUT - 0.5:
            fl = [0.6, 0.15, 0.9, 0.05, 0.7, 0.0]; v = fl[min(5, int((T - (LIGHTS_OUT - 0.5)) / 0.1))]
            inside = 0 if T > LIGHTS_OUT + 0.1 else v; outside = inside
    if id_ == 'dark':
        inside = outside = 0; show(R['bio']); R['biomat'].node_tree.nodes['T'].outputs[0].default_value = T; R['biomat'].node_tree.nodes['amt'].outputs[0].default_value = 1.0
        R['bio'].matrix_basis = M3((0, (d * 0.6) % 9 - 4.5, 0))
        show(R['angler']['ob'])
        k = ease_out(smooth(LURE, LURE + 2.0, T)); ap = Vector((lerp(1.6, 0.06, k), lerp(0.9, 1.47, k) + 0.01 * math.sin(T * 2), lerp(-7.5, -1.5, k)))
        R['angler']['ob'].matrix_basis = M3(ap, (0.05 * math.sin(T * 1.3), math.pi / 2 + 0.25 * (1 - k), 0.06 * math.sin(T * 1.7)))
        on = 1.0 if T > LURE else 0.0
        R['angler']['light'].data.energy = 1.1 * on; R['angler']['lmat'].node_tree.nodes['Emission'].inputs[1].default_value = 60 * on * (0.9 + 0.1 * math.sin(T * 5))
        lit = smooth(LIGHTS_ON, LIGHTS_ON + 0.15, T) * (1 if (T > LIGHTS_ON + 0.25 or T < LIGHTS_ON + 0.12) else 0.3)
        inside = outside = lit
        cp = Vector((0.06, 1.5, 0.2)); lk = ap + Vector((0, 0.005, 0))
        fov = 30 if T < LURE else lerp(30, 15, smooth(LURE, LURE + 2.1, T)); fov = lerp(fov, 55, ease_out(smooth(LIGHTS_ON + 0.15, LIGHTS_ON + 0.9, T)))
        if T > LIGHTS_ON: lk = lk.lerp(Vector((0.1, 1.35, -5)), smooth(LIGHTS_ON + 0.2, LIGHTS_ON + 1.0, T))
        focus = (ap - cp).length; fst = 2.0
        exp = 0.25 * (1 - lit)
    if id_ == 'vent':
        outside = 1; show(R['vent']); show(R['wallR']); show(R['wallB'])
        R['vent'].matrix_basis = M3((0, (d - s['d0']) * 1.0 - 1.5, 0))
        R['smokemat'].node_tree.nodes['T'].outputs[0].default_value = T
        lk = Vector((2.4, lerp(-1.2, -0.2, smooth(33.5, 39.5, T)), -14)); cp = Vector((0.35, 1.6, 0.4)); fov = 54; focus = 13; fst = 5.6
        R['floods'][0]['tgt'] = (1.5, -3, -13); R['floods'][1]['tgt'] = (4.5, -2.5, -16)
    else:
        R['floods'][0]['tgt'] = (-1.5, -3.5, -15); R['floods'][1]['tgt'] = (2.8, -3.5, -15)
    if id_ == 'crack':
        outside = 1; show(R['wallR']); show(R['wallB'])
        R['wallR'].matrix_basis = M3((-8.5, d - s['d0'], 0)); R['wallB'].matrix_basis = M3((0, d - s['d0'], 37))
        sh = max(0, 1 - (T - CRACK) / 0.9) * (1 if T > CRACK else 0); cp = cp + Vector((0.035 * sh * math.sin(T * 61), 0.03 * sh * math.sin(T * 47), 0))
        lk = Vector((0.4, 1.3, -5)); fov = lerp(52, 46, smooth(39.5, 46.5, T)); focus = 2.2; fst = 4
        if CRACK < T < CRACK + 0.25: inside = 0.4 + 0.6 * abs(math.sin(T * 60))
    if id_ == 'snail':
        outside = 1; show(R['wallR']); show(R['wallB']); show(R['snail']['ob'])
        R['wallR'].matrix_basis = M3((-9.0, d - s['d0'] - 30, 0)); R['wallB'].matrix_basis = M3((0, d - s['d0'] - 30, 36))
        k = smooth(46.6, 50.8, T); sp = Vector((lerp(-0.6, 1.1, k), 1.3 + 0.05 * math.sin(T * 1.3), lerp(-2.0, -1.9, k)))
        R['snail']['ob'].matrix_basis = M3(sp, (0, math.pi + 0.15 * math.sin(T * 1.1), 0.05 * math.sin(T * 1.7)))
        for i, fn in enumerate(R['snail']['fins']): fn.rotation_euler = (0.35 * math.sin(T * 4.5) * (1 if i else -1), 0, 0)
        lk = sp + Vector((-0.15, 0.01, 0)); fov = 30; cp = Vector((0.1, 1.5, 0.5)); focus = (sp - cp).length; fst = 2.8
    if id_ == 'bottom':
        outside = 1; show(R['floor']); show(R['wallB'])
        for c in R['cukes']: show(c)
        rise = s['d1'] - d; R['floor'].matrix_basis = M3((0, -rise, 0)); R['wallB'].matrix_basis = M3((0, -rise - 20, 0))
        for c in R['cukes']: c.matrix_basis = M3((c['x'], -1.22 - rise, c['z']), (0, c['rot'], 0))
        bump_ = math.exp(-(T - ARRIVE) * 5) * math.sin((T - ARRIVE) * 30) if T > ARRIVE else 0; cp = cp + Vector((0, 0.04 * bump_, 0))
        lk = Vector((0.3, lerp(0.6, 1.0, smooth(53, 55, T)), -5))
        ks = math.exp(-(T - KNOCK) * 12) * math.sin((T - KNOCK) * 80) if KNOCK < T < KNOCK + 0.5 else 0; cp = cp + Vector((0, 0.006 * ks, 0))
        if T > KNOCK: lk.y += 0.25 * smooth(KNOCK, KNOCK + 0.6, T) * (1 - smooth(SUB + 0.2, SUB + 1.0, T))
        sub = R['sub']; vis = T > KNOCK - 0.5
        for o in [sub['root']] + sub['root'].children_recursive: o.hide_render = not vis
        down = ease_out(smooth(SUB, BOX - 0.1, T)); spos = Vector((0.4, lerp(6.0, 1.45, down) + 0.03 * math.sin(T * 1.4), -4.9))
        srot = (0, 0.12 - 0.08 * down, 0.02 * math.sin(T * 0.9))
        lampOn = 1.0 if T > SUB - 0.2 else 0.0
        for sp_ in sub['spots']: sp_.data.energy = 900 * lampOn
        sub['inner'].data.energy = 2.5
        ext = ease_out(smooth(BOX - 0.4, BOX + 0.3, T))
        a1, a2 = lerp(-0.9, -0.3, ext), lerp(1.5, 0.32, ext)
        sub['arm']['pivot'].matrix_basis = M3((-1.0, -0.35, 1.0), (a1, 0.15, 0))
        sub['arm']['elbow'].matrix_basis = M3((0, 0, 1.3), (a2, 0, 0))
        sub['arm']['wrist'].matrix_basis = M3((0, 0, 1.2), (-(a1 + a2), 0, 0))
        sub['arm']['box'].matrix_basis = M3((0, 0, 0.3), (0, 0, 0.04 * math.sin(T * 1.1)))
        sub['root'].matrix_basis = M3(spos, srot, 0.7)
        bpy.context.view_layer.update()
        bw = sub['arm']['box'].matrix_world.translation; bw3 = Vector((bw.x, bw.z, -bw.y))
        spos.x += (0.2 - bw3.x) * ext; sub['root'].matrix_basis = M3(spos, srot, 0.7)
        sub['hand'].matrix_basis = M3((0.5 + 0.03 * math.sin(T * 9), 0.09 + (0.02 if T > 56 else -0.06) + 0.62, 0.72), (0, 0, 0))
        lk = Vector((0.25, lerp(lk.y, 1.35, smooth(SUB, BOX, T)), -5)); cp = Vector((cp.x, cp.y, 0.75)); focus = 3.6; fst = 4
        exp = -0.2
    lights(R, inside, outside, d)
    for fl in R['floods']: aim(fl, P(*fl['tgt']))
    snow_at(R, d, T)
    if id_ in ('crack', 'snail', 'bottom'): update_crack(R, T)
    else: R['crackob'].hide_render = True
    cp = cp + Vector((noise1(T * 0.6, 3) * 0.012, noise1(T * 0.6, 7) * 0.01, 0))
    set_cam(cam, tuple(cp), tuple(lk), fov, focus, fst)
    sc.view_settings.exposure = exp

def main():
    argv = sys.argv[1:]
    samples = 40; res = 720
    if '--samples' in argv: i = argv.index('--samples'); samples = int(argv[i + 1]); del argv[i:i + 2]
    if '--res' in argv: i = argv.index('--res'); res = int(argv[i + 1]); del argv[i:i + 2]
    out, a, b = argv[0], int(argv[1]), int(argv[2]); step = int(argv[3]) if len(argv) > 3 else 1
    os.makedirs(out, exist_ok=True)
    sc, cam = setup(samples, res); t0 = time.time(); R = build_all(); print('aufgebaut in %.1fs' % (time.time() - t0), flush=True)
    frames = [int(x) for x in os.environ['FRAMES'].split(',')] if os.environ.get('FRAMES') else range(a, b, step)
    for f in frames:
        fn = os.path.join(out, 'f%05d.png' % f)
        if os.path.exists(fn) and not os.environ.get('FORCE'): continue
        t1 = time.time(); update(R, cam, f); bpy.context.view_layer.update()
        sc.render.filepath = fn + '.tmp.png'; bpy.ops.render.render(write_still=True); os.replace(fn + '.tmp.png', fn)
        print('frame %d %.1fs' % (f, time.time() - t1), flush=True)

if __name__ == '__main__':
    main()
