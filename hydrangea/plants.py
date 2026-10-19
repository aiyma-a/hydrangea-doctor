"""Trimming rules for every plant except hydrangea (hydrangea has its own,
more detailed rules in pruning.py because they depend on the species).

Each plant is a list of "windows": when the season (and optionally the stage)
matches, that advice applies. The first matching window wins. If none match,
the plant gets "Not now" plus a note saying when the right time is.

Sources: RHS pruning guides (roses, lilac, peonies, apples & pears, plums &
cherries, grapes, raspberries, currants); University of Minnesota Extension
(pruning fruit trees, perennials). Stone fruit (apricot, cherry, plum) is never
pruned in winter: slow-healing cuts let in silver leaf and bacterial canker
and make the tree bleed gum.
"""
from dataclasses import dataclass

ANY = None


@dataclass(frozen=True)
class Window:
    seasons: frozenset
    stages: frozenset | None  # None = any stage
    trim: str  # "yes" | "light"
    headline: str
    how: str
    notes: tuple = ()
    cut_fraction: float = 0.0


def W(seasons, trim, headline, how, stages=ANY, notes=(), cut=0.0) -> Window:
    return Window(frozenset(seasons), frozenset(stages) if stages else None, trim, headline, how, tuple(notes), cut)


GROWING = ("spring", "summer", "late_summer")
STONE_FRUIT = [
    W(["summer", "late_summer"], "yes", "after_harvest", "stone_summer_how", notes=["stone_dry_day"]),
    W(GROWING + ("early_spring",), "yes", "after_harvest", "stone_summer_how", stages=["fruiting"], notes=["stone_dry_day"]),
    W(["spring"], "yes", "tree_main_prune", "stone_how", notes=["max_quarter", "stone_dry_day"]),
]

RULES: dict[str, dict] = {
    "rose": {"when": "rose_when", "windows": [
        W(["early_spring"], "yes", "main_prune", "rose_how", cut=0.4),
        W(GROWING, "light", "deadhead_only", "rose_deadhead_how", stages=["fading_blooms"]),
        W(["autumn"], "light", "light_tidy", "rose_autumn_how"),
    ]},
    "peony": {"when": "peony_when", "windows": [
        W(["autumn"], "yes", "cut_to_ground", "peony_autumn_how"),
        W(GROWING, "light", "deadhead_only", "peony_deadhead_how", stages=["fading_blooms"], notes=["keep_leaves"]),
    ]},
    "lilac": {"when": "lilac_when", "windows": [
        W(["spring", "summer"], "yes", "trim_after_flowering", "lilac_how", stages=["fading_blooms"]),
        W(["late_winter", "early_spring"], "light", "dead_wood_only", "dead_wood_how", notes=["lilac_buds"]),
    ]},
    "tulip": {"when": "tulip_when", "windows": [
        W(GROWING, "light", "deadhead_only", "tulip_how", stages=["fading_blooms"], notes=["keep_leaves"]),
        W(["summer", "late_summer"], "yes", "cut_leaves", "tulip_leaves_how", stages=["dormant"]),
    ]},
    "iris": {"when": "iris_when", "windows": [
        W(GROWING, "light", "deadhead_only", "iris_deadhead_how", stages=["fading_blooms"]),
        W(["autumn"], "yes", "cut_leaves", "iris_autumn_how"),
    ]},
    "apple": {"when": "pome_when", "windows": [
        W(["late_winter", "early_spring"], "yes", "tree_main_prune", "pome_how", notes=["max_quarter"]),
        W(["summer"], "light", "summer_tidy", "water_sprouts_how"),
    ]},
    "pear": {"when": "pome_when", "windows": [
        W(["late_winter", "early_spring"], "yes", "tree_main_prune", "pome_how", notes=["max_quarter"]),
        W(["summer"], "light", "summer_tidy", "water_sprouts_how"),
    ]},
    "apricot": {"when": "stone_when", "windows": STONE_FRUIT, "never": "stone_no_winter"},
    "cherry": {"when": "stone_when", "windows": STONE_FRUIT, "never": "stone_no_winter"},
    "plum": {"when": "stone_when", "windows": STONE_FRUIT, "never": "stone_no_winter"},
    "grape": {"when": "grape_when", "windows": [
        W(["autumn", "winter"], "yes", "vine_main_prune", "grape_how", stages=["dormant", "fading_blooms"],
          notes=["grape_autumn_note"]),
        W(["late_winter"], "yes", "vine_main_prune", "grape_how", notes=["grape_bleed_note"]),
        W(["summer", "late_summer"], "light", "summer_tidy", "grape_summer_how"),
    ]},
    "raspberry": {"when": "raspberry_when", "windows": [
        W(["summer", "late_summer", "autumn"], "yes", "after_harvest", "raspberry_how", stages=["fruiting", "dormant"]),
        W(["late_summer", "autumn"], "yes", "after_harvest", "raspberry_how"),
        W(["early_spring"], "light", "spring_thin", "raspberry_spring_how"),
    ]},
    "currant": {"when": "currant_when", "windows": [
        W(["late_winter", "early_spring", "autumn"], "yes", "bush_main_prune", "currant_how", stages=["dormant", "unknown"]),
        W(["autumn"], "yes", "bush_main_prune", "currant_how"),
    ]},
}


def match(plant: str, season: str, stage: str) -> tuple[Window | None, dict]:
    spec = RULES[plant]
    for w in spec["windows"]:
        if season in w.seasons and (w.stages is None or stage in w.stages):
            return w, spec
    return None, spec
