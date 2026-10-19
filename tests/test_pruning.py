from hydrangea.pruning import advise, season
from hydrangea.train import plant_id
from hydrangea.weather import Weather, summarize
from pathlib import Path


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
    assert a.trim_now == "yes" and "50 cm" in a.how_far


def test_bigleaf_not_cut_in_autumn():
    assert advise("healthy", "fading_blooms", "bigleaf", 10).trim_now == "light"
    assert advise("healthy", "dormant", "bigleaf", 11).trim_now == "no"


def test_bigleaf_cut_after_flowering_in_summer():
    assert advise("healthy", "fading_blooms", "bigleaf", 7).trim_now == "yes"


def test_frost_blocks_late_summer_cut():
    a = advise("healthy", "fading_blooms", "bigleaf", 8, weather=w(frost=True))
    assert a.trim_now == "no" and "Frost" in a.notes[0]


def test_weather_sets_hemisphere():
    # February in Sydney is summer: no main prune for panicle
    assert advise("healthy", "blooming", "panicle", 2, weather=w(lat=-33.9)).trim_now == "no"


def test_young_plant_cut_halved():
    a = advise("healthy", "dormant", "panicle", 2, height_cm=150, age_years=1)
    assert a.trim_now == "light" and "25 cm" in a.how_far


def test_old_plant_gets_renewal_note():
    a = advise("healthy", "dormant", "panicle", 2, age_years=10)
    assert any("renewal" in n for n in a.notes)


def test_wilting_hot_dry_says_thirst():
    a = advise("wilting", "blooming", "bigleaf", 7, weather=w(hot_dry=True))
    assert any("thirst" in n for n in a.notes)


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
    assert a.trim_now == "no" and "Couldn't judge health" in a.notes[0]
    assert advise("unknown", "unknown", "panicle", 2).trim_now == "yes"
