"""Blender side of the avatar: builds the posable R15 character from work/avatar/rig.json (made by prep_avatar.py).
build(D) returns {"root", pivot name -> empty ("torso", "waist", "head", "la", "la_elbow", ..., "rl_ankle"),
"faces": {"smile", "shock"}, "grips": {"la", "ra"} -> empties in the hands to parent props to}.
Rotating a pivot bends that joint; pivots have no rotation at rest so (-80, 0, 50) on "ra" raises the right arm."""
import json, math
import bpy, bmesh
from mathutils import Vector


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


def build(D, name="me"):
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
    h = bpy.context.active_object; h.name = "Head"; h.scale = (s[0] * 1.04, s[2], s[1]); h.parent = head
    h.location = hc
    bpy.ops.object.transform_apply(scale=True)
    bv = h.modifiers.new("b", "BEVEL"); bv.width = 0.32; bv.segments = 5; bv.limit_method = 'NONE'
    for p in h.data.polygons: p.use_smooth = True
    h.data.materials.append(_material("av_skin", D, None, rig["skin"]))
    faces = {}
    for k in ("smile", "shock"):
        m = bpy.data.materials.new("face_" + k); m.use_nodes = True; m.blend_method = 'CLIP'; m.shadow_method = 'CLIP'
        nn = m.node_tree.nodes; img = nn.new("ShaderNodeTexImage"); img.image = bpy.data.images.load(D + f"face_{k}.png")
        pb = nn["Principled BSDF"]; pb.inputs["Roughness"].default_value = 0.5
        m.node_tree.links.new(img.outputs["Color"], pb.inputs["Base Color"]); m.node_tree.links.new(img.outputs["Alpha"], pb.inputs["Alpha"])
        bpy.ops.mesh.primitive_plane_add(size=s[0] * 0.88, location=hc + Vector((0, -s[2] / 2 - 0.012, 0)), rotation=(math.radians(90), 0, 0))
        fo = bpy.context.active_object; fo.name = "face_" + k; fo.data.materials.append(m); fo.parent = head
        fo.location = hc + Vector((0, -s[2] / 2 - 0.012, 0))
        faces[k] = fo
    faces["shock"].hide_render = True; faces["shock"].hide_viewport = True

    grips = {k: _empty("grip_" + k, Vector(g) - Vector(J[k + "_wrist"]), piv[k + "_wrist"]) for k, g in rig["grips"].items()}
    return {"root": root, **piv, "faces": faces, "grips": grips}
