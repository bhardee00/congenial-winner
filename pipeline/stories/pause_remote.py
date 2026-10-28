""""I Found a Remote That Pauses the World" - sets and choreography. Line numbers refer to stories/pause_remote.json.
Characters face -Y at rest; cameras mostly look from -Y. Frames are absolute frames of the final video."""
import math, random
import bpy
from mathutils import Vector
import shortkit as K
from shortkit import Set, prim, mat, ground, place, empty, vis, show_between, camera, follow, pose, rest, at, turn, walk, sit, press, hold_out, nod
import avatar, characters as C
from avatar import react

random.seed(4)
SKIN_MAN, SKIN_KID = (234, 184, 146), (204, 142, 105)
MAN = {"shirt": (60, 140, 90), "pants": (50, 60, 90), "skin": SKIN_MAN}
KID = {"shirt": (240, 200, 40), "pants": (200, 60, 60), "hair": True, "hair_color": (40, 25, 15), "scale": 0.65, "skin": SKIN_KID}
GUY = {"shirt": (230, 120, 40), "pants": (40, 40, 45), "hair": True, "hair_color": (200, 160, 90), "skin": (160, 110, 80)}
CLERK = {"shirt": (190, 40, 40), "pants": (60, 50, 40), "hair": True, "hair_color": (235, 210, 140), "skin": (240, 205, 180)}
BENCH_AT, BENCH_SEAT = (0.0, 3.4), 1.9


# ---------------- props ----------------
def remote(parent=None, loc=(0, 0, 0), rot=(0, 0, 0)):
    r = empty("remote", loc, parent); r.rotation_euler = [math.radians(a) for a in rot]
    prim("box", (0.3, 0.16, 0.85), (0, -0.05, -0.22), mat((22, 22, 24), 0.35), parent=r, bevel=0.04)
    prim("cylY", (0.13, 0.13, 0.06), (0, -0.14, -0.45), mat((255, 40, 40), 0.3, emit=2.5), rot=(90, 0, 0), parent=r)
    for i in range(3): prim("box", (0.18, 0.04, 0.06), (0, -0.14, -0.2 + i * 0.12), mat((90, 90, 95), 0.4), parent=r)
    return r


def model_prop(ctx, name, scale, parent=None, loc=(0, 0, 0), rot_z=0):
    o = place(ctx.D, ctx.M[name], loc, rot_z, scale, name)
    if parent: o.parent = parent; o.location = loc
    return o


def tissue(parent=None, loc=(0, 0, 0)):
    t = empty("tissue", loc, parent)
    prim("box", (0.75, 0.04, 0.6), (0, 0, 0), mat((250, 250, 250), 0.9), rot=(0, 8, 0), parent=t, bevel=0.03)
    return t


def beard(ctx, av):
    """The year-long beard, on the chin of an R15 avatar (shown later with show_between)."""
    b = model_prop(ctx, "beard", 0.8, av["head"], (0, -0.36, -0.25))
    return b


def pigeon_beard(ctx, pg):
    b = model_prop(ctx, "beard", 0.32, pg["head"], (0, -0.62, -0.12))
    b.rotation_euler = (0, 0, math.radians(-90))
    return b


def floaters(n, lo, hi, c, size=0.12, kind="ball", m=None):
    """Things frozen mid-air (snowflakes, leaves, dust)."""
    m = m or mat(c, 0.7)
    for _ in range(n):
        p = [random.uniform(lo[k], hi[k]) for k in range(3)]
        s = size * random.uniform(0.6, 1.4)
        prim(kind, (s, s * (0.4 if kind == "box" else 1), s), p, m, rot=[random.uniform(0, 180) for _ in range(3)])


def trees(ctx, spots):
    for x, y, k, s in spots: place(ctx.D, ctx.M[k], (x, y, 0), random.uniform(0, 360), s)


# ---------------- sets ----------------
def park(ctx):
    S, L = ctx.short, ctx.L
    st = Set("park", sky=(110, 175, 240), horizon=(215, 232, 245), sun=(52, 0, -38))
    with st:
        ground(300, (96, 168, 74))
        prim("box", (80, 4.2, 0.06), (0, 0, 0.03), mat((214, 198, 154), 0.9))
        place(ctx.D, ctx.M["bench"], (BENCH_AT[0], BENCH_AT[1], 0), 0, 0.85, "bench")
        trees(ctx, [(-16, 16, "pine", 0.35), (13, 18, "pine", 0.32), (24, 9, "tree", 0.35), (-25, 7, "tree", 0.4),
                    (-7, 24, "tree", 0.4), (6, 30, "pine", 0.4), (-30, 22, "pine", 0.38), (32, 26, "tree", 0.4)])
        for x in (-7.5, 8.5): place(ctx.D, ctx.M["lamp"], (x, 2.8, 0), 0, 0.55)
        for x, y, r in ((-11, 5, 1.6), (-9.5, 6.5, 1.2), (11, 6, 1.5), (16, 4, 1.2), (-4.5, 8, 1.1)):
            prim("ball", (r * 2, r * 2, r * 1.5), (x, y, r * 0.6), mat((70, 140, 60), 0.8))
        for x, y, r in ((-60, 120, 45), (40, 140, 55), (110, 110, 40)):
            prim("ball", (r * 2, r * 2, r), (x, y, -r * 0.2), mat((110, 170, 90), 0.9))
        leaves = empty("leaves")
        lm = mat((235, 140, 40), 0.7)
        for _ in range(40):
            p = (random.uniform(-9, 10), random.uniform(-5, 4), random.uniform(1.2, 6.5)); s = random.uniform(0.15, 0.28)
            prim("box", (s, s * 0.15, s * 0.7), p, lm, rot=[random.uniform(0, 180) for _ in range(3)], parent=leaves)

        me = avatar.build(ctx.D); man = avatar.build(ctx.D, "man", MAN); kid = avatar.build(ctx.D, "kid", KID)
        guy = avatar.build(ctx.D, "guy", GUY); pg = C.pigeon(ctx.D)
        bd = beard(ctx, me); pbd = pigeon_beard(ctx, pg)
        L31a = L(31)[0]
        show_between(bd, L31a); show_between(pbd, L31a)

        # remote: in my hand until I put it back (34), then on the bench, then in the guy's hand (35)
        a34, b34 = L(34); a35, b35 = L(35)
        K.carry(lambda p: remote(p, (0, -0.02, -0.05)) if p else remote(None, (BENCH_AT[0] + 0.9, BENCH_AT[1] - 0.6, BENCH_SEAT + 0.12), (90, 0, 15)),
                {"me": me["grips"]["ra"], "bench": None, "guy": guy["grips"]["ra"]},
                [(0, "me"), (a34 + 40, "bench"), (a35 + 36, "guy")])
        # ice cream: in the kid's hand, frozen mid-fall (1), in my hand (7), eaten
        a7, b7 = L(7)
        K.carry(lambda p: model_prop(ctx, "icecream", 0.45, p, (0, -0.1, -0.35)) if p else model_prop(ctx, "icecream", 0.45, None, (6.6, -1.0, 1.25)),
                {"kid": kid["grips"]["ra"], "air": None, "me": me["grips"]["la"]},
                [(0, "kid"), (L(1)[0] - 2, "air"), (a7 + 9, "me"), (b7 - 3, "gone")])
        for o in bpy.data.objects:
            if o.name.startswith("icecream") and o.parent is None and abs(o.location.x - 6.6) < 0.01:
                o.rotation_euler = (math.radians(35), math.radians(20), 0)
        # tissue in front of the man's face (5), flies off when he sneezes (32)
        a5, b5 = L(5); a32, b32 = L(32)
        ts = tissue(None, (-5.05, -1.0, 4.25)); show_between(ts, a5 + 28)
        K._key(ts, "location", a32 + 5, (-5.05, -1.0, 4.25), 1); K._key(ts, "location", a32 + 30, (-5.6, -3.2, 5.4))
        K._key(ts, "rotation_euler", a32 + 5, (0, 0, 0), 1); K._key(ts, "rotation_euler", a32 + 30, (0.8, 0.5, 1.4))

        # --- positions at rest
        at(me, 1, (1.5, -1.0, 0), 0); at(man, 1, (-5.0, -0.3, 0), 15); at(kid, 1, (6.2, 0.4, 0), -15)
        at(guy, 1, (16, -0.5, 0), 90); pg["root"].location = (4.0, -2.6, 0); pg["root"].rotation_euler = (0, 0, math.radians(-123))
        # man mid-sneeze, kid dropping the ice cream (frozen from line 1)
        pose(man, 1, None, head=(-22, 0, 0), la=(-55, 0, -25), la_elbow=(-70, 0, 0), waist=(-6, 0, 0)); react(man, "sleepy", 2)
        pose(kid, 1, None, ra=(-35, 0, 15), ra_elbow=(-20, 0, 0)); react(kid, "happy", 2)
        hold_out(me, 1, up=-40, ease=None)

        # 0: found it, pressed pause
        a, b = L(0); P = b - 8
        react(me, "suspicious", 2); react(me, "grin", a + 22); press(me, P)
        S.flash(P); ctx.overlay("icon_pause.png", P, P + 24)
        C.look(pg, 12, 0, 30); C.look(pg, 26, 0, 0); C.look(pg, 34, 0, 30)
        camera(st, "c0", (4.6, -11.5, 4.4), (1.3, -1.0, 3.4), 40, a, b, (4.0, -9.8, 4.2), (1.3, -1.0, 3.6))
        S.shot(st, "c0", a, b)
        # 1: the world stopped
        a, b = L(1)
        react(me, "big_eyes", a + 2); react(kid, "shock", a - 1); hold_out(me, a + 4, up=-35)
        camera(st, "c1", (0.5, -19, 6.0), (0.6, 0, 2.8), 30, a, b, (0.5, -17, 5.5), (0.6, 0, 3.0))
        S.shot(st, "c1", a, b, frozen=True)
        # 2: except me. and a pigeon
        a, b = L(2)
        pose(me, a + 4, head=(0, 0, 35)); pose(me, a + 16, head=(0, 0, -40)); react(me, "nervous", a + 16)
        C.look(pg, a + 10, -30, -10)
        camera(st, "c2", (4.2, -9.5, 3.2), (2.8, -1.8, 2.2), 35)
        S.shot(st, "c2", a, b, frozen=True)
        # 3: the pigeon looked at me like I owed it money
        a, b = L(3)
        C.look(pg, a + 6, 0, -22); C.blink(pg, b - 14, 4)
        camera(st, "c3", (3.7, 0.7, 3.2), (4.0, -2.6, 1.2), 42, a, b, (3.8, 0.2, 2.9), (4.0, -2.6, 1.2), fstop=2.8)
        S.shot(st, "c3", a, b, frozen=True)
        # 4: a man frozen mid-sneeze
        a, b = L(4)
        camera(st, "c4", (-3.4, -6.4, 4.6), (-5.0, -0.3, 4.1), 50, a, b, (-3.8, -5.6, 4.6), (-5.0, -0.3, 4.2))
        S.shot(st, "c4", a, b, frozen=True)
        # 5: I put a tissue in front of him
        walk(me, a + 4, a5 + 18, (1.5, -1.0, 0), (-3.5, -1.6, 0)); turn(me, a5 + 24, (-5, -0.3))
        rest(me, a5 + 24, "head"); react(me, "determined", a5); pose(me, a5 + 26, la=(-70, 0, -20)); rest(me, a5 + 36, "la")
        react(me, "grin", a5 + 34)
        camera(st, "c5", (-1.6, -10.5, 4.4), (-4.2, -0.8, 3.4), 35)
        S.shot(st, "c5", a5, b5, frozen=True)
        # 6: kid's ice cream frozen halfway to the ground
        a, b = L(6)
        walk(me, a + 4, b - 4, (-3.5, -1.6, 0), (5.3, -2.3, 0))
        camera(st, "c6", (8.4, -6.8, 1.4), (6.3, -0.6, 1.9), 35)
        S.shot(st, "c6", a, b, frozen=True)
        # 7: I caught it. I ate it.
        turn(me, a7 + 2, (6.6, -1.0), 4); pose(me, a7 + 7, la=(-55, 0, -25), la_elbow=(-20, 0, 0)); react(me, "happy", a7 + 10)
        pose(me, a7 + 16, la=(-95, 0, -35), la_elbow=(-95, 0, 0)); rest(me, b7 + 4, "la", "la_elbow")
        camera(st, "c7", (9.2, -4.6, 4.2), (5.9, -1.5, 3.2), 40)
        S.shot(st, "c7", a7, b7, frozen=True)
        # 8: I'm not proud of it.
        a, b = L(8)
        turn(me, a, 0, 4); react(me, "embarrassed", a)
        camera(st, "c8", (4.6, -7.0, 4.9), (5.3, -2.3, 4.6), 55)
        S.shot(st, "c8", a, b, frozen=True)
        # 9: pressed play. nothing. dead batteries.
        a, b = L(9)
        react(me, "determined", a); press(me, a + 8); ctx.overlay("icon_play.png", a + 8, a + 17)
        react(me, "suspicious", a + 16); react(me, "annoyed", a + 30); hold_out(me, a + 34, up=-40)
        camera(st, "c9", (3.4, -8.6, 4.5), (5.3, -2.3, 3.7), 40)
        S.shot(st, "c9", a, b, frozen=True)
        # 10: the pigeon sighed
        a, b = L(10)
        K._key(pg["root"], "location", a, (7.3, -4.4, 0), 1); K._key(pg["root"], "rotation_euler", a, (0, 0, math.radians(-15)), 1)
        C.sigh(pg, a + 4); react(me, "suspicious", a + 20)
        camera(st, "c10", (7.9, -8.0, 1.7), (7.2, -4.4, 1.1), 45, fstop=3.5)
        S.shot(st, "c10", a, b, frozen=True)

        # ---- back from the trip (31-37): beard, press play, world moves again
        a, b = L(31)
        at(me, a - 1, (1.5, -1.0, 0), 0); hold_out(me, a - 1, up=-40, ease=None)
        K._key(pg["root"], "location", a - 1, (3.2, -2.2, 0), 1); K._key(pg["root"], "rotation_euler", a - 1, (0, 0, math.radians(-120)), 1)
        react(me, "determined", a - 1); P = a + 5; press(me, P); react(me, "happy", P + 4)
        S.flash(P); ctx.overlay("icon_play.png", P, P + 22)
        K._key(leaves, "location", P, (0, 0, 0), 1); K._key(leaves, "location", P + 45, (0.6, 0.4, -7.0)); vis(leaves, P + 46, False)
        camera(st, "c31", (0.9, -6.2, 4.7), (1.5, -1.0, 4.35), 50)
        S.shot(st, "c31", a, b)
        # 32: the man sneezed into his tissue
        a, b = L(32)
        pose(man, a + 5, ease=3, head=(28, 0, 0), waist=(10, 0, 0)); react(man, "shock", a + 5); react(man, "happy", a + 22)
        camera(st, "c32", (-3.0, -7.8, 4.5), (-5.0, -0.5, 4.0), 45)
        S.shot(st, "c32", a, b)
        # 33: the kid looked at his empty hand
        a, b = L(33)
        pose(kid, a + 4, head=(30, 0, 0), ra=(-45, 0, 5)); react(kid, "sad", a + 6); react(kid, "suspicious", a + 22)
        camera(st, "c33", (8.2, -6.0, 3.0), (6.2, 0.0, 2.4), 40)
        S.shot(st, "c33", a, b)
        # 34: I put the remote back on the bench
        front = (BENCH_AT[0] + 0.9, BENCH_AT[1] - 2.0, 0)
        walk(me, a34 + 2, a34 + 30, (1.5, -1.0, 0), front); turn(me, a34 + 34, 180, 5)
        pose(me, a34 + 38, ra=(-60, 0, 0), ra_elbow=(-10, 0, 0)); rest(me, a34 + 48, "ra", "ra_elbow")
        react(me, "smile", a34)
        walk(me, b34 - 14, b34 + 4, front, (2.6, 0.2, 0)); turn(me, b34 + 10, (1.0, -10), 6)
        camera(st, "c34", (4.0, -11.5, 5.0), (1.0, 1.4, 3.0), 35)
        S.shot(st, "c34", a34, b34)
        # 35: a guy sat down and picked it up. "Is this yours?"
        seat = (BENCH_AT[0] - 1.4, BENCH_AT[1] - 0.3)
        walk(guy, a34 + 20, a35 + 14, (16, -0.5, 0), (seat[0], seat[1] - 1.6, 0))
        turn(guy, a35 + 18, 0, 4); sit(guy, a35 + 26, BENCH_SEAT, seat, 0)
        pose(guy, a35 + 34, ra=(-30, 0, 0)); hold_out(guy, a35 + 44, up=-60); react(guy, "grin", a35 + 40)
        camera(st, "c35", (2.0, -12.5, 5.0), (0.4, 2.0, 2.9), 32)
        S.shot(st, "c35", a35, b35)
        # 36: I said no.
        a, b = L(36)
        react(me, "annoyed", a); nod(me, a + 2, 2, 14, axis=2)
        camera(st, "c36", (1.6, -4.4, 4.8), (2.6, 0.2, 4.4), 50)
        S.shot(st, "c36", a, b)
        # 37: the pigeon landed next to him. It winked at me.
        a, b = L(37)
        C.fly(pg, a, a + 32, (3.2, -2.2, 0), (BENCH_AT[0] + 0.6, BENCH_AT[1] - 0.4, BENCH_SEAT))
        K._key(pg["root"], "rotation_euler", a + 32, (0, 0, math.radians(10)), 6)
        C.blink(pg, S.total - 28, 8)
        camera(st, "c37", (1.2, -12.0, 5.2), (-0.4, 2.6, 3.0), 32, a, S.total, (0.2, -8.2, 4.0), (-0.3, 2.9, 3.0))
        S.shot(st, "c37", a, S.total + 1)
    return st


def store(ctx):
    S, L = ctx.short, ctx.L
    st = Set("store", sky=(200, 205, 210), horizon=(230, 230, 230), sun=(60, 0, 20), sun_energy=1.5)
    with st:
        prim("box", (60, 30, 0.2), (0, 0, -0.1), mat((225, 225, 220), 0.35))
        for x in range(-28, 30, 4):
            prim("box", (0.05, 30, 0.01), (x, 0, 0.005), mat((200, 200, 195), 0.4))
        prim("box", (60, 0.5, 14), (0, 9, 7), mat((240, 232, 215), 0.8))
        prim("box", (60, 30, 0.3), (0, 0, 12), mat((245, 245, 245), 0.9))
        for x in range(-24, 26, 8):
            prim("box", (5, 1.2, 0.1), (x, 2, 11.8), mat((255, 255, 250), 0.5, emit=4))
        bl = bpy.data.lights.new("store", "AREA"); bl.energy = 6000; bl.size = 30
        lo = bpy.data.objects.new("store_light", bl); st.link(lo); lo.location = (0, -2, 11.5)
        for x in (-9, 0, 9):
            place(ctx.D, ctx.M["shelf"], (x, 2.6, 0), 90, 0.62)
        K.plane_image(ctx.A + "sign_soldout.png", (3.0, 1.66), (0, 1.3, 6.7), emit=0.4)
        K.plane_image(ctx.A + "sign_noaa.png", (3.0, 1.66), (9, 1.3, 6.7), emit=0.4)
        K.plane_image(ctx.A + "sign_batteries.png", (3.4, 1.0), (-9, 1.3, 6.5), emit=0.4)
        me = avatar.build(ctx.D); pg = C.pigeon(ctx.D)

        a, b = L(11)
        at(me, 1, (-0.8, -0.6, 0), 180); react(me, "sad", a + 18); turn(me, a + 16, (3, -8), 8)
        K._key(pg["root"], "location", 1, (1.6, -1.2, 0), 1)
        camera(st, "s11", (3.0, -8.0, 5.4), (0.0, 2.2, 4.4), 30, a, b, (2.6, -7.0, 5.2), (0.0, 2.2, 4.4))
        S.shot(st, "s11", a, b, frozen=True)
        a, b = L(12)
        at(me, a - 1, (8.6, -0.7, 0), 0); react(me, "angry", a + 2, b + 6)
        pose(me, a + 4, la=(-20, 0, -20), ra=(-20, 0, 20), la_elbow=(-60, 0, 0), ra_elbow=(-60, 0, 0))
        K._key(pg["root"], "location", a - 1, (10.4, -1.4, 0), 1); K._key(pg["root"], "rotation_euler", a - 1, (0, 0, math.radians(-20)), 1)
        camera(st, "s12", (7.6, -7.4, 4.8), (8.8, 0.8, 4.2), 35)
        S.shot(st, "s12", a, b, frozen=True)
        a, b = L(13)
        rest(me, a + 4, "la", "ra", "la_elbow", "ra_elbow"); react(me, "annoyed", a + 8)
        C.look(pg, a + 10, -20, -25); C.sigh(pg, a + 30)
        camera(st, "s13", (9.9, -5.6, 3.6), (9.4, -0.9, 3.2), 35)
        S.shot(st, "s13", a, b, frozen=True)
    return st


def ocean(ctx):
    S, L = ctx.short, ctx.L
    st = Set("ocean", sky=(255, 170, 120), horizon=(255, 215, 170), sun=(84, 0, -40), sun_energy=3, sun_color=(255, 200, 150))
    with st:
        import bmesh
        me_ = bpy.data.meshes.new("waves"); bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=160, y_segments=160, size=120)
        for v in bm.verts:
            x, y = v.co.x, v.co.y
            v.co.z = 0.9 * math.sin(x * 0.55 + y * 0.12) + 0.35 * math.sin(x * 1.3 - y * 0.7) + 0.25 * math.sin(y * 0.9)
        bm.to_mesh(me_); bm.free()
        for p in me_.polygons: p.use_smooth = True
        w = bpy.data.objects.new("waves", me_); st.link(w); me_.materials.append(mat((90, 160, 205), 0.08))
        crests = [(-9.0, 0.0), (-4.5, 0.2), (0.0, -0.1), (4.5, 0.1), (9.0, 0.0)]
        for x, y in crests:
            prim("ball", (2.4, 3.2, 1.2), (x, y, 1.2), mat((235, 245, 255), 0.3))
        for x, y, s in ((40, 70, 0.18), (-55, 80, 0.22), (-15, 110, 0.15)): place(ctx.D, ctx.M["iceberg"], (x, y, -2), random.uniform(0, 360), s)
        floaters(30, (-14, -6, 0.8), (14, 6, 3.5), (240, 250, 255), 0.14)  # frozen spray
        me = avatar.build(ctx.D); pg = C.pigeon(ctx.D)
        a, b = L(14)
        tops = [(x, y, 1.8) for x, y in crests]
        n = len(tops) - 1; step = (b + 8 - a) / n
        for i in range(n):
            f = int(a + i * step); g = int(a + (i + 1) * step); p, q = Vector(tops[i]), Vector(tops[i + 1])
            at(me, f, tuple(p), 90, ease=1 if i == 0 else None)
            mid = (p + q) / 2; mid.z += 1.8
            at(me, int((f + g) / 2), tuple(mid), 90, ease=None); at(me, g, tuple(q), 90, ease=None)
            pose(me, f + 2, ll=(-30, 0, 0), rl=(20, 0, 0), la=(-50, 0, -30), ra=(30, 0, 30)); pose(me, g - 1, ll=(0, 0, 0), rl=(0, 0, 0))
        react(me, "happy", a)
        C.walk(pg, a, b + 8, (-12, 0.4, 1.6), (4.5, 0.4, 1.6), 4)
        camera(st, "o14", (-3.0, -16.0, 4.0), (-3.0, 0.0, 2.4), 32, a, b, (5.0, -16.0, 4.0), (5.0, 0.0, 2.4))
        S.shot(st, "o14", a, b, frozen=True)
    return st


def paris(ctx):
    S, L = ctx.short, ctx.L
    st = Set("paris", sky=(220, 215, 205), horizon=(235, 230, 220), sun=(60, 0, 30), sun_energy=1.2)
    with st:
        prim("box", (40, 30, 0.2), (0, 0, -0.1), mat((140, 92, 55), 0.35))
        prim("box", (40, 0.4, 14), (0, 3.2, 7), mat((150, 40, 45), 0.9))
        prim("box", (40, 30, 0.3), (0, 0, 12.5), mat((245, 240, 230), 0.9))
        place(ctx.D, ctx.M["mona"], (0, 2.85, 5.0), 0, 0.85, "mona")
        sm = K.plane_image(ctx.A + "smile_decal.png", (0.8, 0.4), (-0.08, 2.74, 5.95))
        for x, w_, h_, c in ((-8, 3.6, 2.6, (60, 90, 140)), (8, 3.0, 3.8, (190, 150, 60))):
            prim("box", (w_ + 0.4, 0.2, h_ + 0.4), (x, 3.0, 5.2), mat((200, 160, 60), 0.3, metal=0.8))
            prim("box", (w_, 0.22, h_), (x, 2.95, 5.2), mat(c, 0.8))
        for x in (-3.2, 3.2):
            prim("cylY", (0.25, 0.25, 2.6), (x, 0.6, 1.3), mat((210, 170, 60), 0.25, metal=0.9))
        prim("cyl", (6.4, 0.16, 0.16), (0, 0.6, 2.35), mat((170, 20, 30), 0.6))
        sp = bpy.data.lights.new("spot", "SPOT"); sp.energy = 2500; sp.spot_size = math.radians(45)
        so = bpy.data.objects.new("spot", sp); st.link(so); so.location = (0, -2.5, 11); so.rotation_euler = (math.radians(35), 0, 0)
        al = bpy.data.lights.new("fill", "AREA"); al.energy = 2500; al.size = 20
        ao = bpy.data.objects.new("fill", al); st.link(ao); ao.location = (0, -10, 10); ao.rotation_euler = (math.radians(50), 0, 0)
        me = avatar.build(ctx.D); pg = C.pigeon(ctx.D)
        marker = prim("cylY", (0.12, 0.12, 0.7), (0, -0.05, -0.3), mat((20, 20, 20), 0.4), parent=me["grips"]["ra"])
        a, b = L(15); a2, b2 = L(16)
        show_between(sm, a + 22, a2 + 10); show_between(marker, 0, a2 + 30)
        at(me, 1, (1.0, 1.5, 0), 200); react(me, "determined", a)
        pose(me, a + 12, ra=(-125, 0, -20), ra_elbow=(-30, 0, 0)); pose(me, a + 18, ra=(-120, 0, -10)); pose(me, a + 24, ra=(-125, 0, -25))
        rest(me, a + 32, "ra", "ra_elbow"); turn(me, a + 34, (-3, -8), 6); react(me, "grin", a + 36)
        K._key(pg["root"], "location", 1, (-1.6, 0.2, 0), 1); K._key(pg["root"], "rotation_euler", 1, (0, 0, math.radians(30)), 1)
        ctx.overlay("card_paris.png", a, a + 38)
        camera(st, "p15", (-5.0, -4.2, 4.8), (0.3, 2.2, 4.8), 32, a, b, (-4.4, -3.6, 4.8), (0.3, 2.2, 4.9))
        S.shot(st, "p15", a, b, frozen=True)
        turn(me, a2 + 2, 200, 4); pose(me, a2 + 8, ra=(-125, 0, -20), ra_elbow=(-30, 0, 0)); rest(me, a2 + 16, "ra", "ra_elbow")
        turn(me, a2 + 20, (-2, -8), 5); react(me, "nervous", a2 + 22); C.look(pg, a2 + 24, 30, -15)
        camera(st, "p16", (-2.0, -4.6, 5.2), (0.2, 2.6, 5.0), 38)
        S.shot(st, "p16", a2, b2, frozen=True)
    return st


def japan(ctx):
    S, L = ctx.short, ctx.L
    st = Set("japan", sky=(120, 180, 240), horizon=(225, 235, 245), sun=(50, 0, 30))
    with st:
        ground(600, (120, 175, 95))
        prim("cone", (240, 240, 95), (40, 300, 47), mat((90, 110, 140), 0.9))
        prim("cone", (90, 90, 36), (40, 300, 77.5), mat((250, 250, 255), 0.7))
        prim("box", (400, 8.5, 1.0), (0, 0, 6.0), mat((170, 170, 175), 0.8))
        for x in range(-180, 200, 16): prim("box", (1.6, 3.0, 6.0), (x, 0, 3.0), mat((150, 150, 155), 0.8))
        for x, y in ((-30, 20), (-12, 26), (20, 18), (55, 24), (90, 16), (110, -26), (70, -30), (130, 30)):
            prim("cylY", (0.8, 0.8, 4), (x, y, 2), mat((90, 60, 45), 0.8))
            prim("ball", (7, 7, 5.5), (x, y, 6.2), mat((250, 180, 205), 0.7))
        place(ctx.D, ctx.M["train"], (0, 0, 6.5), 0, 0.55, "train")
        dust = mat((240, 240, 240), 0.9)
        for _ in range(26):  # frozen wind behind the stopped train
            prim("box", (random.uniform(4, 12), 0.08, 0.08), (random.uniform(-90, -60), random.uniform(-5, 5), random.uniform(6.6, 13)), dust)
        me = avatar.build(ctx.D); pg = C.pigeon(ctx.D)
        a, b = L(17)
        at(me, 1, (79.5, -2.0, 6.5), 70); react(me, "big_eyes", a + 10)
        pose(me, a + 14, head=(-20, 0, 0))
        K._key(pg["root"], "location", 1, (81, -3.0, 6.5), 1)
        ctx.overlay("card_japan.png", a, a + 38)
        camera(st, "j17", (100, -26, 11), (68, 0, 9), 32, a, b, (96, -22, 10), (70, 0, 9))
        S.shot(st, "j17", a, b, frozen=True)
    return st


def train_inside(ctx):
    S, L = ctx.short, ctx.L
    st = Set("train_in", sky=(255, 240, 245), horizon=(255, 225, 235), sun=(55, 0, 60), sun_energy=2.5)
    with st:
        prim("box", (40, 14, 0.2), (0, 0, -0.1), mat((70, 70, 90), 0.7))
        prim("box", (40, 14, 0.3), (0, 0, 8.5), mat((245, 245, 248), 0.6))
        prim("box", (40, 0.3, 9), (0, 5, 4.2), mat((240, 240, 245), 0.6))
        for x in range(-16, 18, 6):
            prim("box", (4.0, 0.1, 2.6), (x, 4.83, 4.8), mat((255, 205, 225), 0.4, emit=1.5))
        cushion, frame_ = mat((40, 70, 140), 0.8), mat((200, 200, 205), 0.4)
        seats = {}
        for x in (-2.0, 2.0, -9.0, 9.0):
            prim("box", (3.2, 2.8, 0.7), (x, 0.4, 1.75), cushion, bevel=0.2)
            prim("box", (3.2, 0.7, 4.2), (x, 1.75, 3.9), cushion, rot=(-12, 0, 0), bevel=0.2)
            prim("box", (3.0, 0.6, 1.2), (x, 1.95, 6.2), mat((250, 250, 250), 0.9), bevel=0.15)
            prim("box", (3.4, 2.6, 1.4), (x, 0.5, 0.7), frame_)
            for s in (-1, 1): prim("box", (0.35, 2.6, 0.3), (x + s * 1.75, 0.4, 2.6), frame_, bevel=0.08)
            seats[x] = (x, 0.25)
        ll = bpy.data.lights.new("cabin", "AREA"); ll.energy = 3500; ll.size = 25
        lo = bpy.data.objects.new("cabin", ll); st.link(lo); lo.location = (0, -2, 8.2)
        me = avatar.build(ctx.D); pg = C.pigeon(ctx.D)
        a, b = L(18)
        sit(me, 1, 2.1, seats[-2.0], 0, lean=-12, ease=None)
        pose(me, 1, None, la=(-150, 0, 20), ra=(-150, 0, -20), la_elbow=(-120, 0, 0), ra_elbow=(-120, 0, 0), head=(-5, 0, 0))
        react(me, "happy", 2); react(me, "grin", a + 35)
        K._key(pg["root"], "location", 1, (2.0, 0.3, 2.1), 1); C.look(pg, a + 20, 25, -10)
        camera(st, "t18", (0.5, -10.5, 4.6), (0.0, 0.5, 3.4), 32, a, b, (0.5, -8.6, 4.4), (0.0, 0.5, 3.5))
        S.shot(st, "t18", a, b, frozen=True)
    return st


def road(ctx):
    """19-22: the long walk, then a year passes (sky goes round, beards grow)."""
    S, L = ctx.short, ctx.L
    st = Set("road", sky=(130, 180, 235), horizon=(240, 225, 200), sun=(65, 0, 40))
    with st:
        ground(600, (130, 178, 92))
        prim("box", (7, 600, 0.08), (0, 250, 0.04), mat((70, 70, 76), 0.85))
        for y in range(-20, 400, 8): prim("box", (0.3, 3.5, 0.02), (0, y, 0.09), mat((240, 210, 60), 0.6))
        trees(ctx, [(x * s, y, k, sc) for s in (-1, 1) for x, y, k, sc in ((14, 10, "pine", 0.3), (18, 40, "tree", 0.35), (12, 70, "pine", 0.32), (22, 100, "tree", 0.4))])
        for x, y, r in ((-120, 300, 70), (100, 340, 90), (0, 420, 80)):
            prim("ball", (r * 2, r * 2, r), (x, y, -r * 0.2), mat((110, 160, 95), 0.9))
        rock = prim("ball", (2.6, 2.2, 1.6), (5.4, 0.6, 0.5), mat((130, 125, 120), 0.9))
        me = avatar.build(ctx.D); pg = C.pigeon(ctx.D)
        bd = beard(ctx, me); pbd = pigeon_beard(ctx, pg)
        a19, b19 = L(19); a20, b20 = L(20); a21, b21 = L(21); a22, b22 = L(22)
        walk(me, a19, b20 - 8, (0.8, 12, 0), (0.8, -3, 0), 8); react(me, "determined", a19)
        C.walk(pg, a19, b20 - 8, (1.6, 17, 0), (1.6, 2.5, 0), 5)
        camera(st, "r19", (7.5, -14, 3.6), (0.5, 4, 2.6), 35)
        S.shot(st, "r19", a19, b19, frozen=True)
        follow(st, "r20", pg["root"], (4.2, 0.6, 1.1), (0, 0, 0.9), 40)
        S.shot(st, "r20", a20, b20, frozen=True)
        # a year passes: sit on a rock, the sky turns over, beards grow
        sit(me, a21, 1.3, (5.4, 0.3), 0, ease=1); rest(me, a21, "la", "ra", ease=1)
        K._key(pg["root"], "location", a21, (3.6, -0.6, 0), 1); K._key(pg["root"], "rotation_euler", a21, (0, 0, math.radians(-20)), 1)
        react(me, "sleepy", a21)
        sun = st.sun
        for f, r, e in ((a21 - 1, 65, 3.5), (a21 + 10, 120, 0.2), (a21 + 22, 200, 0.2), (a21 + 34, 280, 3.5), (b21, 300, 3.5)):
            K._key(sun, "rotation_euler", f, (math.radians(r), 0, math.radians(40))); sun.data.energy = e; sun.data.keyframe_insert("energy", frame=f)
        for o, s in ((bd, 0.8), (pbd, 0.32)):
            K._key(o, "scale", 0, (0.001,) * 3); K._key(o, "scale", a21, (0.001,) * 3); K._key(o, "scale", b21, (s,) * 3)
        ctx.overlay("card_year.png", a21, b21)
        for i, (x, y) in enumerate(((-290, 230), (290, 330), (-40, 20))):
            ctx.overlays.append((ctx.A + f"clock{i}.png", a21 + 12 + i * 6, b21, 10 + i, x, y, 0.45))
        camera(st, "r21", (8.6, -9.5, 3.8), (4.6, 0.2, 2.8), 35)
        S.shot(st, "r21", a21, b21, frozen=True)
        react(me, "grin", a22 + 18); C.look(pg, a22 + 10, -35, 0)
        camera(st, "r22", (5.2, -7.2, 3.2), (4.4, -0.2, 2.3), 35)
        S.shot(st, "r22", a22, b22, frozen=True)
    return st


def iceland(ctx):
    S, L = ctx.short, ctx.L
    st = Set("iceland", sky=(200, 215, 235), horizon=(235, 240, 248), sun=(60, 0, 50), sun_energy=1.5)
    with st:
        wood = mat((150, 100, 62), 0.7)
        prim("box", (30, 20, 0.2), (0, 0, -0.1), mat((110, 72, 45), 0.6))
        prim("box", (30, 0.4, 12), (0, 5, 6), wood); prim("box", (0.4, 20, 12), (-6, 0, 6), wood)
        prim("box", (30, 20, 0.3), (0, 0, 10), mat((120, 82, 52), 0.7))
        prim("box", (5, 0.1, 3.5), (3.5, 4.75, 5.5), mat((235, 245, 255), 0.5, emit=2.0))
        floaters(25, (1.2, 5.2, 3.8), (5.8, 8, 7.2), (255, 255, 255), 0.12)
        prim("box", (1.6, 6, 0.15), (-5.0, 0.5, 3.4), wood); prim("box", (1.6, 6, 0.15), (-5.0, 0.5, 5.4), wood)
        prim("box", (6, 2.2, 3.2), (3.5, 2.6, 1.6), mat((120, 70, 40), 0.6))
        K.plane_image(ctx.A + "sign_batteries.png", (2.6, 0.75), (-5.75, 0.5, 6.6), rot=(90, 0, -90), emit=0.3)
        ll = bpy.data.lights.new("lamp", "POINT"); ll.energy = 1800; ll.color = (1, 0.85, 0.6)
        lo = bpy.data.objects.new("lamp", ll); st.link(lo); lo.location = (0, -1, 8.5)
        me = avatar.build(ctx.D); clerk = avatar.build(ctx.D, "clerk", CLERK); pg = C.pigeon(ctx.D)
        beard(ctx, me); pigeon_beard(ctx, pg)
        at(clerk, 1, (3.5, 3.9, 0), 0); pose(clerk, 1, None, ra=(-150, 0, 30), ra_elbow=(-40, 0, 0)); react(clerk, "happy", 2)
        a, b = L(23); a2, b2 = L(24)
        at(me, 1, (-2.6, 0.2, 0), -90); react(me, "suspicious", a)
        K.carry(lambda p: model_prop(ctx, "battery", 0.9, p, (0, -0.05, -0.1)) if p else model_prop(ctx, "battery", 0.9, None, (-4.8, 0.5, 3.5)),
                {"shelf": None, "me": me["grips"]["ra"]}, [(0, "shelf"), (a + 24, "me")])
        pose(me, a + 20, ra=(-80, 0, -30)); turn(me, a + 34, (1, -8), 6); hold_out(me, a + 38, up=-75); react(me, "happy", a + 38)
        K._key(pg["root"], "location", 1, (-1.2, -1.4, 0), 1)
        ctx.overlay("card_iceland.png", a, a + 38)
        camera(st, "i23", (2.6, -8.6, 4.4), (-1.6, 0.6, 3.6), 35)
        S.shot(st, "i23", a, b, frozen=True)
        react(me, "sad", a2 + 2)
        camera(st, "i24", (0.2, -5.4, 4.6), (-2.0, 0.0, 4.1), 45)
        S.shot(st, "i24", a2, b2, frozen=True)
    return st


def snow(ctx):
    S, L = ctx.short, ctx.L
    st = Set("snow", sky=(255, 175, 130), horizon=(255, 225, 200), sun=(82, 0, 10), sun_energy=2.6, sun_color=(255, 210, 170))
    with st:
        ground(400, (240, 245, 252), 0.85)
        for x, y, r in ((-6, 4, 2.5), (7, 6, 3.2), (-12, -2, 2.0), (12, -4, 2.4), (-3, 12, 4)):
            prim("ball", (r * 2, r * 2, r * 0.7), (x, y, 0), mat((245, 248, 255), 0.85))
        prim("box", (600, 300, 0.4), (0, 180, -0.1), mat((120, 180, 215), 0.08))
        for x, y, s in ((-30, 90, 0.2), (25, 120, 0.25)): place(ctx.D, ctx.M["iceberg"], (x, y, -1), random.uniform(0, 360), s)
        trees(ctx, [(-18, 10, "pine", 0.3), (20, 14, "pine", 0.33), (-26, 24, "pine", 0.36)])
        floaters(220, (-10, -8, 0.4), (10, 10, 9), (255, 255, 255), 0.09)  # snowflakes, paused
        me = avatar.build(ctx.D); pg = C.pigeon(ctx.D)
        beard(ctx, me); pigeon_beard(ctx, pg)
        # the second battery, tucked under the wing on the side the camera sees
        bat = model_prop(ctx, "battery", 1.2, pg["body"], (0.1, -0.62, 0.85))
        bat.rotation_euler = (0, 0, math.radians(90))
        a25, b25 = L(25); a26, b26 = L(26); a27, b27 = L(27); a28, b28 = L(28); a29, b29 = L(29); a30, b30 = L(30)
        show_between(bat, a26 + 10)
        at(me, 1, (0, 0, 0), 0); react(me, "sad", a25); sit(me, a25 + 16, 0.0, (0, 0), 0, ease=14)
        K._key(pg["root"], "location", 1, (6.0, -1.5, 0), 1)
        camera(st, "n25", (3.6, -10.5, 3.6), (0.2, 0.0, 2.0), 35)
        S.shot(st, "n25", a25, b25, frozen=True)
        C.walk(pg, a26, a26 + 30, (6.0, -1.5, 0), (1.9, -0.9, 0), 5)
        K._key(pg["root"], "rotation_euler", a26 + 36, (0, 0, math.radians(-90)), 5)
        C.wing(pg, "l", b26 - 12, b27 + 4, 115)
        camera(st, "n26", (4.0, -7.2, 2.2), (1.8, -0.6, 1.4), 40)
        S.shot(st, "n26", a26, b26, frozen=True)
        react(me, "big_eyes", a27 + 6)
        camera(st, "n27", (2.4, -4.4, 1.5), (1.7, -0.8, 1.0), 50, fstop=3.0)
        S.shot(st, "n27", a27, b27, frozen=True)
        react(me, "cry", a28, b30)
        camera(st, "n28", (0.6, -5.4, 3.2), (0.0, -0.3, 2.9), 45)
        S.shot(st, "n28", a28, b28, frozen=True)
        C.look(pg, a29 + 4, -55, -25); C.look(pg, a29 + 34, 160, 0, hold=10)
        camera(st, "n29", (3.6, -6.6, 2.6), (1.0, -0.4, 2.0), 40)
        S.shot(st, "n29", a29, b29, frozen=True)
        K._key(pg["root"], "rotation_euler", a30 - 1, (0, 0, math.radians(180)), 1); C.look(pg, a30 - 1, 0, 0, hold=1)
        at(me, a30 - 1, value_loc(me, a30 - 2), 180); react(me, "happy", a30)
        camera(st, "n30", (1.6, -9.5, 3.2), (1.2, 20, 2.4), 32, a30, b30, (1.4, -7.5, 3.0), (1.2, 20, 2.5))
        S.shot(st, "n30", a30, b30, frozen=True)
    return st


def value_loc(av, f):
    return tuple(K.value(av["root"], "location", f))


def build(ctx):
    for fn in (park, store, ocean, paris, japan, train_inside, road, iceland, snow):
        fn(ctx)
