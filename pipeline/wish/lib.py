"""Blender helpers: Roblox-like materials, primitives, text."""
import bpy, bmesh, math, os
from mathutils import Vector

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
WK = os.path.abspath(ROOT + '/work') + '/'


def lin(c):
    if isinstance(c, int): c = ((c >> 16) & 255, (c >> 8) & 255, c & 255)
    return tuple(((x / 255 + 0.055) / 1.055) ** 2.4 if x / 255 > 0.04045 else x / 255 / 12.92 for x in c) + (1,)


COLL = None
def link(o):
    (COLL or bpy.context.scene.collection).objects.link(o); return o


_M = {}
def mat(c, rough=0.55, emit=0.0, metal=0.0, kind='plastic', alpha=1.0, name=None):
    """Roblox-ish material. kind: plastic, neon, grass, wood, brick, concrete, slate, asphalt, glass, fabric, water."""
    key = (str(c), rough, emit, metal, kind, alpha, name)
    if key in _M: return _M[key]
    m = bpy.data.materials.new(name or f"{kind}_{c}"); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; L = nt.links; b = N["Principled BSDF"]
    b.inputs["Base Color"].default_value = lin(c); b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal; b.inputs["Specular IOR Level"].default_value = 0.35
    if kind == 'neon' or emit:
        b.inputs["Emission Color"].default_value = lin(c); b.inputs["Emission Strength"].default_value = emit or 6
    if alpha < 1:
        b.inputs["Alpha"].default_value = alpha; m.blend_method = 'BLEND'; m.shadow_method = 'NONE'
    if kind in ('grass', 'wood', 'brick', 'concrete', 'slate', 'asphalt', 'fabric'):
        tc = N.new("ShaderNodeTexCoord"); mp = N.new("ShaderNodeMapping")
        L.new(tc.outputs["Object" if kind != 'grass' else "Generated"], mp.inputs[0])
        if kind == 'grass': L.new(tc.outputs["Object"], mp.inputs[0])
        nz = N.new("ShaderNodeTexNoise"); L.new(mp.outputs[0], nz.inputs[0])
        cr = N.new("ShaderNodeValToRGB"); L.new(nz.outputs["Fac"], cr.inputs[0])
        base = Vector(lin(c)[:3])
        dark = tuple(base * 0.78) + (1,); light = tuple(min(1, x * 1.12) for x in base) + (1,)
        cr.color_ramp.elements[0].color = dark; cr.color_ramp.elements[1].color = light
        cr.color_ramp.elements[0].position = 0.35; cr.color_ramp.elements[1].position = 0.65
        bump = N.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.15
        if kind == 'grass':
            nz.inputs["Scale"].default_value = 1.6; nz.inputs["Detail"].default_value = 8
            v = N.new("ShaderNodeTexVoronoi"); v.inputs["Scale"].default_value = 9; L.new(mp.outputs[0], v.inputs[0])
            L.new(v.outputs["Distance"], bump.inputs["Height"]); bump.inputs["Strength"].default_value = 0.25
        elif kind == 'wood':
            mp.inputs["Scale"].default_value = (0.4, 6, 0.4); nz.inputs["Scale"].default_value = 3; nz.inputs["Distortion"].default_value = 3
            L.new(nz.outputs["Fac"], bump.inputs["Height"])
        elif kind == 'brick':
            br = N.new("ShaderNodeTexBrick"); L.new(mp.outputs[0], br.inputs[0]); br.inputs["Scale"].default_value = 1.2
            br.inputs["Mortar Size"].default_value = 0.02; br.inputs["Color1"].default_value = lin(c); br.inputs["Color2"].default_value = dark
            br.inputs["Mortar"].default_value = lin((200, 195, 185))
            L.new(br.outputs["Color"], b.inputs["Base Color"]); L.new(br.outputs["Fac"], bump.inputs["Height"])
            L.new(bump.outputs["Normal"], b.inputs["Normal"]); _M[key] = m; return m
        elif kind == 'slate':
            v = N.new("ShaderNodeTexVoronoi"); v.inputs["Scale"].default_value = 1.4; L.new(mp.outputs[0], v.inputs[0])
            L.new(v.outputs["Distance"], bump.inputs["Height"]); bump.inputs["Strength"].default_value = 0.35
            nz.inputs["Scale"].default_value = 2
        else:
            nz.inputs["Scale"].default_value = 4 if kind != 'fabric' else 20; L.new(nz.outputs["Fac"], bump.inputs["Height"])
            bump.inputs["Strength"].default_value = 0.08
        L.new(cr.outputs["Color"], b.inputs["Base Color"]); L.new(bump.outputs["Normal"], b.inputs["Normal"])
    if kind == 'glass':
        b.inputs["Transmission Weight"].default_value = 0.0; b.inputs["Alpha"].default_value = 0.35
        m.blend_method = 'BLEND'; m.shadow_method = 'NONE'; b.inputs["Roughness"].default_value = 0.05
    _M[key] = m
    return m


def img_mat(path, name=None, clip=False, emit=0.0, rough=0.55, grey=False):
    key = ('img', path, clip, emit, grey)
    if key in _M: return _M[key]
    m = bpy.data.materials.new(name or os.path.basename(path)); m.use_nodes = True
    N = m.node_tree.nodes; L = m.node_tree.links; b = N["Principled BSDF"]
    t = N.new("ShaderNodeTexImage"); t.image = bpy.data.images.load(path, check_existing=True)
    t.interpolation = 'Linear'
    col = t.outputs["Color"]
    if grey:
        hs = N.new("ShaderNodeHueSaturation"); hs.inputs["Saturation"].default_value = 0.0; hs.inputs["Value"].default_value = 1.9
        L.new(col, hs.inputs["Color"]); col = hs.outputs["Color"]
    L.new(col, b.inputs["Base Color"]); b.inputs["Roughness"].default_value = rough
    b.inputs["Specular IOR Level"].default_value = 0.3
    if clip:
        L.new(t.outputs["Alpha"], b.inputs["Alpha"]); m.blend_method = 'CLIP'; m.shadow_method = 'NONE'; m.alpha_threshold = 0.4
    if emit:
        L.new(col, b.inputs["Emission Color"]); b.inputs["Emission Strength"].default_value = emit
    _M[key] = m
    return m


def obj_from(bm, name, m=None, parent=None, loc=(0, 0, 0), smooth=False):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = link(bpy.data.objects.new(name, me)); o.location = loc
    if m: o.data.materials.append(m)
    if smooth:
        for p in me.polygons: p.use_smooth = True
    if parent: o.parent = parent
    return o


def box(size, loc, m, parent=None, rot=(0, 0, 0), name="box", bevel=0.0):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * size[0], v.co.y * size[1], v.co.z * size[2]))
    o = obj_from(bm, name, m, parent, loc); o.rotation_euler = rot
    if bevel:
        md = o.modifiers.new("b", "BEVEL"); md.width = bevel; md.segments = 2; md.limit_method = 'NONE'
    return o


def cyl(r, h, loc, m, parent=None, rot=(0, 0, 0), v=32, r2=None, name="cyl", smooth=True):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=v, radius1=r, radius2=r if r2 is None else r2, depth=h)
    o = obj_from(bm, name, m, parent, loc); o.rotation_euler = rot
    if smooth:
        for p in o.data.polygons: p.use_smooth = abs(p.normal.z) < 0.5
    return o


def sphere(r, loc, m, parent=None, scale=(1, 1, 1), seg=24, name="sph"):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=seg // 2, radius=r)
    o = obj_from(bm, name, m, parent, loc, smooth=True); o.scale = scale
    return o


def tube(r_in, r_out, h, loc, m, v=48, name="tube", parent=None):
    bm = bmesh.new()
    a = bmesh.ops.create_circle(bm, cap_ends=False, segments=v, radius=r_out)['verts']
    b = bmesh.ops.create_circle(bm, cap_ends=False, segments=v, radius=r_in)['verts']
    a2 = [bm.verts.new(x.co + Vector((0, 0, h))) for x in a]; b2 = [bm.verts.new(x.co + Vector((0, 0, h))) for x in b]
    for i in range(v):
        j = (i + 1) % v
        bm.faces.new([a[i], a[j], a2[j], a2[i]]); bm.faces.new([b[j], b[i], b2[i], b2[j]])
        bm.faces.new([a2[i], a2[j], b2[j], b2[i]]); bm.faces.new([b[i], b[j], a[j], a[i]])
    o = obj_from(bm, name, m, parent, loc)
    for p in o.data.polygons: p.use_smooth = abs(p.normal.z) < 0.5
    return o


def wedge(w, d, h, loc, m, name="roof", rot=(0, 0, 0)):
    bm = bmesh.new()
    vs = [bm.verts.new(v) for v in [(-w / 2, -d / 2, 0), (w / 2, -d / 2, 0), (w / 2, d / 2, 0), (-w / 2, d / 2, 0), (-w / 2, 0, h), (w / 2, 0, h)]]
    for f in [(0, 1, 5, 4), (2, 3, 4, 5), (0, 4, 3), (1, 2, 5), (0, 3, 2, 1)]: bm.faces.new([vs[i] for i in f])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = obj_from(bm, name, m, None, loc); o.rotation_euler = rot
    return o


_FONT = None
def text(s, loc, size, m, rot=(math.radians(90), 0, 0), align='CENTER', extrude=0.05, parent=None, name="txt"):
    global _FONT
    if _FONT is None:
        for p in [WK + 'Fredoka.ttf']:
            try: _FONT = bpy.data.fonts.load(p); break
            except Exception: pass
    cu = bpy.data.curves.new(name, 'FONT'); cu.body = s; cu.size = size; cu.extrude = extrude
    cu.align_x = align; cu.align_y = 'CENTER'
    if _FONT: cu.font = _FONT
    o = link(bpy.data.objects.new(name, cu)); o.location = loc; o.rotation_euler = rot
    o.data.materials.append(m)
    if parent: o.parent = parent
    return o


def heart(size, loc, m, name="heart", depth=0.4):
    bm = bmesh.new(); pts = []
    for i in range(48):
        t = i / 48 * math.tau
        x = 16 * math.sin(t) ** 3; y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((x / 17 * size, y / 17 * size))
    f = [bm.verts.new((x, 0, y)) for x, y in pts]; face = bm.faces.new(f)
    ext = bmesh.ops.extrude_face_region(bm, geom=[face])
    for v in [e for e in ext['geom'] if isinstance(e, bmesh.types.BMVert)]: v.co.y += depth
    bmesh.ops.translate(bm, verts=bm.verts, vec=(0, -depth / 2, 0))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = obj_from(bm, name, m, None, loc)
    md = o.modifiers.new("b", "BEVEL"); md.width = size * 0.08; md.segments = 3
    return o


def key_vis(o, f, show):
    o.hide_render = not show; o.keyframe_insert("hide_render", frame=f)
    o.hide_viewport = not show; o.keyframe_insert("hide_viewport", frame=f)
