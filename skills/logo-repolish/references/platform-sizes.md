# Platform sizes

Sizes and crop behaviour as of late 2026. Platforms change these from time to time: if an upload looks cropped,
check the platform's own help page and adjust `PLATFORMS` in `covers.py`.

## Website

| File | Size | Notes |
|---|---|---|
| favicon.svg | scalable | rounded square, modern browsers |
| favicon-32.png, favicon-48.png | 32, 48 | classic tab icons; 48 is what Google Search shows |
| favicon.ico | 16 to 64 | old browsers and tools that request /favicon.ico |
| apple-touch-icon.png | 180 | full square, no transparency; iOS rounds the corners itself |
| icon-192.png, icon-512.png | 192, 512 | web app manifest |
| icon-maskable-512.png | 512 | Android adaptive icon; the mark within the central 80% |
| logo-512.png | 512 | Organization logo in structured data (at least 112 px, square works everywhere) |
| og-image | 1200 x 630 | link previews; keep text and the mark in the central 1080 x 566 |
| header logo | SVG | give the img width and height attributes matching the viewBox ratio to avoid layout shift |

## Profile pictures

All platforms crop to a circle or a rounded square. `profiles.py` keeps the mark inside the circle (reach 0.87).

| Platform | Upload | Shown as |
|---|---|---|
| LinkedIn company | 400 x 400 or larger | square with rounded corners |
| LinkedIn personal | 400 x 400 or larger | circle |
| X | 400 x 400 | circle (square for some business accounts) |
| Facebook, Instagram, Threads | 320 or larger, 1080 recommended | circle |
| YouTube | 800 x 800 | circle |
| GitHub | 500 x 500 or larger | circle for users, rounded square for organisations |
| WhatsApp, Telegram, Slack, Teams | 512 or larger | circle or rounded square |

## Covers and banners

| Platform | Upload | Safe area and overlaps |
|---|---|---|
| LinkedIn company | 1128 x 191 | the company logo overlaps the lower left; keep the left 25 to 28% clear |
| LinkedIn personal | 1584 x 396 | the profile photo overlaps the lower left; keep the left 27 to 30% clear |
| X | 1500 x 500 | the photo overlaps the lower left; phones trim about 60 px top and bottom |
| Facebook page | 1640 x 624 (shown 820 x 312) | phones show the middle only; keep content in the central 76% |
| YouTube | 2560 x 1440 | only the central 1546 x 423 shows on every device; TVs show all of it |

Upload PNG for flat graphics and text (no JPEG artefacts around letters); JPEG at quality 95 where a platform
recompresses PNG badly. `covers.py` writes both, plus a 2x PNG for platforms that accept larger files.

## Print and documents

- Give printers the vector PDF or SVG, never a PNG. The PDFs from `export_kit.py` are RGB; for offset print the
  printer converts to CMYK or matches a spot colour from the hex value. Ask them for a proof when the colour matters.
- Letterheads, invoices, slide decks: the horizontal lockup on light, PNG at 2400 px wide or the SVG.
- Email signatures: PNG at 2x the display size (for example 400 x 100 shown at 200 x 50); many email apps block SVG.
- Embroidery and engraving: the one-colour versions and the simplified small mark if there is one.
