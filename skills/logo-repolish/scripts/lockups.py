# logo-repolish, (c) 2026 Ali Raza, MIT License. https://github.com/ali-raza-arain/logo-repolish-skill
"""Lockups: the logo mark with the brand name, side by side (horizontal) and name-under-mark (stacked).
The name is set as vector outlines from a real font, so SVG and PDF are pure vector at any size.

Variants: on-dark, on-light (with background), and transparent for dark or light backgrounds (name colour changes,
the mark never does). Formats: SVG, PDF, PNG (2400 px wide horizontal, 1600 px stacked), JPG for the backed ones.

Usage:
  python lockups.py logo.svg --text BRAND --out kit/lockup [--font font.ttf] [--weight 600] [--tracking 0.14]
                    [--dark #03070d] [--light #ffffff] [--name brand-lockup]
The default font is Instrument Sans (bundled, SIL Open Font License). Pass the brand's own font when it has one.
"""
import argparse
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import Renderer, hex_to_rgb, load_mark, safe_output_dir, save_image, svg_doc, wordmark  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('svg')
ap.add_argument('--text', required=True)
ap.add_argument('--out', required=True)
ap.add_argument('--name', default='lockup')
ap.add_argument('--font')
ap.add_argument('--weight', type=float, default=600)
ap.add_argument('--tracking', type=float, default=0.14, help='letter spacing in em; 0.1 to 0.16 suits caps')
ap.add_argument('--dark', default='#03070d')
ap.add_argument('--light', default='#ffffff')
ap.add_argument('--text-on-dark', default='#f5f5f5')
ap.add_argument('--text-on-light', default='#03070d')
ap.add_argument('--force', action='store_true')
args = ap.parse_args()

mark = load_mark(args.svg)
OUT = safe_output_dir(args.out, args.force)
WD, WORD_W, CAP = wordmark(args.text, args.font, args.weight, tracking=args.tracking)


def lockup(kind, text_fill, bg=None):
    L = 1000.0
    mw = mark.aspect * L
    if kind == 'horizontal':
        cap = 0.36 * L; ws = cap / CAP; gap = 0.30 * L
        Wt, Ht = mw + gap + WORD_W * ws, L
        body = mark.at(0, 0, L) + f'<path fill="{text_fill}" transform="translate({mw + gap:.2f} {L / 2 + cap / 2:.2f}) scale({ws:.5f})" d="{WD}"/>'
    else:
        cap = 0.20 * L; ws = cap / CAP; ww = WORD_W * ws; gap = 0.20 * L
        Wt, Ht = max(mw, ww), L + gap + cap
        body = mark.at((Wt - mw) / 2, 0, L) + f'<path fill="{text_fill}" transform="translate({(Wt - ww) / 2:.2f} {Ht:.2f}) scale({ws:.5f})" d="{WD}"/>'
    m = 0.18 * L
    rect = f'<rect x="{-m:.1f}" y="{-m:.1f}" width="{Wt + 2 * m:.1f}" height="{Ht + 2 * m:.1f}" fill="{bg}"/>' if bg else ''
    return svg_doc((-m, -m, Wt + 2 * m, Ht + 2 * m), rect + body, args.text), (Wt + 2 * m) / (Ht + 2 * m)


VARIANTS = [('on-dark', args.text_on_dark, args.dark), ('on-light', args.text_on_light, args.light),
            ('transparent-for-dark-backgrounds', args.text_on_dark, None),
            ('transparent-for-light-backgrounds', args.text_on_light, None)]
tiles = []
with Renderer() as r:
    for kind, width in (('horizontal', 2400), ('stacked', 1600)):
        for vname, text_fill, bg in VARIANTS:
            text, ratio = lockup(kind, text_fill, bg)
            base = f'{args.name}-{kind}-{vname}'
            (OUT / 'svg').mkdir(parents=True, exist_ok=True)
            (OUT / 'svg' / f'{base}.svg').write_text(text)
            r.pdf(text, width / 4, width / 4 / ratio, OUT / 'pdf' / f'{base}.pdf')
            img = r.png(text, width, width / ratio, transparent=bg is None)
            save_image(img, OUT / 'png' / f'{base}-{width}w.png')
            if bg:
                save_image(img, OUT / 'jpg' / f'{base}-{width}w.jpg')
            back = args.dark if 'dark' in vname else args.light
            shown = Image.new('RGBA', img.size, hex_to_rgb(back) + (255,))
            shown.alpha_composite(img.convert('RGBA'))
            tw = 560 if kind == 'horizontal' else 260
            tiles.append(shown.convert('RGB').resize((tw, round(img.height * tw / img.width)), Image.LANCZOS))

rows = [tiles[:4], tiles[4:]]
sheet = Image.new('RGB', (max(sum(t.width + 10 for t in r_) for r_ in rows) + 10,
                          sum(max(t.height for t in r_) + 10 for r_ in rows) + 10), (150, 150, 150))
y = 10
for row in rows:
    x = 10
    for t in row:
        sheet.paste(t, (x, y))
        x += t.width + 10
    y += max(t.height for t in row) + 10
sheet.save(OUT / 'preview.png')
print(f'wrote lockups to {OUT}; open preview.png to check')
