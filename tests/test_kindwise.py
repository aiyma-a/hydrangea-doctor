import pytest

from hydrangea import kindwise, pruning
from hydrangea.i18n import LANGS, MESSAGES


def reply(name, p=0.7, plant=0.99):
    return {"result": {"is_plant": {"probability": plant}, "classification": {"suggestions": [{"name": name, "probability": p}]}}}


def test_hydrangea_kinds_map_to_our_rules():
    assert kindwise.map_name("Hydrangea paniculata") == ("hydrangea", "panicle")
    assert kindwise.map_name("Hydrangea arborescens") == ("hydrangea", "smooth")
    assert kindwise.map_name("Hydrangea macrophylla") == ("hydrangea", "bigleaf")
    assert kindwise.map_name("Hydrangea quercifolia") == ("hydrangea", "oakleaf")
    assert kindwise.map_name("Hydrangea serrata") == ("hydrangea", None)  # a hydrangea, but no rule for the kind


def test_other_plants_and_unknowns():
    assert kindwise.map_name("Prunus armeniaca") == ("apricot", None)
    assert kindwise.map_name("Prunus laurocerasus") == (None, None)  # not one of ours
    assert kindwise.map_name("Rubus idaeus") == ("raspberry", None)
    assert kindwise.map_name("Viburnum rhytidophyllum") == (None, None)
    assert kindwise.map_name("") == (None, None)


def test_parse_confidence_levels_and_refusals():
    assert kindwise.parse(reply("Hydrangea paniculata", 0.83))["confidence"] == "high"
    assert kindwise.parse(reply("Hydrangea paniculata", 0.45))["confidence"] == "medium"
    assert kindwise.parse(reply("Hydrangea paniculata", 0.2))["confidence"] == "low"
    assert kindwise.parse(reply("Hydrangea paniculata", 0.9, plant=0.1)) is None  # not a plant
    assert kindwise.parse(reply("Viburnum rhytidophyllum")) is None  # not supported: Gemini decides


def test_no_key_is_unavailable(monkeypatch):
    monkeypatch.delenv("KINDWISE_API_KEY", raising=False)
    with pytest.raises(kindwise.Unavailable):
        kindwise.identify([b"x"])


def test_variety_adds_a_size_note_only_when_it_fits():
    notes = lambda **kw: [n.key for n in pruning.advise("healthy", "dormant", kw.pop("species"), 2, **kw).notes]
    assert "variety_bobo" in notes(species="panicle", variety="bobo")
    assert "variety_annabelle" in notes(species="smooth", variety="annabelle")
    assert "variety_bobo" not in notes(species="smooth", variety="bobo")  # the variety belongs to another kind
    assert "variety_bobo" not in notes(species="panicle")
    assert "variety_limelight" not in [n.key for n in pruning.advise("healthy", "blooming", "panicle", 7, variety="limelight").notes]  # nothing to cut now


def test_every_variety_has_text_in_every_language():
    for lang in LANGS:
        for v in pruning.VARIETIES:
            assert f"variety_{v}" in MESSAGES[lang]
