"""Draws the avatar's expression decals into assets/face_<name>.png (1024x1024, transparent, classic Roblox style).
Run: python3 faces.py  (writes every face; avatar.py loads them all and react() switches between them)."""
import os, math
from PIL import Image, ImageDraw

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets')
S = 2  # supersample for smooth edges
INK, WHITE, TEAR, BLUSH, SWEAT = (26, 20, 18, 255), (255, 255, 255, 255), (90, 170, 255, 235), (240, 90, 100, 120), (150, 210, 255, 255)
EYE_L, EYE_R, MOUTH_Y = 345, 650, 640   # face layout matches the original smile/shock decals


def canvas(): return Image.new("RGBA", (1024 * S, 1024 * S), (0, 0, 0, 0))
def s(*v): return [x * S for x in v]


def ell(d, cx, cy, rx, ry, fill): d.ellipse(s(cx - rx, cy - ry, cx + rx, cy + ry), fill=fill)


def thick(d, pts, w, fill=INK):
    """Polyline with round caps and joints."""
    d.line([tuple(s(*p)) for p in pts], fill=fill, width=w * S, joint="curve")
    for p in (pts[0], pts[-1]): ell(d, p[0], p[1], w / 2, w / 2, fill)


def arc(d, cx, cy, rx, ry, a0, a1, w, fill=INK, n=40):
    thick(d, [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n)))
              for i in range(n + 1)], w, fill)


BLINK = {"on": False, "used": False}  # while on, the eye helpers draw closed lids (for the *_blink variants)


def lids(d, y=405, w=26):
    for x in (EYE_L, EYE_R): arc(d, x, y - 30, 58, 34, 20, 160, w)


def dot_eyes(d, ry=82, rx=47, shine=True):
    BLINK["used"] = True
    if BLINK["on"]: return lids(d)
    for x in (EYE_L, EYE_R):
        ell(d, x, 400, rx, ry, INK)
        if shine: ell(d, x - 8, 360, 15, 24, WHITE)


def big_eyes(d, r=(78, 106), pupil=38, look=(0, 6), ring=24):
    BLINK["used"] = True
    if BLINK["on"]: return lids(d)
    for x in (EYE_L, EYE_R):
        ell(d, x, 400, r[0], r[1], INK); ell(d, x, 400, r[0] - ring, r[1] - ring, WHITE)
        ell(d, x + look[0], 400 + look[1], pupil, pupil, INK)


def brows(d, l, r, w=28):
    thick(d, l, w); thick(d, r, w)


def face_smile(d):
    brows(d, [(276, 254), (410, 254)], [(580, 254), (714, 254)]); dot_eyes(d); arc(d, 495, 545, 175, 165, 25, 155, 40)


def face_shock(d):
    brows(d, [(272, 240), (425, 208)], [(585, 208), (738, 240)]); big_eyes(d, r=(78, 106), pupil=33)
    ell(d, 505, 665, 58, 68, INK)


def face_big_eyes(d):  # huge "WHAT" eyes for sudden surprises
    brows(d, [(250, 180), (420, 150)], [(590, 150), (760, 180)])
    big_eyes(d, r=(118, 140), pupil=26, ring=26)
    ell(d, 505, 700, 70, 88, INK); ell(d, 505, 728, 42, 40, (200, 70, 70, 255))


def face_happy(d):  # eyes closed ^ ^, big open grin
    brows(d, [(276, 230), (410, 222)], [(580, 222), (714, 230)])
    for x in (EYE_L, EYE_R): arc(d, x, 420, 58, 52, 200, 340, 30)
    d.chord(s(345, 520, 665, 760), 0, 180, fill=INK)
    d.chord(s(380, 590, 630, 690), 0, 180, fill=WHITE)  # teeth along the top of the mouth
    d.pieslice(s(430, 640, 580, 745), 200, 340, fill=(200, 70, 70, 255))


def face_grin(d):  # smug / proud
    brows(d, [(276, 250), (410, 240)], [(580, 222), (714, 250)]); dot_eyes(d, ry=70)
    arc(d, 520, 560, 175, 110, 15, 150, 36); thick(d, [(355, 610), (330, 590)], 30)


def face_sad(d):
    brows(d, [(272, 270), (418, 222)], [(582, 222), (728, 270)]); dot_eyes(d, ry=74)
    arc(d, 500, 760, 140, 105, 205, 335, 34)


def face_cry(d):  # streaming tears, wobbly mouth
    brows(d, [(272, 270), (418, 215)], [(582, 215), (728, 270)])
    for x in (EYE_L, EYE_R):
        arc(d, x, 395, 60, 46, 200, 340, 30)
        d.polygon([tuple(s(*p)) for p in ((x - 32, 430), (x + 32, 430), (x + 44, 1000), (x - 44, 1000))], fill=TEAR)
    thick(d, [(390, 720), (430, 690), (470, 720), (510, 690), (550, 720), (590, 690), (630, 720)], 26)


def face_angry(d):
    brows(d, [(250, 250), (430, 330)], [(580, 330), (760, 250)], w=36); dot_eyes(d, ry=66, shine=False)
    d.rounded_rectangle(s(370, 640, 640, 730), radius=30 * S, fill=INK)
    d.rounded_rectangle(s(392, 660, 618, 710), radius=12 * S, fill=WHITE)
    for x in range(430, 600, 40): d.line(s(x, 660, x, 710), fill=INK, width=8 * S)  # gritted teeth


def face_annoyed(d):  # flat half-lidded eyes
    for x in (EYE_L, EYE_R):
        ell(d, x, 410, 50, 60, INK); d.rectangle(s(x - 60, 330, x + 60, 395), fill=(0, 0, 0, 0))
        thick(d, [(x - 62, 395), (x + 62, 395)], 24)
    thick(d, [(410, 670), (600, 665)], 30)


def face_suspicious(d):  # one brow up, eyes to the side
    brows(d, [(276, 280), (410, 290)], [(580, 205), (714, 235)])
    for x in (EYE_L, EYE_R):
        ell(d, x, 410, 64, 52, INK); ell(d, x, 410, 42, 32, WHITE); ell(d, x + 22, 412, 22, 22, INK)
    thick(d, [(420, 680), (520, 668), (600, 690)], 28)


def face_nervous(d):  # wobbly smile and a sweat drop
    brows(d, [(272, 262), (418, 228)], [(582, 228), (728, 262)]); big_eyes(d, r=(62, 80), pupil=22, ring=20)
    thick(d, [(390, 690), (440, 665), (490, 690), (540, 665), (590, 690), (630, 668)], 24)
    d.polygon([tuple(s(*p)) for p in ((820, 200), (775, 300), (865, 300))], fill=SWEAT); ell(d, 820, 310, 46, 46, SWEAT)


def face_embarrassed(d):
    face_nervous(d)
    for x in (EYE_L - 40, EYE_R + 40): ell(d, x, 555, 85, 45, BLUSH)


def face_determined(d):
    brows(d, [(262, 270), (420, 300)], [(590, 300), (748, 270)], w=34); dot_eyes(d, ry=72)
    arc(d, 505, 590, 120, 70, 20, 160, 34)


def face_sleepy(d):
    brows(d, [(276, 270), (410, 270)], [(580, 270), (714, 270)])
    for x in (EYE_L, EYE_R): arc(d, x, 380, 60, 50, 20, 160, 28)
    ell(d, 505, 680, 40, 30, INK)


RED, PINK, GOLD = (215, 45, 50, 255), (240, 70, 120, 255), (255, 200, 40, 255)


def heart(d, cx, cy, r, fill):
    ell(d, cx - r * 0.5, cy - r * 0.2, r * 0.55, r * 0.55, fill); ell(d, cx + r * 0.5, cy - r * 0.2, r * 0.55, r * 0.55, fill)
    d.polygon([tuple(s(*p)) for p in ((cx - r * 1.02, cy - r * 0.05), (cx + r * 1.02, cy - r * 0.05), (cx, cy + r * 1.05))], fill=fill)


def star(d, cx, cy, r, fill, rot=-90):
    pts = [(cx + (r if i % 2 == 0 else r * 0.45) * math.cos(math.radians(rot + i * 36)),
            cy + (r if i % 2 == 0 else r * 0.45) * math.sin(math.radians(rot + i * 36))) for i in range(10)]
    d.polygon([tuple(s(*p)) for p in pts], fill=fill)


def face_laugh(d):  # squeezed > < eyes, huge open mouth, tears of joy
    brows(d, [(276, 230), (410, 215)], [(580, 215), (714, 230)])
    thick(d, [(EYE_L - 55, 360), (EYE_L + 45, 405), (EYE_L - 55, 450)], 30)
    thick(d, [(EYE_R + 55, 360), (EYE_R - 45, 405), (EYE_R + 55, 450)], 30)
    d.chord(s(320, 500, 690, 830), 0, 180, fill=INK); d.chord(s(360, 570, 650, 680), 0, 180, fill=WHITE)
    d.pieslice(s(420, 680, 590, 820), 200, 340, fill=(200, 70, 70, 255))
    for x in (EYE_L - 95, EYE_R + 95): ell(d, x, 470, 26, 38, TEAR)


def face_terrified(d):  # tiny pupils, brows high, wobbly open mouth
    brows(d, [(262, 230), (420, 180)], [(590, 180), (748, 230)])
    big_eyes(d, r=(100, 122), pupil=14, ring=22)
    d.polygon([tuple(s(*p)) for p in ((395, 650), (440, 630), (480, 655), (525, 630), (565, 655), (610, 632), (615, 760), (390, 760))], fill=INK)
    d.polygon([tuple(s(*p)) for p in ((825, 210), (780, 310), (870, 310))], fill=SWEAT); ell(d, 825, 320, 46, 46, SWEAT)


def face_scream(d):  # AAAH: huge tall mouth
    brows(d, [(262, 220), (420, 175)], [(590, 175), (748, 220)]); big_eyes(d, r=(96, 120), pupil=20, ring=24)
    ell(d, 505, 740, 105, 170, INK); ell(d, 505, 820, 62, 70, (200, 70, 70, 255))


def face_furious(d):  # beyond angry: white eyes, tiny pupils, shouting mouth
    brows(d, [(240, 230), (440, 345)], [(570, 345), (770, 230)], w=40)
    for x, sx in ((EYE_L, 1), (EYE_R, -1)):
        d.polygon([tuple(s(*p)) for p in ((x - 75, 370 + 25 * sx), (x + 75, 370 - 25 * sx), (x + 70, 470), (x - 70, 470))], fill=INK)
        d.polygon([tuple(s(*p)) for p in ((x - 55, 388 + 20 * sx), (x + 55, 388 - 20 * sx), (x + 50, 452), (x - 50, 452))], fill=WHITE)
        ell(d, x, 425, 14, 14, INK)
    d.rounded_rectangle(s(350, 600, 660, 790), radius=50 * S, fill=INK)
    d.rounded_rectangle(s(375, 615, 635, 660), radius=10 * S, fill=WHITE); d.rounded_rectangle(s(375, 735, 635, 775), radius=10 * S, fill=WHITE)


def face_love(d):
    brows(d, [(276, 240), (410, 230)], [(580, 230), (714, 240)])
    for x in (EYE_L, EYE_R): heart(d, x, 400, 95, RED)
    arc(d, 505, 560, 160, 150, 25, 155, 38)
    for x in (EYE_L - 40, EYE_R + 40): ell(d, x, 560, 85, 45, BLUSH)


def face_starstruck(d):
    brows(d, [(276, 220), (410, 205)], [(580, 205), (714, 220)])
    for x in (EYE_L, EYE_R): star(d, x, 405, 115, GOLD); star(d, x, 405, 60, WHITE)
    d.chord(s(355, 540, 655, 760), 0, 180, fill=INK); d.pieslice(s(430, 650, 580, 750), 200, 340, fill=(200, 70, 70, 255))


def face_dizzy(d):  # spiral eyes, wavy mouth
    for x in (EYE_L, EYE_R):
        pts = [(x + (6 + t * 2.4) * math.cos(t * 0.35), 405 + (6 + t * 2.4) * math.sin(t * 0.35)) for t in range(0, 40)]
        thick(d, pts, 18)
    thick(d, [(400, 690), (450, 665), (500, 690), (550, 665), (600, 690)], 26)


def face_smug(d):  # half-lidded eyes to the side, lopsided smirk
    brows(d, [(276, 255), (410, 262)], [(580, 238), (714, 222)])
    for x in (EYE_L, EYE_R):
        ell(d, x + 15, 420, 52, 55, INK); d.rectangle(s(x - 50, 340, x + 80, 405), fill=(0, 0, 0, 0)); thick(d, [(x - 45, 405), (x + 75, 398)], 24)
    arc(d, 560, 590, 130, 75, 10, 120, 32)


def face_worried(d):  # brows up in the middle, small eyes, little frown
    brows(d, [(272, 275), (420, 215)], [(580, 215), (728, 275)]); dot_eyes(d, ry=62, rx=40)
    arc(d, 505, 730, 90, 55, 205, 335, 28)
    d.polygon([tuple(s(*p)) for p in ((825, 210), (780, 310), (870, 310))], fill=SWEAT); ell(d, 825, 320, 46, 46, SWEAT)


def face_relieved(d):  # eyes closed u u, soft smile
    brows(d, [(276, 262), (410, 245)], [(580, 245), (714, 262)])
    for x in (EYE_L, EYE_R): arc(d, x, 375, 58, 48, 20, 160, 28)
    arc(d, 505, 590, 110, 70, 25, 155, 32)


def face_disgusted(d):  # one squinted eye, tongue out
    brows(d, [(276, 285), (410, 305)], [(580, 230), (714, 250)])
    thick(d, [(EYE_L - 60, 410), (EYE_L + 60, 400)], 28); ell(d, EYE_R, 405, 47, 70, INK)
    thick(d, [(400, 680), (460, 660), (540, 690), (610, 665)], 28)
    d.pieslice(s(470, 640, 570, 760), 0, 180, fill=(225, 90, 110, 255))


def face_confused(d):  # one big eye, one small, squiggly mouth
    brows(d, [(276, 230), (410, 200)], [(580, 290), (714, 300)])
    ell(d, EYE_L, 400, 60, 90, INK); ell(d, EYE_L - 8, 360, 15, 24, WHITE); ell(d, EYE_R, 410, 34, 48, INK)
    thick(d, [(410, 690), (450, 670), (490, 690), (530, 670), (570, 690)], 24)


def face_blank(d):  # dead inside: o_o
    for x in (EYE_L, EYE_R): ell(d, x, 410, 26, 26, INK)
    thick(d, [(440, 680), (570, 680)], 24)


def face_sideeye(d):  # the mom side-eye: heavy lids, pupils hard to one side, flat little smirk
    brows(d, [(270, 300), (420, 292)], [(575, 292), (725, 300)], 24)
    for x in (EYE_L, EYE_R):
        ell(d, x, 410, 70, 44, WHITE); ell(d, x + 34, 418, 26, 26, INK)
        thick(d, [(x - 72, 392), (x + 72, 392)], 26)
    thick(d, [(430, 680), (560, 680), (600, 662)], 22)


def face_chad(d):  # confident meme grin: low brows, narrow eyes, big lopsided smile, chin line
    brows(d, [(270, 300), (420, 315)], [(575, 315), (725, 300)], 34)
    for x in (EYE_L, EYE_R): thick(d, [(x - 50, 400), (x + 50, 395)], 26)
    arc(d, 520, 600, 170, 90, 15, 150, 30); thick(d, [(470, 800), (560, 800)], 18)
    thick(d, [(690, 560), (715, 600)], 16)


def face_raspberry(d):  # pfffbt: eyes squeezed shut, cheeks puffed, tongue out
    for x, sgn in ((EYE_L, 1), (EYE_R, -1)): thick(d, [(x - 55, 370 + 0 * sgn), (x + 15 * sgn, 410), (x - 55 + 110, 370)][:3], 24)
    ell(d, 495, 660, 110, 55, INK); d.pieslice(s(440, 640, 560, 790), 0, 180, fill=(235, 95, 120, 255))
    thick(d, [(500, 690), (500, 760)], 8, (180, 60, 80, 255))
    for x in (250, 750): ell(d, x, 590, 60, 32, BLUSH)


def face_meltdown(d):  # ugly cry: brows up, eyes shut tight, waterfalls of tears, wide wailing mouth
    brows(d, [(270, 300), (420, 230)], [(580, 230), (730, 300)])
    for x in (EYE_L, EYE_R): arc(d, x, 420, 60, 40, 200, 340, 26)
    for x in (EYE_L, EYE_R): d.rectangle(s(x - 22, 430, x + 22, 900), fill=TEAR)
    d.ellipse(s(395, 600, 615, 780), fill=INK); d.ellipse(s(445, 690, 565, 770), fill=(235, 95, 120, 255))


def emote(name, fn, size=512):
    im = Image.new("RGBA", (size * S, size * S), (0, 0, 0, 0)); fn(ImageDraw.Draw(im))
    im.resize((size, size), Image.LANCZOS).save(os.path.join(OUT, f"emote_{name}.png"))


def _stroke_poly(d, pts, fill, w=14):
    d.polygon([tuple(s(*p)) for p in pts], fill=fill, outline=INK, width=w * S)


def emotes():
    """Little cartoon pops shown beside the head (avatar.emote): anger vein, sweat, ! ? hearts zzz stars steam bulb."""
    def anger(d):
        for a in (45, 135, 225, 315):
            cx, cy = 256 + 85 * math.cos(math.radians(a)), 256 + 85 * math.sin(math.radians(a))
            arc(d, cx, cy, 70, 70, a + 120, a + 240, 46, fill=INK); arc(d, cx, cy, 70, 70, a + 125, a + 235, 28, fill=(235, 40, 45, 255))
    def sweat(d):
        _stroke_poly(d, [(256, 60), (170, 300), (342, 300)], (150, 210, 255, 255)); ell(d, 256, 320, 98, 98, INK); ell(d, 256, 320, 86, 86, (150, 210, 255, 255))
        d.polygon([tuple(s(*p)) for p in ((256, 82), (184, 296), (328, 296))], fill=(150, 210, 255, 255)); ell(d, 225, 300, 22, 34, WHITE)
    def exclaim(d):
        _stroke_poly(d, [(200, 40), (312, 40), (290, 330), (222, 330)], (255, 70, 60, 255), 16); ell(d, 256, 420, 52, 52, INK); ell(d, 256, 420, 38, 38, (255, 70, 60, 255))
    def question(d):
        arc(d, 256, 180, 110, 110, 180, 405, 74, fill=INK); arc(d, 256, 180, 110, 110, 182, 403, 48, fill=(70, 150, 255, 255))
        thick(d, [(320, 260), (256, 300), (256, 345)], 74, fill=INK); thick(d, [(320, 262), (256, 302), (256, 343)], 48, fill=(70, 150, 255, 255))
        ell(d, 256, 440, 46, 46, INK); ell(d, 256, 440, 32, 32, (70, 150, 255, 255))
    def hearts(d):
        for cx, cy, r in ((180, 300, 110), (370, 170, 75)): heart(d, cx, cy, r + 12, INK); heart(d, cx, cy, r, RED)
    def zzz(d):
        from PIL import ImageFont
        for i, (x, y, sz) in enumerate(((150, 380, 170), (290, 230, 130), (400, 110, 95))):
            pts = [(x - sz / 2, y - sz / 2), (x + sz / 2, y - sz / 2), (x - sz / 2, y + sz / 2), (x + sz / 2, y + sz / 2)]
            thick(d, pts, int(sz * 0.22) + 14, fill=INK); thick(d, pts, int(sz * 0.22), fill=WHITE)
    def stars(d):
        for cx, cy, r, rot in ((130, 300, 95, -90), (300, 160, 80, -70), (400, 340, 70, -100)): star(d, cx, cy, r + 14, INK, rot); star(d, cx, cy, r, GOLD, rot)
    def steam(d):
        for cx, cy, r in ((170, 330, 95), (300, 250, 110), (390, 130, 80)): ell(d, cx, cy, r + 10, r + 10, (60, 60, 60, 255))
        for cx, cy, r in ((170, 330, 95), (300, 250, 110), (390, 130, 80)): ell(d, cx, cy, r, r, (245, 245, 245, 255))
    def bulb(d):
        ell(d, 256, 210, 150, 150, INK); ell(d, 256, 210, 134, 134, (255, 235, 90, 255))
        d.rectangle(s(196, 330, 316, 420), fill=INK); d.rectangle(s(210, 340, 302, 410), fill=(170, 170, 180, 255))
        for a in range(200, 341, 35): thick(d, [(256 + 175 * math.cos(math.radians(a)), 210 + 175 * math.sin(math.radians(a))),
                                                (256 + 235 * math.cos(math.radians(a)), 210 + 235 * math.sin(math.radians(a)))], 22)
    for k, fn in locals().copy().items():
        if callable(fn): emote(k, fn)


FACES = {k[5:]: v for k, v in globals().items() if k.startswith("face_")}


def main():
    blinks = []
    for name, fn in FACES.items():
        im = canvas(); BLINK["used"] = False; fn(ImageDraw.Draw(im))
        im.resize((1024, 1024), Image.LANCZOS).save(os.path.join(OUT, f"face_{name}.png"))
        if BLINK["used"]:  # same face with the eyes shut, for automatic blinking
            im = canvas(); BLINK["on"] = True; fn(ImageDraw.Draw(im)); BLINK["on"] = False
            im.resize((1024, 1024), Image.LANCZOS).save(os.path.join(OUT, f"face_{name}_blink.png")); blinks.append(name)
    emotes()
    print("faces:", ", ".join(FACES)); print("blink variants:", ", ".join(blinks))


if __name__ == "__main__":
    main()
