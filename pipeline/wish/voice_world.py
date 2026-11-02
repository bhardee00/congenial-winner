"""Extra sets for 'The Voice': town square, river + old bridge + bus stop, city, wedding, fire, beach, train tracks,
classroom, Nora's room, Eli's room, underwater. Built on top of world.py's town (which is built with river=True)."""
import bpy, bmesh, math, random
from mathutils import Vector
from lib import *
import world
from world import CTRL, tree, lamp_post, room, house, window_mat

SQ = Vector((-40, 100, 0))              # town square centre
BR = Vector((40, 180, 0))               # bridge centre (river runs along X between y=165 and y=195)
RIV_Y0, RIV_Y1, WATER_Z = 165, 195, -3.0
INT = dict(classroom=Vector((900, 0, 0)), nora_room=Vector((1100, 0, 0)), eli_room=Vector((1200, 0, 0)), underwater=Vector((1300, 0, 0)))
CITY = Vector((300, 320, 0)); BEACH = Vector((0, -270, 0)); TRACKS = Vector((220, -110, 0)); FIRE = Vector((60, -20, 0)); WED = Vector((-125, 12, 0))
V = {}   # handles to animated props


def water_mat(name, base=0x1d5f86, rough=0.05):
    m = bpy.data.materials.new(name); m.use_nodes = True; N = m.node_tree.nodes; L = m.node_tree.links
    b = N["Principled BSDF"]; b.inputs["Base Color"].default_value = lin(base); b.inputs["Roughness"].default_value = rough
    b.inputs["Specular IOR Level"].default_value = 0.7
    tc = N.new("ShaderNodeTexCoord"); mp = N.new("ShaderNodeMapping"); wv = N.new("ShaderNodeTexWave"); bump = N.new("ShaderNodeBump")
    wv.inputs["Scale"].default_value = 0.25; wv.inputs["Distortion"].default_value = 7; wv.inputs["Detail"].default_value = 3; bump.inputs["Strength"].default_value = 0.15
    L.new(tc.outputs["Object"], mp.inputs[0]); L.new(mp.outputs[0], wv.inputs[0]); L.new(wv.outputs["Fac"], bump.inputs["Height"]); L.new(bump.outputs["Normal"], b.inputs["Normal"])
    for f, v in ((0, 0.0), (4000, 60.0)):
        mp.inputs["Location"].default_value = (v, v * 0.2, 0); mp.inputs["Location"].keyframe_insert("default_value", frame=f)
    for fc in m.node_tree.animation_data.action.fcurves:
        for k in fc.keyframe_points: k.interpolation = 'LINEAR'
    m['flow'] = True
    return m


def square():
    c = SQ; stone = mat(0xb9b2a5, 0.85, kind='slate', name='sqstone')
    box((44, 44, 0.3), (c.x, c.y, 0.15), stone, name='square')
    for i in range(-2, 3):
        box((44, 0.2, 0.05), (c.x, c.y + i * 8, 0.31), mat(0x8f8a80, 0.8))
    # clock post + fountain in the middle
    tube(4.5, 5.4, 1.2, (c.x, c.y, 0.3), mat(0x9e9e9e, 0.7, kind='slate'), v=32, name='fountain')
    cyl(4.5, 0.2, (c.x, c.y, 1.1), water_mat('fountainwater'), v=32)
    cyl(0.6, 9, (c.x, c.y, 4.8), mat(0x263238, 0.4, metal=0.6), v=12)
    box((2.6, 2.6, 2.6), (c.x, c.y, 10.4), mat(0x263238, 0.4, metal=0.6))
    for s in (-1, 1):
        cyl(1.05, 0.15, (c.x, c.y + s * 1.32, 10.4), mat(0xfffde7, 0.4, emit=1.2, name='sqclock'), rot=(math.radians(90), 0, 0), v=28)
        for (ax, l) in ((0, 0.8), (0.1, 0.6)):
            box((0.1, 0.05, l), (c.x, c.y + s * 1.42, 10.4 + l / 2 - 0.05), mat(0x111111, 0.4), rot=(0, ax, 0))
    # benches, lamps, string lights, trees
    for (x, y, r) in [(-14, -12, 0), (14, -12, 0), (-14, 12, 180), (14, 12, 180)]:
        box((6, 1.6, 0.4), (c.x + x, c.y + y, 1.8), mat(0x8d5a32, 0.6, kind='wood'), rot=(0, 0, math.radians(r)))
        box((6, 0.3, 1.6), (c.x + x, c.y + y + (0.8 if r == 0 else -0.8), 2.6), mat(0x8d5a32, 0.6, kind='wood'))
        for sx in (-2.6, 2.6): box((0.3, 1.4, 1.8), (c.x + x + sx, c.y + y, 0.9), mat(0x263238, 0.4, metal=0.5))
    for (x, y) in [(-20, -20), (20, -20), (-20, 20), (20, 20)]:
        cyl(0.25, 10, (c.x + x, c.y + y, 5), mat(0x263238, 0.4, metal=0.5), v=10)
        sphere(0.7, (c.x + x, c.y + y, 10.3), mat(0xfff1c2, 0.3, emit=6), seg=12)
        bpy.ops.object.light_add(type='POINT', location=(c.x + x, c.y + y, 9.4)); l = bpy.context.active_object
        l.data.energy = 900; l.data.color = (1, 0.82, 0.55); l.data.use_shadow = False; l['on'] = 900; l.data.use_custom_distance = True; l.data.cutoff_distance = 45
        CTRL.setdefault('nightlights', []).append(l)
    cols = [0xffd54f, 0xff8a65, 0x81d4fa, 0xa5d6a7, 0xf48fb1]
    for (a, b) in [((-20, -20), (20, 20)), ((20, -20), (-20, 20))]:
        for k in range(1, 18):
            t = k / 18; x = a[0] + (b[0] - a[0]) * t; y = a[1] + (b[1] - a[1]) * t; z = 10 - 2.5 * math.sin(math.pi * t)
            sphere(0.22, (c.x + x, c.y + y, z), mat(cols[k % 5], 0.3, emit=8, name=f'bulb{k % 5}'), seg=8)
    for (x, y) in [(-26, -26), (26, -26), (-26, 26), (26, 26), (-30, 0), (30, 0)]: tree(c.x + x, c.y + y, 1.0, random.randrange(3))
    # shops around the square
    for (x, w, col) in [(-12, 14, 0xffcc80), (6, 16, 0xce93d8), (24, 12, 0x80cbc4)]:
        box((w, 10, 12), (c.x + x, c.y + 32, 6), mat(col, 0.6, kind='concrete'))
        wm = CTRL.get('windows', [None])[0] or window_mat()
        box((w * 0.7, 0.3, 4), (c.x + x, c.y + 26.9, 3.4), wm)
        box((w + 0.6, 2.4, 0.4), (c.x + x, c.y + 26.0, 6.6), mat(0xc62828 if x < 0 else 0x1565c0, 0.6, kind='fabric'))


def river_and_bridge():
    grass = mat(0x5ba83f, 0.85, kind='grass'); mud = mat(0x6b5a3f, 0.9, kind='grass', name='bankmud')
    box((700, 30, 3), (50, (RIV_Y0 + RIV_Y1) / 2, -7.5), mat(0x3e3a2f, 0.9, kind='slate'), name='riverbed')
    # sloped banks (from ground level down below the water line)
    for (y, s) in ((RIV_Y0, 1), (RIV_Y1, -1)):
        o = box((700, 9, 1.0), (50, y + s * 3.9, -2.2), mud, name='bank'); o.rotation_euler = (math.radians(-28 * s), 0, 0)
        o = box((700, 4, 1.0), (50, y - s * 1.6, -0.5), grass, name='bankedge')
    w = water_mat('river', 0x174f6e)
    box((700, RIV_Y1 - RIV_Y0 + 4, 0.2), (50, (RIV_Y0 + RIV_Y1) / 2, WATER_Z), w, name='riverwater')
    for i in range(30):
        x = random.uniform(-200, 300); y = random.choice([RIV_Y0 - 3, RIV_Y1 + 3]) + random.uniform(-1, 1)
        if abs(x - BR.x) < 10: continue
        for k in range(3): cyl(0.08, random.uniform(1.5, 3), (x + k * 0.3, y, 0.8), mat(0x7cb342, 0.7), v=5)
    # old wooden bridge
    c = BR; wood = mat(0x8b6a43, 0.75, kind='wood', name='bridgewood'); dark = mat(0x5d4430, 0.8, kind='wood', name='bridgedark')
    L0, L1 = RIV_Y0 - 8, RIV_Y1 + 8
    for i, y in enumerate(range(L0, L1)):
        box((7, 0.9, 0.35), (c.x, y + 0.5, 1.8), wood if i % 2 else dark, name='plank')
    for sx in (-3.2, 3.2): box((0.5, L1 - L0, 0.7), (c.x + sx, (L0 + L1) / 2, 1.35), dark)
    for y in (RIV_Y0 + 6, RIV_Y1 - 6):
        box((8, 2.2, 10), (c.x, y, -3.2), mat(0x6f6a62, 0.85, kind='slate'))
    posts = list(range(L0, L1 + 1, 4))
    for sx in (-3.3, 3.3):
        for y in posts: box((0.45, 0.45, 3.0), (c.x + sx, y, 3.4), dark)
    # railings: west side whole, east side in pieces, middle piece is the one that snaps
    for (y0, y1) in [(L0, L1)]: box((0.3, y1 - y0, 0.35), (c.x - 3.3, (y0 + y1) / 2, 4.6), wood); box((0.25, y1 - y0, 0.25), (c.x - 3.3, (y0 + y1) / 2, 3.4), wood)
    SN0, SN1 = 177, 185
    for (y0, y1) in [(L0, SN0), (SN1, L1)]:
        box((0.3, y1 - y0, 0.35), (c.x + 3.3, (y0 + y1) / 2, 4.6), wood); box((0.25, y1 - y0, 0.25), (c.x + 3.3, (y0 + y1) / 2, 3.4), wood)
    piv = link(bpy.data.objects.new('snap_rail', None)); piv.location = (c.x + 3.3, SN0, 4.6)
    for (z, t) in ((0, 0.35), (-1.2, 0.25)):
        o = box((0.3, SN1 - SN0, t), (0, (SN1 - SN0) / 2, z), wood, name='snap_part'); o.parent = piv
    V['snap'] = piv
    # far side: road + bus stop + lamp
    box((700, 10, 0.2), (50, RIV_Y1 + 18, 0.05), mat(0x3a3d42, 0.8, kind='asphalt'))
    for i in range(-10, 14): box((5, 0.35, 0.05), (i * 16, RIV_Y1 + 18, 0.17), mat(0xf6c544, 0.5))
    bs = Vector((c.x + 12, RIV_Y1 + 11, 0))
    box((10, 0.3, 6), (bs.x, bs.y + 2.6, 3), mat(0xcfe8f5, 0.1, alpha=0.45)); box((10.6, 4, 0.3), (bs.x, bs.y + 1, 6.1), mat(0x37474f, 0.4, metal=0.6))
    for sx in (-5, 5): box((0.3, 0.3, 6), (bs.x + sx, bs.y + 2.6, 3), mat(0x37474f, 0.4, metal=0.6))
    box((7, 1.4, 0.3), (bs.x, bs.y + 1.8, 1.8), mat(0x8d5a32, 0.6, kind='wood')); [box((0.3, 1.2, 1.8), (bs.x + sx, bs.y + 1.8, 0.9), mat(0x37474f, 0.4)) for sx in (-3, 3)]
    cyl(0.12, 7, (bs.x - 7, bs.y, 3.5), mat(0x9e9e9e, 0.4, metal=0.7), v=8)
    cyl(1.0, 0.15, (bs.x - 7, bs.y - 0.1, 6.6), mat(0x1565c0, 0.4), rot=(math.radians(90), 0, 0), v=24)
    text("BUS", (bs.x - 7, bs.y - 0.2, 6.6), 0.55, mat(0xffffff, 0.5), extrude=0.02)
    V['busstop'] = bs
    lamp_post(c.x - 6, RIV_Y1 + 6, 700); lamp_post(c.x + 6, RIV_Y0 - 6, 700)
    # the last bus
    bus = link(bpy.data.objects.new('bus', None)); bus.location = (bs.x + 40, RIV_Y1 + 20.5, 0)
    body = mat(0x1e88e5, 0.45, name='busbody'); win = mat(0xfff3c4, 0.2, emit=2.5, name='buswin')
    box((26, 8, 7.2), (0, 0, 4.4), body, bus); box((26.2, 8.2, 1.2), (0, 0, 1.4), mat(0xeceff1, 0.5), bus)
    for k in range(6): box((3.2, 8.3, 2.4), (-10 + k * 4, 0, 5.6), win, bus)
    box((0.3, 7, 2.4), (13.05, 0, 5.6), win, bus); box((0.3, 7.6, 1.0), (13.1, 0, 7.6), mat(0x111111, 0.4), bus)
    for sx in (-8.5, 8.5):
        for sy in (-4.05, 4.05): cyl(1.4, 0.8, (sx, sy, 1.4), mat(0x212121, 0.6), bus, rot=(math.radians(90), 0, 0), v=20)
    for sy in (-2.8, 2.8): box((0.2, 1.0, 0.7), (13.1, sy, 2.6), mat(0xfff5cc, 0.2, emit=6), bus)
    V['bus'] = bus
    # path from town to the bridge
    box((5, RIV_Y0 - 8 - 40, 0.08), (c.x, (RIV_Y0 - 8 + 40) / 2, 0.04), mat(0xa1887f, 0.9, kind='concrete'))
    for (x, y) in [(20, 150), (62, 150), (15, 215), (70, 220), (95, 150), (-10, 150)]: tree(x, y, 1.1, random.randrange(3))
    # splash (hidden until used)
    sp = link(bpy.data.objects.new('splash', None)); sp.location = (c.x + 6.5, 181, WATER_Z)
    for k in range(14):
        a = k / 14 * math.tau; o = sphere(random.uniform(0.35, 0.7), (math.cos(a) * 1.2, math.sin(a) * 1.2, random.uniform(0.3, 2.2)), mat(0xe3f2fd, 0.2, alpha=0.8, name='splashm'), seg=8)
        o.parent = sp
    tube(1.2, 1.8, 0.15, (0, 0, 0.1), mat(0xffffff, 0.3, alpha=0.7, name='ringm'), v=24, parent=sp)
    V['splash'] = sp


def city():
    c = CITY; random.seed(21)
    box((120, 80, 0.3), (c.x, c.y, 0.15), mat(0x9e9e9e, 0.7, kind='concrete'))
    gm = mat(0x4f7fa8, 0.25, metal=0.3, name='cityglass')
    for i in range(14):
        x = c.x - 60 + i * 9 + random.uniform(-1, 1); y = c.y + 30 + random.uniform(0, 25); h = random.uniform(30, 90); w = random.uniform(6, 9)
        box((w, w, h), (x, y, h / 2), random.choice([gm, mat(0x546e7a, 0.4, metal=0.3), mat(0xb0bec5, 0.3, metal=0.4)]))
        for z in range(4, int(h) - 2, 5): box((w * 0.8, 0.1, 0.5), (x, y - w / 2 - 0.05, z), mat(0xfff3c4, 0.2, emit=1.5, name='citywin'))
    box((26, 14, 40), (c.x, c.y + 14, 20), gm, name='tower')
    text("WILSON & CO.", (c.x, c.y + 6.8, 14), 1.4, mat(0xffd54f, 0.3, metal=1), extrude=0.1)
    for k in range(4): box((26 - k * 3, 3, 0.5), (c.x, c.y + 5 - k * 1.2, 0.3 + k * 0.5), mat(0xeeeeee, 0.5, kind='concrete'))
    gold = mat(0xffc107, 0.2, metal=1, name='goldcar')
    car = link(bpy.data.objects.new('goldcar', None)); car.location = (c.x + 8, c.y - 4, 0); car.rotation_euler = (0, 0, math.radians(-75))
    box((5, 11, 1.8), (0, 0, 1.6), gold, car); box((4.4, 5, 1.4), (0, 0.8, 3.1), mat(0x263238, 0.1), car)
    for sx in (-2.5, 2.5):
        for sy in (-3.4, 3.4): cyl(1.0, 0.8, (sx, sy, 1.0), mat(0x111111, 0.5), car, rot=(0, math.radians(90), 0), v=18)
    for k in range(5): cyl(1.2, 0.3, (c.x - 10 + k * 2.4, c.y - 6, 1.0 + k * 0.2), mat(0xffd54f, 0.2, metal=1), v=20)   # gold coins stack
    for (x, y) in [(-20, -10), (24, -12)]: tree(c.x + x, c.y + y, 0.9, 1)


def wedding():
    c = WED; white = mat(0xffffff, 0.5, name='archwhite')
    for sx in (-4, 4): cyl(0.3, 9, (c.x + sx, c.y, 4.5), white, v=10)
    tube(3.7, 4.3, 0.6, (c.x, c.y, 8.6), white, v=32, name='arch').rotation_euler = (math.radians(90), 0, 0)
    cols = [0xf8bbd0, 0xffffff, 0xf48fb1, 0xfff59d]
    for k in range(26):
        a = k / 25 * math.pi; sphere(0.55, (c.x + math.cos(a) * 4, c.y - 0.4, 8.6 + math.sin(a) * 4), mat(cols[k % 4], 0.6), seg=10)
    box((3, 14, 0.06), (c.x, c.y - 9, 0.04), mat(0xffffff, 0.8, kind='fabric'))
    for k in range(60):
        box((0.25, 0.04, 0.18), (c.x + random.uniform(-7, 7), c.y - random.uniform(0, 8), random.uniform(2, 10)), mat(random.choice([0xf48fb1, 0xfff176, 0x81d4fa, 0xffffff]), 0.5), rot=(random.random(), random.random(), random.random()))
    for s in (-1, 1):
        for r in range(3):
            for k in range(3): box((1.6, 1.6, 0.9), (c.x + s * (6 + k * 2.2), c.y - 6 - r * 3, 1.5), white)
    veil = cyl(0.9, 2.2, (0, 0, 0), mat(0xffffff, 0.4, alpha=0.6, name='veil'), v=16, r2=0.65); V['veil'] = veil
    bq = link(bpy.data.objects.new('bouquet', None))
    for k in range(5): o = sphere(0.28, (math.cos(k) * 0.25, math.sin(k) * 0.25, 0.1), mat(cols[k % 4], 0.6), seg=8); o.parent = bq
    V['bouquet'] = bq


def fire_scene():
    c = FIRE; random.seed(5)
    fl = [mat(0xff6f00, 0.3, emit=12, name='fire1'), mat(0xffab00, 0.3, emit=14, name='fire2'), mat(0xff3d00, 0.3, emit=10, name='fire3')]
    root = link(bpy.data.objects.new('fire', None)); root.location = c
    for k in range(22):   # flames on the roof and out of the windows (house front is at local y=0, body spans y 0..-14)
        x = random.uniform(-8, 8); roof = k % 3 != 0
        z = random.uniform(10.5, 13) if roof else random.choice([4.5, 5.5]); y = random.uniform(-12, -3) if roof else 0.4
        o = cyl(random.uniform(0.6, 1.4), random.uniform(2, 4.5), (x, y, z + 1.5), random.choice(fl), v=8, r2=0.05); o.parent = root
    for k in range(10):
        o = sphere(random.uniform(2, 4), (random.uniform(-8, 8), random.uniform(-12, -2), random.uniform(15, 24)), mat(0x424242, 0.9, alpha=0.75, name='smoke'), seg=10); o.parent = root
    bpy.ops.object.light_add(type='POINT', location=(c.x, c.y - 2, 6)); l = bpy.context.active_object; l.data.energy = 6000; l.data.color = (1, 0.5, 0.2); l.data.use_custom_distance = True; l.data.cutoff_distance = 40; l.parent = None; l.location = (c.x, c.y + 3, 6)
    V['firelight'] = l; V['fire'] = root
    truck = link(bpy.data.objects.new('firetruck', None)); truck.location = (c.x + 18, c.y + 24, 0); truck.rotation_euler = (0, 0, math.radians(90))
    red = mat(0xd50000, 0.4, name='truckred')
    box((7, 22, 6), (0, 0, 3.6), red, truck); box((6.6, 6, 3), (0, -9, 7.6), red, truck); box((6.4, 0.2, 2.4), (0, -12.1, 7.6), mat(0x90caf9, 0.1), truck)
    box((1.4, 18, 0.6), (0, 2, 7.2), mat(0xcfd8dc, 0.3, metal=0.8), truck)
    for sy in (-7, 7):
        for sx in (-3.5, 3.5): cyl(1.4, 0.9, (sx, sy, 1.4), mat(0x111111, 0.5), truck, rot=(0, math.radians(90), 0), v=18)
    box((2, 1, 0.7), (0, -9, 9.4), mat(0x2979ff, 0.2, emit=10), truck)
    helm = link(bpy.data.objects.new('helmet', None))
    o = sphere(0.78, (0, 0, 0), mat(0xffc400, 0.3, name='helm'), scale=(1, 1.1, 0.75), seg=16); o.parent = helm
    o = cyl(1.05, 0.12, (0, 0.15, -0.15), mat(0xffc400, 0.3, name='helm'), v=20); o.parent = helm
    V['helmet'] = helm; V['truck'] = truck


def beach():
    c = BEACH
    box((160, 70, 1), (c.x, c.y, -0.3), mat(0xf0d9a0, 0.9, kind='concrete', name='sand'))
    box((800, 600, 0.2), (c.x, c.y - 330, -0.6), water_mat('ocean', 0x1e88c8), name='ocean')
    box((160, 12, 0.6), (c.x, c.y - 38, -0.55), mat(0xd8c08a, 0.6, kind='concrete', name='wetsand'))
    ch = Vector((c.x + 8, c.y - 6, 0))
    for sx in (-1.4, 1.4):
        for sy in (-1.2, 1.2): box((0.3, 0.3, 7), (ch.x + sx, ch.y + sy, 3.5), mat(0xffffff, 0.5))
    box((3.4, 3, 0.4), (ch.x, ch.y, 7), mat(0xffffff, 0.5)); box((4.4, 3.8, 0.2), (ch.x, ch.y, 10.4), mat(0xe53935, 0.5))
    cyl(0.12, 3.4, (ch.x, ch.y, 8.7), mat(0xffffff, 0.5), v=6)
    for k in range(4):
        u = Vector((c.x - 30 + k * 18, c.y + 10, 0)); cyl(0.12, 7, (u.x, u.y, 3.5), mat(0xeeeeee, 0.5), v=6)
        cyl(3.4, 1.0, (u.x, u.y, 7.2), mat([0xff7043, 0x29b6f6, 0xffee58, 0x66bb6a][k], 0.5), v=12, r2=0.2)
    fl = tube(0.6, 1.1, 0.4, (0, 0, 0), mat(0xff1744, 0.4, name='float'), v=24, name='lifefloat'); V['float'] = fl


def tracks():
    c = TRACKS
    box((300, 12, 1.0), (c.x, c.y, 0.0), mat(0x8d8478, 0.9, kind='slate', name='ballast'))
    for i in range(150): box((2, 9, 0.35), (c.x - 150 + i * 2, c.y, 0.6), mat(0x5d4037, 0.8, kind='wood', name='sleeper'))
    for sy in (-2.6, 2.6): box((300, 0.35, 0.45), (c.x, c.y + sy, 0.95), mat(0x9e9e9e, 0.3, metal=0.9, name='rail'))
    train = link(bpy.data.objects.new('train', None)); train.location = (c.x - 70, c.y, 0)
    tb = mat(0x37474f, 0.4, metal=0.4, name='trainbody')
    box((40, 10, 11), (-20, 0, 7), tb, train); box((2, 9, 6), (0.8, 0, 9), tb, train)
    box((0.3, 7, 3), (1.9, 0, 10), mat(0x90caf9, 0.1), train); box((0.4, 9.4, 1.2), (1.9, 0, 4.0), mat(0xffd600, 0.4), train)
    sphere(0.9, (2.0, 0, 7), mat(0xfffde7, 0.1, emit=25, name='trainlight'), seg=12).parent = train
    bpy.ops.object.light_add(type='SPOT', location=(3, 0, 7)); sl = bpy.context.active_object; sl.data.energy = 30000; sl.data.spot_size = math.radians(50)
    sl.rotation_euler = (0, math.radians(90), 0); sl.parent = train; sl.location = (3, 0, 7)
    V['train'] = train
    for (x, y) in [(-30, 20), (25, 22), (60, -20)]: tree(c.x + x, c.y + y, 1.0, 0)


def classroom():
    c = INT['classroom']; room(c, 34, 26, 13, 0xf3e5ab, 0x9c7a54, power=3200)
    box((16, 0.3, 6), (c.x, c.y + 12.7, 7), mat(0x1f3a2c, 0.9)); box((16.6, 0.4, 0.4), (c.x, c.y + 12.6, 3.9), mat(0x8d6e63, 0.6))
    for i, s in enumerate(["Monday", "2 + 2 = 4", "Spelling: future, voice, river"]):
        text(s, (c.x - 5 + i * 0.5, c.y + 12.5, 8.8 - i * 1.4), 0.7, mat(0xf5f5f5, 0.8), extrude=0.01)
    box((7, 3.4, 0.4), (c.x - 9, c.y + 8, 3.6), mat(0x6d4c41, 0.6, kind='wood')); box((6.6, 3, 3.4), (c.x - 9, c.y + 8, 1.7), mat(0x5d4037, 0.6, kind='wood'))
    sphere(0.5, (c.x - 10.5, c.y + 8, 4.3), mat(0xd32f2f, 0.3), seg=12)
    desk = mat(0xd7ccc8, 0.5, name='desktop'); leg = mat(0x546e7a, 0.4, metal=0.5)
    V['desks'] = []
    for r in range(3):
        for k in range(4):
            x = c.x - 10.5 + k * 7; y = c.y + 2 - r * 6.5
            box((4.4, 2.8, 0.3), (x, y, 3.2), desk); [box((0.25, 0.25, 3.1), (x + sx, y + sy, 1.55), leg) for sx in (-2, 2) for sy in (-1.2, 1.2)]
            box((2.6, 2.4, 0.3), (x, y - 2.6, 2.2), mat(0x1976d2, 0.5)); box((2.6, 0.3, 2.6), (x, y - 3.85, 3.4), mat(0x1976d2, 0.5))
            V['desks'].append(Vector((x, y - 2.6, 2.35)))
    for k in range(3): box((5, 0.3, 5), (c.x + 16.8, c.y - 6 + k * 7, 7), mat(0xbfe3ff, 0.2, emit=1.2))
    text("ABCDEFG", (c.x, c.y + 12.6, 11.4), 0.9, mat(0xc62828, 0.5), extrude=0.01)


def nora_room():
    c = INT['nora_room']; room(c, 22, 20, 12, 0xf8bbd0, 0x8d6e4f, power=2400)
    box((6, 10, 1.6), (c.x + 4, c.y + 3, 1.2), mat(0xffffff, 0.6)); box((5.6, 9.6, 0.8), (c.x + 4, c.y + 3, 2.3), mat(0xce93d8, 0.8, kind='fabric'))
    box((4, 2, 0.7), (c.x + 4, c.y + 7.2, 2.9), mat(0xf5f5f5, 0.8, kind='fabric'))
    V['note'] = [box((1.6, 2.1, 0.04), (c.x + 4, c.y + 4.2, 2.74), mat(0xfffde7, 0.8, name='note'), rot=(0, 0, 0.15), name='note'),
                 text("I'm leaving.", (c.x + 4, c.y + 4.4, 2.78), 0.24, mat(0x1a237e, 0.6), rot=(0, 0, 0.15), extrude=0.0),
                 text("Don't look for me.", (c.x + 4.05, c.y + 4.0, 2.78), 0.2, mat(0x1a237e, 0.6), rot=(0, 0, 0.15), extrude=0.0),
                 text("- Nora", (c.x + 4.2, c.y + 3.6, 2.78), 0.22, mat(0x1a237e, 0.6), rot=(0, 0, 0.15), extrude=0.0)]
    box((0.3, 5, 4), (c.x - 10.8, c.y + 2, 7), mat(0xffcc80, 0.2, emit=1.8))
    box((3, 1.4, 3), (c.x - 6, c.y + 8.6, 1.5), mat(0xffffff, 0.6)); sphere(0.7, (c.x - 6, c.y + 8.6, 3.6), mat(0xffe082, 0.3, emit=3), seg=12)
    box((5, 0.2, 3.6), (c.x - 2, c.y + 9.8, 7), mat(0xe1bee7, 0.6)); text("NORA", (c.x - 2, c.y + 9.65, 7), 0.9, mat(0x6a1b9a, 0.5), extrude=0.02)
    V['note_pos'] = Vector((c.x + 4, c.y + 4.0, 2.76))


def eli_room():
    c = INT['eli_room']; room(c, 22, 20, 12, 0xa5d6a7, 0x8d6e4f, power=2400)
    box((6, 10, 1.6), (c.x + 6, c.y + 2, 1.2), mat(0x5d4037, 0.6, kind='wood')); box((5.6, 9.6, 0.8), (c.x + 6, c.y + 2, 2.3), mat(0x1e88e5, 0.8, kind='fabric'))
    box((8, 3.4, 0.4), (c.x - 5, c.y + 8, 3.4), mat(0x8d5a32, 0.6, kind='wood'))
    for k in range(6): box((1.8, 1.4, 0.4), (c.x - 7 + k * 0.1, c.y + 8.3, 3.8 + k * 0.4), mat([0xc62828, 0x1565c0, 0x2e7d32][k % 3], 0.6))
    box((4.4, 0.2, 3), (c.x - 4, c.y + 9.8, 7.5), mat(0x263238, 0.5)); text("SPACE", (c.x - 4, c.y + 9.65, 7.5), 0.8, mat(0xffeb3b, 0.4, emit=1), extrude=0.02)
    box((0.3, 5, 4), (c.x + 10.8, c.y - 2, 7), mat(0x90caf9, 0.2, emit=1.2))
    ph = link(bpy.data.objects.new('phone', None))
    o = box((0.5, 0.15, 1.0), (0, 0, 0), mat(0x212121, 0.3), name='phonebody'); o.parent = ph
    o = box((0.42, 0.05, 0.8), (0, -0.08, 0), mat(0x80d8ff, 0.2, emit=2.5), name='phonescreen'); o.parent = ph
    V['phone'] = ph


def underwater():
    c = INT['underwater']
    wm = mat(0x0b3d4f, 0.9, emit=0.08, name='uwwall')
    box((70, 70, 0.4), (c.x, c.y, -0.2), mat(0x3e5a4a, 0.9, kind='slate', name='uwfloor'))
    for (sx, sy, w, d) in [(0, 35, 70, 0.4), (0, -35, 70, 0.4), (35, 0, 0.4, 70), (-35, 0, 0.4, 70)]: box((w, d, 50), (c.x + sx, c.y + sy, 25), wm)
    box((70, 70, 0.3), (c.x, c.y, 40), mat(0x4fc3f7, 0.1, emit=1.5, name='uwsurface'))
    for k in range(7):
        o = box((1.2, 0.05, 46), (c.x - 12 + k * 4, c.y + 8, 20), mat(0x80deea, 0.2, emit=1.2, alpha=0.12, name='ray'), rot=(0, math.radians(14), math.radians(20)))
    for k in range(14):
        for j in range(2): cyl(0.15, random.uniform(3, 7), (c.x + random.uniform(-25, 25), c.y + random.uniform(5, 25), 2.5), mat(0x2e7d32, 0.7), v=5)
    bubs = link(bpy.data.objects.new('bubbles', None)); bubs.location = (c.x, c.y, 10)
    bm = mat(0xe0f7fa, 0.05, alpha=0.5, name='bubble')
    for k in range(40):
        o = sphere(random.uniform(0.08, 0.3), (random.uniform(-3, 3), random.uniform(-3, 3), random.uniform(-2, 10)), bm, seg=8); o.parent = bubs
    for f, z in ((0, 4), (4000, 4 + 4000 * 0.12)):
        bubs.location = (c.x, c.y, z); bubs.keyframe_insert('location', frame=f)
    for fc in bubs.animation_data.action.fcurves:
        for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
    bpy.ops.object.light_add(type='AREA', location=(c.x, c.y, 30)); l = bpy.context.active_object; l.name = 'uw_light'
    l.data.energy = 30000; l.data.size = 30; l.data.color = (0.5, 0.85, 1.0); l.data.use_custom_distance = True; l.data.cutoff_distance = 80
    V['uw_light'] = l


def whisper_rings():
    """glowing sound-rings that appear around someone's head when their future voice speaks."""
    root = link(bpy.data.objects.new('whisper', None))
    for k in range(3):
        o = tube(0.95 + k * 0.4, 1.0 + k * 0.4, 0.04, (0, 0, -0.25 + k * 0.25), mat(0xfff3c4, 0.2, emit=3, alpha=0.6 - k * 0.15, name=f'ring{k}'), v=40, name=f'ring{k}')
        o.parent = root
    bpy.ops.object.light_add(type='POINT', location=(0, 0, 0)); l = bpy.context.active_object; l.data.energy = 120; l.data.color = (1, 0.9, 0.6)
    l.data.use_shadow = False; l.data.use_custom_distance = True; l.data.cutoff_distance = 12; l.parent = root; l.name = 'whisperlight'
    V['whisper'] = root


def build_extras():
    random.seed(77)
    square(); river_and_bridge(); city(); wedding(); fire_scene(); beach(); tracks()
    classroom(); nora_room(); eli_room(); underwater(); whisper_rings()
