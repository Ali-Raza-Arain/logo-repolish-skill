# Logo audit: demo-logo.svg

Sizes are given per 1000 units of logo height (the logo is 999 units wide).

## Circles and holes
- 1 enclosed holes. Radius 57.6, spread 0.00 (identical).

## Stroke weights
| Part (bounding box, x0 y0 x1 y1) | Typical width | 10th to 90th percentile |
| --- | --- | --- |
| -2 0 997 999 | 72.5 | 69.9 to 73.1 |
| 329 628 667 737 | 53.0 | 20.2 to 53.8 |

Weight tiers: 53.0 (x1), 72.5 (x1). One or two clear tiers read as intentional; several close tiers read as inconsistent.

## Gaps
- Usual gap 85.0, narrowest 43.3. Spots under 59.5 (70% of the usual gap, or 60% of the main stroke weight if that is more): 448 skeleton pixels, shown in red in tight-gaps.png. Tight spots close up first at small sizes and in print.

## Angles
- 10 straight segments over 25 units; 0 are close to a 45 degree multiple without being on it.

## Alignment
- Circle centres that almost share a row or column (1 to 12 units apart): 0.

## Small sizes
- See small-sizes.png (each size shown 4x, pixels visible). If the detail merges below 48 px, plan a simplified mark for favicons and app icons rather than shrinking the full logo.
