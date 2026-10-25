"""Score the model on real phone photos of a real garden (garden/labels.csv).

Run:  python scripts/garden_eval.py

The question: does the app work on photos it was never built from? Four ways to answer,
all scored on the same garden photos:

  1. zero-shot, old labels         (what the live app used before)
  2. zero-shot, with "autumn"      (new label, no training)
  3. trained on the internet photos only (data/)
  4. trained on internet photos + garden photos, tested on garden photos from groups it
     never saw (leave-one-group-out). Photos taken one after another are in one group.

Health: every garden photo is "autumn" (late October), so a correct answer is "autumn",
and for the old label set "healthy" counts as correct too (nothing to treat).
Stage: only photos that clearly show flowers are labelled (blooming / fading_blooms).
"""
import csv
import sys
from pathlib import Path

import numpy as np
from sklearn.model_selection import LeaveOneGroupOut

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from hydrangea import zeroshot  # noqa: E402
from hydrangea.config import TASKS  # noqa: E402
from hydrangea.data import load_dataset  # noqa: E402
from hydrangea.embed import embed_paths_cached  # noqa: E402
from hydrangea.predict import NO_PROBLEM  # noqa: E402
from hydrangea.train import make_classifier  # noqa: E402

GARDEN = Path(__file__).resolve().parent.parent / "garden"
FLOWER_STAGES = [s for s in TASKS["stage"] if s != "fruiting"]  # a hydrangea doesn't fruit


def load_garden():
    rows = list(csv.DictReader(open(GARDEN / "labels.csv")))
    paths = [GARDEN / r["file"] for r in rows]
    return rows, paths, embed_paths_cached(paths)


def zs_pick(task, X, labels_allowed):
    labels, proba = zeroshot.predict_proba(task, X)
    cols = [labels.index(label) for label in labels_allowed]
    return np.array(labels_allowed)[proba[:, cols].argmax(axis=1)]


def fit_on(task, extra_X=None, extra_y=None, allowed=None):
    paths, y = load_dataset(task)
    keep = [i for i, label in enumerate(y) if allowed is None or label in allowed]
    X = embed_paths_cached([paths[i] for i in keep])
    y = [y[i] for i in keep]
    if extra_X is not None:
        X, y = np.vstack([X, extra_X]), y + list(extra_y)
    return make_classifier().fit(X, y)


def pct(a):
    return f"{100 * np.mean(a):.0f}%"


def main():
    rows, _, X = load_garden()
    groups = np.array([r["group"] for r in rows])
    out = {}

    # ---------- health ----------
    old = [label for label in TASKS["health"] if label != "autumn"]
    ok = lambda pred: np.array([p in NO_PROBLEM for p in pred])  # noqa: E731  "no false alarm"
    h1 = zs_pick("health", X, old)
    h2 = zs_pick("health", X, list(TASKS["health"]))
    h3 = fit_on("health", allowed=old).predict(X)
    h4 = np.empty(len(rows), dtype=object)
    for tr, te in LeaveOneGroupOut().split(X, groups=groups):
        clf = fit_on("health", X[tr], ["autumn"] * len(tr))
        h4[te] = clf.predict(X[te])
    out["health"] = [("zero-shot, old labels", h1), ("zero-shot, with autumn label", h2),
                     ("trained on internet photos", h3), ("trained + garden photos (unseen groups)", h4)]

    # ---------- stage ----------
    idx = [i for i, r in enumerate(rows) if r["stage"]]
    Xs, ys, gs = X[idx], np.array([rows[i]["stage"] for i in idx]), groups[idx]
    s1 = zs_pick("stage", Xs, FLOWER_STAGES)
    s2 = fit_on("stage", allowed=FLOWER_STAGES).predict(Xs)
    s3 = np.empty(len(idx), dtype=object)
    for tr, te in LeaveOneGroupOut().split(Xs, groups=gs):
        s3[te] = fit_on("stage", Xs[tr], ys[tr], allowed=FLOWER_STAGES).predict(Xs[te])
    majority = max(np.mean(ys == s) for s in set(ys))

    lines = ["# Garden test", "",
             f"{len(rows)} phone photos of panicle hydrangeas, late October, {len(set(groups))} groups of photos taken in a row.",
             f"Stage is scored on the {len(idx)} photos that clearly show flowers.", "",
             "## Health (every photo is normal autumn)", "",
             "| method | right (autumn, or healthy for the old labels) | false alarm (says disease, wilting or yellowing) |", "|---|---|---|"]
    for name, pred in out["health"]:
        lines.append(f"| {name} | {pct(ok(pred))} | {pct(~ok(pred))} |")
    lines += ["", "Answers the old zero-shot gave: " + ", ".join(f"{k} {int((h1 == k).sum())}" for k in sorted(set(h1))), "",
              "## Stage (blooming vs fading_blooms)", "", "| method | accuracy |", "|---|---|",
              f"| always guess the most common stage | {majority * 100:.0f}% |",
              f"| zero-shot | {pct(s1 == ys)} |",
              f"| trained on internet photos | {pct(s2 == ys)} |",
              f"| trained + garden photos (unseen groups) | {pct(s3 == ys)} |", "",
              "## Read this before trusting the numbers", "",
              "- Health in the garden photos has only ONE true answer (autumn). A model that always says 'autumn' scores 100% here. "
              "In the trained + garden row, 'autumn' also comes only from phone photos, so the model may be learning "
              "'phone photo of a garden' instead of 'autumn'. A fair test needs healthy summer photos and some diseased leaves from the same garden.",
              "- Groups are photos taken one after another, not confirmed separate bushes, so leakage between train and test is possible.",
              f"- Stage has {len(idx)} photos and one season. Treat differences of a few photos as noise."]
    Path(__file__).resolve().parent.parent.joinpath("reports", "garden.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
