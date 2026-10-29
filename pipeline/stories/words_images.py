"""Pictures for words.py (made by make_short.py before Blender runs): chest-counter badges, the big on-screen
countdown, clothing prints, signs, cue cards and the sign-language book."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import town

INK, WHITE, CREAM, MINT = (30, 30, 40), (255, 255, 255), (252, 248, 236), (140, 255, 210)
# every counter value shown on someone's chest (words.py keys them to frames)
ME = [7211 - k for k in range(9)] + [4560 - k for k in range(13)] + [1337 - k for k in range(9)] + [902] + list(range(15))
MOM = [3412 - k for k in range(9)]
MAX = [9870 - k for k in range(6)]
PEARL = [9000, 8999, 8998] + [8998 - k for k in range(18)]
CROWD = [2316, 5870, 8950, 0, 1, 6120, 7450, 4021, 6688, 3157, 9204, 5512, 2890, 7733, 1846, 8312, 4477, 6930, 10000]
VALUES = sorted(set(ME + MOM + MAX + PEARL + CROWD))
PRINTS = {  # name: (kind, base, accent, accent2)
    "plaid_red": ("plaid", (150, 55, 45), (60, 35, 30), (230, 210, 170)),
    "plaid_brown": ("plaid", (120, 90, 60), (70, 50, 35), (210, 190, 150)),
    "floral_blue": ("floral", (60, 70, 140), (220, 120, 160), (250, 240, 220)),
    "floral_green": ("floral", (70, 120, 90), (250, 200, 90), (250, 250, 240)),
    "stripes_blue": ("stripes", (240, 240, 245), (60, 110, 210), (250, 250, 250)),
    "stripes_red": ("stripes", (240, 240, 240), (210, 60, 60), (250, 250, 250)),
    "dots_pink": ("dots", (235, 120, 150), (255, 230, 240), (250, 250, 250)),
    "denim": ("denim", (60, 85, 140), (30, 45, 80), (250, 250, 250)),
    "denim_dark": ("denim", (40, 50, 80), (20, 25, 45), (250, 250, 250)),
}


def badge_name(v): return f"badge_{v}.png"


def make(out, font):
    for v in VALUES: town.badge_png(f"{v:,}", out + badge_name(v), font)
    for k, (kind, base, a1, a2) in PRINTS.items(): town.cloth_png(kind, base, a1, out + f"print_{k}.png", a2)
    from PIL import Image, ImageDraw, ImageFilter
    # big countdown numbers over the climax (full frame, upper middle, clear of the captions at 70%)
    W, H = 1080, 1440
    for n in range(15):
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        f = font(330); ImageDraw.Draw(g).text((W / 2, H * 0.3), str(n), font=f, anchor="mm", fill=(60, 255, 180, 230))
        im.alpha_composite(g.filter(ImageFilter.GaussianBlur(22)))
        ImageDraw.Draw(im).text((W / 2, H * 0.3), str(n), font=f, anchor="mm", fill=MINT, stroke_width=14, stroke_fill=(10, 40, 32))
        im.save(out + f"count_{n}.png")
    # diner menu board
    im = Image.new("RGBA", (1200, 800), (35, 35, 38, 255)); d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 1199, 799), outline=(150, 110, 70), width=26)
    d.text((600, 110), "MENU", font=font(110), anchor="mm", fill=(255, 210, 90))
    for k, (a, b) in enumerate((("PANCAKES", "$5"), ("SYRUP", "$1"), ("EGGS", "$4"), ("COFFEE", "$2"))):
        d.text((150, 270 + k * 125), a, font=font(80), anchor="lm", fill=WHITE); d.text((1050, 270 + k * 125), b, font=font(80), anchor="rm", fill=WHITE)
    im.save(out + "menu.png")
    # mayor's cue cards: the speech, card 40 says only THANKS
    for k, (t, n) in enumerate((("Good evening,\nQuietville.", "1/40"), ("The budget\nis...", "17/40"), ("THANKS.", "40/40"))):
        im = Image.new("RGBA", (900, 600), CREAM + (255,)); d = ImageDraw.Draw(im)
        d.rectangle((0, 0, 899, 599), outline=(200, 190, 170), width=10)
        d.multiline_text((450, 280), t, font=font(140 if k == 2 else 96), anchor="mm", fill=INK, align="center")
        d.text((850, 560), n, font=font(44), anchor="rm", fill=(150, 150, 150))
        im.save(out + f"cue_{k}.png")
    # sign-language book: cover and a page of four signs
    im = Image.new("RGBA", (700, 900), (40, 110, 180, 255)); d = ImageDraw.Draw(im)
    d.rectangle((20, 20, 680, 880), outline=(255, 220, 90), width=14)
    d.text((350, 170), "SIGN", font=font(130), anchor="mm", fill=WHITE); d.text((350, 300), "LANGUAGE", font=font(96), anchor="mm", fill=WHITE)
    d.text((350, 400), "for beginners", font=font(60), anchor="mm", fill=(255, 220, 90))
    _hand(d, 350, 640, 1.6, (250, 215, 180))
    im.save(out + "book_cover.png")
    im = Image.new("RGBA", (1000, 700), CREAM + (255,)); d = ImageDraw.Draw(im)
    for k, t in enumerate(("HELLO", "THANK YOU", "HELP", "FREEZE")):
        x, y = 250 + (k % 2) * 500, 170 + (k // 2) * 330
        _hand(d, x, y, 1.0, (234, 190, 150), k); d.text((x, y + 140), t, font=font(60), anchor="mm", fill=(200, 50, 50) if t == "FREEZE" else INK)
    im.save(out + "book_page.png")
    # block party banner, ice cream truck sign, town sign, library sign
    im = Image.new("RGBA", (2000, 400), (230, 60, 70, 255)); d = ImageDraw.Draw(im)
    for k in range(0, 2000, 100): d.polygon([(k, 0), (k + 100, 0), (k + 50, 60)], fill=(255, 220, 90))
    d.text((1000, 230), "BLOCK PARTY!", font=font(200), anchor="mm", fill=WHITE, stroke_width=8, stroke_fill=(120, 20, 30))
    im.save(out + "banner.png")
    im = Image.new("RGBA", (1200, 500), (255, 245, 250, 255)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((10, 10, 1190, 490), 60, outline=(240, 110, 160), width=24)
    d.text((730, 250), "ICE CREAM", font=font(140), anchor="mm", fill=(240, 90, 150), stroke_width=6, stroke_fill=WHITE)
    d.polygon([(120, 230), (240, 230), (180, 440)], fill=(220, 170, 100)); d.ellipse((105, 110, 255, 260), fill=(255, 190, 210))
    im.save(out + "truck_sign.png")
    im = Image.new("RGBA", (1400, 700), (40, 110, 70, 255)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((14, 14, 1386, 686), 40, outline=WHITE, width=18)
    d.text((700, 220), "WELCOME TO", font=font(110), anchor="mm", fill=WHITE); d.text((700, 400), "QUIETVILLE", font=font(190), anchor="mm", fill=WHITE)
    d.text((700, 580), "PLEASE KEEP IT DOWN", font=font(70), anchor="mm", fill=(255, 220, 90))
    im.save(out + "town_sign.png")
    im = Image.new("RGBA", (1000, 360), (250, 245, 230, 255)); d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 999, 359), outline=INK, width=16); d.text((500, 180), "LIBRARY", font=font(150), anchor="mm", fill=INK)
    im.save(out + "library_sign.png")
    im = Image.new("RGBA", (1000, 360), (250, 250, 250, 255)); d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 999, 359), outline=(200, 40, 40), width=20); d.text((500, 180), "DINER", font=font(170), anchor="mm", fill=(200, 40, 40))
    im.save(out + "diner_sign.png")
    # TV game (a soccer game: the shot goes wide) and the stadium scoreboard
    im = Image.new("RGBA", (1280, 720), (60, 150, 70, 255)); d = ImageDraw.Draw(im)
    for k in range(0, 1280, 160): d.rectangle((k, 0, k + 80, 720), fill=(70, 165, 80))
    d.rectangle((40, 40, 1240, 680), outline=WHITE, width=10); d.line((640, 40, 640, 680), fill=WHITE, width=10)
    d.rectangle((1100, 250, 1240, 470), outline=WHITE, width=10); d.ellipse((900, 140, 960, 200), fill=WHITE, outline=INK, width=6)
    d.rectangle((40, 30, 520, 120), fill=(20, 20, 30)); d.text((280, 75), "HOME 0 - 0 AWAY", font=font(52), anchor="mm", fill=WHITE)
    im.save(out + "tv_game.png")
    im = Image.new("RGBA", (1400, 600), (25, 25, 30, 255)); d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 1399, 599), outline=(200, 200, 200), width=14)
    d.text((350, 160), "HOME", font=font(110), anchor="mm", fill=WHITE); d.text((1050, 160), "AWAY", font=font(110), anchor="mm", fill=WHITE)
    d.text((350, 380), "14", font=font(220), anchor="mm", fill=(255, 200, 60)); d.text((1050, 380), "7", font=font(220), anchor="mm", fill=(255, 200, 60))
    im.save(out + "scoreboard.png")


def _hand(d, x, y, s, skin, kind=0):
    """A simple cartoon hand (palm + fingers) for the sign-language book."""
    pw, ph = 90 * s, 100 * s
    d.rounded_rectangle((x - pw / 2, y - ph / 2 + 20 * s, x + pw / 2, y + ph / 2 + 20 * s), 24 * s, fill=skin, outline=INK, width=int(5 * s))
    n = 4 if kind != 3 else 0
    for k in range(n):
        fx = x - pw / 2 + 12 * s + k * 22 * s; up = 0 if kind != 1 else 20 * s
        d.rounded_rectangle((fx, y - ph / 2 - 50 * s + up, fx + 18 * s, y - ph / 2 + 30 * s), 9 * s, fill=skin, outline=INK, width=int(4 * s))
    if kind == 3:  # FREEZE: two crossed arms
        for a in (-1, 1):
            d.line((x - 70 * s * a, y - 80 * s, x + 70 * s * a, y + 80 * s), fill=skin, width=int(40 * s))
    d.rounded_rectangle((x - pw / 2 - 26 * s, y, x - pw / 2 + 4 * s, y + 18 * s), 9 * s, fill=skin, outline=INK, width=int(4 * s))
