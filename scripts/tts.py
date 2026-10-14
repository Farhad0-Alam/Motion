#!/usr/bin/env python3
"""Kokoro text-to-speech for any supported language.

Japanese and Mandarin are converted to phonemes with misaki first: espeak-ng,
which kokoro-onnx uses by default, mispronounces them badly.

    python3 scripts/tts.py "Hola, bienvenidos." -l es -o hola.wav
    python3 scripts/tts.py "こんにちは。" -l ja -o hello.wav
    python3 scripts/tts.py --list-voices

Default voice per language is used unless --voice is given.
"""
import argparse
import os
import sys

import soundfile as sf
from kokoro_onnx import Kokoro

CACHE = os.path.expanduser("~/.cache/hyperframes/tts")
MODEL = f"{CACHE}/models/kokoro-v1.0.onnx"
VOICES = f"{CACHE}/voices/voices-v1.0.bin"

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


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("text", nargs="?", help="text to speak, or a path to a .txt file")
    ap.add_argument("-l", "--lang", default="en", choices=sorted(LANGS))
    ap.add_argument("-v", "--voice", help="Kokoro voice id (default depends on --lang)")
    ap.add_argument("-s", "--speed", type=float, default=1.0)
    ap.add_argument("-o", "--output", default="speech.wav")
    ap.add_argument("--list-voices", action="store_true")
    args = ap.parse_args()

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
