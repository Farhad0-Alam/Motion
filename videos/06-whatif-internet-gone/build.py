#!/usr/bin/env python3
"""What if the Internet Disappeared for a Year? (whatif-channel ep 1), ~8 min explainer.

Everything comes from scenes.txt (93 scenes). Steps, in order:

    python3 build.py prompts           -> prompts.md (image prompts) + script.txt (read-through)
    python3 build.py tts [--only 001,002] [--force] [--voice Iapetus]
                                       -> assets/voice/NNN.wav via Gemini TTS (needs GEMINI_API_KEY)
    python3 build.py render --preview  -> renders/internet-gone-preview.mp4 (720p, fast)
    python3 build.py render            -> renders/internet-gone.mp4 (1080p) + .srt + -chapters.txt
    python3 build.py thumb             -> renders/thumb.png from assets/thumb.png

Missing images render as labelled placeholder cards and missing voice as timed silence, so the
cut can be checked at any stage. Clips are cached per scene; replacing an image re-renders only it.
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib"))
import whatif  # noqa: E402

TITLE = "What if the Internet Disappeared for a Year?"
SLUG = "internet-gone"
THUMB = [("1 YEAR", (255, 255, 255)), ("OFFLINE", (255, 214, 64))]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("step", choices=["prompts", "tts", "render", "thumb"])
    ap.add_argument("--preview", action="store_true")
    ap.add_argument("--only", help="comma-separated scene ids (tts)")
    ap.add_argument("--force", action="store_true", help="redo existing voice clips (tts)")
    ap.add_argument("--voice", default="Iapetus")
    a = ap.parse_args()
    scenes = whatif.load_scenes(os.path.join(HERE, "scenes.txt"))
    os.makedirs(os.path.join(HERE, "renders"), exist_ok=True)
    if a.step == "prompts":
        whatif.write_prompts(HERE, scenes, TITLE)
    elif a.step == "tts":
        whatif.tts(HERE, scenes, a.voice, a.only and a.only.split(","), a.force)
    elif a.step == "render":
        whatif.render(HERE, scenes, SLUG, a.preview)
    else:
        whatif.thumbnail(HERE, THUMB, os.path.join(HERE, "renders", "thumb.png"))


if __name__ == "__main__":
    main()
