"""Draw classic Roblox clothing templates (585x559) for the test: Mom's red gingham dress with a white apron."""
from PIL import Image, ImageDraw
import sys
sys.path.insert(0, "/home/user/congenial-winner/pipeline")
RECTS = {"torso": {"F": (231, 74, 128, 128), "B": (427, 74, 128, 128), "R": (165, 74, 64, 128), "L": (361, 74, 64, 128),
                   "U": (231, 8, 128, 64), "D": (231, 204, 128, 64)},
         "right": {"L": (19, 355, 64, 128), "B": (85, 355, 64, 128), "R": (151, 355, 64, 128), "F": (217, 355, 64, 128),
                   "U": (217, 289, 64, 64), "D": (217, 485, 64, 64)},
         "left": {"F": (308, 355, 64, 128), "L": (374, 355, 64, 128), "B": (440, 355, 64, 128), "R": (506, 355, 64, 128),
                  "U": (308, 289, 64, 64), "D": (308, 485, 64, 64)}}
OUT = "/home/user/congenial-winner/work/tmp/rs/"
RED, WHITE, DK = (205, 30, 35, 255), (250, 248, 245, 255), (150, 20, 25, 255)


def gingham(d, box, cell=3):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=WHITE)
    for x in range(x0, x1, cell * 2): d.rectangle((x, y0, x + cell - 1, y1), fill=(230, 120, 125, 255))
    for y in range(y0, y1, cell * 2): d.rectangle((x0, y, x1, y + cell - 1), fill=(230, 120, 125, 255))
    for x in range(x0, x1, cell * 2):
        for y in range(y0, y1, cell * 2): d.rectangle((x, y, x + cell - 1, y + cell - 1), fill=RED)


def r(rect): x, y, w, h = rect; return (x, y, x + w - 1, y + h - 1)


# shirt: gingham bodice + white apron bib on the torso; puffy gingham short sleeves, skin below
im = Image.new("RGBA", (585, 559), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
for side, rc in RECTS["torso"].items():
    gingham(d, r(rc))
x, y, w, h = RECTS["torso"]["F"]
d.polygon([(x + 22, y + 40), (x + w - 22, y + 40), (x + w - 14, y + h), (x + 14, y + h)], fill=WHITE)  # apron bib
d.rectangle((x + 30, y, x + 38, y + 44), fill=WHITE); d.rectangle((x + w - 38, y, x + w - 30, y + 44), fill=WHITE)  # straps
d.rectangle((x, y + h - 22, x + w, y + h), fill=RED)  # waistband
d.polygon([(x + 34, y), (x + 64, y + 26), (x + w - 34, y)], fill=(240, 160, 110, 0))  # neckline shows skin
for arm in ("left", "right"):
    for side, rc in RECTS[arm].items():
        if side in ("U",): gingham(d, r(rc)); continue
        if side == "D": continue
        X, Y, W, H = rc; gingham(d, (X, Y, X + W - 1, Y + 34))
        d.rectangle((X, Y + 30, X + W - 1, Y + 36), fill=RED)
im.save(OUT + "mom_shirt.png")
# pants: red skirt over the upper legs with the apron front, skin below, white socks + red shoes
im = Image.new("RGBA", (585, 559), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
for leg in ("left", "right"):
    for side, rc in RECTS[leg].items():
        X, Y, W, H = rc
        if side == "U": d.rectangle(r(rc), fill=RED); continue
        if side == "D": d.rectangle(r(rc), fill=(200, 30, 40, 255)); continue
        d.rectangle((X, Y, X + W - 1, Y + 62), fill=RED)
        if side == "F": d.rectangle((X + 6, Y, X + W - 7, Y + 70), fill=WHITE)
        d.rectangle((X, Y + H - 22, X + W - 1, Y + H - 1), fill=(250, 250, 250, 255)); d.rectangle((X, Y + H - 10, X + W - 1, Y + H - 1), fill=(200, 30, 40, 255))
for side, rc in RECTS["torso"].items(): d.rectangle(r(rc), fill=RED)
im.save(OUT + "mom_pants.png")
print("ok")
