"""Narration: reads work/lines.json (list of strings) and writes work/voice.wav + timed work/lines_timed.json."""
import os, json, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
W = os.environ.get('SHORTS_WORK', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'work')) + '/'
k = Kokoro(W + "tts/kokoro.onnx", W + "tts/voices.bin")
lines = json.load(open(W + "lines.json"))
out = []; au = []; sr = 24000; t = 0.25; au.append(np.zeros(int(0.25 * sr), dtype=np.float32))
for x in lines:
    s, sr = k.create(x, voice="am_michael", speed=1.1, lang="en-us")
    i = np.where(np.abs(s) > 0.01)[0]; s = s[max(0, i[0] - 200):i[-1] + 400]
    out.append({"text": x, "start": t, "end": t + len(s) / sr})
    au += [s, np.zeros(int(0.3 * sr), dtype=s.dtype)]; t += len(s) / sr + 0.3
sf.write(W + "voice.wav", np.concatenate(au), sr)
json.dump(out, open(W + "lines_timed.json", "w"), indent=1)
print("narration seconds:", round(t, 2))
