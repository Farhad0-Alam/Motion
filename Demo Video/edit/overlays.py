"""Overlay + subtitle layer for the 30 s 'World's Most Expensive Cities' demo.

Writes raw RGBA 1920x1080 @ 24 fps to stdout (pipe into ffmpeg), or with
--preview t1,t2,... writes PNGs of the layer at those times to argv[2].
"""
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS, DUR = 1920, 1080, 24, 30.0
HERE = os.path.dirname(os.path.abspath(__file__))
F = lambda name, size: ImageFont.truetype(os.path.join(HERE, "fonts", name), size)

WHITE = (255, 255, 255)
GOLD = (243, 207, 138)
MX = 120  # left safe margin

# ---------- timing (timeline seconds, from Vosk word timings) ----------
SUBS = [
    (0.05, 2.60, "Fifty-four thousand dollars a year."),
    (2.95, 4.35, "For one bedroom."),
    (4.60, 6.60, "That's roughly the average annual rent"),
    (6.63, 8.66, "for a city-centre one-bedroom flat"),
    (8.66, 9.65, "in New York."),
    (9.90, 11.40, "Before bills."),
    (11.50, 12.85, "Before food."),
    (12.94, 15.05, "Before you've even stepped outside."),
    (15.30, 17.04, "From Dubai's Burj Khalifa"),
    (17.04, 18.50, "to the streets of London,"),
    (18.54, 19.95, "we're counting down ten"),
    (19.95, 22.15, "of the world's most expensive cities —"),
    (22.28, 25.30, "and showing you what the money actually buys."),
]
TAGS = [  # location supers
    (0.35, 4.15, "NEW YORK", "UNITED STATES"),
    (9.95, 14.90, "MIDTOWN MANHATTAN", "NEW YORK"),
    (15.35, 21.90, "DUBAI", "UNITED ARAB EMIRATES"),
    (22.45, 25.10, "LONDON", "UNITED KINGDOM"),
]
HOOK = (0.20, 4.30)     # $54,000 / YEAR
MONTH = (4.62, 9.55)    # ≈ $4,500 / MONTH
TITLE = (25.30, 30.0)   # end title


# ---------- helpers ----------
def ease_out(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


def ease_io(x):
    x = min(max(x, 0.0), 1.0)
    return 3 * x * x - 2 * x * x * x


def env(t, a, b, fin=0.35, fout=0.30):
    """0..1 visibility envelope with eased fade in/out."""
    if t < a or t > b:
        return 0.0
    return min(ease_out((t - a) / fin), ease_io((b - t) / fout))


_cache = {}


def text_img(text, font, fill=WHITE, track=0, shadow=0.55, blur=7, oy=3):
    """Tight RGBA text with letter-spacing and a soft drop shadow."""
    key = (text, font.path, font.size, fill, track, shadow, blur, oy)
    if key in _cache:
        return _cache[key]
    asc, desc = font.getmetrics()
    widths = [font.getlength(c) for c in text]
    tw = int(sum(widths) + track * max(len(text) - 1, 0))
    pad = blur * 3
    im = Image.new("L", (tw + pad * 2, asc + desc + pad * 2), 0)
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
    arr[..., 3] = (arr[..., 3].astype(np.float32) * a).astype(np.uint8)
    return Image.fromarray(arr)


def put(canvas, ti, x, y, a, anchor="l"):
    """Place text so its ink box starts at x (or centres on x) with top at y."""
    im, pad, _ = ti
    if a <= 0.003:
        return
    w = im.width - pad * 2
    px = x - pad if anchor == "l" else int(x - w / 2 - pad)
    canvas.alpha_composite(fade(im, a), (int(px), int(y - pad)))


def text_w(ti):
    return ti[0].width - ti[1] * 2


def rect(canvas, x, y, w, h, color, a):
    if a <= 0.003 or w <= 0:
        return
    r = Image.new("RGBA", (max(int(w), 1), h), color + (int(255 * a),))
    canvas.alpha_composite(r, (int(x), int(y)))


def grad_left(max_a, reach):
    xs = np.linspace(0, 1, W, dtype=np.float32)
    g = np.clip(1 - xs / reach, 0, 1) ** 1.6 * max_a
    a = np.repeat(g[None, :], H, 0)
    arr = np.zeros((H, W, 4), np.uint8)
    arr[..., 3] = (a * 255).astype(np.uint8)
    return Image.fromarray(arr)


def grad_v(max_a, reach, top=True):
    ys = np.linspace(0, 1, H, dtype=np.float32)
    ys = ys if top else ys[::-1]
    g = np.clip(1 - ys / reach, 0, 1) ** 1.5 * max_a
    arr = np.zeros((H, W, 4), np.uint8)
    arr[..., 3] = (np.repeat(g[:, None], W, 1) * 255).astype(np.uint8)
    return Image.fromarray(arr)


def corner_glow(max_a, rx, ry):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - MX) / rx) ** 2 + ((yy - 110) / ry) ** 2)
    g = np.clip(1 - d, 0, 1) ** 1.4 * max_a
    arr = np.zeros((H, W, 4), np.uint8)
    arr[..., 3] = (g * 255).astype(np.uint8)
    return Image.fromarray(arr)


SCRIM_L = grad_left(0.70, 0.66)
SCRIM_TAG = corner_glow(0.62, 620, 190)
SCRIM_TOP = grad_v(0.66, 0.50, top=True)
SCRIM_BOT = grad_v(0.38, 0.26, top=False)


# ---------- elements ----------
def draw_tag(c, t):
    for a0, b0, big, small in TAGS:
        a = env(t, a0, b0, 0.45, 0.35)
        if a <= 0:
            continue
        c.alpha_composite(fade(SCRIM_TAG, a))
        slide = (1 - ease_out((t - a0) / 0.6)) * -24
        y = 92
        bar = ease_out((t - a0) / 0.5) * 34
        rect(c, MX + slide, y + 6, bar, 3, GOLD, a)
        put(c, text_img(big, F("Montserrat-700.ttf", 26), track=7), MX + 50 + slide, y - 6, a)
        put(c, text_img(small, F("Montserrat-500.ttf", 17), fill=(225, 225, 225), track=5),
            MX + 50 + slide, y + 30, a * 0.85)


def draw_hook(c, t):
    a0, b0 = HOOK
    a = env(t, a0, b0, 0.35, 0.30)
    if a <= 0:
        return
    c.alpha_composite(fade(SCRIM_L, a))
    y0 = 360
    put(c, text_img("AVERAGE ANNUAL RENT", F("Montserrat-700.ttf", 25), fill=GOLD, track=6, shadow=0.8), MX, y0, a)
    # count-up synced to "Fifty-four thousand dollars" (0.06–1.53 s)
    k = ease_out((t - 0.25) / 1.35)
    val = int(round(54000 * k / 100.0)) * 100
    num = text_img(f"${val:,}", F("Montserrat-800.ttf", 172), blur=10, shadow=0.6, oy=5)
    rise = (1 - ease_out((t - a0) / 0.5)) * 18
    put(c, num, MX - 6, y0 + 34 + rise, a)
    nw = text_w(text_img("$54,000", F("Montserrat-800.ttf", 172)))
    yr_a = a * ease_out((t - 1.45) / 0.35)
    put(c, text_img("/ YEAR", F("Montserrat-700.ttf", 46), track=3), MX + nw + 22, y0 + 128, yr_a)
    # "FOR ONE BEDROOM." lands with the spoken words (3.06 s)
    ba = a * ease_out((t - 2.98) / 0.35)
    wipe = ease_out((t - 2.98) / 0.45)
    rect(c, MX, y0 + 262, 400 * wipe, 4, GOLD, ba)
    put(c, text_img("FOR ONE BEDROOM.", F("Montserrat-700.ttf", 42), track=5), MX, y0 + 284, ba)


def draw_month(c, t):
    a0, b0 = MONTH
    a = env(t, a0, b0, 0.35, 0.30)
    if a <= 0:
        return
    c.alpha_composite(fade(SCRIM_L, a))
    y0 = 330
    put(c, text_img("$54,000 ÷ 12 MONTHS", F("Montserrat-700.ttf", 26), fill=GOLD, track=5, shadow=0.8), MX, y0, a)
    rise = (1 - ease_out((t - a0) / 0.5)) * 18
    na = a * ease_out((t - 4.85) / 0.4)
    approx = text_img("≈", F("Montserrat-700.ttf", 110), fill=(235, 235, 235))
    put(c, approx, MX - 4, y0 + 66 + rise, na)
    ax = MX + text_w(approx) + 18
    num = text_img("$4,500", F("Montserrat-800.ttf", 156), blur=10, shadow=0.6, oy=5)
    put(c, num, ax, y0 + 40 + rise, na)
    ma = a * ease_out((t - 5.15) / 0.35)
    put(c, text_img("/ MONTH", F("Montserrat-700.ttf", 44), track=3), ax + text_w(num) + 22, y0 + 128, ma)
    la = a * ease_out((t - 6.65) / 0.4)   # with "city-centre one-bedroom"
    rect(c, MX, y0 + 250, 380 * ease_out((t - 6.65) / 0.5), 4, GOLD, la)
    put(c, text_img("City-centre 1-bedroom average", F("Montserrat-500.ttf", 34)), MX, y0 + 272, la)
    put(c, text_img("Source: Numbeo, Oct 2026 · rounded estimate", F("Inter-600.ttf", 23),
                    fill=(230, 230, 230), shadow=0.9, blur=4, oy=2), MX, y0 + 326, la * 0.9)


TITLE_L1 = "THE WORLD'S MOST"
TITLE_L2 = "EXPENSIVE CITIES"


def draw_title(c, t):
    a0, b0 = TITLE
    if t < a0:
        return
    a = ease_out((t - a0) / 0.6)
    c.alpha_composite(fade(SCRIM_TOP, a))
    # tracking settles from wide to tight
    k = ease_out((t - a0) / 1.4)
    trk = int(round(34 - 28 * k))
    put(c, text_img("COUNTDOWN  ·  TOP 10", F("Montserrat-700.ttf", 26), fill=GOLD, track=int(14 - 4 * k), shadow=0.8),
        W / 2, 96, a, anchor="c")
    f = F("Montserrat-800.ttf", 92)
    put(c, text_img(TITLE_L1, f, track=trk, blur=12, shadow=0.65, oy=5), W / 2, 140, a, anchor="c")
    a2 = ease_out((t - a0 - 0.18) / 0.6)
    put(c, text_img(TITLE_L2, f, track=trk, blur=12, shadow=0.65, oy=5), W / 2, 246, a2, anchor="c")
    rw = 520 * ease_out((t - a0 - 0.35) / 0.9)
    rect(c, W / 2 - rw / 2, 372, rw, 4, GOLD, a2)


def draw_subs(c, t):
    for a0, b0, s in SUBS:
        a = env(t, a0, b0, 0.12, 0.12)
        if a <= 0:
            continue
        c.alpha_composite(fade(SCRIM_BOT, a * 0.9))
        ti = text_img(s, F("Inter-600.ttf", 46), shadow=0.85, blur=5, oy=2)
        put(c, ti, W / 2, H - 140, a, anchor="c")


def frame(t):
    c = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_hook(c, t)
    draw_month(c, t)
    draw_title(c, t)
    draw_tag(c, t)
    draw_subs(c, t)
    return c


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--preview":
        out = sys.argv[3]
        for ts in sys.argv[2].split(","):
            frame(float(ts)).save(os.path.join(out, f"ov_{float(ts):06.2f}.png"))
    else:
        o = sys.stdout.buffer
        for i in range(int(DUR * FPS)):
            o.write(frame(i / FPS).tobytes())
