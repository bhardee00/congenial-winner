"""'The Wish' — 9:16 Roblox R6 animation synced to the user's voiceover (word timings in work/wish/words.json).
No captions, no music, no audio in the output.
  blender -b -P story.py -- build              -> work/wish/wish.blend
  blender -b work/wish/wish.blend -P story.py -- render START END [preview]
"""
import bpy, sys, os, math, json, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mathutils import Vector
from lib import *

FPS = 30
OUT = WK + 'wish/'
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else ['build']

# ------------------------------------------------------------------ timing
WORDS = json.load(open(OUT + 'words.json'))
TOK = [w['w'].lower() for w in WORDS]
END_T = json.load(open(OUT + 'meta.json'))['duration']
LAST_F = int(round(END_T * FPS))           # exclusive
_cursor = [0]
def at(phrase):
    p = phrase.lower().replace("-", " ").split()
    for i in range(_cursor[0], len(TOK) - len(p) + 1):
        if TOK[i:i + len(p)] == p:
            _cursor[0] = i + 1; return WORDS[i]['s']
    raise ValueError('anchor not found: ' + phrase)


# ------------------------------------------------------------------ shots
# (anchor, light, camera(target, dir, d0, d1, lens), setup-fn name)
SHOTS = []
def shot(anchor, light, target, direction, d0, d1, lens=35):
    def deco(fn):
        SHOTS.append(dict(anchor=anchor, light=light, target=Vector(target), dir=Vector(direction).normalized(), d0=d0, d1=d1, lens=lens, fn=fn)); return fn
    return deco


def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    import world, r6, r15
    sc = bpy.context.scene
    world.build_all()
    cast = json.load(open(WK + 'chars/cast.json'))
    C = {n: r15.R15(n, cfg) for n, cfg in cast.items()}
    W = world.WELL; I = world.INT; CT = world.CTRL
    random.seed(3)

    # ---------------- helpers ----------------
    def P(**k):
        d = dict(rs=(0, 0, 0), ls=(0, 0, 0), rh=(0, 0, 0), lh=(0, 0, 0), neck=(0, 0, 0), torso=(0, 0, 0), tz=0.0); d.update(k); return d
    def kp(c, f, p): c.pose(f, **p)
    def add(p, **k):
        q = dict(p)
        for j, v in k.items():
            if j == 'tz': q['tz'] = q.get('tz', 0) + v
            else: q[j] = tuple(a + b for a, b in zip(q[j], v))
        return q
    def idle(c, f0, f1, p=None, amp=1.0, look=0.0):
        p = p or P(); t = 0; f = f0; ph = random.random() * 6
        while f < f1:
            s = math.sin(ph + t * 1.3)
            kp(c, f, add(p, rs=(2 * s * amp, 0, 0), ls=(-2 * s * amp, 0, 0), neck=(1.5 * s * amp, 0, look + 3 * math.sin(ph + t * 0.7) * amp), tz=0.03 * s * amp))
            f += 20; t += 1
        kp(c, f1 - 1, add(p, neck=(0, 0, look)))
    def seq(c, keys):
        for f, p in keys: kp(c, f, p)
    def head(dx, dy): return math.degrees(math.atan2(dx, -dy))
    def stand(c, f0, f1, pos, hd=0, face='smile', p=None, amp=1.0, look=0.0):
        c.place(f0, pos, hd); c.place(f1 - 1, pos, hd); c.face(f0, face); idle(c, f0, f1, p, amp, look)
    def walk(c, f0, f1, a, b, face='smile', speed_div=10, arms=30, legs=32, look=0.0, extra=None):
        a, b = Vector(a), Vector(b); hd = head(b.x - a.x, b.y - a.y)
        c.place(f0, a, hd); c.place(f1 - 1, b, hd); c.face(f0, face)
        k = 0
        for f in range(f0, f1, speed_div):
            s = 1 if k % 2 == 0 else -1
            p = P(rs=(-arms * s, 0, 0), ls=(arms * s, 0, 0), rh=(legs * s, 0, 0), lh=(-legs * s, 0, 0), neck=(0, 0, look), tz=0.06 * (k % 2))
            if extra: p = add(p, **extra)
            kp(c, f, p); k += 1
        kp(c, f1 - 1, P(neck=(0, 0, look)))
    def path_walk(c, f0, f1, pts, face='smile', look=(0, 0, 0)):
        """walk along a list of (x,y,z) points (used for the spiral steps)."""
        n = len(pts) - 1; c.face(f0, face)
        for i, q in enumerate(pts):
            f = f0 + round((f1 - 1 - f0) * i / n)
            nx = pts[min(i + 1, n)]; pv = pts[max(i - 1, 0)]; d = Vector(nx) - Vector(pv)
            c.place(f, q, head(d.x, d.y))
            s = 1 if i % 2 == 0 else -1
            kp(c, f, P(rs=(-25 * s, 0, 0), ls=(25 * s, 0, 0), rh=(28 * s, 0, 0), lh=(-28 * s, 0, 0), neck=look))
    def sit_pose(**k): return P(rh=(-90, 0, 0), lh=(-90, 0, 0), **k)
    def facing(pos, tgt): return head(tgt[0] - pos[0], tgt[1] - pos[1])
    def step_pos(i, r=None):
        a = math.radians(-90 + i * 15); rm = r or 5.7
        return (W.x + math.cos(a) * rm, W.y + math.sin(a) * rm, -0.45 * (i + 1))
    BOTTOM = lambda ang, r=5.6: Vector((W.x + math.cos(math.radians(ang)) * r, W.y + math.sin(math.radians(ang)) * r, -10.0))
    def crowd(f0, f1, names, faces, p=None, a0=25, a1=155, r=9.6):
        for i, n in enumerate(names):
            a = math.radians(a0 + (a1 - a0) * i / max(1, len(names) - 1)); pos = (W.x + math.cos(a) * r, W.y + math.sin(a) * r, 0.02)
            stand(C[n], f0, f1, pos, facing(pos, W), faces[i % len(faces)] if isinstance(faces, list) else faces, p)
    PROPS = []
    def prop(o): o.hide_render = True; o.hide_viewport = True; PROPS.append(o); return o
    def show(o, f0, f1):
        if f0 > 0: key_vis(o, 0, False)
        key_vis(o, f0, True); key_vis(o, f1, False)

    # ---------------- props ----------------
    cake_root = prop(link(bpy.data.objects.new('cake', None)))
    picnic = box((7, 3.6, 0.35), (-95, 14.2, 3.0), mat(0x8d6e4f, 0.6, kind='wood')); picnic.parent = cake_root
    for sx in (-3, 3): o = box((0.4, 3, 3), (-95 + sx, 14.2, 1.4), mat(0x8d6e4f, 0.6, kind='wood')); o.parent = cake_root
    o = box((7.2, 3.8, 0.05), (-95, 14.2, 3.2), mat(0xffffff, 0.8, kind='fabric')); o.parent = cake_root
    o = cyl(1.3, 1.1, (-95, 13.8, 3.8), mat(0xfce4ec, 0.5), v=28); o.parent = cake_root
    o = cyl(1.33, 0.25, (-95, 13.8, 4.25), mat(0xec407a, 0.5), v=28); o.parent = cake_root
    for k in range(13):
        a = k / 13 * math.tau; o = cyl(0.06, 0.6, (-95 + math.cos(a) * 0.9, 13.8 + math.sin(a) * 0.9, 4.65), mat([0x42a5f5, 0xffee58, 0x66bb6a][k % 3], 0.5), v=6); o.parent = cake_root
        o = sphere(0.08, (-95 + math.cos(a) * 0.9, 13.8 + math.sin(a) * 0.9, 5.02), mat(0xffb300, 0.3, emit=12), scale=(1, 1, 1.6), seg=8); o.parent = cake_root
    for k in range(3):
        o = box((0.9, 0.9, 0.9), (-98 + k * 0.3, 13.6 + k * 0.5, 3.65), mat([0x7e57c2, 0x26a69a, 0xffa726][k], 0.5)); o.parent = cake_root
    for o in cake_root.children: prop(o)
    hrt = prop(heart(0.9, (0, 0, 0), mat(0xff1744, 0.2, emit=9, name='heartneon'), name='heart'))
    bulb = prop(sphere(0.55, (0, 0, 0), mat(0xffee58, 0.2, emit=14, name='bulb'), seg=16, name='bulb'))
    bb = prop(cyl(0.3, 0.45, (0, 0, -0.6), mat(0x9e9e9e, 0.3, metal=1), v=10)); bb.parent = bulb
    money = prop(text("$1,000,000", (0, 0, 0), 1.6, mat(0x00e676, 0.2, emit=7, name='money'), extrude=0.2, name='money'))
    trash = prop(cyl(0.9, 2.4, (0, 0, 0), mat(0x607d8b, 0.4, metal=0.6), v=16, name='trashcan'))
    tl = prop(cyl(1.0, 0.25, (0, 0, 1.3), mat(0x546e7a, 0.4, metal=0.6), v=16)); tl.parent = trash
    hat = prop(link(bpy.data.objects.new('hat', None)))
    o = prop(cyl(0.95, 0.12, (0, 0, 0), mat(0x4e342e, 0.7, kind='fabric'), v=24)); o.parent = hat
    o = prop(cyl(0.6, 0.65, (0, 0, 0.35), mat(0x4e342e, 0.7, kind='fabric'), v=24)); o.parent = hat
    o = prop(cyl(0.62, 0.15, (0, 0, 0.12), mat(0x212121, 0.6), v=24)); o.parent = hat
    paper = prop(box((1.2, 0.04, 1.6), (0, 0, 0), mat(0xe8d9b0, 0.8, name='heldpaper'), name='paper'))
    balloon = prop(sphere(0.95, (0, 0, 0), mat(0xff4081, 0.25), scale=(1, 1, 1.18), seg=16, name='balloon'))
    bs = prop(cyl(0.03, 5.5, (0, 0, -3.8), mat(0xeeeeee, 0.5), v=4)); bs.parent = balloon
    car = world.car(-43.5, 25, 180, body=0x8d6e63, rust=True, name='dadcar')
    def car_at(f, x, y, hd): car.location = (x, y, 0); car.rotation_euler = (0, 0, math.radians(hd)); car.keyframe_insert('location', frame=f); car.keyframe_insert('rotation_euler', frame=f)

    def water(f, emit, light=0.0, col=(1.0, 0.9, 0.55)):
        s, p = CT['water_emit']; s.default_value = emit; s.keyframe_insert('default_value', frame=f)
        s, p = CT['water_col']; s.default_value = col + (1,); s.keyframe_insert('default_value', frame=f)
        CT['well_light'].data.energy = light; CT['well_light'].data.keyframe_insert('energy', frame=f)

    # ================================================================ SHOT LIST
    M, T, L_ = C['milo'], C['tess'], C['lila']
    MF = lambda pos: Vector(pos) + Vector((0, 0, 5.15))         # face height for a standing character

    @shot("in this world", 'day', (-65, 10.5, 5.15), (0, -1, 0.13), 2.4, 30, 35)
    def s01(f0, f1):
        stand(M, f0, f1, (-65, 10.5, 0.5), 0, 'smile', amp=0.6)

    @shot("not the wish", 'day', (-95, 15.5, 5.0), (0.15, -1, 0.28), 13, 9, 35)
    def s02(f0, f1):
        show(cake_root, f0, f1); [show(o, f0, f1) for o in cake_root.children]
        stand(C['kid'], f0, f1, (-95, 16.4, 0.6), 0, 'whisper', P(rs=(-35, 0, 10), ls=(-35, 0, -10)))

    @shot("the one you actually", 'day', (-95, 16.4, 4.6), (0.1, -1, 0.08), 9, 5.5, 35)
    def s03(f0, f1):
        show(cake_root, f0, f1); [show(o, f0, f1) for o in cake_root.children]
        stand(C['kid'], f0, f1, (-95, 16.4, 0.6), 0, 'closed', P(rs=(-20, 0, 25), ls=(-20, 0, -25)), amp=0.4)
        hrt.location = (-95, 15.2, 3.9); hrt.keyframe_insert('location', frame=f0); hrt.keyframe_insert('location', frame=f1 - 1); show(hrt, f0, f1)
        for k, f in enumerate(range(f0, f1, 8)):
            s = 1.0 + 0.12 * (k % 2); hrt.scale = (s, s, s); hrt.keyframe_insert('scale', frame=f)

    @shot("at midnight", 'night', (125, 30, 17), (0, -1, 0.12), 62, 48, 32)
    def s04(f0, f1):
        walk(C['kid'], f0, f1, (110, 14, 0.0), (102, 17, 0.0), 'neutral')

    @shot("of the old well", 'night', (125, 72, -4), (0, -0.62, 1), 30, 22, 30)
    def s05(f0, f1):
        path_walk(C['kid'], f0, f1, [(W.x, W.y - 9.5, 0.02)] + [step_pos(i) for i in range(0, 12)], 'neutral')

    @shot("close your eyes", 'night', BOTTOM(240) + Vector((0, 0, 5.1)), (0.5, 0.866, 0.12), 6.5, 4.0, 40)
    def s06(f0, f1):
        pos = BOTTOM(240); stand(C['kid'], f0, f1, pos, facing(pos, W), 'closed', P(rs=(-15, 0, 0), ls=(-15, 0, 0)), amp=0.3)

    @shot("and by sunrise", 'dawn', (125, 76, -9.3), (0.35, 0.45, 1), 13, 21, 32)
    def s07(f0, f1):
        water(f0, 1.0, 900); water(f1, 0, 0)
        pos = BOTTOM(240); stand(C['kid'], f0, f1, pos, facing(pos, W), 'happy', P(rs=(0, 150, 0), ls=(0, -150, 0)))

    @shot("a girl named lila", 'morning', (-95, 15.5, 4.8), (0.1, -1, 0.1), 15, 10, 35)
    def s08(f0, f1):
        stand(L_, f0, f1, (-95, 15.5, 0.6), 0, 'closed', P(rs=(-40, 0, 25), ls=(-40, 0, -25)), amp=0.4)
        for k, f in enumerate(range(f0, f1, 6)):
            pass

    @shot("now she floats", 'morning', (-12, 2, 7), (0, -1, 0.05), 15, 27, 32)
    def s09(f0, f1):
        L = L_; L.face(f0, 'laugh')
        for k, f in enumerate(range(f0, f1, 12)):
            t = (f - f0) / max(1, f1 - f0); L.place(f, (-22 + t * 16, 2, 6.5 + 0.5 * math.sin(k * 1.4)), -90, 0, 0)
            kp(L, f, P(rs=(0, 75 + 6 * (k % 2), 0), ls=(0, -75 - 6 * (k % 2), 0), rh=(12, 0, 0), lh=(18, 0, 0), neck=(-10, 0, 0)))
        L.place(f1 - 1, (-6, 2, 6.8), -90); kp(L, f1 - 1, P(rs=(0, 75, 0), ls=(0, -75, 0), rh=(12, 0, 0), lh=(18, 0, 0)))
        for n, x, hd in (('boy2', -20, -90), ('girl2', -14, -90), ('boy3', -9, -90)):
            walk(C[n], f0, f1, (x, -10.5, 0.5), (x + 3.5, -10.5, 0.5), 'shock', speed_div=12, arms=20, legs=22, extra=dict(neck=(-25, 0, 0)))

    @shot("my name is milo", 'day', (-65, 16, 4.6), (0, -1, 0.12), 16, 10, 35)
    def s10(f0, f1):
        M.place(f0, (-65, 16.5, 0.6), 0); M.place(f1 - 1, (-65, 16.5, 0.6), 0); M.face(f0, 'happy')
        for k, f in enumerate(range(f0, f1, 7)):
            kp(M, f, P(rs=(-165, 18 if k % 2 else -12, 0), ls=(3, 0, 0), neck=(0, 0, 4 * (k % 2))))
        kp(M, f1 - 1, P(rs=(-165, 0, 0)))

    @shot("i'm twelve", 'day', I['bedroom'] + Vector((0, 4, 4.6)), (0, -1, 0.12), 7, 14, 32)
    def s11(f0, f1):
        stand(M, f0, f1, I['bedroom'] + Vector((0, 4, 0)), 0, 'smirk', P(rs=(0, 28, 0), ls=(0, -28, 0)), amp=0.6)

    @shot("i've planned my wish", 'day', I['bedroom'] + Vector((-3, 10.6, 7.2)), (0.05, -1, 0.0), 18, 13, 32)
    def s12(f0, f1):
        pos = I['bedroom'] + Vector((-6.5, 6.5, 0))
        stand(M, f0, f1, pos, 150, 'happy', P(ls=(-125, 0, -20)), amp=0.5, look=-20)

    @shot("my best friend is tess", 'day', (-29.3, 10.5, 4.6), (0, -1, 0.1), 17, 11, 35)
    def s13(f0, f1):
        stand(T, f0, f1, (-31.2, 10.5, 0.5), 12, 'angry', P(rs=(-80, 0, 42), ls=(-72, 0, -42)), amp=0.4)
        stand(M, f0, f1, (-27.4, 10.5, 0.5), -12, 'happy', P(rs=(-15, 0, 0)), look=-10)

    @shot("and the whole town is scared", 'day', (-32, 13, 4.5), (0, -1, 0.18), 24, 17, 35)
    def s14(f0, f1):
        walk(T, f0, f1, (-36, 10.5, 0.5), (-30, 10.5, 0.5), 'angry', speed_div=11, arms=18)
        for n, pos, hd in (('woman', (-24, 16.5, 0.6), -60), ('man', (-20.5, 15.5, 0.0), -70), ('man2', (-46, 17, 0.0), 50), ('woman2', (-28.5, 17.5, 0.6), -40)):
            c = C[n]; c.place(f0, pos, hd); c.place(f1 - 1, Vector(pos) + Vector((0, 1.0, 0)), hd); c.face(f0, 'worried')
            seq(c, [(f0, P(rs=(-40, 0, 20), ls=(-40, 0, -20))), (f1 - 1, P(rs=(-70, 0, 20), ls=(-70, 0, -20), neck=(-5, 0, 0)))])

    @shot("her dad left", 'sunset', (-47, -3.5, 2.5), (0.2, 1, 0.35), 26, 33, 32)
    def s15(f0, f1):
        car_at(f0, -40, -3.5, -90); car_at(f1 - 1, -54, -3.5, -90)
        stand(T, f0, f1, (-28, 16.2, 0.6), facing((-28, 16.2), (-50, 0)), 'sad', P(ls=(-75, 0, 0)), amp=0.3)

    @shot("and ever since then", 'day', (-36, 10, 3), (0.1, -1, 0.15), 15, 10, 35)
    def s16(f0, f1):
        pos = (-37.5, 10.5, 0.5); T.place(f0, pos, -35); T.place(f1 - 1, pos, -35); T.face(f0, 'angry')
        k1 = f0 + int((f1 - f0) * 0.35)
        seq(T, [(f0, P(rs=(-60, 0, 35), ls=(-60, 0, -35))), (k1 - 6, P(rh=(25, 0, 0), rs=(-60, 0, 35), ls=(-60, 0, -35))),
                (k1, P(rh=(-75, 0, 0), rs=(20, 0, 0), ls=(-20, 0, 0), torso=(8, 0, 0))), (k1 + 10, P(rh=(-30, 0, 0), rs=(10, 0, 0), ls=(-10, 0, 0))), (f1 - 1, P(rs=(-70, 0, 40), ls=(-70, 0, -40)))])
        show(trash, f0, f1)
        trash.location = (-35.3, 10.0, 1.7); trash.rotation_euler = (0, 0, 0); trash.keyframe_insert('location', frame=f0); trash.keyframe_insert('rotation_euler', frame=f0)
        trash.keyframe_insert('location', frame=k1); trash.keyframe_insert('rotation_euler', frame=k1)
        trash.location = (-31.5, 9.6, 1.3); trash.rotation_euler = (0, math.radians(84), 0.3); trash.keyframe_insert('location', frame=k1 + 12); trash.keyframe_insert('rotation_euler', frame=k1 + 12)
        trash.keyframe_insert('location', frame=f1 - 1); trash.keyframe_insert('rotation_euler', frame=f1 - 1)

    @shot("the grown ups whisper", 'day', (-10.7, 11, 4.9), (0, -1, 0.08), 12, 7.5, 35)
    def s17(f0, f1):
        stand(C['woman'], f0, f1, (-12.3, 11, 0.5), 28, 'whisper', P(rs=(-135, 0, 35), neck=(0, 0, 18)), amp=0.4)
        stand(C['man'], f0, f1, (-9.0, 11, 0.5), -28, 'worried', P(), amp=0.4, look=-12)
        stand(T, f0, f1, (-26, -10.5, 0.5), 160, 'angry', P(rs=(-80, 0, 42), ls=(-72, 0, -42)), amp=0.3)

    @shot("her birthday was one week away", 'day', I['bedroom'] + Vector((8, 10.6, 7.9)), (-0.22, -1, -0.05), 10, 5.5, 35)
    def s18(f0, f1):
        stand(M, f0, f1, I['bedroom'] + Vector((4.2, 6.0, 0)), 165, 'worried', amp=0.4, look=10)

    @shot("so i went to the library", 'day', (35, 17, 7), (0, -1, 0.12), 36, 27, 32)
    def s19(f0, f1):
        walk(M, f0, f1, (33.5, 6, 0.5), (34.5, 15.5, 1.2), 'smile', speed_div=11)

    @shot("and read every wish record", 'day', I['library'] + Vector((-3.5, -5.6, 4.2)), (0.05, 1, 0.38), 8, 14, 32)
    def s20(f0, f1):
        pos = I['library'] + Vector((-3.5, -6.4, 0.85)); M.place(f0, pos, 180); M.place(f1 - 1, pos, 180); M.face(f0, 'neutral')
        for k, f in enumerate(range(f0, f1, 9)):
            kp(M, f, sit_pose(rs=(-70 - 15 * (k % 2), 0, 10), ls=(-60, 0, -10), neck=(14, 0, 6 * (k % 2))))
        kp(M, f1 - 1, sit_pose(rs=(-70, 0, 10), ls=(-60, 0, -10), neck=(14, 0, 0)))

    @shot("one boy wished out loud", 'day', BOTTOM(240) + Vector((0, 0, 5)), (0.5, 0.866, 0.55), 11, 8, 32)
    def s21(f0, f1):
        pos = BOTTOM(240); stand(C['boy2'], f0, f1, pos, facing(pos, W), 'laugh', P(rs=(0, 155, 0), ls=(0, -155, 0)))
        money.location = W + Vector((0, 0, -5)); money.rotation_euler = (math.radians(90), 0, math.radians(30)); money.keyframe_insert('location', frame=f0)
        money.location = W + Vector((0, 0, -3.5)); money.keyframe_insert('location', frame=f1 - 1); show(money, f0, f1)

    @shot("instead his grandma", 'day', I['hospital'] + Vector((0.8, 5, 4.6)), (0, -1, 0.25), 10, 15, 32)
    def s22(f0, f1):
        g = C['grandma']; gp = I['hospital'] + Vector((0, 6.2, 2.05))
        g.place(f0, gp, 0); g.place(f1 - 1, gp, 0); g.face(f0, 'shock')
        seq(g, [(f0, sit_pose(rs=(0, 15, 0), ls=(0, -15, 0), torso=(-25, 0, 0))), (f0 + 18, sit_pose(rs=(-40, 0, 0), ls=(-40, 0, 0))), (f1 - 1, sit_pose(rs=(-80, 0, 25), ls=(-80, 0, -25)))])
        g.face(f0 + 18, 'happy')
        b = C['boy2']; bp = I['hospital'] + Vector((3.8, 1.8, 0)); b.place(f0, bp, facing(bp, gp)); b.place(f1 - 1, bp, facing(bp, gp)); b.face(f0, 'shock')
        seq(b, [(f0, P()), (f0 + 14, P(rs=(-85, 0, 25), ls=(-85, 0, -25))), (f1 - 1, P(rs=(-85, 0, 25), ls=(-85, 0, -25)))])
        b.face(f0 + 14, 'cry')

    @shot("that's when i figured it out", 'day', I['library'] + Vector((-3.5, -6.0, 5.6)), (0.05, 1, 0.18), 12, 7.5, 35)
    def s23(f0, f1):
        pos = I['library'] + Vector((-3.5, -7.4, 0)); stand(M, f0, f1, pos, 180, 'shock', P(rs=(-20, 0, 0), ls=(-20, 0, 0)), amp=0.5)
        bulb.location = pos + Vector((0, 0, 7.8)); bulb.keyframe_insert('location', frame=f0); show(bulb, f0 + 6, f1)
        bulb.scale = (0.01, 0.01, 0.01); bulb.keyframe_insert('scale', frame=f0 + 6); bulb.scale = (1, 1, 1); bulb.keyframe_insert('scale', frame=f0 + 14)

    @shot("the well doesn't listen", 'night', (125, 76, -8), (0.35, 0.45, 1), 24, 16, 32)
    def s24(f0, f1):
        water(f0, 0, 0)

    @shot("it listens to the loudest", 'night', (125, 76, -6.0), (0, -0.35, 1), 12, 7, 35)
    def s25(f0, f1):
        hrt.location = W + Vector((0, 0, -6.0)); hrt.keyframe_insert('location', frame=f0); hrt.keyframe_insert('location', frame=f1 - 1); show(hrt, f0, f1)
        for k, f in enumerate(range(f0, f1, 9)):
            s = 1.8 + 0.25 * (k % 2); hrt.scale = (s, s, s); hrt.keyframe_insert('scale', frame=f)
        water(f0, 0.6, 600, (1.0, 0.3, 0.35))

    @shot("and i was terrified", 'night', I['library'] + Vector((-3.5, -6.4, 5.4)), (0.1, 1, 0.12), 8.5, 5.0, 40)
    def s26(f0, f1):
        pos = I['library'] + Vector((-3.5, -6.4, 0.85)); M.place(f0, pos, 180); M.place(f1 - 1, pos, 180); M.face(f0, 'worried')
        idle(M, f0, f1, sit_pose(rs=(-75, 0, 10), ls=(-75, 0, -10), neck=(6, 0, 0)), 0.5)

    @shot("so on her birthday", 'day', (-12, 10.5, 4.5), (0.12, -1, 0.15), 14, 25, 32)
    def s27(f0, f1):
        walk(M, f0, f1, (-17, 10.5, 0.5), (-7, 10.5, 0.5), 'happy', speed_div=11)
        walk(T, f0, f1, (-19.5, 11.5, 0.5), (-9.5, 11.5, 0.5), 'neutral', speed_div=11)
        balloon.parent = M.ls; balloon.location = (0, -0.4, 4.0); show(balloon, f0, f1)
        C['woman2'].place(f0, (-1, 16, 0.0), 120); stand(C['woman2'], f0, f1, (-1, 16, 0.0), 120, 'smile')

    @shot("pancakes", 'day', I['diner'] + Vector((-1.4, 7.6, 4.9)), (0.55, -1, 0.35), 12, 9, 35)
    def s28(f0, f1):
        tp = I['diner'] + Vector((-1.4, 7.6, 0.9)); mp = I['diner'] + Vector((1.4, 0.4, 0.9))
        T.place(f0, tp, 0); T.place(f1 - 1, tp, 0); T.face(f0, 'smile'); idle(T, f0, f1, sit_pose(rs=(-70, 0, 10), ls=(-70, 0, -10)))
        M.place(f0, mp, 180); M.place(f1 - 1, mp, 180); M.face(f0, 'happy'); idle(M, f0, f1, sit_pose(rs=(-70, 0, 10), ls=(-70, 0, -10)))

    @shot("the arcade", 'day', I['arcade'] + Vector((0, 6.6, 4.2)), (-0.25, -1, 0.15), 12, 17, 32)
    def s29(f0, f1):
        tp = I['arcade'] + Vector((-2.5, 6.6, 0)); mp = I['arcade'] + Vector((2.5, 6.6, 0))
        T.place(f0, tp, 180); T.place(f1 - 1, tp, 180); T.face(f0, 'laugh'); M.place(f0, mp, 180); M.place(f1 - 1, mp, 180); M.face(f0, 'happy')
        for k, f in enumerate(range(f0, f1, 5)):
            kp(T, f, P(rs=(-55 - 8 * (k % 2), 0, 8), ls=(-55 + 8 * (k % 2), 0, -8)))
            kp(M, f, P(rs=(-55 + 8 * (k % 2), 0, 8), ls=(-55 - 8 * (k % 2), 0, -8), neck=(0, 0, -25)))

    ROOF = 16.9
    @shot("and stars on the library", 'night', (33, 27, 17.5), (0.05, -0.3, 1), 8, 19, 32)
    def s30(f0, f1):
        for c, x, face in ((M, 31.6, 'happy'), (T, 34.4, 'smile')):
            pos = (x, 23.8, ROOF + 0.5); c.place(f0, pos, 0, -90); c.place(f1 - 1, pos, 0, -90); c.face(f0, face)
            idle(c, f0, f1, P(rs=(0, 10, 0), ls=(0, -10, 0), neck=(0, 0, 10 if c is M else -10)), 0.3)

    @shot("i told her dumb jokes", 'night', (33, 25, ROOF + 2.6), (0.15, -1, 0.12), 13, 8.5, 35)
    def s31(f0, f1):
        mp = (31.5, 25, ROOF - 1.5); tp = (34.5, 25, ROOF - 1.5)
        M.place(f0, mp, -15); M.place(f1 - 1, mp, -15); M.face(f0, 'laugh')
        for k, f in enumerate(range(f0, f1, 10)): kp(M, f, sit_pose(rs=(-60 - 30 * (k % 2), 0, 0), ls=(-20, 0, 0), neck=(0, 0, -20)))
        kp(M, f1 - 1, sit_pose(rs=(-60, 0, 0), neck=(0, 0, -20)))
        T.place(f0, tp, 15); T.place(f1 - 1, tp, 15); T.face(f0, 'smile'); T.face(f0 + (f1 - f0) // 2, 'laugh')
        seq(T, [(f0, sit_pose(rs=(-30, 0, 0), ls=(-30, 0, 0), neck=(0, 0, 15))), (f0 + (f1 - f0) // 2, sit_pose(rs=(-120, 0, 30), ls=(-30, 0, 0), neck=(-12, 0, 10), torso=(-8, 0, 0))),
                (f1 - 1, sit_pose(rs=(-110, 0, 30), ls=(-40, 0, 0), neck=(-15, 0, 10), torso=(-10, 0, 0)))])

    @shot("at eleven fifty nine", 'night', (125, 25, 25), (0, -1, 0), 26, 14, 40)
    def s32(f0, f1):
        h = CT['minhand']; h.rotation_euler = (0, math.radians(-6), 0); h.keyframe_insert('rotation_euler', frame=f0)
        h.keyframe_insert('rotation_euler', frame=f1 - 6); h.rotation_euler = (0, math.radians(-3), 0); h.keyframe_insert('rotation_euler', frame=f1 - 3)
        h.rotation_euler = (0, math.radians(-6), 0); h.keyframe_insert('rotation_euler', frame=f1 + 1)

    CROWD = ['kid', 'lila', 'woman', 'man', 'man2', 'woman2', 'boy2', 'boy3', 'girl2']
    @shot("she walked down the steps", 'night', (125, 74, -3), (0, -0.7, 1), 30, 24, 30)
    def s33(f0, f1):
        path_walk(T, f0, f1, [step_pos(i) for i in range(2, 14)], 'neutral', look=(10, 0, 0))
        crowd(f0, f1, CROWD + ['milo'], 'worried')

    @shot("and closed her eyes", 'night', BOTTOM(240) + Vector((0, 0, 5.1)), (0.5, 0.866, 0.1), 7, 4.2, 40)
    def s34(f0, f1):
        pos = BOTTOM(240); stand(T, f0, f1, pos, facing(pos, W), 'closed', P(rs=(-15, 0, 0), ls=(-15, 0, 0)), amp=0.3)
        water(f0, 0, 0)

    @shot("the water didn't glow", 'night', (125, 76, -9.5), (0.05, -0.2, 1), 12, 9, 30)
    def s35(f0, f1):
        pos = BOTTOM(240); stand(T, f0, f1, pos, facing(pos, W), 'closed', amp=0.2)

    @shot("it just sat there", 'night', (125, 76, -8), (0.35, 0.45, 1), 14, 26, 30)
    def s36(f0, f1):
        pos = BOTTOM(240); stand(T, f0, f1, pos, facing(pos, W), 'sad', amp=0.2)
        crowd(f0, f1, CROWD + ['milo'], 'worried')

    @shot("the town gasped", 'night', (125, 76 + 9.6, 4), (0, -1, 0.0), 26, 18, 35)
    def s37(f0, f1):
        crowd(f0, f1, CROWD + ['milo'], 'shock', P(rs=(-50, 0, 15), ls=(-50, 0, -15)))

    @shot("someone whispered", 'night', (125 + math.cos(math.radians(57)) * 9.6, 76 + math.sin(math.radians(57)) * 9.6, 4.9), (-0.5, -0.86, 0.1), 7, 4.5, 40)
    def s38(f0, f1):
        crowd(f0, f1, CROWD + ['milo'], ['worried', 'worried', 'whisper', 'worried', 'sad'], P(rs=(-20, 0, 0)))
        c = C['woman']; c.face(f0, 'whisper')

    @shot("tess walked home alone", 'night', (-14, 10.5, 3.5), (0.3, -1, 0.15), 14, 26, 32)
    def s39(f0, f1):
        walk(T, f0, f1, (-8, 10.5, 0.5), (-20, 10.5, 0.5), 'sad', speed_div=13, arms=14, legs=20, extra=dict(neck=(18, 0, 0)))

    @shot("back at the library", 'night', I['library'] + Vector((-1.5, -6.5, 5.0)), (0.1, 1, 0.3), 12, 7.5, 32)
    def s40(f0, f1):
        pos = I['library'] + Vector((-1.6, -6.6, 0)); M.place(f0, pos, 180); M.place(f1 - 1, pos, 180); M.face(f0, 'neutral')
        for k, f in enumerate(range(f0, f1, 10)): kp(M, f, P(rs=(-60 - 20 * (k % 2), 0, 15), ls=(-50 + 15 * (k % 2), 0, -15), neck=(20, 0, 0)))
        kp(M, f1 - 1, P(rs=(-70, 0, 10), ls=(-70, 0, -10), neck=(10, 0, 0)))

    @shot("when the water stays still", 'night', I['library'] + Vector((-1.6, -6.6, 5.0)), (0.08, 1, 0.08), 7.5, 4.5, 40)
    def s41(f0, f1):
        pos = I['library'] + Vector((-1.6, -6.6, 0)); stand(M, f0, f1, pos, 180, 'shock', P(rs=(-70, 0, 12), ls=(-70, 0, -12), neck=(12, 0, 0)), amp=0.3)
        paper.parent = M.rs; paper.location = (0.55, -0.4, -1.75); paper.rotation_euler = (math.radians(-20), 0, 0); show(paper, f0, f1)

    @shot("one week later", 'night', (125, 76 - 9.4, 4.4), (0, -1, 0.15), 16, 10, 35)
    def s42(f0, f1):
        stand(M, f0, f1, (125, 76 - 9.4, 0.02), 180, 'neutral', amp=0.4)
        crowd(f0, f1, CROWD + ['tess'], 'neutral')

    @shot("smartest person alive", 'night', (125, 76, -2.5), (0, -0.7, 1), 26, 20, 30)
    def s43(f0, f1):
        path_walk(M, f0, f1, [step_pos(i) for i in range(0, 8)], 'smirk')
        crowd(f0, f1, CROWD + ['tess'], 'neutral')

    @shot("i'd practiced it", 'night', BOTTOM(240) + Vector((0, 0, 5.1)), (0.5, 0.866, 0.15), 5.0, 8.5, 38)
    def s44(f0, f1):
        pos = BOTTOM(240); stand(M, f0, f1, pos, facing(pos, W), 'whisper', P(rs=(-25, 0, 0), ls=(-25, 0, 0)), amp=0.6)
        for k, f in enumerate(range(f0, f1, 8)): M.face(f, 'whisper' if k % 2 == 0 else 'smirk')

    @shot("but when i closed my eyes", 'night', BOTTOM(240) + Vector((0, 0, 5.1)), (0.5, 0.866, 0.08), 6.5, 3.6, 42)
    def s45(f0, f1):
        pos = BOTTOM(240); stand(M, f0, f1, pos, facing(pos, W), 'closed', P(rs=(-12, 0, 0), ls=(-12, 0, 0)), amp=0.2)

    @shot("the only thing in my heart", 'night', (-14, 10.5, 3.8), (-0.2, -1, 0.3), 26, 18, 32)
    def s46(f0, f1):
        walk(T, f0, f1, (-6, 10.5, 0.5), (-19, 10.5, 0.5), 'cry', speed_div=13, arms=12, legs=18, extra=dict(neck=(20, 0, 0)))

    @shot("the water lit up", 'night', (125, 76, -8), (0.35, 0.45, 1), 12, 30, 30)
    def s47(f0, f1):
        water(f0, 0, 0); water(f0 + 8, 40, 30000); water(f1, 40, 30000)
        pos = BOTTOM(240); stand(M, f0, f1, pos, facing(pos, W), 'closed', amp=0.2)
        crowd(f0, f1, CROWD + ['tess'], 'shock')

    @shot("the whole town had to look away", 'night', (125, 76 + 9.6, 4.2), (0, -1, 0.05), 18, 26, 32)
    def s48(f0, f1):
        water(f0, 40, 30000); water(f1, 0, 0)
        crowd(f0, f1, CROWD + ['tess'], 'closed', P(rs=(-145, 0, 30), ls=(-145, 0, -30), neck=(-10, 0, 0), torso=(-6, 0, 0)))

    @shot("the next morning", 'morning', I['bedroom'] + Vector((2, 2, 5.0)), (0, -1, 0.1), 12, 7.5, 35)
    def s49(f0, f1):
        stand(M, f0, f1, I['bedroom'] + Vector((2, 2, 0)), 0, 'neutral', P(rs=(-165, 0, 35)), amp=0.6)
        for k, f in enumerate(range(f0, f1, 6)): kp(M, f, P(rs=(-160 - 8 * (k % 2), 0, 35), neck=(0, 0, 8 * (k % 2))))

    @shot("but there was a beat up car", 'morning', (-43.5, 24, 3), (0.25, -1, 0.15), 24, 15, 35)
    def s50(f0, f1):
        car_at(f0, -43.5, 25, 180); car_at(f1 - 1, -43.5, 25, 180)

    @shot("and a man on her porch", 'morning', (-28, 16.2, 4.4), (0.1, -1, 0.1), 14, 8, 35)
    def s51(f0, f1):
        d = C['dad']; pos = (-28, 16.2, 0.6); stand(d, f0, f1, pos, 0, 'sad', P(rs=(-45, 0, 25), ls=(-45, 0, -25), neck=(14, 0, 0)), amp=0.3)
        hat.parent = d.rs; hat.location = (0.5, -0.25, -1.9); hat.rotation_euler = (math.radians(70), 0, 0); show(hat, f0, f1); [show(o, f0, f1) for o in hat.children]
        car_at(f0, -43.5, 25, 180); car_at(f1 - 1, -43.5, 25, 180)

    @shot("tess was crying", 'morning', (-28, 15.0, 4.8), (0.35, -1, 0.1), 9, 5.5, 38)
    def s52(f0, f1):
        d = C['dad']; dp = (-28, 16.4, 0.6); tp = (-28, 14.4, 0.6)
        stand(d, f0, f1, dp, 180, 'cry', P(rs=(-80, 0, 30), ls=(-80, 0, -30), neck=(10, 0, 0)), amp=0.3)
        stand(T, f0, f1, tp, 0, 'cry', P(rs=(-85, 0, 25), ls=(-85, 0, -25), neck=(-8, 0, 0)), amp=0.3)

    SIT_M = (31.5, 23.8, ROOF - 1.5); SIT_T = (34.5, 23.8, ROOF - 1.5)
    @shot("that night on the roof", 'night', (33, 23.8, ROOF + 2.4), (0, -1, 0.18), 10, 20, 32)
    def s53(f0, f1):
        M.place(f0, SIT_M, 0); M.place(f1 - 1, SIT_M, 0); M.face(f0, 'neutral'); idle(M, f0, f1, sit_pose(rs=(-30, 0, 0), ls=(-30, 0, 0)), 0.4, look=-25)
        T.place(f0, SIT_T, 0); T.place(f1 - 1, SIT_T, 0); T.face(f0, 'neutral'); idle(T, f0, f1, sit_pose(rs=(-30, 0, 0), ls=(-30, 0, 0)), 0.3, look=-5)

    @shot("somebody who'd never leave", 'night', Vector(SIT_T) + Vector((0, 0, 4.65)), (-0.2, -1, 0.05), 6.5, 4.2, 40)
    def s54(f0, f1):
        T.place(f0, SIT_T, 0); T.place(f1 - 1, SIT_T, 0); T.face(f0, 'closed_sad'); idle(T, f0, f1, sit_pose(rs=(-30, 0, 0), ls=(-30, 0, 0), neck=(12, 0, 0)), 0.3)
        M.place(f0, SIT_M, 0); M.place(f1 - 1, SIT_M, 0); M.face(f0, 'neutral'); idle(M, f0, f1, sit_pose(rs=(-30, 0, 0), ls=(-30, 0, 0)), 0.3, look=-25)

    @shot("turns out i already had one", 'night', (33, 23.8, ROOF + 3.1), (0, -1, 0.06), 10, 7, 38)
    def s55(f0, f1):
        T.place(f0, SIT_T, 0); T.place(f1 - 1, SIT_T, 0); T.face(f0, 'happy'); idle(T, f0, f1, sit_pose(rs=(-30, 0, 0), ls=(-30, 0, 0)), 0.3, look=28)
        M.place(f0, SIT_M, 0); M.place(f1 - 1, SIT_M, 0); M.face(f0, 'shock'); M.face(f0 + 14, 'smile'); idle(M, f0, f1, sit_pose(rs=(-30, 0, 0), ls=(-30, 0, 0)), 0.3, look=-28)

    @shot("i gave up being", 'night', Vector(SIT_M) + Vector((0, 0, 4.65)), (0.2, -1, 0.05), 4.2, 7.5, 40)
    def s56(f0, f1):
        M.place(f0, SIT_M, 0); M.place(f1 - 1, SIT_M, 0); M.face(f0, 'happy'); idle(M, f0, f1, sit_pose(rs=(-30, 0, 0), ls=(-30, 0, 0)), 0.4, look=12)
        T.place(f0, SIT_T, 0); T.place(f1 - 1, SIT_T, 0); T.face(f0, 'smile'); idle(T, f0, f1, sit_pose(rs=(-30, 0, 0), ls=(-30, 0, 0)), 0.3, look=-12)

    @shot("best trade i ever made", 'night', (33, 23.8, ROOF + 3), (0, -1, 0.3), 12, 34, 30)
    def s57(f0, f1):
        M.place(f0, SIT_M, 0); M.place(f1 - 1, SIT_M, 0); M.face(f0, 'happy'); idle(M, f0, f1, sit_pose(rs=(-30, 0, 0), ls=(-30, 0, 0)), 0.4)
        T.place(f0, SIT_T, 0); T.place(f1 - 1, SIT_T, 0); T.face(f0, 'happy'); idle(T, f0, f1, sit_pose(rs=(0, 0, 0), ls=(-30, 0, 0)), 0.3)

    # ---------------- resolve timing + key everything ----------------
    starts = []
    for i, s in enumerate(SHOTS):
        t = 0.0 if i == 0 else at(s['anchor']) - 0.12
        starts.append(int(round(t * FPS)))
    starts.append(LAST_F)
    cd = bpy.data.cameras.new('cam'); cd.sensor_fit = 'VERTICAL'; cd.sensor_height = 24; cd.clip_start = 0.1; cd.clip_end = 3000
    cam = link(bpy.data.objects.new('cam', cd)); sc.camera = cam
    info = []
    for i, s in enumerate(SHOTS):
        f0, f1 = starts[i], starts[i + 1]
        for c in C.values(): c.park(f0); c.park(f1 - 1); c.face(f0, 'smile')
        world.key_light(f0, s['light'])
        water(f0, 0, 0)
        car_at(f0, -60, -300, 0); car_at(f1 - 1, -60, -300, 0)   # car parked off-screen unless a shot uses it
        s['fn'](f0, f1)
        tg, dr = s['target'], s['dir']
        for f, d in ((f0, s['d0']), (f1 - 1, s['d1'])):
            cam.location = tg + dr * d
            cam.rotation_euler = (-dr).to_track_quat('-Z', 'Y').to_euler()
            cam.keyframe_insert('location', frame=f); cam.keyframe_insert('rotation_euler', frame=f)
        cd.lens = s['lens']; cd.keyframe_insert('lens', frame=f0)
        info.append(dict(i=i + 1, name=s['fn'].__name__, anchor=s['anchor'], f0=f0, f1=f1, secs=round((f1 - f0) / FPS, 2)))
    json.dump(info, open(OUT + 'shots.json', 'w'), indent=1)
    for x in info: print(f"{x['i']:2d} {x['f0']:5d}-{x['f1']:5d} {x['secs']:5.2f}s  {x['anchor']}")

    # interpolation: camera + roots linear, joints eased per segment, switches constant
    roots = {c.root.name for c in C.values()} | {'cam', 'dadcar', 'trashcan', 'money', 'bulb', 'heart', 'balloon'}
    def fix(ad, name):
        if not ad or not ad.action: return
        for fc in ad.action.fcurves:
            for k in fc.keyframe_points:
                if fc.data_path in ('hide_render', 'hide_viewport', 'lens') or 'energy' in fc.data_path or 'color' in fc.data_path or 'default_value' in fc.data_path \
                        or (name == 'Sun') or fc.data_path.startswith('nodes'):
                    k.interpolation = 'CONSTANT'
                elif name in roots: k.interpolation = 'LINEAR'
                else: k.interpolation = 'SINE'; k.easing = 'EASE_IN_OUT'
    for o in bpy.data.objects:
        fix(o.animation_data, o.name)
        if o.data is not None and hasattr(o.data, 'animation_data'): fix(o.data.animation_data, o.name)
    for m in bpy.data.materials:
        if m.node_tree: fix(m.node_tree.animation_data, m.name)
    if sc.world.node_tree: fix(sc.world.node_tree.animation_data, 'world')
    # face-swaps and the min-hand tick should snap
    render_settings(sc)
    sc.frame_start = 0; sc.frame_end = LAST_F - 1
    bpy.ops.wm.save_as_mainfile(filepath=OUT + 'wish.blend')
    print('BUILD_OK frames', LAST_F)


def render_settings(sc, preview=False):
    sc.render.engine = 'BLENDER_EEVEE'; ee = sc.eevee
    ee.taa_render_samples = 4 if preview else 6
    ee.use_gtao = True; ee.gtao_distance = 2.0; ee.gtao_factor = 1.2
    ee.use_soft_shadows = True; ee.shadow_cascade_size = '1024'; ee.shadow_cube_size = '512'
    ee.use_bloom = True; ee.bloom_threshold = 1.0; ee.bloom_intensity = 0.06; ee.bloom_radius = 5
    ee.use_ssr = False
    sc.view_settings.view_transform = 'Standard'
    try: sc.view_settings.look = 'Medium Contrast'
    except Exception: pass
    sc.render.resolution_x = 360 if preview else 720; sc.render.resolution_y = 640 if preview else 1280; sc.render.resolution_percentage = 100
    sc.render.fps = FPS
    sc.render.image_settings.file_format = 'JPEG' if preview else 'PNG'; sc.render.image_settings.quality = 85
    sc.render.film_transparent = False


def render(a, b, preview=False):
    sc = bpy.context.scene; render_settings(sc, preview)
    os.makedirs(OUT + ('preview/' if preview else 'frames/'), exist_ok=True)
    frames = json.load(open(OUT + 'shots.json')) if preview and a < 0 else None
    if frames:
        for x in frames:
            for tag, f in (('a', x['f0'] + 2), ('b', (x['f0'] + x['f1']) // 2), ('c', x['f1'] - 2)):
                if b >= 0 and tag != 'b': continue
                sc.frame_set(f); sc.render.filepath = OUT + f"preview/s{x['i']:02d}{tag}.jpg"; bpy.ops.render.render(write_still=True)
        return
    import time
    for f in range(a, b):
        p = OUT + f'frames/f_{f:05d}.png'
        if os.path.exists(p): continue
        t = time.time(); sc.frame_set(f); sc.render.filepath = p; bpy.ops.render.render(write_still=True)
        print(f'FRAME {f} {time.time() - t:.2f}s', flush=True)


if argv[0] == 'build': build()
elif argv[0] == 'render': render(int(argv[1]), int(argv[2]), len(argv) > 3 and argv[3] == 'preview')
