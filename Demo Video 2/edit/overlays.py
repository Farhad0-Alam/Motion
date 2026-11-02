"""WOW-grade Overlay + Subtitle Renderer for '/root/Motion/Demo Video 2' (30.0s @ 24fps).

Strictly edits Marked 1 -> Marked 2 -> Marked 3 into a 30.0-second 1080p master:
  - Shot 1 (0.00 - 5.96s): Marked 1 Shot A (NYC Skyline aerial glide)
  - Shot 2 (5.96 - 9.96s): Marked 1 Shot B (Minimalist NYC 1-bedroom apartment interior)
  - Shot 3 (9.96 - 15.92s): Marked 2 Shot A (High-altitude Midtown Manhattan skyline)
  - Shot 4 (15.92 - 20.04s): Marked 2 Shot B (Sunlit furnished NYC 1-bedroom living room)
  - Shot 5 (20.04 - 24.00s): Marked 3 Shot A (Sweeping East River & Empire State skyline)
  - Shot 6 (24.00 - 30.00s): Marked 3 Shot B (Luxury high-floor Manhattan apartment + End Title)

Typography (per shwbster brief):
  - Montserrat headings & figures (Montserrat-800, Montserrat-700, Montserrat-500)
  - Clean white Inter subtitles (Inter-600, Inter-400)
  - Required figures & labels:
      * "$54,000 / YEAR"
      * "≈ $4,500 / MONTH"
      * "City-centre 1-bedroom average"
      * "Numbeo, Oct 2026 - rounded estimate"
      * "The World's 10 Most Expensive Cities to Live In"
"""
import sys
import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS, DUR = 1920, 1080, 24, 30.0
HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, "fonts")
F = lambda name, size: ImageFont.truetype(os.path.join(FONT_DIR, name), size)

WHITE = (255, 255, 255)
OFF_WHITE = (232, 236, 242)
MUTED = (195, 204, 216)
GOLD = (243, 207, 138)
GOLD_BRIGHT = (255, 223, 158)
DARK_GLASS = (10, 14, 22)
MX = 116  # left safe margin

# ---------- Subtitles synced to the unified 30s timeline ----------
SUBS = [
    (1.05, 2.25, "New York City —"),
    (2.45, 5.20, "a place defined by its iconic skyline."),
    (6.35, 7.30, "For millions,"),
    (7.45, 9.65, "this is where the modern dream begins."),
    (10.30, 12.15, "Fifty-four thousand dollars a year."),
    (12.55, 14.30, "For one bedroom."),
    (16.05, 18.00, "That's roughly the average annual rent"),
    (18.05, 19.90, "for a city-centre one-bedroom flat"),
    (20.05, 21.85, "in New York."),
]

# ---------- Top-left location supers ----------
TAGS = [
    (0.35, 5.65, "NEW YORK CITY", "MANHATTAN SKYLINE  ·  40.7484° N"),
    (6.15, 9.65, "MIDTOWN MANHATTAN", "1-BEDROOM RESIDENCE  ·  INTERIOR"),
    (10.15, 15.65, "BILLIONAIRES' ROW & MIDTOWN", "ANNUAL HOUSING COST INDEX"),
    (16.10, 19.80, "NEW YORK CITY CENTRE", "ILLUSTRATIVE 1-BEDROOM FLAT"),
    (20.20, 23.75, "LOWER & MIDTOWN MANHATTAN", "EAST RIVER AERIAL CORRIDOR"),
]

HOOK_WIN = (10.15, 15.70)    # $54,000 / YEAR graphic
MONTH_WIN = (16.05, 23.75)   # ≈ $4,500 / MONTH + City-centre 1-bedroom average + Numbeo credit
TITLE_WIN = (24.15, 30.00)   # The World's 10 Most Expensive Cities to Live In


# ---------- Easing & Envelope Helpers ----------
def ease_out(x):
    x = min(max(x, 0.0), 1.0)
    return 1.0 - (1.0 - x) ** 3


def ease_io(x):
    x = min(max(x, 0.0), 1.0)
    return 3.0 * x * x - 2.0 * x * x * x


def env(t, a, b, fin=0.35, fout=0.30):
    if t < a or t > b:
        return 0.0
    return min(ease_out((t - a) / fin), ease_io((b - t) / fout))


_cache = {}


def text_img(text, font, fill=WHITE, track=0, shadow=0.60, blur=7, oy=3):
    key = (text, font.path, font.size, fill, track, shadow, blur, oy)
    if key in _cache:
        return _cache[key]
    asc, desc = font.getmetrics()
    widths = [font.getlength(c) for c in text]
    tw = int(sum(widths) + track * max(len(text) - 1, 0))
    pad = max(blur * 3, 12)
    im = Image.new("L", (max(tw + pad * 2, 4), max(asc + desc + pad * 2, 4)), 0)
    d = ImageDraw.Draw(im)
    x = pad
    for c, w in zip(text, widths):
        d.text((x, pad), c, font=font, fill=255)
        x += w + track
    sh = im.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(v * shadow))
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    shadow_layer = Image.new("RGBA", im.size, (0, 0, 0, 255))
    shadow_layer.putalpha(sh)
    out.alpha_composite(shadow_layer, (0, oy))
    col = Image.new("RGBA", im.size, fill + (255,))
    col.putalpha(im)
    out.alpha_composite(col)
    res = (out, pad, asc)
    _cache[key] = res
    return res


def fade(im, a):
    if a >= 0.999:
        return im
    arr = np.array(im)
    arr[..., 3] = (arr[..., 3].astype(np.float32) * max(min(a, 1.0), 0.0)).astype(np.uint8)
    return Image.fromarray(arr)


def put(canvas, ti, x, y, a, anchor="l"):
    im, pad, _ = ti
    if a <= 0.003:
        return
    w = im.width - pad * 2
    if anchor == "l":
        px = x - pad
    elif anchor == "c":
        px = int(x - w / 2 - pad)
    else:
        px = int(x - w - pad)
    canvas.alpha_composite(fade(im, a), (int(px), int(y - pad)))


def text_w(ti):
    return ti[0].width - ti[1] * 2


def rect(canvas, x, y, w, h, color, a):
    if a <= 0.003 or w <= 0 or h <= 0:
        return
    r = Image.new("RGBA", (max(int(w), 1), max(int(h), 1)), color + (int(255 * min(max(a, 0.0), 1.0)),))
    canvas.alpha_composite(r, (int(x), int(y)))


def rounded_pill(canvas, x, y, w, h, radius, fill_rgb, fill_a, border_rgb=None, border_a=0.0):
    if fill_a <= 0.003 and border_a <= 0.003:
        return
    w, h = max(int(w), 4), max(int(h), 4)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    fill_col = fill_rgb + (int(255 * min(max(fill_a, 0.0), 1.0)),)
    outline_col = (border_rgb + (int(255 * min(max(border_a, 0.0), 1.0)),)) if border_rgb and border_a > 0.003 else None
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=radius, fill=fill_col, outline=outline_col, width=2 if outline_col else 0)
    canvas.alpha_composite(im, (int(x), int(y)))


def grad_left(max_a, reach):
    xs = np.linspace(0, 1, W, dtype=np.float32)
    g = np.clip(1 - xs / reach, 0, 1) ** 1.65 * max_a
    a = np.repeat(g[None, :], H, 0)
    arr = np.zeros((H, W, 4), np.uint8)
    arr[..., 3] = (a * 255).astype(np.uint8)
    return Image.fromarray(arr)


def grad_v(max_a, reach, top=True):
    ys = np.linspace(0, 1, H, dtype=np.float32)
    ys = ys if top else ys[::-1]
    g = np.clip(1 - ys / reach, 0, 1) ** 1.55 * max_a
    arr = np.zeros((H, W, 4), np.uint8)
    arr[..., 3] = (np.repeat(g[:, None], W, 1) * 255).astype(np.uint8)
    return Image.fromarray(arr)


def corner_glow(max_a, rx, ry):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - MX) / rx) ** 2 + ((yy - 104) / ry) ** 2)
    g = np.clip(1 - d, 0, 1) ** 1.45 * max_a
    arr = np.zeros((H, W, 4), np.uint8)
    arr[..., 3] = (g * 255).astype(np.uint8)
    return Image.fromarray(arr)


# Light, localized scrims so footage stays bright and clearly visible
SCRIM_L = grad_left(0.58, 0.60)
SCRIM_TAG = corner_glow(0.52, 580, 175)
SCRIM_TOP = grad_v(0.60, 0.56, top=True)
SCRIM_BOT = grad_v(0.42, 0.24, top=False)


# ---------- Visual Layers ----------
def draw_tag(c, t):
    for a0, b0, big, small in TAGS:
        a = env(t, a0, b0, 0.40, 0.32)
        if a <= 0:
            continue
        c.alpha_composite(fade(SCRIM_TAG, a))
        slide = (1.0 - ease_out((t - a0) / 0.55)) * -22
        y = 82
        # Vertical gold accent bar
        bar_h = int(52 * ease_out((t - a0) / 0.45))
        rect(c, MX + slide, y, 4, bar_h, GOLD, a)
        put(c, text_img(big, F("Montserrat-700.ttf", 24), track=6, shadow=0.75), MX + 20 + slide, y - 4, a)
        put(c, text_img(small, F("Montserrat-500.ttf", 15), fill=OFF_WHITE, track=4, shadow=0.75),
            MX + 20 + slide, y + 29, a * 0.88)


def draw_opening_badge(c, t):
    """Subtle editorial kicker during Shots 1 & 2 (0.8s - 9.6s) so opening visuals feel luxury-branded."""
    a = env(t, 0.85, 9.55, 0.50, 0.40)
    if a <= 0:
        return
    # Top-right minimal index pill
    pw, ph = 310, 44
    px, py = W - MX - pw, 82
    rounded_pill(c, px, py, pw, ph, 22, DARK_GLASS, a * 0.58, GOLD, a * 0.45)
    # Pulsing gold dot
    dot_a = a * (0.65 + 0.35 * math.sin(t * 4.0))
    rounded_pill(c, px + 18, py + 16, 12, 12, 6, GOLD_BRIGHT, dot_a)
    put(c, text_img("COST OF LIVING INDEX · 2026", F("Montserrat-700.ttf", 14), fill=OFF_WHITE, track=2, shadow=0.4),
        px + 42, py + 13, a * 0.95)


def draw_hook(c, t):
    """Shot 3 (10.15s - 15.70s): Bold figure '$54,000 / YEAR' + 'FOR ONE BEDROOM.'"""
    a0, b0 = HOOK_WIN
    a = env(t, a0, b0, 0.35, 0.30)
    if a <= 0:
        return
    c.alpha_composite(fade(SCRIM_L, a))
    y0 = 340

    # Kicker pill
    rounded_pill(c, MX, y0 - 8, 392, 40, 8, DARK_GLASS, a * 0.62, GOLD, a * 0.50)
    put(c, text_img("AVERAGE ANNUAL RENT  ·  NYC", F("Montserrat-700.ttf", 18), fill=GOLD_BRIGHT, track=4, shadow=0.6),
        MX + 18, y0, a)

    # Smooth count-up from $0 to $54,000 synced to "Fifty-four thousand dollars a year" (10.30 - 11.75s)
    k = ease_out((t - 10.25) / 1.35)
    val = int(round(54000 * k / 100.0)) * 100
    num = text_img(f"${val:,}", F("Montserrat-800.ttf", 164), blur=10, shadow=0.68, oy=5)
    rise = (1.0 - ease_out((t - a0) / 0.50)) * 18
    put(c, num, MX - 6, y0 + 42 + rise, a)

    nw = text_w(text_img("$54,000", F("Montserrat-800.ttf", 164)))
    yr_a = a * ease_out((t - 11.40) / 0.35)
    put(c, text_img("/ YEAR", F("Montserrat-700.ttf", 46), fill=GOLD_BRIGHT, track=3), MX + nw + 22, y0 + 132, yr_a)

    # "FOR ONE BEDROOM." lands cleanly with the spoken words at 12.55s
    ba = a * ease_out((t - 12.50) / 0.35)
    wipe = ease_out((t - 12.50) / 0.45)
    rect(c, MX, y0 + 266, 430 * wipe, 4, GOLD, ba)
    put(c, text_img("FOR ONE BEDROOM.", F("Montserrat-700.ttf", 40), track=5), MX, y0 + 286, ba)


def draw_month(c, t):
    """Shots 4 & 5 (16.05s - 23.75s): '≈ $4,500 / MONTH' + 'City-centre 1-bedroom average' + Numbeo credit."""
    a0, b0 = MONTH_WIN
    a = env(t, a0, b0, 0.35, 0.30)
    if a <= 0:
        return
    c.alpha_composite(fade(SCRIM_L, a))
    y0 = 316

    # Top calculation tag
    rounded_pill(c, MX, y0 - 8, 360, 40, 8, DARK_GLASS, a * 0.62, GOLD, a * 0.50)
    put(c, text_img("$54,000  ÷  12 MONTHS", F("Montserrat-700.ttf", 18), fill=GOLD_BRIGHT, track=4, shadow=0.6),
        MX + 18, y0, a)

    rise = (1.0 - ease_out((t - a0) / 0.50)) * 18
    na = a * ease_out((t - 16.15) / 0.40)
    approx = text_img("≈", F("Montserrat-700.ttf", 108), fill=OFF_WHITE)
    put(c, approx, MX - 4, y0 + 68 + rise, na)
    ax = MX + text_w(approx) + 18

    # Count-up from $0 to $4,500 over 0.9s
    km = ease_out((t - 16.15) / 0.95)
    mval = int(round(4500 * km / 50.0)) * 50
    num = text_img(f"${mval:,}", F("Montserrat-800.ttf", 152), blur=10, shadow=0.68, oy=5)
    put(c, num, ax, y0 + 42 + rise, na)

    nw_fixed = text_w(text_img("$4,500", F("Montserrat-800.ttf", 152)))
    ma = a * ease_out((t - 16.65) / 0.35)
    put(c, text_img("/ MONTH", F("Montserrat-700.ttf", 44), fill=GOLD_BRIGHT, track=3),
        ax + nw_fixed + 22, y0 + 128, ma)

    # Smaller label: "City-centre 1-bedroom average" (synced to "for a city-centre one-bedroom flat" at 18.0s)
    la = a * ease_out((t - 17.65) / 0.40)
    rect(c, MX, y0 + 252, 460 * ease_out((t - 17.65) / 0.50), 4, GOLD, la)
    put(c, text_img("City-centre 1-bedroom average", F("Montserrat-500.ttf", 34), fill=WHITE),
        MX, y0 + 272, la)

    # Required small source credit: "Numbeo, Oct 2026 - rounded estimate"
    sa = a * ease_out((t - 18.25) / 0.45)
    rounded_pill(c, MX, y0 + 332, 488, 42, 10, DARK_GLASS, sa * 0.68, GOLD, sa * 0.38)
    rounded_pill(c, MX + 16, y0 + 348, 10, 10, 5, GOLD, sa)
    put(c, text_img("Source: Numbeo, Oct 2026 - rounded estimate", F("Inter-600.ttf", 21),
                    fill=OFF_WHITE, shadow=0.75, blur=4, oy=2), MX + 36, y0 + 340, sa * 0.96)


def draw_title(c, t):
    """Shot 6 (24.15s - 30.00s): Full video title 'The World's 10 Most Expensive Cities to Live In'."""
    a0, b0 = TITLE_WIN
    if t < a0:
        return
    a = ease_out((t - a0) / 0.65)
    c.alpha_composite(fade(SCRIM_TOP, a))

    # Subtle glass card behind title block at top-center so luxury apartment interior below stays bright & visible
    card_w, card_h = 1360, 340
    rounded_pill(c, (W - card_w) // 2, 72, card_w, card_h, 24, DARK_GLASS, a * 0.56, GOLD, a * 0.42)

    k = ease_out((t - a0) / 1.35)
    trk = int(round(26 - 20 * k))

    put(c, text_img("GLOBAL RANKING  ·  TOP 10 COUNTDOWN", F("Montserrat-700.ttf", 22),
                    fill=GOLD_BRIGHT, track=int(10 - 3 * k), shadow=0.8),
        W / 2, 102, a, anchor="c")

    f_main = F("Montserrat-800.ttf", 76)
    put(c, text_img("THE WORLD'S 10 MOST", f_main, track=trk, blur=11, shadow=0.70, oy=4),
        W / 2, 146, a, anchor="c")

    a2 = ease_out((t - a0 - 0.18) / 0.60)
    put(c, text_img("EXPENSIVE CITIES TO LIVE IN", F("Montserrat-800.ttf", 64),
                    fill=WHITE, track=max(trk - 2, 4), blur=11, shadow=0.70, oy=4),
        W / 2, 240, a2, anchor="c")

    rw = 560 * ease_out((t - a0 - 0.35) / 0.85)
    rect(c, W / 2 - rw / 2, 336, rw, 4, GOLD, a2)

    a3 = ease_out((t - a0 - 0.45) / 0.60)
    put(c, text_img("REAL RENTS   ·   COST BREAKDOWNS   ·   WHAT YOUR MONEY BUYS",
                    F("Inter-600.ttf", 19), fill=OFF_WHITE, track=4, shadow=0.7),
        W / 2, 356, a3 * 0.92, anchor="c")


def draw_subs(c, t):
    """Clean white Inter-style subtitles at bottom center."""
    for a0, b0, s in SUBS:
        a = env(t, a0, b0, 0.12, 0.12)
        if a <= 0:
            continue
        c.alpha_composite(fade(SCRIM_BOT, a * 0.85))
        ti = text_img(s, F("Inter-600.ttf", 44), fill=WHITE, shadow=0.88, blur=5, oy=2)
        sw = text_w(ti)
        # Subtle dark translucent pill behind subtitle for 100% legibility over bright windows
        rounded_pill(c, (W - sw) / 2 - 28, H - 144, sw + 56, 68, 14, DARK_GLASS, a * 0.48)
        put(c, ti, W / 2, H - 134, a, anchor="c")


def frame(t):
    c = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_opening_badge(c, t)
    draw_hook(c, t)
    draw_month(c, t)
    draw_title(c, t)
    draw_tag(c, t)
    draw_subs(c, t)
    return c


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--preview":
        out = sys.argv[3]
        os.makedirs(out, exist_ok=True)
        for ts in sys.argv[2].split(","):
            frame(float(ts)).save(os.path.join(out, f"ov_{float(ts):06.2f}.png"))
    else:
        o = sys.stdout.buffer
        for i in range(int(DUR * FPS)):
            o.write(frame(i / FPS).tobytes())

