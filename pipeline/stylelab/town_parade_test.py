"""Test: recreate the reference's 6-second shot (Mom walking toward the camera in the plaza, golden hour)."""
import sys, math, random
import bpy
from mathutils import Vector
sys.path.insert(0, "/home/user/congenial-winner/pipeline")
import shortkit as K
from shortkit import prim, mat, empty, pose
import blocky, town, toys
from avatar import react

R = "/home/user/congenial-winner/work/tmp/rs/"; T = "/home/user/congenial-winner/work/tmp/"; D = "/home/user/congenial-winner/work/"
random.seed(2)
bpy.ops.wm.read_factory_settings(use_empty=True)
st = K.Set("plaza")
sc = st.scene


def texmat(base, scale, rough=0.85, tint=None):
    m = bpy.data.materials.new(base); m.use_nodes = True; nt = m.node_tree; pb = nt.nodes["Principled BSDF"]
    geo = nt.nodes.new("ShaderNodeNewGeometry"); mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (scale,) * 3
    nt.links.new(geo.outputs["Position"], mp.inputs["Vector"])
    d = nt.nodes.new("ShaderNodeTexImage"); d.image = bpy.data.images.load(T + f"ph/{base}/{base}_Diffuse_1k.jpg"); nt.links.new(mp.outputs[0], d.inputs[0])
    if tint:
        mx = nt.nodes.new("ShaderNodeMixRGB"); mx.blend_type = 'MULTIPLY'; mx.inputs[0].default_value = 1; mx.inputs[2].default_value = tint + (1,)
        nt.links.new(d.outputs[0], mx.inputs[1]); nt.links.new(mx.outputs[0], pb.inputs["Base Color"])
    else: nt.links.new(d.outputs[0], pb.inputs["Base Color"])
    n = nt.nodes.new("ShaderNodeTexImage"); n.image = bpy.data.images.load(T + f"ph/{base}/{base}_nor_gl_1k.jpg"); n.image.colorspace_settings.name = "Non-Color"
    nt.links.new(mp.outputs[0], n.inputs[0]); nm = nt.nodes.new("ShaderNodeNormalMap"); nm.inputs["Strength"].default_value = 1.4
    nt.links.new(n.outputs[0], nm.inputs["Color"]); nt.links.new(nm.outputs[0], pb.inputs["Normal"]); pb.inputs["Roughness"].default_value = rough
    return m


with st:
    # ---------- light: golden-hour sun + the mountain sky ----------
    w = sc.world; nt = w.node_tree; bg = nt.nodes["Background"]
    env = nt.nodes.new("ShaderNodeTexEnvironment"); env.image = bpy.data.images.load(T + "ph/golden_gate_hills.hdr")
    mp = nt.nodes.new("ShaderNodeMapping"); tc = nt.nodes.new("ShaderNodeTexCoord"); mp.inputs["Rotation"].default_value = (0, 0, math.radians(200))
    nt.links.new(tc.outputs["Generated"], mp.inputs["Vector"]); nt.links.new(mp.outputs[0], env.inputs[0])
    nt.links.new(env.outputs[0], bg.inputs["Color"]); bg.inputs["Strength"].default_value = 0.55
    sun = st.sun; sun.data.energy = 6.0; sun.data.color = (1.0, 0.82, 0.62); sun.data.angle = math.radians(1.2)
    sun.rotation_euler = (math.radians(62), 0, math.radians(-35))   # low sun from behind-left: long shadows toward the camera
    ee = sc.eevee; ee.use_gtao = True; ee.gtao_distance = 3; ee.use_bloom = True; ee.bloom_intensity = 0.08; ee.bloom_threshold = 1.0
    ee.use_soft_shadows = True; ee.shadow_cascade_size = '4096'; sun.data.shadow_cascade_max_distance = 120; ee.taa_render_samples = 48
    sc.view_settings.view_transform = 'Filmic'; sc.view_settings.look = 'High Contrast'; sc.view_settings.exposure = 0.0

    # ---------- ground: cobblestone plaza with a ring of lighter stone, grass beyond ----------
    cob = texmat("cobblestone_floor_04", 0.22, 0.8, (1.05, 0.9, 0.75))
    town.slab((140, 140, 0.4), (0, 0, -0.2), cob, "plaza")
    ring = texmat("cobblestone_floor_08", 0.3, 0.8, (1.0, 0.85, 0.7))
    town._cyl((0, 30, 0.01), 20, 20, 0.04, ring, 64, "ring")
    # ---------- the clock tower ----------
    tw = empty("tower", (0, 46, 0)); cream = mat((238, 205, 150), 0.7); white = mat((250, 245, 235), 0.5); teal = mat((70, 170, 160), 0.4)
    prim("box", (9, 9, 34), (0, 0, 17), cream, parent=tw, bevel=0.1)
    for z in (8, 20, 31, 34.5): prim("box", (10, 10, 0.8), (0, 0, z), white, parent=tw, bevel=0.1)
    for sx in (-4.4, 4.4):
        for sy in (-4.4, 4.4): prim("box", (1.0, 1.0, 34), (sx, sy, 17), white, parent=tw)
    for sy in (-4.6,):
        prim("box", (4.0, 0.3, 6.0), (0, sy, 26.0), mat((70, 45, 30), 0.6), parent=tw, bevel=0.3)  # arched bell opening (dark)
        prim("cyl", (0.3, 4.0, 4.0), (0, sy, 29.0), mat((70, 45, 30), 0.6), rot=(0, 0, 90), parent=tw)
    bell = prim("cone", (2.4, 2.4, 2.6), (0, -3.6, 26.3), mat((220, 165, 50), 0.25, metal=0.9), rot=(180, 0, 0), parent=tw)
    K.plane_image(R + "clockface.png", (5.5, 5.5), (0, -4.62, 33.0), parent=tw)
    prim("box", (9.5, 9.5, 4.5), (0, 0, 37.5), cream, parent=tw, bevel=0.2); prim("box", (10.2, 10.2, 0.6), (0, 0, 39.9), white, parent=tw)
    prim("cone", (11, 11, 9), (0, 0, 44.5), teal, parent=tw); prim("cylY", (0.4, 0.4, 4), (0, 0, 50), mat((220, 190, 90), 0.3, metal=0.8), parent=tw)
    for k in range(10): prim("box", (0.25, 9.6, 0.25), (0, 0, 9 + k * 1.2), mat((245, 235, 215), 0.6), parent=tw)
    # ---------- the TOWN PARADE banner on two posts ----------
    bn = empty("banner", (0, 20, 0)); pole = mat((90, 55, 35), 0.5)
    for sx in (-8.5, 8.5): prim("cylY", (0.45, 0.45, 15), (sx, 0, 7.5), pole, parent=bn); prim("ball", (0.9, 0.9, 0.9), (sx, 0, 15.2), mat((230, 180, 70), 0.3, metal=0.7), parent=bn)
    K.plane_image(R + "banner.png", (16, 3.4), (0, -0.25, 12.4), parent=bn, emit=0.15)
    prim("box", (16.4, 0.3, 3.8), (0, 0.0, 12.4), mat((140, 20, 25), 0.5), parent=bn)
    prim("cyl", (2.4, 2.4, 0.3), (0, -0.3, 14.6), mat((200, 25, 30), 0.5), rot=(0, 0, 90), parent=bn)
    # ---------- bunting strings across the plaza ----------
    cols = [(230, 60, 60), (250, 200, 60), (70, 140, 230), (110, 200, 110), (240, 140, 220), (250, 140, 60)]
    for (a, b) in (((-24, 8, 11), (24, 12, 11)), ((-24, 26, 12), (24, 24, 12)), ((-22, -4, 10.5), (22, 2, 10.5))):
        r_ = toys.bunting(a, b, a[2] + 2, 26, 0.9); r_.scale = (1, 1, 1)
    # ---------- surroundings: houses, trees, pines, lamp posts, planters ----------
    for k, x in enumerate((-40, 40)):
        town.place(f"suburban/building-type-{'ah'[k]}", (x, 62, 0), 180)
    for k, x in enumerate((-46, -40, 40, 46)): town.place(f"suburban/building-type-{'bdkm'[k]}", (x, 20 + k * 6, 0), 90 if x < 0 else -90)
    for k in range(-9, 10): town.pine(k * 10 + 3, 80 + (k % 3) * 6, 1.1 + 0.2 * (k % 2), k)
    for (x, y, s_) in ((-14, 38, 1.0), (13, 40, 1.1), (-26, 14, 0.9), (26, 16, 1.0)): town.tree(x, y, s_, int(x))
    for x in (-20, 20): town.place("roads/light-curved", (x, 6, 0), 0 if x < 0 else 180)
    for (x, y) in ((-9, 26), (9, 26)):
        prim("box", (3, 3, 1.6), (x, y, 0.8), mat((170, 75, 55), 0.8), bevel=0.05); prim("ball", (3.2, 3.2, 2.2), (x, y, 2.3), mat((70, 140, 60), 0.8))

    # ---------- Mom: real-Roblox-style avatar (classic templates, bun hair tinted red, ^^ face) ----------
    mom = blocky.build(D, "mom", {"skin": (238, 128, 78), "shirt_tpl": R + "mom_shirt.png", "pants_tpl": R + "mom_pants.png", "hair": None})
    hair = blocky.wear(D, mom, 1044357592); hair2 = blocky.wear(D, mom, 1012594937)
    hm = mat((200, 30, 25), 0.55)
    for o in list(hair.children_recursive) + list(hair2.children_recursive):
        if o.type == 'MESH':
            m = o.material_slots[0].material.copy(); pb = m.node_tree.nodes["Principled BSDF"]
            img = [n for n in m.node_tree.nodes if n.type == 'TEX_IMAGE']
            mx = m.node_tree.nodes.new("ShaderNodeMixRGB"); mx.blend_type = 'MULTIPLY'; mx.inputs[0].default_value = 1; mx.inputs[2].default_value = (1.6, 0.12, 0.06, 1)
            if img: m.node_tree.links.new(img[0].outputs["Color"], mx.inputs[1])
            else: mx.inputs[1].default_value = (1, 1, 1, 1)
            m.node_tree.links.new(mx.outputs[0], pb.inputs["Base Color"]); o.material_slots[0].material = m
    for k, fo in mom["faces"].items(): fo.hide_render = k != "happy"
    # walking toward the camera: Roblox default walk (arms and legs swing in opposition, smooth sine)
    start, end_ = Vector((0.6, 12.0, 0)), Vector((0.0, 4.0, 0))
    mom["root"].rotation_euler = (0, 0, 0)
    for f in range(0, 121):
        u = f / 120; p = start.lerp(end_, u); ph = f / 30 * math.tau * 0.85
        mom["root"].location = (p.x, p.y, abs(math.sin(ph)) * 0.08); mom["root"].keyframe_insert("location", frame=f)
        sw = math.sin(ph) * 32
        for j, v in (("ll", sw), ("rl", -sw), ("la", -sw * 0.9), ("ra", sw * 0.9)):
            mom[j].rotation_euler = (math.radians(v), 0, 0); mom[j].keyframe_insert("rotation_euler", frame=f)
    # background parade-goers
    for k, (x, y, c) in enumerate(((-7, 24, (60, 90, 200)), (6, 23, (230, 200, 40)), (-12, 30, (40, 40, 45)), (11, 31, (200, 60, 60)), (3, 34, (250, 250, 250)))):
        b = blocky.build(D, f"bg{k}", {"skin": random.choice([(240, 155, 105), (245, 205, 45), (200, 130, 90)]), "shirt": c, "pants": (40, 40, 50), "hair": (60, 40, 30) if k % 2 else (220, 40, 30)})
        b["root"].location = (x, y, 0); b["root"].rotation_euler = (0, 0, math.radians(random.uniform(-30, 30)))
    # glowing step circle + floating notes
    glow = mat((255, 235, 170), 0.4, emit=1.2, alpha=0.35)
    for k in range(2): town._cyl((0.5 - k * 1.0, 9.6 + k * 1.6, 0.03), 0.6, 0.6, 0.02, glow, 32, "step_glow")
    for k in range(4):
        n = K.plane_image(R + "note.png", (0.9, 0.9), (random.choice((-2.4, 2.6)), 4.5 + k * 1.5, 1.5 + k * 0.8), emit=2.0)
    # ---------- camera: chest height, 35mm, shallow focus on Mom, dollying back ----------
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam); sc.camera = cam
    cam.data.lens = 30; cam.data.dof.use_dof = True; cam.data.dof.focus_object = mom["waist"]; cam.data.dof.aperture_fstop = 1.6
    for f, y in ((0, 3.5), (120, -4.5)):
        cam.location = (0.4, y, 3.4); cam.keyframe_insert("location", frame=f)
    tgt = empty("tgt", (0.2, 8, 4.6))
    c = cam.constraints.new("TRACK_TO"); c.target = tgt; c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'
    for f, y in ((0, 12.0), (120, 4.0)): tgt.location = (0.3, y, 3.0); tgt.keyframe_insert("location", frame=f)

sc.use_nodes = True; ct = sc.node_tree
rl = ct.nodes["Render Layers"]; rl.scene = sc; comp = ct.nodes["Composite"]
hs = ct.nodes.new("CompositorNodeHueSat"); hs.inputs["Saturation"].default_value = 1.12
cb = ct.nodes.new("CompositorNodeColorBalance"); cb.correction_method = 'LIFT_GAMMA_GAIN'; cb.gain = (1.05, 1.0, 0.93); cb.lift = (1.0, 0.99, 0.98)
ct.links.new(rl.outputs["Image"], hs.inputs["Image"]); ct.links.new(hs.outputs["Image"], cb.inputs["Image"]); ct.links.new(cb.outputs["Image"], comp.inputs["Image"])
sc.render.resolution_x, sc.render.resolution_y = 480, 640; sc.render.resolution_percentage = 100
for f in (40, 70, 100):
    with bpy.context.temp_override(scene=sc):
        sc.frame_set(f); sc.render.filepath = R + f"test_{f}.png"; bpy.ops.render.render(write_still=True)
