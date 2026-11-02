"""Normalize all 71 shots to exact 24fps frame counts (totaling 11,520 frames = 480.000s) and concat."""
import json
import os
import subprocess

BASE_DIR = "/root/Motion/shwbster_order"
LOG_PATH = os.path.join(BASE_DIR, "assets/full_asset_log.json")
NORM_DIR = os.path.join(BASE_DIR, "assets/norm_shots")
OUT_BASE = os.path.join(BASE_DIR, "assets/base_71_shots_480s.mp4")
os.makedirs(NORM_DIR, exist_ok=True)


def norm_one(entry):
    s = entry["shot"]
    dur = entry["end"] - entry["start"]
    n_frames = int(round(dur * 24))
    out_mp4 = os.path.join(NORM_DIR, f"seg_{s:02d}.mp4")
    if os.path.exists(out_mp4) and os.path.getsize(out_mp4) > 20000:
        # Check if Shot 26 or 70 was updated
        if s not in (26, 70):
            return out_mp4

    lp = entry["local_path"]
    if lp == "COMPOSITE_SPLIT":
        # Shot 68 (456-462s, 6s): Split screen #1 New York vs #7 Bern
        nyc = "/root/Motion/shwbster_order/assets/shot2_manhattan_11471275.mp4"
        bern = "/root/Motion/shwbster_order/assets/shot4_bern_switzerland_3655304.mp4"
        vf = (
            "[0:v]fps=24,scale=1920:1080:force_original_aspect_ratio=increase,"
            "crop=958:1080:480:0,setsar=1[left];"
            "[1:v]fps=24,scale=1920:1080:force_original_aspect_ratio=increase,"
            "crop=958:1080:480:0,setsar=1[right];"
            "color=c=#F3CF8A:s=4x1080:r=24[div];"
            "[left][div][right]hstack=inputs=3,format=yuv420p[v]"
        )
        subprocess.run([
            "ffmpeg", "-v", "error", "-y",
            "-ss", "2.0", "-i", nyc,
            "-ss", "2.0", "-i", bern,
            "-filter_complex", vf,
            "-map", "[v]", "-frames:v", str(n_frames), "-r", "24",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-pix_fmt", "yuv420p",
            out_mp4
        ], check=True)
        return out_mp4

    if entry["id"] == "MAP_ECA_2026":
        # Shot 5: Animated World Map (loop/trim cleanly to 144 frames = 6.000s)
        vf = "fps=24,scale=1920:1080,setsar=1,format=yuv420p"
        subprocess.run([
            "ffmpeg", "-v", "error", "-y",
            "-stream_loop", "-1", "-i", lp,
            "-vf", vf, "-frames:v", str(n_frames), "-r", "24",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-pix_fmt", "yuv420p",
            out_mp4
        ], check=True)
        return out_mp4

    # Standard Pexels HD shot: gentle slow push-in or pan, bright & clear natural documentary grade
    pan_dir = 1 if (s % 2 == 1) else -1
    if pan_dir == 1:
        crop_expr = f"crop=1920:1080:48+{36.0/dur:.2f}*t:27+{18.0/dur:.2f}*t"
    else:
        crop_expr = f"crop=1920:1080:84-{36.0/dur:.2f}*t:45-{18.0/dur:.2f}*t"

    vf = (
        f"fps=24,scale=2016:1134:force_original_aspect_ratio=increase,crop=2016:1134,"
        f"{crop_expr},eq=contrast=1.03:saturation=1.05:brightness=0.01,setsar=1,format=yuv420p"
    )
    subprocess.run([
        "ffmpeg", "-v", "error", "-y",
        "-stream_loop", "-1", "-i", lp,
        "-vf", vf, "-frames:v", str(n_frames), "-r", "24",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-pix_fmt", "yuv420p",
        out_mp4
    ], check=True)
    return out_mp4


def main():
    log = json.load(open(LOG_PATH))
    concat_lines = []
    total_f = 0
    for entry in log:
        s = entry["shot"]
        dur = entry["end"] - entry["start"]
        nf = int(round(dur * 24))
        total_f += nf
        p = norm_one(entry)
        concat_lines.append(f"file '{p}'")
        if s % 10 == 0 or s == 71:
            print(f"  Normalized up to Shot {s:02d}/71 (cumulative frames={total_f})")

    concat_txt = os.path.join(NORM_DIR, "concat_list.txt")
    open(concat_txt, "w").write("\n".join(concat_lines) + "\n")
    print(f"Concatenating 71 segments ({total_f} frames = {total_f/24:.3f}s) into {OUT_BASE}...")
    subprocess.run([
        "ffmpeg", "-v", "error", "-y",
        "-f", "concat", "-safe", "0", "-i", concat_txt,
        "-c", "copy", OUT_BASE
    ], check=True)
    print(f"SUCCESS: {OUT_BASE} ready!")


if __name__ == "__main__":
    main()

