"""Narration: reads work/lines.json (list of strings) and writes work/voice.wav + timed work/lines_timed.json.
Voice: Kokoro am_adam at its natural pitch, sped up 1.3x from the 1.1 base.
Override with env SHORTS_VOICE / SHORTS_SPEED / SHORTS_PITCH."""
import os, json, subprocess, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
W = os.environ.get('SHORTS_WORK', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'work')) + '/'
VOICE = os.environ.get("SHORTS_VOICE", "am_adam")
SPEED = float(os.environ.get("SHORTS_SPEED", 1.43))  # 1.1 x 1.3
PITCH = float(os.environ.get("SHORTS_PITCH", 1.0))  # >1 raises pitch (formants shifted, like CapCut's slider)
GAP = 0.3

k = Kokoro(W + "tts/kokoro.onnx", W + "tts/voices.bin")
lines = json.load(open(W + "lines.json"))
out = []; au = []; sr = 24000; t = 0.25; au.append(np.zeros(int(0.25 * sr), dtype=np.float32))
for x in lines:
    s, sr = k.create(x, voice=VOICE, speed=SPEED, lang="en-us")
    i = np.where(np.abs(s) > 0.01)[0]; s = s[max(0, i[0] - 200):i[-1] + 400]
    out.append({"text": x, "start": t, "end": t + len(s) / sr})
    au += [s, np.zeros(int(GAP * sr), dtype=s.dtype)]; t += len(s) / sr + GAP
raw = W + "voice_raw.wav"
sf.write(raw, np.concatenate(au), sr)
# rubberband keeps the duration, so the line timings above stay valid
pitch = f"rubberband=pitch={PITCH}:formant=shifted," if PITCH != 1.0 else ""
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af", pitch + "loudnorm=I=-16:TP=-1.5",
                "-ar", "48000", W + "voice.wav"], check=True)
json.dump(out, open(W + "lines_timed.json", "w"), indent=1)
print("narration seconds:", round(t, 2))
