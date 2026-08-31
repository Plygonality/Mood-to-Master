"""Self-contained bpy script for the live Blender loop.

Hard-SciFi-idea-generator → Mood-to-Master → Master-Node → Plygon-mcp screenshot.

Plygon-mcp: execute_blender_code(this) → get_viewport_screenshot().

Binds the mapped category on the active object (or a cube) and writes every
socket through ``set_param``.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mood_to_master import map_look, to_live_script  # noqa: E402

CANONICAL = map_look(
    moods=["desolate"],
    tags=["derelict"],
    palette="oxidized copper, rust, and deep shadow",
    lighting="harsh, unfiltered starlight raking across bare metal",
    composition="a debris-field foreground framing the structure beyond",
)


def run():
    """Apply the canonical desolate / oxidized-copper / derelict look."""
    script = to_live_script(CANONICAL)
    ns: dict = {}
    exec(compile(script, "<mood-to-master-live>", "exec"), ns, ns)
    return ns["run"]()


if __name__ == "__main__":
    print(json.dumps(CANONICAL.to_dict(), indent=2))
    try:
        import bpy  # noqa: F401
    except ImportError:
        raise SystemExit(0) from None
    print(run())
