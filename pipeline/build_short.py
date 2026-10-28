"""Blender entry (run by make_short.py): builds every set from the story module, cuts the edit, packs everything
into render/<slug>.blend.   blender -b -P build_short.py -- <story.json> [--preview]"""
import os, sys, json, importlib
import bpy
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, HERE + "/stories")
import shortkit as K

REPO = os.path.dirname(HERE)
D = os.environ.get('SHORTS_WORK', os.path.join(REPO, 'work')) + '/'
args = sys.argv[sys.argv.index("--") + 1:]
story = json.load(open(args[0])); preview = "--preview" in args
timed = json.load(open(D + "lines_timed.json"))


class Ctx:
    def __init__(self):
        self.D = D; self.A = D + "short/"; self.story = story; self.timed = timed
        self.M = {k: v["id"] for k, v in story["models"].items()}
        self.short = K.Short(story["title"], timed)
        self.overlays = []

    def L(self, i): return self.short.line_frames(i)

    def overlay(self, name, f0, f1, channel=7): self.overlays.append((self.A + name, f0, f1, channel))


bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.scene.name = "SHORT"  # the active scene is what `blender -b file.blend -a` renders
ctx = Ctx()
mod = importlib.import_module(story["module"])
mod.build(ctx)

S = ctx.short
words = [(p, S.frame(s), S.frame(e)) for p, s, e in json.load(open(ctx.A + "words.json"))]
S.assemble(D + "voice.wav", words, ctx.overlays)
out_blend = os.path.join(REPO, "render", story["slug"] + ".blend")
S.output("//" + story["slug"] + ".mp4")
for o in bpy.data.objects:
    if o.animation_data and o.animation_data.action:
        for fc in o.animation_data.action.fcurves:
            if fc.data_path in ("hide_render", "hide_viewport"):
                for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=out_blend, compress=True, relative_remap=True)
print("SAVED", out_blend, "frames", S.total, "shots", len(S.shots))

if preview:
    pv = D + "short/preview/"; os.makedirs(pv, exist_ok=True)
    m = S.master; m.render.resolution_percentage = 30
    for sc in bpy.data.scenes: sc.eevee.taa_render_samples = 8
    m.render.image_settings.file_format = 'PNG'
    frames = [int((a + b) / 2) for _, _, a, b, _ in sorted(S.shots, key=lambda s: s[2])]
    pick = [x for x in args if x.startswith("--frames=")]
    if pick: frames = [int(v) for v in pick[0].split("=")[1].split(",")]
    for f in frames:
        m.frame_set(f); m.render.filepath = pv + f"f{f:04d}.png"
        bpy.ops.render.render(write_still=True, scene=m.name)
    print("PREVIEW", len(frames))
