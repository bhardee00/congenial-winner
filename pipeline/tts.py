"""Narration: reads work/lines.json (list of strings) and writes work/voice.wav + timed work/lines_timed.json,
including when every word is spoken (for the captions).
Voice: Kokoro am_adam (full-precision model, clearer than int8), gently sped up, pitched up to ~167 Hz with
formants kept (so it doesn't go chipmunk), then EQ + compression for a crisp, upfront sound.
Override with env SHORTS_VOICE / SHORTS_SPEED / SHORTS_PITCH / SHORTS_GAP."""
import os, json, subprocess, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
W = os.environ.get('SHORTS_WORK', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'work')) + '/'
VOICE = os.environ.get("SHORTS_VOICE", "am_adam")
SPEED = float(os.environ.get("SHORTS_SPEED", 1.25))
PITCH = float(os.environ.get("SHORTS_PITCH", 1.329))  # am_adam ~126 Hz -> ~167 Hz like the reference
GAP = float(os.environ.get("SHORTS_GAP", 0.35))  # short breath after each line, brisk like the reference
MODEL = W + "tts/kokoro-fp32.onnx" if os.path.exists(W + "tts/kokoro-fp32.onnx") else W + "tts/kokoro.onnx"
CLEAR = ("highpass=f=90,equalizer=f=280:t=q:w=1.2:g=-3,equalizer=f=3500:t=q:w=1.0:g=4,equalizer=f=8000:t=q:w=1.0:g=2,"
         "acompressor=threshold=-20dB:ratio=3:attack=5:release=60:makeup=2,loudnorm=I=-14:TP=-1.0")

k = Kokoro(MODEL, W + "tts/voices.bin")


def say(text):
    s, sr = k.create(text, voice=VOICE, speed=SPEED, lang="en-us")
    i = np.where(np.abs(s) > 0.01)[0]
    return s[max(0, i[0] - 200):i[-1] + 400], sr


def word_times(text, s, sr):
    """Kokoro can't report timings with this model, so each word's end is measured by saying the line's first
    1, 2, 3... words on their own (same voice and speed); the last word runs to the end of the line."""
    words = text.split(); total = len(s) / sr; ends = []
    for j in range(1, len(words)):
        p, _ = say(" ".join(words[:j]))
        ends.append(min((len(p) - 400) / sr, total - 0.12))
    ends = list(np.maximum.accumulate(ends)) + [total] if ends else [total]
    starts = [0.0] + ends[:-1]
    return [[w, round(a, 3), round(b, 3)] for w, a, b in zip(words, starts, ends)]


lines = json.load(open(W + "lines.json"))
out = []; au = []; sr = 24000; t = 0.25; au.append(np.zeros(int(0.25 * sr), dtype=np.float32))
for x in lines:
    s, sr = say(x)
    out.append({"text": x, "start": t, "end": t + len(s) / sr,
                "words": [[w, round(t + a, 3), round(t + b, 3)] for w, a, b in word_times(x, s, sr)]})
    au += [s, np.zeros(int(GAP * sr), dtype=s.dtype)]; t += len(s) / sr + GAP
raw = W + "voice_raw.wav"
sf.write(raw, np.concatenate(au), sr)
# rubberband keeps the duration, so the line timings above stay valid
pitch = f"rubberband=pitch={PITCH}:formant=preserved:pitchq=quality:transients=crisp," if PITCH != 1.0 else ""
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af", pitch + CLEAR,
                "-ar", "48000", W + "voice.wav"], check=True)
json.dump(out, open(W + "lines_timed.json", "w"), indent=1)
print("narration seconds:", round(t, 2))
