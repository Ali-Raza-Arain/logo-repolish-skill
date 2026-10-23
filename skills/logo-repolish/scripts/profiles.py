# logo-repolish, (c) 2026 Ali Raza, MIT License. https://github.com/ali-raza-arain/logo-repolish-skill
"""Profile pictures for social platforms from the logo mark.

Every design is circle-safe: the mark's farthest bounding-box corner sits at --reach of the circle's radius
(0.87 by default), so nothing is cut when a platform crops to a circle, and it still fills a rounded square well.

Designs come from assets/palettes.json, or pass your own with --pair BG:FG (FG 'keep' = the logo's own colours).
Also --brand-solid adds the logo colour as a solid background with the mark in white and in near-black.
Each design: 1080 px PNG and JPG, 400 px PNG, SVG. preview-all.png shows each as a circle and a rounded square,
labelled, so the user can choose.

Usage:
  python profiles.py logo.svg --out kit/profiles [--palettes ink-brand,navy-white,...] [--pair "#0e1f38:#ffffff"]
                    [--brand-solid] [--reach 0.87]
"""
import argparse
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import DEFAULT_FONT, SKILL_DIR, Renderer, contrast, load_mark, safe_output_dir, save_image, svg_doc  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('svg')
ap.add_argument('--out', required=True)
ap.add_argument('--name', default='profile')
ap.add_argument('--palettes', help='comma-separated names from assets/palettes.json; default: all')
ap.add_argument('--pair', action='append', default=[], help='extra BG:FG pair, FG may be "keep"')
ap.add_argument('--brand-solid', action='store_true', help='add the logo colour as a background')
ap.add_argument('--reach', type=float, default=0.87)
ap.add_argument('--force', action='store_true')
args = ap.parse_args()

mark = load_mark(args.svg)
OUT = safe_output_dir(args.out, args.force)
pal = json.loads((SKILL_DIR / 'assets' / 'palettes.json').read_text())['palettes']
if args.palettes:
    wanted = args.palettes.split(',')
    pal = [p for p in pal if p['name'] in wanted]
designs = [(p['name'], p['label'], p['bg'], p['fg']) for p in pal]
for i, pair in enumerate(args.pair, 1):
    bg, fg = pair.split(':')
    designs.append((f'custom-{i}', f'{bg} and {fg}', bg, fg))
if args.brand_solid:
    main = mark.colors[0]
    designs += [('brand-solid-white', 'Logo colour and white', main, '#ffffff'),
                ('brand-solid-black', 'Logo colour and near-black', main, '#03070d')]

SIZE = 1000
height = args.reach * (SIZE / 2) / mark.half_diagonal * mark.h
with Renderer() as r:
    for i, (name, label, bg, fg) in enumerate(designs, 1):
        fill = None if fg == 'keep' else fg
        for c in ([fg] if fill else mark.colors):
            if contrast(c, bg) < 3:
                print(f'warning: {name}: {c} on {bg} has contrast {contrast(c, bg):.1f}:1 (under 3:1)')
        text = svg_doc((0, 0, SIZE, SIZE), f'<rect width="{SIZE}" height="{SIZE}" fill="{bg}"/>'
                       + mark.placed(SIZE / 2, SIZE / 2, height, fill), label)
        base = f'{args.name}-{i:02d}-{name}'
        (OUT / f'{base}.svg').write_text(text)
        img = r.png(text, 1080, 1080, False)
        save_image(img, OUT / f'{base}-1080.png')
        save_image(img, OUT / f'{base}-1080.jpg')
        save_image(img.resize((400, 400), Image.LANCZOS), OUT / f'{base}-400.png')
        designs[i - 1] = (base, label, bg, fg)

tile, cols = 240, 5
cw, ch = 2 * tile + 30, tile + 56
rows = (len(designs) + cols - 1) // cols
sheet = Image.new('RGB', (cols * cw + 20, rows * ch + 20), (236, 236, 236))
d = ImageDraw.Draw(sheet)
font = ImageFont.truetype(str(DEFAULT_FONT), 20)
for i, (base, label, _, _) in enumerate(designs):
    x0, y0 = 20 + (i % cols) * cw, 20 + (i // cols) * ch
    img = Image.open(OUT / f'{base}-1080.png').resize((tile, tile), Image.LANCZOS)
    for j, shape in enumerate(('circle', 'rounded')):
        m = Image.new('L', (tile * 4, tile * 4), 0)
        dm = ImageDraw.Draw(m)
        (dm.ellipse if shape == 'circle' else lambda b, fill: dm.rounded_rectangle(b, radius=tile * 4 // 14, fill=fill))(
            (0, 0, tile * 4 - 1, tile * 4 - 1), fill=255)
        sheet.paste(img, (x0 + j * (tile + 10), y0), m.resize((tile, tile), Image.LANCZOS))
    d.text((x0, y0 + tile + 10), f'{i + 1:02d}  {label}', fill=(30, 30, 30), font=font)
sheet.save(OUT / 'preview-all.png')
print(f'wrote {len(designs)} designs to {OUT}; open preview-all.png to choose')
