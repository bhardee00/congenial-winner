""""A Karen Tried To Kick My Baby Brother Out Of The Library" - reference #3 style, made as detailed as possible
(user request): every event is set up -> shown happening in close-up -> reacted to, every character is alive
(breathing, weight shift, heads that follow the talk, listeners reacting, hand beats while talking), mouths move on
every spoken line, no texture VFX, top UPPERCASE captions with a thick stroke. Voices 1.30x / 1.50x, Leo pitched up.
Line numbers follow stories/library.json (0-25). The set is stories/library_set.py."""
import math, random
from mathutils import Vector, Matrix
import shortkit as K
from shortkit import Set, prim, mat, empty, show_between, pose, rest, at, turn, sit, idle, shake
import blocky
from avatar import react
from storykit import Kit, hold, glasses, clear_view
from acting import act, chatter, bounce_walk
import life
import library_set as LS

random.seed(31)
SKIN, TAN, BROWN = (234, 190, 150), (204, 142, 105), (150, 100, 70)
HAIR = {"karen": 1012594937, "mom": 8199034057, "grandma": 15440914286,
        "x1": 11268431947, "x2": 4887515664, "x3": 10976405810, "x4": 9661319036}
SEAT, TOP = LS.SEAT, LS.TABLE_TOP


def fr(pos, face, head, dist=3.0, ang=0.0, dz=0.15):
    yaw = math.radians(K.yaw_to(pos, face))
    d = Matrix.Rotation(math.radians(ang), 3, 'Z') @ Vector((math.sin(yaw), -math.cos(yaw), 0))
    return (pos[0] + d.x * dist, pos[1] + d.y * dist, head + dz), (pos[0], pos[1], head)


def build(ctx):
    S, L, A, D = ctx.short, ctx.L, ctx.A, ctx.D
    kit = Kit(ctx); seg, wf, sh = kit.seg, kit.wf, kit.sh
    timed = ctx.timed

    blocked = []

    def shf(f0, f1, who, dist=3.2, ang=0.0, lens=26, push=0.08, dz=0.2, subj=None, **kw):
        """Face shot that checks the view: tries the asked angle, then swings around (and a bit closer) until
        nothing stands between the lens and the face at the middle of the shot."""
        lb.scene.frame_set((f0 + f1) // 2)
        tries = [(ang + da, dist * dm) for dm in (1.0, 0.8, 1.25, 0.65) for da in (0, 18, -18, 36, -36, 55, -55, 75, -75)]
        for a_, d_ in tries:
            loc, tgt = fr(*who, dist=d_, ang=a_, dz=dz)
            if clear_view(lb.scene, loc, tgt, subj["root"] if subj else None, margin=1.15): break
        else:
            loc, tgt = fr(*who, dist=dist, ang=ang, dz=dz); blocked.append(("shf", f0))
        return sh(lb, f0, f1, loc, tgt, lens, dl=tuple((t - l) * push for l, t in zip(loc, tgt)), **kw)

    def person(name, lk, hair=None, lift=0.0):
        a = blocky.build(D, name, lk); at(a, 0, (0, -300, 0), 0, ease=1); idle(a, ("head",), 0.015, 50); life.alive(a)
        if hair:
            r = blocky.wear(D, a, hair); r.location.z += lift
        return a

    def words(i, f0=None, f1=None):
        a, b = L(i); f0 = f0 or a; f1 = f1 or b
        return [S.frame(w[1]) for w in timed[i]["words"] if f0 <= S.frame(w[1]) < f1]

    def say(av, i, arm=None, sway=1.0, listeners=()):
        """A spoken line: mouth flaps per syllable, the head and body sway, hand beats on stressed words (if the arm
        is free), and everyone listening turns to the speaker."""
        a, b = L(i); kit.mouth(av, i); chatter(av, a, b, sway, 11)
        if arm: life.gesture_talk(av, words(i), arm, 0.9, i)
        for k, l in enumerate(listeners): life.listen(l, av, a + 2 * k, b, seed=i * 10 + k)

    # ======================= the library =======================
    lb = Set("library")
    with lb:
        P = LS.build(lb, A)
        me = blocky.build(D, "me"); idle(me, ("head",), 0.015, 50); life.alive(me)
        leo = person("leo", {"skin": SKIN, "shirt_tex": A + "print_stripes_yellow.png", "pants": (90, 140, 210), "hair": (150, 100, 60), "shoes": (250, 250, 250), "scale": 0.42})
        mom = person("mom", {"skin": SKIN, "shirt_tex": A + "print_dots_teal.png", "pants": (245, 245, 250), "hair": None, "shoes": (250, 250, 250)}, HAIR["mom"])
        karen = person("karen", {"skin": SKIN, "shirt_tex": A + "print_floral_lav.png", "pants": (245, 245, 250), "hair": None, "shoes": (250, 250, 250)}, HAIR["karen"])
        gma = person("grandma", {"skin": SKIN, "shirt_tex": A + "print_cardigan.png", "pants": (80, 80, 100), "hair": None, "shoes": (60, 40, 30)}, HAIR["grandma"], 0.32)
        glasses(gma); K.plane_image(A + "badge.png", (1.0, 0.6), (0.45, -0.53, 1.45), parent=gma["waist"])
        r1 = person("reader1", {"skin": TAN, "shirt_tex": A + "print_stripes_navy.png", "pants": (50, 50, 70), "hair": None, "shoes": (40, 40, 45)}, HAIR["x2"])
        r2 = person("reader2", {"skin": BROWN, "shirt_tex": A + "print_floral_red.png", "pants": (60, 60, 80), "hair": None, "shoes": (250, 250, 250)}, HAIR["x3"])
        r3 = person("browser", {"skin": SKIN, "shirt": (120, 180, 120), "pants": (50, 50, 60), "hair": None, "shoes": (40, 40, 45)}, HAIR["x1"])
        glasses(r1)
        kids = []
        for k in range(12):
            sk = (SKIN, TAN, BROWN)[k % 3]
            lk = {"skin": sk, "shirt": random.choice([(240, 120, 90), (90, 170, 230), (250, 200, 70), (130, 200, 120), (200, 120, 200), (250, 150, 180)]),
                  "pants": random.choice([(60, 60, 80), (90, 140, 210), (240, 240, 240)]), "hair": random.choice([(60, 40, 30), (230, 190, 120), (30, 20, 15), (150, 90, 40)]),
                  "shoes": (250, 250, 250), "scale": 0.55}
            kids.append(person(f"kid{k}", lk))
        # props
        rattle_m = mat((250, 120, 160), 0.3)

        def rattle():
            r = empty("rattle"); prim("cylY", (0.14, 0.14, 0.7), (0, 0, -0.25), mat((250, 230, 120), 0.4), parent=r)
            prim("ball", (0.42, 0.42, 0.42), (0, 0, 0.25), rattle_m, parent=r); return r
        rat_leo, rat_karen, rat_drop = rattle(), rattle(), rattle()
        hold(leo, rat_leo, "la", (0, -0.25, 0.1), (60, 0, 0))
        hold(karen, rat_karen, "ra", (0, -0.25, 0.1), (60, 0, 0))
        mom_book = LS.book((150, 80, 160), (1.4, 0.15, 1.8)); hold(mom, mom_book, "ra", (0.55, -0.6, 0.35), (0, 0, 0))
        r_books = []
        for av in (r1, r2):
            bk = LS.book((60, 110, 190), (1.3, 0.15, 1.7)); hold(av, bk, "ra", (0.5, -0.6, 0.35), (0, 0, 0)); r_books.append(bk)
        story_bk = K.plane_image(A + "story_book.png", (1.6, 2.0), (0, -0.55, 0.5), parent=leo["waist"])
        # the page Leo turns: a hinge at the open book's spine with a thin page on it
        ob = P["open_book"]; hinge = empty("page_hinge", (0, 0, 0.09), ob)
        page = prim("box", (0.75, 1.0, 0.02), (0.38, 0, 0), mat((252, 248, 235), 0.8), parent=hinge)
        pg_txt = [prim("box", (0.5, 0.04, 0.005), (0.38, -0.3 + k * 0.15, 0.015), mat((120, 110, 100), 0.8), parent=hinge) for k in range(5)]

    # ======================= starting places =======================
    TX, TY = LS.READ_TABLE
    LEO = (TX, TY + 2.5); MOM = (TX + 2.4, TY + 2.6); ME = (TX, TY - 2.6)
    sit(leo, 0, SEAT + 1.0, LEO, 0, ease=1); react(leo, "happy", 1)
    sit(mom, 0, SEAT, MOM, 0, ease=1); act(mom, 1, "read", 1); pose(mom, 1, 1, head=(-14, 0, 0)); react(mom, "relieved", 1)
    sit(me, 0, SEAT, ME, 180, ease=1); react(me, "smile", 1)
    pose(leo, 1, 1, la=(-70, 0, 15), ra=(-55, 0, -10), head=(-16, 0, 0))
    R1, R2 = (10.8, -6.4), (15.2, -11.6)
    sit(r1, 0, SEAT, R1, 0, ease=1); act(r1, 1, "read", 1); pose(r1, 1, 1, head=(-14, 0, 0)); react(r1, "smile", 1)
    sit(r2, 0, SEAT, R2, 180, ease=1); act(r2, 1, "read", 1); pose(r2, 1, 1, head=(-14, 0, 0)); react(r2, "relieved", 1)
    at(r3, 0, (18.4, 2.0, 0), (21, 2), ease=1); pose(r3, 1, 1, ra=(-95, 0, 0), head=(10, 0, 0)); react(r3, "suspicious", 1)
    sw = P["swivel"]; sw.rotation_euler = (0, 0, math.radians(180))
    gma["root"].parent = sw; sit(gma, 0, 2.0, (0, 0), 0, ease=1); act(gma, 1, "cross", 1); react(gma, "sleepy", 1)
    show_between(rat_karen, 0, 0); show_between(rat_drop, 0, 0)
    for k, kd in enumerate(kids): at(kd, 0, (-30 - k, -30, 0), 0, ease=1)

    # ======================= 0: Karen comes in =======================
    (a, s1), (_, s2), (_, b) = seg(0, "tried", "baby")
    sh(lb, a, s1, (16, -14, 12), (-4, 4, 2.0), 20, dl=(-3, 3, -2.5)); ctx.sfx("doorbell", a + 4, 0.3)
    at(karen, a, (-18, -19.5, 0), (-18, -12), ease=1); react(karen, "annoyed", a)
    dr_ = P["door"]; K._key(dr_, "rotation_euler", s1 - 14, (0, 0, 0), 1); K._key(dr_, "rotation_euler", s1 - 4, (0, 0, math.radians(95)), None)
    K._key(dr_, "rotation_euler", s1 + 22, (0, 0, math.radians(95)), 1); K._key(dr_, "rotation_euler", s1 + 34, (0, 0, 0), None)
    bounce_walk(karen, s1 - 6, L(1)[0] + 2, (-18, -19.5, 0), (2.0, -0.2, 0), 8)
    sh(lb, s1, s2, (-15.0, -7.5, 5.0), (-17.0, -13.5, 4.4), 24, dt=(1.2, 2.0, 0))  # she walks in toward us
    for k in range(3): ctx.sfx("step", s1 + k * 8, 0.3)
    react(leo, "happy", s2); pose(leo, s2 + 4, 6, head=(-10, 0, 8))
    page_turn0 = s2 + 6
    shf(s2, b, (LEO, 0, 4.05), 2.6, 15, lens=26)  # Leo happily reading
    # ======================= 1: "Shh! Is that a baby? In my library?" =======================
    (a, s1), (_, b) = seg(1, "is")
    at(karen, a, (2.0, -0.2, 0), (TX, TY + 2.5), ease=3); react(karen, "angry", a)
    life.act2(karen, a, "shush"); ctx.sfx("ahem", a, 0.1)
    say(karen, 1, None, 1.3, (me, leo, mom))
    shf(a, s1, ((2.0, -0.2), (TX, 2.5), 4.75), 3.6, 25, lens=24)
    life.act2(karen, s1, "point"); react(karen, "disgusted", s1 + 2); react(leo, "confused", s1 + 6); react(me, "confused", s1 + 4)
    sh(lb, s1, b, (4.6, -2.4, 4.9), (TX + 0.4, TY + 2.0, 3.6), 24, dl=(-0.4, 0.2, 0))  # over Karen's shoulder at Leo
    # ======================= 2: me "He's just reading." =======================
    a, b = L(2)
    act(karen, a, "hips"); react(me, "blank", a); life.act2(me, a + 2, "shrug"); say(me, 2, None, 0.9, (karen,))
    life.look(me, a, (2.0, -0.2, 4.7)); react(karen, "suspicious", a + 6)
    shf(a, b, (ME, (2.0, -0.2), 4.8), 3.4, -25, lens=26)
    act(me, b + 4, None)
    # ======================= 3: "Babies can't read. That's ridiculous." =======================
    (a, s1), (_, b) = seg(3, "that's")
    act(karen, a, "cross"); react(karen, "smug", a); say(karen, 3, None, 1.0, (me, mom))
    life.shake_head(karen, a + 2, 2, 9, 4)
    shf(a, s1, ((2.0, -0.2), (TX, 2.5), 4.75), 3.0, 10, lens=26)
    react(karen, "laugh", s1); pose(karen, s1, 3, waist=(-10, 0, 0)); pose(karen, b, 5, waist=(0, 0, 0))
    react(mom, "sideeye", s1 + 4); life.look(mom, s1 + 2, (2.0, -0.2, 4.7))
    shf(s1, b, (MOM, 0, 4.8), 3.0, -30, lens=26)  # Mom's side-eye over her book
    # ======================= 4: "Leo turned the page. Then he said one word." =======================
    (a, s1), (_, b) = seg(4, "then")
    # insert: the page turns
    pt = wf(4, "turned")
    K._key(hinge, "rotation_euler", 0, (0, 0, 0), 1); K._key(hinge, "rotation_euler", pt - 2, (0, 0, 0), 1); K._key(hinge, "rotation_euler", pt + 12, (0, math.radians(-178), 0))
    pose(leo, pt - 4, 4, ra=(-80, 0, 10)); pose(leo, pt + 8, 6, ra=(-60, 0, -25)); pose(leo, pt + 16, 5, ra=(-55, 0, -10))
    sh(lb, a, s1, (TX + 0.6, TY - 0.7, 4.3), (TX, TY + 1.0, TOP), 30, dl=(0, 0.2, -0.2)); ctx.sfx("rustle", pt, 0.5)
    pose(leo, s1, 6, head=(8, 0, 0)); react(leo, "blank", s1); life.look(leo, s1 + 2, (2.0, -0.2, 4.7), 8)
    for av in (me, mom): react(av, "nervous", s1 + 8); life.look(av, s1 + 6, (TX, TY + 2.5, 4.0))
    react(karen, "suspicious", s1 + 4)
    shf(s1, b, (LEO, (2.0, -0.2), 4.05), 2.2, 10, lens=28, push=0.25)  # slow push in: everyone waits
    ctx.sfx("heartbeat", s1 + 4, 0.25)
    # ======================= 5: Leo "Goo." =======================
    a, b = L(5)
    react(leo, "chad", a - 1); kit.mouth(leo, 5); pose(leo, a, 3, head=(0, 8, 0))
    shf(a, b + 2, (LEO, (2.0, -0.2), 4.05), 1.8, 10, lens=30, pz=a + 1, amount=1.12); ctx.sfx("pop", a, 0.2)
    # ======================= 6: Karen "Shh!" =======================
    a, b = L(6)
    react(karen, "furious", a, b + 20); act(karen, a - 2, "shush", 3); kit.mouth(karen, 6)
    pose(karen, a - 2, 3, waist=(22, 0, 0))  # leans in over the table
    c = shf(a - 1, b + 2, ((2.0, -0.2), (TX, 2.5), 4.75), 2.4, 15, lens=26, pz=a + 1, amount=1.2); shake(c, a + 1, 6, 0.2)
    for av in (r1, r2, r3): life.look(av, a + 3, (2.0, -0.2, 4.7), 5); react(av, "annoyed", a + 5)
    # ======================= 7: the rattle (+ action beat) =======================
    a, b = L(7); g = wf(7, "grabbed"); dr = wf(7, "dropped")
    pose(karen, a, 4, waist=(0, 0, 0)); act(karen, a, None)
    life.act2(karen, g, "reach"); pose(karen, g, 4, waist=(26, 0, 0))
    snatch = g + 6
    show_between(rat_leo, 0, snatch); show_between(rat_karen, snatch, dr + 6); react(leo, "shock", snatch + 1); life.flinch(leo, snatch + 1, 0.4)
    pose(leo, snatch + 2, 4, la=(-90, 0, 10))
    sh(lb, a, snatch + 8, (TX - 1.6, TY - 0.6, 4.8), (TX + 0.8, TY + 1.9, 3.6), 24, dl=(0.2, 0.1, 0))  # the grab, close
    ctx.sfx("whoosh", snatch, 0.4)
    react(karen, "smug", snatch + 4); pose(karen, snatch + 4, 4, waist=(0, 0, 0), ra=(-40, 0, 0))
    RET = LS.RETURN; RS = (RET[0] - 0.2, RET[1] - 2.2)
    bounce_walk(karen, snatch + 6, dr - 6, (2.0, -0.2, 0), (RS[0], RS[1], 0), 7)
    kit.follow(lb, snatch + 8, dr - 4, karen["root"], (3.5, -5.5, 4.2), (0, 0, 3.6), 24); ctx.sfx("step", snatch + 12, 0.3); ctx.sfx("step", snatch + 20, 0.3)
    at(karen, dr - 5, (RS[0], RS[1], 0), (RET[0], RET[1]), ease=3)
    pose(karen, dr - 4, 4, ra=(-118, 0, -4))  # the hand over the slot
    show_between(rat_drop, dr + 6, dr + 22)
    K._key(rat_drop, "location", dr + 6, (RET[0] - 0.1, RET[1] - 1.5, 4.35), 1); K._key(rat_drop, "location", dr + 14, (RET[0], RET[1] - 1.25, 3.25))
    K._key(rat_drop, "rotation_euler", dr + 6, (math.radians(90), 0, 0), 1); K._key(rat_drop, "rotation_euler", dr + 14, (math.radians(70), 0, math.radians(20)))
    sh(lb, dr - 4, b + 12, (RET[0] + 3.1, RET[1] - 2.2, 3.9), (RET[0] + 0.1, RET[1] - 1.2, 3.4), 28, dl=(-0.4, 0.2, 0))  # the slot, close
    ctx.sfx("clang", dr + 15, 0.35)
    # reaction beat: Leo's little face, Mom's book comes down, me
    rb_ = b + 12
    react(leo, "sad", rb_); pose(leo, rb_, 6, head=(-14, 0, 0), la=(-30, 0, 0)); life.look(leo, rb_, (RET[0], RET[1], 3.0), 8)
    react(me, "shock", rb_ + 2); life.look(me, rb_, (RS[0], RS[1], 4.7)); act(mom, rb_ + 6, None); react(mom, "annoyed", rb_ + 8); life.look(mom, rb_ + 4, (RS[0], RS[1], 4.7))
    shf(rb_, L(8)[0], (LEO, (RS[0], RS[1]), 4.05), 2.4, 20, lens=28); ctx.sfx("sad", rb_ + 2, 0.35)
    # ======================= 8: Karen "Oops. Quiet time." =======================
    a, b = L(8)
    at(karen, a, (RS[0], RS[1], 0), (TX, TY + 2.5), ease=4); react(karen, "smug", a)
    for k in range(3): pose(karen, a + 3 + k * 5, 2, ra=(-50, 0, -30 if k % 2 else -8), la=(-50, 0, 30 if k % 2 else 8))  # brushing off her hands
    say(karen, 8, None, 1.0)
    rest(karen, b + 2, "ra", "la", ease=5)
    shf(a, b, ((RS[0], RS[1]), (TX, 2.5), 4.75), 3.0, 18, lens=26)
    # ======================= 9: the book stack (+ action beat) =======================
    (a, s1), (_, b) = seg(9, "then")
    react(leo, "blank", a); life.look(leo, a, (RS[0], RS[1], 4.7), 8)
    shf(a, s1, (LEO, (RS[0], RS[1]), 4.05), 1.9, 0, lens=30, push=0.2)  # the stare
    ctx.sfx("crickets", a + 4, 0.3)
    psh = wf(9, "pushed"); off = wf(9, "off")
    react(leo, "determined", s1); life.look(leo, s1, (TX - 1.9, TY + 1.0, TOP + 1.0), 6)
    pose(leo, psh - 8, 8, ra=(-80, 0, -30)); pose(leo, off, 14, ra=(-82, 0, -58))  # the slow push
    sh(lb, s1, off - 4, (TX - 5.8, TY - 4.6, 5.4), (TX - 1.2, TY + 1.4, TOP + 0.8), 24, dl=(0.6, 0.4, 0))  # Leo and the tall stack
    stack = P["stack"]; land0 = off + 16; lands = []
    for k, bk in enumerate(stack):
        p0 = Vector(bk.location); r0 = bk.rotation_euler.copy()
        K._key(bk, "location", off - 2, tuple(p0), 1); K._key(bk, "rotation_euler", off - 2, tuple(r0), 1)
        tilt_f = off + 4 + k // 3
        K._key(bk, "location", tilt_f, (p0.x - 0.25 - k * 0.12, p0.y, p0.z + 0.05), None); K._key(bk, "rotation_euler", tilt_f, (r0.x, math.radians(22 + k * 3), r0.z), None)
        lf = land0 + k * 6; lands.append(lf)
        end = (TX - 4.4 - k * 0.3 + random.uniform(-0.4, 0.4), TY + 0.9 + random.uniform(-1.4, 1.4), 0.15)
        mid = ((p0.x + end[0]) / 2 - 0.4, (p0.y + end[1]) / 2, p0.z + 0.6)
        K._key(bk, "location", lf - 6, mid, None); K._key(bk, "location", lf, end, None)
        K._key(bk, "rotation_euler", lf, (math.radians(random.choice((0, 180))), 0, math.radians(random.uniform(-80, 80))), None)
        K._key(bk, "location", lf + 3, (end[0], end[1], end[2] + 0.18), None); K._key(bk, "location", lf + 6, end, None)  # little bounce
    sh(lb, off - 4, b + 40, (TX - 10.5, TY - 4.0, 3.6), (TX - 4.4, TY + 0.8, 1.8), 24, dl=(0.4, 0, 0))  # the stack goes over
    ctx.sfx("whoosh", off + 2, 0.4)
    for lf in lands[:5]: ctx.sfx("slap", lf, 0.45)
    react(karen, "shock", lands[0] + 2); life.flinch(karen, lands[0] + 1, 0.8)
    for k, av in enumerate((r1, r2, r3, me, mom)): life.flinch(av, lands[0] + 3 + k, 0.6); react(av, "big_eyes", lands[0] + 4 + k)
    # ======================= 10: "Every single one hit the floor." =======================
    a, b = L(10)
    sh(lb, a, b + 20, (TX - 7.4, TY - 4.0, 0.9), (TX - 6.2, TY + 1.0, 0.4), 22, dl=(-0.3, 0, 0))  # floor level: books still landing
    for lf in lands[5:]: ctx.sfx("slap", lf, 0.45)
    react(leo, "chad", a + 6)
    # ======================= 11-12: Karen calls the librarian, Mom's reply =======================
    a, b = L(11)
    KS = Vector(value_loc(karen, a))
    react(karen, "furious", a, b + 10); life.act2(karen, a, "arms_out"); say(karen, 11, None, 1.6, (me, mom, r1, r2))
    shf(a, b, ((KS.x, KS.y), (TX, 2.5), 4.75), 3.2, -15, lens=24); ctx.sfx("angry", a + 4, 0.3)
    act(karen, b + 2, None)
    (a, s1), (_, b) = seg(12, "you're")
    rest(mom, a, "ra", "la", ease=6); pose(mom, a, 6, head=(0, 0, 0)); react(mom, "sideeye", a); say(mom, 12, "la", 0.7, (karen,))
    shf(a, s1, (MOM, (KS.x, KS.y), 4.8), 3.0, -20, lens=26)
    ld = wf(12, "loudest")
    for k, av in enumerate((r1, r2, r3)): life.act2(av, ld + 2 + k * 3, "shush"); react(av, "annoyed", ld + k * 3); life.look(av, ld, (KS.x, KS.y, 4.7))
    life.nod_yes(me, ld + 2, 2, 8)
    shf(s1, ld + 4, ((KS.x, KS.y), (TX, 2.5), 4.75), 3.4, 35, lens=24, subj=karen)
    sh(lb, ld + 4, b, (13.0, -1.2, 6.0), (13.0, -9.0, 3.6), 22, dl=(0, -0.6, 0))  # the readers all shush her
    react(karen, "embarrassed", ld + 6)
    # ======================= 13: Karen marches to the desk, slams the bell (+ beat) =======================
    (a, s1), (_, b) = seg(13, "and")
    BELL = LS.BELL; KD = (BELL[0], 6.5)
    react(karen, "furious", a, s1); life.stomp(karen, a + 2, s1 - 3, (KS.x, KS.y, 0), (KD[0], KD[1], 0), 6)
    kit.follow(lb, a, s1, karen["root"], (-4.5, -6.0, 4.6), (0, 0, 3.6), 24)
    for k in range(4): ctx.sfx("step", a + 6 + k * 7, 0.45)
    at(karen, s1 - 2, (KD[0], KD[1], 0), (KD[0], 12), ease=2)
    sl = wf(13, "slammed") + 2; hits = [sl + k * 7 for k in range(9)]
    for k, h in enumerate(hits):
        pose(karen, h - 3, 2, ra=(-128, 0, -6)); pose(karen, h, 2, ra=(-96, 0, -6))
        K._key(P["bell_button"], "location", h - 1, (0, 0, 0.55), 1); K._key(P["bell_button"], "location", h, (0, 0, 0.42)); K._key(P["bell_button"], "location", h + 3, (0, 0, 0.55))
        ctx.sfx("ding", h, 0.55)
    react(karen, "angry", s1)
    sh(lb, s1, wf(13, "over"), (BELL[0] + 1.4, BELL[1] - 2.4, 4.6), (BELL[0], BELL[1], 3.5), 30, dl=(-0.1, 0.2, 0))  # the bell, close
    sh(lb, wf(13, "over"), b + 36, (15.0, 8.0, 7.5), (KD[0], KD[1], 4.4), 24, dl=(-0.3, 0, -0.3))  # from behind the desk: Karen slamming
    # ======================= 14: "Hello! I want the head librarian! Now!" =======================
    a, b = L(14)
    react(karen, "furious", a, b + 6); pose(karen, a, 4, waist=(18, 0, 0), ra=(-60, 0, -10)); say(karen, 14, None, 1.6)
    nw = wf(14, "now"); pose(karen, nw - 2, 2, ra=(-128, 0, -6)); pose(karen, nw, 2, ra=(-96, 0, -6)); ctx.sfx("ding", nw, 0.7)
    shf(a, b, (KD, (KD[0], 12), 4.75), 3.0, 20, lens=24)
    # ======================= 15: the chair turns (+ beat) =======================
    a, b = L(15); slw = wf(15, "slowly")
    pose(karen, a, 6, waist=(0, 0, 0)); rest(karen, a, "ra", ease=6); react(karen, "suspicious", a + 4)
    K._key(sw, "rotation_euler", slw, (0, 0, math.radians(180)), 1); K._key(sw, "rotation_euler", b + 26, (0, 0, math.radians(0)), None)
    for fc in sw.animation_data.action.fcurves:
        for kp in fc.keyframe_points:
            if kp.co.x >= slw: kp.interpolation = 'SINE'
    ctx.sfx("tick", slw, 0.4); ctx.sfx("tick", slw + 20, 0.4); ctx.sfx("scared", b + 24, 0.45)
    react(gma, "smug", slw); rest(gma, slw, "ra", "la", ease=1); act(gma, slw, "cross", 1)
    sh(lb, a, b + 30, (KD[0] + 2.8, KD[1] - 2.6, 6.6), (11.0, 11.6, 4.6), 26, dl=(-0.2, 0.6, -0.2))  # past Karen at the chair
    for av in (me, mom, r1, r2, r3): life.look(av, slw + 6, (11.0, 11.6, 4.5), 10)
    # ======================= 16: "It was Grandma..." =======================
    (a, s1), (_, b) = seg(16, "wearing")
    GM = (11.0, 11.6); gh = 5.05
    react(gma, "chad", a); life.look(gma, a, (KD[0], KD[1], 4.7))
    shf(a, s1, (GM, (KD[0], KD[1]), gh), 2.8, 0, lens=28, push=0.18); ctx.sfx("ding", a + 4, 0.4)
    bd = wf(16, "badge")
    pose(gma, bd - 4, 5, la=(-70, 0, -5))  # she taps her badge
    sh(lb, s1, bd + 8, (GM[0] + 0.45, 10.0, 4.5), (GM[0] + 0.45, GM[1] - 0.5, 3.9), 30, dl=(0, 0.2, 0))  # the badge, close
    react(karen, "big_eyes", bd + 6); life.flinch(karen, bd + 6, 0.7)
    shf(bd + 8, b + 16, (KD, (KD[0], 12), 4.75), 2.6, -15, lens=28, pz=bd + 10, amount=1.15)
    rest(gma, b, "la", ease=6)
    # ======================= 17-19: Grandma and Karen =======================
    a, b = L(17)
    act(gma, a, "cross"); react(gma, "sideeye", a); say(gma, 17, None, 0.8, (karen,)); life.look(gma, a, (KD[0], KD[1], 4.7))
    sh(lb, a, b, (14.4, 4.8, 5.4), (10.4, 8.6, 4.6), 26, dl=(-0.3, 0.2, 0))  # two-shot across the desk
    a, b = L(18)
    react(karen, "confused", a); life.act2(karen, a, "shrug"); say(karen, 18, None, 1.1, (gma,)); life.look(karen, a, (GM[0], GM[1], 5.0))
    shf(a, b, (KD, (KD[0], 12), 4.75), 2.8, 25, lens=26)
    act(karen, b + 4, None)
    (a, s1), (_, b) = seg(19, "story")
    react(gma, "chad", a); act(gma, a, None); say(gma, 19, None, 0.8, (karen,))
    life.act2(gma, s1 - 2, "point_left"); life.look(gma, s1, (LS.STORY[0], LS.STORY[1], 3.0), 8)
    shf(a, s1, (GM, (KD[0], KD[1]), gh), 2.8, -25, lens=28)
    sh(lb, s1, b + 2, (6.0, 3.0, 6.0), (-14.0, 11.0, 3.0), 22, dl=(0, 0, -0.3))  # whip to the story corner
    # ======================= 20: story time (+ beat) =======================
    a, b = L(20)
    SC = (LS.STORY[0], LS.STORY[1] + 2.5); seat = P["story_chair_seat_z"]
    show_between(P["open_book"], 0, a)
    at(leo, a, (SC[0], SC[1] - 2.6, 0), (SC[0], SC[1]), ease=1); rest(leo, a, ease=1); react(leo, "determined", a)
    cl0, cl1 = wf(20, "climbed"), wf(20, "chair") + 4
    for k in range(4):  # climbs up onto the seat, a knee and a pull at a time
        f = cl0 + k * (cl1 - cl0) // 4
        K._key(leo["root"], "location", f, (SC[0], SC[1] - 2.0 + k * 0.3, k * 0.6), 2)
        pose(leo, f, 2, ra=(-150 if k % 2 else -110, 0, 0), la=(-110 if k % 2 else -150, 0, 0), ll=(-60 if k % 2 else 0, 0, 0), rl=(0 if k % 2 else -60, 0, 0))
    turn(leo, cl1, (SC[0], -5), 5); sit(leo, cl1 + 4, seat, (SC[0], SC[1] - 0.2), 0, ease=6); react(leo, "happy", cl1 + 6)
    sh(lb, a, cl1 + 4, (SC[0] + 4.6, SC[1] - 6.0, 3.2), (SC[0], SC[1] - 1.0, 2.2), 26, dl=(-0.4, 0.4, 0))  # Leo climbing
    ctx.sfx("step", cl0 + 4, 0.3); ctx.sfx("boing", cl1 + 4, 0.3)
    op = wf(20, "opened"); act(leo, op - 2, "read", 6); show_between(story_bk, op + 2, L(23)[0])
    sh(lb, cl1 + 4, wf(20, "and"), (SC[0] + 0.4, SC[1] - 3.8, 3.4), (SC[0], SC[1] - 0.6, 2.8), 30, dl=(0, 0.4, 0))  # the book opens
    ctx.sfx("rustle", op + 2, 0.6)
    tw = wf(20, "twenty")
    spots = [(SC[0] - 5 + (k % 4) * 3.3, SC[1] - 6.5 - (k // 4) * 2.2) for k in range(12)]
    for k, (kd, sp) in enumerate(zip(kids, spots)):
        start = (sp[0] + (-12 if k % 2 else 10), sp[1] - 8, 0)
        f0_ = tw - 14 + k * 2; f1_ = wf(20, "sat") + (k % 4)
        bounce_walk(kd, f0_, f1_, start, (sp[0], sp[1], 0), 5); react(kd, "happy", f0_)
        sit(kd, f1_ + 1, 0.35, sp, (SC[0], SC[1]), ease=3); react(kd, random.choice(("starstruck", "happy", "love")), f1_ + 4)
    sh(lb, wf(20, "and"), b + 10, (SC[0] + 9.0, SC[1] - 15.0, 8.0), (SC[0] + 0.5, SC[1] - 4.5, 1.8), 22, dl=(-1, 1, -0.6))  # kids running in
    for k in range(5): ctx.sfx("step", tw + k * 4, 0.2)
    # the beat: Leo reads aloud (silent mouth flaps), kids laugh and clap
    for f in range(b - 4, b + 40, 9): avatar_flap(leo, f)
    for k, kd in enumerate(kids):
        if k % 3 == 0: life.act2(kd, b + 10 + k, "clap"); pose(kd, b + 18 + k, 3, ra=(-70, 0, -10), la=(-70, 0, 10)); act(kd, b + 26 + k, "clap", 3)
        react(kd, "laugh", b + 8 + k)
    sh(lb, b + 10, L(21)[0], (SC[0] + 0.2, SC[1] + 0.2, 5.4), (SC[0], SC[1] - 7.0, 1.5), 24, dl=(0, -0.3, 0))  # over Leo's shoulder: his audience
    ctx.sfx("giggle", b + 12, 0.4); ctx.sfx("clap", b + 22, 0.4)
    # ======================= 21-22: "That's impossible!" / banned =======================
    a, b = L(21)
    react(karen, "meltdown", a, b + 30); life.act2(karen, a, "both_head"); say(karen, 21, None, 1.8); life.look(karen, a, (SC[0], SC[1], 3.0), 6)
    shf(a, b, (KD, (SC[0], SC[1]), 4.75), 2.8, 0, lens=26, pz=a + 2, amount=1.15)
    act(karen, b + 6, None)
    (a, s1), (_, b) = seg(22, "you're")
    life.act2(gma, a, "shush"); react(gma, "sideeye", a); say(gma, 22, None, 0.8); life.look(gma, a, (KD[0], KD[1], 4.7))
    shf(a, s1, (GM, (KD[0], KD[1]), gh), 2.8, 20, lens=28)
    ex = wf(22, "exit"); life.act2(gma, ex - 2, "point")
    for k, av in enumerate((r1, r2, r3)): life.act2(av, ex + k * 2, "point"); react(av, "smug", ex + k * 2)
    react(karen, "sad", s1 + 4)
    sh(lb, s1, b + 2, (14.4, 4.8, 5.4), (10.4, 8.6, 4.6), 26, dl=(-0.3, 0.2, 0))
    # ======================= 23: the trip into the bean bags (+ beat) =======================
    a, b = L(23)
    bx, by = LS.BEANS; TRIP = (TX - 5.4, TY + 0.6); K0 = (TX + 1.0, TY + 4.6)
    at(karen, a, (K0[0], K0[1], 0), (TRIP[0], TRIP[1]), ease=1)
    react(karen, "furious", a, a + 30); life.stomp(karen, a, wf(23, "book") + 2, (K0[0], K0[1], 0), (TRIP[0], TRIP[1], 0), 6)
    kit.follow(lb, a, wf(23, "book"), karen["root"], (-4.0, -5.0, 4.4), (0, 0, 3.0), 24); ctx.sfx("step", a + 6, 0.4); ctx.sfx("step", a + 14, 0.4)
    tr = wf(23, "book") + 3
    react(karen, "terrified", tr + 2); pose(karen, tr, 3, waist=(45, 0, 0), ra=(-170, 0, 30), la=(-170, 0, -30), ll=(-40, 0, 0), rl=(30, 0, 0))
    ctx.sfx("whoosh", tr + 2, 0.7)
    land = wf(23, "landed") + 2
    K._key(karen["root"], "location", tr, (TRIP[0], TRIP[1], 0), 1)
    pk_ = ((TRIP[0] + bx) / 2 - 0.5, (TRIP[1] + by) / 2, 5.0)
    K._key(karen["root"], "location", (tr + land) // 2, pk_, None); K._key(karen["root"], "location", land, (bx + 0.5, by + 0.6, 0.4), None)
    r0 = value_rot(karen, tr)
    K._key(karen["root"], "rotation_euler", tr, tuple(r0), 1); K._key(karen["root"], "rotation_euler", land - 2, (r0[0] + math.radians(-300), r0[1], r0[2]), None)
    K._key(karen["root"], "rotation_euler", land, (math.radians(-80), r0[1], r0[2]), None)
    sh(lb, tr - 2, land - 4, (TRIP[0] - 8.0, TRIP[1] - 2.0, 5.0), (TRIP[0], TRIP[1] - 1.0, 2.8), 22, dt=(0.5, -7.0, -1.5))  # the trip and the flight
    for k, bean in enumerate(P["beans"]):
        p0 = Vector(bean.location); d_ = (p0.xy - Vector((bx + 0.5, by + 0.6))).normalized() if (p0.xy - Vector((bx + 0.5, by + 0.6))).length > 0.1 else Vector((1, 0))
        K._key(bean, "location", land - 1, tuple(p0), 1); K._key(bean, "location", land + 6, (p0.x + d_.x * 0.8, p0.y + d_.y * 0.8, p0.z + 1.4 - 0.1 * k), None)
        K._key(bean, "location", land + 14, (p0.x + d_.x * 1.0, p0.y + d_.y * 1.0, p0.z), None)
        K._key(bean, "scale", land - 1, (2.6, 2.6, 1.8), 1); K._key(bean, "scale", land + 2, (3.0, 3.0, 1.2), None); K._key(bean, "scale", land + 10, (2.6, 2.6, 1.9), None)
    ctx.sfx("boing", land, 0.9); ctx.sfx("bounce", land + 4, 0.5)
    react(karen, "dizzy", land + 4, land + 60)
    sh(lb, land - 4, b + 46, (bx + 7.0, by + 3.5, 6.0), (bx + 0.3, by + 0.4, 1.2), 24, dl=(-0.6, -0.3, 0))  # into the bean bags
    for k, av in enumerate([leo] + kids[:6]): react(av, "laugh", land + 8 + k)
    for k, av in enumerate((r1, r2, r3, me, mom)): react(av, "laugh", land + 10 + k)
    ctx.sfx("giggle", land + 10, 0.6)
    # ======================= 24-25: the sign =======================
    a, b = L(24); S.flash(a, 5); ctx.sfx("whoosh", a, 0.4)
    at(karen, a, (0, -300, 0), ease=1)
    for k, kd in enumerate(kids): react(kd, "happy", a)
    for av in (r1, r2): act(av, a, "read", 1); react(av, "relieved", a)
    sh(lb, a, b, (12, -14, 11), (-8, 4, 2.0), 20, dl=(-2, 2, -1.5))
    (a, s1), (_, b) = seg(25, "stamped")
    sh(lb, a, s1, (-14.5, -10.6, 6.2), (-14.5, -15.6, 6.4), 28, dl=(0, -1.6, 0))
    sh(lb, s1, b + 50, (-13.9, -12.2, 4.8), (-13.9, -15.6, 4.6), 30, dl=(0, -1.0, 0.3)); ctx.sfx("pop", wf(25, "handprint"), 0.4)

    # line-of-sight report: every shot, at its middle frame, camera -> its aim point
    for st_, cam, f0, f1, _ in S.shots:
        c = st_.cams[cam] if isinstance(cam, str) else cam; st_.scene.frame_set((f0 + f1) // 2)
        dg = st_.scene.view_layers[0].depsgraph; dg.update()
        ce = c.evaluated_get(dg); te = c.constraints["Track To"].target.evaluated_get(dg)
        if not clear_view(st_.scene, ce.matrix_world.translation, te.matrix_world.translation, margin=1.2):
            o_, t_ = ce.matrix_world.translation, te.matrix_world.translation; d_ = t_ - o_
            hit_ = st_.scene.ray_cast(dg, o_, d_.normalized(), distance=d_.length)
            print("BLOCKED", f0, f1, tuple(round(v, 1) for v in o_), tuple(round(v, 1) for v in t_), "by", hit_[4].name if hit_[4] else None, round((hit_[1] - o_).length, 2), "of", round(d_.length, 2))
    print("SHF_FALLBACKS", blocked)

    # mouths for the spoken lines that weren't voiced through say()
    for i, (who, _) in enumerate(ctx.story["lines"]):
        if who == "me" and i != 2: kit.mouth(me, i)


def value_loc(av, f):
    from anim import value
    return value(av["root"], "location", f)


def value_rot(av, f):
    from anim import value
    return value(av["root"], "rotation_euler", f)


def avatar_flap(av, f):
    """One silent 'reading aloud' mouth flap at frame f."""
    import avatar
    avatar.lipsync(av, [("la", f, f + 5)])
