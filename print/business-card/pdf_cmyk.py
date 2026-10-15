"""Native-CMYK print PDF for the business card (ReportLab).

Mirrors the geometry of the SVG masters (pixels at 300 dpi, y down) and
paints every colour as an explicit ink recipe instead of converting RGB:

  * Background: rich black, about 240% total ink (presses cap around 300%).
  * Small text and the QR code: single-ink black (K) or a K tint, so they
    stay sharp even if the press plates are slightly misregistered.
  * Lime: C25 Y85. The screen lime (#c8f04f) is outside what CMYK can print,
    so this is the closest clean process mix; for a truly vivid lime, print it
    as a Pantone spot colour (pick from a physical swatch book).
"""
import math
import os

from reportlab.lib.colors import CMYKColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

HERE = os.path.dirname(os.path.abspath(__file__))
PX = 72 / 300  # points per pixel at 300 dpi

pdfmetrics.registerFont(TTFont("Sans-Bold", os.path.join(HERE, "fonts/InstrumentSans-700.ttf")))
pdfmetrics.registerFont(TTFont("Mono-Medium", os.path.join(HERE, "fonts/IBMPlexMono-500.ttf")))
pdfmetrics.registerFont(TTFont("Mono-SemiBold", os.path.join(HERE, "fonts/IBMPlexMono-600.ttf")))


def ink(c, m, y, k):
    return CMYKColor(c / 100, m / 100, y / 100, k / 100)


RICH_TOP = ink(62, 48, 45, 78)    # 233%: lifted slate, top-left of the front
RICH_BOT = ink(60, 40, 40, 100)   # 240%: classic rich black, bottom-right
GRID = ink(61, 47, 44, 73)       # just lighter than the field: a whisper of grid
GLOW = ink(48, 30, 52, 62)        # rich black tinted towards lime
MARK_BG = ink(65, 50, 50, 100)    # 265%: logo tile, a touch deeper than the field
MARK_EDGE = ink(45, 33, 33, 62)
PAPER_INK = ink(3, 0, 4, 0)       # near-white type on the dark side
LIME = ink(25, 0, 85, 0)
PAPER = ink(2, 1, 4, 0)           # warm paper tint on the light side
K100, K70, K55, K28 = ink(0, 0, 0, 100), ink(0, 0, 0, 70), ink(0, 0, 0, 55), ink(0, 0, 0, 28)
WHITE = ink(0, 0, 0, 0)
REG = ink(100, 100, 100, 100)     # registration colour for crop marks

MARK_A = [(22.2, 55.22), (22.2, 18.18), (29.98, 18.18), (46, 55.22), (37.53, 55.22),
          (34.07, 47.22), (29.98, 47.22), (29.98, 55.22)]
MARK_HOLE = [(29.98, 41), (31.37, 41), (29.98, 37.77)]


class Art:
    """Draws in SVG-like pixel coordinates (origin top-left, y down)."""

    def __init__(self, c, w_px, h_px):
        self.c = c
        c.translate(0, h_px * PX)
        c.scale(PX, -PX)

    def rect(self, x, y, w, h, fill, r=0):
        self.c.setFillColor(fill)
        if r:
            self.c.roundRect(x, y, w, h, r, stroke=0, fill=1)
        else:
            self.c.rect(x, y, w, h, stroke=0, fill=1)

    def text(self, x, y, s, font, size, fill, spacing=0, anchor="start"):
        c = self.c
        width = pdfmetrics.stringWidth(s, font, size) + spacing * (len(s) - 1)
        if anchor == "middle":
            x -= width / 2
        c.saveState()
        c.translate(x, y)
        c.scale(1, -1)
        t = c.beginText(0, 0)
        t.setFont(font, size)
        t.setCharSpace(spacing)
        t.setFillColor(fill)
        t.textOut(s)
        c.drawText(t)
        c.restoreState()

    def mark(self, x, y, scale, tile, letter, edge=None, edge_w=0):
        c = self.c
        c.saveState()
        c.translate(x, y)
        c.scale(scale, scale)
        c.setFillColor(tile)
        if edge:
            c.setStrokeColor(edge)
            c.setLineWidth(edge_w)
        c.roundRect(0, 0, 64, 64, 14, stroke=1 if edge else 0, fill=1)
        p = c.beginPath()
        for poly in (MARK_A, MARK_HOLE):
            p.moveTo(*poly[0])
            for pt in poly[1:]:
                p.lineTo(*pt)
            p.close()
        c.setFillColor(letter)
        c.drawPath(p, stroke=0, fill=1, fillMode=0)  # even-odd: the hole stays open
        c.setFillColor(LIME)
        c.circle(26.09, 9.55, 5.52, stroke=0, fill=1)
        c.restoreState()


def draw_front(a, W, H, B, card):
    c = a.c
    # Everything on this side stays inside the bleed box.
    c.saveState()
    p = c.beginPath()
    p.rect(0, 0, W, H)
    c.clipPath(p, stroke=0, fill=0)
    c.linearGradient(0, 0, W, H, (RICH_TOP, RICH_BOT), extend=True)
    # soft lime glow behind the mark (no transparency: a clipped radial blend)
    c.saveState()
    p = c.beginPath()
    p.circle(230, 190, 260)
    c.clipPath(p, stroke=0, fill=0)
    c.radialGradient(230, 190, 260, (GLOW, ink(61, 46, 44, 82)), extend=False)
    c.restoreState()
    c.setStrokeColor(GRID)
    c.setLineWidth(1.5)
    x = B
    while x < W:
        c.line(x, 0, x, H)
        x += 75
    y = B
    while y < H:
        c.line(0, y, W, y)
        y += 75
    # gnomon at 23.4 degrees (Earth's axial tilt, from the brand's sundial)
    t = math.radians(-23.4)
    c.setStrokeColor(ink(40, 18, 62, 38))
    c.setLineWidth(3)
    c.line(1080, 640, 1080 + 440 * math.sin(t), 640 - 440 * math.cos(t))  # clears the wordmark and tagline
    a.mark(150, 207, 4, MARK_BG, PAPER_INK, MARK_EDGE, 0.6)
    a.text(440, 356, "iAgentice", "Sans-Bold", 100, PAPER_INK, spacing=-2)
    a.text(444, 422, "WORK THAT NEVER SLEEPS.", "Mono-Medium", 31, K28, spacing=3)
    c.restoreState()


def draw_back(a, W, H, B, S, card, qr_matrix):
    c = a.c
    a.rect(0, 0, W, H, PAPER)
    a.rect(0, H - B - 16, W, B + 16, LIME)
    a.mark(S + 15, S + 15, 1.05, K100, PAPER)
    a.text(S + 15, 262, card["name"], "Sans-Bold", 62, K100, spacing=-1)
    a.text(S + 17, 312, card["title"].upper(), "Mono-Medium", 31, K70, spacing=1)
    c.setStrokeColor(K100)
    c.setLineWidth(3)
    c.line(S + 15, 342, S + 115, 342)
    rows = [("T", card["phone"]), ("E", card["email"]), ("W", card["web"]), ("L", card["location"])]
    for i, (k, v) in enumerate(rows):
        y = 400 + i * 52
        a.text(S + 15, y, k, "Mono-SemiBold", 33, K55)
        a.text(S + 60, y, v, "Mono-Medium", 33, K100)
    qsize = 270
    qx, qy = W - S - 15 - qsize, 150
    a.rect(qx - 18, qy - 18, qsize + 36, qsize + 36, WHITE, r=18)
    n = len(qr_matrix)
    cell = qsize / n
    c.setFillColor(K100)
    for yy, row in enumerate(qr_matrix):
        xx = 0
        while xx < n:
            if row[xx]:
                x0 = xx
                while xx < n and row[xx]:
                    xx += 1
                c.rect(qx + x0 * cell, qy + yy * cell, (xx - x0) * cell, cell, stroke=0, fill=1)
            else:
                xx += 1
    a.text(qx + qsize / 2, qy + qsize + 58, "SCAN · " + card["web"].upper(), "Mono-Medium", 29, K70,
           spacing=1, anchor="middle")


def make_pdf(path, card, qr_matrix, W, H, B, S, marks=False):
    """W/H/B/S in pixels at 300 dpi. With marks, adds a 0.25 in slug with crop marks."""
    slug = 75 if marks else 0
    pw, ph = (W + 2 * slug) * PX, (H + 2 * slug) * PX
    c = canvas.Canvas(path, pagesize=(pw, ph), initialFontName="Mono-Medium", initialFontSize=10)
    c.setFont("Mono-Medium", 10)
    c.setTitle("iAgentice business card")
    c.setAuthor("iAgentice")
    for side in ("front", "back"):
        c.setPageSize((pw, ph))
        trim = ((slug + B) * PX, (slug + B) * PX, (slug + W - B) * PX, (slug + H - B) * PX)
        c.setTrimBox(trim)
        c.setBleedBox((slug * PX, slug * PX, (slug + W) * PX, (slug + H) * PX))
        c.setFont("Mono-Medium", 10)  # never let the default (unembedded) Helvetica into the file
        c.saveState()
        c.translate(slug * PX, slug * PX)
        a = Art(c, W, H)
        if side == "front":
            draw_front(a, W, H, B, card)
        else:
            draw_back(a, W, H, B, S, card, qr_matrix)
        c.restoreState()
        if marks:
            c.setStrokeColor(REG)
            c.setLineWidth(0.25)
            gap = 9  # points between the marks and the bleed edge
            x0, y0, x1, y1 = trim
            for x in (x0, x1):
                c.line(x, 0, x, slug * PX - gap)
                c.line(x, ph - slug * PX + gap, x, ph)
            for y in (y0, y1):
                c.line(0, y, slug * PX - gap, y)
                c.line(pw - slug * PX + gap, y, pw, y)
        c.showPage()
    c.save()
