"""Chili Chick: join the two Veo 3.1 shots and score them.

Veo's own audio (chick squeaks, tortoise snore, footsteps, launch roar) is kept
as the base layer. Everything else is synthesized here, timed to frames read
from the clips:

    00.00-03.05  sneaky pizzicato tiptoe cue + desert wind
    03.10        lunge whoosh            03.40  chili crunch (bite)
    04.75        cartoon gulp            05.00  satisfied glock "ding"
    06.00-08.45  belly sizzle + rising whistle riser
    07.45        steam pfft (head puffs)
    08.46        launch: boom + rocket whoosh + dust debris
    09.45/09.70  "dun-dun" button as the tortoise opens one eye

    python3 build.py            -> renders/chili-chick.mp4
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib"))
from cartoon_sfx import *  # noqa: E402,F403

ASSETS = os.path.join(HERE, "assets")
RENDERS = os.path.join(HERE, "renders")
DUR = 10.0
SHOT1_LEN = 6.0  # trim shot 1 to exactly 144 frames


# -------------------------------------------------------------------- music

def sneak_cue():
    """D-minor tiptoe pizzicato timed to the chick's moves in shot 1.

    0.0-0.9 tiptoe steps, 1.0-1.9 freezes on one leg, 2.0 foot down,
    2.4 sly grin, 3.1 lunge (music cuts dead before it).
    """
    music = np.zeros(int(DUR * SR))
    notes = [  # (time, midi, velocity)
        (0.12, 38, 0.9), (0.12, 50, 0.35),   # step
        (0.37, 57, 0.55),                    # tip
        (0.62, 45, 0.8), (0.62, 57, 0.3),    # step
        (0.87, 60, 0.55),                    # tip
        (1.00, 74, 0.5),                     # freeze "plink"
        (2.00, 38, 0.9), (2.00, 62, 0.45),   # foot down
        (2.40, 69, 0.6), (2.52, 68, 0.55),   # sly chromatic slide down
        (2.64, 67, 0.55), (2.76, 66, 0.5),
        (2.92, 62, 0.6), (2.92, 38, 0.9),    # lands, then silence
        (9.45, 38, 1.0), (9.45, 50, 0.4),    # "dun..."
        (9.70, 33, 1.1), (9.70, 45, 0.45),   # "...dun"
    ]
    for at, m, vel in notes:
        place(music, pluck(midi(m), 0.9 if at > 9 else 0.5, vel), at)
    place(music, harmonic_tone(midi(74), 0.9), 1.02, 0.12)  # held breath on the freeze
    return reverb(music)


def build_audio():
    bus = np.zeros(int(DUR * SR))
    place(bus, wind(DUR), 0, 0.05)
    place(bus, sneak_cue(), 0, 0.42)
    place(bus, whoosh(0.32, 500, 2500), 3.02, 0.35)
    place(bus, crunch(), 3.40, 0.55)
    place(bus, gulp(), 4.70, 0.6)
    place(bus, glock(midi(88)), 5.00, 0.16)
    place(bus, sizzle(2.45), 6.00, 0.22)
    place(bus, riser(2.0), 6.46, 0.16)
    place(bus, steam(), 7.45, 0.3)
    place(bus, steam(), 7.58, 0.22)
    place(bus, boom(), 8.44, 0.95)
    place(bus, rocket(), 8.46, 0.5)
    place(bus, debris(), 8.60, 0.3)
    return bus


def main():
    os.makedirs(RENDERS, exist_ok=True)
    out = render([(os.path.join(ASSETS, "shot1.mp4"), SHOT1_LEN),
                  (os.path.join(ASSETS, "shot2.mp4"), DUR - SHOT1_LEN)],
                 build_audio(), os.path.join(RENDERS, "chili-chick.mp4"), fade=0.25)
    print(out)


if __name__ == "__main__":
    main()
