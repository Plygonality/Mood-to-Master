from __future__ import annotations

from mood_to_master.catalog import CATEGORIES, PRESETS, SOCKETS, socket_map
from mood_to_master.map import Look, map_concept, map_look
from mood_to_master.rules import MOODS, PALETTE_HITS

GENERATOR_PALETTES = (
    "oxidized copper, rust, and deep shadow",
    "gunmetal, ice-blue, and sterile white",
    "obsidian black veined with molten gold",
    "bone-white, ash-grey, and faded ochre",
    "an iridescent oil-slick sheen over matte carbon",
    "crimson, char, and ember-orange",
    "teal, violet, and phosphor green",
    "muted earth tones bleeding into corroded teal",
    "high-key silver and glass with pinpoint colour accents",
)


def _assert_valid(look: Look) -> None:
    assert look.category in CATEGORIES
    assert look.preset in PRESETS
    assert look.preset.startswith(look.category + ".")
    sockets = socket_map(look.category)
    assert set(look.values) == set(sockets)
    for name, spec in sockets.items():
        value = look.values[name]
        if spec.kind == "COLOR":
            assert isinstance(value, list) and len(value) == 4
            assert all(0.0 <= c <= 1.0 for c in value)
        else:
            assert isinstance(value, float)
            if spec.min is not None:
                assert value >= spec.min
            if spec.max is not None:
                assert value <= spec.max
    items = look.set_param_items()
    assert [row["name"] for row in items] == [s.name for s in SOCKETS[look.category]]


def test_canonical_desolate_oxidized_derelict() -> None:
    look = map_look(
        moods=["desolate"],
        tags=["derelict"],
        palette="oxidized copper, rust, and deep shadow",
        lighting="harsh, unfiltered starlight raking across bare metal",
        composition="a debris-field foreground framing the structure beyond",
    )
    _assert_valid(look)
    assert look.category == "metal"
    assert look.preset == "metal.brushed_aluminum"
    assert look.paid_preset == "metal.aged_brass"
    assert "desolate" in look.hits
    assert "derelict" in look.hits
    assert "oxidized copper" in look.hits
    color = look.values["Color"]
    assert color[0] > color[1] > color[2]
    assert 0.15 < color[0] < 0.55
    assert look.values["Roughness"] >= 0.6
    assert look.values["Roughness"] <= 1.0
    assert look.values["Anisotropy"] < 0.65
    assert look.values["Coat Weight"] == 0.0


def test_canonical_value_map_is_set_param_ready() -> None:
    look = map_look(
        moods=["desolate"],
        tags=["derelict"],
        palette="oxidized copper, rust, and deep shadow",
    )
    payload = look.to_dict()
    assert payload["format"] == "mood-to-master"
    assert payload["category"] == "metal"
    values = payload["values"]
    assert set(values) == {
        "Color",
        "Roughness",
        "Anisotropy",
        "Rotation",
        "Coat Weight",
        "Coat Roughness",
    }
    for item in look.set_param_items():
        assert item["name"] in values
        assert item["value"] == values[item["name"]]


def test_map_concept_reads_generator_shape() -> None:
    concept = {
        "structure": {
            "text": "a derelict Ringworld segment",
            "tags": ["derelict", "orbital", "stellar", "desolate"],
        },
        "technology": {
            "text": "being deconstructed by self-replicating Von Neumann probes",
            "tags": ["deconstructing", "synthetic"],
        },
        "theme": {
            "text": "built as a monument to a civilization's greatest failure",
            "tags": ["melancholy"],
        },
        "lighting": {
            "text": "harsh, unfiltered starlight raking across bare metal",
            "tags": ["desolate"],
        },
        "palette": {
            "text": "oxidized copper, rust, and deep shadow",
            "tags": ["desolate"],
        },
        "composition": {
            "text": "a debris-field foreground framing the structure beyond",
            "tags": ["desolate"],
        },
    }
    look = map_concept(concept)
    assert look.category == "metal"
    assert look.preset == "metal.brushed_aluminum"
    assert "oxidized copper" in look.hits
    assert look.values["Roughness"] > PRESETS["metal.brushed_aluminum"]["Roughness"]


def test_sublime_silver_glass_prefers_glass_or_chrome() -> None:
    look = map_look(
        moods=["sublime"],
        palette="high-key silver and glass with pinpoint colour accents",
    )
    _assert_valid(look)
    assert look.category in {"glass", "metal"}
    if look.category == "metal":
        assert look.preset == "metal.chrome"
        assert look.values["Roughness"] < 0.2
    else:
        assert look.preset in {"glass.clear", "glass.frosted"}


def test_uncanny_phosphor_goes_emissive() -> None:
    look = map_look(
        moods=["uncanny"],
        palette="teal, violet, and phosphor green",
        lighting="half-corrupted holographic overlays strobing through static",
    )
    _assert_valid(look)
    assert look.category == "emissive"
    assert look.preset == "emissive.neon"
    assert look.values["Strength"] >= 40.0


def test_every_generator_palette_maps() -> None:
    for palette in GENERATOR_PALETTES:
        look = map_look(palette=palette)
        _assert_valid(look)


def test_every_mood_maps() -> None:
    for mood in sorted(MOODS):
        look = map_look(moods=[mood])
        _assert_valid(look)
        assert mood in look.hits


def test_mood_roughness_desolate_vs_sublime() -> None:
    desolate = map_look(moods=["desolate"], tags=["derelict"])
    sublime = map_look(moods=["sublime"])
    _assert_valid(desolate)
    _assert_valid(sublime)
    d_rough = next(v for k, v in desolate.values.items() if "ough" in k)
    s_rough = next(v for k, v in sublime.values.items() if "ough" in k)
    assert d_rough > s_rough


def test_empty_brief_falls_back_to_metal() -> None:
    look = map_look()
    _assert_valid(look)
    assert look.category == "metal"


def test_palette_keywords_are_unique_and_longest_first() -> None:
    names = [hit.name for hit in PALETTE_HITS]
    assert len(names) == len(set(names))
    assert names == sorted(names, key=lambda name: (-len(name), name))
