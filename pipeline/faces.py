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


def dot_eyes(d, ry=82, rx=47, shine=True):
    for x in (EYE_L, EYE_R):
        ell(d, x, 400, rx, ry, INK)
        if shine: ell(d, x - 8, 360, 15, 24, WHITE)


def big_eyes(d, r=(78, 106), pupil=38, look=(0, 6), ring=24):
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


FACES = {k[5:]: v for k, v in globals().items() if k.startswith("face_")}


def main():
    for name, fn in FACES.items():
        im = canvas(); fn(ImageDraw.Draw(im))
        im.resize((1024, 1024), Image.LANCZOS).save(os.path.join(OUT, f"face_{name}.png"))
    print("faces:", ", ".join(FACES))


if __name__ == "__main__":
    main()
