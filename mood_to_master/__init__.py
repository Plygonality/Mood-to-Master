"""Maps generator moods and tags onto Master Node category, preset IDs, and socket deltas.

Output is a value map Plygon-mcp can set_param. Artists still look-dev in the N-panel.
"""

from mood_to_master.apply import set_param_map, to_live_script
from mood_to_master.map import FORMAT, FORMAT_VERSION, Look, generate_and_map, map_concept, map_look
from mood_to_master.rules import MOODS

__all__ = [
    "FORMAT",
    "FORMAT_VERSION",
    "MOODS",
    "Look",
    "generate_and_map",
    "map_concept",
    "map_look",
    "set_param_map",
    "to_live_script",
]

__version__ = "0.1.0"
