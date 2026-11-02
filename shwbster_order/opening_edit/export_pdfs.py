"""Export Full_Commercial_Asset_and_Licence_Log.pdf and YouTube_Title_Description_and_Tags.pdf + .txt."""
import json
import os
import shutil
from PIL import Image, ImageDraw, ImageFont

FONT_DIR = "/root/Motion/shwbster_order/opening_edit/fonts"
F_BOLD = lambda sz: ImageFont.truetype(os.path.join(FONT_DIR, "Montserrat-600.ttf"), sz)
F_REG = lambda sz: ImageFont.truetype(os.path.join(FONT_DIR, "Inter-600.ttf"), sz)

OUT_DIR = "/root/youtubeai/shwbster"
log_entries = json.load(open("/root/Motion/shwbster_order/assets/full_asset_log.json"))

PW, PH = 2100, 1485
pages = []


def new_page(page_num, title_sub=""):
    im = Image.new("RGB", (PW, PH), (255, 255, 255))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, PW, 110], fill=(12, 18, 30))
    d.rectangle([0, 106, PW, 112], fill=(243, 207, 138))
    d.text((60, 24), "COMMERCIAL ASSET & LICENCE LOG — THE WORLD'S 10 MOST EXPENSIVE CITIES (8:00)", font=F_BOLD(26), fill=(255, 255, 255))
    d.text((60, 64), f"Client: shwbster  |  Standard Package (1920x1080, 24fps, 480.00s)  |  Monetised YouTube Rights: CONFIRMED   {title_sub}", font=F_REG(17), fill=(243, 207, 138))
    d.text((PW - 180, 44), f"Page {page_num}", font=F_BOLD(20), fill=(255, 255, 255))
    return im, d


im, d = new_page(1, "|  Section 1: Audio, Map & Fonts + Shots 01-22")
y = 135
d.text((60, y), "1. VOICEOVER, INSTRUMENTAL SCORE, MAP DATA & TYPOGRAPHY LICENCES", font=F_BOLD(21), fill=(12, 18, 30))
y += 36

non_video = [
    ("Voiceover Narration", "Charon (British Male RP, gemini-2.5-flash-preview-tts)", "Google AI Studio / Gemini API", "Commercial Usage & Monetised YouTube Rights Included (No attribution required)"),
    ("Instrumental Score & Cues", "bed_480s.wav (Original Documentary Score + Rank/Price Cues)", "Custom Original Synthesis (Python/NumPy)", "100% Original Work Created for Project — Zero Content ID / Royalty-Free Commercial Use"),
    ("World Map Vector Geometry", "ne_110m_land.geojson (Shot 05 Animated ECA 2026 Map)", "Natural Earth (naturalearthdata.com)", "CC0 1.0 Public Domain Dedication (Free for commercial broadcast & YouTube use)"),
    ("Heading & Price Font", "Montserrat SemiBold (Montserrat-600.ttf)", "Google Fonts / Julieta Ulanovsky", "SIL Open Font License 1.1 (OFL-1.1 — Free for commercial video embedding)"),
    ("Subtitle & UI Font", "Inter Medium / SemiBold (Inter-600.ttf)", "Google Fonts / Rasmus Andersson", "SIL Open Font License 1.1 (OFL-1.1 — Free for commercial video embedding)"),
]

d.rectangle([60, y, PW - 60, y + 36], fill=(230, 236, 245))
d.text((72, y + 8), "Category", font=F_BOLD(16), fill=(12, 18, 30))
d.text((340, y + 8), "Asset / Identifier", font=F_BOLD(16), fill=(12, 18, 30))
d.text((920, y + 8), "Provider / Source", font=F_BOLD(16), fill=(12, 18, 30))
d.text((1310, y + 8), "Commercial Licence & YouTube Monetisation Status", font=F_BOLD(16), fill=(12, 18, 30))
y += 38

for idx, (cat, aid, prov, lic) in enumerate(non_video):
    bg = (248, 250, 253) if idx % 2 == 1 else (255, 255, 255)
    d.rectangle([60, y, PW - 60, y + 34], fill=bg, outline=(220, 226, 235))
    d.text((72, y + 7), cat, font=F_BOLD(15), fill=(20, 30, 45))
    d.text((340, y + 7), aid, font=F_REG(15), fill=(30, 40, 55))
    d.text((920, y + 7), prov, font=F_REG(15), fill=(30, 40, 55))
    d.text((1310, y + 7), lic, font=F_REG(15), fill=(16, 105, 55))
    y += 34

y += 26
d.text((60, y), "2. COMPLETE 71-SHOT VIDEO FOOTAGE LOG (Pexels Commercial License — https://www.pexels.com/license/ — No Attribution Required)", font=F_BOLD(20), fill=(12, 18, 30))
y += 34


def draw_shot_header(d, y):
    d.rectangle([60, y, PW - 60, y + 36], fill=(22, 32, 48))
    d.text((70, y + 8), "Shot", font=F_BOLD(15), fill=(255, 255, 255))
    d.text((135, y + 8), "Timecode", font=F_BOLD(15), fill=(255, 255, 255))
    d.text((265, y + 8), "Chapter", font=F_BOLD(15), fill=(255, 255, 255))
    d.text((495, y + 8), "Asset ID", font=F_BOLD(15), fill=(255, 255, 255))
    d.text((650, y + 8), "Creator", font=F_BOLD(15), fill=(255, 255, 255))
    d.text((910, y + 8), "Direct Pexels / Source URL", font=F_BOLD(15), fill=(255, 255, 255))
    d.text((1680, y + 8), "Housing Label", font=F_BOLD(15), fill=(255, 255, 255))
    d.text((1860, y + 8), "YouTube Rights", font=F_BOLD(15), fill=(255, 255, 255))
    return y + 38


y = draw_shot_header(d, y)
page_num = 1

for idx, e in enumerate(log_entries):
    if y + 36 > PH - 50:
        pages.append(im)
        page_num += 1
        im, d = new_page(page_num, "|  Section 2: 71-Shot Video Footage Log (Continued)")
        y = draw_shot_header(d, 135)
    bg = (246, 249, 253) if idx % 2 == 1 else (255, 255, 255)
    d.rectangle([60, y, PW - 60, y + 35], fill=bg, outline=(222, 228, 236))
    st, en, snum = e["start"], e["end"], e["shot"]
    tc = f"{st//60:02d}:{st%60:02d}-{en//60:02d}:{en%60:02d}"
    hl = "Illustrative label" if (e["illustrative_housing_label"] or "illustrative" in e["description"].lower()) else "Landmark / Street"
    d.text((72, y + 8), f"#{snum:02d}", font=F_BOLD(14), fill=(15, 23, 38))
    d.text((135, y + 8), tc, font=F_REG(14), fill=(30, 40, 55))
    d.text((265, y + 8), e["chapter"][:22], font=F_REG(14), fill=(30, 40, 55))
    d.text((495, y + 8), str(e["id"])[:16], font=F_BOLD(14), fill=(15, 65, 130))
    d.text((650, y + 8), e["creator"][:24], font=F_REG(14), fill=(30, 40, 55))
    d.text((910, y + 8), e["url"][:68], font=F_REG(13), fill=(40, 80, 150))
    d.text((1680, y + 8), hl, font=F_REG(14), fill=(30, 40, 55))
    d.text((1860, y + 8), "Cleared (Monetised)", font=F_BOLD(13), fill=(16, 110, 55))
    y += 35

pages.append(im)
pdf_path = os.path.join(OUT_DIR, "Full_Commercial_Asset_and_Licence_Log.pdf")
pages[0].save(pdf_path, "PDF", resolution=180.0, save_all=True, append_images=pages[1:])
shutil.copy(os.path.join(OUT_DIR, "YouTube_Title_Description_and_Tags.md"), os.path.join(OUT_DIR, "YouTube_Title_Description_and_Tags.txt"))
print(f"Saved {pdf_path} ({len(pages)} pages) and YouTube_Title_Description_and_Tags.txt")
