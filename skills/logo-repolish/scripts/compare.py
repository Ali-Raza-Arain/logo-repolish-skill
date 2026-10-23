# logo-repolish, (c) 2026 Ali Raza, MIT License. https://github.com/ali-raza-arain/logo-repolish-skill
"""Overlay check: renders the vector in the source image's own pixel frame and compares it with the artwork.

Writes <out>-diff.png (grey where both agree, red where the artwork has ink the vector lacks, blue where the vector
adds ink) and <out>-zoom.png (the vector over the artwork at the worst spots, vector on top, artwork below).
A faithful single-colour trace differs on roughly 1 to 2% of the ink pixels, almost all on antialiased edges.

Usage: python compare.py source.png logo.svg out-prefix
"""
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import Renderer  # noqa: E402

src_path, svg_path, prefix = sys.argv[1:4]
src = Image.open(src_path).convert('RGBA')
W0, H0 = src.size
S = max(1, min(3, 3000 // max(W0, H0)))                 # compare at up to 3x for edge detail
svg = Path(svg_path).read_text()
full = re.sub(r'viewBox="[^"]*"', f'viewBox="0 0 {W0} {H0}"', svg, count=1)

with Renderer() as r:
    vec = r.png(full, W0 * S, H0 * S, transparent=True)
va = np.asarray(vec)[..., 3] > 127

s = np.asarray(src.resize((W0 * S, H0 * S), Image.LANCZOS)).astype(np.float32)
if s[..., 3].min() < 250:
    sa = s[..., 3] > 127
else:
    rgb = s[..., :3]
    border = np.concatenate([rgb[0], rgb[-1], rgb[:, 0], rgb[:, -1]])
    bg = np.median(border, 0)
    d = np.linalg.norm(rgb - bg, axis=-1)
    sa = d > max(40.0, 0.5 * np.percentile(d, 99.5))

missing, added = sa & ~va, va & ~sa
ink = max(int(sa.sum()), 1)
diff = np.full((*sa.shape, 3), 255, np.uint8)
diff[sa & va] = (200, 200, 200)
diff[missing] = (230, 0, 0)
diff[added] = (0, 90, 230)
Image.fromarray(diff).save(f'{prefix}-diff.png')

# The worst spots: mismatch that is thicker than an antialiased edge.
bad = ndimage.binary_opening(missing | added, iterations=max(1, S))
dens = ndimage.uniform_filter(bad.astype(np.float32), size=60 * S)
spots = []
work = dens.copy()
for _ in range(6):
    y, x = np.unravel_index(np.argmax(work), work.shape)
    if work[y, x] <= 0:
        break
    spots.append((y, x))
    work[max(0, y - 120 * S):y + 120 * S, max(0, x - 120 * S):x + 120 * S] = 0
if not spots:
    spots = [(H0 * S // 2, W0 * S // 2)]
half = 50 * S
tile = 240
vec_rgb = Image.new('RGB', vec.size, (255, 255, 255))
vec_rgb.paste(vec, mask=vec.split()[3])
src_rgb = Image.alpha_composite(Image.new('RGBA', (W0 * S, H0 * S), (255, 255, 255, 255)),
                                src.resize((W0 * S, H0 * S), Image.LANCZOS)).convert('RGB')
sheet = Image.new('RGB', (len(spots) * (tile + 8) + 8, 2 * tile + 24), (128, 128, 128))
for i, (y, x) in enumerate(spots):
    box = (max(0, x - half), max(0, y - half), min(W0 * S, x + half), min(H0 * S, y + half))
    sheet.paste(vec_rgb.crop(box).resize((tile, tile), Image.LANCZOS), (8 + i * (tile + 8), 8))
    sheet.paste(src_rgb.crop(box).resize((tile, tile), Image.LANCZOS), (8 + i * (tile + 8), 16 + tile))
sheet.save(f'{prefix}-zoom.png')

print(f'ink pixels: {ink}; missing {missing.sum() / ink * 100:.2f}%, added {added.sum() / ink * 100:.2f}% '
      f'(antialiased edges account for about 1 to 2%)')
print(f'wrote {prefix}-diff.png and {prefix}-zoom.png (top row vector, bottom row artwork)')
