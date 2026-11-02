"""Score + SFX + master for the Muse cut, reusing the order's build_score_v2 on the Muse timeline.

Clean VO is rebuilt from the raw narration (part_a_clean @ 0.04 s, part_b_clean @ 211.10 s),
so the Muse render's baked-in music bed is discarded. Bars are fitted per chapter (about 90 BPM,
locally stretched) so every rank banner still lands on a downbeat.
"""
import json
import subprocess
import sys

import numpy as np

sys.path.insert(0, "/root/Motion/shwbster_order/opening_edit")
import build_score_v2 as b  # noqa: E402

MV = "/root/Motion/muse_version"
AUD = "/root/Motion/shwbster_order/audio"
TL = json.load(open(f"{MV}/timeline.json"))
DUR = 387.625
LEVELS = [1, 2, 2, 2, 2, 3, 3, 3, 3, 3, 4, 4, 0]

a480, am = (np.array(x) for x in TL["anchors"])


def g(t):
    return float(np.interp(t, a480, am, left=t * am[0] / a480[0]))


def build_vo(path):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{AUD}/part_a_clean.wav", "-i", f"{AUD}/part_b_clean.wav",
                    "-filter_complex", "[0:a]aresample=48000,adelay=40[a];[1:a]aresample=48000,adelay=211100[b];"
                    "[a][b]amix=inputs=2:duration=longest:normalize=0,apad", "-t", str(DUR), "-ac", "1", path],
                   check=True)


def main():
    vo = f"{MV}/audio/vo_muse.wav"
    build_vo(vo)
    starts = [t for t, _ in TL["chapters"]]
    starts[2:12] = [g(t) for t in b.RANKS]  # city downbeats exactly on the rank banners
    starts[12] = g(b.CLOSE)
    bounds = starts + [DUR]
    sections, bars_t, bars_i, k = [], [], [], 0
    for i, lvl in enumerate(LEVELS):
        nb = max(2, round((bounds[i + 1] - bounds[i]) / b.BAR))
        sections.append((k, nb, lvl))
        bars_i.append(k)
        bars_t.append(bounds[i])
        k += nb
    bars_i.append(k)
    bars_t.append(DUR)

    b.SECTIONS, b.BAR_TIMES, b.T0 = sections, (bars_i, bars_t), 0.0
    b.DUR, b.N = DUR, int(b.SR * DUR)
    b.RANKS = [g(t) for t in b.RANKS]
    b.PRICES = [g(t) for t in b.PRICES]
    b.CARDS = [g(t) for t in b.CARDS]
    b.CLOSE = g(b.CLOSE)
    b.VO, b.WORK, b.OUT = vo, f"{MV}/audio", f"{MV}/audio/master_mix_muse.wav"
    music = b.render_music()
    b.write(f"{b.WORK}/music_v2.wav", music * 0.9)
    b.write(f"{b.WORK}/sfx_v2.wav", b.render_sfx())
    b.mix_bus(0.62, 0.8)


if __name__ == "__main__":
    main()
