# logo-repolish, (c) 2026 Ali Raza, MIT License. https://github.com/ali-raza-arain/logo-repolish-skill
"""4x upscale of a raster logo (3D render, metallic or photographic artwork) with Real-ESRGAN, on the CPU.

Only for artwork that cannot be a vector. A flat 2D logo should be rebuilt with vectorize.py instead: an upscaler
guesses detail, a vector is exact at every size.

The upscaler is good at edges and fine detail but invents blotchy texture in flat areas (plain backgrounds, soft
gradients). With --hybrid (the default) the result keeps the upscaled pixels only where the source has detail, and
uses a plain LANCZOS enlargement in flat areas, blended softly so no seam shows. Transparency, if any, is enlarged
with LANCZOS and kept.

Needs the optional upscale setup: scripts/setup_env.sh --upscale (torch CPU, spandrel, the RealESRGAN_x4plus model).
Usage: python upscale.py logo.png logo-4x.png [--model path.pth] [--tile 256] [--no-hybrid] [--threads 8]
A 1024 px image takes a few minutes on a laptop CPU; progress is printed per tile.
"""
import argparse
import os
import time
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

Image.MAX_IMAGE_PIXELS = None
DEFAULT_MODEL = Path(os.environ.get('LOGO_REPOLISH_HOME', Path.home() / '.cache' / 'logo-repolish')) / 'models' / 'RealESRGAN_x4plus.pth'

ap = argparse.ArgumentParser()
ap.add_argument('src')
ap.add_argument('out')
ap.add_argument('--model', default=str(DEFAULT_MODEL))
ap.add_argument('--tile', type=int, default=256, help='smaller uses less memory')
ap.add_argument('--threads', type=int, default=os.cpu_count() or 4)
ap.add_argument('--no-hybrid', action='store_true', help='use the upscaled pixels everywhere')
args = ap.parse_args()

if Path(args.out).exists():
    raise SystemExit(f'{args.out} exists; choose another name so the earlier result is kept')
if not Path(args.model).exists():
    raise SystemExit(f'model not found: {args.model}. Run scripts/setup_env.sh --upscale first.')

import torch  # noqa: E402  (imported late so the checks above work without the optional setup)
from spandrel import ModelLoader  # noqa: E402

torch.set_num_threads(args.threads)
model = ModelLoader().load_from_file(args.model).eval()
S = model.scale

src = Image.open(args.src)
alpha = src.getchannel('A') if 'A' in src.getbands() else None
rgb = np.asarray(src.convert('RGB')).astype(np.float32) / 255
H, W, _ = rgb.shape
result = np.zeros((H * S, W * S, 3), np.float32)
tile, pad = args.tile, 16
tiles = [(y, x) for y in range(0, H, tile) for x in range(0, W, tile)]
t0 = time.time()
with torch.no_grad():
    for i, (y, x) in enumerate(tiles):
        y0, x0 = max(y - pad, 0), max(x - pad, 0)
        y1, x1 = min(y + tile + pad, H), min(x + tile + pad, W)
        inp = torch.from_numpy(rgb[y0:y1, x0:x1].transpose(2, 0, 1).copy()).unsqueeze(0)
        o = model(inp).squeeze(0).clamp(0, 1).numpy().transpose(1, 2, 0)
        oy, ox = (y - y0) * S, (x - x0) * S
        h, w = min(tile, H - y) * S, min(tile, W - x) * S
        result[y * S:y * S + h, x * S:x * S + w] = o[oy:oy + h, ox:ox + w]
        print(f'tile {i + 1}/{len(tiles)}, {time.time() - t0:.0f}s', flush=True)
result *= 255

if not args.no_hybrid:
    # Detail map: local gradient strength in the source, grown and softened, then enlarged to the output size.
    grey = rgb.mean(axis=2)
    grad = np.hypot(ndimage.sobel(grey, 0), ndimage.sobel(grey, 1))
    detail = ndimage.binary_dilation(grad > 0.08, iterations=max(2, W // 170))
    weight = ndimage.gaussian_filter(detail.astype(np.float32), max(1.5, W / 340))
    weight = np.asarray(Image.fromarray((np.clip(weight, 0, 1) * 255).astype(np.uint8)).resize((W * S, H * S), Image.BILINEAR))
    weight = (weight.astype(np.float32) / 255)[..., None]
    smooth = np.asarray(src.convert('RGB').resize((W * S, H * S), Image.LANCZOS)).astype(np.float32)
    result = result * weight + smooth * (1 - weight)
    print(f'hybrid: upscaled pixels on {weight.mean() * 100:.0f}% of the image, plain enlargement elsewhere')

out = Image.fromarray(np.clip(result + 0.5, 0, 255).astype(np.uint8))
if alpha is not None:
    out.putalpha(alpha.resize(out.size, Image.LANCZOS))
Path(args.out).parent.mkdir(parents=True, exist_ok=True)
out.save(args.out)
print(f'wrote {args.out} ({out.width} x {out.height}) in {time.time() - t0:.0f}s')
