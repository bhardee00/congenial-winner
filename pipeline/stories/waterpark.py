""""A Karen Didn't Want My Baby Brother At The Water Park" - reference #3 style with the user's feedback applied:
third-person scenes where every narrated action is acted out on screen, shots of ~2-4 s that let the action finish,
a busy background (swimmers bob, people walk past, toddlers splash), mouths moving on every spoken line, real Roblox
hair (free Creator Store accessories), no texture VFX (splashes are simple droplets), UPPERCASE captions at the top
with a thick stroke. Voices 1.30x / 1.50x with action beats after the big moments.
Line numbers follow stories/waterpark.json (0-23). The set is stories/waterpark_set.py."""
import math, random
from mathutils import Vector, Matrix
import shortkit as K
from shortkit import Set, prim, mat, empty, show_between, pose, rest, at, turn, sit, idle, shake
import blocky
from avatar import react
from storykit import Kit, hold
from acting import act, tilt, chatter, bounce_walk
import waterpark_set as WS

random.seed(21)
SKIN, TAN, BROWN = (234, 190, 150), (204, 142, 105), (150, 100, 70)
HAIR = {"karen": 1012594937, "mom": 8199034057, "grandma": 15440914286,
        "x1": 11268431947, "x2": 4887515664, "x3": 10976405810, "x4": 9661319036}
WZ = WS.WATER_Z


def fr(pos, face, head, dist=3.0, ang=0.0, dz=0.15):
    yaw = math.radians(K.yaw_to(pos, face))
    d = Matrix.Rotation(math.radians(ang), 3, 'Z') @ Vector((math.sin(yaw), -math.cos(yaw), 0))
    return (pos[0] + d.x * dist, pos[1] + d.y * dist, head + dz), (pos[0], pos[1], head)


def build(ctx):
    S, L, A, D = ctx.short, ctx.L, ctx.A, ctx.D
    kit = Kit(ctx); seg, wf, sh = kit.seg, kit.wf, kit.sh

    def shf(st, f0, f1, who, dist=3.2, ang=0.0, lens=26, push=0.08, dz=0.2, **kw):
        loc, tgt = fr(*who, dist=dist, ang=ang, dz=dz)
        return sh(st, f0, f1, loc, tgt, lens, dl=tuple((t - l) * push for l, t in zip(loc, tgt)), **kw)

    def person(name, lk, hair=None, loc=(0, -300, 0), yaw=0):
        a = blocky.build(D, name, lk); at(a, 0, loc, yaw, ease=1); idle(a, ("head",), 0.02, 50)
        if hair: blocky.wear(D, a, hair)
        return a

    def drops(center, f, n=14, spread=2.5, up=3.0, size=0.28, col=(185, 225, 255)):
        """A splash made of droplets flying out and falling (plain geometry, no VFX textures)."""
        with pk: _drops(center, f, n, spread, up, size, col)

    def _drops(center, f, n, spread, up, size, col):
        m = mat(col, 0.05, emit=0.3); c = Vector(center)
        for k in range(n):
            a = k / n * math.tau + random.uniform(-0.3, 0.3); r = spread * random.uniform(0.5, 1.0)
            d = prim("ball", (size, size, size * 1.3), (0, -300, 0), m)
            out = c + Vector((math.cos(a) * r, math.sin(a) * r, 0))
            for fr_, p in ((0, (0, -300, 0)), (f - 1, (0, -300, 0)), (f, tuple(c)), (f + 6, tuple(c + (out - c) * 0.55 + Vector((0, 0, up * random.uniform(0.7, 1.2))))),
                           (f + 14, tuple(out + Vector((0, 0, -0.6)))), (f + 15, (0, -300, 0))):
                K._key(d, "location", fr_, p, None)
            for fc in d.animation_data.action.fcurves:
                for kp in fc.keyframe_points: kp.interpolation = 'LINEAR' if 0 < kp.co.x < f + 15 and kp.co.x >= f else 'CONSTANT'

    def bob(av, f0, f1, base, amp=0.12, period=26, seed=0):
        for k, f in enumerate(range(f0, f1, period // 2)):
            K._key(av["root"], "location", f, (base[0], base[1], base[2] + (amp if (k + seed) % 2 else -amp)), None)

    # ======================= the park =======================
    pk = Set("park")
    with pk:
        P = WS.build(pk, A)
        for t, (x, y) in zip(P["towels"], ((12, -5.4), (12, -4.6))): t.location = (x, y, 1.36 + 0.09 * (y > -5))
        me = blocky.build(D, "me"); idle(me)
        mom = person("mom", {"skin": SKIN, "shirt_tex": A + "print_dots_teal.png", "pants": (250, 250, 250), "hair": None, "shoes": (250, 250, 250)}, HAIR["mom"])
        maxb = person("max", {"skin": SKIN, "shirt": (120, 200, 250), "pants": (120, 200, 250), "hair": (150, 100, 60), "shoes": SKIN, "scale": 0.42})
        karen = person("karen", {"skin": SKIN, "shirt_tex": A + "print_floral_lav.png", "pants": (245, 245, 250), "hair": None, "shoes": (250, 250, 250)}, HAIR["karen"])
        gma = person("grandma", {"skin": SKIN, "shirt": (225, 40, 45), "pants": (225, 40, 45), "hair": None, "shoes": (250, 250, 250)}, HAIR["grandma"])
        K.plane_image(A + "lifeguard.png", (1.4, 0.95), (0, -0.53, 1.1), parent=gma["waist"])
        for o in gma["head"].children:
            if "_acc" in o.name: o.location.z += 0.32; o.location.y += 0.1
        shades = empty("shades", (0, 0, 0), gma["head"]); sm = mat((15, 15, 18), 0.1)
        for sx in (-0.27, 0.27): prim("cyl", (0.06, 0.46, 0.34), (sx, -0.68, 0.72), sm, rot=(0, 0, 90), parent=shades)
        prim("box", (0.25, 0.06, 0.06), (0, -0.68, 0.76), sm, parent=shades)
        whistle = P["whistle"]
        swimmers = []
        for k, (x, y, hk, sk) in enumerate(((-12, 12, "x1", TAN), (8, 16, "x2", SKIN), (-3, 20, "x3", BROWN), (13, 9, "x4", SKIN), (-15, 6, "x2", BROWN))):
            sw = person(f"sw{k}", {"skin": sk, "shirt": sk, "pants": random.choice([(40, 60, 140), (220, 60, 60), (40, 40, 50)]), "hair": None, "shoes": sk}, HAIR[hk])
            swimmers.append((sw, (x, y, WZ - 3.6)))
        walkers = [person(f"wk{k}", {"skin": s_, "shirt_tex": A + f"print_{p_}.png", "pants": (50, 50, 70), "hair": None, "shoes": (250, 250, 250)}, HAIR[h_])
                   for k, (s_, p_, h_) in enumerate(((TAN, "stripes_navy", "x2"), (SKIN, "floral_red", "x3")))]
        loungers = [person(f"ln{k}", {"skin": s_, "shirt": c_, "pants": (60, 60, 80), "hair": None, "shoes": s_}, HAIR[h_])
                    for k, (s_, c_, h_) in enumerate(((BROWN, (250, 200, 60), "x1"), (SKIN, (120, 200, 150), "x4")))]
        toddlers = [person(f"td{k}", {"skin": s_, "shirt": c_, "pants": c_, "hair": h_, "shoes": s_, "scale": 0.5})
                    for k, (s_, c_, h_) in enumerate(((SKIN, (250, 150, 180), (230, 190, 120)), (TAN, (130, 210, 250), (40, 30, 25))))]
        magazine = prim("box", (1.2, 0.05, 1.5), (0, 0, 0), mat((240, 90, 120), 0.6)); hold(mom, magazine, "ra", (0.4, -0.5, 0.2), (0, 0, 0))

    # ---- everyone's resting places (whole short) ----
    sit(me, 0, 1.3, (4, -5.2), 180, ease=1); react(me, "smile", 1)
    sit(mom, 0, 1.3, (8, -5.2), 180, ease=1); react(mom, "sideeye", 1); pose(mom, 1, 1, ra=(-70, 0, -10), head=(-12, 0, 0))
    MAXP = (4.0, 4.2, WZ - 0.85)
    at(maxb, 0, MAXP, 180, ease=1); react(maxb, "happy", 1); pose(maxb, 1, 1, ra=(-60, 0, 30), la=(-60, 0, -30))
    P["ring"].location = (MAXP[0], MAXP[1], WZ + 0.2)
    sit(gma, 0, 6.35, (23, -1.8), 0, ease=1); react(gma, "blank", 1); pose(gma, 1, 1, head=(0, 0, 0))
    total = S.total + 60
    for k, (sw, p) in enumerate(swimmers):
        at(sw, 0, p, random.choice((0, 90, 180, 270)), ease=1); bob(sw, 0, total, p, 0.12, 24 + 4 * k, k); react(sw, random.choice(("smile", "happy", "grin")), 1)
        pose(sw, 1, 1, ra=(-80, 0, 30), la=(-80, 0, -30))
    for k, wk in enumerate(walkers):  # stroll back and forth along the far deck the whole time
        y = 30 + k * 3; xs = (-18, 18) if k == 0 else (16, -16); f = 0; d = 0
        while f < total:
            a_, b_ = (xs if d == 0 else xs[::-1]); bounce_walk(wk, f, f + 150, (a_, y, 0), (b_, y, 0), 8); f += 160; d ^= 1
        react(wk, "smile", 1)
    for k, ln in enumerate(loungers):
        sit(ln, 0, 1.3, ((-6, -5.2), (-10, -5.2))[k], 180, ease=1); react(ln, "sleepy" if k else "smile", 1); pose(ln, 1, 1, waist=(-25, 0, 0))
    KX, KY, _ = WS.KIDDIE
    for k, td in enumerate(toddlers):
        p = (KX - 1.5 + 3 * k, KY + 1.2 - 2.0 * k, -0.6); at(td, 0, p, 0 if k else 200, ease=1); bob(td, 0, total, p, 0.08, 20, k); react(td, "happy", 1)
    show_between(magazine, 0)

    # ======================= 0-3: Karen walks up =======================
    a, b = L(0)
    sh(pk, a, b, (16, -20, 14), (2, 6, 0), 22, dl=(-4, 6, -5)); ctx.sfx("splash", a + 10, 0.25)
    KP = (6.2, 0.6, 0)
    bounce_walk(karen, a - 10, L(1)[0] + 4, (24, 0.6, 0), KP, 8); react(karen, "annoyed", a)
    (a, s1), (_, b) = seg(1, "is")
    turn(karen, a, (4, 4.2), 5); react(karen, "angry", a); act(karen, a, "hips"); kit.mouth(karen, 1); chatter(karen, a, b, 1.2, 10)
    shf(pk, a, s1, (KP[:2], (4, 4.2), 4.75), 4.6, 28, lens=24)
    act(karen, s1, "point"); react(maxb, "confused", s1)
    sh(pk, s1, b, (9.6, 0.9, 3.2), (4.4, 3.8, 0.4), 24, dl=(-0.3, 0.2, 0))
    a, b = L(2)
    rest(me, a, "ll", "rl", "ll_knee", "rl_knee", "waist", ease=6); at(me, a, (4, -3.4, 0), (6.2, 0.6), ease=6)
    act(me, a + 4, "shrug"); react(me, "blank", a); kit.mouth(me, 2); tilt(me, a + 4, 10)
    shf(pk, a, b, ((4, -3.4), (6.2, 0.6), 4.75), 4.5, 30, lens=24); ctx.sfx("pop", a, 0.2)
    act(me, b + 4, None)
    (a, s1), (_, b) = seg(3, "that's")
    act(karen, a, "arms_out"); react(karen, "disgusted", a); kit.mouth(karen, 3); chatter(karen, a, b, 1.5, 9)
    for sw, p in swimmers[:3]: turn(sw, s1, (KP[0], KP[1]), 6); react(sw, "confused", s1)
    shf(pk, a, s1, (KP[:2], (4, 4.2), 4.75), 4.0, 20, lens=24)
    sh(pk, s1, b, (-2, 14, 3.2), (6.2, 0.6, 4.0), 24, dl=(0.6, -0.4, 0)); ctx.sfx("gasp", s1 + 2, 0.3)
    act(karen, b, None)

    # ======================= 4-5: the floatie =======================
    a, b = L(4); pop = wf(4, "popped") + 3
    # she kneels at the edge, reaches down, grabs the floatie, lifts it and pokes it with her nail
    K._key(karen["root"], "location", a + 4, KP, 1); K._key(karen["root"], "location", a + 12, (5.0, 1.0, -0.9))
    turn(karen, a + 4, (4, 4.2), 4)
    pose(karen, a + 12, 8, ll=(70, 0, 0), rl=(70, 0, 0), waist=(35, 0, 0), ra=(-120, 0, -10))
    grab = wf(4, "grabbed") + 4
    K._key(P["ring"], "location", grab, (MAXP[0], MAXP[1], WZ + 0.2), 1); K._key(P["ring"], "location", grab + 8, (4.6, 2.0, 2.4))
    K._key(maxb["root"], "location", grab, MAXP, 1)
    pose(karen, grab + 8, 6, waist=(5, 0, 0), ra=(-95, 0, -20)); pose(karen, wf(4, "popped"), 4, la=(-100, 0, 30))
    K._key(P["ring"], "scale", pop - 1, (1, 1, 1), 1); K._key(P["ring"], "scale", pop + 2, (0.5, 0.5, 0.2)); K._key(P["ring"], "scale", pop + 8, (0.35, 0.35, 0.08))
    K._key(maxb["root"], "location", pop + 2, MAXP, 1); K._key(maxb["root"], "location", pop + 10, (MAXP[0], MAXP[1], MAXP[2] - 0.45))
    react(karen, "smug", grab + 6); react(maxb, "shock", pop + 2)
    sh(pk, a, grab + 10, (2.4, 7.8, 2.6), (4.9, 1.4, 1.4), 24, dl=(0.2, -0.4, 0)); ctx.sfx("whoosh", grab, 0.3)
    sh(pk, grab + 10, b + 18, (9.0, 4.4, 2.8), (4.8, 1.4, 2.3), 26, dl=(-0.3, -0.2, 0)); ctx.sfx("pop", pop, 0.9); ctx.sfx("sad", pop + 6, 0.35)
    a, b = L(5)
    K._key(karen["root"], "location", a, (5.0, 1.0, -0.9), 1); K._key(karen["root"], "location", a + 8, (5.0, 0.6, 0))
    rest(karen, a + 8, "ll", "rl", "waist", "la", ease=8); pose(karen, a + 8, 1, ra=(-60, 0, -20))
    for k in range(3): pose(karen, a + 12 + k * 6, 3, ra=(-55, 0, -35 if k % 2 else -15), la=(-55, 0, 35 if k % 2 else 15))  # brushing off her hands
    K._key(P["ring"], "location", a + 8, (4.6, 2.0, 2.4), 1); K._key(P["ring"], "location", a + 16, (5.6, 1.4, 0.05))
    react(karen, "smug", a); kit.mouth(karen, 5); tilt(karen, a + 6, -10)
    shf(pk, a, b, ((5.0, 0.6), (4, 4.2), 4.75), 4.4, -25, lens=24)
    rest(karen, b + 2, "ra", "la")

    # ======================= 6-8: the splash =======================
    (a, s1), (_, b) = seg(6, "then")
    react(maxb, "blank", a); pose(maxb, a, 4, head=(15, 0, 0))
    sh(pk, a, s1, (4.0, 8.6, 1.4), (4.2, 3.0, 1.4), 26, dl=(0, -0.6, 0))  # Max looking up at her, from the water
    kick = wf(6, "kicked"); spl = wf(6, "splashed")
    react(maxb, "determined", kick)
    for k in range(0, spl - kick + 6, 3): pose(maxb, kick + k, 2, ll=(35 if k % 6 else -35, 0, 0), rl=(-35 if k % 6 else 35, 0, 0))
    drops((4.6, 2.6, WZ + 0.3), spl, 40, 1.8, 6.0, 0.16); drops((5.2, 1.2, 2.5), spl + 5, 24, 1.4, 2.0, 0.13)
    K._key(karen["root"], "location", spl + 4, (5.0, 0.6, 0), 1); K._key(karen["root"], "location", spl + 12, (5.8, -0.6, 0))
    pose(karen, spl + 4, 4, waist=(-18, 0, 0), ra=(-100, 0, 40), la=(-100, 0, -40)); react(karen, "shock", spl + 5)
    c = sh(pk, s1, b + 20, (6.6, 7.4, 2.4), (5.2, 0.4, 3.2), 24, dl=(-0.2, -0.4, 0)); shake(c, spl + 5, 10, 0.3)
    ctx.sfx("splash", spl, 1.0); ctx.sfx("gasp", spl + 8, 0.4)
    wet = mat((120, 170, 230), 0.05, alpha=0.7)  # dripping water on Karen's head and shoulders
    with pk: drips = [prim("ball", (0.12, 0.12, 0.2), (0, -300, 0), wet) for _ in range(6)]
    for k, d in enumerate(drips):
        hold(karen, d, "ra" if k % 2 else "la", (random.uniform(-0.3, 0.3), -0.2, random.uniform(0.6, 1.4))); show_between(d, spl + 6, L(10)[1])
    a, b = L(7)
    rest(karen, a, "waist", ease=4); act(karen, a, "arms_up"); react(karen, "meltdown", a, b + 10); kit.mouth(karen, 7); chatter(karen, a, b, 1.6, 8)
    shf(pk, a, b, ((5.8, -0.6), (4, 4.2), 4.75), 3.4, 15, lens=24)
    act(karen, b, None)
    a, b = L(8)
    turn(karen, a, (8, -5.2), 4); react(mom, "sideeye", a); kit.mouth(mom, 8); tilt(mom, a + 2, 8)
    shf(pk, a, b, ((8, -5.2), 180, 4.35), 3.8, -20, lens=24)

    # ======================= 9-10: the towels =======================
    (a, s1), (_, b) = seg(9, "threw")
    react(karen, "furious", a, s1)
    bounce_walk(karen, a + 2, s1 - 4, (5.8, -0.6, 0), (12.2, -2.6, 0), 6); ctx.sfx("step", a + 6, 0.5); ctx.sfx("step", a + 14, 0.5)
    kit.follow(pk, a, s1, karen["root"], (4.5, -7.5, 4.6), (0, 0, 3.6), 24)
    at(karen, s1 - 3, (12.2, -2.6, 0), (12, -5), ease=3)
    pose(karen, s1, 4, waist=(30, 0, 0), ra=(-110, 0, -10), la=(-110, 0, 10))
    thr = s1 + 6
    for k, t in enumerate(P["towels"]):
        p0 = tuple(t.location); K._key(t, "location", thr - 4, p0, 1)
        K._key(t, "location", thr + 2, (12.4 + k * 0.3, -3.8, 4.6)); K._key(t, "location", thr + 12, (15.5 + k * 1.2, -7.5 - k, 0.06))
        K._key(t, "rotation_euler", thr - 4, (0, 0, 0), 1); K._key(t, "rotation_euler", thr + 12, (math.radians(10), math.radians(40 + k * 50), math.radians(30)))
    pose(karen, thr, 3, waist=(-10, 0, 0), ra=(-160, 0, 40), la=(-160, 0, -40)); ctx.sfx("whoosh", thr, 0.7); ctx.sfx("slap", thr + 12, 0.5)
    react(me, "shock", thr + 4); react(mom, "annoyed", thr + 6)
    sh(pk, s1, b + 14, (19, -9, 5.0), (12.5, -4.5, 2.6), 24, dl=(-0.6, 0.4, 0))
    a, b = L(10)
    rest(karen, a, "waist", ease=4); act(karen, a, "point"); turn(karen, a, (8, -5.2), 4); react(karen, "smug", a); kit.mouth(karen, 10); chatter(karen, a, b, 1.2, 10)
    shf(pk, a, b, ((12.2, -2.6), (8, -5.2), 4.75), 3.8, 25, lens=24)
    act(karen, b, None)

    # ======================= 11-12: the whistle =======================
    (a, s1), (_, b) = seg(11, "and")
    react(karen, "determined", a)
    bounce_walk(karen, a, s1 - 2, (12.2, -2.6, 0), (23, -4.6, 0), 6)
    sh(pk, a, s1, (17, -14, 6.0), (18, -2, 4.0), 22, dt=(3, 0, 0)); ctx.sfx("step", a + 6, 0.4); ctx.sfx("step", a + 18, 0.4)
    # up two rungs of the tower ladder, then the whistle she snatched off its hook
    K._key(karen["root"], "location", s1, (23, -4.6, 0), 1); K._key(karen["root"], "location", s1 + 6, (23, -4.4, 1.0)); K._key(karen["root"], "location", s1 + 12, (23, -4.3, 2.0))
    turn(karen, s1, (23, 0), 2); pose(karen, s1 + 2, 4, ra=(-150, 0, 0), la=(-150, 0, 0))
    hold(karen, whistle, "ra", (0, -0.3, 0.1)); show_between(whistle, s1 + 12, L(12)[1])
    blow = wf(11, "whistle"); turn(karen, blow - 6, (19, -12), 4); pose(karen, blow - 4, 3, ra=(-135, 0, -25), la=(-20, 0, 0))
    react(karen, "angry", blow - 4); ctx.sfx("ahem", blow, 0.1)
    for sw, p in swimmers: react(sw, "shock", blow + 4); turn(sw, blow + 4, (23, -4), 6)
    react(gma, "suspicious", blow + 4)
    sh(pk, s1, b + 14, (17.5, -11.5, 5.4), (23, -4.3, 5.6), 24, dl=(0.5, 0.5, 0)); ctx.sfx("whistle", blow, 0.9)
    a, b = L(12)
    turn(karen, a, (23, -1.8), 4); act(karen, a, "point_up"); react(karen, "furious", a, b + 6); kit.mouth(karen, 12); chatter(karen, a, b, 1.8, 7)
    pose(gma, a + 4, 6, head=(-28, 0, 0))
    sh(pk, a, a + (b - a) // 2, (25.5, -9.5, 3.2), (23, -3.0, 6.0), 22, dl=(-0.3, 0.3, 0))  # low, looking up past Karen at the tower
    sh(pk, a + (b - a) // 2, b, (26.0, -7.0, 8.6), (23, -1.8, 7.6), 26, dl=(-0.3, 0.3, 0))  # over Grandma's shoulder, down at Karen
    act(karen, b, None)

    # ======================= 13-17: Grandma =======================
    (a, s1), (_, b) = seg(13, "slowly")
    K._key(karen["root"], "location", a, (23, -4.3, 2.0), 1); K._key(karen["root"], "location", a + 8, (19.8, -6.8, 0))
    turn(karen, a + 8, (23, -4.6), 3); react(karen, "smug", a + 8)
    # Grandma climbs down the ladder rung by rung, facing it
    rest(gma, a, "ll", "rl", "ll_knee", "rl_knee", ease=1); at(gma, a, (23, -3.0, 5.2), (23, 0), ease=1)
    n = 5
    for k in range(n + 1):
        f = a + 4 + k * (s1 - a - 6) // n
        K._key(gma["root"], "location", f, (23, -3.0, 5.2 - k * 5.2 / n), 2)
        pose(gma, f, 2, ra=(-150 if k % 2 else -120, 0, 0), la=(-120 if k % 2 else -150, 0, 0), ll=(20 if k % 2 else -10, 0, 0), rl=(-10 if k % 2 else 20, 0, 0))
    sh(pk, a, s1, (31, -12, 6.5), (23, -3.0, 4.0), 20, dt=(0, 0, -2.2)); ctx.sfx("step", a + 8, 0.3); ctx.sfx("step", a + 20, 0.3)
    at(gma, s1, (23, -4.6, 0), (19.8, -6.8), ease=4); rest(gma, s1, ease=4); react(gma, "blank", s1)
    off = wf(13, "sunglasses")
    pose(gma, off - 10, 8, ra=(-160, 0, -18))
    K._key(shades, "location", off - 4, (0, 0, 0), 1); K._key(shades, "location", off + 6, (0, -0.15, 0.55))
    K._key(shades, "scale", off + 6, (1, 1, 1), 1); K._key(shades, "scale", off + 7, (0.0001, 0.0001, 0.0001))
    rest(gma, off + 8, "ra", ease=6)
    shf(pk, s1, b + 18, ((23, -4.6), (19.8, -6.8), 4.75), 3.2, -30, lens=28, push=0.18); ctx.sfx("ding", off + 2, 0.5)
    a, b = L(14)
    react(gma, "smug", a); react(karen, "shock", b - 2)
    shf(pk, a, b - 2, ((23, -4.6), (19.8, -6.8), 4.75), 2.6, -30, lens=28, pz=wf(14, "grandma"), amount=1.15); ctx.sfx("ding", wf(14, "grandma"), 0.5)
    c = shf(pk, b - 2, b + 18, ((19.8, -6.8), (23, -4.6), 4.75), 2.8, 25, lens=26, pz=b, amount=1.2); shake(c, b, 8, 0.2); ctx.sfx("scared", b, 0.5)
    a, b = L(15)
    act(gma, a, "cross"); kit.mouth(gma, 15); chatter(gma, a, b, 0.8, 12); react(gma, "sideeye", a)
    sh(pk, a, b, (19.6, -12.5, 4.9), (21.4, -5.6, 4.4), 24, dl=(0.2, 0.4, 0))  # two-shot: Grandma and Karen
    a, b = L(16)
    react(karen, "confused", a); act(karen, a, "shrug"); kit.mouth(karen, 16); tilt(karen, a + 2, 12)
    shf(pk, a, b, ((19.8, -6.8), (23, -4.6), 4.75), 3.0, 30, lens=26)
    act(karen, b + 2, None)
    a, b = L(17)
    react(gma, "chad", a); kit.mouth(gma, 17); tilt(gma, a + 2, -8)
    shf(pk, a, b, ((23, -4.6), (19.8, -6.8), 4.75), 3.0, -25, lens=26); ctx.sfx("ding", b - 4, 0.4)

    # ======================= 18-20: the high dive =======================
    (a, s1), (_, b) = seg(18, "and")
    DX, DY = WS.DIVE
    at(maxb, a, (DX, DY + 0.6, 0), (DX, DY + 5), ease=1); rest(maxb, a, ease=1); react(maxb, "determined", a)
    n = 9; top = s1 - 8
    for k in range(n + 1):
        f = a + k * (top - a) // n
        K._key(maxb["root"], "location", f, (DX, DY + 0.6, k * 9.0 / n), 2)
        pose(maxb, f, 2, ra=(-160 if k % 2 else -130, 0, 0), la=(-130 if k % 2 else -160, 0, 0))
    sh(pk, a, s1, (DX + 4.5, DY - 4.0, 3.2), (DX, DY + 0.6, 2.0), 24, dl=(0, 0, 6.0), dt=(0, 0, 7.0)); ctx.sfx("step", a + 6, 0.3)
    rest(maxb, top, ease=3); at(maxb, top, (DX, DY + 0.2, 9.15), (DX, 0), ease=3)
    bounce_walk(maxb, top + 2, s1 + 10, (DX, DY + 0.2, 9.15), (DX, DY - 7.8, 9.15), 5)
    flip = s1 + 14; land = flip + 24
    K._key(maxb["root"], "location", flip, (DX, DY - 7.8, 9.15), 1); K._key(maxb["root"], "location", flip + 12, (DX, DY - 10.5, 13.0)); K._key(maxb["root"], "location", land, (DX, DY - 12.5, WZ - 1.5))
    K._key(maxb["root"], "rotation_euler", flip, (0, 0, 0), 1); K._key(maxb["root"], "rotation_euler", land - 4, (math.radians(-360), 0, 0))
    pose(maxb, flip, 3, ll=(-80, 0, 0), rl=(-80, 0, 0), ra=(-170, 0, 0), la=(-170, 0, 0)); rest(maxb, land - 4, ease=4)
    drops((DX, DY - 12.5, WZ + 0.2), land, 40, 2.4, 7.0, 0.18); react(maxb, "chad", land + 6)
    for sw, p in swimmers: react(sw, "happy", land + 4); pose(sw, land + 4, 4, ra=(-170, 0, 20), la=(-170, 0, -20))
    sh(pk, s1, b + 28, (DX + 9, DY - 17, 9.5), (DX, DY - 9, 9.5), 24, dt=(0, -2, -6.5)); ctx.sfx("whoosh", flip, 0.6); ctx.sfx("splash", land, 1.0); ctx.sfx("cheer", land + 4, 0.6)
    a, b = L(19)
    act(karen, a, "arms_out"); react(karen, "meltdown", a, b + 10); kit.mouth(karen, 19); chatter(karen, a, b, 1.6, 7)
    shf(pk, a, b, ((19.8, -6.8), (23, -4.6), 4.75), 3.0, 20, lens=26, pz=a + 2, amount=1.15)
    act(karen, b, None)
    (a, s2_), (_, b) = seg(20, "you")
    react(gma, "chad", a); kit.mouth(gma, 20); act(gma, a, "cross")
    sh(pk, a, s2_, (19.6, -12.5, 4.9), (21.4, -5.6, 4.4), 24, dl=(0.2, 0.4, 0))
    turn(gma, s2_, (-34, 21), 5); act(gma, s2_ + 2, "point"); react(karen, "shock", s2_ + 4)
    sh(pk, s2_, b + 4, (24.6, -6.4, 5.8), (-34, 18, 7.0), 24, dl=(-0.4, 0.2, 0))  # past Grandma's pointing arm to the slide
    act(gma, b + 10, "cross")

    # ======================= 21: down the slide =======================
    a, b = L(21)
    path = P["slide_path"]
    sit(karen, a, 12.6, (path[0][0], path[0][1]), 225, ease=1); react(karen, "terrified", a); act(karen, a, "arms_up")
    n = len(path); ride0, ride1 = a + 4, wf(21, "landed") + 4
    for k, p in enumerate(path):
        f = ride0 + k * (ride1 - ride0) // (n - 1)
        nxt = path[min(k + 1, n - 1)]; prv = path[max(k - 1, 0)]
        yaw = math.degrees(math.atan2(nxt[1] - prv[1], nxt[0] - prv[0])) + 90
        K._key(karen["root"], "location", f, (p[0], p[1], p[2] - 0.6), None)
        K._key(karen["root"], "rotation_euler", f, (0, 0, math.radians(yaw)), None)
    for fc in karen["root"].animation_data.action.fcurves:
        for kp in fc.keyframe_points:
            if ride0 <= kp.co.x <= ride1: kp.interpolation = 'BEZIER'
    land = ride1
    K._key(karen["root"], "location", land + 4, (KX + 0.2, KY + 0.2, -1.7), None); react(karen, "meltdown", land + 2, land + 60)
    drops((KX + 0.2, KY + 0.2, 0), land + 2, 34, 2.2, 4.0, 0.16)
    for td in toddlers: react(td, "laugh", land + 6); pose(td, land + 6, 4, ra=(-170, 0, 20), la=(-170, 0, -20))
    kit.follow(pk, a, land - 18, karen["root"], (5, -9, 6), (0, 0, 2.0), 22); ctx.sfx("whoosh", a + 4, 0.8)
    sh(pk, land - 18, b + 28, (KX + 9, KY - 11, 5.0), (KX, KY, 1.0), 24, dl=(-0.8, 1, 0)); ctx.sfx("splash", land + 2, 1.0); ctx.sfx("giggle", land + 10, 0.6)

    # ======================= 22-23: the sign =======================
    a, b = L(22); S.flash(a, 5); ctx.sfx("whoosh", a, 0.4)
    at(karen, a, (0, -300, 0), ease=1)
    at(maxb, a, MAXP, 180, ease=1); rest(maxb, a, ease=1); react(maxb, "happy", a); pose(maxb, a + 2, 4, ra=(-170, 0, 20))
    P["ring"].keyframe_insert("scale", frame=a - 1); P["ring"].scale = (1, 1, 1); P["ring"].keyframe_insert("scale", frame=a)
    K._key(P["ring"], "location", a, (MAXP[0], MAXP[1], WZ + 0.2), 1)
    at(gma, a, (23, -1.8, 6.35), 0, ease=1); sit(gma, a, 6.35, (23, -1.8), 0, ease=1); react(gma, "smile", a)
    react(me, "happy", a); react(mom, "smile", a)
    sh(pk, a, b, (26, -22, 13), (8, 4, 2.0), 22, dl=(-2, 3, -2))
    a, b = L(23)
    sh(pk, a, wf(23, "signed"), (14, -4.2, 4.6), (14, 1.0, 4.4), 28, dl=(0, 0.8, 0))
    sh(pk, wf(23, "signed"), b + 50, (15.1, -0.6, 3.6), (15.3, 0.9, 3.4), 30, dl=(0, -3.5, 1.2)); ctx.sfx("pop", wf(23, "footprint"), 0.4)
