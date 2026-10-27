"""Minimal reader for Roblox binary model files (.rbxm) and mesh files (versions 1-5)."""
import struct, gzip, math


def lz4_block(src, out_len):
    dst = bytearray(); i = 0; n = len(src)
    while i < n:
        tok = src[i]; i += 1
        lit = tok >> 4
        if lit == 15:
            while True:
                b = src[i]; i += 1; lit += b
                if b != 255: break
        dst += src[i:i + lit]; i += lit
        if i >= n: break
        off = src[i] | (src[i + 1] << 8); i += 2
        ml = tok & 15
        if ml == 15:
            while True:
                b = src[i]; i += 1; ml += b
                if b != 255: break
        ml += 4
        st = len(dst) - off
        for k in range(ml): dst.append(dst[st + k])
    return bytes(dst)


def _deinterleave(b, count, width=4):
    return [int.from_bytes(bytes(b[j * count + k] for j in range(width)), 'big') for k in range(count)]


def _zz(v): return (v >> 1) ^ -(v & 1)


def _rfloat(v):
    v = ((v >> 1) | ((v & 1) << 31)) & 0xffffffff
    return struct.unpack('<f', struct.pack('<I', v))[0]


_NORM = [(1, 0, 0), (0, 1, 0), (0, 0, 1), (-1, 0, 0), (0, -1, 0), (0, 0, -1)]


def _special_rot(id_):
    o = id_ - 1; r = _NORM[o // 6]; u = _NORM[o % 6]
    b = (r[1] * u[2] - r[2] * u[1], r[2] * u[0] - r[0] * u[2], r[0] * u[1] - r[1] * u[0])
    # row-major R00..R22, columns are right, up, back
    return [r[0], u[0], b[0], r[1], u[1], b[1], r[2], u[2], b[2]]


class Inst:
    def __init__(s, cls, ref): s.cls = cls; s.ref = ref; s.props = {}; s.children = []; s.parent = None
    @property
    def name(s): return s.props.get('Name', '')
    def walk(s):
        yield s
        for c in s.children: yield from c.walk()
    def __repr__(s): return f"<{s.cls} {s.name}>"


def read_rbxm(data):
    if data[:2] == b'\x1f\x8b': data = gzip.decompress(data)
    assert data[:8] == b'<roblox!'
    p = 32; classes = {}; insts = {}
    while p < len(data):
        name = data[p:p + 4]; clen, ulen = struct.unpack('<II', data[p + 4:p + 12]); p += 16
        if clen == 0:
            body = data[p:p + ulen]; p += ulen
        else:
            raw = data[p:p + clen]; p += clen
            if raw[:4] == b'\x28\xb5\x2f\xfd':
                import zstandard; body = zstandard.ZstdDecompressor().decompress(raw, max_output_size=ulen)
            else:
                body = lz4_block(raw, ulen)
        if name == b'END\x00': break
        q = 0
        def u32():
            nonlocal q; v = struct.unpack('<I', body[q:q + 4])[0]; q += 4; return v
        def rstr():
            nonlocal q; L = u32(); s = body[q:q + L]; q += L; return s
        if name == b'INST':
            cid = u32(); cname = rstr().decode(); q += 1; cnt = u32()
            refs = _deinterleave(body[q:q + cnt * 4], cnt); acc = 0; lst = []
            for r in refs:
                acc += _zz(r); lst.append(acc); insts[acc] = Inst(cname, acc)
            classes[cid] = lst
        elif name == b'PROP':
            cid = u32(); pname = rstr().decode(); t = body[q]; q += 1
            refs = classes[cid]; n = len(refs); vals = None
            try:
                if t == 0x01:
                    vals = []
                    for _ in range(n):
                        s = rstr()
                        try: s = s.decode()
                        except UnicodeDecodeError: pass
                        vals.append(s)
                elif t == 0x02: vals = [bool(x) for x in body[q:q + n]]
                elif t == 0x03: vals = [_zz(v) for v in _deinterleave(body[q:q + 4 * n], n)]
                elif t == 0x04: vals = [_rfloat(v) for v in _deinterleave(body[q:q + 4 * n], n)]
                elif t == 0x0E:
                    xs = [_rfloat(v) for v in _deinterleave(body[q:q + 4 * n], n)]
                    ys = [_rfloat(v) for v in _deinterleave(body[q + 4 * n:q + 8 * n], n)]
                    zs = [_rfloat(v) for v in _deinterleave(body[q + 8 * n:q + 12 * n], n)]
                    vals = list(zip(xs, ys, zs))
                elif t == 0x0C:
                    rs = [_rfloat(v) for v in _deinterleave(body[q:q + 4 * n], n)]
                    gs = [_rfloat(v) for v in _deinterleave(body[q + 4 * n:q + 8 * n], n)]
                    bs = [_rfloat(v) for v in _deinterleave(body[q + 8 * n:q + 12 * n], n)]
                    vals = list(zip(rs, gs, bs))
                elif t == 0x10:
                    rots = []
                    for _ in range(n):
                        i_ = body[q]; q += 1
                        if i_ == 0:
                            rots.append(list(struct.unpack('<9f', body[q:q + 36]))); q += 36
                        else:
                            rots.append(_special_rot(i_))
                    xs = [_rfloat(v) for v in _deinterleave(body[q:q + 4 * n], n)]
                    ys = [_rfloat(v) for v in _deinterleave(body[q + 4 * n:q + 8 * n], n)]
                    zs = [_rfloat(v) for v in _deinterleave(body[q + 8 * n:q + 12 * n], n)]
                    vals = [(pos, r) for pos, r in zip(zip(xs, ys, zs), rots)]
                elif t == 0x12: vals = _deinterleave(body[q:q + 4 * n], n)
                elif t == 0x1A:
                    vals = list(zip(body[q:q + n], body[q + n:q + 2 * n], body[q + 2 * n:q + 3 * n]))
            except Exception:
                vals = None
            if vals is not None:
                for r, v in zip(refs, vals): insts[r].props[pname] = v
        elif name == b'PRNT':
            q += 1; cnt = u32()
            ch = _deinterleave(body[q:q + 4 * cnt], cnt); pa = _deinterleave(body[q + 4 * cnt:q + 8 * cnt], cnt)
            a = 0; b = 0
            for c, pr in zip(ch, pa):
                a += _zz(c); b += _zz(pr)
                if b != -1 and b in insts:
                    insts[a].parent = insts[b]; insts[b].children.append(insts[a])
    return [i for i in insts.values() if i.parent is None]


def read_mesh(data):
    """Returns (verts[(x,y,z)], uvs[(u,v)], faces[(a,b,c)]) using the highest LOD."""
    if data[:2] == b'\x1f\x8b': data = gzip.decompress(data)
    head, rest = data.split(b'\n', 1)
    ver = head.strip().decode()
    if ver == 'version 1.00' or ver == 'version 1.01':
        lines = rest.split(b'\n'); nf = int(lines[0]); body = lines[1].decode()
        nums = [float(x) for x in body.replace('][', ',').strip('[]\r ').split(',')]
        sc = 0.5 if ver == 'version 1.00' else 1.0
        V, U, F = [], [], []
        for k in range(nf * 3):
            b = nums[k * 9:k * 9 + 9]
            V.append((b[0] * sc, b[1] * sc, b[2] * sc)); U.append((b[6], 1 - b[7]))
        F = [(3 * i, 3 * i + 1, 3 * i + 2) for i in range(nf)]
        return V, U, F
    d = rest; p = 0
    major = int(ver.split()[1].split('.')[0])
    if major == 2:
        hs, vs, fs, nv, nfc = struct.unpack('<HBBII', d[:12]); p = hs; lods = None
    elif major == 3:
        hs, vs, fs, ls, nl, nv, nfc = struct.unpack('<HBBHHII', d[:16]); p = hs; lods = (nl, ls)
    elif major in (4, 5):
        hs, lodtype, nv, nfc, nl, nb, bns, nsub, nhq, _ = struct.unpack('<HHIIHHIHBB', d[:24]); p = hs; vs = 40; fs = 12; lods = (nl, 4)
    else:
        raise ValueError('unsupported mesh ' + ver)
    V, U = [], []
    for i in range(nv):
        x, y, z, nx, ny, nz, u, v = struct.unpack('<8f', d[p:p + 32]); p += vs
        V.append((x, y, z)); U.append((u, 1 - v))
    if major in (4, 5) and nb > 0: p += 8 * nv
    F = [struct.unpack('<3I', d[p + 12 * i:p + 12 * i + 12]) for i in range(nfc)]; p += 12 * nfc
    if lods and lods[0] >= 2:
        offs = struct.unpack(f'<{lods[0]}I', d[p:p + 4 * lods[0]])
        F = F[offs[0]:offs[1]]
    return V, U, F
