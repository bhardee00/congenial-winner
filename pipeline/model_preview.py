"""Contact sheet of converted Creator Store models: blender -b -P model_preview.py -- out.png id1 id2 ...
Each model is scaled to the same size and labelled with its id so candidates can be compared at a glance."""
import os, sys, math
import bpy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import models
from mathutils import Vector
D = os.environ.get('SHORTS_WORK', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'work')) + '/'
args = sys.argv[sys.argv.index("--") + 1:]; out, ids = args[0], args[1:]

bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.75, 0.82, 0.9, 1); w.node_tree.nodes["Background"].inputs[1].default_value = 1.0
sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN")); sc.collection.objects.link(sun)
sun.data.energy = 3; sun.rotation_euler = (math.radians(50), 0, math.radians(-35))
cols = 4; gap = 6.0
for i, a in enumerate(ids):
    x, y = (i % cols) * gap, -(i // cols) * gap * 1.2
    r = models.place(D, a, (x, y, 0)); bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(c) for o in r.children for c in o.bound_box]
    lo = Vector([min(p[k] for p in pts) for k in range(3)]); hi = Vector([max(p[k] for p in pts) for k in range(3)])
    s = 4.0 / max(max(hi - lo), 1e-3); r.scale = (s, s, s)
    r.location = (x - ((lo.x + hi.x) / 2 - x) * s, y - ((lo.y + hi.y) / 2 - y) * s, -lo.z * s)
    bpy.ops.object.text_add(location=(x - 2, y - 2.6, 0)); t = bpy.context.active_object
    t.data.body = str(a); t.data.size = 0.7
rows = (len(ids) + cols - 1) // cols
cd = bpy.data.cameras.new("c"); cd.type = 'ORTHO'; cd.ortho_scale = max(cols, rows) * gap * 1.1
cam = bpy.data.objects.new("c", cd); sc.collection.objects.link(cam); sc.camera = cam
cx, cy = (cols - 1) * gap / 2, -(rows - 1) * gap * 1.2 / 2
cam.location = (cx, cy - 60, 40); cam.rotation_euler = (Vector((cx, cy, 1.5)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
sc.render.engine = 'BLENDER_EEVEE'; sc.eevee.taa_render_samples = 16
sc.render.resolution_x = 1600; sc.render.resolution_y = 1600
sc.render.filepath = out; bpy.ops.render.render(write_still=True)
