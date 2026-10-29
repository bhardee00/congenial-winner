"""Realistic-ish Roblox suburb kit (reference #2 look): free Kenney models (CC0) and Poly Haven textures/sky (CC0)
from assets/town, plus procedural leafy and pine trees and the glowing chest counter badge.
    import town
    town.sky(st)                                    # Poly Haven sky + warm sun on a Set
    town.place("suburban/building-type-c", (x, y, 0), yaw=180)   # Kenney models, scaled to R6 characters
    town.street(...), town.lawn(...), town.tree(...), town.pine(...)
    town.badge(av, png) / town.counter(av, {frame: png})          # chest counter (pictures made by the story's _images.py)
Kenney sizes: buildings x24, cars x4.2, furniture x7.5 (a chair seat lands at ~1.6, like blocky sit heights).
Every model is imported once per file and then instanced; its pivot is moved to the bottom centre."""
import math, os, random
try:  # the *_png helpers also run outside Blender (story _images.py)
    import bpy
    from mathutils import Vector, noise
except ImportError: bpy = None

HERE = os.path.dirname(os.path.abspath(__file__)); T = os.path.join(os.path.dirname(HERE), "assets", "town") + "/"
SCALE = {"suburban": 24.0, "cars": 4.2, "roads": 24.0, "furniture": 7.5}
_cols = {}


def _collection(rel):
    """Import a model once into its own (unlinked) collection, pivot at the bottom centre."""
    if rel in _cols: return _cols[rel]
    path = T + rel + (".glb" if not rel.endswith((".glb", ".gltf")) else "")
    if rel.startswith("ph/"):
        a = rel.split("/")[1]; path = T + f"ph/{a}/{a}_1k.gltf"
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=path)
    new = set(bpy.data.objects) - before
    pts = [o.matrix_world @ Vector(c) for o in new if o.type == 'MESH' for c in o.bound_box]
    mn = Vector([min(p[i] for p in pts) for i in range(3)]); mx = Vector([max(p[i] for p in pts) for i in range(3)])
    root = bpy.data.objects.new("m_" + os.path.basename(rel), None)
    col = bpy.data.collections.new(os.path.basename(rel))
    for o in new:
        if o.parent is None: o.parent = root
        for c in list(o.users_collection): c.objects.unlink(o)
        col.objects.link(o)
    col.objects.link(root)
    root.location = (-(mn.x + mx.x) / 2, -(mn.y + mx.y) / 2, -mn.z)
    _cols[rel] = col; col["size"] = list(mx - mn)
    return col


def place(rel, loc, yaw=0, scale=None, name=None):
    """Instance a model from assets/town (e.g. "suburban/building-type-c", "cars/sedan", "furniture/chair",
    "ph/fire_hydrant"). yaw 0 = as modelled (Kenney houses and furniture face +Y)."""
    col = _collection(rel)
    s = scale if scale is not None else SCALE.get(rel.split("/")[0], 3.0)
    o = bpy.data.objects.new(name or "i_" + os.path.basename(rel), None)
    o.instance_type = 'COLLECTION'; o.instance_collection = col
    bpy.context.scene.collection.objects.link(o)
    o.location = loc; o.rotation_euler = (0, 0, math.radians(yaw)); o.scale = (s, s, s)
    return o


def size(rel, scale=None):
    s = scale if scale is not None else SCALE.get(rel.split("/")[0], 3.0)
    return [v * s for v in _collection(rel)["size"]]


_mats = {}


def texmat(name, scale=0.1, tint=None, rough=0.9):
    """Poly Haven ground texture (leafy_grass, clean_asphalt, concrete_pavement) mapped in world space."""
    key = (name, scale, tint)
    if key in _mats: return _mats[key]
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; pb = nt.nodes["Principled BSDF"]
    geo = nt.nodes.new("ShaderNodeNewGeometry"); mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (scale,) * 3
    nt.links.new(geo.outputs["Position"], mp.inputs["Vector"])
    d = nt.nodes.new("ShaderNodeTexImage"); d.image = bpy.data.images.load(T + f"tex/{name}_diff_1k.jpg", check_existing=True)
    nt.links.new(mp.outputs[0], d.inputs[0])
    if tint:
        mx = nt.nodes.new("ShaderNodeMixRGB"); mx.blend_type = 'MULTIPLY'; mx.inputs[0].default_value = 1
        mx.inputs[2].default_value = tuple(c / 255 for c in tint) + (1,)
        nt.links.new(d.outputs[0], mx.inputs[1]); nt.links.new(mx.outputs[0], pb.inputs["Base Color"])
    else: nt.links.new(d.outputs[0], pb.inputs["Base Color"])
    n = nt.nodes.new("ShaderNodeTexImage"); n.image = bpy.data.images.load(T + f"tex/{name}_nor_gl_1k.jpg", check_existing=True)
    n.image.colorspace_settings.name = "Non-Color"; nt.links.new(mp.outputs[0], n.inputs[0])
    nm = nt.nodes.new("ShaderNodeNormalMap"); nt.links.new(n.outputs[0], nm.inputs["Color"]); nt.links.new(nm.outputs[0], pb.inputs["Normal"])
    pb.inputs["Roughness"].default_value = rough
    _mats[key] = m; return m


def _mesh(name, build, m, loc, smooth=False):
    """Mesh object from a bmesh builder (bpy.ops add-mesh operators don't work inside a Set's context)."""
    import bmesh
    bm = bmesh.new(); build(bm); me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    if smooth:
        for p in me.polygons: p.use_smooth = True
    me.materials.append(m)
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o); o.location = loc; return o


def slab(size, loc, m, name="slab"):
    import bmesh
    o = _mesh(name, lambda bm: bmesh.ops.create_cube(bm, size=1), m, loc); o.scale = size; return o


def grass(): return texmat("leafy_grass", 0.08, (90, 190, 50))
def asphalt(): return texmat("clean_asphalt", 0.06)
def concrete(): return texmat("concrete_pavement", 0.12)


def lawn(size=800, loc=(0, 0)):
    return slab((size, size, 1), (loc[0], loc[1], -0.5), grass(), "lawn")


def street(y=14, length=600, width=26, x=0, walks=True, lines=True):
    """A road along X centred on y, with curbs and sidewalks on both sides (sidewalk top at z 0.3)."""
    slab((length, width, 0.2), (x, y, 0.0), asphalt(), "road")
    if walks:
        for s in (-1, 1):
            slab((length, 7, 0.6), (x, y + s * (width / 2 + 3.5), 0.0), concrete(), "walk")
    if lines:
        lm = bpy.data.materials.get("roadline") or bpy.data.materials.new("roadline"); lm.use_nodes = True
        lm.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.9, 0.72, 0.12, 1)
        for k in range(int(-length / 2), int(length / 2), 14): slab((7, 0.5, 0.05), (x + k, y, 0.12), lm, "dash")


def sky(st, strength=1.0, sun_energy=4.5, sun=(48, 0, -35)):
    """Replace a Set's gradient sky with the Poly Haven partly-cloudy sky (lights the scene too)."""
    nt = st.scene.world.node_tree; bg = nt.nodes["Background"]
    env = nt.nodes.new("ShaderNodeTexEnvironment"); env.image = bpy.data.images.load(T + "sky.hdr", check_existing=True)
    nt.links.new(env.outputs[0], bg.inputs["Color"]); bg.inputs["Strength"].default_value = strength
    st.sun.data.energy = sun_energy; st.sun.data.color = (1, 0.95, 0.86); st.sun.rotation_euler = [math.radians(a) for a in sun]
    st.scene.eevee.shadow_cascade_size = '4096'; st.sun.data.shadow_cascade_max_distance = 220
    st.scene.view_settings.view_transform = 'Filmic'; st.scene.view_settings.look = 'Medium High Contrast'
    st.scene.view_settings.exposure = 0.0


def _leaf():
    if "leaf" in _mats: return _mats["leaf"]
    m = bpy.data.materials.new("leaf"); m.use_nodes = True; nt = m.node_tree; pb = nt.nodes["Principled BSDF"]
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 6; nz.inputs["Detail"].default_value = 8
    cr = nt.nodes.new("ShaderNodeValToRGB"); cr.color_ramp.elements[0].color = (0.04, 0.13, 0.02, 1); cr.color_ramp.elements[1].color = (0.2, 0.4, 0.07, 1)
    nt.links.new(nz.outputs["Fac"], cr.inputs[0]); nt.links.new(cr.outputs[0], pb.inputs["Base Color"])
    vz = nt.nodes.new("ShaderNodeTexVoronoi"); vz.inputs["Scale"].default_value = 14
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.6
    nt.links.new(vz.outputs["Distance"], bp.inputs["Height"]); nt.links.new(bp.outputs[0], pb.inputs["Normal"])
    pb.inputs["Roughness"].default_value = 0.8
    _mats["leaf"] = m; return m


def _bark():
    if "bark" in _mats: return _mats["bark"]
    m = bpy.data.materials.new("bark"); m.use_nodes = True; pb = m.node_tree.nodes["Principled BSDF"]
    pb.inputs["Base Color"].default_value = (0.08, 0.045, 0.025, 1); pb.inputs["Roughness"].default_value = 0.9
    _mats["bark"] = m; return m


def _blob(loc, r, m):
    import bmesh
    o = _mesh("leaves", lambda bm: bmesh.ops.create_icosphere(bm, subdivisions=4, radius=r), m, loc, smooth=True)
    for v in o.data.vertices:
        v.co *= 1 + 0.12 * noise.noise(v.co * (0.9 / r) + Vector(loc))
    return o


def _cyl(loc, r1, r2, depth, m, segs=10, name="cyl", smooth=False):
    import bmesh
    return _mesh(name, lambda bm: bmesh.ops.create_cone(bm, cap_ends=True, segments=segs, radius1=r1, radius2=r2, depth=depth), m, loc, smooth)


def tree(x, y, s=1.0, seed=0):
    """Leafy street tree (trunk ~13*s tall, crown of lumpy spheres)."""
    rnd = random.Random(seed); h = 13 * s
    _cyl((x, y, h / 2), 0.9 * s, 0.75 * s, h, _bark(), name="trunk")
    for i in range(7):
        a = rnd.uniform(0, 6.28); d = rnd.uniform(1.5, 4.5) * s
        _blob((x + math.cos(a) * d, y + math.sin(a) * d, h + rnd.uniform(-2, 3) * s), rnd.uniform(3.2, 4.8) * s, _leaf())
    _blob((x, y, h + 4 * s), 5 * s, _leaf())


def pine(x, y, s=1.0, seed=0):
    """Background pine (the reference town's tree line): stacked lumpy cones."""
    rnd = random.Random(seed); h = 30 * s
    _cyl((x, y, h * 0.25), 0.7 * s, 0.6 * s, h * 0.5, _bark(), 8, "trunk")
    m = _mats.get("pine")
    if m is None:
        m = _leaf().copy(); m.name = "pine"; cr = [n for n in m.node_tree.nodes if n.type == 'VALTORGB'][0]
        cr.color_ramp.elements[0].color = (0.02, 0.07, 0.03, 1); cr.color_ramp.elements[1].color = (0.06, 0.2, 0.08, 1); _mats["pine"] = m
    for k in range(5):
        z = h * (0.22 + k * 0.16); r = (7.5 - k * 1.3) * s * rnd.uniform(0.9, 1.1)
        o = _cyl((x, y, z), r, 0.0, h * 0.3, m, 14, "pine", smooth=True)
        for v in o.data.vertices: v.co.x *= 1 + 0.15 * noise.noise(v.co * 0.5 + Vector((x, y, k))); v.co.y *= 1 + 0.15 * noise.noise(v.co * 0.5 + Vector((y, x, k)))


def _img_mat(path, emit=1.6):
    if path in _mats: return _mats[path]
    m = bpy.data.materials.new(os.path.basename(path)); m.use_nodes = True; nt = m.node_tree; nn = nt.nodes
    pb = nn["Principled BSDF"]; img = nn.new("ShaderNodeTexImage"); img.image = bpy.data.images.load(path, check_existing=True)
    nt.links.new(img.outputs["Color"], pb.inputs["Base Color"]); nt.links.new(img.outputs["Color"], pb.inputs["Emission Color"])
    nt.links.new(img.outputs["Alpha"], pb.inputs["Alpha"]); pb.inputs["Emission Strength"].default_value = emit
    m.blend_method = 'CLIP'; m.shadow_method = 'NONE'
    _mats[path] = m; return m


def _plane(name, m, parent, loc, w, h):
    import bmesh
    me = bpy.data.meshes.get("badge_plane")
    if me is None:
        me = bpy.data.meshes.new("badge_plane"); bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=0.5)
        bm.to_mesh(me); bm.free(); uv = me.uv_layers.new()
        for poly in me.polygons:
            for li in poly.loop_indices:
                co = me.vertices[me.loops[li].vertex_index].co; uv.data[li].uv = (co.x + 0.5, co.y + 0.5)
        me.materials.append(None)
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o)
    o.material_slots[0].link = 'OBJECT'; o.material_slots[0].material = m
    o.parent = parent; o.location = loc; o.rotation_euler = (math.radians(90), 0, 0); o.scale = (w, h, 1)
    return o


def counter(av, keys, w=1.5, h=0.6):
    """Glowing chest counter on a blocky character. keys = {frame: badge png} (first one from frame 0); each
    picture shows from its frame until the next. Badges are dark rounded plates with mint numbers (see badge_png)."""
    out = {}; items = sorted(keys.items())
    for k, (f, png) in enumerate(items):
        o = _plane(f"{av['name']}_ctr{k}", _img_mat(png), av["waist"], (0, -0.515 - 0.001 * k, 1.25), w, h)
        nxt = items[k + 1][0] if k + 1 < len(items) else None
        for fr_, on in ((0, k == 0), (f, True)) + (((nxt, False),) if nxt is not None else ()):
            o.scale = (w, h, 1) if on else (0.0001, 0.0001, 1); o.keyframe_insert("scale", frame=fr_)
        for fc in o.animation_data.action.fcurves:
            for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'
        o.scale = (w, h, 1) if k == 0 else (0.0001, 0.0001, 1); out[f] = o
    return out


def badge_png(text, path, font, big=False):
    """PIL (outside Blender): the reference's counter badge - dark rounded plate, mint border, mint numbers."""
    from PIL import Image, ImageDraw, ImageFilter
    W, H = (900, 360) if big else (600, 240)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im); r = H // 4
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
    gd.rounded_rectangle((10, 10, W - 10, H - 10), r, outline=(80, 255, 190, 255), width=18)
    im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(8)))
    d.rounded_rectangle((16, 16, W - 16, H - 16), r, fill=(14, 22, 24, 245), outline=(120, 255, 205, 255), width=8)
    f = font(int(H * 0.52)); d.text((W / 2, H / 2 + 4), text, font=f, anchor="mm", fill=(140, 255, 210), stroke_width=2, stroke_fill=(20, 60, 50))
    im.save(path)


def cloth_png(kind, base, accent, path, accent2=(250, 250, 250)):
    """PIL (outside Blender): a 512px tileable print for blocky clothes - plaid, stripes, floral, dots, denim."""
    from PIL import Image, ImageDraw, ImageFilter
    import random as R
    S = 512; rnd = R.Random(hash((kind, base, accent)) & 0xffff)
    im = Image.new("RGB", (S, S), base); d = ImageDraw.Draw(im, "RGBA")
    if kind == "plaid":
        for k in range(0, S, 128):
            d.rectangle((k, 0, k + 44, S), fill=accent + (150,)); d.rectangle((0, k, S, k + 44), fill=accent + (150,))
            d.rectangle((k + 70, 0, k + 78, S), fill=accent2 + (120,)); d.rectangle((0, k + 70, S, k + 78), fill=accent2 + (120,))
    elif kind == "stripes":
        for k in range(0, S, 64): d.rectangle((0, k, S, k + 28), fill=accent + (255,))
    elif kind == "floral":
        for _ in range(70):
            x, y = rnd.randrange(S), rnd.randrange(S); r = rnd.randint(10, 22); c = rnd.choice([accent, accent2])
            for a in range(5):
                px, py = x + math.cos(a * 1.257) * r, y + math.sin(a * 1.257) * r
                for ox in (-S, 0, S):
                    for oy in (-S, 0, S): d.ellipse((px - r * 0.6 + ox, py - r * 0.6 + oy, px + r * 0.6 + ox, py + r * 0.6 + oy), fill=c + (255,))
            d.ellipse((x - 5, y - 5, x + 5, y + 5), fill=(250, 220, 90, 255))
    elif kind == "dots":
        for y in range(0, S, 64):
            for x in range(0, S, 64): d.ellipse((x + (32 if (y // 64) % 2 else 0) - 12, y - 12, x + (32 if (y // 64) % 2 else 0) + 12, y + 12), fill=accent + (255,))
    elif kind == "denim":
        for _ in range(6000):
            x, y = rnd.randrange(S), rnd.randrange(S); d.line((x, y, x + 6, y + 6), fill=accent + (90,), width=1)
    # soft fabric noise so flat areas don't look like plastic
    for _ in range(3000):
        x, y = rnd.randrange(S), rnd.randrange(S); v = rnd.randint(-18, 18)
        d.point((x, y), fill=(128 + v, 128 + v, 128 + v, 40))
    im.filter(ImageFilter.GaussianBlur(0.6)).save(path)
