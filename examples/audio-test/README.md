# Audio test

HyperFrames "swiss-grid" example extended to 14.5s with a voiceover, a music bed
and sound effects.

- `assets/audio/vo_*.wav`: Kokoro TTS (voice `af_heart`), loudness-matched to about -16 LUFS
- `assets/audio/bgm.mp3`: ambient pad synthesized with SoX, ducked under the voice
  through `data-automation` on `#bgm`
- `assets/audio/*.mp3` effects: from the bundled HyperFrames SFX library
- `vendor/gsap.min.js`: local GSAP, so rendering does not need the jsDelivr CDN

Regenerate the voice and re-sync the captions, then render:

```bash
python3 tools/voice.py assets/audio     # writes vo_*.wav and vo.json
python3 tools/captions.py .             # re-times caption words to the voice
npm run render -- -q delivery
```

`voice.py` doesn't loudness-match its output; the committed clips were
leveled afterwards with ffmpeg.
