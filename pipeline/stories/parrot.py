""""My Grandpa Left Me $1,000,000 If I Could Keep His Parrot Quiet" - built to match the user's reference channel:
~1 s shots, a wide low camera that is always moving (handheld float), full-screen object inserts (clock, stopwatch,
will, freezer, phone, check), time of day changing the light, a white glow into the flashback, a sound effect on every
beat and an expression change on every line. Line numbers follow stories/parrot.json (0-54).
Sets: funeral (lawn), house (Grandpa's living room + kitchen), porch (flashback, sunset), redclock (23:59 insert).
Characters face -Y at rest; yaw 180 faces +Y. Frames are frames of the final video."""
import math, random
import bpy
from mathutils import Vector
import shortkit as K
from shortkit import Set, prim, mat, empty, vis, show_between, camera, punch, shake, pose, rest, at, turn, walk, sit, idle, lin
import blocky, toys
from avatar import react, talk
from anim import value

random.seed(7)
GRANDPA = {"shirt": (150, 100, 70), "pants": (95, 95, 105), "skin": (234, 190, 150), "hair": (220, 220, 225), "shoes": (70, 45, 30)}
LAWYER = {"shirt": (45, 50, 65), "pants": (45, 50, 65), "skin": (204, 142, 105), "hair": (30, 25, 20), "shoes": (20, 20, 22)}
DEREK = {"shirt": (245, 125, 40), "pants": (60, 70, 160), "skin": (234, 184, 146), "hair": (230, 200, 120), "hat": "cap", "hat_color": (25, 25, 30), "shoes": (250, 250, 250)}
NEIGHBOR = {"shirt": (110, 200, 120), "pants": (70, 70, 90), "skin": (160, 110, 80), "hair": (20, 20, 20)}
MOURNERS = [{"shirt": c, "pants": (35, 35, 42), "skin": s, "hair": h} for c, s, h in (
    ((40, 40, 48), (234, 190, 150), (60, 40, 30)), ((30, 30, 36), (160, 110, 80), (20, 20, 20)), ((55, 50, 60), (250, 215, 180), (230, 200, 120)),
    ((35, 38, 50), (204, 142, 105), (40, 30, 20)), ((50, 45, 45), (234, 190, 150), (150, 150, 155)), ((28, 30, 34), (180, 120, 90), None))]


# ---------------- helpers ----------------
def rel(p, d): return tuple(a + b for a, b in zip(p, d))


def wall_mat(c, rough=0.8):
    """Walls and ceiling don't cast shadows, so the sun lights the room like Roblox's bright interiors."""
    m = bpy.data.materials.new("wall"); m.use_nodes = True; pb = m.node_tree.nodes["Principled BSDF"]
    pb.inputs["Base Color"].default_value = lin(c); pb.inputs["Roughness"].default_value = rough
    m.shadow_method = 'NONE'; return m


def npc(ctx, name, look, loc, yaw=0):
    a = blocky.build(ctx.D, name, look); at(a, 0, loc, yaw, ease=1); idle(a, ("head",), 0.03, 50); return a


def glasses(av, c=(25, 25, 30), dark=False):
    hc = Vector((0, -0.66, 0.7)); m = mat(c, 0.3)
    lens = mat((15, 15, 18), 0.1) if dark else mat((215, 235, 255), 0.05, alpha=0.25)
    for sx in (-0.27, 0.27):
        prim("cyl", (0.04, 0.42, 0.34), hc + Vector((sx, 0, 0)), lens, rot=(0, 0, 90), parent=av["head"])
        if not dark:
            for dz in (-0.17, 0.17): prim("box", (0.42, 0.05, 0.05), hc + Vector((sx, 0, dz)), m, parent=av["head"])
            for dx in (-0.21, 0.21): prim("box", (0.05, 0.05, 0.38), hc + Vector((sx + dx, 0, 0)), m, parent=av["head"])
    prim("box", (0.2, 0.05, 0.05), hc + Vector((0, 0, 0.05)), m, parent=av["head"])
    for sx in (-0.48, 0.48): prim("box", (0.05, 0.6, 0.05), hc + Vector((sx, 0.3, 0.05)), m, parent=av["head"])


def tie(av, c=(200, 40, 50)):
    prim("box", (0.32, 0.06, 1.3), (0, -0.53, 1.25), mat(c, 0.5), parent=av["waist"])
    prim("box", (0.9, 0.05, 0.5), (0, -0.52, 1.85), mat((245, 245, 245), 0.6), parent=av["waist"])


def hold(av, obj, hand="ra", loc=(0, -0.15, 0), rot=(0, 0, 0)):
    obj.parent = av["grips"][hand]; obj.location = loc; obj.rotation_euler = [math.radians(a) for a in rot]; return obj


TIMED = []; SHORT = []  # filled by build(): word timings for talk_nod


def talk_nod(av, f0, f1, every=None, amt=None, amount=1.0):
    """Head motion while someone talks between f0 and f1: a nod on every spoken word (avatar.talk)."""
    S = SHORT[0]; fr = [S.frame(w[1]) for l in TIMED for w in l.get("words", []) if f0 <= S.frame(w[1]) < f1]
    talk(av, fr or list(range(f0, f1, 7)), amount)


def build(ctx):
    S, L, A = ctx.short, ctx.L, ctx.A
    timed = ctx.timed; TIMED[:] = timed; SHORT[:] = [S]

    def norm(w): return w.strip('.,?!"').lower()

    def seg(i, *marks):
        """Split line i into shots: cut just before each mark (a word, matched in order) or at a fraction."""
        a, b = L(i); ws = timed[i]["words"]; out = [a]; k = 0
        for m in marks:
            if isinstance(m, float): f = int(a + (b - a) * m)
            else:
                if isinstance(m, tuple):
                    m, nth = m; k = [j for j, w in enumerate(ws) if norm(w[0]) == m][nth]
                while k < len(ws) and norm(ws[k][0]) != m: k += 1
                if k == len(ws): raise ValueError(f"line {i}: no word '{m}'")
                f = S.frame(ws[k][1]) - 1; k += 1
            out.append(max(f, out[-1] + 6))
        out.append(max(b, out[-1] + 6))
        return list(zip(out, out[1:]))

    def wf(i, word, nth=0):
        hits = [w for w in timed[i]["words"] if norm(w[0]) == word]
        return S.frame(hits[min(nth, len(hits) - 1)][1]) if hits else L(i)[0]

    def sh(st, f0, f1, loc, tgt, lens=24, dl=None, dt=None, cap="auto", pz=None, amount=1.25, look=None):
        """One shot: camera at loc aimed at tgt, easing by dl/dt over the shot (else a slow push-in)."""
        name = f"{st.name}_{f0}_{len(st.cams)}"
        if dl or dt: c = camera(st, name, loc, tgt, lens, f0, f1, rel(loc, dl or (0, 0, 0)), rel(tgt, dt or (0, 0, 0)))
        else: c = camera(st, name, loc, tgt, lens)
        S.shot(st, name, f0, f1, caption=cap, look=look)
        if pz: punch(c, pz, amount)
        return c

    # ======================= sets =======================
    # ---- funeral: lawn, white chairs, coffin, Grandpa's portrait
    fun = Set("funeral", sky=(140, 175, 225), horizon=(225, 230, 240), sun=(52, 0, 35), sun_energy=3.6, sun_color=(255, 245, 235))
    with fun:
        prim("box", (300, 300, 0.2), (0, 0, -0.1), mat((105, 180, 90), 0.9))
        prim("box", (3, 40, 0.06), (0, -10, 0.02), mat((200, 190, 170), 0.9))  # aisle
        for x in range(-40, 41, 10): toys.tree(x + random.uniform(-2, 2), 22 + random.uniform(-2, 3), 1.2)
        for x in (-16, -12, 12, 16): toys.flower_bush(x, 9, 1.0)
        for k in range(-30, 31, 3): prim("box", (0.3, 0.3, 2.2), (k, 16, 1.1), mat((250, 250, 250), 0.5))
        prim("box", (61, 0.2, 0.3), (0, 16, 1.9), mat((250, 250, 250), 0.5))
        toys.clouds(10, (-80, 50, 30), (80, 120, 50), 3, 7)
        cof = toys.coffin(0, 6); toys.easel(6, 7.2, A + "portrait.png", rot=-12); toys.podium(-6.5, 4.6)
        for x in (-3.4, 3.4): toys.flower_bush(x * 1.0, 8.0, 0.6)
        f_me = blocky.build(ctx.D, "me_f"); idle(f_me); at(f_me, 0, (-6.5, 5.7, 0), 0, ease=1)
        paper = toys.card(A + "will.png", 0.5, 0.65); hold(f_me, paper, "la", (0, -0.25, 0.1), (80, 0, 0)); pose(f_me, 0, None, la=(-60, 0, 10))
        rows = {}
        for r, y in enumerate((-2.5, -5.5, -8.5, -11.5)):
            for x in (-10.5, -7, -3.5, 3.5, 7, 10.5):
                toys.chair(x, y, 180)
                rows[(r, x)] = (x, y)
        f_law = npc(ctx, "lawyer_f", LAWYER, (0, 0, 0)); glasses(f_law); tie(f_law); sit(f_law, 0, 1.58, (3.5, -2.5 + 0.1), 180, ease=1)
        f_der = npc(ctx, "derek_f", DEREK, (0, 0, 0)); glasses(f_der, dark=True); sit(f_der, 0, 1.58, (-3.5, -2.4), 180, ease=1)
        mourners = []
        for k, ((r, x), (px, py)) in enumerate(sorted(rows.items())):
            if (r, x) in ((0, 3.5), (0, -3.5)): continue
            m = npc(ctx, f"mourner{k}", MOURNERS[k % len(MOURNERS)], (0, 0, 0)); sit(m, 0, 1.58, (px, py + 0.1), 180, ease=1); mourners.append(m)
        f_cap = toys.parrot("captain_f", 0.95)
    # ---- house: living room (cage), lawyer's armchair, kitchen (fridge), window, front door
    hs = Set("house", sky=(120, 185, 255), horizon=(215, 232, 255), sun=(50, 0, -38), sun_energy=4.2, sun_color=(255, 244, 228))
    with hs:
        prim("box", (300, 300, 0.2), (0, 0, -0.15), mat((105, 180, 90), 0.9))  # lawn outside
        prim("box", (36, 19, 0.2), (-4, -0.5, -0.05), mat((190, 140, 95), 0.45))  # wood floor
        for x in range(-22, 14, 2): prim("box", (0.06, 19, 0.01), (x, -0.5, 0.06), mat((165, 115, 75), 0.5))
        wm, trim = wall_mat((245, 232, 205)), wall_mat((255, 255, 255))
        # back wall (y=9) with an open window x 3.5..8.5, z 2..6 (the neighbour films through it)
        prim("box", (25.5, 0.4, 11), (-9.25, 9, 5.5), wm); prim("box", (5.5, 0.4, 11), (11.25, 9, 5.5), wm)
        prim("box", (5, 0.4, 2), (6, 9, 1), wm); prim("box", (5, 0.4, 5), (6, 9, 8.5), wm)
        for dx in (3.5, 8.5): prim("box", (0.25, 0.6, 4.2), (dx, 9, 4), trim)
        for dz in (2, 6): prim("box", (5.3, 0.6, 0.25), (6, 9, dz), trim)
        prim("box", (0.4, 19, 11), (-22, -0.5, 5.5), wm)                   # left wall
        # right wall (x=14) with the front door opening y 1.5..4.5
        prim("box", (0.4, 11, 11), (14, -4.5, 5.5), wm); prim("box", (0.4, 4.5, 11), (14, 6.75, 5.5), wm); prim("box", (0.4, 3, 4.5), (14, 3, 8.75), wm)
        door = empty("door_hinge", (14, 4.5, 0))
        prim("box", (0.25, 3.0, 6.4), (0, -1.5, 3.2), mat((150, 90, 55), 0.5), parent=door, bevel=0.05)
        prim("ball", (0.25, 0.25, 0.25), (-0.2, -2.6, 3.0), mat((230, 190, 80), 0.3, 0.8), parent=door)
        prim("box", (36.5, 19.5, 0.3), (-4, -0.5, 11.1), wall_mat((250, 250, 248)))  # ceiling
        prim("box", (36, 0.3, 0.5), (-4, 8.75, 0.25), trim)
        prim("box", (10, 9, 0.05), (0, 2.5, 0.08), mat((170, 60, 70), 0.9))  # rug
        cage = toys.cage(0, 3)
        cap = toys.parrot("captain", 0.9); cap["root"].location = (0, 3, 4.2)
        perch = empty("perch_stand", (0, 1.2, 0))  # T-perch on the table for the final staring contest (L33+)
        prim("cylY", (0.15, 0.15, 1.6), (0, 0, 2.35), mat((150, 100, 60), 0.6), parent=perch)
        prim("cyl", (1.6, 0.14, 0.14), (0, 0, 3.15), mat((150, 100, 60), 0.6), parent=perch)
        prim("cylY", (0.9, 0.9, 0.1), (0, 0, 1.6), mat((150, 100, 60), 0.6), parent=perch)
        tbl = toys.table(0, 1.2, 3.0, 1.8, 1.5)
        show_between(perch, 0, 0); show_between(tbl, 0, 0)
        toys.couch(-11, -2.5, 180); toys.table(-11, 1.0, 4, 2, 1.0)
        tvr, tv_on = toys.tv(-11, 7.6)
        rt = toys.router(); rt.location = (-13.2, 7.6, 4.3)
        toys.card(A + "wifi.png", 1.0, 0.45).location = (-13.2, 7.25, 3.65)
        toys.armchair(8, 0.5, -90)
        lamp1, l1 = toys.lamp(10.5, 4.5); lamp2, l2 = toys.lamp(-15.5, 5.0)
        clk = toys.wall_clock(A + "dial_blue.png", 3.0); clk["root"].location = (-4, 8.75, 7.4)
        pf = toys.card(A + "portrait.png", 2.2, 2.75); pf.location = (-8.5, 8.75, 6.6)
        # kitchen
        prim("box", (8, 2.6, 3.0), (-17, 7.4, 1.5), mat((250, 250, 250), 0.4), bevel=0.05)
        prim("box", (8.2, 2.8, 0.25), (-17, 7.4, 3.1), mat((70, 70, 80), 0.3))
        frg, fz = toys.fridge(-20.2, 7.2)
        nug = toys.nugget(); nug.location = (-20.2, 7.0, 4.95); nug.scale = (0.9, 0.9, 0.9)
        note = toys.card(A + "note.png", 1.0, 0.75); note.location = (-20.4, 7.6, 5.35); note.rotation_euler = (math.radians(-10), 0, 0)
        prim("box", (1.4, 1.4, 2.0), (-14, 5.8, 1.0), mat((90, 90, 100), 0.5), bevel=0.1)  # bin
        # cast
        me = blocky.build(ctx.D); idle(me)
        law = npc(ctx, "lawyer", LAWYER, (8, 0.6, 0), -90); glasses(law); tie(law)
        sw, swbtn = toys.stopwatch(A + "stopwatch.png"); sw.scale = (0.55, 0.55, 0.55); hold(law, sw, "ra", (0, -0.35, 0), (0, 0, 0))
        clip = toys.card(A + "will.png", 0.9, 1.15); hold(law, clip, "la", (0, -0.35, 0.2), (75, 0, 0))
        der = npc(ctx, "derek", DEREK, (19, 3, 0), -90); glasses(der, dark=True)
        nb = npc(ctx, "neighbor", NEIGHBOR, (6, 10.6, 0), 0)
        nph = toys.phone(); hold(nb, nph, "ra", (0, -0.2, 0.1), (80, 0, 0)); pose(nb, 0, None, ra=(-95, 0, 15))
        toys.house(6, 34, 180); toys.house(-14, 34, 180); toys.house(26, 34, 180); toys.tree(14, 22, 1.1); toys.tree(-4, 24, 1.0)
        out_l = bpy.data.objects.new("porch_light", bpy.data.lights.new("porch_light", "POINT")); hs.link(out_l)
        out_l.location = (17, 3, 7); out_l.data.energy = 0; out_l.data.color = (1, 0.85, 0.6)
    # ---- porch flashback (sunset, faded warm)
    pc = Set("porch", sky=(255, 160, 120), horizon=(255, 215, 170), sun=(62, 0, -55), sun_energy=2.6, sun_color=(255, 205, 160))
    pc.scene.view_settings.exposure = -0.45
    with pc:
        prim("box", (300, 300, 0.2), (0, 0, -0.1), mat((110, 175, 90), 0.9))
        toys.house(0, 7.5, 0, w=18, d=9, h=9, color=(250, 235, 200), roof=(150, 70, 60))
        prim("box", (18, 5, 0.8), (0, 1.0, 0.4), mat((205, 160, 115), 0.6))   # porch deck
        for x in (-8.5, 8.5): prim("box", (0.4, 0.4, 7), (x, -1.2, 3.5), mat((255, 255, 255), 0.5))
        prim("box", (18, 5.5, 0.4), (0, 1.0, 7.1), mat((240, 240, 235), 0.6))
        for k in range(3): prim("box", (4, 1.0, 0.3), (0, -2.0 - k, 0.15 + 0.25 * (2 - k)), mat((190, 145, 100), 0.6))
        swing = empty("swing", (-3.5, 1.8, 0))
        prim("box", (5, 1.6, 0.3), (0, 0, 2.2), mat((150, 100, 60), 0.6), parent=swing); prim("box", (5, 0.3, 1.6), (0, 0.7, 3.1), mat((150, 100, 60), 0.6), parent=swing)
        for sx in (-2.4, 2.4): prim("box", (0.08, 0.08, 4.9), (sx, 0.1, 4.6), mat((90, 90, 95), 0.4), parent=swing)
        rt2 = toys.router(); rt2.location = (5.0, 2.7, 3.2); prim("box", (3, 0.2, 2.5), (5.0, 3.1, 3.6), mat((120, 150, 190), 0.3, emit=0.15))
        for x in range(-30, 31, 12): toys.tree(x, 24, 1.1)
        toys.clouds(8, (-60, 40, 25), (60, 100, 45), 3, 6)
        gp = npc(ctx, "grandpa", GRANDPA, (0, 0, 0)); glasses(gp); sit(gp, 0, 2.35, (-2.3, 1.7), 0, ease=1)
        kid = blocky.build(ctx.D, "me_young"); kid["root"].scale = (0.72, 0.72, 0.72); kid["scale"] = 0.72; idle(kid)
        sit(kid, 0, 2.35, (-4.7, 1.7), 0, ease=1)
        yder = npc(ctx, "derek_young", {**DEREK, "scale": 0.72}, (0, 0, 0)); sit(yder, 0, 0.8 + 0.1, (4.6, -0.5), 20, ease=1)
        yph = toys.phone(); hold(yder, yph, "ra", (0, -0.2, 0.1), (70, 0, 0)); pose(yder, 0, None, ra=(-80, 0, 10), head=(-12, 0, 0))
        p_cap = toys.parrot("captain_p", 0.55); p_cap["root"].parent = gp["waist"]; p_cap["root"].location = (0.6, 0.05, 2.0)
    # ---- 23:59 red clock insert
    rc = Set("redclock", sky=(60, 20, 30), horizon=(120, 30, 40), sun=(10, 0, 0), sun_energy=2.0, sun_color=(255, 160, 150))
    with rc:
        prim("box", (40, 0.4, 30), (0, 1.0, 0), wall_mat((90, 30, 40)))
        rclk = toys.wall_clock(A + "dial_red.png", 5.0, (205, 40, 45)); rclk["root"].location = (0, 0.6, 0)
        rl = bpy.data.objects.new("red_glow", bpy.data.lights.new("red_glow", "AREA")); rc.link(rl)
        rl.data.energy = 900; rl.data.color = (1, 0.35, 0.3); rl.data.size = 8; rl.location = (0, -8, 3); rl.rotation_euler = (math.radians(90), 0, 0)
        toys.set_time(rclk, 0, 8, 58); toys.set_time(rclk, L(34)[0] + 4, 8, 59, ease=2)

    # ---- inserts: full-screen object close-ups on a desk (the reference cuts to objects as their own shots)
    ins = Set("inserts", sky=(235, 225, 210), horizon=(245, 240, 230), sun=(40, 0, -30), sun_energy=3.6)
    with ins:
        prim("box", (60, 30, 1), (0, 6, -0.5), mat((150, 100, 62), 0.45))
        prim("box", (60, 0.4, 20), (0, 9, 6), wall_mat((235, 215, 185)))
        will = toys.card(A + "will.png", 1.6, 2.08); will.rotation_euler = (math.radians(-90), 0, math.radians(8)); will.location = (0, 0, 0.03)
        ipen = empty("ipen", (0.7, -0.2, 0.25)); prim("cylY", (0.1, 0.1, 1.6), (0, 0, 0), mat((30, 30, 40), 0.3), parent=ipen)
        prim("cone", (0.1, 0.1, 0.2), (0, 0, -0.9), mat((220, 190, 60), 0.3, 0.7), rot=(180, 0, 0), parent=ipen); ipen.rotation_euler = (math.radians(-35), 0, math.radians(20))
        isw, isw_btn = toys.stopwatch(A + "stopwatch.png"); isw.location = (10, 0, 0.75); isw.rotation_euler = (0, 0, math.radians(-10))
        iph = toys.card(A + "phone_whale.png", 1.0, 1.8); iph.location = (20, 0, 1.0); iph.rotation_euler = (math.radians(-12), 0, 0)
        prim("box", (1.1, 0.08, 1.95), (20, 0.06, 1.0), mat((20, 20, 25), 0.2), rot=(-12, 0, 0), bevel=0.06)
        igold = toys.box_prop(A + "cracker_gold.png", 1.2, 0.5, 1.6, (250, 200, 40)); igold.location = (30, 0, 0); igold.rotation_euler = (0, 0, math.radians(-12))

    hs.__enter__()  # props made from here on belong to the house set (other sets only get cameras below)

    # ======================= time of day in the house =======================
    def daylight(f, energy, color, world, window_night):
        sun = hs.sun.data; sun.energy = energy; sun.keyframe_insert("energy", frame=f)
        sun.color = lin(color)[:3]; sun.keyframe_insert("color", frame=f)
        bg = hs.scene.world.node_tree.nodes["Background"].inputs["Strength"]; bg.default_value = world; bg.keyframe_insert("default_value", frame=f)
        for l in (l1, l2): l.energy = 900 if window_night else 0; l.keyframe_insert("energy", frame=f)
        out_l.data.energy = 600 if window_night else 0; out_l.data.keyframe_insert("energy", frame=f)
    daylight(0, 4.2, (255, 244, 228), 1.25, False)
    daylight(L(24)[0], 0.9, (140, 160, 255), 0.12, True)       # hour twelve: night
    daylight(L(34)[0], 3.4, (255, 205, 170), 0.9, False)       # 23:59: morning
    toys.set_time(clk, 0, 9, 0)
    for i, (h, m) in ((10, (10, 0)), (22, (15, 0)), (24, (21, 0)), (29, (27, 0)), (34, (32, 59)), (41, (32, 59))):
        toys.set_time(clk, L(i)[0] - 1, h, m); toys.set_time(clk, L(i)[1], h, m)  # held through the insert; hours count past 24 so hands turn forwards
    toys.set_time(clk, wf(41, "clock") + 4, 32, 60, ease=2)

    # ======================= cast defaults in the house =======================
    sit(law, 0, 1.5, (8.1, 0.6), -90, ease=1); pose(law, 0, None, ra=(-55, 0, -10), la=(-50, 0, 10))
    at(me, 0, (0.2, -1.6, 0), 180, ease=1)
    beak = lambda f0, f1, every=5: toys.beak(cap, f0, f1, every)

    def click(btn, f):
        btn.keyframe_insert("location", frame=f - 1); btn.location.z -= 0.12; btn.keyframe_insert("location", frame=f)
        btn.location.z += 0.12; btn.keyframe_insert("location", frame=f + 3)

    def stopwatch_gag(i, f1=None):
        """'Starting over.' - a full-screen stopwatch click (insert), then the lawyer's blank face."""
        a, b = L(i); b = f1 or b; f = a + 4; m = a + max(8, (b - a) * 3 // 5)
        click(isw_btn, f); ctx.sfx("click", f, 1.2); react(law, "blank", a); pose(law, a, 4, ra=(-95, 0, -25)); pose(law, b, 6, ra=(-55, 0, -10))
        sh(ins, a, m, (10.3, -3.4, 1.2), (10, 0, 0.8), 30, dl=(0, 0.9, 0), pz=f, amount=1.3, cap="top")
        sh(hs, m, b, (4.0, -2.2, 4.5), (8.1, 0.6, 4.3), 26, dl=(0.3, 0.2, 0))

    # ======================= 0-2: the funeral (cold open) =======================
    fp = (0, 6, 3.35)  # top of the coffin lid
    (a, s1), (_, s2), (_, s3), (_, s4), (_, b) = seg(0, "funeral", "parrot", "coffin", "password")
    react(f_me, "sad", a); talk_nod(f_me, a, s2)
    sh(fun, a, s1, (0, -16, 4.2), (-3, 5, 4.4), 22, dl=(0, 3.5, 0.2))                       # slow push down the aisle
    sh(fun, s1, s2, (-4.5, 1.2, 3.6), (-6.5, 5.7, 4.7), 26, dl=(0.4, 0.5, 0))              # me at the podium, sad
    # the parrot swoops in over the crowd and lands on the coffin
    K._key(f_cap["root"], "location", s2 - 2, (24, -18, 16), 1); K._key(f_cap["root"], "location", s3 + 10, rel(fp, (0, 0, 0)))
    f_cap["root"].rotation_euler = (0, 0, math.radians(120)); f_cap["root"].keyframe_insert("rotation_euler", frame=s2 - 2)
    f_cap["root"].rotation_euler = (0, 0, math.radians(0)); f_cap["root"].keyframe_insert("rotation_euler", frame=s3 + 10)
    toys.flap({"wings": f_cap["wings"]}, s2 - 2, s3 + 10, 6, 70); ctx.sfx("flap", s2); ctx.sfx("whoosh", s2 + 2, 0.7)
    fc = K.follow(fun, f"fun_follow_{s2}", f_cap["root"], (-3.5, -6.0, -1.2), (0, 0, 0.8), 24); S.shot(fun, fc.name, s2, s3)                           # low, the bird overhead
    sh(fun, s3, s4, (1.6, 1.8, 3.0), rel(fp, (0, 0, 0.9)), 24, dl=(-0.5, 0.6, 0)); ctx.sfx("squawk", s3 + 10, 0.7)
    toys.tilt(f_cap, s3 + 14, 18)
    react(f_me, "big_eyes", s4); sh(fun, s4, s5 := s4 + max(8, (b - s4) // 2), (-6.0, 3.1, 4.9), (-6.5, 5.7, 4.75), 28, pz=s4 + 2)
    for m in mourners + [f_law, f_der]: react(m, "shock", s5 + random.randint(0, 4)); pose(m, s5, 6, head=(10, 0, 0))
    sh(fun, s5, b, (-4.5, 3.0, 9.0), (0, -8, 3.2), 24, dl=(0, -0.6, 0)); ctx.sfx("gasp", s5, 0.9)
    # 1: "Password one two three!"
    a, b = L(1); toys.beak(f_cap, a + 2, b - 4, 4); ctx.sfx("squawk", a, 0.8)
    c = sh(fun, a, b, (0.3, 3.4, 3.5), rel(fp, (0, 0, 1.0)), 24, dl=(0.0, 0.5, 0.1), pz=wf(1, "three"), amount=1.3)
    shake(c, wf(1, "three"), 10, 0.3)
    # 2: "That's not my... okay, that's my password."
    (a, s1), (_, b) = seg(2, "okay")
    react(f_me, "nervous", a); sh(fun, a, s1, (-5.4, 2.6, 5.0), (-6.5, 5.7, 4.75), 30, dl=(0.2, 0.4, 0))
    react(f_me, "embarrassed", s1)
    for m in mourners[:8]: turn(m, s1, (-6.5, 5.7), 8); react(m, "suspicious", s1 + 2)
    sh(fun, s1, b, (0, -7, 6.2), (-6, 5, 4.3), 22, dl=(-0.3, 1.0, 0)); ctx.sfx("pop", s1, 0.5)

    # ======================= 3-9: a week earlier, the will =======================
    a3, b3 = L(3)
    S.flash(a3, 6); ctx.sfx("whoosh", a3, 0.9)
    toys.set_time(clk, a3, 9, 0)
    (a, s1), (_, s2), (_, s3), (_, b) = seg(3, "my", "one", "if")
    react(me, "smile", a); turn(me, a, (8, 0.6), 1); pose(law, a, 4, la=(-80, 0, 10))
    sh(hs, a, s1, (-6, -8.5, 4.0), (2, 2, 4.2), 22, dl=(1.5, 1.5, 0))                       # wide room, lawyer reads the will
    sh(ins, s1, s2, (0.2, -2.6, 2.6), (0, 0.1, 0), 30, dl=(0, 0.7, -0.5), cap="top"); ctx.sfx("rustle", s1, 0.7)  # the will
    react(me, "starstruck", s2); ctx.sfx("coin", s2, 0.8)
    sh(hs, s2, s3, (2.8, -0.6, 4.8), (0.2, -1.6, 4.7), 26, pz=s2 + 2)                       # me: one million
    toys.tilt(cap, s3 + 4, -20); ctx.sfx("tweet", s3 + 2, 0.4)
    sh(hs, s3, b, (2.0, 1.2, 5.8), (0, 3, 5.7), 24, dl=(-0.3, 0.3, 0))                     # Captain cocks his head
    # 4-6: "Twenty-four hours. Not one word." / "That's it?" / "That's it."
    a, b = L(4); react(law, "blank", a); talk_nod(law, a, b); pose(law, a, 4, la=(-50, 0, 10))
    sh(hs, a, b, (5.6, -1.0, 3.2), (8.1, 0.6, 4.4), 24, dl=(0.4, 0.3, 0))
    a, b = L(5); react(me, "suspicious", a); sh(hs, a, b, (2.9, -1.0, 4.7), (0.2, -1.6, 4.7), 28, dl=(0.2, 0.2, 0))
    a, b = L(6); react(law, "smug", a); talk_nod(law, a, b, 8, 10); sh(hs, a, b, (5.2, -0.9, 4.5), (8.1, 0.6, 4.4), 32, pz=a + 3, amount=1.15)
    # 7: "I signed immediately. How hard could it be to keep a bird quiet?"
    (a, s1), (_, s2), (_, b) = seg(7, "how", "bird")
    pen = empty("pen"); prim("cylY", (0.1, 0.1, 0.9), (0, 0, 0), mat((30, 30, 40), 0.3), parent=pen); hold(me, pen, "ra", (0, -0.2, 0), (60, 0, 0))
    show_between(pen, 0, 0); react(me, "grin", a); ctx.sfx("rustle", a + 2, 0.8)
    for k, f in enumerate(range(a, s1, 4)):  # the pen scribbles a signature
        ipen.location = (0.3 + 0.18 * k, -0.6 + (0.08 if k % 2 else -0.08), 0.25); ipen.keyframe_insert("location", frame=f)
    sh(ins, a, s1, (0.9, -2.2, 2.0), (0.6, -0.4, 0), 30, dl=(0.1, 0.4, -0.3), cap="top")
    rest(me, s1, "ra", ease=6); react(me, "smug", s1)
    sh(hs, s1, s2, (2.6, -0.4, 4.8), (0.2, -1.6, 4.7), 24, dl=(0.1, 0.3, 0))
    turn_f = s2 + 2; toys.tilt(cap, turn_f, 25, 10, axis=2); toys.lids(cap, turn_f + 10, False)
    sh(hs, s2, b, (2.0, 1.2, 5.8), (0, 3, 5.7), 26, dl=(-0.3, 0.3, 0)); ctx.sfx("scared", s2 + 4, 0.5)
    # 8: "Well, the parrot's name was Captain. And Captain had been listening ... forty years."
    (a, s1), (_, s2), (_, b) = seg(8, "captain", "and")
    toys.tilt(cap, a, 0, 6, axis=2)
    sh(hs, a, s1, (4.5, 0.0, 4.2), (0, 3, 5.4), 22, dl=(-1.0, 0.6, 0))
    sh(hs, s1, s2, (0.6, 0.6, 5.8), (0, 3, 5.8), 30, pz=s1 + 1, amount=1.3); ctx.sfx("ding", s1, 0.5)
    sh(hs, s2, b, (-7, -5, 3.0), (0, 3, 5.0), 20, dl=(2.0, 2.0, 0.6))                        # slow push across the whole room
    # 9: "He knew every secret, every swear word, and the Wi-Fi password."
    (a, s1), (_, s2), (_, b) = seg(9, "swear", "wi-fi")
    toys.lids(cap, a + 2, False); toys.tilt(cap, a + 2, -12, 6, axis=0)
    sh(hs, a, s1, (-1.4, 0.6, 5.6), (0, 3, 5.8), 30, dl=(0.4, 0.3, 0))
    sh(hs, s1, s2, (1.5, 0.9, 5.9), (0, 3, 5.8), 34, dl=(-0.3, 0.3, 0)); ctx.sfx("squawk", s1 + 6, 0.35)
    sh(hs, s2, b, (-12.6, 4.4, 4.4), (-13.2, 7.4, 4.0), 30, dl=(0, 0.6, 0)); ctx.sfx("ding", s2 + 2, 0.5)

    # ======================= 10-14: hour one, the cracker =======================
    def clock_insert(f0, f1, push=0.6):
        sh(hs, f0, f1, (-4, 4.6, 7.4), (-4, 8.75, 7.4), 30, dl=(0, push, 0), cap="low"); ctx.sfx("tick", f0, 0.8)
    (a, s1), (_, b) = seg(10, "i")
    clock_insert(a, s1)
    crk = empty("cracker"); prim("box", (0.45, 0.08, 0.45), (0, 0, 0), mat((230, 175, 90), 0.8), parent=crk, bevel=0.03)
    hold(me, crk, "ra", (0, -0.2, 0.15), (90, 0, 0)); show_between(crk, s1, L(11)[0] + 6)
    at(me, s1, (0.2, 0.0, 0), 180, ease=1); pose(me, s1, 6, ra=(-95, 0, 0)); react(me, "smile", s1)
    sh(hs, s1, b, (3.8, -0.6, 4.8), (0.1, 1.5, 5.0), 26, dl=(-0.4, 0.3, 0))
    # 11: "Thank you, loser!"
    a, b = L(11); beak(a + 2, b - 3, 4); ctx.sfx("squawk", a, 0.7); ctx.sfx("nom", a + 4, 0.6); toys.tilt(cap, a, 15)
    sh(hs, a, b, (-1.7, 1.5, 5.8), (0, 3, 5.8), 26, pz=wf(11, "loser"), amount=1.35); react(me, "shock", wf(11, "loser"))
    # 12: "He said that to me! That doesn't count!"
    a12, b12 = L(12); s1 = seg(12, "doesn't")[0][1]
    react(me, "angry", a12, b12 + 10); turn(me, a12, (8, 0.6), 6); pose(me, a12, 4, ra=(-95, 0, 30))
    sh(hs, a12, s1, (3.0, -1.2, 4.7), (0.2, 0.0, 4.7), 24, dl=(-0.3, 0.3, 0))
    sh(hs, s1, b12, (1.8, -2.2, 4.4), (8.1, 0.6, 4.3), 24, dl=(0.6, 0.2, 0)); ctx.sfx("angry", s1, 0.5)
    rest(me, b12, "ra")
    # 13: "It counts double."
    a, b = L(13); react(law, "smug", a); talk_nod(law, a, b)
    sh(hs, a, b, (4.0, -2.2, 4.4), (8.1, 0.6, 4.3), 26, dl=(0.2, 0.2, 0)); ctx.sfx("rustle", a + 4, 0.6)
    stopwatch_gag(14); react(me, "annoyed", L(14)[0])

    # ======================= 15-21: the blanket, Grandpa's voice, the freezer =======================
    (a, s1), (_, b) = seg(15, "that's")
    bl = toys.blanket(); bl.location = (0, 3, 0)
    K._key(bl, "location", a + 4, (0, 1.0, 5.5), 1); K._key(bl, "location", a + 12, (0, 3, 0))
    bl.scale = (0.3, 0.3, 0.3); bl.keyframe_insert("scale", frame=a + 4); bl.scale = (1, 1, 1); bl.keyframe_insert("scale", frame=a + 12)
    show_between(bl, a + 4, L(18)[0] + 2); ctx.sfx("whoosh", a + 4, 0.8)
    pose(me, a, 4, ra=(-150, 0, 0), la=(-150, 0, 0)); pose(me, a + 12, 6, ra=(-60, 0, 0), la=(-60, 0, 0)); react(me, "determined", a)
    sh(hs, a, s1, (4.4, -1.2, 4.4), (0.1, 1.8, 5.2), 22, dl=(-0.4, 0.4, 0))
    react(me, "smug", s1); rest(me, s1, "ra", "la"); turn(me, s1, (1.9, 2.3), 8)
    sh(hs, s1, b, (2.1, 2.5, 4.8), (0.2, 0.0, 4.7), 26, dl=(-0.2, -0.2, 0))
    # 16: "He fell asleep, all right. Then he started sleep talking. In Grandpa's voice."
    (a, s1), (_, s2), (_, b) = seg(16, "then", "in")
    ctx.sfx("snore", a + 2, 0.6)
    sh(hs, a, s1, (-2.6, 0.4, 4.8), (0, 3, 5.4), 24, dl=(0.3, 0.3, 0))
    at(me, s1, (0.9, 1.0, 0), (0, 3), ease=1); pose(me, s1, 6, waist=(18, 0, 0), head=(0, 0, -15)); react(me, "suspicious", s1)
    sh(hs, s1, s2, (3.4, 2.0, 4.8), (0.9, 1.0, 4.8), 26, dl=(-0.3, 0.1, 0))
    react(me, "big_eyes", s2); turn(me, s2, (-2.8, 0.6), 4); sh(hs, s2, b, (-2.8, 0.6, 4.8), (0.9, 1.0, 4.8), 30, pz=s2 + 2); ctx.sfx("scared", s2, 0.6)
    # 17: "Don't tell my grandson about the money in the freezer."
    (a, s1), (_, b) = seg(17, "money")
    ctx.music(a, "paused")
    sh(hs, a, s1, (-3.2, -1.2, 5.0), (0, 3, 5.4), 24, dl=(0.6, 0.6, 0))                    # slow creep toward the covered cage
    react(me, "starstruck", s1); turn(me, s1, (-2.6, -1.8), 6)
    sh(hs, s1, b, (-2.6, -1.8, 4.8), (0.9, 1.0, 4.8), 34, pz=wf(17, "freezer"), amount=1.3)
    ctx.sfx("sparkle", wf(17, "freezer"), 0.7)
    # 18: "I froze. Then I ran to the freezer."
    (a, s1), (_, b) = seg(18, "then")
    ctx.music(a, "normal"); react(me, "shock", a)
    sh(hs, a, s1, (-2.8, -2.0, 4.8), (0.9, 1.0, 4.8), 30); ctx.sfx("freeze", a, 0.6)
    walk(me, s1, b - 1, (0.9, 0.0, 0), (-19.2, 3.6, 0), 5, 40); react(me, "determined", s1)
    sh(hs, s1, b, (-19.5, 1.0, 3.0), (-8, 2.2, 4.4), 22, dt=(-6, 1.2, 0)); ctx.sfx("step", s1 + 3); ctx.sfx("step", s1 + 8); ctx.sfx("step", s1 + 13)
    # 19: "Inside was one frozen chicken nugget and a note that said, 'Nice try.'"
    (a, s1), (_, s2), (_, b) = seg(19, "one", "nice")
    at(me, a, (-19.2, 3.6, 0), (-20.2, 7.2), ease=1); pose(me, a, 4, la=(-100, 0, 30))
    fz.keyframe_insert("rotation_euler", frame=a); fz.rotation_euler = (0, 0, math.radians(105)); fz.keyframe_insert("rotation_euler", frame=a + 8)
    ctx.sfx("freeze", a + 2, 0.7); react(me, "starstruck", a + 4)
    sh(hs, a, s1, (-16.4, 1.4, 4.8), (-19.6, 5.6, 5.0), 22, dl=(-0.4, 0.4, 0))
    sh(hs, s1, s2, (-20.2, 4.6, 5.4), (-20.2, 7.0, 5.05), 30, dl=(0, 0.5, -0.05)); react(me, "blank", s2)
    sh(hs, s2, b, (-20.4, 5.2, 5.5), (-20.4, 7.6, 5.35), 34, pz=s2 + 2, amount=1.2); ctx.sfx("sad", s2 + 2, 0.5)
    # 20: "I'm not proud of it. I ate the nugget."
    (a, s1), (_, b) = seg(20, "ate")
    hn = toys.nugget(); hold(me, hn, "ra", (0, -0.25, 0.1)); show_between(hn, a, s1 + 14); show_between(nug, 0, a)
    pose(me, a, 4, ra=(-80, 0, 0)); react(me, "embarrassed", a); turn(me, a, (-18, 0), 4)
    sh(hs, a, s1, (-18.2, 0.6, 4.8), (-19.2, 3.6, 4.8), 28, dl=(0.2, 0.4, 0))
    pose(me, s1, 4, ra=(-150, 0, 20)); react(me, "happy", s1 + 2); ctx.sfx("nom", s1 + 4, 0.9)
    sh(hs, s1, b, (-18.2, 0.8, 4.6), (-19.2, 3.6, 4.7), 26, pz=s1 + 4, amount=1.2)
    rest(me, b, "ra", "la")
    stopwatch_gag(21)

    # ======================= 22-28: sign language, whale sounds, the viral video =======================
    (a, s1), (_, b) = seg(22, "i")
    clock_insert(a, s1); at(me, s1, (0.2, 0.0, 0), 180, ease=1); react(me, "determined", s1)
    for k, f in enumerate(range(s1, b, 6)):
        pose(me, f, 3, ra=((-110, 0, 30) if k % 2 else (-70, 0, -20)), la=((-70, 0, 20) if k % 2 else (-120, 0, -30)))
    sh(hs, s1, b, (1.9, 2.3, 4.9), (0.2, 0.0, 4.7), 26, dl=(-0.2, -0.2, 0))
    rest(me, b, "ra", "la")
    # 23: "He learned it in ten minutes. Then he signed something I can't repeat."
    (a, s1), (_, s2), (_, b) = seg(23, "then", "i")
    for k, f in enumerate(range(a, s2, 5)):
        for w, sd in cap["wings"]:
            w.rotation_euler = (math.radians(-60 if k % 2 else -20), math.radians(sd * (40 if k % 2 else 70)), 0); w.keyframe_insert("rotation_euler", frame=f)
    for w, sd in cap["wings"]: w.rotation_euler = (0, 0, 0); w.keyframe_insert("rotation_euler", frame=s2 + 10)
    sh(hs, a, s1, (1.7, 1.5, 5.6), (0, 3, 5.4), 28, dl=(-0.2, 0.3, 0))
    sh(hs, s1, s2, (-1.7, 1.5, 5.6), (0, 3, 5.4), 30, cap="top"); ctx.overlays.append((A + "censored.png", s1 + 3, s2, 7, 0, 60, 1.1))
    ctx.sfx("buzz", s1 + 3, 0.6); react(me, "shock", s2); react(law, "disgusted", s2)
    sh(hs, s2, b, (1.9, 2.3, 4.9), (0.2, 0.0, 4.7), 26, dl=(-0.2, -0.2, 0))
    # 24: "By hour twelve, I was desperate. I put headphones on him and played whale sounds."
    (a, s1), (_, s2), (_, b) = seg(24, "i", "and")
    clock_insert(a, s1)
    react(me, "worried", s1); sh(hs, s1, s1 + max(6, (s2 - s1) // 2), (1.9, 2.3, 4.9), (0.2, 0.0, 4.7), 28, dl=(-0.1, -0.2, 0))
    hp_ = toys.headphones(); hp_.parent = cap["head"]; hp_.location = (0, 0, 0.3); hp_.scale = (1.15, 1.15, 1.15); show_between(hp_, s2 - 6)
    pose(me, s1 + max(6, (s2 - s1) // 2), 4, ra=(-130, 0, 0))
    sh(hs, s1 + max(6, (s2 - s1) // 2), s2, (1.7, 1.5, 5.8), (0, 3, 5.8), 30, dl=(-0.2, 0.3, 0))
    wp = toys.card(A + "phone_whale.png", 0.5, 0.9); hold(me, wp, "la", (0, -0.25, 0.1), (80, 0, 0)); show_between(wp, s2, L(25)[0])
    pose(me, s2, 4, la=(-100, 0, 20), ra=(-30, 0, 0)); ctx.sfx("whale", s2 + 2, 0.7)
    sh(ins, s2, b, (20.1, -3.2, 1.4), (20, 0, 1.0), 30, dl=(0, 1.0, 0), cap="top")
    rest(me, b, "ra", "la")
    # 25: "He loved it. He started singing along. Like, professionally. My neighbor started filming."
    (a, s1), (_, s2), (_, s3), (_, b) = seg(25, ("he", 1), "like", "my")
    toys.lids(cap, a, True); toys.tilt(cap, a + 2, 12, 6, axis=1); react(me, "relieved", a)
    sh(hs, a, s1, (1.7, 1.5, 5.8), (0, 3, 5.8), 30, dl=(-0.2, 0.3, 0))
    beak(s1, s3, 5); ctx.sfx("sing", s1, 0.8); ctx.sfx("sing", s2, 0.8); toys.lids(cap, s1 + 2, False)
    for k, f in enumerate(range(s1, s3, 10)): toys.tilt(cap, f, 14 if k % 2 else -14, 5, axis=1)
    react(me, "shock", s1); sh(hs, s1, s2, (-2.0, -1.0, 4.6), (0, 3, 5.8), 24, dl=(0.6, 0.4, 0))
    react(me, "confused", s2); sh(hs, s2, s3, (-1.7, 1.5, 5.8), (0, 3, 5.8), 26, pz=s2 + 2, amount=1.2)
    react(nb, "starstruck", s3); sh(hs, s3, b, (4.8, 4.4, 4.0), (6, 10.6, 4.6), 24, dl=(0.2, 0.6, 0)); ctx.sfx("click", s3 + 6, 0.6)
    # 26: "Bro, this bird can sing!"
    a, b = L(26); talk_nod(nb, a, b, 8, 10)
    sh(hs, a, b, (6.6, 7.0, 4.6), (6, 10.6, 5.0), 26, pz=wf(26, "sing"), amount=1.2)
    # 27: "The video got a million views. The lawyer said singing counts as words."
    (a, s1), (_, b) = seg(27, "lawyer")
    sh(hs, a, s1, (6, 8.0, 4.2), (6, 10.6, 4.6), 30, cap="top"); ctx.overlays.append((A + "viral.png", a + 2, s1, 7, 0, 0, 1.0))
    ctx.sfx("whoosh", a + 1, 0.6); ctx.sfx("coin", wf(27, "million"), 0.7)
    react(law, "annoyed", s1); talk_nod(law, s1, b)
    sh(hs, s1, b, (4.0, -2.2, 4.3), (8.1, 0.6, 4.3), 26, dl=(0.3, 0.3, 0))
    # 28: "Starting over. Also, can I get an autograph?"
    (a, s1), (_, b) = seg(28, "also")
    click(isw_btn, a + 4); ctx.sfx("click", a + 4, 1.2); react(law, "blank", a)
    sh(ins, a, s1, (9.6, -3.2, 1.3), (10, 0, 0.8), 30, dl=(0.2, 0.9, 0), pz=a + 4, amount=1.3, cap="top")
    react(law, "love", s1); pose(law, s1, 6, ra=(-55, 0, -10), la=(-110, 0, -30)); talk_nod(law, s1, b, 8, 8)
    sh(hs, s1, b, (4.6, 1.8, 4.6), (8.1, 0.6, 4.4), 26, dl=(0.3, 0, 0)); ctx.sfx("sparkle", s1 + 2, 0.5)
    pose(law, b, 6, la=(-50, 0, 10))

    # ======================= 29-32: hour eighteen, the taxes =======================
    (a, s1), (_, s2), (_, b) = seg(29, "i", "i")
    clock_insert(a, s1)
    tx = toys.papers(A + "taxes.png", 10); hold(me, tx, "la", (0.5, -0.4, 0.2), (90, 0, 0)); show_between(tx, s1, L(31)[0] + 6)
    at(me, s1, (0.2, -0.4, 0), 180, ease=1); pose(me, s1, 4, la=(-85, 0, 30), ra=(-85, 0, -30)); react(me, "sleepy", s1)
    sh(hs, s1, s2, (2.6, 1.4, 4.4), (0.2, -0.4, 4.8), 24, dl=(-0.3, 0.3, 0)); ctx.sfx("rustle", s1 + 2, 0.8)
    sh(hs, s2, b, (1.9, 2.3, 4.9), (0.2, -0.4, 4.6), 26, dl=(-0.2, -0.2, 0)); ctx.sfx("rustle", s2 + 4, 0.6)
    # 30: "He fell asleep in two minutes. Then he woke up and corrected my math."
    (a, s1), (_, b) = seg(30, "then")
    toys.lids(cap, a + 2, True); h = cap["head"]; toys.tilt(cap, a + 8, 25, 8, axis=0); ctx.sfx("snore", a + 6, 0.5)
    react(me, "relieved", a); sh(hs, a, s1, (-1.0, -0.2, 4.8), (0, 3, 5.6), 26, dl=(0.3, 0.4, 0))
    toys.lids(cap, s1 + 1, False, 2); toys.tilt(cap, s1 + 1, -8, 2, axis=0); react(me, "shock", s1 + 2)
    sh(hs, s1, b, (0.4, 0.8, 5.9), (0, 3, 5.9), 30, pz=s1 + 2, amount=1.25); ctx.sfx("boing", s1 + 1, 0.5)
    # 31: "Wrong!"
    a, b = L(31); beak(a + 1, b - 2, 4); ctx.sfx("squawk", a, 0.9); react(me, "annoyed", a + 4)
    c = sh(hs, a, b, (0.2, 1.4, 5.8), (0, 3, 5.9), 22, pz=a + 1, amount=1.45); shake(c, a + 2, 10, 0.4)
    stopwatch_gag(32)

    # ======================= 33-41: the final staring contest =======================
    a33, b33 = L(33)
    for o in (perch, tbl): vis(o, a33, True)
    cap_root = cap["root"]; K._key(cap_root, "location", a33, (0, 1.2, 3.2), 1)  # Captain on the T-perch on the table
    sit(me, a33, 1.58, (0, -1.4), 180, ease=1)
    seat = toys.chair(0, -1.5, 180)
    show_between(seat, a33)
    (a, s1), (_, s2), (_, s3), (_, s4), (_, s5), (_, b) = seg(33, "final", "i'd", "no", "no", "no")
    react(me, "determined", a); sh(hs, a, s1, (3.4, 1.8, 4.6), (0, -1.0, 4.4), 22, dl=(-0.4, -0.3, 0))
    sh(hs, s1, s2, (1.2, 0.2, 4.6), (0, -1.4, 4.6), 30, pz=s1 + 1, amount=1.2)
    sh(hs, s2, s3, (-4.5, -0.2, 3.4), (0, 0, 4.0), 22, dl=(0.6, 0.4, 0))
    tv_on.keyframe_insert("default_value", frame=s3 + 2); tv_on.default_value = 0.0; tv_on.keyframe_insert("default_value", frame=s3 + 3)
    sh(hs, s3, s4, (-11, 3.4, 3.2), (-11, 7.6, 3.0), 26, dl=(0, 0.6, 0), cap="top"); ctx.sfx("pause", s3 + 2, 0.5)
    ph = toys.phone(); K._key(ph, "location", s4, (0.6, -1.2, 3.6), 1); K._key(ph, "location", s4 + 10, (-10.5, -2.4, 1.7))
    ph.rotation_euler = (0, 0, 0); ph.keyframe_insert("rotation_euler", frame=s4); ph.rotation_euler = (math.radians(540), 0, math.radians(90)); ph.keyframe_insert("rotation_euler", frame=s4 + 10)
    show_between(ph, s4); pose(me, s4, 3, ra=(-120, 0, 40)); rest(me, s4 + 8, "ra")
    sh(hs, s4, s5, (-4.0, -6.0, 3.8), (-6, -2, 2.4), 22, dt=(-4, 0, -0.5)); ctx.sfx("whoosh", s4 + 1, 0.6)
    cb = toys.box_prop(A + "cracker_red.png", 0.9, 0.4, 1.2); K._key(cb, "location", s5, (0.4, -0.6, 3.8), 1); K._key(cb, "location", s5 + 9, (-14, 5.8, 1.8))
    show_between(cb, s5, s5 + 10); ctx.sfx("splat", s5 + 9, 0.5)
    sh(hs, s5, b, (-10.6, 2.4, 3.2), (-14, 5.8, 1.6), 26, dl=(-0.3, 0.3, 0))
    # 34: "Hour twenty-three. Fifty-nine minutes. I was staring at him. He was staring at me."
    (a, s1), (_, s2), (_, s3), (_, b) = seg(34, "fifty-nine", "i", "he")
    ctx.music(a, "paused")
    sh(rc, a, s1, (0, -9, 0), (0, 0.6, 0), 34, dl=(0, 1.5, 0), cap="low"); ctx.sfx("tick", a, 1.0)
    sh(rc, s1, s2, (1.2, -6.5, 0.4), (0, 0.6, 0.2), 34, dl=(-0.6, 1.0, 0), cap="low"); ctx.sfx("heartbeat", s1, 0.7)
    react(me, "determined", s2); sh(hs, s2, s3, (0.5, 0.0, 4.7), (0, -1.4, 4.6), 40, dl=(0, -0.25, 0))
    sh(hs, s3, b, (0.3, -0.5, 4.6), (0, 1.2, 4.7), 32, dl=(0, 0.25, 0)); toys.lids(cap, s3, False)
    # 35: "Then the doorbell rang. It was my cousin Derek. Grandpa's other grandson."
    (a, s1), (_, s2), (_, b) = seg(35, "it", "grandpa's")
    ctx.sfx("doorbell", a + 2, 0.9); react(me, "shock", a + 4); turn(me, a + 6, (14, 3), 6)
    sh(hs, a, s1, (2.6, -3.4, 4.6), (0, -1.4, 4.6), 26, pz=a + 4, amount=1.15)
    door.keyframe_insert("rotation_euler", frame=s1); door.rotation_euler = (0, 0, math.radians(-100)); door.keyframe_insert("rotation_euler", frame=s1 + 8)
    at(der, s1, (16.5, 3, 0), -90, ease=1); react(der, "smug", s1); ctx.sfx("whoosh", s1 + 2, 0.5)
    sh(hs, s1, s2, (10.5, -1.5, 3.6), (15, 3, 4.6), 22, dl=(0.6, 0.2, 0))
    walk(der, s2, min(s2 + 30, L(36)[0] - 2), (16.5, 3, 0), (3.0, 1.8, 0), 6, 30)
    sh(hs, s2, b, (4.0, -1.6, 3.8), (12, 3, 4.6), 22, dt=(-6, -0.6, 0)); react(me, "annoyed", s2)
    # 36-37: Derek: "Hey, Captain! Say 'Derek is the best'!" / "Come on, buddy... Say Derek!"
    a, b = L(36); turn(me, a, (0, 1.2), 6); at(der, a, (2.4, 2.4, 0), (0, 1.2), ease=1); pose(der, a, 4, waist=(20, 0, 0)); react(der, "grin", a); talk_nod(der, a, b, 8, 8)
    sh(hs, a, b, (-0.2, -0.6, 4.8), (2.4, 2.4, 4.7), 22, dl=(0.1, 0.2, 0))
    a, b = L(37); gold = toys.box_prop(A + "cracker_gold.png", 0.8, 0.35, 1.05, (250, 200, 40)); hold(der, gold, "ra", (0, -0.4, 0.3), (90, 0, 0))
    show_between(gold, a, L(39)[0]); pose(der, a, 4, ra=(-100, 0, -30)); react(der, "happy", a); talk_nod(der, a, b, 8, 8)
    for k, f in enumerate(range(a + 4, b, 6)): pose(der, f, 2, ra=(-100 if k % 2 else -85, 0, -30))
    sh(hs, a, b, (0.0, -0.4, 4.0), (2.0, 2.2, 4.6), 22, dl=(0.1, 0.2, 0)); toys.tilt(cap, a + 6, 10, 6, axis=2)
    # 38: "Derek wanted the money too. He even brought crackers. The good ones."
    (a, s1), (_, s2), (_, b) = seg(38, "he", "the")
    react(me, "suspicious", a); sh(hs, a, s1, (-1.8, 0.4, 4.6), (0, -1.4, 4.7), 26, dl=(0.2, 0.2, 0))
    sh(ins, s1, s2, (30.3, -3.4, 1.6), (30, 0, 0.8), 28, dl=(0, 1.0, 0), cap="top"); ctx.sfx("sparkle", s1 + 2, 0.7)
    react(der, "smug", s2); sh(hs, s2, b, (-1.2, -0.6, 5.0), (2.4, 2.4, 5.0), 26, pz=s2 + 2, amount=1.15)
    # 39: "Captain opened his beak. I couldn't breathe."
    (a, s1), (_, b) = seg(39, "i")
    toys.beak_open(cap, s1 - 2, 30, 14); ctx.sfx("heartbeat", a, 0.8)
    sh(hs, a, s1, (0.2, -0.5, 4.6), (0, 1.2, 4.7), 28, dl=(0, 0.5, 0), cap="top")
    react(me, "terrified", s1); react(der, "starstruck", s1)
    sh(hs, s1, b, (0.4, 0.6, 4.6), (0, -1.4, 4.6), 40, dl=(0, 0.35, 0))
    # 40: "Then he closed it, flew across the room, and landed on my shoulder."
    (a, s1), (_, s2), (_, b) = seg(40, "flew", "landed")
    j = cap["jaw"]; j.keyframe_insert("rotation_euler", frame=a + 2); j.rotation_euler = (0, 0, 0); j.keyframe_insert("rotation_euler", frame=a + 6)
    sh(hs, a, s1, (0.2, -0.5, 4.6), (0, 1.2, 4.7), 28, pz=a + 5, amount=1.15); ctx.sfx("click", a + 5, 0.4)
    shoulder = empty("shoulder", (-0.62, 0.05, 2.02), me["waist"])
    land = s2 + 6
    for f, p in ((s1, (0, 1.2, 3.2)), (s1 + (land - s1) // 2, (-4.0, -4.0, 8.0)), (land, (0.62, -1.45, 4.0))):
        K._key(cap_root, "location", f, p)
    cap_root.rotation_euler = (0, 0, 0); cap_root.keyframe_insert("rotation_euler", frame=s1)
    cap_root.rotation_euler = (0, 0, math.radians(200)); cap_root.keyframe_insert("rotation_euler", frame=s1 + 8)
    cap_root.rotation_euler = (0, 0, math.radians(360 + 90)); cap_root.keyframe_insert("rotation_euler", frame=land)
    con = cap_root.constraints.new("COPY_LOCATION"); con.target = shoulder
    con.influence = 0; con.keyframe_insert("influence", frame=land - 1); con.influence = 1; con.keyframe_insert("influence", frame=land)
    toys.flap({"wings": cap["wings"]}, s1, land, 6, 70); ctx.sfx("flap", s1, 0.9)
    sh(hs, s1, s2, (-6, -7.5, 2.8), (-2, -1.5, 5.0), 20, dt=(-2.4, -1.6, 1.0))
    react(me, "big_eyes", land); react(der, "shock", land)
    c = sh(hs, s2, b, (1.6, 1.0, 5.0), (0.3, -1.4, 5.0), 26, dl=(-0.2, 0.3, 0)); ctx.sfx("pop", land, 0.6)
    # 41: "The clock hit twenty-four hours. Silence."
    (a, s1), (_, b) = seg(41, "silence")
    clock_insert(a, s1, 0.9); ctx.sfx("bell", wf(41, "clock") + 4, 0.6)
    sh(hs, s1, b, (-8, -7, 3.4), (2, 0, 4.4), 22, dl=(1.0, 1.0, 0)); ctx.sfx("sigh", s1, 0.3)

    # ======================= 42-51: the win, the whisper, the flashback =======================
    a, b = L(42); ctx.music(a, "normal")
    chk = toys.card(A + "check.png", 1.4, 0.6); hold(law, chk, "la", (0, -0.4, 0.3), (80, 0, 0)); show_between(chk, a); show_between(clip, 0, a)
    at(law, a, (3.4, -2.6, 0), (0, -1.4), ease=1); rest(law, a, "ll", "rl", "ll_knee", "rl_knee", "waist", ease=1)
    pose(law, a, 4, la=(-95, 0, 20)); react(law, "happy", a); talk_nod(law, a, b)
    sh(hs, a, b, (-0.8, -4.0, 4.2), (2.2, -1.8, 4.6), 24, dl=(0.3, 0.3, 0)); ctx.sfx("coin", a + 6, 0.8)
    # 43: "Derek dropped to his knees. I couldn't believe it."
    (a, s1), (_, b) = seg(43, "i")
    at(der, a, (2.4, 2.4, -1.2), (0, -1.4), ease=4); pose(der, a, 4, ll_knee=(90, 0, 0), rl_knee=(90, 0, 0), la=(-150, 0, 20), ra=(-150, 0, -20))
    react(der, "cry", a, b + 20); ctx.sfx("cry", a + 4, 0.6)
    sh(hs, a, s1, (0.8, -0.2, 3.4), (2.4, 2.4, 3.2), 24, dl=(-0.2, 0.2, 0))
    react(me, "starstruck", s1); sh(hs, s1, b, (1.3, 0.8, 4.6), (-0.2, -1.4, 4.8), 28, pz=s1 + 2, amount=1.1)
    # 44: "Why did you stay quiet, Captain?"
    a, b = L(44); react(me, "smile", a); pose(me, a, 6, head=(0, 0, -25))
    sh(hs, a, b, (1.6, 0.6, 4.7), (0.3, -1.4, 4.8), 30, dl=(-0.2, 0.2, 0))
    # 45: "He leaned in and whispered in Grandpa's voice."
    a, b = L(45); toys.tilt(cap, a + 4, -25, 10, axis=2); toys.tilt(cap, a + 10, 18, 8, axis=0)
    sh(hs, a, b, (2.2, 0.2, 4.8), (0.4, -1.4, 4.7), 34, dl=(-0.4, 0.4, 0))
    # 46: "Because you stayed."
    a, b = L(46); beak(a + 2, b - 4, 7); react(me, "cry", a + 6, L(47)[0] + 40); ctx.sfx("sparkle", a, 0.4)
    ctx.music(a, "paused")
    sh(hs, a, b, (1.8, 0.2, 4.6), (0.5, -1.3, 4.7), 36, dl=(-0.2, 0.25, 0)); S.whiteout(b - 2, 10, 4, 14)
    # 47: "I wanted to cry. Every Sunday for ten years, I visited Grandpa. Derek visited once. For the Wi-Fi."
    (a, s1), (_, s2), (_, s3), (_, b) = seg(47, "every", "derek", "for")
    sh(hs, a, s1, (0.6, 0.6, 4.6), (-0.1, -1.4, 4.8), 36, dl=(0, 0.25, 0))
    react(gp, "happy", s1); react(kid, "happy", s1)
    sh(pc, s1, s2, (-3.5, -9.0, 3.2), (-3.5, 1.7, 3.8), 26, dl=(0, 2.0, 0.2), look="flashback")
    react(yder, "blank", s2); sh(pc, s2, s3, (6.5, -5.0, 3.0), (4.6, -0.5, 1.8), 26, dl=(-0.3, 0.4, 0), look="flashback")
    sh(pc, s3, b, (4.2, 0.4, 3.0), (5.0, 2.7, 3.3), 30, dl=(0.1, 0.4, 0), look="flashback"); ctx.sfx("ding", s3 + 2, 0.4)
    # 48: "Grandpa always told me, 'Anybody can talk. Not everybody listens.'"
    (a, s1), (_, b) = seg(48, "anybody")
    pose(gp, a, 10, head=(0, 0, -30))
    sh(pc, a, s1, (-3.4, -5.5, 4.6), (-3.5, 1.7, 4.4), 30, dl=(0, 0.6, 0), look="flashback")
    talk_nod(gp, s1, b, 12, 6); react(gp, "smile", s1); pose(kid, s1, 10, head=(-12, 0, 20))
    sh(pc, s1, b, (-3.6, -2.6, 5.0), (-2.3, 1.7, 4.8), 30, dl=(0.2, 0.3, 0), look="flashback")
    # 49: "Captain wasn't the test. The visits were."
    (a, s1), (_, b) = seg(49, ("the", 1))
    ctx.music(a, "normal"); react(me, "relieved", a)
    toys.tilt(cap, a, 0, 6, axis=0); toys.tilt(cap, a + 2, -30, 8, axis=2)
    sh(hs, a, s1, (1.6, 0.8, 4.8), (0.2, -1.4, 4.8), 26, dl=(-0.2, 0.2, 0))
    react(me, "smile", s1); sh(hs, s1, b, (-5, 2.5, 4.6), (0.2, -1.4, 4.4), 22, dl=(1.0, -0.4, 0))
    # 50: "Then the lawyer cleared his throat."
    a, b = L(50); react(law, "smug", a); ctx.sfx("ahem", a + 6, 0.9); pose(law, a + 4, 4, ra=(-130, 0, 40))
    sh(hs, a, b, (1.2, -1.9, 4.6), (3.4, -2.6, 4.6), 30, pz=a + 8, amount=1.15); rest(law, b, "ra")
    # 51: "One more thing. You also inherit Captain."
    (a, s1), (_, b) = seg(51, "you")
    talk_nod(law, a, b); react(law, "grin", a)
    sh(hs, a, s1, (1.0, -2.4, 4.4), (3.4, -2.6, 4.6), 26, dl=(0.2, 0.1, 0))
    react(me, "blank", s1); toys.tilt(cap, s1 + 4, 0, 6, axis=2); toys.tilt(cap, wf(51, "captain") + 2, 22, 5, axis=1)
    sh(hs, s1, b, (0.8, 1.0, 4.8), (0.2, -1.4, 4.9), 28, pz=wf(51, "captain") + 2, amount=1.25); ctx.sfx("tweet", wf(51, "captain") + 4, 0.6)

    # ======================= 52-54: back to the funeral =======================
    a52, b52 = L(52); S.flash(a52, 6); ctx.sfx("whoosh", a52, 0.9)
    for m in mourners + [f_law, f_der]: react(m, "smile", a52)
    react(f_me, "blank", a52)
    f_cap["root"].keyframe_insert("location", frame=a52)
    sh(fun, a52, b52, (0, -17, 5.0), (0, 6, 4.0), 22, dl=(0, 4.0, -0.4))
    # 53: "Password one two three!"
    a, b = L(53); toys.beak(f_cap, a + 2, b - 4, 4); ctx.sfx("squawk", a, 0.9); toys.tilt(f_cap, a, -10, 4, axis=0)
    for m in mourners + [f_law, f_der]: react(m, "shock", a + random.randint(2, 6))
    c = sh(fun, a, b, (0.2, 3.0, 3.6), rel(fp, (0, 0, 1.0)), 22, pz=wf(53, "three"), amount=1.35); shake(c, wf(53, "three"), 10, 0.3)
    ctx.sfx("gasp", wf(53, "three") + 4, 0.8)
    # 54: "I changed my password. He already knows the new one."
    (a, s1), (_, b) = seg(54, "he")
    react(f_me, "annoyed", a); sh(fun, a, s1, (-5.2, 2.6, 5.1), (-6.5, 5.7, 5.3), 30, dl=(0.2, 0.3, 0))
    toys.tilt(f_cap, s1 + 2, 20, 6, axis=2); toys.beak(f_cap, s1 + 6, s1 + 16, 5); ctx.sfx("tweet", s1 + 6, 0.6)
    sh(fun, s1, b, (2.4, -1.5, 3.2), (-1.5, 5.4, 4.8), 22, dl=(-0.6, 0.8, 0.4))

    # ======================= head motion on every spoken line =======================
    # dialogue: the speaker's head nods on each word; narration: lighter, on whichever "me" is on screen
    speakers = {i: law for i in (4, 6, 13, 14, 21, 28, 32, 42, 51)}; speakers.update({26: nb, 36: der, 37: der})
    for i, (who, _) in enumerate(ctx.story["lines"]):
        a, b = L(i)
        if i in speakers: talk_nod(speakers[i], a, b)
        elif who == "narrator" and i not in (47, 48): talk_nod(f_me if i in (0, 2, 52, 54) else me, a, b, amount=0.6)
    talk_nod(gp, *seg(48, "anybody")[1])
    hs.__exit__(None, None, None)
