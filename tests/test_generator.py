from __future__ import annotations

import pytest
from mood_to_master.catalog import CATEGORIES
from mood_to_master.map import generate_and_map, map_concept

pytest.importorskip("hard_scifi_idea_generator")


def test_generate_and_map_desolate_seed() -> None:
    look, concept = generate_and_map(1234, mood=["desolate"])
    assert look.category in CATEGORIES
    assert look.preset.split(".", 1)[0] == look.category
    assert set(look.values)
    mapped = map_concept(concept)
    assert mapped.to_dict() == look.to_dict()
    tags = set().union(*(frag.tags for frag in concept.values()))
    assert "desolate" in tags
