import os
import json, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
D = os.environ.get('SHORTS_WORK', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'work')) + '/'
OUT = sys.argv[1]
FPS, N, FREEZE = 30, 150, 86

font = ImageFont.truetype(D + "Fredoka.ttf", 92)
try: font.set_variation_by_name("Bold")
except Exception: pass

# one word at a time, timed proportionally to word length within each spoken line
words = []
for l in json.load(open(D + "lines_timed.json")):
    ws = l["text"].split(); tot = sum(len(w) + 1 for w in ws); acc = 0
    for w in ws:
        s = l["start"] + acc / tot * (l["end"] - l["start"]); acc += len(w) + 1
        words.append([w.strip(".,").lower(), s])
for i, w in enumerate(words):
    w.append(words[i + 1][1] if i + 1 < len(words) else w[1] + 0.6)

ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "image2pipe", "-framerate", str(FPS), "-c:v", "png", "-i", "-",
                       "-i", D + "voice.wav", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "17", "-preset", "slow",
                       "-c:a", "aac", "-b:a", "192k", "-shortest", OUT], stdin=subprocess.PIPE)
for f in range(N):
    t = f / FPS
    im = Image.open(D + f"frames/f_{f:04d}.png").convert("RGB")
    if f >= FREEZE:  # world paused: cooler, less saturated
        im = ImageEnhance.Color(im).enhance(0.55)
        blue = Image.new("RGB", im.size, (120, 150, 200)); im = Image.blend(im, blue, 0.08)
        if f < FREEZE + 6:  # flash on the button press
            im = Image.blend(im, Image.new("RGB", im.size, (255, 255, 255)), 0.8 * (1 - (f - FREEZE) / 6))
    d = ImageDraw.Draw(im)
    cur = next((w for w in words if w[1] <= t < w[2]), None)
    if cur:
        x, y = im.width / 2, im.height * 0.62
        d.text((x, y), cur[0], font=font, anchor="mm", fill=(255, 226, 61), stroke_width=9, stroke_fill=(0, 0, 0))
    im.save(ff.stdin, "PNG", compress_level=1)
ff.stdin.close(); ff.wait()
print("done", OUT)
