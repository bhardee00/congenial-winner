"""Pictures for waterpark.py: pool tiles, deck tiles, the park sign, the lifeguard shirt, the final NO KARENS sign,
classic Roblox shirt templates."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import town

INK, WHITE = (35, 30, 40), (255, 255, 255)


def make(out, font):
    from PIL import Image, ImageDraw
    im = Image.new("RGB", (512, 512), (90, 185, 225)); d = ImageDraw.Draw(im)  # pool floor tiles
    for k in range(0, 512, 64): d.line((k, 0, k, 512), fill=(150, 215, 240), width=4); d.line((0, k, 512, k), fill=(150, 215, 240), width=4)
    im.save(out + "pool_tile.png")
    im = Image.new("RGB", (512, 512), (205, 192, 172)); d = ImageDraw.Draw(im)  # warm deck tiles
    for k in range(0, 512, 128): d.line((k, 0, k, 512), fill=(180, 168, 150), width=6); d.line((0, k, 512, k), fill=(180, 168, 150), width=6)
    im.save(out + "deck_tile.png")
    im = Image.new("RGBA", (1600, 500), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((10, 10, 1590, 490), 120, fill=(40, 150, 230), outline=WHITE, width=18)
    d.text((800, 250), "SPLASH ZONE", font=font(230), anchor="mm", fill=WHITE, stroke_width=10, stroke_fill=(20, 90, 170))
    im.save(out + "park_sign.png")
    im = Image.new("RGBA", (600, 400), (225, 40, 45, 255)); d = ImageDraw.Draw(im)
    d.text((300, 120), "LIFEGUARD", font=font(96), anchor="mm", fill=WHITE)
    d.rectangle((260, 200, 340, 380), fill=WHITE); d.rectangle((210, 250, 390, 330), fill=WHITE)
    im.save(out + "lifeguard.png")
    im = Image.new("RGBA", (1000, 1300), WHITE + (255,)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((10, 10, 990, 1290), 40, outline=(220, 30, 40), width=26)
    d.text((500, 170), "NO KARENS", font=font(150), anchor="mm", fill=(220, 30, 40))
    d.text((500, 310), "IN THE DEEP END", font=font(80), anchor="mm", fill=INK)
    d.ellipse((310, 400, 690, 780), outline=(220, 30, 40), width=34); d.line((360, 450, 640, 730), fill=(220, 30, 40), width=34)
    d.ellipse((410, 470, 590, 650), fill=(245, 225, 140)); d.rectangle((440, 600, 560, 640), fill=(200, 60, 60))
    d.text((500, 900), "- the management", font=font(60), anchor="mm", fill=INK)
    d.ellipse((620, 1020, 700, 1180), fill=(40, 80, 200))
    for k, (dx, dy, r) in enumerate(((600, 995, 16), (630, 980, 14), (662, 978, 13), (690, 988, 12), (712, 1004, 11))): d.ellipse((dx - r, dy - r, dx + r, dy + r), fill=(40, 80, 200))
    im.save(out + "nokarens_sign.png")
    im = Image.new("RGBA", (900, 500), (250, 240, 200, 255)); d = ImageDraw.Draw(im)
    d.text((450, 250), "SNACKS", font=font(200), anchor="mm", fill=(220, 90, 40), stroke_width=8, stroke_fill=WHITE)
    im.save(out + "snack_sign.png")
    for k, (kind, base, a1, a2) in {"floral_lav": ("floral", (175, 165, 230), (235, 230, 250), (250, 200, 225)),
                                    "stripes_navy": ("stripes", (250, 250, 250), (40, 60, 120), (250, 250, 250)),
                                    "dots_teal": ("dots", (80, 190, 190), (240, 250, 250), (250, 250, 250)),
                                    "floral_red": ("floral", (220, 70, 80), (250, 230, 120), (250, 250, 250)),
                                    "denim": ("denim", (60, 85, 140), (30, 45, 80), (250, 250, 250))}.items():
        town.cloth_png(kind, base, a1, out + f"print_{k}.png", a2)
