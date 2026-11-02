"""Shared cartoon sound kit for the Motion episodes.

Everything is synthesized with numpy (no stock or licensed audio), so any
episode can score itself: instruments (pizzicato, glock, string harmonic),
sound effects (whoosh, crunch, gulp, boom, ...) and a render helper that joins
Veo shots, lays the score under Veo's own audio and masters to -14 LUFS.
"""
import os
import subprocess

import numpy as np

SR = 48000
rng = np.random.default_rng(7)


def t_axis(sec):
    return np.arange(int(sec * SR)) / SR


def place(bus, sig, at, gain=1.0):
    i = int(at * SR)
    n = min(len(sig), len(bus) - i)
    if n > 0:
        bus[i:i + n] += sig[:n] * gain


def env(n, attack, release):
    """Linear attack, exponential release envelope of n samples."""
    e = np.ones(n)
    a = max(1, int(attack * SR))
    e[:a] = np.linspace(0, 1, a)
    e *= np.exp(-np.arange(n) / (release * SR))
    return e


def fft_filter(x, lo=0.0, hi=None):
    """Brick-ish bandpass with soft edges, applied in the frequency domain."""
    hi = hi or SR / 2
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    w = 1 / (1 + (lo / np.maximum(f, 1)) ** 4) / (1 + (f / hi) ** 4)
    return np.fft.irfft(X * w, len(x))


def swept_band(x, centers, width=0.6):
    """Bandpass whose centre moves over time (overlap-add of short FFT frames)."""
    hop, size = 512, 2048
    out = np.zeros(len(x) + size)
    win = np.hanning(size)
    f = np.fft.rfftfreq(size, 1 / SR)
    pad = np.concatenate([x, np.zeros(size)])
    for s in range(0, len(x), hop):
        c = centers[min(s, len(centers) - 1)]
        mask = np.exp(-0.5 * (np.log2(np.maximum(f, 1) / c) / width) ** 2)
        frame = np.fft.irfft(np.fft.rfft(pad[s:s + size] * win) * mask, size)
        out[s:s + size] += frame * win
    return out[:len(x)] / 1.5


def norm(x, peak=1.0):
    m = np.max(np.abs(x))
    return x / m * peak if m > 0 else x


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def pluck(freq, dur=0.5, vel=1.0):
    """Additive pizzicato: decaying harmonics, finger transient, body resonance."""
    t = t_axis(dur)
    base = np.clip(0.55 * (110 / freq) ** 0.5, 0.12, 0.6)  # low strings ring longer
    s = np.zeros(len(t))
    for k in range(1, 16):
        fk = freq * k * (1 + 0.0004 * k * k)  # slight string stiffness
        if fk > 12000:
            break
        amp = (1 / k ** 1.3) * abs(np.sin(np.pi * k * 0.13))  # plucked near the bridge
        s += amp * np.sin(2 * np.pi * fk * t) * np.exp(-t * (1 + 0.55 * (k - 1)) / base)
    s *= np.minimum(1, t / 0.0025)
    snap = fft_filter(noise(0.012), 900, 5000) * env(int(0.012 * SR), 0.0005, 0.003)
    place(s, snap, 0, 0.08 * np.max(np.abs(s)))
    body = fft_filter(s, 180, 450) * 0.5 + fft_filter(s, 1800, 3200) * 0.25
    return norm(s + body) * vel


def harmonic_tone(freq, dur):
    """Soft held flautando string harmonic for the freeze."""
    t = t_axis(dur)
    vib = 1 + 0.004 * np.sin(2 * np.pi * 5.5 * t) * np.minimum(1, t / 0.3)
    ph = 2 * np.pi * np.cumsum(freq * vib) / SR
    s = np.sin(ph) + 0.08 * np.sin(2 * ph)
    shape = np.minimum(1, t / 0.12) * np.minimum(1, (dur - t) / 0.18)
    return s * shape


def reverb(x, sec=0.9, wet=0.22):
    """Small hall: convolve with decaying filtered noise."""
    n = int(sec * SR)
    ir = fft_filter(noise(sec), 200, 7000) * np.exp(-np.arange(n) / (0.22 * SR))
    ir[:int(0.012 * SR)] = 0  # pre-delay
    y = np.fft.irfft(np.fft.rfft(x, len(x) + n) * np.fft.rfft(ir, len(x) + n))[:len(x)]
    return x + norm(y) * np.max(np.abs(x)) * wet


def glock(freq, dur=0.7):
    t = t_axis(dur)
    s = (np.sin(2 * np.pi * freq * t) + 0.35 * np.sin(2 * np.pi * freq * 2.76 * t)
         + 0.15 * np.sin(2 * np.pi * freq * 5.4 * t) * np.exp(-t * 18))
    return norm(s) * env(len(t), 0.001, 0.15)


def noise(sec):
    return rng.standard_normal(int(sec * SR))


def wind(sec):
    x = fft_filter(noise(sec), 120, 900)
    t = t_axis(sec)
    lfo = 0.6 + 0.4 * np.sin(2 * np.pi * 0.17 * t + 1) * np.sin(2 * np.pi * 0.05 * t)
    return norm(x) * lfo


def whoosh(sec, f0, f1, width=0.5):
    n = int(sec * SR)
    centers = np.geomspace(f0, f1, n)
    w = swept_band(noise(sec), centers, width)
    shape = np.sin(np.linspace(0, np.pi, n)) ** 1.5
    return norm(w * shape)


def crunch():
    n = int(0.18 * SR)
    x = fft_filter(noise(0.18), 900, 7000) * env(n, 0.001, 0.03)
    for _ in range(9):  # crackly grains
        place(x, fft_filter(noise(0.012), 2000, 9000) * env(int(0.012 * SR), 0.0005, 0.003),
              rng.uniform(0, 0.12), rng.uniform(0.6, 1.4))
    return norm(x)


def gulp():
    t = t_axis(0.28)
    f = np.geomspace(520, 140, len(t))
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR)
    body = tone * env(len(t), 0.01, 0.07)
    bloop = np.sin(2 * np.pi * np.cumsum(np.geomspace(260, 90, len(t))) / SR) * env(len(t), 0.005, 0.05)
    out = np.zeros(len(t))
    out += body
    place(out, bloop[:int(0.18 * SR)], 0.09, 0.8)
    return norm(out)


def sizzle(sec):
    n = int(sec * SR)
    hiss = fft_filter(noise(sec), 3000, 12000)
    pops = np.zeros(n)
    for at in np.sort(rng.uniform(0, sec, 140)):
        place(pops, fft_filter(noise(0.006), 1500, 10000) * env(int(0.006 * SR), 0.0003, 0.0015),
              at, rng.uniform(0.2, 1.0) * (0.3 + at / sec))
    ramp = np.linspace(0.05, 1, n) ** 2
    return norm(hiss * 0.5 + pops) * ramp


def riser(sec, f0=220, f1=1400):
    t = t_axis(sec)
    f = np.geomspace(f0, f1, len(t)) * (1 + 0.015 * np.sin(2 * np.pi * 9 * t))
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) + 0.3 * np.sin(2 * ph) + 0.12 * np.sin(3 * ph)
    trem = 0.75 + 0.25 * np.sin(2 * np.pi * np.linspace(5, 16, len(t)) * t)
    return norm(s) * trem * np.linspace(0, 1, len(t)) ** 2.2


def steam():
    n = int(0.35 * SR)
    return norm(fft_filter(noise(0.35), 2500, 11000) * env(n, 0.004, 0.09))


def boom():
    t = t_axis(1.6)
    f = 70 * np.exp(-t * 2.5) + 32
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(t), 0.002, 0.45)
    blast = fft_filter(noise(1.6), 40, 1800) * env(len(t), 0.001, 0.22)
    # tanh adds harmonics so the boom still reads on phone speakers
    return norm(np.tanh(2.5 * sub) * 0.8 + blast * 0.7)


def rocket(sec=1.4):
    n = int(sec * SR)
    roar = swept_band(noise(sec), np.geomspace(1800, 500, n), 0.9)
    t = t_axis(sec)
    whistle = np.sin(2 * np.pi * np.cumsum(np.geomspace(1500, 700, n)) / SR) * 0.25
    fade = np.minimum(1, t / 0.03) * np.exp(-t * 2.2)
    return norm(roar + whistle) * fade


def debris(sec=1.4):
    n = int(sec * SR)
    out = np.zeros(n)
    for at in np.sort(rng.exponential(0.35, 120)):
        if at < sec - 0.02:
            g = fft_filter(noise(0.01), 1200, 7000) * env(int(0.01 * SR), 0.0005, 0.002)
            place(out, g, at, rng.uniform(0.2, 1.0) * np.exp(-at * 1.6))
    out += fft_filter(noise(sec), 200, 2500) * np.exp(-t_axis(sec) * 3) * 0.15
    return norm(out)



def boing(sec=0.45, f0=180, f1=520):
    """Spring 'sproing': pitch jumps up and wobbles as it settles."""
    t = t_axis(sec)
    f = f1 + (f0 - f1) * np.exp(-t * 14) + 60 * np.sin(2 * np.pi * 22 * t) * np.exp(-t * 6)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR)
    s += 0.3 * np.sin(4 * np.pi * np.cumsum(f) / SR)
    return norm(s) * env(len(t), 0.003, sec * 0.35)


def thud(sec=0.35, f0=110):
    """Soft body landing on sand."""
    t = t_axis(sec)
    tone = np.sin(2 * np.pi * np.cumsum(f0 * np.exp(-t * 6) + 40) / SR) * env(len(t), 0.002, 0.07)
    grit = fft_filter(noise(sec), 300, 3000) * env(len(t), 0.001, 0.04)
    return norm(tone + 0.6 * grit)


def scuffle(sec, rate=9.0):
    """Little feet kicking in sand: a burst of grit grains at about `rate` per second."""
    n = int(sec * SR)
    out = np.zeros(n)
    at = 0.0
    while at < sec - 0.05:
        g = fft_filter(noise(0.05), 600, 6000) * env(int(0.05 * SR), 0.002, 0.012)
        place(out, g, at, rng.uniform(0.5, 1.0))
        at += rng.uniform(0.7, 1.3) / rate
    return norm(out)


def flutter(sec=0.4, rate=26):
    """Tiny wings flapping: amplitude-modulated airy noise."""
    t = t_axis(sec)
    air = fft_filter(noise(sec), 400, 4000)
    am = (0.5 + 0.5 * np.sin(2 * np.pi * rate * t)) ** 3
    return norm(air * am) * np.sin(np.pi * t / sec)


def dizzy(sec=0.7, f=1300):
    """Woozy wobbling whistle for spiral eyes."""
    t = t_axis(sec)
    fr = f * (1 + 0.12 * np.sin(2 * np.pi * 6 * t)) * (1 - 0.15 * t / sec)
    s = np.sin(2 * np.pi * np.cumsum(fr) / SR)
    return s * np.sin(np.pi * t / sec) ** 0.7


def poof(sec=0.3):
    """Fluff bristling: an airy burst with a short rising zip."""
    t = t_axis(sec)
    burst = fft_filter(noise(sec), 1500, 9000) * env(len(t), 0.002, 0.06)
    zip_ = np.sin(2 * np.pi * np.cumsum(np.geomspace(500, 2400, len(t))) / SR) * env(len(t), 0.002, 0.05)
    return norm(burst + 0.5 * zip_)


def scrape(sec=0.6):
    """Something slid slowly across sand and stone."""
    t = t_axis(sec)
    grit = fft_filter(noise(sec), 250, 2500) * (0.6 + 0.4 * np.abs(np.sin(2 * np.pi * 7 * t)))
    return norm(grit) * np.sin(np.pi * t / sec)


def hiss(sec):
    """Soft steam curl."""
    t = t_axis(sec)
    return norm(fft_filter(noise(sec), 3500, 12000)) * np.minimum(1, t / 0.4) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.8 * t))


def tremolo_riser(sec, note=50):
    """Suspense: string tremolo that climbs a semitone at a time and swells."""
    t = t_axis(sec)
    steps = np.floor(t / (sec / 4))
    f = midi(note) * 2 ** (steps / 12)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) + 0.5 * np.sin(2 * ph) + 0.25 * np.sin(3 * ph) + 0.12 * np.sin(4 * ph)
    trem = 0.55 + 0.45 * np.sign(np.sin(2 * np.pi * 14 * t)) * 0.8
    return norm(s) * trem * np.linspace(0.15, 1, len(t)) ** 1.5


# ClientFalcon end card (videos/endcard-clientfalcon), appended to every After Hours episode:
#   shots.append((ENDCARD, ENDCARD_DUR)); place(bus, endcard_sting(), card_start)
ENDCARD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "endcard-clientfalcon",
                       "renders", "endcard.mp4")
ENDCARD_DUR = 3.0


def endcard_sting():
    """Score for the 3.0 s end card, timed to its timeline (endcard-clientfalcon/index.html):

        0.08       coral dot pops            glock A5
        0.22-0.80  waiting-on circle draws   airy glide, rising
        0.80-1.02  stoop into the dot        whoosh swelling into the hit
        1.02       dot pulses (answered)     open chime D5 A5 E6 + low D pluck + held harmonic
        1.60       coral period lands        high tick
    """
    bus = np.zeros(int(ENDCARD_DUR * SR))
    place(bus, glock(midi(81), 0.6), 0.08, 0.35)
    place(bus, whoosh(0.58, 500, 1800, 0.7), 0.22, 0.08)
    stoop = whoosh(0.24, 1600, 5200, 0.5)
    place(bus, stoop * np.linspace(0.2, 1, len(stoop)), 0.80, 0.18)
    for m, g in ((74, 0.30), (81, 0.26), (88, 0.18)):
        place(bus, glock(midi(m), 1.6), 1.02, g)
    place(bus, pluck(midi(50), 1.9, 0.8), 1.02, 0.22)
    place(bus, harmonic_tone(midi(74), 1.8), 1.02, 0.10)
    place(bus, glock(midi(93), 0.3), 1.60, 0.12)
    return reverb(bus, 1.2, 0.3)


def _measure_lufs(wav):
    r = subprocess.run(["ffmpeg", "-v", "info", "-i", wav, "-af", "ebur128", "-f", "null", "-"],
                       capture_output=True, text=True)
    line = [l for l in r.stderr.splitlines() if l.strip().startswith("I:")][-1]
    return float(line.split()[1])


def render(shots, bus, out, veo_gain=0.9, fade=0.06, lufs=-14.0):
    """Join Veo shots (path, seconds-to-keep), lay `bus` under Veo's audio, master, encode.

    Mastering is a fixed gain to `lufs` plus a -2 dB limiter (AAC adds ~0.5 dB overshoot), not dynamic
    loudnorm, which pumps Veo's background hum up in the quiet gaps.
    """
    dur = sum(k for _, k in shots)
    base = os.path.splitext(out)[0]
    score, mix = base + "-score.wav", base + "-mix.wav"
    pcm = (np.clip(np.stack([bus] * 2, axis=1), -1, 1) * 32767).astype("<i2")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "s16le", "-ar", str(SR), "-ac", "2",
                    "-i", "-", score], input=pcm.tobytes(), check=True)
    n = len(shots)
    ins = []
    for path, _ in shots:
        ins += ["-i", path]

    # 1. Veo audio + score -> unmastered mix
    fc = "".join(f"[{i}:a]atrim=0:{k},asetpts=PTS-STARTPTS,aresample={SR}[a{i}];"
                 for i, (_, k) in enumerate(shots))
    fc += "".join(f"[a{i}]" for i in range(n)) + f"concat=n={n}:v=0:a=1,volume={veo_gain}[veo];"
    fc += (f"[{n}:a]aresample={SR}[score];[veo][score]amix=inputs=2:normalize=0,atrim=0:{dur},"
           "acompressor=threshold=0.125:ratio=2.5:attack=8:release=160[a]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-i", score, "-filter_complex", fc,
                    "-map", "[a]", "-c:a", "pcm_f32le", mix], check=True)

    # 2. fixed gain to target, limit peaks, fade the tail; join pictures
    gain = lufs - _measure_lufs(mix)
    fc = "".join(f"[{i}:v]trim=0:{k},setpts=PTS-STARTPTS[v{i}];" for i, (_, k) in enumerate(shots))
    fc += "".join(f"[v{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=0,fps=24,format=yuv420p[v];"
    fc += (f"[{n}:a]volume={gain:.2f}dB,alimiter=limit=0.79:attack=3:release=60:level=false,"
           f"afade=t=out:st={dur - fade}:d={fade}[a]")
    subprocess.run(["taskset", "-c", "0,1", "ffmpeg", "-v", "error", "-y", *ins, "-i", mix,
                    "-filter_complex", fc, "-map", "[v]", "-map", "[a]", "-t", str(dur),
                    "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-profile:v", "high",
                    "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                    "-c:a", "aac", "-b:a", "192k", "-ar", str(SR), out], check=True)
    os.remove(mix)
    return out
