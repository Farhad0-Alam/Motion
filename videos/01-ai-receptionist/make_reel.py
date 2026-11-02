#!/usr/bin/env python3
"""Generates a broadcast-quality 9:16 vertical Reel (1080x1920) from ep01-v2-4k.mp4.

Architecture:
1. Dynamic animated blurred background reflecting the original video colors
2. Sleek framed center stage for the 16:9 animation
3. Executive top hook card (3:00 AM Customer Test)
4. Premium bold subtitles positioned in the mobile safe zone
5. Seamless audio trim with smooth fade-out
"""

import json
import os
import subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = "/root/Motion/videos/01-ai-receptionist"
SOURCE_VIDEO = os.path.join(HERE, "renders/ep01-v2-4k.mp4")
TIMELINE_JSON = os.path.join(HERE, "timeline.json")
OUT_DIR = os.path.join(HERE, "renders/reels")
OVERLAY_PNG = os.path.join(OUT_DIR, "reel_overlay.png")
OUTRO_PNG = os.path.join(OUT_DIR, "reel_outro.png")
SUBTITLES_ASS = os.path.join(OUT_DIR, "reel_subs.ass")
FINAL_OUTPUT = os.path.join(OUT_DIR, "reel-01-who-answers-3am.mp4")

os.makedirs(OUT_DIR, exist_ok=True)

# -------------------------------------------------------------
# 1. CREATE SUBTITLES (ASS)
# -------------------------------------------------------------
def format_ass_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hours:01d}:{minutes:02d}:{secs:05.2f}"

def build_subtitles():
    with open(TIMELINE_JSON, "r") as f:
        data = json.load(f)

    words = [w for w in data["words"] if w["sc"] in ("s1", "s2")]
    
    # Custom high-impact chunks for the 41-second reel
    chunks = [
        # (text, start, end, highlight_words)
        ("It's 3 in the morning,", 0.65, 1.85, ["3 in the morning"]),
        ("and a customer just messaged your business.", 1.85, 4.30, ["messaged"]),
        ("Who answers?", 4.45, 5.50, ["Who answers?"]),
        ("If the answer is \"nobody until nine,\"", 5.75, 7.95, ["nobody until nine"]),
        ("that customer is already talking to someone else.", 8.10, 11.60, ["already talking to someone else"]),
        ("In the next few minutes,", 12.00, 13.00, []),
        ("here's exactly how an AI receptionist answers,", 13.00, 17.00, ["AI receptionist"]),
        ("and what separates a good one from an annoying one.", 17.05, 20.40, ["good one", "annoying one"]),
        ("Most businesses are open 40 hours a week.", 21.00, 24.50, ["40 hours"]),
        ("Customers message all 168.", 24.55, 27.50, ["all 168"]),
        ("Evenings, weekends, other time zones.", 27.60, 31.00, ["Evenings,", "weekends,"]),
        ("And every channel is different:", 31.00, 32.90, []),
        ("your website, WhatsApp, the phone.", 32.90, 35.80, ["website,", "WhatsApp,", "phone."]),
        ("An AI receptionist sits on all of them at once,", 35.80, 38.90, ["all of them at once,"]),
        ("and never goes off shift.", 38.95, 40.80, ["never goes off shift."]),
    ]

    ass_content = """[Script Info]
Title: iAgentice Reel Subtitles
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
"""
    # ASS colors: &H00BBGGRR -> Lime (#D1F349) is &H0049F3D1&
    lime_tag = "{\\c&H0049F3D1&}"
    white_tag = "{\\c&H00FFFFFF&}"

    for text, start, end, hl_list in chunks:
        styled_text = text
        for hl in hl_list:
            if hl in styled_text:
                styled_text = styled_text.replace(hl, f"{lime_tag}{hl}{white_tag}")
        
        t_start = format_ass_time(start)
        t_end = format_ass_time(end)
        ass_content += f"Dialogue: 0,{t_start},{t_end},ReelSub,,0,0,0,,{styled_text}\n"

    with open(SUBTITLES_ASS, "w") as f:
        f.write(ass_content)
    print("✓ Created subtitles ASS file")

# -------------------------------------------------------------
# 2. CREATE OVERLAY PNG (Top Header & Center Bezel)
# -------------------------------------------------------------
def build_overlay():
    canvas = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    font_badge = ImageFont.truetype("/root/.fonts/brandtest/InstrumentSans-600.ttf", 26)
    font_h1 = ImageFont.truetype("/root/.fonts/brandtest/InstrumentSans.ttf", 54)
    font_sub = ImageFont.truetype("/root/.fonts/brandtest/InstrumentSans-600.ttf", 28)
    font_footer = ImageFont.truetype("/root/.fonts/brandtest/InstrumentSans-600.ttf", 26)

    # --- TOP CARD BACKGROUND (Y: 120 to 440) ---
    card_box = [60, 120, 1020, 440]
    draw.rounded_rectangle(card_box, radius=24, fill=(13, 16, 24, 230), outline=(255, 255, 255, 30), width=1)

    # Top Pill Badge with sleek green indicator dot
    pill_text = "LIVE INQUIRY TEST"
    tb = font_badge.getbbox(pill_text)
    text_w = tb[2] - tb[0]
    text_h = tb[3] - tb[1]
    pw = text_w + 64
    ph = text_h + 22
    pill_x = 540 - pw // 2
    pill_y = 150
    draw.rounded_rectangle([pill_x, pill_y, pill_x + pw, pill_y + ph], radius=16, fill=(20, 26, 38, 255), outline=(209, 243, 73, 110), width=1)
    # Draw green dot
    dot_x = pill_x + 22
    dot_y = pill_y + ph // 2
    draw.ellipse([dot_x - 5, dot_y - 5, dot_x + 5, dot_y + 5], fill=(209, 243, 73, 255))
    draw.text((dot_x + 16, pill_y + 9), pill_text, font=font_badge, fill=(209, 243, 73, 255))

    # Main Headline
    line1 = "WHO ANSWERS YOUR"
    line2 = "CUSTOMERS AT 3 AM?"
    
    tb1 = font_h1.getbbox(line1)
    tb2 = font_h1.getbbox(line2)
    w1 = tb1[2] - tb1[0]
    w2 = tb2[2] - tb2[0]

    draw.text((540 - w1 // 2, 235), line1, font=font_h1, fill=(255, 255, 255, 255))
    draw.text((540 - w2 // 2, 305), line2, font=font_h1, fill=(209, 243, 73, 255))

    sub_text = "AI Receptionist vs. Missed Leads"
    tbs = font_sub.getbbox(sub_text)
    ws = tbs[2] - tbs[0]
    draw.text((540 - ws // 2, 385), sub_text, font=font_sub, fill=(160, 174, 192, 255))

    # --- CENTER VIDEO BEZEL (X: 30 to 1050, Y: 490 to 1080) ---
    # The video itself is 1000x562.5 placed at (40, 500). Bezel surrounds it:
    frame_box = [34, 494, 1046, 1070]
    draw.rounded_rectangle(frame_box, radius=20, fill=(0, 0, 0, 0), outline=(255, 255, 255, 45), width=2)
    # Inner subtle glow edge
    draw.rounded_rectangle([37, 497, 1043, 1067], radius=18, fill=(0, 0, 0, 0), outline=(209, 243, 73, 35), width=1)

    # --- FOOTER BADGE (Y: 1720) ---
    footer_text = "iAgentice · ClientFalcon Voice"
    tbf = font_footer.getbbox(footer_text)
    wf = tbf[2] - tbf[0] + 48
    hf = tbf[3] - tbf[1] + 20
    fx = 540 - wf // 2
    fy = 1710
    draw.rounded_rectangle([fx, fy, fx + wf, fy + hf], radius=18, fill=(12, 15, 22, 220), outline=(255, 255, 255, 25), width=1)
    draw.text((fx + 24, fy + 8), footer_text, font=font_footer, fill=(203, 213, 225, 255))

    canvas.save(OVERLAY_PNG, "PNG")
    print("✓ Created overlay PNG")

# -------------------------------------------------------------
# 3. CREATE OUTRO CARD (at 40.5s - 43.5s)
# -------------------------------------------------------------
def build_outro():
    canvas = Image.new("RGBA", (1080, 1920), (10, 12, 18, 255))
    draw = ImageDraw.Draw(canvas)

    font_badge = ImageFont.truetype("/root/.fonts/brandtest/InstrumentSans-600.ttf", 30)
    font_h1 = ImageFont.truetype("/root/.fonts/brandtest/InstrumentSans.ttf", 64)
    font_sub = ImageFont.truetype("/root/.fonts/brandtest/InstrumentSans.ttf", 36)
    font_link = ImageFont.truetype("/root/.fonts/brandtest/InstrumentSans-600.ttf", 38)

    # Center card
    card_box = [80, 480, 1000, 1440]
    draw.rounded_rectangle(card_box, radius=32, fill=(16, 20, 30, 245), outline=(209, 243, 73, 90), width=2)

    # Badge
    badge = "24/7 AI RECEPTIONIST"
    tbb = font_badge.getbbox(badge)
    bw = tbb[2] - tbb[0] + 50
    bh = tbb[3] - tbb[1] + 24
    bx = 540 - bw // 2
    by = 560
    draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=18, fill=(26, 33, 48, 255), outline=(209, 243, 73, 150), width=1)
    draw.text((bx + 25, by + 10), badge, font=font_badge, fill=(209, 243, 73, 255))

    # Headline
    l1 = "Never Miss Another"
    l2 = "Customer Lead."
    tb1 = font_h1.getbbox(l1)
    tb2 = font_h1.getbbox(l2)
    draw.text((540 - (tb1[2]-tb1[0])//2, 670), l1, font=font_h1, fill=(255, 255, 255, 255))
    draw.text((540 - (tb2[2]-tb2[0])//2, 755), l2, font=font_h1, fill=(209, 243, 73, 255))

    # Description
    desc1 = "Web Chat · WhatsApp · Voice AI"
    desc2 = "Trained on your business knowledge."
    tbd1 = font_sub.getbbox(desc1)
    tbd2 = font_sub.getbbox(desc2)
    draw.text((540 - (tbd1[2]-tbd1[0])//2, 890), desc1, font=font_sub, fill=(203, 213, 225, 255))
    draw.text((540 - (tbd2[2]-tbd2[0])//2, 945), desc2, font=font_sub, fill=(148, 163, 184, 255))

    # Divider
    draw.line([240, 1060, 840, 1060], fill=(255, 255, 255, 30), width=1)

    # CTA Pill
    link1 = "Deploy at iAgentice.com"
    tbl = font_link.getbbox(link1)
    lw = tbl[2] - tbl[0] + 60
    lh = tbl[3] - tbl[1] + 28
    lx = 540 - lw // 2
    ly = 1130
    draw.rounded_rectangle([lx, ly, lx + lw, ly + lh], radius=22, fill=(209, 243, 73, 255))
    draw.text((lx + 30, ly + 12), link1, font=font_link, fill=(10, 12, 18, 255))

    link2 = "ClientFalcon Voice Assistant"
    tbl2 = font_sub.getbbox(link2)
    draw.text((540 - (tbl2[2]-tbl2[0])//2, 1240), link2, font=font_sub, fill=(148, 163, 184, 255))

    canvas.save(OUTRO_PNG, "PNG")
    print("✓ Created outro PNG")

# -------------------------------------------------------------
# 4. RENDER REEL WITH FFMPEG (Restricted to 2 cores via taskset)
# -------------------------------------------------------------
def render_reel():
    print("Rendering Reel with FFmpeg (taskset -c 0,1)...")
    
    # We cut exactly 0.0s to 41.2s from source video, followed by 2.8s outro (total 44.0s).
    # Audio smoothly fades out over the last 2 seconds.
    cmd = [
        "taskset", "-c", "0,1",
        "ffmpeg", "-y",
        "-ss", "0.0", "-t", "41.2", "-i", SOURCE_VIDEO,
        "-loop", "1", "-t", "2.8", "-i", OUTRO_PNG,
        "-i", OVERLAY_PNG,
        "-filter_complex",
        # 1. Background: Blurred video scaled to full vertical height
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=28:5,eq=brightness=-0.18:contrast=1.05[bg];"
        # 2. Foreground: Crisp center video (1000x562.5), overlaid on blurred bg at (40, 501)
        "[0:v]scale=1000:562.5[fg];"
        "[bg][fg]overlay=40:501[comp];"
        # 3. Add Top Header & Frame Bezel overlay
        "[comp][2:v]overlay=0:0[with_overlay];"
        # 4. Burn in dynamic ASS subtitles
        f"[with_overlay]ass={SUBTITLES_ASS},setsar=1,fps=30[main_v];"
        # 5. Outro card fade in
        "[1:v]format=yuv420p,fade=t=in:st=0:d=0.5,setsar=1,fps=30[outro_v];"
        # 6. Concatenate main video + outro
        "[main_v][outro_v]concat=n=2:v=1:a=0[v_out];"
        # 7. Audio: trim + fade out over last 2.5s (starts fading at 39.5s to 42.0s)
        "[0:a]afade=t=out:st=39.5:d=2.5,apad=pad_dur=2.8[a_out]",
        "-map", "[v_out]",
        "-map", "[a_out]",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        "-t", "44.0",
        FINAL_OUTPUT
    ]
    
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print("FFmpeg error:", res.stderr)
        raise RuntimeError("FFmpeg render failed")
    print(f"✓ Successfully rendered Reel to: {FINAL_OUTPUT}")

if __name__ == "__main__":
    build_subtitles()
    build_overlay()
    build_outro()
    render_reel()
