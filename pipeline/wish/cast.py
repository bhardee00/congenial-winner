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
}

def tmpl(x):
    if x == 'gown':
        im = Image.new('RGBA', (585, 559), (0, 0, 0, 0)); from PIL import ImageDraw; d = ImageDraw.Draw(im)
        for r in [(231, 8, 359, 72), (231, 74, 359, 202), (427, 74, 555, 202), (165, 74, 229, 202), (361, 74, 425, 202), (231, 204, 359, 268)]:
            d.rectangle(r, fill=(170, 205, 230, 255))
        for i in range(0, 559, 18): d.line((0, i, 585, i), fill=(150, 190, 220, 255), width=3)
        for r in [(19, 355, 281, 400), (308, 355, 570, 400), (217, 289, 281, 353), (308, 289, 372, 353)]: d.rectangle(r, fill=(170, 205, 230, 255))
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
