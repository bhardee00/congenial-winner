"""Roblox VFX in Blender: plays flipbook textures from free Creator Store VFX packs (downloaded by store.py into
work/models/cache, indexed in work/models/vfx_index.json) as animated sprites.
    vfx.burst("splash", loc, f, size=3, face=camera_location, tint=(170, 220, 255))
Presets name a texture and its flipbook grid; any texture id from the index also works with grid=(4, 4)."""
import math, os
import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(os.path.dirname(HERE), "work", "models", "cache") + "/"
KEPT = os.path.join(os.path.dirname(HERE), "assets", "vfx") + "/"  # the presets, kept in the repo
# from "MASSIVE Vfx Pack" (asset 99987311514598) and "VFX PACK" (112672322113504), both free
PRESETS = {
    "splash": ("82438454955771", 4),     # cartoon liquid splash
    "drops": ("72464786650138", 4),      # small water droplets
    "puff": ("136795493746726", 4),      # cartoon smoke puff (poof / dust / impact cloud)
    "burst": ("98511101471915", 4),      # white star burst (hit / pop)
    "glint": ("109204940734898", 4),     # twinkle glint (sparkle)
    "ring": ("96788219463216", 4),       # shockwave ring
    "ringburst": ("16047576636", 4),     # ring burst
    "flash": ("15814918201", 4),         # impact flash (blue-white)
    "dust": ("91803413175576", 4),       # dust / smoke dissolving
}


def _mat(tex, n, f0, frames, step, tint, emit):
    m = bpy.data.materials.new(f"vfx_{tex}_{f0}"); m.use_nodes = True; nt = m.node_tree; nn = nt.nodes
    nn.remove(nn["Principled BSDF"])
    img = nn.new("ShaderNodeTexImage"); img.image = bpy.data.images.load((KEPT if os.path.exists(KEPT + f"{tex}.png") else CACHE) + f"{tex}.png", check_existing=True)
    img.interpolation = 'Linear'; img.extension = 'CLIP'
    tc = nn.new("ShaderNodeTexCoord"); mp = nn.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1 / n, 1 / n, 1)
    nt.links.new(tc.outputs["UV"], mp.inputs["Vector"]); nt.links.new(mp.outputs[0], img.inputs[0])
    em = nn.new("ShaderNodeEmission"); em.inputs["Strength"].default_value = emit
    mul = nn.new("ShaderNodeMixRGB"); mul.blend_type = 'MULTIPLY'; mul.inputs[0].default_value = 1
    mul.inputs[2].default_value = tuple(c / 255 for c in tint) + (1,)
    nt.links.new(img.outputs["Color"], mul.inputs[1]); nt.links.new(mul.outputs[0], em.inputs["Color"])
    tr = nn.new("ShaderNodeBsdfTransparent"); mix = nn.new("ShaderNodeMixShader")
    nt.links.new(img.outputs["Alpha"], mix.inputs["Fac"]); nt.links.new(tr.outputs[0], mix.inputs[1]); nt.links.new(em.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], nn["Material Output"].inputs["Surface"])
    m.blend_method = 'BLEND'; m.shadow_method = 'NONE'
    loc = mp.inputs["Location"]
    loc.default_value = (0, (n - 1) / n, 0); loc.keyframe_insert("default_value", frame=0)  # keyed from frame 0 (EEVEE skips node animation that starts later)
    for k in range(frames):  # step through the flipbook, left to right, top row first
        col, row = k % n, k // n
        loc.default_value = (col / n, (n - 1 - row) / n, 0); loc.keyframe_insert("default_value", frame=f0 + k * step)
    for fc in nt.animation_data.action.fcurves:
        for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'
    return m


def burst(kind, loc, f, size=2.0, face=None, tint=(255, 255, 255), emit=1.6, step=2, grid=None, frames=None, rise=0.0, spin=0.0):
    """Play one flipbook effect at loc starting at frame f (step = video frames per flipbook frame). face = a point
    the sprite turns toward (the shot's camera). rise moves it up over its life; spin turns it (degrees)."""
    import bmesh
    tex, n = PRESETS.get(kind, (kind, grid or 4))
    frames = frames or n * n
    me = bpy.data.meshes.new("vfx"); bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=0.5)
    bm.to_mesh(me); bm.free(); uv = me.uv_layers.new()
    for poly in me.polygons:
        for li in poly.loop_indices:
            co = me.vertices[me.loops[li].vertex_index].co; uv.data[li].uv = (co.x + 0.5, co.y + 0.5)
    me.materials.append(_mat(tex, n, f, frames, step, tint, emit))
    o = bpy.data.objects.new(f"vfx_{kind}", me); bpy.context.scene.collection.objects.link(o)
    o.location = loc
    if face is not None: o.rotation_euler = (Vector(face) - Vector(loc)).to_track_quat('Z', 'Y').to_euler()
    end = f + frames * step
    o.scale = (size, size, size)
    for fr, on in ((0, False), (f, True), (end + 1, False)):
        o.hide_render = not on; o.keyframe_insert("hide_render", frame=fr)
        o.hide_viewport = not on; o.keyframe_insert("hide_viewport", frame=fr)
    if rise or spin:
        o.keyframe_insert("location", frame=f); o.location = Vector(loc) + Vector((0, 0, rise)); o.keyframe_insert("location", frame=end)
        if spin:
            r0 = o.rotation_euler.copy(); o.keyframe_insert("rotation_euler", frame=f)
            o.rotation_euler = (r0.x, r0.y, r0.z + math.radians(spin)); o.keyframe_insert("rotation_euler", frame=end)
    for fc in o.animation_data.action.fcurves:
        if fc.data_path in ("hide_render", "hide_viewport"):
            for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'
    return o
