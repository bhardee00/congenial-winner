"""Quick check of the built avatar: blender -b -P avatar_preview.py  ->  work/avatar_preview_{front,three_quarter,pose}.png"""
import os, sys, math
import bpy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import avatar
from mathutils import Vector
D = os.environ.get('SHORTS_WORK', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'work')) + '/'

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
av = avatar.build(D)

w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.55, 0.7, 0.9, 1); w.node_tree.nodes["Background"].inputs[1].default_value = 0.8
sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN")); sc.collection.objects.link(sun)
sun.data.energy = 3.5; sun.rotation_euler = (math.radians(50), 0, math.radians(-30))
bpy.ops.mesh.primitive_plane_add(size=30); g = bpy.context.active_object
gm = bpy.data.materials.new("g"); gm.use_nodes = True; gm.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.25, 0.45, 0.2, 1)
g.data.materials.append(gm)

cd = bpy.data.cameras.new("cam"); cd.lens = 50
cam = bpy.data.objects.new("cam", cd); sc.collection.objects.link(cam); sc.camera = cam
def look(loc, target=(0, 0, 3)):
    cam.location = loc; cam.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()

sc.render.engine = 'BLENDER_EEVEE'; sc.eevee.taa_render_samples = 32; sc.eevee.use_gtao = True
sc.eevee.use_soft_shadows = True; sc.eevee.shadow_cube_size = '1024'
sc.render.resolution_x = 720; sc.render.resolution_y = 960
for name, loc in (("front", (0, -13, 3.2)), ("three_quarter", (8, -10, 4.5))):
    look(loc); sc.render.filepath = D + f"avatar_preview_{name}.png"; bpy.ops.render.render(write_still=True)
for k, r in (("ra", (-80, 0, 50)), ("ra_elbow", (-30, 0, 0)), ("la", (10, 0, -10)), ("ll", (25, 0, 0)), ("ll_knee", (-40, 0, 0)), ("head", (10, 0, 20))):
    av[k].rotation_euler = [math.radians(v) for v in r]
av["faces"]["smile"].hide_render = True; av["faces"]["shock"].hide_render = False
look((-6, -11, 4.2)); sc.render.filepath = D + "avatar_preview_pose.png"; bpy.ops.render.render(write_still=True)
