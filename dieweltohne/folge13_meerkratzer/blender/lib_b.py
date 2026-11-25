# Hilfsfunktionen für die Blender-Fassung: Mathe, Meshes, Materialien (Node-Bau)
import bpy, bmesh, math, random
from mathutils import Vector, Matrix, Euler, noise

def clamp(x, a=0.0, b=1.0): return a if x < a else b if x > b else x
def lerp(a, b, k): return a + (b - a) * k
def smooth(a, b, t):
    k = clamp((t - a) / (b - a)); return k * k * (3 - 2 * k)
def ease_out(k): return 1 - (1 - k) ** 3
def ease_in(k): return k ** 3
def noise1(t, seed=0): return noise.noise(Vector((t, seed * 7.31, 0.5)))

# Umrechnung three.js (y oben, -z nach vorn) -> Blender (z oben, +y nach vorn)
def P(x, y, z): return Vector((x, -z, y))

# ---------- Szenen-Objekte ----------
COLL = {}
def coll(name):
    if name not in COLL:
        c = bpy.data.collections.new(name); bpy.context.scene.collection.children.link(c); COLL[name] = c
    return COLL[name]

def link(ob, c):
    for u in ob.users_collection: u.objects.unlink(ob)
    coll(c).objects.link(ob); return ob

# Alle Geometrie wird in three.js-Koordinaten (y oben) gebaut und beim Erzeugen nach Blender gedreht.
C3 = Matrix(((1, 0, 0, 0), (0, 0, -1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))
C3i = C3.inverted()
def M3(pos=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1)):
    """three.js-Transformation (Position, Euler XYZ, Skalierung) -> Blender-Weltmatrix"""
    s = scale if isinstance(scale, (tuple, list, Vector)) else (scale, scale, scale)
    m = Matrix.Translation(Vector(pos)) @ Euler(rot, 'XYZ').to_matrix().to_4x4() @ Matrix.Diagonal((*s, 1))
    return C3 @ m @ C3i

def mesh_obj(name, bm, mat=None, c='SEA', smooth_shade=True, subsurf=0, three=True):
    if three: bmesh.ops.transform(bm, matrix=C3, verts=bm.verts)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    if smooth_shade:
        for p in me.polygons: p.use_smooth = True
    ob = bpy.data.objects.new(name, me); coll(c).objects.link(ob)
    if mat is not None:
        for m in (mat if isinstance(mat, (list, tuple)) else [mat]): me.materials.append(m)
    if subsurf:
        md = ob.modifiers.new('sub', 'SUBSURF'); md.levels = subsurf; md.render_levels = subsurf
    return ob

def box_bm(x0, x1, y0, y1, z0, z1, bm=None):
    bm = bm or bmesh.new()
    r = bmesh.ops.create_cube(bm, size=1.0)
    for v in r['verts']:
        v.co = Vector((lerp(x0, x1, v.co.x + 0.5), lerp(y0, y1, v.co.y + 0.5), lerp(z0, z1, v.co.z + 0.5)))
    return bm

def box(name, x0, x1, y0, y1, z0, z1, mat, c='SEA', bevel=0.0):
    ob = mesh_obj(name, box_bm(x0, x1, y0, y1, z0, z1), mat, c, smooth_shade=False)
    if bevel > 0:
        md = ob.modifiers.new('bev', 'BEVEL'); md.width = bevel; md.segments = 2; md.limit_method = 'ANGLE'
    return ob

def cyl_bm(r0, r1, h, seg=24, bm=None, mat=Matrix(), caps=True):
    bm = bm or bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=caps, cap_tris=False, segments=seg, radius1=r0, radius2=r1, depth=h, matrix=mat)
    return bm

def sphere_bm(r, seg=24, rings=16, bm=None, mat=Matrix()):
    bm = bm or bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=rings, radius=r, matrix=mat)
    return bm

def hull_bm(L, prof, nu=60, nv=32, bm=None, xform=None, cap=True):
    """Rumpf entlang +X (Kopf x=0, Schwanz x=L), three-Koordinaten (y oben, z seitlich). prof(u) -> (halbe Höhe, halbe Breite, Exponent, Höhen-Versatz)."""
    bm = bm or bmesh.new(); rings = []
    for i in range(nu + 1):
        u = i / nu; h, w, ex, zo = prof(u); e = 2.0 / (ex or 2.0); ring = []
        for j in range(nv):
            a = j / nv * math.tau; c, s = math.cos(a), math.sin(a)
            up = math.copysign(abs(c) ** e, c) * h + zo; side = math.copysign(abs(s) ** e, s) * w
            co = Vector((u * L, up, side))
            if xform: co = xform(co, u)
            ring.append(bm.verts.new(co))
        rings.append(ring)
    for i in range(nu):
        for j in range(nv):
            a, b = rings[i][j], rings[i][(j + 1) % nv]; c2, d2 = rings[i + 1][(j + 1) % nv], rings[i + 1][j]
            bm.faces.new((a, d2, c2, b))
    if cap:
        for ring, rev in ((rings[0], False), (rings[-1], True)):
            try: bm.faces.new(list(reversed(ring)) if not rev else ring)
            except ValueError: pass
    return bm

# ---------- Materialien ----------
class NB:
    """Kleiner Node-Bauer: NB(mat) ; n = nb.n('ShaderNodeTexNoise', Scale=4) ; nb.l(a.outputs[0], b.inputs[1])"""
    def __init__(self, tree, x=0):
        self.t = tree; self.N = tree.nodes; self.L = tree.links; self.x = x
    def n(self, typ, **kw):
        nd = self.N.new(typ); nd.location = (self.x, 0); self.x -= 220
        for k, v in kw.items():
            if hasattr(nd, k) and not k[0].isupper(): setattr(nd, k, v)
            else:
                key = k.replace('_', ' ')
                if key in nd.inputs: nd.inputs[key].default_value = v
                elif k in nd.inputs: nd.inputs[k].default_value = v
                else: setattr(nd, k, v)
        return nd
    def l(self, a, b): self.L.new(a, b); return b
    def math(self, op, a, b=None, clamp_=False):
        nd = self.n('ShaderNodeMath', operation=op); nd.use_clamp = clamp_
        self._in(nd.inputs[0], a)
        if b is not None: self._in(nd.inputs[1], b)
        return nd.outputs[0]
    def mix(self, fac, a, b, blend='MIX'):
        nd = self.n('ShaderNodeMix', data_type='RGBA', blend_type=blend)
        self._in(nd.inputs[0], fac); self._in(nd.inputs[6], a); self._in(nd.inputs[7], b); return nd.outputs[2]
    def mixf(self, fac, a, b):
        nd = self.n('ShaderNodeMix', data_type='FLOAT')
        self._in(nd.inputs[0], fac); self._in(nd.inputs[2], a); self._in(nd.inputs[3], b); return nd.outputs[0]
    def _in(self, sock, v):
        if hasattr(v, 'is_output') or isinstance(v, bpy.types.NodeSocket): self.L.new(v, sock)
        else:
            if isinstance(v, tuple) and len(v) == 3 and sock.type == 'RGBA': v = (*v, 1)
            sock.default_value = v
    def ramp(self, fac, stops):
        nd = self.n('ShaderNodeValToRGB'); cr = nd.color_ramp
        while len(cr.elements) > 1: cr.elements.remove(cr.elements[-1])
        cr.elements[0].position = stops[0][0]; cr.elements[0].color = stops[0][1]
        for p, c in stops[1:]:
            e = cr.elements.new(p); e.color = c
        self._in(nd.inputs[0], fac); return nd.outputs[0]

def new_mat(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial'); out.location = (300, 0)
    return m, NB(nt), out

def principled(name, color=(0.8, 0.8, 0.8), rough=0.5, metal=0.0, **kw):
    m, nb, out = new_mat(name)
    p = nb.n('ShaderNodeBsdfPrincipled')
    nb._in(p.inputs['Base Color'], (*color, 1) if len(color) == 3 else color)
    p.inputs['Roughness'].default_value = rough; p.inputs['Metallic'].default_value = metal
    for k, v in kw.items():
        key = k.replace('_', ' ')
        if isinstance(v, tuple) and len(v) == 3 and p.inputs[key].type == 'RGBA': v = (*v, 1)
        p.inputs[key].default_value = v
    nb.l(p.outputs[0], out.inputs['Surface'])
    return m

def P_in(m): return next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')

def emission(name, color, strength):
    m, nb, out = new_mat(name)
    e = nb.n('ShaderNodeEmission'); e.inputs[0].default_value = (*color, 1); e.inputs[1].default_value = strength
    nb.l(e.outputs[0], out.inputs['Surface']); return m

def glass_mat(name, color=(0.9, 0.97, 1.0), rough=0.0, ior=1.5):
    """Glas, das Schatten nicht blockiert (sonst wäre alles hinter der Scheibe ohne Licht aus der Kabine)."""
    m, nb, out = new_mat(name)
    g = nb.n('ShaderNodeBsdfPrincipled')
    g.inputs['Base Color'].default_value = (*color, 1); g.inputs['Roughness'].default_value = rough
    g.inputs['Transmission Weight'].default_value = 1.0; g.inputs['IOR'].default_value = ior
    tr = nb.n('ShaderNodeBsdfTransparent'); tr.inputs[0].default_value = (*color, 1)
    lp = nb.n('ShaderNodeLightPath')
    mx = nb.n('ShaderNodeMixShader')
    nb.l(lp.outputs['Is Shadow Ray'], mx.inputs[0]); nb.l(g.outputs[0], mx.inputs[1]); nb.l(tr.outputs[0], mx.inputs[2])
    nb.l(mx.outputs[0], out.inputs['Surface'])
    return m

def ray_vis(ob, camera=True, diffuse=True, glossy=True, transmission=True, scatter=True, shadow=True):
    ob.visible_camera = camera; ob.visible_diffuse = diffuse; ob.visible_glossy = glossy
    ob.visible_transmission = transmission; ob.visible_volume_scatter = scatter; ob.visible_shadow = shadow

def light(name, typ, loc, energy, color=(1, 1, 1), c='SEA', **kw):
    ld = bpy.data.lights.new(name, typ); ld.energy = energy; ld.color = color
    for k, v in kw.items(): setattr(ld, k, v)
    ob = bpy.data.objects.new(name, ld); ob.location = loc; coll(c).objects.link(ob); return ob

def aim(ob, target, up='Z'):
    d = Vector(target) - ob.location
    ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()

def set_vis(ob, v):
    ob.hide_render = not v

def mr(nb, val, a, b, c=0.0, d=1.0, smooth_=True):
    nd = nb.n('ShaderNodeMapRange', interpolation_type='SMOOTHSTEP' if smooth_ else 'LINEAR')
    nb._in(nd.inputs['Value'], val); nd.inputs['From Min'].default_value = a; nd.inputs['From Max'].default_value = b
    nd.inputs['To Min'].default_value = c; nd.inputs['To Max'].default_value = d; return nd.outputs['Result']

def coords(nb, kind='Object'):
    tc = nb.n('ShaderNodeTexCoord'); return tc.outputs[kind]

def sep(nb, v):
    s = nb.n('ShaderNodeSeparateXYZ'); nb._in(s.inputs[0], v); return s.outputs

def noise_tex(nb, vec, scale, detail=4.0, rough=0.55, dist=0.0, dims='3D', w=None):
    n = nb.n('ShaderNodeTexNoise', noise_dimensions=dims); nb._in(n.inputs['Vector'], vec)
    n.inputs['Scale'].default_value = scale; n.inputs['Detail'].default_value = detail; n.inputs['Roughness'].default_value = rough
    n.inputs['Distortion'].default_value = dist
    if w is not None: nb._in(n.inputs['W'], w)
    return n

def bump(nb, height, strength=0.3, distance=0.01, normal=None):
    b = nb.n('ShaderNodeBump'); nb._in(b.inputs['Height'], height); b.inputs['Strength'].default_value = strength
    b.inputs['Distance'].default_value = distance
    if normal is not None: nb._in(b.inputs['Normal'], normal)
    return b.outputs['Normal']

def bsdf(nb, out, color, rough=0.5, metal=0.0, normal=None, **kw):
    p = nb.n('ShaderNodeBsdfPrincipled'); nb._in(p.inputs['Base Color'], color if not isinstance(color, tuple) or len(color) == 4 else (*color, 1))
    nb._in(p.inputs['Roughness'], rough); p.inputs['Metallic'].default_value = metal
    if normal is not None: nb._in(p.inputs['Normal'], normal)
    for k, v in kw.items():
        key = k.replace('_', ' ')
        if isinstance(v, tuple) and len(v) == 3 and p.inputs[key].type == 'RGBA': v = (*v, 1)
        nb._in(p.inputs[key], v)
    nb.l(p.outputs[0], out.inputs['Surface']); return p

def tube_obj(name, n, radial, mat, c='SEA'):
    """Schlauch mit fester Topologie (n Segmente, radial Ecken); Punkte werden jedes Bild neu gesetzt."""
    me = bpy.data.meshes.new(name); verts = [(0, 0, 0)] * ((n + 1) * radial + 1); faces = []
    for i in range(n):
        for j in range(radial):
            a = i * radial + j; b = i * radial + (j + 1) % radial
            faces.append((a, a + radial, b + radial, b))
    tip = (n + 1) * radial
    for j in range(radial): faces.append((n * radial + j, tip, n * radial + (j + 1) % radial)[::-1])
    faces.append(tuple(reversed(range(radial))))
    me.from_pydata(verts, [], faces); me.update()
    uv = me.uv_layers.new(name='UVMap')
    for p in me.polygons:
        for li, vi in zip(p.loop_indices, p.vertices):
            i, j = divmod(vi, radial) if vi < tip else (n, 0)
            uv.data[li].uv = (j / radial, i / n)
    for p in me.polygons: p.use_smooth = True
    me.materials.append(mat)
    ob = bpy.data.objects.new(name, me); coll(c).objects.link(ob); ob['n'] = n; ob['radial'] = radial
    return ob

def tube_set(ob, pts, radius, up=Vector((0, 0, 1)), flat=1.0, twist=0.0):
    """pts: n+1 Blender-Punkte, radius(i, u) -> Radius. Rahmen per Paralleltransport."""
    n, radial = ob['n'], ob['radial']; co = []
    t0 = (pts[1] - pts[0]).normalized(); nrm = up - t0 * up.dot(t0)
    if nrm.length < 1e-5: nrm = Vector((1, 0, 0)) - t0 * t0.x
    nrm.normalize()
    for i in range(n + 1):
        a, b = pts[max(0, i - 1)], pts[min(n, i + 1)]; t = (b - a).normalized()
        nrm = (nrm - t * nrm.dot(t)).normalized(); bn = t.cross(nrm)
        r = radius(i, i / n)
        for j in range(radial):
            an = j / radial * math.tau + twist
            v = nrm * math.cos(an) + bn * math.sin(an) * flat
            p = pts[i] + v * r; co.extend((p.x, p.y, p.z))
    tipp = pts[-1] + (pts[-1] - pts[-2]).normalized() * radius(n, 1.0) * 0.6
    co.extend((tipp.x, tipp.y, tipp.z))
    ob.data.vertices.foreach_set('co', co); ob.data.update()
    return nrm
