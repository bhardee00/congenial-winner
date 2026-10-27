"""Blender: the pigeon (free Creator Store model 8889620440 by ForestFossils, rigged here) and its animations.
pigeon(D) returns {"root", "body", "head", "wing_l", "wing_r", "leg_l", "leg_r", "eyes"}; root faces -Y at rest.
All animation helpers take frames and key the rig directly."""
import json, math
import bpy
from mathutils import Matrix, Vector
import models

PIGEON = 8889620440
PINK = (212, 144, 189)


def _group(it):
    x, y, z = it["rpos"]; sx, sy, sz = it["rsize"]
    # model +Z ends up on the pigeon's right once it faces -Y
    if sx < 0.15 and sy > 0.7: return "wing_r" if z > 34.9 else "wing_l"
    if tuple(it["color"]) == PINK or (abs(sx - 0.23) < 0.01 and abs(sy - 0.51) < 0.01): return "leg_r" if z > 34.9 else "leg_l"
    if x > -278.25 and y > 173.6: return "head"
    return "body"


def _empty(name, parent, loc=(0, 0, 0), coll=None):
    o = bpy.data.objects.new(name, None); (coll or bpy.context.scene.collection).objects.link(o)
    o.parent = parent; o.location = loc; o.empty_display_size = 0.2
    return o


def pigeon(D, name="pigeon", scale=0.6, coll=None):
    d = json.load(open(D + f"models/{PIGEON}.json"))
    root = _empty(name, None, coll=coll)
    turn = _empty(name + "_turn", root, coll=coll); turn.rotation_euler = (0, 0, math.radians(90)); turn.scale = (scale,) * 3
    groups = {}
    for it in d["items"]: groups.setdefault(_group(it), []).append(it)
    def centers(g): return [Vector(Matrix(it["M"]).translation) for it in groups[g]]
    piv = {"body": _empty(name + "_body", turn, coll=coll)}
    for g in ("head", "wing_l", "wing_r", "leg_l", "leg_r"):
        cs = centers(g); mid = sum(cs, Vector()) / len(cs)
        top = max(c.z for c in cs); bot = min(c.z for c in cs)
        piv[g] = _empty(f"{name}_{g}", piv["body"], (mid.x, mid.y, bot if g == "head" else top), coll)
    eyes = []
    for g, its in groups.items():
        for it in its:
            M = Matrix(it["M"]); me = models._unit(it["kind"]) if it["kind"] != "mesh" else None
            M = M @ Matrix.Diagonal(Vector(list(it["size"]) + [1]))
            if not me.materials: me.materials.append(None)
            o = bpy.data.objects.new(f"{name}_part", me); (coll or bpy.context.scene.collection).objects.link(o)
            o.parent = piv[g]; o.matrix_basis = Matrix.Translation(-piv[g].location) @ M if g != "body" else M
            o.material_slots[0].link = 'OBJECT'; o.material_slots[0].material = models._material(it)
            x, y, _ = it["rpos"]
            if g == "head" and abs(x + 278.0) < 0.05 and 174.65 < y < 174.78: eyes.append(o)
    return {"root": root, **piv, "eyes": eyes, "scale": scale, "turn": turn}


def _k(o, path, f, v=None):
    if v is not None: setattr(o, path, v)
    o.keyframe_insert(path, frame=f)


def walk(pg, f0, f1, a, b, step=5):
    """Walk from a to b (world xy, z) between frames, legs alternating and the pigeon head-bob."""
    r = pg["root"]; a, b = Vector(a), Vector(b)
    yaw = math.atan2(b.y - a.y, b.x - a.x) + math.pi / 2  # rest pose faces -Y
    _k(r, "location", f0, a); _k(r, "location", f1, b)
    _k(r, "rotation_euler", f0, (0, 0, yaw)); _k(r, "rotation_euler", f1, (0, 0, yaw))
    for fc in r.animation_data.action.fcurves:
        if fc.data_path == "location":
            for kp in fc.keyframe_points[-2:]: kp.interpolation = 'LINEAR'
    hb = pg["head"].location.copy()
    for i, f in enumerate(range(f0, f1 + 1, step)):
        s = 1 if i % 2 else -1
        _k(pg["leg_l"], "rotation_euler", f, (0, math.radians(25 * s), 0))
        _k(pg["leg_r"], "rotation_euler", f, (0, math.radians(-25 * s), 0))
        _k(pg["head"], "location", f, hb + Vector((-0.12 if i % 2 else 0.05, 0, 0)))
    for g in ("leg_l", "leg_r"): _k(pg[g], "rotation_euler", f1 + step, (0, 0, 0))
    _k(pg["head"], "location", f1 + step, hb)


def look(pg, f, yaw=0, pitch=0, hold=None):
    """Turn the head (degrees; yaw + looks to the pigeon's left, pitch + looks down)."""
    h = pg["head"]
    if hold is not None: _k(h, "rotation_euler", f - hold)
    _k(h, "rotation_euler", f, (0, math.radians(pitch), math.radians(yaw)))


def wing(pg, side, f0, f1, angle=110):
    w = pg["wing_" + side]; s = 1 if side == "r" else -1
    _k(w, "rotation_euler", f0, (0, 0, 0)); _k(w, "rotation_euler", f0 + 8, (math.radians(angle * s), 0, 0))
    _k(w, "rotation_euler", f1 - 6, (math.radians(angle * s), 0, 0)); _k(w, "rotation_euler", f1, (0, 0, 0))


def blink(pg, f, length=6):
    """A wink from the side the camera sees (the eye block goes through the head)."""
    for e in pg["eyes"]:
        s = e.scale.copy()
        _k(e, "scale", f - 1, s); _k(e, "scale", f + 2, (s.x, s.y, s.z * 0.12))
        _k(e, "scale", f + 2 + length, (s.x, s.y, s.z * 0.12)); _k(e, "scale", f + 5 + length, s)


def sigh(pg, f0, length=30):
    b = pg["body"]; h = pg["head"]
    _k(b, "location", f0, (0, 0, 0)); _k(b, "location", f0 + 8, (0, 0, 0.12))
    _k(b, "location", f0 + 20, (0, 0, -0.08)); _k(b, "location", f0 + length, (0, 0, 0))
    look(pg, f0 + 20, 0, 25); look(pg, f0 + length + 10, 0, 0)


def fly(pg, f0, f1, a, b, arc=3.0):
    """Flap from a to b (used for the final landing)."""
    r = pg["root"]; a, b = Vector(a), Vector(b)
    for i in range(0, 11):
        t = i / 10; p = a.lerp(b, t); p.z += math.sin(t * math.pi) * arc
        _k(r, "location", int(f0 + (f1 - f0) * t), p)
    for f in range(f0, f1, 4):
        up = ((f - f0) // 4) % 2 == 0
        for side, s in (("r", 1), ("l", -1)): _k(pg["wing_" + side], "rotation_euler", f, (math.radians((100 if up else 20) * s), 0, 0))
    for side in "lr": _k(pg["wing_" + side], "rotation_euler", f1 + 3, (0, 0, 0))
