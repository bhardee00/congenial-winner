import os
import bpy, math, random, sys
from mathutils import Vector
D = os.environ.get('SHORTS_WORK', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'work')) + '/'
random.seed(7)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene

def lin(h):
    c = [((h >> s) & 255) / 255 for s in (16, 8, 0)]
    return tuple(((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c) + (1,)

MATS = {}
def mat(h, rough=0.45, emit=0.0, metal=0.0):
    k = (h, rough, emit, metal)
    if k in MATS: return MATS[k]
    m = bpy.data.materials.new(f"m{h:06x}_{rough}")
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = lin(h)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emit:
        b.inputs["Emission Color"].default_value = lin(h)
        b.inputs["Emission Strength"].default_value = emit
    MATS[k] = m
    return m

def finish(o, m, bevel=0.0, seg=3, smooth=True, parent=None):
    o.data.materials.append(m)
    if bevel:
        md = o.modifiers.new("b", "BEVEL"); md.width = bevel; md.segments = seg; md.limit_method = 'NONE'
    if smooth:
        for p in o.data.polygons: p.use_smooth = True
        o.data.use_auto_smooth = True; o.data.auto_smooth_angle = math.radians(35)
    if parent: o.parent = parent
    return o

def rbox(sx, sy, sz, loc, m, bevel=0.08, parent=None, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.active_object; o.scale = (sx, sy, sz)
    bpy.ops.object.transform_apply(scale=True)
    return finish(o, m, bevel, parent=parent)

def ball(r, loc, m, parent=None, scale=(1, 1, 1), seg=24):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=seg, ring_count=seg // 2)
    o = bpy.context.active_object; o.scale = scale
    return finish(o, m, parent=parent)

def cyl(r, h, loc, m, parent=None, rot=(0, 0, 0), v=24, r2=None):
    if r2 is None:
        bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, location=loc, rotation=rot, vertices=v)
    else:
        bpy.ops.mesh.primitive_cone_add(radius1=r, radius2=r2, depth=h, location=loc, rotation=rot, vertices=v)
    return finish(bpy.context.active_object, m, parent=parent)

def empty(name, loc, parent=None):
    o = bpy.data.objects.new(name, None); sc.collection.objects.link(o)
    o.location = loc
    if parent: o.parent = parent
    return o

def roof(w, d, h, loc, m):
    # triangular prism roof, ridge along x
    import bmesh
    me = bpy.data.meshes.new("roof"); bm = bmesh.new()
    vs = [bm.verts.new(v) for v in [(-w/2, -d/2, 0), (w/2, -d/2, 0), (w/2, d/2, 0), (-w/2, d/2, 0), (-w/2, 0, h), (w/2, 0, h)]]
    for f in [(0, 1, 5, 4), (2, 3, 4, 5), (0, 4, 3), (1, 2, 5), (0, 3, 2, 1)]: bm.faces.new([vs[i] for i in f])
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new("roof", me); sc.collection.objects.link(o); o.location = loc
    return finish(o, m, 0.04, seg=2, smooth=False)

# ---------------- world / sky ----------------
w = bpy.data.worlds.new("W"); sc.world = w; w.use_nodes = True
nt = w.node_tree; bg = nt.nodes["Background"]
tc = nt.nodes.new("ShaderNodeTexCoord"); sep = nt.nodes.new("ShaderNodeSeparateXYZ"); ramp = nt.nodes.new("ShaderNodeValToRGB")
nt.links.new(tc.outputs["Generated"], sep.inputs[0]); tc.outputs['Generated']; nt.links.new(sep.outputs["Z"], ramp.inputs[0])
cr = ramp.color_ramp
cr.elements[0].position = 0.0; cr.elements[0].color = lin(0xffd2a8)
cr.elements[1].position = 0.45; cr.elements[1].color = lin(0x2f7fe0)
e = cr.elements.new(0.08); e.color = lin(0xa9d8ff)
e = cr.elements.new(0.2); e.color = lin(0x5fa8f5)
nt.links.new(ramp.outputs["Color"], bg.inputs["Color"]); bg.inputs["Strength"].default_value = 1.0

# sun (low, warm, from behind-right for rim light)
bpy.ops.object.light_add(type='SUN', rotation=(math.radians(62), 0, math.radians(150)))
sun = bpy.context.active_object; sun.data.energy = 4.2; sun.data.color = lin(0xffc69a)[:3]; sun.data.angle = math.radians(3)
# soft fill from camera side
bpy.ops.object.light_add(type='AREA', location=(4, -14, 9))
fill = bpy.context.active_object; fill.data.energy = 2500; fill.data.size = 12; fill.data.color = lin(0xcfe0ff)[:3]
fill.rotation_euler = (Vector((0, 2, 2)) - fill.location).to_track_quat('-Z', 'Y').to_euler()

# ---------------- water ----------------
bpy.ops.mesh.primitive_plane_add(size=400, location=(0, 60, 0))
water = bpy.context.active_object
wm = bpy.data.materials.new("water"); wm.use_nodes = True; n = wm.node_tree.nodes; L = wm.node_tree.links
p = n["Principled BSDF"]; p.inputs["Base Color"].default_value = lin(0x1f8fd6); p.inputs["Roughness"].default_value = 0.08
p.inputs["Specular IOR Level"].default_value = 0.9
tco = n.new("ShaderNodeTexCoord"); mp = n.new("ShaderNodeMapping"); wv = n.new("ShaderNodeTexWave"); bump = n.new("ShaderNodeBump")
wv.inputs["Scale"].default_value = 0.35; wv.inputs["Distortion"].default_value = 6; wv.inputs["Detail"].default_value = 3
bump.inputs["Strength"].default_value = 0.12
L.new(tco.outputs["Object"], mp.inputs[0]); L.new(mp.outputs[0], wv.inputs[0]); L.new(wv.outputs["Fac"], bump.inputs["Height"]); L.new(bump.outputs["Normal"], p.inputs["Normal"])
FREEZE = 86
for f, v in ((0, 0.0), (FREEZE, 1.6)):
    mp.inputs["Location"].default_value = (v, v * 0.6, 0); mp.inputs["Location"].keyframe_insert("default_value", frame=f)
water.data.materials.append(wm)

# ---------------- dock ----------------
wood, wood2, post = mat(0xc89462, 0.6), mat(0xb8834f, 0.6), mat(0x8a5a33, 0.7)
for i in range(30):
    y = -8 + i * 0.62
    rbox(3.4, 0.54, 0.22, (0, y, 0.75), wood if i % 2 else wood2, 0.05)
for y in (-7.5, -3, 1.5, 6, 10):
    for x in (-1.75, 1.75):
        cyl(0.22, 2.6, (x, y, 0.4), post)
for x in (-1.75, 1.75):
    rbox(0.18, 18.5, 0.25, (x, 1.2, 0.55), post, 0.04)
# a little boat
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(4.6, 4, 0.25)); boat = bpy.context.active_object
boat.scale = (1.0, 2.4, 0.45); finish(boat, mat(0xe74c3c, 0.4))
rbox(1.7, 4.2, 0.12, (4.6, 4, 0.55), mat(0xf5f5f5, 0.5), 0.05)

# ---------------- shore + town ----------------
rbox(400, 30, 1.2, (0, 52, 0.3), mat(0x67c24a, 0.8), 0.3)
rbox(400, 2.5, 0.9, (0, 37.4, 0.25), mat(0xf1d9a8, 0.8), 0.3)
cols = [0xe53935, 0xfdd835, 0x1e88e5, 0x43a047, 0xfb8c00, 0xf06292, 0x8e24aa, 0x00acc1]
roofs = [0x2e7d32, 0xc62828, 0x1565c0, 0x6d4c41, 0x37474f]
x = -46
while x < 46:
    wdt = random.uniform(5, 7.5); hgt = random.uniform(4.5, 7.5); dep = 5.5
    y = 44 + random.uniform(-1, 2); c = random.choice(cols)
    rbox(wdt, dep, hgt, (x, y, 0.9 + hgt / 2), mat(c, 0.55), 0.12)
    roof(wdt + 0.8, dep + 0.8, 2.6, (x, y, 0.9 + hgt), mat(random.choice(roofs), 0.6))
    rbox(0.8, 0.8, 2.2, (x + wdt * 0.25, y + 1, 0.9 + hgt + 1.6), mat(0x8d4b3a, 0.7), 0.05)
    for wx in (-wdt * 0.25, wdt * 0.25):
        for wz in (hgt * 0.35, hgt * 0.72):
            rbox(1.1, 0.12, 1.2, (x + wx, y - dep / 2 - 0.02, 0.9 + wz), mat(0xfff3c4, 0.3, emit=0.6), 0.03)
            rbox(1.35, 0.1, 1.45, (x + wx, y - dep / 2 + 0.02, 0.9 + wz), mat(0xffffff, 0.5), 0.03)
    x += wdt + random.uniform(1.5, 3.5)
# trees (stylised blob trees)
leaf = [mat(0x4caf50, 0.7), mat(0x66bb6a, 0.7), mat(0xff9800, 0.7)]
for i in range(26):
    tx = -50 + i * 4 + random.uniform(-1, 1); ty = random.choice([39.5, 49])
    cyl(0.3, 3, (tx, ty, 2.2), mat(0x795548, 0.8))
    lm = random.choice(leaf)
    for k in range(4):
        ball(random.uniform(1.1, 1.6), (tx + random.uniform(-0.8, 0.8), ty + random.uniform(-0.6, 0.6), 4.3 + random.uniform(-0.3, 1.0)), lm, seg=12)
# clouds
cw = mat(0xffffff, 0.9, emit=0.35)
for i in range(9):
    cx, cz = -70 + i * 17 + random.uniform(-4, 4), 26 + random.uniform(-4, 8)
    for k in range(5):
        ball(random.uniform(3, 5), (cx + k * 3 - 6, 120 + random.uniform(-3, 3), cz + random.uniform(-1, 1.5)), cw, scale=(1.3, 0.6, 0.7), seg=14)
# distant hills
for i in range(7):
    ball(random.uniform(18, 26), (-90 + i * 30, 95, -6), mat(0x7fbf8f, 0.9), scale=(1.4, 0.6, 0.55), seg=20)
# lamp post near dock end
cyl(0.12, 4.5, (1.75, 9.5, 2.9), mat(0x263238, 0.4))
ball(0.38, (1.75, 9.5, 5.3), mat(0xffe9a8, 0.2, emit=8))

# ---------------- avatar ----------------
SKIN, JACKET, TEE, PANTS, HAIR, SHOE = 0xd9a47a, 0x1d1d20, 0x2fa7c8, 0x18181a, 0xb8682a, 0x3f8a74
root = empty("me", (0, 0, 0.86))
torso = empty("torso", (0, 0, 3), root)
rbox(2, 1, 2, (0, 0, 0), mat(JACKET, 0.5), 0.12, parent=torso)
tee = rbox(0.95, 0.06, 1.95, (0, -0.5, 0), mat(TEE, 0.5), 0.02, parent=torso)
rbox(0.5, 0.03, 0.42, (0.05, -0.54, 0.35), mat(0x14394a, 0.5), 0.01, parent=torso)
for s in (-1, 1):
    rbox(0.16, 0.1, 1.95, (s * 0.53, -0.52, 0), mat(0x2c2c30, 0.5), 0.03, parent=torso)

def limb(name, x, z, upper, lower, shoe=None):
    piv = empty(name, (x, 0, z), torso)
    rbox(1, 1, 2, (0, 0, -1), mat(lower, 0.5), 0.12, parent=piv)
    if upper:
        rbox(1.05, 1.05, 1.45, (0, 0, -0.72), mat(upper, 0.5), 0.12, parent=piv)
    if shoe:
        rbox(1.07, 1.15, 0.45, (0, -0.05, -1.78), mat(shoe, 0.45), 0.1, parent=piv)
        rbox(1.1, 1.2, 0.14, (0, -0.06, -1.97), mat(0xf4f4f4, 0.5), 0.05, parent=piv)
    return piv
la = limb("la", -1.5, 1, JACKET, SKIN); ra = limb("ra", 1.5, 1, JACKET, SKIN)
ll = limb("ll", -0.5, -1, None, PANTS, SHOE); rl = limb("rl", 0.5, -1, None, PANTS, SHOE)
for piv, k in ((ll, 0), (rl, 1)):
    rbox(1.06, 1.06, 0.1, (0, 0, -0.6 - k * 0.35), mat(0x6b6b6b, 0.4), 0.02, parent=piv)

head = empty("head", (0, 0, 1), torso)
hm = rbox(1.25, 1.2, 1.2, (0, 0, 0.62), mat(SKIN, 0.5), 0.3, parent=head)
# face decals
FACES = {}
for k in ("smile", "shock"):
    m = bpy.data.materials.new("face_" + k); m.use_nodes = True; m.blend_method = 'CLIP'; m.shadow_method = 'CLIP'
    nn = m.node_tree.nodes; img = nn.new("ShaderNodeTexImage"); img.image = bpy.data.images.load(D + f"face_{k}.png")
    pb = nn["Principled BSDF"]; m.node_tree.links.new(img.outputs["Color"], pb.inputs["Base Color"]); m.node_tree.links.new(img.outputs["Alpha"], pb.inputs["Alpha"])
    pb.inputs["Roughness"].default_value = 0.5
    bpy.ops.mesh.primitive_plane_add(size=1.05, location=(0, -0.611, 0.6), rotation=(math.radians(90), 0, 0))
    fo = bpy.context.active_object; fo.data.materials.append(m); fo.parent = head
    FACES[k] = fo
# fluffy hair
hmat, hdark = mat(HAIR, 0.55), mat(0x8f4f1f, 0.6)
ball(0.78, (0, 0.05, 1.28), hmat, head, (1.0, 1.0, 0.6))
for (x, y, z, r) in [(-0.42, -0.05, 1.42, 0.36), (0.38, 0.0, 1.45, 0.38), (0, 0.32, 1.48, 0.42), (-0.2, -0.28, 1.5, 0.3), (0.2, 0.4, 1.3, 0.4), (-0.4, 0.35, 1.3, 0.38)]:
    ball(r, (x, y, z), hmat, head, seg=16)
rbox(1.4, 0.4, 1.0, (0, 0.52, 0.92), hmat, 0.18, parent=head)
for s in (-1, 1):
    rbox(0.2, 0.85, 0.6, (s * 0.66, 0.2, 1.02), hmat, 0.08, parent=head)
o = rbox(1.0, 0.18, 0.26, (-0.12, -0.6, 1.2), hmat, 0.08, parent=head); o.rotation_euler = (0, -0.18, 0)
o = rbox(0.45, 0.18, 0.22, (0.4, -0.6, 1.15), hdark, 0.08, parent=head); o.rotation_euler = (0, 0.3, 0)
# flame crown
crown = empty("crown", (0.05, 0.05, 1.82), head); crown.rotation_euler = (0, 0.08, 0)
cyl(0.44, 0.22, (0, 0, 0), mat(0xd8342a, 0.35), crown)
for k in range(8):
    a = k / 8 * math.tau
    cyl(0.13, 0.46, (math.sin(a) * 0.4, math.cos(a) * 0.4, 0.3), mat(0xf0552d, 0.35, emit=0.6), crown, v=8, r2=0.0)
    ball(0.065, (math.sin(a) * 0.4, math.cos(a) * 0.4, 0.55), mat(0xffc23a, 0.2, emit=2.5), crown, seg=10)
# remote in right hand
rem = empty("remote", (0, -0.15, -2.1), ra)
rbox(0.45, 0.2, 1.2, (0, -0.1, -0.3), mat(0x151515, 0.35), 0.06, parent=rem)
cyl(0.08, 0.08, (0, -0.22, -0.65), mat(0xff2020, 0.3, emit=3), rem, rot=(math.radians(90), 0, 0))
root.rotation_euler = (0, 0, math.radians(-12))

# ---------------- animation ----------------
def key(o, f, rot=None, loc=None):
    if rot is not None: o.rotation_euler = [math.radians(v) for v in rot]; o.keyframe_insert("rotation_euler", frame=f)
    if loc is not None: o.location = loc; o.keyframe_insert("location", frame=f)
# idle sway, head looks around, then raise arm and press
key(head, 0, (0, 0, 20)); key(head, 30, (5, 0, -15)); key(head, 52, (12, 0, 0)); key(head, 86, (10, 0, 0)); key(head, 92, (-6, 0, 0)); key(head, 150, (-4, 0, 3))
key(ra, 0, (0, 0, 0)); key(ra, 40, (0, 0, 0)); key(ra, 66, (-80, 0, 50)); key(ra, 82, (-78, 0, 50)); key(ra, 85, (-70, 0, 50)); key(ra, 88, (-78, 0, 50))
key(la, 0, (6, 0, 0)); key(la, 60, (-4, 0, 0)); key(la, 86, (0, 0, -6))
key(torso, 0, None, (0, 0, 3)); key(torso, 40, None, (0, 0, 3.05)); key(torso, 80, None, (0, 0, 3))
for o in bpy.data.objects:
    if o.animation_data and o.animation_data.action:
        for fc in o.animation_data.action.fcurves:
            for kp in fc.keyframe_points: kp.interpolation = 'BEZIER'; kp.easing = 'AUTO'
# swap face to shock at freeze
for f, smile in ((0, True), (95, True), (96, False)):
    FACES["smile"].hide_render = not smile; FACES["smile"].keyframe_insert("hide_render", frame=f)
    FACES["shock"].hide_render = smile; FACES["shock"].keyframe_insert("hide_render", frame=f)

# ---------------- cameras (cuts via markers) ----------------
def camera(name, loc, target, lens, f0, fstop=2.8, focus=None, move=None):
    cd = bpy.data.cameras.new(name); cd.lens = lens; cd.dof.use_dof = True; cd.dof.aperture_fstop = fstop
    c = bpy.data.objects.new(name, cd); sc.collection.objects.link(c)
    tgt = empty(name + "_t", target)
    tr = c.constraints.new("TRACK_TO"); tr.target = tgt; tr.track_axis = 'TRACK_NEGATIVE_Z'; tr.up_axis = 'UP_Y'
    cd.dof.focus_object = focus or tgt
    c.location = loc; c.keyframe_insert("location", frame=f0)
    if move: c.location = move[1]; c.keyframe_insert("location", frame=move[0])
    m = sc.timeline_markers.new(name, frame=f0); m.camera = c
    return c
camera("wide", (7.5, -14, 5.5), (0, 3, 2.6), 32, 0, 5.6, move=(40, (6.8, -12.5, 5.1)))
camera("med", (-3.2, -10.5, 5.4), (0.9, -1.2, 4.3), 38, 41, 2.4, move=(100, (-2.7, -9.4, 5.3)))
camera("close", (-1.9, -6.2, 6.0), (0.05, 0, 5.75), 55, 101, 1.8, move=(150, (-1.6, -5.5, 5.95)))
sc.camera = bpy.data.objects["wide"]

# ---------------- render settings ----------------
sc.render.engine = 'BLENDER_EEVEE'
ee = sc.eevee
ee.taa_render_samples = int(sys.argv[-1]) if sys.argv[-1].isdigit() else 32
ee.use_bloom = True; ee.bloom_intensity = 0.06; ee.bloom_threshold = 0.9
ee.use_ssr = True; ee.use_ssr_refraction = False; ee.ssr_quality = 0.5
ee.use_gtao = True; ee.gtao_distance = 1.2
ee.use_soft_shadows = True; ee.shadow_cascade_size = '2048'; ee.shadow_cube_size = '1024'
sun.data.shadow_cascade_max_distance = 80
sc.view_settings.view_transform = 'Standard'
try: sc.view_settings.look = 'Medium High Contrast'
except Exception: sc.view_settings.look = 'None'
sc.render.resolution_x = 1080; sc.render.resolution_y = 1920; sc.render.resolution_percentage = 100
sc.render.fps = 30; sc.frame_start = 0; sc.frame_end = 149
sc.render.image_settings.file_format = 'PNG'
sc.render.filepath = D + "frames/f_"
bpy.ops.wm.save_as_mainfile(filepath=D + "scene.blend")
