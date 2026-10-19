"""Look at one photo: health + stage (ML), then trimming advice (rules).

Uses your trained model for a task if models/<task>.joblib exists,
otherwise falls back to zero-shot.

CLI:  python -m hydrangea.predict photo.jpg --species panicle --place Bishkek --age 4
"""
import argparse
from dataclasses import dataclass
from datetime import date

import joblib
import numpy as np

from . import pruning, zeroshot
from .config import MIN_CONFIDENCE, MODELS_DIR, TASKS
from .embed import embed_images
from .weather import Weather


@dataclass
class TaskResult:
    label: str
    confidence: float
    probabilities: dict[str, float]
    method: str  # "trained" | "zero-shot"

    @property
    def unsure(self) -> bool:
        return self.confidence < MIN_CONFIDENCE


def _load_trained(task: str):
    path = MODELS_DIR / f"{task}.joblib"
    return joblib.load(path) if path.exists() else None


def classify(embedding: np.ndarray, task: str) -> TaskResult:
    clf = _load_trained(task)
    if clf is not None:
        labels, proba, method = [str(c) for c in clf.classes_], clf.predict_proba(embedding[None])[0], "trained"
    else:
        labels, p = zeroshot.predict_proba(task, embedding[None])
        proba, method = p[0], "zero-shot"
    i = int(np.argmax(proba))
    return TaskResult(labels[i], float(proba[i]),
                      {label: float(v) for label, v in zip(labels, proba)}, method)


def analyse(image, species: str = "unknown", month: int | None = None, hemisphere: str = "north",
            height_cm: float | None = None, age_years: float | None = None,
            weather: Weather | None = None) -> dict:
    emb = embed_images([image])[0]
    results = {task: classify(emb, task) for task in TASKS}
    health, stage = results["health"], results["stage"]
    # An unsure guess must not drive the advice: pass "unknown" so the rules
    # fall back to the safe, generic answer instead of e.g. "remove mildew leaves".
    advice = pruning.advise("unknown" if health.unsure else health.label,
                            "unknown" if stage.unsure else stage.label,
                            species, month or date.today().month,
                            hemisphere, height_cm, age_years, weather)
    if health.unsure or stage.unsure:
        if advice.trim_now == "yes":  # safety net: an unsure model must never cause a big cut
            advice.trim_now = "light"
        unsure = " and ".join(t for t, r in results.items() if r.unsure)
        advice.notes.insert(0, f"I'm not confident about the {unsure} from this photo. For health, try a close-up "
                               "of one leaf in daylight; for stage, a photo of the whole plant.")
    return {"health": health, "stage": stage, "advice": advice}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("image")
    ap.add_argument("--species", default="unknown", choices=list(pruning.SPECIES))
    ap.add_argument("--month", type=int)
    ap.add_argument("--hemisphere", default="north", choices=["north", "south"])
    ap.add_argument("--height", type=float, help="plant height in cm")
    ap.add_argument("--age", type=float, help="plant age in years")
    ap.add_argument("--place", help="town for live weather, e.g. Bishkek")
    a = ap.parse_args()

    weather = None
    if a.place:
        from .weather import fetch
        weather = fetch(a.place)
        print("Weather:", weather.summary())
    r = analyse(a.image, a.species, a.month, a.hemisphere, a.height, a.age, weather)
    for task in TASKS:
        t = r[task]
        flag = "  (unsure)" if t.unsure else ""
        print(f"{task:>7}: {t.label} {t.confidence:.0%} [{t.method}]{flag}")
    adv = r["advice"]
    print(f"\nTrim now? {adv.trim_now.upper()} - {adv.headline}")
    if adv.how_far:
        print("How far:", adv.how_far)
    for n in adv.notes:
        print(" -", n)


if __name__ == "__main__":
    main()
