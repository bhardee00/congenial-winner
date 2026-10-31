"""The library set for library.py. Room x -22..22, y -16..16 (back wall y 16, entrance on the front-left at x -18).
Key places:
  READ_TABLE   centre (-3, 0): Leo's booster seat at (-3, 1.9) facing -Y, Mom (0.4, 1.9), me (-3, -2.0) facing +Y
  BOOK_STACK   on the table at (-1.2, 1.2): a tall stack Leo pushes off toward +x
  DESK         front desk (11, 9.5) with the bell at (9.4, 8.3); Grandma's swivel chair at (11, 11.6)
  RETURN       book-return box with a slot at (5.0, 9.6)
  STORY        corner (-14, 10): rug, the big story-time armchair at (-14, 12.5) facing -Y, kids sit at y 4..9
  BEANBAGS     pit at (12, -9)
  DOOR         (-18, -15.8); the sign goes beside it at (-14.5, -15.6)"""
import math, random
import bpy
from mathutils import Vector
import shortkit as K
from shortkit import prim, mat, empty
from storykit import wall_mat
import town, toys

READ_TABLE = (-3.0, 0.0); DESK = (11.0, 9.5); BELL = (9.4, 8.2, 3.42); RETURN = (4.5, 6.2); STORY = (-14.0, 10.0)
BEANS = (-7.0, -9.0); DOOR = (-18.0, -15.8); TABLE_TOP = 2.74; SEAT = 1.75
BOOK_COLS = [(200, 60, 60), (60, 110, 190), (240, 190, 70), (80, 160, 90), (150, 80, 160), (235, 130, 60), (90, 180, 190),
             (240, 240, 230), (60, 60, 70), (220, 120, 160)]


def _tiled(path, scale, rough=0.5):
    m = K.image_mat(path); nt = m.node_tree; img = [n for n in nt.nodes if n.type == 'TEX_IMAGE'][0]
    geo = nt.nodes.new("ShaderNodeNewGeometry"); mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (scale,) * 3
    nt.links.new(geo.outputs["Position"], mp.inputs["Vector"]); nt.links.new(mp.outputs[0], img.inputs[0])
    nt.nodes["Principled BSDF"].inputs["Roughness"].default_value = rough
    return m


def shelf(x, y, yaw=0, w=6.0, h=8.0, d=1.6, rows=4, rnd=None, wood=(150, 100, 60)):
    """A wooden bookshelf packed with books of random colours, heights and leans. Front faces -Y at yaw 0."""
    rnd = rnd or random.Random(int(x * 13 + y * 7))
    r = empty("shelf", (x, y, 0)); r.rotation_euler = (0, 0, math.radians(yaw)); wm = mat(wood, 0.6)
    prim("box", (w, 0.2, h), (0, d / 2 - 0.1, h / 2), wm, parent=r)
    for sx in (-1, 1): prim("box", (0.25, d, h), (sx * (w / 2 - 0.12), 0, h / 2), wm, parent=r)
    rh = (h - 0.4) / rows
    for k in range(rows + 1): prim("box", (w, d, 0.2), (0, 0, 0.1 + k * rh), wm, parent=r)
    mats = [mat(c, 0.6) for c in BOOK_COLS]
    for k in range(rows):
        z0 = 0.2 + k * rh; xx = -w / 2 + 0.35
        while xx < w / 2 - 0.5:
            bw = rnd.uniform(0.18, 0.34); bh = rh * rnd.uniform(0.6, 0.88)
            if rnd.random() < 0.06: xx += bw * 2; continue  # a gap
            lean = rnd.choice((0, 0, 0, 0, 8, -8))
            prim("box", (bw, d * 0.75, bh), (xx + bw / 2, -0.05, z0 + bh / 2), rnd.choice(mats), rot=(0, lean, 0), parent=r, bevel=0.02)
            xx += bw + 0.02
    return r


def book(c, size=(0.55, 0.8, 0.14)):
    o = empty("book"); prim("box", size, (0, 0, 0), mat(c, 0.6), parent=o, bevel=0.02)
    prim("box", (size[0] * 0.92, size[1] * 0.96, size[2] * 0.8), (0.03, 0, 0), mat((250, 245, 230), 0.8), parent=o)
    return o


def build(st, A, seed=5):
    random.seed(seed); rnd = random.Random(seed); out = {}
    town.sky(st, 0.7, 2.6, (55, 0, -30))
    st.scene.view_settings.look = 'Medium Contrast'; st.scene.view_settings.exposure = 0.3
    floor = _tiled(A + "wood_floor.png", 0.08, 0.45)
    town.slab((46, 34, 0.4), (0, 0, -0.2), floor, "floor")
    wallc = wall_mat((236, 226, 205)); trim = wall_mat((120, 80, 50)); green = wall_mat((95, 140, 105))
    prim("box", (46, 0.5, 14), (0, 16.2, 7), wallc); prim("box", (0.5, 34, 14), (-22.2, 0, 7), wallc); prim("box", (0.5, 34, 14), (22.2, 0, 7), wallc)
    dxl = DOOR[0]  # front wall with a doorway (x dxl-2.6 .. dxl+2.6, up to z 9.2)
    prim("box", (dxl - 2.6 + 23, 0.5, 14), ((-23 + dxl - 2.6) / 2, -16.2, 7), wallc)
    prim("box", (23 - (dxl + 2.6), 0.5, 14), ((dxl + 2.6 + 23) / 2, -16.2, 7), wallc)
    prim("box", (5.2, 0.5, 4.8), (dxl, -16.2, 11.6), wallc)
    for (sx, sy, cx, cy) in ((46, 0.52, 0, 16.0), (0.52, 34, -22.0, 0), (0.52, 34, 22.0, 0), (46, 0.52, 0, -16.0)):
        prim("box", (sx, sy, 3.2), (cx, cy, 1.6), green); prim("box", (sx, sy * 1.02, 0.3), (cx, cy, 3.25), trim)
    prim("box", (46, 34, 0.4), (0, 0, 14.2), wall_mat((250, 248, 240)))
    for x in (-12, 0, 12):
        for y in (-8, 4):
            prim("box", (5, 1.4, 0.15), (x, y, 13.9), mat((255, 252, 235), 0.3, emit=3.0))
    for y in (-8, 2, 10): toys.window(22.0, y, 5, 5, 8.0, 90, (170, 215, 250))
    for y in (-8, 2): toys.window(-22.0, y, 5, 5, 8.0, 90, (170, 215, 250))
    # the door and the library sign
    door = empty("door", (DOOR[0] - 2.5, -16.0, 0))  # hinged on its left edge: rotate z to open it inward
    prim("box", (5.0, 0.4, 9.0), (2.5, 0, 4.5), mat((130, 85, 50), 0.5), parent=door, bevel=0.05)
    prim("box", (3.0, 0.45, 4.0), (2.5, 0, 5.5), mat((190, 225, 250), 0.1), parent=door)
    prim("ball", (0.35, 0.35, 0.35), (4.4, -0.35, 4.2), mat((230, 200, 90), 0.2, metal=0.9), parent=door)
    out["door"] = door
    town.slab((60, 30, 0.4), (0, -32, -0.25), town.concrete(), "sidewalk_out")  # outside the doorway
    K.plane_image(A + "library_sign.png", (12, 2.6), (0, 15.9, 11.4))
    # shelves: back wall, side walls, two free-standing rows
    for x in (-19, -13, 3, 17): shelf(x, 15.0, 0, rnd=rnd)
    for y in (-10, -3, 4): shelf(-21.0, y, 90, rnd=rnd); shelf(21.0, y + 1, -90, rnd=rnd)  # fronts face into the room
    # reading table with chairs, a booster seat for Leo, the tall book stack, a lamp
    tx, ty = READ_TABLE
    town.place("furniture/table", (tx, ty, 0), 0, scale=8.4)
    for dx in (-2.4, 0.0, 2.4): town.place("furniture/chairCushion", (tx + dx, ty + 2.6, 0), 0)    # back side, facing the table
    for dx in (-2.4, 0.0): town.place("furniture/chairCushion", (tx + dx, ty - 2.6, 0), 180)
    prim("box", (1.5, 1.5, 1.0), (tx, ty + 2.5, SEAT + 0.5), mat((240, 200, 70), 0.5), bevel=0.15)   # Leo's booster
    prim("box", (1.5, 0.3, 1.3), (tx, ty + 3.2, SEAT + 1.3), mat((240, 200, 70), 0.5), bevel=0.1)
    stack = []
    for k in range(8):
        b = book(BOOK_COLS[k % len(BOOK_COLS)], (rnd.uniform(1.0, 1.3), rnd.uniform(1.4, 1.7), 0.24))
        b.location = (tx - 1.9 + rnd.uniform(-0.08, 0.08), ty + 1.0, TABLE_TOP + 0.12 + k * 0.25); b.rotation_euler = (0, 0, math.radians(rnd.uniform(-12, 12)))
        stack.append(b)
    out["stack"] = stack
    out["open_book"] = book((60, 110, 190), (1.6, 1.1, 0.12)); out["open_book"].location = (tx, ty + 1.0, TABLE_TOP + 0.08)
    # second table with readers, computers along the right
    town.place("furniture/table", (13, -9, 0), 0, scale=8.4)   # readers' table
    for dx in (-2.2, 2.2):
        town.place("furniture/chairCushion", (13 + dx, -9 + 2.6, 0), 0); town.place("furniture/chairCushion", (13 + dx, -9 - 2.6, 0), 180)
    for k, x in enumerate((10.8, 15.2)):
        b = book(BOOK_COLS[(k * 3) % 10], (1.3, 0.9, 0.1)); b.location = (x, -9 + (1.0 if k == 0 else -1.0), TABLE_TOP + 0.06)
    # front desk: L-shaped counter, bell, book return box, Grandma's swivel chair (pivot for the slow turn)
    dx, dy = DESK
    prim("box", (9.0, 2.2, 3.4), (dx, dy - 0.8, 1.7), mat((150, 100, 60), 0.5), bevel=0.06); prim("box", (9.3, 2.6, 0.2), (dx, dy - 0.8, 3.45), mat((90, 60, 40), 0.4))
    prim("box", (2.2, 4.4, 3.4), (dx + 3.4, dy + 1.4, 1.7), mat((150, 100, 60), 0.5), bevel=0.06)
    bell = empty("bell", BELL); prim("cylY", (0.9, 0.9, 0.12), (0, 0, 0.06), mat((90, 60, 40), 0.4), parent=bell)
    dome = prim("ball", (0.75, 0.75, 0.6), (0, 0, 0.2), mat((235, 200, 90), 0.15, metal=0.9), parent=bell)
    btn = prim("cylY", (0.12, 0.12, 0.25), (0, 0, 0.55), mat((200, 200, 205), 0.2, metal=0.9), parent=bell)
    out["bell"] = bell; out["bell_button"] = btn
    chair = empty("swivel", (dx, dy + 2.1, 0)); cm = mat((60, 60, 70), 0.4); seat = mat((150, 40, 45), 0.6)
    prim("cylY", (0.3, 0.3, 1.6), (0, 0, 0.8), cm, parent=chair)
    for a in range(5): prim("box", (1.4, 0.2, 0.2), (math.cos(a * 1.257) * 0.7, math.sin(a * 1.257) * 0.7, 0.15), cm, rot=(0, 0, math.degrees(a * 1.257)), parent=chair)
    prim("box", (2.6, 2.4, 0.5), (0, 0, 1.75), seat, parent=chair, bevel=0.15)
    prim("box", (2.6, 0.5, 4.2), (0, 1.15, 3.9), seat, parent=chair, bevel=0.2)  # tall back: hides whoever sits in it
    out["swivel"] = chair
    rb = empty("return", (RETURN[0], RETURN[1], 0)); bm_ = mat((40, 90, 160), 0.4)
    prim("box", (2.6, 2.4, 4.0), (0, 0, 2.0), bm_, parent=rb, bevel=0.1); prim("box", (2.8, 2.6, 0.3), (0, 0, 4.1), bm_, parent=rb, bevel=0.1)
    prim("box", (1.6, 0.1, 0.35), (0, -1.22, 3.3), mat((15, 15, 20), 0.6), parent=rb)  # the slot
    K.plane_image(A + "return_sign.png", (2.2, 0.9), (0, -1.23, 2.4), parent=rb)
    # story corner: rug, the big chair, cushions
    sx, sy = STORY
    town.place("furniture/rugRound", (sx, sy - 3.0, 0.01), 0, scale=12)
    big = empty("story_chair", (sx, sy + 2.5, 0)); bc = mat((90, 70, 170), 0.6)
    prim("box", (5.4, 3.6, 2.0), (0, 0, 1.0), bc, parent=big, bevel=0.3); prim("box", (5.4, 1.0, 6.0), (0, 1.4, 3.0), bc, parent=big, bevel=0.35)
    for s_ in (-1, 1): prim("box", (0.9, 3.6, 3.4), (s_ * 2.6, 0, 1.7), bc, parent=big, bevel=0.3)
    prim("box", (4.6, 3.0, 0.5), (0, -0.1, 2.2), mat((250, 210, 80), 0.6), parent=big, bevel=0.2)
    K.plane_image(A + "storytime_sign.png", (6, 1.8), (sx, 15.9, 9.4))
    out["story_chair_seat_z"] = 2.45
    # bean bag pit
    bx, by = BEANS; pit = mat((235, 225, 210), 0.6)
    for (w_, d_, cx, cy) in ((10, 0.5, 0, -3.4), (10, 0.5, 0, 3.4), (0.5, 7.3, -4.8, 0), (0.5, 7.3, 4.8, 0)):
        prim("box", (w_, d_, 1.4), (bx + cx, by + cy, 0.7), pit, bevel=0.08)
    bean_cols = [(240, 110, 90), (90, 170, 230), (250, 200, 70), (130, 200, 120), (200, 120, 200), (250, 150, 180)]
    beans = []
    for k in range(9):
        b = prim("ball", (2.6, 2.6, 1.8), (bx - 3.0 + (k % 3) * 3.0 + rnd.uniform(-0.3, 0.3), by - 2.0 + (k // 3) * 2.0, 0.9), mat(bean_cols[k % 6], 0.8))
        beans.append(b)
    out["beans"] = beans
    # plants, lamps, posters, a cart of books
    for (x, y) in ((-20.5, 14.5), (20.5, 14.5), (-20.5, -14.5), (8.5, -14.5)): town.place("furniture/pottedPlant", (x, y, 0), 0, scale=8)
    for (x, y) in ((-8.0, 13.5), (19.0, -14.0)): town.place("furniture/lampSquareFloor", (x, y, 0), 0, scale=7.5)
    for k, (x, img) in enumerate(((-6.5, "poster_read.png"), (0.5, "poster_quiet.png"))):
        K.plane_image(A + img, (3.0, 4.0), (x, 15.9, 6.5))
    out["sign"] = toys.card(A + "quiet_sign.png", 3.6, 4.6); out["sign"].location = (-11.5, -15.85, 6.0); out["sign"].rotation_euler = (0, 0, math.radians(180))  # faces into the room
    return out
