""""I Grabbed the Balloon Nobody Can Let Go Of" - R6 blocky cast, toy-town parade and sky sets.
Line numbers follow stories/balloon.json (0-43). Characters face -Y at rest. Frames are frames of the final video.
Pacing follows the reference channels: a moving camera in every shot, extra cuts inside longer lines,
punch-in zooms and a sound effect on every beat."""
import math, random
import bpy
from mathutils import Vector
import shortkit as K
from shortkit import Set, prim, mat, empty, vis, show_between, camera, orbit, punch, shake, pose, rest, at, turn, walk, sit, idle
import blocky, toys
from avatar import react
from anim import value

random.seed(5)
DAD = {"shirt": (70, 90, 140), "pants": (60, 60, 70), "skin": (234, 190, 150), "hair": (150, 150, 155), "shoes": (60, 40, 30)}
KID26 = {"shirt": (250, 205, 50), "pants": (60, 120, 220), "shoes": (245, 245, 245), "skin": (234, 184, 146), "hair": (90, 60, 30),
         "hat": "propeller", "hat_color": (230, 60, 60)}
PILOT = {"shirt": (60, 110, 70), "pants": (60, 110, 70), "skin": (200, 150, 110), "hat": "cap", "hat_color": (40, 60, 40)}
MIME = {"shirt": (245, 245, 245), "pants": (20, 20, 25), "skin": (250, 250, 250), "hat": "beret"}
MOM = {"shirt": (230, 120, 150), "pants": (90, 70, 120), "skin": (234, 190, 150), "hair": (120, 70, 40)}
GIRL = {"shirt": (255, 130, 190), "pants": (255, 130, 190), "shoes": (250, 250, 250), "skin": (204, 142, 105), "hair": (45, 28, 20),
        "pigtails": True, "scale": 0.68}
GIRLDAD = {"shirt": (90, 180, 120), "pants": (70, 70, 90), "skin": (204, 142, 105), "hair": (45, 28, 20)}
TUBA = {"shirt": (200, 40, 50), "pants": (250, 250, 250), "skin": (234, 190, 150), "hat": "cap", "hat_color": (200, 40, 50)}
CROWD = [{"shirt": c, "pants": p, "skin": s, "hair": h} for c, p, s, h in (
    ((240, 120, 60), (60, 60, 80), (234, 190, 150), (60, 40, 30)), ((120, 90, 220), (40, 40, 50), (160, 110, 80), (20, 20, 20)),
    ((80, 200, 220), (200, 80, 80), (250, 215, 180), (230, 200, 120)), ((250, 250, 250), (70, 120, 70), (204, 142, 105), (40, 30, 20)),
    ((230, 60, 90), (40, 60, 120), (234, 190, 150), (150, 90, 40)), ((150, 210, 90), (90, 70, 60), (180, 120, 90), None))]


# ---------------- helpers ----------------
def sentence_frames(ctx, i):
    """Frame where each sentence of line i starts (for cutting inside a line)."""
    S = ctx.short; ws = ctx.timed[i]["words"]; out = [S.frame(ws[0][1])]
    for k in range(1, len(ws)):
        if ws[k - 1][0][-1] in ".?!\"": out.append(S.frame(ws[k][1]))
    return out


def word_frame(ctx, i, word, nth=0):
    S = ctx.short; hits = [w for w in ctx.timed[i]["words"] if w[0].strip('.,?!"').lower() == word]
    return S.frame(hits[min(nth, len(hits) - 1)][1]) if hits else ctx.L(i)[0]


def hang(av, f, ease=12):
    """Hanging from the balloon: right arm straight up, legs dangling."""
    pose(av, f, ease, ra=(-172, 0, 6), la=(-25, 0, -18), ll=(12, 0, 3), rl=(-6, 0, -3), waist=(-4, 0, 0))


def handshake(a, b, f0, f1, a_hand="la", b_hand="ra"):
    for k, f in enumerate(range(f0, f1, 5)):
        up = k % 2 == 0
        pose(a, f, 3, **{a_hand: (-62 if up else -38, 0, 0)}); pose(b, f, 3, **{b_hand: (-62 if up else -38, 0, 0)})
    rest(a, f1 + 4, a_hand); rest(b, f1 + 4, b_hand)


def npc(ctx, name, look, loc, yaw=0):
    a = blocky.build(ctx.D, name, look); at(a, 0, loc, yaw, ease=None); idle(a, ("head",), 0.03, 50); return a


def cam(st, name, loc, target, lens=35, f0=None, f1=None, d_loc=(0, 0, 0), d_target=(0, 0, 0), fstop=None):
    """Camera with a move: shifts by d_loc / d_target between f0 and f1 (eased)."""
    if f0 is None: return camera(st, name, loc, target, lens, fstop=fstop)
    l2 = tuple(a + b for a, b in zip(loc, d_loc)); t2 = tuple(a + b for a, b in zip(target, d_target))
    return camera(st, name, loc, target, lens, f0, f1, l2, t2, fstop=fstop)


def rel(p, d): return tuple(a + b for a, b in zip(p, d))


# ---------------- town (parade) ----------------
def town(ctx):
    S, L = ctx.short, ctx.L
    st = Set("town", sky=(60, 150, 255), horizon=(190, 225, 255), sun=(48, 0, -35), sun_energy=5)
    with st:
        prim("box", (300, 300, 0.2), (0, 0, -0.1), mat((110, 200, 90), 0.9))
        prim("box", (200, 10, 0.12), (0, 1.5, 0.0), mat((90, 92, 100), 0.85))                  # street
        for y in (-4.6, 7.6): prim("box", (200, 3.6, 0.35), (0, y, 0.12), mat((225, 220, 210), 0.8))  # sidewalks
        for x in range(-60, 61, 6): prim("box", (2.6, 0.3, 0.02), (x, 1.5, 0.07), mat((255, 255, 255), 0.6))
        for x in range(-56, 60, 9):
            toys.house(x + random.uniform(-1, 1), 16, 0); toys.house(x + random.uniform(-1, 1), -19, 180)
        for x in range(-50, 52, 12):
            toys.tree(x + 4, 10.5, 0.9)
            if abs(x - 2) > 24: toys.tree(x - 2, -12, 0.9)
            toys.bunting((x, 9.4, 7.5), (x + 12, 9.4, 7.5), 7.5); toys.bunting((x, -6.4, 7.5), (x + 12, -6.4, 7.5), 7.5)
        toys.clouds(14, (-80, 40, 35), (80, 120, 60), 3, 7)
        # bouncy castle for the 26-year-old's childhood
        bc = empty("castle", (16, -9, 0))
        prim("box", (8, 7, 1.2), (0, 0, 0.6), mat((250, 80, 120), 0.4), parent=bc, bevel=0.5)
        for dx in (-3.5, 3.5):
            for dy in (-3, 3): prim("cylY", (1.4, 1.4, 5), (dx, dy, 3.2), mat((80, 170, 250), 0.4), parent=bc); prim("ball", (1.8, 1.8, 1.8), (dx, dy, 6), mat((250, 210, 60), 0.4), parent=bc)
        prim("box", (8, 0.6, 3.5), (0, 3.2, 2.9), mat((250, 210, 60), 0.4), parent=bc, bevel=0.3)
        # cast
        me = blocky.build(ctx.D); idle(me)
        kid = npc(ctx, "kid", KID26, (1.9, -3.1, 0.35), -10); dad = npc(ctx, "dad", DAD, (3.6, -3.4, 0.35), 20)
        girl = npc(ctx, "girl", GIRL, (-3.0, -3.2, 0.3), 180); gdad = npc(ctx, "gdad", GIRLDAD, (-7.2, -3.9, 0.3), 180)
        tub = npc(ctx, "tuba", TUBA, (-8.5, 1.2, 0), 0); tb = toys.tuba(); tb.parent = tub["waist"]; tb.location = (1.6, 0.2, 0.3); tb.scale = (1.3, 1.3, 1.3)
        crowd = []
        for k, (x, y) in enumerate(((-9, -5.2), (-12, -4.8), (6.5, -5.0), (9, -5.3), (12, -4.9), (-6.5, 8), (-2, 8.2), (4, 7.9), (8, 8.1))):
            crowd.append(npc(ctx, f"crowd{k}", CROWD[k % len(CROWD)], (x, y, 0.3), 0 if y < 0 else 180))
        laugher = crowd[2]
        drummers = []
        for k, x in enumerate((-2, 2, 6)):
            d = npc(ctx, f"drummer{k}", {**TUBA, "shirt": (40, 70, 160)}, (x + 20, 2.5, 0), 90)
            dr = toys.drum(); dr.parent = d["waist"]; dr.location = (0, -1.2, 0.6); drummers.append(d)
        broom = empty("broom"); broom.parent = me["grips"]["la"]; broom.location = (0, -0.1, 0)
        prim("cylY", (0.14, 0.14, 4.2), (0, 0, -0.6), mat((170, 120, 70), 0.7), parent=broom)
        prim("box", (1.4, 0.4, 0.6), (0, 0, -2.8), mat((240, 200, 70), 0.8), parent=broom, bevel=0.1)
        wrapper = prim("box", (0.5, 0.3, 0.06), (-0.6, -4.2, 0.33), mat((255, 120, 200), 0.4))
        cream = toys.ice_cream(); cream.parent = girl["grips"]["la"]; cream.location = (0, -0.2, -0.1)
        cream_drop = toys.ice_cream()
        bd = place_beard(ctx, me); goose_hat = toys.goose(0, 0, 0, 0.55, "goosehat"); goose_hat["root"].parent = me["head"]; goose_hat["root"].location = (0, 0.1, 1.75)
        birds = [toys.bird(0, 0, 0, c, 0.5) for c in ((90, 170, 250), (250, 200, 60))]
        for b, x in zip(birds, (-0.35, 0.4)): b.parent = me["head"]; b.location = (x, -0.95, 0.05)
        trk = toys.truck(); trk.parent = me["root"]; trk.location = (0, 0, -6.5); trk.scale = (0.7, 0.7, 0.7)
        for o in [bd, goose_hat["root"], trk] + birds: show_between(o, 0, 0); vis(o, L(33)[0], True)

        # balloon: kid -> free -> me ... (flashbacks: kid) ... me -> free -> girl -> girl's dad
        free = empty("free", (1.9, -3.4, 2.4)); free2 = empty("free2", (0, 0, 0))
        a0, b0 = L(0); grab = a0 + 34
        K._key(free, "location", a0 + 6, (1.9, -3.4, 2.4)); K._key(free, "location", grab, (-1.6, -3.3, 4.6))
        fb = [L(26)[0], L(27)[0], L(29)[0]]
        a36, b36 = L(36); a37, b37 = L(37); a39, b39 = L(39)
        holders = {"kid": kid["grips"]["ra"], "free": free, "me": me["grips"]["ra"], "free2": free2, "girl": girl["grips"]["ra"], "gdad": gdad["grips"]["ra"]}
        vis(broom, 0, True); vis(broom, sentence_frames(ctx, 7)[-1], False)
        keys = [(0, "kid"), (a0 + 6, "free"), (grab, "me"), (fb[0], "kid"), (L(28)[0], "me"), (fb[2], "kid"), (L(30)[0], "me"),
                (a36 + 4, "free2"), (a37 + 14, "girl"), (a39 + 16, "gdad")]
        bal, knot, bfaces = toys.balloon(holders, keys)
        for n, tgt in holders.items():
            sg = toys.string(tgt, knot, name="string_" + n)
            on = [f for f, h in keys if h == n]; vis(sg, 0, keys[0][1] == n)
            for f, h in keys: vis(sg, f, h == n)
        # free2: the balloon drifting down to the girl after letting me go
        K._key(free2, "location", a36 + 4, (-4.0, -6.9, 8.4)); K._key(free2, "location", a37 + 14, (-3.3, -2.6, 2.4))

        # ---- 0: caught the string
        sf = sentence_frames(ctx, 0)
        at(me, 0, (0, -3.0, 0.35), -8, None); react(me, "smile", 1)
        pose(kid, 1, None, ra=(-40, 0, 10)); react(kid, "happy", 1); react(dad, "smile", 1)
        pose(kid, a0 + 6, 6, ra=(-60, 0, 25)); react(kid, "big_eyes", a0 + 8)
        pose(me, grab - 10, 12, ra=(-165, 0, 15)); react(me, "suspicious", grab - 8)
        ctx.sfx("whoosh", a0 + 6, 0.6); ctx.sfx("pop", grab)
        cam(st, "t0a", (8, -17, 6.5), (1.5, -3.2, 3.6), 32, a0, grab, (-3, 4, -1.2), (0, 0, 0.6))
        S.shot(st, "t0a", a0, grab - 4)
        c = cam(st, "t0b", (-0.4, -9.0, 4.6), (-1.4, -3.4, 5.2), 45, grab - 4, b0, (0.4, 1.6, 0.3), (0, 0, 0.2)); punch(c, grab, 1.25)
        S.shot(st, "t0b", grab - 4, b0)
        # ---- 1: his dad shook my hand
        a, b = L(1)
        turn(me, a + 2, (3.6, -3.4), 8); turn(dad, a + 2, (0, -3.0), 8); react(me, "nervous", a + 4); react(dad, "happy", a + 4)
        handshake(me, dad, a + 10, b - 2); ctx.sfx("handshake", a + 10, 0.8)
        orbit(st, "t1", (1.8, -3.2, 0.35), 9.5, 3.8, -30, 5, a, b, 38, target_h=3.8)
        S.shot(st, "t1", a, b)
        # ---- 2: DAD "Thank you. He's been holding that since kindergarten."
        a, b = L(2)
        turn(dad, a, (1.0, -12), 6); react(dad, "cry", a + 2, b + 10); ctx.sfx("sad", a + 2, 0.35)
        c = cam(st, "t2", (2.8, -9.5, 4.9), (3.4, -3.4, 4.6), 52, a, b, (0, 2.0, 0), (0, 0, 0)); punch(c, sentence_frames(ctx, 2)[-1], 1.15)
        S.shot(st, "t2", a, b, caption="high")
        # ---- 3: the kid was twenty-six
        a, b = L(3)
        react(kid, "grin", a); pose(kid, a, 6, ra=(0, 0, 0), la=(0, 0, 0))
        c = cam(st, "t3", (2.2, -9.0, 0.9), (1.9, -3.1, 1.2), 40, a, a + 18, (0, 0.6, 3.9), (0, 0, 3.6))
        punch(c, word_frame(ctx, 3, "twenty-six"), 1.4); ctx.sfx("boing", word_frame(ctx, 3, "twenty-six"))
        S.shot(st, "t3", a, b)
        # ---- 4: I sweep the street... reaching for a gum wrapper
        a, b = L(4); s2 = sentence_frames(ctx, 4)[-1]
        turn(me, a, -10, 6)
        for k, f in enumerate(range(a, s2, 9)): pose(me, f, 5, la=(-25 if k % 2 else 15, 0, -10), waist=(10, 0, 0))
        ctx.sfx("whoosh", a + 4, 0.35); ctx.sfx("whoosh", a + 22, 0.3)
        cam(st, "t4a", (2.6, -10.5, 3.4), (0, -3.0, 2.6), 32, a, s2, (-1.5, 1.2, -0.3), (0, 0, -0.2))
        S.shot(st, "t4a", a, s2)
        pose(me, s2 + 6, 10, waist=(55, 0, 0), la=(-70, 0, -10)); react(me, "determined", s2)
        c = cam(st, "t4b", (-1.6, -7.2, 0.9), (-0.6, -4.2, 0.5), 38, s2, b, (0.4, 0.8, 0), (0, 0, 0)); punch(c, word_frame(ctx, 4, "gum"), 1.3)
        ctx.sfx("pop", word_frame(ctx, 4, "gum"), 0.6)
        S.shot(st, "t4b", s2, b, caption="high")
        rest(me, b + 4, "waist", "la")
        # ---- 5: the kid ran off to finally have a childhood
        a, b = L(5)
        walk(kid, a + 2, b - 6, (1.9, -3.1, 0.35), (14.5, -7.5, 1.2), 7, 40); react(kid, "happy", a)
        for k, f in enumerate(range(b - 6, L(26)[0] - 10, 9)):  # bounce, bounce
            K._key(kid["root"], "location", f, (15.5, -8.5, 1.2 + (2.6 if k % 2 else 0)))
        ctx.sfx("boing", b - 4, 0.8); ctx.sfx("giggle", b - 10, 0.5)
        cam(st, "t5", (6, -14.5, 4.5), (4, -4.5, 2.5), 28, a, b, (6, 2, 0.5), (9, -2.5, 0.5))
        S.shot(st, "t5", a, b)
        # ---- 6: the balloon looked down at me
        a, b = L(6)
        toys.face(bfaces, a + 4, "suspicious"); react(me, "nervous", a + 10)
        c = cam(st, "t6", (0.6, -5.4, 2.4), (-1.5, -3.2, 9.0), 24, a, b, (0.3, 0.6, 0.2), (0, 0, 0)); punch(c, a + 6, 1.2)
        ctx.sfx("tick", a + 4, 0.4)
        S.shot(st, "t6", a, b)
        # ---- 7: then it went up. so did I.
        a, b = L(7); s2 = sentence_frames(ctx, 7)[-1]
        toys.face(bfaces, a + 2, "grin")
        lift = [(s2, 0.35), (s2 + 12, 2.0), (b + 30, 16), (L(26)[0], 40)]
        for f, z in lift: K._key(me["root"], "location", f, (0, -3.0, z))
        hang(me, s2 + 6, 8); react(me, "big_eyes", s2 + 2)
        for crowd_npc in crowd[:5] + [dad]: pose(crowd_npc, s2 + 10, 12, head=(-28, 0, 0)); react(crowd_npc, "shock", s2 + 8)
        ctx.sfx("whoosh", a + 2, 0.8); ctx.sfx("boing", s2, 0.7); ctx.sfx("wind", s2 + 6, 0.6)
        c = cam(st, "t7", (5, -15, 4.5), (0, -3, 5), 30, a, b, (2, 2, 12), (0, 0, 13)); shake(c, s2, 14, 0.35)
        S.shot(st, "t7", a, b)

        # ---- flashbacks (26, 27, 29): the kid at last year's parade
        for f in fb: at(kid, f, (1.9, -3.1, 0.35), -10, 1)
        a, b = L(26); react(kid, "sleepy", a); pose(kid, a, 1, ra=(-40, 0, 10))
        cam(st, "f26", (4.6, -13.0, 4.6), (1.9, -3.1, 3.8), 40, a, b, (-0.8, 1.5, 0), (0, 0, 0))
        S.shot(st, "f26", a, b, look="flashback")
        a, b = L(27); react(laugher, "happy", a); pose(laugher, a + 4, 6, head=(0, 0, -25))
        for f in range(a + 6, b, 5): pose(laugher, f, 2, waist=(-12 if (f // 5) % 2 else 4, 0, 0))
        at(laugher, a, (6.5, -5.0, 0.3), 70, 1)
        cam(st, "f27", (8.8, -12, 4.2), (6.5, -5.0, 4.2), 42, a, b, (-1, 1.2, 0), (0, 0, 0))
        ctx.sfx("giggle", a + 4, 0.45)
        S.shot(st, "f27", a, b, look="flashback")
        a, b = L(29); react(kid, "sad", a)
        cam(st, "f29", (1.9, -13, 3.0), (1.9, -3.1, 3.8), 32, a, b, (0, 2.5, 0.6), (0, 0, 0))
        S.shot(st, "f29", a, b, look="flashback")
        # crowd not looking up (31, second sentence)
        s31 = sentence_frames(ctx, 31)[-1]; a31, b31 = L(31)
        for cn in crowd: pose(cn, s31 - 2, 1, head=(30, 0, 0)); react(cn, "annoyed", s31 - 2)
        cam(st, "t31", (-3, -14, 3.5), (-3, -5, 3.2), 30, s31, b31, (2, 0, 0), (2, 0, 0))
        S.shot(st, "t31", s31, b31)

        # ---- 32: drums. the parade. one year later.
        a, b = L(32); sf = sentence_frames(ctx, 32)
        for cn in crowd: pose(cn, a - 1, 1, head=(0, 0, 0)); react(cn, "happy", a)
        for d in drummers:
            walk(d, a - 20, L(36)[0], value(d["root"], "location", 0), rel(value(d["root"], "location", 0), (-44, -2, 0)), 9, 18)
        for f in range(a, a + 40, 6): ctx.sfx("drums", a, 1.0); break
        c = cam(st, "t32a", (0, -12, 40), (0, 0, 2), 28, a, sf[-1], (0, 4, -32), (0, 0, 1.5)); S.shot(st, "t32a", a, sf[min(1, len(sf) - 1)])
        cam(st, "t32b", (-2, 5.2, 2.4), (6, 2.0, 3.2), 30, sf[min(1, len(sf) - 1)], b, (-1, 0, 0.4), (-6, 0, 0))
        S.shot(st, "t32b", sf[min(1, len(sf) - 1)], b)
        # ---- 33: I came down over row one (beard, birds, goose, truck)
        a, b = L(33); sf = sentence_frames(ctx, 33)
        at(me, a - 1, (-2.4, -6.5, 26), 180, 1); hang(me, a - 1, 1); react(me, "determined", a)
        K._key(me["root"], "location", b, (-2.6, -6.8, 9.5))
        trk.rotation_euler = (0, 0, 0); trk.keyframe_insert("rotation_euler", frame=a)
        for k, f in enumerate(range(a, b, 14)): trk.rotation_euler = (math.radians(8 if k % 2 else -8), 0, 0); trk.keyframe_insert("rotation_euler", frame=f)
        ctx.sfx("honk", sf[min(2, len(sf) - 1)]); ctx.sfx("tweet", sf[min(1, len(sf) - 1)], 0.8); ctx.sfx("wind", a, 0.4)
        cam(st, "t33a", (1, 4.5, 1.6), (-2.4, -6.5, 16), 24, a, sf[1], (-1, -1, 0), (0, 0, -3)); S.shot(st, "t33a", a, sf[1])
        c = cam(st, "t33b", (-1.8, 2.5, 17), (-2.4, -6.6, 15.8), 40, sf[1], b, (0, -1.0, -6), (0, 0, -6.2)); punch(c, sf[min(2, len(sf) - 1)], 1.2)
        S.shot(st, "t33b", sf[1], b, caption="high")
        # ---- 34: a little girl looked up at me
        a, b = L(34)
        pose(girl, a + 4, 10, head=(-22, 0, 0)); react(girl, "suspicious", a + 2); react(girl, "shock", a + 18)
        cam(st, "t34", (-2.0, 3.6, 2.6), (-3.0, -3.2, 3.2), 34, a, b, (0, -0.8, 0), (0, 0, 0)); ctx.sfx("pop", a + 18, 0.6)
        S.shot(st, "t34", a, b)
        # ---- 35: she laughed so hard she dropped her ice cream
        a, b = L(35)
        react(girl, "happy", a + 2)
        for f in range(a + 4, b + 8, 4): pose(girl, f, 2, waist=(-14 if (f // 4) % 2 else 2, 0, 0))
        vis(cream, a + 14, False); cream_drop.location = (-3.0, -2.6, 1.6); vis(cream_drop, 0, False); vis(cream_drop, a + 14, True)
        K._key(cream_drop, "location", a + 14, (-2.6, -2.6, 1.6), 1); K._key(cream_drop, "location", a + 26, (-2.4, -2.0, 0.45))
        K._key(cream_drop, "rotation_euler", a + 14, (0, 0, 0), 1); K._key(cream_drop, "rotation_euler", a + 26, (math.radians(110), 0, 0))
        ctx.sfx("giggle", a + 2); ctx.sfx("splat", a + 26)
        rest(girl, b + 14, "waist", ease=8)
        c = cam(st, "t35", (-2.0, 3.6, 3.0), (-3.0, -3.2, 2.9), 38, a, b, (0, -1.0, 0), (0, 0, 0)); punch(c, a + 4, 1.2)
        S.shot(st, "t35", a, b)
        # ---- 36: the balloon let go. I fell into a tuba.
        s2 = sentence_frames(ctx, 36)[-1]
        react(me, "big_eyes", a36 + 4); rest(me, a36 + 6, "ra", ease=4)
        bell = (-8.5 + 1.6, 1.2 + 0.2, 2.0 + 0.3 + 3.75 * 1.3)
        K._key(me["root"], "location", a36 + 4, (-2.6, -6.8, 9.5), 1)
        K._key(me["root"], "location", s2 + 8, (bell[0], bell[1], bell[2] + 1.2))
        K._key(me["root"], "rotation_euler", a36 + 4, (0, 0, 0), 1); K._key(me["root"], "rotation_euler", s2 + 8, (math.radians(180), 0, 0))
        vis(trk, a36 + 4, False)
        ctx.sfx("pop", a36 + 4); ctx.sfx("whoosh", a36 + 8); ctx.sfx("tuba", s2 + 8, 1.2)
        c = cam(st, "t36a", (3, 5.5, 9), (-2.6, -6.6, 10), 30, a36, s2, (-3, 0, -2), (-3, 5, -4)); S.shot(st, "t36a", a36, s2)
        c = cam(st, "t36b", (-2.6, 5.6, 6.4), (bell[0], bell[1], bell[2] + 0.6), 34, s2, b36, (0.6, -0.6, 0), (0, 0, 0)); shake(c, s2 + 8, 14, 0.5)
        S.shot(st, "t36b", s2, b36)
        # ---- 37: the string landed in her hand
        pose(girl, a37 + 4, 8, head=(-10, 0, 0), ra=(-75, 0, 10)); react(girl, "big_eyes", a37 + 14)
        c = cam(st, "t37", (-2.0, 2.6, 2.4), (-3.1, -3.0, 2.3), 40, a37, b37, (0, -0.6, 0), (0, 0, 0)); punch(c, a37 + 14, 1.25)
        ctx.sfx("pop", a37 + 14)
        S.shot(st, "t37", a37, b37)
        # ---- 38: she wasn't scared. she was eight. best day of her life.
        a, b = L(38); sf = sentence_frames(ctx, 38)
        react(girl, "happy", a); pose(girl, a + 4, 10, ra=(-170, 0, 6), head=(-10, 0, 0))
        K._key(girl["root"], "location", a + 6, (-3.0, -3.2, 0.3), 1); K._key(girl["root"], "location", b, (-3.0, -3.2, 2.6))
        toys.face(bfaces, a, "happy"); ctx.sfx("sparkle", sf[-1])
        orbit(st, "t38", (-3.0, -3.2, 2.6), 7.5, 1.2, 160, 200, a, b, 32, target_h=1.6)
        S.shot(st, "t38", a, b)
        # ---- 39: her dad grabbed the string to stop her
        walk(gdad, a39 - 14, a39 + 4, (-7.2, -3.9, 0.3), (-4.8, -3.4, 0.3), 9, 24)
        pose(gdad, a39 + 10, 8, ra=(-165, 0, -10)); turn(gdad, a39 + 8, (-3, -3.2), 6); react(gdad, "big_eyes", a39 + 6)
        K._key(girl["root"], "location", a39 + 16, (-3.0, -3.2, 2.6), 1); K._key(girl["root"], "location", a39 + 26, (-3.0, -3.2, 0.3))
        rest(girl, a39 + 18, "ra")
        K._key(gdad["root"], "location", a39 + 16, (-4.8, -3.4, 0.3), 1); K._key(gdad["root"], "location", L(42)[0], (-4.8, -3.4, 22))
        ctx.sfx("pop", a39 + 16); ctx.sfx("whoosh", a39 + 20, 0.6)
        cam(st, "t39", (-1.5, 5.0, 3.6), (-3.9, -3.3, 4.0), 32, a39, b39, (0, -0.8, 1.2), (0, 0, 1.4))
        S.shot(st, "t39", a39, b39)
        # ---- 40: his daughter shook his hand for a full minute (callback)
        a, b = L(40)
        turn(girl, a, (-4.8, -3.4), 6); react(gdad, "nervous", a); react(girl, "happy", a)
        handshake(girl, gdad, a + 4, b - 2, "la", "la"); ctx.sfx("handshake", a + 4, 0.8)
        orbit(st, "t40", (-3.9, -3.3, 1.5), 8.0, 2.4, 198, 165, a, b, 34, target_h=2.4)
        S.shot(st, "t40", a, b)
        # ---- 41: GIRL "Thank you, Dad."
        a, b = L(41)
        turn(girl, a, 180, 6); pose(girl, a + 2, 8, head=(-18, 0, 0)); react(girl, "happy", a)
        c = cam(st, "t41", (-2.6, 2.0, 3.3), (-3.0, -3.2, 3.3), 45, a, b, (0, -0.6, 0), (0, 0, 0)); punch(c, a + 2, 1.15)
        S.shot(st, "t41", a, b, caption="high")
        # ---- 42b: every morning she waves
        a, b = L(42); s2 = sentence_frames(ctx, 42)[-1]
        at(girl, s2 - 1, (-3.0, -3.2, 0.3), 180, 1); react(girl, "happy", s2)
        for k, f in enumerate(range(s2, b + 6, 7)): pose(girl, f, 3, ra=(-160, 0, 25 if k % 2 else -10))
        st.sun.rotation_euler = (math.radians(75), 0, math.radians(-120)); st.sun.keyframe_insert("rotation_euler", frame=s2)
        st.sun.rotation_euler = (math.radians(48), 0, math.radians(-35)); st.sun.keyframe_insert("rotation_euler", frame=s2 - 1)
        cam(st, "t42", (-2.2, 4.0, 1.2), (-3.0, -3.2, 3.9), 28, s2, b, (0, -1.0, 0.3), (0, 0, 1.0))
        S.shot(st, "t42", s2, b)
        ctx.sfx("tweet", s2 + 4, 0.6)
    return st


def place_beard(ctx, av):
    b = K.place(ctx.D, ctx.M["beard"], (0, 0, 0), 0, 0.85, "beard"); b.parent = av["head"]; b.location = (0, -0.42, -0.2)
    return b


# ---------------- sky (one big scene with areas far apart) ----------------
AREAS = {"stadium": (0, -30, 66), "canada": (1000, -30, 66), "ocean": (2000, -30, 38), "paris": (4000, -20, 18),
         "sky": (5000, 0, 60), "iceland": (7000, 0, 55)}


def sky(ctx):
    S, L = ctx.short, ctx.L
    st = Set("sky", sky=(40, 130, 255), horizon=(200, 230, 255), sun=(40, 0, -30), sun_energy=5)
    with st:
        # stadium
        prim("box", (600, 600, 0.2), (0, 0, -0.1), mat((110, 190, 90), 0.9))
        for x in range(-150, 151, 22):
            for y in range(-150, 151, 22):
                if abs(x) > 60 or abs(y) > 45: toys.house(x + random.uniform(-4, 4), y + random.uniform(-4, 4), random.choice((0, 90, 180)), 9, 8, 7)
        stad, crowd = toys.stadium(0, 0)
        toys.clouds(10, (-80, -70, 50), (80, 40, 85), 3, 7)
        # canada: forest and lakes
        prim("box", (700, 700, 0.2), (1000, 0, -0.1), mat((70, 150, 80), 0.9))
        for _ in range(170): toys.pine(1000 + random.uniform(-120, 120), random.uniform(-40, 160), random.uniform(1.5, 2.6))
        for x, y, r in ((990, 40, 30), (1040, 90, 40)): prim("ball", (r * 2, r * 1.3, 0.4), (x, y, 0.1), mat((60, 150, 240), 0.1))
        toys.clouds(8, (920, -70, 50), (1080, 40, 85), 3, 7)
        # ocean + cruise ship
        prim("box", (800, 800, 0.2), (2000, 0, -0.1), mat((40, 140, 240), 0.08))
        sh = toys.ship(2000, -10); sh.rotation_euler = (0, 0, math.radians(70))
        toys.clouds(8, (1920, -70, 45), (2080, 40, 70), 3, 7)
        # london: river, buildings and the clock tower
        toys._A[0] = ctx.A
        prim("box", (600, 600, 0.2), (3000, 0, -0.1), mat((120, 180, 100), 0.9)); prim("box", (600, 40, 0.15), (3000, 30, 0.05), mat((70, 140, 200), 0.1))
        tw, top = toys.tower(3000, 0)
        for x in range(-90, 91, 18):
            for y in (-30, -55, 60): toys.house(3000 + x, y, 0, 10, 9, random.uniform(9, 16), color=random.choice([(220, 200, 160), (200, 170, 140), (230, 225, 210)]))
        toys.clouds(8, (2920, -70, 55), (3080, 40, 90), 3, 7)
        # paris rooftops
        prim("box", (600, 600, 0.2), (4000, 0, -0.1), mat((200, 200, 205), 0.8))
        for x in range(-60, 61, 9):
            for y in range(-40, 61, 10): toys.house(4000 + x, y, 0, 8, 9, 10, color=(235, 225, 205), roof=(80, 95, 120))
        toys.clouds(6, (3940, -60, 40), (4060, 40, 70), 3, 6)
        # open sky
        toys.clouds(40, (4880, -80, 20), (5120, 120, 110), 3, 9)
        # iceland
        prim("box", (600, 600, 0.2), (7000, 0, -0.1), mat((240, 245, 252), 0.85))
        for _ in range(20): prim("box", (random.uniform(10, 30), random.uniform(10, 30), random.uniform(4, 16)), (7000 + random.uniform(-100, 100), random.uniform(-20, 140), 0), mat((190, 225, 250), 0.15), rot=(0, 0, random.uniform(0, 90)))
        toys.clouds(10, (6920, -70, 40), (7080, 60, 80), 3, 7)
        # mom's kitchen (far away)
        kx = 6000
        prim("box", (20, 20, 0.2), (kx, 0, -0.1), mat((230, 210, 170), 0.6)); prim("box", (20, 0.4, 12), (kx, 4, 6), mat((250, 230, 140), 0.8))
        prim("box", (0.4, 20, 12), (kx - 6, 0, 6), mat((250, 230, 140), 0.8)); prim("box", (6, 2.5, 3), (kx + 3, 2.6, 1.5), mat((250, 250, 250), 0.4), bevel=0.1)
        kl = bpy.data.lights.new("kitchen", "AREA"); kl.energy = 2500; kl.size = 12; ko = bpy.data.objects.new("kitchen", kl); st.link(ko); ko.location = (kx, -4, 10)

        me = blocky.build(ctx.D); idle(me); idle(me, ("ll", "rl"), 0.07, 30)
        bal, knot, bfaces = toys.balloon({"me": me["grips"]["ra"]}, [(0, "me")])
        toys.string(me["grips"]["ra"], knot, name="sky_string")
        bd = place_beard(ctx, me); show_between(bd, 0, 0); vis(bd, L(21)[0] + 1, True)  # beard grows during the trip
        K._key(bd, "scale", L(17)[0], (0.01,) * 3, 1); K._key(bd, "scale", L(31)[1], (0.85,) * 3)
        hang(me, 0, None)

        def put(f, area, d=(0, 0, 0), yaw=0, drift=(1.2, 0, 0.6), until=None):
            p = rel(AREAS[area], d); at(me, f, p, yaw, 1)
            if until: K._key(me["root"], "location", until, rel(p, drift))
            return p

        # ---- 8: over the stadium, the wave, I did it too
        a, b = L(8); sf = sentence_frames(ctx, 8)
        p = put(a, "stadium", until=b); toys.wave(crowd, sf[1] - 10, b + 10, 1.2)
        react(me, "happy", a); pose(me, sf[-1], 6, la=(-175, 0, -15)); pose(me, sf[-1] + 8, 6, la=(-60, 0, -20)); pose(me, sf[-1] + 16, 6, la=(-175, 0, -15))
        ctx.sfx("wind", a, 0.4); ctx.sfx("giggle", sf[1], 0.2)
        cam(st, "s8a", rel(p, (9, -14, 10)), (0, 0, 0), 26, a, sf[-1], (-3, 2, -3), (0, 0, 0)); S.shot(st, "s8a", a, sf[-1])
        c = cam(st, "s8b", rel(p, (3, -9, 3.5)), rel(p, (0, 0, 3.6)), 36, sf[-1], b, (-1, 1, 0), (0, 0, 0)); punch(c, sf[-1] + 4, 1.15)
        S.shot(st, "s8b", sf[-1], b)
        # ---- 9-12: the helicopter
        a9, b9 = L(9); a12, b12 = L(12)
        p = put(a9, "stadium", (0, 0, 2), until=b12, drift=(1.5, 0, 0.5))
        heli = toys.helicopter(0, 0, 0)
        K._key(heli, "location", a9 - 1, rel(p, (40, 6, 6)), 1); K._key(heli, "location", a9 + 30, rel(p, (8.5, 0.5, 4.0)))
        K._key(heli, "location", b12, rel(p, (10, 0.5, 4.5)))
        pilot = blocky.build(ctx.D, "pilot", PILOT); pilot["root"].parent = heli; pilot["root"].location = (-2.3, -1.2, -2.6)
        pilot["root"].rotation_euler = (0, 0, math.radians(-90)); idle(pilot, ("head",), 0.04, 30)
        pose(pilot, 0, None, waist=(0, -18, 0), la=(-40, 0, -20))
        react(me, "shock", a9 + 20); ctx.sfx("wind", a9, 0.8)
        cam(st, "s9", rel(p, (3, -16, 4)), rel(p, (5, 0, 4)), 30, a9, b9, (-2, 3, 0.5), (0, 0, 0)); S.shot(st, "s9", a9, b9)
        a, b = L(10); react(pilot, "suspicious", a)
        c = cam(st, "s10", rel(p, (3.6, -7.5, 6.6)), rel(p, (6.2, -0.7, 6.4)), 46, a, b, (0, 0.8, 0), (0, 0, 0)); S.shot(st, "s10", a, b, caption="high")
        a, b = L(11); react(me, "nervous", a); react(me, "happy", a + 8)
        c = cam(st, "s11", rel(p, (1.0, -6.5, 5.0)), rel(p, (0, 0, 4.7)), 50, a, b, (0, 0.8, 0), (0, 0, 0)); punch(c, a + 6, 1.2)
        S.shot(st, "s11", a, b)
        a, b = L(12); react(pilot, "grin", a); react(me, "big_eyes", a + 10)
        ctx.overlay("live_banner.png", a + 6, L(13)[0] + 20, 7); ctx.sfx("live", a + 6)
        c = cam(st, "s12", rel(p, (4, -11, 5)), rel(p, (4, 0, 5)), 34, a, b, (0, 2, 0), (0, 0, 0)); punch(c, a + 8, 1.25); shake(c, a + 8, 10, 0.2)
        S.shot(st, "s12", a, b)
        # ---- 13: Canada, a goose joined me
        a, b = L(13); sf = sentence_frames(ctx, 13)
        p = put(a, "canada", until=b, drift=(3, 0, 0)); react(me, "smile", a)
        g = toys.goose(0, 0, 0, 1.2, "goose_ca"); K._key(g["root"], "location", a - 1, rel(p, (-12, -3, 5)), 1)
        K._key(g["root"], "location", sf[1], rel(p, (2.4, -1.2, 4.2))); K._key(g["root"], "location", b, rel(p, (5.4, -1.2, 4.6)))
        g["root"].rotation_euler = (0, 0, math.radians(90)); g["root"].keyframe_insert("rotation_euler", frame=sf[1])
        g["root"].rotation_euler = (0, 0, math.radians(-90)); g["root"].keyframe_insert("rotation_euler", frame=sf[-1])
        toys.flap(g, a, b + 10); react(me, "suspicious", sf[1] + 4); react(me, "annoyed", sf[-1] + 4)
        ctx.sfx("honk", sf[1]); ctx.sfx("honk", sf[-1] + 6, 0.7)
        cam(st, "s13a", rel(p, (6, -18, 10)), rel(p, (0, 0, -20)), 26, a, sf[1], (0, 4, -4), (0, 0, 10)); S.shot(st, "s13a", a, sf[1])
        c = cam(st, "s13b", rel(p, (2, -9, 4.6)), rel(p, (2, 0, 4.4)), 40, sf[1], b, (2.5, 0.8, 0.2), (3, 0, 0)); punch(c, sf[-1], 1.15)
        S.shot(st, "s13b", sf[1], b)
        # ---- 14: ocean, a cruise ship threw me a sandwich
        a, b = L(14); sf = sentence_frames(ctx, 14)
        p = put(a, "ocean", until=b, drift=(1, 0, 0.3)); react(me, "happy", sf[-1])
        sw = toys.sandwich(); vis(sw, 0, False); vis(sw, a + 6, True)
        K._key(sw, "location", a + 6, (2000, -12, 14), 1); K._key(sw, "location", sf[-1] - 2, rel(p, (1.6, -0.4, 2.4)))
        K._key(sw, "rotation_euler", a + 6, (0, 0, 0), 1); K._key(sw, "rotation_euler", sf[-1] - 2, (math.radians(720), math.radians(360), 0))
        sw2 = toys.sandwich(); sw2.parent = me["grips"]["la"]; sw2.location = (0, -0.3, 0); sw2.scale = (0.8, 0.8, 0.8); show_between(sw2, sf[-1] - 2, b)
        vis(sw, sf[-1] - 2, False); pose(me, sf[-1] - 8, 6, la=(-95, 0, -10)); ctx.sfx("whoosh", a + 8, 0.7); ctx.sfx("pop", sf[-1] - 2); ctx.sfx("nom", sf[-1] + 8, 0.7)
        cam(st, "s14a", rel(p, (4, -9, 7)), (2000, -10, 2), 30, a, sf[-1], (-1, 1.5, -1), (0, 0, 0)); S.shot(st, "s14a", a, sf[-1])
        c = cam(st, "s14b", rel(p, (2.5, -7, 4.0)), rel(p, (0.8, 0, 3.4)), 42, sf[-1], b, (0, 1, 0), (0, 0, 0)); punch(c, sf[-1] + 2, 1.2)
        S.shot(st, "s14b", sf[-1], b)
        # ---- 15: London, on top of the tower for one minute
        a, b = L(15); sf = sentence_frames(ctx, 15)
        at(me, a, (3000, -0.5, top - 4.3), 0, 1); pose(me, a, 1, ll=(-88, 0, 6), rl=(-88, 0, -6), ra=(-172, 0, 6), la=(-10, 0, -20)); react(me, "smile", a); react(me, "annoyed", sf[-1])
        ctx.sfx("bell", a + 4, 1.0); ctx.sfx("tick", sf[-1], 0.6)
        orbit(st, "s15a", (3000, 0, top), 30, -6, -40, -10, a, sf[-1], 28, target_h=-8); S.shot(st, "s15a", a, sf[-1])
        c = cam(st, "s15b", (3001.5, -8.5, top + 3.5), (3000, -0.5, top + 3.8), 45, sf[-1], b, (0, 1.2, 0), (0, 0, 0)); punch(c, sf[-1] + 6, 1.15)
        S.shot(st, "s15b", sf[-1], b, caption="high")
        # ---- 16: Paris, a mime pretended to pull me down
        a, b = L(16); sf = sentence_frames(ctx, 16)
        p = put(a, "paris"); hang(me, a, 1)
        mime = blocky.build(ctx.D, "mime", MIME); at(mime, a - 1, (4000, -17, 12.3), 180, 1); react(mime, "determined", a)
        for k, f in enumerate(range(a + 4, sf[-1] + 10, 8)):
            pose(mime, f, 4, ra=(-150 if k % 2 else -110, 0, 10), la=(-110 if k % 2 else -150, 0, -10), waist=(10 if k % 2 else 4, 0, 0))
            K._key(me["root"], "location", f, rel(p, (0, 0, -0.9 * (k + 1))))
        K._key(me["root"], "location", b, rel(p, (0.6, 0, 1.5))); react(me, "nervous", a + 8); react(me, "happy", sf[-1] + 8)
        ctx.sfx("whoosh", a + 6, 0.4); ctx.sfx("boing", sf[-1] + 6)
        cam(st, "s16", (4013, -32, 13), (4000, -18, 16), 30, a, b, (-4, 2, 1), (0, 0, 0.5)); S.shot(st, "s16", a, b)
        # ---- 17: I tried everything
        a, b = L(17); p = put(a, "sky", until=b); react(me, "determined", a)
        c = cam(st, "s17", rel(p, (0.4, -6.5, 4.8)), rel(p, (0, 0, 4.7)), 50, a, b, (0, 1.0, 0), (0, 0, 0)); punch(c, a + 3, 1.3)
        ctx.sfx("pop", a + 3, 0.7); S.shot(st, "s17", a, b)
        # ---- 18: let go with one hand, it held on with both
        a, b = L(18); sf = sentence_frames(ctx, 18); p = put(a, "sky", (30, 0, 0), until=b)
        react(me, "determined", a); pose(me, a + 6, 6, la=(-172, 0, -6))
        pose(me, a + 18, 6, la=(-20, 0, -18)); toys.face(bfaces, sf[-1], "grin"); react(me, "annoyed", sf[-1] + 6)
        for k, f in enumerate(range(sf[-1] + 4, b, 6)): pose(me, f, 3, ra=(-172, 0, 18 if k % 2 else -8))
        ctx.sfx("whoosh", a + 18, 0.4); ctx.sfx("boing", sf[-1] + 4, 0.6)
        cam(st, "s18", rel(p, (3, -9, 7)), rel(p, (0, 0, 7.5)), 34, a, b, (-1.5, 1.5, 0), (0, 0, 0)); S.shot(st, "s18", a, b)
        # ---- 19: tied to a truck, now I have a truck (it stays for the rest of the trip)
        a, b = L(19); sf = sentence_frames(ctx, 19); p = put(a, "sky", (60, 0, 0), until=b)
        trk = toys.truck(); trk.parent = me["root"]; trk.location = (0, 0, -6.5); trk.scale = (0.7, 0.7, 0.7); show_between(trk, sf[-1] - 2, None)
        rope = prim("cylY", (0.06, 0.06, 6.5), (0, 0, -3.25), mat((230, 230, 230), 0.5), parent=me["root"]); show_between(rope, sf[-1] - 2, None)
        for k, f in enumerate(range(sf[-1], L(32)[0], 16)): trk.rotation_euler = (math.radians(10 if k % 2 else -10), 0, 0); trk.keyframe_insert("rotation_euler", frame=f)
        react(me, "suspicious", a); react(me, "nervous", sf[-1] + 4); ctx.sfx("boing", sf[-1], 0.9); shake_c = None
        cam(st, "s19a", rel(p, (2, -8, 3)), rel(p, (0, 0, 3)), 36, a, sf[-1], (0, 1, 0), (0, 0, 0)); S.shot(st, "s19a", a, sf[-1])
        c = cam(st, "s19b", rel(p, (6, -16, -8)), rel(p, (0, 0, -1)), 28, sf[-1], b, (-1, 1, 2), (0, 0, 0)); shake(c, sf[-1], 10, 0.3)
        S.shot(st, "s19b", sf[-1], b)
        # ---- 20: asked a bird to pop it, the bird asked for a ride
        a, b = L(20); sf = sentence_frames(ctx, 20); p = put(a, "sky", (90, 0, 0), until=b)
        bb = toys.bird(0, 0, 0, (90, 170, 250), 0.9)
        K._key(bb, "location", a - 1, rel(p, (8, -2, 12)), 1); K._key(bb, "location", sf[-1], rel(p, (-1.4, 0.1, 11.6)))
        react(me, "grin", a); toys.face(bfaces, sf[-1] + 2, "suspicious"); react(me, "annoyed", sf[-1] + 6)
        ctx.sfx("tweet", a + 6); ctx.sfx("tweet", sf[-1] + 4)
        cam(st, "s20", rel(p, (4, -12, 8)), rel(p, (0, 0, 8)), 30, a, b, (-2, 2, 0.5), (0, 0, 0.5)); S.shot(st, "s20", a, b)
        # ---- 21: breakfast in a cloud, rent to a weather balloon
        a, b = L(21); sf = sentence_frames(ctx, 21); p = put(a, "sky", (120, 0, 0), until=b)
        toys.cloud(*rel(p, (0, 0.5, 1.5)), 1.4); bowl = prim("cylY", (1.0, 1.0, 0.45), (0, -0.4, 0.1), mat((250, 250, 250), 0.3), parent=me["grips"]["la"]); show_between(bowl, a, sf[-1])
        pose(me, a + 4, 6, la=(-80, 0, -10)); react(me, "happy", a)
        for f in range(a + 8, sf[-1] - 4, 10): pose(me, f, 4, head=(12, 0, 0)); pose(me, f + 5, 4, head=(-4, 0, 0))
        wb = toys.weather_balloon(*rel(p, (5.5, 1.0, 9))); coin = prim("cylY", (0.45, 0.45, 0.1), (0, -0.3, 0), mat((250, 210, 60), 0.2, metal=1), rot=(90, 0, 0), parent=me["grips"]["la"])
        show_between(coin, sf[-1] + 2, b); pose(me, sf[-1] + 4, 8, la=(-80, 0, 45)); ctx.sfx("nom", a + 8, 0.6); ctx.sfx("coin", sf[-1] + 10)
        cam(st, "s21a", rel(p, (1.5, -8, 5)), rel(p, (0, 0, 4.0)), 40, a, sf[-1], (0, 1, 0), (0, 0, 0)); S.shot(st, "s21a", a, sf[-1])
        cam(st, "s21b", rel(p, (2, -16, 6)), rel(p, (3, 0, 6)), 32, sf[-1], b, (1, 2, 0), (0, 0, 0)); S.shot(st, "s21b", sf[-1], b)
        # ---- 22-24: mom's call, mostly rain
        a, b = L(22); p = put(a, "sky", (150, 0, 0), until=L(24)[1])
        ph = toys.phone(); ph.parent = me["grips"]["la"]; ph.location = (0, -0.1, 0); show_between(ph, a, L(24)[1])
        pose(me, a + 4, 8, la=(-150, 0, -50)); react(me, "smile", a); ctx.sfx("ding", a + 2, 0.6)
        cam(st, "s22", rel(p, (2, -7, 5)), rel(p, (0, 0, 4.6)), 42, a, b, (0, 1, 0), (0, 0, 0)); S.shot(st, "s22", a, b)
        a, b = L(23); mom = blocky.build(ctx.D, "mom", MOM); at(mom, 0, (kx, 0, 0), 0, None); idle(mom, ("head",), 0.04, 30)
        mph = toys.phone(); mph.parent = mom["grips"]["la"]; mph.location = (0, -0.1, 0); pose(mom, 0, None, la=(-150, 0, -50)); react(mom, "suspicious", a)
        c = cam(st, "s23", (kx + 1.2, -7.5, 4.6), (kx, 0, 4.5), 45, a, b, (0, 1, 0), (0, 0, 0)); punch(c, a + 2, 1.15); S.shot(st, "s23", a, b, caption="high")
        a, b = L(24); rc = toys.cloud(*rel(p, (0.5, 0.5, 13)), 1.6); rain = empty("rain", rel(p, (0, 0, 0)))
        for _ in range(60): prim("cylY", (0.05, 0.05, 1.0), (random.uniform(-3, 3), random.uniform(-2, 2), random.uniform(0, 12)), mat((150, 200, 255), 0.1, alpha=0.7), parent=rain)
        show_between(rc, a - 1, b + 2); show_between(rain, a - 1, b + 2)
        rain.location = rel(p, (0.5, 0.5, 2)); rain.keyframe_insert("location", index=2, frame=a); rain.location.z -= 30; rain.keyframe_insert("location", index=2, frame=b + 2)
        react(me, "annoyed", a); ctx.sfx("wind", a, 0.5)
        cam(st, "s24", rel(p, (1.5, -9, 6)), rel(p, (0, 0, 6)), 36, a, b, (0, 1.2, 0), (0, 0, 0.5)); S.shot(st, "s24", a, b)
        # ---- 25: then I figured out the rule (light bulb)
        a, b = L(25); p = put(a, "sky", (180, 0, 0), until=b); react(me, "suspicious", a); react(me, "big_eyes", a + 12)
        bulb = empty("bulb"); bulb.parent = me["head"]; bulb.location = (0.9, 0, 2.2)
        prim("ball", (0.9, 0.9, 1.1), (0, 0, 0), mat((255, 230, 80), 0.2, emit=6), parent=bulb); prim("cylY", (0.45, 0.45, 0.4), (0, 0, -0.65), mat((170, 170, 175), 0.3, metal=1), parent=bulb)
        show_between(bulb, a + 12, b)
        ctx.sfx("ding", a + 12)
        c = cam(st, "s25", rel(p, (1.2, -7, 5.5)), rel(p, (0.3, 0, 5.4)), 45, a, b, (0, 1, 0), (0, 0, 0)); punch(c, a + 12, 1.2); S.shot(st, "s25", a, b)
        # ---- 28: the rule (balloon close, smug)
        a, b = L(28); p = put(a, "sky", (210, 0, 0), until=b); toys.face(bfaces, a, "grin"); react(me, "annoyed", a)
        orbit(st, "s28", rel(p, (0, 0, 10)), 7, 0, -40, 30, a, b, 34, target_h=-1.5); S.shot(st, "s28", a, b)
        # ---- 30: so I needed one laugh. From a mile up. (pull back)
        a, b = L(30); sf = sentence_frames(ctx, 30); p = put(a, "sky", (240, 0, 0)); react(me, "determined", a)
        cam(st, "s30a", rel(p, (0.6, -6, 5)), rel(p, (0, 0, 4.7)), 45, a, sf[-1], (0, 1, 0), (0, 0, 0)); S.shot(st, "s30a", a, sf[-1])
        cam(st, "s30b", rel(p, (2, -12, 6)), rel(p, (0, 0, 4)), 30, sf[-1], b, (20, -120, 40), (0, 0, -10)); ctx.sfx("whoosh", sf[-1], 0.8)
        S.shot(st, "s30b", sf[-1], b)
        # ---- 31a: geese spelling HA HA (top down)
        a31, b31 = L(31); s31 = sentence_frames(ctx, 31)[-1]; gx, gy, gz = rel(AREAS["sky"], (300, 0, -10))
        cells = []
        for ox in (0, 22):
            cells += [(ox + 0, y) for y in range(0, 10, 2)] + [(ox + 6, y) for y in range(0, 10, 2)] + [(ox + 2, 4), (ox + 4, 4)]  # H
            cells += [(ox + 10, y) for y in range(0, 10, 2)] + [(ox + 16, y) for y in range(0, 10, 2)] + [(ox + 12, 8), (ox + 14, 8), (ox + 12, 4), (ox + 14, 4)]  # A
        for k, (cx, cy) in enumerate(cells):
            g = toys.goose(gx + cx * 1.6 - 32, gy + cy * 1.6, gz, 1.3, f"spell{k}"); g["root"].rotation_euler = (0, 0, math.radians(90)); toys.flap(g, a31, s31 + 6, 10)
        ctx.sfx("honk", a31 + 4); ctx.sfx("honk", a31 + 14, 0.7)
        cam(st, "s31", (gx - 7, gy - 10, gz + 38), (gx - 7, gy + 7, gz), 34, a31, s31, (0, 3, -6), (0, 0, 0)); S.shot(st, "s31", a31, s31)
        # ---- 42a / 43: Iceland, the girl's dad and a goose waving back
        a, b = L(42); s2 = sentence_frames(ctx, 42)[-1]
        dadsky = blocky.build(ctx.D, "gdad_sky", GIRLDAD); idle(dadsky, ("head", "ll", "rl"), 0.06, 30)
        p = AREAS["iceland"]; at(dadsky, a - 1, p, 0, 1); K._key(dadsky["root"], "location", L(43)[1], rel(p, (3, 0, 1))); hang(dadsky, a - 1, 1)
        hide_me = put(a - 1, "iceland", (500, 0, 0))  # keep the narrator out of these shots
        b2, k2, f2 = toys.balloon({"d": dadsky["grips"]["ra"]}, [(0, "d")], name="balloon_ice"); toys.string(dadsky["grips"]["ra"], k2, name="ice_string")
        react(dadsky, "nervous", a); g = toys.goose(0, 0, 0, 1.2, "goose_ice")
        K._key(g["root"], "location", a - 1, rel(p, (2.6, -1.0, 4.4)), 1); K._key(g["root"], "location", L(43)[1], rel(p, (5.6, -1.0, 5.4)))
        g["root"].rotation_euler = (0, 0, math.radians(-90)); toys.flap(g, a, L(43)[1] + 20, 10)
        cam(st, "s42", rel(p, (4, -16, 2)), rel(p, (1, 0, 4)), 28, a, s2, (-2, 4, 2), (0, 0, 0)); S.shot(st, "s42", a, s2)
        a, b = L(43)
        w, sd = g["wings"][0]
        for k, f in enumerate(range(a + 4, b + 40, 7)): w.rotation_euler = (0, math.radians(sd * (95 if k % 2 else 30)), math.radians(40)); w.keyframe_insert("rotation_euler", frame=f)
        react(dadsky, "happy", a + 10); ctx.sfx("honk", a + 4, 0.8); ctx.sfx("sparkle", a + 12)
        c = cam(st, "s43", rel(p, (4.5, -9, 5)), rel(p, (2.6, -1, 4.8)), 40, a, S.total, (0, 2, 0), (0, 0, 0)); punch(c, a + 6, 1.15)
        S.shot(st, "s43", a, S.total + 1)
    return st


def build(ctx):
    town(ctx); sky(ctx)
