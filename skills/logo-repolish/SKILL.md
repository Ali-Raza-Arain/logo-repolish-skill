---
name: logo-repolish
description: Repolish, rebuild or recreate an existing logo and produce a complete brand kit from it, entirely on the local machine. Turns a raster logo (PNG, JPG, screenshot, AI-generated image) into a precise master SVG with exactly straight lines, true circles and clean corners; audits it against design rules (stroke weights, gaps, angles, alignment, small sizes); and exports every format and theme (SVG, PDF, transparent PNG, light and dark JPG, one-colour), name lockups, favicons and app icons, profile pictures in professional palettes, and LinkedIn, X, Facebook and YouTube covers with correct safe areas. Handles 3D and metallic logos without destructive tracing. Use it whenever the user wants to vectorize, trace, clean up, sharpen, perfect, redraw, upscale or make HD a logo, asks for a logo in more formats, sizes or colours, a brand kit, favicon, profile picture, banner or cover from their logo, or says the logo looks blurry, uneven or not straight, even without saying "vector".
license: MIT, see LICENSE.txt. Bundled font under the SIL Open Font License, see assets/fonts/OFL.txt.
metadata:
  author: Ali Raza
  version: 1.0.0
  source: https://github.com/ali-raza-arain/logo-repolish-skill
---

# Logo repolish

Rebuild an existing logo as an exact vector master, check it the way a mark designer would, and export a full
brand kit from it. Everything runs locally with the bundled scripts.

The owner's logo is their identity, so the work is conservative: reproduce faithfully, report what could be
better, change shape or colour only with their agreement, and let them choose between options by looking at previews.

## Ground rules

These matter more than any technique, because breaking one costs the owner's trust:

1. **Local only.** Never upload the logo or anything made from it to a website, image generator, design tool, cloud
   storage, artifact, gist or paste service. Read and render files on this machine only. If a step seems to need an
   online tool, stop and ask.
2. **Never change the logo's colours** or proportions on your own. Themes change the background, not the logo.
   One-colour white and black versions are the standard exception, named as such. Suggest a colour or shape fix and
   wait for a yes.
3. **Never overwrite.** Write results into new folders (the scripts refuse non-empty folders unless `--force`). Before
   replacing files in a project (a website's public folder, a brand folder), copy the old files to a dated backup
   folder first, and prefer moving files to the trash over deleting them.
4. **Never invent copy.** Headlines, taglines, URLs and names on covers and lockups come from the user or their
   existing site. If none are given, ask, or make mark-only versions.
5. **Show, then ask.** Look at every preview image yourself (open the PNG with the file-reading tool) before showing
   the user, describe what you see honestly, including flaws, and let them pick among options.

## Setup (once per machine)

```bash
bash <skill>/scripts/setup_env.sh            # core tools
bash <skill>/scripts/setup_env.sh --upscale  # only for 3D/raster upscaling
PY=~/.cache/logo-repolish/venv/bin/python    # use this Python for every script below
```

`<skill>` is this skill's folder. Rendering uses headless Chromium (installed by the setup) so SVGs come out exactly
as browsers draw them. If the download fails, a system Chrome is used.

## Step 1: understand what you have

Ask for or locate the best source before doing anything. Questions worth asking, if the answers are not obvious:
- Is there a flat 2D version, the designer's original file, or a higher-resolution export?
- Which colour(s) are official (a hex code beats sampling pixels)?
- Where will the logo be used (website, social, print, merchandise), so you know which outputs matter?
- Is there a brand name and font for lockups, and copy for covers?

Then sort the source into one of four cases:

| Source | Route |
|---|---|
| Flat 2D raster (solid colours, maybe antialiased) | Step 2: vectorize |
| Existing SVG that is messy (traced, uneven, bloated) | render it to a large PNG and vectorize that, or audit it as is |
| 3D, metallic, shaded or photographic | read `references/3d-logos.md` first; ask for a flat source |
| Clean SVG already | skip to Step 3 (audit) or Step 4 (kit) |

## Step 2: build the master vector

```bash
$PY <skill>/scripts/vectorize.py source.png work/logo.svg --colors 1 --title "Brand"
$PY <skill>/scripts/compare.py source.png work/logo.svg work/check
```

What `vectorize.py` does differently from a generic tracer: it reads edges at sub-pixel precision, turns every
stretch running near a multiple of `--snap` degrees into an exact straight line fitted over its whole length, meets
lines at their exact intersections, smooths only the true curves, and replaces round holes and dots with exact
circles of matching sizes. Coordinates stay in the source's pixel units, so the vector overlays the artwork exactly.

Options worth knowing:
- `--colors N` for multi-colour logos (N colours, not counting the background); `--fill #hex` to use the official
  colour instead of the sampled one (single colour).
- `--snap 30` or `15` for marks built on other angle grids; `--snap 0` for purely organic shapes.
- `--background #hex` when the image corners are not background; `--no-circles` when round parts are not meant to be
  true circles.

Check the result, every time:
- `compare.py` prints how much ink differs. Around 1 to 2% for a single-colour mark is normal (antialiased edges).
  Much more means a missed part, a wrong colour count or a background problem.
- Open `check-diff.png` (red: missing, blue: added) and `check-zoom.png` (the worst spots, enlarged). Look closely at
  corners, thin parts and holes.
- Render the SVG large on the logo's usual background and look at it as a whole.

If the source artwork itself has flaws (a line that wobbles, a corner a little off), the vector will follow the
source where it cannot tell intent from error. Note these for Step 3 rather than hand-fixing silently.

## Step 3: audit against design rules

```bash
$PY <skill>/scripts/audit.py work/logo.svg work/audit --snap 45
```

Read `work/audit/audit.md`, `small-sizes.png` and `tight-gaps.png`, then read `references/design-rules.md` to judge
the findings. Report to the user in plain words: what is consistent, what looks off, and a proposed fix for each.
Apply only the fixes they approve, then re-run compare and audit. Typical outcomes: angles snapped exactly, same-size
holes unified, one stroke brought into its weight tier, a tight gap widened, and a note that the mark needs a
simplified version below 32 px if its details vanish there.

## Step 4: export the kit

Make a kit folder next to (not inside) the source, then run what the user needs. All scripts take the master SVG.

```bash
$PY <skill>/scripts/export_kit.py work/logo.svg --out kit/logo --name brand-logo [--dark #03070d --light #ffffff]
$PY <skill>/scripts/lockups.py   work/logo.svg --out kit/lockup --text "BRAND" [--font brand.ttf --weight 600]
$PY <skill>/scripts/icons.py     work/logo.svg --out kit/icons [--bg #03070d]
$PY <skill>/scripts/profiles.py  work/logo.svg --out kit/profiles [--palettes ink-brand,navy-white] [--brand-solid]
$PY <skill>/scripts/covers.py    work/logo.svg --out kit/covers --headline "..." --url example.com [--layout split]
```

- **export_kit**: SVG and PDF (transparent, on light, on dark, one-colour), transparent PNG 256 to 4096 px, square
  light and dark PNG and JPG 512 to 4096, favicon.ico, and `preview.png`. Pick `--dark` and `--light` from the
  brand's own site colours when it has them. Contrast warnings mean the logo colour is weak on that background:
  tell the user, do not recolour.
- **lockups**: mark plus name, horizontal and stacked, on dark, on light and transparent, with the name set as
  vector outlines from a real font (Instrument Sans by default, bundled under the SIL Open Font License). Use the
  brand's font if it has one. Spacing and sizes follow common practice; adjust only if the user asks.
- **icons**: the full website and app icon set, and it prints the head tags. Small tab icons enlarge the mark a
  little so it reads at 16 to 48 px. It refuses to replace existing icon files unless `--force`, so back up a site's
  icons before writing into its public folder.
- **profiles**: circle-safe profile pictures in classic professional palettes (`assets/palettes.json`), each as a
  1080 PNG and JPG, a 400 PNG and an SVG, plus `preview-all.png` showing every design as a circle and a rounded
  square, numbered so the user can choose. `--pair BG:FG` adds a custom pair; FG `keep` keeps the logo colours.
- **covers**: banners for LinkedIn (company and personal), X, Facebook and YouTube with each platform's safe area,
  and a `-guides.png` per platform showing the safe area (green) and where the profile picture sits (red). Copy only
  from the user. Layouts: `split`, `centered`, `mark`; `--theme light`; `--texture grid` for a faint grid.

Platform sizes, safe areas and print notes are in `references/platform-sizes.md`.

## Step 5: apply to a project (when asked)

For a website:
1. Back up the files you will replace (dated folder), then copy the master SVG to the project's brand or assets
   folder and the icons to its public folder.
2. Use the SVG for the header and footer logo, with `width` and `height` attributes matching its viewBox ratio so
   the page does not shift while loading, and empty `alt` when the brand name is next to it as text.
3. Update the head tags (printed by `icons.py`), the web app manifest, the social preview image if it shows the
   logo, and any structured data `logo` URL.
4. Run the project's own build and lint, and check the pages that show the logo.
5. Note in the project README where the master lives and that icons are generated from it, so nobody redraws it.

## Step 6: hand over

Tell the user, briefly: where every output is, what was checked (compare percentage, audit findings and what was
done about them), any contrast warnings, and which preview to open first. Mention anything you could not do or
are unsure about. Keep the work folder until they confirm they are happy, then offer to move intermediate files to
the trash.

## Common mistakes and how to avoid them

- **Diagonals a degree off and small nubs at corners** after tracing: caused by fitting lines piece by piece. The
  vectorizer splits runs by direction, fits each over its full length with a tolerance that grows with length, and
  drops the tiny curve bits between two lines so they meet at a true corner. If a corner still shows a nub, check
  that `--snap` matches the mark's angle grid.
- **Tracing a 3D logo** into flat shapes loses the shine and looks cheap. Keep 3D as a raster; vectorize only a
  flat source.
- **Cutting a logo out of its background** leaves halos and glitches. Keep the background or use the flat mark.
- **Light-theme versions of a dark render with recreated shadows** look dirty. Use the 2D mark on light.
- **Covers with generic decoration** (glowing blobs, neon lines, circuit patterns unrelated to the business) look
  like templates. Prefer plain grounds, the real mark, real copy and at most a faint grid.
- **Profile pictures cut at the corners**: the mark must fit the circle, not the square. `profiles.py` handles it
  with `--reach`; lower it (0.8) for marks with long diagonals if they feel tight.
- **Losing the master**: keep the master SVG and the kit in the project's brand folder, not a temporary folder,
  and remind the user to commit it.

## Files

```
scripts/common.py       shared helpers (mark loading, placing, rendering, contrast, wordmark outlines)
scripts/vectorize.py    raster to precise SVG
scripts/compare.py      overlay and difference check against the source
scripts/audit.py        design-rule measurements and small-size sheet
scripts/export_kit.py   formats and themes
scripts/lockups.py      mark with name
scripts/icons.py        favicons, touch and app icons
scripts/profiles.py     profile pictures in palettes
scripts/covers.py       social covers with safe areas
scripts/upscale.py      Real-ESRGAN 4x for raster (3D) logos, hybrid with plain enlargement
scripts/setup_env.sh    one-time environment setup
references/design-rules.md     what the audit measures and how to judge it
references/3d-logos.md         rules for 3D, metallic and photographic logos
references/platform-sizes.md   icon, profile, cover and print sizes
assets/palettes.json           professional colour pairs for profiles
assets/fonts/                  Instrument Sans (SIL OFL) for lockups and covers
```
