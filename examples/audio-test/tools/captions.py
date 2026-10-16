# Times the caption words from the voiceover itself.
#
# Each vo_*.wav is transcribed with `hyperframes transcribe` (Parakeet when it
# is installed, else whisper) to get real word timings. The words shown on
# screen stay the script's words from vo.json: the recogniser may write
# "62%" where the script says "Sixty-two percent", so script words are mapped
# onto the recognised timings by their position in the spoken letters.
#
#     python3 tools/captions.py .
import json, re, subprocess, sys, tempfile
from pathlib import Path

demo = Path(sys.argv[1])
pin = re.search(r"hyperframes@[\w.-]+", (demo / "package.json").read_text()).group(0)

ONES = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split()
TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()


def number_words(n):
    if n < 20:
        return ONES[n]
    if n < 100:
        return TENS[n // 10] + ("" if n % 10 == 0 else ONES[n % 10])
    return ONES[n // 100] + "hundred" + ("" if n % 100 == 0 else number_words(n % 100))


def spoken(token):
    """Letters a token is pronounced with: "62%" -> "sixtytwopercent"."""
    token = token.lower().replace("%", " percent")
    token = re.sub(r"\d+", lambda m: number_words(int(m.group(0))), token)
    return re.sub(r"[^a-z]", "", token)


def transcribe(wav):
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["npx", "--yes", pin, "transcribe", str(wav.resolve()), "--json", "-d", tmp],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return json.loads((Path(tmp) / "transcript.json").read_text())


def align(script_tokens, asr_words):
    """Give each script token the time span of the recognised letters it covers."""
    marks = []  # (letter offset, time) along the recognised speech
    pos = 0
    for w in asr_words:
        n = max(1, len(spoken(w["text"])))
        marks.append((pos, w["start"]))
        marks.append((pos + n, w["end"]))
        pos += n
    ratio = pos / sum(max(1, len(spoken(t))) for t in script_tokens)

    def time_at(offset):
        offset *= ratio  # absorb small spelling differences
        for (p0, t0), (p1, t1) in zip(marks, marks[1:]):
            if offset <= p1:
                return t0 if p1 == p0 else t0 + (t1 - t0) * (offset - p0) / (p1 - p0)
        return marks[-1][1]

    out, pos = [], 0
    for tok in script_tokens:
        n = max(1, len(spoken(tok)))
        out.append((tok, time_at(pos + 1e-6), time_at(pos + n)))
        pos += n
    return out


words = []
for line in json.loads((demo / "assets/audio/vo.json").read_text()):
    asr = transcribe(demo / line["file"])
    for tok, start, end in align(line["text"].split(), asr):
        words.append({"text": tok, "start": round(line["start"] + start, 3),
                      "end": round(line["start"] + end, 3)})

path = demo / "compositions/captions.html"
html = path.read_text()
body = ",\n".join(f'          {{ text: {json.dumps(w["text"])}, start: {w["start"]}, end: {w["end"]} }}' for w in words)
html, n = re.subn(r"const TRANSCRIPT = \[.*?\];", lambda _: "const TRANSCRIPT = [\n" + body + ",\n        ];", html, flags=re.S)
assert n == 1
path.write_text(html)
print(len(words), "words, last ends at", words[-1]["end"])
