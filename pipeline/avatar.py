"""Blender side of the avatar: builds the posable R15 character from work/avatar/rig.json (made by prep_avatar.py).
build(D) returns {"root", pivot name -> empty ("torso", "waist", "head", "la", "la_elbow", ..., "rl_ankle"),
"faces": {"smile", "shock"}, "grips": {"la", "ra"} -> empties in the hands to parent props to}.
Rotating a pivot bends that joint; pivots have no rotation at rest so (-80, 0, 50) on "ra" raises the right arm."""
import json, math, os, glob
import bpy, bmesh
from anim import key, value
from mathutils import Vector

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets") + "/"
ALL = []  # every character built, so finish() can add blinks once all reactions are known


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


# emote popped beside the head with each expression (emote=False in react() to skip, or pass another)
EMOTES = {"angry": "anger", "furious": "steam", "nervous": "sweat", "worried": "sweat", "embarrassed": "sweat",
          "shock": "exclaim", "big_eyes": "exclaim", "terrified": "exclaim", "scream": "exclaim",
          "suspicious": "question", "confused": "question", "love": "hearts", "sleepy": "zzz", "dizzy": "stars"}
GESTURES = True  # head moves with every expression (set False to rebuild an older short exactly as it was)
# head gesture per expression on the neck pivot: (frames after the change, (pitch, roll, yaw) degrees); pitch + looks
# down. A trailing "hold" keeps the last pose until the expression's end (f1) instead of settling back.
GESTURE = {
    "shock": [(3, (-14, 0, 0)), (9, (-6, 0, 0)), (18, (0, 0, 0))],
    "big_eyes": [(3, (-16, 0, 0)), (10, (-8, 0, 0)), (20, (0, 0, 0))],
    "terrified": [(3, (-12, 0, 0)), (6, (-10, 0, 5)), (9, (-12, 0, -5)), (12, (-10, 0, 5)), (15, (-12, 0, -5)), (18, (-10, 0, 3)), (21, (-12, 0, -3)), "hold"],
    "scream": [(3, (-20, 0, 0)), (6, (-18, 0, 4)), (9, (-20, 0, -4)), (12, (-18, 0, 0)), "hold"],
    "happy": [(4, (9, 0, 0)), (8, (-2, 0, 0)), (12, (7, 0, 0)), (18, (0, 0, 0))],
    "laugh": [(4, (-14, 0, 0)), (8, (-5, 0, 0)), (12, (-14, 0, 0)), (16, (-5, 0, 0)), (20, (-13, 0, 0)), (24, (-5, 0, 0)), (30, (0, 0, 0))],
    "smile": [(5, (6, 0, 0)), (12, (0, 4, 0)), "hold"],
    "grin": [(6, (-6, 9, 0)), "hold"],
    "smug": [(8, (-9, 11, 7)), "hold"],
    "sad": [(12, (17, 0, 0)), "hold"],
    "cry": [(8, (15, 0, 0)), (13, (15, 0, 7)), (18, (15, 0, -7)), (23, (15, 0, 7)), (28, (15, 0, -7)), (34, (15, 0, 0)), "hold"],
    "worried": [(8, (9, -7, -8)), "hold"],
    "angry": [(4, (9, 0, 0)), (7, (9, 0, 9)), (10, (9, 0, -9)), (13, (9, 0, 9)), (16, (9, 0, -9)), (21, (7, 0, 0)), "hold"],
    "furious": [(3, (12, 0, 0)), (5, (12, 0, 11)), (7, (12, 0, -11)), (9, (12, 0, 11)), (11, (12, 0, -11)), (13, (12, 0, 11)), (15, (12, 0, -11)), (20, (10, 0, 0)), "hold"],
    "annoyed": [(8, (4, 0, 14)), (16, (-7, 0, 10)), "hold"],
    "suspicious": [(8, (5, 13, -9)), "hold"],
    "confused": [(6, (0, 17, 0)), (14, (0, -13, 0)), "hold"],
    "nervous": [(4, (5, 0, 7)), (8, (5, 0, -7)), (12, (5, 0, 7)), (16, (5, 0, -7)), (21, (5, 0, 0)), "hold"],
    "embarrassed": [(10, (13, 0, -15)), "hold"],
    "determined": [(4, (11, 0, 0)), (9, (3, 0, 0)), "hold"],
    "relieved": [(8, (-11, 0, 0)), (18, (6, 0, 0)), (26, (0, 0, 0))],
    "love": [(8, (0, 13, 0)), (18, (0, -13, 0)), (28, (0, 11, 0)), "hold"],
    "starstruck": [(4, (-11, 0, 0)), (10, (-6, 9, 0)), "hold"],
    "blank": [(12, (0, -4, 0)), "hold"],
    "sleepy": [(20, (19, 0, 0)), "hold"],
    "dizzy": [(6, (6, 9, 0)), (12, (-6, 0, 0)), (18, (6, -9, 0)), (24, (-6, 0, 0)), (30, (0, 0, 0))],
    "disgusted": [(6, (-9, 0, -17)), "hold"],
}


def _clear_after(o, path, f, until=None):
    """Drop o's keys on path after frame f (up to `until`), so a new gesture replaces what was there before."""
    act = o.animation_data.action if o.animation_data else None
    if not act: return
    for fc in act.fcurves:
        if fc.data_path == path:
            for kp in [k for k in fc.keyframe_points if k.co[0] > f and (until is None or k.co[0] <= until)][::-1]: fc.keyframe_points.remove(kp)


def gesture(av, face, f0, f1):
    """Move the head with the expression (neck pivot, so it adds to the story's own head poses)."""
    n = av.get("neck"); seq = GESTURE.get(face)
    if n is None or not seq or not GESTURES: return
    _clear_after(n, "rotation_euler", f0)
    key(n, "rotation_euler", f0, tuple(value(n, "rotation_euler", f0)))
    last = (0, 0, 0)
    for st in seq:
        if st == "hold":
            key(n, "rotation_euler", max(f1, f0 + st_f + 4) - 4, tuple(math.radians(v) for v in last))
            key(n, "rotation_euler", max(f1, f0 + st_f + 4) + 6, (0, 0, 0)); return
        st_f, last = st
        key(n, "rotation_euler", f0 + st_f, tuple(math.radians(v) for v in last))


def talk(av, frames, amount=1.0):
    """Subtle head motion while someone speaks (nod pivot): a small, soft nod on a few stressed words (at most one
    every ~0.4 s) and a slow, gentle turn that changes once per phrase. Kept small on purpose - the user found
    a nod on every word too much."""
    n = av.get("nod")
    if n is None or not frames or not GESTURES: return
    import random
    rnd = random.Random(sum(map(ord, av.get("name", ""))) + frames[0])
    f0, f1 = frames[0], frames[-1] + 14
    _clear_after(n, "rotation_euler", f0 - 6, f1)  # only this speech's own stretch
    key(n, "rotation_euler", f0 - 6, (0, 0, 0))
    picked, last = [], -99
    for f in frames:
        if f - last >= 12 and rnd.random() < 0.6: picked.append(f); last = f
    yaw = math.radians(rnd.choice((-1, 1)) * rnd.uniform(1.5, 3) * amount)
    for k, f in enumerate(picked):
        if k % 3 == 0: yaw = -yaw  # new gentle direction every few nods
        down = math.radians(rnd.uniform(1.8, 3.2) * amount)
        key(n, "rotation_euler", f + 2, (down, 0, yaw))
        key(n, "rotation_euler", f + 8, (down * 0.25, 0, yaw))
    key(n, "rotation_euler", f1, (0, 0, 0))


AUTO_EMOTES = False  # the reference style has no floating icons; pass emote_kind="..." to pop one on purpose
POP = ("shock", "big_eyes", "terrified", "scream", "starstruck")


def _free(o, path, f0, f1):
    """True if o has no keys on path between f0 and f1 (so an extra head move won't fight the story's own poses)."""
    act = o.animation_data.action if o.animation_data else None
    if not act: return True
    return not any(f0 <= kp.co[0] <= f1 for fc in act.fcurves if fc.data_path == path for kp in fc.keyframe_points)


def emote(av, kind, f0, f1=None):
    """Cartoon pop beside the head (assets/emote_<kind>.png): springs in, bobs, shrinks away at f1."""
    f1 = f1 if f1 is not None else f0 + 36
    m = bpy.data.materials.get("emote_" + kind)
    if m is None:
        m = bpy.data.materials.new("emote_" + kind); m.use_nodes = True; m.blend_method = 'CLIP'; m.shadow_method = 'NONE'
        t = m.node_tree.nodes; img = t.new("ShaderNodeTexImage"); img.image = bpy.data.images.load(ASSETS + f"emote_{kind}.png", check_existing=True)
        pb = t["Principled BSDF"]; pb.inputs["Roughness"].default_value = 0.6
        m.node_tree.links.new(img.outputs["Color"], pb.inputs["Base Color"]); m.node_tree.links.new(img.outputs["Alpha"], pb.inputs["Alpha"])
        m.node_tree.links.new(img.outputs["Color"], pb.inputs["Emission Color"] if "Emission Color" in pb.inputs else pb.inputs["Emission"])
        (pb.inputs.get("Emission Strength") or pb.inputs[0]).default_value = 0.35
    fp = av["faces"]["smile"]
    me = bpy.data.meshes.get("faceplane")
    o = bpy.data.objects.new(f"{av.get('name', 'av')}_emote_{kind}", me)
    av["head"].users_collection[0].objects.link(o)
    o.material_slots[0].link = 'OBJECT'; o.material_slots[0].material = m
    o.parent = av["head"]; o.rotation_euler = fp.rotation_euler
    side = 1 if len([e for e in av.setdefault("emotes", []) if e > f0 - 40]) % 2 == 0 else -1
    av["emotes"].append(f0)
    base = fp.location + Vector((1.1 * side, -0.15, 0.85)) if kind not in ("zzz", "steam", "bulb") else fp.location + Vector((0.55 * side, 0.1, 1.05))
    s = 1.15
    for f, sc, dz in ((f0 - 1, 0.001, 0), (f0 + 3, s * 1.3, 0.08), (f0 + 7, s, 0), (f1 - 5, s, 0.06 if kind != "zzz" else 0.35), (f1, 0.001, 0.1)):
        o.scale = (sc, sc, sc); o.keyframe_insert("scale", frame=f)
        o.location = base + Vector((0, 0, dz)); o.keyframe_insert("location", frame=f)
    if kind in ("anger", "hearts"):  # throb
        for f in range(f0 + 10, f1 - 6, 8):
            for ff, sc in ((f, s * 1.12), (f + 4, s)): o.scale = (sc, sc, sc); o.keyframe_insert("scale", frame=ff)
    for f, vis in ((0, False), (f0 - 1, True), (f1 + 1, False)): _vis(o, vis, f)
    o.hide_render = o.hide_viewport = True
    return o


def react(av, face, f0, f1=None, emote_kind=None):
    """Switch to an expression at frame f0 (held until the next react). Effects run up to f1:
    shock / big_eyes / terrified / scream pop the head (squash and stretch), angry / furious flush red and shake,
    cry drips tears, laugh shakes the head, sad / cry / worried droop it, and most faces pop an emote (EMOTES).
    Faces: see faces.py (smile, shock, big_eyes, happy, grin, sad, cry, angry, annoyed, suspicious, nervous,
    embarrassed, determined, sleepy, laugh, terrified, scream, furious, love, starstruck, dizzy, smug, worried,
    relieved, disgusted, confused, blank). Blinking is added afterwards by finish()."""
    f1 = f1 if f1 is not None else f0 + 45
    if face not in av["faces"]: raise KeyError(f"no face '{face}' (faces: {', '.join(sorted(av['faces']))})")
    prev = av["reacts"][-1][1] if av["reacts"] else "smile"
    for k, fo in av["faces"].items():
        if not av["reacts"]: _vis(fo, k == "smile", 0)
        _vis(fo, k == prev, f0 - 1); _vis(fo, k == face, f0)
    av["reacts"].append((f0, face))
    fo = av["faces"][face]
    h = av["head"]
    if face in POP and _free(h, "scale", f0 - 2, f0 + 12):  # cartoon squash and stretch on the whole head
        for f, sc in ((f0 - 1, (1, 1, 1)), (f0 + 2, (0.9, 0.9, 1.22)), (f0 + 5, (1.1, 1.1, 0.92)), (f0 + 9, (1, 1, 1))):
            h.scale = sc; h.keyframe_insert("scale", frame=f)
    if not GESTURES and face in ("sad", "cry", "worried", "blank") and _free(h, "rotation_euler", f0 + 1, f1 + 6):
        base = value(h, "rotation_euler", f0)
        key(h, "rotation_euler", f0, base); key(h, "rotation_euler", f0 + 10, (base[0] + math.radians(-14), base[1], base[2]))
        key(h, "rotation_euler", f1 - 4, (base[0] + math.radians(-14), base[1], base[2])); key(h, "rotation_euler", f1 + 4, base)
    if not GESTURES and face in ("laugh", "happy") and _free(h, "rotation_euler", f0 + 1, f0 + 30):
        base = value(h, "rotation_euler", f0); n = 6 if face == "laugh" else 2
        key(h, "rotation_euler", f0, base)
        for i in range(n): key(h, "rotation_euler", f0 + 3 + i * 4, (base[0] + math.radians(12 if i % 2 == 0 else 4), base[1], base[2]))
        key(h, "rotation_euler", f0 + 5 + n * 4, base)
    gesture(av, face, f0, f1)
    em = emote_kind if emote_kind is not None else (EMOTES.get(face) if AUTO_EMOTES else None)
    if em: emote(av, em, f0, min(f1, f0 + 40))
    if face in ("shock", "big_eyes"):
        for f, sc in ((f0 - 1, 1.0), (f0 + 3, 1.28), (f0 + 8, 1.0)):
            fo.scale = (sc, sc, sc); fo.keyframe_insert("scale", frame=f)
        if not GESTURES:  # older shorts: a small jerk on the head pivot (gesture() covers this now)
            h = av["head"]; base = value(h, "rotation_euler", f0)
            for f, dx in ((f0, 0), (f0 + 3, -9), (f0 + 9, 0)):
                key(h, "rotation_euler", f, (base[0] + math.radians(dx), base[1], base[2]))
    if face in ("angry", "furious"):
        fac = av["skin"].node_tree.nodes["flush"].inputs["Fac"]
        r = 0.55 if face == "angry" else 0.8
        for f, v in ((f0, 0), (f0 + 10, r), (f1 - 8, r), (f1, 0)):
            fac.default_value = v; fac.keyframe_insert("default_value", frame=f)
        if not GESTURES:
            h = av["head"]; base = value(h, "rotation_euler", f0 + 6)
            for i, f in enumerate(range(f0 + 6, min(f1, f0 + 30), 2)):  # quick shake
                key(h, "rotation_euler", f, (base[0], base[1] + math.radians(4 if i % 2 else -4), base[2]))
            key(h, "rotation_euler", min(f1, f0 + 32), base)
    if face == "cry":
        _tears(av, f0, f1)


def blink(av, f0, f1, seed=0):
    """Blink every 2-4 s from f0 to f1 (3-frame blinks), skipping moments near an expression change."""
    import random
    rnd = random.Random(sum(map(ord, av.get("name", ""))) + seed)
    reacts = sorted(av["reacts"]); f = f0 + rnd.randint(20, 80)
    while f < f1 - 6:
        cur = "smile"
        for rf, k in reacts:
            if rf <= f: cur = k
        near = any(abs(rf - f) < 8 for rf, _ in reacts) or any(a - 3 <= f <= b + 3 for a, b in av.get("talk", []))
        b = av["faces"].get(cur + "_blink")
        if b and not near:
            fo = av["faces"][cur]
            for o, on0 in ((fo, cur == "smile"), (b, False)):
                if not (o.animation_data and o.animation_data.action): _vis(o, on0, 0)
            _vis(fo, False, f); _vis(b, True, f); _vis(b, False, f + 3); _vis(fo, True, f + 3)
            if rnd.random() < 0.15: _vis(fo, False, f + 6); _vis(b, True, f + 6); _vis(b, False, f + 8); _vis(fo, True, f + 8)  # double blink
        f += rnd.randint(65, 125)


def lipsync(av, words):
    """Mouth flaps while av talks: words = [(text, first frame, last frame)]. The face switches to its open-mouth
    version (face_<name>_talk) once per syllable; applied in finish(), when every expression change is known."""
    import re
    for w, f0, f1 in words:
        n = max(1, len(re.findall(r"[aeiouy]+", w.lower().rstrip("e")) or [1]))
        span = max(4, f1 - f0) / n
        for k in range(n):
            o = int(f0 + k * span); c = int(o + max(2, span * 0.6))
            if c - o >= 2: av.setdefault("talk", []).append((o, c))


def _mouths(av):
    reacts = sorted(av["reacts"]); last = -10
    for o, c in sorted(av.get("talk", [])):
        if o <= last + 1 or any(o - 2 <= rf <= c + 2 for rf, _ in reacts): continue
        cur = "smile"
        for rf, k in reacts:
            if rf <= o: cur = k
        t = av["faces"].get(cur + "_talk"); fo = av["faces"].get(cur)
        if not t or not fo: continue
        for x, on0 in ((fo, cur == "smile"), (t, False)):
            if not (x.animation_data and x.animation_data.action): _vis(x, on0, 0)
        _vis(fo, False, o); _vis(t, True, o); _vis(t, False, c); _vis(fo, True, c); last = c


def finish(total):
    """Call once after the story is built: every character blinks for the whole short, and mouths move on speech."""
    for av in ALL:
        blink(av, 0, total); _mouths(av)


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
