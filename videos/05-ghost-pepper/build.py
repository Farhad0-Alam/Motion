#!/usr/bin/env python3
"""Ghost Pepper (Puff & Bramble ep 2): the hook opening, scored.

Shot A (wide, first 5.0 s) then shot B (Bramble close-up, 4.0 s) = 9.0 s.
Veo's own audio stays underneath (falling whistle, squeaks, snore); cues below
are timed to frames read from the clips:

    00.00-00.61  falling air rush        00.61  crash: thud, boom, dust
    00.78-01.93  feet kicking in sand    01.97  pop-out boing + sand spray
    02.02        wing flutter            02.45  landing thud
    02.60        dizzy wobble (spiral eyes)
    03.22        fluff bristles: poof + shock stab
    04.25/04.70  "dun... dun" grudge glare
    04.92        cut to close-up
    05.55        sly pizzicato slide (Ep 1 motif) on the side-eye
    06.25        pepper scrape           06.30  steam hiss
    06.90-09.00  tremolo riser, cut dead on the dare (cliffhanger)

    python3 build.py            -> renders/ghost-pepper.mp4
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib"))
from cartoon_sfx import *  # noqa: E402,F403

ASSETS = os.path.join(HERE, "assets")
RENDERS = os.path.join(HERE, "renders")
SHOT_A, SHOT_B = 5.0, 4.0
DUR = SHOT_A + SHOT_B


def score():
    music = np.zeros(int(DUR * SR))
    notes = [  # (time, midi, velocity)
        (3.22, 74, 0.7), (3.22, 62, 0.6), (3.22, 50, 0.8),   # shock stab
        (4.25, 38, 1.0), (4.70, 37, 1.0),                    # dun... dun
        (5.55, 69, 0.6), (5.67, 68, 0.55), (5.79, 67, 0.55),  # sly slide (Ep 1 motif)
        (5.91, 66, 0.5), (6.07, 62, 0.6), (6.07, 38, 0.8),
    ]
    for at, m, vel in notes:
        place(music, pluck(midi(m), 0.7 if m < 45 else 0.5, vel), at)
    place(music, tremolo_riser(DUR - 6.9, 50), 6.9, 0.45)
    return reverb(music)


def build_audio():
    bus = np.zeros(int(DUR * SR))
    place(bus, wind(DUR), 0, 0.05)
    place(bus, score(), 0, 0.42)
    # shot A
    place(bus, whoosh(0.62, 2500, 600, 0.8), 0.0, 0.3)
    place(bus, thud(0.6, 70), 0.61, 0.9)  # short sand crash; boom() rang on as a buzzy drone
    place(bus, thud(0.3, 160), 0.61, 0.4)
    place(bus, debris(1.0), 0.65, 0.25)
    place(bus, scuffle(1.15, 10), 0.78, 0.22)
    place(bus, boing(), 1.97, 0.35)
    place(bus, debris(0.5), 1.97, 0.18)
    place(bus, flutter(0.4), 2.02, 0.25)
    place(bus, thud(0.25, 140), 2.45, 0.45)
    place(bus, dizzy(0.6), 2.60, 0.10)
    place(bus, poof(), 3.22, 0.35)
    # shot B
    place(bus, whoosh(0.18, 600, 2500), 4.90, 0.15)
    place(bus, scrape(0.6), 6.25, 0.3)
    place(bus, hiss(DUR - 6.3), 6.30, 0.05)
    return bus


def main():
    os.makedirs(RENDERS, exist_ok=True)
    out = render([(os.path.join(ASSETS, "shotA.mp4"), SHOT_A),
                  (os.path.join(ASSETS, "shotB.mp4"), SHOT_B)],
                 build_audio(), os.path.join(RENDERS, "ghost-pepper.mp4"))
    print(out)


if __name__ == "__main__":
    main()
