"""Reference #3 acting (simple Roblox-animation style): characters mostly stand and use clear gestures, small head tilts
and a gentle sway while talking, and short stiff walks.
    act(av, f, "point")            # hold a gesture from frame f (eases in over 4 frames)
    act(av, f, "cross")            # arms crossed;  act(av, f, None) back to rest
    chatter(av, f0, f1)            # talking: head tilts side to side + small body sway
    tilt(av, f, deg)               # one head tilt (+ = to the character's left)
Blocky joints (degrees): ra/la x<0 raises the arm forward; ra y>0 / la y<0 swing it out sideways; when raised,
ra z>0 / la z<0 swing it outward. head y>0 tilts to the character's left, head z turns it."""
from shortkit import pose, rest

GESTURES = {
    "point": dict(ra=(-90, 0, 0)),
    "point_left": dict(la=(-90, 0, 0)),
    "point_up": dict(ra=(-165, 0, 0)),
    "cross": dict(ra=(-72, 0, -38), la=(-72, 0, 38)),            # arms crossed
    "hips": dict(ra=(-8, 22, 0), la=(-8, -22, 0)),                 # hands on hips (arms angled out)
    "head": dict(ra=(-165, 0, -28)),                               # hand on head (stress)
    "facepalm": dict(ra=(-128, 0, -34)),
    "shrug": dict(ra=(-28, 0, 38), la=(-28, 0, -38)),
    "arms_out": dict(ra=(-20, 75, 0), la=(-20, -75, 0)),           # "what?!" / presenting
    "arms_up": dict(ra=(-170, 0, 18), la=(-170, 0, -18)),          # cheer / panic
    "wave": dict(ra=(-160, 0, 25)),
    "phone": dict(ra=(-105, 0, -22)),                              # phone held up in front of the face
    "hold": dict(ra=(-60, 0, -10), la=(-60, 0, 10)),               # holding something in front
    "hug": dict(ra=(-85, 0, -35), la=(-85, 0, 35)),
    "fists": dict(ra=(-40, 0, -12), la=(-40, 0, 12)),              # angry fists down at the sides, a bit forward
    "stop": dict(ra=(-100, 0, 0), la=(-100, 0, 0)),                # both hands out: stop / freeze
    "shush": dict(ra=(-152, 0, -34)),                              # finger to the lips
    "both_head": dict(ra=(-165, 0, -28), la=(-165, 0, 28)),        # both hands on the head (meltdown)
    "reach": dict(ra=(-78, 0, -12)),                               # reaching forward to grab
    "read": dict(ra=(-62, 0, -18), la=(-62, 0, 18)),               # holding a book open in front
    "clap": dict(ra=(-70, 0, -32), la=(-70, 0, 32)),
}
ARMS = ("ra", "la", "ra_elbow", "la_elbow")


def act(av, f, name, ease=7):
    """Switch arms to a gesture at frame f (None = arms down)."""
    rest(av, f, "ra", "la", ease=ease)
    if name: pose(av, f, ease, **GESTURES[name])


def tilt(av, f, deg, turn=0.0, ease=5):
    pose(av, f, ease, head=(0, deg, turn))


def chatter(av, f0, f1, amount=1.0, period=18):
    """Talking like the reference: the head tilts side to side and the body sways a little, on a steady rhythm."""
    k = 0
    for f in range(f0, f1, period):
        s = 1 if k % 2 else -1
        pose(av, f + period // 2, period // 2, head=(2 * amount, 6 * s * amount, 3 * s * amount), waist=(0, 2.5 * s * amount, 0))
        k += 1
    pose(av, f1 + 4, 6, head=(0, 0, 0), waist=(0, 0, 0))


def bounce_walk(av, f0, f1, a, b, step=7):
    """Stiff, bouncy Roblox walk: legs and arms swing straight, the body bobs on each step."""
    from shortkit import walk, _key
    walk(av, f0, f1, a, b, step, 32)
    for i, f in enumerate(range(f0, f1, step)):
        z = a[2] + (b[2] - a[2]) * (f - f0) / max(1, f1 - f0)
        x = a[0] + (b[0] - a[0]) * (f - f0) / max(1, f1 - f0); y = a[1] + (b[1] - a[1]) * (f - f0) / max(1, f1 - f0)
        _key(av["root"], "location", f, (x, y, z))
        u = (f + step // 2 - f0) / max(1, f1 - f0)
        if u < 1: _key(av["root"], "location", f + step // 2, (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u, z + 0.18 * av.get("scale", 1.0)))
    _key(av["root"], "location", f1, b)
