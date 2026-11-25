"""Hilfsfunktionen: Materialien, Primitive, Mesh-Generatoren (Blender 5 / bpy)."""
import bpy, bmesh, math, random
from mathutils import Vector, Euler, Matrix

C = bpy.context
D = bpy.data


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    sc.cycles.device = 'CPU'
    sc.render.use_persistent_data = True
    return sc


def link(ob, coll=None):
    (coll or bpy.context.scene.collection).objects.link(ob)
    return ob


# ---------------------------------------------------------------- Materialien
def _nodes(mat):
    mat.use_nodes = True
    nt = mat.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    return nt, out


def principled(name, color, rough=0.5, metal=0.0, sss=0.0, sss_r=(1, .4, .2), coat=0.0,
               emit=None, emit_str=0.0, alpha=1.0, trans=0.0, ior=1.45, film=0.0, film_ior=1.4,
               sheen=0.0, spec=0.5, bump=None, aniso=0.0):
    mat = D.materials.new(name)
    nt, out = _nodes(mat)
    b = nt.nodes.new('ShaderNodeBsdfPrincipled')
    b.inputs['Base Color'].default_value = (*color, 1)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    b.inputs['IOR'].default_value = ior
    if sss:
        b.inputs['Subsurface Weight'].default_value = sss
        b.inputs['Subsurface Radius'].default_value = sss_r
        b.inputs['Subsurface Scale'].default_value = 0.05
        b.subsurface_method = 'BURLEY'
    if coat:
        b.inputs['Coat Weight'].default_value = coat
    if emit:
        b.inputs['Emission Color'].default_value = (*emit, 1)
        b.inputs['Emission Strength'].default_value = emit_str
    if trans:
        b.inputs['Transmission Weight'].default_value = trans
    if film:
        b.inputs['Thin Film Thickness'].default_value = film
        b.inputs['Thin Film IOR'].default_value = film_ior
    if sheen:
        b.inputs['Sheen Weight'].default_value = sheen
    if aniso:
        b.inputs['Anisotropic'].default_value = aniso
    b.inputs['Alpha'].default_value = alpha
    nt.links.new(b.outputs[0], out.inputs[0])
    if bump:
        add_noise_bump(mat, b, *bump)
    mat['bsdf'] = b.name
    return mat


def add_noise_bump(mat, bsdf, scale=40.0, strength=0.15, detail=6.0, kind='noise'):
    nt = mat.node_tree
    tc = nt.nodes.new('ShaderNodeTexCoord')
    if kind == 'noise':
        tx = nt.nodes.new('ShaderNodeTexNoise')
        tx.inputs['Scale'].default_value = scale
        tx.inputs['Detail'].default_value = detail
        nt.links.new(tc.outputs['Object'], tx.inputs['Vector'])
        src = tx.outputs['Fac']
    elif kind == 'knit':  # Strickmuster: Wellen in V-Form
        mp = nt.nodes.new('ShaderNodeMapping')
        mp.inputs['Scale'].default_value = (1, 1, 1)
        nt.links.new(tc.outputs['Object'], mp.inputs['Vector'])
        sep = nt.nodes.new('ShaderNodeSeparateXYZ')
        nt.links.new(mp.outputs[0], sep.inputs[0])
        m1 = nt.nodes.new('ShaderNodeMath'); m1.operation = 'MULTIPLY'; m1.inputs[1].default_value = scale
        nt.links.new(sep.outputs['X'], m1.inputs[0])
        m2 = nt.nodes.new('ShaderNodeMath'); m2.operation = 'SINE'
        nt.links.new(m1.outputs[0], m2.inputs[0])
        m3 = nt.nodes.new('ShaderNodeMath'); m3.operation = 'ABSOLUTE'
        nt.links.new(m2.outputs[0], m3.inputs[0])
        m4 = nt.nodes.new('ShaderNodeMath'); m4.operation = 'MULTIPLY'; m4.inputs[1].default_value = scale * 1.6
        nt.links.new(sep.outputs['Z'], m4.inputs[0])
        m5 = nt.nodes.new('ShaderNodeMath'); m5.operation = 'ADD'
        nt.links.new(m4.outputs[0], m5.inputs[0]); nt.links.new(m3.outputs[0], m5.inputs[1])
        m6 = nt.nodes.new('ShaderNodeMath'); m6.operation = 'FRACT'
        nt.links.new(m5.outputs[0], m6.inputs[0])
        m7 = nt.nodes.new('ShaderNodeMath'); m7.operation = 'PINGPONG'; m7.inputs[1].default_value = 0.5
        nt.links.new(m6.outputs[0], m7.inputs[0])
        src = m7.outputs[0]
    elif kind == 'wave':
        tx = nt.nodes.new('ShaderNodeTexWave')
        tx.inputs['Scale'].default_value = scale
        tx.inputs['Distortion'].default_value = 3
        tx.inputs['Detail'].default_value = detail
        nt.links.new(tc.outputs['Object'], tx.inputs['Vector'])
        src = tx.outputs['Fac']
    bp = nt.nodes.new('ShaderNodeBump')
    bp.inputs['Strength'].default_value = strength
    nt.links.new(src, bp.inputs['Height'])
    nt.links.new(bp.outputs[0], bsdf.inputs['Normal'])
    return src


def emission(name, color, strength=5.0, alpha=None):
    mat = D.materials.new(name)
    nt, out = _nodes(mat)
    e = nt.nodes.new('ShaderNodeEmission')
    e.inputs[0].default_value = (*color, 1)
    e.inputs[1].default_value = strength
    if alpha is None:
        nt.links.new(e.outputs[0], out.inputs[0])
    else:
        tr = nt.nodes.new('ShaderNodeBsdfTransparent')
        mx = nt.nodes.new('ShaderNodeMixShader')
        mx.inputs[0].default_value = alpha
        nt.links.new(tr.outputs[0], mx.inputs[1]); nt.links.new(e.outputs[0], mx.inputs[2])
        nt.links.new(mx.outputs[0], out.inputs[0])
    mat['emit'] = e.name
    return mat


def glass(name, color=(0.85, 0.95, 1.0), rough=0.02, ior=1.45):
    mat = D.materials.new(name)
    nt, out = _nodes(mat)
    g = nt.nodes.new('ShaderNodeBsdfGlass')
    g.inputs['Color'].default_value = (*color, 1)
    g.inputs['Roughness'].default_value = rough
    g.inputs['IOR'].default_value = ior
    # Schattenstrahlen durchlassen (sonst schwarzes Fenster)
    lp = nt.nodes.new('ShaderNodeLightPath')
    tr = nt.nodes.new('ShaderNodeBsdfTransparent')
    tr.inputs[0].default_value = (*color, 1)
    mx = nt.nodes.new('ShaderNodeMixShader')
    nt.links.new(lp.outputs['Is Shadow Ray'], mx.inputs[0])
    nt.links.new(g.outputs[0], mx.inputs[1]); nt.links.new(tr.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs[0])
    return mat


def window_glass(name, tint=(0.8, 0.92, 1.0), refl=0.08):
    """Dünnes Fensterglas: fast transparent + leichte Spiegelung."""
    mat = D.materials.new(name)
    nt, out = _nodes(mat)
    tr = nt.nodes.new('ShaderNodeBsdfTransparent'); tr.inputs[0].default_value = (*tint, 1)
    gl = nt.nodes.new('ShaderNodeBsdfGlossy'); gl.inputs['Roughness'].default_value = 0.03
    fr = nt.nodes.new('ShaderNodeFresnel'); fr.inputs[0].default_value = 1.5
    mm = nt.nodes.new('ShaderNodeMath'); mm.operation = 'MULTIPLY_ADD'
    mm.inputs[1].default_value = 1.0; mm.inputs[2].default_value = refl
    nt.links.new(fr.outputs[0], mm.inputs[0])
    mx = nt.nodes.new('ShaderNodeMixShader')
    nt.links.new(mm.outputs[0], mx.inputs[0])
    nt.links.new(tr.outputs[0], mx.inputs[1]); nt.links.new(gl.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs[0])
    mat.blend_method = 'BLEND' if hasattr(mat, 'blend_method') else None
    return mat


def set_emit(mat, strength=None, color=None):
    nt = mat.node_tree
    if 'emit' in mat:
        e = nt.nodes[mat['emit']]
        if strength is not None: e.inputs[1].default_value = strength
        if color is not None: e.inputs[0].default_value = (*color, 1)
    else:
        b = nt.nodes[mat['bsdf']]
        if strength is not None: b.inputs['Emission Strength'].default_value = strength
        if color is not None: b.inputs['Emission Color'].default_value = (*color, 1)


def color_ramp_mat(name, stops, coord='Z', rough=0.4, sss=0.0, film=0.0, film_ior=1.4, coat=0.0, bump=None, metal=0.0,
                   lo=-1.0, hi=1.0, space='Object'):
    """Principled mit Farbverlauf entlang einer Objektachse."""
    mat = principled(name, (1, 1, 1), rough=rough, sss=sss, film=film, film_ior=film_ior, coat=coat, metal=metal, bump=bump)
    nt = mat.node_tree
    b = nt.nodes[mat['bsdf']]
    tc = nt.nodes.new('ShaderNodeTexCoord')
    sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    nt.links.new(tc.outputs[space], sep.inputs[0])
    mr = nt.nodes.new('ShaderNodeMapRange')
    mr.inputs['From Min'].default_value = lo; mr.inputs['From Max'].default_value = hi
    nt.links.new(sep.outputs[coord], mr.inputs['Value'])
    cr = nt.nodes.new('ShaderNodeValToRGB')
    el = cr.color_ramp.elements
    el[0].position, el[0].color = stops[0][0], (*stops[0][1], 1)
    el[1].position, el[1].color = stops[-1][0], (*stops[-1][1], 1)
    for p, c in stops[1:-1]:
        e = el.new(p); e.color = (*c, 1)
    nt.links.new(mr.outputs[0], cr.inputs[0])
    nt.links.new(cr.outputs[0], b.inputs['Base Color'])
    return mat


def hexc(h):
    h = h.lstrip('#')
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c)


# ---------------------------------------------------------------- Objekte
def mesh_obj(name, verts, faces, mat=None, smooth=True, coll=None):
    me = D.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    ob = D.objects.new(name, me)
    link(ob, coll)
    if smooth:
        for p in me.polygons: p.use_smooth = True
    if mat: me.materials.append(mat)
    return ob


def prim(kind, name, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), mat=None, smooth=True, parent=None,
         subsurf=0, bevel=0.0, seg=32, coll=None, bake=True, **kw):
    if kind == 'cube':
        bm = bmesh.new(); bmesh.ops.create_cube(bm, size=2.0)
    elif kind == 'sphere':
        bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=max(8, seg // 2), radius=1.0)
    elif kind == 'cyl':
        bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=kw.get('r1', 1.0),
                                                radius2=kw.get('r2', 1.0), depth=2.0)
    elif kind == 'torus':
        ob = torus(name, kw.get('R', 1.0), kw.get('r', 0.25), seg, kw.get('seg2', 16), mat, coll)
        if bake and tuple(scale) != (1, 1, 1):
            from mathutils import Matrix
            ob.data.transform(Matrix.Diagonal((*scale, 1))); scale = (1, 1, 1)
        _xf(ob, loc, rot, scale, parent); return ob
    elif kind == 'plane':
        bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=1.0)
    me = D.meshes.new(name)
    if bake:
        bmesh.ops.scale(bm, vec=scale, verts=bm.verts)
        scale = (1, 1, 1)
    bm.to_mesh(me); bm.free()
    ob = D.objects.new(name, me)
    link(ob, coll)
    if smooth and kind != 'cube' and kind != 'plane':
        for p in me.polygons: p.use_smooth = True
    if kind == 'cyl' and smooth:
        # Deckel flach lassen: Auto-Smooth über Kantenwinkel
        for p in me.polygons:
            if abs(p.normal.z) > 0.9: p.use_smooth = False
    if mat: me.materials.append(mat)
    if bevel:
        m = ob.modifiers.new('bev', 'BEVEL'); m.width = bevel; m.segments = 3; m.limit_method = 'ANGLE'
        m.harden_normals = False
        for p in me.polygons: p.use_smooth = True
        if kind in ('cube', 'cyl', 'plane'):
            ob.modifiers.new('ws', 'WEIGHTED_NORMAL')
    if subsurf:
        m = ob.modifiers.new('sub', 'SUBSURF'); m.levels = subsurf; m.render_levels = subsurf
    _xf(ob, loc, rot, scale, parent)
    return ob


def _xf(ob, loc, rot, scale, parent):
    if parent: ob.parent = parent
    ob.location = loc
    ob.rotation_euler = rot
    ob.scale = scale


def torus(name, R, r, seg=48, seg2=16, mat=None, coll=None):
    vs, fs = [], []
    for i in range(seg):
        a = 2 * math.pi * i / seg
        for j in range(seg2):
            b = 2 * math.pi * j / seg2
            vs.append(((R + r * math.cos(b)) * math.cos(a), (R + r * math.cos(b)) * math.sin(a), r * math.sin(b)))
    for i in range(seg):
        for j in range(seg2):
            a = i * seg2 + j; b2 = ((i + 1) % seg) * seg2 + j
            c = ((i + 1) % seg) * seg2 + (j + 1) % seg2; d = i * seg2 + (j + 1) % seg2
            fs.append((a, b2, c, d))
    return mesh_obj(name, vs, fs, mat, coll=coll)


def empty(name, loc=(0, 0, 0), rot=(0, 0, 0), parent=None, coll=None):
    ob = D.objects.new(name, None)
    link(ob, coll)
    _xf(ob, loc, rot, (1, 1, 1), parent)
    return ob


def lathe(name, profile, seg=48, mat=None, coll=None, close_top=True, close_bot=True):
    """profile: Liste (r, z). Rotation um Z."""
    vs, fs = [], []
    n = len(profile)
    for i in range(seg):
        a = 2 * math.pi * i / seg
        for r, z in profile:
            vs.append((r * math.cos(a), r * math.sin(a), z))
    for i in range(seg):
        for j in range(n - 1):
            a = i * n + j; b = ((i + 1) % seg) * n + j
            fs.append((a, b, b + 1, a + 1))
    if close_bot and profile[0][0] > 1e-4:
        c = len(vs); vs.append((0, 0, profile[0][1]))
        for i in range(seg):
            fs.append((((i + 1) % seg) * n, i * n, c))
    if close_top and profile[-1][0] > 1e-4:
        c = len(vs); vs.append((0, 0, profile[-1][1]))
        for i in range(seg):
            fs.append((i * n + n - 1, ((i + 1) % seg) * n + n - 1, c))
    return mesh_obj(name, vs, fs, mat, coll=coll)


def tube(name, pts, radius, seg=12, mat=None, coll=None, radii=None):
    """Röhre entlang Punktliste (für Kabel, Rohre, Finger)."""
    vs, fs = [], []
    P = [Vector(p) for p in pts]
    n = len(P)
    up = Vector((0, 0, 1))
    for i, p in enumerate(P):
        t = (P[min(i + 1, n - 1)] - P[max(i - 1, 0)]).normalized()
        ref = up if abs(t.dot(up)) < 0.95 else Vector((1, 0, 0))
        nx = t.cross(ref).normalized(); ny = t.cross(nx).normalized()
        r = radii[i] if radii else radius
        for j in range(seg):
            a = 2 * math.pi * j / seg
            vs.append(tuple(p + (nx * math.cos(a) + ny * math.sin(a)) * r))
    for i in range(n - 1):
        for j in range(seg):
            a = i * seg + j; b = i * seg + (j + 1) % seg
            fs.append((a, b, b + seg, a + seg))
    c0 = len(vs); vs.append(tuple(P[0])); c1 = len(vs); vs.append(tuple(P[-1]))
    for j in range(seg):
        fs.append(((j + 1) % seg, j, c0))
        fs.append(((n - 1) * seg + j, (n - 1) * seg + (j + 1) % seg, c1))
    return mesh_obj(name, vs, fs, mat, coll=coll)


def text_obj(name, s, size=1.0, mat=None, extrude=0.0, align='CENTER', coll=None, bevel=0.0, font=None):
    cu = D.curves.new(name, 'FONT')
    cu.body = s
    cu.size = size
    cu.extrude = extrude
    cu.bevel_depth = bevel
    cu.align_x = align
    cu.align_y = 'CENTER'
    if font: cu.font = font
    ob = D.objects.new(name, cu)
    link(ob, coll)
    if mat: cu.materials.append(mat)
    return ob


def instance(src, name, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), parent=None, coll=None):
    ob = D.objects.new(name, src.data)
    link(ob, coll)
    for m in src.modifiers:
        n = ob.modifiers.new(m.name, m.type)
        for attr in ('levels', 'render_levels', 'width', 'segments', 'limit_method', 'thickness', 'offset'):
            if hasattr(m, attr):
                try: setattr(n, attr, getattr(m, attr))
                except Exception: pass
    _xf(ob, loc, rot, scale, parent)
    return ob


def add_light(kind, name, loc, energy, color=(1, 1, 1), size=0.5, rot=(0, 0, 0), spot=None, blend=0.3, coll=None):
    ld = D.lights.new(name, kind)
    ld.energy = energy
    ld.color = color
    if kind in ('POINT', 'SPOT'):
        ld.shadow_soft_size = size
    if kind == 'AREA':
        ld.size = size
    if kind == 'SPOT':
        ld.spot_size = spot or math.radians(45); ld.spot_blend = blend
    if kind == 'SUN':
        ld.angle = size
    ob = D.objects.new(name, ld)
    link(ob, coll)
    ob.location = loc; ob.rotation_euler = rot
    return ob


def look_at(ob, target, roll=0.0):
    d = Vector(target) - ob.location
    q = d.to_track_quat('-Z', 'Y')
    ob.rotation_euler = q.to_euler()
    if roll:
        ob.rotation_euler.rotate_axis('Z', roll)


def camera(name='Cam', lens=35.0):
    cd = D.cameras.new(name)
    cd.lens = lens
    cd.sensor_width = 36
    cd.clip_start = 0.02; cd.clip_end = 3000
    ob = D.objects.new(name, cd)
    link(ob)
    bpy.context.scene.camera = ob
    return ob


def world(color=(0.02, 0.05, 0.08), strength=1.0, top=None, bottom=None):
    w = D.worlds.new('W')
    bpy.context.scene.world = w
    w.use_nodes = True
    nt = w.node_tree
    for n in list(nt.nodes): nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputWorld')
    bg = nt.nodes.new('ShaderNodeBackground')
    bg.inputs[1].default_value = strength
    if top is None:
        bg.inputs[0].default_value = (*color, 1)
    else:
        tc = nt.nodes.new('ShaderNodeTexCoord')
        sep = nt.nodes.new('ShaderNodeSeparateXYZ')
        nt.links.new(tc.outputs['Generated'], sep.inputs[0])
        cr = nt.nodes.new('ShaderNodeValToRGB')
        el = cr.color_ramp.elements
        el[0].position = 0.0; el[0].color = (*bottom, 1)
        el[1].position = 1.0; el[1].color = (*top, 1)
        e = el.new(0.5); e.color = (*color, 1)
        mr = nt.nodes.new('ShaderNodeMapRange')
        mr.inputs['From Min'].default_value = -1; mr.inputs['From Max'].default_value = 1
        nt.links.new(sep.outputs['Z'], mr.inputs[0])
        nt.links.new(mr.outputs[0], cr.inputs[0])
        nt.links.new(cr.outputs[0], bg.inputs[0])
    nt.links.new(bg.outputs[0], out.inputs[0])
    return w


def render_settings(w=720, h=1280, spp=24, bounces=4, film_transparent=False):
    sc = bpy.context.scene
    sc.render.resolution_x = w; sc.render.resolution_y = h
    sc.render.resolution_percentage = 100
    sc.cycles.samples = spp
    sc.cycles.use_adaptive_sampling = True
    sc.cycles.adaptive_threshold = 0.03
    sc.cycles.use_denoising = True
    sc.cycles.denoiser = 'OPENIMAGEDENOISE'
    sc.cycles.max_bounces = bounces
    sc.cycles.diffuse_bounces = 2
    sc.cycles.glossy_bounces = 2
    sc.cycles.transmission_bounces = 6
    sc.cycles.transparent_max_bounces = 12
    sc.cycles.volume_bounces = 0
    sc.cycles.caustics_reflective = False
    sc.cycles.caustics_refractive = False
    sc.cycles.blur_glossy = 1.0
    sc.cycles.sample_clamp_indirect = 6.0
    sc.render.film_transparent = film_transparent
    sc.view_settings.view_transform = 'AgX'
    sc.view_settings.look = 'AgX - Punchy'
    sc.render.image_settings.file_format = 'PNG'
    sc.render.image_settings.color_depth = '8'
    sc.cycles.use_auto_tile = False
    sc.render.threads_mode = 'AUTO'


def rnd(seed):
    return random.Random(seed)


def smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def ease(t, t0, t1):
    if t1 <= t0: return 1.0 if t >= t1 else 0.0
    return smooth((t - t0) / (t1 - t0))


def lerp(a, b, k):
    if isinstance(a, (tuple, list, Vector)):
        return tuple(x + (y - x) * k for x, y in zip(a, b))
    return a + (b - a) * k


def keys(t, kf):
    """kf: Liste (t, value); geglättete Interpolation."""
    if t <= kf[0][0]: return kf[0][1]
    for (t0, v0), (t1, v1) in zip(kf, kf[1:]):
        if t <= t1:
            return lerp(v0, v1, smooth((t - t0) / (t1 - t0)))
    return kf[-1][1]
