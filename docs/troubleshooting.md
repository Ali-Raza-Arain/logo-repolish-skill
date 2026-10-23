# Troubleshooting

## Setup

**`No Chromium found` or a Playwright launch error.**
Run `~/.cache/logo-repolish/venv/bin/python -m playwright install chromium`. On a fresh Linux machine Chromium may
also need system libraries: `sudo ~/.cache/logo-repolish/venv/bin/python -m playwright install-deps chromium`.
If the download is blocked, install Google Chrome or Chromium from your package manager; the scripts fall back to
it.

**`python3 -m venv` fails on Debian or Ubuntu.**
Install the venv module: `sudo apt install python3-venv`.

**Windows.**
Use WSL, or create a virtual environment yourself, `pip install -r requirements.txt`, then
`python -m playwright install chromium`, and run the scripts with that Python.

**PyTorch install is large or slow.**
It is only needed for `upscale.py`. Skip `--upscale` unless you work with 3D or photographic logos.

## Vectorizing

**`No logo pixels found: is the background right?`**
The image border is not background (the logo touches the edge, or the image is a screenshot of a page). Add a
margin around the logo, crop to the logo on its own background, or pass `--background #hex`.

**`warning: the source is only N px`.**
The result can still be good for simple marks, but thin strokes and small holes suffer. Use a larger export if
one exists.

**Parts of the logo are missing in the diff (solid red).**
They are probably a second colour, or a colour close to the background. Try `--colors 2`. For a light logo on
white, put it on a dark background first, or use a version with transparency.

**A line that should be diagonal came out as a curve.**
Its angle is not on the grid. Check the angle with the audit, then use the matching `--snap` (30, 15) or
`--snap 0`.

**A sharp corner came out rounded, or a small nub remains at a corner.**
The two lines meeting there were not both recognised as lines. Usually the grid is wrong (`--snap`) or the source
is small; a larger source helps most.

**Oval dots turned into circles.**
Pass `--no-circles`.

**Colours in a multi-colour logo are slightly off.**
Sampled colours are medians of the pixels and can differ from the official values by a few steps, especially in
JPGs. Replace the `fill` values in the SVG with the official codes; that does not change the shapes.

**The SVG opens with the wrong size in a design tool.**
The coordinates are in source pixels and the `viewBox` is the logo's bounding box, with no `width` or `height`.
Most tools read the `viewBox`; set a size on export if a tool asks for one.

## Audit

**Many tight-gap spots in a logo that looks fine.**
The limit is relative: 70% of the usual gap, or 60% of the main stroke. A deliberately tight detail will be
flagged. Look at `tight-gaps.png` and at `small-sizes.png`; if the detail survives at the sizes you need, it is
fine.

**Stroke weights in many close tiers.**
Either the weights really are uneven, or the mark has tapering strokes on purpose. The 10th to 90th percentile
range shows which: a narrow range means even strokes, a wide range means tapering.

## Kit and social images

**Contrast warnings.**
The logo colour is weak on that background (under 3:1). Use the other theme there, or the one-colour version.
Changing the logo colour is the owner's decision.

**`... already has files. Choose a new folder, or pass --force`.**
The scripts refuse to overwrite earlier results. Use a new folder, or back up and pass `--force`.

**Fonts look different in covers or lockups.**
Lockups convert the name to outlines, so they always match the font file. Covers render text with the font file
you pass; if the font has no glyph for a character, the browser substitutes one. Pass a font that covers your
text.

**A platform crops the cover differently than the guide shows.**
Platforms change their layouts. Adjust the safe area for that platform in `PLATFORMS` at the top of `covers.py`,
and please open an issue so the defaults can be updated.

## Upscaling

**`model not found`.** Run `setup_env.sh --upscale`, or pass `--model` with the path to a 4x model.

**It is slow.** It runs on the CPU. A 1024 px image takes a few minutes. Lower `--tile` only if memory runs out.

**Blotchy texture in flat areas.** The hybrid mode should prevent this; make sure `--no-hybrid` is not set. If a
soft gradient still shows texture, the gradient was detected as detail; use the plain enlargement for that file.
