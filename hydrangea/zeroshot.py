"""Zero-shot classification: no training, just "which sentence matches this photo best?"."""
from functools import lru_cache

import numpy as np

from .config import PLANTS, TASKS
from .embed import embed_texts

# CLIP's own learned "temperature". Similarities are small numbers (~0.2-0.3);
# multiplying by 100 before softmax turns them into confident probabilities.
LOGIT_SCALE = 100.0


@lru_cache(maxsize=None)
def label_embeddings(task: str, plant: str = "hydrangea") -> tuple[list[str], np.ndarray]:
    labels = list(TASKS[task])
    name = PLANTS[plant][0] if plant in PLANTS else "plant"
    vecs = []
    for label in labels:
        prompts = [p.replace("{plant}", name) for p in TASKS[task][label]]
        v = embed_texts(prompts).mean(axis=0)  # average the phrasings
        vecs.append(v / np.linalg.norm(v))
    return labels, np.stack(vecs)


def softmax(x: np.ndarray) -> np.ndarray:
    e = np.exp(x - x.max(axis=-1, keepdims=True))
    return e / e.sum(axis=-1, keepdims=True)


def predict_proba(task: str, image_embeddings: np.ndarray, plant: str = "hydrangea") -> tuple[list[str], np.ndarray]:
    """Returns (labels, probabilities of shape (n_images, n_labels))."""
    labels, text = label_embeddings(task, plant)
    return labels, softmax(LOGIT_SCALE * image_embeddings @ text.T)
