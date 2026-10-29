""""Every Time I Say 'I'm Bored,' My Grandpa Gets 10 Years Younger" - faster-paced edit (voices at 1.60x / 1.75x):
shots of ~0.6-1.2 s, a cut on every sentence and often mid-sentence, punch zooms on punchlines, a sound effect on
nearly every beat, an expression change on every line, subtle talking head motion. R6 cast.
Line numbers follow stories/bored_grandpa.json (0-50). Sets: classroom, house (living room + kitchen + bedroom
corner), yard (driveway, street with the marathon finish, garage, lake with a dock), inserts (object close-ups).
Grandpa is nine separate characters (80, 70, 60, 50, 40, 30, 20, 10, 5 and 4); `age()` shows exactly one per set."""
import math, random
import bpy
from mathutils import Vector
import shortkit as K
from shortkit import Set, prim, mat, empty, vis, show_between, pose, rest, at, turn, walk, sit, idle, lin, shake, punch
import blocky, toys
from avatar import react
from storykit import Kit, rel, wall_mat, glasses, hold

random.seed(9)
CARDIGAN = (150, 110, 80)
G = {  # Grandpa at every age
    "g80": {"shirt": CARDIGAN, "pants": (95, 95, 105), "skin": (234, 190, 150), "hair": (215, 215, 220), "shoes": (70, 45, 30)},
    "g70": {"shirt": CARDIGAN, "pants": (95, 95, 105), "skin": (234, 190, 150), "hair": (170, 160, 150), "shoes": (70, 45, 30)},
    "g60": {"shirt": CARDIGAN, "pants": (95, 95, 105), "skin": (234, 190, 150), "hair": (130, 100, 75), "shoes": (70, 45, 30)},
    "g50": {"shirt": (235, 80, 60), "pants": (40, 40, 50), "skin": (234, 190, 150), "hair": (110, 75, 45), "shoes": (250, 250, 250)},
    "g40": {"shirt": (40, 120, 220), "pants": (40, 120, 220), "skin": (234, 190, 150), "hair": (85, 55, 35), "shoes": (250, 250, 250)},
    "g30": {"shirt": (30, 30, 35), "pants": (60, 70, 140), "skin": (234, 190, 150), "hair": (40, 30, 25), "shoes": (20, 20, 22)},
    "g20": {"shirt": (110, 200, 220), "pants": (70, 70, 90), "skin": (234, 190, 150), "hair": (60, 40, 25), "shoes": (250, 250, 250)},
    "g10": {"shirt": CARDIGAN, "pants": (95, 95, 105), "skin": (234, 190, 150), "hair": (90, 60, 35), "shoes": (70, 45, 30), "scale": 0.7},
    "g5": {"shirt": CARDIGAN, "pants": (95, 95, 105), "skin": (234, 190, 150), "hair": (150, 100, 60), "shoes": (70, 45, 30), "scale": 0.56},
    "g4": {"shirt": (250, 220, 120), "pants": (120, 170, 230), "skin": (234, 190, 150), "hair": (200, 150, 90), "shoes": (250, 250, 250), "scale": 0.5},
}
TEACHER = {"shirt": (170, 80, 120), "pants": (60, 60, 80), "skin": (204, 142, 105), "hair": (40, 25, 20), "pigtails": False}
MAILMAN = {"shirt": (70, 110, 180), "pants": (60, 70, 100), "skin": (160, 110, 80), "hat": "cap", "hat_color": (40, 60, 120)}
KIDS = [{"shirt": c, "pants": p, "skin": s, "hair": h, "scale": 0.75} for c, p, s, h in (
    ((240, 120, 60), (60, 60, 80), (234, 190, 150), (60, 40, 30)), ((120, 90, 220), (40, 40, 50), (160, 110, 80), (20, 20, 20)),
    ((80, 200, 220), (200, 80, 80), (250, 215, 180), (230, 200, 120)), ((250, 250, 250), (70, 120, 70), (204, 142, 105), (40, 30, 20)),
    ((230, 60, 90), (40, 60, 120), (234, 190, 150), (150, 90, 40)), ((150, 210, 90), (90, 70, 60), (180, 120, 90), (30, 20, 15)))]


def fr(pos, face, head, dist=3.0, ang=0.0, dz=0.15):
    """Camera in front of a character's face: pos (x, y), facing a point or yaw, head height. ang swings it
    around the character (degrees, + = to the character's left). Returns (camera location, aim point)."""
    from mathutils import Matrix
    yaw = math.radians(K.yaw_to(pos, face))
    d = Matrix.Rotation(math.radians(ang), 3, 'Z') @ Vector((math.sin(yaw), -math.cos(yaw), 0))
    return (pos[0] + d.x * dist, pos[1] + d.y * dist, head + dz), (pos[0], pos[1], head)


# where people stand in each set: (x, y), facing (point or yaw), head height
ME_COUCH = ((-4.0, 3.9), 0, 4.8); G_SHELF = ((9.0, 6.4), (-4, 3.9), 4.3); G30H = ((0.0, 2.0), (-4, 3.9), 4.6)
G20H = ((-6.5, 6.5), (-4, 3.9), 4.6); G10H = ((1.0, 2.6), (-4, 3.9), 3.2); G10PH = ((8.0, 1.6), (8.8, 2.6), 3.2)
ME_PH = ((7.0, 0.8), (8.8, 2.6), 4.6); ME_PLAN = ((-1.0, 0.0), 0, 4.6); G5 = ((1.5, 1.8), (-1, 0), 2.6); G4 = ((1.5, 1.8), (-1, 0), 2.3)
G4CART = ((2.5, 0.5), 0, 2.3); ME_BED = ((-13.4, -3.4), (-15.5, -2.0), 4.8); G4_COLOR = ((-15.0, -2.6), 0, 3.4)
ME_SIT_BED = ((-13.4, -3.0), (-15.0, -2.6), 4.8); G4_FLOOR = ((-12.6, -5.4), (-13.4, -3.0), 2.3)
G80B_SHELF = ((9.0, 6.2), (-1, 4), 4.3); ME_SHELF = ((6.8, 4.2), (10.5, 8.5), 4.6)
ME_C = ((2.2, -1.0), 180, 4.65); G10_C = ((-2.2, -1.0), 180, 3.7)


def npc(ctx, name, look, loc=(0, 0, 0), yaw=0):
    a = blocky.build(ctx.D, name, look); at(a, 0, loc, yaw, ease=1); idle(a, ("head",), 0.025, 50); return a


def hand_receiver(c=(210, 60, 60)):
    r = empty("hand_receiver"); m = mat(c, 0.35)
    prim("box", (1.3, 0.3, 0.22), (0, 0, 0), m, parent=r, bevel=0.1)
    for sx in (-0.55, 0.55): prim("box", (0.32, 0.36, 0.3), (sx, 0, -0.1), m, parent=r, bevel=0.1)
    return r


def grandpas(ctx, prefix, keys):
    out = {}
    for k in keys:
        a = npc(ctx, f"{prefix}_{k}", G[k], (0, -200, 0))
        if k in ("g80", "g70", "g10", "g5"): glasses(a)
        if k == "g30": glasses(a, dark=True)
        out[k] = a
    return out


def build(ctx):
    S, L, A = ctx.short, ctx.L, ctx.A
    timed = ctx.timed
    kit = Kit(ctx); seg, wf, sh = kit.seg, kit.wf, kit.sh

    def shf(st, f0, f1, who, dist=3.0, ang=0.0, lens=26, push=0.12, dz=0.15, **kw):
        """Shot of a character's face (who = (pos, facing, head)), easing in by `push` of the distance."""
        loc, tgt = fr(*who, dist=dist, ang=ang, dz=dz)
        dl = tuple((t - l) * push for l, t in zip(loc, tgt))
        return sh(st, f0, f1, loc, tgt, lens, dl=dl, **kw)
    sched = {}  # set name -> [(frame, grandpa key)]; one Grandpa visible at a time per set

    def age(st, f, k): sched.setdefault(st.name, []).append((f, k))

    def poof(f, gain=0.8): ctx.sfx("poof", f, gain); S.flash(f, 5)

    # ======================= sets =======================
    # ---- classroom
    cl = Set("class", sky=(140, 190, 250), horizon=(225, 235, 250), sun=(50, 0, -35), sun_energy=3.8)
    with cl:
        prim("box", (40, 30, 0.2), (0, -2, -0.1), mat((200, 185, 160), 0.5))
        wm = wall_mat((240, 230, 200))
        prim("box", (30, 0.4, 12), (0, 8, 6), wm); prim("box", (0.4, 22, 12), (-13, -2, 6), wm); prim("box", (0.4, 22, 12), (13, -2, 6), wm)
        prim("box", (30, 22, 0.3), (0, -2, 12), wall_mat((250, 250, 248)))
        K.plane_image(A + "chalkboard.png", (10, 5), (0, 7.75, 6.2))
        for x in (-11.5,):
            for y in (-6, 0, 5):
                prim("box", (0.3, 3, 3), (x + 1.2, y, 6), mat((200, 230, 255), 0.2, emit=0.6))
        prim("box", (4, 2, 2.6), (5, 5, 1.3), mat((150, 100, 60), 0.5), bevel=0.05)  # teacher's desk
        seats = {}
        for r_, y in enumerate((-1.0, -5.0)):
            for x in (-6.5, -2.2, 2.2, 6.5):
                dk = toys.desk(); dk.location = (x, y + 1.3, 0); dk.rotation_euler = (0, 0, math.radians(180))  # students face the board
                seats[(r_, x)] = (x, y)
        c_me = blocky.build(ctx.D, "me_c"); idle(c_me); sit(c_me, 0, 1.6, (2.2, -1.0), 180, ease=1)
        c_g10 = npc(ctx, "c_g10", G["g10"]); glasses(c_g10)
        teacher = npc(ctx, "teacher", TEACHER, (4.0, 3.5, 0), 0); glasses(teacher)
        kids = []
        for k, ((r_, x), (px, py)) in enumerate(sorted(seats.items())):
            if (r_, x) in ((0, 2.2), (0, -2.2)): continue
            kid = npc(ctx, f"kid{k}", KIDS[k % len(KIDS)]); sit(kid, 0, 1.6, (px, py), 180, ease=1); kids.append(kid)
    # ---- house
    hs = Set("house", sky=(120, 185, 255), horizon=(215, 232, 255), sun=(50, 0, -38), sun_energy=4.2, sun_color=(255, 244, 228))
    with hs:
        prim("box", (300, 300, 0.2), (0, 0, -0.15), mat((105, 180, 90), 0.9))
        prim("box", (36, 20, 0.2), (-3, -0.5, -0.05), mat((175, 125, 85), 0.45))
        for x in range(-20, 15, 2): prim("box", (0.06, 20, 0.01), (x, -0.5, 0.06), mat((150, 105, 70), 0.5))
        wm = wall_mat((205, 225, 190)); trim = wall_mat((255, 255, 255))
        prim("box", (36, 0.4, 11), (-3, 9.2, 5.5), wm); prim("box", (0.4, 20, 11), (-21, -0.5, 5.5), wm); prim("box", (0.4, 20, 11), (15, -0.5, 5.5), wm)
        prim("box", (36.5, 20.5, 0.3), (-3, -0.5, 11.1), wall_mat((250, 250, 245)))
        prim("box", (36, 0.3, 0.6), (-3, 8.95, 0.3), trim)
        wnd, pane = toys.window(7, 9.0, 4.0, 3.6, 5.2, 0, (160, 210, 255))
        prim("box", (11, 8, 0.05), (0, 2.5, 0.08), mat((170, 90, 70), 0.9))  # rug
        toys.couch(-4, 4.2, 0, (110, 140, 90)); toys.armchair(5, 3.4, 0, (160, 80, 60))
        gclk = toys.grandfather_clock(A + "dial_gold.png"); gclk["root"].location = (0, 8.4, 0)
        toys.swing_pendulum(gclk, 0, S.total + 30)
        for o, a in ((gclk["h"], 290), (gclk["m"], 60)): o.rotation_euler = (0, math.radians(a), 0)
        shelf = empty("rock_shelf", (10.5, 8.5, 0))
        for z in (3.0, 4.6): prim("box", (4.0, 1.0, 0.2), (0, 0, z), mat((140, 95, 60), 0.6), parent=shelf)
        for k in range(16): prim("ball", (0.35, 0.3, 0.25), (-1.6 + (k % 8) * 0.45, 0, 3.25 + (k // 8) * 1.6), mat(random.choice([(150, 150, 150), (120, 120, 125), (175, 170, 165)]), 0.8), parent=shelf)
        toys.card(A + "rocks.png", 2.2, 0.7).location = (10.5, 8.0, 5.6)
        doug = toys.cat("doug"); doug["root"].location = (1.6, 0.6, 0); doug["root"].scale = (0.9, 0.9, 0.9)
        for k, f in enumerate(range(0, S.total + 30, 24)):
            doug["tail"].rotation_euler = (0, math.radians(25 if k % 2 else -25), 0); doug["tail"].keyframe_insert("rotation_euler", frame=f)
        toys.table(8.8, 2.6, 1.6, 1.4, 2.0); phone, receiver = toys.landline(); phone.location = (8.8, 2.6, 2.1)
        rshelf = prim("box", (2.4, 0.8, 0.15), (-8, 8.7, 5.0), mat((140, 95, 60), 0.6))
        router = toys.router(); router.location = (-8, 8.6, 5.1)
        # kitchen
        frg, fz = toys.fridge(-17.5, 7.4)
        bcard = toys.card(A + "card_front.png", 1.0, 1.25); bcard.location = (-17.6, 6.0, 3.6)
        prim("box", (6, 2.6, 3.0), (-11.5, 7.6, 1.5), mat((250, 250, 250), 0.4), bevel=0.05); prim("box", (6.2, 2.8, 0.25), (-11.5, 7.6, 3.1), mat((70, 70, 80), 0.3))
        for k in range(10): prim("cylY", (0.3, 0.3, 0.6), (-13.5 + k * 0.45, 8.6, 4.6), mat(random.choice([(220, 60, 50), (230, 180, 50), (90, 160, 80), (150, 90, 50)]), 0.5))
        prim("box", (5, 0.5, 0.12), (-11.5, 8.7, 4.25), mat((140, 95, 60), 0.6))
        # bedroom corner and the card table
        toys.bed().location = (-15.5, -3.0, 0)
        cdesk = toys.table(2, -4, 3.2, 2.0, 2.4)
        chair_me = toys.chair(2, -6.3, 180); chair_g = toys.chair(2, -1.7, 0)
        for o in (cdesk, chair_me, chair_g): show_between(o, 0, 0)
        lamp1, l1 = toys.lamp(-9, 6.5); lamp2, l2 = toys.lamp(11.5, 4.5)
        h_me = blocky.build(ctx.D, "me_h"); idle(h_me)
        hg = grandpas(ctx, "h", ("g80", "g70", "g30", "g20", "g10", "g5", "g4"))
        h_g80b = npc(ctx, "h_g80b", G["g80"], (0, -200, 0)); glasses(h_g80b)   # the eighty-year-old again at the end
        hg["g80b"] = h_g80b
    # ---- yard
    yd = Set("yard", sky=(80, 165, 255), horizon=(205, 230, 255), sun=(52, 0, -40), sun_energy=4.6)
    with yd:
        prim("box", (400, 400, 0.2), (0, 0, -0.1), mat((110, 190, 90), 0.9))
        toys.house(0, 16, 0, w=16, d=10, h=8, color=(240, 225, 190), roof=(150, 70, 60))
        prim("box", (7, 6, 6), (13, 15, 3), mat((230, 215, 180), 0.7), bevel=0.1); prim("box", (5.6, 0.2, 4.6), (13, 11.9, 2.3), mat((250, 250, 250), 0.5))
        prim("box", (7, 14, 0.12), (13, 4, 0.0), mat((190, 190, 195), 0.8))  # driveway
        prim("box", (300, 8, 0.12), (0, -12, 0.0), mat((90, 92, 100), 0.85))  # street
        for x in range(-120, 121, 8): prim("box", (3, 0.3, 0.02), (x, -12, 0.08), mat((255, 255, 255), 0.6))
        hp = toys.hoop(); hp.location = (13, 9.5, 0)
        mb = toys.mailbox(); mb.location = (-5, -7, 0)
        moto = toys.motorcycle(); moto.location = (8, -2, 0); moto.rotation_euler = (0, 0, math.radians(90))
        for x in (-6, 6): prim("cylY", (0.3, 0.3, 7), (x - 60, -12, 3.5), mat((240, 240, 240), 0.5))
        fin = K.plane_image(A + "finish.png", (12, 2.7), (-60, -12, 6.2))
        tape = prim("box", (12, 0.08, 0.15), (-60, -12, 2.8), mat((250, 250, 250), 0.5))
        toys.lake(0, 70)
        for x in range(-40, 41, 10): toys.tree(x + random.uniform(-2, 2), 30 + random.uniform(0, 4), 1.1)
        for x in range(-35, 36, 14): toys.tree(x, -24, 1.0)
        toys.clouds(10, (-90, 30, 30), (90, 130, 55), 3, 7)
        mower = empty("mower", (-7, 3, 0)); prim("box", (1.6, 2.0, 0.8), (0, 0, 0.7), mat((220, 50, 40), 0.4), parent=mower, bevel=0.1)
        prim("box", (0.12, 1.6, 0.12), (0, 1.4, 1.6), mat((40, 40, 45), 0.4), rot=(-40, 0, 0), parent=mower)
        y_me = blocky.build(ctx.D, "me_y"); idle(y_me)
        yg = grandpas(ctx, "y", ("g60", "g50", "g40", "g30", "g4", "g80"))
        mail = npc(ctx, "mailman", MAILMAN, (-5, -8.6, 0), 0)
        bball = toys.ball(); bball.location = (0, -200, 0)
        rodg = toys.rod(); rodm = toys.rod(); bt = toys.boot(); bt.location = (0, -200, 0)
    # ---- inserts: full-screen object close-ups on a desk
    ins = Set("inserts", sky=(235, 225, 210), horizon=(245, 240, 230), sun=(40, 0, -30), sun_energy=3.6)
    with ins:
        prim("box", (80, 30, 1), (20, 6, -0.5), mat((150, 100, 62), 0.45))
        prim("box", (80, 0.4, 20), (20, 9, 6), wall_mat((225, 210, 185)))
        cfront = toys.card(A + "card_front.png", 1.6, 2.0); cfront.location = (0, 0, 1.05)
        cin = toys.card(A + "card_inside.png", 1.6, 2.0); cin.location = (8, 0, 1.05)
        bj, bills = toys.jar(A + "bored_jar.png", 12); bj.location = (16, 0, 0); bj.scale = (1.4, 1.4, 1.4)
        jb = toys.juice_box(); jb.location = (24, 0, 0); jb.scale = (2.2, 2.2, 2.2)
        book = toys.box_prop(A + "storybook.png", 1.4, 0.3, 1.8, (120, 70, 160)); book.location = (32, 0, 0)
        cards = []
        for k in range(6):
            c = K.plane_image(A + ("card_face.png" if k % 2 else "card_back.png"), (0.75, 1.05), (40 + random.uniform(-0.8, 0.8), random.uniform(-0.5, 0.5), 0.02 + k * 0.01), rot=(0, 0, random.uniform(-30, 30)))
            cards.append(c)
        tooth = [prim("box", (0.25, 0.15, 0.32), (48 + dx, 0, 2.5), mat((250, 250, 245), 0.3), bevel=0.05) for dx in (-0.2, 0.2)]

    # ======================= time of day in the house (night for bedtime / midnight cards) =======================
    def light(f, night):
        sun = hs.sun.data; sun.energy = 0.9 if night else 4.2; sun.keyframe_insert("energy", frame=f)
        sun.color = lin((140, 160, 255) if night else (255, 244, 228))[:3]; sun.keyframe_insert("color", frame=f)
        bg = hs.scene.world.node_tree.nodes["Background"].inputs["Strength"]; bg.default_value = 0.12 if night else 1.25; bg.keyframe_insert("default_value", frame=f)
        for l in (l1, l2): l.energy = 900 if night else 0; l.keyframe_insert("energy", frame=f)
        pane.inputs["Emission Strength"].default_value = 0.15 if night else 1.4; pane.inputs["Emission Strength"].keyframe_insert("default_value", frame=f)
        c = lin((40, 50, 110) if night else (160, 210, 255)); pane.inputs["Emission Color"].default_value = c; pane.inputs["Emission Color"].keyframe_insert("default_value", frame=f)
    light(0, False); light(L(29)[0], True); light(L(42)[0], False)

    hs.__enter__()
    # ======================= 0-2: math class (cold open) =======================
    (a, s1), (_, b) = seg(0, "he")
    react(c_me, "blank", a); age(cl, 0, "c_g10")
    walk(c_g10, a, s1 - 2, (-9, 3, 0), (-2.2, -0.2, 0), 6, 22); sit(c_g10, s1, 1.6, (-2.2, -1.0), 180, ease=4)
    sh(cl, a, s1, (0.0, 5.6, 5.0), (-1.5, -1.5, 3.8), 20, dl=(0, -0.8, 0)); ctx.sfx("step", a + 6); ctx.sfx("step", a + 12)
    react(c_g10, "smile", s1); react(c_me, "big_eyes", s1 + 4)
    shf(cl, s1, b, ME_C, 2.6, 20, pz=s1 + 4, amount=1.3); ctx.sfx("boing", s1 + 4, 0.6)
    a, b = L(1); react(teacher, "happy", a); kit.speak(teacher, 1); turn(teacher, a, (-2.2, -1.0), 6)
    sh(cl, a, b, (2.0, 0.5, 4.8), (4.0, 3.5, 4.6), 26, dl=(0.3, 0.3, 0))
    a, b = L(2); react(c_g10, "smug", a); kit.speak(c_g10, 2)
    shf(cl, a, b, G10_C, 2.2, -15, pz=wf(2, "pension"), amount=1.3); ctx.sfx("ding", wf(2, "pension"), 0.5)

    # ======================= 3-10: the summer, the rule =======================
    a3, b3 = L(3); poof(a3)
    age(hs, 0, "g80")
    at(hg["g80"], 0, (5.0, 3.1, 0), 0, ease=1); sit(hg["g80"], 0, 1.5, (5.0, 3.2), 0, ease=1)
    sit(h_me, 0, 1.75, (-4.0, 3.9), 0, ease=1); pose(h_me, 0, None, waist=(-12, 0, 0))
    (a, s1), (_, b) = seg(3, "grandpa's")
    react(h_me, "sad", a)
    sh(yd, a, s1, (-8, -18, 4.0), (0, 10, 4.0), 22, dl=(2, 3, 0)); ctx.sfx("whoosh", a + 2, 0.5)
    sh(hs, s1, b, (-1.0, -6.5, 4.6), (-2.5, 3.6, 4.2), 22, dl=(0.4, 1.0, 0))
    (a, s1), (_, s2), (_, b) = seg(4, "video", "just")
    react(h_me, "annoyed", a)
    sh(hs, a, s1, (-2.6, 0.6, 4.8), (-4.0, 3.9, 4.8), 26, dl=(0.2, 0.3, 0)); ctx.sfx("crickets", a, 0.5)
    sh(hs, s1, s2, (-5.6, 1.0, 4.4), (-4.0, 3.9, 4.6), 30, pz=s1 + 2, amount=1.15)
    sh(hs, s2, s2 + (b - s2) // 2, (1.6, -1.6, 1.4), (1.6, 0.6, 1.1), 26, dl=(0, 0.4, 0)); ctx.sfx("tweet", s2 + 3, 0.3)
    sh(hs, s2 + (b - s2) // 2, b, (0.4, 4.6, 5.8), (0, 8.4, 6.0), 30, dl=(0, 0.5, 0)); ctx.sfx("tick", s2 + (b - s2) // 2, 1.0)
    # 5: "Want to see my rock collection? It's mostly gravel."
    a, b = L(5); at(hg["g80"], a, (9.0, 6.4, 0), (-4, 3.9), ease=1); rest(hg["g80"], a, "ll", "rl", "ll_knee", "rl_knee", ease=1)
    pose(hg["g80"], a, 1, waist=(14, 0, 0)); rock = prim("ball", (0.5, 0.45, 0.35), (0, 0, 0), mat((140, 140, 140), 0.8)); hold(hg["g80"], rock, "ra", (0, -0.3, 0.1))
    pose(hg["g80"], a + 4, 6, ra=(-80, 0, -10)); react(hg["g80"], "happy", a); kit.speak(hg["g80"], 5)
    sh(hs, a, b, (6.6, 3.0, 4.2), (9.0, 6.4, 4.1), 24, dl=(0.3, 0.3, 0)); ctx.sfx("pop", a + 4, 0.5)
    # 6: "On day one, I said 'I'm so bored.' Grandpa's back cracked. Then it uncracked."
    (a, s1), (_, s2), (_, b) = seg(6, "grandpa's", "then")
    react(h_me, "blank", a); kit.speak(h_me, 6, 0.6, a, s1)
    sh(hs, a, s1, (-3.0, 1.4, 4.8), (-4.0, 3.9, 4.8), 30, pz=wf(6, "bored") + 2, amount=1.2); ctx.sfx("crickets", wf(6, "bored") + 4, 0.4)
    react(hg["g80"], "shock", s1)
    c = shf(hs, s1, s2, G_SHELF, 3.4, 25, lens=24, pz=s1 + 2, amount=1.2); ctx.sfx("crack", s1 + 2, 1.0); shake(c, s1 + 2, 8, 0.3)
    pose(hg["g80"], s2 + 2, 4, waist=(0, 0, 0)); react(hg["g80"], "starstruck", s2 + 2)
    shf(hs, s2, b, G_SHELF, 3.4, -20, lens=22, dz=-1.0); ctx.sfx("crack", s2 + 3, 0.8); ctx.sfx("boing", s2 + 6, 0.5)
    # 7: "He stood up straight... His gray hair turned brown. He was seventy."
    (a, s1), (_, s2), (_, b) = seg(7, "his", ("he", 1))
    shf(hs, a, s1, G_SHELF, 3.0, -30)
    age(hs, s2, "g70"); at(hg["g70"], s2, (9.0, 6.4, 0), (-4, 3.9), ease=1); react(hg["g70"], "happy", s2); poof(s2, 0.7)
    shf(hs, s1, s2, G_SHELF, 3.0, 10); ctx.sfx("sparkle", s1 + 2, 0.5)
    react(h_me, "shock", s2)
    sh(hs, s2, b, (4.0, 0.6, 4.8), (7.0, 5.5, 4.6), 24, dl=(-0.4, 0.4, 0))
    # 8: "The next day, I said it again. He was sixty. He did a cartwheel. He hadn't done one since 1974."
    (a, s1), (_, s2), (_, s3), (_, b) = seg(8, ("he", 0), ("he", 1), ("he", 2))
    react(h_me, "suspicious", a)
    sh(hs, a, s1, (-2.8, 1.0, 4.8), (-4.0, 3.9, 4.8), 30, dl=(0.2, 0.3, 0)); ctx.sfx("crickets", a + 4, 0.35)
    age(yd, 0, "none"); age(yd, s1, "g60"); at(yg["g60"], s1, (-6, 0, 0), 0, ease=1); react(yg["g60"], "starstruck", s1)
    sh(yd, s1, s2, (-6, -6, 4.2), (-6, 0, 4.4), 26, pz=s1 + 2, amount=1.2); poof(s1, 0.6)
    g = yg["g60"]; K._key(g["root"], "location", s2, (-6, 0, 0), 1)
    K._key(g["root"], "location", s2 + 8, (-2.5, 0, 2.3)); K._key(g["root"], "location", s2 + 16, (1, 0, 0))
    g["root"].rotation_euler = (0, 0, 0); g["root"].keyframe_insert("rotation_euler", frame=s2)
    g["root"].rotation_euler = (0, math.radians(-360), 0); g["root"].keyframe_insert("rotation_euler", frame=s2 + 16)
    pose(g, s2, 2, ra=(-170, 0, 0), la=(-170, 0, 0)); rest(g, s2 + 18, "ra", "la", ease=4); ctx.sfx("whoosh", s2 + 2, 0.7)
    sh(yd, s2, s3, (-2.5, -9, 3.2), (-2.5, 0, 3.4), 22, dt=(1.5, 0, 0))
    react(g, "happy", s3); react(y_me, "shock", s3); at(y_me, 0, (4.5, -4.0, 0), (0, 0), ease=1)
    sh(yd, s3, b, (3.0, -7.0, 4.6), (2.5, 0, 4.2), 24, dl=(0.4, 0.6, 0)); ctx.sfx("clap", s3 + 4, 0.6)
    # 9: "That's when I figured out the rule..."
    (a, s1), (_, b) = seg(9, "every")
    react(h_me, "suspicious", a); react(h_me, "big_eyes", s1, b + 6)
    sh(hs, a, s1, (-3.2, 0.8, 4.8), (-4.0, 3.9, 4.8), 34, dl=(0.1, 0.4, 0))
    sh(hs, s1, b, (-3.8, 1.6, 4.9), (-4.0, 3.9, 4.8), 40, pz=wf(9, "younger"), amount=1.3); ctx.sfx("ding", wf(9, "younger"), 0.6)
    # 10: "At first, it was awesome."
    a, b = L(10); react(h_me, "grin", a); pose(h_me, a + 2, 4, ra=(-150, 0, 30))
    sh(hs, a, b, (-2.4, 0.0, 4.4), (-4.0, 3.9, 4.8), 24, pz=a + 3, amount=1.2); ctx.sfx("sparkle", a + 2, 0.6)
    rest(h_me, b, "ra")

    # ======================= 11-15: fifty, forty, thirty, twenty =======================
    (a, s1), (_, s2), (_, b) = seg(11, ("he", 1), ("he", 2))
    age(yd, a, "g50"); g = yg["g50"]
    walk(g, a, s2 + 4, (-60, -20, 0), (-60, -8, 0), 4, 40); react(g, "determined", a)
    sh(yd, a, s1, (-60, -4, 3.0), (-60, -16, 4.0), 22, dt=(0, 6, 0)); ctx.sfx("step", a + 4); ctx.sfx("step", a + 8)
    tape.keyframe_insert("scale", frame=s1 + 6); tape.scale = (0.01, 1, 1); tape.keyframe_insert("scale", frame=s1 + 8)
    react(g, "laugh", s1 + 6); pose(g, s1 + 6, 4, ra=(-170, 0, 20), la=(-170, 0, -20))
    sh(yd, s1, s2, (-56, -2, 2.0), (-60, -12, 5.0), 20, pz=s1 + 7, amount=1.15); ctx.sfx("pop", s1 + 7, 0.8)
    sh(yd, s2, b, (-60, 10, 9.0), (-60, -12, 2.0), 22, dl=(0, 2, 2)); ctx.sfx("crickets", s2 + 2, 0.5); ctx.sfx("clap", s2 + 6, 0.5)
    # 12: forty, basketball, dunk on the mailman
    (a, s1), (_, b) = seg(12, "then")
    age(yd, a, "g40"); g = yg["g40"]; at(g, a, (11.0, 2.0, 0), (13, 9.5), ease=1); at(y_me, a, (15.5, 2.5, 0), (11, 2), ease=1)
    hold(g, bball, "ra", (0, -0.6, 0)); pose(g, a, 1, ra=(-60, 0, 0))
    for k, f in enumerate(range(a, s1, 8)): pose(g, f, 3, ra=(-40 if k % 2 else -70, 0, 0))
    react(g, "smug", a); react(y_me, "annoyed", a + 6); ctx.sfx("bounce", a + 2, 0.8)
    sh(yd, a, s1, (8.0, -4.0, 3.6), (12.5, 3.0, 3.6), 22, dl=(0.4, 0.6, 0))
    at(mail, s1, (13.0, 8.0, 0), (13, 0), ease=1)
    K._key(g["root"], "location", s1 + 2, (11.0, 2.0, 0), 1); K._key(g["root"], "location", s1 + 10, (13.0, 7.6, 4.2)); K._key(g["root"], "location", b + 4, (13.0, 7.6, 3.4))
    pose(g, s1 + 2, 4, ra=(-175, 0, 0), la=(-175, 0, 0)); react(g, "furious", s1 + 6, b); react(mail, "shock", s1 + 10)
    sh(yd, s1, b, (9.0, 1.0, 2.0), (13, 8.4, 6.5), 20, pz=s1 + 11, amount=1.2); ctx.sfx("whoosh", s1 + 3, 0.5); ctx.sfx("clang", s1 + 11, 0.9)
    c = yd.cams[list(yd.cams)[-1]]; shake(c, s1 + 11, 10, 0.4)
    at(mail, b + 2, (-5, -8.6, 0), 0, ease=1)
    # 13: thirty, motorcycle, jacket, sunglasses inside
    (a, s1), (_, s2), (_, b) = seg(13, "and", ("and", 1))
    age(yd, a, "g30"); g = yg["g30"]; g["root"].parent = moto; sit(g, a, 2.45, (0, 0.5), 0, ease=1); pose(g, a, 1, ra=(-75, 0, 0), la=(-75, 0, 0))
    K._key(moto, "location", a, (8, -2, 0), 1); K._key(moto, "location", s1 + 4, (2, -2, 0))
    react(g, "smug", a); ctx.sfx("rev", a, 0.9)
    sh(yd, a, s1, (-2.0, -9.0, 2.0), (5, -2, 2.6), 20, dt=(-2.5, 0, 0)); ctx.sfx("rev", s1 - 4, 0.6)
    sh(yd, s1, s2, (6.0, -4.5, 4.4), (1.6, -2.0, 4.4), 26, pz=s1 + 2, amount=1.15); ctx.sfx("pop", s1 + 2, 0.5)
    age(hs, s2, "g30"); h30 = hg["g30"]; at(h30, s2, (0.0, 2.0, 0), (-4, 3.9), ease=1); react(h30, "smug", s2)
    rest(h_me, s2, "waist", ease=1); react(h_me, "annoyed", s2)
    shf(hs, s2, b, G30H, 3.0, 0); ctx.sfx("ding", s2 + 2, 0.4)
    # 14: "Kid, call me Hal."
    a, b = L(14); kit.speak(h30, 14); react(h30, "grin", a); pose(h30, a, 4, ra=(-95, 0, 20))
    shf(hs, a, b, G30H, 2.2, 15, pz=wf(14, "hal"), amount=1.25); ctx.sfx("boing", wf(14, "hal"), 0.4)
    rest(h30, b, "ra")
    # 15: twenty, Wi-Fi
    (a, s1), (_, s2), (_, b) = seg(15, "there", "so")
    age(hs, a, "g20"); g = hg["g20"]; at(g, a, (-6.5, 6.5, 0), (-4, 3.9), ease=1); react(g, "happy", a); kit.speak(g, 15, 0.6, a, s1)
    shf(hs, a, s1, G20H, 3.0, 0); react(h_me, "blank", s1)
    sh(hs, s1, s2, (-2.6, 1.0, 4.8), (-4.0, 3.9, 4.8), 30, pz=s1 + 2, amount=1.15); ctx.sfx("crickets", s1 + 2, 0.4)
    at(g, s2, (-9.8, 7.0, 0), (-8, 8.6), ease=1); pose(g, s2 + 2, 4, ra=(-170, 0, 0), la=(-170, 0, 0)); react(g, "determined", s2)
    sh(hs, s2, b, (-5.6, 6.2, 5.0), (-8.6, 8.0, 5.0), 24, dl=(-0.3, 0.3, 0)); ctx.sfx("ding", b - 8, 0.8); ctx.sfx("sparkle", b - 6, 0.6)
    rest(g, b, "ra", "la")

    # ======================= 16-19: ten, Mom calls =======================
    (a, s1), (_, b) = seg(16, "he")
    rest(h_me, a, "waist", ease=1); react(h_me, "grin", a); kit.speak(h_me, 16, 0.6)
    sh(hs, a, s1, (-2.8, 1.2, 4.8), (-4.0, 3.9, 4.8), 28, dl=(0.2, 0.3, 0)); ctx.sfx("crickets", a + 2, 0.3)
    age(hs, s1, "g10"); g10 = hg["g10"]; at(g10, s1, (1.0, 2.6, 0), (-4, 3.9), ease=1); react(g10, "happy", s1); poof(s1, 0.8)
    react(h_me, "terrified", s1 + 4)
    shf(hs, s1, b, G10H, 2.6, 0, pz=s1 + 3, amount=1.3)
    # 17: Mom: "Why is a child answering Grandpa's phone?"
    a, b = L(17); ctx.sfx("ring", a - 14, 0.6)
    rc_g = hand_receiver(); hold(g10, rc_g, "ra", (0, -0.2, 0.2), (90, 0, 90)); show_between(rc_g, a, L(18)[0])
    rc_m = hand_receiver(); hold(h_me, rc_m, "ra", (0, -0.2, 0.2), (90, 0, 90)); show_between(rc_m, L(18)[0], seg(18, "that's")[0][1])
    show_between(receiver, 0, a); vis(receiver, seg(18, "that's")[0][1], True)
    at(g10, a, (8.0, 1.6, 0), (8.8, 2.6), ease=1); pose(g10, a, 1, ra=(-160, 0, 40)); react(g10, "smile", a)
    shf(hs, a, b, G10PH, 2.6, 0)
    # 18: "I said, 'Wrong number,' and hung up. That's when I knew I had a problem."
    (a, s1), (_, b) = seg(18, "that's")
    at(h_me, a, (7.0, 0.8, 0), (8.8, 2.6), ease=1); pose(h_me, a, 1, ra=(-160, 0, 40)); react(h_me, "nervous", a)
    rest(g10, a, "ra", ease=1); react(g10, "confused", a)
    shf(hs, a, s1, ME_PH, 2.6, -20); ctx.sfx("click", s1 - 4, 1.0)
    rest(h_me, s1, "ra", ease=4); react(h_me, "embarrassed", s1)
    shf(hs, s1, b, ME_PH, 2.2, 10, pz=s1 + 2, amount=1.15)
    # 19: "So I made a plan. Never say 'I'm bored' again."
    a, b = L(19); at(h_me, a, (-1.0, 0.0, 0), 0, ease=1); react(h_me, "determined", a)
    sh(hs, a, b, (-1.0, -3.0, 4.6), (-1.0, 0.0, 4.6), 26, pz=a + 4, amount=1.2); ctx.sfx("whoosh", a, 0.4)

    # ======================= 20-29: the attempts, five, four =======================
    (a, s1), (_, b) = seg(20, "he")
    react(h_me, "smug", a); kit.speak(h_me, 20, 0.6, a, s1)
    sh(hs, a, s1, (-0.4, -2.0, 4.8), (-1.0, 0.0, 4.8), 30, dl=(0.1, 0.3, 0)); ctx.sfx("crickets", a + 4, 0.3)
    age(hs, s1, "g5"); g5 = hg["g5"]; at(g5, s1, (1.5, 1.8, 0), (-1, 0), ease=1); react(g5, "happy", s1); poof(s1, 0.7)
    react(h_me, "annoyed", s1 + 6)
    shf(hs, s1, b, G5, 2.2, 0, pz=s1 + 3, amount=1.25)
    # 21: bored jar
    (a, s1), (_, s2), (_, b) = seg(21, "every", ("i", 3))
    sh(ins, a, s1, (16.2, -4.2, 2.6), (16, 0, 1.2), 30, dl=(0, 1.0, -0.2), cap="auto"); ctx.sfx("pop", a + 2, 0.5)
    for k, bl in enumerate(bills):
        bl.keyframe_insert("location", frame=s1 + k * 2); z = bl.location.z; bl.location.z = z + 3; bl.keyframe_insert("location", frame=s1 + k * 2 - 6)
        bl.location.z = z
    for k in range(4): ctx.sfx("coin", s1 + k * 4, 0.5)
    sh(ins, s1, s2, (16.0, -3.2, 2.2), (16, 0, 1.4), 34, pz=s1 + 4, amount=1.1)
    react(h_me, "sad", s2); pose(h_me, s2, 4, la=(-50, 0, 30), ra=(-50, 0, -30))
    sh(hs, s2, b, (-0.4, -2.6, 4.6), (-1.0, 0.0, 4.6), 28, dl=(0.1, 0.3, 0)); ctx.sfx("sad", s2 + 2, 0.5)
    rest(h_me, b, "la", "ra")
    # 22: yawn, baby teeth
    (a, s1), (_, s2), (_, b) = seg(22, "his", "baby")
    react(h_me, "sleepy", a); pose(h_me, a, 4, head=(-20, 0, 0)); rest(h_me, s1, "head", ease=4)
    shf(hs, a, s1, ME_PLAN, 2.6, 0, pz=a + 3, amount=1.15); ctx.sfx("sigh", a, 0.6)
    teeth = []
    for dx in (-0.12, 0.12):
        t = prim("box", (0.16, 0.08, 0.2), (dx, -0.67, 0.42), mat((250, 250, 245), 0.3), parent=g5["head"], bevel=0.03); teeth.append(t)
        t.keyframe_insert("location", frame=s1 + 2); t.location.z -= 3.2; t.location.y -= 0.3; t.keyframe_insert("location", frame=s1 + 12)
        show_between(t, 0, s2 + 12)
    react(g5, "shock", s1 + 2)
    turn(g5, s1, (4.5, -1.5), 1)
    sh(hs, s1, s2, (4.3, -1.3, 2.8), (1.5, 1.8, 2.5), 26, dl=(-0.3, 0.3, 0), pz=s1 + 3, amount=1.2); ctx.sfx("pop", s1 + 4, 0.6); ctx.sfx("pop", s1 + 8, 0.5)
    sh(ins, s2, b, (48, -2.6, 2.9), (48, 0, 2.5), 34, dl=(0, 0.8, 0), cap="auto"); ctx.sfx("ding", s2 + 2, 0.4)
    # 23: busy - garage, lawn, spices
    (a, s1), (_, s2), (_, s3), (_, b) = seg(23, ("i", 1), "mowed", "alphabetized")
    react(h_me, "determined", a); sh(hs, a, s1, (-1.6, -3.0, 4.4), (-1.0, 0.0, 4.4), 26, pz=a + 2, amount=1.15)
    at(y_me, s1, (13, 9.8, 0), 0, ease=1); react(y_me, "determined", s1)
    for k, f in enumerate(range(s1, s2, 5)): pose(y_me, f, 2, ra=(-120 if k % 2 else -60, 0, 20))
    sh(yd, s1, s2, (12, 4.0, 3.8), (13, 9.8, 3.6), 24, dl=(0.4, 0.4, 0)); ctx.sfx("whoosh", s1, 0.4); ctx.sfx("rustle", s1 + 4, 0.6)
    walk(y_me, s2, s3 + 6, (-7, 1, 0), (-7, -6, 0), 5, 26); K._key(mower, "location", s2, (-7, 0, 0), 1); K._key(mower, "location", s3 + 6, (-7, -7, 0))
    for o in (mower,):
        for fc in o.animation_data.action.fcurves:
            for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
    sh(yd, s2, s3, (-9.5, -11.0, 3.6), (-7, -2, 3.4), 22, dt=(0, -2.5, 0)); ctx.sfx("rev", s2, 0.4)
    at(h_me, s3, (-11.5, 5.4, 0), (-11.5, 8.6), ease=1); pose(h_me, s3, 1, ra=(-140, 0, 0)); react(h_me, "suspicious", s3)
    sh(hs, s3, b, (-10.0, 3.0, 5.4), (-11.8, 8.6, 4.6), 26, dl=(-0.4, 0.4, 0)); ctx.sfx("pop", s3 + 3, 0.3); ctx.sfx("pop", s3 + 7, 0.3)
    rest(h_me, b, "ra")
    # 24: "Then I sighed. Just once. He started teething."
    (a, s1), (_, s2), (_, b) = seg(24, "just", "he")
    at(h_me, a, (-1.0, 0.0, 0), 0, ease=1); react(h_me, "relieved", a); pose(h_me, a + 2, 6, head=(-15, 0, 0))
    sh(hs, a, s1, (-0.8, -2.2, 4.8), (-1.0, 0.0, 4.8), 32, dl=(0, 0.3, 0)); ctx.sfx("sigh", a + 1, 0.9)
    react(h_me, "terrified", s1); rest(h_me, s1, "head", ease=3)
    shf(hs, s1, s2, ME_PLAN, 1.9, 0, lens=34, pz=s1 + 2, amount=1.3); ctx.sfx("scared", s1 + 2, 0.5)
    age(hs, s2, "g4"); g4 = hg["g4"]; at(g4, s2, (1.5, 1.8, 0), (-1, 0), ease=1); react(g4, "cry", s2, b + 4); poof(s2, 0.7)
    ring = prim("cylY", (0.5, 0.5, 0.12), (0, 0, 0), mat((120, 200, 255), 0.3)); hold(g4, ring, "ra", (0, -0.3, 0.3), (90, 0, 0)); show_between(ring, s2, L(26)[1])
    pose(g4, s2, 1, ra=(-150, 0, 20))
    shf(hs, s2, b, G4, 2.0, 0, pz=s2 + 3, amount=1.2); ctx.sfx("cry", s2 + 4, 0.4)
    # 25: "Grandpa was four years old."
    a, b = L(25); react(g4, "blank", a); react(h_me, "blank", a)
    sh(hs, a, b, (-0.2, -6.5, 3.0), (0.4, 1.0, 2.6), 22, dl=(0.4, 1.5, 0)); ctx.sfx("crickets", a, 0.4)
    # 26: "Juice box. Now."
    (a, s1), (_, b) = seg(26, "now")
    react(g4, "angry", a, b + 6); pose(g4, a, 3, ra=(-90, 0, 0)); kit.speak(g4, 26)
    shf(hs, a, s1, G4, 2.2, 60, pz=a + 2, amount=1.2)
    sh(ins, s1, b, (24.2, -3.0, 1.6), (24, 0, 0.9), 30, dl=(0, 0.8, 0), cap="auto"); ctx.sfx("pop", s1 + 1, 0.7)
    rest(g4, b, "ra")
    # 27: naps, cartoons, bit the mailman
    (a, s1), (_, s2), (_, b) = seg(27, ("he", 1), ("he", 2))
    at(g4, a, (-3.6, 3.9, 1.45), 0, ease=1); react(g4, "sleepy", a)
    sh(hs, a, s1, (-3.6, 0.6, 3.4), (-3.6, 3.9, 2.4), 28, dl=(0, 0.4, 0)); ctx.sfx("snore", a + 2, 0.5)
    at(g4, s1, (2.5, 0.5, 0), 0, ease=1); react(g4, "happy", s1); react(h_me, "annoyed", s1); pose(g4, s1, 2, ra=(-120, 0, 30))
    shf(hs, s1, s2, G4CART, 2.2, 0); ctx.sfx("boing", s1 + 2, 0.4)
    age(yd, s2, "g4"); yg4 = yg["g4"]; at(mail, s2, (-5, -8.6, 0), 0, ease=1); at(yg4, s2, (-4.6, -9.6, 0), 0, ease=1)
    react(yg4, "furious", s2, b + 10); react(mail, "terrified", s2 + 4); pose(yg4, s2, 2, waist=(30, 0, 0))
    sh(yd, s2, b, (-3.6, -13.0, 2.4), (-5, -8.6, 2.6), 22, pz=s2 + 4, amount=1.2); ctx.sfx("nom", s2 + 3, 0.9)
    # 28: Mailman: "Ow! Not again!"
    a, b = L(28); kit.speak(mail, 28); react(mail, "scream", a)
    K._key(mail["root"], "location", a, (-5, -8.6, 0), 1); K._key(mail["root"], "location", a + 6, (-5, -8.6, 1.2)); K._key(mail["root"], "location", a + 12, (-5, -8.6, 0))
    c = sh(yd, a, b, (-5.5, -13.6, 4.6), (-5, -8.6, 4.8), 26, pz=a + 2, amount=1.25); shake(c, a + 2, 10, 0.3)
    # 29: bedtime story
    (a, s1), (_, s2), (_, b) = seg(29, "he", "then")
    age(hs, a, "g4"); at(g4, a, (-15.5, -2.0, 1.8), 0, ease=1); pose(g4, a, 1, waist=(-60, 0, 0)); react(g4, "sleepy", a)
    at(h_me, a, (-13.2, -3.4, 0), (-15.5, -2.0), ease=1); sit(h_me, a, 1.8, (-13.4, -3.4), (-15.5, -2), ease=1)
    book2 = toys.box_prop(A + "storybook.png", 0.7, 0.15, 0.9, (120, 70, 160)); hold(h_me, book2, "la", (0, -0.3, 0.2), (90, 0, 0)); show_between(book2, a, b)
    pose(h_me, a, 1, la=(-80, 0, 20)); react(h_me, "smile", a); kit.speak(h_me, 29, 0.5, a, s1)
    shf(hs, a, s1, ME_BED, 3.0, -35); ctx.sfx("rustle", a + 2, 0.6)
    sh(hs, s1, s2, (-15.5, -6.5, 5.4), (-15.5, -1.8, 2.6), 26, dl=(0, 0.4, 0)); ctx.sfx("snore", s1 + 2, 0.5)
    pose(g4, s2, 3, waist=(0, 0, 0), ra=(-90, 0, 0)); react(g4, "annoyed", s2); react(h_me, "shock", s2 + 4)
    sh(hs, s2, b, (-17.8, -5.5, 4.6), (-15.3, -2.2, 2.8), 26, pz=s2 + 3, amount=1.2); ctx.sfx("boing", s2 + 2, 0.5)
    rest(g4, b, "ra")

    # ======================= 30-35: the birthday card, the truth =======================
    (a, s1), (_, b) = seg(30, "under")
    at(h_me, a, (-17.5, 3.0, 0), (-17.5, 7.4), ease=1); rest(h_me, a, "ll", "rl", "ll_knee", "rl_knee", "la", ease=1); react(h_me, "sad", a)
    sh(hs, a, s1, (-15.8, 5.6, 4.8), (-17.5, 3.0, 4.6), 26, dl=(-0.2, 0.1, 0)); ctx.sfx("tick", a, 0.6)
    sh(ins, s1, b, (0.3, -3.6, 1.4), (0, 0, 1.05), 28, dl=(0, 1.0, 0), cap="auto"); ctx.sfx("rustle", s1 + 2, 0.6)
    a, b = L(31); ctx.music(a, "paused")
    sh(ins, a, b, (8.0, -4.2, 1.3), (8, 0, 1.0), 34, dl=(0, 1.4, 0), cap="auto")
    (a, s1), (_, b) = seg(32, "every")
    react(h_me, "cry", a, L(34)[0])
    sh(hs, a, s1, (-16.4, 5.4, 4.8), (-17.5, 3.0, 4.7), 30, dl=(0.1, -0.3, 0)); ctx.sfx("sad", a + 4, 0.35)
    age(hs, s1, "g80"); at(hg["g80"], s1, (5.0, 3.2, 0), 0, ease=1); sit(hg["g80"], s1, 1.5, (5.0, 3.2), 0, ease=1); react(hg["g80"], "sad", s1, b + 6)
    sh(hs, s1, b, (5.0, -1.6, 4.0), (5.0, 3.2, 4.2), 30, dl=(0, 0.5, 0), look="flashback")
    (a, s1), (_, b) = seg(33, ("he", 2))
    age(hs, a, "g4"); at(g4, a, (-15.0, -2.6, 1.8), 0, ease=1); sit(g4, a, 1.85, (-15.0, -2.6), 0, ease=1); react(g4, "sad", a, b + 30)
    pencil = prim("box", (0.08, 0.08, 0.6), (0, 0, 0), mat((250, 200, 60), 0.4)); hold(g4, pencil, "ra", (0, -0.2, 0.1), (60, 0, 0)); show_between(pencil, a, L(38)[0])
    sheet = prim("box", (1.4, 1.0, 0.02), (-15.0, -3.6, 1.86), mat((255, 255, 255), 0.8)); show_between(sheet, a, L(38)[0])
    for k, f in enumerate(range(a, L(35)[1], 6)): pose(g4, f, 3, ra=(-60 if k % 2 else -50, 0, 10 if k % 2 else -10))
    sh(hs, a, s1, (-12.6, -6.6, 3.4), (-15.0, -2.6, 2.6), 26, dl=(0.2, 0.4, 0))
    sh(hs, s1, b, (-14.0, -5.0, 2.6), (-15.0, -3.0, 2.4), 32, dl=(0, 0.3, 0))
    # 34: "I went to his room. He was coloring. Inside the lines. Very carefully."
    (a, s1), (_, s2), (_, b) = seg(34, "he", "inside")
    at(h_me, a, (-11.5, -3.6, 0), (-15, -2.6), ease=1); react(h_me, "worried", a)
    shf(hs, a, s1, ((-11.5, -3.6), (-15, -2.6), 4.6), 3.0, 20); ctx.sfx("step", a + 3, 0.6)
    sh(hs, s1, s2, (-15.0, -6.0, 4.8), (-15.0, -3.0, 2.6), 28, dl=(0, 0.3, 0))
    shf(hs, s2, b, G4_COLOR, 2.0, 0, lens=30); ctx.sfx("rustle", s2 + 2, 0.4)
    # 35: "Grandpa, I don't need you young..."
    (a, s1), (_, b) = seg(35, ("i", 2))
    sit(h_me, a, 1.8, (-13.4, -3.0), (-15, -2.6), ease=1); react(h_me, "sad", a); kit.speak(h_me, 35, 1.0)
    shf(hs, a, s1, ME_SIT_BED, 2.8, 30)
    react(h_me, "smile", s1); react(g4, "worried", s1)
    sh(hs, s1, b, (-14.2, -6.8, 4.6), (-14.2, -2.8, 3.6), 24, dl=(0, 0.4, 0))

    # ======================= 36-41: "Like what?", Spit, laughing him old again =======================
    a, b = L(36); react(g4, "confused", a); kit.speak(g4, 36)
    shf(hs, a, b, G4_COLOR, 2.2, 0, pz=a + 2, amount=1.15)
    (a, s1), (_, s2), (_, b) = seg(37, ("how", 1), "that")
    react(h_me, "happy", a); kit.speak(h_me, 37, 0.6)
    shf(hs, a, s1, ME_SIT_BED, 2.6, 35); ctx.sfx("splash", a + 2, 0.4)
    shf(hs, s1, s2, ME_SIT_BED, 2.2, 15, pz=s1 + 2, amount=1.1)
    sh(ins, s2, b, (40.2, -2.6, 2.4), (40, 0, 0.0), 30, dl=(0, 0.8, -0.3), cap="auto"); ctx.sfx("slap", s2 + 3, 0.8); ctx.sfx("slap", s2 + 8, 0.6)
    (a, s1), (_, b) = seg(38, "then")
    react(g4, "blank", a); shf(hs, a, s1, G4_COLOR, 2.4, -15, lens=30); ctx.sfx("tick", a, 0.6)
    react(g4, "determined", s1)
    K._key(g4["root"], "location", s1, (-15.0, -2.6, 1.8 - 2.0 * 0.5 + 0.45 * 0.5), 1); K._key(g4["root"], "location", s1 + 6, (-14.0, -4.2, 1.6)); K._key(g4["root"], "location", s1 + 12, (-13.0, -5.0, 0))
    rest(g4, s1, "ll", "rl", "ll_knee", "rl_knee", "ra", ease=3); pose(g4, s1 + 2, 3, ra=(-160, 0, 0), la=(-160, 0, 0)); rest(g4, s1 + 14, "ra", "la", ease=4)
    sh(hs, s1, b, (-10.6, -8.6, 2.6), (-14.0, -4.0, 2.2), 22, dl=(0.4, 0.4, 0)); ctx.sfx("boing", s1 + 6, 0.6)
    a, b = L(39); at(g4, a, (-12.6, -5.4, 0), (-13.4, -3.0), ease=1); react(g4, "smug", a); kit.speak(g4, 39)
    deck = prim("box", (0.5, 0.7, 0.3), (0, 0, 0), mat((40, 80, 170), 0.5)); hold(g4, deck, "ra", (0, -0.3, 0.1)); show_between(deck, a, b)
    pose(g4, a, 3, ra=(-100, 0, 0))
    shf(hs, a, b, G4_FLOOR, 2.2, -30, pz=wf(39, "lose"), amount=1.3); ctx.sfx("ding", wf(39, "lose"), 0.5)
    rest(g4, b, "ra")
    # 40: "We played until midnight. I lost forty times. I laughed every single time."
    (a, s1), (_, s2), (_, b) = seg(40, "i", ("i", 1))
    for o in (cdesk, chair_me, chair_g): vis(o, a, True)
    sit(h_me, a, 1.58, (2, -6.0), 180, ease=1); at(g4, a, (2, -1.9, 1.58), 0, ease=1); rest(g4, a, "ll", "rl", "ll_knee", "rl_knee", ease=1)
    react(h_me, "happy", a); react(g4, "laugh", a)
    tcards = []
    for k in range(5):
        tc = K.plane_image(A + ("card_face.png" if k % 2 else "card_back.png"), (0.7, 1.0), (2 + random.uniform(-0.6, 0.6), -4 + random.uniform(-0.4, 0.4), 2.52 + k * 0.01), rot=(0, 0, random.uniform(-40, 40)))
        show_between(tc, a + k * 4, L(41)[1]); tcards.append(tc)
    for k, f in enumerate(range(a, b, 7)):
        pose(h_me, f, 2, ra=(-90 if k % 2 else -60, 0, 0)); pose(g4, f + 3, 2, ra=(-100 if k % 2 else -70, 0, 0)); ctx.sfx("slap", f + 2, 0.5)
    sh(hs, a, s1, (6.0, -4.0, 5.4), (2, -4, 2.6), 22, dl=(-0.4, 0.4, 0))
    react(h_me, "annoyed", s1); sh(hs, s1, s2, (1.4, -2.4, 4.6), (2, -6.0, 4.6), 30, pz=s1 + 2, amount=1.1); ctx.sfx("sad", s1 + 2, 0.3)
    react(h_me, "laugh", s2); ctx.sfx("giggle", s2 + 2, 0.4)
    sh(hs, s2, b, (2.6, -2.2, 4.4), (2, -6.0, 4.6), 26, dl=(0, -0.3, 0))
    # 41: every laugh, ten, twenty, fifty, eighty
    (a, s1), (_, s2), (_, s3), (_, b) = seg(41, "ten", "twenty", "fifty")
    react(h_me, "laugh", a)
    sh(hs, a, s1, (1.6, -3.0, 4.6), (2, -6.0, 4.6), 28, dl=(0, -0.3, 0)); ctx.sfx("giggle", a + 2, 0.4)
    for f, k, z in ((s1, "g10", 1.58), (s2, "g20", 1.58), (s3, "g70", 1.58), (s3 + (b - s3) // 2, "g80b", 1.58)):
        age(hs, f, k); sit(hg[k], f, z, (2, -1.7), 0, ease=1); react(hg[k], "laugh", f); poof(f, 0.6)
    sh(hs, s1, s2, (5.6, -3.8, 4.4), (2, -1.7, 3.9), 24, pz=s1 + 2, amount=1.15)
    sh(hs, s2, s3, (-1.6, -3.6, 4.6), (2, -1.7, 4.3), 24, pz=s2 + 2, amount=1.15)
    sh(hs, s3, b, (5.0, -4.4, 4.8), (2, -1.7, 4.4), 22, dl=(-0.4, 0.4, 0))
    ctx.music(b - 6, "normal")

    # ======================= 42-45: back to eighty, fishing, rocks, best summer =======================
    (a, s1), (_, s2), (_, b) = seg(42, ("his", 1), ("his", 2))
    g80 = hg["g80b"]; at(g80, a, (2, -1.7, 0), 0, ease=1); rest(g80, a, "ll", "rl", "ll_knee", "rl_knee", ease=1)
    for o in (cdesk, chair_me, chair_g): vis(o, a, False)
    at(g80, a, (3.0, 1.0, 0), 0, ease=1); pose(g80, a, 1, waist=(14, 0, 0)); react(g80, "happy", a)
    sh(hs, a, s1, (3.6, -2.4, 4.0), (3.0, 1.0, 4.0), 26, pz=a + 2, amount=1.15); ctx.sfx("crack", a + 2, 0.9)
    sh(hs, s1, s2, (0.4, 4.6, 5.8), (0, 8.4, 6.0), 30, dl=(0, 0.5, 0)); ctx.sfx("tick", s1, 1.0)
    sh(hs, s2, b, (1.6, -1.6, 1.4), (1.6, 0.6, 1.1), 26, dl=(0, 0.4, 0)); ctx.sfx("tweet", s2 + 3, 0.3)
    # 43: fishing, the boot
    (a, s1), (_, s2), (_, b) = seg(43, "i", "we")
    age(yd, a, "g80"); yg80 = yg["g80"]
    sit(yg80, a, 0.62, (-1.0, 51.0), 180, ease=1); sit(y_me, a, 0.62, (1.0, 51.0), 180, ease=1)
    hold(yg80, rodg, "ra", (0, -0.1, 0), (-30, 0, 0)); hold(y_me, rodm, "ra", (0, -0.1, 0), (-30, 0, 0))
    pose(yg80, a, 1, ra=(-70, 0, 0)); pose(y_me, a, 1, ra=(-70, 0, 0)); react(yg80, "smile", a); react(y_me, "happy", a)
    sh(yd, a, s1, (4.5, 55.5, 3.4), (0, 51, 2.8), 22, dl=(-0.6, -0.4, 0)); ctx.sfx("splash", a + 4, 0.5)
    K._key(bt, "location", s1, (1.5, 55, -1.0), 1); K._key(bt, "location", s1 + 10, (1.5, 53.5, 3.5))
    pose(y_me, s1, 3, ra=(-150, 0, 0)); pose(yg80, s1 + 4, 3, ra=(-150, 0, 0)); react(y_me, "starstruck", s1); react(yg80, "starstruck", s1 + 4)
    sh(yd, s1, s2, (8.0, 52.0, 3.4), (0.5, 52.6, 2.9), 22, pz=s1 + 10, amount=1.2); ctx.sfx("splash", s1 + 2, 0.7); ctx.sfx("boing", s1 + 10, 0.5)
    react(y_me, "angry", s2, b + 6); react(yg80, "angry", s2 + 4, b + 6); turn(y_me, s2, (-1, 51), 4); turn(yg80, s2, (1, 51), 4)
    pose(y_me, s2, 4, ra=(-60, 0, 0)); pose(yg80, s2, 4, ra=(-60, 0, 0)); K._key(bt, "location", s2, (1.5, 53.5, 3.5), 1); K._key(bt, "location", s2 + 6, (3.5, 52.0, 0.8))
    kit.speak(y_me, 43, 1.0, s2, b); kit.speak(yg80, 43, 1.0, s2 + 6, b)
    sh(yd, s2, b, (0.0, 55.5, 4.0), (0, 51, 3.7), 24, dl=(0, -0.4, 0))
    # 44: rock collection
    (a, s1), (_, b) = seg(44, "i")
    age(hs, a, "g80b"); at(g80, a, (9.0, 6.2, 0), (-1, 4), ease=1); pose(g80, a, 1, waist=(14, 0, 0), ra=(-80, 0, -10)); react(g80, "happy", a)
    at(h_me, a, (6.8, 4.2, 0), (10.5, 8.5), ease=1); rest(h_me, a, "ll", "rl", "ll_knee", "rl_knee", "la", "ra", ease=1); react(h_me, "smile", a)
    shf(hs, a, s1, G80B_SHELF, 2.8, -20); ctx.sfx("pop", a + 2, 0.4)
    rk2 = prim("ball", (0.45, 0.4, 0.3), (0, 0, 0), mat((140, 140, 140), 0.8)); hold(h_me, rk2, "ra", (0, -0.3, 0.1)); show_between(rk2, s1, b)
    pose(h_me, s1, 3, ra=(-90, 0, 0)); react(h_me, "love", s1)
    shf(hs, s1, b, ME_SHELF, 2.6, 25); ctx.sfx("sparkle", s1 + 2, 0.5)
    # 45: "Best summer of my life. I didn't say I was bored once."
    a, b = L(45); react(y_me, "relieved", a); react(yg80, "smile", a)
    sit(y_me, a, 0.62, (1.0, 51.0), 180, ease=1); sit(yg80, a, 0.62, (-1.0, 51.0), 180, ease=1)
    sh(yd, a, b, (0, 38.0, 6.0), (0, 52, 2.6), 22, dl=(0, 2.5, -0.6))

    # ======================= 46-50: back to math class =======================
    a, b = L(46); poof(a); react(c_me, "blank", a); sit(c_g10, a, 1.6, (-2.2, -1.0), 180, ease=1); react(c_g10, "smile", a)
    sh(cl, a, b, (0.0, 6.4, 6.4), (0, -3.0, 3.0), 22, dl=(0, -1.0, 0))
    (a, s1), (_, b) = seg(47, "i")
    react(c_me, "sleepy", a); sh(cl, a, s1, (1.4, 1.6, 4.6), (2.2, -1.0, 4.6), 30, dl=(0, 0.4, 0)); ctx.sfx("crickets", a + 2, 0.5)
    react(c_me, "nervous", s1)
    for k in range(5): ctx.sfx("pop", s1 + 3 + k * 4, 0.35)
    shf(cl, s1, b, ME_C, 2.2, 0, lens=30, pz=s1 + 4, amount=1.25)
    (a, s1), (_, b) = seg(48, "he's")
    react(c_g10, "happy", a); pose(c_g10, a + 4, 4, ra=(-175, 0, 0)); react(c_me, "annoyed", s1)
    shf(cl, a, s1, G10_C, 3.0, -25); ctx.sfx("ding", a + 6, 0.4)
    sh(cl, s1, b, (0.0, 3.4, 6.0), (0.0, -1.0, 3.8), 22, dl=(0, -0.4, 0))
    a, b = L(49); react(teacher, "annoyed", a); kit.speak(teacher, 49); pose(teacher, a, 4, ra=(-95, 0, 20))
    sh(cl, a, b, (3.0, 0.8, 4.8), (4.0, 3.5, 4.7), 28, pz=a + 3, amount=1.15)
    a, b = L(50); react(c_g10, "smug", a); kit.speak(c_g10, 50)
    sh(cl, a, b, (-1.4, 1.6, 3.6), (-2.2, -1.0, 3.4), 26, pz=wf(50, "there"), amount=1.3); ctx.sfx("boing", wf(50, "there"), 0.5)
    rest(c_g10, b, "ra")

    # ======================= every held beat has a sound in it (a silent gap sounds like an audio bug) =======================
    beat_sfx = {"2": "boing", "6": "crickets", "7": "sparkle", "9": "ding", "14": "boing", "16": "scared", "18": "crickets",
                "22": "pop", "25": "crickets", "28": "boing", "31": "sad", "39": "ding", "41": "sparkle", "47": "crickets", "50": "boing"}
    for k, nm in beat_sfx.items():
        i = int(k)
        if str(i) in ctx.story.get("beats", {}): ctx.sfx(nm, S.frame(timed[i]["end"]) + 2, 0.6)

    # ======================= head motion for narration on whoever is "me" on screen =======================
    for i, (who, _) in enumerate(ctx.story["lines"]):
        if who != "narrator" or i in (6, 16, 20, 29, 35, 37, 43): continue
        a, b = L(i)
        av = c_me if i in (0, 46, 47, 48) else (y_me if i in (45,) else h_me)
        kit.speak(av, i, 0.5)

    # ======================= one Grandpa per set at a time =======================
    sets = {"house": hg, "yard": yg, "class": {"c_g10": c_g10}}
    for sn, avs in sets.items():
        sc = sorted(sched.get(sn, [(0, "none")]))
        if sc[0][0] > 0: sc = [(0, "none")] + sc
        for name, av in avs.items():  # hide by shrinking to nothing (vis() would also switch every face on)
            r = av["root"]; base = av.get("scale", 1.0)
            for f, k in sc:
                v = base if k == name else 0.0001; r.scale = (v, v, v); r.keyframe_insert("scale", frame=f)
            for fc in r.animation_data.action.fcurves:
                if fc.data_path == "scale":
                    for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'
            r.scale = (base,) * 3
    hs.__exit__(None, None, None)
