"""Use recorded voice files (e.g. ElevenLabs Adam exported at 1.33x / 1.68x) instead of generated narration.
Finds every script line in the recordings, then builds work/voice.wav and work/lines_timed.json (with word times)
in script order, so captions, cuts and effects sync to the real performance.
    python3 voice_import.py stories/<story>.json
story["voice_files"] = {"narrator": wav, "others": wav, "others_order": [speaker per line, in recorded order]}
Sentences are found by matching the recording's sound against a local TTS reading of the same script (dynamic
time warping on mel spectra), then snapped to the real pauses; word times inside a sentence follow its voiced parts.
Short recordings with one piece per line (the other voices) are simply fitted to the pauses."""
import os, re, sys, json, subprocess
import numpy as np, soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(HERE)
W = os.environ.get('SHORTS_WORK', os.path.join(REPO, 'work')) + '/'
SR = 48000


def load(path):
    a, sr = sf.read(path, always_2d=False)
    if a.ndim > 1: a = a.mean(1)
    if sr != SR: a = np.interp(np.arange(int(len(a) * SR / sr)) * sr / SR, np.arange(len(a)), a)
    return a.astype(np.float32)


def segments(a, thr_db=-38, min_gap=0.12, min_len=0.1):
    """Voiced regions [start, end] in seconds."""
    hop = int(0.01 * SR); fr = hop * 2; peak = abs(a).max() + 1e-9
    r = np.array([np.sqrt((a[i:i + fr] ** 2).mean()) / peak for i in range(0, len(a) - fr, hop)])
    on = 20 * np.log10(r + 1e-9) > thr_db
    out, i, n = [], 0, len(on)
    while i < n:
        if on[i]:
            j = i
            while j < n and on[j]: j += 1
            out.append([i * hop / SR, j * hop / SR]); i = j
        else: i += 1
    merged = []
    for s, e in out:
        if merged and s - merged[-1][1] < min_gap: merged[-1][1] = e
        else: merged.append([s, e])
    return [m for m in merged if m[1] - m[0] >= min_len]


def expected_lengths(texts):
    """Relative spoken length of each line from a quick local TTS read (same words, any voice)."""
    from kokoro_onnx import Kokoro
    k = Kokoro(W + "tts/kokoro.onnx", W + "tts/voices.bin")
    out = []
    for t in texts:
        s, sr = k.create(t, voice="am_adam", speed=1.0, lang="en-us")
        out.append(len(s) / sr)
    return np.array(out)


def split_sentences(text):
    return [x.strip() for x in re.findall(r"[^.?!]+[.?!\"]*", text) if x.strip()]


def mel(a, sr, n_mels=32):
    """Normalised log-mel frames (20 ms hop) at 16 kHz."""
    a = np.interp(np.arange(int(len(a) * 16000 / sr)) * sr / 16000, np.arange(len(a)), a)
    n, hop = 400, 320; frames = np.lib.stride_tricks.sliding_window_view(a, n)[::hop] * np.hanning(n)
    spec = np.abs(np.fft.rfft(frames, 512)) ** 2
    hz = np.linspace(0, 8000, spec.shape[1]); m = 2595 * np.log10(1 + hz / 700)
    edges = np.linspace(m[1], 2595 * np.log10(1 + 7000 / 700), n_mels + 2); fb = np.zeros((n_mels, len(hz)))
    for k in range(n_mels):
        lo, c, hi = edges[k], edges[k + 1], edges[k + 2]
        fb[k] = np.clip(np.minimum((m - lo) / (c - lo), (hi - m) / (hi - c)), 0, None)
    f = np.log(spec @ fb.T + 1e-6); f = (f - f.mean(0)) / (f.std(0) + 1e-6)
    return (f / (np.linalg.norm(f, axis=1, keepdims=True) + 1e-6)).astype(np.float32)


def dtw_map(ref, rec):
    """For every reference frame, the matching recording frame (steps of 0, 1 or 2 recording frames)."""
    C = 1 - ref @ rec.T; n, m = C.shape; INF = np.float32(1e9)
    D = np.full(m, INF, np.float32); D[:25] = C[0, :25]; B = np.zeros((n, m), np.int8)
    for i in range(1, n):
        a = D; b = np.concatenate([[INF], D[:-1]]); c = np.concatenate([[INF, INF], D[:-2]])
        stk = np.stack([a, b, c]); k = stk.argmin(0); D = C[i] + stk[k, np.arange(m)]; B[i] = k
    j = m - 1 - int(np.argmin(D[::-1][:25])); path = np.zeros(n, int)
    for i in range(n - 1, -1, -1):
        path[i] = j; j = max(0, j - int(B[i, j]))
    return path


def align_sentences(audio, texts):
    """[(start, end)] in the recording for each sentence, in order."""
    from kokoro_onnx import Kokoro
    import hashlib
    cache = W + "align_ref_" + hashlib.sha1("|".join(texts).encode()).hexdigest()[:12] + ".npz"
    if os.path.exists(cache):
        z = np.load(cache); ref, bounds, sr = z["ref"], [tuple(b) for b in z["bounds"]], int(z["sr"])
    else:
        k = Kokoro(W + "tts/kokoro.onnx", W + "tts/voices.bin"); parts, bounds, t = [], [], 0.0
        for x in texts:
            s, sr = k.create(x, voice="am_adam", speed=1.3, lang="en-us"); i = np.where(np.abs(s) > 0.01)[0]; s = s[i[0]:i[-1]]
            bounds.append((t, t + len(s) / sr)); parts += [s, np.zeros(int(0.2 * sr), np.float32)]; t += len(s) / sr + 0.2
        ref = np.concatenate(parts); np.savez(cache, ref=ref, bounds=np.array(bounds), sr=sr)
    path = dtw_map(mel(ref, sr), mel(audio, SR))
    to_rec = lambda tt: path[min(len(path) - 1, int(tt / 0.02))] * 0.02
    segs = segments(audio)
    starts = np.array([a for a, _ in segs]); ends = np.array([b for _, b in segs])
    out = []
    for a, b in bounds:
        ra, rb = to_rec(a), to_rec(b)
        sa = starts[np.argmin(abs(starts - ra))]; sb = ends[np.argmin(abs(ends - rb))]
        out.append([sa if abs(sa - ra) < 0.45 else ra, sb if abs(sb - rb) < 0.45 else rb])
    for q in range(1, len(out)):  # keep order and no overlaps
        out[q][0] = max(out[q][0], out[q - 1][1]); out[q][1] = max(out[q][1], out[q][0] + 0.1)
    return out, segs


def fit_lines(segs, exp):
    """Group consecutive voiced segments into len(exp) lines so line lengths match the expected proportions;
    longer pauses are preferred as line breaks."""
    M, L = len(segs), len(exp)
    if M < L: raise SystemExit(f"found {M} voiced parts but the script has {L} lines - pauses too short?")
    total = segs[-1][1] - segs[0][0]; ratio = total / exp.sum()
    gap = [segs[i + 1][0] - segs[i][1] for i in range(M - 1)] + [1.0]
    INF = 1e18; cost = np.full((L + 1, M + 1), INF); back = np.zeros((L + 1, M + 1), int); cost[0, 0] = 0
    for l in range(1, L + 1):
        for j in range(l, M - (L - l) + 1):
            for i in range(l - 1, j):
                if cost[l - 1, i] >= INF: continue
                dur = segs[j - 1][1] - segs[i][0]
                c = cost[l - 1, i] + ((dur - exp[l - 1] * ratio) / (exp[l - 1] * ratio + 0.3)) ** 2 - 1.5 * min(gap[j - 1], 0.8)
                if c < cost[l, j]: cost[l, j] = c; back[l, j] = i
    groups, j = [], M
    for l in range(L, 0, -1):
        i = back[l, j]; groups.append(segs[i:j]); j = i
    return groups[::-1]


def syllables(w):
    w = re.sub(r"[^a-z]", "", w.lower())
    return max(1, len(re.findall(r"[aeiouy]+", w)) - (1 if w.endswith("e") and len(w) > 3 else 0))


def word_times(text, parts, sentence_spans=None):
    """Spread words over the voiced parts: per aligned sentence when known, else one sentence per part when the
    counts match, else across the whole line."""
    sentences = split_sentences(text)
    if sentence_spans:
        chunks = [(x.split(), [[max(p0, a), min(p1, b)] for p0, p1 in parts if p1 > a and p0 < b] or [[a, b]])
                  for x, (a, b) in zip(sentences, sentence_spans)]
    elif len(sentences) == len(parts): chunks = [(x.split(), [p]) for x, p in zip(sentences, parts)]
    else: chunks = [(text.split(), parts)]
    out = []
    for words, ps in chunks:
        wts = np.array([syllables(w) + 0.6 for w in words], float); cum = np.concatenate([[0], np.cumsum(wts)]) / wts.sum()
        voiced = sum(e - s for s, e in ps)
        def at(u):  # position u (0..1) through the voiced time -> seconds
            t = u * voiced
            for s, e in ps:
                if t <= e - s + 1e-9: return s + t
                t -= e - s
            return ps[-1][1]
        for k, w in enumerate(words): out.append([w, round(at(cum[k]), 3), round(at(cum[k + 1]), 3)])
    return out


def main(story_path):
    story = json.load(open(story_path)); vf = story["voice_files"]
    lines = [l if isinstance(l, list) else ["narrator", l] for l in story["lines"]]
    nar = load(os.path.join(REPO, vf["narrator"])); oth = load(os.path.join(REPO, vf["others"]))
    n_idx = [i for i, l in enumerate(lines) if l[0] == "narrator"]; o_idx = [i for i, l in enumerate(lines) if l[0] != "narrator"]
    assert [lines[i][0] for i in o_idx] == vf["others_order"], "others_order must match the script's other-voice lines"
    placed, spans = {}, {}
    sent = [(i, x) for i in n_idx for x in split_sentences(lines[i][1])]
    sspans, nsegs = align_sentences(nar, [x for _, x in sent])
    for i in n_idx:
        sp = [sspans[q] for q, (li, _) in enumerate(sent) if li == i]; spans[i] = sp
        placed[i] = (nar, [[a, b] for a, b in nsegs if b > sp[0][0] + 0.02 and a < sp[-1][1] - 0.02] or [[sp[0][0], sp[-1][1]]])
    groups = fit_lines(segments(oth), expected_lengths([lines[i][1] for i in o_idx]))
    for i, g in zip(o_idx, groups): placed[i] = (oth, g)
    # stitch in script order with tight, natural gaps
    out, timed, t = [np.zeros(int(0.12 * SR), np.float32)], [], 0.12
    for i, (speaker, text) in enumerate(lines):
        audio, g = placed[i]
        if i in spans: g = [[max(a, spans[i][0][0]), min(b, spans[i][-1][1])] for a, b in g]
        s0, e0 = max(0, g[0][0] - 0.03), g[-1][1] + 0.05
        clip = audio[int(s0 * SR):int(e0 * SR)]
        words = [[w, round(t + a - s0, 3), round(t + b - s0, 3)] for w, a, b in word_times(text, g, spans.get(i))]
        timed.append({"speaker": speaker, "text": text, "start": t, "end": t + len(clip) / SR, "words": words})
        nxt = lines[i + 1][0] if i + 1 < len(lines) else None
        gap = 0.1 if (nxt and (nxt != "narrator" or speaker != "narrator")) else 0.18
        out += [clip, np.zeros(int(gap * SR), np.float32)]; t += len(clip) / SR + gap
    raw = W + "voice_raw.wav"; sf.write(raw, np.concatenate(out), SR)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af", "loudnorm=I=-14:TP=-1.0", "-ar", str(SR), W + "voice.wav"], check=True)
    json.dump(timed, open(W + "lines_timed.json", "w"), indent=1)
    print(f"voice: {t:.1f}s, {len(lines)} lines")


if __name__ == "__main__":
    main(sys.argv[1])
