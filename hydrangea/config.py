"""Everything you might want to tweak lives here: labels, prompts, paths, model name.

Each "task" is one question the ML answers from a photo. Each label in a task
is one possible answer. The folders under data/ mirror this exactly:

    data/health/healthy/*.jpg
    data/health/leaf_spot/*.jpg
    ...
    data/stage/blooming/*.jpg
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
MODELS_DIR = ROOT / "models"
REPORTS_DIR = ROOT / "reports"
CACHE_DIR = ROOT / ".cache"

# CLIP = a model trained on 400M (image, caption) pairs. It turns any image or
# any sentence into a list of 512 numbers (an "embedding") such that matching
# images and sentences end up close together. We use it two ways:
#   1. zero-shot: compare the photo to sentences describing each label
#   2. transfer learning: feed its numbers into a small classifier we train
CLIP_MODEL = "openai/clip-vit-base-patch32"

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".heic"}

# Below this confidence we tell the user we're not sure instead of pretending.
MIN_CONFIDENCE = 0.5

# Plants the app knows. key -> English words CLIP understands + kind.
# To add a plant: add it here, add its trimming rules in plants.py and its
# names in i18n_plants.py.
PLANTS = {
    "hydrangea": ("hydrangea", "flower"),
    "rose": ("rose bush", "flower"),
    "peony": ("peony", "flower"),
    "lilac": ("lilac bush", "flower"),
    "tulip": ("tulip", "flower"),
    "iris": ("iris flower", "flower"),
    "apple": ("apple tree", "fruit"),
    "pear": ("pear tree", "fruit"),
    "apricot": ("apricot tree", "fruit"),
    "cherry": ("cherry tree", "fruit"),
    "plum": ("plum tree", "fruit"),
    "grape": ("grape vine", "fruit"),
    "raspberry": ("raspberry bush", "fruit"),
    "currant": ("currant bush", "fruit"),
}

# label -> sentences used for zero-shot. Several phrasings per label make the
# guess more stable (we average them). {plant} is replaced with the plant's
# name, e.g. "a apricot tree leaf with brown spots". Edit these freely and
# re-run training: "prompt engineering" for vision models is a real thing and
# you can measure it.
TASKS = {
    "plant": {key: [f"a photo of a {name}", f"a {name} in a garden", f"a close-up of {name} leaves"]
              for key, (name, _) in PLANTS.items()},
    "health": {
        "healthy": [
            "a photo of a healthy {plant} with green leaves",
            "a lush green {plant} with no damage",
        ],
        "leaf_spot": [
            "a {plant} leaf with brown or purple spots",
            "a close-up of a {plant} leaf with fungal leaf spot disease",
        ],
        "powdery_mildew": [
            "a {plant} leaf covered in white powdery mildew",
            "a {plant} leaf with a dusty white fungal coating",
        ],
        "wilting": [
            "a wilting {plant} with drooping leaves",
            "a thirsty {plant} collapsing from lack of water",
        ],
        "yellowing": [
            "a {plant} with yellow leaves and green veins",
            "a {plant} leaf turning pale yellow",
        ],
    },
    "stage": {
        "budding": [
            "a {plant} with small green buds",
            "a {plant} with new spring growth and buds",
        ],
        "blooming": [
            "a {plant} in full bloom with fresh flowers",
            "bright fresh {plant} flowers",
        ],
        "fading_blooms": [
            "a {plant} with faded brown dried flowers",
            "spent wilted {plant} flowers turning brown",
        ],
        "fruiting": [
            "a {plant} with ripe fruit or berries",
            "a {plant} branch with fruit hanging",
        ],
        "dormant": [
            "a dormant {plant} with bare woody stems in winter",
            "a leafless {plant} with bare branches",
        ],
    },
}
