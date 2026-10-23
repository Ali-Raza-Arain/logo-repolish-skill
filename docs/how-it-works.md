# How it works

The methods behind each tool, for anyone who wants to tune them, extend them or check that they do what they say.

## Contents

1. [Vectorizing](#1-vectorizing)
2. [Comparing](#2-comparing)
3. [Auditing](#3-auditing)
4. [Rendering](#4-rendering)
5. [Lockups and fonts](#5-lockups-and-fonts)
6. [Profile pictures](#6-profile-pictures)
7. [Covers](#7-covers)
8. [Upscaling](#8-upscaling)

## 1. Vectorizing

`vectorize.py` treats a logo as geometry, not as pixels.

**Background and colours.** The background is the median colour of the image border (or `--background`). Ink
is anything clearly different from it, or, for images with transparency, the opaque pixels. With one colour,
the logo colour is the median of the ink. With several, a k-means clustering on a sample of ink pixels finds
them.

**Coverage at sub-pixel precision.** For one colour, each pixel's colour is projected onto the line from the
background colour to the logo colour, which gives how much of that pixel the logo covers (0 to 1). Antialiased
edge pixels carry exactly this information. The coverage map is enlarged with bicubic interpolation (4x for
images up to 1024 px, less for larger ones, so the work stays near 4096 px) and thresholded at one half. The
contour of that mask follows the true edge to within a fraction of a source pixel.

For several colours each enlarged pixel goes to the nearest colour. Larger layers sit underneath, and each lower
layer is grown slightly under the layers above it so no hairline of background shows where two colours meet.

**Circles first.** In each layer, enclosed holes and separate parts whose bounding box is close to square are
fitted with a least-squares circle. If no edge point strays more than 0.6 px or 6% of the radius from it, the
shape becomes an exact circle. Radii that differ by less than 0.6 px or about 5% are grouped and set to the
group's median, so dots that are meant to match do match.

**Lines and curves.** Every other contour is split by direction. Distances below are in source pixels; the code
scales them by the working factor.

1. The contour is smoothed (Gaussian, 2.5 px) only to measure its direction at each point.
2. Points whose direction is within 3 degrees of a multiple of `--snap` get that angle as their key; others get
   no key.
3. Consecutive points with the same key form a run. A keyed run longer than 10 px becomes a line candidate.
4. The candidate is fitted with a line at exactly the snapped angle, through the mean offset of its middle three
   quarters. It is accepted when no point strays more than 0.6 px or 1.2% of the run's length, whichever is
   larger. The length-based allowance is what straightens a long line that bows by a pixel or two, which is
   common in generated artwork, while a real curve that only passes through the angle is rejected.
5. Everything else is a curve, and neighbouring curve pieces are merged.
6. A short curve (under 9 px) between two lines that meet at a real angle is the bitmap's rounding of a sharp
   corner, so it is dropped and the two lines meet at their exact intersection.
7. Curves are smoothed lightly and their ends are eased onto the neighbouring lines over 6 px, so a curve joins a
   line without a step.
8. Curves are then simplified to straight segments within 0.08 px of the smoothed edge.

**Output.** Each layer is one path: line corners, curve points and circles as two arcs, all with even-odd fill
so holes are subpaths rather than masks. Coordinates are divided back to source pixels, so the vector overlays
the source exactly, and the `viewBox` is the logo's bounding box.

**Tuning.** The thresholds (3 degrees, 10 px, 0.6 px or 1.2%, 9 px, 6 px) are in `rebuild()` and were set on
real generated and exported logos. If a mark has intentional angles that are not on a regular grid, use
`--snap 0`: lines are then kept as traced and only smoothed.

## 2. Comparing

`compare.py` swaps the SVG's `viewBox` for the source's full frame, renders it at the source size (times up to
3) and thresholds both images into ink masks. Missing ink is ink in the source but not the vector; added ink is
the reverse. Both are given as a share of the source's ink pixels. For the zoom sheet, mismatch thinner than an
antialiased edge is ignored, and up to six windows with the most remaining mismatch are shown enlarged, vector
above and source below.

A thin line of red and blue along every edge is normal; it is where the source's antialiasing is cut at a
different place than the vector's. A solid patch of red or blue is a real difference.

## 3. Auditing

`audit.py` renders the mark in black at 2400 px tall and measures the bitmap. Results are scaled to 1000 units of
logo height.

- **Holes:** connected background regions that do not touch the canvas edge. Their radius is the radius of a
  circle with the same area.
- **Stroke weights:** for each part (holes and a ring around them are masked out so rings do not distort the
  result), the skeleton is computed and the distance from each skeleton point to the nearest edge doubled. The
  median is the part's weight. Weights within 8% of each other form one tier.
- **Gaps:** the skeleton of the empty space, kept only where stepping from the nearest edge through the skeleton
  point and on by 1.15 to 1.45 times that distance meets the mark again. That leaves the narrow spaces between
  facing edges, and ignores the margin around the logo, wide open areas and the spurs a skeleton grows into
  corners. The width there is twice the distance to the edge. Spots under 70% of the median gap, or under 60% of
  the largest part's stroke weight, are marked.
- **Angles:** read from the SVG path data itself (subpaths with arcs or curves are skipped). Segments longer than
  25 units that sit between 0.05 and 5 degrees off the grid are listed.
- **Alignment:** hole centres that differ by 1 to 12 units in x or y.
- **Small sizes:** Chromium renders each size directly from the vector (not a downscaled bitmap), which is how
  browsers will show a favicon.

## 4. Rendering

All rasters come from headless Chromium through Playwright: the SVG is placed in a page at the target size and
screenshotted, with a transparent background when needed. This gives exactly what browsers show, including
antialiasing and even-odd fills, and it handles fonts for covers. PDFs are printed from the same page, so they
stay vector. The renderer is in `common.py` (`Renderer`).

## 5. Lockups and fonts

The name is not text in the SVG; it is converted to outlines with fontTools, so the files look the same on
every machine and in print. Variable fonts are instanced at the requested weight first. Letter spacing is added
per glyph. The name's cap height is matched to a share of the mark's height (36% for horizontal, 20% for
stacked), and the gap between mark and name is 30% (horizontal) or 20% (stacked) of the mark's height.

## 6. Profile pictures

Platforms crop profile pictures to a circle. A mark fits the circle when its bounding-box corners do, so the
mark is sized so that half its bounding-box diagonal is `--reach` (0.87) of the circle's radius. That leaves a
little air inside the circle and still fills a rounded square well.

## 7. Covers

Each platform has a table entry: upload size, render scale, safe area and, where the profile picture overlaps the
cover, a clear zone. The layout is plain HTML and CSS rendered by Chromium. Type sizes are set in `em` against
a unit equal to 1% of the safe area's height, and a small script in the page (it runs only in the local
renderer) reduces that unit until the copy fits its box. The guide image draws the safe area and the clear zone
over the result.

## 8. Upscaling

`upscale.py` runs Real-ESRGAN x4plus through spandrel on the CPU, in overlapping tiles so memory stays low.
Real-ESRGAN sharpens edges and fine detail well but invents blotchy texture in flat colour and soft gradients.
The hybrid step measures the source's local gradient strength, grows and softens that map, and uses it as a
blend weight: upscaled pixels where the source has detail, a plain LANCZOS enlargement where it is flat. The
blend is soft, so no seam shows.
