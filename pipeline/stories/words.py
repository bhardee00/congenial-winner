""""Everyone In My Town Only Gets 10,000 Words" - reference #2 style (the step-counter short): a realistic-lit
suburb (Kenney CC0 models + Poly Haven sky and textures, see town.py), R6 characters in printed clothes, and a
glowing counter on every chest that ticks down one per spoken word. Voices at 1.60x / 1.75x with no dead air.
Line numbers follow stories/words.json (0-55). Sets: town (street, porches, bench, front yard, block party, park
stage, football field) and inside (living room, bathroom, dining room, bedroom, library, diner)."""
import math, random
from mathutils import Vector, Matrix
import shortkit as K
from shortkit import Set, prim, mat, empty, show_between, pose, rest, at, turn, walk, sit, idle, shake, nod
import blocky, toys, town
from avatar import react
from storykit import Kit, wall_mat, glasses, hold
import words_images as WI

random.seed(10)
SKIN, TAN, BROWN = (234, 190, 150), (204, 142, 105), (150, 100, 70)


def fr(pos, face, head, dist=3.0, ang=0.0, dz=0.15):
    """Camera in front of a face: pos (x, y), facing (point or yaw), head height; ang swings it around (deg)."""
    yaw = math.radians(K.yaw_to(pos, face))
    d = Matrix.Rotation(math.radians(ang), 3, 'Z') @ Vector((math.sin(yaw), -math.cos(yaw), 0))
    return (pos[0] + d.x * dist, pos[1] + d.y * dist, head + dz), (pos[0], pos[1], head)


def chest(pos, face, head, dist=2.2, ang=0.0):
    """Camera on someone's chest counter (badge sits ~1.4 below the head centre)."""
    loc, tgt = fr(pos, face, head - 1.45, dist, ang, 0.0)
    return loc, tgt


LOOKS = {
    "max": {"skin": SKIN, "shirt_tex": "stripes_blue", "pants_tex": "denim", "hair": (230, 120, 40), "shoes": (240, 240, 240), "scale": 0.62},
    "mom": {"skin": SKIN, "shirt_tex": "dots_pink", "pants": (60, 60, 80), "hair": (120, 60, 35), "shoes": (40, 40, 45), "pigtails": False},
    "pearl": {"skin": SKIN, "shirt_tex": "floral_blue", "pants": (90, 90, 140), "hair": (225, 225, 230), "shoes": (60, 40, 30)},
    "hend": {"skin": SKIN, "shirt_tex": "plaid_red", "pants_tex": "denim", "hair": (110, 75, 45), "shoes": (60, 40, 30)},
    "gibbs": {"skin": TAN, "shirt_tex": "plaid_brown", "pants": (90, 85, 80), "hair": (200, 200, 205), "shoes": (40, 30, 25)},
    "mayor": {"skin": SKIN, "shirt": (35, 40, 70), "sleeves": (35, 40, 70), "pants": (35, 40, 70), "hair": (60, 45, 35), "shoes": (20, 20, 20)},
    "waitress": {"skin": BROWN, "shirt": (240, 120, 150), "pants": (240, 240, 240), "hair": (40, 25, 20), "shoes": (250, 250, 250)},
    "player1": {"skin": TAN, "shirt": (200, 40, 40), "pants": (240, 240, 240), "hair": None, "hat": "cap", "hat_color": (200, 40, 40), "shoes": (20, 20, 20)},
    "player2": {"skin": BROWN, "shirt": (40, 80, 200), "pants": (240, 240, 240), "hair": None, "hat": "cap", "hat_color": (40, 80, 200), "shoes": (20, 20, 20)},
    "baby": {"skin": SKIN, "shirt": (250, 220, 120), "pants": (250, 220, 120), "hair": (230, 180, 120), "shoes": (250, 250, 250), "scale": 0.42},
}
CROWD = [("floral_green", (60, 60, 80), (40, 30, 20), SKIN), ("plaid_red", (50, 60, 90), (20, 20, 20), BROWN), ("stripes_red", (40, 40, 50), (230, 200, 120), SKIN),
         (None, (70, 120, 70), (150, 90, 40), TAN), ("dots_pink", (60, 60, 80), (30, 20, 15), BROWN), ("plaid_brown", (40, 50, 80), (90, 60, 35), SKIN),
         ("floral_blue", (90, 90, 120), (200, 200, 205), SKIN), (None, (200, 120, 50), (20, 20, 20), BROWN), ("stripes_blue", (40, 40, 50), (240, 210, 140), SKIN),
         ("denim_dark", (60, 60, 70), (110, 75, 45), TAN), ("plaid_red", (80, 80, 90), (60, 40, 30), SKIN), ("floral_green", (40, 50, 80), (230, 120, 40), TAN)]
CROWD_N = [4021, 6688, 3157, 9204, 5512, 2890, 7733, 1846, 8312, 4477, 6930, 6120]


def build(ctx):
    S, L, A, D = ctx.short, ctx.L, ctx.A, ctx.D
    timed = ctx.timed
    kit = Kit(ctx); seg, wf, sh = kit.seg, kit.wf, kit.sh
    B = lambda v: A + WI.badge_name(v)

    def look(k):
        lk = dict(LOOKS[k])
        for p in ("shirt_tex", "pants_tex"):
            if lk.get(p): lk[p] = A + f"print_{lk[p]}.png"
        return lk

    def npc(name, lk, loc=(0, -300, 0), yaw=0):
        a = blocky.build(D, name, lk); at(a, 0, loc, yaw, ease=1); idle(a, ("head",), 0.025, 50); return a

    def shf(st, f0, f1, who, dist=3.0, ang=0.0, lens=26, push=0.12, dz=0.15, **kw):
        loc, tgt = fr(*who, dist=dist, ang=ang, dz=dz)
        return sh(st, f0, f1, loc, tgt, lens, dl=tuple((t - l) * push for l, t in zip(loc, tgt)), **kw)

    def shc(st, f0, f1, who, dist=2.0, ang=0.0, lens=30, **kw):  # chest-counter close-up
        loc, tgt = chest(*who, dist=dist, ang=ang)
        return sh(st, f0, f1, loc, tgt, lens, dl=tuple((t - l) * 0.15 for l, t in zip(loc, tgt)), **kw)

    def word_frames(i):
        return [S.frame(w[1]) for w in timed[i]["words"]]

    def ticks(keys, i, start, sound=True):
        """The speaker's counter drops by one on every word of line i (starting from `start`)."""
        for k, f in enumerate(word_frames(i)):
            keys[f] = start - 1 - k
            if sound: ctx.sfx("counter", f, 0.5)
        return start - len(word_frames(i))

    # ---------------- counter timelines (frame -> value) ----------------
    me_k = {0: 7211}; ticks(me_k, 11, 7211)
    me_k[L(12)[0]] = 4560; ticks(me_k, 13, 4560)
    a14, b14 = L(14); me_k[a14] = 1337
    for k in range(8): me_k[a14 + 6 + k * (b14 - a14 - 8) // 8] = 1336 - k
    me_k[L(15)[0]] = 902; me_k[L(17)[0]] = 14
    ticks(me_k, 36, 14); ticks(me_k, 39, 4)
    mom_k = {0: 3412}; ticks(mom_k, 19, 3412)
    max_k = {0: 9870}; ticks(max_k, 23, 9870)
    pearl_k = {0: 9000}; ticks(pearl_k, 6, 9000); ticks(pearl_k, 49, 8998)
    gibbs_k = {0: 0, seg(8, "his", "he", "the", "it")[2][0]: 1, wf(8, "fumble"): 0}

    def badge(av, keys): town.counter(av, {f: B(v) for f, v in keys.items()})

    # ======================= TOWN =======================
    tw = Set("town", sun=(48, 0, -35))
    with tw:
        town.sky(tw)
        town.lawn(); town.street(14, length=900)
        types = "abcdefghijklmnopqrstu"
        for k, x in enumerate(range(-240, 241, 40)):
            town.place(f"suburban/building-type-{types[(k * 5) % 21]}", (x, 52, 0), 180)
            town.place(f"suburban/building-type-{types[(k * 7 + 3) % 21]}", (x + 20, -36, 0), 0)
            town.place("suburban/driveway-long", (x + 34, 40, 0.02), 180)
            if abs(x) > 30: town.tree(x + 28, 38, 1.0 + 0.15 * (k % 3), k)
            if x + 6 not in (-54, 94, 54, 6, -34): town.tree(x + 6, -18, 0.85 + 0.1 * (k % 2), k + 40)
            town.place("roads/light-curved", (x + 10, -0.8, 0.3), 0)
        for k in range(-20, 21): town.pine(k * 18 + 7, 100 + (k % 3) * 7, 1.0 + 0.2 * (k % 2), k)
        for k in range(-20, 21): town.pine(k * 18 + 3, -95 - (k % 3) * 7, 1.0 + 0.2 * (k % 2), k + 99)
        town.place("cars/sedan", (52, 9, 0.1), -90); town.place("cars/suv", (-74, 19, 0.1), 90); town.place("cars/hatchback-sports", (130, 9, 0.1), -90)
        for x in (-20, 72): town.place("ph/fire_hydrant", (x, -1.2, 0.3), 0)
        # town sign by the road (opening shot)
        sg = empty("town_sign", (-46, -4.5, 0.3))
        for sx in (-3.2, 3.2): prim("cylY", (0.3, 0.3, 6), (sx, 0, 3), mat((90, 70, 50), 0.7), parent=sg)
        K.plane_image(A + "town_sign.png", (8, 4), (0, -0.2, 5.4), parent=sg)
        prim("box", (8.3, 0.2, 4.3), (0, 0.02, 5.4), mat((90, 70, 50), 0.7), parent=sg)
        # Pearl's porch chair (south lawn, x 60) and Mr. Gibbs's bench (south walk, x -60)
        town.place("furniture/loungeChair", (60, -9, 0), 180)
        town.place("ph/painted_wooden_bench", (-60, -4.6, 0.3), 180)
        # Biscuit's front yard tree (x 100) with the squirrel
        town.tree(94, -14, 1.0, 7)
        dog = toys.cat("biscuit", (170, 110, 60)); dog["root"].scale = (1.3, 1.3, 1.3)
        sq = toys.cat("squirrel", (130, 110, 100)); sq["root"].scale = (0.45, 0.45, 0.45)
        K._key(dog["root"], "location", 0, (106, -9, 0)); K._key(sq["root"], "location", 0, (98, -11, 0))
        # stroller with a baby (line 0: "born with ten thousand words")
        strl = empty("stroller", (-30, -2.4, 0.3)); sm = mat((60, 120, 200), 0.4)
        prim("box", (1.6, 2.2, 1.0), (0, 0, 1.4), sm, parent=strl, bevel=0.2); prim("box", (1.6, 0.9, 1.4), (0, 0.9, 2.2), sm, parent=strl, bevel=0.3)
        for dx in (-0.8, 0.8):
            for dy in (-0.8, 0.8): prim("cyl", (0.2, 0.7, 0.7), (dx, dy, 0.35), mat((30, 30, 30), 0.5), parent=strl)
        # block party (from line 28): tables, banner, speakers, balloons, the ice cream truck
        party = empty("party")
        for k, x in enumerate((-24, -12, 12, 24)):
            t = town.place("furniture/tableCloth", (x, 23, 0.1), 0); t.parent = party
            for j in range(4):
                c = prim("cylY", (0.7, 0.7, 0.4), (x - 1.5 + j, 23, 2.75), mat(random.choice([(240, 200, 120), (230, 120, 90), (250, 240, 220)]), 0.6), parent=party)
        for x in (-14, 14): prim("cylY", (0.4, 0.4, 16), (x, 30, 8), mat((240, 240, 240), 0.5), parent=party)
        K.plane_image(A + "banner.png", (20, 4), (0, 29.8, 13.5), parent=party)
        toys.bunting((-14, 30, 15.8), (14, 30, 15.8), 15.8).parent = party
        spk = []
        for x in (-30, 30):
            s = town.place("furniture/speaker", (x, 26, 0.1), 0, scale=12); s.parent = party; spk.append(s)
        pballs = []
        for k in range(10):
            b = prim("ball", (1.6, 1.6, 1.9), (-26 + k * 5.5, 30.4, 15 + (k % 3)), mat(random.choice([(235, 40, 50), (250, 210, 60), (70, 150, 240), (110, 200, 110)]), 0.2), parent=party)
            pballs.append(b)
        truck = empty("icecream_truck", (-90, 13.5, 0.1)); truck.rotation_euler = (0, 0, math.radians(-90))
        tb = town.place("cars/delivery", (0, 0, 0), 0); tb.parent = truck
        for sx in (-1, 1):
            p = K.plane_image(A + "truck_sign.png", (7, 2.9), (sx * 3.25, 2.4, 4.4), parent=truck); p.rotation_euler = (math.radians(90), 0, math.radians(90 * sx))
        cone = toys.ice_cream(); cone.parent = truck; cone.location = (0, 3, 8.4); cone.scale = (2.4, 2.4, 2.4)
        rl = [prim("box", (1.0, 0.1, 0.5), (sx * 2.2, 6.9, 2.0), mat((255, 255, 255), 0.3, emit=0.0), parent=truck) for sx in (-1, 1)]
        scoops = [prim("ball", (0.9, 0.9, 0.8), (0, 0, 0), mat(random.choice([(255, 190, 210), (250, 240, 200), (140, 90, 60), (180, 230, 170)]), 0.5)) for _ in range(9)]
        # free balloon Max chases
        fb = empty("max_balloon", (0, -300, 0)); prim("ball", (1.5, 1.5, 1.8), (0, 0, 0), mat((235, 40, 50), 0.2), parent=fb)
        prim("cylY", (0.04, 0.04, 3.0), (0, 0, -2.3), mat((250, 250, 250), 0.5), parent=fb)
        # park stage for the mayor (x -300) and the football field for Mr. Gibbs (x 320)
        town.slab((40, 26, 0.6), (-300, -12, 0.0), town.concrete(), "plaza")
        prim("box", (16, 8, 1.6), (-300, -18, 0.8), mat((150, 100, 60), 0.5), bevel=0.1)
        pod = toys.podium(-300, -16.5, 0); pod.location.z = 1.6
        toys.bunting((-308, -21.5, 9), (-292, -21.5, 9), 9)
        cue = [toys.card(A + f"cue_{k}.png", 1.5, 1.0) for k in range(3)]
        town.slab((70, 40, 0.1), (340, -24, 0.0), mat((70, 150, 60), 0.85), "field")
        for x in range(310, 371, 10): town.slab((0.4, 38, 0.02), (x, -24, 0.06), mat((250, 250, 250), 0.5), "yardline")
        for k in range(5): town.slab((60, 3, 1.2 + k * 1.2), (340, -48 - k * 3, (1.2 + k * 1.2) / 2), mat((170, 170, 180), 0.5), "bleacher")
        for sx in (-1.6, 1.6): prim("cylY", (0.3, 0.3, 10), (375 + sx, -24, 5), mat((250, 220, 60), 0.4))
        prim("box", (3.6, 0.3, 0.3), (375, -24, 4), mat((250, 220, 60), 0.4))
        K.plane_image(A + "scoreboard.png", (14, 6), (340, -64, 16)); prim("box", (14.5, 0.6, 6.5), (340, -63.6, 16), mat((40, 40, 45), 0.4))
        ball = prim("ball", (0.6, 0.6, 1.0), (0, -300, 0), mat((130, 70, 40), 0.6))
        # the cast
        me_t = blocky.build(D, "me_t"); idle(me_t); at(me_t, 0, (0, -300, 0), 0)
        max_t = npc("max_t", look("max")); mom_t = npc("mom_t", look("mom")); pearl_t = npc("pearl_t", look("pearl")); glasses(pearl_t)
        hend_t = npc("hend_t", look("hend")); glasses(hend_t); gibbs_t = npc("gibbs_t", look("gibbs")); glasses(gibbs_t)
        mayor_t = npc("mayor_t", look("mayor")); baby = npc("baby", look("baby"))
        pl1 = npc("pl1", look("player1")); pl2 = npc("pl2", look("player2"))
        crowd = []
        for k, (pr, pants, hair, skin) in enumerate(CROWD):
            lk = {"skin": skin, "pants": pants, "hair": hair, "shoes": (40, 40, 45), "shirt": (random.randint(60, 230), random.randint(60, 230), random.randint(60, 230))}
            if pr: lk["shirt_tex"] = A + f"print_{pr}.png"
            crowd.append(npc(f"crowd{k}", lk))
        for av, kk in ((me_t, me_k), (max_t, max_k), (mom_t, mom_k), (pearl_t, pearl_k), (gibbs_t, gibbs_k)): badge(av, kk)
        badge(hend_t, {0: 2316}); badge(mayor_t, {0: 8950}); badge(baby, {0: 10000}); badge(pl1, {0: 6120}); badge(pl2, {0: 7450})
        for av, v in zip(crowd, CROWD_N): badge(av, {0: v})

    # ======================= INSIDE =======================
    ins = Set("inside", sun=(50, 0, -40), sun_energy=3.8)
    with ins:
        town.sky(ins, 1.1, 3.8, (50, 0, -40))
        floor = mat((175, 125, 85), 0.45)
        rooms = {"living": 0, "bath": 40, "dining": 80, "bed": 120, "library": 160, "diner": 200}
        wallc = {"living": (220, 230, 210), "bath": (200, 225, 235), "dining": (240, 225, 200), "bed": (200, 215, 245), "library": (225, 215, 195), "diner": (250, 240, 225)}
        for nm, x in rooms.items():
            prim("box", (30, 22, 0.3), (x, 0, -0.15), floor if nm != "bath" else mat((235, 240, 245), 0.3))
            wm = wall_mat(wallc[nm])
            prim("box", (30, 0.4, 12), (x, 8, 6), wm); prim("box", (0.4, 22, 12), (x - 15, -3, 6), wm); prim("box", (0.4, 22, 12), (x + 15, -3, 6), wm)
            prim("box", (30, 0.3, 0.6), (x, 7.75, 0.3), wall_mat((255, 255, 255)))
            toys.window(x + 8, 7.9, 4.5, 3.8, 5.0, 0, (160, 210, 255))
        # living room: sofa, TV with the game on it
        town.place("furniture/loungeSofa", (0, 5.0, 0), 0)
        town.place("furniture/cabinetTelevision", (0, -7.5, 0), 180); town.place("furniture/televisionModern", (0, -7.5, 2.3), 180)
        K.plane_image(A + "tv_game.png", (4.6, 2.6), (0, -6.9, 4.25), rot=(90, 0, 180), emit=1.2)
        town.place("furniture/rugRectangle", (0, -1, 0.02), 0); town.place("furniture/pottedPlant", (10, 6, 0), 0)
        ctrl = prim("box", (0.9, 0.5, 0.25), (0, 0, 0), mat((30, 30, 35), 0.4), bevel=0.1)
        # bathroom: tiled shower corner, shower head, water, curtain
        prim("box", (10, 0.3, 11), (40, 7.6, 5.5), mat((235, 245, 250), 0.15)); prim("box", (0.3, 8, 11), (35, 4, 5.5), mat((235, 245, 250), 0.15))
        prim("cylY", (0.25, 0.25, 2), (40, 7.0, 9.8), mat((200, 200, 210), 0.2, metal=1.0), rot=(90, 0, 0)); prim("cylY", (1.2, 1.2, 0.3), (40, 6.0, 9.6), mat((200, 200, 210), 0.2, metal=1.0))
        water = []
        for k in range(14):
            w = prim("cylY", (0.05, 0.05, 6.5), (40 + random.uniform(-0.9, 0.9), 6.0 + random.uniform(-0.9, 0.9), 6.2), mat((200, 230, 255), 0.05, alpha=0.35)); water.append(w)
        prim("box", (0.1, 6, 9), (45, 4, 5.5), mat((120, 200, 230), 0.6, alpha=0.85))
        town.place("furniture/bathroomSink", (52, 7.2, 0), 180); town.place("furniture/toilet", (30, 6.5, 0), 180)
        # dining room: table, cake with 11 candles, ketchup
        town.place("furniture/table", (80, 2, 0), 0)
        for x, y, yw in ((80, -1.6, 180), (77.5, 5.6, 0), (82.5, 5.6, 0)): town.place("furniture/chair", (x, y, 0), yw)
        cake = empty("cake", (80, 2, 2.5)); prim("cylY", (2.6, 2.6, 1.0), (0, 0, 0.5), mat((250, 240, 245), 0.5), parent=cake)
        prim("cylY", (2.0, 2.0, 0.6), (0, 0, 1.3), mat((250, 170, 200), 0.5), parent=cake)
        flames = []
        for k in range(11):
            a = k / 11 * math.tau
            prim("cylY", (0.1, 0.1, 0.6), (math.cos(a) * 0.7, math.sin(a) * 0.7, 1.9), mat(random.choice([(120, 180, 250), (250, 220, 90), (240, 120, 160)]), 0.5), parent=cake)
            flames.append(prim("ball", (0.14, 0.14, 0.26), (math.cos(a) * 0.7, math.sin(a) * 0.7, 2.35), mat((255, 200, 80), 0.5, emit=6.0), parent=cake))
        ketchup = empty("ketchup", (81.6, 3.6, 2.5)); prim("cylY", (0.5, 0.5, 1.2), (0, 0, 0.6), mat((210, 30, 30), 0.3), parent=ketchup); prim("cylY", (0.25, 0.25, 0.4), (0, 0, 1.4), mat((240, 240, 240), 0.4), parent=ketchup)
        [prim("cylY", (1.2, 1.2, 0.08), (x, y, 2.55), mat((250, 250, 250), 0.3)) for x, y in ((77.5, 0.6), (82.5, 0.6), (77.5, 3.6), (82.5, 3.6))]
        # bedroom: bed, mirror (the camera stands in for it), desk
        town.place("furniture/bedSingle", (112, 3, 0), 180); town.place("furniture/desk", (128, 6.5, 0), 180)
        mirror = empty("mirror", (120, 7.7, 0)); prim("box", (4.4, 0.3, 7.4), (0, 0, 4.8), mat((150, 110, 70), 0.5), parent=mirror)
        prim("box", (3.9, 0.1, 6.9), (0, -0.2, 4.8), mat((210, 225, 235), 0.02, metal=1.0), parent=mirror)
        # library
        for k, x in enumerate((150, 156, 164, 170)): town.place("furniture/bookcaseOpen", (x, 6.8, 0), 180, scale=8)
        for x in (152, 168):
            for y in (-1, 2): town.place("furniture/bookcaseClosedWide", (x, y, 0), 0, scale=8)
        K.plane_image(A + "library_sign.png", (5, 1.8), (160, 7.75, 9.6))
        town.place("furniture/table", (163, -0.5, 0), 0)
        book = toys.box_prop(A + "book_cover.png", 1.2, 0.3, 1.6, (40, 110, 180)); book.location = (163, -0.5, 2.5)
        # diner: counter, stools, menu board, pancakes, syrup
        for x in range(188, 214, 3): town.place("furniture/kitchenBar", (x, 3.0, 0), 180, scale=7.5)
        for x in (192, 198, 204, 210): town.place("furniture/stoolBar", (x, 0.2, 0), 0)
        K.plane_image(A + "menu.png", (7.5, 5), (200, 7.75, 7.2)); K.plane_image(A + "diner_sign.png", (5.4, 2.0), (200, 7.75, 10.9))
        pancakes = empty("pancakes", (198, 2.6, 3.15)); prim("cylY", (1.4, 1.4, 0.08), (0, 0, 0), mat((250, 250, 250), 0.3), parent=pancakes)
        for k in range(3): prim("cylY", (1.0, 1.0, 0.16), (0, 0, 0.12 + k * 0.17), mat((220, 160, 80), 0.6), parent=pancakes)
        syrup = empty("syrup", (199.6, 2.8, 3.15)); prim("cylY", (0.45, 0.45, 1.1), (0, 0, 0.55), mat((150, 70, 20), 0.2, alpha=0.9), parent=syrup)
        prim("cylY", (0.2, 0.2, 0.4), (0, 0, 1.3), mat((220, 40, 40), 0.4), parent=syrup)
        me_i = blocky.build(D, "me_i"); idle(me_i); at(me_i, 0, (0, -300, 0), 0)
        max_i = npc("max_i", look("max")); mom_i = npc("mom_i", look("mom"))
        hend_i = npc("hend_i", look("hend")); glasses(hend_i); wait_i = npc("waitress", look("waitress"))
        for av, kk in ((me_i, me_k), (max_i, max_k), (mom_i, mom_k)): badge(av, kk)
        badge(hend_i, {0: 2316}); badge(wait_i, {0: 5870})

    H, HK = 4.6, 3.05  # head height of an adult / of Max (scale 0.62) standing on the floor
    W = 0.3  # sidewalk top

    # ======================= 0-2: the rule =======================
    (a, s1), (_, s2), (_, s3), (_, b) = seg(0, "everyone", "when", "forever")
    for k, av in enumerate(crowd[:6]):
        walk(av, a - 10, s2 + 30, (-40 + k * 7, -1.0 - (k % 2) * 2.5, W), (-40 + k * 7, -5.0 - (k % 2) * 2.5, W), 12, 20)
    at(mom_t, a, (-33, -2.0, W), 0)
    at(baby, a, (-31.5, -3.4, W), 0); react(baby, "happy", a)
    sh(tw, a, s1, (-58, -26, 22), (-38, 10, 4), 20, dl=(6, 8, -8)); ctx.sfx("whoosh", a + 2, 0.5)
    shc(tw, s1, s2, ((-31.5, -3.4), 0, 1.93 + W + 0.9), 1.5, 0, lens=26, pz=wf(0, "thousand"), amount=1.2); ctx.sfx("sparkle", wf(0, "ten"), 0.5)
    at(gibbs_t, s2, (-60, -4.2, W), 0); sit(gibbs_t, s2, 1.65, (-60, -4.4), 0, ease=1); react(gibbs_t, "sad", s2)
    shc(tw, s2, s3, ((-60, -4.4), 0, 4.7), 2.0, 0, lens=26, pz=wf(0, "zero"), amount=1.25); ctx.sfx("counter", wf(0, "zero"), 0.8)
    react(gibbs_t, "blank", s3)
    shf(tw, s3, b, ((-60, -4.4), 0, 4.7), 2.4, 10, pz=s3 + 3, amount=1.2); ctx.sfx("scared", s3 + 2, 0.4)
    # 1: "The number glows right on your chest, so everyone knows exactly how much you've got left."
    (a, s1), (_, b) = seg(1, "so")
    at(hend_t, a, (-6, -2.5, W), (-11, -2.5)); at(crowd[6], a, (-11, -2.5, W), (-6, -2.5)); react(hend_t, "suspicious", s1); react(crowd[6], "suspicious", s1 + 4)
    shc(tw, a, s1, ((-6, -2.5), (-11, -2.5), H + W), 2.2, 0, lens=28)
    pose(hend_t, s1, 6, head=(-18, 0, 0)); pose(crowd[6], s1 + 4, 6, head=(-18, 0, 0))
    sh(tw, s1, b, (-8.5, -11, 4.6), (-8.5, -2.5, 3.8), 24, dl=(0, 1.5, 0)); ctx.sfx("pop", s1 + 3, 0.3)
    rest(hend_t, b, "head"); rest(crowd[6], b, "head")
    # 2: "So nobody here talks much."
    a, b = L(2)
    for k, av in enumerate(crowd[6:12]):
        at(av, a, (-14 + k * 5, 30.5 + (k % 2) * 2, W), 0 if k % 2 else 180); react(av, "blank", a)
    pose(crowd[7], a + 6, 6, ra=(-160, 0, 20)); rest(crowd[7], b, "ra")
    sh(tw, a, b, (-2, 17, 4.4), (-2, 31, 4.6), 22, dl=(0, 2, 0)); ctx.sfx("crickets", a, 0.6)

    # ======================= 3: the diner =======================
    (a, s1), (_, s2), (_, s3), (_, s4), (_, b) = seg(3, "pancakes", "syrup", "the", "she's")
    sit(hend_i, a, 3.3, (198, 0.2), 180, ease=1); at(wait_i, a, (200, 5.6, 0), 0); react(hend_i, "blank", a); react(wait_i, "smile", a)
    sh(ins, a, s1, (190, -9, 6.5), (199, 3, 4.0), 22, dl=(2, 2, -1)); ctx.sfx("bell", a, 0.2)
    pose(hend_i, s1, 4, ra=(-95, 0, -10)); react(hend_i, "determined", s1)
    sh(ins, s1, s2, (201.5, -0.8, 6.8), (199.5, 7.7, 7.6), 26, dl=(0, 0.6, 0)); ctx.sfx("pop", s1 + 2, 0.4)
    sh(ins, s2, s3, (201.5, -0.8, 4.4), (199.6, 2.8, 3.6), 30, pz=s2 + 3, amount=1.2); ctx.sfx("pop", s2 + 2, 0.4)
    pose(hend_i, s3, 4, ra=(-80, 0, 0)); react(wait_i, "love", s3 + 4)
    shf(ins, s3, s4, ((200, 5.6), 0, H), 4.2, 15, lens=26); ctx.sfx("boing", s3 + 3, 0.4)
    react(hend_i, "love", s4); rest(hend_i, s4, "ra")
    sh(ins, s4, b, (192, 6.2, 6.5), (199, 1.5, 5.6), 24, dl=(0.6, -0.4, 0)); ctx.sfx("sparkle", s4 + 4, 0.5)

    # ======================= 4: the mayor's cue cards =======================
    (a, s1), (_, s2), (_, b) = seg(4, "forty", "the")
    at(mayor_t, a, (-300, -18.8, 1.6), 180); react(mayor_t, "smile", a)
    for k, av in enumerate(crowd[:8]):
        at(av, a, (-306 + (k % 4) * 4, -8 + (k // 4) * 3.5, 0.3), (-300, -18)); react(av, "blank", a)
    for k, c in enumerate(cue): hold(mayor_t, c, "ra", (0, -0.4, 0.3), (0, 0, 0)); show_between(c, [a, s1, s2][k], [s1, s2, b][k])
    pose(mayor_t, a, 1, ra=(-108, 0, 0))
    sh(tw, a, s1, (-289, 0, 8.5), (-300, -18, 5.6), 24, dl=(-1, -1.5, 0)); ctx.sfx("rustle", a + 2, 0.5)
    sh(tw, s1, s2, (-300, -14.5, 6.5), (-300, -18, 5.8), 30, dl=(0, -0.5, 0)); ctx.sfx("rustle", s1 + 2, 0.6); ctx.sfx("rustle", s1 + 8, 0.6)
    react(mayor_t, "happy", s2 + 4); pose(mayor_t, s2, 4, ra=(-95, 0, 0))
    c = sh(tw, s2, b, (-300, -14.0, 6.6), (-300, -18.2, 6.4), 34, pz=wf(4, "thanks"), amount=1.25); ctx.sfx("ding", wf(4, "thanks"), 0.5)
    rest(mayor_t, b, "ra")

    # ======================= 5-7: Grandma Pearl =======================
    (a, s1), (_, b) = seg(5, "she")
    sit(pearl_t, a, 1.7, (60, -9.2), 180, ease=1); react(pearl_t, "smug", a)
    PEARL = ((60, -9.2), 180, 4.75)
    sh(tw, a, a + (s1 - a) // 2, (56, 2, 5.0), (60, -9, 4.0), 22, dl=(1, -2, 0))
    shc(tw, a + (s1 - a) // 2, s1, PEARL, 1.9, 0, lens=28, pz=wf(5, "saved"), amount=1.15); ctx.sfx("sparkle", wf(5, "nine"), 0.4)
    react(pearl_t, "happy", s1)
    shf(tw, s1, b, PEARL, 3.0, -20); ctx.sfx("pop", s1 + 4, 0.3)
    a, b = L(6); kit.speak(pearl_t, 6); react(pearl_t, "smug", a); pose(pearl_t, a, 4, ra=(-100, 0, 20))
    shf(tw, a, b, PEARL, 2.2, 10, pz=a + 2, amount=1.2); ctx.sfx("boing", b - 2, 0.4)
    rest(pearl_t, b, "ra")
    a, b = L(7); react(pearl_t, "smile", a)
    sh(tw, a, b, (66, 1, 7.0), (60, -9, 4.0), 22, dl=(-2, -1, -1)); ctx.sfx("crickets", a, 0.5)

    # ======================= 8: Mr. Gibbs =======================
    (a, s1), (_, s2), (_, s3), (_, s4), (_, b) = seg(8, "his", "he", "the", "it")
    GB = ((-60, -4.4), 0, 4.7)
    react(gibbs_t, "sad", a)
    sh(tw, a, s1, (-54, -14, 4.8), (-60, -4.4, 3.8), 24, dl=(-1, 1, 0)); ctx.sfx("crickets", a, 0.3)
    shc(tw, s1, s2, GB, 1.8, -10, lens=28, pz=wf(8, "zero"), amount=1.25); ctx.sfx("counter", wf(8, "zero"), 0.8)
    # flashback: the football game
    at(gibbs_t, s2, (330, -50.5, 2.4), 0); sit(gibbs_t, s2, 2.4, (330, -50.5), 0, ease=1); react(gibbs_t, "determined", s2)
    at(pl1, s2, (338, -22, 0.1), 0); at(pl2, s2, (342, -20, 0.1), 180); hold(pl1, ball, "ra", (0, -0.5, 0)); pose(pl1, s2, 1, ra=(-90, 0, 0))
    sh(tw, s2, s3, (348, -8, 8), (332, -48, 4), 22, dl=(-2, -1, 0), look="flashback"); ctx.sfx("cheer", s2, 0.5)
    at(gibbs_t, s3, (330, -50.5, 2.4), 0, ease=1); rest(gibbs_t, s3, "ll", "rl", "ll_knee", "rl_knee", ease=4); react(gibbs_t, "scream", s3)
    pose(gibbs_t, s3, 4, ra=(-170, 0, 20), la=(-170, 0, -20))
    c = shf(tw, s3, s4, ((330, -50.5), 0, H + 2.4), 3.0, -15, look="flashback", pz=wf(8, "fumble"), amount=1.3); shake(c, wf(8, "fumble"), 10, 0.3)
    ctx.sfx("counter", wf(8, "fumble"), 0.8); ctx.sfx("gasp", wf(8, "fumble") + 3, 0.5)
    pose(pl1, s4, 4, ra=(-170, 0, 0)); react(pl1, "smug", s4); react(gibbs_t, "embarrassed", s4 + 6); rest(gibbs_t, s4 + 6, "ra", "la")
    sh(tw, s4, b, (344, -14, 4.6), (339, -22, 5.6), 26, dl=(0.4, 0.4, 0), look="flashback"); ctx.sfx("ding", s4 + 4, 0.4)

    # ======================= 9-16: how I wasted mine =======================
    a, b = L(9)
    walk(me_t, a - 4, b + 6, (2, -2.2, W), (2, -6.0, W), 9, 22); react(me_t, "grin", a)
    sh(tw, a, b, (2, -14, 4.4), (2, -3, 4.3), 26, dl=(0, 1.4, 0)); ctx.sfx("pop", a + 2, 0.4)
    pose(me_t, b - 6, 4, ra=(-160, 0, 25)); rest(me_t, b + 4, "ra")
    # 10-11: video games
    (a, s1), (_, b) = seg(10, "out")
    sit(me_i, a, 1.75, (0, 4.6), 0, ease=1); react(me_i, "happy", a); hold(me_i, ctrl, "ra", (0.3, -0.4, 0.1)); pose(me_i, a, 1, ra=(-60, 0, -25), la=(-60, 0, 25))
    sh(ins, a, s1, (6, -5.5, 4.6), (0, 3.5, 3.6), 22, dl=(-1, 1, 0)); ctx.sfx("blip", a + 2, 0.5)
    sh(ins, s1, b, (0, 0.8, 4.4), (0, -7.0, 4.25), 26, pz=s1 + 2, amount=1.15); ctx.sfx("blip", s1, 0.4)
    a, b = L(11); kit.speak(me_i, 11); react(me_i, "laugh", a); react(me_i, "shock", wf(11, "oh"))
    shf(ins, a, wf(11, "oh"), ((0, 4.6), 0, 4.8), 2.6, 15, pz=a + 2, amount=1.15)
    c = shc(ins, wf(11, "oh"), b, ((0, 4.6), 0, 4.8), 1.9, 0, lens=28); ctx.sfx("boing", wf(11, "missed"), 0.5)
    rest(me_i, b, "ra", "la")
    # 12-13: Biscuit and the squirrel
    (a, s1), (_, b) = seg(12, "every")
    at(me_t, a, (101, -6.5, 0), 90); react(me_t, "happy", a)
    K._key(dog["root"], "location", a, (106, -9, 0), 1); K._key(dog["root"], "location", b, (96, -12.5, 0))
    dog["root"].rotation_euler = (0, 0, math.radians(-60)); dog["root"].keyframe_insert("rotation_euler", frame=a)
    K._key(sq["root"], "location", a, (98, -11, 0), 1); K._key(sq["root"], "location", s1 + 8, (94.6, -13.4, 0.2)); K._key(sq["root"], "location", s1 + 22, (94.6, -13.4, 9.0))
    sh(tw, a, s1, (110, 2, 5.0), (100, -10, 3.0), 22, dl=(-2, -1, 0)); ctx.sfx("bark", a + 3, 0.6)
    sh(tw, s1, b, (101, -1.5, 3.0), (95, -13, 5.0), 22, dt=(0, 0, 3)); ctx.sfx("bark", s1 + 4, 0.6); ctx.sfx("whoosh", s1 + 8, 0.4)
    a, b = L(13); kit.speak(me_t, 13); react(me_t, "starstruck", a); pose(me_t, a, 4, ra=(-110, 0, 20))
    K._key(dog["root"], "location", a, (96, -12.5, 0), 1); K._key(dog["root"], "location", a + 8, (96, -12.5, 1.6)); K._key(dog["root"], "location", a + 16, (96, -12.5, 0))
    shf(tw, a, wf(13, "he's"), ((101, -6.5), 90, H), 2.8, 25); ctx.sfx("bark", a + 6, 0.5)
    sh(tw, wf(13, "he's"), wf(13, "biscuit"), (100, -4, 2.2), (95, -13, 8.0), 20, dt=(0, 0, 1.5)); ctx.sfx("tweet", wf(13, "he's") + 4, 0.4)
    react(me_t, "sad", wf(13, "biscuit"))
    shf(tw, wf(13, "biscuit"), b, ((101, -6.5), 90, H), 2.2, 0, pz=wf(13, "again"), amount=1.15); ctx.sfx("sad", wf(13, "again"), 0.4)
    rest(me_t, b, "ra")
    # 14: the shower
    (a, s1), (_, s2), (_, b) = seg(14, "every", "both")
    at(me_i, a, (40, 4.6, 0), 0); rest(me_i, a, ease=1); react(me_i, "laugh", a)
    for w in water: show_between(w, a - 1, b + 1)
    for k in range(0, b - a, 8): pose(me_i, a + k, 4, head=(0, 0, 10 if (k // 8) % 2 else -10), ra=(-120 if (k // 8) % 2 else -100, 0, 20))
    sh(ins, a, s1, (44, -4.5, 5.2), (40, 4.6, 4.4), 26, dl=(-1, 1, 0)); ctx.sfx("shower", a, 0.5)
    react(me_i, "happy", s1); shc(ins, s1, s2, ((40, 4.6), 0, H), 1.9, 10, lens=28); ctx.sfx("shower", s1, 0.3)
    react(me_i, "grin", s2); pose(me_i, s2, 4, ra=(-160, 0, 20), la=(-160, 0, -20))
    shf(ins, s2, b, ((40, 4.6), 0, H), 2.4, -20, pz=s2 + 2, amount=1.15); ctx.sfx("boing", s2 + 3, 0.4)
    rest(me_i, b + 2, "ra", "la", "head")
    # 15-16
    a, b = L(15); at(me_t, a, (2, -3.0, W), 0); react(me_t, "smug", a); pose(me_t, a, 4, la=(-20, 0, -40), ra=(-20, 0, 40))
    shf(tw, a, b, ((2, -3.0), 0, H + W), 3.0, -15, pz=wf(15, "infinity"), amount=1.15); ctx.sfx("sparkle", wf(15, "infinity"), 0.4)
    a, b = L(16); react(me_t, "blank", a); rest(me_t, a, "la", "ra", ease=1)
    shc(tw, a, b, ((2, -3.0), 0, H + W), 1.8, 0, lens=30); ctx.sfx("crickets", a, 0.6)

    # ======================= 17-21: the birthday =======================
    (a, s1), (_, s2), (_, b) = seg(17, "i", "and")
    sit(me_i, a, 1.6, (80, -1.0), 180, ease=1); react(me_i, "happy", a)
    sit(max_i, a, 1.6, (82.5, 5.2), 0, ease=1); react(max_i, "happy", a); at(mom_i, a, (85.2, 2.0, 0), 90); react(mom_i, "happy", a)
    sh(ins, a, s1, (86, -8, 6.5), (80, 2.5, 3.6), 22, dl=(-1, 1.5, 0)); ctx.sfx("clap", a, 0.5)
    pose(me_i, s1, 4, waist=(12, 0, 0)); ctx.sfx("whoosh", s1 + 4, 0.7)
    for fl in flames: K._key(fl, "scale", s1 + 6, (0.14, 0.14, 0.26), 1); K._key(fl, "scale", s1 + 8, (0.001, 0.001, 0.001))
    sh(ins, s1, s2, (80, 5.4, 6.4), (80, -1.0, 4.4), 28, dl=(0, -0.6, 0)); ctx.sfx("pop", s2 - 6, 0.3)
    rest(me_i, s2, "waist"); pose(me_i, s2 + 2, 6, head=(-28, 0, 0)); react(me_i, "confused", s2)
    shf(ins, s2, b, ((80, -1.0), 180, 4.65), 2.6, 15)
    a, b = L(18); react(me_i, "terrified", a)
    c = shc(ins, a, b, ((80, -1.0), 180, 4.65), 1.5, 0, lens=34, pz=a + 2, amount=1.3); shake(c, a + 2, 8, 0.25)
    ctx.sfx("scared", a, 0.7)
    # 19: Mom
    a, b = L(19); kit.speak(mom_i, 19); react(mom_i, "scream", a); react(mom_i, "furious", wf(19, "what"), b + 10)
    rest(me_i, a, "head", ease=3)
    c = shf(ins, a, wf(19, "what"), ((85.2, 2.0), 90, H), 2.6, 0, lens=24, pz=a + 2, amount=1.3); shake(c, a + 2, 12, 0.35)
    pose(mom_i, wf(19, "what"), 4, ra=(-120, 0, 30), la=(-120, 0, -30))
    shf(ins, wf(19, "what"), b, ((85.2, 2.0), 90, H), 3.4, 30, lens=22)
    rest(mom_i, b + 2, "ra", "la")
    (a, s1), (_, b) = seg(20, "she")
    shc(ins, a, s1, ((85.2, 2.0), 90, H), 1.9, 0, lens=28); ctx.sfx("counter", a, 0.5)
    react(mom_i, "angry", s1)
    shf(ins, s1, b, ((85.2, 2.0), 90, H), 2.4, -15); ctx.sfx("angry", s1 + 2, 0.4)
    # 21: stopped talking - a little montage
    (a, s1), (_, s2), (_, s3), (_, b) = seg(21, "no", ("no", 1), "not")
    at(me_t, a, (2, -3.0, W), 0); react(me_t, "determined", a); pose(me_t, a + 2, 4, ra=(-130, 0, -40))
    shf(tw, a, s1, ((2, -3.0), 0, H + W), 2.4, 0, pz=a + 4, amount=1.15); ctx.sfx("pop", a + 6, 0.4)
    rest(me_t, s1, "ra", ease=1)
    at(mom_t, s1, (8, -2.5, W), -90); pose(mom_t, s1, 4, ra=(-160, 0, 20)); react(mom_t, "happy", s1); react(me_t, "nervous", s1 + 4)
    sh(tw, s1, s2, (5, -11, 4.6), (5, -2.6, 4.2), 26, dl=(0, 1, 0)); ctx.sfx("tweet", s1, 0.3)
    rest(mom_t, s2, "ra")
    at(hend_t, s2, (-2, -2.5, W), 90); pose(hend_t, s2, 4, ra=(-80, 0, 0)); react(hend_t, "smile", s2); nod(me_t, s2 + 4, 1, 12)
    sh(tw, s2, s3, (0, -10, 4.4), (0, -2.8, 4.2), 26, dl=(0, 1, 0)); ctx.sfx("pop", s2 + 3, 0.3)
    rest(hend_t, s3, "ra"); react(hend_t, "blank", s3)
    pose(hend_t, s3, 3, head=(25, 0, 0)); pose(hend_t, s3 + 6, 3, head=(-15, 0, 0)); rest(hend_t, s3 + 12, "head", ease=4)
    react(me_t, "nervous", s3 + 8)
    shf(tw, s3, b, ((2, -3.0), 0, H + W), 2.4, 30); ctx.sfx("gasp", s3 + 4, 0.4); ctx.sfx("crickets", s3 + 10, 0.4)
    at(hend_t, b, (0, -300, 0)); at(mom_t, b, (0, -300, 0))

    # ======================= 22-24: the ketchup =======================
    (a, s1), (_, b) = seg(22, "my")
    react(me_i, "blank", a); react(max_i, "happy", a); at(mom_i, a, (0, -300, 0)); show_between(cake, 0, a)
    sh(ins, a, s1, (88, -6, 6.5), (80, 2.5, 3.6), 22, dl=(-1, 1, 0)); ctx.sfx("chew", a, 0.4)
    shf(ins, s1, b, ((82.5, 5.2), 0, 3.5), 2.6, 10, lens=26)
    a, b = L(23); kit.speak(max_i, 23); react(max_i, "smile", a); pose(max_i, a, 4, ra=(-80, 0, 0))
    shf(ins, a, b, ((82.5, 5.2), 0, 3.5), 2.2, -10, pz=wf(23, "ketchup"), amount=1.15); ctx.sfx("pop", wf(23, "ketchup"), 0.3)
    rest(max_i, b, "ra")
    (a, s1), (_, b) = seg(24, ("i", 1))
    react(me_i, "blank", a)
    shf(ins, a, s1, ((80, -1.0), 180, 4.65), 3.0, 0, lens=28, pz=a + 2, amount=1.2); ctx.sfx("crickets", a, 0.5)
    react(me_i, "worried", s1); react(max_i, "confused", s1)
    sh(ins, s1, b, (73, 2.0, 4.4), (81, 2.0, 3.6), 24, dl=(1, 0, 0)); ctx.sfx("sad", s1 + 4, 0.3)

    # ======================= 25-27: sign language =======================
    (a, s1), (_, b) = seg(25, "i")
    walk(me_i, a - 4, a + (s1 - a) // 2, (159, -9, 0), (159, -3.0, 0), 9, 22); react(me_i, "determined", a)
    sh(ins, a, a + (s1 - a) // 2, (160, -11, 5.0), (160, 3, 4.0), 22, dl=(0, 1.5, 0)); ctx.sfx("step", a + 3, 0.4)
    sh(ins, a + (s1 - a) // 2, s1, (163.3, -3.8, 3.6), (163, -0.5, 3.3), 30, dl=(0, 0.8, 0)); ctx.sfx("pop", a + (s1 - a) // 2 + 2, 0.5)
    at(me_i, s1, (120, 2.0, 0), 180); rest(me_i, s1, ease=1); react(me_i, "determined", s1)
    sh(ins, s1, b, (123.5, -6, 5.2), (120, 4, 4.4), 24, dl=(-0.5, 1, 0)); ctx.sfx("rustle", s1 + 2, 0.4)
    # 26: Hello. Thank you. Help. And Max's favorite sign: freeze.  (camera = the mirror)
    (a, s1), (_, s2), (_, s3), (_, b) = seg(26, "thank", "help", "and")
    M = ((120, 2.0), 180, H)
    react(me_i, "happy", a); [pose(me_i, a + k * 4, 2, ra=(-165, 0, 20 + (15 if k % 2 else -15))) for k in range(4)]
    shf(ins, a, s1, M, 3.2, 0, lens=26)
    react(me_i, "smile", s1); pose(me_i, s1, 3, ra=(-120, 0, -35)); pose(me_i, s1 + 7, 4, ra=(-70, 0, 0))
    shf(ins, s1, s2, M, 3.0, 12); ctx.sfx("pop", s1 + 2, 0.3)
    react(me_i, "worried", s2); pose(me_i, s2, 3, ra=(-80, 0, -10), la=(-95, 0, 10))
    shf(ins, s2, s3, M, 3.0, -12); ctx.sfx("pop", s2 + 2, 0.3)
    rest(me_i, s3, "ra", "la", ease=3); react(me_i, "determined", s3)
    freeze_at = wf(26, "freeze")
    pose(me_i, freeze_at, 3, ra=(-90, 0, -28), la=(-90, 0, 28))
    shf(ins, s3, b, M, 2.6, 0, pz=freeze_at, amount=1.25); ctx.sfx("freeze", freeze_at, 0.6)
    # 27: the freeze game
    (a, s1), (_, s2), (_, b) = seg(27, "when", "max")
    at(me_i, a, (-5, -2, 0), (2, -2)); rest(me_i, a, ease=1); react(me_i, "smile", a)
    walk(max_i, a, s1 + 4, (8, 0, 0), (2, -2, 0), 6, 30); react(max_i, "laugh", a)
    sh(ins, a, s1, (9, -6, 5.0), (0, -1.5, 3.4), 22, dl=(-0.6, 0.4, 0)); ctx.sfx("giggle", a + 2, 0.5)
    pose(me_i, s1 + 2, 3, ra=(-90, 0, -28), la=(-90, 0, 28))
    f_frz = s1 + 6; at(max_i, f_frz, (2, -2, 0), (-5, -2), ease=1); react(max_i, "determined", f_frz)
    pose(max_i, f_frz, 1, ll=(-35, 0, 0), rl=(25, 0, 0), la=(-60, 0, -20), ra=(40, 0, 20), ll_knee=(0, 0, 0), rl_knee=(0, 0, 0))
    sh(ins, s1, s2, (2.5, -7.5, 2.8), (2, -2, 2.4), 26, pz=f_frz, amount=1.2); ctx.sfx("freeze", f_frz, 0.6)
    rest(me_i, s2, "ra", "la"); react(max_i, "smug", s2)
    shf(ins, s2, b, ((2, -2), (-5, -2), HK), 2.2, 10); ctx.sfx("ding", s2 + 4, 0.5)
    rest(max_i, b, ease=4)

    # ======================= 28-34: the block party =======================
    a, b = L(28)
    guests = [(-26, 24.5), (-21, 25), (-10, 25.5), (-14, 21.3), (10, 25), (14, 21.3), (22, 25.5), (26, 21.3), (-6, 31), (4, 31.5), (18, 31), (-30, 21.3)]
    for k, (av, (x, y)) in enumerate(zip(crowd, guests)): at(av, a, (x, y, 0.1 if y < 27 else W), (x, 14) if y < 27 else 180); react(av, "smile", a)
    at(hend_t, a, (-18, 26, 0.1), 180); at(pearl_t, a, (6, 26, 0.1), 180); at(mom_t, a, (-3, 26.5, 0.1), 180); at(gibbs_t, a, (20, 26.5, 0.1), 180)
    at(mayor_t, a, (28, 26.5, 0.1), 180); at(baby, a, (0, -300, 0))
    for av in (hend_t, pearl_t, mom_t, gibbs_t, mayor_t): rest(av, a, ease=1); react(av, "smile", a)
    at(me_t, a, (-8, 25.5, 0.1), 180); at(max_t, a, (-1, 21.5, 0.1), 180); react(me_t, "happy", a); react(max_t, "happy", a)
    sh(tw, a, b, (-6, -14, 16), (0, 24, 6), 22, dl=(2, 4, -6)); ctx.sfx("cheer", a, 0.5); ctx.sfx("jingle", a + 6, 0.35)
    (a, s1), (_, s2), (_, b) = seg(29, "nobody", "just")
    sh(tw, a, s1, (-28, 6, 5.0), (-10, 24, 4.0), 22, dl=(3, 1, 0))
    for av in crowd + [hend_t, pearl_t, mom_t, gibbs_t, mayor_t]: react(av, "blank", s1)
    sh(tw, s1, s2, (12, 10, 4.6), (14, 23, 4.2), 26, dl=(-1, 1, 0)); ctx.sfx("crickets", s1, 0.6)
    for k, av in enumerate(crowd[:4]):
        for j in range(0, b - s2, 6): pose(av, s2 + j, 2, head=(8 if (j // 6 + k) % 2 else -4, 0, 0))
    shf(tw, s2, b, ((10, 25), (10, 14), H + 0.1), 2.6, 0); ctx.sfx("chew", s2, 0.8)
    # 30: Max chases the balloon into the street
    a, b = L(30)
    K._key(fb, "location", a, (1.0, 19.0, 6.0), 1); K._key(fb, "location", b + 30, (1.0, 6.0, 11.0))
    walk(max_t, a, b + 6, (-1, 21.5, 0.1), (0, 9.6, 0.1), 5, 34); react(max_t, "starstruck", a)
    kit.follow(tw, a, b, max_t["root"], (5.5, -7, 3.2), (0, 0, 2.2), 24); ctx.sfx("step", a + 4, 0.4); ctx.sfx("step", a + 10, 0.4)
    # 31: the truck backs up
    (a, s1), (_, b) = seg(31, "beep")
    at(max_t, a, (0, 9.6, 0.1), 180); pose(max_t, a, 3, ra=(-170, 0, 10)); react(max_t, "happy", a)
    K._key(truck, "location", a, (-70, 13.5, 0.1), 1); K._key(truck, "location", L(44)[0], (-14, 13.5, 0.1))
    for fc in truck.animation_data.action.fcurves:
        for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
    for r_ in rl: show_between(r_, a)
    sh(tw, a, s1, (-40, 4, 3.2), (-62, 13.5, 4.0), 24, dt=(4, 0, 0)); ctx.sfx("rev", a, 0.3)
    sh(tw, s1, b, (-32, 20, 2.8), (-50, 13.5, 3.6), 22, dt=(4, 0, 0)); ctx.sfx("beep", s1, 0.9)
    # 32
    (a, s1), (_, b) = seg(32, "max")
    sh(tw, a, s1, (-58, 11, 10.5), (0, 9.6, 2.0), 24, dl=(3, 0, 0)); ctx.sfx("beep", a, 0.7)
    for s_ in spk: s_.keyframe_insert("scale", frame=s1); s_.scale = (13, 13, 13); s_.keyframe_insert("scale", frame=s1 + 3); s_.scale = (12, 12, 12); s_.keyframe_insert("scale", frame=s1 + 6)
    sh(tw, s1, b, (-37, 18, 4.0), (-30, 26, 3.2), 26, pz=s1 + 2, amount=1.15); ctx.sfx("jingle", s1, 0.5)
    # 33: fifty people saw it
    (a, s1), (_, s2), (_, b) = seg(33, ("fifty", 1), "nobody")
    for av in crowd + [hend_t, pearl_t, gibbs_t, mayor_t]: react(av, "shock", a)
    sh(tw, a, s1, (0, 15, 3.4), (0, 26, 4.4), 20, dl=(0, 2, 0)); ctx.sfx("gasp", a, 0.6)
    sh(tw, s1, s2, (-26, 16.5, 3.6), (-26, 24, 3.4), 26, dl=(30, 0, 0), dt=(30, 0, 0)); ctx.sfx("counter", s1, 0.3)
    for av in crowd + [hend_t, pearl_t, gibbs_t, mayor_t]: react(av, "nervous", s2)
    sh(tw, s2, b, (8, 12, 5.0), (8, 26, 4.4), 24, dl=(0, 1, 0)); ctx.sfx("crickets", s2, 0.6)
    # 34
    (a, s1), (_, s2), (_, b) = seg(34, "grandma", "then")
    pose(hend_t, a, 3, ra=(-90, 0, 30)); react(hend_t, "shock", a)
    shf(tw, a, s1, ((-18, 26), 180, H + 0.1), 3.0, 20); ctx.sfx("pop", a + 2, 0.3)
    react(pearl_t, "scream", s1)
    shf(tw, s1, s2, ((6, 26), 180, H + 0.1), 2.4, 0, pz=s1 + 2, amount=1.15); ctx.sfx("gasp", s1 + 2, 0.4)
    react(pearl_t, "nervous", s2)
    shf(tw, s2, b, ((6, 26), 180, H + 0.1), 2.2, 10); ctx.sfx("crickets", s2 + 2, 0.5)

    # ======================= 35-40: I ran and I yelled =======================
    (a, s1), (_, b) = seg(35, "and")
    react(me_t, "determined", a)
    walk(me_t, a, L(36)[0] + 12, (-8, 25.5, 0.1), (-1, 18.0, 0.1), 4, 40); at(me_t, L(36)[0] + 13, (-1, 18.0, 0.1), (0, 9.6), ease=3)
    kit.follow(tw, a, s1, me_t["root"], (0, -6.5, 4.2), (0, 0, 3.8), 24); ctx.sfx("whoosh", a, 0.6)
    react(me_t, "scream", s1)
    sh(tw, s1, b, (-1.5, 13.5, 3.6), (-5, 22, 4.4), 24, dl=(0, 0.8, 0), pz=s1 + 2, amount=1.15)
    # 36: Max! Stop! Truck! Behind you! Max! Move! Please! Max! Max!  (big countdown 13 .. 4)
    a, b = L(36); kit.speak(me_t, 36); react(me_t, "scream", a)
    wfr = word_frames(36)
    for k, f in enumerate(wfr): ctx.overlay(f"count_{13 - k}.png", f, wfr[k + 1] if k + 1 < len(wfr) else b)
    cuts = [a, wfr[2] - 1, wfr[5] - 1, wfr[7] - 1, b]
    kit.follow(tw, cuts[0], cuts[1], me_t["root"], (-1.5, -5.0, 4.4), (0, 0, 4.2), 24)
    sh(tw, cuts[1], cuts[2], (6, 3.0, 2.2), (-24, 13.5, 4.0), 22, dt=(6, 0, 0)); ctx.sfx("beep", cuts[1], 0.6)
    react(max_t, "happy", cuts[2]); c = sh(tw, cuts[2], cuts[3], (-1.5, 13.0, 4.0), (0, 9.6, 3.2), 24, dl=(0, -0.6, 0)); ctx.sfx("jingle", cuts[2], 0.4)
    c = shf(tw, cuts[3], cuts[4], ((-1, 18.0), (0, 9.6), H + 0.1), 2.2, 10, lens=26); shake(c, cuts[3] + 2, 10, 0.25)
    # 37
    (a, s1), (_, s2), (_, b) = seg(37, "he", "the")
    shc(tw, a, s1, ((-1, 18.0), (0, 9.6), H + 0.1), 1.8, 0, lens=30); ctx.sfx("heartbeat", a, 0.5)
    sh(tw, s1, s2, (0, 3.5, 4.0), (0, 9.6, 3.0), 24, dl=(0, 0.8, 0)); ctx.sfx("beep", s1, 0.8)
    for s_ in spk: s_.keyframe_insert("scale", frame=s2); s_.scale = (13, 13, 13); s_.keyframe_insert("scale", frame=s2 + 3); s_.scale = (12, 12, 12); s_.keyframe_insert("scale", frame=s2 + 6)
    sh(tw, s2, b, (37, 18, 4.0), (30, 26, 3.2), 26, pz=s2 + 2, amount=1.15); ctx.sfx("jingle", s2, 0.5)
    a, b = L(38)
    shc(tw, a, b, ((-1, 18.0), (0, 9.6), H + 0.1), 1.5, 0, lens=34, pz=a + 2, amount=1.3); ctx.sfx("heartbeat", a, 0.8)
    # 39: Max! Look at me!  (4 .. 0)
    a, b = L(39); kit.speak(me_t, 39); react(me_t, "scream", a)
    wfr = word_frames(39)
    for k, f in enumerate(wfr): ctx.overlay(f"count_{3 - k}.png", f, wfr[k + 1] if k + 1 < len(wfr) else b + 8)
    c = shf(tw, a, b, ((-1, 18.0), (0, 9.6), H + 0.1), 2.0, 0, lens=26, pz=wfr[-1], amount=1.3); shake(c, wfr[-1], 12, 0.35)
    # 40: the voice stops
    (a, s1), (_, s2), (_, b) = seg(40, "like", "zero")
    react(me_t, "shock", a); pose(me_t, a + 2, 4, ra=(-150, 0, -50))
    ctx.sfx("pause", a, 0.7)
    shf(tw, a, s1, ((-1, 18.0), (0, 9.6), H + 0.1), 2.2, 20, lens=26)
    react(me_t, "sad", s1)
    shf(tw, s1, s2, ((-1, 18.0), (0, 9.6), H + 0.1), 3.4, -20, lens=24)
    shc(tw, s2, b, ((-1, 18.0), (0, 9.6), H + 0.1), 1.6, 0, lens=32, pz=s2 + 2, amount=1.25); ctx.sfx("counter", s2, 0.8)
    rest(me_t, b, "ra")

    # ======================= 41-47: freeze =======================
    (a, s1), (_, b) = seg(41, "he")
    turn(max_t, a, (-1, 18), 10); rest(max_t, a, "ra"); react(max_t, "confused", a + 6)
    sh(tw, a, s1, (1.5, 3.5, 3.4), (0, 9.6, 3.0), 26, dl=(0, 0.6, 0)); ctx.sfx("whoosh", a + 4, 0.4)
    shf(tw, s1, b, ((0, 9.6), (-1, 18), HK + 0.1), 2.4, 0, pz=s1 + 2, amount=1.15)
    (a, s1), (_, b) = seg(42, ("i", 2))
    react(me_t, "determined", a)
    shf(tw, a, s1, ((-1, 18.0), (0, 9.6), H + 0.1), 2.6, 0, lens=26)
    fz = wf(42, "freeze"); pose(me_t, fz - 2, 3, ra=(-90, 0, -28), la=(-90, 0, 28))
    sh(tw, s1, b, (2.5, 13.5, 3.0), (-1, 18, 4.0), 22, pz=fz, amount=1.2); ctx.sfx("freeze", fz, 0.8)
    # 43: Max froze mid-step (he had started to run to me - into the truck's path)
    (a, s1), (_, s2), (_, b) = seg(43, "mid-step", "not")
    at(max_t, a, (0, 9.6, 0.1), (-1, 18), ease=1); react(max_t, "determined", a)
    pose(max_t, a, 1, ll=(-35, 0, 0), rl=(25, 0, 0), la=(-60, 0, -20), ra=(40, 0, 20))
    sh(tw, a, s1, (-6, 3.5, 2.6), (0, 9.6, 2.2), 24, pz=a + 2, amount=1.2); ctx.sfx("freeze", a, 0.5)
    sh(tw, s1, s2, (0, 4.5, 1.0), (0, 9.6, 1.0), 26, dl=(0, 0.6, 0))
    shf(tw, s2, b, ((0, 9.6), (-1, 18), HK + 0.1), 1.9, 25); ctx.sfx("heartbeat", s2, 0.4)
    # 44: the truck rolls past, six inches away
    (a, s1), (_, b) = seg(44, "six")
    K._key(truck, "location", a, (-14, 13.5, 0.1), None); K._key(truck, "location", L(45)[0] + 6, (30, 13.5, 0.1))
    sh(tw, a, s1, (0, 2.0, 2.4), (0, 14, 3.0), 18); ctx.sfx("whoosh", a + 4, 1.0); ctx.sfx("beep", a, 0.5)
    sh(tw, s1, b, (-1.5, 7.5, 3.0), (0.6, 10.4, 3.0), 22, pz=s1 + 2, amount=1.2); ctx.sfx("wind", s1, 0.5)
    # 45: brakes, ice cream everywhere
    (a, s1), (_, b) = seg(45, "ice")
    K._key(truck, "location", s1, (34, 13.5, 0.1), 6)
    sh(tw, a, s1, (44, 3, 3.6), (30, 13.5, 4.0), 22, dl=(-2, 0, 0)); ctx.sfx("screech", a + 2, 0.9)
    for k, sc_ in enumerate(scoops):
        p0 = Vector((34, 13.5 + random.uniform(-2, 2), 8.0)); p1 = p0 + Vector((random.uniform(4, 14), random.uniform(-8, 8), 0))
        K._key(sc_, "location", 0, (0, -300, 0), 1); K._key(sc_, "location", s1, tuple(p0), 1)
        K._key(sc_, "location", s1 + 8, tuple(p0 + (p1 - p0) * 0.5 + Vector((0, 0, 5)))); K._key(sc_, "location", s1 + 16, (p1.x, p1.y, 0.5))
    sh(tw, s1, b, (38, 2, 10), (40, 13.5, 2.0), 22, dl=(-1, 1, 0)); ctx.sfx("splat", s1 + 16, 0.8); ctx.sfx("splat", s1 + 20, 0.6)
    # 46: the hug, Max signs thank you
    (a, s1), (_, s2), (_, b) = seg(46, "then", "he'd")
    rest(max_t, a, ease=1); at(max_t, a, (-0.6, 16.4, 0.1), (-1, 18), ease=1); rest(me_t, a, "ra", "la", ease=1); at(me_t, a, (-1, 18.0, 0.1), (0, 9.6), ease=1)
    pose(max_t, a + 2, 4, ra=(-85, 0, 30), la=(-85, 0, -30)); react(max_t, "cry", a, s1); react(me_t, "cry", a, b)
    sh(tw, a, s1, (3.5, 12, 3.6), (-0.8, 17.2, 2.8), 26, dl=(-0.6, 0.6, 0)); ctx.sfx("sad", a + 4, 0.3)
    rest(max_t, s1, "ra", "la", ease=3); at(max_t, s1, (-0.6, 15.4, 0.1), (-1, 18), ease=1); react(max_t, "smile", s1)
    pose(max_t, s1 + 4, 3, ra=(-120, 0, -35)); pose(max_t, s1 + 12, 4, ra=(-70, 0, 0))
    shf(tw, s1, s2, ((-0.6, 15.4), (-1, 18), HK + 0.1), 2.4, 20); ctx.sfx("sparkle", s1 + 6, 0.5)
    react(me_t, "cry", s2, b + 20)
    shf(tw, s2, b, ((-1, 18.0), (0, 9.6), H + 0.1), 2.2, 0, pz=wf(46, "thank"), amount=1.2)
    rest(max_t, b, "ra")
    # 47: mom squeezes us
    (a, s1), (_, b) = seg(47, "i")
    at(mom_t, a, (-1.0, 14.6, 0.1), (-1, 18), ease=1); rest(mom_t, a, ease=1); pose(mom_t, a + 2, 4, ra=(-85, 0, 35), la=(-85, 0, -35))
    at(max_t, a, (-0.4, 16.6, 0.1), (-1, 18), ease=1); react(mom_t, "cry", a, b); react(max_t, "love", a)
    sh(tw, a, s1, (7.0, 16.4, 4.8), (-1.0, 16.4, 3.6), 24, dl=(-0.8, 0, 0)); ctx.sfx("gasp", a + 2, 0.3)
    react(me_t, "dizzy", s1); c = shf(tw, s1, b, ((-1, 18.0), (0, 9.6), H + 0.1), 2.0, 15, pz=wf(47, "ow"), amount=1.15); ctx.sfx("boing", wf(47, "ow"), 0.5)

    # ======================= 48-50: Grandma Pearl speaks =======================
    a, b = L(48)
    walk(pearl_t, a - 4, b - 3, (6, 26, 0.1), (8, 19, 0.1), 9, 20); react(pearl_t, "determined", a)
    sh(tw, a, b, (14, 9, 4.0), (8, 21, 4.2), 24, dl=(-0.5, 1, 0)); ctx.sfx("step", a + 4, 0.4); ctx.sfx("step", a + 14, 0.4)
    (a, s1), (_, b) = seg(49, "what")
    at(pearl_t, a, (8, 19, 0.1), (8, 30), ease=1); kit.speak(pearl_t, 49); react(pearl_t, "angry", a)
    pose(pearl_t, a + 2, 4, ra=(-95, 0, 25))
    shf(tw, a, s1, ((8, 19), (8, 30), H + 0.1), 2.6, 10)
    for av in crowd + [hend_t, gibbs_t, mayor_t]: react(av, "embarrassed", s1 + 4)
    rest(pearl_t, s1, "ra"); pose(pearl_t, s1 + 2, 4, la=(-150, 0, -30))
    sh(tw, s1, s1 + (b - s1) // 2, (10, 14, 6.5), (6, 26, 4.2), 22, dl=(-2, 0, 0)); ctx.sfx("crickets", s1, 0.3)
    shf(tw, s1 + (b - s1) // 2, b, ((8, 19), (8, 30), H + 0.1), 2.0, -15, pz=wf(49, "yours"), amount=1.2)
    rest(pearl_t, b, "la")
    (a, s1), (_, b) = seg(50, "that")
    react(pearl_t, "smile", a)
    shc(tw, a, s1, ((8, 19), (8, 30), H + 0.1), 1.9, 0, lens=28); ctx.sfx("counter", a, 0.4)
    react(pearl_t, "happy", s1); shf(tw, s1, b, ((8, 19), (8, 30), H + 0.1), 3.0, 25); ctx.sfx("sparkle", s1 + 2, 0.6)

    # ======================= 51-55: the town changed =======================
    a, b = L(51); hide_party = a
    sh(tw, a, b, (-60, -20, 30), (0, 30, 4), 22, dl=(10, 8, -10)); ctx.sfx("whoosh", a, 0.6); S.flash(a, 5)
    (a, s1), (_, s2), (_, b) = seg(52, "the", "they're")
    pairs = [(crowd[0], crowd[1], -24), (crowd[2], crowd[3], -10), (crowd[4], crowd[5], 12)]
    for k, (p, q, x) in enumerate(pairs):
        at(p, a, (x - 1.6, -2.5, W), 90); at(q, a, (x + 1.6, -2.5, W), -90); react(p, "happy", a); react(q, "smile", a)
        for j in range(0, s1 - a, 6):
            pose(p, a + j, 3, ra=(-110 if (j // 6) % 2 else -80, 0, -20)); pose(q, a + j + 3, 3, la=(-110 if (j // 6) % 2 else -80, 0, 20))
        rest(p, s1, "ra"); rest(q, s1, "la")
    sh(tw, a, s1, (-6, -14, 5), (-6, -2.5, 4.0), 22, dl=(4, 2, 0)); ctx.sfx("cheer", a, 0.3)
    at(mayor_t, s1, (-300, -18.8, 1.6), 180, ease=1); react(mayor_t, "happy", s1)
    for k, av in enumerate(crowd[6:12]): at(av, s1, (-306 + (k % 3) * 6, -8 + (k // 3) * 4, 0.3), (-300, -18)); react(av, "happy", s1)
    for j in range(0, s2 - s1, 6): pose(mayor_t, s1 + j, 3, ra=(-120 if (j // 6) % 2 else -80, 0, -30), la=(-80 if (j // 6) % 2 else -120, 0, 30))
    sh(tw, s1, s2, (-297, -9, 5.6), (-300, -18.5, 5.4), 26, dl=(-0.5, -1, 0)); ctx.sfx("pop", s1 + 4, 0.3)
    rest(mayor_t, s2, "ra", "la"); pose(mayor_t, s2 + 2, 4, ra=(-170, 0, 20)); react(mayor_t, "grin", s2)
    for av in crowd[6:12]: pose(av, s2 + 4, 4, ra=(-160, 0, 20), la=(-160, 0, -20))
    sh(tw, s2, b, (-291, -21, 6.0), (-302, -6, 4.4), 22, dl=(0, 1, 0)); ctx.sfx("cheer", s2 + 2, 0.6)
    # 53: Mr. Gibbs signs "fumble" at the game
    (a, s1), (_, b) = seg(53, "it's")
    sit(gibbs_t, a, 2.4, (330, -50.5), 0, ease=1); react(gibbs_t, "happy", a)
    for j in range(0, s1 - a, 6): pose(gibbs_t, a + j, 3, ra=(-140 if (j // 6) % 2 else -100, 0, -40), la=(-100 if (j // 6) % 2 else -140, 0, 40))
    at(pl1, a, (338, -22, 0.1), 0); hold(pl1, ball, "ra", (0, -0.5, 0)); pose(pl1, a, 1, ra=(-170, 0, 0)); react(pl1, "smug", a)
    shf(tw, a, s1, ((330, -50.5), 0, 5.45), 3.4, -20); ctx.sfx("cheer", a, 0.4)
    react(gibbs_t, "laugh", s1); rest(gibbs_t, s1, "ra", "la")
    sh(tw, s1, b, (344, -14, 4.6), (339, -22, 5.6), 26, dl=(0.4, 0.4, 0), pz=s1 + 3, amount=1.15); ctx.sfx("boing", s1 + 3, 0.4)
    # 54-55: zero words, never been heard more
    (a, s1), (_, b) = seg(54, "i've")
    for av in (me_t, max_t, mom_t): rest(av, a, ease=1)
    at(me_t, a, (2, -3.0, W), 0); at(max_t, a, (5.5, -3.0, W), 0); at(mom_t, a, (-1.8, -3.2, W), 0); react(me_t, "smile", a); react(max_t, "happy", a); react(mom_t, "smile", a)
    shc(tw, a, s1, ((2, -3.0), 0, H + W), 1.7, 0, lens=30); ctx.sfx("counter", a, 0.4)
    react(me_t, "happy", s1); shf(tw, s1, b, ((2, -3.0), 0, H + W), 2.6, 15, pz=s1 + 2, amount=1.15)
    a, b = L(55)
    for k, av in enumerate(crowd[:6]):
        at(av, a, (-12 + k * 5 if k < 3 else 9 + (k - 3) * 5, -2.4 - (k % 2), W), 0); react(av, "happy", a)
    pose(me_t, a, 3, ra=(-160, 0, 20)); pose(max_t, a + 2, 3, ra=(-160, 0, 20))
    for k, av in enumerate(crowd[:6]): pose(av, a + 3 + k, 3, ra=(-160, 0, 20))
    sh(tw, a, b + 40, (2, -10, 4.0), (2, -2, 4.4), 24, dl=(0, -14, 12)); ctx.sfx("cheer", a, 0.5); ctx.sfx("sparkle", a + 4, 0.5)
    show_between(party, L(28)[0], hide_party)

    # ======================= head motion while narrating =======================
    town_lines = {0, 1, 2, 9, 12, 15, 16, 21} | set(range(28, 56))
    for i, (who, _) in enumerate(ctx.story["lines"]):
        if who != "narrator" or i in (40, 41, 43, 44, 45, 51, 52, 53): continue
        kit.speak(me_t if i in town_lines else me_i, i, 0.4)
