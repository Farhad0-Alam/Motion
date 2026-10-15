#!/usr/bin/env bash
# Renders each thumbnail SVG to a 1280x720 PNG and JPG with Chrome (so the
# brand web fonts embedded via @font-face are used), then builds a preview
# sheet at YouTube's real display sizes with the duration badge overlaid.
set -euo pipefail
cd "$(dirname "$0")"
CHROME=$(ls /root/.cache/hyperframes/chrome/chrome-headless-shell/*/chrome-headless-shell-linux64/chrome-headless-shell | tail -1)
mkdir -p out
for svg in *.svg; do
  name=${svg%.svg}
  "$CHROME" --headless --no-sandbox --hide-scrollbars --disable-gpu --allow-file-access-from-files \
    --window-size=1280,720 --virtual-time-budget=3000 --screenshot="$PWD/out/$name.png" "file://$PWD/$svg" >/dev/null 2>&1
  magick "out/$name.png" -strip -quality 92 "out/$name.jpg"
done
# Preview: big (home feed), 320x180 (search), 168x94 (suggested / mobile sidebar), with "3:06" badge.
for f in out/*.png; do
  [[ $f == *preview* ]] && continue
  n=$(basename "$f" .png)
  for w in 640 320 168; do
    h=$((w * 9 / 16)); fs=$((w / 22 + 6))
    magick "$f" -resize ${w}x${h} \( -size $((fs * 3))x$((fs + 6)) xc:'#000000cc' -fill white -font DejaVu-Sans-Bold \
      -pointsize $fs -gravity center -annotate +0+0 '3:06' \) -gravity southeast -geometry +$((w / 80 + 2))+$((w / 80 + 2)) \
      -composite "out/.p-$n-$w.png"
  done
  magick "out/.p-$n-640.png" \( "out/.p-$n-320.png" "out/.p-$n-168.png" -background '#202020' -gravity north -append \) \
    -background '#202020' -gravity north +append -bordercolor '#202020' -border 12 "out/.row-$n.png"
done
magick out/.row-*.png -background '#202020' -append out/preview-sheet.png
rm -f out/.p-* out/.row-*
ls -la out
