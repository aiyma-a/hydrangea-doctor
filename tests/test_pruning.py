from hydrangea.pruning import advise, season
from hydrangea.train import plant_id
from hydrangea.weather import Weather, summarize
from pathlib import Path

from hydrangea.i18n import LANGS, MESSAGES
from hydrangea.predict import TaskResult, combine_average, combine_health


def w(frost=False, hot_dry=False, lat=42.9):
    return Weather("Test", lat, frost, 3 if frost else None, hot_dry, 32 if hot_dry else 20, 0 if hot_dry else 20)


def test_seasons_flip_in_south():
    assert season(1, "north") == "winter"
    assert season(1, "south") == "summer"
    assert season(7, "south") == "winter"


def test_wilting_never_prunes():
    assert advise("wilting", "blooming", "panicle", 3).trim_now == "no"


def test_panicle_late_winter_cuts_a_third():
    a = advise("healthy", "dormant", "panicle", 2, height_cm=150)
    assert a.trim_now == "yes" and "50 cm" in a.render()["how_far"]


def test_bigleaf_not_cut_in_autumn():
    assert advise("healthy", "fading_blooms", "bigleaf", 10).trim_now == "light"
    assert advise("healthy", "dormant", "bigleaf", 11).trim_now == "no"


def test_bigleaf_cut_after_flowering_in_summer():
    assert advise("healthy", "fading_blooms", "bigleaf", 7).trim_now == "yes"


def test_frost_blocks_late_summer_cut():
    a = advise("healthy", "fading_blooms", "bigleaf", 8, weather=w(frost=True))
    assert a.trim_now == "no" and "Frost" in a.render()["notes"][0]


def test_weather_sets_hemisphere():
    # February in Sydney is summer: no main prune for panicle
    assert advise("healthy", "blooming", "panicle", 2, weather=w(lat=-33.9)).trim_now == "no"


def test_young_plant_cut_halved():
    a = advise("healthy", "dormant", "panicle", 2, height_cm=150, age_years=1)
    assert a.trim_now == "light" and "25 cm" in a.render()["how_far"]


def test_old_plant_gets_renewal_note():
    a = advise("healthy", "dormant", "panicle", 2, age_years=10)
    assert any("oldest" in n for n in a.render()["notes"])


def test_wilting_hot_dry_says_thirst():
    a = advise("wilting", "blooming", "bigleaf", 7, weather=w(hot_dry=True))
    assert any("thirst" in n for n in a.render()["notes"])


def test_unknown_species_only_deadheads():
    assert advise("healthy", "fading_blooms", "unknown", 9).trim_now == "light"


def test_summarize_weather():
    daily = {"temperature_2m_min": [10] * 7 + [5, 3, -1] + [2] * 11,
             "temperature_2m_max": [31] + [25] * 20,
             "precipitation_sum": [0] * 21}
    s = summarize(daily, "X", 40)
    assert s.frost_soon and s.first_frost_in_days == 2 and s.hot_dry_recently


def test_plant_id():
    assert plant_id(Path("bush3_leaf_02.jpg")) == "bush3"
    assert plant_id(Path("Bush3-a.JPG")) == "bush3"


def test_unknown_health_and_stage_fall_back_safely():
    a = advise("unknown", "unknown", "bigleaf", 10)
    assert a.trim_now == "no" and "Couldn't judge health" in a.render()["notes"][0]
    assert advise("unknown", "unknown", "panicle", 2).trim_now == "yes"


def test_every_advice_renders_in_every_language():
    w_frost = w(frost=True)
    for lang in LANGS:
        for health in ["healthy", "leaf_spot", "powdery_mildew", "wilting", "yellowing", "unknown"]:
            for stage in ["budding", "blooming", "fading_blooms", "dormant", "unknown"]:
                for species in ["bigleaf", "oakleaf", "panicle", "smooth", "unknown"]:
                    for month in range(1, 13):
                        a = advise(health, stage, species, month, height_cm=100, age_years=1, weather=w_frost)
                        r = a.render(lang)
                        assert r["headline"] and "{" not in r["headline"] + r["how_far"] + "".join(r["notes"])


def test_russian_disease_name_inside_sentence():
    r = advise("powdery_mildew", "blooming", "bigleaf", 6).render("ru")
    assert "мучнистая роса" in r["headline"]


def test_weather_summary_translated():
    assert "үшүк" in w(frost=True).summary("ky")


def _tr(label, conf, labels=("healthy", "leaf_spot")):
    probs = {l: (conf if l == label else (1 - conf) / (len(labels) - 1)) for l in labels}
    return TaskResult(label, conf, probs, "zero-shot")


def test_one_confident_problem_photo_wins():
    # whole-plant photo looks healthy, leaf close-up clearly shows spots -> leaf_spot
    assert combine_health([_tr("healthy", 0.9), _tr("leaf_spot", 0.7)]).label == "leaf_spot"


def test_unsure_problem_does_not_override_healthy():
    assert combine_health([_tr("healthy", 0.8), _tr("leaf_spot", 0.4)]).label == "healthy"


def test_stage_is_averaged():
    labels = ("blooming", "dormant")
    r = combine_average([_tr("blooming", 0.9, labels), _tr("dormant", 0.6, labels)])
    assert r.label == "blooming" and abs(r.confidence - 0.65) < 1e-6


from hydrangea.config import PLANTS


def test_every_plant_renders_in_every_language():
    for lang in LANGS:
        for plant in [*PLANTS, "unknown"]:
            for stage in ["budding", "blooming", "fading_blooms", "fruiting", "dormant", "unknown"]:
                for month in range(1, 13):
                    r = advise("healthy", stage, "unknown", month, plant=plant, age_years=10, height_cm=100).render(lang)
                    assert r["headline"] and "{" not in r["headline"] + r["how_far"] + "".join(r["notes"])


def test_apricot_never_in_winter():
    a = advise("healthy", "dormant", "unknown", 1, plant="apricot")
    assert a.trim_now == "no" and any("winter" in n for n in a.render()["notes"])


def test_apricot_after_harvest():
    assert advise("healthy", "fruiting", "unknown", 7, plant="apricot").trim_now == "yes"


def test_apple_late_winter():
    assert advise("healthy", "dormant", "unknown", 2, plant="apple").trim_now == "yes"


def test_grape_autumn_after_leaf_fall():
    assert advise("healthy", "dormant", "unknown", 10, plant="grape").trim_now == "yes"


def test_peony_cut_down_in_autumn():
    assert advise("healthy", "dormant", "unknown", 10, plant="peony").trim_now == "yes"


def test_lilac_after_flowering_not_winter():
    assert advise("healthy", "fading_blooms", "unknown", 6, plant="lilac").trim_now == "yes"
    assert advise("healthy", "dormant", "unknown", 12, plant="lilac").trim_now == "no"


def test_no_renewal_advice_for_trees():
    a = advise("healthy", "dormant", "unknown", 2, plant="apple", age_years=20)
    assert not any("oldest" in n for n in a.render()["notes"])


def test_sick_tree_still_gets_disease_advice():
    assert advise("wilting", "fruiting", "unknown", 7, plant="cherry").trim_now == "no"


def test_zeroshot_disease_needs_high_confidence():
    from hydrangea.predict import _doubt
    assert _doubt("health", _tr("leaf_spot", 0.6)).unsure
    assert not _doubt("health", _tr("leaf_spot", 0.8)).unsure
    assert not _doubt("health", _tr("healthy", 0.6)).unsure
