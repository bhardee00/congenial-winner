"""Blender: classic blocky characters (2x2x1 torso, 1x2x1 limbs, rounded head) like the reference channels.
build(D, name, look) returns the same rig dict as avatar.build, so shortkit acting helpers and avatar.react
(faces, red flush, tears, pop) work unchanged. look=None dresses it in the channel avatar's shirt/pants templates
(work/avatar/tex_*.png) with its hair and crown; otherwise plain colours:
look = {"shirt", "pants", "shoes", "skin", "hair": rgb or None, "hat": "cap"|"propeller"|"beret"|None, "scale"}."""
import json, math, os, glob
import bpy, bmesh
from mathutils import Vector
import avatar

TEMPLATE = (585, 559)
RECTS = {"torso": {"F": (231, 74, 128, 128), "B": (427, 74, 128, 128), "R": (165, 74, 64, 128), "L": (361, 74, 64, 128),
                   "U": (231, 8, 128, 64), "D": (231, 204, 128, 64)},
         "right": {"L": (19, 355, 64, 128), "B": (85, 355, 64, 128), "R": (151, 355, 64, 128), "F": (217, 355, 64, 128),
                   "U": (217, 289, 64, 64), "D": (217, 485, 64, 64)},
         "left": {"F": (308, 355, 64, 128), "L": (374, 355, 64, 128), "B": (440, 355, 64, 128), "R": (506, 355, 64, 128),
                  "U": (308, 289, 64, 64), "D": (308, 485, 64, 64)}}


def _empty(name, loc, parent=None):
    o = bpy.data.objects.new(name, None); bpy.context.scene.collection.objects.link(o)
    o.empty_display_size = 0.2
    if parent: o.parent = parent
    o.location = loc
    return o


def _box(name, size, center, mat, parent, rects=None, bevel=0.06):
    """A block with optional classic-template UVs. Blender axes: character faces -Y, its right is -X."""
    sx, sy, sz = size; hx, hy, hz = sx / 2, sy / 2, sz / 2
    bm = bmesh.new(); uvl = bm.loops.layers.uv.new()
    # faces as (template side, 4 corners seen from outside: bottom-left, bottom-right, top-right, top-left)
    F = {"F": [(-hx, -hy, -hz), (hx, -hy, -hz), (hx, -hy, hz), (-hx, -hy, hz)],     # front (-Y): image left = char's right (-X)
         "B": [(hx, hy, -hz), (-hx, hy, -hz), (-hx, hy, hz), (hx, hy, hz)],
         "R": [(-hx, hy, -hz), (-hx, -hy, -hz), (-hx, -hy, hz), (-hx, hy, hz)],     # character's right side (-X)
         "L": [(hx, -hy, -hz), (hx, hy, -hz), (hx, hy, hz), (hx, -hy, hz)],
         "U": [(-hx, -hy, hz), (hx, -hy, hz), (hx, hy, hz), (-hx, hy, hz)],        # front edge at the bottom of the image
         "D": [(-hx, hy, -hz), (hx, hy, -hz), (hx, -hy, -hz), (-hx, -hy, -hz)]}
    for side, corners in F.items():
        f = bm.faces.new([bm.verts.new(c) for c in corners])
        if rects:
            x, y, w, h = rects[side]
            uv = [(x + 0.5, y + h - 0.5), (x + w - 0.5, y + h - 0.5), (x + w - 0.5, y + 0.5), (x + 0.5, y + 0.5)]
            for l, (u, v) in zip(f.loops, uv): l[uvl].uv = (u / TEMPLATE[0], 1 - v / TEMPLATE[1])
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(mat)
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o)
    o.parent = parent; o.location = center
    if bevel:
        b = o.modifiers.new("b", "BEVEL"); b.width = bevel; b.segments = 3; b.limit_method = 'NONE'; b.harden_normals = True
        me.use_auto_smooth = True
    return o


def _mat(name, color=None, tex=None, rough=0.55):
    m = bpy.data.materials.new(name); m.use_nodes = True; nn = m.node_tree.nodes; pb = nn["Principled BSDF"]
    pb.inputs["Roughness"].default_value = rough
    if color: pb.inputs["Base Color"].default_value = avatar._lin(color)
    if tex:
        img = nn.new("ShaderNodeTexImage"); img.image = bpy.data.images.load(tex, check_existing=True)
        img.interpolation = 'Closest' if False else 'Linear'
        m.node_tree.links.new(img.outputs["Color"], pb.inputs["Base Color"])
    return m


def build(D, name="me", look=None):
    rig = json.load(open(D + "avatar/rig.json"))
    skin = (look or {}).get("skin", tuple(rig["skin"]))
    root = _empty(name, (0, 0, 0))
    waist = _empty(name + "_waist", (0, 0, 2.0), root)          # hips: upper body bends here
    head = _empty(name + "_head", (0, 0, 2.0), waist)           # neck (z 4 in the world)
    la = _empty(name + "_la", (1.5, 0, 1.5), waist); ra = _empty(name + "_ra", (-1.5, 0, 1.5), waist)
    ll = _empty(name + "_ll", (0.5, 0, 2.0), root); rl = _empty(name + "_rl", (-0.5, 0, 2.0), root)
    # joints the R15 helpers expect; blocky limbs don't bend there, so they are just carried along
    extra = {"la_elbow": la, "ra_elbow": ra, "la_wrist": la, "ra_wrist": ra, "ll_knee": ll, "rl_knee": rl, "ll_ankle": ll, "rl_ankle": rl}
    piv = {"torso": waist, "waist": waist, "head": head, "la": la, "ra": ra, "ll": ll, "rl": rl}
    for k, p in extra.items(): piv[k] = _empty(f"{name}_{k}", (0, 0, 0), p)
    if look is None:
        A = D + "avatar/"
        mt, mal, mar, mll, mlr = (_mat(f"{name}_{k}", tex=A + f"tex_{k}.png") for k in ("torso", "arm_l", "arm_r", "leg_l", "leg_r"))
        rt, rr, rlf = RECTS["torso"], RECTS["right"], RECTS["left"]
    else:
        mt = _mat(name + "_shirt", look.get("shirt", (80, 120, 200))); mal = mar = _mat(name + "_sleeve", look.get("sleeves", look.get("shirt", (80, 120, 200))))
        mll = mlr = _mat(name + "_pants", look.get("pants", (50, 50, 70))); rt = rr = rlf = None
    _box(name + "_torso", (2, 1, 2), (0, 0, 1.0), mt, waist, rt)
    _box(name + "_arm_l", (1, 1, 2), (0, 0, -0.5), mal, la, rlf)
    _box(name + "_arm_r", (1, 1, 2), (0, 0, -0.5), mar, ra, rr)
    _box(name + "_leg_l", (1, 1, 2), (0, 0, -1.0), mll, ll, rlf)
    _box(name + "_leg_r", (1, 1, 2), (0, 0, -1.0), mlr, rl, rr)
    if look is not None:
        hand = _mat(name + "_hand", skin)
        for p, x in ((la, 0), (ra, 0)): _box(name + "_hand", (1.02, 1.02, 0.45), (x, 0, -1.3), hand, p, bevel=0.08)
        shoe = _mat(name + "_shoe", look.get("shoes", (40, 40, 45)))
        for p in (ll, rl): _box(name + "_shoe", (1.04, 1.12, 0.4), (0, -0.04, -1.82), shoe, p, bevel=0.08)
    # head: rounded block + faces (from avatar.py's drawing), skin can flush red
    sm = avatar._material(name + "_skin", D, None, skin); nn = sm.node_tree.nodes
    mix = nn.new("ShaderNodeMixRGB"); mix.name = "flush"; mix.inputs["Fac"].default_value = 0
    mix.inputs["Color1"].default_value = avatar._lin(skin); mix.inputs["Color2"].default_value = avatar._lin((235, 40, 30))
    sm.node_tree.links.new(mix.outputs["Color"], nn["Principled BSDF"].inputs["Base Color"])
    hc = Vector((0, 0, 0.62)); hs = 1.25
    hb = _box(name + "_headblock", (hs * 1.05, hs * 0.98, hs), hc, sm, head, bevel=0.32)
    hb.modifiers["b"].segments = 6
    faces = {}
    for k in sorted(os.path.basename(f)[5:-4] for f in glob.glob(avatar.ASSETS + "face_*.png")):
        m = bpy.data.materials.get("face_" + k)
        if m is None:
            m = bpy.data.materials.new("face_" + k); m.use_nodes = True; m.blend_method = 'CLIP'; m.shadow_method = 'CLIP'
            t = m.node_tree.nodes; img = t.new("ShaderNodeTexImage"); img.image = bpy.data.images.load(avatar.ASSETS + f"face_{k}.png", check_existing=True)
            pb = t["Principled BSDF"]; pb.inputs["Roughness"].default_value = 0.5
            m.node_tree.links.new(img.outputs["Color"], pb.inputs["Base Color"]); m.node_tree.links.new(img.outputs["Alpha"], pb.inputs["Alpha"])
        me = bpy.data.meshes.get("faceplane") or _faceplane()
        fo = bpy.data.objects.new(f"{name}_face_{k}", me); bpy.context.scene.collection.objects.link(fo)
        fo.material_slots[0].link = 'OBJECT'; fo.material_slots[0].material = m
        fo.parent = head; fo.location = hc + Vector((0, -hs * 0.49 - 0.012, 0)); fo.scale = (hs * 0.9, hs * 0.9, 1)
        fo.rotation_euler = (math.radians(90), 0, 0)
        fo.hide_render = fo.hide_viewport = k != "smile"; faces[k] = fo
    # hair / crown from the channel avatar, or simple hats for side characters
    if look is None:
        hcen = Vector(rig["head"]["center"])
        for m in rig["meshes"]:
            if "UL" in m: continue
            me = bpy.data.meshes.new(m["name"]); me.from_pydata([tuple(Vector(v) - hcen) for v in m["V"]], [], [tuple(f) for f in m["F"]])
            uv = me.uv_layers.new()
            for poly in me.polygons:
                for li in poly.loop_indices: uv.data[li].uv = m["U"][me.loops[li].vertex_index]
            for p in me.polygons: p.use_smooth = True
            me.materials.append(avatar._material("acc_" + (m["tex"] or "x"), D, m["tex"], m["color"], alpha=bool(m["tex"])))
            o = bpy.data.objects.new(f"{name}_{m['name']}", me); bpy.context.scene.collection.objects.link(o)
            o.parent = head; o.location = hc + Vector((0, 0, 0.04)); o.scale = (1.04, 1.04, 1.04)
    else:
        if look.get("hair"):
            hm = _mat(name + "_hair", look["hair"], rough=0.7)
            _box(name + "_hair", (hs * 1.12, hs * 1.06, 0.42), hc + Vector((0, 0.03, hs * 0.45)), hm, head, bevel=0.15)
            _box(name + "_hairback", (hs * 1.12, 0.32, hs * 0.75), hc + Vector((0, hs * 0.44, 0.08)), hm, head, bevel=0.12)
            if look.get("pigtails"):
                for s in (-1, 1): _box(name + "_tail", (0.32, 0.32, 0.7), hc + Vector((s * 0.78, 0.15, 0.05)), hm, head, bevel=0.12)
        hat = look.get("hat")
        if hat in ("cap", "propeller"):
            cm = _mat(name + "_cap", look.get("hat_color", (220, 50, 50)))
            _box(name + "_cap", (hs * 1.1, hs * 1.04, 0.36), hc + Vector((0, 0, hs * 0.55)), cm, head, bevel=0.14)
            _box(name + "_brim", (hs * 0.9, 0.55, 0.08), hc + Vector((0, -hs * 0.68, hs * 0.4)), cm, head, bevel=0.03)
            if hat == "propeller":
                _box(name + "_stem", (0.08, 0.08, 0.3), hc + Vector((0, 0, hs * 0.85)), _mat("stem", (240, 200, 40)), head, bevel=0)
                prop = _empty(name + "_prop", hc + Vector((0, 0, hs * 1.0)), head)
                for a in (0, 90):
                    p = _box(name + "_blade", (1.2, 0.14, 0.04), (0, 0, 0), _mat("blade", (60, 130, 230)), prop, bevel=0)
                    p.rotation_euler = (0, 0, math.radians(a))
                prop.keyframe_insert("rotation_euler", frame=0); prop.rotation_euler = (0, 0, math.radians(360 * 40))
                prop.keyframe_insert("rotation_euler", frame=4000)
                for fc in prop.animation_data.action.fcurves:
                    for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
        elif hat == "beret":
            _box(name + "_beret", (hs * 1.15, hs * 1.1, 0.25), hc + Vector((0.1, 0, hs * 0.55)), _mat("beret", (25, 25, 30)), head, bevel=0.12)
    grips = {"la": _empty(name + "_grip_la", (0, -0.05, -1.45), la), "ra": _empty(name + "_grip_ra", (0, -0.05, -1.45), ra)}
    if look and look.get("scale"): root.scale = (look["scale"],) * 3
    s = look.get("scale", 1.0) if look else 1.0
    eyes = [hc + Vector((x, -hs * 0.5 - 0.03, 0.06)) for x in (-0.22, 0.22)]
    av = {"root": root, **piv, "faces": faces, "grips": grips, "skin": sm, "reacts": [], "eyes": eyes,
          "joints": {"ll": [0.5, 0, 2.0]}, "scale": s, "face_pos": faces["smile"].location.copy(), "name": name}
    avatar.ALL.append(av)
    return av


def _faceplane():
    me = bpy.data.meshes.new("faceplane"); bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=0.5)
    bm.to_mesh(me); bm.free(); uv = me.uv_layers.new()
    for poly in me.polygons:
        for li in poly.loop_indices:
            co = me.vertices[me.loops[li].vertex_index].co; uv.data[li].uv = (co.x + 0.5, co.y + 0.5)
    me.materials.append(None)
    return me
