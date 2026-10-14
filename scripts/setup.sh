#!/usr/bin/env bash
# Installs the toolchain for this project: HyperFrames (pinned in package.json),
# its headless Chrome, and a static FFmpeg build.
set -euo pipefail

FFMPEG_VERSION="${FFMPEG_VERSION:-9.0}"
PREFIX="${PREFIX:-/usr/local/bin}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "==> Installing HyperFrames"
(cd "$ROOT" && npm ci)

echo "==> Installing FFmpeg ${FFMPEG_VERSION}"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
name="ffmpeg-n${FFMPEG_VERSION}-latest-linux64-gpl-${FFMPEG_VERSION}"
curl -fsSL -o "$tmp/ffmpeg.tar.xz" \
  "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/${name}.tar.xz"
tar -xf "$tmp/ffmpeg.tar.xz" -C "$tmp"
install -m 755 "$tmp/$name/bin/ffmpeg" "$tmp/$name/bin/ffprobe" "$PREFIX/"

echo "==> Installing headless Chrome for HyperFrames"
(cd "$ROOT" && npx hyperframes browser ensure)

ffmpeg -version | head -1
(cd "$ROOT" && npx hyperframes --version)
