# 3D, metallic and photographic logos

A 3D render (bevels, metal shine, reflections, soft shadows) cannot be turned into an exact vector. Its value is in
the shading, and every shortcut that "cleans it up" destroys that. These rules keep it intact.

## Contents
1. What never to do
2. Ask for the flat source first
3. Making the most of the raster
4. Backgrounds and themes
5. Transparent versions
6. From a 2D master to a new 3D render

## 1. What never to do

- Never posterize or trace a 3D render into flat vector shapes. The result loses the metal shine and gradients and
  looks like a cheap copy of the original.
- Never cut the logo out of its background with a threshold, colour key or quick mask. Shadows, glow and reflections
  are mixed into the background pixels; cutting leaves halos, jagged edges and half-transparent glitches.
- Never recolour, tint or "correct" the metal. Colour belongs to the owner.
- Never redraw or regenerate it with an image generator, and never upload it to any online service, design tool,
  image host or artifact to process it. All work stays on the local machine.
- Never paste a 3D render onto a light background with re-created shadows: the shading was lit for the original
  background, and re-grounded shadows look dirty.

## 2. Ask for the flat source first

Almost every 3D logo was made from a flat drawing, or has a flat version somewhere (the designer's file, an earlier
draft, the outline the generator was given). Ask for it before anything else. With a flat source:
- `vectorize.py` gives an exact master vector, which becomes the main logo for the site, favicon, profiles and print;
- the 3D render stays as a showpiece: hero images, covers, presentation slides, merchandise mock-ups.

If there is truly no flat version, offer to draw one by vectorizing the render's silhouette as a starting point,
and say clearly that it is a new 2D design for the owner to approve, not a copy.

## 3. Making the most of the raster

- Work from the largest, least compressed file. A PNG beats a JPEG; the original export beats a screenshot.
- Small renders (1024 px and under) can be enlarged 4x with `upscale.py`. The default hybrid mode takes the
  upscaler's output only where the image has detail (edges, shine) and a plain enlargement in flat areas, because the
  upscaler invents blotchy texture in smooth backgrounds and gradients. Check the result at 100% around the edges and
  in the background before using it.
- Generator watermarks and badges are the owner's question: ask, and work only on artwork they own.
- Crop and frame with the background intact: square for profiles, the logo centred with even margins.

## 4. Backgrounds and themes

- A render belongs on its own background or one that continues it (same colour, same lighting direction). A dark
  metallic render goes on dark grounds.
- For light themes use the flat 2D mark, not the render.
- When an extended canvas is needed (a wide cover from a square render), extend the background by sampling its edge
  colour and fade the render into it with a wide soft mask, never a hard cut.

## 5. Transparent versions

If a transparent PNG of the render is really needed:
- keep only the logo body (the metal), with the shadow and glow removed, and soften its edge by a pixel or two;
- the edge pixels still carry the original background's colour, so label the file "for dark backgrounds" and show
  it on dark, light and mid-grey before handing it over;
- if the edges look wrong on light grounds, do not try to fix it with more masking. Use the 2D mark there.

## 6. From a 2D master to a new 3D render

This skill does not render 3D. When the owner wants a fresh 3D version of an approved 2D mark, the clean route is:
import the master SVG into Blender (File, Import, Scalable Vector Graphics), convert to mesh, extrude, bevel the
edges, give it a metallic material with the owner's colour as base colour, light it with an HDRI and render on the
background the logo will live on. The result can then be framed and exported with the steps above.
