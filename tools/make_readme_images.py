# logo-repolish, (c) 2026 Ali Raza, MIT License. https://github.com/ali-raza-arain/logo-repolish-skill
"""Rebuilds the images in docs/images and the demo files in examples/ from a smoke test run.

  python tests/smoke_test.py --keep /tmp/lr-run
  python tools/make_readme_images.py /tmp/lr-run

Everything shown comes from the made-up demo logo, never from a real brand.
"""
import shutil
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'skills' / 'logo-repolish' / 'scripts'))
from common import DEFAULT_FONT, Renderer  # noqa: E402

run = Path(sys.argv[1])
IMG = ROOT / 'docs' / 'images'
IMG.mkdir(parents=True, exist_ok=True)
font = ImageFont.truetype(str(DEFAULT_FONT), 22)


def fit(src, width, out):
    img = Image.open(run / src).convert('RGB')
    if img.width > width:
        img = img.resize((width, round(img.height * width / img.width)), Image.LANCZOS)
    img.save(IMG / out, optimize=True)


def labelled(tiles, out, pad=16):
    """Tiles side by side with a caption under each."""
    w = sum(t.width for t, _ in tiles) + pad * (len(tiles) + 1)
    h = max(t.height for t, _ in tiles) + 2 * pad + 34
    sheet = Image.new('RGB', (w, h), (236, 236, 236))
    d = ImageDraw.Draw(sheet)
    x = pad
    for t, caption in tiles:
        sheet.paste(t, (x, pad))
        d.text((x, pad + t.height + 8), caption, fill=(30, 30, 30), font=font)
        x += t.width + pad
    sheet.save(IMG / out, optimize=True)


# Before and after: the top corner of the demo mark, enlarged 5x, source pixels against the vector.
x0, y0, cw, ch, k = 442, 92, 140, 112, 5
src = Image.open(run / 'demo-logo.png').convert('RGB').crop((x0, y0, x0 + cw, y0 + ch)).resize((cw * k, ch * k), Image.NEAREST)
svg = (run / 'demo-logo.svg').read_text()
svg = svg.replace(svg[svg.index('viewBox="'):svg.index('"', svg.index('viewBox="') + 9) + 1], f'viewBox="{x0} {y0} {cw} {ch}"', 1)
with Renderer() as r:
    vec = r.png(svg, cw * k, ch * k, False, background='#ffffff')
labelled([(src, 'Source PNG, enlarged: staircase edges'), (vec, 'Vector: exact 45 degree lines, sharp corner')], 'before-after.png')

fit('check-diff.png', 520, 'compare-diff.png')
fit('audit/small-sizes.png', 900, 'small-sizes.png')
fit('kit/preview.png', 640, 'kit-preview.png')
fit('lockup/preview.png', 1000, 'lockups.png')
fit('profiles/preview-all.png', 1000, 'profiles.png')
fit('covers/cover-linkedin-company-1128x191.png', 1128, 'cover-linkedin-company.png')
fit('covers/cover-x-guides.png', 1000, 'cover-x-guides.png')

(ROOT / 'examples').mkdir(exist_ok=True)
for f in ('demo-logo.png', 'demo-logo.svg'):
    shutil.copy2(run / f, ROOT / 'examples' / f)
shutil.copy2(run / 'audit' / 'audit.md', ROOT / 'examples' / 'demo-audit.md')
print(f'updated {IMG} and examples/')
