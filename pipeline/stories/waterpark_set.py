"""The water park set for waterpark.py: pool, deck, kiddie pool, lounge chairs, umbrellas, lifeguard tower, high dive,
a big open slide ending in the kiddie pool, snack stand, trees and a fence. Everything is built inside the given Set.
Key places (x, y, z top):
  POOL        x -20..20, y 2..26, water surface z -0.5 (deep end near the high dive at y 26)
  KIDDIE      circle at (-26, -10), r 5, water z -0.15 (the slide ends here)
  CHAIRS      family chairs on the deck at y -5, x 4..12; LIFEGUARD tower at (23, -2) seat z 6.2
  HIGH DIVE   ladder at (-8, 30), board top z 9.0 reaching out to y 22
  SLIDE       tower top (-34, 18, 12) curving down to the kiddie pool"""
import math, random
import bpy
from mathutils import Vector
import shortkit as K
from shortkit import prim, mat, empty
import town, toys

POOL = (-20, 20, 2, 26); WATER_Z = -0.5; KIDDIE = (-26, -10, 5.0); TOWER = (23, -2); DIVE = (-8, 30)


def _tiled(path, scale, rough=0.4):
    m = K.image_mat(path); nt = m.node_tree; img = [n for n in nt.nodes if n.type == 'TEX_IMAGE'][0]
    geo = nt.nodes.new("ShaderNodeNewGeometry"); mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (scale,) * 3
    nt.links.new(geo.outputs["Position"], mp.inputs["Vector"]); nt.links.new(mp.outputs[0], img.inputs[0])
    nt.nodes["Principled BSDF"].inputs["Roughness"].default_value = rough
    return m


def water_mat(c=(70, 175, 225)):
    m = bpy.data.materials.new("water"); m.use_nodes = True; nt = m.node_tree; pb = nt.nodes["Principled BSDF"]
    pb.inputs["Base Color"].default_value = K.lin(c); pb.inputs["Roughness"].default_value = 0.04
    pb.inputs["Alpha"].default_value = 0.72; pb.inputs["IOR"].default_value = 1.33
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 1.2; nz.inputs["Detail"].default_value = 4
    tc = nt.nodes.new("ShaderNodeTexCoord"); mp = nt.nodes.new("ShaderNodeMapping")
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"]); nt.links.new(mp.outputs[0], nz.inputs["Vector"])
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.25
    nt.links.new(nz.outputs["Fac"], bp.inputs["Height"]); nt.links.new(bp.outputs[0], pb.inputs["Normal"])
    # ripples drift over time
    mp.inputs["Location"].default_value = (0, 0, 0); mp.inputs["Location"].keyframe_insert("default_value", frame=0)
    mp.inputs["Location"].default_value = (0.0, 0.0, 3.0); mp.inputs["Location"].keyframe_insert("default_value", frame=4000)
    for fc in nt.animation_data.action.fcurves:
        for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
    m.blend_method = 'BLEND'; m.shadow_method = 'NONE'; m.use_screen_refraction = True
    return m


def torus(name, R, r, loc, m, seg=24, ring=12):
    import bmesh
    bm = bmesh.new(); rows = []
    for i in range(seg):
        a = i / seg * math.tau; row = []
        for j in range(ring):
            b = j / ring * math.tau
            row.append(bm.verts.new(((R + r * math.cos(b)) * math.cos(a), (R + r * math.cos(b)) * math.sin(a), r * math.sin(b))))
        rows.append(row)
    for i in range(seg):
        for j in range(ring):
            bm.faces.new((rows[i][j], rows[(i + 1) % seg][j], rows[(i + 1) % seg][(j + 1) % ring], rows[i][(j + 1) % ring]))
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    me.materials.append(m); o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o); o.location = loc
    return o


def umbrella(x, y, c):
    r = empty("umbrella", (x, y, 0))
    prim("cylY", (0.18, 0.18, 6.4), (0, 0, 3.2), mat((240, 240, 240), 0.4), parent=r)
    prim("cone", (6, 6, 1.6), (0, 0, 6.6), mat(c, 0.5), parent=r)
    return r


def lounge(x, y, yaw=0, c=(250, 250, 250), cushion=(80, 170, 230)):
    """A pool lounge chair facing -Y at yaw 0 (back raised at +Y). Seat top at z 1.3."""
    r = empty("lounge", (x, y, 0)); r.rotation_euler = (0, 0, math.radians(yaw)); fm = mat(c, 0.4)
    prim("box", (2.2, 5.2, 0.3), (0, 0, 1.0), fm, parent=r, bevel=0.08)
    prim("box", (2.0, 5.0, 0.2), (0, 0, 1.2), mat(cushion, 0.7), parent=r, bevel=0.06)
    b = prim("box", (2.0, 2.2, 0.25), (0, 2.6, 2.0), mat(cushion, 0.7), rot=(-55, 0, 0), parent=r, bevel=0.06)
    for dx in (-0.9, 0.9):
        for dy in (-2.2, 2.2): prim("box", (0.2, 0.2, 1.0), (dx, dy, 0.5), fm, parent=r)
    return r


def slide_curve(m):
    """An open half-pipe slide from the tower top down to the kiddie pool (a curve with a U-shaped bevel)."""
    prof = bpy.data.curves.new("slide_profile", "CURVE"); prof.dimensions = '2D'
    sp = prof.splines.new("POLY"); pts = [(math.cos(a) * 1.4, -math.sin(a) * 1.4) for a in [math.pi * i / 12 for i in range(13)]]
    sp.points.add(len(pts) - 1)
    for p, (x, y) in zip(sp.points, pts): p.co = (x, y, 0, 1)
    po = bpy.data.objects.new("slide_profile", prof); bpy.context.scene.collection.objects.link(po); po.hide_render = True
    cu = bpy.data.curves.new("slide", "CURVE"); cu.dimensions = '3D'; cu.bevel_mode = 'OBJECT'; cu.bevel_object = po; cu.use_fill_caps = False
    path = [(-34, 18, 12.4), (-40, 12, 10.5), (-36, 4, 8.6), (-28, 4, 6.6), (-26, 10, 5.0), (-33, 12, 3.6), (-38, 4, 2.4), (-33, -4, 1.2), (-27, -8, 0.3)]
    sp = cu.splines.new("NURBS"); sp.points.add(len(path) - 1)
    for p, c in zip(sp.points, path): p.co = (*c, 1)
    sp.use_endpoint_u = True; sp.order_u = 4; sp.resolution_u = 24
    o = bpy.data.objects.new("slide", cu); bpy.context.scene.collection.objects.link(o); cu.materials.append(m)
    return o, path


def build(st, A, seed=3):
    """Build the park inside Set st. Returns props a story animates (floaties, whistle, towels, sign...)."""
    random.seed(seed)
    town.sky(st, 0.9, 3.2, (50, 0, -30))  # Filmic, soft and neutral like the reference (no blown-out whites)
    st.scene.view_settings.look = 'Medium Contrast'; st.scene.view_settings.exposure = 0.2
    out = {}
    deck = _tiled(A + "deck_tile.png", 0.12, 0.6)
    x0, x1, y0, y1 = POOL
    # deck around the pool (four slabs), the pool basin and its water
    town.slab((200, 100, 1), (0, y0 - 50, -0.5), deck, "deck_s"); town.slab((200, 60, 1), (0, y1 + 30, -0.5), deck, "deck_n")
    town.slab((80, y1 - y0, 1), (x0 - 40, (y0 + y1) / 2, -0.5), deck, "deck_w"); town.slab((80, y1 - y0, 1), (x1 + 40, (y0 + y1) / 2, -0.5), deck, "deck_e")
    tile = _tiled(A + "pool_tile.png", 0.25, 0.2)
    town.slab((x1 - x0, y1 - y0, 0.2), ((x0 + x1) / 2, (y0 + y1) / 2, -6.0), tile, "pool_floor")
    for (sx, sy, cx, cy) in (((x1 - x0), 0.3, (x0 + x1) / 2, y0), ((x1 - x0), 0.3, (x0 + x1) / 2, y1), (0.3, y1 - y0, x0, (y0 + y1) / 2), (0.3, y1 - y0, x1, (y0 + y1) / 2)):
        town.slab((sx, sy, 6), (cx, cy, -3), tile, "pool_wall")
    town.slab((x1 - x0 + 1.2, 0.6, 0.15), ((x0 + x1) / 2, y0 - 0.3, 0.07), mat((250, 250, 250), 0.4), "coping")
    wm = water_mat(); water = town.slab((x1 - x0, y1 - y0, 0.02), ((x0 + x1) / 2, (y0 + y1) / 2, WATER_Z), wm, "water"); out["water"] = water
    for k in range(5):  # lane ropes of floats
        x = x0 + 6 + k * 7
        for j in range(12): prim("ball", (0.5, 0.5, 0.35), (x, y0 + 1 + j * 2, WATER_Z + 0.05), mat((250, 70, 70) if j % 2 else (250, 250, 250), 0.4))
    # kiddie pool
    kx, ky, kr = KIDDIE
    town._cyl((kx, ky, -0.45), kr + 0.6, kr + 0.6, 0.9, mat((250, 250, 250), 0.4), 40, "kiddie_rim")
    town._cyl((kx, ky, -0.12), kr, kr, 0.06, water_mat((110, 205, 235)), 40, "kiddie_water")
    out["kiddie"] = (kx, ky)
    # loungers, umbrellas, towels
    chairs = [(4, -5), (8, -5), (12, -5), (-6, -5), (-10, -5), (18, -9), (-14, -9)]
    for k, (x, y) in enumerate(chairs): lounge(x, y, 180, cushion=random.choice([(80, 170, 230), (250, 150, 80), (120, 210, 150), (240, 120, 160)]))
    for x, c in ((6, (240, 90, 90)), (-8, (250, 210, 60)), (16, (80, 170, 230))): umbrella(x, -9.5, c)
    out["towels"] = []
    for x in (4, 8):
        t = prim("box", (1.9, 3.6, 0.08), (x, -5.2, 1.36), mat(random.choice([(250, 130, 160), (120, 190, 250)]), 0.8)); out["towels"].append(t)
    # lifeguard tower
    tx, ty = TOWER; tw = mat((250, 250, 250), 0.4); red = mat((225, 40, 45), 0.4)
    for dx in (-1.2, 1.2):
        for dy in (-1.2, 1.2): prim("box", (0.3, 0.3, 6.2), (tx + dx, ty + dy, 3.1), tw)
    prim("box", (3.0, 3.0, 0.3), (tx, ty, 6.2), tw, bevel=0.05); prim("box", (2.6, 0.3, 2.2), (tx, ty + 1.3, 7.4), red, bevel=0.05)
    prim("box", (0.3, 2.6, 1.2), (tx - 1.3, ty, 6.9), tw); prim("box", (0.3, 2.6, 1.2), (tx + 1.3, ty, 6.9), tw)
    K.plane_image(A + "lifeguard.png", (2.4, 1.6), (tx, ty - 1.6, 4.8), rot=(90, 0, 0))
    for z in range(1, 6): prim("box", (2.0, 0.2, 0.2), (tx, ty - 1.5, z * 1.0), tw)
    for dx in (-1.0, 1.0): prim("box", (0.2, 0.2, 6.0), (tx + dx, ty - 1.5, 3.0), tw)
    out["tower"] = (tx, ty)
    # high dive (ladder at the far end, the board reaching over the deep end)
    dx_, dy_ = DIVE; steel = mat((200, 205, 215), 0.25, metal=0.8)
    for sx in (-1.0, 1.0): prim("box", (0.3, 0.3, 9.0), (dx_ + sx, dy_, 4.5), steel)
    for z in range(1, 9): prim("box", (2.0, 0.18, 0.18), (dx_, dy_ - 0.1, z * 1.0), steel)
    prim("box", (1.6, 8.5, 0.3), (dx_, dy_ - 4.2, 9.0), mat((60, 150, 230), 0.4), bevel=0.05)
    for sx in (-1.0, 1.0): prim("box", (0.12, 2.5, 0.12), (dx_ + sx, dy_ - 0.8, 10.0), steel)
    out["dive"] = (dx_, dy_)
    # the big slide: tower + open half-pipe down into the kiddie pool
    sm = mat((250, 200, 40), 0.25)
    for sx in (-1.5, 1.5):
        for sy in (-1.5, 1.5): prim("box", (0.35, 0.35, 12.2), (-34 + sx, 21 + sy, 6.1), mat((60, 150, 230), 0.4))
    prim("box", (4, 4, 0.4), (-34, 21, 12.2), mat((60, 150, 230), 0.4))
    for z in range(1, 12): prim("box", (2.2, 0.2, 0.2), (-34, 23.2, z * 1.0), mat((250, 250, 250), 0.4))
    sl, path = slide_curve(sm); out["slide_path"] = path
    for p in path[1:-1]: prim("cylY", (0.3, 0.3, p[2]), (p[0], p[1], p[2] / 2), mat((250, 250, 250), 0.4))
    # snack stand, park sign, fence, trees
    prim("box", (10, 5, 5), (30, -20, 2.5), mat((250, 240, 220), 0.6), bevel=0.1); prim("box", (11, 6, 0.6), (30, -20, 5.4), mat((240, 90, 70), 0.5))
    K.plane_image(A + "snack_sign.png", (5.4, 3.0), (30, -17.4, 3.4))
    K.plane_image(A + "park_sign.png", (16, 5), (0, 45, 9)); prim("box", (16.5, 0.4, 5.5), (0, 45.3, 9), mat((250, 250, 250), 0.4))
    for sx in (-7, 7): prim("cylY", (0.5, 0.5, 9), (sx, 45.3, 4.5), mat((250, 250, 250), 0.4))
    for k in range(-30, 31, 3): prim("box", (0.2, 0.2, 3), (k * 2, 48, 1.5), mat((250, 250, 250), 0.4))
    prim("box", (122, 0.2, 0.2), (0, 48, 2.8), mat((250, 250, 250), 0.4))
    for k in range(-5, 6): town.tree(k * 13, 56 + (k % 2) * 4, 1.0 + 0.15 * (k % 3), k)
    for k in range(-5, 6): town.pine(k * 15 + 6, 72, 1.0, k)
    for k in range(3): town.tree(-52, -10 + k * 14, 1.1, 40 + k); town.tree(52, -10 + k * 14, 1.1, 50 + k)
    # floaties and pool toys
    out["ring"] = torus("floatie", 1.0, 0.42, (4.0, 4.0, WATER_Z + 0.25), mat((250, 90, 120), 0.3))
    for k, (x, y, c) in enumerate(((-12, 14, (250, 210, 60)), (8, 18, (90, 200, 250)), (-4, 9, (120, 220, 140)))):
        torus(f"tube{k}", 1.4, 0.55, (x, y, WATER_Z + 0.3), mat(c, 0.3))
    out["whistle"] = prim("box", (0.25, 0.5, 0.2), (0, -300, 0), mat((240, 200, 30), 0.3))
    out["sign"] = toys.card(A + "nokarens_sign.png", 3.6, 4.7); out["sign"].location = (14, 1.0, 4.5)
    prim("cylY", (0.25, 0.25, 4.2), (14, 1.25, 2.1), mat((250, 250, 250), 0.4))
    return out
