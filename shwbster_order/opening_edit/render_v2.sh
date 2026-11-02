#!/usr/bin/env bash
# v2 master render: re-cut picture (build_base_video_v2.py) + new score/SFX mix (build_score_v2.py).
set -euo pipefail

mkdir -p /root/youtubeai/shwbster/_v1_backup
for f in /root/youtubeai/shwbster/*_1080p.mp4; do [ -e "/root/youtubeai/shwbster/_v1_backup/$(basename "$f")" ] || cp "$f" /root/youtubeai/shwbster/_v1_backup/; done

BASE_DIR="/root/Motion/shwbster_order"
OUT_DIR="/root/youtubeai/shwbster"
BASE_VID="$BASE_DIR/assets/base_v2_480s.mp4"
MASTER_AUD="$BASE_DIR/audio/master_mix_v2_480s.wav"
SRT_FILE="$OUT_DIR/The_Worlds_10_Most_Expensive_Cities.srt"
OVL="$BASE_DIR/opening_edit/overlays_v2.py"

V1_MP4="$OUT_DIR/The_Worlds_10_Most_Expensive_Cities_1080p.mp4"
V2_MP4="$OUT_DIR/The_Worlds_10_Most_Expensive_Cities_Clean_No_Subtitles_1080p.mp4"

render() {  # $1 = overlay flags, $2 = output, $3 = extra input (or ""), rest = extra output args
  local flags="$1" out="$2" extra_in="$3"; shift 3
  taskset -c 0,1 python3 "$OVL" $flags \
    | taskset -c 0,1 ffmpeg -v error -y \
        -i "$BASE_VID" \
        -f rawvideo -pixel_format rgba -video_size 1920x1080 -framerate 24 -i - \
        -i "$MASTER_AUD" ${extra_in:+-i "$extra_in"} \
        -filter_complex "[0:v][1:v]overlay=0:0:format=auto,format=yuv420p[v]" \
        -map "[v]" -map 2:a \
        -frames:v 11520 -r 24 \
        -c:v libx264 -preset medium -crf 18 -tune film -pix_fmt yuv420p \
        -c:a aac -b:a 256k -ar 48000 \
        -movflags +faststart "$@" \
        "$out.tmp.mp4"
  mv "$out.tmp.mp4" "$out"
}

echo "[1/2] burned-in subtitles -> $V1_MP4"
render "" "$V1_MP4" ""
echo "[2/2] clean + soft SRT -> $V2_MP4"
render "--no-subs" "$V2_MP4" "$SRT_FILE" -map 3:s -c:s mov_text -metadata:s:s:0 language=eng
ls -lh "$V1_MP4" "$V2_MP4"
