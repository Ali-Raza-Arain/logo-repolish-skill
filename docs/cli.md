# Command reference

All scripts live in `skills/logo-repolish/scripts/`. Run them with the Python from the setup
(`~/.cache/logo-repolish/venv/bin/python`) or any Python that has `requirements.txt` installed.

Colours are hex values such as `#03070d`. Sizes are in pixels unless stated otherwise.
Scripts that write a folder refuse to write into a folder that already has files, unless you pass `--force`, so
earlier results are never replaced by accident.

## Contents

- [setup_env.sh](#setup_envsh)
- [vectorize.py](#vectorizepy)
- [compare.py](#comparepy)
- [audit.py](#auditpy)
- [export_kit.py](#export_kitpy)
- [lockups.py](#lockupspy)
- [icons.py](#iconspy)
- [profiles.py](#profilespy)
- [covers.py](#coverspy)
- [upscale.py](#upscalepy)
- [Environment variables](#environment-variables)
- [Repository tools](#repository-tools)

## setup_env.sh

```
bash setup_env.sh [--upscale]
```

Creates a virtual environment at `$LOGO_REPOLISH_HOME/venv` (default `~/.cache/logo-repolish/venv`) and installs
Pillow, NumPy, SciPy, scikit-image, fontTools, Brotli and Playwright, then downloads Playwright's Chromium.
With `--upscale` it also installs PyTorch (CPU build), torchvision and spandrel, and downloads
`RealESRGAN_x4plus.pth` into `$LOGO_REPOLISH_HOME/models`. Safe to run again; it skips what is already there.

## vectorize.py

```
vectorize.py SRC OUT [--colors N] [--fill HEX] [--background HEX] [--snap DEG] [--no-circles] [--title TEXT] [--force]
```

Rebuilds a flat raster logo as an SVG.

| Option | Default | Meaning |
|---|---|---|
| `SRC` | | PNG or JPG of the logo, ideally 800 px or more; transparency is used when present |
| `OUT` | | SVG to write; refused if it exists, unless `--force` |
| `--colors N` | 1 | number of logo colours, not counting the background |
| `--fill HEX` | sampled | use this colour instead of the sampled one (single-colour logos) |
| `--background HEX` | border median | the background colour, when the image corners are not background |
| `--snap DEG` | 45 | angle grid for straight lines; 30 or 15 for other grids, 0 to turn line snapping off |
| `--no-circles` | off | keep round holes and dots as traced shapes instead of exact circles |
| `--title TEXT` | Logo | the SVG title (read by screen readers and shown in some apps) |

Output: one `<path>` per colour with `fill-rule="evenodd"`, coordinates in source pixels, a `viewBox` that is
the logo's bounding box, and `data-source-size` with the source dimensions. It prints the colours found, the
circle groups per layer and the working scale.

## compare.py

```
compare.py SOURCE SVG PREFIX
```

Renders the SVG in the source's pixel frame (up to 3x) and compares the two.

Writes `PREFIX-diff.png` (grey: both agree, red: ink in the source that the vector lacks, blue: ink the vector
adds) and `PREFIX-zoom.png` (close-ups of the worst areas, vector in the top row, source below). Prints the
missing and added ink as a share of the source's ink. One to two percent in total is normal for a single-colour
logo and comes from antialiased edges.

## audit.py

```
audit.py SVG OUT_FOLDER [--snap DEG]
```

Measures the mark and writes `audit.md`, `small-sizes.png` and `tight-gaps.png` into `OUT_FOLDER`. Sizes in
the report are per 1000 units of logo height, so reports of different logos compare directly.

| Section | Method |
|---|---|
| Circles and holes | every enclosed hole's equivalent radius, and whether they are identical |
| Stroke weights | twice the distance to the edge along each part's skeleton: median and 10th to 90th percentile, grouped into tiers |
| Gaps | the width of the empty space between facing edges of the mark; spots under 70% of the usual gap, or under 60% of the main stroke weight, are marked red |
| Angles | straight segments longer than 25 units that sit 0.05 to 5 degrees off the `--snap` grid |
| Alignment | pairs of hole centres 1 to 12 units off a shared row or column |
| Small sizes | the mark rendered at 16, 24, 32, 48, 64 and 128 px, shown 4x |

`--snap 0` skips the angle check.

## export_kit.py

```
export_kit.py SVG --out FOLDER [--name NAME] [--dark HEX] [--light HEX] [--mono-light HEX] [--mono-dark HEX]
              [--margin SHARE] [--force]
```

| Option | Default | Meaning |
|---|---|---|
| `--name` | logo | file name prefix |
| `--dark` | #03070d | dark theme background |
| `--light` | #ffffff | light theme background |
| `--mono-light` | #f5f5f5 | ink of the one-colour light version |
| `--mono-dark` | #03070d | ink of the one-colour dark version |
| `--margin` | 0.12 | space around the logo on square versions, per side, as a share of the logo's size |

Writes `svg/`, `pdf/`, `png/transparent/` (256 to 4096 px tall), `png/light/` and `png/dark/` (square, 512 to
4096), `jpg/`, `png/one-colour/`, `ico/favicon.ico` and `preview.png`. Warns when a logo colour has less than 3:1
contrast against a theme background.

## lockups.py

```
lockups.py SVG --text TEXT --out FOLDER [--name NAME] [--font FILE] [--weight N] [--tracking EM]
           [--dark HEX] [--light HEX] [--text-on-dark HEX] [--text-on-light HEX] [--force]
```

| Option | Default | Meaning |
|---|---|---|
| `--text` | | the name to set, exactly as it should appear (case included) |
| `--name` | lockup | file name prefix |
| `--font` | Instrument Sans | a TTF, OTF or WOFF2 file; variable fonts are set at `--weight` |
| `--weight` | 600 | weight for variable fonts |
| `--tracking` | 0.14 | letter spacing in em; 0.1 to 0.16 suits capitals, 0 to 0.02 suits lowercase |
| `--dark`, `--light` | #03070d, #ffffff | backgrounds of the backed versions |
| `--text-on-dark`, `--text-on-light` | #f5f5f5, #03070d | name colours |

Writes horizontal and stacked lockups, each on dark, on light, and transparent for dark or light backgrounds, as
SVG and PDF (vector, the name as outlines), PNG (2400 px wide horizontal, 1600 px stacked) and JPG, plus
`preview.png`.

## icons.py

```
icons.py SVG --out FOLDER [--bg HEX] [--radius SHARE] [--fill keep|HEX] [--force]
```

| Option | Default | Meaning |
|---|---|---|
| `--out` | | a new folder, or a site's public folder |
| `--bg` | #03070d | icon background |
| `--radius` | 0.19 | corner radius of `favicon.svg`, as a share of its size |
| `--fill` | keep | `keep` for the logo's colours, or one colour |
| `--force` | off | replace icon files that already exist in `--out`; back them up first |

Writes `favicon.svg`, `favicon-32.png`, `favicon-48.png`, `favicon.ico` (16 to 64), `apple-touch-icon.png`
(180), `icon-192.png`, `icon-512.png`, `icon-maskable-512.png` and `logo-512.png`, and prints the head tags.
A web app manifest that uses them looks like this:

```json
{
  "icons": [
    { "src": "/icon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/icon-512.png", "sizes": "512x512", "type": "image/png" },
    { "src": "/icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable" }
  ]
}
```

## profiles.py

```
profiles.py SVG --out FOLDER [--name NAME] [--palettes A,B,...] [--pair BG:FG] [--brand-solid] [--reach SHARE] [--force]
```

| Option | Default | Meaning |
|---|---|---|
| `--name` | profile | file name prefix |
| `--palettes` | all | names from `assets/palettes.json`, comma-separated |
| `--pair BG:FG` | | an extra design; FG `keep` keeps the logo's colours; repeat for more |
| `--brand-solid` | off | adds the logo colour as background, with the mark in white and in near-black |
| `--reach` | 0.87 | how far the mark's bounding-box corner reaches toward the circle's edge |

Each design is written as `NAME-NN-PALETTE.svg`, `-1080.png`, `-1080.jpg` and `-400.png`. `preview-all.png`
shows every design as a circle and a rounded square, numbered. Palettes in `assets/palettes.json`:
navy-white, navy-brand, racing-green-cream, racing-green-brand, oxblood-cream, oxblood-gold, graphite-cream,
steel-white, petrol-sand, stone-navy, stone-oxblood, ink-brand, white-brand, black-white. A palette whose
foreground is `keep` uses the logo's own colours.

## covers.py

```
covers.py SVG --out FOLDER [--name NAME] [--platforms LIST] [--layout split|centered|mark] [--theme dark|light]
          [--headline TEXT] [--subline TEXT] [--url TEXT] [--texture none|grid]
          [--bg HEX] [--text HEX] [--muted HEX] [--mark-fill keep|HEX] [--font FILE] [--force]
```

| Option | Default | Meaning |
|---|---|---|
| `--platforms` | all | any of linkedin-company, linkedin-personal, x, facebook, youtube |
| `--layout` | split | `split`: text left, mark right; `centered`: mark and text side by side; `mark`: mark only |
| `--theme` | dark | dark (#03070d, #f5f5f5, #9aa4b2) or light (#f6f4ef, #03070d, #5b6470) |
| `--headline`, `--subline`, `--url` | empty | the copy; without any, the layout falls back to `mark` |
| `--texture` | none | `grid` adds a faint grid that fades toward the text side |
| `--bg`, `--text`, `--muted` | from theme | override the background, headline and secondary text colours |
| `--mark-fill` | keep | `keep` for the logo's colours, or one colour |
| `--font` | Instrument Sans | TTF, OTF, WOFF or WOFF2 |

The URL is shown without `https://` and without a trailing slash. Text shrinks to fit its box if it is long.
For each platform: the upload-size PNG and JPG, a 2x PNG where the platform accepts it, and a `-guides.png` with
the safe area in green and the profile picture zone in red.

## upscale.py

```
upscale.py SRC OUT [--model FILE] [--tile N] [--threads N] [--no-hybrid]
```

| Option | Default | Meaning |
|---|---|---|
| `--model` | `$LOGO_REPOLISH_HOME/models/RealESRGAN_x4plus.pth` | any 4x model spandrel can load |
| `--tile` | 256 | tile size; lower it if memory is short |
| `--threads` | all CPU cores | PyTorch threads |
| `--no-hybrid` | off | use the upscaled pixels everywhere instead of only where the source has detail |

Refuses to overwrite `OUT`. Keeps transparency. Needs `setup_env.sh --upscale`.

## Environment variables

| Variable | Used by | Meaning |
|---|---|---|
| `LOGO_REPOLISH_HOME` | setup_env.sh, upscale.py | where the venv and models live (default `~/.cache/logo-repolish`) |
| `PLAYWRIGHT_BROWSERS_PATH` | all renderers | standard Playwright setting, if you keep browsers elsewhere |

## Repository tools

| Command | What it does |
|---|---|
| `python examples/make_demo_logo.py OUT.png` | draws the made-up demo mark used in the docs and tests |
| `python tests/smoke_test.py [--keep DIR] [--upscale]` | runs every script on the demo mark and checks the outputs |
| `python tools/make_readme_images.py DIR` | rebuilds `docs/images` and `examples/` from a `--keep` smoke test folder |
| `python tools/package_skill.py` | writes `dist/logo-repolish.zip` (and `.skill`) for upload |
