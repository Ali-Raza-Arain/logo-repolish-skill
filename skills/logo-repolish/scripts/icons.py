# logo-repolish, (c) 2026 Ali Raza, MIT License. https://github.com/ali-raza-arain/logo-repolish-skill
"""Website and app icons from the logo mark: the full set a modern site links in its <head>.

  favicon.svg            scalable tab icon, rounded square (modern browsers)
  favicon-32.png, favicon-48.png, favicon.ico   classic tab icons
  apple-touch-icon.png   180 px, full square (iOS rounds it itself)
  icon-192.png, icon-512.png    for a web app manifest
  icon-maskable-512.png  Android adaptive icon: the mark inside the 80% safe zone
  logo-512.png           square logo for structured data (Organization.logo)

Small tab icons get a slightly larger mark so the shape still reads at 16 to 48 px. If the mark is very detailed,
the audit's small-size sheet will show it; consider a simplified mark for these files.

Usage: python icons.py logo.svg --out public [--bg #03070d] [--radius 0.19] [--fill keep] [--force]
Prints the <link> tags to paste into the page head.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import Renderer, contrast, load_mark, save_image, svg_doc  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('svg')
ap.add_argument('--out', required=True, help='a new folder, or a site public folder (see --force)')
ap.add_argument('--bg', default='#03070d')
ap.add_argument('--radius', type=float, default=0.19, help='corner radius of favicon.svg, as a share of its size')
ap.add_argument('--fill', default='keep', help='"keep" for the logo colours, or one colour')
ap.add_argument('--force', action='store_true', help='replace icon files that already exist (back them up first)')
args = ap.parse_args()

mark = load_mark(args.svg)
fill = None if args.fill == 'keep' else args.fill
OUT = Path(args.out)
OUT.mkdir(parents=True, exist_ok=True)
NAMES = ('favicon.svg', 'favicon-32.png', 'favicon-48.png', 'favicon.ico', 'apple-touch-icon.png', 'icon-192.png',
         'icon-512.png', 'icon-maskable-512.png', 'logo-512.png')
existing = [n for n in NAMES if (OUT / n).exists()]
if existing and not args.force:
    raise SystemExit(f'{OUT} already has {", ".join(existing)}. Back them up, then pass --force to replace them.')
for c in ([fill] if fill else mark.colors):
    if contrast(c, args.bg) < 3:
        print(f'warning: {c} on {args.bg} has contrast {contrast(c, args.bg):.1f}:1, too weak for an icon')


def doc(size, mark_share, radius=0.0):
    """mark_share: the mark's height as a share of the icon, limited so its width also fits."""
    h = min(mark_share * size, mark_share * size / mark.aspect)
    rect = f'<rect width="{size}" height="{size}" rx="{radius * size:.2f}" fill="{args.bg}"/>'
    return svg_doc((0, 0, size, size), rect + mark.placed(size / 2, size / 2, h, fill))


(OUT / 'favicon.svg').write_text(doc(64, 0.72, args.radius))
with Renderer() as r:
    tab = doc(64, 0.78, args.radius)
    save_image(r.png(tab, 32, 32, True), OUT / 'favicon-32.png')
    save_image(r.png(tab, 48, 48, True), OUT / 'favicon-48.png')
    ico = [r.png(tab, s, s, True) for s in (16, 32, 48, 64)]
    ico[-1].save(OUT / 'favicon.ico', sizes=[(i.width, i.height) for i in ico], append_images=ico[:-1])
    save_image(r.png(doc(180, 0.69), 180, 180, False), OUT / 'apple-touch-icon.png')
    for s in (192, 512):
        save_image(r.png(doc(s, 0.69), s, s, False), OUT / f'icon-{s}.png')
    save_image(r.png(doc(512, 0.56), 512, 512, False), OUT / 'icon-maskable-512.png')
    save_image(r.png(doc(512, 0.64), 512, 512, False), OUT / 'logo-512.png')

print(f'wrote icons to {OUT}. Head tags:')
print('''  <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
  <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png" />
  <link rel="icon" type="image/png" sizes="48x48" href="/favicon-48.png" />
  <link rel="apple-touch-icon" href="/apple-touch-icon.png" />''')
print(f'Manifest icons: icon-192.png, icon-512.png, icon-maskable-512.png (purpose "maskable"); theme colour {args.bg}')
