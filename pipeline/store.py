"""Creator Store: search FREE models only and download them into work/models/.
Never buys anything: results with a price, scripts, or that are not marked free are dropped before anything else
happens, and only the read-only search + asset download endpoints are used.
Usage: python3 store.py search "park bench"      python3 store.py get <assetId>"""
import os, sys, json, urllib.request, urllib.parse
from fetch_avatar import KEY, asset

W = os.environ.get('SHORTS_WORK', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'work')) + '/models/'
os.makedirs(W, exist_ok=True)
CREDITS = W + "credits.json"


def is_free(a):
    q = a.get("creatorStoreProduct", {}).get("purchasePrice", {}).get("quantity", {})
    return q.get("significand", 1) == 0


def search(query, n=30):
    url = "https://apis.roblox.com/toolbox-service/v2/assets:search?" + urllib.parse.urlencode(
        {"searchCategoryType": "Model", "query": query, "maxPageSize": n})
    d = json.loads(urllib.request.urlopen(urllib.request.Request(url, headers={"x-api-key": KEY}), timeout=60).read())
    out = []
    for a in d.get("creatorStoreAssets", []):
        s = a["asset"]
        if not is_free(a) or s.get("hasScripts"): continue
        out.append({"id": s["id"], "name": s["name"], "creator": a["creator"]["name"],
                    "tris": s.get("objectMeshSummary", {}).get("triangles", 0),
                    "meshParts": s.get("instanceCounts", {}).get("meshPart", 0),
                    "votes": a.get("voting", {}).get("upVotePercent", 0), "_raw": a})
    return out


def get(asset_id, info=None):
    """Download a free model (cached) and record who made it for the video credits."""
    p = W + f"{asset_id}.rbxm"
    if not os.path.exists(p):
        b = asset(asset_id)
        if b[:7] != b"<roblox": raise RuntimeError(f"model {asset_id}: {b[:200]!r}")
        open(p, "wb").write(b)
    if info:
        c = json.load(open(CREDITS)) if os.path.exists(CREDITS) else {}
        c[str(asset_id)] = {"name": info["name"], "creator": info["creator"]}
        json.dump(c, open(CREDITS, "w"), indent=1)
    return p


if __name__ == "__main__":
    if sys.argv[1] == "search":
        for r in search(" ".join(sys.argv[2:])):
            print(f'{r["id"]:>16}  {r["tris"]:>7} tris  {r["meshParts"]:>3} mp  {r["votes"]:>3}%  {r["name"][:44]:44}  {r["creator"]}')
    elif sys.argv[1] == "get":
        print(get(int(sys.argv[2])))
