#!/usr/bin/env bash
# Muse AI cut: original Muse picture + order graphics/subtitles (re-timed) + v2 score/SFX mix.
set -euo pipefail
MV="/root/Motion/muse_version"
OUT_DIR="/root/youtubeai/shwbster/Muse_Version"
SRC="$MV/src/muse.mp4"
AUD="$MV/audio/master_mix_muse.wav"
SRT="$OUT_DIR/The_Worlds_10_Most_Expensive_Cities_Muse.srt"
mkdir -p "$OUT_DIR"

python3 - "$SRT" <<'E'
import json, sys
f = lambda s: f"{int(s//3600):02d}:{int(s%3600//60):02d}:{int(s%60):02d},{int(round(s%1*1000))%1000:03d}"
subs = json.load(open("/root/Motion/muse_version/timeline.json"))["subs"]
open(sys.argv[1], "w").write("".join(f"{i}\n{f(c['start'])} --> {f(c['end'])}\n{c['text']}\n\n" for i, c in enumerate(subs, 1)))
E

render() {  # $1 = overlay flags, $2 = output, $3 = extra input (or ""), rest = extra output args
  local flags="$1" out="$2" extra_in="$3"; shift 3
  taskset -c 0,1 python3 "$MV/overlays_muse.py" $flags \
    | taskset -c 0,1 ffmpeg -v error -y \
        -i "$SRC" \
        -f rawvideo -pixel_format rgba -video_size 1920x1080 -framerate 24 -i - \
        -i "$AUD" ${extra_in:+-i "$extra_in"} \
        -filter_complex "[0:v][1:v]overlay=0:0:format=auto,format=yuv420p[v]" \
        -map "[v]" -map 2:a \
        -frames:v 9303 -r 24 \
        -c:v libx264 -preset medium -crf 18 -tune film -pix_fmt yuv420p \
        -c:a aac -b:a 256k -ar 48000 \
        -movflags +faststart "$@" \
        "$out.tmp.mp4"
  mv "$out.tmp.mp4" "$out"
}

render "" "$OUT_DIR/The_Worlds_10_Most_Expensive_Cities_Muse_1080p.mp4" ""
render "--no-subs" "$OUT_DIR/The_Worlds_10_Most_Expensive_Cities_Muse_Clean_No_Subtitles_1080p.mp4" "$SRT" \
  -map 3:s -c:s mov_text -metadata:s:s:0 language=eng
ls -lh "$OUT_DIR"
