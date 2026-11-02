"""Overlay + Subtitle + SRT Generator for shwbster's Opening Approval Video (34.00s @ 24fps, 1920x1080).

Strictly follows Expensive_Cities_8_Minute_Script_and_Brief.docx:
  - Montserrat SemiBold (Montserrat-600.ttf): 64-80px headings, 88-112px hero prices (102px)
  - Inter (Inter-600.ttf): 42px white subtitles in lower safe area (~100px above bottom), short phrase groups
  - Mandatory labels:
      * "Illustrative housing footage" on housing shots where a price/housing appears
      * "Numbeo · accessed 1 Nov 2026" beside rental graphics
      * "ECA 2026 · international employees" on the map sequence
      * "1 bed · city centre · monthly" + "USD estimate"
"""
import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1920, 1080, 24
TOTAL_FRAMES = 816  # 34.000s exact
DUR = TOTAL_FRAMES / FPS

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, "fonts")
F = lambda name, size: ImageFont.truetype(os.path.join(FONT_DIR, name), size)

WHITE = (255, 255, 255)
OFF_WHITE = (232, 237, 244)
MUTED = (190, 200, 214)
GOLD = (243, 207, 138)
GOLD_BRIGHT = (255, 224, 160)
DARK_GLASS = (10, 15, 24)
MX = 108

# Frame-verified subtitle cues synced to /root/youtubeai/shwbster/Demo.wav
SUBS = [
    (0.24, 2.32, "Fifty-four thousand dollars a year."),
    (2.68, 3.62, "For one bedroom."),
    (4.45, 6.22, "That's roughly the average annual rent"),
    (6.35, 8.42, "for a city-centre one-bedroom in New York."),
    (8.85, 9.65, "Before bills."),
    (10.02, 10.76, "Before food."),
    (10.84, 12.50, "Before you've even stepped outside."),
    (13.58, 14.65, "Think Dubai is expensive?"),
    (15.18, 16.60, "Nine cities rank above it."),
    (17.02, 18.42, "And one quieter city on this list"),
    (18.46, 19.88, "has lower rent than Dubai."),
    (20.52, 21.85, "So what are you actually paying for?"),
    (22.74, 25.38, "Our ranking follows ECA International's 2026"),
    (25.44, 27.80, "cost-of-living list for international employees."),
    (28.30, 30.78, "Rent figures are Numbeo estimates for a one-bedroom,"),
    (31.05, 32.62, "in US dollars, before bills."),
]

# Discreet top-left location supers
LOC_TAGS = [
    (0.20, 6.05, "NEW YORK CITY", "1-BEDROOM APARTMENT  ·  INTERIOR"),
    (6.40, 13.05, "MANHATTAN, NEW YORK", "MIDTOWN SKYLINE"),
    (13.40, 16.80, "DUBAI, UAE", "BURJ KHALIFA SKYLINE"),
    (17.10, 22.35, "BERN, SWITZERLAND", "UNESCO OLD TOWN & AARE RIVER"),
    (28.25, 33.80, "DUBAI MARINA", "RESIDENTIAL TOWERS"),
]


def ease_out(x):
    x = min(max(x, 0.0), 1.0)
    return 1.0 - (1.0 - x) ** 3


def ease_io(x):
    x = min(max(x, 0.0), 1.0)
    return 3.0 * x * x - 2.0 * x * x * x


def env(t, a, b, fin=0.32, fout=0.28):
    if t < a or t > b:
        return 0.0
    return min(ease_out((t - a) / fin), ease_io((b - t) / fout))


_cache = {}


def text_img(text, font, fill=WHITE, track=0, shadow=0.65, blur=6, oy=3):
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
    sh_layer = Image.new("RGBA", im.size, (0, 0, 0, 255))
    sh_layer.putalpha(sh)
    out.alpha_composite(sh_layer, (0, oy))
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


def local_glow(cx, cy, rx, ry, max_a):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2)
    g = np.clip(1.0 - d, 0.0, 1.0) ** 1.5 * max_a
    arr = np.zeros((H, W, 4), np.uint8)
    arr[..., 3] = (g * 255).astype(np.uint8)
    return Image.fromarray(arr)


# Localized contrast gradients ONLY immediately behind text (per brief line 090: keep rest of frame bright & clear)
SCRIM_TAG = local_glow(260, 95, 420, 130, 0.44)
SCRIM_CARD_L = local_glow(360, 560, 560, 290, 0.48)


def draw_loc_tags(c, t):
    for a0, b0, big, small in LOC_TAGS:
        a = env(t, a0, b0, 0.35, 0.28)
        if a <= 0:
            continue
        c.alpha_composite(fade(SCRIM_TAG, a))
        slide = (1.0 - ease_out((t - a0) / 0.45)) * -18
        y = 66
        rect(c, MX + slide, y, 4, int(46 * ease_out((t - a0) / 0.40)), GOLD, a)
        put(c, text_img(big, F("Montserrat-600.ttf", 22), track=4, shadow=0.75), MX + 18 + slide, y - 3, a)
        put(c, text_img(small, F("Inter-600.ttf", 14), fill=OFF_WHITE, track=2, shadow=0.75), MX + 18 + slide, y + 26, a * 0.90)


def draw_housing_label(c, t, a0, b0):
    """Mandatory brief label: 'Illustrative housing footage' on apartment/housing shots."""
    a = env(t, a0, b0, 0.35, 0.28)
    if a <= 0:
        return
    txt = "Illustrative housing footage"
    ti = text_img(txt, F("Inter-600.ttf", 17), fill=OFF_WHITE, shadow=0.6, blur=4, oy=2)
    tw = text_w(ti)
    pw, ph = tw + 36, 36
    px, py = W - MX - pw, 66
    rounded_pill(c, px, py, pw, ph, 18, DARK_GLASS, a * 0.62, GOLD, a * 0.35)
    put(c, ti, px + 18, py + 7, a * 0.95)


def draw_shot1_annual(c, t):
    """00:00-00:06.25: Real NYC 1-bed interior | ≈ $54,000 / YEAR | Central New York 1-bed average | Numbeo credit."""
    a0, b0 = 0.20, 6.05
    a = env(t, a0, b0, 0.32, 0.28)
    if a <= 0:
        return
    draw_housing_label(c, t, a0, b0)
    c.alpha_composite(fade(SCRIM_CARD_L, a))

    # Compact glass card in lower-left above subtitle safe zone so apartment room & windows stay wide open
    cx, cy = MX, 462
    rounded_pill(c, cx, cy, 740, 250, 18, DARK_GLASS, a * 0.66, GOLD, a * 0.42)

    # Hero figure: Montserrat SemiBold 102px (within brief's 88-112px spec), count-up once then settle
    k = ease_out((t - 0.28) / 1.05)
    val = int(round(54000 * k / 100.0)) * 100
    hero_str = f"≈ ${val:,}"
    ti_num = text_img(hero_str, F("Montserrat-600.ttf", 102), fill=WHITE, shadow=0.70, blur=8, oy=3)
    put(c, ti_num, cx + 28, cy + 18, a)

    nw_final = text_w(text_img("≈ $54,000", F("Montserrat-600.ttf", 102)))
    yr_a = a * ease_out((t - 1.10) / 0.35)
    put(c, text_img("/ YEAR", F("Montserrat-600.ttf", 34), fill=GOLD_BRIGHT, track=2),
        cx + 28 + nw_final + 16, cy + 72, yr_a)

    # Divider + small label: "Central New York 1-bed average · USD estimate"
    la = a * ease_out((t - 1.45) / 0.40)
    rect(c, cx + 28, cy + 144, int(680 * ease_out((t - 1.45) / 0.50)), 3, GOLD, la * 0.85)
    put(c, text_img("Central New York 1-bed average  ·  USD estimate", F("Montserrat-600.ttf", 23), fill=WHITE),
        cx + 28, cy + 158, la)

    # Required source credit: "Numbeo · accessed 1 Nov 2026"
    put(c, text_img("Numbeo · accessed 1 Nov 2026", F("Inter-600.ttf", 18), fill=MUTED),
        cx + 28, cy + 198, la * 0.95)


def draw_shot2_monthly(c, t):
    """00:06.25-00:13.25: Manhattan skyline | ≈ $4,500 / MONTH | 1 bed · city centre · monthly | USD estimate."""
    a0, b0 = 6.38, 13.00
    a = env(t, a0, b0, 0.32, 0.28)
    if a <= 0:
        return
    c.alpha_composite(fade(SCRIM_CARD_L, a))

    cx, cy = MX, 462
    rounded_pill(c, cx, cy, 740, 250, 18, DARK_GLASS, a * 0.66, GOLD, a * 0.42)

    k = ease_out((t - 6.45) / 0.85)
    val = int(round(4500 * k / 50.0)) * 50
    ti_num = text_img(f"≈ ${val:,}", F("Montserrat-600.ttf", 102), fill=WHITE, shadow=0.70, blur=8, oy=3)
    put(c, ti_num, cx + 28, cy + 18, a)

    nw_final = text_w(text_img("≈ $4,500", F("Montserrat-600.ttf", 102)))
    ma = a * ease_out((t - 6.95) / 0.35)
    put(c, text_img("/ MONTH", F("Montserrat-600.ttf", 34), fill=GOLD_BRIGHT, track=2),
        cx + 28 + nw_final + 16, cy + 72, ma)

    # Brief's exact repeated label: "1 bed · city centre · monthly" + "USD estimate"
    la = a * ease_out((t - 7.20) / 0.40)
    rect(c, cx + 28, cy + 144, int(680 * ease_out((t - 7.20) / 0.50)), 3, GOLD, la * 0.85)
    put(c, text_img("1 bed · city centre · monthly   |   USD estimate", F("Montserrat-600.ttf", 23), fill=WHITE),
        cx + 28, cy + 158, la)
    put(c, text_img("Numbeo · accessed 1 Nov 2026  (bills extra)", F("Inter-600.ttf", 18), fill=MUTED),
        cx + 28, cy + 198, la * 0.95)


def draw_shot4_question(c, t):
    """00:16.96-00:22.50: Bern Switzerland | Brief question: WHAT DOES IT BUY?"""
    a0, b0 = 20.15, 22.38
    a = env(t, a0, b0, 0.28, 0.25)
    if a <= 0:
        return
    # Montserrat SemiBold 68px (right inside brief's 64-80px heading spec)
    ti = text_img("WHAT DOES IT BUY?", F("Montserrat-600.ttf", 68), fill=WHITE, track=3, shadow=0.75, blur=8, oy=3)
    tw = text_w(ti)
    pw, ph = tw + 84, 118
    px, py = (W - pw) // 2, 456
    rounded_pill(c, px, py, pw, ph, 20, DARK_GLASS, a * 0.68, GOLD, a * 0.55)
    put(c, ti, W / 2, py + 18, a, anchor="c")


def draw_shot5_eca(c, t):
    """00:22.50-00:28.08: Animated World Map | ECA 2026 · international employees."""
    a0, b0 = 22.65, 27.92
    a = env(t, a0, b0, 0.35, 0.28)
    if a <= 0:
        return
    px, py = MX, 58
    rounded_pill(c, px, py, 640, 108, 16, DARK_GLASS, a * 0.78, GOLD, a * 0.55)
    rect(c, px + 22, py + 22, 5, 64, GOLD, a)
    put(c, text_img("ECA 2026 · international employees", F("Montserrat-600.ttf", 28), fill=WHITE, track=1),
        px + 42, py + 20, a)
    put(c, text_img("Cost-of-living ranking across 208 global locations", F("Inter-600.ttf", 18), fill=GOLD_BRIGHT),
        px + 42, py + 62, a * 0.94)


def draw_shot6_setup_and_title(c, t):
    """00:28.08-00:34.00: Verified Dubai Marina housing | 1 bed · monthly · USD estimate + Small title reveal."""
    a0, b0 = 28.22, 33.85
    a = env(t, a0, b0, 0.35, 0.35)
    if a <= 0:
        return
    draw_housing_label(c, t, a0, b0)

    # Rental comparison method pill (lower-left above subtitles)
    cx, cy = MX, 560
    rounded_pill(c, cx, cy, 620, 134, 16, DARK_GLASS, a * 0.68, GOLD, a * 0.45)
    put(c, text_img("1 bed · monthly · USD estimate", F("Montserrat-600.ttf", 28), fill=GOLD_BRIGHT),
        cx + 26, cy + 22, a)
    put(c, text_img("Numbeo · accessed 1 Nov 2026  ·  bills extra", F("Inter-600.ttf", 19), fill=OFF_WHITE),
        cx + 26, cy + 72, a * 0.95)

    # Small title reveal (29.6s -> 33.85s) at upper-center, keeping Marina towers clearly visible
    ta = env(t, 29.60, 33.85, 0.45, 0.35)
    if ta > 0:
        tw_box, th_box = 1140, 164
        tx, ty = (W - tw_box) // 2, 148
        rounded_pill(c, tx, ty, tw_box, th_box, 20, DARK_GLASS, ta * 0.68, GOLD, ta * 0.48)
        put(c, text_img("The World's 10 Most Expensive Cities to Live In", F("Montserrat-600.ttf", 40),
                        fill=WHITE, track=1, shadow=0.75), W / 2, ty + 28, ta, anchor="c")
        rw = int(420 * ease_out((t - 29.80) / 0.65))
        rect(c, W / 2 - rw / 2, ty + 92, rw, 3, GOLD, ta)
        put(c, text_img("AND WHAT RENT ACTUALLY BUYS", F("Montserrat-600.ttf", 21),
                        fill=GOLD_BRIGHT, track=4, shadow=0.65), W / 2, ty + 108, ta * 0.95, anchor="c")


def draw_subs(c, t):
    """Inter 42px white subtitles, subtle shadow + localized dark pill, ~100px above bottom."""
    for a0, b0, s in SUBS:
        a = env(t, a0, b0, 0.10, 0.10)
        if a <= 0:
            continue
        ti = text_img(s, F("Inter-600.ttf", 42), fill=WHITE, shadow=0.88, blur=5, oy=2)
        sw = text_w(ti)
        # Bottom of pill sits at H - 86, baseline ~100px above bottom edge (per brief line 095)
        py = H - 150
        rounded_pill(c, (W - sw) / 2 - 26, py, sw + 52, 64, 12, DARK_GLASS, a * 0.56)
        put(c, ti, W / 2, py + 8, a, anchor="c")


def frame(t):
    c = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_loc_tags(c, t)
    draw_shot1_annual(c, t)
    draw_shot2_monthly(c, t)
    draw_shot4_question(c, t)
    draw_shot5_eca(c, t)
    draw_shot6_setup_and_title(c, t)
    draw_subs(c, t)
    return c


def write_srt(path):
    def fmt(sec):
        ms = int(round(sec * 1000))
        h, ms = divmod(ms, 3600000)
        m, ms = divmod(ms, 60000)
        s, ms = divmod(ms, 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

    lines = []
    for idx, (a0, b0, s) in enumerate(SUBS, 1):
        lines.append(f"{idx}\n{fmt(a0)} --> {fmt(b0)}\n{s}\n")
    open(path, "w").write("\n".join(lines))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--srt":
        write_srt(sys.argv[2])
    elif len(sys.argv) > 1 and sys.argv[1] == "--preview":
        out = sys.argv[3]
        os.makedirs(out, exist_ok=True)
        for ts in sys.argv[2].split(","):
            frame(float(ts)).save(os.path.join(out, f"ov_{float(ts):06.2f}.png"))
    else:
        o = sys.stdout.buffer
        for i in range(TOTAL_FRAMES):
            o.write(frame(i / FPS).tobytes())

