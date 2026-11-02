"""Download classic Roblox hair accessories (mesh + texture) and shirt/pants templates by asset id into work/cat/.
Usage: python3 fetch_items.py id [id ...]"""
import os, sys, io, re, json, gzip, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import rbx
W = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'work', 'cat') + '/'; os.makedirs(W, exist_ok=True)
def get(i):
    b = urllib.request.urlopen(f"https://assetdelivery.roblox.com/v1/asset/?id={i}", timeout=60).read()
    return gzip.decompress(b) if b[:2] == b'\x1f\x8b' else b
info = json.load(open(W + "index.json")) if os.path.exists(W + "index.json") else {}
for a in sys.argv[1:]:
    b = get(a); out = {}
    if b[:8] == b'<roblox!':
        for r in rbx.read_rbxm(b):
            for i in r.walk():
                if i.cls == 'Accessory' or i.cls == 'Hat': out['attach_point'] = i.props.get('AttachmentPoint')
                if i.cls == 'SpecialMesh':
                    out['mesh'] = re.findall(r'\d+', i.props['MeshId'])[-1]; out['tex'] = re.findall(r'\d+', i.props.get('TextureId', '') or '0')[-1]
                    out['scale'] = i.props.get('Scale'); out['offset'] = i.props.get('Offset')
                if i.cls == 'Attachment' and i.parent and i.parent.cls == 'Part': out['att_name'] = i.name; out['att_pos'] = i.props['CFrame'][0]
        if 'mesh' in out:
            open(W + f"{a}.mesh", "wb").write(get(out['mesh']))
            if out['tex'] != '0': open(W + f"{a}_tex.png", "wb").write(get(out['tex']))
    elif b'class="Accessory"' in b or b'class="Hat"' in b:  # XML accessory
        import xml.etree.ElementTree as ET
        root = ET.fromstring(b.decode('utf8', 'replace'))
        v3 = lambda e: tuple(float(e.find(k).text) for k in 'XYZ')
        for it in root.iter('Item'):
            pr = it.find('Properties'); cls = it.get('class')
            if cls == 'SpecialMesh':
                for c in pr:
                    n = c.get('name')
                    if n in ('MeshId', 'TextureId'):
                        u = c.find('url'); ids = re.findall(r'\d+', u.text if u is not None and u.text else '0')
                        out['mesh' if n == 'MeshId' else 'tex'] = ids[-1] if ids else '0'
                    if n in ('Scale', 'Offset'): out[n.lower()] = v3(c)
            if cls == 'Attachment':
                for c in pr:
                    if c.get('name') == 'CFrame': out['att_pos'] = v3(c)
                    if c.get('name') == 'Name': out['att_name'] = c.text
        open(W + f"{a}.mesh", "wb").write(get(out['mesh']))
        if out.get('tex', '0') != '0': open(W + f"{a}_tex.png", "wb").write(get(out['tex']))
    else:  # XML (classic clothing)
        tid = re.findall(rb"id=(\d+)", b)[-1].decode(); out['template'] = tid
        from PIL import Image
        Image.open(io.BytesIO(get(tid))).convert("RGBA").save(W + f"{a}_template.png")
    info[a] = out; print(a, out)
json.dump(info, open(W + "index.json", "w"), indent=1, default=str)
