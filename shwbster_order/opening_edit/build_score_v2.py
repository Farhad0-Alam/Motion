"""v2 score + sound design + master for the 8:00 cut.

Replaces the sine-wave bed of build_master_audio_480s.py with:
  - An orchestral documentary score written as MIDI here and rendered by FluidSynth with the
    FluidR3_GM soundfont (MIT licence, commercial-safe). D minor, 90 BPM: one bar = 2.667 s, so
    every 40 s city chapter is exactly 15 bars and each rank entry lands on a downbeat.
    Arrangement escalates across the countdown (piano + strings -> cello -> pizzicato pulse +
    soft kick -> horns, choir, toms for #2 and #1) and resolves on the closing question.
  - Celesta chime on every price card, in key.
  - Synthesised SFX bus (no third-party samples): reverse swell + whoosh + sub impact into each
    rank banner, soft UI ticks/air on card slide-ins.
  - VO-keyed ducking on music only, two-pass loudnorm to -14 LUFS / -1.5 dBTP.
Run with the scratchpad venv (needs mido, numpy, scipy).
"""
import json
import os
import random
import subprocess
import sys
import wave

import mido
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve

AUDIO = "/root/Motion/shwbster_order/audio"
VO = os.path.join(AUDIO, "master_vo_480s.wav")
WORK = os.path.join(AUDIO, "v2")
SF2 = "/usr/share/sounds/sf2/FluidR3_GM.sf2"
OUT = os.path.join(AUDIO, "master_mix_v2_480s.wav")
SR, DUR = 48000, 480.0
N = int(SR * DUR)
BPM, TPB = 90, 480
BAR = 4 * 60 / BPM
T0 = 0.35  # bar grid origin: rank banners appear at T0 + 15k bars
BAR_TIMES = None  # optional (bar_index, seconds) anchors for a non-uniform grid (Muse cut)
os.makedirs(WORK, exist_ok=True)
random.seed(7)

RANKS = [40.25, 80.25, 120.25, 160.25, 208.25, 248.25, 288.25, 328.25, 368.25, 408.25]
PRICES = [0.25, 7.2, 48.0, 85.0, 124.4, 166.2, 214.7, 263.2, 293.2, 339.5, 374.4, 414.8]
CARDS = [24.8, 28.2, 34.2, 58.2, 61.3, 89.3, 96.4, 102.4, 129.0, 135.2, 174.7, 182.2, 220.4,
         225.0, 254.6, 269.0, 297.8, 301.5, 348.4, 381.0, 387.2, 422.0, 429.0, 435.0, 468.2, 474.2]
CLOSE = 456.25

C = {  # bass, upper voicing
    "Dm9": (38, [50, 53, 57, 64]), "Bb9": (34, [50, 53, 57, 60]), "F9": (41, [53, 55, 57, 60]),
    "C2": (36, [48, 52, 55, 62]), "Gm9": (43, [50, 53, 57, 58]), "Asus": (45, [50, 52, 57, 62]),
    "A": (45, [49, 52, 57, 61]),
}
P, Q = ["Dm9", "Bb9", "F9", "C2"], ["Dm9", "Gm9", "Bb9", "Asus"]
TOP = {"Dm9": [69, 72], "Bb9": [69, 65], "F9": [67, 69], "C2": [67, 64], "Gm9": [70, 67],
       "Asus": [69, 74], "A": [73, 69]}

# (first bar, bars, level) -- level 1 sparse ... 4 full
SECTIONS = [(0, 10, 1), (10, 5, 2), (15, 15, 2), (30, 15, 2), (45, 15, 2), (60, 18, 3),
            (78, 15, 3), (93, 15, 3), (108, 15, 3), (123, 15, 3), (138, 15, 4), (153, 18, 4),
            (171, 9, 0)]


def chords_for(nbars, closing=False):
    if closing:
        return (["Bb9", "F9", "Gm9", "Asus"] + ["Dm9"] * nbars)[:nbars]
    body = []
    while len(body) < nbars - 3:
        body += P if (len(body) // 4) % 2 == 0 else Q
    body = body[: nbars - 3] if nbars != 18 else (P + Q + P + Q)
    tail = ["Gm9", "Asus", "A"] if nbars != 18 else ["Asus", "A"]
    return (body + tail)[:nbars]


def bt(bar):
    if BAR_TIMES is None:
        return bar * BAR
    return float(np.interp(bar, *BAR_TIMES))


class Song:
    def __init__(self):
        self.ev = []  # (sec, ch, type, a, b)

    def note(self, ch, t, dur, n, v):
        t += random.uniform(-0.008, 0.008)
        v = max(1, min(127, int(v + random.uniform(-5, 5))))
        self.ev.append((max(t, 0), ch, "on", n, v))
        self.ev.append((max(t, 0) + dur, ch, "off", n, 0))

    def cc(self, ch, t, num, val):
        self.ev.append((t, ch, "cc", num, int(val)))

    def write(self, path, programs):
        mf = mido.MidiFile(ticks_per_beat=TPB)
        tr = mido.MidiTrack()
        mf.tracks.append(tr)
        tr.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(BPM)))
        for ch, pg in programs.items():
            tr.append(mido.Message("program_change", channel=ch, program=pg))
            tr.append(mido.Message("control_change", channel=ch, control=91, value=70))
        order = {"off": 0, "cc": 1, "on": 2}
        last = 0
        for t, ch, ty, a, b in sorted(self.ev, key=lambda e: (e[0], order[e[2]])):
            tick = int(round(t / (60 / BPM) * TPB))
            d = max(tick - last, 0)
            last += d
            if ty == "on":
                tr.append(mido.Message("note_on", channel=ch, note=a, velocity=b, time=d))
            elif ty == "off":
                tr.append(mido.Message("note_off", channel=ch, note=a, velocity=0, time=d))
            else:
                tr.append(mido.Message("control_change", channel=ch, control=a, value=b, time=d))
        mf.save(path)


PIANO, STR, CELLO, PIZZ, TIMP, HORN, CHOIR, CELESTA, DR = 0, 1, 2, 3, 4, 5, 6, 7, 9
PROGRAMS = {PIANO: 0, STR: 49, CELLO: 42, PIZZ: 45, TIMP: 47, HORN: 60, CHOIR: 52, CELESTA: 8}


def compose():
    s = Song()
    for first, nb, lvl in SECTIONS:
        closing = lvl == 0
        chs = chords_for(nb, closing)
        for k, name in enumerate(chs):
            bar = first + k
            t = bt(bar)  # MIDI time; audio is delayed by T0 later
            bass, up = C[name]
            L = 2 if closing else lvl
            held = closing and k >= 4
            # strings pad (always), swell into each bar
            sv = [40, 50, 60, 68, 76][L] if not (lvl == 1 and bar < 4) else 34
            if not held or k == 4:
                dur = BAR * (5 if held else 1) + 0.15
                for n in up:
                    s.note(STR, t, dur, n, sv)
                s.note(STR, t, dur, bass + 12, sv - 8)
            # piano arpeggio
            if not (lvl == 1 and bar < 2) and not (held and k > 4):
                if held:
                    for j, n in enumerate([62, 65, 69, 76]):
                        s.note(PIANO, t + j * 0.18, BAR * 3, n + 0, 46 - j * 3)
                else:
                    pat = [0, 2, 1, 3, 2, 3, 1, 2] if L >= 2 else [0, 2, 3, 1]
                    step = BAR / len(pat)
                    for j, ix in enumerate(pat):
                        v = (40 if L == 1 else 46 + 3 * L) + (8 if j == 0 else 0)
                        s.note(PIANO, t + j * step, step * 1.6, up[ix] + 12, v)
                    s.note(PIANO, t, BAR, bass + 12, 44)
            # cello / basses
            if L >= 2 and not (held and k > 4):
                s.note(CELLO, t, BAR * (5 if held else 1) - 0.05, bass, 50 + 6 * L)
            # pizzicato pulse
            if L >= 3 and not closing:
                for j in range(8):
                    n = bass + 12 if j % 2 == 0 else bass + 19
                    s.note(PIZZ, t + j * BAR / 8, 0.2, n, 52 + 4 * (L - 3) + (10 if j % 4 == 0 else 0))
                # soft kick on 1 and 3, closed hat ghost on offbeats at level 4
                for b in (0, 2):
                    s.note(DR, t + b * BAR / 4, 0.1, 36, 62 + 8 * (L - 3))
                if L == 4:
                    for b in range(4):
                        s.note(DR, t + (b + 0.5) * BAR / 4, 0.05, 42, 30)
                    s.note(DR, t + 3.5 * BAR / 4, 0.1, 45, 48)
            # horns + choir for #2 and #1
            if L >= 4 and not closing:
                a, b = TOP[name]
                s.note(HORN, t, BAR / 2 - 0.05, a, 58)
                s.note(HORN, t + BAR / 2, BAR / 2 - 0.05, b, 54)
                for n in up:
                    s.note(CHOIR, t, BAR + 0.1, n + 12, 42)
        # chapter downbeat: timpani + crash; cymbal roll into it
        t = bt(first)
        if first > 0:
            s.note(TIMP, t, 1.5, 38, 70 + 10 * min(lvl, 3))
            s.note(TIMP, t, 1.5, 26 + 12, 60)
            if lvl >= 2:
                s.note(DR, t, 2.0, 49, 46 + 10 * (lvl - 2) if lvl else 50)
                for j in range(16):  # suspended-cymbal style roll on the ride, 1 bar crescendo
                    s.note(DR, t - BAR + j * BAR / 16, 0.1, 51, 12 + j * 3)
        if first == 153:  # timpani roll into #1
            for j in range(24):
                s.note(TIMP, t - BAR + j * BAR / 24, 0.1, 38, 30 + j * 3)
    # opening hit under "$54,000"
    s.note(TIMP, 0.0, 2.0, 38, 72)
    s.note(CELLO, 0.0, BAR * 2, 26 + 12, 64)
    # celesta chime on each price card (in D minor), placed in absolute time
    chime = [[74, 81], [77, 84], [76, 81], [74, 86]]
    for i, pt in enumerate(PRICES):
        for j, n in enumerate(chime[i % 4]):
            s.note(CELESTA, pt - T0 + j * 0.09, 1.6, n, 60 - j * 8)
    return s


def render_music():
    mid = os.path.join(WORK, "score_v2.mid")
    wav = os.path.join(WORK, "score_v2_raw.wav")
    compose().write(mid, PROGRAMS)
    subprocess.run(["fluidsynth", "-ni", "-q", "-r", str(SR), "-g", "0.55", "-R", "1", "-C", "1",
                    "-o", "synth.reverb.room-size=0.82", "-o", "synth.reverb.damp=0.35",
                    "-o", "synth.reverb.width=1.0", "-o", "synth.reverb.level=0.75",
                    "-o", "synth.chorus.level=0.6", "-F", wav, SF2, mid], check=True)
    x = read(wav)
    out = np.zeros((N, 2), np.float32)
    d = int(T0 * SR)
    m = min(len(x), N - d)
    out[d:d + m] = x[:m]
    f0 = int((DUR - 3.5) * SR)
    out[f0:] *= np.linspace(1, 0, N - f0, dtype=np.float32)[:, None] ** 1.5
    return out


def read(path):
    with wave.open(path) as w:
        a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
        return a.reshape(-1, w.getnchannels()) if w.getnchannels() == 2 else np.repeat(a[:, None], 2, 1)


def write(path, x):
    x = np.clip(x, -1, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype(np.int16).tobytes())


# ---------------- sound design (all synthesised) ----------------
rng = np.random.default_rng(3)
_IR = None


def verb(x, decay=1.6, mix=0.35):
    global _IR
    if _IR is None:
        n = int(SR * 2.5)
        t = np.arange(n) / SR
        ir = rng.standard_normal((n, 2)) * np.exp(-t * 6.9 / decay)[:, None]
        ir = sosfilt(butter(2, 6000, "low", fs=SR, output="sos"), ir, axis=0)
        _IR = (ir / np.abs(ir).sum(0).max() * 6).astype(np.float32)
    wet = np.stack([fftconvolve(x[:, c], _IR[:, c])[: len(x)] for c in range(2)], 1)
    return x * (1 - mix) + wet * mix


def swept_noise(dur, f_from, f_to, env):
    n = int(dur * SR)
    noise = rng.standard_normal((n, 2)).astype(np.float32)
    out = np.zeros_like(noise)
    blk = 1024
    for i in range(0, n, blk):
        p = i / max(n - 1, 1)
        fc = f_from * (f_to / f_from) ** p
        sos = butter(2, [max(fc / 1.8, 40), min(fc * 1.8, 20000)], "band", fs=SR, output="sos")
        seg = noise[max(i - 2048, 0): i + blk]
        out[i:i + blk] = sosfilt(sos, seg, axis=0)[-len(out[i:i + blk]):]
    t = np.linspace(0, 1, n, dtype=np.float32)
    return out * env(t)[:, None]


def impact():
    n = int(2.4 * SR)
    t = np.arange(n) / SR
    f = 34 + 40 * np.exp(-t * 9)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.2) * (1 - np.exp(-t * 400))
    click = rng.standard_normal(n) * np.exp(-t * 90) * 0.25
    click = sosfilt(butter(2, 2500, "low", fs=SR, output="sos"), click)
    m = (body * 0.9 + click).astype(np.float32)
    return verb(np.stack([m, m], 1), decay=2.0, mix=0.25)


def riser(dur=1.4):
    x = swept_noise(dur, 300, 5000, lambda p: (p ** 2.2) * 0.5)
    return verb(x[::-1].copy(), 1.4, 0.4)[::-1].copy()  # reverse-reverb swell


def whoosh(dur=0.9):
    return verb(swept_noise(dur, 250, 3500, lambda p: np.sin(np.pi * p) ** 2 * 0.55), 1.0, 0.3)


def tick():
    n = int(0.5 * SR)
    t = np.arange(n) / SR
    c = (np.sin(2 * np.pi * 2350 * t) * np.exp(-t * 60) * 0.25
         + sosfilt(butter(2, [3000, 9000], "band", fs=SR, output="sos"), rng.standard_normal(n)) * np.exp(-t * 180) * 0.4)
    air = swept_noise(0.32, 1500, 6000, lambda p: np.sin(np.pi * p) ** 2 * 0.12)
    c = np.stack([c, c], 1).astype(np.float32)
    c[: len(air)] += air
    return verb(c, 0.8, 0.3)


def place(bus, clip, at, gain, pan=0.0):
    i = int(at * SR)
    if i < 0:
        clip, i = clip[-i:], 0
    m = min(len(clip), N - i)
    g = np.array([gain * (1 - max(pan, 0)), gain * (1 + min(pan, 0))], np.float32)
    bus[i:i + m] += clip[:m] * g


def render_sfx():
    bus = np.zeros((N, 2), np.float32)
    imp, ris, wh, tk = impact(), riser(), whoosh(), tick()
    for t in RANKS + [CLOSE]:
        place(bus, ris, t - len(ris) / SR + 0.02, 0.32)
        place(bus, wh, t - 0.45, 0.28, pan=0.0)
        place(bus, imp, t, 0.55)
    place(bus, imp, 0.25, 0.45)  # opening figure
    for i, t in enumerate(CARDS + PRICES[1:]):
        place(bus, tk, t, 0.16, pan=(-0.25 if i % 2 else 0.25))
    return bus


def lufs_pass(src, extra_filter):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", src, "-af",
                        extra_filter + "loudnorm=I=-14:TP=-1.5:LRA=9:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    return json.loads(r.stderr[r.stderr.rindex("{"):])


def main():
    print("composing + rendering score (FluidSynth)...", flush=True)
    music = render_music()
    write(os.path.join(WORK, "music_v2.wav"), music * 0.9)
    print("sound design...", flush=True)
    write(os.path.join(WORK, "sfx_v2.wav"), render_sfx())
    if "--stems-only" in sys.argv:
        return
    mix_bus(float(os.environ.get("MUSIC_GAIN", "0.55")), float(os.environ.get("SFX_GAIN", "0.8")))


def mix_bus(mg, sg):
    pre = os.path.join(WORK, "premaster_v2.wav")
    fc = ("[0:a]aresample=48000,pan=stereo|c0=c0|c1=c0,highpass=f=75,"
          "acompressor=threshold=-19dB:ratio=2.4:attack=12:release=160:makeup=2dB,asplit=2[vo][sc];"
          f"[1:a]acompressor=threshold=-30dB:ratio=3:attack=300:release=2500:knee=6,volume={mg}[mu];"
          "[mu][sc]sidechaincompress=threshold=0.02:ratio=6:attack=40:release=700:knee=4[mud];"
          f"[2:a]volume={sg}[fx];"
          "[vo][mud][fx]amix=inputs=3:duration=first:normalize=0,"
          "alimiter=limit=0.95:attack=5:release=60:level=disabled[a]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", VO, "-i", os.path.join(WORK, "music_v2.wav"),
                    "-i", os.path.join(WORK, "sfx_v2.wav"), "-filter_complex", fc, "-map", "[a]",
                    "-t", str(DUR), "-c:a", "pcm_s24le", "-ar", "48000", pre], check=True)
    m = lufs_pass(pre, "")
    ln = (f"loudnorm=I=-14:TP=-1.5:LRA=9:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", pre, "-af", ln + ",aresample=48000",
                    "-c:a", "pcm_s24le", OUT], check=True)
    print("OK", OUT, lufs_pass(OUT, "")["input_i"], "LUFS")


if __name__ == "__main__":
    main()
