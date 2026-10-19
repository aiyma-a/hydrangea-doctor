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
"""
from dataclasses import dataclass, field

from .weather import Weather

OLD_WOOD = {"bigleaf", "oakleaf"}
NEW_WOOD = {"panicle", "smooth"}
SPECIES = {
    "bigleaf": "Bigleaf (H. macrophylla) – big round blue/pink balls",
    "oakleaf": "Oakleaf (H. quercifolia) – leaves shaped like oak leaves",
    "panicle": "Panicle (H. paniculata) – cone-shaped, usually white",
    "smooth": "Smooth (H. arborescens) – white balls, e.g. 'Annabelle'",
    "unknown": "I don't know",
}


@dataclass
class Advice:
    trim_now: str  # "yes" | "light" | "no"
    headline: str
    how_far: str = ""
    cut_fraction: float = 0.0  # share of stem height to remove (for the cm estimate)
    notes: list[str] = field(default_factory=list)


def season(month: int, hemisphere: str = "north") -> str:
    if hemisphere == "south":
        month = (month + 5) % 12 + 1  # shift by 6 months
    return {12: "winter", 1: "winter", 2: "late_winter", 3: "early_spring", 4: "spring",
            5: "spring", 6: "summer", 7: "summer", 8: "late_summer", 9: "autumn",
            10: "autumn", 11: "autumn"}[month]


YOUNG_YEARS = 3  # plants younger than this are still building roots
OLD_YEARS = 6  # older shrubs benefit from renewal pruning


def advise(health: str, stage: str, species: str, month: int,
           hemisphere: str = "north", height_cm: float | None = None,
           age_years: float | None = None, weather: Weather | None = None) -> Advice:
    if weather is not None:
        hemisphere = weather.hemisphere
    s = season(month, hemisphere)
    a = _advise(health, stage, species, s)

    # Weather adjustments
    if weather is not None:
        if health == "wilting":
            a.notes.append("It's been hot and dry lately, so this is almost certainly thirst." if weather.hot_dry_recently
                           else "It hasn't been hot and dry lately. If the soil is wet, suspect too much water / root rot.")
        if weather.frost_soon and a.trim_now == "yes" and s in ("late_summer", "autumn"):
            a.trim_now, a.headline = "no", "Wait: frost is coming."
            a.notes.insert(0, f"Frost expected in {weather.first_frost_in_days} day(s). Cutting now pushes out soft "
                              "new shoots that frost will kill. Wait until late winter.")
        elif weather.frost_soon and a.trim_now == "yes":
            a.notes.append("Frost is still in the forecast: pick a dry, mild day for cutting.")

    # Age adjustments
    if age_years is not None and a.trim_now == "yes":
        if age_years < YOUNG_YEARS:
            a.trim_now, a.cut_fraction = "light", a.cut_fraction / 2
            a.headline += " Go gently, it's a young plant."
            if a.how_far:
                a.how_far += " Young plant: cut about half as much as that."
            a.notes.append(f"Under {YOUNG_YEARS} years old: the plant is still building roots. Remove dead wood and "
                           "faded flowers, but no more than half the usual cut.")
        elif age_years >= OLD_YEARS:
            a.notes.append("Older shrub: also do renewal pruning. Cut up to 1/3 of the oldest, thickest stems "
                           "right at the ground each year so young stems replace them.")

    if height_cm and a.cut_fraction:
        a.how_far += f" On a {height_cm:.0f} cm plant that's about {height_cm * a.cut_fraction:.0f} cm off the top."
    return a


def _advise(health: str, stage: str, species: str, s: str) -> Advice:
    # 1. Sick or stressed plants first: pruning adds stress.
    if health == "wilting":
        return Advice("no", "Water first, don't prune.",
                      notes=["Wilting is usually thirst or heat. Water deeply at the base and check again "
                             "next morning. If it hasn't recovered by then, check roots for rot."])
    if health in ("leaf_spot", "powdery_mildew"):
        disease = "leaf spot" if health == "leaf_spot" else "powdery mildew"
        return Advice("light", f"Only remove the infected leaves ({disease}).",
                      how_far="Pick off affected leaves; cut badly affected stems back to healthy tissue.",
                      notes=["Bin the leaves, don't compost them.",
                             "Water at the soil, not over the leaves, and clean pruners between cuts.",
                             "Hold off on any shaping cuts until the plant is healthy."])
    if health == "unknown":
        notes = ["Couldn't judge health from this photo; advice assumes the plant is healthy."]
    elif health == "yellowing":
        notes = ["Yellow leaves with green veins usually mean the soil is too alkaline (iron can't be absorbed); "
                 "pruning won't fix it. A soil pH test is the next step."]
    else:
        notes = []

    # 2. Healthy (or just yellowing): depends on species + season + stage.
    if species == "unknown":
        return Advice("light", "Tell me the hydrangea type for full advice. Until then, only deadhead.",
                      how_far="Snip faded flower heads just above the first pair of fat buds below the flower. "
                              "That's safe for every type.",
                      notes=notes + ["Bigleaf/oakleaf flower on last year's stems; panicle/smooth on this year's. "
                                     "Cutting the wrong type at the wrong time costs you next year's flowers."])

    if species in NEW_WOOD:
        if s in ("late_winter", "early_spring") or (stage == "dormant" and s == "winter"):
            if species == "panicle":
                return Advice("yes", "Good time for the main prune.",
                              how_far="Cut every stem back by about one third, just above a pair of buds. "
                                      "Remove thin, crossing, or dead stems at the base.",
                              cut_fraction=1 / 3, notes=notes)
            return Advice("yes", "Good time for the main prune.",
                          how_far="Cut all stems down to about 30–45 cm from the ground. "
                                  "Shorter stems flop less under heavy flowers.",
                          cut_fraction=0.5, notes=notes)
        if stage == "fading_blooms":
            return Advice("light", "Optional tidy-up only.",
                          how_far="Deadhead faded flowers if you don't like the look; leave the main prune for late winter.",
                          notes=notes + ["Many people leave dried heads on for winter interest."])
        return Advice("no", "Not now. The main prune is in late winter / early spring.", notes=notes)

    # OLD_WOOD species
    if stage == "fading_blooms" and s in ("summer", "late_summer"):
        return Advice("yes", "Trim now, right after flowering.",
                      how_far="Cut each faded flower stem back to the first pair of healthy, fat buds below the flower head "
                              "(usually 10–30 cm down). Remove a few of the oldest stems at the base to thin.",
                      notes=notes + ["Stop by late summer: after that, cuts remove the buds that make next year's flowers."])
    if s in ("early_spring", "spring") and stage in ("budding", "dormant"):
        return Advice("light", "Only remove dead wood.",
                      how_far="Cut stems that show no green buds back to the first live pair of buds, or to the ground if fully dead.",
                      notes=notes + ["Scratch a stem with your nail: green underneath = alive."])
    if stage == "fading_blooms":
        return Advice("light", "Light deadheading only.",
                      how_far="Snip only the flower head itself, just above the first pair of buds. No hard cuts.",
                      notes=notes + ["Next year's flower buds have already formed in these stems. Hard cuts now remove them.",
                                     "Leaving dried heads on over winter also protects the buds from frost."])
    return Advice("no", "Leave it. This type flowers on last year's stems.",
                  notes=notes + ["The right window is right after it finishes flowering in summer."])
