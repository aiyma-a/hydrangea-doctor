"""Look at one or more photos: health + stage (ML), then trimming advice (rules).

Uses your trained model for a task if models/<task>.joblib exists,
otherwise falls back to zero-shot.

Several photos of the same plant (e.g. a leaf close-up + the whole plant) are
combined into one answer:
  - health: if any photo confidently shows a problem, report it (a leaf
    close-up sees spots a whole-plant photo can't); otherwise "healthy".
  - stage: average the photos' probabilities.

CLI:  python -m hydrangea.predict leaf.jpg plant.jpg --species panicle --place Bishkek --age 4 --lang ru
"""
import argparse
from dataclasses import dataclass
from datetime import date

import joblib
import numpy as np

from . import pruning, zeroshot
from .config import MIN_CONFIDENCE, MODELS_DIR, PLANTS
from .embed import embed_images
from .i18n import LANGS, M, t
from .weather import Weather


@dataclass
class TaskResult:
    label: str
    confidence: float
    probabilities: dict[str, float]
    method: str  # "trained" | "zero-shot"
    min_confidence: float = MIN_CONFIDENCE

    @property
    def unsure(self) -> bool:
        return self.confidence < self.min_confidence


# Untrained (zero-shot) disease guesses are often wrong, and people tend to trust
# an app too much. So without a trained model, only report a disease when very sure.
ZEROSHOT_DISEASE_MIN = 0.75


def _doubt(task: str, r: TaskResult) -> TaskResult:
    if task == "health" and r.method == "zero-shot" and r.label != "healthy":
        r.min_confidence = ZEROSHOT_DISEASE_MIN
    return r


def _load_trained(task: str):
    path = MODELS_DIR / f"{task}.joblib"
    return joblib.load(path) if path.exists() else None


def classify(embeddings: np.ndarray, task: str, plant: str = "hydrangea") -> list[TaskResult]:
    """One TaskResult per photo."""
    clf = _load_trained(task)
    if clf is not None:
        labels, proba, method = [str(c) for c in clf.classes_], clf.predict_proba(embeddings), "trained"
    else:
        labels, proba = zeroshot.predict_proba(task, embeddings, plant)
        method = "zero-shot"
    if task == "stage" and "fruiting" in labels and PLANTS.get(plant, ("", "flower"))[1] != "fruit":
        # Flowers don't fruit: drop that answer and re-share its probability.
        keep = [i for i, label in enumerate(labels) if label != "fruiting"]
        labels, proba = [labels[i] for i in keep], proba[:, keep] / proba[:, keep].sum(axis=1, keepdims=True)
    return [_doubt(task, _result(labels, p, method)) for p in proba]


def _result(labels, proba, method) -> TaskResult:
    i = int(np.argmax(proba))
    return TaskResult(labels[i], float(proba[i]), {label: float(v) for label, v in zip(labels, proba)}, method)


def combine_health(results: list[TaskResult]) -> TaskResult:
    problems = [r for r in results if r.label != "healthy" and not r.unsure]
    if problems:
        return max(problems, key=lambda r: r.confidence)
    healthy = [r for r in results if r.label == "healthy" and not r.unsure]
    if healthy:
        return max(healthy, key=lambda r: r.confidence)
    return combine_average(results)


def combine_average(results: list[TaskResult]) -> TaskResult:
    labels = list(results[0].probabilities)
    mean = np.mean([[r.probabilities[label] for label in labels] for r in results], axis=0)
    return _result(labels, mean, results[0].method)


TASKS = ("plant", "health", "stage")


def analyse(images: list, species: str = "unknown", month: int | None = None, hemisphere: str = "north",
            height_cm: float | None = None, age_years: float | None = None,
            weather: Weather | None = None, plant: str = "auto", ages: dict | None = None) -> dict:
    """images: one or more paths / PIL images of the SAME plant.
    plant: a key from config.PLANTS, or "auto" to recognise it from the photos."""
    if not isinstance(images, (list, tuple)):
        images = [images]
    emb = embed_images(list(images))
    if plant == "auto":
        plant_result = combine_average(classify(emb, "plant"))
        plant = "unknown" if plant_result.unsure else plant_result.label
    else:
        plant_result = TaskResult(plant, 1.0, {plant: 1.0}, "chosen")
    if age_years is None and ages:
        age_years = ages.get(plant)  # remembered age of the recognised plant
    per_photo = {"plant": [plant_result] * len(images),
                 **{task: classify(emb, task, plant) for task in ("health", "stage")}}
    health = _doubt("health", combine_health(per_photo["health"]))
    stage = combine_average(per_photo["stage"])
    # An unsure guess must not drive the advice: pass "unknown" so the rules
    # fall back to the safe, generic answer instead of e.g. "remove mildew leaves".
    advice = pruning.advise("unknown" if health.unsure else health.label,
                            "unknown" if stage.unsure else stage.label,
                            species, month or date.today().month,
                            hemisphere, height_cm, age_years, weather, plant)
    if health.unsure or stage.unsure:
        if advice.trim_now == "yes":  # safety net: an unsure model must never cause a big cut
            advice.trim_now = "light"
        if health.unsure:  # the photo tip below replaces the generic "couldn't judge health" note
            advice.notes = [n for n in advice.notes if n.key != "unknown_health"]
        advice.notes[:0] = [M(f"unsure_{task}") for task, r in (("health", health), ("stage", stage)) if r.unsure]
    return {"plant": plant_result, "plant_key": plant, "health": health, "stage": stage, "advice": advice,
            "photos": [{task: per_photo[task][i] for task in TASKS} for i in range(len(images))]}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("images", nargs="+")
    ap.add_argument("--plant", default="auto", choices=["auto", *PLANTS])
    ap.add_argument("--species", default="unknown", choices=list(pruning.SPECIES))
    ap.add_argument("--month", type=int)
    ap.add_argument("--hemisphere", default="north", choices=["north", "south"])
    ap.add_argument("--height", type=float, help="plant height in cm")
    ap.add_argument("--age", type=float, help="plant age in years")
    ap.add_argument("--place", help="town for live weather, e.g. Bishkek")
    ap.add_argument("--lang", default="en", choices=LANGS)
    a = ap.parse_args()

    weather = None
    if a.place:
        from .weather import fetch
        weather = fetch(a.place)
        print(weather.summary(a.lang))
    r = analyse(a.images, a.species, a.month, a.hemisphere, a.height, a.age, weather, a.plant)
    for path, photo in zip(a.images, r["photos"]):
        print(f"  {path}: " + ", ".join(f"{t(f'label.{photo[k].label}', a.lang)} {photo[k].confidence:.0%}" for k in ("health", "stage")))
    p = r["plant"]
    print(f"  plant: {t(f'plant.{r['plant_key']}', a.lang)} {p.confidence:.0%} [{p.method}]{'  (unsure)' if p.unsure else ''}")
    for task in ("health", "stage"):
        res = r[task]
        flag = "  (unsure)" if res.unsure else ""
        print(f"{task:>7}: {t(f'label.{res.label}', a.lang)} {res.confidence:.0%} [{res.method}]{flag}")
    adv = r["advice"].render(a.lang)
    print(f"\n>>> {adv['trim_now'].upper()} - {adv['headline']}")
    if adv["how_far"]:
        print(adv["how_far"])
    for n in adv["notes"]:
        print(" -", n)


if __name__ == "__main__":
    main()
