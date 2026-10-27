"""Blender side of Creator Store models: place(D, asset_id, loc, rot_z, scale) rebuilds work/models/<id>.json
(made by rbx_model.py) under one empty and returns it. Primitive and mesh data are shared between copies."""
import json, math
import bpy, bmesh
from mathutils import Matrix, Vector

_MESH, _MAT, _JSON = {}, {}, {}


def _lin(c): return tuple(((x / 255 + 0.055) / 1.055) ** 2.4 if x / 255 > 0.04045 else x / 255 / 12.92 for x in c[:3]) + (1,)


def _unit(kind):
    """Shared unit-size primitives in Roblox part space (cylinder along X like Roblox, cylY along Y)."""
    if kind in _MESH: return _MESH[kind]
    bm = bmesh.new()
    if kind == "box":
        bmesh.ops.create_cube(bm, size=1)
    elif kind == "ball":
        bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=12, radius=0.5)
    elif kind in ("cyl", "cylY"):
        bmesh.ops.create_cone(bm, cap_ends=True, segments=24, radius1=0.5, radius2=0.5, depth=1,
                              matrix=Matrix.Rotation(math.radians(90), 4, "Y" if kind == "cyl" else "X"))
    elif kind == "wedge":  # Roblox wedge: full bottom and back (+Z), slope facing front (-Z) and up
        v = [bm.verts.new(p) for p in ((-.5, -.5, -.5), (.5, -.5, -.5), (.5, -.5, .5), (-.5, -.5, .5), (-.5, .5, .5), (.5, .5, .5))]
        for f in ((0, 1, 2, 3), (3, 2, 5, 4), (0, 4, 5, 1), (0, 3, 4), (1, 5, 2)): bm.faces.new([v[i] for i in f])
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new("rbx_" + kind); bm.to_mesh(me); bm.free()
    if kind in ("ball", "cyl", "cylY"):
        for p in me.polygons: p.use_smooth = True
        me.use_auto_smooth = True; me.auto_smooth_angle = math.radians(40)
    _MESH[kind] = me
    return me


def _filemesh(path):
    if path in _MESH: return _MESH[path]
    d = json.load(open(path))
    me = bpy.data.meshes.new("rbxmesh"); me.from_pydata([tuple(v) for v in d["V"]], [], [tuple(f) for f in d["F"]])
    uv = me.uv_layers.new()
    for poly in me.polygons:
        for li in poly.loop_indices: uv.data[li].uv = d["U"][me.loops[li].vertex_index]
    for p in me.polygons: p.use_smooth = True
    me.use_auto_smooth = True; me.auto_smooth_angle = math.radians(45)
    lo = Vector([min(v[k] for v in d["V"]) for k in range(3)]); hi = Vector([max(v[k] for v in d["V"]) for k in range(3)])
    _MESH[path] = (me, lo, hi)
    return _MESH[path]


def _material(it):
    key = (tuple(it["color"]), round(it["alpha"], 2), it["mat"], it.get("tex"), it["kind"] == "decal")
    if key in _MAT: return _MAT[key]
    m = bpy.data.materials.new("rbx_" + it["mat"]); m.use_nodes = True
    nn = m.node_tree.nodes; pb = nn["Principled BSDF"]; L = m.node_tree.links
    pb.inputs["Base Color"].default_value = _lin(it["color"])
    pb.inputs["Roughness"].default_value = {"metal": 0.35, "glass": 0.05, "ice": 0.1, "neon": 0.5}.get(it["mat"], 0.6)
    if it["mat"] == "metal": pb.inputs["Metallic"].default_value = 0.8
    if it["mat"] == "neon":
        pb.inputs["Emission Color"].default_value = _lin(it["color"]); pb.inputs["Emission Strength"].default_value = 3
    a = it["alpha"] * (0.45 if it["mat"] == "glass" else 1)
    if it.get("tex"):
        img = nn.new("ShaderNodeTexImage"); img.image = bpy.data.images.load(it["tex"], check_existing=True)
        if it["kind"] == "decal":
            L.new(img.outputs["Color"], pb.inputs["Base Color"]); L.new(img.outputs["Alpha"], pb.inputs["Alpha"])
        else:  # texture over the part colour where the texture is transparent
            mix = nn.new("ShaderNodeMixRGB"); mix.inputs["Color1"].default_value = _lin(it["color"])
            L.new(img.outputs["Alpha"], mix.inputs["Fac"]); L.new(img.outputs["Color"], mix.inputs["Color2"])
            L.new(mix.outputs["Color"], pb.inputs["Base Color"])
        m.blend_method = 'CLIP' if it["kind"] == "decal" else m.blend_method; m.shadow_method = 'CLIP'
    if a < 0.98:
        pb.inputs["Alpha"].default_value = a; m.blend_method = 'BLEND'; m.shadow_method = 'HASHED'
        m.show_transparent_back = False
    _MAT[key] = m
    return m


def _decal(it):
    a, s = it["face"]; size = it["size"]
    n = Vector([0, 0, 0]); n[a] = s
    up = Vector((0, 0, -1)) if a == 1 and s > 0 else Vector((0, 0, 1)) if a == 1 else Vector((0, 1, 0))
    right = (-n).cross(up)
    ext = lambda v: abs(v.x) * size[0] + abs(v.y) * size[1] + abs(v.z) * size[2]
    c = n * (size[a] / 2 + 0.01); hr = right * (ext(right) / 2); hu = up * (ext(up) / 2)
    me = bpy.data.meshes.new("decal")
    me.from_pydata([tuple(c - hr - hu), tuple(c + hr - hu), tuple(c + hr + hu), tuple(c - hr + hu)], [], [(0, 1, 2, 3)])
    uv = me.uv_layers.new()
    for li, t in zip(range(4), ((0, 0), (1, 0), (1, 1), (0, 1))): uv.data[li].uv = t
    return me


def place(D, asset_id, loc=(0, 0, 0), rot_z=0.0, scale=1.0, name=None, coll=None):
    p = D + f"models/{asset_id}.json"
    if p not in _JSON: _JSON[p] = json.load(open(p))
    coll = coll or bpy.context.scene.collection
    root = bpy.data.objects.new(name or f"model_{asset_id}", None); coll.objects.link(root)
    root.location = loc; root.rotation_euler = (0, 0, math.radians(rot_z)); root.scale = (scale,) * 3
    for it in _JSON[p]["items"]:
        M = Matrix(it["M"])
        if it["kind"] == "decal":
            me = _decal(it)
        elif it["kind"] == "mesh":
            me, lo, hi = _filemesh(it["mesh"])
            if "fit" in it:  # MeshPart: mesh bounds stretched to the part size
                sz = hi - lo; f = Vector(it["fit"])
                M = M @ Matrix.Diagonal(Vector([f[k] / max(sz[k], 1e-6) for k in range(3)] + [1])) @ Matrix.Translation(-(lo + hi) / 2)
            else:
                M = M @ Matrix.Diagonal(Vector(list(it.get("scale", (1, 1, 1))) + [1]))
        else:
            me = _unit(it["kind"]); M = M @ Matrix.Diagonal(Vector(list(it["size"]) + [1]))
        if not me.materials: me.materials.append(None)  # one slot; each object fills it with its own material
        o = bpy.data.objects.new("rbx", me); coll.objects.link(o)
        o.parent = root; o.matrix_basis = M
        o.material_slots[0].link = 'OBJECT'; o.material_slots[0].material = _material(it)
    return root
