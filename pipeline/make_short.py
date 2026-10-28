"""One command from story to a packed, render-ready .blend:
    python3 pipeline/make_short.py pipeline/stories/pause_remote.json [--preview]
1. narration (tts.py, cached until the lines change)  2. free Creator Store models (downloaded, converted, credited)
3. caption words, title cards and other images  4. Blender builds every set + the edit -> render/<slug>.blend
Render it anywhere with Blender 4.0:  blender -b render/<slug>.blend -a   (writes render/<slug>.mp4)
--preview also renders a few low-res frames into work/short/preview/ to check the shots here."""
import os, sys, json, hashlib, subprocess, math
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
D = os.environ.get('SHORTS_WORK', os.path.join(REPO, 'work')) + '/'
OUT = D + "short/"
W, H = 1080, 1440  # 3:4 portrait
YELLOW, BLACK, WHITE = (255, 226, 61), (0, 0, 0), (255, 255, 255)


def font(size):
    f = ImageFont.truetype(D + "Fredoka.ttf", size)
    try: f.set_variation_by_name("Bold")
    except Exception: pass
    return f


def narration(story):
    if story.get("voice_files"):  # recorded voices (e.g. ElevenLabs): place each line in the recordings
        vf = story["voice_files"]
        files = [os.path.join(REPO, vf[k]) for k in ("narrator", "others")] + [os.path.join(REPO, f) for f in vf.get("replace", {}).values()]
        key = hashlib.sha1((json.dumps(story["lines"]) + json.dumps(vf, sort_keys=True) + "".join(str(os.path.getsize(f)) for f in files)
                            + open(HERE + "/voice_import.py").read()).encode()).hexdigest()
        stamp = D + "voice.key"
        if os.path.exists(D + "voice.wav") and os.path.exists(stamp) and open(stamp).read() == key: return
        sys.path.insert(0, HERE); import voice_import; voice_import.main(os.path.abspath(sys.argv[1]))
        open(stamp, "w").write(key); return
    lines = [l[1] if isinstance(l, list) else l for l in story["lines"]]
    key = hashlib.sha1(json.dumps([lines, open(HERE + "/tts.py").read()]).encode()).hexdigest()
    stamp = D + "voice.key"
    if os.path.exists(D + "voice.wav") and os.path.exists(stamp) and open(stamp).read() == key:
        return
    json.dump(lines, open(D + "lines.json", "w"))
    subprocess.run([sys.executable, HERE + "/tts.py"], check=True)
    open(stamp, "w").write(key)


def fetch_models(story):
    """Download + convert each free model once, and write the credits list for the video description."""
    sys.path.insert(0, HERE)
    import store, rbx_model
    for name, m in story["models"].items():
        if not os.path.exists(D + f"models/{m['id']}.json"):
            store.get(m["id"], m); rbx_model.convert(m["id"])
    with open(os.path.join(REPO, "render", story["slug"] + "_credits.txt"), "w") as f:
        f.write("Free models from the Roblox Creator Store:\n")
        for name, m in story["models"].items(): f.write(f'- {m["name"]} by {m["creator"]} (asset {m["id"]})\n')
        if story.get("music_credit"): f.write(f'\nMusic: {story["music_credit"]}\n')


CAPTION_FONT = os.path.join(REPO, "assets", "fonts", "LiberationSans-Bold.ttf")  # free Arial look-alike (SIL OFL)
CAPTION_Y = 0.70  # one fixed spot for every word, like the user's example


def captions(timed):
    """One full-frame transparent PNG per spoken word: white, bold sans, thin black outline, lowercase, in one fixed
    spot (CAPTION_Y), shown while it is said - matching the user's example. Used by every short."""
    os.makedirs(OUT + "words", exist_ok=True); f = ImageFont.truetype(CAPTION_FONT, 92); words = []
    for l in timed:
        if "words" in l: words += [[w.strip(".,?!\"").lower(), s, e] for w, s, e in l["words"]]
        else:  # older narration without word timings: spread the line by word length
            ws = l["text"].split(); tot = sum(len(w) + 1 for w in ws); acc = 0
            for w in ws:
                s = l["start"] + acc / tot * (l["end"] - l["start"]); acc += len(w) + 1
                words.append([w.strip(".,?!\"").lower(), s, s + (len(w) + 1) / tot * (l["end"] - l["start"])])
    out = []
    for i, (w, s, e) in enumerate(words):
        nxt = words[i + 1][1] if i + 1 < len(words) else e + 0.6
        e = nxt if nxt - e < 0.35 else e + 0.25  # hold until the next word unless there is a real pause
        p = OUT + f"words/w{i:03d}.png"
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.text((W / 2 + 3, H * CAPTION_Y + 4), w, font=f, anchor="mm", fill=(0, 0, 0, 110), stroke_width=4, stroke_fill=(0, 0, 0, 110))  # soft shadow
        d.text((W / 2, H * CAPTION_Y), w, font=f, anchor="mm", fill=WHITE, stroke_width=4, stroke_fill=BLACK)
        im.save(p, optimize=True); out.append((p, s, e))
    return out


def sounds(story, timed):
    """Synthesised effects and music (audio.py), plus spoken effects said by the voice model (story "voice_sfx")."""
    sys.path.insert(0, HERE)
    import audio
    audio.make_sfx(OUT + "sfx")
    # the user's own sound effects (assets/sfx/<name>.wav|mp3) replace or add to the synthesized ones by name
    import glob
    for f in sorted(glob.glob(os.path.join(REPO, "assets", "sfx", "*"))):
        name = os.path.splitext(os.path.basename(f))[0]
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f, "-ac", "1", "-ar", str(audio.SR), OUT + f"sfx/{name}.wav"], check=True)
    if story.get("music_file"):  # your own track; muffled and quieter while the world is paused
        src = os.path.join(REPO, story["music_file"])
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-ac", "1", "-ar", str(audio.SR), OUT + "music_normal.wav"], check=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-ac", "1", "-ar", str(audio.SR), "-af", "lowpass=f=700,volume=0.7",
                        OUT + "music_paused.wav"], check=True)
    elif story.get("synth_music"):
        audio.make_music(OUT + "music_normal.wav", OUT + "music_paused.wav", timed[-1]["end"] + 4)
    from kokoro_onnx import Kokoro
    k = Kokoro(D + "tts/kokoro.onnx", D + "tts/voices.bin")
    for name, (text, voice, speed) in story.get("voice_sfx", {}).items():
        a, sr = k.create(text, voice=voice, speed=speed, lang="en-us")
        tmp = OUT + f"sfx/{name}_raw.wav"; import soundfile as sf; sf.write(tmp, a, sr)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-ar", str(audio.SR), "-ac", "1", OUT + f"sfx/{name}.wav"], check=True)
        os.remove(tmp)


def card(text, name, size=150, y=0.2, color=WHITE, sub=None):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.text((W / 2, H * y), text, font=font(size), anchor="mm", fill=color, stroke_width=12, stroke_fill=BLACK)
    if sub: d.text((W / 2, H * y + size * 0.9), sub, font=font(int(size * 0.4)), anchor="mm", fill=WHITE, stroke_width=6, stroke_fill=BLACK)
    im.save(OUT + name)


def icon(kind, name):
    """Big pause / play symbol flashed when the remote is pressed."""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im); cx, cy = W / 2, H * 0.36
    if kind == "pause":
        for x in (-95, 45):
            d.rounded_rectangle((cx + x - 8, cy - 158, cx + x + 58, cy + 158), 22, fill=WHITE, outline=BLACK, width=12)
    else:
        d.polygon([(cx - 110, cy - 160), (cx - 110, cy + 160), (cx + 160, cy)], fill=WHITE, outline=BLACK, width=12)
    im.save(OUT + name)


def sign(lines, name, bg=(200, 30, 30), fg=WHITE, size=(900, 500)):
    im = Image.new("RGBA", size, bg + (255,)); d = ImageDraw.Draw(im)
    d.rectangle((10, 10, size[0] - 10, size[1] - 10), outline=fg, width=14)
    n = len(lines)
    for i, (t, s) in enumerate(lines):
        d.text((size[0] / 2, size[1] * (i + 1) / (n + 1)), t, font=font(s), anchor="mm", fill=fg)
    im.save(OUT + name)


def smile_decal(name):
    im = Image.new("RGBA", (400, 200), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.arc((30, -170, 370, 170), 20, 160, fill=(25, 15, 12, 255), width=38)
    im.save(OUT + name)


def clock(hour, minute, name):
    s = 600; im = Image.new("RGBA", (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = s / 2
    d.ellipse((10, 10, s - 10, s - 10), fill=WHITE, outline=BLACK, width=26)
    for k in range(12):
        a = k / 12 * math.tau; d.line((c + math.sin(a) * 230, c - math.cos(a) * 230, c + math.sin(a) * 260, c - math.cos(a) * 260), fill=BLACK, width=14)
    for ang, ln, w in (((hour % 12 + minute / 60) / 12 * math.tau, 150, 26), (minute / 60 * math.tau, 225, 16)):
        d.line((c, c, c + math.sin(ang) * ln, c - math.cos(ang) * ln), fill=BLACK, width=w)
    d.ellipse((c - 22, c - 22, c + 22, c + 22), fill=(200, 40, 40))
    im.save(OUT + name)


def images():
    card("PARIS", "card_paris.png"); card("JAPAN", "card_japan.png"); card("ICELAND", "card_iceland.png")
    card("1 YEAR LATER", "card_year.png", 120, sub="(probably)")
    icon("pause", "icon_pause.png"); icon("play", "icon_play.png")
    live = Image.new("RGBA", (W, 230), (0, 0, 0, 0)); d = ImageDraw.Draw(live)
    d.rounded_rectangle((40, 40, 260, 140), 18, fill=(225, 30, 40)); d.text((150, 90), "LIVE", font=font(70), anchor="mm", fill=WHITE)
    d.rounded_rectangle((40, 150, W - 40, 220), 14, fill=(250, 250, 250)); d.text((W / 2, 185), "MAN STUCK TO BALLOON", font=font(54), anchor="mm", fill=(30, 30, 40))
    live.save(OUT + "live_banner.png")
    dot = Image.new("RGBA", (70, 70), (0, 0, 0, 0)); ImageDraw.Draw(dot).ellipse((8, 8, 62, 62), fill=(235, 30, 40), outline=(255, 255, 255), width=5)
    dot.save(OUT + "live_dot.png")
    lt = Image.new("RGBA", (200, 90), (0, 0, 0, 0)); ImageDraw.Draw(lt).text((100, 45), "LIVE", font=font(72), anchor="mm", fill=WHITE, stroke_width=6, stroke_fill=BLACK)
    lt.save(OUT + "live_text.png")
    sign([("AA BATTERIES", 110), ("SOLD OUT", 150)], "sign_soldout.png")
    sign([("SORRY!", 120), ("NO AA", 160)], "sign_noaa.png", bg=(240, 190, 30), fg=(40, 30, 20))
    sign([("BATTERIES", 120)], "sign_batteries.png", bg=(30, 90, 170), size=(900, 260))
    smile_decal("smile_decal.png")
    for i, (h, m) in enumerate(((3, 10), (8, 45), (11, 55))): clock(h, m, f"clock{i}.png")


SHARED = ("Fredoka.ttf", "avatar", "models", "tts", "whisper")  # downloaded/converted once, used by every short


def story_workdir(slug):
    """Each short gets its own work folder (voice, timings, captions, previews) so building one never overwrites
    another's; the big shared things (voice model, avatar, models) are linked in from work/."""
    global D, OUT
    base = os.path.join(REPO, "work"); d = os.path.join(base, "stories", slug)
    os.makedirs(d, exist_ok=True)
    for n in SHARED:
        src, dst = os.path.join(base, n), os.path.join(d, n)
        if os.path.exists(src) and not os.path.lexists(dst): os.symlink(src, dst)
    os.environ["SHORTS_WORK"] = d; D = d + "/"; OUT = D + "short/"


def main():
    story_path = os.path.abspath(sys.argv[1]); story = json.load(open(story_path))
    if "SHORTS_WORK" not in os.environ: story_workdir(story["slug"])
    os.makedirs(OUT, exist_ok=True); os.makedirs(os.path.join(REPO, "render"), exist_ok=True)
    narration(story)
    timed = json.load(open(D + "lines_timed.json"))
    fetch_models(story)
    json.dump(captions(timed), open(OUT + "words.json", "w"))
    images()
    extra = os.path.join(HERE, "stories", story["module"] + "_images.py")  # story-specific pictures (no bpy needed)
    if os.path.exists(extra):
        sys.path.insert(0, os.path.dirname(extra)); __import__(story["module"] + "_images").make(OUT, font)
    sounds(story, timed)
    args = ["blender", "-b", "--python-exit-code", "1", "-P", HERE + "/build_short.py", "--", story_path] + [a for a in sys.argv[2:] if a.startswith("--")]
    subprocess.run(args, check=True)


if __name__ == "__main__":
    main()
