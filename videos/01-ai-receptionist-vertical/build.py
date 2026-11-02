#!/usr/bin/env python3
"""Builds index.html for video 01 from src/template.html.in and the voice-over.

Inputs (assets/audio/vo/):
  sN.txt   approved narration per scene (may contain [delivery] tags)
  sN.mp3   ElevenLabs render of that text
  sN.json  whisper.cpp word timings (-ml 1 -sow -ojf)

It places the scenes back to back, aligns the script words to whisper's
timings (so captions show the script, not whisper's spelling), normalizes
the voice, loops the music bed, and writes every cue time into the page.

    python3 build.py && npx hyperframes lint && npx hyperframes render
"""
import difflib
import json
import os
import re
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
VO = os.path.join(HERE, "assets/audio/vo")
AUDIO = os.path.join(HERE, "assets/audio")
SFX_LIB = os.path.join(HERE, "../../node_modules/hyperframes/dist/skills/media-use/audio/assets/sfx")

SCENES = ["s1", "s2", "s3a", "s3b", "s3c", "s3d", "s4", "s5"]
LEAD_IN = 0.6      # silence before the first line
GAP = 0.8          # pause between scenes
SUB_GAP = 0.45     # pause between the four parts of scene 3
TAIL = 7.0         # end screen after the last line


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", path], capture_output=True, text=True, check=True)
    return float(out.stdout)


def norm(word):
    return re.sub(r"[^a-z0-9]", "", word.lower())


def script_words(text):
    text = re.sub(r"\[[^\]]+\]", " ", text)
    return text.split()


def whisper_words(path):
    data = json.load(open(path))
    words = []
    for seg in data["transcription"]:
        w = seg["text"].strip()
        if w:
            words.append((w, seg["offsets"]["from"] / 1000, seg["offsets"]["to"] / 1000))
    return words


def align(script, heard, dur):
    """Gives each script word a (start, end) using whisper's matching words."""
    a = [norm(w) for w in script]
    b = [norm(w) for w, _, _ in heard]
    times = [None] * len(script)
    for blk in difflib.SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks():
        for k in range(blk.size):
            times[blk.a + k] = (heard[blk.b + k][1], heard[blk.b + k][2])
    # Interpolate words whisper wrote differently ("forty" vs "40").
    known = [i for i, t in enumerate(times) if t]
    for i, t in enumerate(times):
        if t:
            continue
        prev = max([k for k in known if k < i], default=None)
        nxt = min([k for k in known if k > i], default=None)
        t0 = times[prev][1] if prev is not None else 0.0
        t1 = times[nxt][0] if nxt is not None else dur
        lo = prev if prev is not None else -1
        hi = nxt if nxt is not None else len(script)
        step = (t1 - t0) / (hi - lo)
        times[i] = (t0 + step * (i - lo - 1), t0 + step * (i - lo))
    return times


def main():
    scenes, words, t = {}, [], LEAD_IN
    for i, s in enumerate(SCENES):
        src = os.path.join(VO, f"{s}.mp3")
        wav = os.path.join(VO, f"{s}.norm.wav")
        if not os.path.exists(wav) or os.path.getmtime(wav) < os.path.getmtime(src):
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-af",
                            "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", "48000", wav], check=True)
        dur = duration(src)
        scenes[s] = {"start": round(t, 3), "dur": round(dur, 3)}
        sw = script_words(open(os.path.join(VO, f"{s}.txt"), encoding="utf-8").read())
        for w, (a, b) in zip(sw, align(sw, whisper_words(os.path.join(VO, f"{s}.json")), dur)):
            words.append({"w": w, "s": round(t + a, 3), "e": round(t + b, 3), "sc": s})
        nxt = SCENES[i + 1] if i + 1 < len(SCENES) else None
        t += dur + (SUB_GAP if nxt and s.startswith("s3") and nxt.startswith("s3") else GAP)
    total = round(scenes["s5"]["start"] + scenes["s5"]["dur"] + TAIL, 2)

    # Music: loop the MusicGen bed with crossfades to cover the whole video.
    raw = os.path.join(AUDIO, "music_raw.wav")
    music = os.path.join(AUDIO, "music.wav")
    if os.path.exists(raw):
        loop = duration(raw)
        n = int(total // (loop - 3)) + 2
        inputs, chain = [], ""
        for k in range(n):
            inputs += ["-i", raw]
        chain = "[0:a]"
        for k in range(1, n):
            last = k == n - 1
            chain += f"[{k}:a]acrossfade=d=3:c1=tri:c2=tri" + ("" if last else f"[x{k}];[x{k}]")
        subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex",
                        chain + f",atrim=0:{total},afade=t=out:st={total - 4}:d=4,"
                        "loudnorm=I=-24:TP=-3", "-ar", "48000", "-ac", "2", music], check=True)

    # Duck the music under every voice line.
    pts = [{"t": 0, "v": 0.9}]
    for s in SCENES:
        a, b = scenes[s]["start"], scenes[s]["start"] + scenes[s]["dur"]
        pts += [{"t": round(a - 0.35, 2), "v": 0.9}, {"t": round(a, 2), "v": 0.35},
                {"t": round(b, 2), "v": 0.35}, {"t": round(b + 0.4, 2), "v": 0.9}]
    pts = [p for p in pts if p["t"] >= 0]
    duck = {"version": 1, "lanes": [{"target": "volume", "points": pts}]}

    def cue(scene, word, nth=1, edge="s"):
        hits = [w for w in words if w["sc"] == scene and norm(w["w"]) == norm(word)]
        if len(hits) < nth:
            raise SystemExit(f"cue not found: {scene} {word} #{nth}")
        return hits[nth - 1][edge]

    cues = {
        # scene 1
        "s1_msg": cue("s1", "messaged"), "s1_who": cue("s1", "Who"),
        "s1_nobody": cue("s1", "nobody"), "s1_else": cue("s1", "someone"),
        "s1_title": cue("s1", "next"), "s1_good": cue("s1", "good"),
        # scene 2
        "s2_forty": cue("s2", "forty"), "s2_168": cue("s2", "one"),
        "s2_evenings": cue("s2", "Evenings"), "s2_web": cue("s2", "website,"),
        "s2_wa": cue("s2", "WhatsApp,"), "s2_phone": cue("s2", "phone."),
        "s2_all": cue("s2", "sits"), "s2_shift": cue("s2", "never"),
        # scene 3a
        "a_part": cue("s3a", "Part"), "a_chat": cue("s3a", "chat"),
        "a_voice": cue("s3a", "voice"), "a_wa": cue("s3a", "WhatsApp"),
        "a_single": cue("s3a", "single"), "a_same": cue("s3a", "same"),
        # scene 3b
        "b_part": cue("s3b", "Part"), "b_messy": cue("s3b", "messy,"),
        "b_nothing": cue("s3b", "nothing"), "b_ask": cue("s3b", "Ask"),
        "b_guess": cue("s3b", "guess."),
        # scene 3c
        "c_kb": cue("s3c", "knowledge"), "c_services": cue("s3c", "services,"),
        "c_prices": cue("s3c", "prices,"), "c_hours": cue("s3c", "hours,"),
        "c_policies": cue("s3c", "policies."), "c_question": cue("s3c", "question"),
        "c_finds": cue("s3c", "finds"), "c_hands": cue("s3c", "hands"),
        "c_rag": cue("s3c", "retrieval-augmented"), "c_looks": cue("s3c", "looks"),
        "c_think": cue("s3c", "think"), "c_were2": cue("s3c", "We're"),
        # scene 3d
        "d_part": cue("s3d", "Part"), "d_lead": cue("s3d", "lead."),
        "d_name": cue("s3d", "name,"), "d_need": cue("s3d", "need,"),
        "d_reach": cue("s3d", "reach"), "d_inbox": cue("s3d", "inbox."),
        "d_wake": cue("s3d", "wake"),
        # scene 4
        "g_bad": cue("s4", "bad"), "g_one": cue("s4", "One:"), "g_two": cue("s4", "Two:"),
        "g_three": cue("s4", "Three:"), "g_right": cue("s4", "right,"),
        # scene 5
        "f_cf": cue("s5", "ClientFalcon"), "f_web": cue("s5", "website"),
        "f_wa": cue("s5", "WhatsApp"), "f_lead": cue("s5", "lead"),
        "f_want": cue("s5", "want"), "f_link": cue("s5", "link's"),
        "f_sub": cue("s5", "subscribe."),
    }

    audio = [f'<audio id="music" src="assets/audio/music.wav" data-start="0" data-duration="{total}" '
             f'data-volume="1" data-fade-in="1" data-fade-out="3" data-track-index="10" '
             f"data-automation='{json.dumps(duck, separators=(',', ':'))}'></audio>"]
    for s in SCENES:
        sc = scenes[s]
        audio.append(f'<audio id="vo-{s}" src="assets/audio/vo/{s}.norm.wav" data-start="{sc["start"]}" '
                     f'data-duration="{sc["dur"]}" data-volume="1" data-track-index="11"></audio>')

    # Sound effects: (file, time, volume). Two tracks so overlaps are allowed.
    sfx = [
        ("notification", cues["s1_msg"], 0.35), ("impact-bass-1", cues["s1_title"] - 0.1, 0.12),
        ("whoosh", scenes["s2"]["start"] - 0.5, 0.25), ("pop", cues["s2_web"], 0.25),
        ("pop", cues["s2_wa"], 0.25), ("pop", cues["s2_phone"], 0.25),
        ("sparkle", cues["s2_shift"], 0.22), ("whoosh", scenes["s3a"]["start"] - 0.5, 0.25),
        ("pop", cues["a_chat"], 0.25), ("pop", cues["a_voice"], 0.25), ("pop", cues["a_wa"], 0.25),
        ("whoosh-short", cues["b_part"], 0.25), ("error", cues["b_guess"], 0.18),
        ("whoosh-short", cues["c_kb"], 0.25), ("click-soft", cues["c_finds"], 0.3),
        ("whoosh-short", cues["c_hands"], 0.22), ("whoosh-short", cues["d_part"], 0.25),
        ("ping", cues["d_inbox"] + 0.35, 0.3), ("whoosh", scenes["s4"]["start"] - 0.5, 0.25),
        ("click", cues["g_one"], 0.3), ("click", cues["g_two"], 0.3), ("click", cues["g_three"], 0.3),
        ("whoosh", scenes["s5"]["start"] - 0.5, 0.25), ("chime", cues["f_sub"], 0.25),
    ]
    os.makedirs(os.path.join(AUDIO, "sfx"), exist_ok=True)
    manifest = json.load(open(os.path.join(SFX_LIB, "manifest.json")))
    ends = {12: 0.0, 13: 0.0}
    for k, (name, at, vol) in enumerate(sfx):
        dst = os.path.join(AUDIO, "sfx", f"{name}.mp3")
        if not os.path.exists(dst):
            subprocess.run(["cp", os.path.join(SFX_LIB, f"{name}.mp3"), dst], check=True)
        d = round(min(float(manifest[name]["duration"]), 2.5), 2)
        at = round(max(at, 0), 2)
        track = 12 if ends[12] <= at else 13
        ends[track] = at + d
        audio.append(f'<audio id="sfx-{k}" src="assets/audio/sfx/{name}.mp3" data-start="{at}" '
                     f'data-duration="{d}" data-volume="{vol}" data-track-index="{track}"></audio>')

    data = {"total": total, "scenes": scenes, "words": words,
            "cues": {k: round(v, 3) for k, v in cues.items()}}
    html = open(os.path.join(HERE, "src/template.html.in"), encoding="utf-8").read()
    html = (html.replace("__TOTAL__", str(total))
                .replace("/*__DATA__*/null", json.dumps(data))
                .replace("<!--__AUDIO__-->", "\n      ".join(audio)))
    for s, sc in scenes.items():
        html = html.replace(f"__{s.upper()}_START__", str(sc["start"]))
    open(os.path.join(HERE, "index.html"), "w", encoding="utf-8").write(html)
    json.dump(data, open(os.path.join(HERE, "timeline.json"), "w"), indent=1)
    print(f"index.html written: {total}s, {len(words)} words, {len(sfx)} sound effects")
    for s in SCENES:
        print(f"  {s:4} {scenes[s]['start']:7.2f}s  +{scenes[s]['dur']:.2f}s")


if __name__ == "__main__":
    main()
