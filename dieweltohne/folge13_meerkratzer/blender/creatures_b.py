# Meeresbewohner und Tauchboot für die Blender-Fassung. Geometrie in three.js-Koordinaten (y oben), siehe lib_b.mesh_obj.
import bpy, bmesh, math, random
from mathutils import Vector, Matrix, Euler, noise
from lib_b import *

# ======================= Fisch (Sardine) =======================
def fish_mats():
    m, nb, out = new_mat('fish')
    z = sep(nb, coords(nb, 'Object'))[2]  # Blender-lokal: z = oben
    k = mr(nb, z, -0.012, 0.016)
    col = nb.ramp(k, [(0.0, (0.85, 0.88, 0.9, 1)), (0.55, (0.62, 0.68, 0.72, 1)), (0.8, (0.12, 0.22, 0.28, 1)), (1.0, (0.05, 0.1, 0.14, 1))])
    sc = noise_tex(nb, coords(nb, 'Object'), 900, 2)
    bsdf(nb, out, col, rough=0.22, metal=0.85, normal=bump(nb, sc.outputs['Fac'], 0.15, 0.0005), Coat_Weight=0.4)
    fin, nb2, out2 = new_mat('fishfin')
    bsdf(nb2, out2, (0.55, 0.6, 0.62), rough=0.35, Transmission_Weight=0.6, Alpha=0.75)
    return m, fin

def fish_variant(i, mat, fin, phase):
    bm = bmesh.new()
    L = 0.2
    def prof(u):
        h = 0.024 * math.sin(math.pi * min(1, (u + 0.06) / 1.0)) ** 0.75 + 0.002
        w = 0.011 * math.sin(math.pi * min(1, (u + 0.05) / 1.02)) ** 0.9 + 0.0015
        return (h, w, 2.0, 0.002 * u)
    def xf(co, u):  # Schwanzschlag (seitlich)
        co.z += 0.018 * (u ** 2) * math.sin(phase - 3.5 * u); return co
    hull_bm(L, prof, 22, 12, bm, xf)
    # Schwanzflosse (gegabelt)
    tz = 0.018 * math.sin(phase - 3.5)
    vs = [bm.verts.new(Vector(c)) for c in [(0.19, 0.003, tz), (0.245, 0.03, tz + 0.006 * math.sin(phase - 4)), (0.228, 0.002, tz + 0.004 * math.sin(phase - 4)), (0.245, -0.026, tz + 0.006 * math.sin(phase - 4)), (0.19, -0.002, tz)]]
    bm.faces.new(vs)
    ob = mesh_obj('fishv%d' % i, bm, [mat, fin], c='LIB')
    ob.data.polygons[-1].material_index = 1
    return ob.data

# ======================= Pottwal =======================
def whale_mat():
    m, nb, out = new_mat('whale')
    o = coords(nb, 'Object'); x, y, z = sep(nb, o)[:3]
    n1 = noise_tex(nb, o, 0.35, 6, 0.6)
    base = nb.mix(n1.outputs['Fac'], (0.018, 0.017, 0.017, 1), (0.055, 0.05, 0.047, 1))
    # Narben: lange helle Kratzer + kreisrunde Saugnapf-Narben (vom Riesenkalmar)
    vm = nb.n('ShaderNodeVectorMath', operation='MULTIPLY'); nb.l(o, vm.inputs[0]); vm.inputs[1].default_value = (0.25, 1.6, 1.6)
    n2 = noise_tex(nb, vm.outputs[0], 2.2, 2, 0.5)
    ln = nb.math('ABSOLUTE', nb.math('SUBTRACT', n2.outputs['Fac'], 0.5))
    scar = nb.math('LESS_THAN', ln, 0.004)
    vor = nb.n('ShaderNodeTexVoronoi'); nb.l(o, vor.inputs['Vector']); vor.inputs['Scale'].default_value = 4.0
    ring = nb.math('MULTIPLY', nb.math('MULTIPLY', nb.math('GREATER_THAN', vor.outputs['Distance'], 0.08), nb.math('LESS_THAN', vor.outputs['Distance'], 0.092)), nb.math('LESS_THAN', sep(nb, vor.outputs['Color'])[0], 0.25))
    head = mr(nb, x, 6.5, 3.5)
    sc = nb.math('MULTIPLY', nb.math('MAXIMUM', scar, nb.math('MULTIPLY', ring, 0.7)), nb.math('ADD', nb.math('MULTIPLY', head, 0.8), 0.25))
    col = nb.mix(nb.math('MULTIPLY', sc, 0.6), base, (0.2, 0.19, 0.18, 1))
    mouth = nb.math('MULTIPLY', mr(nb, z, -0.95, -1.25), mr(nb, x, 5.2, 4.2))
    col = nb.mix(nb.math('MULTIPLY', mouth, 0.85), col, (0.62, 0.6, 0.56, 1))
    # Falten (Pflaumenhaut) hinter dem Kopf
    wv = nb.n('ShaderNodeTexWave', wave_type='BANDS', bands_direction='X'); nb.l(o, wv.inputs['Vector'])
    wv.inputs['Scale'].default_value = 3.2; wv.inputs['Distortion'].default_value = 14; wv.inputs['Detail'].default_value = 5; wv.inputs['Detail Scale'].default_value = 1.5
    wr = nb.math('MULTIPLY', wv.outputs['Fac'], nb.math('MULTIPLY', mr(nb, x, 4.0, 6.0), mr(nb, x, 12.5, 10.0)))
    fine = noise_tex(nb, o, 18, 8, 0.6)
    h = nb.math('ADD', nb.math('MULTIPLY', wr, 1.0), nb.math('MULTIPLY', fine.outputs['Fac'], 0.25))
    h = nb.math('SUBTRACT', h, nb.math('MULTIPLY', sc, 0.4))
    bsdf(nb, out, col, rough=0.55, normal=bump(nb, h, 0.7, 0.05), Coat_Weight=0.3, Coat_Roughness=0.3)
    return m

def whale():
    L = 14.0; mat = whale_mat(); bm = bmesh.new()
    def prof(u):
        if u < 0.025: k = math.sqrt(u / 0.025); h, w, ex = lerp(0.95, 1.32, k), lerp(0.72, 1.02, k), 3.0
        elif u < 0.33: k = (u - 0.025) / 0.305; h, w, ex = 1.32 + 0.08 * k, 1.02 + 0.06 * k, 3.1 - 0.4 * k
        elif u < 0.45: k = (u - 0.33) / 0.12; h, w, ex = lerp(1.4, 1.42, k), lerp(1.08, 1.12, k), lerp(2.7, 2.15, k)
        elif u < 0.64: k = (u - 0.45) / 0.19; h, w, ex = lerp(1.42, 1.28, k), lerp(1.12, 0.98, k), 2.1
        else: k = (u - 0.64) / 0.36; h, w, ex = lerp(1.28, 0.24, k ** 0.8), lerp(0.98, 0.14, k ** 0.95), 2.0 + 0.4 * k
        return (h, w, ex, -0.05 * u)
    def xf(co, u):
        # Höcker und "Knöchel" auf dem Rücken, Kiel am Schwanzstiel
        if co.y > 0:
            top = co.y / max(0.2, prof(u)[0])
            hump = 0.2 * math.exp(-((u - 0.655) / 0.025) ** 2)
            kn = sum(0.06 * math.exp(-((u - c) / 0.012) ** 2) for c in (0.72, 0.76, 0.8, 0.84, 0.88))
            co.y += (hump + kn) * max(0, top) ** 3
        if co.y < 0 and u > 0.75: co.y -= 0.18 * ((u - 0.75) / 0.25) * max(0, -co.y / max(0.2, prof(u)[0])) ** 4
        # Kopf vorne oben leicht überhängend
        if u < 0.08 and co.y > 0.4: co.x -= 0.15 * (1 - u / 0.08)
        return co
    hull_bm(L, prof, 140, 48, bm, xf)
    # Unterkiefer: schmal, unter dem Kopf
    jaw = lambda u: (lerp(0.13, 0.26, u), lerp(0.15, 0.36, u ** 0.7), 2.2, 0)
    hull_bm(4.4, jaw, 30, 16, bm, lambda co, u: Vector((co.x + 0.55, co.y - 1.18 + 0.05 * u, co.z)))
    # Brustflossen
    for s in (-1, 1):
        fb = bmesh.new(); hull_bm(1.3, lambda u: (0.06 * math.sin(math.pi * min(1, u + 0.05)) + 0.01, 0.32 * math.sin(math.pi * min(1, u * 0.95 + 0.05)) ** 0.6 + 0.02, 2, 0), 16, 12, fb)
        bmesh.ops.transform(fb, matrix=Matrix.Translation((4.6, -0.95, s * 1.05)) @ Euler((s * 0.5, s * 0.4, -0.6)).to_matrix().to_4x4(), verts=fb.verts)
        mesh_tmp = bpy.data.meshes.new('t'); fb.to_mesh(mesh_tmp); fb.free(); bm.from_mesh(mesh_tmp); bpy.data.meshes.remove(mesh_tmp)
    # Fluke (dreieckig mit Kerbe)
    bm.verts.ensure_lookup_table(); nf = len(bm.verts)
    outline = []
    for i in range(25):
        t = i / 24; z = lerp(0, 2.15, t); x = 13.75 + 0.15 + 1.25 * t ** 1.3 + 0.35 * math.sin(t * math.pi) ** 2
        outline.append((x, z))
    trail = []
    for i in range(25):
        t = 1 - i / 24; z = lerp(0.12, 2.15, t); x = 13.75 + 1.75 + 0.55 * t - 0.4 * (1 - t) ** 3
        trail.append((x, z))
    pts2 = outline + trail
    full = [(x, z) for x, z in pts2] + [(x, -z) for x, z in reversed(pts2)]
    top = [bm.verts.new(Vector((x, 0.06, z))) for x, z in full]; bot = [bm.verts.new(Vector((x, -0.06, z))) for x, z in full]
    bm.faces.new(top); bm.faces.new(list(reversed(bot)))
    for i in range(len(full)):
        j = (i + 1) % len(full); bm.faces.new((top[i], bot[i], bot[j], top[j]))
    ob = mesh_obj('whale', bm, mat, subsurf=1)
    # Auge (Kamera-Seite = three +z)
    eb = bmesh.new(); sphere_bm(0.085, 24, 16, eb, Matrix.Translation((4.9, -0.78, 1.06)) @ Matrix.Diagonal((1.3, 0.8, 0.55, 1)))
    eye = mesh_obj('whale_eye', eb, principled('weye', (0.01, 0.01, 0.012), 0.05, Coat_Weight=1.0))
    eye.parent = ob
    me = ob.data; base = [v.co.copy() for v in me.vertices]
    ob['L'] = L
    return {'ob': ob, 'base': base, 'eye': eye, 'nf': nf}

def whale_swim(w, T, amp):
    """Auf- und Abschlag (vertikal, wie echte Wale). Lokale Blender-Koordinaten: x = Körperachse, z = oben."""
    me = w['ob'].data; co = []
    ph = T * 1.6
    sl = lambda x: amp * smooth(5.0, 14.5, x) ** 2 * math.sin(ph - 0.35 * x)
    xa = 13.85; za = sl(xa); slope = (sl(xa + 0.05) - sl(xa - 0.05)) / 0.1
    ang = math.atan(slope) + 0.35 * amp * 4 * math.sin(ph - 0.35 * xa - 0.9)
    ca, sa = math.cos(ang), math.sin(ang)
    for i, v in enumerate(w['base']):
        if i >= w['nf']:  # Fluke dreht als Ganzes
            dx, dz = v.x - xa, v.z
            co.extend((xa + dx * ca - dz * sa, v.y, za + dx * sa + dz * ca))
        else:
            co.extend((v.x, v.y, v.z + sl(v.x)))
    me.vertices.foreach_set('co', co); me.update()

# ======================= Riesenkalmar =======================
def squid_mats():
    m, nb, out = new_mat('squid')
    o = coords(nb, 'Object')
    vor = nb.n('ShaderNodeTexVoronoi'); nb.l(o, vor.inputs['Vector']); vor.inputs['Scale'].default_value = 38
    dots = mr(nb, vor.outputs['Distance'], 0.3, 0.12)
    n1 = noise_tex(nb, o, 3, 5)
    base = nb.mix(n1.outputs['Fac'], (0.07, 0.01, 0.008, 1), (0.17, 0.035, 0.022, 1))
    col = nb.mix(nb.math('MULTIPLY', dots, 0.8), base, (0.07, 0.008, 0.008, 1))
    bsdf(nb, out, col, rough=0.32, normal=bump(nb, nb.math('ADD', noise_tex(nb, o, 22, 6).outputs['Fac'], nb.math('MULTIPLY', vor.outputs['Distance'], 0.5)), 0.45, 0.004), Subsurface_Weight=0.35, Subsurface_Radius=(0.05, 0.012, 0.008), Coat_Weight=0.7, Coat_Roughness=0.15)
    # Arme: Oberseite rot, Unterseite (Saugnapfseite) blass
    a, nb2, out2 = new_mat('squidarm')
    uv = sep(nb2, coords(nb2, 'UV'))
    side = mr(nb2, nb2.math('ABSOLUTE', nb2.math('SUBTRACT', uv[0], 0.75)), 0.08, 0.2)
    o2 = coords(nb2, 'Object')
    vor2 = nb2.n('ShaderNodeTexVoronoi'); nb2.l(o2, vor2.inputs['Vector']); vor2.inputs['Scale'].default_value = 60
    dots2 = nb2.math('LESS_THAN', vor2.outputs['Distance'], 0.2)
    top = nb2.mix(nb2.math('MULTIPLY', dots2, 0.8), (0.14, 0.025, 0.017, 1), (0.04, 0.005, 0.005, 1))
    col2 = nb2.mix(side, (0.6, 0.36, 0.3, 1), top)
    wvb = nb2.n('ShaderNodeTexWave', wave_type='BANDS', bands_direction='Y'); nb2.l(coords(nb2, 'UV'), wvb.inputs['Vector']); wvb.inputs['Scale'].default_value = 90; wvb.inputs['Distortion'].default_value = 4
    bsdf(nb2, out2, col2, rough=0.3, normal=bump(nb2, nb2.math('ADD', noise_tex(nb2, o2, 45, 5).outputs['Fac'], nb2.math('MULTIPLY', wvb.outputs['Fac'], 0.4)), 0.4, 0.003), Subsurface_Weight=0.4, Subsurface_Radius=(0.03, 0.008, 0.005), Coat_Weight=0.8, Coat_Roughness=0.1)
    s = principled('sucker', (0.88, 0.74, 0.68), 0.2, Coat_Weight=0.9, Subsurface_Weight=0.5, Subsurface_Radius=(0.01, 0.004, 0.003))
    return m, a, s

def squid():
    mat, arm_m, suck_m = squid_mats(); bm = bmesh.new()
    def mprof(u):
        r = lerp(0.24, 0.34, u / 0.15) if u < 0.15 else lerp(0.34, 0.04, ((u - 0.15) / 0.85) ** 1.6)
        return (r, r * 0.96, 2, 0)
    hull_bm(2.6, mprof, 50, 28, bm)
    # Flossen am Mantelende
    for s in (-1, 1):
        fb = bmesh.new(); sphere_bm(1, 20, 12, fb, Matrix.Translation((2.35, 0, s * 0.2)) @ Matrix.Diagonal((0.3, 0.02, 0.26, 1)))
        tmp = bpy.data.meshes.new('t'); fb.to_mesh(tmp); fb.free(); bm.from_mesh(tmp); bpy.data.meshes.remove(tmp)
    sphere_bm(0.3, 32, 20, bm, Matrix.Translation((-0.15, 0, 0)) @ Matrix.Diagonal((1.25, 0.95, 1.05, 1)))
    ob = mesh_obj('squid', bm, mat, subsurf=1)
    eyes = []
    for s in (1, -1):
        eb = bmesh.new(); sphere_bm(0.14, 32, 20, eb, Matrix.Translation((-0.18, 0.02, s * 0.27)) @ Matrix.Diagonal((1, 1, 0.55, 1)))
        iris = mesh_obj('sq_iris%d' % s, eb, principled('sqiris', (0.55, 0.5, 0.38), 0.25, 0.6, Coat_Weight=1.0)); iris.parent = ob
        pb = bmesh.new(); sphere_bm(0.092, 32, 20, pb, Matrix.Translation((-0.18, 0.02, s * 0.322)) @ Matrix.Diagonal((1, 1, 0.45, 1)))
        pu = mesh_obj('sq_pupil%d' % s, pb, principled('sqpupil', (0.004, 0.004, 0.005), 0.02, Coat_Weight=1.0)); pu.parent = ob
        eyes.append(pu)
    arms = [tube_obj('sqarm%d' % i, 64, 18, arm_m) for i in range(10)]
    suck = bpy.data.objects.new('suckers', bpy.data.meshes.new('suckers')); coll('SEA').objects.link(suck); suck.data.materials.append(suck_m)
    # Saugnapf-Vorlage (Achse +Z, Radius 1)
    sb = bmesh.new(); cyl_bm(1.0, 0.85, 0.55, 16, sb, Matrix.Translation((0, 0, 0.27)), caps=False)
    bmesh.ops.create_circle(sb, cap_ends=True, segments=16, radius=0.6, matrix=Matrix.Translation((0, 0, 0.3)))
    tv = [v.co.copy() for v in sb.verts]; tf = [[v.index for v in f.verts] for f in sb.faces]; sb.free()
    return {'ob': ob, 'arms': arms, 'suck': suck, 'tv': tv, 'tf': tf, 'eyes': eyes}

def suckers_set(sq, items):
    """items: Liste (Position, Normale, Radius) in Blender-Weltkoordinaten"""
    verts, faces = [], []
    for p, n, r in items:
        m = Matrix.Translation(p) @ n.to_track_quat('Z', 'Y').to_matrix().to_4x4() @ Matrix.Diagonal((r, r, r, 1))
        o = len(verts); verts.extend([m @ v for v in sq['tv']]); faces.extend([[o + i for i in f] for f in sq['tf']])
    me = sq['suck'].data; me.clear_geometry(); me.from_pydata(verts, [], faces)
    for pl in me.polygons: pl.use_smooth = True
    me.update()

# ======================= Anglerfisch (15 cm) =======================
def angler():
    skin, nb, out = new_mat('angler')
    o = coords(nb, 'Object'); n1 = noise_tex(nb, o, 140, 6)
    vor = nb.n('ShaderNodeTexVoronoi'); nb.l(o, vor.inputs['Vector']); vor.inputs['Scale'].default_value = 260
    h = nb.math('ADD', n1.outputs['Fac'], nb.math('MULTIPLY', vor.outputs['Distance'], -0.6))
    col = nb.mix(noise_tex(nb, o, 40, 3).outputs['Fac'], (0.03, 0.02, 0.016, 1), (0.1, 0.065, 0.05, 1))
    bsdf(nb, out, col, rough=0.55, normal=bump(nb, h, 0.6, 0.0015), Sheen_Weight=0.6, Sheen_Roughness=0.4, Coat_Weight=0.3, Coat_Roughness=0.3)
    bm = bmesh.new()
    def prof(u):
        if u < 0.35: k = u / 0.35; h, w = lerp(0.026, 0.06, k ** 0.6), lerp(0.034, 0.052, k ** 0.6)
        else: k = (u - 0.35) / 0.65; h, w = lerp(0.06, 0.014, k ** 1.2), lerp(0.052, 0.01, k ** 1.1)
        return (h, w, 2.0, 0.004)
    hull_bm(0.15, prof, 40, 28, bm, lambda co, u: Vector((co.x - 0.075, co.y, co.z)))
    # Unterkiefer, vorgeschoben
    hull_bm(0.075, lambda u: (lerp(0.016, 0.028, u), lerp(0.03, 0.05, u ** 0.6), 2, 0), 16, 20, bm, lambda co, u: Vector((co.x - 0.092, co.y - 0.03 + 0.004 * u, co.z)))
    ob = mesh_obj('angler', bm, skin, subsurf=1)
    # Rachen
    rb = bmesh.new(); sphere_bm(0.042, 24, 14, rb, Matrix.Translation((-0.075, -0.012, 0)) @ Matrix.Diagonal((0.55, 0.55, 0.95, 1)))
    mesh_obj('angler_mouth', rb, principled('amouth', (0.004, 0.002, 0.002), 0.7)).parent = ob
    # Zähne: lange gebogene, durchscheinende Nadeln
    tb = bmesh.new(); r = random.Random(8)
    for i in range(26):
        up = i < 11; n = 11 if up else 15; a = ((i if up else i - 11) + r.random() * 0.4) / (n - 1) * math.pi * 0.86 - math.pi * 0.43
        ln = 0.012 + r.random() ** 2 * 0.028
        base = Vector((-0.083 - 0.022 * math.cos(a) + (0.0 if up else -0.012), 0.004 if up else -0.024, 0.044 * math.sin(a)))
        d = Vector((r.random() * 0.3 - 0.15 - 0.25, -1 if up else 1, r.random() * 0.2 - 0.1)).normalized()
        q = d.to_track_quat('Z', 'X').to_matrix().to_4x4()
        cyl_bm(0.0016, 0.0002, ln, 6, tb, Matrix.Translation(base + d * ln / 2) @ q)
    mesh_obj('angler_teeth', tb, principled('tooth', (0.85, 0.82, 0.74), 0.15, Transmission_Weight=0.5, Coat_Weight=0.8)).parent = ob
    # Flossen
    fin = principled('afin', (0.03, 0.025, 0.022), 0.5, Transmission_Weight=0.3, Alpha=0.85)
    fb = bmesh.new(); sphere_bm(1, 16, 10, fb, Matrix.Translation((0.1, 0.004, 0)) @ Matrix.Diagonal((0.035, 0.03, 0.003, 1)))
    for s in (-1, 1): sphere_bm(1, 12, 8, fb, Matrix.Translation((0.02, -0.01, s * 0.05)) @ Euler((0, s * 0.6, 0)).to_matrix().to_4x4() @ Matrix.Diagonal((0.022, 0.016, 0.002, 1)))
    mesh_obj('angler_fins', fb, fin).parent = ob
    # Augen: winzig, milchig
    eb = bmesh.new()
    for s in (-1, 1): sphere_bm(0.0045, 12, 8, eb, Matrix.Translation((-0.045, 0.036, s * 0.033)))
    mesh_obj('angler_eyes', eb, principled('aeye', (0.6, 0.66, 0.68), 0.1, Coat_Weight=1)).parent = ob
    # Angel (Illicium) und Leuchtköder (Esca)
    pts = [Vector(p) for p in [(-0.02, 0.058, 0), (-0.035, 0.09, 0), (-0.06, 0.118, 0), (-0.095, 0.128, 0), (-0.118, 0.115, 0)]]
    sb = bmesh.new()
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]; d = b - a
        cyl_bm(0.0019, 0.0015, d.length, 6, sb, Matrix.Translation((a + b) / 2) @ d.to_track_quat('Z', 'X').to_matrix().to_4x4())
        sphere_bm(0.0018, 6, 4, sb, Matrix.Translation(b))
    mesh_obj('angler_stalk', sb, skin).parent = ob
    lm = emission('lure', (0.35, 0.85, 1.0), 25.0)
    lb = bmesh.new(); sphere_bm(0.0045, 16, 10, lb, Matrix.Translation((-0.12, 0.106, 0)))
    lure = mesh_obj('angler_lure', lb, lm); lure.parent = ob; ray_vis(lure, shadow=False)
    li = light('angler_light', 'POINT', (0, 0, 0), 0.0, (0.55, 0.92, 1.0), shadow_soft_size=0.004)
    li.parent = ob; li.location = P(-0.12, 0.106, 0)
    return {'ob': ob, 'lure': lure, 'lmat': lm, 'light': li}

# ======================= Scheibenbauch (30 cm, durchscheinend) =======================
def snailfish():
    m = principled('snail', (0.92, 0.36, 0.38), 0.2, Subsurface_Weight=0.6, Subsurface_Radius=(0.05, 0.02, 0.018), Subsurface_Scale=1.0, Transmission_Weight=0.1, Coat_Weight=0.8, Coat_Roughness=0.05, IOR=1.36)
    bm = bmesh.new()
    def prof(u):
        if u < 0.2: k = u / 0.2; h, w = lerp(0.012, 0.064, k ** 0.35), lerp(0.014, 0.06, k ** 0.35)
        else: k = (u - 0.2) / 0.8; h, w = lerp(0.06, 0.004, k ** 0.6), lerp(0.058, 0.002, k ** 0.7)
        return (h, w, 2, -0.004 * u)
    hull_bm(0.3, prof, 48, 24, bm)
    fm = principled('snailfin', (0.95, 0.8, 0.78), 0.15, Transmission_Weight=0.85, Alpha=0.55, Coat_Weight=0.6)
    fb2 = bmesh.new()
    # durchgehender Flossensaum oben und unten bis zur Schwanzspitze
    for sgn in (1, -1):
        prev = None
        for i in range(25):
            u = 0.35 + 0.65 * i / 24; h = prof(u)[0]; fh = 0.022 * math.sin(math.pi * min(1, (i / 24) * 0.9 + 0.1))
            a = fb2.verts.new((u * 0.3, sgn * h * 0.9, 0)); b = fb2.verts.new((u * 0.3, sgn * (h + fh), 0))
            if prev: fb2.faces.new((prev[0], prev[1], b, a) if sgn > 0 else (prev[1], prev[0], a, b))
            prev = (a, b)
    fo = mesh_obj('snail_ribbon', fb2, fm)
    ob = mesh_obj('snail', bm, m, subsurf=1); fo.parent = ob
    fins = []
    for s in (1, -1):
        fb = bmesh.new(); sphere_bm(1, 16, 8, fb, Matrix.Translation((0.07, -0.025, s * 0.05)) @ Matrix.Diagonal((0.05, 0.003, 0.045, 1)))
        f = mesh_obj('snail_fin%d' % s, fb, fm); f.parent = ob; fins.append(f)
    eb = bmesh.new()
    for s in (1, -1): sphere_bm(0.0075, 12, 8, eb, Matrix.Translation((0.03, 0.02, s * 0.05)))
    mesh_obj('snail_eyes', eb, principled('seye', (0.02, 0.02, 0.025), 0.05, Coat_Weight=1)).parent = ob
    return {'ob': ob, 'fins': fins}

# ======================= Tauchboot =======================
def submersible():
    white = principled('subwhite', (0.62, 0.62, 0.6), 0.45, Coat_Weight=0.3)
    orange = principled('suborange', (0.75, 0.22, 0.03), 0.45)
    dark = principled('subdark', (0.03, 0.035, 0.04), 0.4, 0.6)
    ti = principled('subti', (0.45, 0.45, 0.43), 0.32, 1.0)
    acr = glass_mat('acrylic', (0.95, 0.98, 1.0), 0.02, 1.49)
    parts = []
    def add(name, bm, mat, sub=0, parent=None):
        o = mesh_obj(name, bm, mat, subsurf=sub); parts.append(o); return o
    # Verkleidung oben (abgerundet)
    b = box_bm(-1.8, 1.8, 0.85, 1.85, -1.1, 1.1)
    o = add('sub_top', b, white); md = o.modifiers.new('bev', 'BEVEL'); md.width = 0.22; md.segments = 5
    for pl in o.data.polygons: pl.use_smooth = True
    add('sub_stripe', box_bm(-1.82, 1.82, 1.05, 1.2, -1.12, 1.12), orange)
    add('sub_plate', box_bm(-1.85, 1.85, 0.74, 0.86, -1.15, 1.15), dark)
    # Druckkugel aus Titan mit Sichtfenster nach vorn (+z)
    add('sub_sphere', sphere_bm(0.85, 48, 32, mat=Matrix.Translation((0.4, 0, 0.1))), ti)
    rb = bmesh.new(); bmesh.ops.create_cone(rb, cap_ends=False, segments=40, radius1=0.3, radius2=0.29, depth=0.12, matrix=Matrix.Translation((0.4, 0.05, 0.94)))
    o = add('sub_ring', rb, dark); md = o.modifiers.new('sol', 'SOLIDIFY'); md.thickness = 0.05
    dome = add('sub_dome', sphere_bm(0.26, 40, 24, mat=Matrix.Translation((0.4, 0.05, 0.92)) @ Matrix.Diagonal((1, 1, 0.55, 1))), acr)
    # Innen: warmes, gedämpftes Licht + Pilot
    inner = light('sub_inner', 'POINT', (0, 0, 0), 2.5, (1.0, 0.72, 0.45), shadow_soft_size=0.05); parts.append(inner); inner['local'] = (0.4, 0.25, 0.55)
    skin = principled('pilotskin', (0.55, 0.35, 0.26), 0.5, Subsurface_Weight=0.3)
    hair = principled('pilothair', (0.03, 0.02, 0.015), 0.6)
    pil = add('sub_pilot', sphere_bm(0.075, 24, 16, mat=Matrix.Translation((0.4, 0.02, 0.68))), skin, 1)
    add('sub_hair', sphere_bm(0.079, 24, 16, mat=Matrix.Translation((0.4, 0.04, 0.665)) @ Matrix.Diagonal((1, 0.9, 0.9, 1))), hair)
    add('sub_body', sphere_bm(0.15, 20, 12, mat=Matrix.Translation((0.4, -0.18, 0.62)) @ Matrix.Diagonal((1.2, 0.8, 0.6, 1))), principled('pilotsuit', (0.05, 0.08, 0.12), 0.8))
    hand = add('sub_hand', sphere_bm(0.028, 16, 10, mat=Matrix.Diagonal((1, 1.3, 0.6, 1))), skin, 1)
    # Rahmen, Kufen
    for x in (-1.6, 1.6):
        for z in (-0.95, 0.95): add('sub_post', cyl_bm(0.05, 0.05, 1.6, 12, mat=Matrix.Translation((x, 0.1, z)) @ Euler((math.pi / 2, 0, 0)).to_matrix().to_4x4()), white)
    for z in (-0.95, 0.95): add('sub_skid', cyl_bm(0.06, 0.06, 3.6, 12, mat=Matrix.Translation((0, -0.7, z)) @ Euler((0, math.pi / 2, 0)).to_matrix().to_4x4()), white)
    # Strahlruder (ummantelt)
    for x, z in ((-1.85, 0.9), (-1.85, -0.9), (1.85, 0.9), (1.85, -0.9)):
        tb = bmesh.new(); bmesh.ops.create_cone(tb, cap_ends=False, segments=24, radius1=0.2, radius2=0.2, depth=0.4, matrix=Matrix.Translation((x, 0.4, z)) @ Euler((0, math.pi / 2, 0)).to_matrix().to_4x4())
        o = add('sub_thr', tb, dark); md = o.modifiers.new('sol', 'SOLIDIFY'); md.thickness = 0.03
        add('sub_hub', sphere_bm(0.06, 12, 8, mat=Matrix.Translation((x, 0.4, z))), dark)
    # Scheinwerfer (Gehäuse + Leuchtfläche)
    led = emission('subled', (1.0, 0.95, 0.88), 6.0)
    for x in (-1.2, -0.6, 1.0, 1.5):
        add('sub_lamph', cyl_bm(0.09, 0.08, 0.12, 20, mat=Matrix.Translation((x, 0.66, 1.13))), dark)
        add('sub_lamp', cyl_bm(0.07, 0.07, 0.01, 20, mat=Matrix.Translation((x, 0.66, 1.195))), led)
    spots = []
    for x in (-0.9, 1.25):
        s = light('sub_spot', 'SPOT', (0, 0, 0), 0, (1.0, 0.94, 0.86), spot_size=math.radians(55), spot_blend=0.6, shadow_soft_size=0.05); s['local'] = (x, 0.66, 1.25); parts.append(s); spots.append(s)
        s['rot'] = (-1.25, 0, 0)
    # Greifarm
    arm = {}
    pivot = bpy.data.objects.new('sub_armpivot', None); coll('SEA').objects.link(pivot); arm['pivot'] = pivot
    def seg(name, L, r, mat):
        o = mesh_obj(name, cyl_bm(r, r * 0.9, L, 16, mat=Matrix.Translation((0, 0, L / 2))), mat); parts.append(o); return o
    s1 = seg('sub_arm1', 1.3, 0.07, white); s1.parent = pivot
    e = bpy.data.objects.new('sub_elbow', None); coll('SEA').objects.link(e); e.parent = pivot; arm['elbow'] = e
    j = add('sub_joint', sphere_bm(0.1, 16, 10), dark); j.parent = e
    s2 = seg('sub_arm2', 1.2, 0.06, white); s2.parent = e
    w = bpy.data.objects.new('sub_wrist', None); coll('SEA').objects.link(w); w.parent = e; arm['wrist'] = w
    j2 = add('sub_joint2', cyl_bm(0.07, 0.07, 0.14, 16, mat=Matrix.Translation((0, 0, 0.05))), dark); j2.parent = w
    for s in (1, -1):
        g = add('sub_jaw', box_bm(s * 0.1, s * 0.14, -0.02, 0.02, 0.05, 0.3), dark); g.parent = w
    # Pizzakarton
    pm, nb, out = new_mat('pizzalid')
    tx = nb.n('ShaderNodeTexImage'); tx.image = bpy.data.images.load(os.path.join(TEX, 'pizza.png'))
    bsdf(nb, out, tx.outputs['Color'], rough=0.85)
    card = principled('card', (0.55, 0.47, 0.34), 0.9)
    bb = box_bm(-0.285, 0.285, -0.285, 0.285, -0.035, 0.035)
    boxo = mesh_obj('pizzabox', bb, [card, pm], smooth_shade=False); parts.append(boxo)
    me = boxo.data; uv = me.uv_layers.new()
    for pl in me.polygons:
        n = pl.normal
        if n.y < -0.9:  # three +z (Deckel zur Kamera) -> Blender -y
            pl.material_index = 1
            for li, vi in zip(pl.loop_indices, pl.vertices):
                v = me.vertices[vi].co; uv.data[li].uv = (v.x / 0.57 + 0.5, v.z / 0.57 + 0.5)
    boxo.parent = w; arm['box'] = boxo
    # Gesamtgruppe
    root = bpy.data.objects.new('sub', None); coll('SEA').objects.link(root)
    for o in parts:
        if o.parent is None: o.parent = root
        if 'local' in o: o.matrix_basis = M3(o['local'], o.get('rot', (0, 0, 0)))
    pivot.parent = root
    return {'root': root, 'arm': arm, 'spots': spots, 'inner': inner, 'hand': hand, 'parts': parts, 'pilot': pil}

import os
TEX = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tex')
