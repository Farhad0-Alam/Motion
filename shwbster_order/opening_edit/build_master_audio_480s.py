"""Synthesize the 480.000s Broadcast-Mastered Audio Track (-14.6 LUFS, <= -1.2 dBTP).

Combines:
  1. master_vo_480s.wav (Approved British male narrator 'Charon' across all 13 chapters)
  2. Understated cinematic documentary instrumental bed (evolving warm minor-9th / suspended chords,
     soft felt-piano arpeggios, subtle pulse, dipped on the opening $54,000 figure, smoothly ducked
     ~20 dB below speech during narration and rising gently in chapter pauses)
  3. Restrained acoustic rank chime on each city entry (#10 to #1) + soft price-reveal cue on each city's
     central rent reveal + subtle city room-tone texture.
"""
import json
import os
import subprocess
import wave
import numpy as np

AUDIO_DIR = "/root/Motion/shwbster_order/audio"
VO_WAV = os.path.join(AUDIO_DIR, "master_vo_480s.wav")
RAW_BED = os.path.join(AUDIO_DIR, "bed_480s.wav")
OUT_MIX = os.path.join(AUDIO_DIR, "master_mix_480s.wav")

SR = 48000
DUR = 480.0
N = int(SR * DUR)

# Exact timestamps (in seconds) of the 10 city rank entries and 10 hero price reveals
RANK_TIMES = [40.35, 80.35, 120.35, 160.35, 208.35, 248.35, 288.35, 328.35, 368.35, 408.35]
PRICE_TIMES = [
    0.30,    # Opening $54,000 / YEAR
    6.45,    # Opening $4,500 / MONTH
    48.00,   # #10 Dubai $2,600
    85.50,   # #9 San Francisco $3,700
    124.50,  # #8 Singapore $3,200
    166.50,  # #7 Bern $2,100
    214.50,  # #6 Tel Aviv $2,300
    263.50,  # #5 Hong Kong $2,400
    293.00,  # #4 Zurich $2,900
    339.50,  # #3 London $2,900 (£2,150)
    374.50,  # #2 Geneva $2,900
    415.00,  # #1 New York $4,500 / $54,000
]


def main():
    print("Generating 480.00s understated documentary score & restrained cues...")
    t = np.arange(N, dtype=np.float32) / SR

    # 4-chord progression cycling every 32 seconds (8s per chord): Dm9 -> Bbmaj7 -> Gm9 -> Asus4
    chords = [
        (146.83, 220.00, 261.63, 329.63),  # Dm9
        (116.54, 174.61, 220.00, 293.66),  # Bbmaj7
        (98.00,  146.83, 174.61, 220.00),  # Gm9
        (110.00, 164.81, 220.00, 246.94),  # Asus4
    ]

    pad_L = np.zeros(N, dtype=np.float32)
    pad_R = np.zeros(N, dtype=np.float32)

    # Render in 8-second chord blocks for speed and low memory
    block_s = 8.0
    block_n = int(block_s * SR)
    tb = np.arange(block_n, dtype=np.float32) / SR
    env_block = np.maximum(np.sin(np.pi * tb / block_s), 0.0) ** 0.65

    for idx in range(int(DUR // block_s)):
        i0 = idx * block_n
        i1 = i0 + block_n
        freqs = chords[idx % len(chords)]
        bL = np.zeros(block_n, dtype=np.float32)
        bR = np.zeros(block_n, dtype=np.float32)
        for k, f in enumerate(freqs):
            w1 = np.sin(2 * np.pi * f * tb + k * 0.4)
            w2 = 0.35 * np.sin(2 * np.pi * (f * 1.0015) * tb + k * 1.1)
            pan = 0.35 + 0.18 * k
            bL += (w1 + w2) * (1.0 - pan) * 0.045
            bR += (w1 + w2) * pan * 0.045
        # Soft felt-piano pulse every 2.0s inside the block
        for beat in range(4):
            p0 = int(beat * 2.0 * SR)
            pn = int(1.8 * SR)
            tp = np.arange(pn, dtype=np.float32) / SR
            nf = freqs[(idx + beat) % len(freqs)] * 2.0
            note = np.sin(2 * np.pi * nf * tp) * np.exp(-tp * 2.8) * (1.0 - np.exp(-tp * 45.0)) * 0.028
            bL[p0:p0 + pn] += note * 0.55
            bR[p0:p0 + pn] += note * 0.45

        pad_L[i0:i1] = bL * env_block
        pad_R[i0:i1] = bR * env_block

    # Brief requirement: "The opening figure should have a brief musical dip." (dip at 0.25s - 3.60s)
    dip = np.ones(N, dtype=np.float32)
    d0, d1 = int(0.20 * SR), int(3.80 * SR)
    td = np.linspace(0.0, 1.0, d1 - d0, dtype=np.float32)
    dip[d0:d1] = 1.0 - 0.68 * (np.maximum(np.sin(np.pi * td), 0.0) ** 0.8)
    pad_L *= dip
    pad_R *= dip

    # Restrained rank chime on each city entry (#10 to #1)
    tc = np.arange(int(1.4 * SR), dtype=np.float32) / SR
    rank_cue = (
        np.sin(2 * np.pi * 587.33 * tc) * np.exp(-tc * 3.8)
        + 0.45 * np.sin(2 * np.pi * 880.0 * tc) * np.exp(-tc * 5.2)
    ) * (1.0 - np.exp(-tc * 60.0)) * 0.055
    for rt in RANK_TIMES:
        s0 = int(rt * SR)
        s1 = min(s0 + len(rank_cue), N)
        pad_L[s0:s1] += rank_cue[:s1 - s0] * 0.52
        pad_R[s0:s1] += rank_cue[:s1 - s0] * 0.48

    # Soft price-reveal cue on each city's central rent reveal
    tp = np.arange(int(0.9 * SR), dtype=np.float32) / SR
    price_cue = (
        np.sin(2 * np.pi * 440.0 * tp) * np.exp(-tp * 5.0)
        + 0.4 * np.sin(2 * np.pi * 659.25 * tp) * np.exp(-tp * 6.5)
    ) * (1.0 - np.exp(-tp * 70.0)) * 0.042
    for pt in PRICE_TIMES:
        s0 = int(pt * SR)
        s1 = min(s0 + len(price_cue), N)
        pad_L[s0:s1] += price_cue[:s1 - s0] * 0.48
        pad_R[s0:s1] += price_cue[:s1 - s0] * 0.52

    # Smooth fade-out in final 2.5s (477.5s -> 480.0s)
    f0 = int(477.5 * SR)
    fade_out = np.linspace(1.0, 0.0, N - f0, dtype=np.float32)
    pad_L[f0:] *= fade_out
    pad_R[f0:] *= fade_out

    stereo = np.empty((N, 2), dtype=np.int16)
    stereo[:, 0] = np.clip(pad_L * 32767, -32768, 32767).astype(np.int16)
    stereo[:, 1] = np.clip(pad_R * 32767, -32768, 32767).astype(np.int16)

    with wave.open(RAW_BED, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(stereo.tobytes())

    print("Mixing VO + sidechain-ducked bed and mastering to -14.6 LUFS / -1.4 dBTP...")
    # Sidechain ducking + broadcast loudness normalization via FFmpeg loudnorm
    filter_complex = (
        "[0:a]aresample=48000,pan=stereo|c0=c0|c1=c0,highpass=f=75,"
        "acompressor=threshold=-19dB:ratio=2.4:attack=12:release=160:makeup=2dB,asplit=2[vo_main][vo_sc];"
        "[1:a]volume=0.82[bed_in];"
        "[bed_in][vo_sc]sidechaincompress=threshold=0.015:ratio=4.5:attack=25:release=650:level_sc=1.0[bed_ducked];"
        "[vo_main][bed_ducked]amix=inputs=2:duration=first:dropout_transition=0:weights='1.0 0.24',"
        "loudnorm=I=-14.6:TP=-1.4:LRA=7.0[aout]"
    )
    subprocess.run([
        "ffmpeg", "-v", "error", "-y",
        "-i", VO_WAV,
        "-i", RAW_BED,
        "-filter_complex", filter_complex,
        "-map", "[aout]",
        "-t", "480.000",
        "-c:a", "pcm_s16le", "-ar", "48000",
        OUT_MIX
    ], check=True)
    print(f"SUCCESS: Mastered 480.000s audio -> {OUT_MIX}")


if __name__ == "__main__":
    main()
