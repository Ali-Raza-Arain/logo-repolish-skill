# Design rules for a logo mark

What a careful mark designer checks, how `audit.py` measures it, and how to talk about it with the owner.
The audit reports facts. Whether a finding is a flaw or a deliberate choice is the owner's call, so present
findings as questions with a proposed fix, and change nothing about the shape until they agree.

## Contents
1. Geometry
2. Stroke weight
3. Gaps and counters
4. Repeated elements
5. Alignment
6. Small sizes
7. Clear space and minimum size
8. Colour and contrast
9. Reading audit.md

## 1. Geometry

- Straight lines are exactly straight. Artwork from image generators and quick raster drawings bow by a pixel or two
  over long runs; `vectorize.py` fits each run over its whole length so it comes out straight.
- Lines sit on an angle grid, usually 45 degrees (0, 45, 90, 135). Some marks use 30 or 60 (isometric) or 15:
  pass `--snap 30` or `--snap 15` to both `vectorize.py` and `audit.py`. A line 1 to 3 degrees off the grid reads as
  a mistake; one 10 degrees off reads as intent.
- Corners where two lines meet are sharp at the exact intersection, unless the design rounds them on purpose. A
  rounded corner should use one radius across the mark, or a small set of radii that relate (for example inner
  radius = outer radius minus stroke weight).
- Curves are smooth with no kinks, and meet lines tangentially when the design intends a smooth join.
- Round shapes overshoot slightly. A circle next to a square of the same height looks smaller, so designers make it
  about 1 to 3% larger. Do not "correct" an overshoot back to the grid.

## 2. Stroke weight

- Parts that should look equally heavy have the same measured width, within about 3%.
- Most well-built marks use one to three weight tiers (for example main strokes, secondary strokes, hairlines).
  The audit groups measured widths into tiers; a part that sits between two tiers is the usual suspect.
- Horizontal strokes are often made 5 to 10% thinner than vertical ones so they look equal (the eye sees horizontals
  as heavier). A difference of that size between horizontals and verticals is likely deliberate.
- Diagonals at 45 degrees measured perpendicular to the stroke should match the verticals they are meant to match.

## 3. Gaps and counters

- Gaps (the space between separate shapes) of the same kind should be equal. A gap much tighter than the rest
  fills in at small sizes and in print (ink spread), and the audit marks it in `tight-gaps.png`.
- Rule of thumb: no gap or counter narrower than about 60% of the main stroke weight if the mark has to work as a
  favicon or on embroidery and screen print.
- Counters (enclosed holes, like the inside of an O or B) need enough area to stay open at 16 to 32 px.

## 4. Repeated elements

- Elements that look the same (dots, holes, nodes, terminals) should be identical in size and shape. The vectorizer
  groups round holes and dots of nearly the same radius and makes them exactly equal (it prints the groups); the
  audit reports whether the enclosed holes are identical.
- Repeated spacing (a row of dots, parallel lines) should be even.

## 5. Alignment

- Centres and edges either line up exactly or are clearly offset. A miss of 0.5 to 2% of the mark's size looks like
  an error. The audit lists hole centres that nearly share a row or column; check other parts by eye on the large
  render. For each, propose aligning or ask whether the offset is intended.
- Optical centre: a mark often looks centred when its visual mass sits slightly above the geometric centre. Check
  by eye at the end, not only by numbers.

## 6. Small sizes

- `small-sizes.png` shows the mark at 16, 24, 32, 48, 64 and 128 px in its own colours on white, enlarged 4x
  so each pixel is visible.
- At 16 to 32 px, any detail under about 1 px disappears or turns to mush. If the mark needs its details to read,
  propose a simplified version for favicons and tiny avatars: fewer elements, thicker strokes, larger gaps. That is
  a new design asset, so make it only when the owner asks, and keep the full mark for everything else.
- Thin strokes in the 1.5 to 3 px range at the target size cause blur at uneven positions; at 32 px and up this is
  rarely a problem.

## 7. Clear space and minimum size

- Clear space: the empty margin no other element may enter. A common unit is a quarter or a third of the mark's
  height, or the width of its main stroke times two. The kit's square versions use 12% per side (`--margin`).
- Minimum size: the smallest height at which the full mark still reads, found from `small-sizes.png`. Typically
  24 px on screen and 8 to 10 mm in print for a simple mark, more for a detailed one.

## 8. Colour and contrast

- The logo's colours belong to the owner. Never change them, not even to "improve" contrast. Choose backgrounds
  that suit the colour instead, and report weak combinations.
- Graphics need a contrast of at least 3:1 against their background (WCAG 2.2, 1.4.11). Aim for 4:1 or more for a
  logo, since it often appears small. The scripts print a warning under 3:1.
- Metallic golds and other mid-tone colours sit around 7:1 on near-black and around 3:1 on white: they belong on dark
  backgrounds, and need a darker shade or the one-colour version on white. Suggest it; do not apply it unasked.
- One-colour versions (all white, all near-black) are the standard exception for embossing, stamps, single-colour
  print and busy photos. Name them clearly as one-colour versions.
- Colour palettes for profile pictures and covers: classic, restrained pairs (navy, racing green, oxblood, graphite,
  stone, cream) look professional. Neon, purple-to-cyan gradients, acid green and glowing blobs date quickly and
  look like templates.

## 9. Reading audit.md

| Section | What it means | Typical action |
|---|---|---|
| Circles and holes | the enclosed holes' sizes and whether they are identical | unify them only if the owner agrees they should match |
| Stroke weights | widths per part and the tiers they form | ask about parts between tiers |
| Gaps | spacing between shapes, the tightest marked | widen gaps under about 60% of the main stroke if the mark must work small |
| Angles | segments 0.3 to 4 degrees off the grid | snap them; usually a vectorizing artefact, not intent |
| Alignment | hole centres that miss a shared row or column by a small amount | align or confirm the offset |
| Small sizes | look at the image | propose a simplified mark only when asked |

Fixing a finding means editing the master SVG (or re-running `vectorize.py` with different settings), re-running
`compare.py` against the source to confirm nothing else moved, and re-running the audit.
