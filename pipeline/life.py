"""Detailed acting layer (user: "make it as detailed as possible"), on top of acting.py for blocky R6 characters.
    life.alive(av)                         # breathing + slow weight shift for the whole short (fcurve modifiers)
    life.look(av, f, point, ease=6)        # turn the head toward a point (and a little of the body if it's far round)
    life.listen(av, speaker_av, f0, f1)    # look at whoever talks; small nods / blinks of attention
    life.gesture_talk(av, frames, arm)     # hand beats on stressed words while talking (one arm, small and varied)
    life.act2(av, f, name)                 # a gesture with anticipation and overshoot (acting.GESTURES names)
    life.flinch(av, f) / life.recoil(av, f, back=1) / life.stomp(av, f0, f1, a, b)
    life.sit_down(av, f, seat_z, xy, face) / life.stand_up(av, f, xy, face)
Angles in degrees, frames in video frames. Everything adds to (never fights) the story's own keys: head looks use the
nod pivot's yaw, breathing and sway are fcurve modifiers on the waist."""
import math, random
from mathutils import Vector
import shortkit as K
from shortkit import pose, rest
from anim import key, value
from acting import GESTURES


def _mod_sine(o, path, index, amp, period, phase=0.0):
    if not (o.animation_data and o.animation_data.action and o.animation_data.action.fcurves.find(path, index=index)):
        o.keyframe_insert(path, index=index, frame=0)
    fc = o.animation_data.action.fcurves.find(path, index=index)
    m = fc.modifiers.new('FNGENERATOR'); m.function_type = 'SIN'; m.use_additive = True
    m.amplitude = amp; m.phase_multiplier = 2 * math.pi / period; m.phase_offset = phase
    return m


def alive(av, breath=1.0, sway=1.0, seed=None):
    """Breathing (the chest rises a hair every ~3 s) and a slow weight shift side to side (~6 s)."""
    rnd = random.Random(seed if seed is not None else sum(map(ord, av["name"])))
    w = av["waist"]
    _mod_sine(w, "rotation_euler", 0, math.radians(1.1 * breath), rnd.uniform(80, 100), rnd.uniform(0, 6))   # breathe
    _mod_sine(w, "rotation_euler", 1, math.radians(1.4 * sway), rnd.uniform(160, 200), rnd.uniform(0, 6))   # weight shift
    _mod_sine(av["neck"], "rotation_euler", 2, math.radians(1.8 * sway), rnd.uniform(130, 170), rnd.uniform(0, 6))


def _root_yaw(av, f):
    r = av["root"]; y = value(r, "rotation_euler", f)[2]
    return y + (value(r.parent, "rotation_euler", f)[2] if r.parent else 0.0)


def _root_loc(av, f):
    """World position at frame f, also for a character riding on a keyed parent (a swivel chair, a car)."""
    r = av["root"]; p = Vector(value(r, "location", f))
    if r.parent:
        from mathutils import Matrix
        py = value(r.parent, "rotation_euler", f)[2]; p = Vector(value(r.parent, "location", f)) + Matrix.Rotation(py, 3, 'Z') @ p
    return p


def look(av, f, point, ease=6, max_head=55, tilt=0.0):
    """Head turns toward point (x, y[, z]) at frame f. Beyond max_head degrees the rest is left to the story."""
    p = _root_loc(av, f); yaw_body = _root_yaw(av, f)
    want = math.atan2(point[1] - p.y, point[0] - p.x) + math.pi / 2  # yaw that faces the point (characters face -Y at 0)
    d = math.degrees((want - yaw_body + math.pi) % (2 * math.pi) - math.pi)
    d = max(-max_head, min(max_head, d))
    up = 0.0
    if len(point) > 2:
        dist = max(0.5, (Vector(point[:2]) - p.xy).length); up = -math.degrees(math.atan2(point[2] - (p.z + 4.6 * av.get("scale", 1)), dist)) * 0.6
    key(av["nod"], "rotation_euler", f, (math.radians(up), math.radians(tilt), math.radians(d)), ease)


def look_back(av, f, ease=6):
    key(av["nod"], "rotation_euler", f, (0, 0, 0), ease)


def listen(av, speaker, f0, f1, nods=True, seed=0):
    """av pays attention to speaker between f0 and f1: turns to them, small attentive nods, a tilt."""
    rnd = random.Random(seed + f0)
    sp = _root_loc(speaker, f0); look(av, f0 + rnd.randint(0, 4), (sp.x, sp.y, sp.z + 4.6 * speaker.get("scale", 1)), 6)
    if nods and f1 - f0 > 30:
        f = f0 + rnd.randint(14, 24)
        cur = value(av["nod"], "rotation_euler", f)
        key(av["nod"], "rotation_euler", f, (cur[0] + math.radians(5), cur[1] + math.radians(rnd.choice((-4, 4))), cur[2]), 4)
        key(av["nod"], "rotation_euler", f + 6, tuple(cur), 4)


def gesture_talk(av, frames, arm="ra", amount=1.0, seed=0):
    """Hand beats while talking: on some stressed words the forearm lifts and drops (blocky arms swing from the
    shoulder), alternating small open-palm and pointing beats."""
    rnd = random.Random(seed + (frames[0] if frames else 0))
    last = -99
    for f in frames:
        if f - last < 10 or rnd.random() > 0.55: continue
        lift = rnd.uniform(25, 50) * amount; out = rnd.uniform(5, 20) * (1 if arm == "ra" else -1)
        pose(av, f - 1, 3, **{arm: (-lift, 0, out)}); pose(av, f + 5, 4, **{arm: (-lift * 0.45, 0, out * 0.5)})
        last = f
    if frames: pose(av, frames[-1] + 12, 6, **{arm: (0, 0, 0)})


def act2(av, f, name, ease=5, overshoot=0.15):
    """Gesture with a little anticipation (a dip the other way) and overshoot before it settles."""
    if not name:
        rest(av, f, "ra", "la", ease=ease); return
    g = GESTURES[name]
    pre = {k: tuple(-v * 0.12 for v in r) for k, r in g.items()}
    over = {k: tuple(v * (1 + overshoot) for v in r) for k, r in g.items()}
    pose(av, f - ease, 2, **pre); pose(av, f, ease - 1, **over); pose(av, f + 4, 3, **g)


def flinch(av, f, amt=1.0):
    """Quick startle: shoulders up (arms in), head back, a little hop."""
    r = _root_loc(av, f)
    pose(av, f, 2, ra=(-25 * amt, 0, -15), la=(-25 * amt, 0, 15), waist=(-8 * amt, 0, 0))
    key(av["root"], "location", f + 2, (r.x, r.y, r.z + 0.25 * amt), 2); key(av["root"], "location", f + 6, tuple(r), 3)
    pose(av, f + 10, 5, waist=(0, 0, 0)); rest(av, f + 12, "ra", "la", ease=6)


def recoil(av, f, back=1.0, frames=8):
    """Step back from something (a slap of water, a shout): the body leans back and slides away."""
    r = _root_loc(av, f); yaw = _root_yaw(av, f)
    d = Vector((-math.sin(yaw), math.cos(yaw), 0)) * back  # behind the character (facing -Y at yaw 0)
    key(av["root"], "location", f + frames, tuple(r + d), frames)
    pose(av, f + 2, 3, waist=(-14, 0, 0)); pose(av, f + frames + 6, 6, waist=(0, 0, 0))


def stomp(av, f0, f1, a, b, step=7):
    """An angry walk: shorter faster steps, fists at the sides, a forward lean, a heavier bob."""
    from acting import bounce_walk
    bounce_walk(av, f0, f1, a, b, step)
    pose(av, f0 + 2, 3, waist=(10, 0, 0)); pose(av, f1 + 4, 4, waist=(0, 0, 0))


def sit_down(av, f, seat_z, xy, face, ease=8):
    K.sit(av, f, seat_z, xy, face, ease=ease)


def stand_up(av, f, xy, face, z=0.0, ease=8):
    K.at(av, f, (xy[0], xy[1], z), face, ease=ease); rest(av, f, "ll", "rl", "ll_knee", "rl_knee", "waist", ease=ease)


def shake_head(av, f, n=3, amt=10, step=4):
    for k in range(n * 2):
        cur = value(av["nod"], "rotation_euler", f)
        key(av["nod"], "rotation_euler", f + k * step, (cur[0], cur[1], math.radians(amt if k % 2 else -amt)), 2)
    look_back(av, f + n * 2 * step + 4, 4)


def nod_yes(av, f, n=2, amt=9, step=5):
    for k in range(n * 2):
        key(av["nod"], "rotation_euler", f + k * step, (math.radians(amt if k % 2 == 0 else 0), 0, 0), 2)
    look_back(av, f + n * 2 * step + 2, 3)
