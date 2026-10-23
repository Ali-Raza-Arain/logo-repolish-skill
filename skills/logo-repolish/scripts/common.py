# logo-repolish, (c) 2026 Ali Raza, MIT License. https://github.com/ali-raza-arain/logo-repolish-skill
"""Shared helpers for the logo-repolish scripts: reading a mark SVG, placing it, rendering SVG to PNG/PDF with
headless Chromium, colour maths, and setting a wordmark as vector outlines.

The mark SVGs these scripts read are the ones vectorize.py writes: a viewBox in source-pixel units and one or more
<path fill="..." d="..."> elements (fill on the path itself, even-odd holes). Any simple path-only SVG works too.
"""
from __future__ import annotations

import os
import re
import shutil
from io import BytesIO
from pathlib import Path

from PIL import Image

Image.MAX_IMAGE_PIXELS = None
SKILL_DIR = Path(__file__).resolve().parent.parent
DEFAULT_FONT = SKILL_DIR / 'assets' / 'fonts' / 'InstrumentSans-Variable-latin.ttf'


# ---------------------------------------------------------------- marks

class Mark:
    """A logo mark: its viewBox and its filled paths, in the SVG's own units."""

    def __init__(self, x, y, w, h, paths):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.paths = paths                      # list of (fill, d)

    @property
    def aspect(self):
        return self.w / self.h

    @property
    def colors(self):
        seen = []
        for fill, _ in self.paths:
            if fill not in seen:
                seen.append(fill)
        return seen

    def markup(self, fill=None):
        """The paths, optionally all in one colour (for one-colour and palette versions)."""
        return ''.join(f'<path fill="{fill or f}" fill-rule="evenodd" d="{d}"/>' for f, d in self.paths)

    def placed(self, cx, cy, height, fill=None):
        """The mark centred on (cx, cy) at a given height, as an SVG group."""
        s = height / self.h
        tx, ty = cx - (self.x + self.w / 2) * s, cy - (self.y + self.h / 2) * s
        return f'<g transform="translate({tx:.3f} {ty:.3f}) scale({s:.6f})">{self.markup(fill)}</g>'

    def at(self, left, top, height, fill=None):
        """The mark with its top-left corner at (left, top)."""
        s = height / self.h
        return f'<g transform="translate({left - self.x * s:.3f} {top - self.y * s:.3f}) scale({s:.6f})">{self.markup(fill)}</g>'

    @property
    def half_diagonal(self):
        """Distance from the centre to a bbox corner, in mark units: what must fit inside a circular crop."""
        return ((self.w / 2) ** 2 + (self.h / 2) ** 2) ** 0.5


def load_mark(path) -> Mark:
    text = Path(path).read_text()
    vb = re.search(r'viewBox="([^"]+)"', text)
    if not vb:
        raise SystemExit(f'{path}: no viewBox')
    x, y, w, h = [float(v) for v in vb.group(1).replace(',', ' ').split()]
    group_fill = re.search(r'<g\b[^>]*\sfill="([^"]+)"', text)
    paths = []
    for m in re.finditer(r'<path\b([^>]*?)/?>', text, re.S):
        attrs = m.group(1)
        d = re.search(r'\sd="([^"]+)"', attrs, re.S)
        if not d:
            continue
        fill = re.search(r'\sfill="([^"]+)"', attrs)
        paths.append((fill.group(1) if fill else (group_fill.group(1) if group_fill else '#000000'), d.group(1)))
    if not paths:
        raise SystemExit(f'{path}: no <path> elements found')
    return Mark(x, y, w, h, paths)


def svg_doc(view, body, title='Logo'):
    if isinstance(view, (tuple, list)):
        view = ' '.join(f'{v:.3f}'.rstrip('0').rstrip('.') for v in view)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{view}"><title>{title}</title>{body}</svg>\n')


# ---------------------------------------------------------------- colour

def hex_to_rgb(h):
    h = h.lstrip('#')
    if len(h) == 3:
        h = ''.join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    return '#%02x%02x%02x' % tuple(int(round(c)) for c in rgb)


def luminance(h):
    c = [v / 255 for v in hex_to_rgb(h)]
    c = [v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4 for v in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def contrast(a, b):
    la, lb = sorted([luminance(a), luminance(b)], reverse=True)
    return (la + 0.05) / (lb + 0.05)


# ---------------------------------------------------------------- rendering

def _chrome_executable():
    for name in ('google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser'):
        p = shutil.which(name)
        if p:
            return p
    return None


class Renderer:
    """Headless Chromium for exact SVG rendering (PNG with or without transparency, and vector PDF)."""

    def __enter__(self):
        from playwright.sync_api import sync_playwright
        self._pw = sync_playwright().start()
        try:
            self._browser = self._pw.chromium.launch()
        except Exception:
            exe = _chrome_executable()
            if not exe:
                raise SystemExit('No Chromium found. Run scripts/setup_env.sh, or install Google Chrome.')
            self._browser = self._pw.chromium.launch(executable_path=exe)
        self.page = self._browser.new_page()
        return self

    def __exit__(self, *exc):
        self._browser.close()
        self._pw.stop()

    def png(self, svg_text, w, h, transparent=True, background='transparent'):
        w, h = int(round(w)), int(round(h))
        self.page.set_viewport_size({'width': w, 'height': h})
        self.page.set_content(f'<html><body style="margin:0;background:{background}">'
                              + svg_text.replace('<svg ', f'<svg width="{w}" height="{h}" ', 1) + '</body></html>')
        self.page.wait_for_timeout(100)
        shot = self.page.screenshot(omit_background=transparent, clip={'x': 0, 'y': 0, 'width': w, 'height': h})
        return Image.open(BytesIO(shot)).convert('RGBA' if transparent else 'RGB')

    def html_png(self, html, w, h):
        self.page.set_viewport_size({'width': int(w), 'height': int(h)})
        self.page.set_content(html)
        self.page.wait_for_timeout(300)
        return Image.open(BytesIO(self.page.screenshot(clip={'x': 0, 'y': 0, 'width': int(w), 'height': int(h)}))).convert('RGB')

    def pdf(self, svg_text, w, h, path):
        w, h = int(round(w)), int(round(h))
        self.page.set_content(f'<html><head><style>@page{{size:{w}px {h}px;margin:0}}body{{margin:0}}</style></head><body>'
                              + svg_text.replace('<svg ', f'<svg width="{w}" height="{h}" ', 1) + '</body></html>')
        self.page.wait_for_timeout(100)
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.page.pdf(path=str(path), width=f'{w}px', height=f'{h}px', print_background=True)


def save_image(img, path, jpg_quality=95):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix.lower() in ('.jpg', '.jpeg'):
        img.convert('RGB').save(path, quality=jpg_quality, optimize=True, subsampling=0)
    elif path.suffix.lower() == '.webp':
        img.save(path, quality=95, method=6)
    else:
        img.save(path, optimize=True)


def safe_output_dir(path, force=False):
    """Refuse to write into a non-empty folder unless asked: never overwrite someone's previous results silently."""
    path = Path(path)
    if path.exists() and any(path.iterdir()) and not force:
        raise SystemExit(f'{path} already has files. Choose a new folder, or pass --force after backing it up.')
    path.mkdir(parents=True, exist_ok=True)
    return path


# ---------------------------------------------------------------- wordmark

def wordmark(text, font_path=None, weight=600, width=100, tracking=0.12):
    """Set `text` as vector outlines. Returns (path d, advance width, cap height), in font units with the baseline
    at y=0 and y pointing down. Works with variable or static TTF, OTF and WOFF2 (WOFF2 needs brotli)."""
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.pens.transformPen import TransformPen
    from fontTools.ttLib import TTFont
    font = TTFont(str(font_path or DEFAULT_FONT))
    if 'fvar' in font:
        from fontTools.varLib.instancer import instantiateVariableFont
        axes = {a.axisTag: a for a in font['fvar'].axes}
        loc = {}
        if 'wght' in axes:
            loc['wght'] = min(max(weight, axes['wght'].minValue), axes['wght'].maxValue)
        if 'wdth' in axes:
            loc['wdth'] = min(max(width, axes['wdth'].minValue), axes['wdth'].maxValue)
        font = instantiateVariableFont(font, loc)
    glyphs, cmap, upm = font.getGlyphSet(), font.getBestCmap(), font['head'].unitsPerEm
    cap = getattr(font['OS/2'], 'sCapHeight', 0) or upm * 0.7
    x, cmds = 0.0, []
    for ch in text:
        gname = cmap.get(ord(ch))
        if gname is None:
            raise SystemExit(f'The font has no glyph for {ch!r}')
        pen = SVGPathPen(glyphs)
        glyphs[gname].draw(TransformPen(pen, (1, 0, 0, -1, x, 0)))
        cmds.append(pen.getCommands())
        x += glyphs[gname].width + tracking * upm
    return ' '.join(cmds), x - tracking * upm, cap


def env_note():
    return os.environ.get('PLAYWRIGHT_BROWSERS_PATH', '(default)')
