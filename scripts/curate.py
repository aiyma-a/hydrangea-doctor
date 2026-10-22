"""Rebuild data/health and data/stage from data_raw/ using a hand-checked keep list.

Every photo in data_raw/ was looked at by eye (contact sheets). Photos were kept only
when they show what the label says; some were moved to the label they actually show.
Photos are numbered by sorted filename within their raw folder.
"""
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW, OUT = ROOT / "data_raw", ROOT / "data"

# (task, label) -> {(raw_task, raw_label): [indices]}
KEEP = {
    ("health", "healthy"): {("health", "healthy"): [18, 22, 23, 24], ("health", "wilting"): [1, 2, 3], ("health", "yellowing"): [12, 14]},
    ("health", "leaf_spot"): {("health", "leaf_spot"): [3, 4, 6, 9, 11, 12, 13, 14, 15, 21, 22, 23, 24]},
    ("health", "powdery_mildew"): {("health", "powdery_mildew"): [2, 3, 11, 12, 13, 16, 20, 21, 22, 23, 24]},
    ("health", "wilting"): {("health", "wilting"): [17, 18, 22, 23, 24]},
    ("health", "yellowing"): {("health", "yellowing"): [0, 10, 11, 17, 18, 19, 24]},
    ("stage", "blooming"): {("stage", "blooming"): [i for i in range(25) if i not in (22, 24)]},
    ("stage", "budding"): {("stage", "budding"): [0, 1, 4, 5, 6, 7, 8, 9, 10, 12, 13, 16, 18, 19, 23, 24]},
    ("stage", "dormant"): {("stage", "dormant"): [4, 11, 12, 13, 14, 16, 17, 19, 22, 23, 24]},
    ("stage", "fading_blooms"): {("stage", "fading_blooms"): [13, 15, 7], ("stage", "dormant"): [5, 8, 10, 15],
                                 ("health", "wilting"): [0, 4, 6, 7, 8, 9, 10, 11], ("health", "yellowing"): [4]},
}

for (task, label), srcs in KEEP.items():
    dest = OUT / task / label
    for old in dest.glob("*.jpg"): old.unlink()
    dest.mkdir(parents=True, exist_ok=True)
    n = 0
    for (rt, rl), idx in srcs.items():
        files = sorted((RAW / rt / rl).glob("*.jpg"))
        for i in idx:
            shutil.copy(files[i], dest / files[i].name); n += 1
    print(task, label, n)
