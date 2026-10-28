"""Pictures for bored_grandpa.py (made by make_short.py before Blender runs)."""
import math
from PIL import Image, ImageDraw

INK, WHITE, CREAM = (30, 30, 40), (255, 255, 255), (252, 248, 236)


def make(out, font):
    # birthday card: front and inside (the wish)
    im = Image.new("RGBA", (800, 1000), (90, 170, 230, 255)); d = ImageDraw.Draw(im)
    for k in range(14): d.ellipse((60 + (k * 137) % 680, 80 + (k * 211) % 860, 90 + (k * 137) % 680, 110 + (k * 211) % 860), fill=(255, 220, 90))
    d.text((400, 330), "HAPPY", font=font(120), anchor="mm", fill=WHITE, stroke_width=6, stroke_fill=INK)
    d.text((400, 480), "80th", font=font(170), anchor="mm", fill=(255, 220, 90), stroke_width=8, stroke_fill=INK)
    d.text((400, 640), "GRANDPA!", font=font(110), anchor="mm", fill=WHITE, stroke_width=6, stroke_fill=INK)
    d.rounded_rectangle((300, 720, 500, 900), 12, fill=(250, 120, 160)); d.rectangle((390, 640, 410, 720), fill=(250, 240, 200))
    im.save(out + "card_front.png")
    im = Image.new("RGBA", (800, 1000), CREAM + (255,)); d = ImageDraw.Draw(im)
    d.text((400, 160), "Make a wish!", font=font(80), anchor="mm", fill=(90, 170, 230))
    d.text((120, 330), "my wish:", font=font(64), anchor="lm", fill=(150, 150, 160))
    for k, t in enumerate(("I wish I wasn't", "too old for", "my grandson.")):
        d.text((400, 470 + k * 120), t, font=font(86), anchor="mm", fill=(40, 60, 150))
    d.text((560, 870), "- Harold", font=font(64), anchor="mm", fill=(40, 60, 150))
    im.save(out + "card_inside.png")
    # chalkboard
    im = Image.new("RGBA", (1600, 800), (40, 85, 60, 255)); d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 1599, 799), outline=(150, 110, 70), width=30)
    d.text((800, 250), "2x + 7 = 19", font=font(150), anchor="mm", fill=(240, 240, 230))
    d.text((800, 470), "x = ?", font=font(150), anchor="mm", fill=(240, 240, 230))
    d.text((1300, 680), "MATH :)", font=font(70), anchor="mm", fill=(255, 220, 120))
    im.save(out + "chalkboard.png")
    # bored jar label, finish banner, storybook, rocks label
    im = Image.new("RGBA", (700, 300), (250, 245, 230, 255)); d = ImageDraw.Draw(im)
    d.rectangle((8, 8, 692, 292), outline=INK, width=10); d.text((350, 150), "BORED JAR", font=font(120), anchor="mm", fill=(200, 50, 50))
    im.save(out + "bored_jar.png")
    im = Image.new("RGBA", (1600, 360), (230, 40, 50, 255)); d = ImageDraw.Draw(im)
    for k in range(0, 1600, 80): d.rectangle((k, 0, k + 40, 40), fill=WHITE); d.rectangle((k + 40, 320, k + 80, 360), fill=WHITE)
    d.text((800, 180), "FINISH", font=font(200), anchor="mm", fill=WHITE)
    im.save(out + "finish.png")
    im = Image.new("RGBA", (700, 900), (120, 70, 160, 255)); d = ImageDraw.Draw(im)
    d.rectangle((20, 20, 680, 880), outline=(255, 220, 90), width=14)
    d.text((350, 200), "The Very", font=font(90), anchor="mm", fill=WHITE); d.text((350, 310), "Sleepy Bear", font=font(90), anchor="mm", fill=WHITE)
    d.ellipse((220, 450, 480, 710), fill=(160, 110, 70)); d.ellipse((205, 430, 285, 510), fill=(160, 110, 70)); d.ellipse((415, 430, 495, 510), fill=(160, 110, 70))
    for x in (305, 395): d.arc((x - 25, 540, x + 25, 580), 20, 160, fill=INK, width=8)
    d.text((350, 800), "zzz", font=font(80), anchor="mm", fill=(255, 220, 90))
    im.save(out + "storybook.png")
    im = Image.new("RGBA", (700, 220), (250, 245, 230, 255)); d = ImageDraw.Draw(im)
    d.text((350, 75), "ROCK COLLECTION", font=font(70), anchor="mm", fill=INK); d.text((350, 160), "(mostly gravel)", font=font(56), anchor="mm", fill=(120, 120, 120))
    im.save(out + "rocks.png")
    # playing card face and back
    im = Image.new("RGBA", (500, 700), WHITE + (255,)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((6, 6, 494, 694), 30, outline=(200, 200, 200), width=8)
    d.text((80, 90), "7", font=font(110), anchor="mm", fill=(210, 40, 50)); d.ellipse((150, 260, 260, 370), fill=(210, 40, 50)); d.ellipse((240, 260, 350, 370), fill=(210, 40, 50))
    d.polygon([(152, 330), (348, 330), (250, 470)], fill=(210, 40, 50))
    im.save(out + "card_face.png")
    im = Image.new("RGBA", (500, 700), (40, 80, 170, 255)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((20, 20, 480, 680), 24, outline=WHITE, width=12)
    for k in range(0, 700, 50): d.line((20, k, 480, k + 200), fill=(70, 110, 200), width=10)
    im.save(out + "card_back.png")
    # grandfather clock dial
    s = 800; im = Image.new("RGBA", (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = s / 2
    d.ellipse((6, 6, s - 6, s - 6), fill=(200, 160, 70)); d.ellipse((40, 40, s - 40, s - 40), fill=CREAM)
    for n in range(1, 13):
        a = n / 12 * math.tau; d.text((c + math.sin(a) * 280, c - math.cos(a) * 280), ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII"][n - 1], font=font(70), anchor="mm", fill=INK)
    im.save(out + "dial_gold.png")
