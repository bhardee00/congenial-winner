"""Pictures for parrot.py (made by make_short.py before Blender runs): clock dials, the stopwatch, the will, the note,
the viral video, the check, Grandpa's portrait and a few labels. make(out_dir, font) writes them into out_dir."""
import math
from PIL import Image, ImageDraw

INK, WHITE, CREAM = (30, 30, 40), (255, 255, 255), (250, 246, 232)


def dial(path, rim, face=CREAM, size=1024):
    """Clock face with numbers and ticks only (the hands are 3D so any time can be shown)."""
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = size / 2
    d.ellipse((8, 8, size - 8, size - 8), fill=rim); d.ellipse((60, 60, size - 60, size - 60), fill=face)
    for k in range(60):
        a = k / 60 * math.tau; r0 = 410 if k % 5 else 385; w = 12 if k % 5 == 0 else 5
        d.line((c + math.sin(a) * r0, c - math.cos(a) * r0, c + math.sin(a) * 440, c - math.cos(a) * 440), fill=INK, width=w)
    return im, d, c


def make(out, font):
    for name, rim in (("dial_blue", (40, 70, 140)), ("dial_red", (205, 40, 45))):
        im, d, c = dial(out + name + ".png", rim)
        for n in range(1, 13):
            a = n / 12 * math.tau; d.text((c + math.sin(a) * 320, c - math.cos(a) * 320), str(n), font=font(96), anchor="mm", fill=INK)
        im.save(out + name + ".png")
    # stopwatch face
    im, d, c = dial(out + "stopwatch.png", (200, 205, 215), (255, 255, 255))
    d.rounded_rectangle((c - 230, c + 90, c + 230, c + 230), 24, fill=(25, 30, 35))
    d.text((c, c + 160), "00:00", font=font(110), anchor="mm", fill=(120, 255, 140))
    im.save(out + "stopwatch.png")
    # the will
    im = Image.new("RGBA", (800, 1040), CREAM + (255,)); d = ImageDraw.Draw(im)
    d.rectangle((20, 20, 780, 1020), outline=(170, 140, 90), width=10)
    d.text((400, 130), "LAST WILL", font=font(96), anchor="mm", fill=INK)
    d.text((400, 230), "of Grandpa", font=font(56), anchor="mm", fill=(90, 80, 70))
    for y in range(320, 520, 50): d.line((90, y, 710, y), fill=(190, 180, 160), width=8)
    d.text((400, 620), "$1,000,000", font=font(120), anchor="mm", fill=(30, 140, 60))
    d.text((400, 740), "if the parrot", font=font(60), anchor="mm", fill=INK)
    d.text((400, 810), "stays QUIET", font=font(70), anchor="mm", fill=(200, 40, 40))
    d.text((400, 880), "for 24 hours", font=font(60), anchor="mm", fill=INK)
    im.save(out + "will.png")
    # the freezer note
    im = Image.new("RGBA", (700, 520), (255, 240, 120, 255)); d = ImageDraw.Draw(im)
    d.text((350, 260), "Nice try.", font=font(130), anchor="mm", fill=INK); d.text((560, 420), "- G", font=font(70), anchor="mm", fill=INK)
    im.save(out + "note.png")
    # phone screens: whale sounds / viral video (overlay, full frame) / views
    im = Image.new("RGBA", (500, 900), (20, 30, 60, 255)); d = ImageDraw.Draw(im)
    d.text((250, 150), "WHALE", font=font(80), anchor="mm", fill=WHITE); d.text((250, 240), "SOUNDS", font=font(80), anchor="mm", fill=WHITE)
    d.text((250, 330), "10 hours", font=font(44), anchor="mm", fill=(150, 200, 255))
    d.ellipse((150, 430, 350, 630), fill=(60, 140, 240)); d.polygon([(225, 480), (225, 580), (305, 530)], fill=WHITE)
    for k in range(9): h = 30 + 50 * abs(math.sin(k * 1.3)); d.rounded_rectangle((70 + k * 42, 780 - h, 100 + k * 42, 780), 8, fill=(120, 190, 255))
    im.save(out + "phone_whale.png")
    W, H = 1080, 1440
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((170, 230, 910, 1210), 70, fill=(20, 20, 25)); d.rounded_rectangle((200, 300, 880, 1140), 30, fill=(250, 250, 250))
    d.rectangle((200, 300, 880, 690), fill=(40, 40, 50)); d.polygon([(500, 430), (500, 560), (610, 495)], fill=WHITE)
    d.text((230, 740), "BIRD SINGS BETTER", font=font(50), anchor="lm", fill=INK); d.text((230, 800), "THAN ME (NOT CLICKBAIT)", font=font(44), anchor="lm", fill=INK)
    d.text((230, 890), "1,000,000 views", font=font(64), anchor="lm", fill=(220, 40, 40))
    d.rounded_rectangle((230, 960, 520, 1050), 20, fill=(230, 40, 40)); d.text((375, 1005), "SUBSCRIBE", font=font(42), anchor="mm", fill=WHITE)
    d.text((620, 1005), "98K likes", font=font(48), anchor="mm", fill=INK)
    im.save(out + "viral.png")
    # censor bar
    im = Image.new("RGBA", (700, 170), (15, 15, 15, 255)); d = ImageDraw.Draw(im)
    d.text((350, 85), "CENSORED", font=font(100), anchor="mm", fill=WHITE); im.save(out + "censored.png")
    # the check
    im = Image.new("RGBA", (1200, 520), (215, 240, 220, 255)); d = ImageDraw.Draw(im)
    d.rectangle((14, 14, 1186, 506), outline=(60, 130, 80), width=10)
    d.text((70, 90), "PAY TO: GRANDSON (THE ONE WHO VISITED)", font=font(44), anchor="lm", fill=INK)
    d.rounded_rectangle((760, 170, 1150, 280), 14, fill=WHITE); d.text((955, 225), "$1,000,000", font=font(72), anchor="mm", fill=(20, 110, 50))
    d.text((70, 225), "One million dollars", font=font(56), anchor="lm", fill=INK)
    d.line((640, 440, 1130, 440), fill=INK, width=5); d.text((885, 400), "Grandpa", font=font(60), anchor="mm", fill=(40, 60, 150))
    im.save(out + "check.png")
    # Grandpa's portrait (blocky head, grey hair, glasses, warm smile)
    im = Image.new("RGBA", (700, 880), (120, 80, 50, 255)); d = ImageDraw.Draw(im)
    d.rectangle((40, 40, 660, 840), fill=(200, 225, 240))
    d.rounded_rectangle((210, 220, 490, 500), 60, fill=(234, 190, 150)); d.rounded_rectangle((195, 180, 505, 280), 40, fill=(200, 200, 205))
    for x in (295, 405): d.ellipse((x - 45, 300, x + 45, 390), outline=INK, width=10); d.ellipse((x - 12, 335, x + 12, 360), fill=INK)
    d.line((340, 345, 360, 345), fill=INK, width=10); d.arc((285, 360, 415, 460), 20, 160, fill=INK, width=12)
    d.rounded_rectangle((160, 500, 540, 840), 40, fill=(140, 90, 60)); d.polygon([(350, 500), (300, 600), (400, 600)], fill=WHITE)
    im.save(out + "portrait.png")
    # taxes stack label, wi-fi password label, gold cracker box label
    im = Image.new("RGBA", (700, 900), (250, 250, 250, 255)); d = ImageDraw.Draw(im)
    d.text((350, 110), "TAXES", font=font(120), anchor="mm", fill=INK); d.text((350, 210), "1987 - 2025", font=font(56), anchor="mm", fill=(90, 90, 90))
    for y in range(300, 860, 46): d.line((60, y, 640, y), fill=(170, 170, 170), width=8)
    im.save(out + "taxes.png")
    im = Image.new("RGBA", (600, 260), WHITE + (255,)); d = ImageDraw.Draw(im)
    d.text((300, 80), "WI-FI", font=font(70), anchor="mm", fill=INK); d.text((300, 180), "pw: Captain4ever", font=font(52), anchor="mm", fill=(40, 90, 200))
    im.save(out + "wifi.png")
    im = Image.new("RGBA", (600, 800), (250, 200, 40, 255)); d = ImageDraw.Draw(im)
    d.rectangle((20, 20, 580, 780), outline=(160, 110, 10), width=16)
    d.text((300, 230), "PREMIUM", font=font(90), anchor="mm", fill=(120, 60, 10)); d.text((300, 340), "CRACKERS", font=font(90), anchor="mm", fill=(120, 60, 10))
    for k in range(5): d.rounded_rectangle((90 + k * 90, 480, 160 + k * 90, 550), 10, fill=(230, 160, 60))
    d.text((300, 660), "parrot approved", font=font(52), anchor="mm", fill=(120, 60, 10))
    im.save(out + "cracker_gold.png")
    im = Image.new("RGBA", (600, 800), (230, 60, 50, 255)); d = ImageDraw.Draw(im)
    d.text((300, 300), "CRACKERS", font=font(96), anchor="mm", fill=WHITE); d.text((300, 420), "store brand", font=font(56), anchor="mm", fill=(255, 220, 220))
    im.save(out + "cracker_red.png")
