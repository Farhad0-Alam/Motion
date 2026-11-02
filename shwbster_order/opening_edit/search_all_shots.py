"""Query Pexels Video API for all 10 cities' required shots and save metadata + thumbnails for visual verification."""
import json
import os
import urllib.parse
import urllib.request
from PIL import Image, ImageDraw, ImageFont

CAND_DIR = "/root/Motion/shwbster_order/candidates_full"
os.makedirs(CAND_DIR, exist_ok=True)

env = dict(line.strip().split("=", 1) for line in open("/root/youtubeai/.env") if "=" in line and not line.startswith("#"))
PEXELS_KEY = env.get("PEXELS_API_KEY", "").strip().strip('"')

# Specific queries per city / shot category
QUERIES = [
    # #10 Dubai
    ("dubai_skyline", "Burj Khalifa Dubai skyline"),
    ("dubai_street", "Dubai Marina street building"),
    ("dubai_residential", "Dubai residential apartment building exterior"),
    ("dubai_metro", "Dubai Metro Sheikh Zayed Road train"),
    ("dubai_deira", "Deira Dubai old city street market"),
    # #9 San Francisco
    ("sf_bridge", "Golden Gate Bridge San Francisco bay"),
    ("sf_victorian", "San Francisco Victorian houses residential street"),
    ("sf_apartment", "San Francisco apartment building street"),
    ("sf_cablecar", "San Francisco cable car tram street"),
    ("sf_ferry", "San Francisco Ferry Building street"),
    # #8 Singapore
    ("sg_mbs", "Marina Bay Sands Singapore skyline"),
    ("sg_hdb", "Singapore residential apartment towers HDB"),
    ("sg_traffic", "Singapore city road car traffic highway"),
    ("sg_mrt", "Singapore MRT train subway station"),
    ("sg_hawker", "Singapore street Chinatown hawker"),
    # #7 Bern
    ("bern_clock", "Bern Switzerland Zytglogge old town"),
    ("bern_street", "Bern Switzerland old town street"),
    ("bern_cafe", "Switzerland outdoor cafe restaurant lunch coffee"),
    ("bern_tram", "Bern Switzerland tram public transport"),
    ("bern_aare", "Bern Switzerland Aare river rooftops"),
    # #6 Tel Aviv
    ("tlv_beach", "Tel Aviv beach coastline skyline"),
    ("tlv_street", "Tel Aviv city street building"),
    ("tlv_jaffa", "Jaffa Tel Aviv street promenade"),
    ("tlv_commute", "Tel Aviv traffic bus street"),
    # #5 Hong Kong
    ("hk_harbour", "Victoria Harbour Hong Kong skyline"),
    ("hk_nature", "Hong Kong mountains green country park island"),
    ("hk_towers", "Hong Kong residential apartment buildings dense"),
    ("hk_tram", "Hong Kong double decker tram street"),
    ("hk_market", "Hong Kong street market neighborhood"),
    # #4 Zurich
    ("zh_limmat", "Zurich Switzerland Grossmunster Limmat river"),
    ("zh_street", "Zurich Switzerland city street Bahnhofstrasse"),
    ("zh_tram", "Zurich Switzerland blue tram street"),
    ("zh_lake", "Lake Zurich Switzerland promenade"),
    # #3 London
    ("lon_bridge", "Tower Bridge London River Thames"),
    ("lon_terrace", "London residential brick houses street"),
    ("lon_tube", "London Underground tube train station"),
    ("lon_walk", "London city street commuters walking"),
    # #2 Geneva
    ("gva_jet", "Geneva Switzerland Jet d'Eau lake"),
    ("gva_oldtown", "Geneva Switzerland old town city buildings"),
    ("gva_tram", "Geneva Switzerland street tram traffic"),
    ("gva_lake", "Lake Geneva Switzerland waterfront"),
    # #1 New York
    ("nyc_skyline", "Manhattan skyline Empire State Building"),
    ("nyc_brownstone", "New York apartment building brownstone entrance"),
    ("nyc_neighborhood", "Brooklyn Queens New York residential street"),
    ("nyc_subway", "New York City subway train station platform"),
    ("nyc_street", "Manhattan New York street walking pedestrians"),
    # Ordinary 1-bedroom apartment interiors (living room, kitchen, compact bedroom)
    ("apt_living", "small apartment living room sofa interior"),
    ("apt_kitchen", "compact apartment kitchen interior modern"),
    ("apt_bedroom", "one bedroom apartment room bed window"),
    ("apt_balcony", "apartment balcony view city window"),
]

# False-positive city names to reject when searching a specific city
FORBIDDEN_SLUGS = {
    "bern": ["berlin", "vienna", "prague", "munich"],
    "zurich": ["berlin", "vienna", "munich", "frankfurt"],
    "geneva": ["berlin", "vienna", "genoa", "venice"],
    "tlv": ["miami", "barcelona", "rio", "california"],
}


def pick_hd_file(video_files):
    best = None
    for vf in video_files:
        w = vf.get("width", 0)
        h = vf.get("height", 0)
        if w >= 1920 and h >= 1080 and w > h and vf.get("file_type") == "video/mp4":
            if w == 1920 and h == 1080:
                return vf
            if best is None or (w * h < best.get("width", 99999) * best.get("height", 99999)):
                best = vf
    return best


def main():
    meta_path = os.path.join(CAND_DIR, "all_candidates.json")
    all_cands = json.load(open(meta_path)) if os.path.exists(meta_path) else {}

    for tag, q in QUERIES:
        if tag in all_cands and len(all_cands[tag]) >= 3:
            continue
        url = f"https://api.pexels.com/videos/search?query={urllib.parse.quote(q)}&orientation=landscape&size=medium&per_page=10"
        req = urllib.request.Request(url, headers={"Authorization": PEXELS_KEY, "User-Agent": "Mozilla/5.0"})
        try:
            data = json.loads(urllib.request.urlopen(req, timeout=20).read().decode())
        except Exception as e:
            print(f"Error fetching {tag}: {e}")
            continue

        prefix = tag.split("_")[0]
        forb = FORBIDDEN_SLUGS.get(prefix, [])
        items = []
        for v in data.get("videos", []):
            vid = v["id"]
            vurl = v.get("url", "")
            slug = vurl.lower()
            if any(bad in slug for bad in forb):
                continue
            vf = pick_hd_file(v.get("video_files", []))
            if not vf:
                continue
            dur = v.get("duration", 0)
            if dur < 5:
                continue
            thumb_url = v.get("image", "")
            thumb_path = os.path.join(CAND_DIR, f"thumb_{vid}.jpg")
            if thumb_url and not os.path.exists(thumb_path):
                try:
                    urllib.request.urlretrieve(thumb_url, thumb_path)
                except Exception:
                    pass
            items.append({
                "id": vid,
                "tag": tag,
                "url": vurl,
                "duration": dur,
                "user": v.get("user", {}).get("name", "Pexels Creator"),
                "user_url": v.get("user", {}).get("url", ""),
                "hd_link": vf["link"],
                "width": vf["width"],
                "height": vf["height"],
                "thumb": thumb_path,
            })
            if len(items) >= 6:
                break
        all_cands[tag] = items
        print(f"{tag:18s} -> {len(items)} HD clips found")

    open(meta_path, "w").write(json.dumps(all_cands, indent=2))
    print(f"Saved {len(all_cands)} categories to {meta_path}")


if __name__ == "__main__":
    main()

