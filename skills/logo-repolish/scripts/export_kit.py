# logo-repolish, (c) 2026 Ali Raza, MIT License. https://github.com/ali-raza-arain/logo-repolish-skill
"""Logo kit from a master vector: every format and theme a brand normally needs.

The logo's own colours are never changed. Themes change only the background. The one-colour white and black
versions are the standard exception, for uses that allow a single colour (embossing, stamps, single-colour print);
they are clearly named as such.

Output (in --out, which must be new or empty):
  svg/  <name>.svg (transparent), <name>-white.svg, <name>-black.svg, <name>-on-light.svg, <name>-on-dark.svg
  pdf/  the same, as vector PDF for print
  png/transparent/  256 to 4096 px tall, for each colour version
  png/light/, png/dark/, jpg/  square, 512 to 4096 px
  png/one-colour/  white on dark and black on light
  ico/favicon.ico  16 to 256 px
  preview.png

Usage: python export_kit.py logo.svg --out kit/logo-2d --name brand-logo [--dark #03070d] [--light #ffffff]
"""
import argparse
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import Renderer, contrast, load_mark, safe_output_dir, save_image, svg_doc  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('svg')
ap.add_argument('--out', required=True)
ap.add_argument('--name', default='logo')
ap.add_argument('--dark', default='#03070d', help='dark theme background')
ap.add_argument('--light', default='#ffffff', help='light theme background')
ap.add_argument('--mono-light', default='#f5f5f5', help='one-colour light ink')
ap.add_argument('--mono-dark', default='#03070d', help='one-colour dark ink')
ap.add_argument('--margin', type=float, default=0.12, help='space around the logo on square versions, per side')
ap.add_argument('--force', action='store_true')
args = ap.parse_args()

mark = load_mark(args.svg)
OUT = safe_output_dir(args.out, args.force)
N = args.name
for c in mark.colors:
    for bg, label in ((args.dark, 'dark'), (args.light, 'light')):
        cr = contrast(c, bg)
        if cr < 3:
            print(f'warning: {c} on the {label} background {bg} has contrast {cr:.1f}:1 (under 3:1, weak for a logo)')


def doc(fill=None, bg=None, square=False):
    x, y, w, h = mark.x, mark.y, mark.w, mark.h
    if square:
        side = max(w, h) * (1 + 2 * args.margin)
        x, y, w, h = x + w / 2 - side / 2, y + h / 2 - side / 2, side, side
    rect = f'<rect x="{x:.3f}" y="{y:.3f}" width="{w:.3f}" height="{h:.3f}" fill="{bg}"/>' if bg else ''
    return svg_doc((x, y, w, h), rect + mark.markup(fill), N), w / h


versions = {'': None, '-white': args.mono_light, '-black': args.mono_dark}
with Renderer() as r:
    for suffix, fill in versions.items():
        text, ratio = doc(fill)
        (OUT / 'svg').mkdir(parents=True, exist_ok=True)
        (OUT / 'svg' / f'{N}{suffix}.svg').write_text(text)
        r.pdf(text, 600 * ratio, 600, OUT / 'pdf' / f'{N}{suffix}.pdf')
        for hpx in (256, 512, 1024, 2048, 4096):
            save_image(r.png(text, hpx * ratio, hpx, True), OUT / 'png' / 'transparent' / f'{N}{suffix}-{hpx}h.png')
    for theme, bg in (('light', args.light), ('dark', args.dark)):
        text, _ = doc(None, bg, square=True)
        (OUT / 'svg' / f'{N}-on-{theme}.svg').write_text(text)
        r.pdf(text, 600, 600, OUT / 'pdf' / f'{N}-on-{theme}.pdf')
        for size in (512, 1024, 2048, 4096):
            img = r.png(text, size, size, False)
            save_image(img, OUT / 'png' / theme / f'{N}-on-{theme}-{size}.png')
            save_image(img, OUT / 'jpg' / f'{N}-on-{theme}-{size}.jpg')
    for label, fill, bg in (('white-on-dark', args.mono_light, args.dark), ('black-on-light', args.mono_dark, args.light)):
        text, _ = doc(fill, bg, square=True)
        img = r.png(text, 2048, 2048, False)
        save_image(img, OUT / 'png' / 'one-colour' / f'{N}-{label}-2048.png')
        save_image(img, OUT / 'jpg' / f'{N}-{label}-2048.jpg')
    # Favicon on the background with the better contrast for the logo colour, each size rendered from the vector.
    main = mark.colors[0]
    ico_bg = args.dark if contrast(main, args.dark) >= contrast(main, args.light) else args.light
    text, _ = doc(None, ico_bg, square=True)
    icons = [r.png(text, s, s, False).convert('RGBA') for s in (16, 32, 48, 64, 128, 256)]
    (OUT / 'ico').mkdir(parents=True, exist_ok=True)
    icons[-1].save(OUT / 'ico' / 'favicon.ico', sizes=[(i.width, i.height) for i in icons], append_images=icons[:-1])

tiles = [Image.open(OUT / 'png' / t / f'{N}-on-{t}-1024.png').convert('RGB').resize((600, 600), Image.LANCZOS) for t in ('light', 'dark')]
tiles += [Image.open(OUT / 'png' / 'one-colour' / f'{N}-{n}-2048.png').convert('RGB').resize((600, 600), Image.LANCZOS)
          for n in ('white-on-dark', 'black-on-light')]
sheet = Image.new('RGB', (1210, 1210), (150, 150, 150))
for i, t in enumerate(tiles):
    sheet.paste(t, ((i % 2) * 610, (i // 2) * 610))
sheet.save(OUT / 'preview.png')
print(f'wrote {sum(1 for _ in OUT.rglob("*") if _.is_file())} files to {OUT}; open preview.png to check')
