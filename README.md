# Mood to Master

Maps [Hard Sci-Fi Idea Generator](https://github.com/Plygonality/Hard-SciFi-idea-generator) moods and tags onto [Master Node](https://github.com/Plygonality/Master-Node) category + preset IDs + socket deltas.

**Output is a value map** [Plygon-mcp](https://github.com/Plygonality/Plygon-mcp) can `set_param`.

```
Hard-SciFi-idea-generator  →  Mood-to-Master  →  Master-Node  →  Plygon-mcp screenshot
     tags / palette              value map         bind + set_param      viewport
```

The canonical brief from the generator — *desolate*, *oxidized copper*, *derelict* — binds **MN Metal**, starts from free preset `metal.brushed_aluminum`, hints paid `metal.aged_brass`, and writes a darker, rougher copper value map.

<p>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-ff6a1a?style=flat-square" alt="MIT"></a>
  <img src="https://img.shields.io/badge/python-3.10%2B-111111?style=flat-square" alt="Python 3.10+">
</p>

## Why this repo exists

The generator produces a production brief: mood, palette line, fragment tags. Master Node is a category master with RNA sliders. Nothing in either repo knows the other.

This library is the join. It does not open Blender. It does not ship paid preset values. It votes a category, picks a free preset as the base, applies socket deltas, and emits the map the agent writes through `set_param`.

| Role | Job |
|---|---|
| **Hard-SciFi-idea-generator** | Coherent megastructure brief (mood, tags, palette) |
| **This library** | Category + preset IDs + socket value map |
| **Master Node** | Bind the category master, expose the sockets |
| **Plygon-mcp** | `set_param` each socket, screenshot the viewport |
| **The `.blend`** | Working cache, never the source of truth |

## Install

```bash
pip install -e ".[dev]"
```

Python 3.10+. No Blender. No third-party runtime deps.

## Quick demo

```bash
python -m mood_to_master \
  --mood desolate \
  --tag derelict \
  --palette "oxidized copper, rust, and deep shadow" \
  --lighting "harsh, unfiltered starlight raking across bare metal" \
  --composition "a debris-field foreground framing the structure beyond"
```

```json
{
  "format": "mood-to-master",
  "version": 1,
  "category": "metal",
  "preset": "metal.brushed_aluminum",
  "paid_preset": "metal.aged_brass",
  "hits": [
    "desolate",
    "derelict",
    "oxidized copper",
    "deep shadow",
    "rust",
    "starlight",
    "bare metal",
    "debris-field"
  ],
  "deltas": {
    "Roughness": 0.66,
    "Coat Weight": -0.35,
    "Anisotropy": -0.45,
    "darken": 0.42
  },
  "values": {
    "Color": [0.248986, 0.114032, 0.05365, 1.0],
    "Roughness": 0.94,
    "Anisotropy": 0.2,
    "Rotation": 0.0,
    "Coat Weight": 0.0,
    "Coat Roughness": 0.03
  }
}
```

`--plain` prints only `values` — the object MCP iterates for `set_param`. `--script` prints a self-contained bpy script.

```python
from mood_to_master import map_look, to_live_script

look = map_look(
    moods=["desolate"],
    tags=["derelict"],
    palette="oxidized copper, rust, and deep shadow",
    lighting="harsh, unfiltered starlight raking across bare metal",
    composition="a debris-field foreground framing the structure beyond",
)
# look.values  →  live.set_param(name, value) for each socket
script = to_live_script(look)
# Plygon-mcp: execute_blender_code(script) → get_viewport_screenshot()
```

A generator `Concept` (Fragment dict or `{text, tags}` mappings) maps the same way:

```python
from mood_to_master import map_concept

look = map_concept(concept)
```

If the generator package is installed, one seed is enough:

```bash
python -m mood_to_master --seed 1234 --mood desolate
```

## What gets mapped

| Input | Source | Effect |
|---|---|---|
| Mood | `desolate` `sublime` `menacing` `melancholy` `uncanny` | Category votes + roughness / coat / emission deltas |
| Tags | `derelict` `abandoned` `constructing` … | Same, biased toward metal for wrecks |
| Palette line | e.g. *oxidized copper, rust, and deep shadow* | Color + category + free/paid preset bias |
| Lighting / composition | optional brief lines | Emission / extra roughness |

Free preset IDs (`metal.brushed_aluminum`, `emissive.neon`, …) are the values that actually apply. Paid IDs (`metal.aged_brass`, `metal.galvanized`, …) are hints for the panel; this library never ships paid packs.

Socket names track Master Node 0.1.0 (`Color`, `Roughness`, `Anisotropy` on metal; `Strength` on emissive; `Base Roughness` on layered). Floats clamp to the catalog min/max.

## Cursor / live loop

The product is the JSON map. The agent loop is optional.

```python
from master_node.live import bind_category, set_param
from mood_to_master import map_look

look = map_look(
    moods=["desolate"],
    tags=["derelict"],
    palette="oxidized copper, rust, and deep shadow",
    lighting="harsh, unfiltered starlight raking across bare metal",
    composition="a debris-field foreground framing the structure beyond",
)
bind_category(look.category)
for name, value in look.values.items():
    set_param(name, value)
```

Or run the self-contained script through Plygon-mcp:

```
execute_blender_code(python -m mood_to_master --mood desolate --tag derelict --palette "oxidized copper, rust, and deep shadow" --lighting "harsh, unfiltered starlight raking across bare metal" --composition "a debris-field foreground framing the structure beyond" --script)
get_viewport_screenshot()
```

`scripts/live_loop.py` embeds the canonical desolate / oxidized-copper / derelict look.

## Tests

No Blender required.

```bash
pip install -e ".[dev]"
pytest -q
```

```bash
UPDATE_GOLDENS=1 pytest tests/test_golden.py   # rewrite the canonical value map
```

## Repo map

| Path | What |
|---|---|
| `mood_to_master/catalog.py` | Frozen Master-Node sockets + free presets |
| `mood_to_master/rules.py` | Mood / tag / palette / lighting hits |
| `mood_to_master/map.py` | Vote category, pick preset, apply deltas |
| `mood_to_master/apply.py` | `set_param` map + bpy live script |
| `scripts/live_loop.py` | Agent: canonical look → bind → set_param |
| `tests/goldens/` | Canonical value-map fixture |

[github.com/Plygonality/Mood-to-Master](https://github.com/Plygonality/Mood-to-Master)
