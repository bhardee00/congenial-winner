"""'The Voice' — 9:16 Roblox R15 animation synced to the user's voiceover (word timings in work/wish/words.json).
No captions, no music, no audio in the output.
  blender -b -P story.py -- build              -> work/wish/wish.blend
  blender -b work/wish/wish.blend -P story.py -- render START END [preview]
"""
import bpy, sys, os, math, json, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mathutils import Vector
from lib import *

FPS = 30
OUT = WK + 'voice/'
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
    world.RIVER = True
    world.build_all()
    import voice_world; voice_world.build_extras()
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
    import voice_world as VW
    VV = VW.V
    E, N_ = C['milo'], C['nora']
    HH = 4.47                                     # head-centre height above the feet (R15 Roblox Boy, scale 1.0)
    SIT = 0.385 - 1.971                           # root z offset for sitting on a surface (thigh half-depth - hip height)
    SPOT = VW.SQ + Vector((0, -9, 0.3))           # where you stand at midnight in the square
    WR = VV['whisper']
    def rings(f0, f1, headpos, strength=1.0):
        show(WR, f0, f1); [show(o, f0, f1) for o in WR.children]
        WR.location = headpos; WR.keyframe_insert('location', frame=f0); WR.keyframe_insert('location', frame=f1 - 1)
        for k, f in enumerate(range(f0, f1, 10)):
            s = (0.85 + 0.35 * (k % 2)) * strength; WR.scale = (s, s, s); WR.rotation_euler = (0, 0, k * 0.4)
            WR.keyframe_insert('scale', frame=f); WR.keyframe_insert('rotation_euler', frame=f)
    def sq_crowd(f0, f1, names, faces, p=None, r=7.5, a0=20, a1=160, center=None):
        cen = center or SPOT
        for i, n in enumerate(names):
            a = math.radians(a0 + (a1 - a0) * i / max(1, len(names) - 1)); pos = (cen.x + math.cos(a) * r, cen.y + math.sin(a) * r, 0.3)
            stand(C[n], f0, f1, pos, facing(pos, cen), faces[i % len(faces)] if isinstance(faces, list) else faces, p)
    CROWD = ['kid', 'lila', 'woman', 'man', 'man2', 'woman2', 'boy2', 'boy3', 'girl2', 'teacher']
    for o in VV['note']: prop(o)
    for k in ('splash', 'phone', 'helmet', 'veil', 'bouquet', 'float', 'fire', 'truck'):
        prop(VV[k]); [prop(o) for o in VV[k].children]
    prop(WR); [prop(o) for o in WR.children]; prop(VV['firelight'])
    for o in VV['truck'].children: [prop(x) for x in o.children]
    def key_obj(o, f, loc=None, rot=None):
        if loc is not None: o.location = loc; o.keyframe_insert('location', frame=f)
        if rot is not None: o.rotation_euler = [math.radians(a) for a in rot]; o.keyframe_insert('rotation_euler', frame=f)
    BUS0 = Vector((VV['busstop'].x + 2, VW.RIV_Y1 + 20.5, 0))
    def bus_at(f, x): key_obj(VV['bus'], f, (x, BUS0.y, 0))
    def train_at(f, x): key_obj(VV['train'], f, (x, VW.TRACKS.y, 0))
    SNAP0 = VV['snap'].location.copy()
    def rail(f, broken=0.0):
        key_obj(VV['snap'], f, SNAP0 + Vector((1.8 * broken, 0, -6.5 * broken)), (0, 75 * broken, -15 * broken))
    UW = VW.INT['underwater']; UWL = VV['uw_light']
    def uw(f, e): UWL.data.energy = e; UWL.data.keyframe_insert('energy', frame=f)
    DECK = 1.98; BANK = (18, 160.8, 0.0)

    @shot("in this world", 'day', SPOT + Vector((0, 0, HH)), (0, -1, 0.12), 2.4, 30, 35)
    def v01(f0, f1):
        stand(E, f0, f1, SPOT, 0, 'smile', amp=0.6)

    @shot("at midnight you close", 'night', SPOT + Vector((0, 0, 4)), (0, -1, 0.3), 32, 22, 32)
    def v02(f0, f1):
        stand(C['kid'], f0, f1, SPOT, 0, 'closed', amp=0.3); sq_crowd(f0, f1, CROWD, 'smile')

    @shot("and a voice that sounds", 'night', SPOT + Vector((0, 0, HH)), (0.1, -1, 0.08), 9, 5.5, 38)
    def v03(f0, f1):
        stand(C['kid'], f0, f1, SPOT, 0, 'closed', amp=0.2); rings(f0 + 6, f1, SPOT + Vector((0, 0, HH))); sq_crowd(f0, f1, CROWD, 'smile')

    @shot("it always comes true", 'night', SPOT + Vector((0, 2, 4)), (0, -1, 0.15), 15, 22, 32)
    def v04(f0, f1):
        stand(C['kid'], f0, f1, SPOT, 0, 'laugh', P(rs=(0, 150, 0), ls=(0, -150, 0)))
        sq_crowd(f0, f1, CROWD, ['happy', 'laugh'], P(rs=(-150, 0, 20), ls=(-150, 0, -20)))

    @shot("my cousin heard", 'night', SPOT + Vector((0, 0, HH)), (-0.1, -1, 0.1), 12, 6.5, 38)
    def v05(f0, f1):
        stand(C['cousin'], f0, f1, SPOT, 0, 'closed', amp=0.2); rings(f0, f1, SPOT + Vector((0, 0, HH))); sq_crowd(f0, f1, CROWD, 'smile')

    @shot("she's rich now", 'day', VW.CITY + Vector((-3, -3, HH + 0.3)), (0.15, -1, 0.12), 9, 30, 32)
    def v06(f0, f1):
        stand(C['cousin'], f0, f1, VW.CITY + Vector((-3, -3, 0.3)), -10, 'smirk', P(rs=(0, 30, 0), ls=(0, -30, 0)), amp=0.5)

    @shot("the boy next door heard", 'night', SPOT + Vector((0, 0, HH)), (0.1, -1, 0.1), 12, 6.5, 38)
    def v07(f0, f1):
        stand(C['boynext'], f0, f1, SPOT, 0, 'closed', amp=0.2); rings(f0, f1, SPOT + Vector((0, 0, HH))); sq_crowd(f0, f1, CROWD, 'smile')

    @shot("he's married", 'day', VW.WED + Vector((0, -2, 4.2)), (0, -1, 0.12), 10, 24, 32)
    def v08(f0, f1):
        g, b = C['groom'], C['bride']; gp = VW.WED + Vector((-1.3, -2, 0)); bp = VW.WED + Vector((1.3, -2, 0))
        stand(g, f0, f1, gp, -15, 'happy', P(ls=(-30, 0, -20)), amp=0.4); stand(b, f0, f1, bp, 15, 'happy', P(rs=(-50, 0, 25)), amp=0.4)
        show(VV['veil'], f0, f1); key_obj(VV['veil'], f0, bp + Vector((0, 0.35, HH + 0.35))); key_obj(VV['veil'], f1 - 1, bp + Vector((0, 0.35, HH + 0.35)))
        show(VV['bouquet'], f0, f1); [show(o, f0, f1) for o in VV['bouquet'].children]
        key_obj(VV['bouquet'], f0, bp + Vector((0.6, -1.0, 2.2))); key_obj(VV['bouquet'], f1 - 1, bp + Vector((0.6, -1.0, 2.2)))
        stand(C['kid'], f0, f1, VW.WED + Vector((-7, -9, 0)), -20, 'happy'); stand(C['lila'], f0, f1, VW.WED + Vector((7.5, -9, 0)), 20, 'happy')

    @shot("my name is eli", 'day', (-65, 16.5, 4.4), (0, -1, 0.12), 16, 10, 35)
    def v09(f0, f1):
        E.place(f0, (-65, 16.5, 0.6), 0); E.place(f1 - 1, (-65, 16.5, 0.6), 0); E.face(f0, 'happy')
        for k, f in enumerate(range(f0, f1, 7)): kp(E, f, P(rs=(-165, 18 if k % 2 else -12, 0), neck=(0, 0, 4 * (k % 2))))
        kp(E, f1 - 1, P(rs=(-165, 0, 0)))

    @shot("my best friend is nora", 'day', (-29.3, 10.5, 4.4), (0, -1, 0.1), 17, 11, 35)
    def v10(f0, f1):
        stand(N_, f0, f1, (-31.2, 10.5, 0.5), 15, 'laugh', P(rs=(-20, 0, 0)), amp=0.6, look=15)
        stand(E, f0, f1, (-27.4, 10.5, 0.5), -15, 'laugh', P(ls=(-20, 0, 0)), amp=0.6, look=-15)

    @shot("and on her thirteenth birthday", 'night', SPOT + Vector((0, 0, 4)), (0, -1, 0.3), 30, 21, 32)
    def v11(f0, f1):
        stand(N_, f0, f1, SPOT, 0, 'smile', amp=0.3); sq_crowd(f0, f1, CROWD + ['milo'], 'smile')

    @shot("she closed her eyes and heard", 'night', SPOT + Vector((0, 0, HH)), (0, -1, 0.06), 9, 5, 40)
    def v12(f0, f1):
        stand(N_, f0, f1, SPOT, 0, 'closed', amp=0.15); sq_crowd(f0, f1, CROWD + ['milo'], 'neutral')

    @shot("the square went quiet", 'night', SPOT + Vector((0, 4, 4.2)), (0, -1, 0.12), 17, 12, 35)
    def v13(f0, f1):
        stand(N_, f0, f1, SPOT, 180, 'worried', amp=0.2); sq_crowd(f0, f1, CROWD + ['milo'], ['shock', 'worried'])

    @shot("then the whispers started", 'night', SPOT + Vector((1.4, 7.2, HH + 0.3)), (0, -1, 0.1), 7, 5, 32)
    def v14(f0, f1):
        names = CROWD + ['milo']; sq_crowd(f0, f1, names, 'worried')
        w, m = C['woman'], C['man']; pw = SPOT + Vector((0.2, 7.3, 0.3)); pm = SPOT + Vector((2.6, 7.3, 0.3))
        stand(w, f0, f1, pw, -25, 'whisper', P(rs=(-135, 0, 35), neck=(0, 0, 20)), amp=0.3)
        stand(m, f0, f1, pm, 25, 'worried', amp=0.3, look=-15)

    @shot("no voice means no future", 'night', SPOT + Vector((0, 0, 1.5)), (0, -0.55, 1), 16, 34, 30)
    def v15(f0, f1):
        stand(N_, f0, f1, SPOT, 0, 'sad', amp=0.2); sq_crowd(f0, f1, CROWD + ['milo'], 'worried', r=12)

    @shot("people stopped inviting", 'day', (-92, 10.5, HH + 0.5), (0.35, -1, 0.15), 15, 10, 35)
    def v16(f0, f1):
        show(cake_root, f0, f1); [show(o, f0, f1) for o in cake_root.children]
        stand(N_, f0, f1, (-92, 10.5, 0.5), 160, 'sad', amp=0.3)
        for n, (x, y, hd) in (('kid', (-97.5, 15.5, 30)), ('lila', (-92.5, 16.4, -30)), ('boy2', (-95, 17.4, 0)), ('girl2', (-99, 14, 60))):
            stand(C[n], f0, f1, (x, y, 0.6), hd, 'laugh', P(rs=(-120, 0, 0)))

    CL = VW.INT['classroom']; DESKS = VV['desks']
    def seat(c, f0, f1, i, face, p=None, amp=0.4):
        d = DESKS[i]; pos = (d.x, d.y, d.z + SIT); c.place(f0, pos, 180); c.place(f1 - 1, pos, 180); c.face(f0, face)
        idle(c, f0, f1, p if p else sit_pose(rs=(-60, 0, 10), ls=(-60, 0, -10)), amp)

    @shot("teachers stopped calling", 'day', CL + Vector((0, 3, 4.6)), (0.1, 1, 0.45), 9, 7, 24)
    def v17(f0, f1):
        seat(N_, f0, f1, 5, 'neutral', sit_pose(rs=(-170, 0, 0), ls=(-60, 0, -10)))
        for i, n in ((0, 'kid'), (2, 'boy2'), (6, 'girl2'), (9, 'boy3'), (3, 'lila')): seat(C[n], f0, f1, i, 'happy', sit_pose(rs=(-170, 0, 0), ls=(-60, 0, -10)) if i in (2, 9) else None)
        t = C['teacher']; tp = CL + Vector((-2, 9.5, 0)); stand(t, f0, f1, tp, 0, 'smile', P(rs=(-90, 0, -25)), amp=0.4, look=-25)

    @shot("and slowly nora stopped trying", 'day', DESKS[5] + Vector((0, 0, SIT + HH)), (0.15, 1, 0.12), 8, 5, 40)
    def v18(f0, f1):
        seat(N_, f0, f1, 5, 'sad', sit_pose(rs=(-75, 0, 25), ls=(-75, 0, -25), neck=(25, 0, 0)), 0.2)
        for i, n in ((0, 'kid'), (6, 'girl2'), (3, 'lila')): seat(C[n], f0, f1, i, 'happy')

    NR = VW.INT['nora_room']
    @shot("even she started believing", 'sunset', NR + Vector((2.0, 3, 2.7 + SIT + HH)), (-1, -0.25, 0.15), 6, 12, 35)
    def v19(f0, f1):
        pos = NR + Vector((2.0, 3, 2.7 + SIT)); N_.place(f0, pos, -90); N_.place(f1 - 1, pos, -90); N_.face(f0, 'closed_sad')
        idle(N_, f0, f1, sit_pose(rs=(-40, 0, 20), ls=(-40, 0, -20), neck=(20, 0, 0)), 0.2)

    @shot("so i did what i always do", 'day', (-12, 10.5, HH + 0.5), (0.1, -1, 0.08), 9, 6, 38)
    def v20(f0, f1):
        stand(E, f0, f1, (-12, 10.5, 0.5), 0, 'smirk', P(rs=(0, 25, 0), ls=(0, -25, 0)), amp=0.4)

    @shot("i went to the library", 'day', (35, 17, 7), (0, -1, 0.12), 36, 27, 32)
    def v21(f0, f1):
        walk(E, f0, f1, (33.5, 6, 0.5), (34.5, 15.5, 1.2), 'smile', speed_div=11)

    @shot("and read every record", 'day', I['library'] + Vector((-3.5, -5.6, 4.2)), (0.05, 1, 0.38), 8, 14, 32)
    def v22(f0, f1):
        pos = I['library'] + Vector((-3.5, -6.4, 2.35 + SIT)); E.place(f0, pos, 180); E.place(f1 - 1, pos, 180); E.face(f0, 'neutral')
        for k, f in enumerate(range(f0, f1, 9)): kp(E, f, sit_pose(rs=(-70 - 15 * (k % 2), 0, 10), ls=(-60, 0, -10), neck=(14, 0, 6 * (k % 2))))
        kp(E, f1 - 1, sit_pose(rs=(-70, 0, 10), ls=(-60, 0, -10), neck=(14, 0, 0)))

    @shot("silent kids were rare", 'day', I['library'] + Vector((-1.6, -6.6, 4.6)), (0.08, 1, 0.1), 8, 5, 40)
    def v23(f0, f1):
        pos = I['library'] + Vector((-1.6, -6.6, 0)); stand(E, f0, f1, pos, 180, 'neutral', P(rs=(-70, 0, 12), ls=(-70, 0, -12), neck=(12, 0, 0)), amp=0.3)
        paper.parent = E.rs; paper.location = (0.5, -0.4, -1.7); paper.rotation_euler = (math.radians(-20), 0, 0); show(paper, f0, f1)

    @shot("but every one of them", 'day', I['library'] + Vector((-3.5, -7.4, 5.2)), (0.05, 1, 0.18), 12, 7.5, 35)
    def v24(f0, f1):
        pos = I['library'] + Vector((-3.5, -7.4, 0)); stand(E, f0, f1, pos, 180, 'shock', P(rs=(-20, 0, 0), ls=(-20, 0, 0)), amp=0.5)
        bulb.location = pos + Vector((0, 0, 7.4)); bulb.keyframe_insert('location', frame=f0); show(bulb, f0 + 6, f1)
        bulb.scale = (0.01, 0.01, 0.01); bulb.keyframe_insert('scale', frame=f0 + 6); bulb.scale = (1, 1, 1); bulb.keyframe_insert('scale', frame=f0 + 14)

    @shot("a firefighter", 'day', VW.FIRE + Vector((0, 8, 5)), (0.15, 1, 0.15), 20, 15, 32)
    def v25(f0, f1):
        show(VV['fire'], f0, f1); [show(o, f0, f1) for o in VV['fire'].children]; show(VV['firelight'], f0, f1)
        show(VV['truck'], f0, f1); [show(o, f0, f1) for o in VV['truck'].children]
        fm = C['fireman']; a = VW.FIRE + Vector((0, 1.5, 0)); b = VW.FIRE + Vector((0, 8, 0))
        walk(fm, f0, f1, a, b, 'neutral', speed_div=11, arms=0, extra=dict(rs=(-80, 0, 15), ls=(-80, 0, -15)))
        kidc = C['boy3']
        for f, p in ((f0, a), (f1 - 1, b)):
            kidc.place(f, Vector(p) + Vector((2.4, 1.4, 3.0)), 90, -90, 0)
        kidc.face(f0, 'closed'); kidc.pose(f0); kidc.pose(f1 - 1)
        show(VV['helmet'], f0, f1); [show(o, f0, f1) for o in VV['helmet'].children]
        key_obj(VV['helmet'], f0, a + Vector((0, 0, HH + 0.75))); key_obj(VV['helmet'], f1 - 1, b + Vector((0, 0, HH + 0.75)))

    @shot("a lifeguard", 'day', VW.BEACH + Vector((0, -31, 3.5)), (0.15, 1, 0.2), 16, 12, 35)
    def v26(f0, f1):
        g = C['guard']; a = VW.BEACH + Vector((0, -36, -0.3)); b = VW.BEACH + Vector((0, -31, 0.1))
        walk(g, f0, f1, a, b, 'neutral', speed_div=12, arms=0, extra=dict(ls=(-20, 0, 0), rs=(160, 0, 0)))
        sw = C['girl2']
        for f, p in ((f0, a), (f1 - 1, b)): sw.place(f, Vector(p) + Vector((0.5, -1.5, 0.3)), 0, -90, 0)
        sw.face(f0, 'closed'); sw.pose(f0, rs=(-170, 0, 0)); sw.pose(f1 - 1, rs=(-170, 0, 0))
        show(VV['float'], f0, f1); key_obj(VV['float'], f0, Vector(a) + Vector((2.2, -1, 0.2))); key_obj(VV['float'], f1 - 1, Vector(b) + Vector((2.2, -1, 0.2)))

    @shot("a woman who pulled", 'sunset', VW.TRACKS + Vector((2, 4, 3.5)), (-0.3, 1, 0.12), 24, 17, 26)
    def v27(f0, f1):
        train_at(f0, VW.TRACKS.x - 30); train_at(f1 - 1, VW.TRACKS.x + 10)
        h = C['hero']; hp = VW.TRACKS + Vector((2, 6.6, 0.5)); m = C['man2']
        stand(h, f0, f1, hp, 160, 'worried', P(rs=(40, 0, 0), ls=(40, 0, 0), torso=(-8, 0, 0)), amp=0.4)
        m.place(f0, VW.TRACKS + Vector((2, -0.5, 1.2)), 180); m.place(f1 - 1, VW.TRACKS + Vector((2, 3.8, 0.8)), 180); m.face(f0, 'shock')
        seq(m, [(f0, P(rs=(-120, 0, 0), ls=(-120, 0, 0), torso=(15, 0, 0))), (f1 - 1, P(rs=(-110, 0, 0), ls=(-110, 0, 0), rh=(30, 0, 0), lh=(-30, 0, 0)))])

    @shot("their future selves", 'day', I['library'] + Vector((-3.5, -7.4, 4.6)), (0.05, 1, 0.1), 11, 7, 38)
    def v28(f0, f1):
        stand(E, f0, f1, I['library'] + Vector((-3.5, -7.4, 0)), 180, 'neutral', P(rs=(-30, 0, 0)), amp=0.4)

    @shot("they were too busy", 'day', I['library'] + Vector((-3.5, -7.4, 4.6)), (0.05, 1, 0.15), 7, 12, 35)
    def v29(f0, f1):
        stand(E, f0, f1, I['library'] + Vector((-3.5, -7.4, 0)), 180, 'happy', P(rs=(0, 40, 0), ls=(0, -40, 0)), amp=0.7)

    @shot("i couldn't wait to tell her", 'sunset', (35, 12, 4), (0, -1, 0.15), 14, 26, 32)
    def v30(f0, f1):
        walk(E, f0, f1, (34.5, 16.5, 1.2), (36, 6, 0.5), 'laugh', speed_div=7, arms=45, legs=45)

    @shot("then came my birthday", 'night', SPOT + Vector((0, 0, 4)), (0, -1, 0.3), 30, 21, 32)
    def v31(f0, f1):
        stand(E, f0, f1, SPOT, 0, 'smile', amp=0.3); sq_crowd(f0, f1, CROWD + ['nora'], 'smile')

    @shot("at midnight i closed", 'night', SPOT + Vector((0, 0, HH)), (0.1, -1, 0.06), 9, 5, 40)
    def v32(f0, f1):
        stand(E, f0, f1, SPOT, 0, 'closed', amp=0.15); sq_crowd(f0, f1, CROWD + ['nora'], 'smile')

    @shot("and my older voice", 'night', SPOT + Vector((0, 0, HH)), (-0.1, -1, 0.06), 7, 4.5, 40)
    def v33(f0, f1):
        stand(E, f0, f1, SPOT, 0, 'closed', amp=0.15); rings(f0, f1, SPOT + Vector((0, 0, HH)))

    @shot("don't cross the bridge", 'night', SPOT + Vector((0, 0, HH)), (0.05, -1, 0.04), 5, 3.4, 45)
    def v34(f0, f1):
        stand(E, f0, f1, SPOT, 0, 'closed', amp=0.1); E.face(f0 + (f1 - f0) * 2 // 3, 'shock'); rings(f0, f1 - 10, SPOT + Vector((0, 0, HH)), 1.2)

    @shot("on friday nora didn't", 'day', DESKS[4] + Vector((1.8, 0, SIT + HH - 0.3)), (0.15, 1, 0.45), 11, 8, 24)
    def v35(f0, f1):
        seat(E, f0, f1, 4, 'worried', sit_pose(rs=(-60, 0, 10), ls=(-60, 0, -10), neck=(0, 0, 50)), 0.2)
        for i, n in ((0, 'kid'), (6, 'girl2'), (3, 'lila'), (8, 'boy3')): seat(C[n], f0, f1, i, 'neutral')

    ER = VW.INT['eli_room']
    @shot("her mom called my house", 'day', ER + Vector((0, 2, HH)), (0.1, -1, 0.1), 7, 4.5, 40)
    def v36(f0, f1):
        pos = ER + Vector((0, 2, 0)); stand(E, f0, f1, pos, 0, 'worried', P(rs=(-150, 0, 40)), amp=0.3)
        ph = VV['phone']; show(ph, f0, f1); [show(o, f0, f1) for o in ph.children]
        key_obj(ph, f0, pos + Vector((-0.85, -0.1, HH)), (0, 0, 0)); key_obj(ph, f1 - 1, pos + Vector((-0.85, -0.1, HH)), (0, 0, 0))

    @shot("nora had left a note", 'day', VV['note_pos'], (0.05, -0.35, 1), 6, 3.2, 40)
    def v37(f0, f1):
        for o in VV['note']: show(o, f0, f1)
        stand(C['noramom'], f0, f1, NR + Vector((0.5, 0, 0)), -40, 'cry', P(rs=(-140, 0, 35), ls=(-140, 0, -35)), amp=0.3)

    BS = VV['busstop']
    @shot("she was waiting for the last bus", 'sunset', BS + Vector((0, 1.8, 3.6)), (0, -1, 0.15), 12, 26, 32)
    def v38(f0, f1):
        pos = BS + Vector((0, 1.8, 1.95 + SIT)); N_.place(f0, pos, 0); N_.place(f1 - 1, pos, 0); N_.face(f0, 'sad')
        idle(N_, f0, f1, sit_pose(rs=(-40, 0, 15), ls=(-40, 0, -15), neck=(15, 0, 0)), 0.2)

    @shot("the only way there", 'sunset', VW.BR + Vector((0, 0, 3)), (-0.65, -1, 0.35), 44, 32, 30)
    def v39(f0, f1):
        rail(f0, 0); rail(f1 - 1, 0)

    @shot("i didn't think twice", 'sunset', (VW.BR.x, VW.RIV_Y0 - 9, DECK + HH), (0.05, -1, 0.06), 7, 4.4, 40)
    def v40(f0, f1):
        stand(E, f0, f1, (VW.BR.x, VW.RIV_Y0 - 9, DECK), 0, 'angry', P(rs=(-10, 0, 0), ls=(-10, 0, 0)), amp=0.3)

    @shot("i ran anyway", 'sunset', (VW.BR.x, VW.RIV_Y0 - 2, 4), (0.15, -1, 0.15), 10, 22, 32)
    def v41(f0, f1):
        walk(E, f0, f1, (VW.BR.x, VW.RIV_Y0 - 12, DECK), (VW.BR.x + 1, VW.RIV_Y0 + 6, DECK), 'angry', speed_div=7, arms=50, legs=48)

    @shot("halfway across the railing", 'sunset', (VW.BR.x + 3, 180, 3.5), (1, -0.55, 0.3), 22, 15, 32)
    def v42(f0, f1):
        rail(f0, 0); km = f0 + (f1 - f0) // 3; rail(km, 0); rail(f1 - 1, 1.0)
        E.face(f0, 'shock'); E.place(f0, (VW.BR.x + 2.2, 179, DECK), 90); E.place(km, (VW.BR.x + 2.6, 179.5, DECK), 90)
        E.place(f1 - 1, (VW.BR.x + 5.5, 180.5, -1.5), 90, 0, 40)
        seq(E, [(f0, P(rs=(-60, 0, 0), ls=(-60, 0, 0))), (km, P(rs=(-80, 0, 0), ls=(-80, 0, 0), torso=(20, 0, 0))),
                (f1 - 1, P(rs=(-170, 0, 20), ls=(-170, 0, -20), rh=(-30, 0, 0), lh=(20, 0, 0)))])

    @shot("and i hit the freezing", 'sunset', (VW.BR.x + 6.5, 181, VW.WATER_Z + 1), (0.4, -1, 0.35), 14, 22, 32)
    def v43(f0, f1):
        rail(f0, 1.0); rail(f1 - 1, 1.0)
        sp = VV['splash']; show(sp, f0, f1); [show(o, f0, f1) for o in sp.children]
        sp.scale = (0.2, 0.2, 0.2); sp.keyframe_insert('scale', frame=f0); sp.scale = (1.3, 1.3, 1.6); sp.keyframe_insert('scale', frame=f0 + 10)
        sp.scale = (1.8, 1.8, 0.6); sp.keyframe_insert('scale', frame=f1 - 1)
        E.place(f0, (VW.BR.x + 6.0, 181, -0.5), 90, 0, 60); E.place(f0 + 6, (VW.BR.x + 6.5, 181, -6), 90, 0, 80); E.place(f1 - 1, (VW.BR.x + 6.5, 181, -8), 90, 0, 80)
        E.face(f0, 'shock'); E.pose(f0, rs=(-170, 0, 20), ls=(-170, 0, -20)); E.pose(f1 - 1, rs=(-170, 0, 20), ls=(-170, 0, -20))

    @shot("i couldn't find the surface", 'night', UW + Vector((0, 0, 14)), (0, -1, 0.1), 12, 20, 32)
    def v44(f0, f1):
        uw(f0, 30000)
        E.place(f0, UW + Vector((0, 0, 12)), 0, 15, 0); E.place(f1 - 1, UW + Vector((0, 0, 9.5)), 20, 25, 10); E.face(f0, 'shock')
        for k, f in enumerate(range(f0, f1, 10)):
            kp(E, f, P(rs=(-160 + 25 * (k % 2), 0, 20), ls=(-160 - 25 * (k % 2), 0, -20), rh=(20 * (1 - 2 * (k % 2)), 0, 0), lh=(-20 * (1 - 2 * (k % 2)), 0, 0)))
        kp(E, f1 - 1, P(rs=(-160, 0, 20), ls=(-160, 0, -20)))

    @shot("everything went dark", 'night', UW + Vector((0, 0, 13.5)), (0, -1, 0.05), 11, 6, 38)
    def v45(f0, f1):
        uw(f0, 26000); uw(f1 - 1, 0)
        E.place(f0, UW + Vector((0, 0, 9.4)), 20, 25, 10); E.place(f1 - 1, UW + Vector((0, 0, 8.5)), 25, 35, 12); E.face(f0, 'closed')
        seq(E, [(f0, P(rs=(-120, 0, 20), ls=(-120, 0, -20))), (f1 - 1, P(rs=(-40, 0, 20), ls=(-40, 0, -20), neck=(15, 0, 0)))])

    @shot("then a hand grabbed", 'night', UW + Vector((0, 0, 15)), (0.1, -1, 0.0), 14, 18, 32)
    def v46(f0, f1):
        uw(f0, 2500); uw(f0 + 10, 14000); uw(f1 - 1, 14000)
        ep = UW + Vector((0, 0, 8.5)); E.place(f0, ep, 25, 35, 12); E.place(f1 - 1, ep + Vector((0, 0, 1.2)), 25, 35, 12); E.face(f0, 'closed')
        E.pose(f0, rs=(-40, 0, 20), ls=(-40, 0, -20), neck=(15, 0, 0)); E.pose(f1 - 1, rs=(-60, 0, 20), ls=(-60, 0, -20))
        npos = ep + Vector((0.4, 0.4, 4.47 + 2.6 + 4.47 + 1.5))
        N_.place(f0, npos + Vector((0, 0, 4)), 0, 0, 180); N_.place(f0 + 14, npos, 0, 0, 180); N_.place(f1 - 1, npos + Vector((0, 0, 1.2)), 0, 0, 180)
        N_.face(f0, 'angry'); N_.pose(f0, rs=(-175, 0, 0), ls=(-175, 0, 0)); N_.pose(f1 - 1, rs=(-180, 0, 8), ls=(-180, 0, -8))

    @shot("and dragged me up the bank", 'sunset', (BANK[0], BANK[1] + 2.5, 2.5), (0.6, -1, 0.5), 14, 22, 32)
    def v47(f0, f1):
        a = Vector(BANK); N_.face(f0, 'angry')
        N_.place(f0, a + Vector((0, 1.5, 0)), 180); N_.place(f1 - 1, a + Vector((0, -2.0, 0)), 180)
        for k, f in enumerate(range(f0, f1, 10)): kp(N_, f, P(rs=(-60, 0, -10), ls=(-60, 0, 10), torso=(25, 0, 0), rh=(20 * (1 - 2 * (k % 2)), 0, 0), lh=(-20 * (1 - 2 * (k % 2)), 0, 0)))
        kp(N_, f1 - 1, P(rs=(-60, 0, -10), ls=(-60, 0, 10), torso=(25, 0, 0)))
        E.place(f0, a + Vector((0, 7.5, 0.0)), 180, -90, 0); E.place(f1 - 1, a + Vector((0, 4.0, 0.55)), 180, -90, 0); E.face(f0, 'closed')
        E.pose(f0, rs=(-10, 0, 0)); E.pose(f1 - 1, rs=(-10, 0, 0))

    @shot("it was nora soaking wet", 'sunset', Vector(BANK) + Vector((0, -2, SIT + HH)), (0.25, -1, 0.15), 7, 4.4, 40)
    def v48(f0, f1):
        pos = Vector(BANK) + Vector((0, -2, SIT)); N_.place(f0, pos, 0); N_.place(f1 - 1, pos, 0); N_.face(f0, 'worried')
        for k, f in enumerate(range(f0, f1, 2)): kp(N_, f, sit_pose(rs=(-40, 0, 25), ls=(-40, 0, -25), neck=(0, 0, 3 * (1 - 2 * (k % 2))), torso=(1.5 * (k % 2), 0, 0)))

    LIE = Vector(BANK) + Vector((-2.5, 2.0, 0.55))
    NP = LIE + Vector((-0.4, -2.6, SIT - 0.55))
    @shot("are you okay eli", 'sunset', LIE + Vector((-0.5, -1.4, 1.5)), (0.3, -0.6, 1), 15, 11, 30)
    def v49(f0, f1):
        E.place(f0, LIE, 90, -90, 0); E.place(f1 - 1, LIE, 90, -90, 0); E.face(f0, 'closed'); E.pose(f0); E.pose(f1 - 1)
        N_.place(f0, NP, 0); N_.place(f1 - 1, NP, 0); N_.face(f0, 'cry')
        for k, f in enumerate(range(f0, f1, 8)): kp(N_, f, sit_pose(rs=(-70, 0, 10 + 10 * (k % 2)), ls=(-70, 0, -10), torso=(30, 0, 0), neck=(25, 0, 0)))

    @shot("are you okay", 'sunset', NP + Vector((0, 0, HH)), (0.1, -1, 0.15), 5.5, 3.8, 42)
    def v50(f0, f1):
        N_.place(f0, NP, 0); N_.place(f1 - 1, NP, 0); N_.face(f0, 'cry')
        idle(N_, f0, f1, sit_pose(rs=(-70, 0, 10), ls=(-70, 0, -10), neck=(10, 0, 0)), 0.5)
        E.place(f0, LIE, 90, -90, 0); E.place(f1 - 1, LIE, 90, -90, 0); E.face(f0, 'closed'); E.pose(f0); E.pose(f1 - 1)

    @shot("and right then her eyes", 'sunset', NP + Vector((0, 0, HH)), (0.05, -1, 0.05), 6, 3.6, 45)
    def v51(f0, f1):
        N_.place(f0, NP, 0); N_.place(f1 - 1, NP, 0); N_.face(f0, 'worried'); N_.face(f0 + 18, 'shock')
        idle(N_, f0, f1, sit_pose(rs=(-40, 0, 10), ls=(-40, 0, -10)), 0.2)
        E.place(f0, LIE, 90, -90, 0); E.place(f1 - 1, LIE, 90, -90, 0); E.face(f0, 'closed'); E.pose(f0); E.pose(f1 - 1)

    @shot("for the first time in her life", 'sunset', NP + Vector((0, 0, HH)), (0.15, -1, 0.12), 5, 13, 35)
    def v52(f0, f1):
        N_.place(f0, NP, 0); N_.place(f1 - 1, NP, 0); N_.face(f0, 'shock'); idle(N_, f0, f1, sit_pose(rs=(-40, 0, 10), ls=(-40, 0, -10)), 0.2)
        rings(f0 + 8, f1, NP + Vector((0, 0, HH)))
        E.place(f0, LIE, 90, -90, 0); E.place(f1 - 1, LIE, 90, -90, 0); E.face(f0, 'closed'); E.pose(f0); E.pose(f1 - 1)

    @shot("older", 'sunset', NP + Vector((0, 0, HH)), (-0.1, -1, 0.06), 8, 4.4, 42)
    def v53(f0, f1):
        N_.place(f0, NP, 0); N_.place(f1 - 1, NP, 0); N_.face(f0, 'closed'); N_.face(f0 + (f1 - f0) * 2 // 3, 'laugh')
        idle(N_, f0, f1, sit_pose(rs=(-30, 0, 10), ls=(-30, 0, -10)), 0.3); rings(f0, f1, NP + Vector((0, 0, HH)), 1.15)
        E.place(f0, LIE, 90, -90, 0); E.place(f1 - 1, LIE, 90, -90, 0); E.face(f0, 'closed'); E.pose(f0); E.pose(f1 - 1)

    EP = LIE + Vector((0.6, 0, SIT - 0.55))
    @shot("told you", 'sunset', (NP + EP) / 2 + Vector((0, 0, 3.0)), (0.05, -1, 0.15), 10, 7, 38)
    def v54(f0, f1):
        N_.place(f0, NP, 0); N_.place(f1 - 1, NP, 0); N_.face(f0, 'laugh'); idle(N_, f0, f1, sit_pose(rs=(-120, 0, 30), ls=(-30, 0, 0), torso=(-8, 0, 0)), 0.6, look=-20)
        E.place(f0, EP, 0); E.place(f1 - 1, EP, 0); E.face(f0, 'shock'); E.face(f0 + 10, 'laugh'); idle(E, f0, f1, sit_pose(rs=(-20, 0, 0), ls=(-20, 0, 0)), 0.5, look=25)

    @shot("she never got on that bus", 'sunset', BS + Vector((6, 6, 4)), (-0.1, -1, 0.25), 26, 40, 30)
    def v55(f0, f1):
        bus_at(f0, BUS0.x - 8); bus_at(f1 - 1, BUS0.x + 22)

    @shot("she didn't need to run", 'sunset', (NP + EP) / 2 + Vector((0, 0, 4.0 - SIT)), (0.1, -1, 0.12), 13, 8, 35)
    def v56(f0, f1):
        a = Vector((NP.x + 0.4, NP.y, 0)); b = Vector((EP.x + 0.6, EP.y, 0))
        N_.place(f0, a, -60); N_.place(f1 - 1, a, -60); N_.face(f0, 'happy'); idle(N_, f0, f1, P(rs=(-80, 0, 25), ls=(-80, 0, -25)), 0.3)
        E.place(f0, b, 60); E.place(f1 - 1, b, 60); E.face(f0, 'closed'); idle(E, f0, f1, P(rs=(-80, 0, 25), ls=(-80, 0, -25)), 0.3)

    @shot("my future self told me", 'sunset', (VW.BR.x + 3.3, 181, 3.5), (1, -0.9, 0.35), 26, 16, 32)
    def v57(f0, f1):
        rail(f0, 1.0); rail(f1 - 1, 1.0)

    SITB = Vector((BANK[0] - 1.5, BANK[1] - 0.5, SIT)); SITB2 = SITB + Vector((3, 0, 0))
    @shot("i think he knew i would", 'sunset', SITB2 + Vector((0, 0, HH)), (0.1, 1, 0.08), 5, 9, 40)
    def v58(f0, f1):
        rail(f0, 1.0); rail(f1 - 1, 1.0)
        E.place(f0, SITB2, 180); E.place(f1 - 1, SITB2, 180); E.face(f0, 'smile'); idle(E, f0, f1, sit_pose(rs=(-20, 0, 0), ls=(-20, 0, 0)), 0.3, look=15)
        N_.place(f0, SITB, 180); N_.place(f1 - 1, SITB, 180); N_.face(f0, 'smile'); idle(N_, f0, f1, sit_pose(rs=(-20, 0, 0), ls=(-20, 0, 0)), 0.3)

    @shot("i think he knew exactly", 'sunset', (SITB + SITB2) / 2 + Vector((0, 0, 3)), (0, -1, 0.35), 9, 46, 30)
    def v59(f0, f1):
        rail(f0, 1.0); rail(f1 - 1, 1.0)
        E.place(f0, SITB2, 180); E.place(f1 - 1, SITB2, 180); E.face(f0, 'happy'); idle(E, f0, f1, sit_pose(rs=(-20, 0, 0), ls=(-20, 0, 0)), 0.3, look=-12)
        N_.place(f0, SITB, 180); N_.place(f1 - 1, SITB, 180); N_.face(f0, 'happy'); idle(N_, f0, f1, sit_pose(rs=(-20, 0, 0), ls=(-20, 0, 0)), 0.3, look=12)

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
        broken = 1.0 if i > [x['fn'].__name__ for x in SHOTS].index('v42') else 0.0
        rail(f0, broken); rail(f1 - 1, broken); bus_at(f0, BUS0.x + 400); bus_at(f1 - 1, BUS0.x + 400)
        train_at(f0, VW.TRACKS.x - 250); train_at(f1 - 1, VW.TRACKS.x - 250); uw(f0, 30000); uw(f1 - 1, 30000)
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
    roots = {c.root.name for c in C.values()} | {'cam', 'dadcar', 'trashcan', 'money', 'bulb', 'heart', 'balloon', 'bus', 'train', 'snap_rail', 'splash', 'whisper', 'bubbles', 'phone', 'helmet', 'veil', 'bouquet', 'lifefloat'}
    def fix(ad, name):
        if not ad or not ad.action: return
        for fc in ad.action.fcurves:
            for k in fc.keyframe_points:
                if name == 'uw_light' and 'energy' in fc.data_path: k.interpolation = 'LINEAR'
                elif fc.data_path in ('hide_render', 'hide_viewport', 'lens') or 'energy' in fc.data_path or 'color' in fc.data_path or 'default_value' in fc.data_path \
                        or (name == 'Sun') or fc.data_path.startswith('nodes'):
                    k.interpolation = 'CONSTANT'
                elif name in roots: k.interpolation = 'LINEAR'
                else: k.interpolation = 'SINE'; k.easing = 'EASE_IN_OUT'
    for o in bpy.data.objects:
        fix(o.animation_data, o.name)
        if o.data is not None and hasattr(o.data, 'animation_data'): fix(o.data.animation_data, o.name)
    for m in bpy.data.materials:
        if m.node_tree and not m.get('flow'): fix(m.node_tree.animation_data, m.name)
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
