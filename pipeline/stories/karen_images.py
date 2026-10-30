"""Pictures for karen.py: floor tiles, menu board (before / after Karen Tears), the LIVE phone screens, the OWNER
apron, shop sign, clothing prints."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import town

INK, WHITE, PINK, MINT = (40, 30, 40), (255, 255, 255), (245, 130, 170), (150, 225, 200)
FLAVORS = [("VANILLA", (250, 240, 210)), ("CHOCOLATE", (120, 75, 50)), ("STRAWBERRY", (245, 150, 175)), ("MINT CHIP", (170, 235, 200)),
           ("COOKIE DOUGH", (230, 200, 150)), ("BUBBLEGUM", (120, 200, 245))]


def make(out, font):
    from PIL import Image, ImageDraw, ImageFilter
    # checkered floor tile (mint / cream, like the reference store)
    im = Image.new("RGB", (512, 512), (250, 246, 232)); d = ImageDraw.Draw(im)
    for x in range(2):
        for y in range(2):
            if (x + y) % 2: d.rectangle((x * 256, y * 256, x * 256 + 255, y * 256 + 255), fill=(200, 238, 220))
    im.save(out + "floor_tile.png")
    for name, extra in (("menu_before", False), ("menu_after", True)):
        im = Image.new("RGBA", (1400, 900), (255, 236, 244, 255)); d = ImageDraw.Draw(im)
        d.rounded_rectangle((10, 10, 1390, 890), 50, outline=PINK, width=22)
        d.text((700, 110), "FLAVORS", font=font(110), anchor="mm", fill=PINK, stroke_width=4, stroke_fill=WHITE)
        rows = FLAVORS + ([("KAREN TEARS", (130, 190, 255))] if extra else [])
        for k, (t, c) in enumerate(rows):
            x, y = (330 if k % 2 == 0 else 1030), 260 + (k // 2) * 150
            d.ellipse((x - 270, y - 42, x - 186, y + 42), fill=c, outline=INK, width=6)
            d.text((x - 160, y), t, font=font(58 if extra and t == "KAREN TEARS" else 54), anchor="lm", fill=(70, 120, 220) if t == "KAREN TEARS" else INK)
        if extra:
            d.text((1030 - 160, 260 + 3 * 150 + 58), "(salty)", font=font(40), anchor="lm", fill=(120, 120, 140))
            d.rounded_rectangle((1150, 640, 1330, 700), 20, fill=(240, 70, 90)); d.text((1240, 670), "NEW!", font=font(44), anchor="mm", fill=WHITE)
        im.save(out + f"{name}.png")
    # phone screens: Karen's LIVE (zero viewers), then the same screen in close-up
    for name, big in (("live", False), ("live_zero", True)):
        im = Image.new("RGBA", (600, 1100), (210, 215, 225, 255)); d = ImageDraw.Draw(im)
        d.ellipse((140, 280, 460, 640), fill=(240, 215, 130)); d.ellipse((190, 360, 410, 640), fill=(234, 190, 150))
        d.rectangle((120, 640, 480, 1100), fill=(170, 160, 230))
        d.rounded_rectangle((30, 40, 230, 130), 22, fill=(235, 40, 50)); d.ellipse((50, 70, 80, 100), fill=WHITE)
        d.text((150, 86), "LIVE", font=font(60), anchor="mm", fill=WHITE)
        d.rounded_rectangle((30, 150, 330 if not big else 560, 220 if not big else 300), 20, fill=(20, 20, 30, 200))
        d.text((50, 185 if not big else 225), "0 watching", font=font(44 if not big else 80), anchor="lm", fill=WHITE)
        im.save(out + f"{name}.png")

    # LIVE phone overlays (full frame, see-through screen so the selfie camera view of the shop shows through)
    W, H = 1080, 1440
    for name, big in (("phone_live", False), ("phone_live_zero", True)):
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle((20, 20, W - 20, H - 20), 110, outline=(18, 18, 22, 255), width=60)
        d.rounded_rectangle((W / 2 - 150, 50, W / 2 + 150, 100), 25, fill=(18, 18, 22, 255))  # notch
        d.rounded_rectangle((110, 230, 330, 320), 22, fill=(235, 40, 50, 255)); d.ellipse((132, 258, 166, 292), fill=WHITE)
        d.text((248, 276), "LIVE", font=font(64), anchor="mm", fill=WHITE)
        if big:
            d.rounded_rectangle((W / 2 - 330, 1000, W / 2 + 330, 1160), 50, fill=(15, 15, 25, 210))
            d.text((W / 2, 1080), "0 watching", font=font(110), anchor="mm", fill=WHITE)
        else:
            d.rounded_rectangle((350, 240, 640, 310), 20, fill=(15, 15, 25, 170)); d.text((495, 276), "0 watching", font=font(44), anchor="mm", fill=WHITE)
        d.rounded_rectangle((110, H - 230, W - 250, H - 140), 45, fill=(255, 255, 255, 90)); d.text((150, H - 185), "Say something...", font=font(44), anchor="lm", fill=(255, 255, 255, 230))
        d.ellipse((W - 220, H - 235, W - 120, H - 135), fill=(245, 90, 120, 200)); d.text((W - 170, H - 185), "<3", font=font(40), anchor="mm", fill=WHITE)
        im.save(out + f"{name}.png")
    # OWNER apron front, the shop sign, the "BANNED" stamp
    im = Image.new("RGBA", (600, 700), (245, 130, 170, 255)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((20, 20, 580, 680), 60, outline=WHITE, width=16)
    d.text((300, 300), "OWNER", font=font(130), anchor="mm", fill=WHITE, stroke_width=6, stroke_fill=(200, 70, 110))
    d.polygon([(250, 420), (350, 420), (300, 620)], fill=(220, 170, 100)); d.ellipse((235, 340, 365, 470), fill=(255, 245, 250))
    im.save(out + "apron.png")
    im = Image.new("RGBA", (1600, 420), (255, 255, 255, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((10, 10, 1590, 410), 120, fill=(245, 130, 170), outline=WHITE, width=16)
    d.text((800, 215), "SCOOP SHOP", font=font(200), anchor="mm", fill=WHITE, stroke_width=8, stroke_fill=(200, 70, 110))
    im.save(out + "shop_sign.png")
    for k, (kind, base, a1, a2) in {"floral_lav": ("floral", (175, 165, 230), (235, 230, 250), (250, 200, 225)),
                                    "dots_white": ("dots", (250, 250, 250), (245, 150, 175), (250, 250, 250)),
                                    "stripes_pink": ("stripes", (255, 255, 255), (245, 150, 175), (250, 250, 250)),
                                    "denim": ("denim", (60, 85, 140), (30, 45, 80), (250, 250, 250))}.items():
        town.cloth_png(kind, base, a1, out + f"print_{k}.png", a2)
