# logo-repolish, (c) 2026 Ali Raza, MIT License. https://github.com/ali-raza-arain/logo-repolish-skill
"""Design-rule audit of a vector logo. Measures what a mark designer checks by eye and writes a short report:

- stroke weights: the width of every part, so uneven strokes stand out;
- gaps: the spacing between shapes, and the spots much tighter than the usual gap;
- circles: holes and dots, and whether same-looking ones really are the same size;
- angles: straight segments that are close to, but not exactly on, the --snap grid (45 degrees by default);
- alignment: centres that almost line up but miss by a small amount (looks like a mistake);
- small sizes: renders at 16 to 128 px, to judge favicon and avatar legibility.

Usage: python audit.py logo.svg out-folder [--snap 45]
Writes out-folder/audit.md, small-sizes.png and tight-gaps.png.
"""
import argparse
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
from skimage.morphology import skeletonize

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import Renderer, load_mark, svg_doc  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('svg')
ap.add_argument('out')
ap.add_argument('--snap', type=float, default=45)
args = ap.parse_args()
out = Path(args.out)
out.mkdir(parents=True, exist_ok=True)

mark = load_mark(args.svg)
REF = 1000.0                                             # report sizes per 1000 units of logo height
H = 2400
S = H / mark.h
W = int(round(mark.w * S))
pad = 40
with Renderer() as r:
    body = mark.at(pad, pad, H, fill='#000')
    img = r.png(svg_doc((0, 0, W + 2 * pad, H + 2 * pad), body), W + 2 * pad, H + 2 * pad, transparent=True)
    small = []
    for px in (16, 24, 32, 48, 64, 128):
        w = max(1, round(px * mark.aspect))
        doc = svg_doc((mark.x, mark.y, mark.w, mark.h), f'<rect x="{mark.x}" y="{mark.y}" width="{mark.w}" height="{mark.h}" fill="#fff"/>' + mark.markup())
        small.append((px, r.png(doc, w, px, transparent=False)))
m = np.asarray(img)[..., 3] > 127
unit = REF / H                                           # report units per rendered pixel
lines = [f'# Logo audit: {Path(args.svg).name}', '',
         f'Sizes are given per 1000 units of logo height (the logo is {mark.w / mark.h * 1000:.0f} units wide).', '']

# ---- holes and dots
hl, hn = ndimage.label(~m)
edge = set(np.unique(np.r_[hl[0], hl[-1], hl[:, 0], hl[:, -1]]))
holes = []
for i in range(1, hn + 1):
    if i in edge:
        continue
    c = hl == i
    a = c.sum()
    if a > (0.2 * H) ** 2:
        continue
    cy, cx = ndimage.center_of_mass(c)
    holes.append((cy, cx, np.sqrt(a / np.pi)))
holes = np.array(holes) if holes else np.zeros((0, 3))
lines.append('## Circles and holes')
if len(holes):
    rr = holes[:, 2] * unit
    lines.append(f'- {len(holes)} enclosed holes. Radius {np.median(rr):.1f}, spread {np.ptp(rr):.2f} '
                 f'({"identical" if np.ptp(rr) < 0.5 else "not identical: make same-looking holes the same size"}).')
else:
    lines.append('- No enclosed holes.')

# ---- stroke widths per part (holes masked out so rings do not skew traces)
body_mask = m.copy()
yy, xx = np.ogrid[:m.shape[0], :m.shape[1]]
for cy, cx, rh in holes:
    body_mask &= ~((yy - cy) ** 2 + (xx - cx) ** 2 <= (rh * 2.3) ** 2)
dt = ndimage.distance_transform_edt(body_mask)
sk = skeletonize(body_mask)
lab, n = ndimage.label(body_mask)
sizes = ndimage.sum(body_mask, lab, range(1, n + 1))
lines += ['', '## Stroke weights', '| Part (bounding box, x0 y0 x1 y1) | Typical width | 10th to 90th percentile |', '| --- | --- | --- |']
weights = []
for i in np.argsort(-sizes)[:16]:
    if sizes[i] < (0.02 * H) ** 2:
        continue
    pts = sk & (lab == i + 1)
    w = 2 * dt[pts] * unit
    w = w[w > 4]
    if len(w) < 10:
        continue
    ys, xs = np.nonzero(lab == i + 1)
    weights.append(np.median(w))
    box = ' '.join(str(int(v * unit)) for v in (xs.min() - pad, ys.min() - pad, xs.max() - pad, ys.max() - pad))
    lines.append(f'| {box} | {np.median(w):.1f} | {np.percentile(w, 10):.1f} to {np.percentile(w, 90):.1f} |')
if weights:
    ws = np.sort(weights)
    tiers = [[ws[0]]]
    for w in ws[1:]:
        (tiers[-1].append(w) if w - tiers[-1][-1] <= 0.08 * tiers[-1][0] else tiers.append([w]))
    lines.append(f'\nWeight tiers: {", ".join(f"{np.median(t):.1f} (x{len(t)})" for t in tiers)}. '
                 'One or two clear tiers read as intentional; several close tiers read as inconsistent.')

# ---- gaps
bdt, (iy, ix) = ndimage.distance_transform_edt(~m, return_indices=True)
# A gap is a skeleton point of the empty space with the mark on both sides: stepping from the nearest edge through
# the point and on by a little more than the same distance meets the mark again. This leaves out the margin around
# the logo, open space, and the spurs a skeleton grows into corners.
yy, xx = np.indices(m.shape)
to_edge = np.minimum.reduce([yy, xx, m.shape[0] - 1 - yy, m.shape[1] - 1 - xx])
sk_bg = skeletonize(~m) & (bdt < to_edge - 2) & (bdt * 2 * unit < 0.12 * REF)
py, px = np.nonzero(sk_bg)
facing = np.zeros(len(py), bool)
for k in (1.15, 1.3, 1.45):
    oy = np.clip(np.round(py + (py - iy[py, px]) * k).astype(int), 0, m.shape[0] - 1)
    ox = np.clip(np.round(px + (px - ix[py, px]) * k).astype(int), 0, m.shape[1] - 1)
    facing |= m[oy, ox]
bsk = np.zeros_like(m)
bsk[py[facing], px[facing]] = True
gw = 2 * bdt * unit
g = gw[bsk]
g = g[g > 2]
lines += ['', '## Gaps']
tight_img = Image.fromarray(np.where(m, 200, 255).astype(np.uint8)).convert('RGB')
if len(g):
    med = np.median(g)
    main = weights[0] if weights else 0.0          # the largest part's stroke weight
    limit = max(0.7 * med, 0.6 * main)
    tight = bsk & (gw > 2) & (gw < limit)
    lines.append(f'- Usual gap {med:.1f}, narrowest {g.min():.1f}. Spots under {limit:.1f} (70% of the usual gap, or 60% of '
                 f'the main stroke weight if that is more): {int(tight.sum())} skeleton pixels, shown in red in '
                 'tight-gaps.png. Tight spots close up first at small sizes and in print.')
else:
    lines.append('- No gaps between parts of the mark.')
    d = ImageDraw.Draw(tight_img)
    for y, x in zip(*np.nonzero(tight)):
        d.point((x, y), fill=(230, 0, 0))
    tight_img = tight_img.resize((tight_img.width // 3, tight_img.height // 3), Image.LANCZOS)
tight_img.save(out / 'tight-gaps.png')

# ---- angles of straight segments (arc subpaths skipped)
lines += ['', '## Angles']
if args.snap > 0:
    total, off = 0, []
    for _, dpath in mark.paths:
        for sub in re.findall(r'M[^MZ]+Z', dpath):
            if re.search(r'[aAcCqQsS]', sub):
                continue
            pts = [tuple(map(float, p.split(','))) for p in re.findall(r'(-?[\d.]+,-?[\d.]+)', sub)]
            for (x1, y1), (x2, y2) in zip(pts, pts[1:] + pts[:1]):
                L = np.hypot(x2 - x1, y2 - y1)
                if L / mark.h * REF < 25:
                    continue
                total += 1
                a = np.degrees(np.arctan2(y2 - y1, x2 - x1)) % 180
                dev = min(abs(a - k) for k in np.arange(0, 180.1, args.snap))
                if 0.05 < dev < 5:
                    off.append((round(a, 2), round(dev, 2)))
    lines.append(f'- {total} straight segments over 25 units; {len(off)} are close to a {args.snap:g} degree '
                 f'multiple without being on it{": " + str(off[:8]) if off else ""}.')
else:
    lines.append('- Not checked (--snap 0).')

# ---- near-alignment of circle centres
lines += ['', '## Alignment']
near = []
for i in range(len(holes)):
    for j in range(i + 1, len(holes)):
        for axis, name in ((1, 'x'), (0, 'y')):
            dd = abs(holes[i][axis] - holes[j][axis]) * unit
            if 1.0 < dd < 12:
                near.append((name, round(dd, 1)))
lines.append(f'- Circle centres that almost share a row or column (1 to 12 units apart): {len(near)}'
             + (f', for example {near[:6]}. Align them exactly, or offset them clearly.' if near else '.'))

# ---- small sizes
tile_w = sum(int(im.width * 4) + 30 for _, im in small) + 30
sheet = Image.new('RGB', (tile_w, 128 * 4 + 60), (230, 230, 230))
x = 30
d = ImageDraw.Draw(sheet)
for px, im in small:
    big = im.resize((im.width * 4, im.height * 4), Image.NEAREST)
    sheet.paste(big, (x, 40))
    d.text((x, 12), f'{px}px', fill=(0, 0, 0))
    x += big.width + 30
sheet.save(out / 'small-sizes.png')
lines += ['', '## Small sizes',
          '- See small-sizes.png (each size shown 4x, pixels visible). If the detail merges below 48 px, plan a '
          'simplified mark for favicons and app icons rather than shrinking the full logo.']

(out / 'audit.md').write_text('\n'.join(lines) + '\n')
print('\n'.join(lines))
print(f'\nwrote {out}/audit.md, small-sizes.png, tight-gaps.png')
