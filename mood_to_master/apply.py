"""Turn a Look into MCP-ready set_param payloads and a Blender live script.

Plygon-mcp: execute_blender_code(to_live_script(look)) → get_viewport_screenshot()
"""

from __future__ import annotations

import json

from mood_to_master.map import Look


def set_param_map(look: Look) -> dict[str, object]:
    """Socket → value. Each pair is one ``master_node.live.set_param`` call."""
    return look.to_dict()["values"]


def to_live_script(look: Look) -> str:
    """Self-contained bpy script. Blender does not need this package installed."""
    payload = json.dumps(look.to_dict(), indent=2)
    return (
        '"""Apply a Mood-to-Master look through Master-Node.\n'
        "\n"
        "Plygon-mcp: execute_blender_code(this) → get_viewport_screenshot()\n"
        '"""\n'
        "from __future__ import annotations\n"
        "\n"
        "import json\n"
        "\n"
        "import bpy\n"
        "\n"
        f"LOOK = json.loads({payload!r})\n"
        "\n"
        "\n"
        "def _ensure_object():\n"
        "    obj = bpy.context.object\n"
        '    if obj is not None and obj.type == "MESH":\n'
        "        return obj\n"
        "    bpy.ops.mesh.primitive_cube_add()\n"
        "    return bpy.context.object\n"
        "\n"
        "\n"
        "def run():\n"
        "    _ensure_object()\n"
        "    from master_node import live\n"
        "\n"
        '    dump = live.bind_category(LOOK["category"])\n'
        '    for name, value in LOOK["values"].items():\n'
        "        dump = live.set_param(name, value)\n"
        "    return dump\n"
        "\n"
        "\n"
        'if __name__ == "__main__":\n'
        "    print(run())\n"
    )
