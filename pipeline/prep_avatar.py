"""Turn the downloaded avatar (work/avatar/, from fetch_avatar.py) into work/avatar/rig.json for avatar.py in Blender.
Downloads body/accessory meshes and textures, poses the R15 parts with their rig attachments and composites
the classic shirt/pants templates over the body colour. Output is in Blender axes (Z up, character facing -Y), studs."""
import os, glob, json, re, io
import numpy as np
from PIL import Image
from rbx import read_rbxm, read_mesh
from fetch_avatar import W, asset

# brickcolor id -> rgb for the skin tones the avatar editor offers (others fall back to Nougat)
BRICK = {1: (242, 243, 243), 5: (215, 197, 154), 18: (204, 142, 105), 38: (160, 95, 53), 125: (234, 184, 146),
         128: (174, 122, 89), 192: (105, 64, 40), 226: (253, 234, 141), 359: (175, 148, 131), 364: (90, 76, 66),
         1030: (255, 204, 153), 1001: (248, 248, 248)}
# default R15 head (no head asset on the avatar): size and attachment positions
HEAD_SIZE = (1.2, 1.2, 1.2)
HEAD_ATT = {"NeckRigAttachment": (0, -0.5, 0), "HatAttachment": (0, 0.6, 0), "HairAttachment": (0, 0.6, 0),
            "FaceFrontAttachment": (0, 0, -0.6)}
# child part, parent part, rig attachment name, Blender pivot name
JOINTS = [("UpperTorso", "LowerTorso", "WaistRigAttachment", "waist"),
          ("Head", "UpperTorso", "NeckRigAttachment", "head"),
          ("LeftUpperArm", "UpperTorso", "LeftShoulderRigAttachment", "la"),
          ("LeftLowerArm", "LeftUpperArm", "LeftElbowRigAttachment", "la_elbow"),
          ("LeftHand", "LeftLowerArm", "LeftWristRigAttachment", "la_wrist"),
          ("RightUpperArm", "UpperTorso", "RightShoulderRigAttachment", "ra"),
          ("RightLowerArm", "RightUpperArm", "RightElbowRigAttachment", "ra_elbow"),
          ("RightHand", "RightLowerArm", "RightWristRigAttachment", "ra_wrist"),
          ("LeftUpperLeg", "LowerTorso", "LeftHipRigAttachment", "ll"),
          ("LeftLowerLeg", "LeftUpperLeg", "LeftKneeRigAttachment", "ll_knee"),
          ("LeftFoot", "LeftLowerLeg", "LeftAnkleRigAttachment", "ll_ankle"),
          ("RightUpperLeg", "LowerTorso", "RightHipRigAttachment", "rl"),
          ("RightLowerLeg", "RightUpperLeg", "RightKneeRigAttachment", "rl_knee"),
          ("RightFoot", "RightLowerLeg", "RightAnkleRigAttachment", "rl_ankle")]
PIVOT = {"LowerTorso": "torso", **{c: p for c, _, _, p in JOINTS}}
# Roblox (Y up, faces -Z) -> Blender (Z up, faces -Y): a proper rotation, so handedness and UVs survive
R2B = np.array([[-1, 0, 0], [0, 0, 1], [0, 1, 0]], float)


def cf(pos, rot=None):
    m = np.eye(4); m[:3, 3] = pos
    if rot is not None: m[:3, :3] = np.array(rot, float).reshape(3, 3)
    return m


def att_cf(inst):
    pos, rot = inst.props["CFrame"]
    return cf(pos, rot)


def cached(i, ext):
    p = W + f"cache_{i}.{ext}"
    if not os.path.exists(p):
        b = asset(i)
        if b[:9] == b'{"error":': raise RuntimeError(f"asset {i}: {b.decode()}")
        open(p, "wb").write(b)
    return p


def asset_id(s): return re.findall(r"(\d+)", s)[-1]


def mesh_world(mesh_id, world, size=None, scale=(1, 1, 1), offset=(0, 0, 0)):
    """Mesh verts placed in Roblox world space. size fits the mesh bbox to a MeshPart; scale/offset are SpecialMesh."""
    V, U, F = read_mesh(open(cached(mesh_id, "mesh"), "rb").read())
    V = np.array(V, float)
    if size is not None:
        lo, hi = V.min(0), V.max(0)
        V = (V - (lo + hi) / 2) * (np.array(size) / np.maximum(hi - lo, 1e-6))
    else:
        V = V * np.array(scale) + np.array(offset)
    V = V @ world[:3, :3].T + world[:3, 3]
    return V, U, F


# classic 585x559 shirt/pants template: (x, y, w, h) of each face, F/B/L/R = -Z/+Z/-X/+X, U/D = +Y/-Y (Roblox axes)
TEMPLATE = (585, 559)
RECTS = {"torso": {"F": (231, 74, 128, 128), "B": (427, 74, 128, 128), "R": (165, 74, 64, 128), "L": (361, 74, 64, 128),
                   "U": (231, 8, 128, 64), "D": (231, 204, 128, 64)},
         "right": {"L": (19, 355, 64, 128), "B": (85, 355, 64, 128), "R": (151, 355, 64, 128), "F": (217, 355, 64, 128),
                   "U": (217, 289, 64, 64), "D": (217, 485, 64, 64)},
         "left": {"F": (308, 355, 64, 128), "L": (374, 355, 64, 128), "B": (440, 355, 64, 128), "R": (506, 355, 64, 128),
                  "U": (308, 289, 64, 64), "D": (308, 485, 64, 64)}}
GROUPS = {"torso": ("UpperTorso", "LowerTorso"), "right_arm": ("RightUpperArm", "RightLowerArm", "RightHand"),
          "left_arm": ("LeftUpperArm", "LeftLowerArm", "LeftHand"), "right_leg": ("RightUpperLeg", "RightLowerLeg", "RightFoot"),
          "left_leg": ("LeftUpperLeg", "LeftLowerLeg", "LeftFoot")}


def template_uvs(V, F, lo, hi, rects, bottom=True):
    """Per-corner UVs that box-project the limb (bounds lo..hi, Roblox world axes) onto the template faces.
    Each face is laid out as seen from outside, so its strip edges meet the neighbouring faces like Roblox's."""
    sz = np.maximum(hi - lo, 1e-6); out = []
    for f in F:
        p = V[list(f)]; n = np.cross(p[1] - p[0], p[2] - p[0]); a = int(np.argmax(np.abs(n)))
        t = (p - lo) / sz  # 0..1 inside the box
        # caps only at the ends of the limb; upward faces mid-limb (thumbs, knuckles) take the nearest side instead
        if a == 1 and (0.12 < t[:, 1].mean() < 0.88 or (n[1] < 0 and not bottom)):
            a = 0 if abs(n[0]) / sz[0] * sz[2] > abs(n[2]) else 2
        side = {(0, 1): "R", (0, 0): "L", (1, 1): "U", (1, 0): "D", (2, 1): "B", (2, 0): "F"}[(a, int(n[a] > 0))]
        x, y, w, h = rects[side]
        su, sv = {"F": (1 - t[:, 0], 1 - t[:, 1]), "B": (t[:, 0], 1 - t[:, 1]), "R": (1 - t[:, 2], 1 - t[:, 1]),
                  "L": (t[:, 2], 1 - t[:, 1]), "U": (1 - t[:, 0], 1 - t[:, 2]), "D": (1 - t[:, 0], t[:, 2])}[side]
        px = x + 0.5 + np.clip(su, 0, 1) * (w - 1); py = y + 0.5 + np.clip(sv, 0, 1) * (h - 1)
        out.append([[float(u), float(v)] for u, v in zip(px / TEMPLATE[0], 1 - py / TEMPLATE[1])])
    return out


def composite(color, layers, name):
    """Body colour under the clothing templates (in order), like Roblox does for R15 parts with no TextureID."""
    out = None
    for f in layers:
        if not os.path.exists(W + f): continue
        im = Image.open(W + f).convert("RGBA")
        if out is None: out = Image.new("RGBA", im.size, color + (255,))
        out.alpha_composite(im.resize(out.size))
    if out is None: return None
    out.convert("RGB").save(W + name)
    return name


def main():
    av = json.load(open(W + "avatar.json"))
    bc = av.get("bodyColors", {})
    def col(k): return BRICK.get(bc.get(k + "ColorId"), BRICK[18])

    # R15 body parts, preferring the artist's intended proportions
    parts, atts = {}, {}
    for f in glob.glob(W + "*.rbxm"):
        data = open(f, "rb").read()
        if data[:8] != b"<roblox!": continue
        roots = read_rbxm(data)
        folder = next((r for r in roots if r.name == "R15ArtistIntent"), None) or \
                 next((r for r in roots if r.name == "R15Fixed"), None)
        if folder:
            for mp in folder.children:
                if mp.cls == "MeshPart": parts[mp.name] = mp
        for r in roots:
            if r.cls == "Accessory": atts.setdefault("acc", []).append(r)

    world = {"LowerTorso": np.eye(4)}
    def att(part, name):
        if part == "Head": return cf(HEAD_ATT[name])
        a = next(c for c in parts[part].children if c.cls == "Attachment" and c.name == name)
        return att_cf(a)
    joints = {"torso": (0, 0, 0)}
    for child, parent, name, piv in JOINTS:
        world[child] = world[parent] @ att(parent, name) @ np.linalg.inv(att(child, name))
        joints[piv] = tuple((world[parent] @ att(parent, name))[:3, 3])

    shirt, pants = "Shirt_template.png", "Pants_template.png"
    tex = {"torso": composite(col("torso"), [pants, shirt], "tex_torso.png"),
           "arm_l": composite(col("leftArm"), [shirt], "tex_arm_l.png"),
           "arm_r": composite(col("rightArm"), [shirt], "tex_arm_r.png"),
           "leg_l": composite(col("leftLeg"), [pants], "tex_leg_l.png"),
           "leg_r": composite(col("rightLeg"), [pants], "tex_leg_r.png")}
    def part_tex(n):
        if "Torso" in n: return tex["torso"], col("torso")
        side = "l" if n.startswith("Left") else "r"
        kind = "arm" if ("Arm" in n or "Hand" in n) else "leg"
        return tex[f"{kind}_{side}"], col(("left" if side == "l" else "right") + kind.capitalize())

    meshes = []
    for n, mp in parts.items():
        if n not in world: continue
        size = mp.props.get("size") or mp.props["InitialSize"]
        V, U, F = mesh_world(asset_id(mp.props["MeshId"]), world[n], size=size)
        t, c = part_tex(n)
        meshes.append({"name": n, "pivot": PIVOT[n], "V": V, "U": U, "F": F, "tex": t, "color": c})
    # the R15 meshes' own UVs follow Roblox's internal composite layout, so project the classic template instead
    for g, names in GROUPS.items():
        ms = [m for m in meshes if m["name"] in names]
        if not ms: continue
        allv = np.concatenate([m["V"] for m in ms]); lo, hi = allv.min(0), allv.max(0)
        rects = RECTS["torso" if g == "torso" else g.split("_")[0]]
        # sleeves' bottom cap would land on the palms, so arms skip it
        for m in ms: m["UL"] = template_uvs(m["V"], m["F"], lo, hi, rects, bottom="arm" not in g)

    head_cf = world["Head"]
    for acc in atts.get("acc", []):
        h = next(c for c in acc.children if c.name == "Handle")
        sm = next((c for c in h.children if c.cls == "SpecialMesh"), None)
        a = next((c for c in h.children if c.cls == "Attachment" and c.name in HEAD_ATT), None)
        if not sm or not a: print("skip accessory", acc.name); continue
        hw = head_cf @ cf(HEAD_ATT[a.name]) @ np.linalg.inv(att_cf(a))
        V, U, F = mesh_world(asset_id(sm.props["MeshId"]), hw, scale=sm.props.get("Scale", (1, 1, 1)),
                             offset=sm.props.get("Offset", (0, 0, 0)))
        t = None
        if sm.props.get("TextureId"):
            t = f"tex_{acc.name.replace(' ', '_')}.png"
            Image.open(cached(asset_id(sm.props["TextureId"]), "img")).convert("RGBA").save(W + t)
        meshes.append({"name": acc.name, "pivot": "head", "V": V, "U": U, "F": F, "tex": t, "color": (200, 200, 200)})

    # feet on the ground, then into Blender axes
    floor = min(m["V"][:, 1].min() for m in meshes)
    shift = np.array([0, -floor, 0])
    def b(p): return (R2B @ (np.asarray(p, float) + shift)).round(5).tolist()
    head_c = (head_cf[:3, 3])
    grips = {}
    for side in ("Left", "Right"):
        g = next((c for c in parts[side + "Hand"].children if c.cls == "Attachment" and c.name == side + "GripAttachment"), None)
        if g: grips[side[0].lower() + "a"] = b((world[side + "Hand"] @ att_cf(g))[:3, 3])
    rig = {"joints": {k: b(v) for k, v in joints.items()},
           "parents": {"torso": None, **{p: PIVOT[par] for _, par, _, p in JOINTS}},
           "head": {"center": b(head_c), "size": HEAD_SIZE},
           "grips": grips, "skin": col("head"),
           "meshes": [{**m, "V": [b(v) for v in m["V"]], "U": [list(map(float, u)) for u in m["U"]], "F": [list(map(int, f)) for f in m["F"]]}
                      for m in meshes]}
    json.dump(rig, open(W + "rig.json", "w"))
    top = max(max(v[2] for v in m["V"]) for m in rig["meshes"])
    print(f"rig.json: {len(rig['meshes'])} meshes, {sum(len(m['F']) for m in rig['meshes'])} tris, height {top:.2f} studs")


if __name__ == "__main__":
    main()
