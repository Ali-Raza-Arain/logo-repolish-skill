# logo-repolish, (c) 2026 Ali Raza, MIT License. https://github.com/ali-raza-arain/logo-repolish-skill
"""Draws the demo logo used in the guide and the smoke test: a made-up flat mark with the typical faults of generated
or hand-exported artwork. Its long straight edges bow by about 1.5 px, and it is antialiased at 1024 px.

The mark: a diamond frame (45 degree lines and sharp corners), a ring in the middle (a true circle with a round
hole), two equal dots and a curved bar (smooth curves). It belongs to no one; use it freely.

Usage: python make_demo_logo.py out.png [--size 1024] [--colour #3a7ca5]
"""
import argparse
import math

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

ap = argparse.ArgumentParser()
ap.add_argument('out')
ap.add_argument('--size', type=int, default=1024)
ap.add_argument('--colour', default='#3a7ca5')
args = ap.parse_args()

S = 4                                   # drawn at 4x, then reduced, which gives real antialiasing
N = args.size * S
c = N / 2
u = N / 1024                            # design units: the mark is laid out on a 1024 grid

mask = Image.new('L', (N, N), 0)
d = ImageDraw.Draw(mask)
diamond = lambda r: [(c, c - r), (c + r, c), (c, c + r), (c - r, c)]
d.polygon(diamond(400 * u), fill=255)
d.polygon(diamond(318 * u), fill=0)
d.ellipse((c - 96 * u, c - 150 * u, c + 96 * u, c + 42 * u), fill=255)        # ring
d.ellipse((c - 46 * u, c - 100 * u, c + 46 * u, c - 8 * u), fill=0)
for dx in (-180, 180):                                                         # two equal dots
    d.ellipse((c + (dx - 30) * u, c - 30 * u, c + (dx + 30) * u, c + 30 * u), fill=255)
d.arc((c - 150 * u, c - 30 * u, c + 150 * u, c + 190 * u), 25, 155, fill=255, width=int(44 * u))   # curved bar

# A gentle bow along every edge, as in generated artwork: a slow sine displacement of about 1.5 px at 1024.
amp = 1.5 * S * args.size / 1024
yy, xx = np.mgrid[0:N, 0:N].astype(np.float32)
warped = ndimage.map_coordinates(np.asarray(mask, np.float32),
                                 [yy + amp * np.sin(2 * math.pi * xx / (N * 0.9)),
                                  xx + amp * np.sin(2 * math.pi * yy / (N * 0.8) + 1.0)], order=1)
alpha = Image.fromarray(np.clip(warped, 0, 255).astype(np.uint8)).resize((args.size, args.size), Image.LANCZOS)

img = Image.new('RGB', alpha.size, (255, 255, 255))
img.paste(Image.new('RGB', alpha.size, args.colour), mask=alpha)
img.save(args.out)
print(f'wrote {args.out}')
