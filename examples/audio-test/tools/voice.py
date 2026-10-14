import json, sys
import soundfile as sf
from kokoro_onnx import Kokoro

out = sys.argv[1]
k = Kokoro("/root/.cache/hyperframes/tts/models/kokoro-v1.0.onnx",
           "/root/.cache/hyperframes/tts/voices/voices-v1.0.bin")
# (start, window end, text) — windows follow the graphics scene changes
lines = [
    (0.15, 1.80, "We asked what you needed."),
    (1.95, 4.55, "Forty-seven percent of you said motion graphics."),
    (4.75, 8.75, "Sixty-two percent said static content was costing you attention."),
    (8.95, 14.0, "And three out of four said you know the look you want, but don't have the editing skills."),
]
meta = []
for i, (start, end, text) in enumerate(lines):
    speed = 1.0
    while True:
        audio, sr = k.create(text, voice="af_heart", speed=speed, lang="en-us")
        dur = len(audio) / sr
        if start + dur <= end or speed >= 1.35:
            break
        speed = round(speed + 0.05, 2)
    path = f"{out}/vo_{i + 1}.wav"
    sf.write(path, audio, sr)
    meta.append({"file": f"assets/audio/vo_{i + 1}.wav", "start": start,
                 "duration": round(dur, 3), "speed": speed, "text": text})
    print(f"line {i + 1}: {dur:.2f}s at speed {speed} (window {end - start:.2f}s)")
json.dump(meta, open(f"{out}/vo.json", "w"), indent=2)
