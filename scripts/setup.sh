#!/usr/bin/env bash
# Installs the full toolchain for this project:
#   - HyperFrames (pinned in package.json) + its headless Chrome
#   - FFmpeg static build (ffmpeg + ffprobe)
#   - Media tools: ImageMagick, SoX, MediaInfo, Inkscape, Blender, x264/x265, ...
#   - Multilingual fonts (Noto incl. CJK/Arabic/Indic/Thai, emoji) + common UI fonts
#   - whisper.cpp (transcription), Kokoro (local TTS), MusicGen deps (local BGM)
#   - Whisper / Kokoro / background-removal model files
#   - espeak-ng (non-English Kokoro voices), ElevenLabs and Gemini SDKs
# Set SKIP_APT=1, SKIP_WHISPER=1, SKIP_PYTHON=1 or SKIP_MODELS=1 to skip a stage.
set -euo pipefail

FFMPEG_VERSION="${FFMPEG_VERSION:-9.0}"
WHISPER_MODELS="${WHISPER_MODELS:-large-v3-turbo small small.en}"
PREFIX="${PREFIX:-/usr/local/bin}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HF_CACHE="$HOME/.cache/hyperframes"

echo "==> Installing HyperFrames"
(cd "$ROOT" && npm ci)

if [ -z "${SKIP_APT:-}" ]; then
  echo "==> Installing media tools and fonts"
  export DEBIAN_FRONTEND=noninteractive
  apt-get update -qq
  apt-get install -y -qq --no-install-recommends \
    imagemagick sox libsox-fmt-all mediainfo gifsicle webp librsvg2-bin potrace \
    inkscape blender x264 x265 fontconfig cmake build-essential espeak-ng \
    fonts-noto-core fonts-noto-extra fonts-noto-ui-core fonts-noto-cjk \
    fonts-noto-cjk-extra fonts-noto-color-emoji fonts-noto-mono \
    fonts-liberation2 fonts-dejavu fonts-roboto fonts-open-sans fonts-inter \
    fonts-ibm-plex fonts-jetbrains-mono fonts-lato fonts-montserrat fonts-firacode \
    fonts-sil-padauk fonts-beng fonts-deva fonts-arabeyes fonts-hosny-amiri \
    fonts-vazirmatn fonts-thai-tlwg fonts-unfonts-core
  fc-cache -f >/dev/null
fi

echo "==> Installing FFmpeg ${FFMPEG_VERSION}"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
name="ffmpeg-n${FFMPEG_VERSION}-latest-linux64-gpl-${FFMPEG_VERSION}"
curl -fsSL -o "$tmp/ffmpeg.tar.xz" \
  "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/${name}.tar.xz"
tar -xf "$tmp/ffmpeg.tar.xz" -C "$tmp"
install -m 755 "$tmp/$name/bin/ffmpeg" "$tmp/$name/bin/ffprobe" "$PREFIX/"

if [ -z "${SKIP_WHISPER:-}" ]; then
  echo "==> Building whisper.cpp"
  git clone -q --depth 1 https://github.com/ggml-org/whisper.cpp "$tmp/whisper.cpp"
  cmake -S "$tmp/whisper.cpp" -B "$tmp/whisper.cpp/build" \
    -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED_LIBS=OFF -DWHISPER_BUILD_TESTS=OFF >/dev/null
  cmake --build "$tmp/whisper.cpp/build" -j"$(nproc)" --target whisper-cli >/dev/null
  install -m 755 "$tmp/whisper.cpp/build/bin/whisper-cli" "$PREFIX/"
fi

if [ -z "${SKIP_PYTHON:-}" ]; then
  echo "==> Installing Kokoro TTS and MusicGen dependencies"
  pip install --break-system-packages -q \
    torch torchaudio kokoro-onnx soundfile transformers numpy accelerate scipy librosa \
    elevenlabs google-genai "misaki[ja,zh]"
fi

if [ -z "${SKIP_MODELS:-}" ]; then
  echo "==> Downloading models"
  mkdir -p "$HF_CACHE/whisper/models" "$HF_CACHE/tts/models" "$HF_CACHE/tts/voices"
  kokoro="https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0"
  [ -f "$HF_CACHE/tts/models/kokoro-v1.0.onnx" ] ||
    curl -fsSL -o "$HF_CACHE/tts/models/kokoro-v1.0.onnx" "$kokoro/kokoro-v1.0.onnx"
  [ -f "$HF_CACHE/tts/voices/voices-v1.0.bin" ] ||
    curl -fsSL -o "$HF_CACHE/tts/voices/voices-v1.0.bin" "$kokoro/voices-v1.0.bin"
  bg="$HF_CACHE/background-removal/models/u2net_human_seg.onnx"
  mkdir -p "$(dirname "$bg")"
  [ -f "$bg" ] || curl -fsSL -o "$bg" \
    https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net_human_seg.onnx
  # Whisper models and MusicGen weights come from huggingface.co.
  python3 -c "from transformers import AutoProcessor, MusicgenForConditionalGeneration as M; AutoProcessor.from_pretrained('facebook/musicgen-small'); M.from_pretrained('facebook/musicgen-small')" \
    || echo "warning: could not download MusicGen (is huggingface.co reachable?)"
  for m in $WHISPER_MODELS; do
    f="$HF_CACHE/whisper/models/ggml-$m.bin"
    [ -f "$f" ] || curl -fsSL -o "$f" \
      "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-$m.bin" ||
      { rm -f "$f"; echo "warning: could not download whisper model $m (is huggingface.co reachable?)"; }
  done
fi

echo "==> Installing headless Chrome for HyperFrames"
(cd "$ROOT" && npx hyperframes browser ensure)

(cd "$ROOT" && npx hyperframes doctor) || true
