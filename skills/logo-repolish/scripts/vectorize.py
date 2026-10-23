# logo-repolish, (c) 2026 Ali Raza, MIT License. https://github.com/ali-raza-arain/logo-repolish-skill
"""Precise vector of a flat (2D) logo from a raster image.

Logos are geometric: straight runs at set angles, smooth curves, true circles. A generic tracer reproduces the
pixels, including their antialiasing staircase and any wobble in the artwork. This rebuilds the geometry instead:
  - edges are read at sub-pixel precision from the antialiased image (worked at up to 4x);
  - stretches running at a multiple of --snap degrees (45 by default) become exact straight lines, fitted over their
    whole length, so long lines that bow by a pixel or two in generated artwork come out dead straight;
  - lines that meet at a corner meet at their exact intersection (the bitmap's rounding of the corner is dropped);
  - everything else is a smooth curve, eased onto the neighbouring lines so there are no steps;
  - circular holes and round dots become exact circles, and circles of nearly the same size are made identical;
  - holes are real even-odd subpaths (no masks), so the SVG opens correctly in Illustrator, Figma, Inkscape and print.
Coordinates stay in the source image's pixel units, so the vector overlays the artwork exactly (see compare.py).

Usage:
  python vectorize.py logo.png logo.svg [--colors 1] [--fill #ad8942] [--snap 45] [--title Brand] [--force]
Use a flat, high-resolution source (800px or more). It does not work on 3D renders or photos.
"""
import argparse
import sys

import numpy as np
from PIL import Image
from scipy import ndimage
from skimage.measure import approximate_polygon, find_contours

sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent))
from common import rgb_to_hex  # noqa: E402

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument('src')
ap.add_argument('out')
ap.add_argument('--colors', type=int, default=1, help='number of logo colours, not counting the background')
ap.add_argument('--fill', help='override the detected logo colour (single-colour logos)')
ap.add_argument('--background', help='background colour, if the corners of the image are not background')
ap.add_argument('--snap', type=float, default=45, help='angle step for straight lines, in degrees (0 disables)')
ap.add_argument('--no-circles', action='store_true', help='keep holes and dots as traced shapes')
ap.add_argument('--title', default='Logo')
ap.add_argument('--force', action='store_true', help='replace the output file if it exists')
args = ap.parse_args()
if __import__('os').path.exists(args.out) and not args.force:
    raise SystemExit(f'{args.out} exists. Choose another name, or pass --force to replace it.')

src = Image.open(args.src)
has_alpha = src.mode in ('RGBA', 'LA') and np.asarray(src.convert('RGBA'))[..., 3].min() < 250
img = np.asarray(src.convert('RGB')).astype(np.float32)
alpha = np.asarray(src.convert('RGBA'))[..., 3].astype(np.float32) / 255 if has_alpha else None
H0, W0 = img.shape[:2]
if max(H0, W0) < 600:
    print(f'warning: the source is only {W0}x{H0}px; precision improves a lot with 800px or more', file=sys.stderr)
UP = int(max(1, min(4, 4096 // max(H0, W0))))

# ---------------------------------------------------------------- colours and coverage
if args.background:
    bg = np.array([int(args.background.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4)], np.float32)
else:
    border = np.concatenate([img[0], img[-1], img[:, 0], img[:, -1]])
    bg = np.median(border, 0)

dist = np.linalg.norm(img - bg, axis=-1)
if has_alpha:
    ink = alpha > 0.9
else:
    ink = dist > max(40.0, 0.6 * np.percentile(dist, 99.5))
pix = img[ink]
if len(pix) == 0:
    raise SystemExit('No logo pixels found: is the background right?')

k = max(1, args.colors)
if k == 1:
    centres = np.median(pix, 0)[None]
else:
    rng = np.random.default_rng(0)
    sample = pix[rng.choice(len(pix), min(len(pix), 60000), replace=False)]
    centres = sample[rng.choice(len(sample), k, replace=False)]
    for _ in range(40):
        lab = ((sample[:, None] - centres[None]) ** 2).sum(-1).argmin(1)
        centres = np.array([np.median(sample[lab == i], 0) if (lab == i).any() else centres[i] for i in range(k)])
if args.fill and k == 1:
    fill_hex = [args.fill]
else:
    fill_hex = [rgb_to_hex(c) for c in centres]


def upsample(a):
    return np.asarray(Image.fromarray(a.astype(np.float32), 'F').resize((W0 * UP, H0 * UP), Image.BICUBIC))


layers = []
if k == 1:
    if has_alpha:
        cov = alpha
    else:
        v = centres[0] - bg
        cov = np.clip(((img - bg) @ v) / max(float(v @ v), 1e-6), 0, 1)
    layers.append(upsample(cov) > 0.5)
else:
    big = np.stack([upsample(img[..., c]) for c in range(3)], -1)
    pal = np.vstack([bg[None], centres])
    nearest = np.zeros(big.shape[:2], np.int16)
    best = np.full(big.shape[:2], np.inf, np.float32)
    for i, c in enumerate(pal):
        dd = ((big - c) ** 2).sum(-1)
        upd = dd < best
        nearest[upd], best[upd] = i, dd[upd]
    layers = [nearest == i + 1 for i in range(k)]
    if has_alpha:
        a = upsample(alpha) > 0.5
        layers = [m & a for m in layers]

# Larger layers go underneath; each lower layer is extended slightly under the layers above it so no hairline gap
# shows where two colours meet.
order = np.argsort([-m.sum() for m in layers])
layers = [layers[i] for i in order]
fill_hex = [fill_hex[i] for i in order]
for i in range(len(layers) - 1):
    above = np.logical_or.reduce(layers[i + 1:])
    grow = ndimage.distance_transform_edt(~layers[i]) <= 0.75 * UP
    layers[i] = layers[i] | (grow & above)


# ---------------------------------------------------------------- geometry helpers
def fit_circle(p):
    A = np.c_[2 * p[:, 1], 2 * p[:, 0], np.ones(len(p))]
    b = (p ** 2).sum(1)
    cx, cy, c = np.linalg.lstsq(A, b, rcond=None)[0]
    r = np.sqrt(max(c + cx ** 2 + cy ** 2, 1e-9))
    res = np.abs(np.hypot(p[:, 0] - cy, p[:, 1] - cx) - r)
    return cy, cx, r, res.max()


def smooth_curve(p, sigma):
    if len(p) < 5:
        return p
    q = np.c_[ndimage.gaussian_filter1d(p[:, 0], sigma, mode='nearest'), ndimage.gaussian_filter1d(p[:, 1], sigma, mode='nearest')]
    q[0], q[-1] = p[0], p[-1]
    return q


def rebuild(contour, snap):
    """Split a closed contour by its local direction into exact lines and smooth curves."""
    c = contour[:-1]
    m = len(c)
    if snap <= 0 or m < 20:
        q = np.c_[ndimage.gaussian_filter1d(c[:, 0], 1.5 * UP, mode='wrap'), ndimage.gaussian_filter1d(c[:, 1], 1.5 * UP, mode='wrap')]
        return approximate_polygon(np.vstack([q, q[:1]]), tolerance=0.08 * UP)[:-1]
    sm = np.c_[ndimage.gaussian_filter1d(c[:, 0], 2.5 * UP, mode='wrap'), ndimage.gaussian_filter1d(c[:, 1], 2.5 * UP, mode='wrap')]
    tang = np.roll(sm, -2, 0) - np.roll(sm, 2, 0)
    theta = np.degrees(np.arctan2(tang[:, 0], tang[:, 1])) % 180
    kk = (np.round(theta / snap) * snap) % 180
    err = np.minimum(np.abs(theta - kk), 180 - np.abs(theta - kk))
    step = np.hypot(*np.diff(np.vstack([c, c[:1]]), axis=0).T)
    key = np.where(err < 3.0, kk, -1)
    if np.all(key == key[0]):
        q = np.c_[ndimage.gaussian_filter1d(c[:, 0], 3, mode='wrap'), ndimage.gaussian_filter1d(c[:, 1], 3, mode='wrap')]
        return approximate_polygon(np.vstack([q, q[:1]]), tolerance=0.1 * UP)[:-1]
    start = int(np.nonzero(key != np.roll(key, 1))[0][0])
    order_ = np.r_[start:m, 0:start]
    runs, cur = [], [order_[0]]
    for i in order_[1:]:
        if key[i] == key[cur[-1]]:
            cur.append(i)
        else:
            runs.append(cur)
            cur = [i]
    runs.append(cur)
    items = []
    for r in runs:
        idx = np.array(r)
        L = step[idx].sum()
        if key[idx[0]] >= 0 and L > 10 * UP:
            ang = np.radians(key[idx[0]])
            u = np.array([np.sin(ang), np.cos(ang)])
            nrm = np.array([u[1], -u[0]])
            core = idx[len(idx) // 8: len(idx) - len(idx) // 8] if len(idx) > 16 else idx
            off = float(np.mean(c[core] @ nrm))
            dev = np.abs(c[core] @ nrm - off)
            # Generated artwork drifts by up to about 1% of a long line's length; a logo needs it straight.
            if dev.max() < max(0.6 * UP, 0.012 * L):
                items.append({'type': 'line', 'n': nrm, 'off': off, 'pts': c[idx]})
                continue
        if items and items[-1]['type'] == 'curve':
            items[-1]['pts'] = np.vstack([items[-1]['pts'], c[idx]])
        else:
            items.append({'type': 'curve', 'pts': c[idx]})
    if len(items) > 1 and items[0]['type'] == 'curve' and items[-1]['type'] == 'curve':
        items[0]['pts'] = np.vstack([items[-1]['pts'], items[0]['pts']])
        items.pop()
    # A short curve between two lines meeting at an angle is the bitmap's rounding of a sharp corner: drop it.
    changed = True
    while changed and len(items) > 2:
        changed = False
        for j in range(len(items)):
            r, prev, nxt = items[j], items[j - 1], items[(j + 1) % len(items)]
            if r['type'] != 'curve' or prev['type'] != 'line' or nxt['type'] != 'line':
                continue
            arc = np.hypot(*np.diff(r['pts'], axis=0).T).sum()
            if arc < 9 * UP and abs(np.linalg.det(np.array([prev['n'], nxt['n']]))) > 0.2:
                items.pop(j)
                changed = True
                break
    out = []
    ni = len(items)

    def proj(p, ln):
        return p - (p @ ln['n'] - ln['off']) * ln['n']

    for j, r in enumerate(items):
        prev, nxt = items[j - 1], items[(j + 1) % ni]
        if r['type'] == 'line':
            if prev['type'] == 'line':
                A = np.array([prev['n'], r['n']])
                if abs(np.linalg.det(A)) > 1e-6:
                    out.append(np.linalg.solve(A, np.array([prev['off'], r['off']])))
                    continue
            out.append(proj(r['pts'][0], r))
        else:
            q = smooth_curve(r['pts'], 2.5)
            seg = np.r_[0, np.cumsum(np.hypot(*np.diff(q, axis=0).T))]
            span = 6 * UP
            if prev['type'] == 'line':
                e = q[0] @ prev['n'] - prev['off']
                q = q - (np.clip(1 - seg / span, 0, 1) * e)[:, None] * prev['n']
            if nxt['type'] == 'line':
                e = q[-1] @ nxt['n'] - nxt['off']
                q = q - (np.clip(1 - (seg[-1] - seg) / span, 0, 1) * e)[:, None] * nxt['n']
            q = approximate_polygon(q, tolerance=0.08 * UP)
            out.extend(q[:-1] if len(q) > 1 else q)
    return np.array(out)


def circles_in(mask):
    """Circular holes (inside the mask) and round dots (separate mask parts) to redraw as exact circles."""
    found = []
    for kind, region in (('hole', ~mask), ('dot', mask)):
        lab, n = ndimage.label(region)
        edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]])))
        objs = ndimage.find_objects(lab)
        for i, sl in enumerate(objs, 1):
            if i in edge or sl is None:
                continue
            hh, ww = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
            if max(hh, ww) > 0.25 * max(mask.shape) or max(hh, ww) < 3 * UP or abs(hh - ww) > 0.15 * max(hh, ww):
                continue
            comp = lab[sl] == i
            cs = find_contours(np.pad(comp.astype(np.float32), 1), 0.5)
            if not cs:
                continue
            p = max(cs, key=len) - 1 + np.array([sl[0].start, sl[1].start])
            cy, cx, r, res = fit_circle(p)
            if res < max(0.6 * UP, 0.06 * r):
                found.append([kind, cy, cx, r])
    # Make circles of nearly the same size identical, as a designer would.
    radii = sorted(f[3] for f in found)
    groups = []
    for r in radii:
        if groups and r - groups[-1][-1] <= max(0.6 * UP, 0.05 * groups[-1][0]):
            groups[-1].append(r)
        else:
            groups.append([r])
    for f in found:
        g = next(g for g in groups if g[0] - 1e-9 <= f[3] <= g[-1] + 1e-9)
        f[3] = float(np.median(g))
    return found, [len(g) for g in groups]


def circle_d(cy, cx, r, s):
    return (f'M{(cx - r) * s:.2f},{cy * s:.2f} a{r * s:.2f},{r * s:.2f} 0 1,0 {2 * r * s:.2f},0 '
            f'a{r * s:.2f},{r * s:.2f} 0 1,0 {-2 * r * s:.2f},0 Z')


# ---------------------------------------------------------------- per layer
s = 1 / UP
body, union = [], np.zeros_like(layers[0])
for li, mask in enumerate(layers):
    union |= mask
    circles, groups = ([], []) if args.no_circles else circles_in(mask)
    if circles:
        print(f'layer {li + 1} ({fill_hex[li]}): {sum(1 for c in circles if c[0] == "hole")} round holes, '
              f'{sum(1 for c in circles if c[0] == "dot")} round dots, size groups {groups}')
    field = ndimage.gaussian_filter(mask.astype(np.float32), 0.6 * UP)
    ds = []
    for contour in find_contours(np.pad(field, 2), 0.5):
        contour = contour - 2
        if len(contour) < 12:
            continue
        cen = contour.mean(0)
        span = np.ptp(contour, axis=0).max()
        is_circle = any(np.hypot(cen[0] - cy, cen[1] - cx) < 0.5 * r and abs(span - 2 * r) < 0.35 * r
                        for _, cy, cx, r in circles)
        if is_circle:
            continue
        pts = rebuild(contour, args.snap) * s
        if len(pts) >= 3:
            ds.append('M' + ' L'.join(f'{x:.2f},{y:.2f}' for y, x in pts) + ' Z')
    ds += [circle_d(cy, cx, r, s) for _, cy, cx, r in circles]
    body.append(f'<path fill="{fill_hex[li]}" fill-rule="evenodd" d="{" ".join(ds)}"/>')

ys, xs = np.nonzero(union)
x0, y0 = xs.min() * s, ys.min() * s
w0, h0 = (xs.max() - xs.min()) * s, (ys.max() - ys.min()) * s
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0:.2f} {y0:.2f} {w0:.2f} {h0:.2f}" '
       f'data-source-size="{W0} {H0}"><title>{args.title}</title>{"".join(body)}</svg>\n')
open(args.out, 'w').write(svg)
print(f'wrote {args.out}: {len(layers)} colour(s) {", ".join(fill_hex)}, background {rgb_to_hex(bg)}, '
      f'{len(svg) // 1024} KB, viewBox {x0:.1f} {y0:.1f} {w0:.1f} {h0:.1f} (source pixels, worked at {UP}x)')
