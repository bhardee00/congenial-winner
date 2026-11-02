"""Classic R6 character: 2x2x1 torso, 1x2x1 limbs, rounded head, real Roblox clothing templates mapped with the
standard 585x559 template layout, real hair accessory meshes, swap-able face decals. Faces -Y by default."""
import bpy, bmesh, math, os, sys, json
from mathutils import Vector, Matrix
from lib import *
sys.path.insert(0, os.path.join(ROOT, 'pipeline')); import rbx

TW, TH = 585.0, 559.0
# template rects (x, y, w, h) per face, in the R6 torso / limb layout
TORSO = dict(F=(231, 74, 128, 128), B=(427, 74, 128, 128), R=(165, 74, 64, 128), L=(361, 74, 64, 128), U=(231, 8, 128, 64), D=(231, 204, 128, 64))
RLIMB = dict(L=(19, 355, 64, 128), B=(85, 355, 64, 128), R=(151, 355, 64, 128), F=(217, 355, 64, 128), U=(217, 289, 64, 64), D=(217, 485, 64, 64))
LLIMB = dict(F=(308, 355, 64, 128), L=(374, 355, 64, 128), B=(440, 355, 64, 128), R=(506, 355, 64, 128), U=(308, 289, 64, 64), D=(308, 485, 64, 64))
FACES = ['smile', 'happy', 'angry', 'sad', 'cry', 'closed', 'closed_sad', 'shock', 'neutral', 'worried', 'whisper', 'smirk', 'laugh']


def uvbox(sx, sy, sz, rects, m, name, parent, loc):
    """Box centred at origin; character faces -Y, character right = -X. Each face gets its template rect."""
    hx, hy, hz = sx / 2, sy / 2, sz / 2
    # corners per face listed as (image top-left, top-right, bottom-right, bottom-left) as seen from outside
    F = {
        'F': [(-hx, -hy, hz), (hx, -hy, hz), (hx, -hy, -hz), (-hx, -hy, -hz)],      # viewer at -Y: left = -X
        'B': [(hx, hy, hz), (-hx, hy, hz), (-hx, hy, -hz), (hx, hy, -hz)],          # viewer at +Y: left = +X
        'R': [(-hx, hy, hz), (-hx, -hy, hz), (-hx, -hy, -hz), (-hx, hy, -hz)],      # viewer at -X: left = +Y(back)
        'L': [(hx, -hy, hz), (hx, hy, hz), (hx, hy, -hz), (hx, -hy, -hz)],          # viewer at +X: left = -Y(front)
        'U': [(-hx, hy, hz), (hx, hy, hz), (hx, -hy, hz), (-hx, -hy, hz)],          # image bottom touches front
        'D': [(-hx, -hy, -hz), (hx, -hy, -hz), (hx, hy, -hz), (-hx, hy, -hz)],      # image top touches front
    }
    bm = bmesh.new(); uvl = bm.loops.layers.uv.new()
    for k, cs in F.items():
        x, y, w, h = rects[k]; inset = 0.6
        uvs = [((x + inset) / TW, 1 - (y + inset) / TH), ((x + w - inset) / TW, 1 - (y + inset) / TH),
               ((x + w - inset) / TW, 1 - (y + h - inset) / TH), ((x + inset) / TW, 1 - (y + h - inset) / TH)]
        f = bm.faces.new([bm.verts.new(c) for c in cs])
        for lp, uv in zip(f.loops, uvs): lp[uvl].uv = uv
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return obj_from(bm, name, m, parent, loc)


def head_mesh(m, parent, name):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=40, radius1=0.6, radius2=0.6, depth=1.2)
    o = obj_from(bm, name, m, parent, (0, 0, 0.6))
    md = o.modifiers.new("b", "BEVEL"); md.width = 0.26; md.segments = 6; md.limit_method = 'ANGLE'; md.angle_limit = math.radians(60)
    o.modifiers.new("ws", "WEIGHTED_NORMAL")
    for p in o.data.polygons: p.use_smooth = True
    o.data.use_auto_smooth = True; o.data.auto_smooth_angle = math.radians(70)
    return o


def face_patch(img, parent, name):
    """Curved decal following the head's front, planar-projected (like a Roblox face decal)."""
    bm = bmesh.new(); uvl = bm.loops.layers.uv.new(); R = 0.607; segs = 16; rows = 8
    grid = []
    for j in range(rows + 1):
        z = -0.5 + j / rows * 1.0; row = []
        for i in range(segs + 1):
            a = math.radians(-62 + i / segs * 124); x = R * math.sin(a); y = -R * math.cos(a)
            row.append(bm.verts.new((x, y, z)))
        grid.append(row)
    for j in range(rows):
        for i in range(segs):
            f = bm.faces.new([grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]])
            for lp in f.loops:
                co = lp.vert.co; lp[uvl].uv = (co.x / 1.2 + 0.5, co.z / 1.2 + 0.5)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:
        if f.normal.y > 0: f.normal_flip()
    o = obj_from(bm, name, img_mat(WK + f'faces/{img}.png', clip=True, rough=0.6), parent, (0, 0, 0.6), smooth=True)
    return o


def load_hair(item, parent, grey=False):
    info = json.load(open(WK + 'cat/index.json')).get(item)
    path = WK + f'cat/{item}.mesh'
    V, U, F = rbx.read_mesh(open(path, 'rb').read())
    if info is None: info = {}
    sc = info.get('scale') or (1, 1, 1); off = info.get('offset') or (0, 0, 0)
    ap = info.get('att_pos') or (0, 0.6, 0)
    # handle centre (Roblox coords, relative to head centre) = head HairAttachment (0,0.6,0) - accessory attachment
    hc = (0 - ap[0] + off[0], 0.6 - ap[1] + off[1], 0 - ap[2] + off[2])
    bm = bmesh.new(); uvl = bm.loops.layers.uv.new()
    vs = []
    for (x, y, z) in V:
        rx, ry, rz = x * sc[0] + hc[0], y * sc[1] + hc[1], z * sc[2] + hc[2]
        vs.append(bm.verts.new((-rx, rz, ry)))
    for (a, b, c) in F:
        try: f = bm.faces.new([vs[a], vs[c], vs[b]])
        except ValueError: continue
        for lp, idx in zip(f.loops, (a, c, b)): lp[uvl].uv = U[idx]
    tex = WK + f'cat/{item}_tex.png'
    m = img_mat(tex, rough=0.6, grey=grey) if os.path.exists(tex) else mat(0x6b4423)
    o = obj_from(bm, 'hair', m, parent, (0, 0, 0.6), smooth=True)
    bmesh_dedupe(o)
    return o


def bmesh_dedupe(o):
    bm = bmesh.new(); bm.from_mesh(o.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bm.to_mesh(o.data); bm.free()
    for p in o.data.polygons: p.use_smooth = True


def crown(parent):
    """Unique Crown (UGC item couldn't be downloaded): floating red->orange crown above the hair."""
    root = bpy.data.objects.new('crown', None); link(root); root.parent = parent; root.location = (0, 0, 1.95)
    root.scale = (0.44, 0.44, 0.44)
    cols = [0xd81b60, 0xe5262f, 0xf0442a, 0xf7742d]
    def cm(i): return mat(cols[i], 0.32, kind='plastic', name=f"crown{i}")
    for k in range(10):   # octagonal ring segments around the base, colour sweeps across
        a = k / 10 * math.tau
        box((0.62, 0.32, 0.22), (math.sin(a) * 0.98, math.cos(a) * 0.98, -0.55), cm(min(3, int((math.sin(a) + 1) * 2))), root, rot=(0, 0, -a))
    tube(0.92, 1.05, 0.34, (0, 0, -0.2), cm(1), v=10, name='band', parent=root)
    tube(0.95, 1.16, 0.12, (0, 0, -0.26), cm(2), v=10, name='lip', parent=root)
    for k in range(10):   # points: big ones front/back, small ones between
        a = k / 10 * math.tau; big = k % 2 == 0; h = 1.15 if big else 0.55
        c = cm(min(3, int((math.sin(a) + 1) * 2)))
        o = cyl(0.36 if big else 0.18, h, (math.sin(a) * 0.9, math.cos(a) * 0.9, 0.14 + h / 2), c, root, v=4, r2=0.04, smooth=False)
        o.rotation_euler = (0, 0, -a + math.pi / 4)
        sphere(0.17 if big else 0.1, (math.sin(a) * 0.9, math.cos(a) * 0.9, 0.16 + h), c, root, seg=10)
    return root


class R6:
    def __init__(s, name, cfg):
        s.name = name
        s.root = link(bpy.data.objects.new(name, None)); s.root.empty_display_size = 2
        s.torso = s._piv('torso', (0, 0, 3), s.root)
        up = img_mat(WK + f'chars/{name}_upper.png', rough=0.55); lo = img_mat(WK + f'chars/{name}_lower.png', rough=0.55)
        uvbox(2, 1, 2, TORSO, up, name + '_T', s.torso, (0, 0, 0))
        s.neck = s._piv('neck', (0, 0, 1), s.torso)
        skin = mat(tuple(cfg['skin']), 0.5, name=name + '_skin')
        head_mesh(skin, s.neck, name + '_H')
        s.faces = {}
        for f in FACES:
            s.faces[f] = face_patch(f, s.neck, f'{name}_face_{f}')
        if cfg.get('hair'): load_hair(cfg['hair'], s.neck, grey=cfg.get('grey', False))
        if cfg.get('crown'): crown(s.neck)
        s.rs = s._piv('rs', (-1.5, 0, 0.5), s.torso); uvbox(1, 1, 2, RLIMB, up, name + '_RA', s.rs, (0, 0, -0.5))
        s.ls = s._piv('ls', (1.5, 0, 0.5), s.torso); uvbox(1, 1, 2, LLIMB, up, name + '_LA', s.ls, (0, 0, -0.5))
        s.rh = s._piv('rh', (-0.5, 0, -1), s.torso); uvbox(1, 1, 2, RLIMB, lo, name + '_RL', s.rh, (0, 0, -1))
        s.lh = s._piv('lh', (0.5, 0, -1), s.torso); uvbox(1, 1, 2, LLIMB, lo, name + '_LL', s.lh, (0, 0, -1))
        s.joints = [s.torso, s.neck, s.rs, s.ls, s.rh, s.lh]
        s.face_now = None
        s.park(0)

    def _piv(s, n, loc, parent):
        o = link(bpy.data.objects.new(f'{s.name}_{n}', None)); o.location = loc; o.parent = parent; o.empty_display_size = 0.3
        return o

    # ---------- keyframing ----------
    def place(s, f, pos, heading=0.0, pitch=0.0, roll=0.0):
        s.root.location = pos; s.root.rotation_euler = (math.radians(pitch), math.radians(roll), math.radians(heading))
        s.root.keyframe_insert('location', frame=f); s.root.keyframe_insert('rotation_euler', frame=f)

    def park(s, f):
        s.place(f, (0, 0, -900)); s.pose(f)

    def pose(s, f, rs=(0, 0, 0), ls=(0, 0, 0), rh=(0, 0, 0), lh=(0, 0, 0), neck=(0, 0, 0), torso=(0, 0, 0), tz=0.0):
        for o, r in ((s.rs, rs), (s.ls, ls), (s.rh, rh), (s.lh, lh), (s.neck, neck), (s.torso, torso)):
            o.rotation_euler = [math.radians(v) for v in r]; o.keyframe_insert('rotation_euler', frame=f)
        s.torso.location = (0, 0, 3 + tz); s.torso.keyframe_insert('location', frame=f)

    def face(s, f, name):
        for k, o in s.faces.items():
            o.hide_render = k != name; o.keyframe_insert('hide_render', frame=f)
            o.hide_viewport = k != name; o.keyframe_insert('hide_viewport', frame=f)


def heading_to(dx, dy):
    return math.degrees(math.atan2(dx, -dy))
