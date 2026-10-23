# logo-repolish, (c) 2026 Ali Raza, MIT License. https://github.com/ali-raza-arain/logo-repolish-skill
"""Social cover images (banners) built around the logo mark, for the platforms a company profile needs.

Every platform crops or overlaps its cover differently, so each one has a safe area (where all content stays) and,
where the platform puts the profile picture over the cover, a clear zone. Each design also gets a -guides.png that
shows both, so the user can check placement before uploading.

  linkedin-company   1128 x 191   company logo overlaps the lower left
  linkedin-personal  1584 x 396   profile photo overlaps the lower left
  x                  1500 x 500   profile photo overlaps the lower left; phones trim the top and bottom
  facebook           1640 x 624   phones show only the middle, so content stays in the centre
  youtube            2560 x 1440  only the middle 1546 x 423 shows on every device

Layouts: split (text left, mark right), centered (mark and text side by side, centred), mark (mark only).
The copy comes only from the arguments: headline, subline and url are all optional, nothing is filled in for you.
The url is shown as plain text (no scheme, no bullet).

Usage:
  python covers.py logo.svg --out kit/covers [--platforms linkedin-company,x] [--layout split] [--theme dark]
                   [--headline "..."] [--subline "..."] [--url example.com] [--texture none|grid]
                   [--bg #03070d] [--text #f5f5f5] [--muted #9aa4b2] [--mark-fill keep] [--font font.ttf]
"""
import argparse
import base64
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import DEFAULT_FONT, Renderer, contrast, load_mark, safe_output_dir, save_image, svg_doc  # noqa: E402

# name: (upload size, render scale, safe area (x0, y0, x1, y1) and clear zone as shares of the cover)
PLATFORMS = {
    'linkedin-company': ((1128, 191), 2, (0.28, 0.12, 0.96, 0.88), (0.0, 0.35, 0.25, 1.0)),
    'linkedin-personal': ((1584, 396), 2, (0.30, 0.12, 0.96, 0.88), (0.02, 0.42, 0.27, 1.0)),
    'x': ((1500, 500), 2, (0.24, 0.16, 0.96, 0.84), (0.01, 0.55, 0.20, 1.0)),
    'facebook': ((1640, 624), 1, (0.12, 0.12, 0.88, 0.88), None),
    'youtube': ((2560, 1440), 1, (0.198, 0.353, 0.802, 0.647), None),
}
THEMES = {'dark': ('#03070d', '#f5f5f5', '#9aa4b2'), 'light': ('#f6f4ef', '#03070d', '#5b6470')}

ap = argparse.ArgumentParser()
ap.add_argument('svg')
ap.add_argument('--out', required=True)
ap.add_argument('--name', default='cover')
ap.add_argument('--platforms', default=','.join(PLATFORMS))
ap.add_argument('--layout', choices=('split', 'centered', 'mark'), default='split')
ap.add_argument('--theme', choices=tuple(THEMES), default='dark')
ap.add_argument('--headline', default='')
ap.add_argument('--subline', default='')
ap.add_argument('--url', default='')
ap.add_argument('--texture', choices=('none', 'grid'), default='none')
ap.add_argument('--bg')
ap.add_argument('--text')
ap.add_argument('--muted')
ap.add_argument('--mark-fill', default='keep', help='"keep" for the logo colours, or one colour')
ap.add_argument('--font', help='TTF, OTF or WOFF2; default Instrument Sans (bundled)')
ap.add_argument('--force', action='store_true')
args = ap.parse_args()

mark = load_mark(args.svg)
OUT = safe_output_dir(args.out, args.force)
bg, ink, muted = (args.bg or THEMES[args.theme][0], args.text or THEMES[args.theme][1], args.muted or THEMES[args.theme][2])
fill = None if args.mark_fill == 'keep' else args.mark_fill
for c in ([fill] if fill else mark.colors):
    if contrast(c, bg) < 3:
        print(f'warning: the mark colour {c} on {bg} has contrast {contrast(c, bg):.1f}:1, under 3:1')
url = args.url.removeprefix('https://').removeprefix('http://').rstrip('/')
if args.layout != 'mark' and not (args.headline or args.subline or url):
    print('note: no headline, subline or url given, so the cover shows the mark only')
    args.layout = 'mark'

font_path = Path(args.font) if args.font else DEFAULT_FONT
font_fmt = {'.ttf': 'truetype', '.otf': 'opentype', '.woff2': 'woff2', '.woff': 'woff'}[font_path.suffix.lower()]
FONT_CSS = (f"@font-face{{font-family:Brand;src:url(data:font/{font_path.suffix[1:]};base64,"
            f"{base64.b64encode(font_path.read_bytes()).decode()}) format('{font_fmt}');font-weight:100 900}}")
mark_svg = svg_doc((mark.x, mark.y, mark.w, mark.h), mark.markup(fill)).replace('<svg ', '<svg class="mark" ', 1)
esc = lambda s: s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
copy = ''.join(f'<div class="{cls}">{esc(t)}</div>' for cls, t in (('h', args.headline), ('s', args.subline), ('u', url)) if t)

# Shrinks the copy until it fits its box. Runs only in the local renderer, never on a website.
FIT = """<script>
document.fonts.ready.then(() => {
  const box = document.querySelector('.copy');
  if (!box) return;
  const unit = parseFloat(getComputedStyle(box).fontSize);
  let k = 1;
  while ((box.scrollWidth > box.clientWidth + 1 || box.scrollHeight > box.clientHeight + 1) && k > 0.4) {
    k -= 0.02; box.style.fontSize = (k * unit) + 'px'; }
});
</script>"""


def page(W, H, safe):
    sx0, sy0, sx1, sy1 = safe[0] * W, safe[1] * H, safe[2] * W, safe[3] * H
    sw, sh = sx1 - sx0, sy1 - sy0
    mark_h = min(0.78 * sh, 0.4 * sw / mark.aspect)
    unit = sh / 100                                    # type scales with the safe area's height (em units below)
    texture = ''
    if args.texture == 'grid':
        line = 'rgb(255 255 255 / .045)' if args.theme == 'dark' else 'rgb(3 7 13 / .05)'
        texture = (f'<div style="position:absolute;inset:0;background-image:linear-gradient({line} 1px,transparent 1px),'
                   f'linear-gradient(90deg,{line} 1px,transparent 1px);background-size:{sh / 3:.0f}px {sh / 3:.0f}px;'
                   '-webkit-mask-image:linear-gradient(90deg,transparent 15%,#000 70%)"></div>')
    if args.layout == 'split':
        body = (f'<div class="copy" style="left:{sx0:.0f}px;top:{sy0:.0f}px;width:{sw - mark.aspect * mark_h - 0.08 * sw:.0f}px;'
                f'height:{sh:.0f}px;justify-content:center">{copy}</div>'
                f'<div style="position:absolute;right:{W - sx1:.0f}px;top:{sy0 + (sh - mark_h) / 2:.0f}px;height:{mark_h:.0f}px">{mark_svg}</div>')
    elif args.layout == 'centered':
        mark_h = min(0.7 * sh, 0.3 * sw / mark.aspect)
        body = (f'<div style="position:absolute;left:{sx0:.0f}px;top:{sy0:.0f}px;width:{sw:.0f}px;height:{sh:.0f}px;display:flex;'
                f'align-items:center;justify-content:center;gap:{0.06 * sw:.0f}px">'
                f'<div style="height:{mark_h:.0f}px;flex:none">{mark_svg}</div>'
                f'<div class="copy" style="position:static;max-width:{0.62 * sw:.0f}px;max-height:{sh:.0f}px">{copy}</div></div>')
    else:
        mark_h = 0.72 * sh
        body = (f'<div style="position:absolute;left:{(sx0 + sx1) / 2 - mark.aspect * mark_h / 2:.0f}px;'
                f'top:{sy0 + (sh - mark_h) / 2:.0f}px;height:{mark_h:.0f}px">{mark_svg}</div>')
    css = (f'{FONT_CSS}*{{margin:0;box-sizing:border-box}}html,body{{width:{W}px;height:{H}px;overflow:hidden}}'
           f'body{{position:relative;background:{bg};color:{ink};font-family:Brand,sans-serif;-webkit-font-smoothing:antialiased}}'
           '.mark{display:block;height:100%;width:auto}'
           f'.copy{{position:absolute;display:flex;flex-direction:column;overflow:hidden;font-size:{unit:.2f}px}}'
           '.h{font-size:24em;line-height:1.04;font-weight:600;letter-spacing:-.035em}'
           f'.s{{margin-top:.55em;font-size:11em;line-height:1.3;color:{muted}}}'
           f'.u{{margin-top:.74em;font-size:9.5em;font-weight:500;color:{muted}}}'
           '.copy>:first-child{margin-top:0}')
    return f'<html><head><style>{css}</style></head><body>{texture}{body}{FIT}</body></html>'


with Renderer() as r:
    for name in args.platforms.split(','):
        if name not in PLATFORMS:
            raise SystemExit(f'unknown platform {name}; choose from {", ".join(PLATFORMS)}')
        (uw, uh), scale, safe, clear = PLATFORMS[name]
        W, H = uw * scale, uh * scale
        img = r.html_png(page(W, H, safe), W, H)
        base = f'{args.name}-{name}'
        upload = img.resize((uw, uh), Image.LANCZOS) if scale > 1 else img
        save_image(upload, OUT / f'{base}-{uw}x{uh}.png')
        save_image(upload, OUT / f'{base}-{uw}x{uh}.jpg')
        if scale > 1:
            save_image(img, OUT / f'{base}-{W}x{H}.png')
        g = img.convert('RGBA')
        over = Image.new('RGBA', g.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(over)
        d.rectangle((safe[0] * W, safe[1] * H, safe[2] * W, safe[3] * H), outline=(40, 200, 120, 255), width=max(2, W // 600))
        if clear:
            d.rectangle((clear[0] * W, clear[1] * H, clear[2] * W, clear[3] * H), fill=(220, 50, 50, 90))
        g.alpha_composite(over)
        g.convert('RGB').save(OUT / f'{base}-guides.png')
        print(f'wrote {name}', flush=True)

print(f'done: {OUT}. In the -guides images, green is the safe area and red is where the profile picture sits.'
      ' Upload the file named with the platform size.')
