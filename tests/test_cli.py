from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from mood_to_master.apply import set_param_map, to_live_script
from mood_to_master.map import map_look

ROOT = Path(__file__).resolve().parents[1]


def test_cli_full_brief_matches_golden() -> None:
    golden = json.loads(
        (Path(__file__).resolve().parent / "goldens" / "desolate_oxidized_derelict.json").read_text()
    )
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "mood_to_master",
            "--mood",
            "desolate",
            "--tag",
            "derelict",
            "--palette",
            "oxidized copper, rust, and deep shadow",
            "--lighting",
            "harsh, unfiltered starlight raking across bare metal",
            "--composition",
            "a debris-field foreground framing the structure beyond",
        ],
        check=True,
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    assert json.loads(proc.stdout) == golden


def test_cli_canonical_json() -> None:
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "mood_to_master",
            "--mood",
            "desolate",
            "--tag",
            "derelict",
            "--palette",
            "oxidized copper, rust, and deep shadow",
        ],
        check=True,
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    data = json.loads(proc.stdout)
    assert data["category"] == "metal"
    assert data["preset"] == "metal.brushed_aluminum"
    assert data["values"]["Roughness"] >= 0.6


def test_cli_plain_is_values_only() -> None:
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "mood_to_master",
            "--mood",
            "desolate",
            "--tag",
            "derelict",
            "--palette",
            "oxidized copper, rust, and deep shadow",
            "--plain",
        ],
        check=True,
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    data = json.loads(proc.stdout)
    assert "category" not in data
    assert "Color" in data
    assert "Roughness" in data


def test_cli_script_calls_set_param() -> None:
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "mood_to_master",
            "--mood",
            "desolate",
            "--tag",
            "derelict",
            "--palette",
            "oxidized copper, rust, and deep shadow",
            "--script",
        ],
        check=True,
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    assert "live.bind_category" in proc.stdout
    assert "live.set_param" in proc.stdout
    assert "LOOK" in proc.stdout


def test_live_script_contains_value_map() -> None:
    look = map_look(
        moods=["desolate"],
        tags=["derelict"],
        palette="oxidized copper, rust, and deep shadow",
    )
    script = to_live_script(look)
    assert "bind_category" in script
    assert "set_param" in script
    assert look.category in script
    values = set_param_map(look)
    assert values == look.values
    assert "Roughness" in values
