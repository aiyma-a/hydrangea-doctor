"""Turn images and text into CLIP embeddings (lists of numbers).

Computing an embedding takes ~0.1s per image on CPU, so we cache them on disk:
re-running training after adding 5 photos only embeds those 5.
"""
from functools import lru_cache
from pathlib import Path

import numpy as np
import torch
from PIL import Image, ImageOps

from .config import CACHE_DIR, CLIP_MODEL

try:  # iPhone photos are .heic; this is optional
    from pillow_heif import register_heif_opener

    register_heif_opener()
except ImportError:
    pass


def _features(out) -> torch.Tensor:
    # transformers >= 5 returns an output object (projected vector in pooler_output);
    # older versions return the tensor directly.
    return out if isinstance(out, torch.Tensor) else out.pooler_output


@lru_cache(maxsize=1)
def _model():
    from transformers import CLIPModel, CLIPProcessor

    model = CLIPModel.from_pretrained(CLIP_MODEL).eval()
    processor = CLIPProcessor.from_pretrained(CLIP_MODEL)
    return model, processor


def open_image(path_or_image) -> Image.Image:
    img = path_or_image if isinstance(path_or_image, Image.Image) else Image.open(path_or_image)
    # Phones store rotation as metadata; apply it so the model sees it upright.
    return ImageOps.exif_transpose(img).convert("RGB")


@torch.no_grad()
def embed_images(images: list, batch_size: int = 16) -> np.ndarray:
    """images: paths or PIL images -> array of shape (n, 512), each row length 1."""
    model, processor = _model()
    out = []
    for i in range(0, len(images), batch_size):
        batch = [open_image(x) for x in images[i : i + batch_size]]
        inputs = processor(images=batch, return_tensors="pt")
        feats = _features(model.get_image_features(**inputs))
        out.append(torch.nn.functional.normalize(feats, dim=-1).numpy())
    return np.concatenate(out) if out else np.zeros((0, 512), dtype=np.float32)


@torch.no_grad()
def embed_texts(texts: list[str]) -> np.ndarray:
    model, processor = _model()
    inputs = processor(text=texts, return_tensors="pt", padding=True)
    feats = _features(model.get_text_features(**inputs))
    return torch.nn.functional.normalize(feats, dim=-1).numpy()


def embed_paths_cached(paths: list[Path], cache_dir: Path = CACHE_DIR) -> np.ndarray:
    """Like embed_images, but remembers results keyed by file path + size + mtime."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file = cache_dir / f"embeddings_{CLIP_MODEL.replace('/', '_')}.npz"
    cache = dict(np.load(cache_file)) if cache_file.exists() else {}

    def key(p: Path) -> str:
        st = p.stat()
        return f"{p.resolve()}|{st.st_size}|{st.st_mtime_ns}"

    keys = [key(p) for p in paths]
    missing = [p for p, k in zip(paths, keys) if k not in cache]
    if missing:
        print(f"Embedding {len(missing)} new image(s)...")
        for p, vec in zip(missing, embed_images(missing)):
            cache[key(p)] = vec
        np.savez(cache_file, **cache)
    return np.stack([cache[k] for k in keys]) if keys else np.zeros((0, 512), dtype=np.float32)
