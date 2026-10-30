""""A Karen Cut Us In Line At The Ice Cream Shop" - reference #3 style (the supermarket Karen short): one bright pastel
shop, ~1 s shots, simple clear acting (gestures, head tilts, a sway while talking, short bouncy walks), a big
expression on every line, quick readable gags, captions UPPERCASE at the top. Voices 1.30x / 1.70x, no dead air.
Line numbers follow stories/karen.json (0-18). Sets: shop (the queue, counter, menu board, kitchen door) and
inserts (Karen's phone screen)."""
import math, random
import shortkit as K
from shortkit import Set, prim, mat, empty, show_between, pose, rest, at, turn, sit, idle, shake
import blocky, toys, town
from avatar import react
from storykit import Kit, wall_mat, hold
from acting import act, tilt, chatter, bounce_walk
import vfx

random.seed(14)
SKIN = (234, 190, 150)


def fr(pos, face, head, dist=3.0, ang=0.0, dz=0.15):
    from mathutils import Vector, Matrix
    yaw = math.radians(K.yaw_to(pos, face))
    d = Matrix.Rotation(math.radians(ang), 3, 'Z') @ Vector((math.sin(yaw), -math.cos(yaw), 0))
    return (pos[0] + d.x * dist, pos[1] + d.y * dist, head + dz), (pos[0], pos[1], head)


def build(ctx):
    S, L, A, D = ctx.short, ctx.L, ctx.A, ctx.D
    kit = Kit(ctx); seg, wf, sh = kit.seg, kit.wf, kit.sh

    def shf(st, f0, f1, who, dist=2.6, ang=0.0, lens=26, push=0.1, dz=0.15, **kw):
        loc, tgt = fr(*who, dist=dist, ang=ang, dz=dz)
        return sh(st, f0, f1, loc, tgt, lens, dl=tuple((t - l) * push for l, t in zip(loc, tgt)), **kw)

    def npc(name, lk, loc=(0, -300, 0), yaw=0):
        a = blocky.build(D, name, lk); at(a, 0, loc, yaw, ease=1); idle(a, ("head",), 0.02, 50); return a

    # ======================= the shop =======================
    sp = Set("shop", sky=(150, 205, 255), horizon=(230, 240, 255), sun=(55, 0, -30), sun_energy=3.0)
    sp.scene.view_settings.exposure = -0.35; sp.scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.9
    with sp:
        fm = K.image_mat(A + "floor_tile.png"); fm.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.35
        fl = prim("box", (34, 26, 0.2), (0, -1, -0.1), fm)
        tc = fm.node_tree.nodes.new("ShaderNodeTexCoord"); mp = fm.node_tree.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (0.25, 0.25, 0.25)
        img = [n for n in fm.node_tree.nodes if n.type == 'TEX_IMAGE'][0]
        fm.node_tree.links.new(tc.outputs["Object"], mp.inputs["Vector"]); fm.node_tree.links.new(mp.outputs[0], img.inputs[0])
        fl.scale = (34, 26, 0.2); mp.inputs["Scale"].default_value = (34 / 4, 26 / 4, 1)
        pinkw, mintw, cream = wall_mat((255, 225, 235)), wall_mat((150, 225, 200)), wall_mat((255, 250, 240))
        prim("box", (34, 0.4, 13), (0, 11.2, 6.5), pinkw); prim("box", (0.4, 26, 13), (-16.8, -1, 6.5), pinkw); prim("box", (0.4, 26, 13), (16.8, -1, 6.5), pinkw)
        for x0, w in ((0, 34),): prim("box", (w, 0.45, 1.1), (x0, 10.95, 9.9), mintw)  # green trim band like the reference
        prim("box", (0.45, 26, 1.1), (-16.55, -1, 9.9), mintw); prim("box", (0.45, 26, 1.1), (16.55, -1, 9.9), mintw)
        prim("box", (34, 26, 0.3), (0, -1, 13), cream)
        for x in (-10, 0, 10):  # ceiling lights
            prim("box", (4, 1.2, 0.1), (x, 2, 12.8), mat((255, 255, 250), 0.3, emit=2.5))
        toys.window(-16.5, -5.5, 6, 5, 4.5, 90, (170, 220, 255))
        K.plane_image(A + "shop_sign.png", (8, 2.1), (-2, 10.95, 11.6))
        menu_b = K.plane_image(A + "menu_before.png", (9, 5.8), (-2, 10.95, 7.6)); menu_a = K.plane_image(A + "menu_after.png", (9, 5.8), (-2, 10.94, 7.6))
        # counter with the glass case of tubs, sprinkle bucket, sample cups
        prim("box", (16, 2.0, 3.2), (-2, 4.0, 1.6), mat((255, 255, 255), 0.4), bevel=0.05)
        prim("box", (16, 0.1, 2.6), (-2, 2.98, 1.6), mat((245, 150, 180), 0.5))
        prim("box", (16.3, 2.3, 0.2), (-2, 4.0, 3.25), mat((250, 210, 225), 0.3))
        tub_cols = [(250, 240, 210), (120, 75, 50), (245, 150, 175), (170, 235, 200), (230, 200, 150), (120, 200, 245)]
        for k in range(10):
            prim("cylY", (1.0, 1.0, 0.7), (-8.6 + k * 1.3, 3.8, 3.7), mat(tub_cols[k % 6], 0.6))
        tears_tub = prim("cylY", (1.0, 1.0, 0.75), (4.4, 3.8, 3.72), mat((130, 190, 255), 0.4))
        bucket = empty("sprinkles", (-0.4, 3.9, 3.35)); prim("cylY", (1.3, 1.3, 1.0), (0, 0, 0.5), mat((245, 130, 170), 0.4), parent=bucket)
        scols = [(240, 70, 90), (250, 210, 60), (90, 170, 250), (120, 210, 120), (250, 250, 250), (200, 120, 240)]
        for k in range(40):
            a_ = random.uniform(0, 6.28); r_ = random.uniform(0, 0.5)
            prim("box", (0.18, 0.06, 0.06), (math.cos(a_) * r_, math.sin(a_) * r_, 1.02), mat(random.choice(scols), 0.5), rot=(0, 0, random.uniform(0, 180)), parent=bucket)
        cups = []
        for k in range(12):
            c = prim("cylY", (0.32, 0.32, 0.3), (-8.6 + (k % 6) * 0.5, 3.35 + (k // 6) * 0.5, 3.5), mat(tub_cols[k % 6], 0.5)); cups.append(c)
        # kitchen door, tables, a couple of customers
        door = prim("box", (3.6, 0.3, 7.4), (9, 10.9, 3.7), mat((250, 250, 250), 0.4), bevel=0.05)
        prim("cyl", (0.2, 1.2, 1.2), (9, 10.7, 5.2), mat((180, 220, 255), 0.05), rot=(0, 0, 90))
        for x, y in ((11, -5), (11, -10)):
            town.place("furniture/tableRound", (x, y, 0), 0)
            for dx in (-2.4, 2.4): town.place("furniture/chairCushion", (x + dx, y, 0), 90 if dx < 0 else -90)
        # stroller (hood toward me, the baby faces the counter)
        strl = empty("stroller", (-2, -1.4, 0)); strl.rotation_euler = (0, 0, math.radians(180)); smt = mat((120, 190, 240), 0.4)
        prim("box", (1.7, 2.2, 1.0), (0, 0, 1.25), smt, parent=strl, bevel=0.2); prim("box", (1.7, 1.0, 1.7), (0, 1.0, 2.1), smt, parent=strl, bevel=0.3)
        prim("box", (1.9, 0.12, 0.12), (0, 1.9, 3.3), mat((40, 40, 45), 0.4), parent=strl); prim("box", (0.1, 1.2, 0.1), (0.9, 1.4, 2.8), mat((40, 40, 45), 0.4), rot=(-35, 0, 0), parent=strl)
        prim("box", (0.1, 1.2, 0.1), (-0.9, 1.4, 2.8), mat((40, 40, 45), 0.4), rot=(-35, 0, 0), parent=strl)
        for dx in (-0.85, 0.85):
            for dy in (-0.85, 0.85): prim("cyl", (0.22, 0.7, 0.7), (dx, dy, 0.35), mat((40, 40, 45), 0.5), parent=strl)
        # the cast
        me = blocky.build(D, "me"); idle(me); at(me, 0, (-2, -4.3, 0), 180)
        baby = npc("rosie", {"skin": SKIN, "shirt_tex": A + "print_stripes_pink.png", "pants": (250, 170, 200), "hair": (230, 200, 140), "shoes": (250, 250, 250), "scale": 0.42})
        bow = prim("ball", (0.5, 0.3, 0.35), (0.45, 0, 1.3), mat((245, 90, 150), 0.4), parent=baby["head"])
        karen = npc("karen", {"skin": SKIN, "shirt_tex": A + "print_floral_lav.png", "pants": (245, 245, 250), "hair": (245, 225, 140), "shoes": (250, 250, 250)})
        hm = mat((245, 225, 140), 0.6)
        for sx in (-1, 1): prim("box", (0.3, 0.9, 1.15), (sx * 0.72, 0.22, 0.45), hm, parent=karen["head"], bevel=0.1)  # the bob
        prim("box", (1.5, 0.35, 1.15), (0, 0.66, 0.45), hm, parent=karen["head"], bevel=0.1)
        mom = npc("mom", {"skin": SKIN, "shirt": (165, 220, 235), "pants": (245, 245, 250), "hair": (235, 235, 240), "shoes": (250, 250, 250)})
        mh = mat((235, 235, 240), 0.6)
        prim("box", (1.45, 0.4, 2.1), (0, 0.66, -0.1), mh, parent=mom["head"], bevel=0.12)
        for sx in (-1, 1): prim("box", (0.28, 1.0, 1.7), (sx * 0.72, 0.15, 0.1), mh, parent=mom["head"], bevel=0.1)
        worker = npc("worker", {"skin": (160, 110, 80), "shirt": (245, 150, 180), "pants": (60, 60, 80), "hair": None, "hat": "cap", "hat_color": (245, 130, 170), "shoes": (40, 40, 45)})
        at(worker, 0, (-5.5, 6.6, 0), 0)
        cust = [npc(f"cust{k}", {"skin": s_, "shirt_tex": A + f"print_{p_}.png", "pants": (60, 60, 80), "hair": h_, "shoes": (40, 40, 45)})
                for k, (s_, p_, h_) in enumerate(((SKIN, "denim", (60, 40, 30)), ((160, 110, 80), "dots_white", (30, 20, 15))))]
        for k, c in enumerate(cust): sit(c, 0, 1.7, (11 + (-2.4 if k == 0 else 2.4), -5), 90 if k == 0 else -90, ease=1)
        sit(baby, 0, 1.75, (-2, -1.25), 180, ease=1)
        at(mom, 0, (3.4, -2.6, 0), 0)
        # props in hands
        cone = toys.ice_cream(); cone.scale = (0.45, 0.45, 0.45); hold(baby, cone, "ra", (0, -0.2, 0.4))
        drop = prim("ball", (0.42, 0.42, 0.4), (0, -300, 0), mat((255, 190, 210), 0.5))
        kphone = prim("box", (0.55, 0.1, 0.95), (0, 0, 0), mat((30, 30, 35), 0.3), bevel=0.04); hold(karen, kphone, "ra", (0, -0.25, 0.1), (90, 0, 0))
        mphone = prim("box", (0.55, 0.1, 0.95), (0, 0, 0), mat((240, 240, 245), 0.3), bevel=0.04); hold(mom, mphone, "ra", (0, -0.25, 0.1), (90, 0, 0))
        fphone = prim("box", (0.55, 0.95, 0.1), (0, -300, 0), mat((30, 30, 35), 0.3), bevel=0.04)
        spoon = prim("box", (0.12, 0.6, 0.06), (0, 0, 0), mat((250, 250, 250), 0.3)); hold(karen, spoon, "ra", (0, -0.3, 0.1))
        apron = K.plane_image(A + "apron.png", (1.5, 1.75), (0, -0.53, 1.0), parent=mom["waist"])
        hair_spr = empty("hair_sprinkles", (0, 0, 0.62), karen["head"])
        for k in range(26):
            prim("box", (0.2, 0.07, 0.07), (random.uniform(-0.75, 0.75), random.uniform(-0.6, 0.6), random.uniform(0.55, 0.85)), mat(random.choice(scols), 0.5),
                 rot=(0, random.uniform(-30, 30), random.uniform(0, 180)), parent=hair_spr)
        flying = [prim("box", (0.22, 0.08, 0.08), (0, -300, 0), mat(random.choice(scols), 0.5), rot=(random.uniform(0, 90), 0, random.uniform(0, 180))) for _ in range(24)]

    # ======================= inserts: Karen's phone screen =======================
    ins = Set("inserts", sky=(235, 225, 230), horizon=(245, 240, 245), sun=(40, 0, -30), sun_energy=3.0)
    with ins:
        prim("box", (60, 30, 1), (10, 6, -0.5), mat((250, 220, 235), 0.6))
        for k, img_ in enumerate(("live.png", "live_zero.png")):
            body = prim("box", (3.3, 0.3, 5.9), (k * 10, 0, 3.5), mat((25, 25, 30), 0.25), bevel=0.25)
            K.plane_image(A + img_, (3.0, 5.5), (k * 10, -0.17, 3.5), emit=1.0)

    # ======================= shots =======================
    KP = (-2, 1.6)  # Karen's place in line (in front of the stroller)
    # 0: "A Karen cut in front of my baby sister at the ice cream shop."
    (a, s1), (_, s2), (_, b) = seg(0, "my", "at")
    show_between(apron, L(13)[0] + 10); show_between(hair_spr, wf(6, "flew") + 10); show_between(menu_a, L(16)[0]); show_between(menu_b, 0, L(16)[0])
    show_between(kphone, L(10)[0], wf(15, "dropped") + 4); show_between(spoon, L(3)[0], L(5)[0]); show_between(cone, 0, L(18)[0])
    show_between(mphone, 0, L(13)[0] + 6); show_between(tears_tub, L(16)[0])
    for c in cups: show_between(c, wf(3, "twelve") + 2, L(5)[0])
    react(me, "smile", a); act(me, a, "hold", 1); react(baby, "happy", a); react(mom, "sideeye", a); act(mom, a, "phone", 1); pose(mom, a, 1, head=(-18, 0, 0))
    react(karen, "annoyed", a); bounce_walk(karen, a - 8, s2 + 6, (-13, -5, 0), (KP[0], KP[1], 0)); ctx.sfx("doorbell", a, 0.5)
    sh(sp, a, s1, (9, -15, 8.0), (-3, 1, 3.0), 22, dl=(-1, 2, -0.8))
    shf(sp, s1, s2, ((-2, -1.25), 180, 2.95), 2.0, 15, lens=26); ctx.sfx("pop", s1 + 2, 0.4)
    react(me, "shock", s2); react(baby, "blank", s2 + 2)
    sh(sp, s2, b, (8.5, -0.6, 4.8), (-2, -0.6, 3.4), 24, dl=(-0.6, 0, 0)); ctx.sfx("whoosh", s2 - 2, 0.5)
    # 1: Karen: "Move. Babies don't even eat ice cream."
    (a, s1), (_, b) = seg(1, "babies")
    turn(karen, a, (-2, -1.4), 4); react(karen, "angry", a); act(karen, a, "point"); chatter(karen, a, b, 1.2, 10)
    shf(sp, a, s1, (KP, (-2, -1.4), 4.75), 3.0, 0, pz=a + 2, amount=1.2); ctx.sfx("boing", a + 2, 0.3)
    react(baby, "blank", s1)
    sh(sp, s1, b, (0.4, 2.2, 5.6), (-2, -1.25, 2.8), 24, dl=(0.2, -0.3, -0.2))
    act(karen, b, None)
    # 2: "My sister looked up at her and said, 'Goo goo gaga.'"
    (a, s1), (_, b) = seg(2, "goo")
    pose(baby, a + 4, 6, head=(22, 0, 0)); react(baby, "big_eyes", a)
    sh(sp, a, s1, (-3.6, -3.0, 2.8), (-2, 1.6, 4.6), 22, dl=(0.2, 0.2, 0))
    react(baby, "happy", s1); chatter(baby, s1, b, 1.4, 8)
    shf(sp, s1, b, ((-2, -1.25), 180, 2.95), 1.7, -10, lens=28, dz=0.4, pz=wf(2, "gaga"), amount=1.15)
    for k, f in enumerate((s1, wf(2, "goo", 1), wf(2, "gaga"))): ctx.sfx("giggle" if k == 2 else "pop", f, 0.35)
    rest(baby, b, "head")
    # 3: "Then Karen ordered twelve samples. She tried every single one. Then she asked for twelve more."
    (a, s1), (_, s2), (_, b) = seg(3, "she", ("then", 1))
    turn(karen, a, (-2, 6), 4); react(karen, "smug", a); act(karen, a, "point")
    react(worker, "smile", a); act(worker, a + 4, "hold")
    sh(sp, a, s1, (-3.6, 5.6, 6.2), (-2, 1.6, 4.6), 24, dl=(0.2, -0.3, 0)); ctx.sfx("pop", wf(3, "twelve") + 2, 0.4)
    act(karen, s1, None)
    for k, f in enumerate(range(s1, s2 - 4, 6)):
        pose(karen, f, 2, ra=(-125, 0, -22)); pose(karen, f + 3, 2, ra=(-95, 0, -10)); ctx.sfx("nom", f + 1, 0.25)
    react(karen, "happy", s1)
    shf(sp, s1, s2, (KP, (-2, 6), 4.75), 2.3, -18, lens=26)
    react(worker, "blank", s2); react(worker, "meltdown", wf(3, "more") - 2)
    shf(sp, s2, b, ((-5.5, 6.6), 0, 4.75), 2.6, -12, lens=26, pz=wf(3, "more"), amount=1.15); ctx.sfx("sad", wf(3, "more"), 0.4)
    rest(karen, b, "ra", ease=3)
    # 4: Karen: "Chocolate tastes way too chocolatey."
    a, b = L(4); react(karen, "disgusted", a); act(karen, a, "shrug"); chatter(karen, a, b, 1.0, 10)
    shf(sp, a, b, (KP, (-2, 6), 4.75), 2.4, 12, pz=wf(4, "chocolatey"), amount=1.15); ctx.sfx("boing", wf(4, "chocolatey"), 0.35)
    act(karen, b, None)
    # 5: "When my sister finally got her cone, Karen bumped the stroller. The scoop landed right on the floor."
    (a, s1), (_, s2), (_, b) = seg(5, "karen", "the")
    at(karen, a, (-4.6, 1.8, 0), (-2, 6), ease=1); react(baby, "starstruck", a); act(baby, a, "hold", 1); pose(baby, a, 1, ra=(-70, 0, -10))
    shf(sp, a, s1, ((-2, -1.25), 180, 2.95), 1.9, 20, lens=26); ctx.sfx("sparkle", a + 2, 0.5)
    react(karen, "annoyed", s1); bounce_walk(karen, s1, s2 - 2, (-4.6, 1.8, 0), (0.4, 0.2, 0), 6)
    K._key(strl, "location", s1 + 8, (-2, -1.4, 0), 1); K._key(strl, "location", s1 + 11, (-2.6, -1.7, 0)); K._key(strl, "location", s1 + 18, (-2.5, -1.6, 0))
    K._key(strl, "rotation_euler", s1 + 8, (0, 0, math.radians(180)), 1); K._key(strl, "rotation_euler", s1 + 11, (0, 0, math.radians(172)))
    bz = baby["root"].location.z; K._key(baby["root"], "location", s1 + 8, (-2, -1.25, bz), 1); K._key(baby["root"], "location", s1 + 11, (-2.6, -1.55, bz)); K._key(baby["root"], "location", s1 + 18, (-2.5, -1.45, bz))
    c = sh(sp, s1, s2, (8, -3.0, 5.4), (-1.5, -0.6, 3.0), 24, dl=(-0.5, 0, 0)); shake(c, s1 + 10, 8, 0.25); ctx.sfx("boing", s1 + 9, 0.6); ctx.sfx("gasp", s1 + 12, 0.3)
    K._key(drop, "location", 0, (0, -300, 0), 1); K._key(drop, "location", s2, (-2.3, -0.4, 2.7), 1); K._key(drop, "location", s2 + 9, (-1.6, 0.1, 0.25))
    K._key(drop, "scale", s2 + 9, (1, 1, 1), 1); K._key(drop, "scale", s2 + 11, (1.6, 1.6, 0.35))
    react(baby, "shock", s2 + 9)
    sh(sp, s2, b, (0.5, -3.6, 1.1), (-1.6, 0.0, 0.5), 24, dl=(-0.2, 0.3, 0)); ctx.sfx("splat", s2 + 9, 0.8)
    with sp: vfx.burst("splash", (-1.6, 0.1, 0.9), s2 + 9, 2.2, (0.5, -3.6, 1.1), (255, 190, 215), step=2)
    act(baby, b, None)
    # 6: "My sister didn't cry. She blew a raspberry so hard, the sprinkles flew into Karen's hair."
    (a, s1), (_, s2), (_, b) = seg(6, "she", "the")
    at(karen, a, (0.4, 0.2, 0), (-2.5, -1.6), ease=1); react(karen, "smug", a)
    K._key(strl, "location", a, (-2.5, -1.6, 0), 1); sit(baby, a, 1.75, (-2.5, -1.45), 180, ease=1)
    react(baby, "sad", a); react(baby, "blank", a + (s1 - a) // 2)
    shf(sp, a, s1, ((-2.5, -1.45), 180, 2.95), 1.8, 0, lens=28); ctx.sfx("sad", a, 0.3)
    react(baby, "raspberry", s1)
    for k in range(0, s2 - s1, 4): pose(baby, s1 + k, 2, head=(0, 0, 8 if (k // 4) % 2 else -8))
    c = shf(sp, s1, s2, ((-2.5, -1.45), 180, 2.95), 1.5, 10, lens=28, pz=s1 + 2, amount=1.25); shake(c, s1 + 2, 10, 0.2)
    ctx.sfx("raspberry", s1, 0.9)
    f_fly = wf(6, "flew")
    for k, o in enumerate(flying):
        p1 = (0.4 + random.uniform(-0.5, 0.5), 0.2 + random.uniform(-0.4, 0.4), 5.2 + random.uniform(0, 0.4))
        K._key(o, "location", 0, (0, -300, 0), 1); K._key(o, "location", s2, (-0.4, 3.9, 4.4), 1)
        K._key(o, "location", s2 + 5, ((p1[0] - 0.4) / 2, 2.0, 6.2 + random.uniform(0, 1))); K._key(o, "location", f_fly + 10, p1)
        K._key(o, "location", f_fly + 11, (0, -300, 0), 1)
    rest(baby, s2, "head", ease=2); react(baby, "chad", s2); react(karen, "shock", f_fly + 10)
    sh(sp, s2, b, (4.5, -6.0, 5.0), (-1.0, 0.0, 4.0), 24, dl=(-0.3, 0.5, 0)); ctx.sfx("whoosh", s2 + 2, 0.6); ctx.sfx("pop", f_fly + 10, 0.6)
    with sp:
        for k, dx in enumerate((-0.6, 0.5)): vfx.burst("glint", (0.4 + dx, 0.0, 5.6 + 0.3 * k), f_fly + 10 + k * 4, 1.4, (4.5, -6.0, 5.0), step=1)
    # 7: Karen: "That baby just attacked me!"
    a, b = L(7); react(karen, "furious", a, b + 10); act(karen, a, "arms_out"); chatter(karen, a, b, 1.6, 8)
    c = shf(sp, a, b, ((0.4, 0.2), (-2.5, -1.6), 4.75), 3.0, 0, pz=a + 2, amount=1.2); shake(c, a + 2, 10, 0.3)
    act(karen, b, None)
    # 8: "Mom didn't even look up from her phone."
    a, b = L(8); react(mom, "sideeye", a)
    shf(sp, a, b, ((3.4, -2.6), 0, 4.75), 2.6, 15, dz=0.1); ctx.sfx("crickets", a, 0.5)
    # 9: Mom: "She's one. You're forty-five."
    (a, s1), (_, b) = seg(9, "you're")
    kit.speak(mom, 9, 0.6); tilt(mom, a, 10); react(mom, "sideeye", a)
    shf(sp, a, s1, ((3.4, -2.6), 0, 4.75), 2.0, -10, lens=28)
    turn(karen, s1, (3.4, -2.6), 3); react(karen, "shock", s1); act(karen, s1, "head")
    shf(sp, s1, b, ((0.4, 0.2), (3.4, -2.6), 4.75), 3.0, 0, pz=s1 + 2, amount=1.2); ctx.sfx("gasp", s1 + 2, 0.5)
    act(karen, b, None); tilt(mom, b, 0)
    # 10: "So Karen pulled out her phone and went live."
    (a, s1), (_, b) = seg(10, "and")
    at(karen, a, (0.4, 0.2, 0), (0.4, -6), ease=1); react(karen, "determined", a); act(karen, a + 2, "phone")
    shf(sp, a, s1, ((0.4, 0.2), (0.4, -6), 4.75), 2.8, 15); ctx.sfx("whoosh", a + 2, 0.3)
    sh(ins, s1, b, (0, -6.5, 3.5), (0, 0, 3.5), 34, dl=(0, 1.2, 0)); ctx.sfx("live", s1, 0.7)
    # 11: Karen: "This shop lets children eat ice cream! I want the owner. Now!"
    (a, s1), (_, b) = seg(11, "i")
    react(karen, "angry", a); chatter(karen, a, b, 1.8, 7)
    shf(sp, a, s1, ((0.4, 0.2), (0.4, -6), 4.75), 2.8, 0, lens=26)
    react(karen, "furious", s1, b + 8)
    c = shf(sp, s1, b, ((0.4, 0.2), (0.4, -6), 4.75), 1.9, 5, lens=28, pz=wf(11, "now"), amount=1.3); shake(c, wf(11, "now"), 12, 0.35)
    # 12: "Her live had zero viewers."
    a, b = L(12)
    sh(ins, a, b, (10, -6.0, 3.5), (10, 0, 3.6), 34, pz=wf(12, "zero"), amount=1.25); ctx.sfx("crickets", a, 0.7)
    # 13: "Then Mom put her phone down, tied on a pink apron that said owner, and walked behind the counter."
    (a, s1), (_, s2), (_, b) = seg(13, "tied", ("and", 0))
    act(mom, a + 4, None); rest(mom, a + 4, "head"); react(mom, "chad", a + 6)
    shf(sp, a, s1, ((3.4, -2.6), 0, 4.75), 2.6, -15)
    sh(sp, s1, s2, (3.4, -4.7, 3.6), (3.4, -2.6, 3.3), 28, pz=wf(13, "owner"), amount=1.2); ctx.sfx("sparkle", L(13)[0] + 10, 0.6); ctx.sfx("ding", wf(13, "owner"), 0.5)
    with sp: vfx.burst("ring", (3.4, -3.3, 3.4), L(13)[0] + 10, 3.0, (3.4, -4.7, 3.6), (255, 200, 225)); vfx.burst("glint", (4.1, -3.4, 4.0), wf(13, "owner"), 1.6, (3.4, -4.7, 3.6), step=1)
    S.flash(L(13)[0] + 10, 4)
    bounce_walk(mom, s2, b - 2, (3.4, -2.6, 0), (7.6, 1.0, 0), 6)
    sh(sp, s2, b, (-9, -12, 7.5), (2, 1, 3.0), 22, dl=(1, 1, 0)); ctx.sfx("step", s2 + 3, 0.4); ctx.sfx("step", s2 + 9, 0.4)
    at(mom, b, (-0.8, 6.6, 0), 0, ease=1); rest(mom, b, ease=1)
    at(worker, b, (-6.5, 6.6, 0), (-0.8, 6.6), ease=1); react(worker, "starstruck", b)
    # 14: Mom: "Hi. I'm the owner. You're banned."
    (a, s1), (_, s2), (_, b) = seg(14, "i'm", "you're")
    at(karen, a, (-0.8, 1.5, 0), 180, ease=1); act(karen, a, None); react(karen, "confused", a)
    react(mom, "smile", a); act(mom, a, "wave"); kit.speak(mom, 14, 0.6)
    sh(sp, a, s1, (-0.8, 3.5, 5.0), (-0.8, 6.6, 4.75), 26, dl=(0, 0.3, 0)); ctx.sfx("pop", a, 0.3)
    act(mom, s1, "hips"); react(mom, "chad", s1)
    shf(sp, s1, s2, ((-0.8, 6.6), 0, 4.75), 2.2, 15, lens=28); ctx.sfx("ding", s1 + 2, 0.4)
    act(mom, s2, "point"); react(karen, "meltdown", s2 + 2, b + 30)
    c = sh(sp, s2, b, (-0.8, 4.2, 4.9), (-0.8, 1.5, 4.75), 26, pz=s2 + 3, amount=1.3); shake(c, s2 + 3, 10, 0.3); ctx.sfx("scared", s2 + 2, 0.6)
    with sp: vfx.burst("burst", (-0.8, 2.2, 4.9), s2 + 3, 2.6, (-0.8, 4.2, 4.9), (255, 240, 200), step=1)
    # 15: "Karen dropped her phone right into the sprinkles."
    (a, s1), (_, b) = seg(15, "right")
    act(karen, a, "phone", 1); pose(karen, a + 4, 3, ra=(-20, 0, 0)); act(mom, a, "cross")
    K._key(fphone, "location", 0, (0, -300, 0), 1); K._key(fphone, "location", a + 4, (-1.0, 2.6, 4.6), 1); K._key(fphone, "location", s1 + 6, (-0.4, 3.9, 4.25))
    K._key(fphone, "rotation_euler", a + 4, (0, 0, 0), 1); K._key(fphone, "rotation_euler", s1 + 6, (math.radians(70), math.radians(20), 0))
    sh(sp, a, s1, (1.4, 3.7, 5.8), (-0.8, 1.5, 4.4), 26, dl=(-0.2, -0.2, 0)); ctx.sfx("whoosh", a + 4, 0.4)
    sh(sp, s1, b, (0.2, 1.6, 5.4), (-0.4, 3.9, 4.1), 30, pz=s1 + 6, amount=1.2); ctx.sfx("splat", s1 + 6, 0.7)
    with sp: vfx.burst("puff", (-0.4, 3.9, 4.3), s1 + 6, 1.1, (0.2, 1.6, 5.4), (255, 220, 240), step=2)
    bounce_walk(karen, b, b + 50, (-0.8, 1.5, 0), (-14, -6, 0), 6)
    # 16-18: the new flavor
    a, b = L(16); S.flash(a, 6); ctx.sfx("whoosh", a, 0.6)
    at(karen, a, (0, -300, 0), ease=1); act(mom, a, "hips"); react(mom, "smile", a); react(me, "happy", a); react(baby, "happy", a)
    K._key(strl, "location", a, (-2, -1.4, 0), 1); K._key(strl, "rotation_euler", a, (0, 0, math.radians(180)), 1); sit(baby, a, 1.75, (-2, -1.25), 180, ease=1); at(worker, a, (-5.5, 6.6, 0), 0, ease=1); react(worker, "smile", a)
    sh(sp, a, b, (6, -13, 7.5), (-2, 9, 6.6), 22, dl=(-1.5, 3, 0)); ctx.sfx("bell", a + 4, 0.2)
    (a, s1), (_, b) = seg(17, "it's")
    sh(sp, a, s1, (-3.6, 6.4, 6.8), (-4.2, 10.9, 6.8), 30, dl=(0, 0.6, 0)); ctx.sfx("sparkle", a, 0.5)
    sh(sp, s1, b, (4.4, 1.4, 4.9), (4.4, 3.8, 3.8), 30, pz=wf(17, "salty"), amount=1.2); ctx.sfx("ding", wf(17, "salty"), 0.5)
    a, b = L(18); react(baby, "chad", a); act(baby, a, "point_up"); react(mom, "laugh", a); react(me, "laugh", a)
    sh(sp, a, b + 36, (-2, 1.0, 3.2), (-2, -1.4, 2.9), 24, dl=(1.5, 6, 2.5)); ctx.sfx("giggle", a + 2, 0.5)

    # head motion for whoever is narrating on screen
    for i, (who, _) in enumerate(ctx.story["lines"]):
        if who == "narrator" and i in (0, 5, 16, 18): kit.speak(me, i, 0.4)
    # mouths move on every spoken line
    for i, (who, _) in enumerate(ctx.story["lines"]):
        if who in ("karen", "mom"): kit.mouth(karen if who == "karen" else mom, i)
