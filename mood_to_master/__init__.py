"""Map Hard Sci-Fi Idea Generator moods/tags onto Master-Node value maps.

The product is the look record. Plygon-mcp binds the category, set_param each
socket, and screenshots the viewport. Artists still look-dev in the N-panel.
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
