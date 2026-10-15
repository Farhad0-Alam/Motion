# iAgentice business card

Premium two-sided card: dark brand side (logo, wordmark, tagline) and a light
info side (name, title, contact, QR to iagentice.com, lime edge).

## Files (`out/`)

| File | Use |
|---|---|
| `card-cmyk.pdf` | **Send this to the printer.** 2 pages (front, back), 3.75 × 2.25 in including bleed, native CMYK, vector, fonts embedded, TrimBox and BleedBox set |
| `card-cropmarks-cmyk.pdf` | Same, on 4.25 × 2.75 in pages with crop marks, for printers that ask for marks |
| `front.svg`, `back.svg` | Editable vector masters (RGB, fonts embedded) for Figma, Illustrator or Inkscape |
| `proof-front.png`, `proof-back.png` | Proofs with the trim line (red) and safe zone (blue dashed) |
| `mockup.png` | Presentation mockup of both sides |

## Print spec

- **Size:** US standard 3.5 × 2 in (89 × 51 mm) trimmed, with 0.125 in bleed on every side.
- **Safe zone:** all text and the QR code sit 0.125 in or more inside the trim line.
- **Type:** smallest text 7 pt, all fonts embedded as TrueType.
- **Color:** native CMYK.
  - Dark side: rich black, about 240% total ink (maximum 265% on the logo tile).
  - Small text and the QR code use black ink only (no colour mix), so they stay sharp.
- **QR code:** 0.9 in, error correction level M. Verified to decode to https://iagentice.com.
- **Lime:** printed as C25 Y85. The screen lime is brighter than CMYK can reproduce.
  For the vivid version, ask the printer to run it as a Pantone spot colour, and
  pick the closest swatch from a physical Pantone book.

## Recommended print options

- **Stock:** 16 pt (about 350 gsm) or heavier, uncoated or soft-touch matte.
  Matte keeps the dark side rich without fingerprints.
- **Premium upgrades (optional):**
  - spot UV gloss on the logo tile and wordmark
  - lime painted edges
  - 32 pt duplex stock (two sheets laminated together)
- Most online printers (Moo, Vistaprint, GotPrint) accept `card-cmyk.pdf` directly.
  Upload page 1 as the front and page 2 as the back.

## Edit

Change the `CARD` details at the top of `build.py`, then run:

```
python3 build.py
```

It regenerates the SVGs, PDFs, proofs and mockup. Lines marked TODO in `CARD` are
placeholders to confirm before printing.
