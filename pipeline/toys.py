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


# ---------------- grandpa's house (parrot short) ----------------
def parrot(name="captain", s=1.0, body=(60, 185, 80), head_c=(70, 200, 90), brow=(230, 50, 50), wing=(40, 120, 220)):
    """Captain: blocky green parrot with a red forehead, blue wing tips, hooked beak (lower half opens) and a captain hat.
    Returns parts: root (feet at 0), body, head, jaw (open with rotation X), wings [(pivot, side)], eyes [planes], hat."""
    r = empty(name, (0, 0, 0)); r.scale = (s, s, s)
    bm, hm, bk, dk = mat(body, 0.55), mat(head_c, 0.55), mat((250, 215, 90), 0.4), mat((25, 25, 30), 0.3)
    b = empty(name + "_body", (0, 0, 0.55), r)
    prim("box", (0.85, 0.75, 1.05), (0, 0, 0.35), bm, rot=(-12, 0, 0), parent=b, bevel=0.2)
    prim("box", (0.6, 0.55, 0.55), (0, -0.12, 0.05), mat((250, 220, 90), 0.5), rot=(-12, 0, 0), parent=b, bevel=0.15)  # yellow belly
    prim("box", (0.42, 0.25, 1.0), (0, 0.42, -0.25), mat(wing, 0.5), rot=(35, 0, 0), parent=b, bevel=0.08)  # tail
    prim("box", (0.3, 0.2, 0.7), (0, 0.6, -0.65), mat(brow, 0.5), rot=(35, 0, 0), parent=b, bevel=0.06)
    h = empty(name + "_head", (0, -0.05, 0.95), b)
    prim("box", (0.72, 0.7, 0.66), (0, 0, 0.25), hm, parent=h, bevel=0.2)
    prim("box", (0.6, 0.5, 0.18), (0, -0.05, 0.6), mat(brow, 0.5), parent=h, bevel=0.07)  # red forehead
    prim("box", (0.3, 0.42, 0.34), (0, -0.48, 0.22), bk, rot=(18, 0, 0), parent=h, bevel=0.1)  # upper beak
    prim("box", (0.18, 0.18, 0.22), (0, -0.66, 0.05), bk, rot=(35, 0, 0), parent=h, bevel=0.06)  # hook
    jaw = empty(name + "_jaw", (0, -0.3, 0.06), h)
    prim("box", (0.24, 0.32, 0.12), (0, -0.14, -0.04), mat((230, 180, 70), 0.4), parent=jaw, bevel=0.05)
    eyes = []
    for sx in (-1, 1):
        prim("ball", (0.26, 0.12, 0.26), (sx * 0.3, -0.27, 0.36), mat((255, 255, 255), 0.3), parent=h)
        e = prim("ball", (0.13, 0.08, 0.15), (sx * 0.31, -0.33, 0.36), dk, parent=h); eyes.append(e)
        lid = prim("box", (0.3, 0.16, 0.3), (sx * 0.3, -0.27, 0.36), hm, parent=h, bevel=0.06); lid.scale = (0.3, 0.16, 0.001); eyes.append(lid)
    hat = empty(name + "_hat", (0, 0, 0.7), h)  # tiny captain hat
    prim("cylY", (0.78, 0.78, 0.1), (0, 0, 0), mat((245, 245, 245), 0.5), parent=hat)
    prim("cylY", (0.6, 0.6, 0.28), (0, 0, 0.17), mat((25, 35, 70), 0.5), parent=hat)
    prim("box", (0.5, 0.25, 0.06), (0, -0.4, -0.02), mat((20, 20, 25), 0.3), rot=(-15, 0, 0), parent=hat)
    prim("ball", (0.14, 0.05, 0.14), (0, -0.31, 0.18), mat((250, 200, 40), 0.2, 0.6), parent=hat)
    hat.rotation_euler = (math.radians(-8), 0, math.radians(8))
    wings = []
    for sd in (-1, 1):
        w = empty(f"{name}_wing", (sd * 0.44, 0, 0.7), b)
        prim("box", (0.16, 0.65, 0.95), (sd * 0.05, 0.05, -0.38), mat(body, 0.55), parent=w, bevel=0.06)
        prim("box", (0.17, 0.5, 0.45), (sd * 0.05, 0.12, -0.8), mat(wing, 0.5), parent=w, bevel=0.06); wings.append((w, sd))
    for sx in (-0.18, 0.18):
        prim("box", (0.12, 0.3, 0.12), (sx, -0.05, 0.06), mat((120, 120, 130), 0.6), parent=r, bevel=0.03)
    return {"root": r, "body": b, "head": h, "jaw": jaw, "wings": wings, "lids": eyes[1::2], "hat": hat}


def beak(p, f0, f1, every=5, amt=32):
    """Beak flapping open/shut while it talks (f0..f1)."""
    j = p["jaw"]
    for k, f in enumerate(range(f0, f1, every)):
        j.rotation_euler = (math.radians(amt if k % 2 == 0 else 4), 0, 0); j.keyframe_insert("rotation_euler", frame=f)
    j.rotation_euler = (0, 0, 0); j.keyframe_insert("rotation_euler", frame=f1); j.keyframe_insert("rotation_euler", frame=f0 - 1)


def beak_open(p, f, amt=34, ease=6):
    j = p["jaw"]; j.keyframe_insert("rotation_euler", frame=f - ease)
    j.rotation_euler = (math.radians(amt), 0, 0); j.keyframe_insert("rotation_euler", frame=f)


def lids(p, f, closed, ease=4):
    """Parrot eyes shut (asleep) or open."""
    for l in p["lids"]:
        l.keyframe_insert("scale", frame=f - ease)
        l.scale = (0.3, 0.24, 0.3) if closed else (0.3, 0.16, 0.001); l.keyframe_insert("scale", frame=f)


def tilt(p, f, deg, ease=6, axis=1):
    h = p["head"]; h.keyframe_insert("rotation_euler", frame=f - ease)
    r = list(h.rotation_euler); r[axis] = math.radians(deg); h.rotation_euler = r; h.keyframe_insert("rotation_euler", frame=f)


def cage(x, y, z=0, name="cage"):
    """Round brass birdcage on a stand, with a perch at local height 4.15 (the parrot's feet); tall enough that the
    parrot's head sits well below the dome."""
    r = empty(name, (x, y, z)); brass = mat((215, 170, 70), 0.3, 0.7)
    prim("cylY", (1.6, 1.6, 0.15), (0, 0, 0.07), brass, parent=r)
    prim("cylY", (0.18, 0.18, 3.2), (0, 0, 1.6), brass, parent=r)
    prim("cylY", (2.7, 2.7, 0.18), (0, 0, 3.25), brass, parent=r)
    for k in range(16):
        a = k / 16 * math.tau; prim("cylY", (0.045, 0.045, 3.7), (math.cos(a) * 1.3, math.sin(a) * 1.3, 5.05), brass, parent=r)
    prim("cylY", (2.68, 2.68, 0.1), (0, 0, 6.9), brass, parent=r)
    prim("ball", (2.7, 2.7, 1.0), (0, 0, 6.95), brass, parent=r)
    prim("cylY", (0.3, 0.3, 0.6), (0, 0, 7.6), brass, parent=r)
    prim("cyl", (2.4, 0.08, 0.08), (0, 0, 4.15), mat((150, 100, 60), 0.6), parent=r)
    return r


def blanket(color=(150, 60, 90)):
    r = empty("blanket"); m = mat(color, 0.9)
    prim("ball", (3.1, 3.1, 1.5), (0, 0, 7.0), m, parent=r)
    prim("cylY", (3.0, 3.0, 3.8), (0, 0, 5.1), m, parent=r)
    for k in range(10):
        a = k / 10 * math.tau; prim("box", (0.7, 0.2, 0.6), (math.cos(a) * 1.5, math.sin(a) * 1.5, 3.1), m, rot=(0, 0, math.degrees(a) + 90), parent=r, bevel=0.1)
    return r


def couch(x, y, rot=0, c=(120, 150, 200)):
    r = empty("couch", (x, y, 0)); r.rotation_euler = (0, 0, math.radians(rot)); m = mat(c, 0.85)
    prim("box", (6, 2.6, 1.2), (0, 0, 0.8), m, parent=r, bevel=0.25)
    prim("box", (6, 0.8, 2.4), (0, 1.0, 1.7), m, parent=r, bevel=0.3)
    for sx in (-3.1, 3.1): prim("box", (0.8, 2.6, 1.9), (sx, 0, 1.15), m, parent=r, bevel=0.3)
    for sx in (-1.4, 1.4): prim("box", (2.7, 2.1, 0.45), (sx, -0.15, 1.55), mat(tuple(min(255, v + 20) for v in c), 0.85), parent=r, bevel=0.2)
    return r


def armchair(x, y, rot=0, c=(160, 70, 60)):
    r = empty("armchair", (x, y, 0)); r.rotation_euler = (0, 0, math.radians(rot)); m = mat(c, 0.8)
    prim("box", (2.8, 2.6, 1.3), (0, 0, 0.85), m, parent=r, bevel=0.25)
    prim("box", (2.8, 0.7, 2.6), (0, 1.0, 1.8), m, parent=r, bevel=0.3)
    for sx in (-1.4, 1.4): prim("box", (0.6, 2.6, 2.0), (sx, 0, 1.2), m, parent=r, bevel=0.25)
    return r   # seat top at ~1.5


def table(x, y, w=3.5, d=2.0, h=1.4, c=(150, 100, 60)):
    r = empty("table", (x, y, 0)); m = mat(c, 0.5)
    prim("box", (w, d, 0.2), (0, 0, h), m, parent=r, bevel=0.05)
    for sx in (-w / 2 + 0.25, w / 2 - 0.25):
        for sy in (-d / 2 + 0.25, d / 2 - 0.25): prim("box", (0.22, 0.22, h), (sx, sy, h / 2), m, parent=r)
    return r


def tv(x, y, rot=0):
    """TV on a low cabinet; returns (root, screen) - key the screen's emission to switch it off."""
    r = empty("tv", (x, y, 0)); r.rotation_euler = (0, 0, math.radians(rot))
    prim("box", (4.5, 1.6, 1.6), (0, 0, 0.8), mat((110, 75, 50), 0.6), parent=r, bevel=0.06)
    prim("box", (4.2, 0.3, 2.5), (0, 0, 2.95), mat((25, 25, 30), 0.3), parent=r, bevel=0.06)
    m = bpy.data.materials.new("tv_screen"); m.use_nodes = True; pb = m.node_tree.nodes["Principled BSDF"]
    pb.inputs["Base Color"].default_value = (0.02, 0.02, 0.03, 1); pb.inputs["Emission Color"].default_value = (0.3, 0.6, 1.0, 1)
    pb.inputs["Emission Strength"].default_value = 2.0
    sc = prim("box", (3.9, 0.05, 2.2), (0, -0.17, 2.95), m, parent=r)
    return r, pb.inputs["Emission Strength"]


def fridge(x, y, rot=0):
    """Fridge with a hollow freezer on top (hinge pivot returned: rotate Z +100 to open the door)."""
    r = empty("fridge", (x, y, 0)); r.rotation_euler = (0, 0, math.radians(rot)); w = mat((240, 245, 250), 0.25)
    prim("box", (2.8, 2.6, 4.6), (0, 0, 2.3), w, parent=r, bevel=0.12)
    inside = mat((200, 230, 255), 0.4, emit=0.5)
    for sz, loc in (((2.8, 2.6, 0.15), (0, 0, 4.68)), ((2.8, 2.6, 0.15), (0, 0, 6.42)), ((2.8, 0.15, 1.9), (0, 1.22, 5.55)),
                    ((0.15, 2.6, 1.9), (-1.32, 0, 5.55)), ((0.15, 2.6, 1.9), (1.32, 0, 5.55))):
        prim("box", sz, loc, w, parent=r, bevel=0.03)
    prim("box", (2.45, 0.05, 1.6), (0, 1.12, 5.55), inside, parent=r)
    prim("box", (2.45, 2.3, 0.05), (0, 0, 4.77), inside, parent=r)
    hinge = empty("freezer_hinge", (1.4, -1.35, 5.55), r)
    prim("box", (2.8, 0.18, 1.9), (-1.4, -0.05, 0), w, parent=hinge, bevel=0.08)
    prim("box", (0.15, 0.15, 1.2), (-2.5, -0.25, 0), mat((180, 185, 190), 0.3, 0.8), parent=hinge)
    prim("box", (0.15, 0.15, 2.2), (-1.1, -1.45, 2.8), mat((180, 185, 190), 0.3, 0.8), parent=r)
    return r, hinge


def nugget():
    r = empty("nugget"); prim("ball", (0.55, 0.38, 0.32), (0, 0, 0), mat((215, 150, 60), 0.8), parent=r)
    prim("ball", (0.5, 0.34, 0.28), (0.04, -0.02, 0.03), mat((235, 180, 90), 0.85, emit=0.05), parent=r)
    return r


def stopwatch(img):
    r = empty("stopwatch"); m = mat((200, 205, 215), 0.25, 0.8)
    prim("cylY", (1.4, 1.4, 0.35), (0, 0, 0), m, rot=(90, 0, 0), parent=r)
    prim("cylY", (0.3, 0.3, 0.35), (0, 0, 0.85), m, parent=r)
    btn = prim("box", (0.35, 0.3, 0.2), (0, 0, 1.08), mat((220, 50, 50), 0.4), parent=r, bevel=0.05)
    plane_image(img, (1.25, 1.25), (0, -0.19, 0), parent=r)
    return r, btn


def wall_clock(dial_img, size=3.0, rim=(40, 70, 140)):
    """3D wall clock facing -Y; set_time() keys its hands."""
    r = empty("wallclock")
    prim("cylY", (size * 1.04, size * 1.04, 0.35), (0, 0.2, 0), mat(rim, 0.35), rot=(90, 0, 0), parent=r)
    plane_image(dial_img, (size, size), (0, -0.0, 0), parent=r)
    hh = empty("hour_hand", (0, -0.08, 0), r); mh = empty("min_hand", (0, -0.12, 0), r)
    ink = mat((30, 30, 40), 0.4)
    prim("box", (size * 0.045, 0.04, size * 0.27), (0, 0, size * 0.11), ink, parent=hh, bevel=0.02)
    prim("box", (size * 0.03, 0.04, size * 0.4), (0, 0, size * 0.17), ink, parent=mh, bevel=0.01)
    prim("cylY", (size * 0.07, size * 0.07, 0.1), (0, -0.16, 0), mat((220, 40, 40), 0.3), rot=(90, 0, 0), parent=r)
    return {"root": r, "h": hh, "m": mh}


def set_time(clk, f, h, m, ease=None):
    for o, a in ((clk["h"], (h + m / 60) / 12 * 360), (clk["m"], (h * 60 + m) / 60 * 360)):
        if ease: o.keyframe_insert("rotation_euler", frame=f - ease)
        o.rotation_euler = (0, math.radians(a), 0); o.keyframe_insert("rotation_euler", frame=f)


def router():
    r = empty("router"); prim("box", (1.2, 0.8, 0.25), (0, 0, 0.12), mat((30, 30, 35), 0.3), parent=r, bevel=0.05)
    for sx in (-0.45, 0.45): prim("box", (0.08, 0.08, 0.8), (sx, 0.3, 0.6), mat((30, 30, 35), 0.3), rot=(0, sx * 20, 0), parent=r)
    for k in range(4): prim("ball", (0.06, 0.03, 0.06), (-0.3 + k * 0.2, -0.41, 0.15), mat((60, 255, 120), 0.2, emit=3), parent=r)
    return r


def headphones(c=(230, 40, 60)):
    r = empty("headphones"); m = mat(c, 0.4)
    for k in range(9):
        a = math.radians(-80 + k * 20); prim("box", (0.16, 0.16, 0.18), (math.sin(a) * 0.48, 0, math.cos(a) * 0.48), m, parent=r, bevel=0.03)
    for sx in (-0.5, 0.5): prim("cyl", (0.22, 0.4, 0.4), (sx, 0, 0), mat((30, 30, 35), 0.4), parent=r)
    return r


def coffin(x, y, rot=0):
    r = empty("coffin", (x, y, 0)); r.rotation_euler = (0, 0, math.radians(rot)); wood = mat((110, 60, 35), 0.35)
    prim("box", (7, 2.4, 0.9), (0, 0, 1.0), mat((210, 210, 215), 0.6), parent=r, bevel=0.05)  # stand
    for sx in (-3, 3): prim("box", (0.4, 2.0, 1.0), (sx, 0, 0.5), mat((180, 180, 185), 0.5), parent=r)
    prim("box", (6.6, 2.2, 1.6), (0, 0, 2.25), wood, parent=r, bevel=0.15)
    prim("box", (6.8, 2.35, 0.3), (0, 0, 3.15), mat((130, 75, 45), 0.3), parent=r, bevel=0.1)
    for k in range(9):  # flowers on the lid
        prim("ball", (0.45, 0.45, 0.4), (-1.6 + k * 0.4, (k % 3 - 1) * 0.35, 3.45), mat(R.choice([(250, 250, 250), (240, 120, 160), (250, 210, 80)]), 0.6), parent=r)
    return r   # lid top at 3.3


def chair(x, y, rot=0, c=(245, 245, 245)):
    r = empty("chair", (x, y, 0)); r.rotation_euler = (0, 0, math.radians(rot)); m = mat(c, 0.6)
    prim("box", (1.5, 1.4, 0.15), (0, 0, 1.5), m, parent=r)
    prim("box", (1.5, 0.15, 1.6), (0, 0.65, 2.3), m, parent=r)
    for sx in (-0.65, 0.65):
        for sy in (-0.6, 0.6): prim("box", (0.12, 0.12, 1.5), (sx, sy, 0.75), m, parent=r)
    return r   # seat top at 1.58


def easel(x, y, img, rot=0):
    r = empty("easel", (x, y, 0)); r.rotation_euler = (0, 0, math.radians(rot)); w = mat((120, 80, 50), 0.6)
    for sx in (-0.8, 0.8): prim("box", (0.15, 0.15, 5.0), (sx, 0.2, 2.5), w, rot=(-8, 0, sx * -6), parent=r)
    prim("box", (2.4, 0.2, 0.15), (0, -0.2, 2.6), w, parent=r)
    plane_image(img, (2.2, 2.75), (0, -0.25, 4.05), rot=(84, 0, 0), parent=r)
    return r


def podium(x, y, rot=0):
    r = empty("podium", (x, y, 0)); r.rotation_euler = (0, 0, math.radians(rot)); w = mat((120, 75, 45), 0.4)
    prim("box", (1.8, 1.4, 3.2), (0, 0, 1.6), w, parent=r, bevel=0.08)
    prim("box", (2.1, 1.6, 0.2), (0, -0.1, 3.3), w, rot=(-15, 0, 0), parent=r, bevel=0.05)
    return r


def flower_bush(x, y, s=1.0):
    r = empty("bush", (x, y, 0)); r.scale = (s, s, s)
    prim("ball", (2.6, 2.6, 1.8), (0, 0, 0.8), mat((70, 160, 80), 0.8), parent=r)
    for k in range(6):
        a = k / 6 * math.tau; prim("ball", (0.45, 0.45, 0.45), (math.cos(a) * 1.0, math.sin(a) * 1.0, 1.4), mat(R.choice([(250, 120, 160), (255, 255, 255), (250, 210, 80)]), 0.6), parent=r)
    return r


def lamp(x, y, z=0):
    """Floor lamp; returns (root, point light) - key the light's energy for night."""
    r = empty("lamp", (x, y, z)); prim("cylY", (1.0, 1.0, 0.15), (0, 0, 0.07), mat((60, 60, 65), 0.4), parent=r)
    prim("cylY", (0.12, 0.12, 4.6), (0, 0, 2.3), mat((60, 60, 65), 0.4), parent=r)
    prim("cone", (1.5, 1.5, 1.1), (0, 0, 4.9), mat((255, 235, 190), 0.6, emit=1.5), parent=r)
    ld = bpy.data.lights.new("lamp", "POINT"); ld.energy = 0; ld.color = (1.0, 0.82, 0.6); ld.shadow_soft_size = 0.6
    lo = bpy.data.objects.new("lamp_light", ld); bpy.context.scene.collection.objects.link(lo); lo.parent = r; lo.location = (0, 0, 4.4)
    return r, ld


def papers(img, n=8):
    r = empty("papers")
    for k in range(n): prim("box", (1.6, 2.1, 0.03), (R.uniform(-0.05, 0.05), R.uniform(-0.05, 0.05), k * 0.04), mat((248, 248, 245), 0.8), rot=(0, 0, R.uniform(-4, 4)), parent=r)
    plane_image(img, (1.55, 2.0), (0, 0, n * 0.04 + 0.01), rot=(0, 0, 0), parent=r)
    return r


def card(img, w, h):
    """A flat picture prop (the will, the note, the check) lying in X/Z, facing -Y."""
    r = empty("card"); prim("box", (w * 1.02, 0.02, h * 1.02), (0, 0.02, 0), mat((245, 245, 240), 0.8), parent=r)
    plane_image(img, (w, h), (0, -0.0, 0), parent=r)
    return r


def box_prop(img, w=1.2, d=0.5, h=1.6, c=(230, 60, 50)):
    r = empty("box"); prim("box", (w, d, h), (0, 0, h / 2), mat(c, 0.5), parent=r, bevel=0.03)
    plane_image(img, (w * 0.98, h * 0.98), (0, -d / 2 - 0.01, h / 2), parent=r)
    return r


def window(x, y, w=4.0, h=3.6, z=3.2, rot=0, sky=(150, 200, 255)):
    """A bright window (frame + glowing pane); returns (root, pane material emission input) for time of day."""
    r = empty("window", (x, y, 0)); r.rotation_euler = (0, 0, math.radians(rot)); fm = mat((255, 255, 255), 0.5)
    m = bpy.data.materials.new("window_pane"); m.use_nodes = True; pb = m.node_tree.nodes["Principled BSDF"]
    from shortkit import lin
    pb.inputs["Base Color"].default_value = lin(sky); pb.inputs["Emission Color"].default_value = lin(sky); pb.inputs["Emission Strength"].default_value = 1.4
    prim("box", (w, 0.1, h), (0, 0, z), m, parent=r)
    for dx in (-w / 2, 0, w / 2): prim("box", (0.18, 0.25, h + 0.2), (dx, -0.05, z), fm, parent=r)
    for dz in (-h / 2, h / 2): prim("box", (w + 0.2, 0.25, 0.18), (0, -0.05, z + dz), fm, parent=r)
    return r, pb
