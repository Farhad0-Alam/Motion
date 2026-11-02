"""Build 480.00s Master Voiceover Track + Frame-Exact Subtitle & SRT Table.

Maps the 13 chapters of part_a_clean.wav (79 chunks) and part_b_clean.wav (63 chunks)
onto shwbster's exact 13 YouTube Chapter timestamps:
  00:00 Opening hook (28s)
  00:28 How the comparison works (12s)
  00:40 Number 10 Dubai (40s)
  01:20 Number 9 San Francisco (40s)
  02:00 Number 8 Singapore (40s)
  02:40 Number 7 Bern (48s)
  03:28 Number 6 Tel Aviv (40s)
  04:08 Number 5 Hong Kong (40s)
  04:48 Number 4 Zurich (40s)
  05:28 Number 3 London (40s)
  06:08 Number 2 Geneva (40s)
  06:48 Number 1 New York (48s)
  07:36 Closing question (24s -> 08:00 / 480.00s)
"""
import base64
import json
import os
import subprocess
import urllib.request
import wave
import numpy as np

AUDIO_DIR = "/root/Motion/shwbster_order/audio"
RAW_JSON = os.path.join(AUDIO_DIR, "raw_chunks.json")
OUT_WAV = os.path.join(AUDIO_DIR, "master_vo_480s.wav")
OUT_SUBS = os.path.join(AUDIO_DIR, "subtitles_480s.json")
OUT_SRT = "/root/Motion/shwbster_order/The_Worlds_10_Most_Expensive_Cities.srt"

# Exact 13 sections: (source_key, start_chunk_idx, end_chunk_idx_inclusive, win_start_sec, win_end_sec, lead_in, tail_out, chapter_name)
SECTIONS = [
    ("part_a", 0,  9,   0.0,  28.0, 0.30, 1.30, "Opening hook"),
    ("part_a", 10, 13, 28.0,  40.0, 0.30, 0.70, "How the comparison works"),
    ("part_a", 14, 27, 40.0,  80.0, 0.35, 1.40, "Number 10 Dubai"),
    ("part_a", 28, 41, 80.0, 120.0, 0.35, 1.40, "Number 9 San Francisco"),
    ("part_a", 42, 52, 120.0, 160.0, 0.35, 1.40, "Number 8 Singapore"),
    ("part_a", 53, 67, 160.0, 208.0, 0.35, 1.50, "Number 7 Bern"),
    ("part_a", 68, 78, 208.0, 248.0, 0.35, 1.40, "Number 6 Tel Aviv"),
    ("part_b", 0,  9,  248.0, 288.0, 0.35, 1.40, "Number 5 Hong Kong"),
    ("part_b", 10, 21, 288.0, 328.0, 0.35, 1.40, "Number 4 Zurich"),
    ("part_b", 22, 30, 328.0, 368.0, 0.35, 1.50, "Number 3 London"),
    ("part_b", 31, 42, 368.0, 408.0, 0.35, 1.40, "Number 2 Geneva"),
    ("part_b", 43, 56, 408.0, 456.0, 0.35, 1.60, "Number 1 New York"),
    ("part_b", 57, 62, 456.0, 480.0, 0.40, 2.80, "Closing question"),
]

SCRIPT_PART_A = """Fifty-four thousand dollars a year... for one bedroom. That's roughly the average annual rent for a city-centre one-bedroom in New York. Before bills. Before food. Before you've even stepped outside. Think Dubai is expensive? Nine cities rank above it. And one quieter city on this list has lower rent than Dubai. So what are you actually paying for? Our ranking follows ECA International's 2026 cost-of-living list for international employees. Rent figures are Numbeo estimates for a one-bedroom, in US dollars, before bills. Ten. Dubai. The Burj Khalifa sells you the dream. The rent tells you what it costs. Our central one-bedroom estimate is about two thousand six hundred dollars a month, though actual prices vary with the neighbourhood, the building and the view. Outside the centre, the estimate falls to roughly one thousand five hundred. That's a gap of around one thousand one hundred dollars every month. So when you see a glossy apartment tour, ask which neighbourhood you're actually being shown. The skyline can look identical in the thumbnail while the commute and the bill look very different. Nine. San Francisco. A central one-bedroom costs around three thousand seven hundred dollars a month in our snapshot. That's forty-four thousand four hundred dollars a year, before bills. The Golden Gate Bridge is free to admire. Keeping a roof over your head is the expensive part. Outside the centre, the estimate drops to two thousand seven hundred a month. Over a year, that difference adds up to twelve thousand dollars. So before falling for the skyline, compare the bedroom, the kitchen and the journey to work. How much of that rent buys convenience and how much buys actual space? Eight. Singapore. Our central one-bedroom estimate is three thousand two hundred dollars a month. Outside the centre, it's about two thousand two hundred. That's a thousand-dollar gap before you've even decided how to get around. And that decision matters here. To own a new car, you'll first need a Certificate of Entitlement, normally valid for ten years and paid for separately from the vehicle itself. So compare life around the MRT with life built around a car. The skyline is the postcard. Your housing and transport choices decide the everyday bill. Seven. Bern. Here's the surprise. This quiet Swiss city ranks above Dubai, yet it has the lowest central rent on our list: around two thousand one hundred dollars a month. Outside the centre, it's about one thousand six hundred. Now add lunch. Numbeo puts a meal at an inexpensive restaurant at twenty-four Swiss francs, roughly twenty-nine US dollars. Eat out regularly, and those ordinary purchases add up fast. That's why the overall ranking and the rent comparison tell different stories. The old-town streets look a world away from Dubai's towers. But a lower housing bill can still sit inside an expensive everyday life. Six. Tel Aviv. The beach is the easy part of the sales pitch. The housing bill takes more thought. Our central one-bedroom estimate is about two thousand three hundred dollars a month, dropping to one thousand seven hundred outside the centre. That frees up roughly six hundred dollars a month for everything else. A seafront apartment and one on an ordinary residential street can feel like different cities. So compare the usable space, the condition of the building and the actual route to work. A coastal address sounds wonderful. But it's the everyday flat you actually live in."""

SCRIPT_PART_B = """Five. Hong Kong. Residential towers crowd the harbour view. Yet government figures put about forty percent of the territory inside country parks and special areas. The skyline is only part of the map. Our central one-bedroom estimate is around two thousand four hundred dollars a month, compared with one thousand eight hundred outside the centre. When it comes to the flat itself, compare floor area, not just bedrooms. A compact one-bedroom and a spacious one share the same label. Storage, daylight and kitchen layout show you what the monthly figure actually buys. Four. Zurich. Our central one-bedroom benchmark is around two thousand nine hundred dollars a month. Outside the centre, it falls to about two thousand one hundred. That's roughly eight hundred dollars between the two. The trams, the lakeside and the old town make a convincing case for living here. But the decision still comes down to the money you keep after the essentials. Rent, food, transport and household bills all have to fit inside the same monthly budget. And that beautiful flat looks very different when there's little left after paying for it. Three. London. Tower Bridge is the easy introduction. For a tenant, the harder number is the rent: about two thousand nine hundred US dollars a month for a central one-bedroom, or roughly two thousand one hundred and fifty pounds. Outside the centre, the dollar estimate falls to two thousand three hundred. That saving matters, but so does the route to work. Count the changes, the walking and the fares before choosing the cheaper flat. Put the rent and the commute together, and you get a far more useful price. Two. Geneva. The Jet d'Eau gives the city its signature view. Our central one-bedroom figure is about two thousand nine hundred dollars a month, level with Zurich once rounded. Outside the centre, it's around two thousand two hundred. Yet Geneva ranks two places higher. That's another reason to keep the overall ranking separate from the rent comparison. Matching rents don't mean matching living costs. Before choosing between cities, compare your full budget in the currency you'll actually be paid in. A neat dollar figure makes comparison easy. Your own circumstances decide whether it's affordable. One. New York. Remember that opening figure? A city-centre one-bedroom averages roughly four thousand five hundred dollars a month in our snapshot. Multiply that by twelve and you're at fifty-four thousand dollars a year. Outside the centre, the estimate is around three thousand a month, or thirty-six thousand a year. That's a difference of roughly eighteen thousand dollars a year. And that's before the rest of daily life. So the layout, the daylight and the actual commute all matter. The famous view is a bonus. The bill arrives every month. Would the address be worth it to you? Across these cities, the useful number is what you have left after the essentials. Compare like with like, include the commute, and treat any average as a starting point. Which city would you pay a premium for? Tell us in the comments, and subscribe for more comparisons of what your money actually buys."""


def transcribe_chunks(part_key, wav_path, chunks, ref_script, gkey):
    mp3_path = os.path.join(AUDIO_DIR, f"{part_key}_tmp.mp3")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", wav_path, "-b:a", "48k", mp3_path], check=True)
    b64 = base64.b64encode(open(mp3_path, "rb").read()).decode()
    chunk_lines = "\n".join(f"[{i}] {c['start']:.2f}s - {c['end']:.2f}s (dur={c['dur']:.2f}s)" for i, c in enumerate(chunks))
    prompt = f"""Listen to this narration audio and align the exact spoken words to each numbered timestamp chunk below.
Reference script for spelling/numbers (use clean figures/currency in subtitles where helpful or exact words, e.g. '$54,000 a year.' or '≈ $2,600 a month' or clear short subtitle text, preserving every spoken word accurately):
{ref_script}

Chunks:
{chunk_lines}

Return ONLY valid JSON: a list of objects [{{"idx": 0, "text": "..."}}, ...] with exact length {len(chunks)} covering every chunk 0 to {len(chunks)-1}."""

    payload = {
        "contents": [{"parts": [
            {"inlineData": {"mimeType": "audio/mp3", "data": b64}},
            {"text": prompt}
        ]}],
        "generationConfig": {"responseMimeType": "application/json"}
    }
    req = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key={gkey}",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"}
    )
    resp = json.loads(urllib.request.urlopen(req, timeout=90).read().decode())
    txt = resp["candidates"][0]["content"]["parts"][0]["text"]
    return json.loads(txt)


def main():
    env = dict(line.strip().split("=", 1) for line in open("/root/youtubeai/.env") if "=" in line and not line.startswith("#"))
    gkey = env.get("GEMINI_API_KEY", "").strip().strip('"')
    raw = json.load(open(RAW_JSON))

    labels_path = os.path.join(AUDIO_DIR, "chunk_labels.json")
    if os.path.exists(labels_path):
        labels = json.load(open(labels_path))
    else:
        print("Aligning Part A chunks...")
        la = transcribe_chunks("part_a", os.path.join(AUDIO_DIR, "part_a_clean.wav"), raw["part_a"], SCRIPT_PART_A, gkey)
        print("Aligning Part B chunks...")
        lb = transcribe_chunks("part_b", os.path.join(AUDIO_DIR, "part_b_clean.wav"), raw["part_b"], SCRIPT_PART_B, gkey)
        labels = {"part_a": {str(x["idx"]): x["text"] for x in la}, "part_b": {str(x["idx"]): x["text"] for x in lb}}
        open(labels_path, "w").write(json.dumps(labels, indent=2))
        print("Saved chunk_labels.json!")

    # Load audio waveforms (24000 Hz mono)
    pcm_data = {}
    sr = 24000
    for k in ("part_a", "part_b"):
        with wave.open(os.path.join(AUDIO_DIR, f"{k}_clean.wav"), "rb") as w:
            sr = w.getframerate()
            pcm_data[k] = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32)

    master = np.zeros(int(sr * 480.0), dtype=np.float32)
    placed_subs = []

    for src_key, i0, i1, w_start, w_end, lead_in, tail_out, ch_name in SECTIONS:
        sec_chunks = raw[src_key][i0:i1 + 1]
        total_speech = sum(c["dur"] for c in sec_chunks)
        orig_gaps = [sec_chunks[j]["sil_after"] for j in range(len(sec_chunks) - 1)]
        total_orig_gaps = sum(orig_gaps)
        avail_window = (w_end - w_start) - lead_in - tail_out
        target_gaps_sum = max(avail_window - total_speech, 0.1 * len(orig_gaps))

        # Scale internal pauses proportionally to original pause lengths so natural sentence phrasing is preserved!
        scale = target_gaps_sum / max(total_orig_gaps, 0.01)
        new_gaps = [g * scale for g in orig_gaps]

        cur_t = w_start + lead_in
        for local_j, c in enumerate(sec_chunks):
            global_idx = i0 + local_j
            # Include a tiny 35ms pad around speech chunk with 15ms cosine fade to avoid any click
            s_sec = max(0.0, c["start"] - 0.03)
            e_sec = min(len(pcm_data[src_key]) / sr, c["end"] + 0.04)
            s_smp = int(round(s_sec * sr))
            e_smp = int(round(e_sec * sr))
            seg = pcm_data[src_key][s_smp:e_smp].copy()
            fade_len = min(int(0.015 * sr), len(seg) // 4)
            if fade_len > 1:
                ramp = np.linspace(0.0, 1.0, fade_len, dtype=np.float32)
                seg[:fade_len] *= ramp
                seg[-fade_len:] *= ramp[::-1]

            dst_s = int(round(cur_t * sr))
            dst_e = min(dst_s + len(seg), len(master))
            master[dst_s:dst_e] += seg[:dst_e - dst_s]

            txt = labels[src_key].get(str(global_idx), "").strip()
            chunk_dur = (dst_e - dst_s) / sr
            if txt:
                placed_subs.append({
                    "chapter": ch_name,
                    "src": src_key,
                    "idx": global_idx,
                    "start": round(cur_t, 2),
                    "end": round(cur_t + chunk_dur, 2),
                    "text": txt
                })
            cur_t += c["dur"]
            if local_j < len(new_gaps):
                cur_t += new_gaps[local_j]

        print(f"{ch_name:26s} | Window {w_start:6.1f}s -> {w_end:6.1f}s | Speech ends at {cur_t:6.2f}s (gap scale={scale:.2f}x)")

    # Write 480.00s Master Voiceover WAV
    master_i16 = np.clip(master, -32768, 32767).astype(np.int16)
    with wave.open(OUT_WAV, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(master_i16.tobytes())

    open(OUT_SUBS, "w").write(json.dumps(placed_subs, indent=2))

    # Also write clean SRT file (merging very short adjacent "<0.6s" rank number + city name like "Ten." + "Dubai." if within 1.2s)
    def fmt_srt(sec):
        ms = int(round(sec * 1000))
        h, ms = divmod(ms, 3600000)
        m, ms = divmod(ms, 60000)
        s, ms = divmod(ms, 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

    srt_blocks = []
    for idx, s in enumerate(placed_subs, 1):
        srt_blocks.append(f"{idx}\n{fmt_srt(s['start'])} --> {fmt_srt(s['end'])}\n{s['text']}\n")
    open(OUT_SRT, "w").write("\n".join(srt_blocks))
    print(f"SUCCESS: {OUT_WAV} (480.00s) + {len(placed_subs)} subtitle cues -> {OUT_SRT}")


if __name__ == "__main__":
    main()

