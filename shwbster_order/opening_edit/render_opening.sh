#!/usr/bin/env bash
# Render shwbster's Opening Approval Video (34.00s @ 24fps, 1920x1080, -14.5 LUFS, <= -1.5 dBTP)
# Strictly obeys CPU governance (taskset -c 0,1) and Expensive_Cities_8_Minute_Script_and_Brief.docx
set -euo pipefail
cd "$(dirname "$0")"
T="taskset -c 0,1"

ASSETS="/root/Motion/shwbster_order/assets"
VO="/root/youtubeai/shwbster/Demo.wav"
OUT="/root/Motion/shwbster_order/Opening_Preview_shwbster_1080p.mp4"
SRT="/root/Motion/shwbster_order/Opening_Preview_shwbster.srt"

mkdir -p work preview

# 1. Export matching SRT subtitle file
$T python3 overlays_opening.py --srt "$SRT"

# 2. Generate understated cinematic instrumental music (-20 dB under speech, brief musical dip on opening figure, restrained price cues)
$T python3 - << 'PY'
import numpy as np, wave

sr = 48000
dur = 34.0
t = np.linspace(0, dur, int(sr * dur), endpoint=False, dtype=np.float32)

def warm_pad(freqs, t0, t1, amp=0.032):
    mask = (t >= t0) & (t < t1)
    lt = t[mask] - t0
    d = t1 - t0
    env = np.minimum(lt / 0.9, 1.0) * np.minimum((d - lt) / 1.1, 1.0)
    env = np.clip(env, 0.0, 1.0) ** 1.35
    sigL = np.zeros_like(lt)
    sigR = np.zeros_like(lt)
    for i, f in enumerate(freqs):
        det = 1.0005 if i % 2 == 0 else 0.9995
        toneL = (np.sin(2*np.pi*f*lt) + 0.26*np.sin(2*np.pi*2*f*lt)*np.exp(-lt*0.5))
        toneR = (np.sin(2*np.pi*f*det*lt + 0.22) + 0.26*np.sin(2*np.pi*2*f*det*lt)*np.exp(-lt*0.5))
        sigL += toneL / len(freqs)
        sigR += toneR / len(freqs)
    out = np.zeros((len(t), 2), dtype=np.float32)
    out[mask, 0] = sigL * env * amp
    out[mask, 1] = sigR * env * amp
    return out

def felt_note(f, t0, decay=2.6, amp=0.036, pan=0.5):
    mask = (t >= t0) & (t < min(t0 + decay * 2.5, dur))
    lt = t[mask] - t0
    env = (1.0 - np.exp(-lt * 40.0)) * np.exp(-lt / decay)
    sig = (np.sin(2*np.pi*f*lt) + 0.20*np.sin(2*np.pi*2*f*lt)*np.exp(-lt*2.0)) * env * amp
    out = np.zeros((len(t), 2), dtype=np.float32)
    out[mask, 0] = sig * np.sqrt(1.0 - pan)
    out[mask, 1] = sig * np.sqrt(pan)
    return out

def soft_cue(t0, f0=52.0, chime_f=587.33, amp=0.10):
    """Restrained documentary price-reveal cue (soft low warmth + delicate harmonic bell)."""
    mask = (t >= t0) & (t < min(t0 + 2.2, dur))
    lt = t[mask] - t0
    sub_env = (1.0 - np.exp(-lt * 60.0)) * np.exp(-lt / 0.95)
    sub = np.sin(2*np.pi*f0*lt) * sub_env * amp
    ch_env = (1.0 - np.exp(-lt * 90.0)) * np.exp(-lt / 1.1)
    ch = np.sin(2*np.pi*chime_f*lt) * ch_env * (amp * 0.22)
    out = np.zeros((len(t), 2), dtype=np.float32)
    out[mask, 0] = sub + ch * 0.9
    out[mask, 1] = sub + ch * 1.1
    return out

bgm = np.zeros((len(t), 2), dtype=np.float32)

# Understated Economist/FT-style progression (D min9 -> Bb maj7 -> F maj9 -> C6 -> G min7 -> D min9)
chords = [
    (0.0,  6.5,  [146.83, 220.00, 261.63, 329.63], 0.030),
    (6.0,  13.5, [116.54, 174.61, 220.00, 293.66], 0.032),
    (13.0, 17.3, [174.61, 220.00, 261.63, 349.23], 0.032),
    (16.8, 22.8, [130.81, 196.00, 246.94, 329.63], 0.033),
    (22.3, 28.4, [146.83, 220.00, 293.66, 349.23], 0.034),
    (27.9, 34.0, [116.54, 174.61, 261.63, 329.63, 440.00], 0.044),
]
for t0, t1, freqs, amp in chords:
    bgm += warm_pad(freqs, t0, t1, amp)

notes = [
    (4.30, 440.00, 0.028, 0.40), (6.45, 523.25, 0.030, 0.60), (9.80, 440.00, 0.026, 0.45),
    (13.45, 587.33, 0.028, 0.55), (17.15, 523.25, 0.028, 0.42), (20.30, 659.25, 0.030, 0.58),
    (22.70, 440.00, 0.028, 0.46), (25.60, 523.25, 0.028, 0.54),
    (28.30, 587.33, 0.030, 0.44), (31.20, 523.25, 0.030, 0.56), (32.65, 587.33, 0.046, 0.50),
]
for t0, f, amp, pan in notes:
    bgm += felt_note(f, t0, decay=2.5, amp=amp, pan=pan)

# Brief line 103: "The opening figure should have a brief musical dip." (dip during 0.15s - 3.65s)
dip = np.ones_like(t)
dip_zone = np.exp(-((t - 1.85) / 1.55) ** 2)
dip = 1.0 - 0.68 * dip_zone
# Gentle swell after speech ends at 32.55s, then smooth fade out at 34.0s
swell = 1.0 + 0.45 * np.clip((t - 32.50) / 0.80, 0.0, 1.0)
bgm[:, 0] *= dip * swell
bgm[:, 1] *= dip * swell

# Restrained price-reveal cues ONLY (no constant whooshes on every cut, per brief line 103)
sfx = np.zeros((len(t), 2), dtype=np.float32)
sfx += soft_cue(0.26,  f0=50.0, chime_f=587.33, amp=0.11)  # ≈ $54,000 / YEAR
sfx += soft_cue(6.42,  f0=48.0, chime_f=523.25, amp=0.10)  # ≈ $4,500 / MONTH
sfx += soft_cue(22.58, f0=46.0, chime_f=440.00, amp=0.08)  # ECA 2026 map entry

tot = bgm + sfx
pcm = np.clip(tot * 32767.0, -32768, 32767).astype(np.int16)
with wave.open("work/score_opening.wav", "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(sr)
    w.writeframes(pcm.tobytes())
PY

# 3. Mix Voiceover (Demo.wav) + Understated Music (-20 dB below narration) & Master to -14.5 LUFS / -1.5 dBTP
$T ffmpeg -v error -y -i "$VO" -i work/score_opening.wav -filter_complex "
  [0:a]aresample=48000,highpass=f=80,acompressor=threshold=-19dB:ratio=2.4:attack=12:release=160:makeup=2.2dB,
    aformat=channel_layouts=stereo,apad=whole_dur=34.0,atrim=0:34.0[vo];
  [1:a]aresample=48000,atrim=0:34.0,volume=0.82[bgm];
  [vo][bgm]amix=inputs=2:normalize=0:duration=longest,
    afade=t=in:st=0:d=0.12,afade=t=out:st=33.15:d=0.85[mix]
" -map "[mix]" -c:a pcm_s24le work/mix_raw.wav

read -r I TP LRA TH OFF < <($T ffmpeg -hide_banner -i work/mix_raw.wav -af loudnorm=I=-14.5:TP=-1.5:LRA=9:print_format=json -f null - 2>&1 |
  python3 -c "import sys,json,re;d=json.loads(re.search(r'\{[^{}]*\}',sys.stdin.read()).group());print(d['input_i'],d['input_tp'],d['input_lra'],d['input_thresh'],d['target_offset'])")
echo "Pre-master loudness: I=$I LUFS, TP=$TP dBTP"

$T ffmpeg -v error -y -i work/mix_raw.wav \
  -af "loudnorm=I=-14.5:TP=-1.5:LRA=9:measured_I=$I:measured_TP=$TP:measured_LRA=$LRA:measured_thresh=$TH:offset=$OFF:linear=true,alimiter=limit=-1.3dB:level=false,aresample=48000" \
  -c:a pcm_s24le work/mix_master.wav

# 4. Assemble 6 Real-Footage + Animated Map Shots (816 frames = 34.000s @ 24fps) + Bright Natural Grade + Overlays
S1="$ASSETS/shot1_nyc_apt_5824189.mp4"
S2="$ASSETS/shot2_manhattan_11471275.mp4"
S3="$ASSETS/shot3_burj_khalifa_35972202.mp4"
S4="$ASSETS/shot4_bern_switzerland_3655304.mp4"
S5="$ASSETS/shot5_world_map_eca.mp4"
S6="$ASSETS/shot6_dubai_marina_30301046.mp4"

VF="fps=24,scale=1920:1080:flags=lanczos,setsar=1"

$T python3 overlays_opening.py | $T ffmpeg -v error -stats -y \
  -i "$S1" -i "$S2" -i "$S3" -i "$S4" -i "$S5" -i "$S6" \
  -f rawvideo -pix_fmt rgba -s 1920x1080 -r 24 -i - \
  -i work/mix_master.wav -filter_complex "
  [0:v]$VF,trim=start_frame=0:end_frame=150,setpts=PTS-STARTPTS,eq=brightness=0.03:contrast=1.04:saturation=1.06[v1];
  [1:v]$VF,trim=start_frame=12:end_frame=180,setpts=PTS-STARTPTS,eq=contrast=1.05:saturation=1.07[v2];
  [2:v]$VF,trim=start_frame=0:end_frame=89,setpts=PTS-STARTPTS,eq=brightness=0.03:contrast=1.06:saturation=1.08[v3];
  [3:v]$VF,trim=start_frame=24:end_frame=157,setpts=PTS-STARTPTS,eq=contrast=1.04:saturation=1.06[v4];
  [4:v]$VF,trim=start_frame=0:end_frame=134,setpts=PTS-STARTPTS[v5];
  [5:v]$VF,trim=start_frame=12:end_frame=154,setpts=PTS-STARTPTS,eq=contrast=1.04:saturation=1.06[v6];
  [v1][v2][v3][v4][v5][v6]concat=n=6:v=1:a=0,
    unsharp=5:5:0.30:5:5:0,
    format=rgba[base];
  [6:v]format=rgba[ov];
  [base][ov]overlay=0:0:format=auto,
    fade=t=in:st=0:d=0.25,fade=t=out:st=33.40:d=0.60,
    trim=start_frame=0:end_frame=816,setpts=PTS-STARTPTS,format=yuv420p[v]
" \
  -map "[v]" -map 7:a -c:v libx264 -preset slow -crf 17 -maxrate 14M -bufsize 28M -threads 2 \
  -profile:v high -level 4.1 -pix_fmt yuv420p -movflags +faststart \
  -color_primaries bt709 -color_trc bt709 -colorspace bt709 \
  -c:a aac -b:a 256k -ar 48000 -t 34.0 "$OUT"

echo "DONE: $OUT"

