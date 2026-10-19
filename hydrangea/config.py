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

# label -> sentences used for zero-shot. Several phrasings per label make the
# guess more stable (we average them). Edit these freely and re-run evaluate:
# "prompt engineering" for vision models is a real thing and you can measure it.
TASKS = {
    "health": {
        "healthy": [
            "a photo of a healthy hydrangea with green leaves",
            "a lush green hydrangea plant with no damage",
        ],
        "leaf_spot": [
            "a hydrangea leaf with brown or purple spots",
            "a close-up of a hydrangea leaf with fungal leaf spot disease",
        ],
        "powdery_mildew": [
            "a hydrangea leaf covered in white powdery mildew",
            "a hydrangea leaf with a dusty white fungal coating",
        ],
        "wilting": [
            "a wilting hydrangea with drooping leaves and flowers",
            "a thirsty hydrangea plant collapsing from lack of water",
        ],
        "yellowing": [
            "a hydrangea with yellow leaves and green veins",
            "a hydrangea leaf turning pale yellow",
        ],
    },
    "stage": {
        "budding": [
            "a hydrangea with small green flower buds",
            "a hydrangea plant with new spring growth and buds",
        ],
        "blooming": [
            "a hydrangea in full bloom with big colorful flowers",
            "fresh bright hydrangea flower heads",
        ],
        "fading_blooms": [
            "a hydrangea with faded brown dried flower heads",
            "spent papery hydrangea blooms turning brown",
        ],
        "dormant": [
            "a dormant hydrangea with bare woody stems in winter",
            "a leafless hydrangea shrub with dry sticks",
        ],
    },
}
