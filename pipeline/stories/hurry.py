""""Every Time Someone Tells Me To Hurry Up, I Get Faster" - reference #4 style (the user's chosen format from here on):
a power-rule list told in ~35 s, ONE sentence = ONE shot that shows exactly that sentence, the action starting with the
sentence and finishing inside it. Plain bright Roblox look, a SPEED meter floating over the hero, comic speech bubbles on
"HURRY UP!", a yellow ring flash when the power triggers, snappy R6 poses, meme faces, whooshes and booms.
Line numbers follow stories/hurry.json (0-13). Sets: inside (hallway x0, living room x100, classroom x200),
outside (house front x0, schoolyard x80, football field x160, sidewalk x240) and space (the planet)."""
import math, random
from mathutils import Vector, Matrix
import bpy
import shortkit as K
from shortkit import Set, prim, mat, empty, show_between, pose, rest, at, turn, sit, idle, shake, punch
import blocky, toys, town
from avatar import react
from storykit import Kit, hold, glasses, wall_mat, clear_view
from acting import act, chatter, bounce_walk
import life
import hurry_images as HI
from waterpark_set import torus

random.seed(44)
SKIN, TAN, BROWN = (234, 190, 150), (204, 142, 105), (150, 100, 70)
HAIR = {"mom": 8199034057, "grandma": 15440914286, "teacher": 10976405810, "x1": 11268431947, "x2": 4887515664, "x4": 9661319036}


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

    def person(name, lk, hair=None, lift=0.0):
        a = blocky.build(D, name, lk); at(a, 0, (0, -400, 0), 0, ease=1); idle(a, ("head",), 0.015, 50); life.alive(a)
        if hair:
            r = blocky.wear(D, a, hair); r.location.z += lift
        return a

    def hero(name):
        a = blocky.build(D, name); at(a, 0, (0, -400, 0), 0, ease=1); idle(a, ("head",), 0.015, 50); life.alive(a); return a

    def bubble(k, f0, f1):
        ctx.overlay(HI.bubble_name(k), f0, f1, channel=6); ctx.sfx("pop", f0, 0.35)

    meters = []

    def meter(av):
        """The SPEED meter floating over a hero copy: one plane per value, swapped by scale keys."""
        planes = {}
        for v in HI.METER:
            planes[v] = K.plane_image(A + HI.meter_name(v), (4.6, 1.5), (0, -0.2, 7.3), parent=av["root"], emit=0.6, name=f"meter{v}")
        meters.append(planes); return planes

    meter_keys = {}

    def set_meter(f, v):
        meter_keys[f] = v

    def aura(av, f, st):
        """Yellow power ring around the hero + a quick bass boom."""
        with st:
            r = torus("aura", 2.2, 0.16, (0, 0, 0), mat((255, 220, 60), 0.3, emit=6.0), 32, 10)
        r.parent = av["root"]; r.location = (0, 0, 2.6)
        for fr_, s_ in ((0, 0.0001), (f - 1, 0.0001), (f, 0.3), (f + 8, 1.6), (f + 12, 0.0001)):
            r.scale = (s_, s_, s_ * 0.5); r.keyframe_insert("scale", frame=fr_)
        for fc in r.animation_data.action.fcurves:
            for kp in fc.keyframe_points: kp.interpolation = 'LINEAR' if f <= kp.co.x <= f + 8 else 'CONSTANT'
        ctx.sfx("play", f, 0.45); ctx.sfx("sparkle", f + 2, 0.4)

    # ======================= INSIDE: hallway (x 0), living room (x 100), classroom (x 200) =======================
    ins = Set("inside", sun=(52, 0, -30), sun_energy=3.4)
    town.sky(ins, 0.9, 3.2, (52, 0, -30)); ins.scene.view_settings.look = 'Medium Contrast'; ins.scene.view_settings.exposure = 0.35
    with ins:
        tiles = K.image_mat(A + "tiles.png"); nt = tiles.node_tree; img = [n for n in nt.nodes if n.type == 'TEX_IMAGE'][0]
        geo = nt.nodes.new("ShaderNodeNewGeometry"); mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (0.12,) * 3
        nt.links.new(geo.outputs["Position"], mp.inputs["Vector"]); nt.links.new(mp.outputs[0], img.inputs[0])
        cream, blue = wall_mat((240, 235, 220)), wall_mat((110, 160, 210))
        # hallway: lockers both sides, ceiling lights, a far window
        town.slab((18, 70, 0.4), (0, 0, -0.2), tiles, "hall_floor")
        for sx in (-1, 1):
            prim("box", (0.5, 70, 12), (sx * 8.4, 0, 6), cream)
            for k in range(-16, 17):
                c = (60, 110, 190) if k % 2 else (70, 125, 205)
                prim("box", (1.0, 1.9, 7.2), (sx * 7.6, k * 2.0, 3.6), mat(c, 0.35), bevel=0.04)
                prim("box", (0.06, 0.25, 0.7), (sx * 7.08, k * 2.0 + 0.5, 4.0), mat((210, 210, 215), 0.2, metal=0.8))
                for z in (6.6, 6.8, 7.0): prim("box", (0.05, 1.2, 0.06), (sx * 7.08, k * 2.0, z), mat((40, 70, 120), 0.5))
        prim("box", (18, 70, 0.3), (0, 0, 12), wall_mat((250, 250, 248)))
        for y in range(-30, 31, 8): prim("box", (4, 1.4, 0.12), (0, y, 11.8), mat((255, 255, 250), 0.3, emit=3.0))
        prim("box", (18, 0.5, 12), (0, 34, 6), cream); toys.window(0, 33.7, 8, 5, 6.0, 0, (170, 215, 250))
        # living room: rug, armchair, lamp, TV, family photo wall
        LX = 100
        town.slab((30, 24, 0.4), (LX, 0, -0.2), mat((175, 125, 85), 0.45), "living_floor")
        lw = wall_mat((215, 225, 205))
        prim("box", (30, 0.5, 12), (LX, 10, 6), lw); prim("box", (0.5, 24, 12), (LX - 15, 0, 6), lw); prim("box", (0.5, 24, 12), (LX + 15, 0, 6), lw)
        prim("box", (30, 24, 0.3), (LX, 0, 12), wall_mat((250, 250, 245)))
        prim("box", (11, 8, 0.05), (LX, 2, 0.05), mat((170, 90, 70), 0.9))
        toys.armchair(LX - 2, 4, 0, (120, 80, 60)); toys.window(LX + 7, 9.8, 5, 4, 5.5, 0, (170, 215, 250))
        lamp, _ = toys.lamp(LX - 6, 6); toys.tv(LX + 8, -6, 180)
        for k, c in enumerate(((230, 200, 120), (180, 210, 230), (220, 170, 170))):
            prim("box", (1.6, 0.1, 1.2), (LX - 4 + k * 2.5, 9.7, 7.0 + (k % 2) * 0.6), mat(c, 0.6), bevel=0.05)
        # classroom: board, teacher's desk, rows of desks, clock
        CX = 200
        town.slab((34, 26, 0.4), (CX, 0, -0.2), mat((200, 185, 160), 0.5), "class_floor")
        prim("box", (34, 0.5, 12), (CX, 12, 6), cream); prim("box", (0.5, 26, 12), (CX - 17, 0, 6), cream); prim("box", (0.5, 26, 12), (CX + 17, 0, 6), cream)
        prim("box", (34, 26, 0.3), (CX, 0, 12), wall_mat((250, 250, 248)))
        K.plane_image(A + "chalkboard.png", (12, 6), (CX, 11.7, 6.0))
        prim("box", (5.0, 2.4, 2.8), (CX + 3.5, 7.0, 1.4), mat((150, 100, 60), 0.5), bevel=0.05)
        prim("box", (5.3, 2.7, 0.2), (CX + 3.5, 7.0, 2.9), mat((110, 70, 45), 0.4))
        for r_ in range(2):
            for c_ in range(3):
                d_ = toys.desk(); d_.location = (CX - 6 + c_ * 6, -1.5 - r_ * 5, 0); d_.rotation_euler = (0, 0, math.radians(180))
        # the cast inside
        me_i = hero("me_i"); mi = meter(me_i)
        gpa = person("grandpa", {"skin": SKIN, "shirt_tex": A + "print_cardigan.png", "pants": (90, 90, 100), "hair": (200, 200, 205), "shoes": (70, 45, 30)}); glasses(gpa)
        watch = prim("box", (0.5, 0.5, 0.25), (0, -0.52, -0.6), mat((220, 180, 60), 0.2, metal=0.9), parent=gpa["la"])
        teacher = person("teacher", {"skin": BROWN, "shirt": (170, 80, 120), "pants": (60, 60, 80), "hair": None, "shoes": (40, 40, 45)}, HAIR["teacher"]); glasses(teacher)
        stack = empty("tests"); [prim("box", (1.6, 2.1, 0.06), (0, 0, k * 0.07), mat((250, 250, 245), 0.8), rot=(0, 0, random.uniform(-6, 6)), parent=stack) for k in range(14)]
        hold(teacher, stack, "ra", (0.6, -0.7, 0.2), (80, 0, 0))
        test = toys.card(A + "test.png", 1.6, 2.1)
        extras = [person(f"kid{k}", {"skin": s_, "shirt": c_, "pants": (50, 50, 70), "hair": None, "shoes": (250, 250, 250)}, HAIR[h_])
                  for k, (s_, c_, h_) in enumerate(((TAN, (230, 120, 60), "x1"), (SKIN, (90, 160, 220), "x2"), (BROWN, (200, 80, 140), "x4")))]

    # ======================= OUTSIDE: house front (x 0), schoolyard (x 80), field (x 160), sidewalk (x 240) =======================
    out = Set("outside", sun=(50, 0, -35))
    town.sky(out, 0.9, 3.6, (50, 0, -35)); out.scene.view_settings.look = 'Medium Contrast'; out.scene.view_settings.exposure = 0.25
    with out:
        town.lawn(900)
        # house front: facade with door and windows, porch step, path, driveway
        prim("box", (26, 1.0, 12), (0, 12.5, 6), wall_mat((245, 235, 215))); prim("wedge", (28, 8, 5), (0, 14.0, 14.5), mat((170, 70, 60), 0.6))
        prim("box", (4.0, 0.3, 7.6), (0, 11.9, 3.8), mat((120, 70, 45), 0.5), bevel=0.05)
        prim("ball", (0.4, 0.4, 0.4), (1.3, 11.6, 3.8), mat((230, 200, 90), 0.2, metal=0.9))
        for x in (-8, 8): toys.window(x, 11.95, 5, 4, 6.0, 0, (170, 215, 250))
        prim("box", (8, 3, 0.6), (0, 10.0, 0.3), mat((200, 200, 205), 0.6))
        town.slab((4, 9, 0.12), (0, 4.0, 0.0), town.concrete(), "path"); town.slab((9, 22, 0.12), (12, 2.0, 0.0), town.concrete(), "driveway")
        for x in (-11, -6, 6): toys.flower_bush(x, 10.5, 0.8)
        town.tree(-20, 8, 1.0, 1); town.tree(24, 10, 1.1, 2)
        town.street(-12, length=700, width=12, walks=False)
        # the convertible in the driveway (open top, so we see me buckled in)
        car = empty("car", (12, 2.0, 0)); red = mat((215, 40, 45), 0.25)
        prim("box", (5.0, 9.6, 2.0), (0, 0, 1.6), red, parent=car, bevel=0.35); prim("box", (4.6, 2.6, 1.4), (0, -3.0, 2.9), red, parent=car, bevel=0.3)
        prim("box", (4.6, 1.8, 1.0), (0, 3.6, 2.8), red, parent=car, bevel=0.3)
        prim("box", (4.4, 0.15, 1.4), (0, -1.6, 3.5), mat((200, 230, 250), 0.05, alpha=0.5), rot=(-25, 0, 0), parent=car)
        for sx in (-1.1, 1.1): prim("box", (1.8, 1.8, 1.0), (sx, 0.8, 2.0), mat((40, 40, 45), 0.6), parent=car, bevel=0.2); prim("box", (1.8, 0.4, 2.2), (sx, 1.7, 2.9), mat((40, 40, 45), 0.6), parent=car, bevel=0.15)
        for sx in (-2.5, 2.5):
            for sy in (-3.0, 3.0): prim("cyl", (0.8, 1.8, 1.8), (sx, sy, 0.9), mat((30, 30, 35), 0.6), parent=car)
        # schoolyard: brick school wall, door, hoop, trash can
        SX = 80
        prim("box", (40, 1.0, 14), (SX, 14, 7), mat((175, 80, 60), 0.8)); prim("box", (6, 0.4, 8), (SX - 8, 13.4, 4), mat((70, 110, 170), 0.4))
        town.slab((40, 26, 0.12), (SX, 2, 0.0), town.asphalt(), "yard")
        can = empty("trash", (SX + 3.2, 2.0, 0)); cm = mat((120, 130, 135), 0.4, metal=0.6)
        prim("cylY", (2.0, 2.0, 3.0), (0, 0, 1.5), cm, parent=can); prim("cylY", (2.2, 2.2, 0.15), (0, 0, 3.05), mat((90, 100, 105), 0.4, metal=0.6), parent=can)
        lid = prim("cylY", (2.3, 2.3, 0.18), (0, 0, 3.25), cm, parent=can)
        hp = toys.hoop(); hp.location = (SX - 12, 8, 0)
        # football field: stripes, goal posts, bleachers
        FX = 160
        town.slab((60, 40, 0.1), (FX, 0, 0.0), mat((70, 150, 60), 0.85), "field")
        for x in range(FX - 25, FX + 26, 10): town.slab((0.4, 38, 0.02), (x, 0, 0.06), mat((250, 250, 250), 0.5), "yardline")
        for sx in (-1.6, 1.6): prim("cylY", (0.3, 0.3, 10), (FX + 26 + sx, 0, 5), mat((250, 220, 60), 0.4))
        prim("box", (3.6, 0.3, 0.3), (FX + 26, 0, 4), mat((250, 220, 60), 0.4))
        for k in range(4): town.slab((50, 3, 1.2 + k * 1.2), (FX, 22 + k * 3, (1.2 + k * 1.2) / 2), mat((170, 170, 180), 0.5), "bleacher")
        # sidewalk for the ending
        WX = 240
        town.slab((60, 6, 0.4), (WX, 0, 0.0), town.concrete(), "sidewalk"); town.slab((60, 10, 0.2), (WX, -8, -0.05), town.asphalt(), "road")
        for k in range(4): town.tree(WX - 20 + k * 13, 7, 0.9, 10 + k)
        # snail
        snail = empty("snail", (0, -400, 0)); sb = mat((140, 200, 110), 0.4)
        prim("box", (0.35, 1.4, 0.3), (0, 0, 0.15), sb, parent=snail, bevel=0.12); prim("ball", (0.3, 0.3, 0.4), (0, -0.7, 0.35), sb, parent=snail)
        for sx in (-0.08, 0.08): prim("cylY", (0.04, 0.04, 0.35), (sx, -0.75, 0.65), sb, rot=(-15, 0, 0), parent=snail)
        shell = prim("ball", (0.9, 0.7, 0.9), (0, 0.15, 0.7), mat((180, 120, 60), 0.4), parent=snail)
        # the cast outside
        me_o = hero("me_o"); mo = meter(me_o)
        mom = person("mom", {"skin": SKIN, "shirt_tex": A + "print_dots_teal.png", "pants": (245, 245, 250), "hair": None, "shoes": (250, 250, 250)}, HAIR["mom"])
        purse = empty("purse"); prim("box", (1.1, 0.5, 0.9), (0, 0, 0), mat((200, 80, 120), 0.5), parent=purse, bevel=0.12)
        prim("box", (0.8, 0.1, 0.6), (0, 0, 0.7), mat((140, 60, 90), 0.5), rot=(0, 0, 0), parent=purse)
        hold(mom, purse, "la", (0, -0.4, 0.2))
        bully = person("bully", {"skin": SKIN, "shirt_tex": A + "print_varsity.png", "pants_tex": A + "print_denim.png", "hair": None, "hat": "cap", "hat_color": (210, 40, 40), "shoes": (250, 250, 250)})
        coach = person("coach", {"skin": TAN, "shirt": (240, 240, 240), "pants": (40, 40, 60), "hair": None, "hat": "cap", "hat_color": (40, 70, 160), "shoes": (40, 40, 45)})
        whistle = prim("box", (0.3, 0.5, 0.25), (0, -0.3, 0), mat((230, 200, 40), 0.3), )
        hold(coach, whistle, "ra", (0, -0.3, 0.1))
        gma = person("grandma", {"skin": SKIN, "shirt_tex": A + "print_floral_lav.png", "pants": (90, 90, 120), "hair": None, "shoes": (60, 40, 30)}, HAIR["grandma"], 0.32); glasses(gma)
        suitcase = empty("suitcase"); prim("box", (1.6, 0.8, 2.2), (0, 0, -0.6), mat((70, 110, 170), 0.4), parent=suitcase, bevel=0.15)
        hold(gma, suitcase, "ra", (0, 0, 0.0))
        belt = prim("box", (0.25, 0.08, 2.6), (0, -0.53, 1.0), mat((40, 40, 45), 0.5), rot=(0, 38, 0), parent=me_o["waist"])

    # ======================= SPACE: the planet =======================
    sp = Set("space", sky=(5, 5, 15), horizon=(10, 10, 30), sun=(40, 0, -60), sun_energy=4.0)
    sp.scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.3
    with sp:
        pm = K.image_mat(A + "planet.png"); pm.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.6
        _im = [n for n in pm.node_tree.nodes if n.type == 'TEX_IMAGE'][0]; _tc = pm.node_tree.nodes.new("ShaderNodeTexCoord")
        _im.projection = 'SPHERE'; pm.node_tree.links.new(_tc.outputs["Object"], _im.inputs[0])
        planet = prim("ball", (16, 16, 16), (0, 0, 0), pm); planet.rotation_euler = (0, math.radians(23), 0)
        K._key(planet, "rotation_euler", 0, (0, math.radians(23), 0), 1); K._key(planet, "rotation_euler", 1200, (0, math.radians(23), math.radians(60)), None)
        atm = prim("ball", (16.8, 16.8, 16.8), (0, 0, 0), mat((120, 180, 255), 0.5, alpha=0.18))
        for k in range(160):
            a, b_, r = random.uniform(0, math.tau), random.uniform(-0.6, 0.9), random.uniform(60, 90)
            prim("ball", (0.25, 0.25, 0.25), (math.cos(a) * r * math.cos(b_), math.sin(a) * r * math.cos(b_), r * math.sin(b_)), mat((255, 255, 240), 0.5, emit=5.0))
        me_s = hero("me_s"); ms = meter(me_s); me_s["root"].scale = (1.6, 1.6, 1.6)
        trail = prim("box", (0.8, 7.0, 0.8), (0, 4.0, 2.5), mat((255, 220, 70), 0.3, emit=5.0, alpha=0.7), parent=me_s["root"])

    W0 = 0.0  # ground level
    H = 4.75   # adult head height standing

    # ======================= 0: the rule (hallway) =======================
    (a, s1), (_, b) = seg(0, "and")
    at(me_i, a, (0, -4, 0), 0, ease=1); react(me_i, "smug", a); act(me_i, a, "hips", 1)
    for k, ex in enumerate(extras): at(ex, a, (-3.5 + k * 3.5, 6 + k * 2, 0), 0, ease=1); react(ex, "annoyed", a)
    set_meter(0, 10); set_meter(wf(0, "faster"), 30)
    sh(ins, a, wf(0, "faster") + 2, (0.6, -10.5, 3.2), (0, -4, 4.4), 26, dl=(0, 2.4, 0.4))  # low angle, slow push
    aura(me_i, wf(0, "faster"), ins); react(me_i, "chad", wf(0, "faster") + 2)
    # "And everyone tells me to hurry up.": the hallway: everyone pointing at their watches / waving him on
    for k, ex in enumerate(extras):
        life.act2(ex, s1 + 2 + k * 3, ("point", "wave", "point_up")[k]); react(ex, ("angry", "annoyed", "furious")[k], s1 + k * 3)
        kit.mouth(ex, 0, s1, b)
    act(me_i, s1, None); react(me_i, "blank", s1)
    sh(ins, s1, b + 2, (5.5, -12.5, 6.5), (0, 3.5, 3.8), 22, dl=(-0.6, 1.2, 0))

    # ======================= 1: Mom "Hurry up, we're late!" =======================
    a, b = L(1)
    MOMP = (0, 10.2)
    at(mom, a, (MOMP[0], MOMP[1], 0.6), 0, ease=1); react(mom, "furious", a, b + 10); life.act2(mom, a, "point"); kit.mouth(mom, 1); chatter(mom, a, b, 1.5, 9)
    at(me_o, a, (-1.0, 6.4, 0), (0, 10.2), ease=1); react(me_o, "sleepy", a)
    sh(out, a, b + 4, (3.2, 3.8, 3.4), (MOMP[0], MOMP[1], 5.2), 24, dl=(0.2, 0.3, 0))  # low angle on Mom yelling
    bubble("mom", a + 2, b); set_meter(b - 2, 45)
    # ======================= 2: buckled in before she finds her keys =======================
    (a, s1), (_, b) = seg(2, "before")
    aura(me_o, a, out); ctx.sfx("whoosh", a, 0.7); ctx.overlay("speedlines.png", a, a + 10)
    sit(me_o, a, 2.5, (12 - 1.1, 2.8), 0, ease=1); show_between(belt, a, L(3)[0]); react(me_o, "chad", a + 1); act(me_o, a, "cross", 1)
    sh(out, a, s1, (5.5, -5.5, 7.0), (11.5, 2.5, 3.4), 24, dl=(0.5, 0.8, 0), pz=a + 2, amount=1.1)
    act(mom, s1, None); life.act2(mom, s1 + 2, "phone")
    for k in range(0, b + 15 - s1, 6): pose(mom, s1 + k, 3, ra=(-55 if (k // 6) % 2 else -75, 0, -25 if (k // 6) % 2 else -10))  # digging in the purse
    react(mom, "confused", s1); pose(mom, s1, 6, head=(-20, 0, 0))
    sh(out, s1, b + 15, (-2.6, 5.2, 5.2), (MOMP[0], MOMP[1], 4.6), 26, dl=(0.3, 0.3, 0)); ctx.sfx("rustle", s1 + 4, 0.5)
    # ======================= 3: Grandpa taps his watch. Nothing happens. =======================
    (a, s1), (_, s2), (_, b) = seg(3, "nothing", "tapping")
    LX = 100
    sit(gpa, a, 1.6, (LX - 2, 4.2), 0, ease=1); react(gpa, "annoyed", a)
    at(me_i, a, (LX + 2.2, 0.6, 0), (LX - 2, 4.2), ease=1); rest(me_i, a, ease=1); react(me_i, "smile", a)
    tp = wf(3, "tapped")
    pose(gpa, a, 1, la=(-75, 0, 25))
    for k in range(5): pose(gpa, tp + k * 6, 2, ra=(-70, 0, -40)); pose(gpa, tp + k * 6 + 3, 2, ra=(-62, 0, -30))
    sh(ins, a, s1, (LX - 3.4, 0.2, 4.2), (LX - 1.8, 4.2, 3.6), 26, dl=(0.2, 0.3, 0))  # Grandpa tapping his watch
    for k in range(5): ctx.sfx("tick", tp + k * 6, 0.35)
    react(me_i, "blank", s1)
    sh(ins, s1, s2, (LX + 4.5, -3.6, 5.0), (LX + 0.4, 2.0, 3.8), 24, dl=(-0.2, 0.3, 0)); ctx.sfx("crickets", s1, 0.5)  # both: nothing happens
    shf(ins, s2, b + 9, ((LX + 2.2, 0.6), (LX - 2, 4.2), H), 3.4, 15, lens=28, push=0.1)  # deadpan close-up
    # ======================= 4: Teacher "Hurry up and finish your test." =======================
    a, b = L(4); CX = 200
    at(teacher, a, (CX - 2.5, 8.0, 0), 0, ease=1); react(teacher, "angry", a); kit.mouth(teacher, 4); chatter(teacher, a, b, 1.2, 9)
    life.act2(teacher, a + 2, "point_left")
    sit(me_i, a, 1.6, (CX, -2.8), 180, ease=1); react(me_i, "blank", a)
    sh(ins, a, b + 2, (CX - 1.0, 2.2, 4.0), (CX - 2.5, 8.0, 4.9), 24, dl=(0, 0.3, 0))  # over the desks at the teacher
    bubble("teacher", a + 2, b); set_meter(b - 3, 65)
    # ======================= 5: finished before she handed it out =======================
    (a, s1), (_, b) = seg(5, "before")
    aura(me_i, a, ins); ctx.sfx("whoosh", a, 0.7); ctx.overlay("speedlines.png", a, a + 8)
    at(me_i, a, (CX + 3.5, 4.6, 0), (CX + 3.5, 7), ease=1); rest(me_i, a, ease=1); react(me_i, "chad", a)
    test.location = (CX + 3.5, 6.6, 3.02); test.rotation_euler = (math.radians(-90), 0, 0); show_between(test, a + 4)
    pose(me_i, a, 1, ra=(-95, 0, 0)); pose(me_i, a + 4, 2, ra=(-60, 0, 0)); ctx.sfx("slap", a + 4, 0.8)
    react(teacher, "shock", s1); life.flinch(teacher, s1, 0.7)
    sh(ins, a, b + 12, (CX + 1.0, 1.4, 6.2), (CX + 1.4, 7.0, 3.6), 24, dl=(0.2, 0.3, 0))  # me + test on the desk + teacher still holding the stack
    # ======================= 6: Bully "Hurry up, slowpoke." =======================
    a, b = L(6); SX = 80; BP = (SX, 2.0)
    at(bully, a, (BP[0], BP[1], 0), 0, ease=1); react(bully, "smug", a); life.act2(bully, a, "point"); kit.mouth(bully, 6); chatter(bully, a, b, 1.3, 8)
    at(me_o, a, (SX - 0.5, -2.2, 0), (BP[0], BP[1]), ease=1); rest(me_o, a, ease=1); react(me_o, "annoyed", a); act(me_o, a, None)
    sh(out, a, b + 2, (SX + 6.5, -1.0, 4.2), (SX - 0.2, 0.0, 4.6), 24, dl=(-0.4, 0, 0))  # side two-shot
    bubble("bully", a + 2, b); set_meter(b - 2, 80)
    # ======================= 7: circles until he's dizzy and falls in the trash =======================
    (a, s1), (_, s2), (_, b) = seg(7, "until", "and")
    aura(me_o, a, out); ctx.sfx("whoosh", a, 0.6)
    laps = 3; R = 2.6
    for k in range(laps * 8 + 1):
        f = a + 2 + k * (s1 - a - 2) // (laps * 8)
        ang_ = k / 8 * math.tau
        p = (BP[0] + math.cos(ang_) * R, BP[1] + math.sin(ang_) * R, 0.0)
        K._key(me_o["root"], "location", f, p, None)
        K._key(me_o["root"], "rotation_euler", f, (0, 0, ang_ + math.pi), None)
    for fc in me_o["root"].animation_data.action.fcurves:
        for kp in fc.keyframe_points:
            if a <= kp.co.x <= s1: kp.interpolation = 'LINEAR'
    for k in range(0, s1 - a, 4): pose(me_o, a + k, 2, ll=(40 if (k // 4) % 2 else -40, 0, 0), rl=(-40 if (k // 4) % 2 else 40, 0, 0), ra=(-60, 0, 0), la=(30, 0, 0))
    act(bully, a, None); react(bully, "confused", a)
    for k in range(0, s1 - a, 5): life.look(bully, a + k, (BP[0] + math.cos(k * 0.6) * 3, BP[1] + math.sin(k * 0.6) * 3, 4.6), 3)
    sh(out, a, s1, (SX + 0.5, -7.5, 6.5), (BP[0], BP[1], 2.8), 24, dl=(0, 1.2, 0)); ctx.overlay("speedlines.png", a, s1)
    for k in range(4): ctx.sfx("whoosh", a + 4 + k * 8, 0.35)
    at(me_o, s1, (SX - 3.5, -1.2, 0), (BP[0], BP[1]), ease=1); rest(me_o, s1, ease=1); react(me_o, "smug", s1); act(me_o, s1, "cross", 1)
    react(bully, "dizzy", s1, b + 30)
    for k in range(0, s2 - s1 + 2, 6): pose(bully, s1 + k, 3, waist=(0, 12 if (k // 6) % 2 else -12, 0), head=(0, -14 if (k // 6) % 2 else 14, 0))
    shf(out, s1, s2, (BP, (BP[0], BP[1] - 5), H), 4.2, 15, lens=26)  # the dizzy close-up
    ctx.sfx("boing", s1 + 2, 0.4)
    # "and fell in the trash": he totters over to the can and topples in head first, legs sticking up
    CN = (SX + 3.2, 2.0)
    K._key(bully["root"], "location", s2, (BP[0], BP[1], 0), 1); K._key(bully["root"], "location", s2 + 8, (CN[0] - 1.2, CN[1], 0.6), None)
    K._key(bully["root"], "location", wf(7, "trash") + 4, (CN[0], CN[1], 5.0), None)
    r0 = bully["root"].rotation_euler.copy()
    K._key(bully["root"], "rotation_euler", s2, tuple(r0), 1); K._key(bully["root"], "rotation_euler", wf(7, "trash") + 4, (math.radians(180), 0, r0.z), None)
    pose(bully, s2 + 4, 5, ra=(-170, 0, 20), la=(-170, 0, -20)); react(bully, "scream", s2 + 4)
    K._key(lid, "location", wf(7, "trash") + 2, (0, 0, 3.25), 1); K._key(lid, "location", wf(7, "trash") + 10, (2.2, -0.5, 0.2), None)
    K._key(lid, "rotation_euler", wf(7, "trash") + 2, (0, 0, 0), 1); K._key(lid, "rotation_euler", wf(7, "trash") + 10, (math.radians(80), 0, 0), None)
    for k in range(0, 30, 5): pose(bully, wf(7, "trash") + 6 + k, 3, ll=(25 if (k // 5) % 2 else -25, 0, 0), rl=(-25 if (k // 5) % 2 else 25, 0, 0))  # kicking legs
    sh(out, s2, b + 18, (CN[0] + 5.5, -5.0, 5.0), (CN[0] - 0.6, CN[1], 2.8), 24, dl=(-0.3, 0.5, 0)); ctx.sfx("clang", wf(7, "trash") + 4, 0.9)
    # ======================= 8: Coach "Hurry up!" =======================
    a, b = L(8); FX = 160; CP = (FX, 0.0)
    at(coach, a, (CP[0], CP[1], 0), 0, ease=1); react(coach, "furious", a, b + 6); kit.mouth(coach, 8)
    life.act2(coach, a, "arms_out"); ctx.sfx("whistle", a - 6, 0.6)
    at(me_o, a, (FX + 2.6, -3.0, 0), (CP[0], CP[1]), ease=1); rest(me_o, a, ease=1); react(me_o, "determined", a); act(me_o, a, None)
    sh(out, a, b + 2, (FX - 1.5, -4.0, 3.4), (CP[0], CP[1], 5.0), 24, pz=a + 2, amount=1.15)
    bubble("coach", a + 1, b + 2); set_meter(b - 2, 100)
    # ======================= 9: I lapped the whole planet =======================
    a, b = L(9)
    aura(me_s, a - 2, sp)
    laps = 2; R = 11.0
    for k in range(laps * 16 + 1):
        f = a + k * (b + 18 - a) // (laps * 16)
        ang_ = k / 16 * math.tau
        K._key(me_s["root"], "location", f, (math.cos(ang_) * R, math.sin(ang_) * R * 0.6, math.sin(ang_) * R * 0.8), None)
        K._key(me_s["root"], "rotation_euler", f, (0, 0, ang_ + math.pi), None)
    for fc in me_s["root"].animation_data.action.fcurves:
        for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
    pose(me_s, a, 2, ra=(-170, 0, 0), la=(30, 0, 0), ll=(-20, 0, 0), rl=(20, 0, 0)); react(me_s, "chad", a)
    sh(sp, a, b + 18, (0, -30, 8), (0, 0, 0), 30, dl=(0, 4, -2)); ctx.sfx("whoosh", a, 0.8); ctx.sfx("whoosh", a + 15, 0.6); ctx.sfx("cheer", b, 0.3)
    # ======================= 10: Grandma moves in =======================
    (a, s1), (_, b) = seg(10, "she")
    at(mom, a - 4, (0, -400, 0), ease=1); bounce_walk(gma, a - 4, s1, (6, -2, 0), (1.6, 8.2, 0.0), 7); react(gma, "happy", a)
    at(me_o, a, (-2.4, 7.0, 0), (1.6, 8.2), ease=1); rest(me_o, a, ease=1); react(me_o, "nervous", a)
    sh(out, a, s1, (-6.0, -4.0, 5.0), (1.6, 6.0, 3.8), 22, dl=(0.6, 0.6, 0)); ctx.sfx("step", a + 6, 0.3); ctx.sfx("step", a + 18, 0.3)
    at(gma, s1, (1.6, 8.2, 0), (-2.4, 7.0), ease=4); react(gma, "smile", s1); react(me_o, "worried", s1 + 4)
    sh(out, s1, b, (-4.6, 2.0, 5.2), (0, 7.6, 4.6), 26, dl=(0.2, 0.4, 0))  # Grandma and me at the door
    # ======================= 11: "Take your time, sweetie." (+ the meter drains) =======================
    a, b = L(11)
    react(gma, "love", a); kit.mouth(gma, 11); chatter(gma, a, b, 0.8, 12); pose(gma, a, 6, head=(0, 12, 0))
    shf(out, a, b, ((1.6, 8.2), (-2.4, 7.0), H + 0.2), 2.8, 0, lens=28)
    bubble("grandma", a + 1, b + 6)
    react(me_o, "terrified", b - 2)
    for k, v in enumerate(range(100, -1, -10)): set_meter(b - 4 + k * 2, v)
    sh(out, b - 2, b + 16, (1.0, 4.6, 5.2), (-2.4, 7.0, 4.8), 26, dl=(-0.4, 0.3, 0)); ctx.sfx("pause", b - 2, 0.7)
    # ======================= 12: slowest kid in town; a snail passes =======================
    (a, s1), (_, b) = seg(12, "a")
    WX = 240
    react(me_o, "sad", a)
    at(me_o, a, (WX + 2.0, 0, 0.2), (WX - 10, 0), ease=1); bounce_walk(me_o, a + 1, b + 30, (WX + 2.0, 0, 0.2), (WX + 1.4, 0, 0.2), 30)  # barely moving
    for f in range(a, b + 30, 30): pose(me_o, f, 15, waist=(18, 0, 0))
    sh(out, a, s1, (WX + 2.5, -7.5, 4.6), (WX + 1.8, 0, 3.6), 24, dl=(0, 1.0, 0)); ctx.sfx("sad", a + 6, 0.35)
    K._key(snail, "location", 0, (WX + 5.0, -1.4, 0.2), 1); K._key(snail, "location", s1, (WX + 5.0, -1.4, 0.2), 1); K._key(snail, "location", b + 14, (WX - 1.0, -1.4, 0.2), None)
    snail.rotation_euler = (0, 0, math.radians(90))
    for fc in snail.animation_data.action.fcurves:
        for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
    react(me_o, "cry", s1, b + 30)
    sh(out, s1, b + 16, (WX + 1.2, -6.5, 2.4), (WX + 1.6, -0.4, 1.6), 22, dt=(-1.5, 0, 0.6))  # low: the snail passes in front of me
    ctx.sfx("tick", s1 + 6, 0.3)
    # ======================= 13: CTA =======================
    a, b = L(13)
    at(me_o, a, (WX, 0, 0.2), 0, ease=1); rest(me_o, a, ease=1); react(me_o, "worried", a); life.act2(me_o, a + 2, "arms_out"); kit.mouth(me_o, 13, a, b)
    chatter(me_o, a, b, 1.0, 12)
    shf(out, a, b + 60, ((WX, 0), 0, H + 0.2), 3.6, 0, lens=26, push=0.12)
    bubble("cta", wf(13, "comment"), b + 50)

    # ======================= the meters: every hero copy shows the same value at the same time =======================
    keys = sorted(meter_keys.items())
    for planes in meters:
        for v, p in planes.items():
            if "full" not in p: p["full"] = tuple(p.scale)
            for f, val in [(0, keys[0][1])] + keys:
                on = (val == v); p.scale = p["full"] if on else (0.0001, 0.0001, 0.0001); p.keyframe_insert("scale", frame=max(0, f))
            for fc in p.animation_data.action.fcurves:
                for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'

    # line-of-sight report
    for st_, cam, f0, f1, _ in S.shots:
        c = st_.cams[cam] if isinstance(cam, str) else cam; st_.scene.frame_set((f0 + f1) // 2)
        dg = st_.scene.view_layers[0].depsgraph; dg.update()
        ce = c.evaluated_get(dg); te = c.constraints["Track To"].target.evaluated_get(dg)
        if not clear_view(st_.scene, ce.matrix_world.translation, te.matrix_world.translation, margin=1.2):
            o_, t_ = ce.matrix_world.translation, te.matrix_world.translation; d_ = t_ - o_
            hit_ = st_.scene.ray_cast(dg, o_, d_.normalized(), distance=d_.length)
            print("BLOCKED", st_.name, f0, f1, "by", hit_[4].name if hit_[4] else None, round((hit_[1] - o_).length, 2), "of", round(d_.length, 2))
