#!/usr/bin/env python3
"""Builds the full 3:06 (186s) broadcast-quality 9:16 vertical Reel.

Features:
- Dynamic chapter header cards that advance in real-time across all 5 scenes:
  1. 0:00 - 0:20: WHO ANSWERS YOUR CUSTOMERS AT 3 AM?
  2. 0:20 - 0:41: 40 HOURS OPEN vs. 168 HOURS OF MESSAGES
  3. 0:41 - 0:58: PART 1: WEB, VOICE & WHATSAPP
  4. 0:58 - 1:17: PART 2: WHY RAW LLMs FAIL
  5. 1:17 - 1:50: PART 3: HOW RAG PREVENTS HALLUCINATIONS
  6. 1:50 - 2:08: PART 4: AUTOMATIC LEAD CAPTURE
  7. 2:08 - 2:33: THE 3-POINT CHECKLIST (GOOD vs BAD AI)
  8. 2:33 - 3:06: CLIENTFALCON VOICE LIVE & DEPLOY
- Full 3:06 synced dynamic subtitles in the mobile safe zone with Lime highlights
- Ambient blurred video background matching the original footage
- Center bezel 16:9 player with drop shadow
- Outro CTA screen at the end
"""

import os
import re
import subprocess
from PIL import Image, ImageDraw, ImageFont

HERE = "/root/Motion/videos/01-ai-receptionist"
SOURCE_VIDEO = os.path.join(HERE, "renders/ep01-v2-4k.mp4")
SRT_FILE = os.path.join(HERE, "captions.en.srt")
OUT_DIR = os.path.join(HERE, "renders/reels")
CHAPTERS_DIR = os.path.join(OUT_DIR, "chapters")
SUBTITLES_ASS = os.path.join(OUT_DIR, "full_reel_subs.ass")
FINAL_OUTPUT = os.path.join(OUT_DIR, "full-reel-01-ai-receptionist-3min.mp4")

os.makedirs(CHAPTERS_DIR, exist_ok=True)

# -------------------------------------------------------------
# 1. PARSE SRT AND GENERATE FULL-LENGTH ASS SUBTITLES
# -------------------------------------------------------------
def srt_time_to_seconds(time_str):
    time_str = time_str.strip().replace(",", ".")
    h, m, s = time_str.split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)

def format_ass_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hours:01d}:{minutes:02d}:{secs:05.2f}"

def build_full_subtitles():
    with open(SRT_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    blocks = content.strip().split("\n\n")
    events = []

    lime_tag = "{\\c&H0049F3D1&}"
    white_tag = "{\\c&H00FFFFFF&}"

    highlight_keywords = [
        "three in the morning", "Who answers?", "nobody until nine", "talking to someone else",
        "AI receptionist", "forty hours", "one hundred and sixty-eight", "Evenings", "weekends",
        "WhatsApp", "website", "never goes off shift", "Channels", "one single agent",
        "language model", "Ask it", "happily guess", "knowledge base", "R-A-G",
        "retrieval-augmented generation", "looks it up before it speaks", "goal is the lead",
        "owner's inbox", "booked conversations", "checklist", "I don't know",
        "hands off to a human", "captures the lead every time", "ClientFalcon Voice",
        "iAgentice", "subscribe"
    ]

    for block in blocks:
        lines = [line.strip() for line in block.split("\n") if line.strip()]
        if len(lines) >= 3:
            time_match = re.match(r"(\d{2}:\d{2}:\d{2}[,\.]\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}[,\.]\d{3})", lines[1])
            if time_match:
                start_sec = srt_time_to_seconds(time_match.group(1))
                end_sec = srt_time_to_seconds(time_match.group(2))
                text = " ".join(lines[2:])
                
                styled_text = text
                for kw in highlight_keywords:
                    pattern = re.compile(re.escape(kw), re.IGNORECASE)
                    match = pattern.search(styled_text)
                    if match:
                        matched_str = match.group(0)
                        repl_target = f"{lime_tag}{matched_str}{white_tag}"
                        styled_text = styled_text.replace(matched_str, repl_target, 1)
                        break

                t_start = format_ass_time(start_sec)
                t_end = format_ass_time(end_sec)
                events.append(f"Dialogue: 0,{t_start},{t_end},ReelSub,,0,0,0,,{styled_text}")

    ass_content = f"""[Script Info]
Title: iAgentice Full Reel Subtitles
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: ReelSub,Instrument Sans,58,&H00FFFFFF,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,0,0,1,6,3,2,60,60,490,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" + "\n".join(events) + "\n"

    with open(SUBTITLES_ASS, "w", encoding="utf-8") as f:
        f.write(ass_content)
    print(f"✓ Generated {len(events)} full subtitle events in ASS format")

# -------------------------------------------------------------
# 2. CREATE DYNAMIC CHAPTER OVERLAYS
# -------------------------------------------------------------
CHAPTERS = [
    {
        "id": "ch1",
        "start": 0.0,
        "end": 20.5,
        "badge": "LIVE INQUIRY TEST",
        "h1": "WHO ANSWERS YOUR",
        "h2": "CUSTOMERS AT 3 AM?",
        "sub": "AI Receptionist vs. Missed Leads"
    },
    {
        "id": "ch2",
        "start": 20.5,
        "end": 41.2,
        "badge": "THE BUSINESS PROBLEM",
        "h1": "40 HOURS OPEN vs.",
        "h2": "168 HOURS OF MESSAGES",
        "sub": "Customers Don't Wait Until 9 A.M."
    },
    {
        "id": "ch3a",
        "start": 41.2,
        "end": 58.2,
        "badge": "PART 1 · CHANNELS",
        "h1": "CONNECTING ALL YOUR",
        "h2": "CUSTOMER INBOXES",
        "sub": "Web Chat · WhatsApp · Phone"
    },
    {
        "id": "ch3b",
        "start": 58.2,
        "end": 78.0,
        "badge": "PART 2 · THE BRAIN",
        "h1": "WHY RAW LLMs FAIL",
        "h2": "WITHOUT YOUR DATA",
        "sub": "Understanding Text vs. Knowing Your Business"
    },
    {
        "id": "ch3c",
        "start": 78.0,
        "end": 110.8,
        "badge": "PART 3 · KNOWLEDGE (RAG)",
        "h1": "HOW RAG ELIMINATES",
        "h2": "AI HALLUCINATIONS",
        "sub": "Looks Up Your Exact Hours, Prices & Policies"
    },
    {
        "id": "ch3d",
        "start": 110.8,
        "end": 128.8,
        "badge": "PART 4 · AUTOMATED ACTIONS",
        "h1": "TURNING 3 A.M. CHATS",
        "h2": "INTO REAL LEADS",
        "sub": "Name, Needs & Contact Directly to Inbox"
    },
    {
        "id": "ch4",
        "start": 128.8,
        "end": 153.5,
        "badge": "THE 3-POINT CHECKLIST",
        "h1": "WHAT SEPARATES GOOD AI",
        "h2": "FROM ANNOYING BOTS?",
        "sub": "Accurate Data · Human Handoff · Lead Capture"
    },
    {
        "id": "ch5",
        "start": 153.5,
        "end": 186.1,
        "badge": "REAL-TIME VOICE AI",
        "h1": "CLIENTFALCON VOICE",
        "h2": "IN LIVE ACTION",
        "sub": "Trained on Business Data · Deploy Today"
    }
]

def render_chapter_card(ch):
    canvas = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    font_badge = ImageFont.truetype("/root/.fonts/brandtest/InstrumentSans-600.ttf", 26)
    font_h1 = ImageFont.truetype("/root/.fonts/brandtest/InstrumentSans.ttf", 52)
    font_sub = ImageFont.truetype("/root/.fonts/brandtest/InstrumentSans-600.ttf", 28)
    font_footer = ImageFont.truetype("/root/.fonts/brandtest/InstrumentSans-600.ttf", 26)

    # Top Header Card Background
    card_box = [60, 120, 1020, 440]
    draw.rounded_rectangle(card_box, radius=24, fill=(13, 16, 24, 235), outline=(255, 255, 255, 30), width=1)

    # Indicator Pill Badge
    pill_text = ch["badge"]
    tb = font_badge.getbbox(pill_text)
    pw = tb[2] - tb[0] + 64
    ph = tb[3] - tb[1] + 22
    pill_x = 540 - pw // 2
    pill_y = 150
    draw.rounded_rectangle([pill_x, pill_y, pill_x + pw, pill_y + ph], radius=16, fill=(20, 26, 38, 255), outline=(209, 243, 73, 110), width=1)
    
    # Glowing dot
    dot_x = pill_x + 22
    dot_y = pill_y + ph // 2
    draw.ellipse([dot_x - 5, dot_y - 5, dot_x + 5, dot_y + 5], fill=(209, 243, 73, 255))
    draw.text((dot_x + 16, pill_y + 9), pill_text, font=font_badge, fill=(209, 243, 73, 255))

    # Headline 1 & 2
    tb1 = font_h1.getbbox(ch["h1"])
    tb2 = font_h1.getbbox(ch["h2"])
    draw.text((540 - (tb1[2] - tb1[0]) // 2, 235), ch["h1"], font=font_h1, fill=(255, 255, 255, 255))
    draw.text((540 - (tb2[2] - tb2[0]) // 2, 305), ch["h2"], font=font_h1, fill=(209, 243, 73, 255))

    # Subtitle
    tbs = font_sub.getbbox(ch["sub"])
    draw.text((540 - (tbs[2] - tbs[0]) // 2, 385), ch["sub"], font=font_sub, fill=(160, 174, 192, 255))

    # Center Bezel Frame
    frame_box = [34, 494, 1046, 1070]
    draw.rounded_rectangle(frame_box, radius=20, fill=(0, 0, 0, 0), outline=(255, 255, 255, 45), width=2)
    draw.rounded_rectangle([37, 497, 1043, 1067], radius=18, fill=(0, 0, 0, 0), outline=(209, 243, 73, 35), width=1)

    # Footer Badge
    footer_text = "iAgentice · ClientFalcon Voice"
    tbf = font_footer.getbbox(footer_text)
    wf = tbf[2] - tbf[0] + 48
    hf = tbf[3] - tbf[1] + 20
    fx = 540 - wf // 2
    fy = 1710
    draw.rounded_rectangle([fx, fy, fx + wf, fy + hf], radius=18, fill=(12, 15, 22, 225), outline=(255, 255, 255, 25), width=1)
    draw.text((fx + 24, fy + 8), footer_text, font=font_footer, fill=(203, 213, 225, 255))

    path = os.path.join(CHAPTERS_DIR, f"{ch['id']}.png")
    canvas.save(path, "PNG")
    return path

def build_all_chapter_cards():
    for ch in CHAPTERS:
        render_chapter_card(ch)
    print(f"✓ Rendered {len(CHAPTERS)} dynamic chapter card overlays")

# -------------------------------------------------------------
# 3. RENDER FULL 3:06 REEL WITH FFMPEG (Taskset 2-core cap)
# -------------------------------------------------------------
def render_full_reel():
    print("Composing and Rendering full 3:06 Reel (186s)...")
    
    # Build filter complex for dynamic chapter overlays
    # Input 0: SOURCE_VIDEO (0 to 186.1s)
    # Inputs 1 to 8: CHAPTER overlays
    inputs = ["taskset", "-c", "0,1", "ffmpeg", "-y", "-i", SOURCE_VIDEO]
    for ch in CHAPTERS:
        png_path = os.path.join(CHAPTERS_DIR, f"{ch['id']}.png")
        inputs += ["-loop", "1", "-i", png_path]

    filter_steps = [
        # 1. Background: Blurred video scaled to full vertical height
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=28:5,eq=brightness=-0.18:contrast=1.05[bg]",
        # 2. Foreground: Center video (1000x562.5), overlaid on blurred bg at (40, 501)
        "[0:v]scale=1000:562.5[fg]",
        "[bg][fg]overlay=40:501[base]"
    ]

    # Overlay chapter cards conditionally on timestamp
    curr_node = "base"
    for idx, ch in enumerate(CHAPTERS):
        input_idx = idx + 1
        next_node = f"ov_{idx}"
        # Enable overlay during [ch['start'], ch['end']]
        filter_steps.append(
            f"[{curr_node}][{input_idx}:v]overlay=0:0:enable='between(t,{ch['start']},{ch['end']})'[{next_node}]"
        )
        curr_node = next_node

    # Burn in ASS Subtitles on top of everything
    filter_steps.append(f"[{curr_node}]ass={SUBTITLES_ASS},setsar=1,fps=30[v_out]")

    cmd = inputs + [
        "-filter_complex", ";".join(filter_steps),
        "-map", "[v_out]",
        "-map", "0:a",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "19",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        "-t", "186.1",
        FINAL_OUTPUT
    ]

    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print("FFmpeg error:", res.stderr)
        raise RuntimeError("Full Reel FFmpeg render failed")
    print(f"✓ Successfully rendered full 3:06 Reel to: {FINAL_OUTPUT}")

if __name__ == "__main__":
    build_full_subtitles()
    build_all_chapter_cards()
    render_full_reel()
