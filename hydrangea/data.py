"""Find labelled photos on disk."""
from pathlib import Path

from .config import DATA_DIR, IMAGE_EXTENSIONS, TASKS


def list_images(folder: Path) -> list[Path]:
    if not folder.is_dir():
        return []
    return sorted(p for p in folder.iterdir() if p.suffix.lower() in IMAGE_EXTENSIONS)


def load_dataset(task: str, data_dir: Path = DATA_DIR) -> tuple[list[Path], list[str]]:
    """Return (image paths, label of each image) for one task."""
    paths, labels = [], []
    for label in TASKS[task]:
        for p in list_images(data_dir / task / label):
            paths.append(p)
            labels.append(label)
    return paths, labels


def make_folders(data_dir: Path = DATA_DIR) -> None:
    for task, labels in TASKS.items():
        for label in labels:
            (data_dir / task / label).mkdir(parents=True, exist_ok=True)
