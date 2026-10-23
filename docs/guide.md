# Guide: from a logo file to a finished brand kit

This walkthrough follows one logo from start to finish: setup, rebuilding it as a vector, checking it, exporting
the kit and putting it on a website. It uses the demo mark from `examples/` so you can repeat every step, and
notes what Claude does at each step when you work through the skill instead of the command line.

## Contents

1. [Before you start](#1-before-you-start)
2. [Setup](#2-setup)
3. [Choose the right source](#3-choose-the-right-source)
4. [Rebuild the logo as a vector](#4-rebuild-the-logo-as-a-vector)
5. [Check the vector against the source](#5-check-the-vector-against-the-source)
6. [Audit the design](#6-audit-the-design)
7. [Export the kit](#7-export-the-kit)
8. [Lockups](#8-lockups)
9. [Website icons](#9-website-icons)
10. [Profile pictures](#10-profile-pictures)
11. [Social covers](#11-social-covers)
12. [Put it on a website](#12-put-it-on-a-website)
13. [3D and metallic logos](#13-3d-and-metallic-logos)
14. [Working with Claude](#14-working-with-claude)

## 1. Before you start

Gather what you can:

- the largest flat version of the logo you have (PNG beats JPG, the original export beats a screenshot);
- the official colour codes, if they exist;
- the brand name exactly as it should be written, and the brand font file if there is one;
- for covers: a headline, an optional second line and the website address.

Make sure you have the right to work with the logo. Everything in this guide runs on your machine; nothing is
uploaded.

## 2. Setup

```bash
git clone https://github.com/ali-raza-arain/logo-repolish-skill.git
cd logo-repolish-skill
bash skills/logo-repolish/scripts/setup_env.sh
PY=~/.cache/logo-repolish/venv/bin/python
S=skills/logo-repolish/scripts
$PY tests/smoke_test.py          # optional: checks every tool on the demo mark, about a minute
```

The commands below assume `PY` and `S` are set as above.

## 3. Choose the right source

| What you have | What to do |
|---|---|
| A flat logo: solid colours, sharp or softly antialiased edges | vectorize it (step 4) |
| A messy SVG (auto-traced, uneven, thousands of nodes) | export it as a large PNG (2000 px or more) and vectorize that, or run the audit on it first |
| A clean SVG | skip to the audit (step 6) or the kit (step 7) |
| A 3D, metallic, shaded or photographic logo | read [section 13](#13-3d-and-metallic-logos) first |
| A small or blurry flat logo (under 600 px) | ask for a larger file; if there is none, vectorize anyway and check the result closely |

For this guide, draw the demo mark:

```bash
mkdir -p work
$PY examples/make_demo_logo.py work/demo.png
```

It is 1024 px, antialiased, and its long edges bow by about 1.5 px, like many generated logos.

## 4. Rebuild the logo as a vector

```bash
$PY $S/vectorize.py work/demo.png work/logo.svg --title "Example"
```

Output for the demo:

```
layer 1 (#3a7ca5): 1 round holes, 3 round dots, size groups [2, 1, 1]
wrote work/logo.svg: 1 colour(s) #3a7ca5, background #ffffff, 2 KB, viewBox 114.0 112.8 799.0 799.5 (source pixels, worked at 4x)
```

Read it like this: one colour was found; one round hole (inside the ring) and three round shapes (the two small
dots and the ring's outer edge) became exact circles; the two small dots were recognised as the same size. The
file is 2 KB.

Choose options to match the logo:

- **More than one colour:** `--colors 2` (or 3). Count only the logo's colours, not the background.
- **Official colour known:** `--fill #123456` for single-colour logos, so the SVG uses the exact value instead of
  the sampled one.
- **A background that is not at the image corners,** for example a logo on a card in a screenshot: crop it first,
  or pass `--background #hex`.
- **A different angle grid:** a logo built on 30 or 60 degree lines needs `--snap 30`; on 15 degree steps,
  `--snap 15`; a hand-drawn or organic mark, `--snap 0`.
- **Round parts that are not meant to be circles** (slightly oval dots, for example): `--no-circles`.

## 5. Check the vector against the source

```bash
$PY $S/compare.py work/demo.png work/logo.svg work/check
```

```
ink pixels: 630346; missing 0.96%, added 0.85% (antialiased edges account for about 1 to 2%)
```

Open `work/check-diff.png`. Grey is where the two agree, red is ink the vector lacks, blue is ink it adds. A thin
red and blue outline along every edge is normal. Look for solid patches:

| What you see | Likely cause | Fix |
|---|---|---|
| A whole part missing | it is a separate colour, or too close to the background | `--colors 2`, or `--background` |
| Blobs of blue around thin parts | the source is soft or small | a larger source |
| A corner cut off or rounded | the corner is not on the angle grid | the right `--snap` |
| An oval hole drawn as a circle | the circle fit was too generous for this mark | `--no-circles` |
| Red and blue on opposite sides of a long line | the source line bows and the vector is straight | nothing: this is the fix working |

Then open `work/check-zoom.png`: the vector (top row) and the source (bottom row) at the spots with the most
difference. Corners, thin strokes and holes deserve the closest look.

Finally, look at the SVG itself, large, in a browser or design tool, on the logo's usual background.

## 6. Audit the design

```bash
$PY $S/audit.py work/logo.svg work/audit
```

The report for the demo is in [examples/demo-audit.md](../examples/demo-audit.md). How to read each part:

- **Circles and holes.** "Spread 0.00 (identical)" means holes that should match do match.
- **Stroke weights.** Each row is one part of the mark, with its typical width. The demo has two tiers: the frame
  at about 72 and the curved bar at about 53. Two clear tiers usually read as intentional. A part whose weight
  sits just between two tiers is worth a question.
- **Gaps.** The usual and narrowest space between facing edges, and how many spots are tight. In the demo the
  tight spots are where the ends of the curved bar come closest to the frame. They are shown in red in
  `tight-gaps.png`. Tight spots fill in first at small sizes and in print.
- **Angles.** Long straight segments that are almost, but not exactly, on the grid. After vectorizing this is
  usually zero.
- **Alignment.** Hole centres that miss a shared row or column by a small amount.
- **Small sizes.** Open `small-sizes.png`. If the mark's details merge at 16 to 32 px, a simplified version for
  favicons may be worth designing.

The audit measures; it does not know intent. [references/design-rules.md](../skills/logo-repolish/references/design-rules.md)
explains each rule and when a finding is likely deliberate. Change the design only when the logo's owner agrees.
After any change, run compare and the audit again.

## 7. Export the kit

```bash
$PY $S/export_kit.py work/logo.svg --out kit/logo --name example
```

Choose `--dark` and `--light` to match the brand's own backgrounds if it has them (the defaults are near-black
`#03070d` and white). The logo's colours are never changed; only the backgrounds differ between themes. If the
script warns about contrast, the logo colour is weak on that background: prefer the other theme there, or use the
one-colour version.

What goes where:

| Need | File |
|---|---|
| Website, apps, design tools | `svg/example.svg` |
| Printer, signage, embroidery quotes | `pdf/example.pdf` (and the one-colour PDFs) |
| Documents, slides, places that do not take SVG | `png/transparent/example-1024h.png` or larger |
| Platforms that need a square image | `png/light/` or `png/dark/`, or `jpg/` where PNG is not accepted |
| Stamps, embossing, single-colour print, busy photos | `-white` and `-black` versions |

Open `kit/logo/preview.png` to check all four themes at once.

## 8. Lockups

```bash
$PY $S/lockups.py work/logo.svg --out kit/lockup --text "EXAMPLE"
```

The name is converted to outlines, so it looks the same everywhere. Use the brand font with `--font path.ttf`. For
a lowercase or mixed-case name, set `--tracking 0.02` or so; the default suits capitals. Check `preview.png`:
the name should sit centred on the mark's height in the horizontal version.

## 9. Website icons

```bash
$PY $S/icons.py work/logo.svg --out kit/icons --bg "#03070d"
```

It prints the head tags to use. The tab icons enlarge the mark slightly so it reads at small sizes. When you
write straight into a site's public folder, back up the old icons first; the script refuses to replace existing
icon files unless you pass `--force`.

## 10. Profile pictures

```bash
$PY $S/profiles.py work/logo.svg --out kit/profiles
```

This writes every palette in `assets/palettes.json`. Open `preview-all.png`: each design is shown as a circle
and as a rounded square, numbered, so you can pick by number. To try a few only, or your own colours:

```bash
$PY $S/profiles.py work/logo.svg --out kit/profiles-2 --palettes navy-white,stone-navy --pair "#1b2a41:keep" --brand-solid
```

The mark is sized to fit inside the circle every platform crops to. If a mark with long diagonals feels tight,
use `--reach 0.8`.

## 11. Social covers

```bash
$PY $S/covers.py work/logo.svg --out kit/covers \
  --headline "Example Co" --subline "Covers built from the logo mark" --url example.com
```

Covers for LinkedIn (company and personal), X, Facebook and YouTube. Each platform also gets a `-guides.png`:
the green box is where content is safe on every device, and the red box is where the platform puts your profile
picture over the cover. Upload the file named with the platform's size.

Other looks: `--layout centered`, `--layout mark` (no text), `--theme light`, `--texture grid`. Keep the copy short
and concrete; the script shrinks long text to fit, but a short headline reads better.

## 12. Put it on a website

1. Back up the files you are about to replace.
2. Copy `work/logo.svg` into the site's assets, and the icon files into its public folder.
3. Use the SVG in the header with `width` and `height` attributes in the ratio of its `viewBox`, so the page does
   not shift while it loads:

   ```html
   <img src="/brand/logo.svg" alt="" width="799" height="800">
   ```

   Use empty `alt` when the brand name appears next to it as text; otherwise use the brand name.
4. Paste the head tags printed by `icons.py`, and add the icons to the web app manifest if the site has one.
5. Point any structured data `logo` field at `logo-512.png`, and update the social preview image if it shows the
   logo.
6. Build the site and check every page that shows the logo, on dark and light sections.
7. Keep the master SVG in the repository and note in the README that the icons are generated from it, so nobody
   redraws it later.

## 13. 3D and metallic logos

A 3D render cannot become an exact vector, and attempts to trace it or cut it out of its background damage it.
Read [references/3d-logos.md](../skills/logo-repolish/references/3d-logos.md). In short:

- ask for the flat version the render was made from, vectorize that, and use it for icons, light themes and print;
- keep the render as a showpiece on its own (dark) background;
- if the render is small, enlarge it with `upscale.py` (after `setup_env.sh --upscale`) and check the result at
  100% around the edges and in flat areas.

```bash
$PY $S/upscale.py logo-3d.png logo-3d-4x.png
```

## 14. Working with Claude

With the skill installed, you can do all of the above by asking. A typical session:

1. You: "Here is our logo, `brand/logo.png`. Make a clean vector and a brand kit."
2. Claude asks what it cannot see: whether there is a larger or flat original, the official colour, the brand
   name for lockups, and where the logo will be used.
3. Claude runs the setup if needed, vectorizes, compares, and looks at the difference images itself. It tells you
   the difference percentage and anything that looked off.
4. Claude runs the audit and explains the findings in plain words, with a proposed fix for each, and waits for
   your decision. Nothing about the shape or colour changes without your yes.
5. Claude exports what you asked for into new folders, looks at each preview, and lists where everything is.
6. If you ask it to update a website, it backs up the old files first, then updates the files and tags and runs
   the site's build.

Things you can ask for at any point: "show me the comparison", "try `--snap 30`", "make the profile pictures only
in navy and stone", "use our font `fonts/Brand.otf` for the lockup", "make the LinkedIn cover lighter".
