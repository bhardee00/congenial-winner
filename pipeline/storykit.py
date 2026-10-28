"""Helpers every story module uses (moved out of stories/parrot.py so new shorts share them).
    kit = Kit(ctx)
    for (a, b) in kit.seg(12, "then", ("he", 1), 0.5): ...   # split a line into shots at words / fractions
    kit.sh(st, a, b, cam_loc, aim, lens, dl=..., dt=..., pz=frame)  # one moving shot (+ optional punch zoom)
    kit.speak(av, i)                                           # head motion while a character says line i
Frames are frames of the final video; characters face -Y at rest (yaw 180 faces +Y)."""
import math
import bpy
from mathutils import Vector
import shortkit as K
from shortkit import prim, mat, camera, punch, shake, lin
import avatar


def rel(p, d): return tuple(a + b for a, b in zip(p, d))


def norm(w): return w.strip('.,?!"').lower()


def wall_mat(c, rough=0.8):
    """Walls and ceilings don't cast shadows, so the sun lights rooms like Roblox's bright interiors."""
    m = bpy.data.materials.new("wall"); m.use_nodes = True; pb = m.node_tree.nodes["Principled BSDF"]
    pb.inputs["Base Color"].default_value = lin(c); pb.inputs["Roughness"].default_value = rough
    m.shadow_method = 'NONE'; return m


def glasses(av, c=(25, 25, 30), dark=False):
    hc = Vector((0, -0.66, 0.7)); m = mat(c, 0.3)
    lens = mat((15, 15, 18), 0.1) if dark else mat((215, 235, 255), 0.05, alpha=0.25)
    for sx in (-0.27, 0.27):
        prim("cyl", (0.04, 0.42, 0.34), hc + Vector((sx, 0, 0)), lens, rot=(0, 0, 90), parent=av["head"])
        if not dark:
            for dz in (-0.17, 0.17): prim("box", (0.42, 0.05, 0.05), hc + Vector((sx, 0, dz)), m, parent=av["head"])
            for dx in (-0.21, 0.21): prim("box", (0.05, 0.05, 0.38), hc + Vector((sx + dx, 0, 0)), m, parent=av["head"])
    prim("box", (0.2, 0.05, 0.05), hc + Vector((0, 0, 0.05)), m, parent=av["head"])
    for sx in (-0.48, 0.48): prim("box", (0.05, 0.6, 0.05), hc + Vector((sx, 0.3, 0.05)), m, parent=av["head"])


def hold(av, obj, hand="ra", loc=(0, -0.15, 0), rot=(0, 0, 0)):
    obj.parent = av["grips"][hand]; obj.location = loc; obj.rotation_euler = [math.radians(a) for a in rot]; return obj


class Kit:
    def __init__(self, ctx):
        self.ctx, self.S, self.L, self.timed = ctx, ctx.short, ctx.L, ctx.timed

    def wf(self, i, word, nth=0):
        """Frame line i's word starts on (nth occurrence)."""
        hits = [w for w in self.timed[i]["words"] if norm(w[0]) == word]
        return self.S.frame(hits[min(nth, len(hits) - 1)][1]) if hits else self.L(i)[0]

    def seg(self, i, *marks):
        """Split line i into shots: cut just before each mark - a word (matched in order), ("word", n) for its n-th
        occurrence, or a fraction of the line. Returns [(start, end), ...]."""
        a, b = self.L(i); ws = self.timed[i]["words"]; out = [a]; k = 0
        for m in marks:
            if isinstance(m, float): f = int(a + (b - a) * m)
            else:
                if isinstance(m, tuple):
                    m, nth = m; k = [j for j, w in enumerate(ws) if norm(w[0]) == m][nth]
                while k < len(ws) and norm(ws[k][0]) != m: k += 1
                if k == len(ws): raise ValueError(f"line {i}: no word '{m}'")
                f = self.S.frame(ws[k][1]) - 1; k += 1
            out.append(max(f, out[-1] + 6))
        out.append(max(b, out[-1] + 6))
        return list(zip(out, out[1:]))

    def sh(self, st, f0, f1, loc, tgt, lens=24, dl=None, dt=None, cap="auto", pz=None, amount=1.25, look=None):
        """One shot: camera at loc aimed at tgt, easing by dl / dt over the shot (else a slow push-in), with an
        optional punch zoom at frame pz."""
        name = f"{st.name}_{f0}_{len(st.cams)}"
        if dl or dt: c = camera(st, name, loc, tgt, lens, f0, f1, rel(loc, dl or (0, 0, 0)), rel(tgt, dt or (0, 0, 0)))
        else: c = camera(st, name, loc, tgt, lens)
        self.S.shot(st, name, f0, f1, caption=cap, look=look)
        if pz: punch(c, pz, amount)
        return c

    def follow(self, st, f0, f1, subject, offset, look=(0, 0, 0), lens=24):
        c = K.follow(st, f"{st.name}_fol_{f0}_{len(st.cams)}", subject, offset, look, lens); self.S.shot(st, c.name, f0, f1); return c

    def speak(self, av, i, amount=1.0, f0=None, f1=None):
        """Head motion while av says line i (or the words between f0 and f1)."""
        a, b = self.L(i); f0 = f0 or a; f1 = f1 or b
        fr = [self.S.frame(w[1]) for w in self.timed[i].get("words", []) if f0 <= self.S.frame(w[1]) < f1]
        avatar.talk(av, fr or list(range(f0, f1, 8)), amount)
