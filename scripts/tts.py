#!/usr/bin/env python3
"""Text-to-speech with Kokoro (local, free) or ElevenLabs (channel voice).

Kokoro: Japanese and Mandarin are converted to phonemes with misaki first:
espeak-ng, which kokoro-onnx uses by default, mispronounces them badly.

    python3 scripts/tts.py "Hola, bienvenidos." -l es -o hola.wav
    python3 scripts/tts.py "こんにちは。" -l ja -o hello.wav
    python3 scripts/tts.py --list-voices

ElevenLabs: channel voice Brian on eleven_v4, which supports expression tags
such as [curious], [warmly] and [pause]. Reads ELEVENLABS_API_KEY from the
environment or from .env in the repo root. Output is MP3.

    python3 scripts/tts.py "[curious] Who answers?" -e elevenlabs -o line.mp3

Default voice per language is used unless --voice is given.
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request

CACHE = os.path.expanduser("~/.cache/hyperframes/tts")
MODEL = f"{CACHE}/models/kokoro-v1.0.onnx"
VOICES = f"{CACHE}/voices/voices-v1.0.bin"

# ElevenLabs channel voice: "Brian" (deep US narrator), chosen October 2026.
EL_VOICE = "nPczCjzI2devNBz1zQrb"
EL_MODEL = "eleven_v4"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# language -> (kokoro-onnx lang code, default voice)
LANGS = {
    "en": ("en-us", "af_heart"),
    "en-gb": ("en-gb", "bf_emma"),
    "es": ("es", "ef_dora"),
    "fr": ("fr-fr", "ff_siwis"),
    "hi": ("hi", "hf_alpha"),
    "it": ("it", "if_sara"),
    "pt": ("pt-br", "pf_dora"),
    "ja": ("ja", "jf_alpha"),
    "zh": ("cmn", "zf_xiaobei"),
}


def to_phonemes(text, lang):
    if lang == "ja":
        from misaki import ja
        g2p = ja.JAG2P()
    elif lang == "zh":
        from misaki import zh
        g2p = zh.ZHG2P()
    else:
        return None
    result = g2p(text)
    return result[0] if isinstance(result, tuple) else result


def elevenlabs_key():
    key = os.environ.get("ELEVENLABS_API_KEY")
    env = os.path.join(REPO, ".env")
    if not key and os.path.isfile(env):
        with open(env, encoding="utf-8") as f:
            for line in f:
                name, _, value = line.strip().partition("=")
                if name == "ELEVENLABS_API_KEY":
                    key = value.strip().strip("'\"")
    if not key:
        sys.exit("ELEVENLABS_API_KEY is not set (environment or .env)")
    return key


def elevenlabs(text, voice, model, output):
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice}?output_format=mp3_44100_128",
        data=json.dumps({"text": text, "model_id": model}).encode(),
        headers={"xi-api-key": elevenlabs_key(), "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=300) as resp, open(output, "wb") as f:
            f.write(resp.read())
    except urllib.error.HTTPError as e:
        sys.exit(f"ElevenLabs error {e.code}: {e.read().decode(errors='replace')[:300]}")
    print(f"{output}: {len(text)} characters, voice {voice}, model {model}", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("text", nargs="?", help="text to speak, or a path to a .txt file")
    ap.add_argument("-e", "--engine", default="kokoro", choices=["kokoro", "elevenlabs"])
    ap.add_argument("-m", "--model", default=EL_MODEL, help="ElevenLabs model id")
    ap.add_argument("-l", "--lang", default="en", choices=sorted(LANGS))
    ap.add_argument("-v", "--voice", help="Kokoro voice, or ElevenLabs voice id (default: per language / Brian)")
    ap.add_argument("-s", "--speed", type=float, default=1.0)
    ap.add_argument("-o", "--output", default="speech.wav")
    ap.add_argument("--list-voices", action="store_true")
    args = ap.parse_args()

    if args.engine == "elevenlabs":
        if not args.text:
            ap.error("text is required")
        text = args.text
        if os.path.isfile(text):
            with open(text, encoding="utf-8") as f:
                text = f.read().strip()
        elevenlabs(text, args.voice or EL_VOICE, args.model, args.output)
        return

    import soundfile as sf
    from kokoro_onnx import Kokoro

    kokoro = Kokoro(MODEL, VOICES)
    if args.list_voices:
        print("\n".join(sorted(kokoro.get_voices())))
        return
    if not args.text:
        ap.error("text is required")

    text = args.text
    if os.path.isfile(text):
        with open(text, encoding="utf-8") as f:
            text = f.read().strip()

    code, default_voice = LANGS[args.lang]
    voice = args.voice or default_voice
    phonemes = to_phonemes(text, args.lang)
    if phonemes is not None:
        audio, sr = kokoro.create(phonemes, voice=voice, speed=args.speed, is_phonemes=True)
    else:
        audio, sr = kokoro.create(text, voice=voice, speed=args.speed, lang=code)
    sf.write(args.output, audio, sr)
    print(f"{args.output}: {len(audio) / sr:.2f}s, voice {voice}", file=sys.stderr)


if __name__ == "__main__":
    main()
