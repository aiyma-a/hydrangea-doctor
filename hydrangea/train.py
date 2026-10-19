"""Train our own classifier on your photos and compare it to zero-shot.

Run:  python -m hydrangea.train            (all tasks)
      python -m hydrangea.train health     (one task)

What happens, step by step:
  1. Load every photo in data/<task>/<label>/ and turn it into a CLIP embedding.
  2. Zero-shot baseline: score the same photos with no training.
  3. Cross-validation: split photos into k groups; train on k-1, test on the
     one left out; repeat so every photo is tested exactly once by a model that
     never saw it. This is the honest accuracy number.
  4. Train a final model on ALL photos and save it to models/<task>.joblib.
  5. Write reports/<task>.md and confusion-matrix pictures.
"""
import sys
from datetime import datetime

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import ConfusionMatrixDisplay, accuracy_score, confusion_matrix
from sklearn.model_selection import StratifiedGroupKFold, StratifiedKFold, cross_val_predict

from . import zeroshot
from .config import MODELS_DIR, REPORTS_DIR, TASKS
from .data import load_dataset
from .embed import embed_paths_cached

MIN_PER_LABEL = 2  # cross-validation needs at least 2 photos of a label


def plant_id(path) -> str:
    """'bush3_leaf_02.jpg' -> 'bush3'. Photos of the same bush look alike, so they
    must never be split across training and testing: that would let the model
    'recognise the bush' instead of learning the disease, and inflate the score."""
    return path.stem.split("_")[0].split("-")[0].lower()


def make_classifier() -> LogisticRegression:
    # Logistic regression = the simplest classifier: one weight per (number, label).
    # On top of CLIP's 512 numbers this is called a "linear probe".
    # class_weight="balanced" stops it from favouring labels with more photos.
    return LogisticRegression(max_iter=2000, C=10.0, class_weight="balanced")


def save_confusion(y_true, y_pred, labels, title, path):
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    fig, ax = plt.subplots(figsize=(1.4 * len(labels) + 2, 1.2 * len(labels) + 1.5))
    ConfusionMatrixDisplay(cm, display_labels=labels).plot(ax=ax, colorbar=False, cmap="Greens")
    ax.set_title(title)
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)


def train_task(task: str) -> dict | None:
    paths, y = load_dataset(task)
    counts = {label: y.count(label) for label in TASKS[task]}
    print(f"\n== {task} == photos per label: {counts}")
    used = [label for label, n in counts.items() if n >= MIN_PER_LABEL]
    skipped = [label for label, n in counts.items() if 0 < n < MIN_PER_LABEL]
    if len(used) < 2:
        print(f"Need at least {MIN_PER_LABEL} photos in at least 2 labels. Skipping.")
        return None
    keep = [i for i, label in enumerate(y) if label in used]
    paths, y = [paths[i] for i in keep], np.array([y[i] for i in keep])

    X = embed_paths_cached(paths)

    # Zero-shot baseline (restricted to labels we actually have photos for, to be fair)
    zs_labels, zs_proba = zeroshot.predict_proba(task, X)
    cols = [zs_labels.index(label) for label in used]
    zs_pred = np.array(used)[zs_proba[:, cols].argmax(axis=1)]
    zs_acc = accuracy_score(y, zs_pred)

    # Honest accuracy of our own model via cross-validation
    groups = np.array([plant_id(p) for p in paths])
    groups_per_label = min(len(set(groups[y == label])) for label in used)
    if groups_per_label >= 2:
        k = min(5, groups_per_label)
        cv = StratifiedGroupKFold(n_splits=k, shuffle=True, random_state=0)
        split_note = f"grouped by plant ({len(set(groups))} plants)"
    else:
        k = min(5, min(counts[label] for label in used))
        cv = StratifiedKFold(n_splits=k, shuffle=True, random_state=0)
        split_note = "NOT grouped by plant (name files bush1_..., bush2_... to enable) - score may be optimistic"
        print("Warning:", split_note)
    cv_pred = cross_val_predict(make_classifier(), X, y, cv=cv, groups=groups)
    cv_acc = accuracy_score(y, cv_pred)

    # Final model on everything
    clf = make_classifier().fit(X, y)
    MODELS_DIR.mkdir(exist_ok=True)
    joblib.dump(clf, MODELS_DIR / f"{task}.joblib")

    REPORTS_DIR.mkdir(exist_ok=True)
    save_confusion(y, zs_pred, used, f"{task}: zero-shot ({zs_acc:.0%})", REPORTS_DIR / f"{task}_zeroshot.png")
    save_confusion(y, cv_pred, used, f"{task}: trained ({cv_acc:.0%})", REPORTS_DIR / f"{task}_trained.png")

    wrong = [(p.name, t, pr) for p, t, pr in zip(paths, y, cv_pred) if t != pr]
    lines = [
        f"# {task} report",
        f"_Generated {datetime.now():%Y-%m-%d %H:%M}_",
        "",
        f"Photos used: {len(y)} ({', '.join(f'{label}={counts[label]}' for label in used)})",
        *( [f"Skipped (fewer than {MIN_PER_LABEL} photos): {', '.join(skipped)}"] if skipped else [] ),
        "",
        "| method | accuracy |",
        "|---|---|",
        f"| zero-shot CLIP (no training) | {zs_acc:.0%} |",
        f"| trained linear probe ({k}-fold cross-validation, {split_note}) | {cv_acc:.0%} |",
        f"| always guess the most common label | {max(counts[label] for label in used) / len(y):.0%} |",
        "",
        f"![zero-shot]({task}_zeroshot.png) ![trained]({task}_trained.png)",
        "",
        "## Photos the trained model got wrong",
        *( [f"- `{n}`: is **{t}**, predicted {pr}" for n, t, pr in wrong] or ["None 🎉"] ),
    ]
    (REPORTS_DIR / f"{task}.md").write_text("\n".join(lines) + "\n")
    print(f"zero-shot: {zs_acc:.0%}   trained (cross-validated): {cv_acc:.0%}   -> reports/{task}.md")
    return {"task": task, "n": len(y), "zeroshot_acc": zs_acc, "trained_acc": cv_acc}


def main(argv: list[str]) -> None:
    for task in argv or list(TASKS):
        train_task(task)


if __name__ == "__main__":
    main(sys.argv[1:])
