#!/usr/bin/env bash
# Assemble the 30 s demo: cuts + grade + overlays/subtitles + mixed, -14 LUFS audio.
# Usage: ./render.sh            -> ../Most_Expensive_Cities_Demo_30s_1080p.mp4
#        ./render.sh preview    -> overlay preview PNGs only (edit/preview/)
set -euo pipefail
cd "$(dirname "$0")"
SRC=..
T="taskset -c 0,1"
OUT="$SRC/Most_Expensive_Cities_Demo_30s_1080p.mp4"
mkdir -p work preview

C1="$SRC/Manhattan_skyline_drone_glide_1520c75a_1080p.mp4"
C2="$SRC/Narrator_discussing_New_York_rent_d7f79564_1080p.mp4"
C3="$SRC/Manhattan_traffic_flowing.mp4"
C4="$SRC/Burj_Khalifa_towering_over_Dubai_ce99b597_1080p.mp4"
C5="$SRC/Drone_flying_over_Tower_Bridge_e29f3b9d_1080p.mp4"

# segment: source-in, duration, timeline-start  (cuts at 4.40 / 9.70 / 15.10 / 22.20)
#   1  0.00  4.40   0.00
#   2  0.50  5.30   4.40
#   3  0.10  5.40   9.70
#   4  0.05  7.10  15.10   (ends 7.15 s, before the stray "and..." at 7.23 s)
#   5  0.00  7.80  22.20

if [[ "${1:-}" == "preview" ]]; then
  $T python3 overlays.py --preview 1.0,3.6,7.4,11.0,16.5,20.0,23.5,26.0,28.5 preview
  exit 0
fi

# ---------- audio: per-clip mix with short crossfades at every cut ----------
$T ffmpeg -v error -y -i "$C1" -i "$C2" -i "$C3" -i "$C4" -i "$C5" -filter_complex "
 [0:a]aresample=48000,atrim=0:4.52,asetpts=N/SR/TB,afade=t=out:st=4.37:d=0.15[a1];
 [1:a]aresample=48000,atrim=0.44:5.92,asetpts=N/SR/TB,afade=t=in:d=0.06,afade=t=out:st=5.33:d=0.15,adelay=4340:all=1[a2];
 [2:a]aresample=48000,atrim=0.04:5.62,asetpts=N/SR/TB,afade=t=in:d=0.06,afade=t=out:st=5.43:d=0.15,adelay=9640:all=1[a3];
 [3:a]aresample=48000,atrim=0.00:7.15,asetpts=N/SR/TB,afade=t=in:d=0.05,afade=t=out:st=7.07:d=0.08,adelay=15050:all=1[a4];
 [4:a]aresample=48000,atrim=0.00:7.80,asetpts=N/SR/TB,afade=t=in:d=0.04,adelay=22200:all=1[a5];
 aevalsrc='0.55*sin(2*PI*46*t)*exp(-2.0*t)+0.22*sin(2*PI*92*t)*exp(-4.5*t)':s=48000:d=3,lowpass=f=180,aformat=channel_layouts=stereo,adelay=25300:all=1[hit];
 anoisesrc=c=pink:r=48000:d=0.75:a=0.18,highpass=f=500,lowpass=f=5000,afade=t=in:d=0.7:curve=exp,afade=t=out:st=0.66:d=0.09,aformat=channel_layouts=stereo,adelay=24560:all=1[sw];
 [a1][a2][a3][a4][a5][hit][sw]amix=inputs=7:normalize=0:duration=longest,atrim=0:30,afade=t=out:st=28.9:d=1.1[mix]" \
 -map "[mix]" -c:a pcm_s24le work/mix.wav

# two-pass loudness to -14 LUFS / -1.5 dBTP
read -r I TP LRA TH OFF < <($T ffmpeg -hide_banner -i work/mix.wav -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 |
  python3 -c "import sys,json,re;d=json.loads(re.search(r'\{[^{}]*\}',sys.stdin.read()).group());print(d['input_i'],d['input_tp'],d['input_lra'],d['input_thresh'],d['target_offset'])")
$T ffmpeg -v error -y -i work/mix.wav -af "loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=$I:measured_TP=$TP:measured_LRA=$LRA:measured_thresh=$TH:offset=$OFF:linear=true,aresample=48000" -c:a pcm_s24le work/mix_14.wav

# ---------- picture: cuts, grade, overlay layer, encode ----------
V="fps=24,scale=1920:1080:flags=lanczos,setsar=1"
$T python3 overlays.py | $T ffmpeg -v error -stats -y \
 -i "$C1" -i "$C2" -i "$C3" -i "$C4" -i "$C5" \
 -f rawvideo -pix_fmt rgba -s 1920x1080 -r 24 -i - \
 -i work/mix_14.wav -filter_complex "
 [0:v]trim=0.00:4.40,setpts=PTS-STARTPTS,$V[v1];
 [1:v]trim=0.50:5.80,setpts=PTS-STARTPTS,$V[v2];
 [2:v]trim=0.10:5.50,setpts=PTS-STARTPTS,$V,eq=contrast=1.05:saturation=1.03[v3];
 [3:v]trim=0.05:7.15,setpts=PTS-STARTPTS,$V[v4];
 [4:v]trim=0.00:7.80,setpts=PTS-STARTPTS,$V[v5];
 [v1][v2][v3][v4][v5]concat=n=5:v=1:a=0,
   eq=contrast=1.04:saturation=1.06:gamma=0.99,
   unsharp=5:5:0.35:5:5:0,
   vignette=angle=PI/5:mode=forward,
   noise=c0s=5:c0f=t,
   format=yuv420p,format=rgba[base];
 [5:v]format=rgba[ov];
 [base][ov]overlay=0:0:format=auto,
   fade=t=in:st=0:d=0.25,fade=t=out:st=29.45:d=0.55,
   trim=0:30,format=yuv420p[v]" \
 -map "[v]" -map 6:a -c:v libx264 -preset slow -crf 17 -maxrate 14M -bufsize 28M -threads 2 \
 -profile:v high -level 4.1 -pix_fmt yuv420p -movflags +faststart -color_primaries bt709 -color_trc bt709 -colorspace bt709 \
 -c:a aac -b:a 256k -ar 48000 -t 30 "$OUT"

echo "wrote $OUT"
