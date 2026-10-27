"""Convert a downloaded Roblox model (work/models/<id>.rbxm, from store.py) into work/models/<id>.json for models.py.
Handles Parts (block/ball/cylinder/wedge), SpecialMesh/BlockMesh/CylinderMesh, MeshParts (+SurfaceAppearance colour
maps) and Decals. Unions (CSG) are skipped and reported. Output is in Blender axes (Z up), studs, model centred on
the origin with its lowest point at z=0.
Usage: python3 rbx_model.py <assetId> [...]"""
import os, sys, json, re, io
import numpy as np
from PIL import Image
from rbx import read_model, read_mesh
from fetch_avatar import asset

W = os.environ.get('SHORTS_WORK', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'work')) + '/models/'
R2B = np.array([[-1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1]], float)
BRICK = {1: (242, 243, 243), 2: (161, 165, 162), 3: (249, 233, 153), 5: (215, 197, 154), 6: (194, 218, 184),
         9: (232, 186, 200), 11: (128, 187, 219), 12: (203, 132, 66), 18: (204, 142, 105), 21: (196, 40, 28),
         23: (13, 105, 172), 24: (245, 205, 48), 25: (98, 71, 50), 26: (27, 42, 53), 27: (109, 110, 108),
         28: (40, 127, 71), 29: (161, 196, 140), 37: (75, 151, 75), 38: (160, 95, 53), 45: (180, 210, 228),
         101: (218, 134, 122), 102: (110, 153, 202), 104: (107, 50, 124), 105: (226, 155, 64), 106: (218, 133, 65),
         107: (0, 143, 156), 119: (164, 189, 71), 125: (234, 184, 146), 135: (116, 134, 157), 141: (39, 70, 45),
         151: (120, 144, 130), 153: (149, 121, 119), 192: (105, 64, 40), 194: (163, 162, 165), 199: (99, 95, 98),
         208: (229, 228, 223), 217: (124, 92, 70), 226: (253, 234, 141), 1001: (248, 248, 248), 1002: (205, 205, 205),
         1003: (17, 17, 17), 1004: (255, 0, 0), 1005: (255, 176, 0), 1009: (255, 255, 0), 1010: (0, 0, 255),
         1011: (0, 32, 96), 1012: (33, 84, 185), 1019: (0, 255, 255), 1020: (0, 255, 0), 1021: (58, 125, 21),
         1024: (175, 221, 255), 1025: (255, 201, 201), 1028: (204, 255, 204), 1030: (255, 204, 153),
         1031: (98, 37, 209), 1032: (255, 0, 191)}
MAT = {288: "neon", 1568: "glass", 1536: "ice", 1040: "metal", 1056: "metal", 1072: "metal", 1088: "metal",
       512: "wood", 528: "wood", 1280: "grass", 1296: "sand", 1312: "fabric"}
FACE = {0: (0, 1), 1: (1, 1), 2: (2, 1), 3: (0, -1), 4: (1, -1), 5: (2, -1)}  # Decal Face enum -> (axis, sign)
PARTS = {"Part", "Seat", "SpawnLocation", "WedgePart", "CornerWedgePart", "TrussPart", "VehicleSeat", "MeshPart"}


def cf(p):
    pos, rot = p; m = np.eye(4); m[:3, :3] = np.array(rot, float).reshape(3, 3); m[:3, 3] = pos; return m


def aid(s):
    r = re.findall(r"(\d{3,})", s or ""); return r[-1] if r else None


def fetch(i, ext):
    os.makedirs(W + "cache", exist_ok=True)
    p = W + f"cache/{i}.{ext}"
    if not os.path.exists(p):
        b = asset(i)
        if b[:9] == b'{"error":': raise RuntimeError(f"asset {i}: {b[:120]!r}")
        if b[:7] == b"<roblox" and ext == "png":  # a Decal asset: follow it to its image
            inner = next((x for r in read_model(b) for x in r.walk() if x.props.get("Texture")), None)
            if not inner or not aid(inner.props["Texture"]): raise RuntimeError(f"decal {i} has no texture")
            return fetch(aid(inner.props["Texture"]), ext)
        if ext == "png": Image.open(io.BytesIO(b)).convert("RGBA").save(p)
        else: open(p, "wb").write(b)
    return p


def mesh_file(i):
    """Mesh in its own space, saved once as JSON (V, U, F) and shared by every model that uses it."""
    p = W + f"cache/{i}.mesh.json"
    if not os.path.exists(p):
        V, U, F = read_mesh(open(fetch(i, "mesh"), "rb").read())
        json.dump({"V": [list(map(float, v)) for v in V], "U": [list(map(float, u)) for u in U],
                   "F": [list(map(int, f)) for f in F]}, open(p, "w"))
    return p


def color(x):
    c = x.props.get("Color3uint8") or x.props.get("Color")
    if c and isinstance(c[0], float) and max(c) <= 1: c = tuple(int(v * 255) for v in c)
    return tuple(c) if c else BRICK.get(x.props.get("BrickColor"), (163, 162, 165))


def convert(asset_id):
    roots = read_model(open(W + f"{asset_id}.rbxm", "rb").read())
    items, skipped = [], {}
    for r in roots:
        for x in r.walk():
            if x.cls == "UnionOperation" or x.cls == "NegateOperation":
                skipped[x.cls] = skipped.get(x.cls, 0) + 1; continue
            if x.cls not in PARTS or "CFrame" not in x.props: continue
            alpha = 1 - float(x.props.get("Transparency", 0))
            if alpha < 0.05: continue
            size = np.array(x.props.get("size") or x.props.get("Size") or (1, 1, 1), float)
            M = cf(x.props["CFrame"]); base = {"color": color(x), "alpha": alpha,
                                               "mat": MAT.get(x.props.get("Material"), "plastic")}
            shape = {"WedgePart": "wedge", "CornerWedgePart": "wedge", "TrussPart": "box"}.get(x.cls) or \
                    {0: "ball", 1: "box", 2: "cyl", 3: "wedge"}.get(x.props.get("shape", x.props.get("Shape", 1)), "box")
            sm = next((c for c in x.children if c.cls in ("SpecialMesh", "BlockMesh", "CylinderMesh", "FileMesh")), None)
            try:
                if x.cls == "MeshPart" and aid(x.props.get("MeshId", "")):
                    sa = next((c for c in x.children if c.cls == "SurfaceAppearance"), None)
                    tex = aid(sa.props.get("ColorMap", "")) if sa else aid(x.props.get("TextureID", ""))
                    init = np.array(x.props.get("InitialSize") or size, float)
                    items.append({**base, "kind": "mesh", "mesh": mesh_file(aid(x.props["MeshId"])),
                                  "fit": size.tolist(), "init": init.tolist(), "M": M,
                                  "tex": fetch(tex, "png") if tex else None})
                elif sm is not None:
                    sc = np.array(sm.props.get("Scale", (1, 1, 1)), float); off = np.array(sm.props.get("Offset", (0, 0, 0)), float)
                    Mo = M.copy(); Mo[:3, 3] += M[:3, :3] @ off
                    mt = {"BlockMesh": 6, "CylinderMesh": 4}.get(sm.cls, sm.props.get("MeshType", 5 if aid(sm.props.get("MeshId", "")) else 6))
                    if mt == 5 and aid(sm.props.get("MeshId", "")):
                        tex = aid(sm.props.get("TextureId", ""))
                        items.append({**base, "kind": "mesh", "mesh": mesh_file(aid(sm.props["MeshId"])), "scale": sc.tolist(),
                                      "M": Mo, "tex": fetch(tex, "png") if tex else None})
                    else:
                        k = {3: "ball", 4: "cylY", 0: "cylY", 2: "wedge"}.get(mt, "box")
                        items.append({**base, "kind": k, "size": (size * sc).tolist(), "M": Mo})
                else:
                    items.append({**base, "kind": shape, "size": size.tolist(), "M": M})
            except Exception as e:
                skipped[f"{x.cls}: {e}"[:80]] = skipped.get(f"{x.cls}: {e}"[:80], 0) + 1
                continue
            for d in x.children:
                if d.cls == "Decal" and aid(d.props.get("Texture", "")) and float(d.props.get("Transparency", 0)) < 0.95:
                    try:
                        items.append({"kind": "decal", "face": FACE.get(d.props.get("Face", 5), (2, -1)),
                                      "size": size.tolist(), "M": M, "tex": fetch(aid(d.props["Texture"]), "png"),
                                      "color": (255, 255, 255), "alpha": 1.0, "mat": "plastic"})
                    except Exception as e:
                        skipped[f"Decal: {e}"[:80]] = 1
    if not items: raise RuntimeError(f"{asset_id}: nothing renderable ({skipped})")
    # Blender axes, centred on x/y, resting on z=0
    pts = []
    for it in items:
        it["M"] = R2B @ it["M"]; pts.append(it["M"][:3, 3])
    lo = np.min(pts, 0); hi = np.max(pts, 0)
    lift = np.array([-(lo[0] + hi[0]) / 2, -(lo[1] + hi[1]) / 2, 0])
    for it in items: it["M"][:3, 3] += lift
    zmin = min(it["M"][2, 3] - (abs(it["M"][2, :3]) @ np.array(it.get("size") or it.get("fit") or [0, 0, 0])) / 2 for it in items)
    for it in items: it["M"][2, 3] -= zmin; it["M"] = it["M"].round(5).tolist()
    out = W + f"{asset_id}.json"
    json.dump({"id": asset_id, "items": items, "skipped": skipped}, open(out, "w"))
    return out, len(items), skipped


if __name__ == "__main__":
    for a in sys.argv[1:]:
        try: print(a, *convert(a))
        except Exception as e: print(a, "FAILED", e)
