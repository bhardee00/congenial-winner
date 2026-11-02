"""Town + interiors for 'The Wish'. Units are studs (R6 character = 5 studs tall). Camera-facing side of town is -Y."""
import bpy, bmesh, math, random
from mathutils import Vector
from lib import *

random.seed(13)
WELL = Vector((125, 76, 0))
INT = dict(bedroom=Vector((400, 0, 0)), library=Vector((500, 0, 0)), hospital=Vector((600, 0, 0)), diner=Vector((700, 0, 0)), arcade=Vector((800, 0, 0)))
CTRL = {}   # keyable controls: name -> (owner, data_path, index)


# ------------------------------------------------------------------ sky / light rig
def sky_and_sun():
    sc = bpy.context.scene
    w = bpy.data.worlds.new("Sky"); sc.world = w; w.use_nodes = True
    nt = w.node_tree; N = nt.nodes; L = nt.links
    bg = N["Background"]; out = N["World Output"]
    tc = N.new("ShaderNodeTexCoord"); sep = N.new("ShaderNodeSeparateXYZ"); L.new(tc.outputs["Generated"], sep.inputs[0])

    def grad(stops):
        r = N.new("ShaderNodeValToRGB"); L.new(sep.outputs["Z"], r.inputs[0]); cr = r.color_ramp
        cr.elements[0].position, cr.elements[0].color = stops[0][0], lin(stops[0][1])
        cr.elements[1].position, cr.elements[1].color = stops[-1][0], lin(stops[-1][1])
        for p, c in stops[1:-1]: e = cr.elements.new(p); e.color = lin(c)
        return r.outputs["Color"]
    day = grad([(0.0, 0xd8ecff), (0.08, 0xa8d4ff), (0.35, 0x5aa6f0), (0.8, 0x3b82e0)])
    dawn = grad([(0.0, 0xffc58a), (0.06, 0xffa070), (0.2, 0xd88aa0), (0.5, 0x6d7dc0), (0.9, 0x3a4f9a)])
    night = grad([(0.0, 0x2b3c72), (0.15, 0x1a2752), (0.6, 0x0b1230)])
    # clouds (day + dawn)
    mp = N.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1.4, 1.4, 4.0); L.new(tc.outputs["Generated"], mp.inputs[0])
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 2.2; nz.inputs["Detail"].default_value = 6; L.new(mp.outputs[0], nz.inputs[0])
    cl = N.new("ShaderNodeMapRange"); cl.inputs[1].default_value = 0.55; cl.inputs[2].default_value = 0.72; L.new(nz.outputs["Fac"], cl.inputs[0])
    hz = N.new("ShaderNodeMapRange"); hz.inputs[1].default_value = 0.02; hz.inputs[2].default_value = 0.12; L.new(sep.outputs["Z"], hz.inputs[0])
    cm = N.new("ShaderNodeMath"); cm.operation = 'MULTIPLY'; L.new(cl.outputs[0], cm.inputs[0]); L.new(hz.outputs[0], cm.inputs[1])
    cd = N.new("ShaderNodeMix"); cd.data_type = 'RGBA'; L.new(cm.outputs[0], cd.inputs[0]); L.new(day, cd.inputs[6]); cd.inputs[7].default_value = (1, 1, 1, 1)
    cw = N.new("ShaderNodeMix"); cw.data_type = 'RGBA'; L.new(cm.outputs[0], cw.inputs[0]); L.new(dawn, cw.inputs[6]); cw.inputs[7].default_value = lin(0xffd2b0)
    # stars (night)
    vo = N.new("ShaderNodeTexVoronoi"); vo.inputs["Scale"].default_value = 260; L.new(tc.outputs["Generated"], vo.inputs[0])
    st = N.new("ShaderNodeMapRange"); st.inputs[1].default_value = 0.06; st.inputs[2].default_value = 0.0; L.new(vo.outputs["Distance"], st.inputs[0])
    sm = N.new("ShaderNodeMath"); sm.operation = 'MULTIPLY'; sm.inputs[1].default_value = 4.0; L.new(st.outputs[0], sm.inputs[0])
    sh = N.new("ShaderNodeMath"); sh.operation = 'MULTIPLY'; L.new(sm.outputs[0], sh.inputs[0]); L.new(hz.outputs[0], sh.inputs[1])
    nst = N.new("ShaderNodeMix"); nst.data_type = 'RGBA'; nst.clamp_factor = True; L.new(sh.outputs[0], nst.inputs[0]); L.new(night, nst.inputs[6]); nst.inputs[7].default_value = (1, 1, 0.92, 1)
    # mixes driven by keyable values
    vd = N.new("ShaderNodeValue"); vd.name = "dawn"; vd.outputs[0].default_value = 0
    vn = N.new("ShaderNodeValue"); vn.name = "night"; vn.outputs[0].default_value = 0
    m1 = N.new("ShaderNodeMix"); m1.data_type = 'RGBA'; L.new(vd.outputs[0], m1.inputs[0]); L.new(cd.outputs[2], m1.inputs[6]); L.new(cw.outputs[2], m1.inputs[7])
    m2 = N.new("ShaderNodeMix"); m2.data_type = 'RGBA'; L.new(vn.outputs[0], m2.inputs[0]); L.new(m1.outputs[2], m2.inputs[6]); L.new(nst.outputs[2], m2.inputs[7])
    L.new(m2.outputs[2], bg.inputs["Color"])
    CTRL['dawn'] = (vd.outputs[0], 'default_value'); CTRL['night'] = (vn.outputs[0], 'default_value')
    CTRL['skyI'] = (bg.inputs["Strength"], 'default_value')

    bpy.ops.object.light_add(type='SUN', location=(0, 0, 50)); sun = bpy.context.active_object; sun.name = 'Sun'
    sun.data.angle = math.radians(1.5); sun.data.shadow_cascade_max_distance = 160
    CTRL['sun'] = sun
    # moon
    moon = sphere(40, (-420, 1400, 420), mat(0xfdf6dc, 0.5, emit=6, name='moon'), seg=32, name='moon')
    CTRL['moon'] = moon
    return sun


PRESETS = {
    'day':     dict(dawn=0, night=0, skyI=1.0, sun=3.6, col=(1.0, 0.96, 0.9), rot=(48, 0, -32), moon=False),
    'morning': dict(dawn=0.25, night=0, skyI=1.0, sun=3.2, col=(1.0, 0.9, 0.78), rot=(62, 0, -55), moon=False),
    'dawn':    dict(dawn=1, night=0, skyI=1.0, sun=2.6, col=(1.0, 0.68, 0.45), rot=(80, 0, 20), moon=False),
    'sunset':  dict(dawn=1, night=0, skyI=0.9, sun=2.4, col=(1.0, 0.6, 0.38), rot=(78, 0, -60), moon=False),
    'night':   dict(dawn=0, night=1, skyI=1.6, sun=1.0, col=(0.55, 0.65, 1.0), rot=(55, 0, 160), moon=True),
}


def key_light(f, preset):
    p = PRESETS[preset]
    for k in ('dawn', 'night', 'skyI'):
        sock, path = CTRL[k]; setattr(sock, path, p[k]); sock.keyframe_insert(path, frame=f)
    s = CTRL['sun']; s.data.energy = p['sun']; s.data.color = p['col']; s.rotation_euler = [math.radians(a) for a in p['rot']]
    s.data.keyframe_insert('energy', frame=f); s.data.keyframe_insert('color', frame=f); s.keyframe_insert('rotation_euler', frame=f)
    key_vis(CTRL['moon'], f, p['moon'])
    for lamp in CTRL.get('nightlights', []):
        lamp.data.energy = lamp['on'] if preset == 'night' else lamp['on'] * 0.15; lamp.data.keyframe_insert('energy', frame=f)
    for m in CTRL.get('windows', []):
        e = m.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
        e.default_value = 2.2 if preset == 'night' else 0.25; e.keyframe_insert('default_value', frame=f)


# ------------------------------------------------------------------ props
def tree(x, y, s=1.0, kind=0):
    trunk = mat(0x6d4a2b, 0.8, kind='wood'); leaves = [mat(0x3f9a3a, 0.75, kind='grass'), mat(0x4caf50, 0.75, kind='grass'), mat(0x2e7d32, 0.75, kind='grass')][kind % 3]
    cyl(0.7 * s, 7 * s, (x, y, 3.5 * s), trunk, v=10)
    for (dx, dy, dz, r) in [(0, 0, 8, 3.4), (1.8, 0.6, 7, 2.5), (-1.7, -0.5, 7.2, 2.6), (0.3, 1.5, 9.2, 2.4)]:
        sphere(r * s, (x + dx * s, y + dy * s, dz * s), leaves, seg=12)


def lamp_post(x, y, power=900):
    cyl(0.22, 9, (x, y, 4.5), mat(0x2b2f36, 0.4, metal=0.5), v=10)
    box((0.3, 2.2, 0.3), (x, y - 1.0 * (1 if y > 0 else -1), 9), mat(0x2b2f36, 0.4, metal=0.5))
    yy = y - 2.0 * (1 if y > 0 else -1)
    box((1.0, 1.2, 0.5), (x, yy, 8.7), mat(0xfff1c2, 0.3, emit=8, name='lampglass'))
    bpy.ops.object.light_add(type='POINT', location=(x, yy, 8.0)); l = bpy.context.active_object
    l.data.energy = power; l.data.color = (1.0, 0.82, 0.55); l.data.shadow_soft_size = 0.6; l.data.use_shadow = False
    l.data.use_custom_distance = True; l.data.cutoff_distance = 40; l['on'] = power
    CTRL.setdefault('nightlights', []).append(l)


def window_mat():
    m = mat(0xffe3a3, 0.2, emit=0.25, name=f'win{len(CTRL.get("windows", []))}')
    CTRL.setdefault('windows', []).append(m); return m


WINM = None
def house(x, front_y, w, d, h, wall, roofc, door_side=0, facing=-1, porch=True, name='house'):
    """facing=-1 -> front faces -Y (north side of street)."""
    global WINM
    if WINM is None: WINM = window_mat()
    cy = front_y + facing * -1 * d / 2
    box((w, d, h), (x, cy, h / 2), mat(wall, 0.6, kind='concrete'), name=name)
    box((w + 0.6, d + 0.6, 0.6), (x, cy, 0.3), mat(0x9e9e9e, 0.8, kind='concrete'))
    wedge(w + 2, d + 2.4, h * 0.45, (x, cy, h), mat(roofc, 0.6, kind='slate'))
    fy = front_y + facing * 0.08
    box((3, 0.4, 6.2), (x + door_side, fy, 3.1), mat(0x7a4a26, 0.6, kind='wood'))
    sphere(0.18, (x + door_side + 1.0, fy + facing * 0.3, 3.0), mat(0xd4af37, 0.3, metal=1))
    for wx in (-w * 0.3, w * 0.3):
        if abs(wx - door_side) < 3: continue
        box((3.4, 0.3, 3.0), (x + wx, fy, 5.0), WINM)
        box((4.0, 0.25, 3.6), (x + wx, fy - facing * 0.06, 5.0), mat(0xf5f5f5, 0.5))
        box((0.2, 0.42, 3.0), (x + wx, fy, 5.0), mat(0xf5f5f5, 0.5))
    if h > 12:
        for wx in (-w * 0.3, 0, w * 0.3):
            box((3.0, 0.3, 2.8), (x + wx, fy, h - 3.5), WINM); box((3.6, 0.25, 3.4), (x + wx, fy - facing * 0.06, h - 3.5), mat(0xf5f5f5, 0.5))
    if porch:
        py = front_y + facing * 3
        box((10, 6, 0.6), (x + door_side, py - facing * 0.0 + facing * -0.0, 0.3), mat(0xa0703f, 0.7, kind='wood'))
        for sx in (-4.6, 4.6): cyl(0.25, 7, (x + door_side + sx, front_y + facing * 5.6, 3.5), mat(0xf2f2f2, 0.5), v=10)
        box((10.6, 6.6, 0.4), (x + door_side, py, 7.1), mat(roofc, 0.6, kind='slate'))
        for i in range(2): box((3, 1.2, 0.35 - i * 0.12), (x + door_side, front_y + facing * (6.6 + i * 1.2), 0.15), mat(0xa0703f, 0.7, kind='wood'))


def car(x, y, heading, body=0x8d6e63, rust=True, name='car'):
    root = link(bpy.data.objects.new(name, None)); root.location = (x, y, 0); root.rotation_euler = (0, 0, math.radians(heading))
    bm_ = mat(body, 0.55, name='carbody' + name); dark = mat(0x222222, 0.6)
    box((5.4, 11, 2.4), (0, 0, 2.0), bm_, root)
    box((4.8, 5.6, 2.2), (0, 0.6, 4.2), bm_, root)
    box((4.6, 0.2, 1.7), (0, -2.3, 4.3), mat(0x9fc4d8, 0.05, alpha=0.6), root)   # windshield
    box((4.9, 4.4, 1.6), (0, 0.6, 4.3), mat(0x7fa4b8, 0.1), root)
    for sx in (-1, 1):
        for sy in (-3.4, 3.4):
            w = cyl(1.15, 0.9, (sx * 2.6, sy, 1.15), dark, root, rot=(0, math.radians(90), 0), v=20)
            cyl(0.55, 0.95, (sx * 2.6, sy, 1.15), mat(0xbdbdbd, 0.3, metal=0.8), root, rot=(0, math.radians(90), 0), v=12)
    for sx in (-1.8, 1.8): box((1.0, 0.2, 0.6), (sx, -5.55, 2.3), mat(0xfff5cc, 0.2, emit=1.5), root)
    for sx in (-1.8, 1.8): box((1.0, 0.2, 0.5), (sx, 5.55, 2.4), mat(0xd32f2f, 0.3, emit=1), root)
    box((5.6, 0.5, 0.5), (0, -5.6, 1.2), mat(0x9e9e9e, 0.3, metal=0.7), root); box((5.6, 0.5, 0.5), (0, 5.6, 1.2), mat(0x9e9e9e, 0.3, metal=0.7), root)
    if rust:
        for (px, py, pz, sx, sy, sz) in [(2.72, 1.5, 1.6, 0.05, 2.2, 1.0), (-2.72, -2.4, 2.4, 0.05, 1.6, 0.8), (1.2, -4.0, 3.22, 1.6, 1.4, 0.05), (2.72, -3.8, 2.6, 0.05, 1.0, 0.6)]:
            box((sx, sy, sz), (px, py, pz), mat(0x8d4b25, 0.9, kind='concrete'), root)
        box((0.05, 2.2, 1.2), (-2.72, 2.8, 2.1), mat(0x6f8fa3, 0.6), root)   # mismatched door panel
    return root


def books_obj(x0, y0, z0, length, height, depth, facing_y=-1, name='books'):
    bm = bmesh.new(); cols = [0xc62828, 0x1565c0, 0x2e7d32, 0xf9a825, 0x6a1b9a, 0xef6c00, 0x00838f, 0x4e342e, 0xad1457, 0x37474f]
    x = x0; me_cols = []
    while x < x0 + length - 0.3:
        t = random.uniform(0.25, 0.55); h = height * random.uniform(0.7, 0.98)
        r = bmesh.ops.create_cube(bm, size=1)['verts']
        for v in r: v.co = Vector((x + t / 2 + v.co.x * t, y0 + v.co.y * depth, z0 + h / 2 + v.co.z * h))
        me_cols.append(random.randrange(len(cols))); x += t + 0.03
    o = obj_from(bm, name, None)
    for c in cols: o.data.materials.append(mat(c, 0.6, name=f'book{c}'))
    for i, p in enumerate(o.data.polygons): p.material_index = me_cols[i // 6]
    return o


def shelf(x, y, w, h, facing=-1, rows=5):
    wood = mat(0x6d4c2f, 0.6, kind='wood')
    box((w, 2.2, 0.3), (x, y, h), wood); box((w, 0.2, h), (x, y - facing * 1.0, h / 2), wood)
    for sx in (-w / 2, w / 2): box((0.3, 2.2, h), (x + sx, y, h / 2), wood)
    for r in range(rows):
        z = 0.3 + r * (h - 0.3) / rows
        box((w, 2.2, 0.25), (x, y, z), wood)
        books_obj(x - w / 2 + 0.3, y, z + 0.12, w - 0.6, (h - 0.3) / rows - 0.4, 1.6)


def room(c, w, d, h, wall, floor, ceil=0xf2f2f2, floor_kind='wood', light=(1.0, 0.92, 0.8), power=4000):
    box((w, d, 0.4), (c.x, c.y, -0.2), mat(floor, 0.5, kind=floor_kind))
    box((w, d, 0.4), (c.x, c.y, h + 0.2), mat(ceil, 0.8))
    wm = mat(wall, 0.85, kind='concrete', name=f'wall{wall}')
    box((w, 0.4, h), (c.x, c.y + d / 2, h / 2), wm); box((w, 0.4, h), (c.x, c.y - d / 2, h / 2), wm)
    box((0.4, d, h), (c.x - w / 2, c.y, h / 2), wm); box((0.4, d, h), (c.x + w / 2, c.y, h / 2), wm)
    box((w, 0.3, 0.6), (c.x, c.y + d / 2 - 0.25, 0.3), mat(0xf5f5f5, 0.5))
    bpy.ops.object.light_add(type='AREA', location=(c.x, c.y - d * 0.15, h - 0.6)); l = bpy.context.active_object
    l.data.energy = power; l.data.size = min(w, d) * 0.7; l.data.color = light; l.data.use_custom_distance = True; l.data.cutoff_distance = max(w, d) * 1.2
    bpy.ops.object.light_add(type='POINT', location=(c.x, c.y - d * 0.4, h * 0.55)); l2 = bpy.context.active_object
    l2.data.energy = power * 0.25; l2.data.color = light; l2.data.use_shadow = False; l2.data.use_custom_distance = True; l2.data.cutoff_distance = max(w, d) * 1.2
    return l


# ------------------------------------------------------------------ town
def town():
    grass = mat(0x5ba83f, 0.85, kind='grass'); asph = mat(0x3a3d42, 0.8, kind='asphalt'); conc = mat(0xb9b7b0, 0.8, kind='concrete')
    hx0, hx1, hy0, hy1 = WELL.x - 12, WELL.x + 12, WELL.y - 12, WELL.y + 12
    for (x0, x1, y0, y1) in [(-300, 400, -260, hy0), (-300, 400, hy1, 400), (-300, hx0, hy0, hy1), (hx1, 400, hy0, hy1)]:
        box((x1 - x0, y1 - y0, 2), ((x0 + x1) / 2, (y0 + y1) / 2, -1), grass, name='ground')
    # road + sidewalks + dashes
    box((700, 16, 0.2), (50, 0, 0.0), asph, name='road')
    for sy in (-10.5, 10.5): box((700, 5, 0.5), (50, sy, 0.25), conc, name='sidewalk')
    for i in range(-14, 22): box((5, 0.4, 0.05), (i * 16, 0, 0.11), mat(0xf6c544, 0.5))
    # houses north side (front at y=20)
    house(-125, 20, 18, 14, 10, 0xd7ccc8, 0x5d4037)
    house(-95, 20, 18, 14, 10, 0xb3e5fc, 0x37474f)
    house(-65, 20, 20, 15, 11, 0x90caf9, 0x283593, name='milo_house')          # Milo's house (blue)
    house(-30, 20, 18, 14, 10, 0xfff176, 0x6d4c41, door_side=2, name='tess_house')  # Tess's house (yellow)
    box((7, 20, 0.12), (-43.5, 23, 0.06), conc)                                 # Tess driveway
    for (x, y) in [(-140, 30), (-110, 32), (-80, 33), (-48, 34), (-12, 33), (62, 32), (88, 30), (155, 30), (165, 60), (100, 70), (150, 92), (105, 95), (135, 100), (85, 60)]:
        tree(x, y, random.uniform(0.9, 1.25), random.randrange(3))
    # library (flat roof, used for rooftop scenes)
    lx = 35; lib_m = mat(0xc9b79c, 0.7, kind='concrete')
    box((32, 22, 16), (lx, 31, 8), lib_m, name='library')
    box((33, 23, 0.8), (lx, 31, 16.4), mat(0x9e8e78, 0.7, kind='concrete'))
    for sx in (-1, 1): box((33, 0.8, 1.6), (lx, 31 + sx * 11.2, 17.6), lib_m); box((0.8, 23, 1.6), (lx + sx * 16.2, 31, 17.6), lib_m)
    for i in range(6): cyl(0.9, 14, (lx - 12.5 + i * 5, 18.2, 7.4), mat(0xf0ebe0, 0.6), v=16)
    box((34, 5, 1.2), (lx, 18.5, 0.6), mat(0xd8d2c6, 0.7, kind='concrete')); box((30, 3, 1.4), (lx, 18.5, 15.0), mat(0xf0ebe0, 0.6))
    text("LIBRARY", (lx, 16.9, 15.0), 1.6, mat(0x3e2723, 0.5), extrude=0.15)
    box((5, 0.4, 8), (lx, 19.95, 4), mat(0x5d3a1f, 0.6, kind='wood'))
    for wx in (-10, -5, 5, 10): box((3, 0.3, 6), (lx + wx, 19.95, 5.5), WINM or window_mat())
    box((5, 4, 4), (lx + 9, 36, 18.6), mat(0xb0a58f, 0.7, kind='concrete'))                  # roof stair hut
    box((3.4, 3, 2.2), (lx - 10, 37, 18.0), mat(0x9e9e9e, 0.5, metal=0.6)); box((3.4, 3, 2.2), (lx - 5.5, 37, 18.0), mat(0x9e9e9e, 0.5, metal=0.6))
    box((7, 9, 0.12), (lx - 2, 27, 16.86), mat(0xc0392b, 0.9, kind='fabric', name='blanket'))   # picnic blanket on roof
    for i in range(6): box((7, 0.6, 0.13), (lx - 2, 23 + i * 1.5, 16.87), mat(0xf5f5f5, 0.9, kind='fabric'))
    # diner + arcade (south side, facing +Y)
    box((26, 18, 11), (-30, -30, 5.5), mat(0xeceff1, 0.5), name='diner')
    box((26.4, 0.6, 2.2), (-30, -20.9, 9.6), mat(0xd32f2f, 0.5)); text("DINER", (-30, -20.5, 9.6), 1.8, mat(0xff5252, 0.3, emit=5), rot=(math.radians(90), 0, math.pi))
    for wx in (-8, 0, 8): box((6, 0.3, 4), (-30 + wx, -20.95, 4.4), WINM or window_mat())
    box((24, 18, 12), (0, -31, 6), mat(0x4a148c, 0.6), name='arcade')
    text("ARCADE", (0, -21.7, 9.6), 2.2, mat(0xe040fb, 0.3, emit=7), rot=(math.radians(90), 0, math.pi))
    box((6, 0.3, 6.5), (0, -21.9, 3.25), mat(0x111111, 0.2))
    house(-65, -20, 18, 14, 10, 0xffccbc, 0x4e342e, facing=1, porch=False); house(30, -20, 20, 14, 10, 0xc5e1a5, 0x33691e, facing=1, porch=False)
    house(-95, -20, 18, 14, 10, 0xf8bbd0, 0x3e2723, facing=1, porch=False); house(60, -20, 18, 14, 10, 0xb2dfdb, 0x263238, facing=1, porch=False)
    # school
    sx = 125; brick = mat(0xa8442f, 0.8, kind='brick')
    box((44, 26, 18), (sx, 33, 9), brick, name='school')
    box((45, 27, 0.8), (sx, 33, 18.4), mat(0x5d4037, 0.7))
    for r in (5, 12):
        for i in range(-4, 5):
            if i == 0 and r == 5: continue
            box((3, 0.3, 3.6), (sx + i * 4.6, 19.95, r), WINM or window_mat()); box((3.6, 0.2, 4.2), (sx + i * 4.6, 19.9, r), mat(0xf5f5f5, 0.5))
    box((7, 0.5, 7.5), (sx, 19.9, 3.75), mat(0x1e3a5f, 0.4)); box((10, 3, 0.6), (sx, 18, 8), mat(0xeeeeee, 0.6))
    text("SCHOOL", (sx, 19.4, 15.5), 2.4, mat(0xf5f5f5, 0.5), extrude=0.2)
    box((9, 9, 12), (sx, 30, 24), brick, name='tower')                                    # clock tower
    wedge(10.5, 10.5, 6, (sx, 30, 30), mat(0x37474f, 0.6, kind='slate'))
    cyl(3.3, 0.4, (sx, 25.4, 25), mat(0xfffde7, 0.4, emit=0.6, name='clockface'), rot=(math.radians(90), 0, 0), v=40)
    tube(3.2, 3.6, 0.5, (sx, 25.1, 25), mat(0x212121, 0.4), name='clockrim').rotation_euler = (math.radians(90), 0, 0)
    for k in range(12):
        a = k / 12 * math.tau; box((0.18, 0.1, 0.6), (sx + math.sin(a) * 2.7, 25.1, 25 + math.cos(a) * 2.7), mat(0x212121, 0.4), rot=(0, -a, 0))
    hh = box((0.3, 0.12, 1.9), (sx - 0.02, 25.0, 25.9), mat(0x111111, 0.4), name='hourhand'); hh.rotation_euler = (0, math.radians(0.5 * 1), 0)
    mh = box((0.22, 0.12, 2.7), (sx, 24.95, 25), mat(0x111111, 0.4), name='minhand')
    hub = bpy.data.objects.new('minpivot', None); link(hub); hub.location = (sx, 24.95, 25); mh.parent = hub; mh.location = (0, 0, 1.25)
    hub.rotation_euler = (0, math.radians(-6), 0)                                       # 11:59
    hub2 = bpy.data.objects.new('hrpivot', None); link(hub2); hub2.location = (sx, 25.0, 25); hh.parent = hub2; hh.location = (0, 0, 0.85)
    hub2.rotation_euler = (0, math.radians(-0.5), 0)
    CTRL['minhand'] = hub
    # street lights
    for i in range(-7, 9): lamp_post(i * 22 + 5, 11.5 if i % 2 else -11.5, 700)
    for (x, y) in [(110, 60), (140, 60)]: lamp_post(x, y, 500)
    # hills
    for i in range(10):
        sphere(random.uniform(60, 90), (-300 + i * 80, 380, -20), mat(0x6aa85a, 0.9, kind='grass'), scale=(1.5, 0.7, 0.5), seg=24)
    birthday_props()
    well()


def birthday_props():
    # banner across the street in front of Milo's house + balloons on his porch
    box((0.12, 0.12, 0.12), (-65, 0, 11), mat(0xffffff))
    for sx in (-80, -50): cyl(0.25, 12, (sx, -11.5 if sx < -60 else 11.5, 6), mat(0x8d6e63, 0.6, kind='wood'), v=8)
    ban = box((22, 0.25, 3.2), (-65, 0, 10.4), mat(0xffffff, 0.6, kind='fabric'), name='banner')
    ban.rotation_euler = (0, 0, math.atan2(23, 30) * 0.0)
    text("HAPPY 13th BIRTHDAY!", (-65, -0.2, 10.4), 1.5, mat(0xe91e63, 0.5), extrude=0.05)
    cols = [0xe53935, 0xfdd835, 0x1e88e5, 0x43a047, 0xab47bc, 0xff7043]
    for i, (bx, by, bz) in enumerate([(-71, 15, 9), (-72.5, 15.5, 10.4), (-70, 16, 10.8), (-58, 15, 9.4), (-59.5, 15.6, 10.6), (-57, 16, 11.2)]):
        sphere(1.0, (bx, by, bz), mat(cols[i % 6], 0.25), scale=(1, 1, 1.18), seg=16)
        cyl(0.03, bz - 1.2, (bx, by, (bz - 1.2) / 2), mat(0xeeeeee, 0.5), v=4)


def well():
    c = WELL; stone = mat(0x8f8f8f, 0.85, kind='slate', name='wellstone'); stone2 = mat(0x7a7570, 0.85, kind='slate', name='wellstone2')
    R = 7.0; plaza = mat(0xb0aca4, 0.85, kind='slate', name='plaza')
    bm = bmesh.new(); n = 64; inner = []; outer = []
    for i in range(n):
        a = i / n * math.tau; d = Vector((math.cos(a), math.sin(a), 0))
        inner.append(bm.verts.new(c + d * R)); s = 12 / max(abs(d.x), abs(d.y)); outer.append(bm.verts.new(c + d * s))
    for i in range(n):
        j = (i + 1) % n; bm.faces.new([inner[i], inner[j], outer[j], outer[i]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:
        if f.normal.z < 0: f.normal_flip()
    obj_from(bm, 'plaza', plaza, loc=(0, 0, 0.02))
    tube(R, R + 0.9, 10.2, c + Vector((0, 0, -10.2)), stone, v=48, name='pitwall')
    # low rim wall above ground with opening on the south side for the stairs
    for k in range(24):
        a = k / 24 * math.tau
        if abs(math.degrees(a) - 270) < 14: continue
        p = c + Vector((math.cos(a), math.sin(a), 0)) * (R + 0.55)
        box((1.95, 1.2, 1.3), (p.x, p.y, 0.65), stone2 if k % 2 else stone, rot=(0, 0, a + math.pi / 2))
    cyl(R, 0.4, c + Vector((0, 0, -10.2)), stone2, v=48)                                     # floor
    tube(3.6, 4.4, 0.7, c + Vector((0, 0, -10.0)), stone, v=40, name='poolrim')
    wm = bpy.data.materials.new('wellwater'); wm.use_nodes = True; N = wm.node_tree.nodes; L = wm.node_tree.links
    b = N["Principled BSDF"]; b.inputs["Base Color"].default_value = lin(0x050a12); b.inputs["Roughness"].default_value = 0.03
    b.inputs["Specular IOR Level"].default_value = 0.8; b.inputs["Emission Color"].default_value = lin(0xffe7a1); b.inputs["Emission Strength"].default_value = 0
    nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 2.5; bump = N.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.03
    L.new(nz.outputs["Fac"], bump.inputs["Height"]); L.new(bump.outputs["Normal"], b.inputs["Normal"])
    cyl(3.6, 0.2, c + Vector((0, 0, -9.6)), wm, v=48, name='water')
    CTRL['water_emit'] = (b.inputs["Emission Strength"], 'default_value'); CTRL['water_col'] = (b.inputs["Emission Color"], 'default_value')
    bpy.ops.object.light_add(type='POINT', location=c + Vector((0, 0, -8.5))); gl = bpy.context.active_object
    gl.data.energy = 0; gl.data.color = (1, 0.85, 0.5); gl.data.shadow_soft_size = 3; gl.data.use_custom_distance = True; gl.data.cutoff_distance = 120
    CTRL['well_light'] = gl
    # spiral steps: 22 steps from the south opening down to the floor
    for i in range(22):
        a = math.radians(-90 + i * 15); top = -0.45 * (i + 1)
        rm = (R - 0.05 + 4.4) / 2; p = c + Vector((math.cos(a), math.sin(a), 0)) * rm
        hgt = top + 10.2
        box((R - 4.45, 1.75, hgt), (p.x, p.y, top - hgt / 2), stone if i % 2 else stone2, rot=(0, 0, a), name='step')
    # old wooden frame + roof + bucket
    wood = mat(0x6b4a2e, 0.8, kind='wood')
    for s in (-1, 1): box((0.9, 0.9, 7.5), (c.x + s * (R + 1.6), c.y + 3, 3.75), wood)
    box((2 * R + 4.5, 0.7, 0.7), (c.x, c.y + 3, 7.3), wood)
    wedge(2 * R + 6, 5, 2.6, (c.x, c.y + 3, 7.65), mat(0x5d4037, 0.7, kind='slate'))
    cyl(0.07, 5.5, (c.x, c.y + 3, 4.6), mat(0xc8b48a, 0.9), v=6)
    cyl(0.75, 1.1, (c.x, c.y + 3, 1.6), wood, v=12)
    # lanterns on the frame
    for s in (-1, 1):
        box((0.6, 0.6, 0.9), (c.x + s * (R + 1.6), c.y + 2.4, 5.2), mat(0xffcf7a, 0.3, emit=10))
        bpy.ops.object.light_add(type='POINT', location=(c.x + s * (R + 1.6), c.y + 1.8, 5.2)); l = bpy.context.active_object
        l.data.energy = 600; l.data.color = (1, 0.75, 0.45); l.data.use_shadow = True; l.data.shadow_soft_size = 0.4; l['on'] = 600
        l.data.use_custom_distance = True; l.data.cutoff_distance = 45
        CTRL.setdefault('nightlights', []).append(l)
    bpy.ops.object.light_add(type='POINT', location=c + Vector((0, -2, -4))); l = bpy.context.active_object
    l.data.energy = 900; l.data.color = (0.8, 0.85, 1.0); l.data.use_shadow = False; l['on'] = 900; l.data.use_custom_distance = True; l.data.cutoff_distance = 20
    CTRL.setdefault('nightlights', []).append(l)


# ------------------------------------------------------------------ interiors
def bedroom():
    c = INT['bedroom']; room(c, 24, 22, 12, 0x9fb8d6, 0x8d6e4f, power=2600)
    bw = c.y + 10.8
    desk = mat(0x8d5a32, 0.6, kind='wood')
    box((10, 4, 0.4), (c.x, bw - 2.2, 3.4), desk); [box((0.4, 4, 3.4), (c.x + s, bw - 2.2, 1.7), desk) for s in (-4.8, 4.8)]
    random.seed(4)
    for k, (bx, n) in enumerate([(-3.6, 7), (-2.2, 5), (2.8, 9), (4.0, 4)]):        # stacks of books
        z = 3.6
        for i in range(n):
            t = random.uniform(0.35, 0.6); box((random.uniform(1.6, 2.1), 1.5, t), (c.x + bx, bw - 2.4, z + t / 2), mat([0xc62828, 0x1565c0, 0x2e7d32, 0xf9a825, 0x6a1b9a][(i + k) % 5], 0.6), rot=(0, 0, random.uniform(-0.2, 0.2))); z += t
    cyl(0.2, 2.4, (c.x + 1.2, bw - 1.6, 4.8), mat(0x263238, 0.4), v=8); cyl(0.9, 0.8, (c.x + 1.2, bw - 1.9, 6.0), mat(0x2e7d32, 0.4), r2=0.4, v=16)
    bpy.ops.object.light_add(type='POINT', location=(c.x + 1.2, bw - 2.6, 5.6)); l = bpy.context.active_object; l.data.energy = 250; l.data.color = (1, 0.85, 0.6); l.data.use_custom_distance = True; l.data.cutoff_distance = 20
    # plan board (cork) with the wish written on it
    box((9, 0.3, 4.6), (c.x - 1, bw - 0.15, 8.4), mat(0xb5835a, 0.9, kind='fabric'))
    text("MY WISH:", (c.x - 1, bw - 0.35, 9.7), 0.8, mat(0x1a1a1a, 0.6), extrude=0.02)
    text("SMARTEST PERSON ALIVE", (c.x - 1, bw - 0.35, 8.4), 0.62, mat(0xc62828, 0.6), extrude=0.02)
    for (px, pz, r) in [(-4.6, 9.9, 0.1), (2.7, 10.2, -0.08), (-4.4, 6.9, 0.12), (2.8, 6.8, -0.1), (-1.0, 6.7, 0.0)]:
        box((1.4, 0.05, 1.1), (c.x - 1 + px, bw - 0.32, pz), mat(0xfff9c4, 0.7), rot=(0, r, 0))
    text("since age 7", (c.x - 1, bw - 0.35, 7.3), 0.42, mat(0x1a1a1a, 0.6), extrude=0.02)
    # chalkboard with equations
    cbx = c.x - 9; box((0.3, 9, 5), (c.x - 11.8, c.y + 4, 6.6), mat(0x1f3a2c, 0.9))
    for i, s in enumerate(["E = mc²", "a² + b² = c²", "∫ x dx = x²/2", "π ≈ 3.14159"]):
        try: text(s, (c.x - 11.6, c.y + 4, 8.2 - i * 1.1), 0.6, mat(0xf5f5f5, 0.8), rot=(math.radians(90), 0, math.radians(-90)), extrude=0.01)
        except Exception: pass
    # calendar with Tess's birthday circled
    box((3.6, 0.2, 4.2), (c.x + 8, bw - 0.12, 7.8), mat(0xfafafa, 0.7))
    box((3.6, 0.22, 0.9), (c.x + 8, bw - 0.14, 9.5), mat(0xc62828, 0.6))
    for r in range(4):
        for k in range(5): box((0.55, 0.05, 0.55), (c.x + 6.6 + k * 0.7, bw - 0.25, 8.4 - r * 0.75), mat(0xe0e0e0, 0.7))
    tube(0.36, 0.48, 0.05, (c.x + 8.0, bw - 0.3, 7.65), mat(0xd50000, 0.5), name='circle').rotation_euler = (math.radians(90), 0, 0)
    text("TESS!", (c.x + 8.0, bw - 0.3, 6.35), 0.42, mat(0xd50000, 0.5), extrude=0.01)
    # bed + window
    box((6, 10, 1.6), (c.x + 8.5, c.y - 3, 1.2), mat(0x5d4037, 0.6, kind='wood')); box((5.6, 9.6, 0.8), (c.x + 8.5, c.y - 3, 2.3), mat(0x1565c0, 0.8, kind='fabric'))
    box((4, 2, 0.7), (c.x + 8.5, c.y + 1.0, 2.9), mat(0xf5f5f5, 0.8, kind='fabric'))
    box((0.3, 5, 4), (c.x + 11.8, c.y - 3, 7), mat(0xbfe3ff, 0.2, emit=1.4))
    box((8, 6, 0.1), (c.x, c.y - 3, 0.06), mat(0x7e57c2, 0.9, kind='fabric'))
    # trophy shelf
    box((6, 1.6, 0.3), (c.x - 7, bw - 0.9, 5.6), mat(0x8d5a32, 0.6, kind='wood'))
    for k in range(3):
        gold = mat(0xffc107, 0.25, metal=1, name='gold')
        cyl(0.3, 0.3, (c.x - 9 + k * 2, bw - 0.9, 5.9), gold, v=12); cyl(0.5, 0.9, (c.x - 9 + k * 2, bw - 0.9, 6.5), gold, r2=0.2, v=12)


def library_in():
    c = INT['library']; room(c, 40, 30, 15, 0xd7c4a8, 0x6d4c41, power=3000, light=(1.0, 0.88, 0.7))
    for i in range(-2, 3): shelf(c.x + i * 7.5, c.y + 13.6, 7, 12)
    for side in (-1, 1):
        for j in range(2): shelf(c.x + side * 13, c.y + 4 - j * 8, 7, 9)
    wood = mat(0x7b4f2c, 0.55, kind='wood')
    box((12, 6, 0.4), (c.x, c.y - 2, 3.4), wood)
    for sx in (-5.5, 5.5):
        for sy in (-4.5, 0.5): box((0.4, 0.4, 3.4), (c.x + sx, c.y + sy, 1.7), wood)
    for sx in (-3.5, 3.5): box((2.2, 2.2, 0.3), (c.x + sx, c.y - 6.4, 2.2), wood); box((2.2, 0.3, 3), (c.x + sx, c.y - 7.4, 3.4), wood)
    lm = mat(0x1b5e20, 0.3, metal=0.3); cyl(0.15, 1.6, (c.x + 4.6, c.y - 0.5, 4.4), mat(0xc9a227, 0.3, metal=1), v=8)
    box((2.2, 0.9, 0.6), (c.x + 4.6, c.y - 0.5, 5.3), lm)
    bpy.ops.object.light_add(type='POINT', location=(c.x + 4.6, c.y - 0.8, 4.9)); l = bpy.context.active_object; l.data.energy = 350; l.data.color = (1, 0.85, 0.55); l.data.use_custom_distance = True; l.data.cutoff_distance = 25
    card = mat(0xc19a6b, 0.8, kind='fabric', name='cardboard')
    random.seed(9)
    for (bx, by, n) in [(1.2, 0.4, 3), (-1.2, 0.6, 2), (8.8, -1, 4), (10.8, 0.4, 3), (-9, -5, 2)]:
        for k in range(n):
            box((2.0, 1.6, 1.2), (c.x + bx + random.uniform(-0.1, 0.1), c.y + by, 3.6 + k * 1.22 if abs(bx) < 6 else 0.6 + k * 1.22), card, rot=(0, 0, random.uniform(-0.1, 0.1)))
    for k in range(9):
        box((0.9, 1.2, 0.03), (c.x + random.uniform(-4.5, 4.5), c.y - 2 + random.uniform(-2, 2), 3.62 + k * 0.004), mat(0xf3e9d2, 0.8), rot=(0, 0, random.uniform(-0.6, 0.6)))
    box((1.6, 2.1, 0.035), (c.x + 0.6, c.y - 3.4, 3.64), mat(0xe8d9b0, 0.8, name='oldpaper'))
    box((0.3, 8, 10), (c.x - 19.7, c.y - 5, 7), mat(0xbfe3ff, 0.2, emit=0.8, name='libwindow'))


def hospital():
    c = INT['hospital']; room(c, 22, 20, 12, 0xe8f1ef, 0xcfd8dc, floor_kind='concrete', power=3200, light=(0.92, 0.97, 1.0))
    by = c.y + 4
    box((6, 11, 1.5), (c.x, by, 2.0), mat(0xb0bec5, 0.4, metal=0.4)); box((5.6, 10.6, 0.9), (c.x, by, 3.1), mat(0xffffff, 0.8, kind='fabric'))
    box((6.2, 0.4, 4), (c.x, by + 5.7, 3), mat(0xb0bec5, 0.4, metal=0.4)); box((4.5, 2.2, 0.8), (c.x, by + 3.8, 3.9), mat(0xf5f5f5, 0.8, kind='fabric'))
    box((5.7, 6, 0.4), (c.x, by - 2.2, 3.6), mat(0x80cbc4, 0.8, kind='fabric', name='hospblanket'))
    box((2.6, 1.6, 2.2), (c.x + 5.5, by + 3, 6), mat(0x37474f, 0.4)); box((2.2, 0.1, 1.6), (c.x + 5.5, by + 2.18, 6), mat(0x00e676, 0.3, emit=3, name='monitor'))
    cyl(0.12, 6, (c.x + 5.5, by + 3, 3), mat(0x90a4ae, 0.3, metal=0.8), v=8)
    cyl(0.1, 7, (c.x - 5, by + 1, 3.5), mat(0x90a4ae, 0.3, metal=0.8), v=8); box((1.2, 0.4, 1.6), (c.x - 5, by + 1, 6.6), mat(0xe3f2fd, 0.3, alpha=0.7))
    box((0.3, 7, 5), (c.x - 10.8, c.y - 1, 7), mat(0xffe9b8, 0.2, emit=2.2, name='hospwin'))
    for k in range(4): box((0.4, 1.6, 9), (c.x - 10.4, c.y - 5 + k * 1.7, 6), mat(0xa5d6a7, 0.9, kind='fabric'))
    box((2.4, 2.4, 3.2), (c.x - 6, by - 4, 1.6), mat(0x8d6e63, 0.6, kind='wood'))
    sphere(0.6, (c.x - 6, by - 4, 3.8), mat(0xe91e63, 0.4), seg=12); cyl(0.4, 1, (c.x - 6, by - 4, 3.4), mat(0xeceff1, 0.2, alpha=0.6), v=12)


def diner_in():
    c = INT['diner']; room(c, 30, 22, 12, 0xfff3e0, 0xeeeeee, floor_kind='concrete', power=3400)
    f = bpy.data.materials.new('checker'); f.use_nodes = True; N = f.node_tree.nodes; ck = N.new("ShaderNodeTexChecker"); ck.inputs["Scale"].default_value = 40
    ck.inputs["Color1"].default_value = lin(0xf5f5f5); ck.inputs["Color2"].default_value = lin(0x212121); f.node_tree.links.new(ck.outputs["Color"], N["Principled BSDF"].inputs["Base Color"])
    box((30, 22, 0.05), (c.x, c.y, 0.03), f)
    red = mat(0xc62828, 0.35); chrome = mat(0xcfd8dc, 0.2, metal=1)
    tx, ty = c.x, c.y + 4
    box((8, 4, 0.4), (tx, ty, 3.4), mat(0x80deea, 0.25)); cyl(0.3, 3.2, (tx, ty, 1.6), chrome, v=12)
    for s in (-1, 1):
        box((8, 2.4, 1.6), (tx, ty + s * 3.6, 1.6), red); box((8, 0.9, 3.8), (tx, ty + s * 4.7, 2.7), red)
    for s in (-1, 1):  # pancake stacks with syrup + butter
        px = tx + s * 2
        cyl(1.3, 0.12, (px, ty - s * 0.6, 3.66), mat(0xffffff, 0.3), v=24)
        for k in range(5): cyl(1.0, 0.28, (px, ty - s * 0.6, 3.85 + k * 0.29), mat(0xd9a05b, 0.6), v=24)
        cyl(1.02, 0.08, (px, ty - s * 0.6, 5.3), mat(0x7a3b0c, 0.1), v=24); box((0.5, 0.5, 0.3), (px, ty - s * 0.6, 5.45), mat(0xfff59d, 0.4))
    cyl(0.45, 1.6, (tx + 3.4, ty, 4.4), mat(0xf8bbd0, 0.3), r2=0.6, v=16); cyl(0.06, 1.2, (tx + 3.5, ty, 5.6), mat(0xe53935, 0.3), v=6)
    box((22, 3, 3.6), (c.x, c.y - 7, 1.8), mat(0xd32f2f, 0.4)); box((22.4, 3.4, 0.3), (c.x, c.y - 7, 3.7), chrome)
    for k in range(5): cyl(0.8, 0.4, (c.x - 8 + k * 4, c.y - 4.6, 2.6), red, v=16); cyl(0.15, 2.4, (c.x - 8 + k * 4, c.y - 4.6, 1.2), chrome, v=8)
    for k in range(3): box((5, 0.3, 4), (c.x - 9 + k * 9, c.y + 10.8, 7), mat(0xbfe3ff, 0.2, emit=1.2))
    text("DINER", (c.x + 9, c.y + 10.6, 10), 1.0, mat(0xff1744, 0.3, emit=6))


def arcade_in():
    c = INT['arcade']; room(c, 30, 24, 12, 0x1a1033, 0x151020, floor_kind='fabric', power=500, light=(0.6, 0.5, 1.0))
    cols = [0xff1744, 0x00e5ff, 0x76ff03, 0xffea00, 0xd500f9, 0xff9100]
    for i in range(6):
        x = c.x - 12.5 + i * 5
        for (y, h) in [(c.y + 10.5, 0)]:
            body = mat(cols[i % 6], 0.4, name=f'cab{i}')
            box((3.6, 3, 8), (x, y, 4), mat(0x222222, 0.4)); box((3.8, 3.2, 0.4), (x, y, 8.2), body)
            box((3.0, 0.2, 2.6), (x, y - 1.55, 5.8), mat(cols[(i + 2) % 6], 0.2, emit=5, name=f'scr{i}'))
            box((3.6, 1.8, 0.4), (x, y - 2.1, 3.6), mat(0x333333, 0.4)); sphere(0.22, (x - 0.6, y - 2.4, 4.0), mat(0xff1744, 0.3), seg=10)
            box((3.8, 0.2, 1.0), (x, y - 1.55, 7.6), mat(cols[i % 6], 0.2, emit=8))
    for k, y in enumerate((c.y - 11.6, c.y + 11.6)):
        box((30, 0.2, 0.3), (c.x, y, 10.5), mat(cols[k * 2 + 1], 0.2, emit=12))
    for k, x in enumerate((c.x - 14.6, c.x + 14.6)): box((0.2, 24, 0.3), (x, c.y, 10.5), mat(cols[k * 2 + 3], 0.2, emit=12))
    for i in range(3):
        bpy.ops.object.light_add(type='POINT', location=(c.x - 8 + i * 8, c.y + 6, 6)); l = bpy.context.active_object
        l.data.energy = 900; l.data.color = [(1, 0.3, 0.8), (0.3, 0.8, 1), (0.6, 0.3, 1)][i]; l.data.use_custom_distance = True; l.data.cutoff_distance = 28
    sphere(0.01, (c.x, c.y, 0), mat(0xffffff))
    # claw machine + prize ticket counter
    box((4, 4, 7), (c.x + 11, c.y + 1, 3.5), mat(0xff4081, 0.4)); box((3.4, 3.4, 3.2), (c.x + 11, c.y + 1, 5.4), mat(0xe1f5fe, 0.1, alpha=0.3))
    for k in range(6): sphere(0.5, (c.x + 10 + (k % 3) * 0.9, c.y + 0.4 + (k // 3) * 0.9, 4.2), mat(cols[k], 0.4), seg=10)


def build_all():
    sky_and_sun(); town(); bedroom(); library_in(); hospital(); diner_in(); arcade_in()
