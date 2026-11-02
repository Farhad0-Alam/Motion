#!/usr/bin/env bash
# Assemble the 30.0s WOW Master for '/root/Motion/Demo Video 2'
# Strictly uses Marked 1 -> Marked 2 -> Marked 3 in sequence (30.0s @ 24fps, 1080p, -14 LUFS).
set -euo pipefail
cd "$(dirname "$0")"
SRC=".."
T="taskset -c 0,1"
OUT="$SRC/Most_Expensive_Cities_Demo_2_30s_1080p.mp4"
mkdir -p work preview fonts

# Copy required Montserrat & Inter fonts if not already present
cp -n "/root/Motion/Demo Video/edit/fonts/"*.ttf fonts/ 2>/dev/null || true

# Marked 1, Marked 2, Marked 3
C1="$SRC/Aerial_glide_of_New_York_676f08e1_1080p.mp4"
C2="$SRC/Charon_narrates_New_York_rent_89081572_1080p.mp4"
C3="$SRC/Charon_narrates_Manhattan_rent_c…_b602f5fe_1080p.mp4"

if [[ "${1:-}" == "preview" ]]; then
  $T python3 overlays.py --preview 2.8,7.8,11.8,13.5,17.2,19.2,21.0,25.5,28.0 preview
  exit 0
fi

# ---------- 1. Generate warm, quiet cinematic felt-piano + strings bed + subtle SFX ----------
$T python3 - << 'PY'
import numpy as np, wave

sr = 48000
dur = 30.0
t = np.linspace(0, dur, int(sr * dur), endpoint=False, dtype=np.float32)

def warm_pad(freqs, t0, t1, amp=0.045):
    mask = (t >= t0) & (t < t1)
    lt = t[mask] - t0
    d = t1 - t0
    env = np.minimum(lt / 0.8, 1.0) * np.minimum((d - lt) / 1.1, 1.0)
    env = np.clip(env, 0.0, 1.0) ** 1.4
    sigL = np.zeros_like(lt)
    sigR = np.zeros_like(lt)
    for i, f in enumerate(freqs):
        # Soft felt piano + warm string harmonics with slight stereo detune
        det = 1.0006 if i % 2 == 0 else 0.9994
        toneL = (np.sin(2*np.pi*f*lt) + 0.30*np.sin(2*np.pi*2*f*lt)*np.exp(-lt*0.6) + 0.10*np.sin(2*np.pi*3*f*lt)*np.exp(-lt*1.2))
        toneR = (np.sin(2*np.pi*f*det*lt + 0.25) + 0.30*np.sin(2*np.pi*2*f*det*lt)*np.exp(-lt*0.6) + 0.10*np.sin(2*np.pi*3*f*det*lt)*np.exp(-lt*1.2))
        sigL += toneL / len(freqs)
        sigR += toneR / len(freqs)
    out = np.zeros((len(t), 2), dtype=np.float32)
    out[mask, 0] = sigL * env * amp
    out[mask, 1] = sigR * env * amp
    return out

def felt_note(f, t0, decay=2.8, amp=0.055, pan=0.5):
    mask = (t >= t0) & (t < min(t0 + decay * 2.5, dur))
    lt = t[mask] - t0
    env = (1.0 - np.exp(-lt * 45.0)) * np.exp(-lt / decay)
    sig = (np.sin(2*np.pi*f*lt) + 0.22*np.sin(2*np.pi*2*f*lt)*np.exp(-lt*1.8) + 0.05*np.sin(2*np.pi*3*f*lt)*np.exp(-lt*3.5)) * env * amp
    out = np.zeros((len(t), 2), dtype=np.float32)
    out[mask, 0] = sig * np.sqrt(1.0 - pan)
    out[mask, 1] = sig * np.sqrt(pan)
    return out

def sub_hit(t0, f0=52.0, amp=0.22, decay=1.4):
    mask = (t >= t0) & (t < min(t0 + 2.8, dur))
    lt = t[mask] - t0
    freq_sweep = f0 * (1.0 + 0.65 * np.exp(-lt * 12.0))
    phase = 2 * np.pi * np.cumsum(freq_sweep) / sr
    env = (1.0 - np.exp(-lt * 80.0)) * np.exp(-lt / decay)
    sig = (np.sin(phase) + 0.25 * np.sin(2 * phase) * np.exp(-lt * 3.0)) * env * amp
    out = np.zeros((len(t), 2), dtype=np.float32)
    out[mask, 0] = sig
    out[mask, 1] = sig
    return out

mix = np.zeros((len(t), 2), dtype=np.float32)

# Chord progression across 30s (D minor9 -> Bb maj7 -> G min7 -> A7sus4 -> D min9 resolve)
chords = [
    (0.0,  6.2,  [146.83, 220.00, 261.63, 329.63], 0.042),
    (5.8,  10.3, [116.54, 174.61, 220.00, 293.66], 0.042),
    (9.9,  16.2, [146.83, 220.00, 293.66, 349.23], 0.045),
    (15.8, 20.3, [130.81, 196.00, 261.63, 329.63], 0.045),
    (19.9, 24.4, [110.00, 164.81, 220.00, 277.18], 0.048),
    (24.0, 30.0, [146.83, 220.00, 293.66, 349.23, 440.00], 0.088),  # End title swell
]
for t0, t1, freqs, amp in chords:
    mix += warm_pad(freqs, t0, t1, amp)

# Delicate Sparse Felt Piano Notes
notes = [
    (0.25, 440.00, 0.042, 0.35), (2.20, 523.25, 0.038, 0.65), (4.10, 392.00, 0.036, 0.45),
    (6.10, 349.23, 0.040, 0.55), (8.10, 440.00, 0.038, 0.40),
    (10.20, 587.33, 0.048, 0.60), (12.55, 523.25, 0.045, 0.40), (14.40, 440.00, 0.040, 0.55),
    (16.10, 523.25, 0.046, 0.38), (18.10, 440.00, 0.042, 0.62), (20.10, 392.00, 0.044, 0.48),
    (22.10, 349.23, 0.042, 0.52),
    (24.20, 587.33, 0.068, 0.45), (25.10, 659.25, 0.062, 0.58), (26.20, 587.33, 0.060, 0.42),
    (27.40, 440.00, 0.058, 0.52), (28.30, 587.33, 0.055, 0.50),
]
for t0, f, amp, pan in notes:
    mix += felt_note(f, t0, decay=2.6, amp=amp, pan=pan)

# Subtle documentary sub-impacts on key graphic reveals
mix += sub_hit(0.20,  f0=48.0, amp=0.14, decay=1.1)
mix += sub_hit(10.18, f0=46.0, amp=0.22, decay=1.4)  # $54,000 / YEAR
mix += sub_hit(12.52, f0=52.0, amp=0.14, decay=0.9)  # FOR ONE BEDROOM.
mix += sub_hit(16.08, f0=48.0, amp=0.20, decay=1.3)  # ≈ $4,500 / MONTH
mix += sub_hit(24.18, f0=44.0, amp=0.28, decay=1.8)  # END TITLE CARD

pcm = np.clip(mix * 32767.0, -32768, 32767).astype(np.int16)
with wave.open("work/score_sfx.wav", "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(sr)
    w.writeframes(pcm.tobytes())
PY

# ---------- 2. Assemble voiceover + score + transitions & master to -14 LUFS ----------
# Clip 1 voice (0.00 - 9.96s): spectral denoise + bandpass + volume gate during non-speech gaps to suppress helicopter noise
# Clip 3 Part A (0.00 - 3.85s placed at 9.90s -> 10.35s..13.30s speech): "Fifty-four thousand dollars a year. For one bedroom."
# Clip 3 Part B (4.15 - 9.96s placed at 15.80s -> 16.00s..21.61s speech): "That's roughly the average annual rent for a city-centre one-bedroom flat in New York."
# Clip 2 piano tail (3.45 - 4.25s placed at 13.75s & 21.60s) for seamless room/piano continuity
$T ffmpeg -v error -y -i "$C1" -i "$C2" -i "$C3" -i work/score_sfx.wav -filter_complex "
 [0:a]aresample=48000,highpass=f=140,lowpass=f=8200,afftdn=nf=-24,
   volume='if(between(t,0.98,2.22)+between(t,2.42,5.22)+between(t,6.30,7.28)+between(t,7.40,9.62), 1.25, 0.08)':eval=frame,
   atrim=0:9.96,asetpts=N/SR/TB,afade=t=in:d=0.12,afade=t=out:st=9.70:d=0.26[vo1];
 [2:a]aresample=48000,atrim=0.00:3.85,asetpts=N/SR/TB,
   afade=t=in:d=0.08,afade=t=out:st=3.60:d=0.25,volume=1.18,adelay=9900:all=1[vo2];
 [2:a]aresample=48000,atrim=4.15:9.96,asetpts=N/SR/TB,
   afade=t=in:d=0.08,afade=t=out:st=5.55:d=0.26,volume=1.18,adelay=15800:all=1[vo3];
 [3:a]aresample=48000,atrim=0:30.0,asetpts=N/SR/TB[bgm];
 anoisesrc=c=pink:r=48000:d=0.55:a=0.11,highpass=f=450,lowpass=f=4200,
   afade=t=in:d=0.45:curve=exp,afade=t=out:st=0.45:d=0.10,aformat=channel_layouts=stereo,adelay=9800:all=1[sw1];
 anoisesrc=c=pink:r=48000:d=0.55:a=0.11,highpass=f=450,lowpass=f=4200,
   afade=t=in:d=0.45:curve=exp,afade=t=out:st=0.45:d=0.10,aformat=channel_layouts=stereo,adelay=15700:all=1[sw2];
 anoisesrc=c=pink:r=48000:d=0.70:a=0.14,highpass=f=450,lowpass=f=4500,
   afade=t=in:d=0.58:curve=exp,afade=t=out:st=0.58:d=0.12,aformat=channel_layouts=stereo,adelay=23800:all=1[sw3];
 [vo1][vo2][vo3][bgm][sw1][sw2][sw3]amix=inputs=7:normalize=0:duration=longest,
   atrim=0:30.0,afade=t=in:st=0:d=0.20,afade=t=out:st=28.85:d=1.15[mix]" \
 -map "[mix]" -c:a pcm_s24le work/mix.wav

read -r I TP LRA TH OFF < <($T ffmpeg -hide_banner -i work/mix.wav -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 |
  python3 -c "import sys,json,re;d=json.loads(re.search(r'\{[^{}]*\}',sys.stdin.read()).group());print(d['input_i'],d['input_tp'],d['input_lra'],d['input_thresh'],d['target_offset'])")
$T ffmpeg -v error -y -i work/mix.wav -af "loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=$I:measured_TP=$TP:measured_LRA=$LRA:measured_thresh=$TH:offset=$OFF:linear=true,aresample=48000" -c:a pcm_s24le work/mix_14.wav

# ---------- 3. Picture: Marked 1 -> Marked 2 -> Marked 3 (30.0s @ 24fps) + Color Grade + Overlays ----------
V="fps=24,scale=1920:1080:flags=lanczos,setsar=1"
$T python3 overlays.py | $T ffmpeg -v error -stats -y \
 -i "$C1" -i "$C2" -i "$C3" \
 -f rawvideo -pix_fmt rgba -s 1920x1080 -r 24 -i - \
 -i work/mix_14.wav -filter_complex "
 [0:v]trim=0.00:5.958,setpts=PTS-STARTPTS,$V,eq=contrast=1.05:saturation=1.08:gamma=0.99[v1];
 [0:v]trim=5.958:9.963,setpts=PTS-STARTPTS,$V,eq=contrast=1.04:saturation=1.06[v2];
 [1:v]trim=0.00:5.958,setpts=PTS-STARTPTS,$V,eq=contrast=1.06:saturation=1.09:gamma=0.98[v3];
 [1:v]trim=5.958:7.930,setpts=2.09*(PTS-STARTPTS),$V,eq=contrast=1.04:saturation=1.06[v4];
 [2:v]trim=0.00:3.958,setpts=PTS-STARTPTS,$V,eq=contrast=1.05:saturation=1.07[v5];
 [2:v]trim=3.958:9.963,setpts=PTS-STARTPTS,$V,eq=contrast=1.04:saturation=1.06[v6];
 [v1][v2][v3][v4][v5][v6]concat=n=6:v=1:a=0,
   unsharp=5:5:0.35:5:5:0,
   vignette=angle=PI/6:mode=forward,
   noise=c0s=4:c0f=t,
   format=yuv420p,format=rgba[base];
 [3:v]format=rgba[ov];
 [base][ov]overlay=0:0:format=auto,
   fade=t=in:st=0:d=0.30,fade=t=out:st=29.35:d=0.65,
   trim=0:30.0,format=yuv420p[v]" \
 -map "[v]" -map 4:a -c:v libx264 -preset slow -crf 17 -maxrate 14M -bufsize 28M -threads 2 \
 -profile:v high -level 4.1 -pix_fmt yuv420p -movflags +faststart -color_primaries bt709 -color_trc bt709 -colorspace bt709 \
 -c:a aac -b:a 256k -ar 48000 -t 30.0 "$OUT"

echo "Successfully rendered: $OUT"

