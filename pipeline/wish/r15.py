"""R15 'Roblox Boy' body (the package RobloxxKF wears) at the avatar's exact scales (height/width/depth/head 1.0,
proportion 0, bodyType 0). Real body-part meshes + real rig attachment offsets; classic shirt/pants templates map
onto the meshes' own UVs. Same animation API as r6.R6 (rs/ls/rh/lh/neck/torso pivots), faces -Y."""
import bpy, bmesh, math
from mathutils import Vector
from lib import *
import r6, rbx

MESH = dict(LowerTorso='8650495385', UpperTorso='8650495328',
            RightUpperArm='8650495303', RightLowerArm='8650495271', RightHand='8650495280',
            LeftUpperArm='8650495273', LeftLowerArm='8650495270', LeftHand='8650495301',
            RightUpperLeg='8650495376', RightLowerLeg='8650495379', RightFoot='8650495330',
            LeftUpperLeg='8650495362', LeftLowerLeg='8650495364', LeftFoot='8650495382')
# rig attachments (Roblox part-local positions) from the package's R15Fixed folder
A = {
 ('LowerTorso', 'Waist'): (0, 0.085, 0.1), ('LowerTorso', 'RightHip'): (0.5, -0.315, 0.1), ('LowerTorso', 'LeftHip'): (-0.5, -0.315, 0.1),
 ('UpperTorso', 'Waist'): (0, -0.744, 0.044), ('UpperTorso', 'Neck'): (0, 0.856, 0.044),
 ('UpperTorso', 'RightShoulder'): (1.0, 0.619, 0.044), ('UpperTorso', 'LeftShoulder'): (-1.0, 0.619, 0.044),
 ('RightUpperArm', 'RightShoulder'): (-0.193, 0.439, -0.019), ('RightUpperArm', 'RightElbow'): (0.307, -0.289, -0.019),
 ('RightLowerArm', 'RightElbow'): (0.19, 0.281, -0.102), ('RightLowerArm', 'RightWrist'): (0.19, -0.479, -0.102), ('RightHand', 'RightWrist'): (0.117, 0.216, -0.002),
 ('LeftUpperArm', 'LeftShoulder'): (0.193, 0.439, -0.019), ('LeftUpperArm', 'LeftElbow'): (-0.307, -0.289, -0.019),
 ('LeftLowerArm', 'LeftElbow'): (-0.19, 0.281, -0.102), ('LeftLowerArm', 'LeftWrist'): (-0.19, -0.479, -0.102), ('LeftHand', 'LeftWrist'): (-0.117, 0.216, -0.002),
 ('RightUpperLeg', 'RightHip'): (0.076, 0.389, 0.058), ('RightUpperLeg', 'RightKnee'): (0.076, -0.433, 0.058),
 ('RightLowerLeg', 'RightKnee'): (0.054, 0.466, -0.045), ('RightLowerLeg', 'RightAnkle'): (0.054, -0.46, -0.045), ('RightFoot', 'RightAnkle'): (0.047, -0.091, 0.139),
 ('LeftUpperLeg', 'LeftHip'): (-0.076, 0.389, 0.058), ('LeftUpperLeg', 'LeftKnee'): (-0.076, -0.433, 0.058),
 ('LeftLowerLeg', 'LeftKnee'): (-0.054, 0.466, -0.045), ('LeftLowerLeg', 'LeftAnkle'): (-0.054, -0.46, -0.045), ('LeftFoot', 'LeftAnkle'): (-0.047, -0.091, 0.139),
}
CHAIN = [('UpperTorso', 'LowerTorso', 'Waist'),
         ('RightUpperArm', 'UpperTorso', 'RightShoulder'), ('RightLowerArm', 'RightUpperArm', 'RightElbow'), ('RightHand', 'RightLowerArm', 'RightWrist'),
         ('LeftUpperArm', 'UpperTorso', 'LeftShoulder'), ('LeftLowerArm', 'LeftUpperArm', 'LeftElbow'), ('LeftHand', 'LeftLowerArm', 'LeftWrist'),
         ('RightUpperLeg', 'LowerTorso', 'RightHip'), ('RightLowerLeg', 'RightUpperLeg', 'RightKnee'), ('RightFoot', 'RightLowerLeg', 'RightAnkle'),
         ('LeftUpperLeg', 'LowerTorso', 'LeftHip'), ('LeftLowerLeg', 'LeftUpperLeg', 'LeftKnee'), ('LeftFoot', 'LeftLowerLeg', 'LeftAnkle')]
POS = {'LowerTorso': Vector((0, 0, 0))}
for part, par, j in CHAIN: POS[part] = POS[par] + Vector(A[(par, j)]) - Vector(A[(part, j)])
NECK = POS['UpperTorso'] + Vector(A[('UpperTorso', 'Neck')])
HEAD = NECK + Vector((0, 0.5, 0))                    # default head: NeckRigAttachment at (0,-0.5,0)
FOOT_BOTTOM = POS['RightFoot'].y - 0.314
HIP_H = -FOOT_BOTTOM                                 # LowerTorso centre height above the ground


def B(v): return Vector((-v[0], v[2], v[1]))         # Roblox -> Blender (faces -Y)

_MESHCACHE = {}
GROUPS = {'torso': (['UpperTorso', 'LowerTorso'], r6.TORSO), 'rarm': (['RightUpperArm', 'RightLowerArm', 'RightHand'], r6.RLIMB),
          'larm': (['LeftUpperArm', 'LeftLowerArm', 'LeftHand'], r6.LLIMB), 'rleg': (['RightUpperLeg', 'RightLowerLeg', 'RightFoot'], r6.RLIMB),
          'lleg': (['LeftUpperLeg', 'LeftLowerLeg', 'LeftFoot'], r6.LLIMB)}
GROUP_OF = {p: g for g, (ps, _) in GROUPS.items() for p in ps}
_BBOX = {}


def _verts(part):
    V, U, F = rbx.read_mesh(open(WK + f'r15/{MESH[part]}.mesh', 'rb').read())
    return [B(v) for v in V], F


def group_bbox(g):
    if g in _BBOX: return _BBOX[g]
    lo = Vector((1e9,) * 3); hi = Vector((-1e9,) * 3)
    for p in GROUPS[g][0]:
        c = B(POS[p])
        for v in _verts(p)[0]:
            w = c + v; lo = Vector(map(min, lo, w)); hi = Vector(map(max, hi, w))
    _BBOX[g] = (lo, hi); return _BBOX[g]


SLICE = dict(UpperTorso=(0, 0.8), LowerTorso=(0.8, 1), RightUpperArm=(0, 0.5), LeftUpperArm=(0, 0.5), RightLowerArm=(0.5, 0.84), LeftLowerArm=(0.5, 0.84),
             RightHand=(0.84, 1), LeftHand=(0.84, 1), RightUpperLeg=(0, 0.5), LeftUpperLeg=(0, 0.5), RightLowerLeg=(0.5, 0.86), LeftLowerLeg=(0.5, 0.86),
             RightFoot=(0.86, 1), LeftFoot=(0.86, 1))


def template_uv(w, n, lo, hi, rects, plo=None, phi=None, sl=(0, 1)):
    """Box-project a point (Blender, rig space) onto the classic 585x559 template, like Roblox does for R15 parts."""
    sx, sy, sz = (hi - lo)
    ax = max(range(3), key=lambda i: abs(n[i]))
    if ax == 1 and n.y < 0: k, u, t = 'F', (w.x - lo.x) / sx, (hi.z - w.z) / sz
    elif ax == 1:           k, u, t = 'B', (hi.x - w.x) / sx, (hi.z - w.z) / sz
    elif ax == 0 and n.x < 0: k, u, t = 'R', (hi.y - w.y) / sy, (hi.z - w.z) / sz
    elif ax == 0:           k, u, t = 'L', (w.y - lo.y) / sy, (hi.z - w.z) / sz
    elif n.z > 0:           k, u, t = 'U', (w.x - lo.x) / sx, (hi.y - w.y) / sy
    else:                   k, u, t = 'D', (w.x - lo.x) / sx, (w.y - lo.y) / sy
    if k not in ('U', 'D') and plo is not None:      # vertical position within this part -> its slice of the strip
        t = sl[0] + (phi.z - w.z) / max(1e-6, phi.z - plo.z) * (sl[1] - sl[0])
    x, y, rw, rh = rects[k]; u = min(max(u, 0.01), 0.99); t = min(max(t, 0.01), 0.99)
    return ((x + u * rw) / 585.0, 1 - (y + t * rh) / 559.0)


def part_mesh(part):
    if part in _MESHCACHE: return _MESHCACHE[part]
    V, F = _verts(part); g = GROUP_OF[part]; lo, hi = group_bbox(g); rects = GROUPS[g][1]; c = B(POS[part])
    plo = Vector((0, 0, min(v.z for v in V))) + c; phi = Vector((0, 0, max(v.z for v in V))) + c
    bm = bmesh.new(); vs = [bm.verts.new(v) for v in V]
    for (a, b, cc) in F:
        try: bm.faces.new([vs[a], vs[b], vs[cc]])
        except ValueError: continue
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    uvl = bm.loops.layers.uv.new()
    for f in bm.faces:
        n = f.normal
        for lp in f.loops: lp[uvl].uv = template_uv(c + lp.vert.co, n, lo, hi, rects, plo, phi, SLICE[part])
    me = bpy.data.meshes.new(part); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    me.use_auto_smooth = True; me.auto_smooth_angle = math.radians(50)
    _MESHCACHE[part] = me
    return me


class R15(r6.R6):
    HC = 0.5   # head centre above the neck joint

    def __init__(s, name, cfg):
        s.name = name
        s.root = link(bpy.data.objects.new(name, None)); s.root.empty_display_size = 2
        s.tz0 = HIP_H
        s.torso = s._piv('torso', (0, 0, HIP_H), s.root)
        up = img_mat(WK + f'chars/{name}_upper.png', rough=0.5); lo = img_mat(WK + f'chars/{name}_lower.png', rough=0.5)

        def put(part, parent, origin_rbx, m):
            o = link(bpy.data.objects.new(f'{name}_{part}', part_mesh(part))); o.data = part_mesh(part)
            o.material_slots and None
            o.parent = parent; o.location = B(POS[part] - origin_rbx)
            if not o.data.materials: o.data.materials.append(m)
            o.active_material = m
            for sl in o.material_slots: sl.link = 'OBJECT'; sl.material = m
            return o
        o0 = POS['LowerTorso']
        put('LowerTorso', s.torso, o0, up); put('UpperTorso', s.torso, o0, up)
        s.neck = s._piv('neck', B(NECK - o0), s.torso)
        skin = mat(tuple(cfg['skin']), 0.5, name=name + '_skin')
        hm = r6.head_mesh(skin, s.neck, name + '_H'); hm.location = (0, 0, s.HC)
        s.faces = {}
        for f in r6.FACES:
            fo = r6.face_patch(f, s.neck, f'{name}_face_{f}'); fo.location = (0, 0, s.HC); s.faces[f] = fo
        if cfg.get('hair'):
            h = r6.load_hair(cfg['hair'], s.neck, grey=cfg.get('grey', False)); h.location = (0, 0, s.HC)
        if cfg.get('crown'):
            c = r6.crown(s.neck); c.location = (0, 0, 1.75 - 0.6 + s.HC)
        sj = {}
        for side, piv in (('Right', 'rs'), ('Left', 'ls')):
            jp = POS['UpperTorso'] + Vector(A[('UpperTorso', side + 'Shoulder')])
            p = s._piv(piv, B(jp - o0), s.torso); sj[piv] = p
            for part in ('UpperArm', 'LowerArm', 'Hand'): put(side + part, p, jp, up)
        for side, piv in (('Right', 'rh'), ('Left', 'lh')):
            jp = POS['LowerTorso'] + Vector(A[('LowerTorso', side + 'Hip')])
            p = s._piv(piv, B(jp - o0), s.torso); sj[piv] = p
            for part in ('UpperLeg', 'LowerLeg', 'Foot'): put(side + part, p, jp, lo)
        s.rs, s.ls, s.rh, s.lh = sj['rs'], sj['ls'], sj['rh'], sj['lh']
        s.joints = [s.torso, s.neck, s.rs, s.ls, s.rh, s.lh]
        s.park(0)

    def pose(s, f, rs=(0, 0, 0), ls=(0, 0, 0), rh=(0, 0, 0), lh=(0, 0, 0), neck=(0, 0, 0), torso=(0, 0, 0), tz=0.0):
        for o, r in ((s.rs, rs), (s.ls, ls), (s.rh, rh), (s.lh, lh), (s.neck, neck), (s.torso, torso)):
            o.rotation_euler = [math.radians(v) for v in r]; o.keyframe_insert('rotation_euler', frame=f)
        s.torso.location = (0, 0, s.tz0 + tz); s.torso.keyframe_insert('location', frame=f)
