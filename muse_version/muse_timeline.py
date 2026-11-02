"""Map the 8:00 order's VO/graphics timeline onto the Muse AI cut (6:27.6).

The Muse cut plays the raw narration back-to-back: PART A at 0.04 s, PART B at 211.10 s
(found by envelope cross-correlation, r=0.77 / 0.90). Every subtitle cue therefore sits at
part offset + its raw chunk time; graphics are moved with a piecewise-linear map anchored on
the cue starts. Writes timeline.json (subs, graphics, shots, chapters).
"""
import json
import subprocess

import numpy as np

SRC = "/root/Motion/muse_version/src/muse.mp4"
AUD = "/root/Motion/shwbster_order/audio"
OUT = "/root/Motion/muse_version/timeline.json"
OFF = {"part_a": 0.04, "part_b": 211.10}
FPS = 24
DUR = 387.625  # 9303 frames


def main():
    subs = json.load(open(f"{AUD}/subtitles_480s.json"))
    raw = json.load(open(f"{AUD}/raw_chunks.json"))
    msubs, a480, am = [], [], []
    for c in subs:
        r = raw[c["src"]][c["idx"]]
        s, e = OFF[c["src"]] + r["start"], OFF[c["src"]] + r["end"]
        msubs.append(dict(c, start=round(s, 3), end=round(e, 3)))
        a480.append(c["start"])
        am.append(s)
    a480, am = np.array(a480), np.array(am)

    def g(t):
        return float(np.interp(t, a480, am, left=t * am[0] / a480[0], right=am[-1] + (t - a480[-1])))

    chapters = []
    for c in msubs:
        if not chapters or chapters[-1][1] != c["chapter"]:
            chapters.append([c["start"] - 0.15, c["chapter"]])
    chapters[0][0] = 0.0

    # scene cuts in the Muse picture -> shot list for the corner location label
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", SRC, "-an", "-vf",
                        "select=gt(scene\\,0.3),metadata=print", "-f", "null", "-"],
                       capture_output=True, text=True)
    cuts = [0.0] + [float(l.split("pts_time:")[1]) for l in r.stderr.splitlines() if "pts_time:" in l] + [DUR]
    cuts = sorted(set(round(c, 3) for c in cuts + [t for t, _ in chapters[1:]]))
    cuts = [c for i, c in enumerate(cuts) if i == 0 or c - cuts[i - 1] > 0.3]
    shots = []
    for i in range(len(cuts) - 1):
        mid = (cuts[i] + cuts[i + 1]) / 2
        ch = [c for t, c in chapters if t <= mid][-1]
        shots.append({"shot": i + 1, "start": cuts[i], "end": cuts[i + 1], "chapter": ch, "id": f"MUSE_{i + 1:02d}",
                      "description": "", "illustrative_housing_label": False})
    json.dump({"subs": msubs, "anchors": [a480.tolist(), am.tolist()], "chapters": chapters, "shots": shots},
              open(OUT, "w"), indent=1)
    for t, c in chapters:
        print(f"{t:7.2f}  {c}")
    print(len(shots), "shots; map(40.25) ->", round(g(40.25), 2))


if __name__ == "__main__":
    main()
