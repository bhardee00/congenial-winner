"""Blender toolkit for building a Short: each location is its own scene (animated in absolute frames of the final
video), and the master scene "SHORT" cuts between them on the video timeline with the narration, captions and
overlays. Story modules (stories/*.py) use these helpers to build sets and act out each shot."""
import math, os
import bpy
from mathutils import Vector
import models
from anim import key, value

FPS = 30
W, H = 1080, 1440  # 3:4 portrait


def lin(c):
    return tuple(((x / 255 + 0.055) / 1.055) ** 2.4 if x / 255 > 0.04045 else x / 255 / 12.92 for x in c[:3]) + (1,)


# ---------------- sets ----------------
class Set:
    """One location: its own scene, built inside `with s:`, so helpers and bpy.ops add objects here."""
    def __init__(self, name, sky=(70, 160, 255), horizon=(200, 230, 255), sun=(50, 0, -30), sun_energy=4.5, sun_color=(255, 245, 230)):
        self.name = name
        self.scene = sc = bpy.data.scenes.new(name)
        sc.render.engine = 'BLENDER_EEVEE'; sc.render.resolution_x, sc.render.resolution_y = W, H; sc.render.fps = FPS
        ee = sc.eevee; ee.taa_render_samples = 32; ee.use_gtao = True; ee.gtao_distance = 1.2
        ee.use_bloom = True; ee.bloom_intensity = 0.05; ee.bloom_threshold = 0.9
        ee.use_soft_shadows = True; ee.shadow_cascade_size = '2048'; ee.shadow_cube_size = '1024'
        sc.view_settings.view_transform = 'Standard'
        try: sc.view_settings.look = 'Medium High Contrast'
        except Exception: pass
        w = bpy.data.worlds.new(name); sc.world = w; w.use_nodes = True
        nt = w.node_tree; bg = nt.nodes["Background"]
        grad = nt.nodes.new("ShaderNodeTexGradient"); mp = nt.nodes.new("ShaderNodeMapping"); tc = nt.nodes.new("ShaderNodeTexCoord")
        ramp = nt.nodes.new("ShaderNodeValToRGB"); sep = nt.nodes.new("ShaderNodeSeparateXYZ")
        nt.links.new(tc.outputs["Generated"], sep.inputs[0]); nt.links.new(sep.outputs["Z"], ramp.inputs["Fac"])
        ramp.color_ramp.elements[0].position = 0.0; ramp.color_ramp.elements[0].color = lin(horizon)
        ramp.color_ramp.elements[1].position = 0.32; ramp.color_ramp.elements[1].color = lin(sky)
        nt.links.new(ramp.outputs["Color"], bg.inputs["Color"]); bg.inputs["Strength"].default_value = 1.25
        sc.view_settings.exposure = 0.15
        self.sun = bpy.data.objects.new(name + "_sun", bpy.data.lights.new(name + "_sun", "SUN")); sc.collection.objects.link(self.sun)
        self.sun.data.energy = sun_energy; self.sun.data.color = lin(sun_color)[:3]; self.sun.data.angle = math.radians(3)
        self.sun.rotation_euler = [math.radians(a) for a in sun]
        self.cams = {}; self._ovr = None

    def __enter__(self):
        self._ovr = bpy.context.temp_override(scene=self.scene, view_layer=self.scene.view_layers[0]); self._ovr.__enter__(); return self

    def __exit__(self, *a): self._ovr.__exit__(*a)

    def link(self, o): self.scene.collection.objects.link(o); return o


_MATS = {}


def mat(c, rough=0.6, metal=0.0, emit=0.0, alpha=1.0, name=None):
    k = (tuple(c), rough, metal, emit, alpha)
    if k in _MATS: return _MATS[k]
    m = bpy.data.materials.new(name or "m"); m.use_nodes = True; pb = m.node_tree.nodes["Principled BSDF"]
    pb.inputs["Base Color"].default_value = lin(c); pb.inputs["Roughness"].default_value = rough; pb.inputs["Metallic"].default_value = metal
    if emit: pb.inputs["Emission Color"].default_value = lin(c); pb.inputs["Emission Strength"].default_value = emit
    if alpha < 1: pb.inputs["Alpha"].default_value = alpha; m.blend_method = 'BLEND'; m.shadow_method = 'NONE'
    _MATS[k] = m
    return m


def image_mat(path, emit=0.0):
    m = bpy.data.materials.new(os.path.basename(path)); m.use_nodes = True; nn = m.node_tree.nodes; pb = nn["Principled BSDF"]
    img = nn.new("ShaderNodeTexImage"); img.image = bpy.data.images.load(path, check_existing=True)
    m.node_tree.links.new(img.outputs["Color"], pb.inputs["Base Color"]); m.node_tree.links.new(img.outputs["Alpha"], pb.inputs["Alpha"])
    if emit: m.node_tree.links.new(img.outputs["Color"], pb.inputs["Emission Color"]); pb.inputs["Emission Strength"].default_value = emit
    pb.inputs["Roughness"].default_value = 0.5; m.blend_method = 'CLIP'; m.shadow_method = 'CLIP'
    return m


def prim(kind, size, loc, m, rot=(0, 0, 0), parent=None, name="p", bevel=0.0):
    """kind: box | ball | cylY (upright cylinder) | cyl (along X) | wedge, sized in studs (Blender axes)."""
    unit = {"cylY": "cylZ"}.get(kind, kind)
    me = _blender_unit(unit)
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o)
    o.location = loc; o.rotation_euler = [math.radians(a) for a in rot]; o.scale = size
    if not me.materials: me.materials.append(None)
    o.material_slots[0].link = 'OBJECT'; o.material_slots[0].material = m
    if bevel:
        b = o.modifiers.new("b", "BEVEL"); b.width = bevel; b.segments = 3; b.limit_method = 'NONE'
    if parent: o.parent = parent
    return o


_UNITS = {}


def _blender_unit(kind):
    """Unit primitives in Blender axes (cylZ upright); reuses the Roblox-space ones from models where they match."""
    if kind in _UNITS: return _UNITS[kind]
    import bmesh
    from mathutils import Matrix
    if kind in ("box", "ball"): me = models._unit(kind)
    else:
        bm = bmesh.new()
        if kind == "cylZ": bmesh.ops.create_cone(bm, cap_ends=True, segments=28, radius1=0.5, radius2=0.5, depth=1)
        elif kind == "cyl": bmesh.ops.create_cone(bm, cap_ends=True, segments=28, radius1=0.5, radius2=0.5, depth=1, matrix=Matrix.Rotation(math.radians(90), 4, "Y"))
        elif kind == "cone": bmesh.ops.create_cone(bm, cap_ends=True, segments=28, radius1=0.5, radius2=0.0, depth=1)
        me = bpy.data.meshes.new("u_" + kind); bm.to_mesh(me); bm.free()
        for p in me.polygons: p.use_smooth = True
        me.use_auto_smooth = True; me.auto_smooth_angle = math.radians(40)
    _UNITS[kind] = me
    return me


def ground(size, c, rough=0.9, z=0.0, loc=(0, 0)):
    return prim("box", (size, size, 0.2), (loc[0], loc[1], z - 0.1), mat(c, rough), name="ground")


def plane_image(path, size, loc, rot=(90, 0, 0), parent=None, emit=0.0, name="img"):
    """Upright picture/sign facing -Y by default (rot=(90,0,0))."""
    import bmesh
    me = bpy.data.meshes.new(name); bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=0.5)
    bm.to_mesh(me); bm.free()
    uv = me.uv_layers.new()
    for poly in me.polygons:
        for li in poly.loop_indices:
            co = me.vertices[me.loops[li].vertex_index].co; uv.data[li].uv = (co.x + 0.5, co.y + 0.5)
    me.materials.append(image_mat(path, emit))
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o)
    o.location = loc; o.rotation_euler = [math.radians(a) for a in rot]; o.scale = (size[0], size[1], 1)
    if parent: o.parent = parent
    return o


def place(D, asset_id, loc, rot_z=0, scale=1.0, name=None):
    return models.place(D, asset_id, loc, rot_z, scale, name, bpy.context.scene.collection)


def empty(name, loc=(0, 0, 0), parent=None):
    o = bpy.data.objects.new(name, None); bpy.context.scene.collection.objects.link(o)
    o.location = loc; o.empty_display_size = 0.3
    if parent: o.parent = parent
    return o


def vis(o, f, on):
    """Show/hide an object (and its children) from frame f."""
    for x in [o] + list(o.children_recursive):
        x.hide_render = not on; x.keyframe_insert("hide_render", frame=f)
        x.hide_viewport = not on; x.keyframe_insert("hide_viewport", frame=f)


def show_between(o, f0, f1=None):
    vis(o, 0, False); vis(o, f0, True)
    if f1 is not None: vis(o, f1, False)


# ---------------- cameras ----------------
def camera(st, name, loc, target, lens=35, f0=None, f1=None, loc2=None, target2=None, fstop=None):
    """A camera aimed at a target empty; optional move from (loc, target) at f0 to (loc2, target2) at f1."""
    cd = bpy.data.cameras.new(name); cd.lens = lens; cd.sensor_width = 36
    if fstop: cd.dof.use_dof = True; cd.dof.aperture_fstop = fstop
    c = bpy.data.objects.new(name, cd); st.link(c)
    t = bpy.data.objects.new(name + "_t", None); st.link(t)
    con = c.constraints.new("TRACK_TO"); con.target = t; con.track_axis = 'TRACK_NEGATIVE_Z'; con.up_axis = 'UP_Y'
    if fstop: cd.dof.focus_object = t
    c.location = loc; t.location = target
    if f0 is not None and loc2 is not None:
        for o, a, b in ((c, loc, loc2), (t, target, target2 or target)):
            o.location = a; o.keyframe_insert("location", frame=f0); o.location = b; o.keyframe_insert("location", frame=f1)
            for fc in o.animation_data.action.fcurves:
                for kp in fc.keyframe_points: kp.interpolation = 'BEZIER'; kp.easing = 'EASE_IN_OUT'
    st.cams[name] = c
    return c


def follow(st, name, subject, offset, look_offset=(0, 0, 0), lens=35, fstop=None):
    """Camera that keeps a fixed offset from a moving subject (child of a copy-location helper)."""
    h = bpy.data.objects.new(name + "_h", None); st.link(h)
    con = h.constraints.new("COPY_LOCATION"); con.target = subject
    c = camera(st, name, offset, look_offset, lens, fstop=fstop)
    c.parent = h; c.constraints["Track To"].target.parent = h
    return c


# ---------------- acting (R15 avatars from avatar.py) ----------------
def _key(o, path, f, v, ease=None):
    key(o, path, f, v, ease)


def pose(av, f, ease=10, **joints):
    """pose(av, 30, ra=(-80, 0, 40), head=(10, 0, 0)) - degrees per pivot, reached at frame f over `ease` frames."""
    for k, r in joints.items(): _key(av[k], "rotation_euler", f, [math.radians(a) for a in r], ease)


def rest(av, f, *joints, ease=10):
    for k in joints or ("waist", "head", "la", "la_elbow", "ra", "ra_elbow", "ll", "ll_knee", "rl", "rl_knee"):
        _key(av[k], "rotation_euler", f, (0, 0, 0), ease)


def yaw_to(loc, face):
    return face if isinstance(face, (int, float)) else math.degrees(math.atan2(face[1] - loc[1], face[0] - loc[0])) + 90


def at(av, f, loc, face=None, ease=1):
    """Put the character at loc (facing a point, or a yaw in degrees) from frame f; ease=1 is a cut/teleport."""
    r = av["root"]; _key(r, "location", f, loc, ease)
    if face is not None: _key(r, "rotation_euler", f, (0, 0, math.radians(yaw_to(loc, face))), ease)


def turn(av, f, face, ease=12):
    loc = value(av["root"], "location", f)
    _key(av["root"], "rotation_euler", f, (0, 0, math.radians(yaw_to(loc, face))), ease)


def walk(av, f0, f1, a, b, step=10, swing=26):
    """Walk from a to b: root moves linearly, faces the way it walks, arms and legs swing."""
    at(av, f0, a, b, ease=4); at(av, f1, b, b, ease=None)
    for fc in av["root"].animation_data.action.fcurves:
        if fc.data_path == "location":
            for kp in fc.keyframe_points:
                if f0 <= kp.co.x <= f1: kp.interpolation = 'LINEAR'
    for i, f in enumerate(range(f0, f1 + 1, step)):
        s = swing * (1 if i % 2 else -1)
        pose(av, f, ease=(6 if i == 0 else None), ll=(s, 0, 0), rl=(-s, 0, 0), la=(-s * 0.8, 0, 0), ra=(s * 0.8, 0, 0), ll_knee=(max(0, -s) * 0.8, 0, 0), rl_knee=(max(0, s) * 0.8, 0, 0))
    rest(av, f1 + step // 2, "ll", "rl", "la", "ra", "ll_knee", "rl_knee", ease=None)


def sit(av, f, seat_z, loc_xy, face, lean=0, ease=10):
    """Sit on something whose top is at seat_z (hips drop so thighs rest on it), settling over `ease` frames."""
    hip = av["joints"]["ll"][2] * av["scale"]
    at(av, f, (loc_xy[0], loc_xy[1], seat_z - hip + 0.45 * av["scale"]), face, ease)
    pose(av, f, ease, ll=(-88, 0, 4), rl=(-88, 0, -4), ll_knee=(88, 0, 0), rl_knee=(88, 0, 0), waist=(lean, 0, 0))


def press(av, f, hand="ra"):
    """Raise the remote and press it at f (arm up over ~10 frames, button click at f)."""
    pose(av, f - 2, ease=14, **{hand: (-78, 0, 20 if hand == "ra" else -20), hand + "_elbow": (-25, 0, 0)})
    pose(av, f + 1, ease=3, **{hand + "_elbow": (-12, 0, 0)}); pose(av, f + 4, ease=None, **{hand + "_elbow": (-25, 0, 0)})


def hold_out(av, f, hand="ra", up=-70, ease=12):
    pose(av, f, ease, **{hand: (up, 0, 10 if hand == "ra" else -10), hand + "_elbow": (-20, 0, 0)})


def nod(av, f, n=2, amt=14, axis=0):
    """Nod (axis 0) or shake the head (axis 2)."""
    for i in range(n * 2 + 1):
        r = [0, 0, 0]; r[axis] = amt if i % 2 else (-amt if i else 0)
        pose(av, f + i * 5, ease=(4 if i == 0 else None), head=tuple(r))
    pose(av, f + (n * 2 + 1) * 5, ease=None, head=(0, 0, 0))


def idle(rig, joints=("waist", "head"), amount=0.035, speed=40):
    """Gentle continuous motion (breathing, small head moves) layered on top of the keyed animation, so nobody
    stands frozen between actions."""
    import random
    for j in joints:
        o = rig[j]
        if not (o.animation_data and o.animation_data.action and o.animation_data.action.fcurves.find("rotation_euler", index=0)):
            o.keyframe_insert("rotation_euler", frame=0)
        for i in (0, 2):
            fc = o.animation_data.action.fcurves.find("rotation_euler", index=i)
            if fc is None: o.keyframe_insert("rotation_euler", index=i, frame=0); fc = o.animation_data.action.fcurves.find("rotation_euler", index=i)
            m = fc.modifiers.new('NOISE'); m.strength = amount * (1.6 if j == "head" else 1.0); m.scale = speed
            m.phase = random.uniform(0, 100); m.blend_in = 0


def smooth(objs):
    for o in objs:
        if o.animation_data and o.animation_data.action:
            for fc in o.animation_data.action.fcurves:
                if fc.data_path in ("hide_render", "hide_viewport"):
                    for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'


# ---------------- props in hands ----------------
def carry(prop, holders, keys):
    """Move a prop between holders over time without parenting tricks: one copy per holder, visibility swapped.
    holders: {"bench": parent_obj_or_None, "hand": grip_empty, ...}; keys: [(frame, holder_name), ...]."""
    copies = {}  # a holder name in keys that is not in holders (e.g. "gone") hides every copy
    for name, parent in holders.items():
        c = prop(parent); copies[name] = c
    for name, c in copies.items():
        vis(c, 0, keys[0][1] == name)
        for f, h in keys: vis(c, f, h == name)
    return copies


# ---------------- assembling the video ----------------
class Short:
    def __init__(self, title, timed, end_pad=2.5):
        self.title = title; self.timed = timed
        self.master = bpy.data.scenes.new("SHORT") if "SHORT" not in bpy.data.scenes else bpy.data.scenes["SHORT"]
        m = self.master; m.render.resolution_x, m.render.resolution_y = W, H; m.render.fps = FPS
        m.view_settings.view_transform = 'Standard'
        self.se = m.sequence_editor_create()
        self.total = self.frame(timed[-1]["end"] + end_pad)
        m.frame_start = 1; m.frame_end = self.total
        self.shots = []

    def frame(self, t): return int(round(t * FPS)) + 1

    def line_frames(self, i):
        """(start, end) frames of line i on the final timeline; a shot for line i runs until the next line starts."""
        a = 1 if i == 0 else self.frame(self.timed[i]["start"] - 0.15)
        b = self.frame(self.timed[i + 1]["start"] - 0.15) if i + 1 < len(self.timed) else self.total + 1
        return a, b

    def shot(self, st, cam, f0, f1, frozen=False, drift=0.08):
        """Cut to `cam` from f0 to f1. A camera that doesn't already move slowly pushes in (drift = share of the
        distance to its target), which keeps every shot alive."""
        c = st.cams[cam] if isinstance(cam, str) else cam
        if drift and not (c.animation_data and c.animation_data.action):
            t = c.constraints["Track To"].target; a = c.location.copy(); b = a + (t.location - a) * drift
            for f, v in ((f0, a), (f1, b)):
                c.location = v; c.keyframe_insert("location", frame=f)
            for fc in c.animation_data.action.fcurves:
                for kp in fc.keyframe_points: kp.interpolation = 'SINE'; kp.easing = 'EASE_IN_OUT'
            c.location = a
        self.shots.append((st, cam, f0, f1, frozen))

    def assemble(self, voice, words, overlays=()):
        se = self.se
        for i, (st, cam, f0, f1, frozen) in enumerate(sorted(self.shots, key=lambda s: s[2])):
            st.scene.frame_start = 1; st.scene.frame_end = self.total
            # added on a free channel at full length (scene frame = video frame), trimmed, then moved down to 1
            s = se.sequences.new_scene(f"{st.name}_{f0}", st.scene, 100 + i, 1)
            s.frame_final_start = f0; s.frame_final_end = f1; s.channel = 1
            s.scene_camera = st.cams[cam] if isinstance(cam, str) else cam
            s.color_saturation = 1.25  # bright and colourful
            if frozen:  # the paused world: just a hint of cool, colour stays full
                cb = s.modifiers.new("cool", 'COLOR_BALANCE'); cb.color_balance.gain = (0.98, 1.0, 1.04)
        se.sequences.new_sound("voice", voice, 30, 1)
        items = [(p, f0, f1, ch, *(pos or (0, 0, 1))) for p, f0, f1, ch, *pos in overlays]
        items += [(p, f0, f1, 9, 0, 0, 1) for p, f0, f1 in words]
        ov = self._overlay_scene(items)
        o = se.sequences.new_scene("overlay", ov, 100, 1)
        o.frame_final_start = 1; o.frame_final_end = self.total + 1; o.channel = 5; o.blend_type = 'ALPHA_OVER'

    def _overlay_scene(self, items):
        """Captions, cards and icons as flat pictures in a transparent scene laid over the shots. (Image strips in
        the video editor can't be packed into the .blend, so they'd be missing on another computer; these can.)
        items: (png, first frame, end frame, layer, x px, y px from centre, scale)."""
        import bmesh
        sc = bpy.data.scenes.new("OVERLAY"); sc.render.engine = 'BLENDER_EEVEE'
        sc.render.resolution_x, sc.render.resolution_y = W, H; sc.render.fps = FPS; sc.render.film_transparent = True
        sc.eevee.taa_render_samples = 8; sc.view_settings.view_transform = 'Standard'
        sc.frame_start = 1; sc.frame_end = self.total
        cd = bpy.data.cameras.new("overlay_cam"); cd.type = 'ORTHO'; cd.ortho_scale = H / 100  # 1 unit = 100 px
        cam = bpy.data.objects.new("overlay_cam", cd); sc.collection.objects.link(cam); cam.location = (0, 0, 10); sc.camera = cam
        me = bpy.data.meshes.new("overlay_plane"); bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=0.5)
        bm.to_mesh(me); bm.free(); uv = me.uv_layers.new()
        for poly in me.polygons:
            for li in poly.loop_indices:
                co = me.vertices[me.loops[li].vertex_index].co; uv.data[li].uv = (co.x + 0.5, co.y + 0.5)
        me.materials.append(None)
        mats = {}
        for path, f0, f1, layer, x, y, s in items:
            if path not in mats:  # unlit: the picture's own colours, see-through where it is transparent
                m = bpy.data.materials.new(os.path.basename(path)); m.use_nodes = True; nt = m.node_tree; nn = nt.nodes
                nn.remove(nn["Principled BSDF"]); img = nn.new("ShaderNodeTexImage")
                img.image = bpy.data.images.load(path, check_existing=True)
                em = nn.new("ShaderNodeEmission"); tr = nn.new("ShaderNodeBsdfTransparent"); mix = nn.new("ShaderNodeMixShader")
                nt.links.new(img.outputs["Color"], em.inputs["Color"]); nt.links.new(img.outputs["Alpha"], mix.inputs["Fac"])
                nt.links.new(tr.outputs[0], mix.inputs[1]); nt.links.new(em.outputs[0], mix.inputs[2])
                nt.links.new(mix.outputs[0], nn["Material Output"].inputs["Surface"])
                m.blend_method = 'BLEND'; m.shadow_method = 'NONE'; mats[path] = m
            m = mats[path]; iw, ih = m.node_tree.nodes["Image Texture"].image.size
            o = bpy.data.objects.new(os.path.basename(path), me); sc.collection.objects.link(o)
            o.material_slots[0].link = 'OBJECT'; o.material_slots[0].material = m
            o.location = (x / 100, y / 100, layer * 0.01); o.scale = (iw * s / 100, ih * s / 100, 1)
            for f, on in ((0, False), (f0, True), (f1, False)):
                o.hide_render = not on; o.keyframe_insert("hide_render", frame=f)
            for fc in o.animation_data.action.fcurves:
                for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'
        return sc

    def flash(self, f, length=7, channel=8):
        c = self.se.sequences.new_effect(f"flash{f}", 'COLOR', channel, frame_start=f, frame_end=f + length)
        c.color = (1, 1, 1); c.blend_type = 'ALPHA_OVER'
        c.blend_alpha = 0.85; c.keyframe_insert("blend_alpha", frame=f); c.blend_alpha = 0.0; c.keyframe_insert("blend_alpha", frame=f + length)

    def output(self, path):
        r = self.master.render
        r.image_settings.file_format = 'FFMPEG'; r.ffmpeg.format = 'MPEG4'; r.ffmpeg.codec = 'H264'
        r.ffmpeg.constant_rate_factor = 'HIGH'; r.ffmpeg.ffmpeg_preset = 'GOOD'; r.ffmpeg.audio_codec = 'AAC'
        r.ffmpeg.audio_bitrate = 192; r.ffmpeg.audio_channels = 'STEREO'; r.ffmpeg.audio_mixrate = 48000
        r.filepath = path; r.use_file_extension = False; r.use_sequencer = True
