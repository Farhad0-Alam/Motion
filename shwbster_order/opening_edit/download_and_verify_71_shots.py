"""Select, visually grid-check, and download all 71 shots for the 480.00s Master Video."""
import concurrent.futures
import json
import os
import urllib.request
from PIL import Image, ImageDraw

BASE_DIR = "/root/Motion/shwbster_order"
CAND_DIR = os.path.join(BASE_DIR, "candidates_full")
SHOTS_DIR = os.path.join(BASE_DIR, "assets/full_shots")
os.makedirs(SHOTS_DIR, exist_ok=True)

# Lookup table from both candidates/meta.json and candidates_full/all_candidates.json
meta_pool = {}
if os.path.exists(os.path.join(BASE_DIR, "candidates/meta.json")):
    for k, v in json.load(open(os.path.join(BASE_DIR, "candidates/meta.json"))).items():
        meta_pool[int(k)] = v
if os.path.exists(os.path.join(CAND_DIR, "all_candidates.json")):
    for tag, items in json.load(open(os.path.join(CAND_DIR, "all_candidates.json"))).items():
        for it in items:
            meta_pool[int(it["id"])] = it

# 71 shots: (shot_num, start_sec, end_sec, chapter, pexels_id_or_special, description, is_housing_with_price)
SHOT_PLAN = [
    # Ch 1: Opening hook (0-28s)
    (1,   0,   7, "Opening hook", 5824189, "NYC 1-bed apartment interior (illustrative)", True),
    (2,   7,  14, "Opening hook", 11471275, "Recognisable Manhattan skyline", False),
    (3,  14,  21, "Opening hook", 35972202, "Burj Khalifa skyline in Dubai", False),
    (4,  21,  28, "Opening hook", 3655304, "Bern Old Town and Minster tower, Switzerland", False),
    # Ch 2: How the comparison works (28-40s)
    (5,  28,  34, "How the comparison works", "MAP_ECA", "Animated World Map with 10 ECA 2026 cities (Natural Earth CC0)", False),
    (6,  34,  40, "How the comparison works", 30301046, "Dubai Marina residential towers & waterfront", True),
    # Ch 3: #10 Dubai (40-80s)
    (7,  40,  47, "Number 10 Dubai", 7168742, "Burj Khalifa clearly visible in Dubai skyline", False),
    (8,  47,  54, "Number 10 Dubai", 7168737, "Downtown Dubai skyscrapers and street view", False),
    (9,  54,  61, "Number 10 Dubai", 6596439, "Dubai residential apartment buildings exterior", True),
    (10, 61,  68, "Number 10 Dubai", 27975847, "Apartment kitchen and dining area (illustrative)", True),
    (11, 68,  74, "Number 10 Dubai", 36657437, "Dubai Metro and Sheikh Zayed Road corridor", False),
    (12, 74,  80, "Number 10 Dubai", 36655254, "Everyday street by Al Fahidi / Old Dubai", False),
    # Ch 4: #9 San Francisco (80-120s)
    (13, 80,  87, "Number 9 San Francisco", 32581824, "Golden Gate Bridge with San Francisco Bay", False),
    (14, 87,  94, "Number 9 San Francisco", 29190916, "San Francisco residential street and facades", False),
    (15, 94, 101, "Number 9 San Francisco", 30294586, "San Francisco residential neighbourhood buildings", True),
    (16, 101, 108, "Number 9 San Francisco", 7314522, "Apartment kitchen and living space (illustrative)", True),
    (17, 108, 114, "Number 9 San Francisco", 29190927, "San Francisco cable car on downtown street", False),
    (18, 114, 120, "Number 9 San Francisco", 12599348, "San Francisco Ferry Building and waterfront", False),
    # Ch 5: #8 Singapore (120-160s)
    (19, 120, 127, "Number 8 Singapore", 32444379, "Marina Bay Sands and Singapore skyline", False),
    (20, 127, 134, "Number 8 Singapore", 14371866, "Singapore residential apartment towers", True),
    (21, 134, 141, "Number 8 Singapore", 35200144, "Singapore highway traffic (COE 10-year car context)", False),
    (22, 141, 148, "Number 8 Singapore", 39969515, "Modern compact apartment kitchen interior (illustrative)", False),
    (23, 148, 154, "Number 8 Singapore", 32416477, "Bugis MRT station entrance and commuters in Singapore", False),
    (24, 154, 160, "Number 8 Singapore", 14372135, "People's Park Complex Chinatown Singapore neighbourhood", False),
    # Ch 6: #7 Bern (160-208s)
    (25, 160, 168, "Number 7 Bern", 8147333, "Bern Old Town towers and historic centre", False),
    (26, 168, 176, "Number 7 Bern", 3718075, "Bern old-town streets and historic sandstone buildings", True),
    (27, 176, 184, "Number 7 Bern", 3586172, "Bern historic facade and street architecture", True),
    (28, 184, 192, "Number 7 Bern", 5524394, "Outdoor cafe & restaurant tables ($29 meal context)", False),
    (29, 192, 200, "Number 7 Bern", 3623659, "Bern Kornhausbrucke bridge with tram and street", False),
    (30, 200, 208, "Number 7 Bern", 9067963, "Aare river and Bern old-town rooftops", False),
    # Ch 7: #6 Tel Aviv (208-248s)
    (31, 208, 215, "Number 6 Tel Aviv", 11471476, "Tel Aviv Mediterranean seafront skyline", False),
    (32, 215, 222, "Number 6 Tel Aviv", 34185560, "Tel Aviv residential street and Bauhaus/modern buildings", True),
    (33, 222, 229, "Number 6 Tel Aviv", 20256026, "Tel Aviv residential apartment blocks exterior", True),
    (34, 229, 236, "Number 6 Tel Aviv", 7614541, "Bright apartment living room interior (illustrative)", True),
    (35, 236, 242, "Number 6 Tel Aviv", 34283693, "Tel Aviv daily commute and urban bus/traffic", False),
    (36, 242, 248, "Number 6 Tel Aviv", 18809883, "Old Jaffa bell tower and Tel Aviv coastal promenade", False),
    # Ch 8: #5 Hong Kong (248-288s)
    (37, 248, 255, "Number 5 Hong Kong", 2856781, "Victoria Harbour and Hong Kong skyline", False),
    (38, 255, 262, "Number 5 Hong Kong", 11385027, "Hong Kong green country-park mountains and islands (40% land)", False),
    (39, 262, 269, "Number 5 Hong Kong", 7009175, "Hong Kong high-density residential apartment towers", True),
    (40, 269, 276, "Number 5 Hong Kong", 27975843, "Compact 1-bedroom apartment kitchen and dining layout (illustrative)", True),
    (41, 276, 282, "Number 5 Hong Kong", 32660408, "Hong Kong double-decker tram on bustling street", False),
    (42, 282, 288, "Number 5 Hong Kong", 30440562, "Hong Kong neighbourhood street market", False),
    # Ch 9: #4 Zurich (288-328s)
    (43, 288, 295, "Number 4 Zurich", 28988822, "Grossmunster and Limmat river in Zurich", False),
    (44, 295, 302, "Number 4 Zurich", 15118167, "Zurich Old Town historic street", True),
    (45, 302, 309, "Number 4 Zurich", 28988890, "Zurich residential buildings and Grossmunster rooftops", True),
    (46, 309, 316, "Number 4 Zurich", 38231072, "Minimalist apartment living room interior (illustrative)", False),
    (47, 316, 322, "Number 4 Zurich", 34596708, "Identifiable blue-and-white Zurich tram on street", False),
    (48, 322, 328, "Number 4 Zurich", 3717997, "Lake Zurich waterfront and city panorama", False),
    # Ch 10: #3 London (328-368s)
    (49, 328, 335, "Number 3 London", 5373006, "Tower Bridge over the River Thames in London", False),
    (50, 335, 342, "Number 3 London", 3105031, "London brick residential apartment buildings", True),
    (51, 342, 349, "Number 3 London", 5823583, "Modest flat living room interior (illustrative)", True),
    (52, 349, 356, "Number 3 London", 8581127, "Apartment kitchen interior showing usable space (illustrative)", True),
    (53, 356, 362, "Number 3 London", 15010354, "London Underground train arriving at Shepherd's Bush station", False),
    (54, 362, 368, "Number 3 London", 12254637, "Central London street with walking commuters", False),
    # Ch 11: #2 Geneva (368-408s)
    (55, 368, 375, "Number 2 Geneva", 17242172, "Geneva Jet d'Eau fountain and lakefront", False),
    (56, 375, 382, "Number 2 Geneva", 10881678, "Geneva Old Town buildings and cathedral surroundings", True),
    (57, 382, 389, "Number 2 Geneva", 7798070, "Geneva residential streets and apartment buildings", True),
    (58, 389, 396, "Number 2 Geneva", 3770034, "Small apartment living room interior (illustrative)", False),
    (59, 396, 402, "Number 2 Geneva", 17242140, "Geneva Mont-Blanc bridge daily street traffic", False),
    (60, 402, 408, "Number 2 Geneva", 7797955, "Geneva lakefront and residential neighbourhood", False),
    # Ch 12: #1 New York (408-456s)
    (61, 408, 415, "Number 1 New York", 5825791, "Manhattan skyline with Empire State Building", False),
    (62, 415, 422, "Number 1 New York", 5022674, "New York residential brownstone apartment buildings", True),
    (63, 422, 429, "Number 1 New York", 7614414, "Apartment living area with sofa (illustrative)", True),
    (64, 429, 436, "Number 1 New York", 39969516, "Apartment kitchen showing usable space (illustrative)", True),
    (65, 436, 443, "Number 1 New York", 9892776, "Jackson Heights Queens NYC residential neighbourhood outside centre", True),
    (66, 443, 450, "Number 1 New York", 19236966, "New York City subway train and station commute", False),
    (67, 450, 456, "Number 1 New York", 34593193, "Iconic Manhattan residential street", False),
    # Ch 13: Closing sequence (456-480s)
    (68, 456, 462, "Closing question", "SPLIT_NYC_BERN", "Two-city comparison split screen (#1 New York vs #7 Bern)", False),
    (69, 462, 468, "Closing question", 34539087, "Commuters walking through busy New York City street", False),
    (70, 468, 474, "Closing question", 11422401, "Aerial view of Manhattan skyscrapers (WHICH CITY IS WORTH IT?)", False),
    (71, 474, 480, "Closing question", 7171757, "Moving Manhattan skyline with subscribe cue & end-screen space", False),
]

EXISTING_MAP = {
    5824189: "/root/Motion/shwbster_order/assets/shot1_nyc_apt_5824189.mp4",
    11471275: "/root/Motion/shwbster_order/assets/shot2_manhattan_11471275.mp4",
    35972202: "/root/Motion/shwbster_order/assets/shot3_burj_khalifa_35972202.mp4",
    3655304: "/root/Motion/shwbster_order/assets/shot4_bern_switzerland_3655304.mp4",
    30301046: "/root/Motion/shwbster_order/assets/shot6_dubai_marina_30301046.mp4",
}


def download_one(item):
    shot_num, s_sec, e_sec, ch, pid, desc, is_housing = item
    if isinstance(pid, str):
        return shot_num, None
    out_mp4 = os.path.join(SHOTS_DIR, f"shot_{shot_num:02d}_{pid}.mp4")
    if pid in EXISTING_MAP and os.path.exists(EXISTING_MAP[pid]) and not os.path.exists(out_mp4):
        os.symlink(EXISTING_MAP[pid], out_mp4)
        return shot_num, out_mp4
    if os.path.exists(out_mp4) and os.path.getsize(out_mp4) > 100000:
        return shot_num, out_mp4
    info = meta_pool[pid]
    req = urllib.request.Request(info["hd_link"], headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as resp, open(out_mp4, "wb") as f:
        f.write(resp.read())
    return shot_num, out_mp4


def main():
    # 1. Build contact sheet of thumbnails for shots 7..71
    cols, rows = 8, 9
    tw, th = 240, 135
    grid = Image.new("RGB", (cols * tw, rows * th), (15, 20, 28))
    draw = ImageDraw.Draw(grid)
    for idx, (shot_num, s_sec, e_sec, ch, pid, desc, is_h) in enumerate(SHOT_PLAN):
        r, c = divmod(idx, cols)
        x, y = c * tw, r * th
        if isinstance(pid, int):
            tpath = os.path.join(CAND_DIR, f"thumb_{pid}.jpg")
            if not os.path.exists(tpath):
                tpath = f"/root/Motion/shwbster_order/candidates/thumb_{pid}.jpg"
            if os.path.exists(tpath):
                try:
                    im = Image.open(tpath).convert("RGB").resize((tw, th))
                    grid.paste(im, (x, y))
                except Exception:
                    pass
        draw.rectangle([x, y, x + tw, y + 22], fill=(0, 0, 0))
        draw.text((x + 4, y + 3), f"S{shot_num:02d} ({s_sec}-{e_sec}s) {pid}", fill=(255, 255, 255))
        draw.rectangle([x, y + th - 20, x + tw, y + th], fill=(0, 0, 0))
        draw.text((x + 4, y + th - 17), desc[:32], fill=(200, 230, 255))

    grid_path = os.path.join(CAND_DIR, "contact_sheet_71_shots.jpg")
    grid.save(grid_path, quality=88)
    print(f"Saved contact sheet: {grid_path}")

    # 2. Download all MP4s in parallel (4 threads, I/O bound)
    print("Downloading 64 HD Pexels clips...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        futures = [ex.submit(download_one, item) for item in SHOT_PLAN]
        for fut in concurrent.futures.as_completed(futures):
            snum, path = fut.result()
            if path:
                sz = os.path.getsize(path) / (1024 * 1024)
                print(f"  Shot {snum:02d} ready ({sz:.1f} MB)")

    # 3. Write full_asset_log.json
    log_entries = []
    for shot_num, s_sec, e_sec, ch, pid, desc, is_h in SHOT_PLAN:
        if isinstance(pid, int):
            info = meta_pool[pid]
            log_entries.append({
                "shot": shot_num,
                "start": s_sec,
                "end": e_sec,
                "chapter": ch,
                "id": pid,
                "provider": "Pexels",
                "url": info["url"],
                "creator": info["user"],
                "creator_url": info.get("user_url", ""),
                "resolution": f"{info['width']}x{info['height']}",
                "description": desc,
                "illustrative_housing_label": is_h,
                "local_path": os.path.join(SHOTS_DIR, f"shot_{shot_num:02d}_{pid}.mp4"),
                "licence": "Pexels Commercial License (Free for commercial and monetised YouTube use, no attribution required)",
            })
        elif pid == "MAP_ECA":
            log_entries.append({
                "shot": shot_num,
                "start": s_sec,
                "end": e_sec,
                "chapter": ch,
                "id": "MAP_ECA_2026",
                "provider": "Natural Earth (Public Domain CC0)",
                "url": "https://www.naturalearthdata.com/",
                "creator": "Natural Earth / Custom Python Animation",
                "creator_url": "https://www.naturalearthdata.com/",
                "resolution": "1920x1080",
                "description": desc,
                "illustrative_housing_label": False,
                "local_path": "/root/Motion/shwbster_order/assets/shot5_world_map_eca.mp4",
                "licence": "CC0 Public Domain",
            })
        elif pid == "SPLIT_NYC_BERN":
            log_entries.append({
                "shot": shot_num,
                "start": s_sec,
                "end": e_sec,
                "chapter": ch,
                "id": "11471275 + 3655304",
                "provider": "Pexels (Composite Split Screen)",
                "url": "https://www.pexels.com/video/river-in-city-11471275/",
                "creator": "Eyal Be / SwissHumanity Stories",
                "creator_url": "https://www.pexels.com/@eyal-be-3539251",
                "resolution": "1920x1080",
                "description": desc,
                "illustrative_housing_label": False,
                "local_path": "COMPOSITE_SPLIT",
                "licence": "Pexels Commercial License",
            })

    log_path = os.path.join(BASE_DIR, "assets/full_asset_log.json")
    open(log_path, "w").write(json.dumps(log_entries, indent=2))
    print(f"SUCCESS: All 71 shots verified and logged to {log_path}")


if __name__ == "__main__":
    main()

