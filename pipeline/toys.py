"""Blender: bright toy-town set pieces and props built from blocks (no downloads needed).
All functions add objects to the current scene (use inside a shortkit.Set) and return the root object."""
import math, random
import bpy
from mathutils import Vector
from shortkit import prim, mat, empty, plane_image, vis

R = random.Random(11)
HOUSE = [(240, 90, 80), (250, 200, 70), (90, 170, 230), (120, 200, 120), (245, 150, 60), (190, 120, 220), (250, 250, 245)]
ROOF = [(70, 90, 140), (180, 60, 50), (60, 120, 90), (90, 70, 60), (40, 60, 110)]


def house(x, y, rot=0, w=7, d=6, h=6, color=None, roof=None):
    r = empty("house", (x, y, 0)); r.rotation_euler = (0, 0, math.radians(rot))
    c = color or R.choice(HOUSE); rc = roof or R.choice(ROOF)
    prim("box", (w, d, h), (0, 0, h / 2), mat(c, 0.7), parent=r, bevel=0.15)
    for s in (-1, 1):  # gable roof from two tilted slabs
        prim("box", (w + 0.6, d * 0.62, 0.35), (0, s * d * 0.25, h + d * 0.2), mat(rc, 0.6), rot=(s * 38, 0, 0), parent=r, bevel=0.08)
    prim("box", (0.9, 0.9, 2.2), (w * 0.3, d * 0.1, h + 1.6), mat((150, 70, 60), 0.8), parent=r, bevel=0.05)  # chimney
    win = mat((255, 245, 200), 0.3, emit=0.6); frame = mat((255, 255, 255), 0.5)
    for wx in (-w * 0.28, w * 0.28):
        for wz in (h * 0.35, h * 0.72):
            prim("box", (1.3, 0.1, 1.2), (wx, -d / 2 - 0.05, wz), frame, parent=r)
            prim("box", (1.05, 0.12, 0.95), (wx, -d / 2 - 0.08, wz), win, parent=r)
    prim("box", (1.4, 0.12, 2.4), (0, -d / 2 - 0.06, 1.2), mat((120, 70, 45), 0.6), parent=r, bevel=0.04)
    return r


def tree(x, y, s=1.0, color=(90, 190, 90)):
    r = empty("tree", (x, y, 0))
    prim("cylY", (0.6 * s, 0.6 * s, 3 * s), (0, 0, 1.5 * s), mat((120, 80, 50), 0.8), parent=r)
    for dx, dy, dz, k in ((0, 0, 4.2, 1.0), (0.9, 0.3, 3.6, 0.75), (-0.8, -0.2, 3.7, 0.7), (0.1, 0.8, 4.8, 0.7)):
        prim("ball", (2.8 * k * s,) * 3, (dx * s, dy * s, dz * s), mat(color, 0.8), parent=r)
    return r


def pine(x, y, s=1.0, color=(40, 120, 70), snow=False):
    r = empty("pine", (x, y, 0))
    prim("cylY", (0.5 * s, 0.5 * s, 2 * s), (0, 0, 1 * s), mat((110, 75, 50), 0.8), parent=r)
    for i, (rad, z) in enumerate(((2.4, 2.6), (1.9, 3.9), (1.3, 5.1))):
        prim("cone", (rad * 2 * s, rad * 2 * s, 2.2 * s), (0, 0, z * s), mat((240, 245, 250) if snow and i == 2 else color, 0.8), parent=r)
    return r


def bunting(a, b, z, n=14, sag=0.8):
    r = empty("bunting"); a, b = Vector(a), Vector(b); cols = [(240, 70, 70), (250, 210, 60), (70, 150, 240), (110, 200, 110), (240, 140, 220)]
    for i in range(n + 1):
        t = i / n; p = a.lerp(b, t); p.z = z - sag * math.sin(t * math.pi)
        if i < n: prim("cone", (0.7, 0.08, 0.9), (p.x, p.y, p.z - 0.45), mat(cols[i % len(cols)], 0.6), rot=(0, 180, 0), parent=r)
    d = b - a; mid = (a + b) / 2; mid.z = z - sag * 0.6
    prim("cyl", (d.length, 0.04, 0.04), tuple(mid), mat((240, 240, 240), 0.5), rot=(0, 0, math.degrees(math.atan2(d.y, d.x))), parent=r)
    return r


def cloud(x, y, z, s=1.0, c=(255, 255, 255)):
    r = empty("cloud", (x, y, z)); m = mat(c, 0.95)
    for dx, dy, dz, k in ((0, 0, 0, 1.0), (1.4, 0.2, -0.2, 0.8), (-1.5, -0.1, -0.25, 0.75), (0.6, -0.3, 0.6, 0.7), (-0.6, 0.3, 0.5, 0.65), (2.5, 0, -0.5, 0.55), (-2.6, 0.1, -0.5, 0.5)):
        prim("ball", (3 * k * s, 2.6 * k * s, 2.2 * k * s), (dx * s, dy * s, dz * s), m, parent=r)
    return r


def clouds(n, lo, hi, smin=1.5, smax=4.0):
    return [cloud(R.uniform(lo[0], hi[0]), R.uniform(lo[1], hi[1]), R.uniform(lo[2], hi[2]), R.uniform(smin, smax)) for _ in range(n)]


def balloon(holder_targets, keys, name="balloon", color=(235, 40, 50), faces=("smile", "suspicious", "grin", "happy"), rise=4.6):
    """Red party balloon with swappable faces, floating `rise` above whichever target holds it.
    holder_targets: {name: grip empty or a free-floating empty}; keys: [(frame, holder name), ...].
    Returns (root, knot empty, {face: plane}); show one face with shortkit.vis."""
    import blocky
    r = empty(name, (0, 0, rise)); m = mat(color, 0.18)
    prim("ball", (2.3, 2.3, 2.7), (0, 0, 0.35), m, parent=r)
    prim("cone", (0.5, 0.5, 0.4), (0, 0, -1.05), m, rot=(180, 0, 0), parent=r)
    prim("ball", (0.5, 0.5, 0.6), (-0.45, -0.75, 0.9), mat((255, 215, 215), 0.1, emit=0.6), parent=r)  # highlight
    fp = bpy.data.meshes.get("faceplane") or blocky._faceplane(); planes = {}
    for k in faces:
        fm = bpy.data.materials.get("face_" + k)
        if not fm: continue
        fo = bpy.data.objects.new(f"{name}_face_{k}", fp); bpy.context.scene.collection.objects.link(fo)
        fo.material_slots[0].link = 'OBJECT'; fo.material_slots[0].material = fm
        fo.parent = r; fo.location = (0, -1.17, 0.45); fo.rotation_euler = (math.radians(84), 0, 0); fo.scale = (1.5, 1.5, 1)
        fo.hide_render = k != faces[0]; planes[k] = fo
    knot = empty(name + "_knot", (0, 0, -1.25), r)
    cons = {}
    for h, tgt in holder_targets.items():
        c = r.constraints.new("COPY_LOCATION"); c.target = tgt; c.use_offset = True; c.name = h; cons[h] = c
    for f, h in keys:
        for n, c in cons.items():
            c.influence = 1.0 if n == h else 0.0; c.keyframe_insert("influence", frame=f)
    for i in (0, 1, 2):  # gentle bobbing on top of the holder's motion
        r.keyframe_insert("location", index=i, frame=0)
    for fc in r.animation_data.action.fcurves:
        if fc.data_path.startswith("constraints"):
            for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'
        elif fc.data_path == "location":
            md = fc.modifiers.new('NOISE'); md.strength = 0.5 if fc.array_index < 2 else 0.3; md.scale = 50; md.phase = 7 * fc.array_index
    return r, knot, planes


def face(planes, f, k):
    """Switch a balloon (or any {name: plane}) to face k from frame f."""
    for n, o in planes.items():
        o.hide_render = n != k; o.keyframe_insert("hide_render", frame=f)


def string(grip, knot, keys_holders=None, name="string"):
    """Thin string from a grip to the balloon knot (stretches as they move)."""
    # Stretch To lengthens along local +Y, so the string is a thin rod from the origin out along +Y
    import bmesh
    me = bpy.data.meshes.get("string_rod")
    if me is None:
        me = bpy.data.meshes.new("string_rod"); bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=0.035, radius2=0.035, depth=1,
                              matrix=__import__("mathutils").Matrix.Translation((0, 0.5, 0)) @ __import__("mathutils").Matrix.Rotation(math.radians(90), 4, "X"))
        bm.to_mesh(me); bm.free(); me.materials.append(mat((245, 245, 245), 0.5))
    s = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(s)
    c = s.constraints.new("COPY_LOCATION"); c.target = grip
    st = s.constraints.new("STRETCH_TO"); st.target = knot; st.rest_length = 1.0; st.volume = 'NO_VOLUME'; st.keep_axis = 'PLANE_X'
    st.bulge = 1
    return s


def goose(x=0, y=0, z=0, s=1.0, name="goose"):
    r = empty(name, (x, y, z)); r.scale = (s, s, s)
    body = mat((245, 245, 240), 0.6); dark = mat((40, 40, 45), 0.6); orange = mat((250, 150, 40), 0.4)
    prim("ball", (1.2, 2.0, 1.1), (0, 0, 0), body, parent=r)
    neck = empty(name + "_neck", (0, -0.7, 0.3), r)
    prim("box", (0.32, 0.32, 1.3), (0, 0, 0.6), dark, parent=neck, bevel=0.1)
    head = empty(name + "_head", (0, 0, 1.25), neck)
    prim("box", (0.45, 0.6, 0.42), (0, -0.1, 0), dark, parent=head, bevel=0.12)
    prim("box", (0.22, 0.45, 0.16), (0, -0.55, -0.05), orange, parent=head, bevel=0.05)
    for sx in (-0.23, 0.23):
        prim("ball", (0.12, 0.08, 0.12), (sx, -0.25, 0.08), mat((255, 255, 255), 0.3), parent=head)
    wings = []
    for sd in (-1, 1):
        w = empty(f"{name}_wing", (sd * 0.5, 0, 0.25), r)
        prim("box", (1.4, 1.3, 0.12), (sd * 0.7, 0.1, 0), mat((200, 200, 205), 0.6), parent=w, bevel=0.05); wings.append((w, sd))
    prim("box", (0.25, 0.25, 0.6), (0, 0.9, 0.15), dark, rot=(-30, 0, 0), parent=r)
    return {"root": r, "neck": neck, "head": head, "wings": wings}


def flap(g, f0, f1, period=8, amp=50):
    for w, sd in g["wings"]:
        for f in range(f0, f1 + 1, period // 2):
            up = ((f - f0) // (period // 2)) % 2 == 0
            w.rotation_euler = (0, math.radians(sd * (amp if up else -amp * 0.4)), 0); w.keyframe_insert("rotation_euler", frame=f)
        for fc in w.animation_data.action.fcurves:
            for kp in fc.keyframe_points: kp.interpolation = 'SINE'; kp.easing = 'EASE_IN_OUT'


def bird(x, y, z, color=(80, 160, 240), s=1.0):
    r = empty("bird", (x, y, z)); r.scale = (s, s, s)
    prim("ball", (0.6, 0.8, 0.6), (0, 0, 0), mat(color, 0.5), parent=r)
    prim("ball", (0.45, 0.45, 0.45), (0, -0.35, 0.3), mat(color, 0.5), parent=r)
    prim("cone", (0.15, 0.15, 0.25), (0, -0.62, 0.3), mat((250, 180, 40), 0.4), rot=(90, 0, 0), parent=r)
    for sx in (-0.12, 0.12): prim("ball", (0.08, 0.05, 0.08), (sx, -0.55, 0.38), mat((20, 20, 20), 0.3), parent=r)
    return r


def helicopter(x, y, z, color=(230, 60, 50)):
    r = empty("heli", (x, y, z)); m = mat(color, 0.35, metal=0.2); glass = mat((150, 210, 255), 0.05, alpha=0.6)
    prim("ball", (4.2, 6.5, 3.6), (0, 0, 0), m, parent=r)
    prim("ball", (3.0, 2.6, 2.4), (0, -2.4, 0.4), glass, parent=r)
    prim("box", (0.7, 7.5, 0.7), (0, 5.5, 0.6), m, parent=r, bevel=0.2)
    prim("box", (0.15, 1.6, 1.8), (0.35, 9.0, 1.2), m, parent=r)
    for sx in (-1.6, 1.6): prim("box", (0.25, 6.0, 0.25), (sx, 0, -2.3), mat((60, 60, 65), 0.4), parent=r)
    rotor = empty("rotor", (0, 0, 2.1), r)
    for a in (0, 90): prim("box", (13, 0.6, 0.12), (0, 0, 0), mat((40, 40, 45), 0.4), rot=(0, 0, a), parent=rotor)
    rotor.keyframe_insert("rotation_euler", frame=0); rotor.rotation_euler = (0, 0, math.radians(360 * 600)); rotor.keyframe_insert("rotation_euler", frame=4000)
    for fc in rotor.animation_data.action.fcurves:
        for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
    return r


def ship(x, y, z=0):
    r = empty("ship", (x, y, z)); white = mat((250, 250, 250), 0.5); blue = mat((40, 70, 150), 0.5)
    prim("box", (9, 40, 4), (0, 0, 2), white, parent=r, bevel=0.6); prim("box", (9.1, 40.1, 1.2), (0, 0, 0.6), blue, parent=r, bevel=0.4)
    for i, (w, l, h) in enumerate(((7.5, 30, 2.4), (6.5, 22, 2.2), (5, 14, 2.0))):
        prim("box", (w, l, h), (0, 1 + i, 4 + i * 2.2 + h / 2), white, parent=r, bevel=0.3)
        for k in range(-int(l / 2.6), int(l / 2.6)):
            prim("box", (w + 0.05, 0.9, 0.6), (0, 1 + i + k * 1.3, 4 + i * 2.2 + h * 0.55), mat((80, 150, 220), 0.2, emit=0.4), parent=r)
    prim("cylY", (2.4, 2.4, 4), (0, 4, 13.5), mat((230, 60, 50), 0.5), parent=r)
    prim("cylY", (2.5, 2.5, 0.9), (0, 4, 15.2), mat((30, 30, 35), 0.5), parent=r)
    return r


def tower(x, y):
    """A tall clock tower in the London style (original blocky build)."""
    r = empty("tower", (x, y, 0)); stone = mat((215, 190, 140), 0.8); gold = mat((230, 190, 80), 0.3, metal=0.6); dark = mat((60, 70, 90), 0.6)
    prim("box", (7, 7, 38), (0, 0, 19), stone, parent=r, bevel=0.2)
    for z in range(4, 38, 4): prim("box", (7.3, 7.3, 0.3), (0, 0, z), mat((190, 165, 120), 0.8), parent=r)
    prim("box", (8, 8, 7), (0, 0, 41.5), stone, parent=r, bevel=0.3)
    for rot in (0, 90, 180, 270):
        a = math.radians(rot); off = Vector((math.sin(a), -math.cos(a), 0)) * 4.06
        plane_image(_A[0] + "clock0.png", (5.6, 5.6), (off.x, off.y, 41.5), rot=(90, 0, rot), parent=r, emit=0.3)
    prim("box", (6.5, 6.5, 4), (0, 0, 47), gold, parent=r, bevel=0.2)
    prim("cone", (7.5, 7.5, 9), (0, 0, 53.5), dark, parent=r)
    prim("cylY", (0.3, 0.3, 3), (0, 0, 59), gold, parent=r)
    return r, 60.5  # top


_A = [""]  # assets dir (set by the story)


def truck(color=(230, 70, 60)):
    r = empty("truck"); m = mat(color, 0.4, metal=0.2); dark = mat((40, 40, 45), 0.6); glass = mat((170, 220, 255), 0.1)
    prim("box", (2.6, 5, 2.6), (0, 1.4, 1.6), mat((240, 240, 240), 0.6), parent=r, bevel=0.15)
    prim("box", (2.6, 2.2, 2.3), (0, -2.4, 1.45), m, parent=r, bevel=0.2)
    prim("box", (2.4, 0.1, 1.0), (0, -3.52, 1.9), glass, parent=r)
    for sx in (-1.3, 1.3):
        for sy in (-2.4, 0.4, 2.8): prim("cyl", (0.4, 1.1, 1.1), (sx, sy, 0.55), dark, parent=r)
    return r


def tuba(color=(235, 190, 70)):
    r = empty("tuba"); g = mat(color, 0.15, metal=1.0)
    prim("cylY", (1.1, 1.1, 2.2), (0, 0, 1.1), g, parent=r)
    prim("cone", (3.2, 3.2, 1.8), (0, 0, 2.9), g, rot=(180, 0, 0), parent=r)
    prim("cylY", (2.7, 2.7, 0.1), (0, 0, 3.75), mat((30, 25, 20), 0.6), parent=r)
    return r


def drum(color=(220, 50, 60)):
    r = empty("drum"); prim("cylY", (1.6, 1.6, 1.1), (0, 0, 0), mat(color, 0.4), parent=r)
    prim("cylY", (1.62, 1.62, 0.06), (0, 0, 0.56), mat((250, 250, 245), 0.6), parent=r)
    return r


def phone():
    r = empty("phone"); prim("box", (0.45, 0.12, 0.9), (0, 0, 0), mat((25, 25, 30), 0.2), parent=r, bevel=0.05)
    prim("box", (0.38, 0.13, 0.75), (0, -0.01, 0), mat((90, 170, 255), 0.1, emit=1.2), parent=r)
    return r


def sandwich():
    r = empty("sandwich")
    for z, c, h in ((0, (230, 190, 120), 0.25), (0.2, (110, 190, 80), 0.1), (0.3, (240, 120, 120), 0.12), (0.42, (250, 220, 90), 0.08), (0.55, (230, 190, 120), 0.25)):
        prim("box", (1.3, 1.3, h), (0, 0, z), mat(c, 0.7), parent=r, bevel=0.06)
    return r


def ice_cream():
    r = empty("icecream"); prim("cone", (0.7, 0.7, 1.3), (0, 0, -0.55), mat((220, 170, 100), 0.7), rot=(180, 0, 0), parent=r)
    prim("ball", (0.9, 0.9, 0.85), (0, 0, 0.2), mat((255, 190, 210), 0.5), parent=r)
    return r


def weather_balloon(x, y, z):
    r = empty("wballoon", (x, y, z)); prim("ball", (4, 4, 4.6), (0, 0, 0), mat((250, 250, 250), 0.3), parent=r)
    prim("box", (0.9, 0.9, 0.9), (0, 0, -4.2), mat((240, 180, 40), 0.5), parent=r, bevel=0.1)
    prim("cylY", (0.04, 0.04, 1.8), (0, 0, -3.0), mat((200, 200, 200), 0.5), parent=r)
    return r


def stadium(x, y, rx=40, ry=28):
    """Oval stadium with a crowd of coloured blocks; returns (root, crowd list of (obj, angle))."""
    r = empty("stadium", (x, y, 0))
    prim("ball", (rx * 1.6, ry * 1.6, 0.4), (0, 0, 0.1), mat((80, 180, 80), 0.9), parent=r)
    for i in range(10): prim("box", (rx * 1.5, 0.6, 0.05), (0, -ry * 0.75 + i * ry * 0.165, 0.31), mat((110, 200, 100), 0.9), parent=r)
    crowd = []; cols = [(240, 80, 80), (80, 140, 240), (250, 210, 60), (250, 250, 250), (120, 200, 120), (240, 140, 200)]
    for ring in range(4):
        n = 70 + ring * 6; k1 = 1.0 + ring * 0.07
        for i in range(n):
            a = i / n * math.tau; px, py = math.cos(a) * rx * k1, math.sin(a) * ry * k1
            o = prim("box", (1.6, 1.6, 2.2), (px, py, 1.5 + ring * 1.6), mat(R.choice(cols), 0.7), rot=(0, 0, math.degrees(a)), parent=r)
            crowd.append((o, a))
    for ring in range(5):  # stands
        k1 = 1.0 + ring * 0.07
    return r, crowd


def wave(crowd, f0, f1, laps=1.5, height=1.4):
    """The crowd does the wave: each block pops up as the wave passes its angle."""
    for o, a in crowd:
        z0 = o.location.z; frac = a / math.tau
        for lap in range(int(laps) + 1):
            fp = int(f0 + (frac + lap) / laps * (f1 - f0))
            if fp > f1: continue
            for df, dz in ((-6, 0), (0, height), (6, 0)):
                o.location.z = z0 + dz; o.keyframe_insert("location", index=2, frame=fp + df)
        o.location.z = z0
