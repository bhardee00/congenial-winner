"""Keyframing that holds still between actions: key(o, "location", f, v, ease=6) first pins the value the property
already has at f - ease, so a move only happens over those ease frames instead of drifting from the last key."""


def value(o, path, f):
    cur = list(getattr(o, path))
    act = o.animation_data.action if o.animation_data else None
    if act:
        for i in range(len(cur)):
            fc = act.fcurves.find(path, index=i)
            if fc: cur[i] = fc.evaluate(f)
    return cur


def key(o, path, f, v=None, ease=None):
    if ease:
        setattr(o, path, value(o, path, f - ease)); o.keyframe_insert(path, frame=f - ease)
    if v is not None: setattr(o, path, v)
    o.keyframe_insert(path, frame=f)
