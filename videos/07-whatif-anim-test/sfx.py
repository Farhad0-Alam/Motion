#!/usr/bin/env python3
"""Sound for the Pip animation test -> assets/sfx.wav (10.0 s), timed to pose() in index.html.

    footsteps    each foot contact of the walk (same walkX as index.html), softening into the stop
    05.60-06.50  phone shaken: soft rattles
    06.60        phone dies: falling blip;  06.74 startled boing
    08.42        shrug: two-note pizzicato "dunno"
    under all    quiet street wind
"""
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib"))
from cartoon_sfx import *  # noqa: E402,F403

DUR = 10.0
X0, X1, T_DEC, DEC, STRIDE = 120, 1420, 4.2, 0.6, 100
V = (X1 - X0) / (T_DEC + DEC / 2)


def walk_x(t):
    if t < T_DEC:
        return X0 + V * t
    d = min(t - T_DEC, DEC)
    return X0 + V * T_DEC + V * (d - d * d / (2 * DEC))


def steps():
    ts = np.arange(0, T_DEC + DEC, 1 / 1000)
    k = np.floor((np.array([walk_x(t) for t in ts]) - X0) / STRIDE - 0.5)  # contacts at legs' extremes
    return ts[1:][np.diff(k) > 0]


bus = np.zeros(int(DUR * SR))
place(bus, wind(DUR), 0, 0.04)
for i, at in enumerate(steps()):
    place(bus, thud(0.09, 210 if i % 2 else 190), at, 0.32 if at < T_DEC else 0.2)
    place(bus, scuffle(0.05, 30), at, 0.05)
for at in np.arange(5.62, 6.5, 1 / 9):
    place(bus, scuffle(0.05, 40), at, 0.12)
place(bus, whoosh(0.32, 2200, 260, 0.3), 6.6, 0.22)
place(bus, boing(0.35, 260, 620), 6.74, 0.3)
place(bus, reverb(pluck(midi(67), 0.4, 0.8)), 8.42, 0.3)
place(bus, reverb(pluck(midi(62), 0.6, 0.8)), 8.62, 0.3)
bus[-int(0.05 * SR):] *= np.linspace(1, 0, int(0.05 * SR))

out = os.path.join(HERE, "assets", "sfx.wav")
pcm = (np.clip(np.stack([bus] * 2, axis=1) / max(1e-9, np.abs(bus).max()) * 0.6, -1, 1) * 32767).astype("<i2")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "s16le", "-ar", str(SR), "-ac", "2", "-i", "-", out],
               input=pcm.tobytes(), check=True)
print(f"{len(steps())} steps -> {out}")
