"""Trimming advice: plain rules, not ML.

Why rules? Whether to cut depends on facts a photo can't show reliably (which
species, what month) and on well-established gardening knowledge. ML decides
what the photo shows; these rules decide what to do about it.

Key fact: hydrangeas either flower on
  - OLD wood (stems grown last year): bigleaf, oakleaf. Cut at the wrong time
    and you cut off next year's flowers.
  - NEW wood (stems grown this year): panicle, smooth. Safe to cut back hard in
    late winter.

Sources: University of Minnesota Extension "Pruning hydrangeas";
Penn State Extension "Pruning Hydrangeas"; RHS "Hydrangeas: pruning".

The rules return message keys (M("water_first")), not sentences, so the same
advice can be shown in English, Russian or Kyrgyz. The text lives in i18n.py.
"""
from dataclasses import dataclass, field

from . import plants
from .i18n import M, Msg
from .weather import Weather

OLD_WOOD = {"bigleaf", "oakleaf"}
NEW_WOOD = {"panicle", "smooth"}
SPECIES = ("bigleaf", "oakleaf", "panicle", "smooth", "unknown")
YOUNG_YEARS = 3  # plants younger than this are still building roots
OLD_YEARS = 6  # older shrubs benefit from renewal pruning
RENEWAL_SHRUBS = {"hydrangea", "lilac", "currant"}  # multi-stem shrubs where you cut old stems at the ground


@dataclass
class Advice:
    trim_now: str  # "yes" | "light" | "no"
    headline: list[Msg]
    how_far: list[Msg] = field(default_factory=list)
    notes: list[Msg] = field(default_factory=list)
    cut_fraction: float = 0.0  # share of stem height to remove (for the cm estimate)

    def render(self, lang: str = "en") -> dict:
        return {
            "trim_now": self.trim_now,
            "headline": " ".join(m.render(lang) for m in self.headline),
            "how_far": " ".join(m.render(lang) for m in self.how_far),
            "notes": [m.render(lang) for m in self.notes],
        }


def _a(trim_now, headline, how_far=None, notes=(), cut_fraction=0.0) -> Advice:
    return Advice(trim_now, [M(headline)], [M(how_far)] if how_far else [], [M(n) for n in notes], cut_fraction)


def season(month: int, hemisphere: str = "north") -> str:
    if hemisphere == "south":
        month = (month + 5) % 12 + 1  # shift by 6 months
    return {12: "winter", 1: "winter", 2: "late_winter", 3: "early_spring", 4: "spring",
            5: "spring", 6: "summer", 7: "summer", 8: "late_summer", 9: "autumn",
            10: "autumn", 11: "autumn"}[month]


def advise(health: str, stage: str, species: str, month: int,
           hemisphere: str = "north", height_cm: float | None = None,
           age_years: float | None = None, weather: Weather | None = None,
           plant: str = "hydrangea") -> Advice:
    if weather is not None:
        hemisphere = weather.hemisphere
    s = season(month, hemisphere)
    a = _advise(health, stage, species, s, plant)

    # Weather adjustments
    if weather is not None:
        if health == "wilting":
            a.notes.append(M("hot_dry_thirst" if weather.hot_dry_recently else "not_hot_dry"))
        if weather.frost_soon and a.trim_now == "yes" and s in ("late_summer", "autumn"):
            a.trim_now, a.headline = "no", [M("frost_wait")]
            a.notes.insert(0, M("frost_wait_note", days=weather.first_frost_in_days))
        elif weather.frost_soon and a.trim_now == "yes":
            a.notes.append(M("frost_mild_day"))

    # Age adjustments
    if age_years is not None and a.trim_now == "yes":
        if age_years < YOUNG_YEARS:
            a.trim_now, a.cut_fraction = "light", a.cut_fraction / 2
            a.headline.append(M("young_gentle"))
            if a.how_far:
                a.how_far.append(M("young_how"))
            a.notes.append(M("young_note", years=YOUNG_YEARS))
        elif age_years >= OLD_YEARS and plant in RENEWAL_SHRUBS:
            a.notes.append(M("renewal_note"))

    if height_cm and a.cut_fraction:
        a.how_far.append(M("cm_estimate", height=f"{height_cm:.0f}", cut=f"{height_cm * a.cut_fraction:.0f}"))
    return a


def _advise(health: str, stage: str, species: str, s: str, plant: str = "hydrangea") -> Advice:
    # 1. Sick or stressed plants first: pruning adds stress.
    if health == "wilting":
        return _a("no", "water_first", notes=["wilting_note"])
    if health in ("leaf_spot", "powdery_mildew"):
        a = _a("light", "remove_infected", "remove_infected_how", ["bin_leaves", "water_soil", "hold_shaping"])
        a.headline = [M("remove_infected", disease=M(f"label.{health}"))]
        return a
    notes = {"unknown": ["unknown_health"], "yellowing": ["yellowing_note"], "autumn": ["autumn_note"]}.get(health, [])

    if plant != "hydrangea":
        return _advise_other(plant, stage, s, notes)

    # 2. Healthy (or just yellowing): depends on species + season + stage.
    if species not in OLD_WOOD | NEW_WOOD:
        return _a("light", "tell_type", "deadhead_safe_how", notes + ["wood_types"])

    if species in NEW_WOOD:
        if s in ("late_winter", "early_spring") or (stage == "dormant" and s == "winter"):
            if species == "panicle":
                return _a("yes", "main_prune", "panicle_how", notes, cut_fraction=1 / 3)
            return _a("yes", "main_prune", "smooth_how", notes, cut_fraction=0.5)
        if stage == "fading_blooms":
            return _a("light", "optional_tidy", "optional_tidy_how", notes + ["dried_heads_interest"])
        return _a("no", "not_now_new_wood", notes=notes)

    # OLD_WOOD species
    if stage == "fading_blooms" and s in ("summer", "late_summer"):
        return _a("yes", "trim_after_flowering", "after_flowering_how", notes + ["stop_late_summer"])
    if s in ("early_spring", "spring") and stage in ("budding", "dormant"):
        return _a("light", "dead_wood_only", "dead_wood_how", notes + ["scratch_test"])
    if stage == "fading_blooms":
        return _a("light", "light_deadhead", "light_deadhead_how", notes + ["buds_formed", "heads_protect"])
    return _a("no", "leave_old_wood", notes=notes + ["right_window"])


def _advise_other(plant: str, stage: str, s: str, notes: list[str]) -> Advice:
    if plant not in plants.RULES:
        return _a("light", "unknown_plant", "unknown_plant_how", notes)
    w, spec = plants.match(plant, s, stage)
    if w is not None:
        return _a(w.trim, w.headline, w.how, notes + list(w.notes), cut_fraction=w.cut_fraction)
    extra = [spec["never"]] if "never" in spec and s in ("winter", "late_winter", "early_spring", "autumn") else []
    return _a("no", spec["when"], notes=notes + extra)
