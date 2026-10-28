"""Narration with ElevenLabs (stock "Adam" voice), the channel's recipe: generate normally, then speed the audio up
1.33x with the pitch rising along with it (plain resampling, like CapCut's speed with "change audio pitch" on).
Other characters use the same voice sped up 1.68x, which makes them higher and quicker.
Reads work/lines.json: a list of strings (narrator) or [speaker, text] pairs; speaker "narrator" or any other name.
Writes work/voice.wav and work/lines_timed.json with exact per-word timings (from ElevenLabs' alignment).
Needs ELEVENLABS_API_KEY in the environment and api.elevenlabs.io allowed by the network policy."""
import os, json, base64, subprocess, urllib.request
import numpy as np, soundfile as sf

W = os.environ.get('SHORTS_WORK', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'work')) + '/'
KEY = os.environ.get("ELEVENLABS_API_KEY")
VOICE_ID = os.environ.get("ELEVENLABS_VOICE", "pNInz6obpgDQGcFmaJgB")  # Adam (ElevenLabs premade voice)
MODEL = os.environ.get("ELEVENLABS_MODEL", "eleven_multilingual_v2")
SPEED = {"narrator": 1.33}; OTHER_SPEED = 1.68
GAP = float(os.environ.get("SHORTS_GAP", 0.12))  # the examples barely pause between lines
SR = 44100
CACHE = W + "eleven_cache/"


def generate(text):
    """Returns (audio float32 at SR, [(char, start, end)]), cached per text so re-runs don't spend credits."""
    os.makedirs(CACHE, exist_ok=True)
    key = base64.urlsafe_b64encode(f"{VOICE_ID}|{MODEL}|{text}".encode()).decode()[:120]
    path = CACHE + key + ".json"
    if not os.path.exists(path):
        req = urllib.request.Request(
            f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/with-timestamps?output_format=pcm_44100",
            data=json.dumps({"text": text, "model_id": MODEL}).encode(),
            headers={"xi-api-key": KEY, "Content-Type": "application/json"})
        json.dump(json.loads(urllib.request.urlopen(req, timeout=120).read()), open(path, "w"))
    d = json.load(open(path))
    pcm = np.frombuffer(base64.b64decode(d["audio_base64"]), dtype="<i2").astype(np.float32) / 32768
    al = d.get("alignment") or d.get("normalized_alignment")
    chars = list(zip(al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]))
    return pcm, chars


def speed_up(a, factor):
    """Faster and higher together: play the samples back `factor` times quicker (resample to keep SR)."""
    n = int(len(a) / factor)
    return np.interp(np.arange(n) * factor, np.arange(len(a)), a).astype(np.float32)


def words_from(chars, text):
    out, cur, s0, e0 = [], "", None, None
    for c, s, e in chars + [(" ", None, None)]:
        if c.isspace():
            if cur: out.append([cur, s0, e0])
            cur, s0 = "", None
        else:
            if s0 is None: s0 = s
            cur += c; e0 = e
    return out


def main():
    if not KEY: raise SystemExit("ELEVENLABS_API_KEY is not set")
    lines = json.load(open(W + "lines.json"))
    out, parts, t = [], [np.zeros(int(0.15 * SR), np.float32)], 0.15
    for x in lines:
        speaker, text = (x if isinstance(x, list) else ["narrator", x])
        f = SPEED.get(speaker, OTHER_SPEED)
        a, chars = generate(text)
        i = np.where(np.abs(a) > 0.01)[0]; lead = max(0, i[0] - 200); a = a[lead:i[-1] + 400]
        a = speed_up(a, f); off = lead / SR
        words = [[w, round(t + (s - off) / f, 3), round(t + (e - off) / f, 3)] for w, s, e in words_from(chars, text)]
        out.append({"speaker": speaker, "text": text, "start": t, "end": t + len(a) / SR, "words": words})
        parts += [a, np.zeros(int(GAP * SR), np.float32)]; t += len(a) / SR + GAP
    raw = W + "voice_raw.wav"; sf.write(raw, np.concatenate(parts), SR)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af", "loudnorm=I=-14:TP=-1.0", "-ar", "48000", W + "voice.wav"], check=True)
    json.dump(out, open(W + "lines_timed.json", "w"), indent=1)
    print("narration seconds:", round(t, 2))


if __name__ == "__main__":
    main()
