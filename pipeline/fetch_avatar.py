"""Download a Roblox user's avatar pieces (body parts, accessories, clothing textures) into work/avatar/.
Usage: python3 fetch_avatar.py <userId>.  Uses ROBLOX_API_KEY if set (needed for newer UGC items)."""
import os, sys, json, gzip, io, re, urllib.request
W = os.environ.get('SHORTS_WORK', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'work')) + '/avatar/'
os.makedirs(W, exist_ok=True)
KEY = os.environ.get("ROBLOX_API_KEY")

def get(url):
    req = urllib.request.Request(url, headers={"x-api-key": KEY} if KEY else {})
    b = urllib.request.urlopen(req, timeout=60).read()
    return gzip.decompress(b) if b[:2] == b'\x1f\x8b' else b

def asset(i):
    # Open Cloud returns a temporary CDN link (needs legacy-asset:manage); the legacy route only serves older items.
    try:
        if KEY:
            loc = json.loads(get(f"https://apis.roblox.com/asset-delivery-api/v1/assetId/{i}"))["location"]
            b = urllib.request.urlopen(loc, timeout=60).read()
            return gzip.decompress(b) if b[:2] == b'\x1f\x8b' else b
        return get(f"https://assetdelivery.roblox.com/v1/asset/?id={i}")
    except Exception as e:
        return b'{"error":"%s"}' % str(e).encode()

if __name__ == "__main__":
    uid = sys.argv[1]
    av = json.loads(get(f"https://avatar.roblox.com/v1/users/{uid}/avatar"))
    json.dump(av, open(W + "avatar.json", "w"), indent=1)
    for a in av["assets"]:
        b = asset(a["id"]); kind = a["assetType"]["name"]
        open(W + f"{kind}_{a['id']}.rbxm", "wb").write(b)
        ok = b[:7] in (b'<roblox', b'<roblox!'[:7])
        print(("OK   " if ok else "FAIL ") + kind, a["name"])
        if kind in ("Shirt", "Pants") and ok:
            tid = re.findall(rb"id=(\d+)", b)[-1].decode()
            from PIL import Image
            Image.open(io.BytesIO(asset(tid))).save(W + f"{kind}_template.png")
