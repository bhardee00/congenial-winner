"""Original sound effects and music, synthesised with numpy (no samples, so nothing to license), and the final mix.
make_short.py calls make_sfx() and make_music(); build_short.py (inside Blender) calls mix() with the cues the story
placed, producing one packed track: narration + effects + music that fades to a music box while the world is paused."""
import math, os, wave
import numpy as np

SR = 48000
rng = np.random.default_rng(7)


# ---------------- wav io (stdlib, so it also runs inside Blender) ----------------
def write(path, x):
    x = np.clip(x, -1, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x * 32767).astype("<i2").tobytes())


def read(path):
    with wave.open(path, "rb") as w:
        n, ch, sw, sr = w.getnframes(), w.getnchannels(), w.getsampwidth(), w.getframerate()
        a = np.frombuffer(w.readframes(n), dtype="<i2" if sw == 2 else "<i4").astype(np.float32) / (32767 if sw == 2 else 2 ** 31)
    if ch > 1: a = a.reshape(-1, ch).mean(1)
    if sr != SR: a = np.interp(np.arange(int(len(a) * SR / sr)) * sr / SR, np.arange(len(a)), a)
    return a


# ---------------- building blocks ----------------
def t_(d): return np.arange(int(d * SR)) / SR


def env(d, a=0.005, r=None, shape=1.0):
    t = t_(d); r = d - a if r is None else r
    e = np.minimum(1, t / max(a, 1e-4)) * np.clip((d - t) / max(r, 1e-4), 0, 1) ** shape
    return e


def tone(freq, d, kind="sine", phase=0.0):
    """freq can be a number or an array (sweeps)."""
    f = np.full(int(d * SR), float(freq)) if np.isscalar(freq) else freq
    ph = 2 * np.pi * np.cumsum(f) / SR + phase
    if kind == "sine": return np.sin(ph)
    if kind == "tri": return 2 / np.pi * np.arcsin(np.sin(ph))
    if kind == "square": return np.sign(np.sin(ph)) * 0.6
    if kind == "saw": return 2 * ((ph / (2 * np.pi)) % 1) - 1
    raise ValueError(kind)


def _fftconv(x, w):
    m = len(x) + len(w) - 1; nfft = 1 << (m - 1).bit_length()
    return np.fft.irfft(np.fft.rfft(x, nfft) * np.fft.rfft(w, nfft), nfft)[:len(x)]


def lp(x, cutoff, passes=2):
    """Smoothing lowpass (exponential kernel, FFT convolution so long tracks stay fast)."""
    k = max(1, int(SR / (2 * math.pi * cutoff)))
    w = np.exp(-np.arange(6 * k) / k); w /= w.sum()
    for _ in range(passes): x = _fftconv(x, w) if len(w) > 64 else np.convolve(x, w)[:len(x)]
    return x


def hp(x, cutoff): return x - lp(x, cutoff, 1)


def noise(d): return rng.uniform(-1, 1, int(d * SR))


def place(buf, x, at, gain=1.0):
    i = int(at * SR)
    if i >= len(buf): return
    x = x[:len(buf) - i]; buf[i:i + len(x)] += x * gain


def sweep(f0, f1, d, curve=1.0):
    u = np.linspace(0, 1, int(d * SR)) ** curve
    return f0 * (f1 / f0) ** u


def note(n): return 440 * 2 ** ((n - 69) / 12)  # MIDI note -> Hz


# ---------------- sound effects ----------------
def sfx_click():
    a = np.zeros(int(0.02 * SR)); place(a, tone(2400, 0.02) * env(0.02, 0.001, shape=3) * 0.6, 0)
    place(a, hp(noise(0.004), 2000) * env(0.004, 0.0005), 0)
    out = np.zeros(int(0.12 * SR)); place(out, a, 0); place(out, a * 0.55, 0.055)
    return out * 0.9


def sfx_pause():  # power-down "vwoooom" as the world stops
    d = 0.9; f = sweep(520, 38, d, 0.6)
    x = (tone(f, d, "saw") * 0.5 + tone(f * 1.5, d, "tri") * 0.3) * env(d, 0.01, shape=1.5)
    return lp(x, 1800) * 0.9 + lp(noise(d), 600) * env(d, 0.05) * 0.25


def sfx_play():  # power-up
    d = 0.6; f = sweep(60, 620, d, 1.6)
    x = (tone(f, d, "saw") * 0.45 + tone(f * 2, d, "sine") * 0.3) * env(d, 0.3, 0.12)
    return lp(x, 2500)


def sfx_whoosh(d=0.5):
    x = noise(d); e = np.sin(np.linspace(0, np.pi, len(x))) ** 2
    return (lp(x, 900) * 0.7 + hp(lp(x, 3000), 600) * 0.3) * e * 1.4


def sfx_pop():
    d = 0.09; return tone(sweep(900, 260, d), d) * env(d, 0.002, shape=2) * 0.9


def sfx_scared():  # "dun dun!" stabs
    out = np.zeros(int(1.0 * SR))
    for at, g in ((0, 0.8), (0.28, 1.0)):
        d = 0.45; ch = sum(tone(note(n), d, "saw") for n in (36, 48, 51, 55)) / 4
        place(out, lp(ch, 1200) * env(d, 0.005, shape=2.5), at, g)
    return out


def sfx_sad():  # sad trombone: wah wah wah waaah
    out = np.zeros(int(2.3 * SR)); notes = [(58, 0.32), (57, 0.32), (56, 0.32), (55, 1.1)]; at = 0
    for i, (n, d) in enumerate(notes):
        f = np.full(int(d * SR), note(n))
        if i == 3: f = f * (1 + 0.012 * np.sin(2 * np.pi * 5.5 * t_(d)))
        x = lp(tone(f, d, "saw") * 0.6 + tone(f, d, "square") * 0.3, 900) * env(d, 0.03, 0.12)
        place(out, x, at); at += d + 0.03
    return out * 0.9


def sfx_cry():  # cartoon sobbing "waaah-uh-uh"
    out = np.zeros(int(1.8 * SR))
    for at, d, f0 in ((0, 0.75, 620), (0.85, 0.25, 520), (1.15, 0.25, 500), (1.45, 0.3, 470)):
        t = t_(d); f = f0 * (1 + 0.04 * np.sin(2 * np.pi * 7 * t)) * np.linspace(1.05, 0.92, len(t))
        x = tone(f, d, "saw") * 0.5 + tone(f * 2, d, "sine") * 0.3
        x = lp(x, 1500) * (0.6 + 0.4 * np.sin(2 * np.pi * 9 * t) ** 2) * env(d, 0.03, 0.1)
        place(out, x, at)
    return out * 0.8


def sfx_angry():  # rising steam whistle over a rumble
    d = 1.0; t = t_(d)
    rum = lp(noise(d), 120) * 3 * env(d, 0.05)
    steam = hp(noise(d), 3000) * np.linspace(0.1, 0.8, len(t)) * env(d, 0.3, 0.1)
    whistle = tone(sweep(900, 2200, d), d) * np.linspace(0, 0.35, len(t)) * env(d, 0.4, 0.08)
    return rum + steam * 0.6 + whistle


def sfx_ding():
    d = 1.1; return (tone(1318, d) + 0.5 * tone(2637, d) + 0.25 * tone(3951, d)) * env(d, 0.002, shape=3) * 0.45


def sfx_sparkle():
    out = np.zeros(int(1.0 * SR))
    for i, n in enumerate((84, 88, 91, 96, 100)):
        d = 0.5; place(out, (tone(note(n), d) + 0.3 * tone(note(n) * 2, d)) * env(d, 0.002, shape=3) * 0.35, i * 0.06)
    return out


def sfx_nom():
    out = np.zeros(int(0.8 * SR))
    for i in range(3):
        d = 0.14; x = lp(noise(d), 700) * env(d, 0.005, shape=2) * 1.6 + tone(sweep(220, 120, d), d) * env(d, 0.005, shape=2) * 0.6
        place(out, x, i * 0.22)
    return out


def sfx_buzz():  # dead batteries: bzzt bzzt
    out = np.zeros(int(0.7 * SR))
    for at in (0, 0.3):
        d = 0.2; place(out, lp(tone(110, d, "square") + 0.5 * tone(165, d, "square"), 2000) * env(d, 0.005, 0.03) * 0.6, at)
    return out


def sfx_coo():  # pigeon: coo-COO-coo
    out = np.zeros(int(1.1 * SR))
    for at, d, f0, g in ((0, 0.22, 330, 0.6), (0.26, 0.38, 360, 1.0), (0.7, 0.3, 300, 0.6)):
        t = t_(d); f = f0 * (1 + 0.06 * np.sin(2 * np.pi * 14 * t)) * np.linspace(1.08, 0.9, len(t))
        place(out, lp(tone(f, d, "tri") + 0.2 * tone(f * 2, d), 900) * np.sin(np.linspace(0, np.pi, len(t))) * g, at)
    return out * 0.8


def sfx_sigh():
    d = 1.1; t = t_(d)
    return lp(noise(d), sweep(1800, 400, d).mean()) * np.sin(np.linspace(0, np.pi, len(t))) ** 1.5 * 1.6


def sfx_boing():
    d = 0.4; t = t_(d); f = 180 * (1 + 0.5 * np.exp(-t * 8) * np.sin(2 * np.pi * 14 * t)) * np.linspace(1, 1.6, len(t))
    return tone(f, d, "tri") * env(d, 0.005, shape=1.5) * 0.6


def sfx_step():
    d = 0.06; return lp(noise(d), 500) * env(d, 0.002, shape=3) * 1.4


def sfx_flap():
    out = np.zeros(int(0.9 * SR))
    for i in range(6):
        d = 0.08; place(out, lp(noise(d), 1500) * env(d, 0.01, shape=2) * 1.2, i * 0.13)
    return out


def sfx_tick():
    out = np.zeros(int(1.6 * SR))
    for i in range(8):
        d = 0.02; place(out, hp(noise(d), 2500) * env(d, 0.001, shape=3) * (0.9 if i % 2 else 0.6), i * 0.2)
    return out


def sfx_swoosh_card(): return sfx_whoosh(0.4) * 0.8


def sfx_honk():  # goose
    out = np.zeros(int(0.7 * SR))
    for at, d in ((0, 0.22), (0.28, 0.3)):
        t = t_(d); f = 420 * (1 + 0.05 * np.sin(2 * np.pi * 30 * t))
        x = lp(tone(f, d, "square") + 0.6 * tone(f * 2.01, d, "saw"), 2200) * env(d, 0.01, 0.06)
        place(out, x, at)
    return out * 0.7


def sfx_tweet():
    out = np.zeros(int(0.5 * SR))
    for i in range(3):
        d = 0.08; place(out, tone(sweep(2600, 4200, d), d) * env(d, 0.005, shape=2) * 0.4, i * 0.12)
    return out


def sfx_giggle():  # cartoon kid laugh: hee-hee-hee-hee
    out = np.zeros(int(1.4 * SR))
    for i in range(6):
        d = 0.12; t = t_(d); f = (820 - i * 25) * (1 + 0.08 * np.sin(2 * np.pi * 18 * t))
        x = lp(tone(f, d, "saw") * 0.5 + tone(f * 2, d) * 0.3 + hp(noise(d), 3000) * 0.15, 3200) * np.sin(np.linspace(0, np.pi, len(t)))
        place(out, x, i * 0.17)
    return out * 0.9


def sfx_tuba():  # bwomp
    d = 0.9; t = t_(d); f = 62 * (1 + 0.02 * np.sin(2 * np.pi * 5 * t)) * np.linspace(1.08, 0.94, len(t))
    return lp(tone(f, d, "saw") + 0.5 * tone(f * 2, d, "square"), 700) * env(d, 0.04, 0.3) * 0.9


def sfx_drums():  # parade drum roll into a hit
    out = np.zeros(int(1.6 * SR))
    for i in range(18):
        d = 0.05; place(out, hp(noise(d), 900) * env(d, 0.001, shape=3) * (0.25 + i * 0.02), i * 0.06)
    kd = 0.4; place(out, (tone(sweep(120, 45, kd), kd) * 0.9 + hp(noise(kd), 800) * 0.4) * env(kd, 0.002, shape=2), 1.1)
    return out


def sfx_splat():
    d = 0.3; return (lp(noise(d), 900) * 1.6 + tone(sweep(300, 80, d), d) * 0.5) * env(d, 0.003, shape=2.5)


def sfx_coin():
    out = np.zeros(int(0.6 * SR))
    for at, f in ((0, 1975), (0.08, 2637)):
        d = 0.4; place(out, (tone(f, d, "square") * 0.25 + tone(f, d) * 0.3) * env(d, 0.002, shape=3), at)
    return out


def sfx_bell():  # big tower bell
    d = 2.5; t = t_(d)
    x = sum(a * tone(f, d) * np.exp(-t * k) for f, a, k in ((196, 1.0, 1.2), (392, 0.5, 1.6), (466, 0.3, 2.2), (588, 0.25, 2.5), (784, 0.15, 3)))
    return x * 0.45


def sfx_live():  # news sting
    out = np.zeros(int(1.0 * SR))
    for i, n in enumerate((67, 72, 76, 79)):
        d = 0.5 - i * 0.05; place(out, lp(tone(note(n), d, "saw") + tone(note(n - 12), d, "square") * 0.5, 2500) * env(d, 0.005, shape=2) * 0.35, i * 0.09)
    return out


def sfx_wind():
    d = 2.0; x = noise(d); e = np.sin(np.linspace(0, np.pi, len(x)))
    return lp(x, 500) * e * 1.4 + hp(lp(x, 2500), 900) * e * 0.25


def sfx_handshake():  # rubbery pumping
    out = np.zeros(int(1.0 * SR))
    for i in range(5):
        d = 0.1; place(out, lp(noise(d), 1200) * env(d, 0.005, shape=2) * 0.8 + tone(sweep(260, 200, d), d) * env(d, 0.005, shape=2) * 0.2, i * 0.18)
    return out


SFX = {k[4:]: v for k, v in globals().items() if k.startswith("sfx_")}


def make_sfx(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    for name, fn in SFX.items(): write(os.path.join(out_dir, name + ".wav"), fn())


# ---------------- music ----------------
PROG = [(60, [60, 64, 67]), (55, [55, 59, 62]), (57, [57, 60, 64]), (53, [53, 57, 60])]  # C G Am F


def make_music(path_normal, path_paused, seconds, bpm=118):
    """Two full-length stems the mix crossfades between: an upbeat band, and a music box for the paused world."""
    n = int(seconds * SR); beat = 60 / bpm; bar = beat * 4
    band = np.zeros(n); box = np.zeros(n)
    for b in range(int(seconds / bar) + 1):
        t0 = b * bar; root, chord = PROG[b % 4]
        for k in range(8):  # bass: eighth notes, root and fifth
            nn = root - 24 + (7 if k % 4 == 3 else 0); d = beat / 2 * 0.9
            place(band, lp(tone(note(nn), d, "tri"), 600) * env(d, 0.005, shape=1.5) * 0.55, t0 + k * beat / 2)
        for k in range(16):  # plucky arpeggio
            nn = chord[k % 3] + (12 if k % 8 >= 4 else 0); d = beat / 4 * 0.95
            place(band, lp(tone(note(nn), d, "square"), 2600) * env(d, 0.003, shape=2.5) * 0.16, t0 + k * beat / 4)
        for k in range(4):  # drums
            kd = 0.18; place(band, tone(sweep(150, 45, kd), kd) * env(kd, 0.002, shape=2) * 0.8, t0 + k * beat)
            if k % 2: sd = 0.12; place(band, hp(noise(sd), 1500) * env(sd, 0.002, shape=2.5) * 0.35, t0 + k * beat)
            for h in (0, 0.5): hd = 0.04; place(band, hp(noise(hd), 6000) * env(hd, 0.001, shape=3) * 0.18, t0 + (k + h) * beat)
        if b % 2 == 0:  # lead melody every other bar
            mel = [chord[2] + 12, chord[1] + 12, chord[2] + 12, chord[0] + 24]
            for k, nn in enumerate(mel):
                d = beat * 0.9; vib = 1 + 0.008 * np.sin(2 * np.pi * 5 * t_(d))
                place(band, lp(tone(note(nn) * vib, d, "tri"), 3000) * env(d, 0.01, 0.2) * 0.18, t0 + k * beat)
        for k in range(8):  # music box: slow, high, sparse
            nn = chord[(k * 2) % 3] + 24 + (12 if k == 7 else 0); d = 1.4
            place(box, (tone(note(nn), d) + 0.4 * tone(note(nn) * 3, d)) * env(d, 0.002, shape=3) * 0.22, t0 + k * beat / 2)
        d = bar; pad = sum(tone(note(c + 12), d, "tri") for c in chord) / 3
        place(box, lp(pad, 900) * env(d, 0.4, 0.5) * 0.12, t0)
    write(path_normal, band / max(1e-6, np.abs(band).max()) * 0.9)
    write(path_paused, box / max(1e-6, np.abs(box).max()) * 0.9)


# ---------------- mix ----------------
def _loop(x, n, xf=2.0):
    """Repeat a track to n samples, crossfading each repeat over xf seconds so the seam isn't heard."""
    if len(x) >= n: return x[:n]
    k = int(xf * SR); out = x.copy(); r = np.linspace(0, 1, k)
    while len(out) < n:
        out[-k:] = out[-k:] * (1 - r) + x[:k] * r; out = np.concatenate([out, x[k:]])
    return out[:n]


def mix(out_path, voice_path, sfx_dir, cues, seconds, music=None, voice_extra=()):
    """cues: [(seconds, sfx name or path, gain)]. music: (normal.wav, paused.wav, [(seconds, "paused"|"normal")])."""
    n = int(seconds * SR); out = np.zeros(n)
    v = read(voice_path); out[:min(n, len(v))] += v[:n]
    vo = np.zeros(n); vo[:min(n, len(v))] = np.abs(v[:n])
    for at, name, g in cues:
        p = name if name.endswith(".wav") else os.path.join(sfx_dir, name + ".wav")
        place(out, read(p), at, 0.55 * g)
    if music:
        normal, paused, switches = music
        a, b = read(normal), read(paused)
        a, b = _loop(a, n), _loop(b, n)
        mode = np.zeros(n)  # 0 = band, 1 = music box
        for at, m in switches: mode[int(at * SR):] = 1.0 if m == "paused" else 0.0
        mode = lp(mode, 3, 1)  # quick crossfades
        duck = 1 - 0.45 * np.clip(lp(vo, 4, 1) * 6, 0, 1)  # lower the music while someone talks
        fade = np.minimum(1, (n - np.arange(n)) / (1.5 * SR))
        out += (a * (1 - mode) * 0.16 + b * mode * 0.2) * duck * fade
    peak = np.abs(out).max()
    out = np.tanh(out / max(peak, 1e-6) * 1.15) * 0.92  # gentle limiter
    write(out_path, out)
