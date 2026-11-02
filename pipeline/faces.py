"""Draws classic-Roblox-style face decals (transparent PNG, black strokes) into work/faces/."""
import os
from PIL import Image, ImageDraw
W = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'work', 'faces') + '/'; os.makedirs(W, exist_ok=True)
S = 4; N = 512 * S; K = (22, 20, 20, 255)
def new(): im = Image.new("RGBA", (N, N), (0, 0, 0, 0)); return im, ImageDraw.Draw(im)
def P(*a): return [v * S for v in a]
def eyes(d, h=62, w=30, y=200, dx=62):           # default Smile eyes: plain vertical ovals
    for x in (256 - dx, 256 + dx): d.ellipse(P(x - w / 2, y - h / 2, x + w / 2, y + h / 2), fill=K)
def arc(d, box, a0, a1, wid=12): d.arc(P(*box), a0, a1, fill=K, width=wid * S)
def brow(d, x0, y0, x1, y1, wid=12): d.line(P(x0, y0, x1, y1), fill=K, width=wid * S)
def save(im, n): im.resize((512, 512), Image.LANCZOS).save(W + n + ".png")

im, d = new(); eyes(d); arc(d, (176, 214, 336, 330), 25, 155); save(im, "smile")
im, d = new(); eyes(d, h=58); arc(d, (176, 214, 336, 330), 25, 155); d.ellipse(P(150, 250, 186, 268), fill=(255, 120, 120, 90)); d.ellipse(P(326, 250, 362, 268), fill=(255, 120, 120, 90)); save(im, "happy")
im, d = new(); eyes(d, h=48, y=210); brow(d, 160, 158, 222, 182); brow(d, 352, 158, 290, 182); arc(d, (200, 290, 312, 370), 205, 335); save(im, "angry")
im, d = new(); eyes(d, h=50, y=212); brow(d, 162, 178, 222, 160); brow(d, 350, 178, 290, 160); arc(d, (200, 296, 312, 372), 210, 330); save(im, "sad")
im, d = new(); eyes(d, h=50, y=212); brow(d, 162, 178, 222, 160); brow(d, 350, 178, 290, 160); arc(d, (196, 292, 316, 372), 205, 335)
for x in (194, 318):
    d.ellipse(P(x - 9, 250, x + 9, 290), fill=(90, 170, 255, 235)); d.ellipse(P(x - 7, 300, x + 7, 330), fill=(90, 170, 255, 210))
save(im, "cry")
im, d = new(); arc(d, (164, 186, 224, 226), 200, 340, 11); arc(d, (288, 186, 348, 226), 200, 340, 11); arc(d, (196, 226, 316, 316), 30, 150, 11); save(im, "closed")   # eyes shut, calm
im, d = new(); arc(d, (164, 196, 224, 236), 200, 340, 11); arc(d, (288, 196, 348, 236), 200, 340, 11); arc(d, (206, 300, 306, 346), 210, 330, 10); save(im, "closed_sad")
im, d = new(); eyes(d, h=72, w=36, y=204); d.ellipse(P(232, 292, 280, 352), fill=K); save(im, "shock")
im, d = new(); eyes(d, h=56); brow(d, 166, 150, 222, 160); brow(d, 346, 150, 290, 160); d.line(P(212, 298, 300, 298), fill=K, width=12 * S); save(im, "neutral")
im, d = new(); eyes(d, h=56); brow(d, 166, 160, 222, 144); brow(d, 346, 160, 290, 144); d.line(P(214, 300, 234, 290, 256, 302, 278, 290, 298, 300), fill=K, width=10 * S, joint="curve"); save(im, "worried")
im, d = new(); eyes(d, h=56, dx=58); d.ellipse(P(150 + 10, 172 + 10, 180, 192), fill=(0, 0, 0, 0)); d.ellipse(P(240, 296, 270, 326), fill=K); save(im, "whisper")
im, d = new(); eyes(d); brow(d, 166, 156, 222, 166); brow(d, 346, 156, 290, 166); arc(d, (206, 224, 336, 320), 20, 130); save(im, "smirk")
im, d = new(); eyes(d, h=64); arc(d, (170, 200, 342, 340), 20, 160, 0); d.chord(P(180, 220, 332, 340), 10, 170, fill=K); d.chord(P(196, 228, 316, 300), 10, 170, fill=(255, 255, 255, 255)); save(im, "laugh")
print(sorted(os.listdir(W)))
