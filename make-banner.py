#!/usr/bin/env python3
"""
The banner at the top of the GitHub profile.

Same frame as the share cards on vormaza.com — starfield, wordmark, a
cyan rule, a line of mono caps — but laid out wide and short, because
GitHub renders a README image at about 860px across and anything taller
pushes the actual words below the fold.

Run from this folder:  python3 make-banner.py
Writes banner.png. The image is committed; this is here so the next
change is an edit rather than a redraw.

Needs Pillow and the fonts macOS ships with.
"""

import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 320
OUT = Path(__file__).resolve().parent / 'banner.png'
CYAN = (103, 232, 249)

BOLD = '/System/Library/Fonts/HelveticaNeue.ttc'   # index 1
MONO = '/System/Library/Fonts/Menlo.ttc'           # index 0

font_bold = lambda s: ImageFont.truetype(BOLD, s, index=1)
font_mono = lambda s: ImageFont.truetype(MONO, s, index=0)


def backdrop():
    """Deep space with a wash of cyan behind the mark."""
    img = Image.new('RGB', (W, H), (0, 0, 0))
    px = img.load()
    r, g, b = CYAN
    for y in range(H):
        t = max(0.0, 1 - abs((y / H) - 0.40) * 2) ** 1.8
        for x in range(W):
            u = max(0.0, 1 - abs((x / W) - 0.5) * 1.6)
            k = t * u * 0.085
            px[x, y] = (int(r * k), int(g * k), int(b * k + 3))
    return img


def stars(draw, seed=11):
    """A fixed field, so regenerating does not reshuffle the sky."""
    rnd = random.Random(seed)
    for _ in range(260):
        x, y = rnd.uniform(0, W), rnd.uniform(0, H)
        # Thinned out behind the wordmark, which is where the eye goes.
        if 230 < x < 1050 and 70 < y < 200 and rnd.random() < 0.72:
            continue
        size = rnd.choice([1, 1, 1, 1, 2, 2, 3])
        lum = rnd.randint(70, 255)
        tint = rnd.random()
        if tint < 0.12:
            colour = (int(lum * 0.45), int(lum * 0.68), lum)
        elif tint < 0.18:
            colour = (int(lum * 0.55), int(lum * 0.85), int(lum * 0.95))
        else:
            colour = (lum, lum, int(lum * 0.98))
        if size == 1:
            draw.point((x, y), fill=colour)
        else:
            draw.ellipse([x, y, x + size - 1, y + size - 1], fill=colour)


def wordmark(img, text, top):
    """White at the top, grey by the baseline — a mask with a ramp behind it."""
    f = font_bold(96)
    probe = ImageDraw.Draw(Image.new('L', (1, 1)))
    box = probe.textbbox((0, 0), text, font=f)
    mask = Image.new('L', (box[2] - box[0] + 8, box[3] - box[1] + 8), 0)
    ImageDraw.Draw(mask).text((-box[0] + 4, -box[1] + 4), text, font=f, fill=255)

    ramp = Image.new('RGB', mask.size)
    rp = ramp.load()
    for y in range(mask.size[1]):
        v = int(255 - 78 * ((y / max(1, mask.size[1] - 1)) ** 1.25))
        for x in range(mask.size[0]):
            rp[x, y] = (v, v, min(255, v + 6))

    img.paste(ramp, ((W - mask.size[0]) // 2, top), mask)
    return top + mask.size[1]


def centred(draw, y, text, font, fill):
    draw.text(((W - draw.textbbox((0, 0), text, font=font)[2]) // 2, y), text, font=font, fill=fill)


if __name__ == '__main__':
    img = backdrop()
    draw = ImageDraw.Draw(img)
    stars(draw)

    bottom = wordmark(img, 'vormaza', 74)

    rule_y = bottom + 26
    draw.line([(W // 2 - 110, rule_y), (W // 2 + 110, rule_y)], fill=CYAN, width=2)

    # Letter-spaced per word, not across the whole string: joining every
    # character of the gaps too threw the line out to both edges. Kept to two
    # words and lifted off the background — a long dim strip under a bright
    # wordmark is the first thing that stops being read.
    label = '    '.join('  '.join(word) for word in ('ENGINEERING', 'LEAD'))
    centred(draw, rule_y + 24, label, font_mono(18), (196, 204, 220))

    f = font_mono(19)
    draw.text((64, H - 52), 'vormaza.com', font=f, fill=(226, 232, 244))
    # The offset rather than the country: a PNG cannot tell the time, and
    # GitHub's own profile clock does that job live.
    right = 'GMT+7'
    draw.text((W - 64 - draw.textbbox((0, 0), right, font=f)[2], H - 52), right, font=f, fill=CYAN)

    img.save(OUT, 'PNG', optimize=True)
    print(f'banner.png  {OUT.stat().st_size // 1024} KB  {W}x{H}')
