#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="/root/Motion/shwbster_order"
OUT_DIR="/root/youtubeai/shwbster"
mkdir -p "$OUT_DIR"

BASE_VID="$BASE_DIR/assets/base_71_shots_480s.mp4"
MASTER_AUD="$BASE_DIR/audio/master_mix_480s.wav"
SRT_FILE="$BASE_DIR/The_Worlds_10_Most_Expensive_Cities.srt"

V1_MP4="$OUT_DIR/The_Worlds_10_Most_Expensive_Cities_1080p.mp4"
V2_MP4="$OUT_DIR/The_Worlds_10_Most_Expensive_Cities_Clean_No_Subtitles_1080p.mp4"

echo "[1/2] Rendering Version 1 (Full 8:00 Master with Burned-In Subtitles) -> $V1_MP4 ..."
taskset -c 0,1 python3 "$BASE_DIR/opening_edit/overlays_full_480s.py" \
  | taskset -c 0,1 ffmpeg -v error -y \
      -i "$BASE_VID" \
      -f rawvideo -pixel_format rgba -video_size 1920x1080 -framerate 24 -i - \
      -i "$MASTER_AUD" \
      -filter_complex "[0:v][1:v]overlay=0:0:format=auto,format=yuv420p[v]" \
      -map "[v]" -map 2:a \
      -frames:v 11520 -r 24 \
      -c:v libx264 -preset veryfast -crf 18 -pix_fmt yuv420p \
      -c:a aac -b:a 192k -ar 48000 \
      -movflags +faststart \
      "$V1_MP4"

echo "[2/2] Rendering Version 2 (Full 8:00 Clean Master without Burned-In Subtitles + Soft SRT) -> $V2_MP4 ..."
taskset -c 0,1 python3 "$BASE_DIR/opening_edit/overlays_full_480s.py" --no-subs \
  | taskset -c 0,1 ffmpeg -v error -y \
      -i "$BASE_VID" \
      -f rawvideo -pixel_format rgba -video_size 1920x1080 -framerate 24 -i - \
      -i "$MASTER_AUD" \
      -i "$SRT_FILE" \
      -filter_complex "[0:v][1:v]overlay=0:0:format=auto,format=yuv420p[v]" \
      -map "[v]" -map 2:a -map 3:s \
      -frames:v 11520 -r 24 \
      -c:v libx264 -preset veryfast -crf 18 -pix_fmt yuv420p \
      -c:a aac -b:a 192k -ar 48000 \
      -c:s mov_text -metadata:s:s:0 language=eng \
      -movflags +faststart \
      "$V2_MP4"

echo "ALL RENDERS COMPLETE!"
ls -lh "$V1_MP4" "$V2_MP4"

