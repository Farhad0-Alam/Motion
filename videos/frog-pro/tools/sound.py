# Synthesizes the score and the comic sound effects for FROG PRO.
#
#   music.wav  keynote-style bed (soft pad + plucked arpeggio) that tape-stops
#              at the burp, so the "launch" literally grinds to a halt
#   burp.wav   the burp: a wobbling glottal buzz through an "aw" vowel
#   ribbit.wav two-syllable croak for the final button
#   crickets.wav  the awkward silence after the burp
#
# Everything is seeded, so the files are identical on every run.
#     python3 tools/sound.py assets/audio
import sys
import numpy as np
import soundfile as sf
from scipy.signal import lfilter, butter

SR = 48000
OUT = sys.argv[1]
rng = np.random.default_rng(7)

TAPE_STOP_AT = 5.05  # seconds: where the burp lands in index.html
TAPE_STOP_LEN = 0.5


def t(seconds):
    return np.arange(int(seconds * SR)) / SR


def hz(note):  # MIDI note -> Hz
    return 440.0 * 2 ** ((note - 69) / 12)


def resonator(x, freq, bw):
    r = np.exp(-np.pi * bw / SR)
    a = [1, -2 * r * np.cos(2 * np.pi * freq / SR), r * r]
    return lfilter([1 - r], a, x)


def reverb(x, seconds=2.2, mix=0.28):
    n = int(seconds * SR)
    ir = rng.standard_normal(n) * np.exp(-np.arange(n) / (SR * seconds / 6.9))
    ir = lfilter(*butter(2, 5000 / (SR / 2)), ir)
    wet = np.convolve(x, ir)[: len(x)]
    wet *= np.max(np.abs(x)) / (np.max(np.abs(wet)) + 1e-9)
    return (1 - mix) * x + mix * wet


def normalize(x, peak=0.89):
    return x * peak / (np.max(np.abs(x)) + 1e-9)


# ---------------------------------------------------------------- music
LEN = 8.5
mus = np.zeros(int(LEN * SR))
tt = t(LEN)

# Pad: Cmaj9 voiced wide, slow swell, gentle detune shimmer
for note in (48, 55, 59, 62, 64):
    f = hz(note)
    voice = sum(np.sin(2 * np.pi * f * d * tt + p) for d, p in ((1, 0), (1.003, 1.1), (0.997, 2.3)))
    env = np.minimum(1, tt / 1.6) * 0.06
    mus += voice * env

# Plucked arpeggio, 8th notes at 104 bpm, starting under the first line
step = 60 / 104 / 2
pattern = [72, 76, 79, 83, 86, 83, 79, 76]
k = 0
start = 0.55
while start < LEN:
    f = hz(pattern[k % len(pattern)])
    nt = t(0.9)
    tone = np.sin(2 * np.pi * f * nt) + 0.35 * np.sin(2 * np.pi * 2 * f * nt) + 0.12 * np.sin(2 * np.pi * 3 * f * nt)
    env = (1 - np.exp(-nt / 0.004)) * np.exp(-nt / 0.22)
    i0 = int(start * SR)
    seg = (tone * env * 0.11)[: len(mus) - i0]
    mus[i0 : i0 + len(seg)] += seg
    start += step
    k += 1

# Soft sub pulse on the title land and on each spec
for at in (0.62, 3.0, 3.8, 4.5):
    nt = t(0.5)
    f = 55 * np.exp(-nt * 3)
    hit = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-nt / 0.12) * 0.25
    i0 = int(at * SR)
    mus[i0 : i0 + len(hit)] += hit

mus = reverb(mus, 2.6, 0.32)

# Tape stop: playback rate falls 1 -> 0, pitch and speed dive together
i0 = int(TAPE_STOP_AT * SR)
n = int(TAPE_STOP_LEN * SR)
rate = np.linspace(1, 0, n) ** 1.4
pos = i0 + np.cumsum(rate)
stopped = np.interp(pos, np.arange(len(mus)), mus) * np.linspace(1, 0.6, n)
mus = np.concatenate([mus[:i0], stopped, np.zeros(len(mus) - i0 - n)])
sf.write(f"{OUT}/music.wav", np.stack([normalize(mus, 0.7)] * 2, 1), SR)

# ---------------------------------------------------------------- burp
BL = 0.72
bt = t(BL)
f0 = 78 + 14 * np.sin(2 * np.pi * 9 * bt) + 10 * np.sin(2 * np.pi * 23 * bt) - 25 * bt
f0 *= 1 + 0.04 * np.cumsum(rng.standard_normal(len(bt))) / np.sqrt(SR)  # rough, irregular pitch
phase = np.cumsum(f0) / SR
pulses = (np.mod(phase, 1) < 0.08).astype(float) - 0.08  # glottal buzz
buzz = pulses + 0.25 * rng.standard_normal(len(bt)) * (np.mod(phase, 1) < 0.3)
voc = sum(resonator(buzz, f, bw) * g for f, bw, g in ((570, 90, 1.0), (840, 110, 0.7), (2400, 200, 0.18)))
env = np.minimum(1, bt / 0.03) * np.exp(-np.maximum(0, bt - 0.45) / 0.09)
env *= 1 + 0.35 * np.sin(2 * np.pi * 6 * bt)  # gurgle
burp = reverb(voc * env, 0.6, 0.12)
burp = lfilter(*butter(2, 60 / (SR / 2), "high"), burp)
sf.write(f"{OUT}/burp.wav", normalize(burp, 0.95), SR)

# ---------------------------------------------------------------- ribbit
def croak(length, f_start, f_end):
    ct = t(length)
    f = np.linspace(f_start, f_end, len(ct))
    ph = np.cumsum(f) / SR
    src = (np.mod(ph, 1) < 0.15).astype(float)
    v = resonator(src, 900, 160) + 0.6 * resonator(src, 1500, 220)
    return v * np.sin(np.pi * ct / length) ** 0.6


gap = np.zeros(int(0.06 * SR))
ribbit = np.concatenate([croak(0.11, 230, 200), gap, croak(0.15, 260, 190)])
sf.write(f"{OUT}/ribbit.wav", normalize(reverb(ribbit, 0.5, 0.15), 0.9), SR)

# ---------------------------------------------------------------- crickets
CL = 3.0
crk = np.zeros(int(CL * SR))
for bug, (carrier, rate, offset, gain) in enumerate(((4700, 0.62, 0.05, 1.0), (4300, 0.71, 0.33, 0.55))):
    at = offset
    while at < CL - 0.2:
        for pulse in range(3):  # one chirp = three rapid pulses
            pt = t(0.022)
            tone = np.sin(2 * np.pi * carrier * pt) * np.sin(np.pi * pt / 0.022) ** 2
            i0 = int((at + pulse * 0.034) * SR)
            crk[i0 : i0 + len(tone)] += tone * gain
        at += rate
crk *= np.minimum(1, t(CL) / 0.4)
sf.write(f"{OUT}/crickets.wav", normalize(reverb(crk, 1.2, 0.35), 0.5), SR)

print("music.wav burp.wav ribbit.wav crickets.wav written")
