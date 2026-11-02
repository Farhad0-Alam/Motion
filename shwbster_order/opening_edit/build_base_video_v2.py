"""v2 picture edit: same 71 licensed shots, re-cut for rhythm.

Changes vs build_base_video_480s.py:
  - Internal cuts snap to the nearest narration pause (within +/-1.6 s) instead of whole seconds.
  - Chapter cuts (into each city) stay fixed and get a 0.5 s cross-dissolve.
  - Camera moves vary per shot (push-in / pull-out / pan L / pan R) via zoompan on a 4K
    intermediate, so the motion is sub-pixel smooth instead of the old stepped crop drift.
  - Subtle filmic finish: gentle contrast curve + light vignette.
Writes assets/timeline_v2.json (shot log with re-timed start/end) and assets/base_v2_480s.mp4.
"""
import json
import os
import subprocess
import sys

BASE_DIR = "/root/Motion/shwbster_order"
LOG_PATH = os.path.join(BASE_DIR, "assets/full_asset_log.json")
SUBS = os.path.join(BASE_DIR, "audio/subtitles_480s.json")
NORM_DIR = os.path.join(BASE_DIR, "assets/norm_v2")
TIMELINE = os.path.join(BASE_DIR, "assets/timeline_v2.json")
OUT_BASE = os.path.join(BASE_DIR, "assets/base_v2_480s.mp4")
FPS = 24
TOTAL = 11520
XF = 12  # dissolve frames at chapter cuts
os.makedirs(NORM_DIR, exist_ok=True)

GRADE = ("eq=contrast=1.04:saturation=1.06:brightness=0.005,"
         "curves=master='0/0.02 0.25/0.235 0.5/0.5 0.75/0.77 1/0.98',vignette=a=0.42")


def retime(log):
    subs = json.load(open(SUBS))
    pauses = [(subs[i - 1]["end"] + subs[i]["start"]) / 2 for i in range(1, len(subs))
              if subs[i]["start"] - subs[i - 1]["end"] >= 0.3]
    out = [dict(e) for e in log]
    for i in range(1, len(out)):
        if out[i]["chapter"] != out[i - 1]["chapter"]:
            continue  # chapter cuts are locked to the rank graphics
        c = float(out[i]["start"])
        lo, hi = float(out[i - 1]["start"]) + 4.0, float(out[i]["end"]) - 4.0
        cands = [p for p in pauses if abs(p - c) <= 1.6 and lo <= p <= hi]
        if cands:
            c = min(cands, key=lambda p: abs(p - c))
        f = round(c * FPS)
        out[i]["start"] = f / FPS
        out[i - 1]["end"] = f / FPS
    for e in out:
        e["frames"] = round(e["end"] * FPS) - round(e["start"] * FPS)
    assert sum(e["frames"] for e in out) == TOTAL
    return out


def move_expr(k, n):
    p = f"(on/{max(n - 1, 1)})"
    kind = k % 4
    if kind == 0:   # push-in
        return f"1.04+0.07*{p}", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    if kind == 1:   # pan right
        return "1.10", f"(iw-iw/zoom)*(0.15+0.7*{p})", "ih/2-(ih/zoom/2)"
    if kind == 2:   # pull-out
        return f"1.11-0.07*{p}", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    return "1.10", f"(iw-iw/zoom)*(0.85-0.7*{p})", "ih/2-(ih/zoom/2)"


def norm_one(e, extra):
    s = e["shot"]
    n = e["frames"] + extra
    out = os.path.join(NORM_DIR, f"seg_{s:02d}.mp4")
    if os.path.exists(out) and os.path.getsize(out) > 20000:
        return out
    lp = e["local_path"]
    enc = ["-frames:v", str(n), "-r", str(FPS), "-an", "-c:v", "libx264", "-preset", "veryfast",
           "-crf", "15", "-pix_fmt", "yuv420p", out]
    if lp == "COMPOSITE_SPLIT":
        nyc = os.path.join(BASE_DIR, "assets/shot2_manhattan_11471275.mp4")
        bern = os.path.join(BASE_DIR, "assets/shot4_bern_switzerland_3655304.mp4")
        vf = ("[0:v]fps=24,scale=1920:1080:force_original_aspect_ratio=increase,crop=958:1080:480:0,setsar=1[l];"
              "[1:v]fps=24,scale=1920:1080:force_original_aspect_ratio=increase,crop=958:1080:480:0,setsar=1[r];"
              "color=c=#F3CF8A:s=4x1080:r=24[d];[l][d][r]hstack=inputs=3," + GRADE + ",format=yuv420p[v]")
        cmd = ["ffmpeg", "-v", "error", "-y", "-ss", "2.0", "-i", nyc, "-ss", "2.0", "-i", bern,
               "-filter_complex", vf, "-map", "[v]"] + enc
    elif e["id"] == "MAP_ECA_2026":
        cmd = ["ffmpeg", "-v", "error", "-y", "-stream_loop", "-1", "-i", lp,
               "-vf", "fps=24,scale=1920:1080,setsar=1,format=yuv420p"] + enc
    else:
        z, x, y = move_expr(s, n)
        vf = (f"fps=24,scale=3840:2160:force_original_aspect_ratio=increase,crop=3840:2160,"
              f"zoompan=z='{z}':x='{x}':y='{y}':d=1:s=1920x1080:fps=24,{GRADE},setsar=1,format=yuv420p")
        cmd = ["ffmpeg", "-v", "error", "-y", "-stream_loop", "-1", "-i", lp, "-vf", vf] + enc
    subprocess.run(cmd, check=True)
    return out


def main():
    tl = retime(json.load(open(LOG_PATH)))
    json.dump(tl, open(TIMELINE, "w"), indent=1)
    chapters = []
    for e in tl:
        if not chapters or chapters[-1][0]["chapter"] != e["chapter"]:
            chapters.append([])
        chapters[-1].append(e)
    if "--timeline-only" in sys.argv:
        return

    chap_files = []
    for ci, ch in enumerate(chapters):
        last = ci == len(chapters) - 1
        segs = [norm_one(e, 0 if (last or e is not ch[-1]) else XF) for e in ch]
        lst = os.path.join(NORM_DIR, f"chap_{ci:02d}.txt")
        open(lst, "w").write("".join(f"file '{p}'\n" for p in segs))
        cf = os.path.join(NORM_DIR, f"chap_{ci:02d}.mp4")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst,
                        "-c", "copy", cf], check=True)
        chap_files.append((cf, sum(e["frames"] for e in ch)))
        print(f"  chapter {ci:02d} {ch[0]['chapter']}: {len(ch)} shots", flush=True)

    inputs, fc, prev, acc = [], [], "[0:v]", 0
    for i, (cf, nf) in enumerate(chap_files):
        inputs += ["-i", cf]
        if i == 0:
            acc = nf
            continue
        lbl = f"[x{i}]"
        fc.append(f"{prev}[{i}:v]xfade=transition=fade:duration={XF / FPS}:offset={acc / FPS}{lbl}")
        prev, acc = lbl, acc + nf
    fc[-1] = fc[-1][: -len(prev)] + ",format=yuv420p[v]"
    subprocess.run(["ffmpeg", "-v", "error", "-y"] + inputs +
                   ["-filter_complex", ";".join(fc), "-map", "[v]", "-frames:v", str(TOTAL),
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "15", "-pix_fmt", "yuv420p",
                    OUT_BASE], check=True)
    print("OK", OUT_BASE)


if __name__ == "__main__":
    main()
