"""Pictures for library.py: wood floor, signs and posters, Grandma's HEAD LIBRARIAN badge, the final QUIET PLEASE
sign with Leo's handprint, the story-time book cover, clothing prints."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import town

INK, WHITE = (40, 32, 28), (255, 255, 255)


def make(out, font):
    from PIL import Image, ImageDraw
    import random
    rnd = random.Random(3)
    im = Image.new("RGB", (512, 512), (180, 130, 85)); d = ImageDraw.Draw(im)  # wood planks
    for k in range(0, 512, 64):
        c = tuple(int(v * rnd.uniform(0.9, 1.08)) for v in (180, 130, 85)); d.rectangle((0, k, 512, k + 62), fill=c)
        d.line((0, k + 62, 512, k + 62), fill=(130, 90, 55), width=3); off = rnd.randint(0, 400); d.line((off, k, off, k + 62), fill=(130, 90, 55), width=3)
        for _ in range(6):
            y = k + rnd.randint(4, 58); d.line((rnd.randint(0, 512), y, rnd.randint(0, 512), y), fill=tuple(int(v * 0.93) for v in c), width=1)
    im.save(out + "wood_floor.png")
    im = Image.new("RGBA", (1600, 350), (60, 100, 70, 255)); d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 1599, 349), outline=(230, 200, 120), width=16)
    d.text((800, 175), "PUBLIC LIBRARY", font=font(170), anchor="mm", fill=(250, 240, 210))
    im.save(out + "library_sign.png")
    im = Image.new("RGBA", (900, 270), (250, 210, 80, 255)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((8, 8, 892, 262), 40, outline=(220, 90, 90), width=14); d.text((450, 135), "STORY TIME", font=font(130), anchor="mm", fill=(200, 70, 90))
    im.save(out + "storytime_sign.png")
    im = Image.new("RGBA", (600, 250), (40, 90, 160, 255)); d = ImageDraw.Draw(im)
    d.text((300, 125), "BOOK RETURN", font=font(80), anchor="mm", fill=WHITE)
    im.save(out + "return_sign.png")
    for name, txt, bg in (("poster_read", ("READ", "MORE!"), (90, 170, 220)), ("poster_quiet", ("SHHH...", "QUIET"), (230, 120, 120))):
        im = Image.new("RGBA", (600, 800), bg + (255,)); d = ImageDraw.Draw(im)
        d.rectangle((0, 0, 599, 799), outline=WHITE, width=20)
        d.text((300, 300), txt[0], font=font(140), anchor="mm", fill=WHITE); d.text((300, 500), txt[1], font=font(120), anchor="mm", fill=WHITE)
        im.save(out + f"{name}.png")
    im = Image.new("RGBA", (500, 300), (250, 250, 245, 255)); d = ImageDraw.Draw(im)  # Grandma's badge
    d.rounded_rectangle((6, 6, 494, 294), 30, fill=(250, 250, 245), outline=(200, 160, 50), width=16)
    d.text((250, 105), "HEAD", font=font(100), anchor="mm", fill=(40, 70, 140)); d.text((250, 205), "LIBRARIAN", font=font(78), anchor="mm", fill=(40, 70, 140))
    im.save(out + "badge.png")
    im = Image.new("RGBA", (1000, 1300), WHITE + (255,)); d = ImageDraw.Draw(im)  # final sign
    d.rounded_rectangle((10, 10, 990, 1290), 40, outline=(60, 100, 70), width=26)
    d.text((500, 210), "QUIET", font=font(190), anchor="mm", fill=(60, 100, 70)); d.text((500, 380), "PLEASE", font=font(150), anchor="mm", fill=(60, 100, 70))
    d.text((500, 560), "(except babies)", font=font(80), anchor="mm", fill=INK)
    d.text((500, 760), "- the head librarian", font=font(56), anchor="mm", fill=INK)
    hx, hy = 660, 1030; c = (60, 120, 200)  # tiny handprint
    d.ellipse((hx - 70, hy - 60, hx + 70, hy + 80), fill=c)
    for k, (dx, dy, l) in enumerate(((-62, -60, 70), (-25, -95, 90), (15, -100, 95), (52, -85, 80))):
        d.rounded_rectangle((hx + dx - 17, hy + dy - l // 2, hx + dx + 17, hy + dy + l // 2), 17, fill=c)
    d.rounded_rectangle((hx - 120, hy - 10, hx - 60, hy + 25), 17, fill=c)
    im.save(out + "quiet_sign.png")
    im = Image.new("RGBA", (800, 1000), (240, 120, 80, 255)); d = ImageDraw.Draw(im)  # Leo's story book
    d.rectangle((20, 20, 780, 980), outline=(255, 220, 90), width=18)
    d.text((400, 220), "THE BIG", font=font(110), anchor="mm", fill=WHITE); d.text((400, 350), "LOUD", font=font(150), anchor="mm", fill=(255, 230, 120))
    d.text((400, 480), "LIBRARY", font=font(110), anchor="mm", fill=WHITE)
    d.ellipse((260, 580, 540, 860), fill=(250, 220, 120)); d.ellipse((330, 660, 370, 700), fill=INK); d.ellipse((430, 660, 470, 700), fill=INK)
    d.arc((340, 700, 460, 800), 20, 160, fill=INK, width=12)
    im.save(out + "story_book.png")
    for k, (kind, base, a1, a2) in {"floral_lav": ("floral", (175, 165, 230), (235, 230, 250), (250, 200, 225)),
                                    "cardigan": ("plaid", (130, 160, 120), (100, 130, 95), (220, 220, 200)),
                                    "dots_teal": ("dots", (80, 190, 190), (240, 250, 250), (250, 250, 250)),
                                    "stripes_navy": ("stripes", (250, 250, 250), (40, 60, 120), (250, 250, 250)),
                                    "stripes_yellow": ("stripes", (255, 245, 210), (240, 190, 60), (250, 250, 250)),
                                    "floral_red": ("floral", (220, 70, 80), (250, 230, 120), (250, 250, 250)),
                                    "denim": ("denim", (60, 85, 140), (30, 45, 80), (250, 250, 250))}.items():
        town.cloth_png(kind, base, a1, out + f"print_{k}.png", a2)
