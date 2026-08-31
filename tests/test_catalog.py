from __future__ import annotations

from mood_to_master.catalog import (
    CATEGORIES,
    DEFAULT_PRESET,
    PAID_PRESETS,
    PRESET_CATEGORY,
    PRESETS,
    SOCKETS,
    socket_map,
)


def test_catalog_categories_match_master_node() -> None:
    assert CATEGORIES == (
        "surface",
        "metal",
        "dielectric",
        "glass",
        "fabric",
        "emissive",
        "layered",
    )
    assert set(SOCKETS) == set(CATEGORIES)
    assert set(DEFAULT_PRESET) == set(CATEGORIES)


def test_metal_interface_matches_master_node() -> None:
    names = [spec.name for spec in SOCKETS["metal"]]
    assert names == [
        "Color",
        "Roughness",
        "Anisotropy",
        "Rotation",
        "Coat Weight",
        "Coat Roughness",
    ]
    roughness = socket_map("metal")["Roughness"]
    assert roughness.min == 0.0
    assert roughness.max == 1.0


def test_every_preset_belongs_to_its_category() -> None:
    for preset_id, values in PRESETS.items():
        category = PRESET_CATEGORY[preset_id]
        allowed = set(socket_map(category))
        assert set(values) <= allowed, preset_id


def test_paid_presets_are_known_categories() -> None:
    assert PAID_PRESETS
    assert all(cat in CATEGORIES for cat in PAID_PRESETS.values())
