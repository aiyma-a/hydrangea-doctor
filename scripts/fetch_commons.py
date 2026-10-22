"""Download freely licensed photos from Wikimedia Commons into data/<task>/<label>/.

Labels come from the search words, so some photos will be wrong: spot-check before
trusting accuracy numbers. Each photo gets its own 'bush' id (p<number>) so the
grouped cross-validation treats them as different plants. Credits go to data/SOURCES.csv.
Usage: python scripts/fetch_commons.py [photos_per_label]
"""
import csv, re, sys, time
from pathlib import Path
import requests

DATA = Path(__file__).resolve().parent.parent / "data"
API = "https://commons.wikimedia.org/w/api.php"
HEADERS = {"User-Agent": "hydrangea-doctor/0.1 (learning project; https://github.com/aiyma-a/hydrangea-doctor)"}
OK_LICENSE = re.compile(r"^(cc0|cc[ -]by|cc[ -]by-sa|public domain|pd)", re.I)

QUERIES = {
    ("health", "healthy"): ["hydrangea leaves", "hydrangea macrophylla foliage", "green hydrangea leaf"],
    ("health", "leaf_spot"): ["hydrangea leaf spot", "Cercospora leaf spot", "leaf spot disease leaf"],
    ("health", "powdery_mildew"): ["powdery mildew hydrangea", "powdery mildew leaf"],
    ("health", "wilting"): ["wilted hydrangea", "wilting leaves plant", "drought wilt leaves"],
    ("health", "yellowing"): ["hydrangea chlorosis", "yellow leaves hydrangea", "chlorosis leaf"],
    ("stage", "dormant"): ["hydrangea winter", "hydrangea dormant stems", "hydrangea bare branches"],
    ("stage", "budding"): ["hydrangea buds", "hydrangea spring new growth"],
    ("stage", "blooming"): ["hydrangea macrophylla flowers", "hydrangea paniculata inflorescence", "hydrangea in bloom"],
    ("stage", "fading_blooms"): ["hydrangea faded flowers", "hydrangea dried flower heads", "hydrangea autumn flowers"],
}

def search(term, limit):
    r = requests.get(API, headers=HEADERS, params={
        "action": "query", "format": "json", "generator": "search", "gsrsearch": f"{term} filetype:bitmap",
        "gsrnamespace": 6, "gsrlimit": limit, "prop": "imageinfo", "iiprop": "url|extmetadata|mime",
        "iiurlwidth": 640}, timeout=30)
    r.raise_for_status()
    return list(r.json().get("query", {}).get("pages", {}).values())

def main(per_label):
    n_id = 0
    rows = []
    for (task, label), terms in QUERIES.items():
        out = DATA / task / label
        out.mkdir(parents=True, exist_ok=True)
        have = len(list(out.glob("*.jpg")))
        for term in terms:
            for page in search(term, 30):
                if have >= per_label:
                    break
                info = (page.get("imageinfo") or [{}])[0]
                meta = info.get("extmetadata", {})
                lic = meta.get("LicenseShortName", {}).get("value", "")
                if info.get("mime") != "image/jpeg" or not OK_LICENSE.match(lic):
                    continue
                n_id += 1
                name = f"p{int(time.time()) % 100000}{n_id:03d}_{label}.jpg"
                try:
                    img = requests.get(info["thumburl"], headers=HEADERS, timeout=60)
                    img.raise_for_status()
                except Exception as e:
                    print("skip", page["title"], e); continue
                (out / name).write_bytes(img.content)
                have += 1
                rows.append([task, label, name, page["title"], lic, info.get("descriptionurl", "")])
                time.sleep(0.3)
        print(task, label, have)
    src = DATA / "SOURCES.csv"
    new = not src.exists()
    with src.open("a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["task", "label", "file", "commons_title", "license", "page"])
        w.writerows(rows)

if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 25)
