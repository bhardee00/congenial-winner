"""Pictures for hurry.py (reference #4 style): the SPEED meter over the hero's head, comic speech bubbles, speed lines,
classroom board, floors, clothing prints."""
import os, sys, math, random
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import town

INK, WHITE = (25, 25, 30), (255, 255, 255)
METER = list(range(0, 101, 5))


def meter_name(v): return f"meter_{v}.png"


def bubble_name(k): return f"bubble_{k}.png"


BUBBLES = {"mom": "HURRY UP!", "teacher": "HURRY UP!", "bully": "HURRY UP!", "coach": "HURRY UP!", "grandma": "TAKE YOUR TIME~", "cta": "COMMENT \"HURRY UP\"!"}


def make(out, font):
    from PIL import Image, ImageDraw, ImageFilter
    for v in METER:  # the floating meter: label + bar, green -> yellow -> red as it empties
        im = Image.new("RGBA", (800, 260), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.text((400, 58), "SPEED", font=font(78), anchor="mm", fill=WHITE, stroke_width=8, stroke_fill=INK)
        d.rounded_rectangle((40, 120, 760, 230), 40, fill=(30, 30, 38, 235), outline=WHITE, width=10)
        c = (70, 220, 90) if v >= 60 else (245, 200, 50) if v >= 30 else (235, 60, 50)
        if v > 0: d.rounded_rectangle((58, 138, 58 + int(684 * v / 100), 212), 28, fill=c)
        d.text((400, 175), f"{v}%", font=font(64), anchor="mm", fill=WHITE, stroke_width=6, stroke_fill=INK)
        im.save(out + meter_name(v))
    W, H = 1080, 1440
    for k, txt in BUBBLES.items():  # comic speech bubble, full frame, upper-middle (under the captions)
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        f = font(110 if len(txt) < 12 else 84); tw = d.textlength(txt, font=f)
        cx, cy = W / 2, H * 0.31; bw, bh = tw / 2 + 70, 105
        d.polygon([(cx - 60, cy + bh - 20), (cx + 10, cy + bh - 20), (cx - 90, cy + bh + 90)], fill=WHITE, outline=INK, width=10)
        d.ellipse((cx - bw, cy - bh, cx + bw, cy + bh), fill=WHITE, outline=INK, width=12)
        d.polygon([(cx - 55, cy + bh - 30), (cx + 5, cy + bh - 30), (cx - 80, cy + bh + 70)], fill=WHITE)
        d.text((cx, cy + 4), txt, font=f, anchor="mm", fill=(220, 40, 40) if k != "grandma" else (220, 90, 160), stroke_width=4, stroke_fill=INK)
        im.save(out + bubble_name(k))
    rnd = random.Random(4)  # speed lines: white streaks rushing in from the edges
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for _ in range(70):
        a = rnd.uniform(0, math.tau); r0 = rnd.uniform(430, 560); r1 = r0 + rnd.uniform(250, 600)
        x0, y0 = W / 2 + math.cos(a) * r0, H / 2 + math.sin(a) * r0 * 1.3; x1, y1 = W / 2 + math.cos(a) * r1, H / 2 + math.sin(a) * r1 * 1.3
        d.line((x0, y0, x1, y1), fill=(255, 255, 255, rnd.randint(120, 220)), width=rnd.randint(4, 12))
    im.filter(ImageFilter.GaussianBlur(1.2)).save(out + "speedlines.png")
    im = Image.new("RGBA", (1600, 800), (40, 85, 60, 255)); d = ImageDraw.Draw(im)  # chalkboard
    d.rectangle((0, 0, 1599, 799), outline=(150, 110, 70), width=30)
    d.text((800, 230), "POP QUIZ!", font=font(170), anchor="mm", fill=(240, 240, 230))
    d.text((800, 470), "12 x 12 = ?", font=font(130), anchor="mm", fill=(240, 240, 230))
    im.save(out + "chalkboard.png")
    im = Image.new("RGBA", (600, 800), (250, 250, 245, 255)); d = ImageDraw.Draw(im)  # the finished test
    d.text((300, 90), "TEST", font=font(90), anchor="mm", fill=INK)
    for k in range(6): d.line((60, 200 + k * 90, 540, 200 + k * 90), fill=(160, 160, 170), width=4); d.text((80, 175 + k * 90), "✓" if False else "A+", font=font(48), anchor="lm", fill=(40, 150, 60))
    d.ellipse((380, 600, 560, 780), outline=(220, 40, 40), width=14); d.text((470, 690), "A+", font=font(90), anchor="mm", fill=(220, 40, 40))
    im.save(out + "test.png")
    im = Image.new("RGB", (512, 512), (232, 232, 222)); d = ImageDraw.Draw(im)  # linoleum tiles
    for k in range(0, 512, 128): d.line((k, 0, k, 512), fill=(205, 205, 195), width=5); d.line((0, k, 512, k), fill=(205, 205, 195), width=5)
    for x in range(0, 512, 128):
        for y in range(0, 512, 128):
            if (x + y) // 128 % 3 == 0: d.rectangle((x + 3, y + 3, x + 125, y + 125), fill=(120, 170, 220))
    im.save(out + "tiles.png")
    im = Image.new("RGB", (1024, 512), (40, 100, 190)); d = ImageDraw.Draw(im)  # the planet: oceans and continents
    for _ in range(26):
        x, y, r = rnd.randint(0, 1024), rnd.randint(80, 430), rnd.randint(30, 110)
        d.ellipse((x - r, y - r * 0.7, x + r, y + r * 0.7), fill=rnd.choice([(70, 160, 80), (90, 175, 85), (190, 170, 110)]))
    d.rectangle((0, 0, 1024, 40), fill=(240, 245, 250)); d.rectangle((0, 472, 1024, 512), fill=(240, 245, 250))
    im.filter(ImageFilter.GaussianBlur(3)).save(out + "planet.png")
    for k, (kind, base, a1, a2) in {"varsity": ("stripes", (40, 110, 60), (240, 240, 230), (250, 250, 250)),
                                    "cardigan": ("plaid", (130, 100, 70), (100, 75, 50), (210, 190, 160)),
                                    "floral_lav": ("floral", (175, 165, 230), (235, 230, 250), (250, 200, 225)),
                                    "dots_teal": ("dots", (80, 190, 190), (240, 250, 250), (250, 250, 250)),
                                    "denim": ("denim", (60, 85, 140), (30, 45, 80), (250, 250, 250))}.items():
        town.cloth_png(kind, base, a1, out + f"print_{k}.png", a2)
