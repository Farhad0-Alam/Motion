"""Generate Main Thumbnail ('$54,000 A YEAR / FOR ONE BEDROOM') + A/B Alternative ('$4,500 A MONTH / ONE BEDROOM').

Strictly follows Part 4 of shwbster's brief:
  - Licensed New York apartment interior (Pexels 5824189) as main image
  - Recognisable Manhattan skyline (Pexels 11471275) as smaller second element (upper-right inset card with gold border)
  - Hero text: "$54,000 A YEAR" (A/B: "$4,500 A MONTH")
  - Supporting text: "FOR ONE BEDROOM" (A/B: "ONE BEDROOM")
  - Small "NYC central average" label
  - Bottom-right kept completely clear for the YouTube duration timestamp
"""
import os
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

W, H = 1920, 1080
HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, "fonts")
OUT_DIR = "/root/youtubeai/shwbster"
os.makedirs(OUT_DIR, exist_ok=True)

F = lambda name, size: ImageFont.truetype(os.path.join(FONT_DIR, name), size)
WHITE = (255, 255, 255)
GOLD = (243, 207, 138)
GOLD_BRIGHT = (255, 224, 160)
DARK = (10, 15, 24)


def draw_tracked(canvas, text, font, x, y, fill=WHITE, track=0, shadow=0.85, blur=10, oy=5):
    asc, desc = font.getmetrics()
    widths = [font.getlength(c) for c in text]
    tw = int(sum(widths) + track * max(len(text) - 1, 0))
    pad = blur * 3
    im = Image.new("L", (tw + pad * 2, asc + desc + pad * 2), 0)
    d = ImageDraw.Draw(im)
    cx = pad
    for c, w in zip(text, widths):
        d.text((cx, pad), c, font=font, fill=255)
        cx += w + track
    sh = im.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(v * shadow))
    sh_rgba = Image.new("RGBA", im.size, (0, 0, 0, 255))
    sh_rgba.putalpha(sh)
    canvas.alpha_composite(sh_rgba, (int(x - pad), int(y - pad + oy)))
    fg = Image.new("RGBA", im.size, fill + (255,))
    fg.putalpha(im)
    canvas.alpha_composite(fg, (int(x - pad), int(y - pad)))
    return tw


def build_thumb(hero_text, support_text, out_prefix):
    apt_frame = "/tmp/thumb_apt.png"
    sky_frame = "/tmp/thumb_sky.png"
    if not os.path.exists(apt_frame):
        subprocess.run([
            "ffmpeg", "-v", "error", "-y", "-ss", "2.5",
            "-i", "/root/Motion/shwbster_order/assets/shot1_nyc_apt_5824189.mp4",
            "-frames:v", "1", "-vf", "scale=1920:1080", apt_frame
        ], check=True)
    if not os.path.exists(sky_frame):
        subprocess.run([
            "ffmpeg", "-v", "error", "-y", "-ss", "3.0",
            "-i", "/root/Motion/shwbster_order/assets/shot2_manhattan_11471275.mp4",
            "-frames:v", "1", "-vf", "scale=1920:1080", sky_frame
        ], check=True)

    # 1. Main background: bright, crisp licensed NYC apartment interior
    bg = Image.open(apt_frame).convert("RGB")
    bg = ImageEnhance.Contrast(bg).enhance(1.08)
    bg = ImageEnhance.Color(bg).enhance(1.10)
    bg = ImageEnhance.Brightness(bg).enhance(1.04)
    canvas = bg.convert("RGBA")

    # 2. Localized dark scrim on the left/lower-left behind the typography only (leaving right side & bottom-right clean)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    scrim_l = np.clip(1.0 - (xx / 1280.0), 0.0, 1.0) ** 1.35 * 0.72
    scrim_b = np.clip((yy - 320.0) / 760.0, 0.0, 1.0) ** 1.2 * 0.45 * np.clip(1.0 - (xx / 1450.0), 0.0, 1.0)
    alpha = np.clip(scrim_l + scrim_b, 0.0, 0.80)
    scrim = np.zeros((H, W, 4), dtype=np.uint8)
    scrim[..., 0] = 8
    scrim[..., 1] = 12
    scrim[..., 2] = 20
    scrim[..., 3] = (alpha * 255).astype(np.uint8)
    canvas.alpha_composite(Image.fromarray(scrim))

    # 3. Smaller second element: recognisable Manhattan skyline inset card in upper-right
    #    (Positioned at y=68..438 so bottom-right y=440..1080 stays 100% clear for YouTube timestamp!)
    iw, ih = 620, 350
    ix, iy = W - iw - 78, 68
    sky = Image.open(sky_frame).convert("RGB")
    sky = ImageEnhance.Contrast(sky).enhance(1.12)
    sky = ImageEnhance.Color(sky).enhance(1.15)
    sky_crop = sky.resize((iw, ih), Image.Resampling.LANCZOS)

    # Drop shadow + rounded gold frame for the Manhattan skyline inset
    shadow_box = Image.new("RGBA", (iw + 60, ih + 60), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow_box)
    sd.rounded_rectangle([24, 28, iw + 36, ih + 40], radius=22, fill=(0, 0, 0, 195))
    shadow_box = shadow_box.filter(ImageFilter.GaussianBlur(14))
    canvas.alpha_composite(shadow_box, (ix - 30, iy - 24))

    mask = Image.new("L", (iw, ih), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, iw - 1, ih - 1], radius=18, fill=255)
    inset_rgba = sky_crop.convert("RGBA")
    inset_rgba.putalpha(mask)
    canvas.alpha_composite(inset_rgba, (ix, iy))

    border_im = Image.new("RGBA", (iw, ih), (0, 0, 0, 0))
    bd = ImageDraw.Draw(border_im)
    bd.rounded_rectangle([0, 0, iw - 1, ih - 1], radius=18, outline=GOLD + (255,), width=5)
    canvas.alpha_composite(border_im, (ix, iy))

    # 4. Small "NYC central average" pill label above the hero text
    lx, ly = 92, 470
    pill = Image.new("RGBA", (420, 58), (0, 0, 0, 0))
    pd = ImageDraw.Draw(pill)
    pd.rounded_rectangle([0, 0, 419, 57], radius=14, fill=(12, 18, 28, 225), outline=GOLD + (230,), width=3)
    pd.rectangle([18, 12, 24, 45], fill=GOLD + (255,))
    canvas.alpha_composite(pill, (lx, ly))
    draw_tracked(canvas, "NYC central average", F("Montserrat-600.ttf", 28), lx + 38, ly + 11, fill=GOLD_BRIGHT, track=1, shadow=0.6, blur=4, oy=2)

    # 5. Hero text group 1: "$54,000 A YEAR" (or "$4,500 A MONTH")
    hero_font = F("Montserrat-600.ttf", 122 if len(hero_text) <= 14 else 114)
    draw_tracked(canvas, hero_text, hero_font, 92, 548, fill=WHITE, track=2, shadow=0.92, blur=14, oy=6)

    # Gold accent bar separating Hero Text and Supporting Text
    bar = Image.new("RGBA", (920, 8), GOLD + (255,))
    canvas.alpha_composite(bar, (96, 706))

    # 6. Supporting text group 2: "FOR ONE BEDROOM" (or "ONE BEDROOM")
    sup_font = F("Montserrat-600.ttf", 84)
    draw_tracked(canvas, support_text, sup_font, 92, 732, fill=GOLD_BRIGHT, track=4, shadow=0.90, blur=12, oy=5)

    out_png = os.path.join(OUT_DIR, f"{out_prefix}_1920x1080.png")
    out_jpg = os.path.join(OUT_DIR, f"{out_prefix}_1280x720_YouTube.jpg")
    canvas.convert("RGB").save(out_png, quality=95)
    canvas.convert("RGB").resize((1280, 720), Image.Resampling.LANCZOS).save(out_jpg, quality=92)
    print(f"Saved {out_png} + {out_jpg}")


def main():
    build_thumb("$54,000 A YEAR", "FOR ONE BEDROOM", "Thumbnail_Main_54000_A_Year")
    build_thumb("$4,500 A MONTH", "ONE BEDROOM", "Thumbnail_AB_4500_A_Month")


if __name__ == "__main__":
    main()
