"""Render Shot 5 (5.75s @ 24fps, 1920x1080): Animated Editorial World Map with 10 ECA Ranked Cities.
Uses Public Domain Natural Earth ne_110m_land.geojson with 2x supersampled anti-aliasing.
"""
import json
import math
import os
import subprocess
from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1080
SW, SH = W * 2, H * 2  # 2x supersampling for crisp vector coastlines
FPS = 24
FRAMES = 140  # 5.83s (trimmed to exact 134 frames = 5.583s in master concat)

GEOJSON = "/root/Motion/shwbster_order/assets/ne_110m_land.geojson"
FONT_DIR = "/root/Motion/shwbster_order/opening_edit/fonts"
OUT_MP4 = "/root/Motion/shwbster_order/assets/shot5_world_map_eca.mp4"
PREVIEW_PNG = "/root/Motion/shwbster_order/opening_edit/preview/map_test.png"

# Exact GPS (lon, lat) of the 10 ECA 2026 ranked cities in countdown order (#10 -> #1)
CITIES = [
    ("#10 Dubai", 55.2708, 25.2048, (14, -22)),
    ("#9 San Francisco", -122.4194, 37.7749, (-158, -14)),
    ("#8 Singapore", 103.8198, 1.3521, (14, 6)),
    ("#7 Bern", 7.4474, 46.9480, (-68, 12)),
    ("#6 Tel Aviv", 34.7818, 32.0853, (14, 4)),
    ("#5 Hong Kong", 114.1694, 22.3193, (14, -10)),
    ("#4 Zurich", 8.5417, 47.3769, (12, -26)),
    ("#3 London", -0.1276, 51.5072, (-92, -24)),
    ("#2 Geneva", 6.1432, 46.2044, (-88, -4)),
    ("#1 New York", -74.0060, 40.7128, (14, -12)),
]


def proj(lon, lat):
    """Clean editorial Robinson-like cropped projection focused on populated latitudes (-48..74)."""
    # Map lon [-165..165] -> [0..SW], lat [74..-48] -> [0..SH]
    x = (lon + 165.0) / 330.0 * SW
    # Slight cosine latitude compression toward poles for natural globe proportions
    y = (74.0 - lat) / 122.0 * SH
    return x, y


def build_base_map():
    base = Image.new("RGB", (SW, SH), (15, 25, 40))
    d = ImageDraw.Draw(base)

    # Subtle radial ocean luminance so map looks bright, editorial, and clean (Economist/FT dark-slate style)
    yy, xx = None, None
    import numpy as np
    arr = np.zeros((SH, SW, 3), dtype=np.uint8)
    gy = np.linspace(-1, 1, SH, dtype=np.float32)[:, None]
    gx = np.linspace(-1, 1, SW, dtype=np.float32)[None, :]
    glow = np.clip(1.0 - 0.55 * (gx * gx * 0.7 + gy * gy), 0.25, 1.0)
    arr[..., 0] = (14 + 18 * glow).astype(np.uint8)
    arr[..., 1] = (26 + 30 * glow).astype(np.uint8)
    arr[..., 2] = (44 + 46 * glow).astype(np.uint8)
    base = Image.fromarray(arr, "RGB")
    d = ImageDraw.Draw(base)

    # Subtle latitude/longitude graticule grid
    grid_col = (42, 64, 92)
    for lon in range(-150, 160, 30):
        x0, y0 = proj(lon, 72)
        x1, y1 = proj(lon, -46)
        d.line([(x0, y0), (x1, y1)], fill=grid_col, width=2)
    for lat in range(-30, 75, 15):
        x0, y0 = proj(-162, lat)
        x1, y1 = proj(162, lat)
        d.line([(x0, y0), (x1, y1)], fill=grid_col, width=2)

    # Draw Natural Earth continents
    geo = json.load(open(GEOJSON))
    land_fill = (54, 78, 108)
    land_edge = (92, 126, 165)

    for feat in geo["features"]:
        geom = feat["geometry"]
        polys = [geom["coordinates"]] if geom["type"] == "Polygon" else geom["coordinates"]
        for poly in polys:
            exterior = poly[0]
            if len(exterior) < 3:
                continue
            pts = [proj(lon, lat) for lon, lat in exterior]
            d.polygon(pts, fill=land_fill, outline=land_edge)
            d.line(pts + [pts[0]], fill=land_edge, width=3)

    return base.resize((W, H), Image.Resampling.LANCZOS)


def ease_out(x):
    x = min(max(x, 0.0), 1.0)
    return 1.0 - (1.0 - x) ** 3


def main():
    os.makedirs(os.path.dirname(PREVIEW_PNG), exist_ok=True)
    base = build_base_map()
    f_lbl = ImageFont.truetype(os.path.join(FONT_DIR, "Montserrat-600.ttf"), 17)

    cmd = [
        "ffmpeg", "-v", "error", "-y",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p",
        OUT_MP4
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)

    city_px = [(name, proj(lon, lat)[0] / 2.0, proj(lon, lat)[1] / 2.0, off) for name, lon, lat, off in CITIES]

    for i in range(FRAMES):
        t = i / FPS
        canvas = base.copy().convert("RGBA")
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)

        # Draw curved connecting arcs progressively between cities
        for idx in range(len(city_px) - 1):
            t_start = 0.25 + idx * 0.34
            p = ease_out((t - t_start) / 0.55)
            if p <= 0:
                continue
            _, x0, y0, _ = city_px[idx]
            _, x1, y1, _ = city_px[idx + 1]
            mx, my = (x0 + x1) / 2.0, (y0 + y1) / 2.0 - 48.0
            steps = max(int(28 * p), 2)
            pts = []
            for s in range(steps + 1):
                u = (s / 28.0)
                if u > p:
                    u = p
                bx = (1 - u) ** 2 * x0 + 2 * (1 - u) * u * mx + u ** 2 * x1
                by = (1 - u) ** 2 * y0 + 2 * (1 - u) * u * my + u ** 2 * y1
                pts.append((bx, by))
            if len(pts) >= 2:
                d.line(pts, fill=(243, 207, 138, 125), width=2)

        # Draw glowing city markers & crisp mini tags
        for idx, (name, cx, cy, (ox, oy)) in enumerate(city_px):
            t_appear = 0.15 + idx * 0.34
            a = ease_out((t - t_appear) / 0.38)
            if a <= 0:
                continue
            # Expanding pulse ring
            pulse = ((t - t_appear) * 0.9) % 1.0
            pr = 7 + 18 * pulse
            pa = int(170 * (1.0 - pulse) * a)
            d.ellipse([cx - pr, cy - pr, cx + pr, cy + pr], outline=(255, 220, 145, pa), width=2)

            # Outer halo + core gold pin
            d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=(243, 207, 138, int(90 * a)))
            d.ellipse([cx - 4.5, cy - 4.5, cx + 4.5, cy + 4.5], fill=(255, 232, 175, int(255 * a)))

            # Compact label pill for key non-overlapping cities (or gentle staggered fade)
            # Note: Bern/Zurich/Geneva are close in Switzerland, so show clean combined/staggered offsets
            if name in ("#4 Zurich", "#2 Geneva"):
                # Keep Swiss cluster clean — dot pulses for all 3, label "#7 Bern · #4 Zurich · #2 Geneva" cleanly or small offset
                continue
            lbl_text = "#7 Bern · #4 Zurich · #2 Geneva" if name == "#7 Bern" else name
            tw = int(f_lbl.getlength(lbl_text))
            lx, ly = int(cx + ox), int(cy + oy)
            d.rounded_rectangle([lx - 7, ly - 3, lx + tw + 7, ly + 23], radius=6,
                                fill=(10, 16, 28, int(195 * a)), outline=(243, 207, 138, int(110 * a)), width=1)
            d.text((lx, ly), lbl_text, font=f_lbl, fill=(245, 248, 252, int(245 * a)))

        canvas.alpha_composite(ov)

        # Subtle slow cinematic camera push-in (1.00x -> 1.065x centered slightly toward Atlantic/Europe/ME)
        z = 1.0 + 0.065 * (t / (FRAMES / FPS))
        cw, ch = int(W / z), int(H / z)
        cx_cam = W * 0.51
        cy_cam = H * 0.46
        x0 = max(0, min(W - cw, int(cx_cam - cw / 2)))
        y0 = max(0, min(H - ch, int(cy_cam - ch / 2)))
        framed = canvas.convert("RGB").crop((x0, y0, x0 + cw, y0 + ch)).resize((W, H), Image.Resampling.BILINEAR)

        if i == 96:
            framed.save(PREVIEW_PNG)
        proc.stdin.write(framed.tobytes())

    proc.stdin.close()
    proc.wait()
    print("Rendered:", OUT_MP4, os.path.getsize(OUT_MP4))


if __name__ == "__main__":
    main()

