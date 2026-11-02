"""Studio-grade mallet bells and hall reverb for the Motion sound kit (stereo, numpy only).

cartoon_sfx.glock() is three sines with one envelope. These are modal models of real struck bars:
each partial at the bar's measured ratio with its own decay (high modes die first), split into a
slightly detuned pair so it beats and shimmers like metal, a felt mallet whose hardness sets how many
overtones ring, and a short contact noise. `hall()` is a stereo convolution reverb whose tail decays
faster in the highs than the lows, with early reflections and pre-delay, like a real room.

    from mallets import bell, hall
    bus = np.zeros((n, 2)); place2(bus, bell(midi(74)), at, 0.2); bus = hall(bus)
"""
import numpy as np

from cartoon_sfx import SR, fft_filter

# (ratio, amplitude, T60 seconds at the fundamental's register) per partial.
BARS = {
    # Vibraphone / tuned aluminium bar: overtones tuned to 4x and 10x, long warm sustain.
    'vibe': [(1.0, 1.0, 3.2), (3.99, 0.32, 1.1), (9.86, 0.10, 0.45), (17.3, 0.025, 0.2)],
    # Celesta-like: steel bar over a resonator, near-harmonic, sweet and short.
    'celesta': [(1.0, 1.0, 1.6), (2.0, 0.22, 0.7), (3.0, 0.08, 0.35), (5.04, 0.03, 0.15)],
    # Glockenspiel: free bar, inharmonic, bright.
    'glock': [(1.0, 1.0, 2.0), (2.756, 0.30, 0.8), (5.404, 0.10, 0.3), (8.933, 0.04, 0.12)],
}


def _t(sec):
    return np.arange(int(sec * SR)) / SR


def bell(freq, dur=2.5, bar='vibe', hardness=0.45, tine=0.18, width=0.6, seed=None):
    """One struck note, stereo (n, 2). hardness 0 = felt, 1 = hard plastic; tine adds a glassy FM ping."""
    r = np.random.default_rng(seed if seed is not None else int(freq * 1000) % 2**31)
    t = _t(dur)
    cutoff = 2500 + 9000 * hardness                     # mallet contact low-passes the strike
    reg = (440 / freq) ** 0.35                          # low notes ring longer
    out = np.zeros((len(t), 2))
    for ratio, amp, t60 in BARS[bar]:
        f = freq * ratio
        if f > 16000:
            continue
        a = amp / (1 + (f / cutoff) ** 2)
        tau = t60 * reg / 6.9                           # T60 -> exponential time constant
        decay = np.exp(-t / tau)
        for ch, side in ((0, -1), (1, 1)):
            beat = f * (1 + side * width * 0.0006) + side * 0.35   # detuned pair -> slow shimmer
            ph = r.uniform(0, 2 * np.pi)
            out[:, ch] += a * decay * 0.5 * (np.sin(2 * np.pi * f * t + ph) + np.sin(2 * np.pi * beat * t + ph * 0.7))
    if tine > 0:                                        # FM tine: bright ping that settles into a pure tone
        idx = 2.2 * np.exp(-t / 0.08) + 0.15
        ping = np.sin(2 * np.pi * freq * t + idx * np.sin(2 * np.pi * freq * 7.0 * t))
        ping *= np.exp(-t / (0.9 * reg))
        out += tine * ping[:, None] * np.array([0.9, 1.0])
    # Felt contact: a few ms of filtered noise, plus a raised-cosine attack so nothing clicks.
    n = int(0.006 * SR)
    contact = fft_filter(r.standard_normal(n), 300, cutoff * 0.6) * np.hanning(n * 2)[n:] * 0.05 * (0.4 + hardness)
    out[:n] += contact[:, None]
    a = int(0.0015 * SR)
    out[:a] *= (0.5 - 0.5 * np.cos(np.linspace(0, np.pi, a)))[:, None]
    f = int(min(0.25, dur * 0.2) * SR)                 # cosine release, so a cut tail never ticks
    out[-f:] *= (0.5 + 0.5 * np.cos(np.linspace(0, np.pi, f)))[:, None]
    return out / (np.max(np.abs(out)) + 1e-9)


def place2(bus, sig, at, gain=1.0, pan=0.0):
    """Add a stereo (n, 2) or mono signal into a stereo bus at `at` seconds, equal-power pan -1..1."""
    i = int(at * SR)
    if sig.ndim == 1:
        sig = np.stack([sig, sig], axis=1)
    lr = np.array([np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)]) * np.sqrt(2)
    n = min(len(sig), len(bus) - i)
    if n > 0:
        bus[i:i + n] += sig[:n] * gain * lr


def _ir(sec, t60_low, t60_high, seed):
    """One channel of a hall impulse: band-split noise, each band with its own decay, plus early reflections."""
    r = np.random.default_rng(seed)
    n = int(sec * SR)
    t = np.arange(n) / SR
    edges = [80, 250, 600, 1400, 3200, 7000, 16000]
    ir = np.zeros(n)
    for k, (lo, hi) in enumerate(zip(edges, edges[1:])):
        t60 = t60_low * (t60_high / t60_low) ** (k / (len(edges) - 2))
        ir += fft_filter(r.standard_normal(n), lo, hi) * np.exp(-6.9 * t / t60)
    pre = int(0.018 * SR)
    ir = np.concatenate([np.zeros(pre), ir])[:n]
    ir *= np.minimum(1, np.arange(n) / (0.03 * SR)) ** 2         # diffuse tail builds in
    for _ in range(9):                                          # early reflections, 7-70 ms
        d = int(r.uniform(0.007, 0.07) * SR)
        ir[d] += r.uniform(0.3, 0.8) * (1 - d / (0.08 * SR)) * r.choice([-1, 1]) * np.max(np.abs(ir)) * 3
    return ir / np.sqrt(np.sum(ir ** 2))


def hall(x, sec=3.0, t60_low=2.6, t60_high=0.7, wet=0.35, seed=11):
    """Stereo hall reverb on a stereo (n, 2) signal; the wet send is high-passed so it never muddies."""
    n = len(x)
    out = x.copy()
    send = np.stack([fft_filter(x[:, c], 180, 12000) for c in (0, 1)], axis=1)
    m = n + int(sec * SR)
    for c in (0, 1):
        ir = _ir(sec, t60_low, t60_high, seed + c)
        y = np.fft.irfft(np.fft.rfft(send[:, c], m) * np.fft.rfft(ir, m), m)[:n]
        out[:, c] += y * wet
    return out
