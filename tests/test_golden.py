from __future__ import annotations

import json
import os
from pathlib import Path

from mood_to_master import map_look

GOLDEN = Path(__file__).resolve().parent / "goldens" / "desolate_oxidized_derelict.json"


def _canonical():
    return map_look(
        moods=["desolate"],
        tags=["derelict"],
        palette="oxidized copper, rust, and deep shadow",
        lighting="harsh, unfiltered starlight raking across bare metal",
        composition="a debris-field foreground framing the structure beyond",
    )


def test_canonical_golden() -> None:
    GOLDEN.parent.mkdir(exist_ok=True)
    got = _canonical().dumps()
    if os.environ.get("UPDATE_GOLDENS") == "1":
        GOLDEN.write_text(got, encoding="utf-8")
    expected = GOLDEN.read_text(encoding="utf-8")
    assert got == expected, (
        "canonical look drifted from golden. "
        "Re-run with UPDATE_GOLDENS=1 if the change is intended."
    )


def test_golden_is_json_value_map() -> None:
    data = json.loads(GOLDEN.read_text(encoding="utf-8"))
    assert data["format"] == "mood-to-master"
    assert data["category"] == "metal"
    assert data["preset"] == "metal.brushed_aluminum"
    assert "Color" in data["values"]
    assert "Roughness" in data["values"]
