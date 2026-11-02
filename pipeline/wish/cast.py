"""Cast list (all classic R6, same 1.0 scale) + clothing compositing (run with system python before Blender)."""
import os, json
from PIL import Image
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
WK = ROOT + '/work/'
AV, CAT = WK + 'avatar/', WK + 'cat/'
CAST = {
 # Milo = RobloxxKF's real avatar: Pal Hair, Blue and Black Motorcycle Shirt, Black Jeans with Sneakers, Nougat skin, Unique Crown
 'milo':    dict(skin=(204, 142, 105), shirt=AV + 'Shirt_template.png', pants=AV + 'Pants_template.png', hair='63690008', crown=True),
 'tess':    dict(skin=(234, 184, 146), shirt='398634295', pants='398634487', hair='164482468'),
 'lila':    dict(skin=(255, 204, 153), shirt='382537702', pants='382537950', hair='376526888'),
 'dad':     dict(skin=(234, 184, 146), shirt='144076436', pants='144076760', hair='62692030'),
 'kid':     dict(skin=(124, 92, 70),   shirt='382537085', pants='382537806', hair='30332157'),
 'grandma': dict(skin=(255, 204, 153), shirt='gown', pants='gown', hair='13745548', grey=True),
 'woman':   dict(skin=(160, 95, 53),   shirt='607785314', pants='398633812', hair='63688835'),
 'man':     dict(skin=(234, 184, 146), shirt='398635081', pants='382537569', hair='343584973'),
 'man2':    dict(skin=(105, 64, 40),   shirt='382538295', pants='129458426', hair='376548738'),
 'woman2':  dict(skin=(255, 204, 153), shirt='398633584', pants='398635338', hair='332746213'),
 'boy2':    dict(skin=(204, 142, 105), shirt='382537702', pants='398634487', hair='376548738'),
 'boy3':    dict(skin=(234, 184, 146), shirt='398633584', pants='144076760', hair='343584973'),
 'girl2':   dict(skin=(160, 95, 53),   shirt='398635081', pants='382537950', hair='63688835'),
 # --- 'The Voice' cast ---
 'nora':    dict(skin=(255, 204, 153), shirt='398633584', pants='398634487', hair='63688835'),
 'noramom': dict(skin=(255, 204, 153), shirt='382537702', pants='382537569', hair='13745548'),
 'cousin':  dict(skin=(204, 142, 105), shirt='607785314', pants='398633812', hair='376526888'),
 'boynext': dict(skin=(234, 184, 146), shirt='382538295', pants='129458426', hair='376548738'),
 'groom':   dict(skin=(234, 184, 146), shirt='tux', pants='tux', hair='376548738'),
 'bride':   dict(skin=(160, 95, 53),   shirt='dress', pants='dress', hair='332746213'),
 'teacher': dict(skin=(234, 184, 146), shirt='398635081', pants='144076760', hair='62692030'),
 'fireman': dict(skin=(105, 64, 40),   shirt='fire', pants='fire', hair=None),
 'guard':   dict(skin=(234, 184, 146), shirt='lifeguard', pants='lifeguard', hair='30332157'),
 'hero':    dict(skin=(204, 142, 105), shirt='398634295', pants='382537569', hair='332746213'),
}

def tmpl(x):
    if x == 'gown':
        im = Image.new('RGBA', (585, 559), (0, 0, 0, 0)); from PIL import ImageDraw; d = ImageDraw.Draw(im)
        for r in [(231, 8, 359, 72), (231, 74, 359, 202), (427, 74, 555, 202), (165, 74, 229, 202), (361, 74, 425, 202), (231, 204, 359, 268)]:
            d.rectangle(r, fill=(170, 205, 230, 255))
        for i in range(0, 559, 18): d.line((0, i, 585, i), fill=(150, 190, 220, 255), width=3)
        for r in [(19, 355, 281, 400), (308, 355, 570, 400), (217, 289, 281, 353), (308, 289, 372, 353)]: d.rectangle(r, fill=(170, 205, 230, 255))
        return im
    if x in ('tux', 'dress', 'fire', 'lifeguard'):
        from PIL import ImageDraw
        im = Image.new('RGBA', (585, 559), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        body = {'tux': (28, 28, 34), 'dress': (250, 250, 252), 'fire': (196, 150, 60), 'lifeguard': (220, 40, 40)}[x]
        torso = [(231, 8, 359, 72), (231, 74, 359, 202), (427, 74, 555, 202), (165, 74, 229, 202), (361, 74, 425, 202), (231, 204, 359, 268)]
        limbs = [(19, 355, 281, 483), (308, 355, 570, 483), (217, 289, 281, 353), (308, 289, 372, 353), (217, 485, 281, 549), (308, 485, 372, 549)]
        for r in torso: d.rectangle(r, fill=body + (255,))
        if x == 'tux':
            for r in limbs: d.rectangle(r, fill=body + (255,))
            d.polygon([(271, 74), (319, 74), (295, 150)], fill=(255, 255, 255, 255)); d.polygon([(288, 84), (302, 84), (299, 140), (291, 140)], fill=(150, 20, 30, 255))
            for r in [(19, 470, 281, 483), (308, 470, 570, 483), (217, 485, 281, 549), (308, 485, 372, 549)]: d.rectangle(r, fill=(12, 12, 12, 255))
        elif x == 'dress':
            for r in limbs[:2]: d.rectangle((r[0], r[1], r[2], r[1] + 128), fill=body + (255,))
            for r in limbs[2:]: d.rectangle(r, fill=body + (255,))
            for i in range(240, 352, 14): d.ellipse((i, 120, i + 10, 130), fill=(235, 225, 240, 255))
        elif x == 'fire':
            for r in limbs: d.rectangle(r, fill=body + (255,))
            for y0 in (150, 180): d.rectangle((165, y0, 555, y0 + 10), fill=(230, 230, 120, 255))
            for y0 in (400, 440): d.rectangle((19, y0, 570, y0 + 8), fill=(230, 230, 120, 255))
            for r in [(19, 470, 281, 483), (308, 470, 570, 483), (217, 485, 281, 549), (308, 485, 372, 549)]: d.rectangle(r, fill=(30, 30, 30, 255))
        elif x == 'lifeguard':
            d.rectangle((231, 8, 359, 72), fill=(0, 0, 0, 0)); d.text((262, 120), "LIFEGUARD", fill=(255, 255, 255, 255))
            for r in [(19, 355, 281, 410), (308, 355, 570, 410)]: d.rectangle(r, fill=body + (255,))
        return im
    p = x if x.endswith('.png') else CAT + f'{x}_template.png'
    return Image.open(p).convert('RGBA').resize((585, 559))

def composite():
    out = WK + 'chars/'; os.makedirs(out, exist_ok=True)
    for n, c in CAST.items():
        base = Image.new('RGBA', (585, 559), c['skin'] + (255,))
        sh, pa = tmpl(c['shirt']), tmpl(c['pants'])
        pt = Image.new('RGBA', (585, 559), (0, 0, 0, 0)); pt.paste(pa.crop((160, 0, 560, 270)), (160, 0))   # pants only on torso area
        up = base.copy(); up.alpha_composite(pt); up.alpha_composite(sh)   # torso + arms: pants (torso part) under shirt
        lo = base.copy(); lo.alpha_composite(pa)                              # legs
        up.convert('RGB').save(out + f'{n}_upper.png'); lo.convert('RGB').save(out + f'{n}_lower.png')
    json.dump(CAST, open(out + 'cast.json', 'w'), indent=1)
    print('composited', len(CAST))

if __name__ == '__main__': composite()
