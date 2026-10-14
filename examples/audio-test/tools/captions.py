# Re-times the caption words to the generated voiceover lines.
import json, re, sys
import numpy as np
import soundfile as sf

demo = sys.argv[1]
meta = json.load(open(f"{demo}/assets/audio/vo.json"))
words = []
for line in meta:
    audio, sr = sf.read(f"{demo}/{line['file']}")
    loud = np.flatnonzero(np.abs(audio) > 0.02)
    on, off = loud[0] / sr, loud[-1] / sr          # trim Kokoro's lead/tail silence
    toks = line["text"].split()
    weight = [len(re.sub(r"[^\w]", "", t)) + 2 for t in toks]  # syllable-ish proxy
    t = line["start"] + on
    span = off - on
    for tok, w in zip(toks, weight):
        d = span * w / sum(weight)
        words.append({"text": tok, "start": round(t, 3), "end": round(t + d * 0.92, 3)})
        t += d
path = f"{demo}/compositions/captions.html"
html = open(path).read()
body = ",\n".join(f'          {{ text: {json.dumps(w["text"])}, start: {w["start"]}, end: {w["end"]} }}' for w in words)
html, n = re.subn(r"const TRANSCRIPT = \[.*?\n\s*\];", "const TRANSCRIPT = [\n" + body + ",\n        ];", html, flags=re.S)
assert n == 1
open(path, "w").write(html)
print(len(words), "words, last ends at", words[-1]["end"])
