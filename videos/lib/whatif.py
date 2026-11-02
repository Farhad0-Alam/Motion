"""What-if explainer pipeline (../../whatif-channel): one scenes.txt -> prompts, voice, video.

An episode folder holds:
    scenes.txt             the single source. "== Chapter" lines mark YouTube chapters; each scene is
                           "NNN | camera [| sfx]" then a "VO:" line (narration) and an "IMG:" line (picture)
    assets/images/NNN.png  one 16:9 still per scene (missing -> a labelled placeholder card)
    assets/voice/NNN.wav   one narration clip per scene (missing -> silence timed at 155 wpm)
    assets/music.*         optional bed, looped quietly under the voice

Each scene becomes a slow Ken Burns move on its still, cut hard to the next, timed to its narration.
"""
import base64
import concurrent.futures
import glob
import json
import os
import re
import subprocess
import sys
import textwrap
import time
import urllib.error
import urllib.request
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from cartoon_sfx import (SR, _measure_lufs, boing, dizzy, glock, midi, place, poof, riser, scrape,
                         thud, whoosh)

CHANNEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "whatif-channel")
FPS = 30
LEAD, TAIL = 0.12, 0.30  # silence before / after each narration clip
WPS = 155 / 60           # placeholder pace for scenes with no voice clip yet
TTS_MODEL = os.environ.get("GEMINI_TTS_MODEL", "gemini-3.1-flash-tts-preview")
TTS_STYLE = ("Narrate in a warm, curious, gently playful storyteller voice, medium pace, "
             "clear American English, like a friendly science explainer:")

# zoompan expressions; {p} is scene progress 0..1. Pictures are rendered at 2x first so the
# integer crop offsets zoompan uses only jitter half an output pixel.
CX, CY = "iw/2-iw/zoom/2", "ih/2-ih/zoom/2"
CAMS = {
    "static": ("1.03+0.03*{p}", CX, CY),  # never fully still: a frozen frame reads as a glitch
    "push-in": ("1+0.12*{p}", CX, CY),
    "pull-out": ("1.12-0.12*{p}", CX, CY),
    "pan-right": ("1.12", "(iw-iw/zoom)*{p}", CY),
    "pan-left": ("1.12", "(iw-iw/zoom)*(1-{p})", CY),
    "rise": ("1.12", CX, "(ih-ih/zoom)*(1-{p})"),
}
SFX = {  # cue on the cut, under the narration
    "whoosh": lambda: whoosh(0.5, 600, 2400, 0.6),
    "thud": lambda: thud(0.35, 90),
    "boing": boing,
    "poof": poof,
    "dizzy": dizzy,
    "scrape": scrape,
    "riser": lambda: riser(1.6),
    "ding": lambda: glock(midi(84), 0.8),
}
PALETTE = [(236, 226, 208), (196, 226, 222), (244, 206, 196), (242, 222, 160), (200, 208, 230)]


# ---------- scenes ----------

def load_scenes(path):
    scenes, chapter = [], None
    for n, raw in enumerate(open(path, encoding="utf-8"), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("=="):
            chapter = line.strip("= ")
            continue
        m = re.match(r"^(\d{3})\s*\|\s*([\w-]+)\s*(?:\|\s*([\w-]*))?$", line)
        if m:
            scenes.append(dict(id=m[1], cam=m[2], sfx=m[3] or None, vo="", img="", chapter=chapter))
            chapter = None
            continue
        key, _, text = line.partition(":")
        if key in ("VO", "IMG") and scenes:
            scenes[-1][key.lower()] = text.strip()
        else:
            sys.exit(f"{path}:{n}: can't read: {line}")
    for s in scenes:
        if s["cam"] not in CAMS:
            sys.exit(f"scene {s['id']}: camera must be one of {', '.join(CAMS)}")
        if s["sfx"] and s["sfx"] not in SFX:
            sys.exit(f"scene {s['id']}: sfx must be one of {', '.join(SFX)}")
        if not (s["vo"] and s["img"]):
            sys.exit(f"scene {s['id']}: needs both VO: and IMG:")
    return scenes


def load_brand():
    style = " ".join(l.strip() for l in open(os.path.join(CHANNEL, "brand", "style.txt"))
                     if l.strip() and not l.startswith("#"))
    cast = {}
    for line in open(os.path.join(CHANNEL, "brand", "cast.txt")):
        name, sep, desc = line.partition(":")
        if sep and not line.startswith("#"):
            cast[name.strip()] = desc.strip()
    return style, cast


def image_prompt(scene, style, cast):
    who = [f"{n} is {d}" for n, d in cast.items() if re.search(rf"\b{n}\b", scene["img"])]
    parts = [scene["img"].rstrip(".") + "."]
    if who:
        parts.append("Characters: " + " ".join(who))
    return "\n".join(parts + [style])


def write_prompts(ep, scenes, title):
    """prompts.md (paste into the image tool, one per scene) and script.txt (read-through)."""
    style, cast = load_brand()
    words = sum(len(s["vo"].split()) for s in scenes)
    out = [f"# {title} - image prompts", "",
           f"{len(scenes)} scenes, {words} words, about {words / WPS / 60:.1f} min of narration.",
           "Save each image as `assets/images/NNN.png` (16:9). Attach the character reference "
           "sheets to every scene that names a character.", "", "## Character reference sheets", ""]
    for name, desc in cast.items():
        out += [f"### {name}", "```", f"Character reference sheet of {name}, {desc} Front, three-quarter "
                "and side views plus four expressions (happy, worried, surprised, determined) on a plain "
                f"cream background.", style, "```", ""]
    out += ["## Scenes", ""]
    for s in scenes:
        if s["chapter"]:
            out += [f"### == {s['chapter']} ==", ""]
        out += [f"#### {s['id']} · {s['cam']}" + (f" · sfx {s['sfx']}" if s["sfx"] else ""),
                f"> {s['vo']}", "```", image_prompt(s, style, cast), "```", ""]
    open(os.path.join(ep, "prompts.md"), "w").write("\n".join(out))
    script = []
    for s in scenes:
        if s["chapter"]:
            script += ["", f"[{s['chapter']}]"]
        script.append(s["vo"])
    open(os.path.join(ep, "script.txt"), "w").write(title + "\n" + "\n".join(script).strip() + "\n")
    print(f"prompts.md + script.txt: {len(scenes)} scenes, {words} words, ~{words / WPS / 60:.1f} min")


# ---------- voice (Gemini TTS) ----------

def voice_path(ep, s):
    return os.path.join(ep, "assets", "voice", s["id"] + ".wav")


def _trim(pcm, thresh=0.01, pad=0.03, rate=24000):
    x = np.frombuffer(pcm, dtype="<i2")
    loud = np.flatnonzero(np.abs(x) > thresh * 32767)
    if not len(loud):
        return pcm
    a, b = max(loud[0] - int(pad * rate), 0), min(loud[-1] + int(pad * rate), len(x))
    return x[a:b].tobytes()


def tts(ep, scenes, voice="Iapetus", only=None, force=False):
    key = (os.environ.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEYS", "").split(",")[0]).strip()
    if not key:
        sys.exit("set GEMINI_API_KEY first")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{TTS_MODEL}:generateContent"
    os.makedirs(os.path.join(ep, "assets", "voice"), exist_ok=True)
    for s in scenes:
        out = voice_path(ep, s)
        if (only and s["id"] not in only) or (os.path.exists(out) and not force):
            continue
        body = json.dumps({
            "contents": [{"parts": [{"text": f"{TTS_STYLE}\n\n{s['vo']}"}]}],
            "generationConfig": {"responseModalities": ["AUDIO"], "speechConfig": {
                "voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}}},
        }).encode()
        for attempt in range(6):
            req = urllib.request.Request(url, body, {"Content-Type": "application/json", "x-goog-api-key": key})
            try:
                data = json.load(urllib.request.urlopen(req, timeout=180))
                break
            except urllib.error.HTTPError as e:
                if e.code in (429, 500, 503) and attempt < 5:
                    print(f"  {s['id']}: HTTP {e.code}, retrying in {20 * (attempt + 1)} s")
                    time.sleep(20 * (attempt + 1))
                    continue
                sys.exit(f"{s['id']}: HTTP {e.code}: {e.read()[:400].decode(errors='replace')}")
        inline = data["candidates"][0]["content"]["parts"][0]["inlineData"]
        rate = int(re.search(r"rate=(\d+)", inline["mimeType"])[1])
        with wave.open(out, "wb") as w:
            w.setnchannels(1), w.setsampwidth(2), w.setframerate(rate)
            w.writeframes(_trim(base64.b64decode(inline["data"]), rate=rate))
        print(f"  {s['id']}: {probe(out):.1f} s")


# ---------- timeline ----------

def probe(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                       capture_output=True, text=True, check=True)
    return float(r.stdout)


def timeline(ep, scenes):
    t = 0.0
    for s in scenes:
        vp = voice_path(ep, s)
        s["voice"] = vp if os.path.exists(vp) else None
        speech = probe(vp) if s["voice"] else len(s["vo"].split()) / WPS
        s["dur"] = round((LEAD + speech + TAIL) * FPS) / FPS
        s["start"], t = t, t + s["dur"]
    return t


def stamp(sec, srt=False):
    h, m, s = int(sec // 3600), int(sec % 3600 // 60), sec % 60
    if srt:
        return f"{h:02d}:{m:02d}:{int(s):02d},{int(round(s % 1 * 1000)) % 1000:03d}"
    return f"{h}:{m:02d}:{int(s):02d}" if h else f"{m}:{int(s):02d}"


def write_captions(ep, scenes, base):
    srt = []
    for i, s in enumerate(scenes, 1):
        srt += [str(i), f"{stamp(s['start'] + LEAD, True)} --> {stamp(s['start'] + s['dur'] - TAIL / 2, True)}",
                textwrap.fill(s["vo"], 42), ""]
    open(base + ".srt", "w").write("\n".join(srt))
    chapters = [f"{stamp(s['start'])} {s['chapter']}" for s in scenes if s["chapter"]]
    if chapters and not chapters[0].startswith("0:00"):
        chapters.insert(0, "0:00 Intro")
    open(base + "-chapters.txt", "w").write("\n".join(chapters) + "\n")


# ---------- pictures ----------

def _font(size, bold=True):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(os.path.join("/usr/share/fonts/truetype/dejavu", name), size)


def placeholder(s, path, size=(1920, 1080)):
    w, h = size
    im = Image.new("RGB", size, PALETTE[int(s["id"]) % len(PALETTE)])
    d = ImageDraw.Draw(im)
    d.text((80, 70), f"{s['id']}  ·  {s['cam']}", font=_font(64), fill=(30, 40, 70))
    d.multiline_text((80, 200), textwrap.fill(s["img"], 52), font=_font(40, False), fill=(30, 40, 70), spacing=12)
    d.rectangle((0, h - 230, w, h), fill=(30, 40, 70))
    d.multiline_text((80, h - 200), textwrap.fill(s["vo"], 70), font=_font(38), fill=(250, 245, 235), spacing=10)
    im.save(path)


def _clip(img, s, out, size, preset, crf):
    w, h = size
    n = round(s["dur"] * FPS)
    z, x, y = (e.format(p=f"(on/{n})") for e in CAMS[s["cam"]])
    vf = (f"scale={2 * w}:{2 * h}:force_original_aspect_ratio=increase,crop={2 * w}:{2 * h},"
          f"zoompan=z='{z}':x='{x}':y='{y}':d={n}:s={w}x{h}:fps={FPS},setsar=1,format=yuv420p")
    subprocess.run(["taskset", "-c", "0,1", "ffmpeg", "-v", "error", "-y", "-i", img, "-vf", vf,
                    "-frames:v", str(n), "-c:v", "libx264", "-preset", preset, "-crf", str(crf),
                    "-threads", "1", "-r", str(FPS), out], check=True)
    return out


def render_video(ep, scenes, out, size, preset, crf):
    tag = f"{size[1]}p"
    clips_dir = os.path.join(ep, "renders", f"clips-{tag}")
    ph_dir = os.path.join(ep, "renders", "placeholders")
    os.makedirs(clips_dir, exist_ok=True), os.makedirs(ph_dir, exist_ok=True)
    jobs, clips, missing = [], [], []
    for s in scenes:
        img = os.path.join(ep, "assets", "images", s["id"] + ".png")
        if not os.path.exists(img):
            missing.append(s["id"])
            img = os.path.join(ph_dir, s["id"] + ".png")
            if not os.path.exists(img):
                placeholder(s, img)
        clip = os.path.join(clips_dir, f"{s['id']}-{s['cam']}-{round(s['dur'] * FPS)}f.mp4")
        clips.append(clip)
        if not os.path.exists(clip) or os.path.getmtime(clip) < os.path.getmtime(img):
            jobs.append((img, s, clip))
    if missing:
        print(f"  {len(missing)} scenes still on placeholder cards: {', '.join(missing[:12])}"
              + (" ..." if len(missing) > 12 else ""))
    print(f"  rendering {len(jobs)} of {len(clips)} clips at {tag} (2 workers, cores 0-1)")
    with concurrent.futures.ThreadPoolExecutor(2) as pool:
        for f in concurrent.futures.as_completed([pool.submit(_clip, *j, size, preset, crf) for j in jobs]):
            f.result()
    listing = os.path.join(clips_dir, "concat.txt")
    open(listing, "w").write("".join(f"file '{os.path.abspath(c)}'\n" for c in clips))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", listing,
                    "-c", "copy", out], check=True)
    return out


# ---------- sound ----------

def load_audio(path):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                       capture_output=True, check=True)
    return np.frombuffer(r.stdout, dtype="<f4").astype(np.float64)


def build_audio(ep, scenes, total, music_gain=0.09):
    n = int(total * SR)
    bus = np.zeros(n)
    for s in scenes:
        if s["voice"]:
            place(bus, load_audio(s["voice"]), s["start"] + LEAD)
        if s["sfx"]:
            place(bus, SFX[s["sfx"]](), s["start"], 0.2)
    music = sorted(glob.glob(os.path.join(ep, "assets", "music.*")))
    if music:
        m = load_audio(music[0])
        m = np.tile(m, n // len(m) + 1)[:n]
        fade = np.ones(n)
        fade[:2 * SR] = np.linspace(0, 1, 2 * SR)
        fade[-4 * SR:] = np.linspace(1, 0, 4 * SR)
        bus += m * fade * music_gain
    return bus


def master(bus, video, out, total, lufs=-14.0):
    """Fixed gain to `lufs` plus a -2 dB limiter (same mastering as cartoon_sfx.render), mux onto the video."""
    mix = os.path.splitext(out)[0] + "-mix.wav"
    pcm = np.clip(bus, -1, 1).astype("<f4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-",
                    "-ac", "2", "-c:a", "pcm_f32le", mix], input=pcm.tobytes(), check=True)
    gain = lufs - _measure_lufs(mix) if np.abs(bus).max() > 1e-4 else 0.0
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-i", mix, "-map", "0:v", "-map", "1:a",
                    "-af", f"volume={gain:.2f}dB,alimiter=limit=0.79:attack=3:release=60:level=false",
                    "-t", f"{total:.3f}", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", str(SR),
                    "-movflags", "+faststart", out], check=True)
    os.remove(mix)


def render(ep, scenes, slug, preview=False):
    size, preset, crf = ((1280, 720), "veryfast", 23) if preview else ((1920, 1080), "medium", 18)
    total = timeline(ep, scenes)
    voiced = sum(1 for s in scenes if s["voice"])
    print(f"{len(scenes)} scenes, {stamp(total)} total, {voiced} with voice")
    renders = os.path.join(ep, "renders")
    base = os.path.join(renders, slug + ("-preview" if preview else ""))
    silent = render_video(ep, scenes, base + "-video.mp4", size, preset, crf)
    master(build_audio(ep, scenes, total), silent, base + ".mp4", total)
    os.remove(silent)
    write_captions(ep, scenes, base)
    print(f"-> {base}.mp4 (+ .srt, -chapters.txt)")
    return base + ".mp4"


# ---------- thumbnail ----------

def thumbnail(ep, lines, out, bg=None):
    """1280x720: the art (assets/thumb.png, or a placeholder) with 1-2 huge outlined words top-left.

    Text is set here, not in the image model, because generated lettering comes out misspelled.
    lines: [(text, (r, g, b)), ...]
    """
    W, H = 1280, 720
    bg = bg or os.path.join(ep, "assets", "thumb.png")
    if os.path.exists(bg):
        im = Image.open(bg).convert("RGB")
        k = max(W / im.width, H / im.height)
        im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
        im = im.crop(((im.width - W) // 2, (im.height - H) // 2, (im.width - W) // 2 + W, (im.height - H) // 2 + H))
    else:
        im = Image.new("RGB", (W, H), (40, 52, 92))
    d = ImageDraw.Draw(im)
    font_path = os.path.join(CHANNEL, "brand", "fonts", "LuckiestGuy-Regular.ttf")
    y = 34
    for text, color in lines:
        size = 200
        while size > 60:
            f = ImageFont.truetype(font_path, size)
            if d.textlength(text, font=f) <= W * 0.62:
                break
            size -= 6
        d.text((48 + 8, y + 10), text, font=f, fill=(15, 20, 40), stroke_width=14, stroke_fill=(15, 20, 40))
        d.text((48, y), text, font=f, fill=color, stroke_width=12, stroke_fill=(22, 28, 56))
        y += int(size * 0.92)
    im.save(out)
    print(f"-> {out}")
