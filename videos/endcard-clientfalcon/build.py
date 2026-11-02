#!/usr/bin/env python3
"""ClientFalcon end card for every After Hours episode (3.0 s, 720x1280, 24 fps).

The picture is the HyperFrames composition in index.html (edit src/endcard_template.html, then
run src/make_endcard.py). This script turns its silent render into the clip episodes append:

    npx hyperframes@0.8.174 render . -q high --fps 24 -o renders/endcard-silent.mp4
    python3 build.py   -> renders/endcard.mp4          (picture + silent stereo track, for render())
                       -> renders/endcard-preview.mp4  (with endcard_sting(), for listening)

In an episode build.py:

    shots = [..., (ENDCARD, ENDCARD_DUR)]
    place(bus, endcard_sting(), DUR - ENDCARD_DUR)
"""
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib"))
from cartoon_sfx import ENDCARD, ENDCARD_DUR, SR, endcard_sting, place, render  # noqa: E402

RENDERS = os.path.join(HERE, "renders")


def main():
    silent = os.path.join(RENDERS, "endcard-silent.mp4")
    # render() reads every clip's audio stream, so the card carries a silent one
    subprocess.run(["taskset", "-c", "0,1", "ffmpeg", "-v", "error", "-y", "-i", silent,
                    "-f", "lavfi", "-t", str(ENDCARD_DUR), "-i", f"anullsrc=channel_layout=stereo:sample_rate={SR}",
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
                    "-shortest", "-movflags", "+faststart", ENDCARD], check=True)
    bus = np.zeros(int(ENDCARD_DUR * SR))
    place(bus, endcard_sting(), 0)
    print(render([(ENDCARD, ENDCARD_DUR)], bus, os.path.join(RENDERS, "endcard-preview.mp4")))


if __name__ == "__main__":
    main()
