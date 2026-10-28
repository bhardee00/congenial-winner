"""Blender side of the avatar: builds the posable R15 character from work/avatar/rig.json (made by prep_avatar.py).
build(D) returns {"root", pivot name -> empty ("torso", "waist", "head", "la", "la_elbow", ..., "rl_ankle"),
"faces": {"smile", "shock"}, "grips": {"la", "ra"} -> empties in the hands to parent props to}.
Rotating a pivot bends that joint; pivots have no rotation at rest so (-80, 0, 50) on "ra" raises the right arm."""
import json, math, os, glob
import bpy, bmesh
from anim import key, value
from mathutils import Vector

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets") + "/"


def _lin(c): return tuple(((x / 255 + 0.055) / 1.055) ** 2.4 if x / 255 > 0.04045 else x / 255 / 12.92 for x in c) + (1,)


def _empty(name, loc, parent=None):
    o = bpy.data.objects.new(name, None); bpy.context.scene.collection.objects.link(o)
    o.empty_display_size = 0.2
    if parent: o.parent = parent
    o.location = loc
    return o


def _material(name, D, tex, color, alpha=False):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nn = m.node_tree.nodes; pb = nn["Principled BSDF"]
    pb.inputs["Roughness"].default_value = 0.55
    pb.inputs["Base Color"].default_value = _lin(color)
    if tex:
        img = nn.new("ShaderNodeTexImage"); img.image = bpy.data.images.load(D + "avatar/" + tex)
        m.node_tree.links.new(img.outputs["Color"], pb.inputs["Base Color"])
        if alpha:
            m.node_tree.links.new(img.outputs["Alpha"], pb.inputs["Alpha"])
            m.blend_method = 'CLIP'; m.shadow_method = 'CLIP'
    return m


def _npc_color(n, look):
    """Plain-coloured outfit for side characters: shirt on torso/arms, pants on legs, shoes on feet."""
    if n == "UpperTorso" or "Arm" in n: return look.get("shirt", (90, 90, 90))
    if n == "LowerTorso" or "UpperLeg" in n or "LowerLeg" in n: return look.get("pants", (40, 40, 60))
    if "Foot" in n: return look.get("shoes", (30, 30, 30))
    return look.get("skin", (204, 142, 105))


def build(D, name="me", look=None):
    """look=None is the channel avatar. For side characters pass look={"shirt", "pants", "shoes", "skin": rgb,
    "hair": bool (Pal Hair, tinted by "hair_color"), "scale": float} - no crown, plain clothes."""
    rig = json.load(open(D + "avatar/rig.json"))
    J = rig["joints"]
    root = _empty(name, (0, 0, 0))
    piv = {}
    def pivot(k):
        if k not in piv:
            p = rig["parents"][k]
            par = pivot(p) if p else root
            base = Vector(J[p]) if p else Vector((0, 0, 0))
            piv[k] = _empty(k, Vector(J[k]) - base, par)
        return piv[k]
    for k in J: pivot(k)

    mats = {}
    for m in rig["meshes"]:
        if look is not None:
            if "UL" not in m and not (look.get("hair") and "Hair" in m["name"]): continue  # no crown / hair
            m = {**m, "tex": None, "color": look.get("hair_color", (60, 40, 25)) if "Hair" in m["name"] else _npc_color(m["name"], look)}
        key = (m["tex"], tuple(m["color"]))
        if key not in mats: mats[key] = _material("av_" + (m["tex"] or "plain"), D, m["tex"], m["color"], alpha=bool(m["tex"]))
        me = bpy.data.meshes.new(m["name"])
        org = Vector(J[m["pivot"]])
        me.from_pydata([tuple(Vector(v) - org) for v in m["V"]], [], [tuple(f) for f in m["F"]])
        uv = me.uv_layers.new()
        # body parts carry per-corner template UVs ("UL"); accessories use the mesh's own per-vertex UVs
        for poly in me.polygons:
            for k, li in enumerate(poly.loop_indices):
                uv.data[li].uv = m["UL"][poly.index][k] if "UL" in m else m["U"][me.loops[li].vertex_index]
        me.materials.append(mats[key])
        for p in me.polygons: p.use_smooth = True
        o = bpy.data.objects.new(m["name"], me); bpy.context.scene.collection.objects.link(o)
        o.parent = piv[m["pivot"]]
        o.modifiers.new("ws", "WEIGHTED_NORMAL"); me.use_auto_smooth = True; me.auto_smooth_angle = math.radians(50)
        # Roblox meshes split verts at UV seams; merge so shading is continuous
        bm = bmesh.new(); bm.from_mesh(me); bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4); bm.to_mesh(me); bm.free()

    # default head: rounded block plus swappable face decals
    head = piv["head"]; hc = Vector(rig["head"]["center"]) - Vector(J["head"]); s = rig["head"]["size"]
    bpy.ops.mesh.primitive_cube_add(size=1, location=hc)
    h = bpy.context.view_layer.objects.active; h.name = "Head"; h.scale = (s[0] * 1.04, s[2], s[1]); h.parent = head
    h.location = hc
    bpy.ops.object.transform_apply(scale=True)
    bv = h.modifiers.new("b", "BEVEL"); bv.width = 0.32; bv.segments = 5; bv.limit_method = 'NONE'
    for p in h.data.polygons: p.use_smooth = True
    # skin colour can blend towards red (angry) or pale blue (cold) via the "flush" mix factor
    skin = look.get("skin", rig["skin"]) if look else rig["skin"]
    sm = _material("av_skin", D, None, skin); nn = sm.node_tree.nodes
    mix = nn.new("ShaderNodeMixRGB"); mix.name = "flush"; mix.inputs["Fac"].default_value = 0
    mix.inputs["Color1"].default_value = _lin(skin); mix.inputs["Color2"].default_value = _lin((235, 40, 30))
    sm.node_tree.links.new(mix.outputs["Color"], nn["Principled BSDF"].inputs["Base Color"])
    h.data.materials.append(sm)
    faces = {}
    for k in sorted(os.path.basename(f)[5:-4] for f in glob.glob(ASSETS + "face_*.png")):
        m = bpy.data.materials.new("face_" + k); m.use_nodes = True; m.blend_method = 'CLIP'; m.shadow_method = 'CLIP'
        nn = m.node_tree.nodes; img = nn.new("ShaderNodeTexImage"); img.image = bpy.data.images.load(ASSETS + f"face_{k}.png")
        pb = nn["Principled BSDF"]; pb.inputs["Roughness"].default_value = 0.5
        m.node_tree.links.new(img.outputs["Color"], pb.inputs["Base Color"]); m.node_tree.links.new(img.outputs["Alpha"], pb.inputs["Alpha"])
        bpy.ops.mesh.primitive_plane_add(size=s[0] * 0.88, location=hc + Vector((0, -s[2] / 2 - 0.012, 0)), rotation=(math.radians(90), 0, 0))
        fo = bpy.context.view_layer.objects.active; fo.name = "face_" + k; fo.data.materials.append(m); fo.parent = head
        fo.location = hc + Vector((0, -s[2] / 2 - 0.012, 0))
        faces[k] = fo
    for k, fo in faces.items(): fo.hide_render = fo.hide_viewport = k != "smile"

    grips = {k: _empty("grip_" + k, Vector(g) - Vector(J[k + "_wrist"]), piv[k + "_wrist"]) for k, g in rig["grips"].items()}
    if look and look.get("scale"): root.scale = (look["scale"],) * 3
    return {"root": root, **piv, "faces": faces, "grips": grips, "skin": sm, "face_pos": faces["smile"].location.copy(),
            "joints": J, "scale": look.get("scale", 1.0) if look else 1.0,
            "eyes": [hc + Vector((x, -s[2] / 2 - 0.03, 0.06)) for x in (-0.22, 0.22)], "reacts": []}


def react(av, face, f0, f1=None):
    """Switch to an expression at frame f0 (held until the next react). Some faces add effects up to f1:
    shock / big_eyes pop the face bigger, angry flushes the head red and shakes it, cry drips tears.
    Faces: see faces.py (smile, shock, big_eyes, happy, grin, sad, cry, angry, annoyed, suspicious, nervous, ...)."""
    f1 = f1 if f1 is not None else f0 + 45
    prev = av["reacts"][-1][1] if av["reacts"] else "smile"
    for k, fo in av["faces"].items():
        if not av["reacts"]: _vis(fo, k == "smile", 0)
        _vis(fo, k == prev, f0 - 1); _vis(fo, k == face, f0)
    av["reacts"].append((f0, face))
    fo = av["faces"][face]
    if face in ("shock", "big_eyes"):
        for f, sc in ((f0 - 1, 1.0), (f0 + 3, 1.28), (f0 + 8, 1.0)):
            fo.scale = (sc, sc, sc); fo.keyframe_insert("scale", frame=f)
        h = av["head"]; base = value(h, "rotation_euler", f0)
        for f, dx in ((f0, 0), (f0 + 3, -9), (f0 + 9, 0)):
            key(h, "rotation_euler", f, (base[0] + math.radians(dx), base[1], base[2]))
    if face == "angry":
        fac = av["skin"].node_tree.nodes["flush"].inputs["Fac"]
        for f, v in ((f0, 0), (f0 + 10, 0.55), (f1 - 8, 0.55), (f1, 0)):
            fac.default_value = v; fac.keyframe_insert("default_value", frame=f)
        h = av["head"]; base = value(h, "rotation_euler", f0 + 6)
        for i, f in enumerate(range(f0 + 6, min(f1, f0 + 30), 2)):  # quick shake
            key(h, "rotation_euler", f, (base[0], base[1] + math.radians(4 if i % 2 else -4), base[2]))
        key(h, "rotation_euler", min(f1, f0 + 32), base)
    if face == "cry":
        _tears(av, f0, f1)


def _vis(o, on, f):
    o.hide_render = not on; o.keyframe_insert("hide_render", frame=f)
    o.hide_viewport = not on; o.keyframe_insert("hide_viewport", frame=f)


def _tears(av, f0, f1, every=7):
    m = bpy.data.materials.get("tear") or _material("tear", "", None, (110, 185, 255))
    m.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.05
    for i, f in enumerate(range(f0 + 4, f1 - 10, every)):
        eye = av["eyes"][i % 2]
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.055, segments=12, ring_count=8)
        t = bpy.context.view_layer.objects.active; t.name = "tear"; t.data.materials.append(m); t.parent = av["head"]
        t.scale = (0.8, 0.8, 1.3)
        for fr, off, vis in ((f - 1, 0, False), (f, 0, True), (f + 12, -0.75, True), (f + 13, -0.75, False)):
            t.location = eye + Vector((0, -0.02, off)); t.keyframe_insert("location", frame=fr)
            t.hide_render = not vis; t.keyframe_insert("hide_render", frame=fr)
        for fc in t.animation_data.action.fcurves:
            for kp in fc.keyframe_points: kp.interpolation = 'QUAD' if fc.data_path == "location" else 'CONSTANT'
        t.hide_render = True
