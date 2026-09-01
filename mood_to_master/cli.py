"""CLI: mood/tags in, Master-Node value map out."""

from __future__ import annotations

import argparse
import json
import sys

from mood_to_master.apply import to_live_script
from mood_to_master.map import generate_and_map, map_look
from mood_to_master.rules import MOODS


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Maps generator moods and tags onto Master Node category, preset IDs, "
            "and socket deltas. Output is a value map MCP can set_param."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "examples:\n"
            "  python -m mood_to_master --mood desolate --tag derelict "
            '--palette "oxidized copper, rust, and deep shadow"\n'
            "  python -m mood_to_master --seed 1234 --mood desolate --script\n"
        ),
    )
    parser.add_argument(
        "--mood",
        action="append",
        default=[],
        choices=sorted(MOODS),
        help="generator mood (repeatable)",
    )
    parser.add_argument(
        "--tag",
        action="append",
        default=[],
        metavar="TAG",
        help="generator tag such as derelict (repeatable)",
    )
    parser.add_argument("--palette", default="", help="palette line from the generator brief")
    parser.add_argument("--lighting", default="", help="lighting line from the generator brief")
    parser.add_argument(
        "--composition", default="", help="composition line from the generator brief"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="run Hard-SciFi-idea-generator with this seed, then map",
    )
    parser.add_argument(
        "--require",
        action="append",
        default=[],
        metavar="TAG",
        help="with --seed: require a generator tag (repeatable)",
    )
    parser.add_argument(
        "--avoid",
        action="append",
        default=[],
        metavar="TAG",
        help="with --seed: exclude a generator tag (repeatable)",
    )
    parser.add_argument(
        "--script",
        action="store_true",
        help="print a self-contained Blender live script instead of JSON",
    )
    parser.add_argument(
        "--plain",
        action="store_true",
        help="print only the values object (the set_param map)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.seed is not None:
        try:
            look, _concept = generate_and_map(
                args.seed,
                require=args.require,
                avoid=args.avoid,
                mood=args.mood,
            )
        except Exception as err:
            print(f"error: {err}", file=sys.stderr)
            return 1
    else:
        look = map_look(
            moods=args.mood,
            tags=args.tag,
            palette=args.palette,
            lighting=args.lighting,
            composition=args.composition,
        )

    if args.script:
        sys.stdout.write(to_live_script(look))
        return 0

    payload = look.to_dict()
    if args.plain:
        payload = payload["values"]
    json.dump(payload, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0
