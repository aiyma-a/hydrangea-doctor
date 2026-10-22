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


# "Is there a plant in this photo at all?" Compare the photo to plant sentences and to
# a list of things people might photograph by mistake. Probability mass on the plant
# sentences is the score.
PLANT_PROMPTS = ["a photo of a plant", "a close-up of a leaf", "a photo of flowers", "a tree or a bush", "a garden with plants"]
NOT_PLANT_PROMPTS = ["a photo of a person's face", "a photo of people", "the inside of a room", "a plate of food", "a car or a vehicle",
                     "a pet or an animal", "a building", "a screenshot or a page of text", "a laptop or a phone", "a piece of furniture",
                     "a blank wall or floor", "a dark blurry photo"]
PLANT_MIN = 0.6  # below this we say "I do not see a plant" (tested: keeps 100% of 111 plant photos, rejects 93% of 44 non-plant photos)


@lru_cache(maxsize=1)
def _presence_embeddings() -> np.ndarray:
    vecs = embed_texts(PLANT_PROMPTS + NOT_PLANT_PROMPTS)
    return vecs / np.linalg.norm(vecs, axis=1, keepdims=True)


def plant_score(image_embeddings: np.ndarray) -> np.ndarray:
    """Per photo: probability (0-1) that it shows a plant."""
    p = softmax(LOGIT_SCALE * image_embeddings @ _presence_embeddings().T)
    return p[:, : len(PLANT_PROMPTS)].sum(axis=1)
