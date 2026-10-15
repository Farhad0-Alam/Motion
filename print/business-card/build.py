#!/usr/bin/env python3
"""iAgentice business card: vector front/back, print-ready PDFs and proofs.

Spec (US standard): trim 3.5 x 2 in, bleed 0.125 in on every side
(document 3.75 x 2.25 in), safe zone 0.125 in inside trim. Artwork is
drawn in pixels at 300 dpi (1 pt = 4.1667 px); no text below 7 pt.

Outputs in out/:
  front.svg, back.svg         editable vector masters (fonts embedded)
  card-cmyk.pdf               print file: 2 pages, 3.75 x 2.25 in, native CMYK,
                              vector, fonts embedded, TrimBox/BleedBox set
  card-cropmarks-cmyk.pdf     same on 4.25 x 2.75 in pages with crop marks
  proof-front.png, proof-back.png   with trim (red) and safe (blue) guides
  mockup.png                  both sides as cut cards

Edit CARD below, then run: python3 build.py
"""
import base64
import os
import subprocess

import segno

from pdf_cmyk import make_pdf

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
FONTS = os.path.join(HERE, "../../videos/01-ai-receptionist/assets/fonts")
# Static 700 instance of the variable brand font: keeps it a TrueType font in the
# CMYK PDF (a variable font gets flattened to Type 3, which preflight flags).
SANS_TTF = os.path.join(HERE, "fonts/InstrumentSans-700.ttf")

# ---- Card content (placeholders marked TODO must be confirmed before print) ----
CARD = {
    "name": "Farhad Alam",                  # TODO confirm spelling
    "title": "Founder · AI Agent Engineer",  # TODO confirm
    "phone": "+1 (000) 000-0000",           # TODO real number
    "email": "hello@iagentice.com",         # TODO real address
    "web": "iagentice.com",
    "location": "Dallas · Dhaka",
    "qr": "https://iagentice.com",
}

DPI = 300
W, H = 1125, 675          # 3.75 x 2.25 in with bleed
B = 37.5                  # bleed
S = 75                    # safe inset from canvas edge (bleed + 0.125 in)
PT = DPI / 72


def font_face():
    def data(f):
        return base64.b64encode(open(os.path.join(FONTS, f), "rb").read()).decode()
    sans = base64.b64encode(open(SANS_TTF, "rb").read()).decode()
    return (
        '@font-face { font-family: "Instrument Sans"; font-weight: 700; '
        f'src: url("data:font/ttf;base64,{sans}") format("truetype"); }}\n'
        '@font-face { font-family: "IBM Plex Mono"; font-weight: 500; '
        f'src: url("data:font/woff2;base64,{data("IBMPlexMono-500.woff2")}") format("woff2"); }}\n'
        '@font-face { font-family: "IBM Plex Mono"; font-weight: 600; '
        f'src: url("data:font/woff2;base64,{data("IBMPlexMono-600.woff2")}") format("woff2"); }}\n'
        '.sans { font-family: "Instrument Sans", sans-serif; }\n'
        '.mono { font-family: "IBM Plex Mono", monospace; }\n'
    )


MARK = ('<rect width="64" height="64" rx="14" fill="{bg}" {stroke}/>'
        '<path d="M22.2 55.22V18.18h7.78L46 55.22h-8.47l-3.46-8h-4.09v8zM29.98 41h1.39l-1.39-3.23z" '
        'fill="{fg}" fill-rule="evenodd"/><circle cx="26.09" cy="9.55" r="5.52" fill="#c8f04f"/>')


def qr_path(text, size):
    q = segno.make(text, error="m")
    m = list(q.matrix)
    n = len(m)
    cell = size / n
    d = []
    for y, row in enumerate(m):
        x = 0
        while x < n:
            if row[x]:
                x0 = x
                while x < n and row[x]:
                    x += 1
                d.append(f"M{x0 * cell:.3f} {y * cell:.3f}h{(x - x0) * cell:.3f}v{cell:.3f}h{-(x - x0) * cell:.3f}z")
            else:
                x += 1
    return "".join(d), n


def front():
    fs_word = round(24 * PT)   # 24 pt wordmark
    fs_tag = round(7.5 * PT)   # 7.5 pt tagline
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="3.75in" height="2.25in" viewBox="0 0 {W} {H}">
  <defs>
    <style>{font_face()}</style>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#171d20"/><stop offset="1" stop-color="#0d1113"/>
    </linearGradient>
    <radialGradient id="glow" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0" stop-color="#c8f04f" stop-opacity="0.18"/><stop offset="1" stop-color="#c8f04f" stop-opacity="0"/>
    </radialGradient>
    <pattern id="grid" width="75" height="75" patternUnits="userSpaceOnUse" x="{B}" y="{B}">
      <path d="M75 0H0V75" fill="none" stroke="#ffffff" stroke-opacity="0.045" stroke-width="1.5"/>
    </pattern>
  </defs>
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <rect width="{W}" height="{H}" fill="url(#grid)"/>
  <!-- gnomon: the sundial blade leans 23.4 degrees, Earth's axial tilt (brand detail) -->
  <circle cx="230" cy="190" r="260" fill="url(#glow)"/>
  <g transform="translate(1080 640) rotate(-23.4)">
    <line x1="0" y1="0" x2="0" y2="-440" stroke="#c8f04f" stroke-opacity="0.55" stroke-width="3"/>
  </g>
  <!-- mark + wordmark, vertically centred on the trim -->
  <g transform="translate(150 207) scale(4)">{MARK.format(bg="#101215", fg="#f3f4f1", stroke='stroke="#ffffff" stroke-opacity="0.22" stroke-width="0.6"')}</g>
  <text x="440" y="356" class="sans" font-weight="700" font-size="{fs_word}" fill="#f3f6f1" letter-spacing="-2">iAgentice</text>
  <text x="444" y="422" class="mono" font-weight="500" font-size="{fs_tag}" fill="#b9c3ba" letter-spacing="3">WORK THAT NEVER SLEEPS.</text>
</svg>'''


def back():
    qsize = 270                      # 0.9 in QR (scans reliably above ~0.8 in)
    qd, _ = qr_path(CARD["qr"], qsize)
    fs_name = round(15 * PT)         # 15 pt
    fs_title = round(7.5 * PT)       # 7.5 pt
    fs_row = round(8 * PT)           # 8 pt
    rows = [("T", CARD["phone"]), ("E", CARD["email"]), ("W", CARD["web"]), ("L", CARD["location"])]
    row_svg = ""
    y0 = 400
    for i, (k, v) in enumerate(rows):
        y = y0 + i * 52
        row_svg += (f'<text x="{S + 15}" y="{y}" class="mono" font-weight="600" font-size="{fs_row}" fill="#5f6b61">{k}</text>'
                    f'<text x="{S + 60}" y="{y}" class="mono" font-weight="500" font-size="{fs_row}" fill="#12171a">{v}</text>')
    qx, qy = W - S - 15 - qsize, 150
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="3.75in" height="2.25in" viewBox="0 0 {W} {H}">
  <defs><style>{font_face()}</style></defs>
  <rect width="{W}" height="{H}" fill="#f3f4f1"/>
  <!-- lime edge: a thin band that bleeds off the bottom -->
  <rect x="0" y="{H - B - 16}" width="{W}" height="{B + 16}" fill="#c8f04f"/>
  <g transform="translate({S + 15} {S + 15}) scale(1.05)">{MARK.format(bg="#12171a", fg="#f3f4f1", stroke="")}</g>
  <text x="{S + 15}" y="262" class="sans" font-weight="700" font-size="{fs_name}" fill="#12171a" letter-spacing="-1">{CARD["name"]}</text>
  <text x="{S + 17}" y="312" class="mono" font-weight="500" font-size="{fs_title}" fill="#4a554c" letter-spacing="1">{CARD["title"].upper()}</text>
  <line x1="{S + 15}" y1="342" x2="{S + 115}" y2="342" stroke="#12171a" stroke-width="3"/>
  {row_svg}
  <g transform="translate({qx} {qy})">
    <rect x="-18" y="-18" width="{qsize + 36}" height="{qsize + 36}" rx="18" fill="#ffffff"/>
    <path d="{qd}" fill="#12171a"/>
  </g>
  <text x="{qx + qsize / 2}" y="{qy + qsize + 58}" text-anchor="middle" class="mono" font-weight="500" font-size="{round(7 * PT)}" fill="#4a554c" letter-spacing="1">SCAN · {CARD["web"].upper()}</text>
</svg>'''


def chrome():
    base = "/root/.cache/hyperframes/chrome/chrome-headless-shell"
    v = sorted(os.listdir(base))[-1]
    return f"{base}/{v}/chrome-headless-shell-linux64/chrome-headless-shell"


def png(svg_path, out):
    subprocess.run([chrome(), "--headless", "--no-sandbox", "--hide-scrollbars", "--disable-gpu",
                    f"--window-size={W},{H}", "--virtual-time-budget=3000", f"--screenshot={out}",
                    f"file://{svg_path}"], check=True, capture_output=True)


def main():
    os.makedirs(OUT, exist_ok=True)
    sides = {"front": front(), "back": back()}
    for name, svg in sides.items():
        p = os.path.join(OUT, f"{name}.svg")
        open(p, "w", encoding="utf-8").write(svg)
        # Proof: px-sized copy so the screenshot is exactly 1125 x 675, then draw guides.
        px = os.path.join(OUT, f".{name}-px.svg")
        open(px, "w", encoding="utf-8").write(svg.replace('width="3.75in" height="2.25in"', f'width="{W}" height="{H}"'))
        raw = os.path.join(OUT, f".{name}.png")
        png(px, raw)
        subprocess.run(["magick", raw, "-fill", "none", "-stroke", "#ff2d55", "-strokewidth", "2",
                        "-draw", f"rectangle {B},{B} {W - B},{H - B}", "-stroke", "#2d7dff",
                        "-draw", f"stroke-dasharray 10 8 rectangle {S},{S} {W - S},{H - S}",
                        os.path.join(OUT, f"proof-{name}.png")], check=True)
    # Print files: drawn natively in CMYK (see pdf_cmyk.py), not converted from RGB.
    matrix = [list(r) for r in segno.make(CARD["qr"], error="m").matrix]
    make_pdf(os.path.join(OUT, "card-cmyk.pdf"), CARD, matrix, W, H, B, S)
    make_pdf(os.path.join(OUT, "card-cropmarks-cmyk.pdf"), CARD, matrix, W, H, B, S, marks=True)
    # Mockup: cut both cards to trim and lay them on a surface.
    cards = []
    for name in ("front", "back"):
        cut = os.path.join(OUT, f".{name}-cut.png")
        subprocess.run(["magick", os.path.join(OUT, f".{name}.png"), "-crop", f"{W - 2 * B:.0f}x{H - 2 * B:.0f}+{B:.0f}+{B:.0f}",
                        "+repage", "-resize", "700x", cut], check=True)
        cards.append(cut)
    subprocess.run(["magick", "-size", "1600x900", "radial-gradient:#3a4046-#1a1d20",
                    "(", cards[0], "-background", "none", "-rotate", "-5",
                    "(", "+clone", "-background", "black", "-shadow", "60x18+0+22", ")", "+swap",
                    "-background", "none", "-layers", "merge", "+repage", ")", "-geometry", "+70+140", "-composite",
                    "(", cards[1], "-background", "none", "-rotate", "4",
                    "(", "+clone", "-background", "black", "-shadow", "60x18+0+22", ")", "+swap",
                    "-background", "none", "-layers", "merge", "+repage", ")", "-geometry", "+820+380", "-composite",
                    os.path.join(OUT, "mockup.png")], check=True)
    for f in os.listdir(OUT):
        if f.startswith("."):
            os.remove(os.path.join(OUT, f))
    todo = [k for k, v in CARD.items() if "000" in v or k in ("name", "title", "email")]
    print("built:", ", ".join(sorted(os.listdir(OUT))))
    print("confirm before print:", ", ".join(todo))


if __name__ == "__main__":
    main()
