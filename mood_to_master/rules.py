"""Mood, tag, palette, and lighting rules.

Inputs are the generator's mood vocabulary, fragment tags, and art-direction
strings (palette / lighting / composition). Outputs are category votes, preset
bias, a palette color, and logical socket deltas that the mapper applies to a
Master-Node free preset.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

MOODS = frozenset({"desolate", "sublime", "menacing", "melancholy", "uncanny"})

Color = tuple[float, float, float, float]


@dataclass(frozen=True)
class Hit:
    """One matched token and the look it argues for."""

    name: str
    category_votes: dict[str, int] = field(default_factory=dict)
    preset_bias: dict[str, int] = field(default_factory=dict)
    paid_bias: dict[str, int] = field(default_factory=dict)
    color: Color | None = None
    color_weight: float = 1.0
    deltas: dict[str, float] = field(default_factory=dict)


def _mood(
    name: str,
    votes: dict[str, int],
    *,
    presets: dict[str, int] | None = None,
    paid: dict[str, int] | None = None,
    deltas: dict[str, float] | None = None,
) -> Hit:
    return Hit(
        name=name,
        category_votes=votes,
        preset_bias=presets or {},
        paid_bias=paid or {},
        deltas=deltas or {},
    )


def _swatch(
    name: str,
    color: Color,
    votes: dict[str, int],
    *,
    presets: dict[str, int] | None = None,
    paid: dict[str, int] | None = None,
    deltas: dict[str, float] | None = None,
    weight: float = 1.0,
) -> Hit:
    return Hit(
        name=name,
        category_votes=votes,
        preset_bias=presets or {},
        paid_bias=paid or {},
        color=color,
        color_weight=weight,
        deltas=deltas or {},
    )


# Moods from hard_scifi_idea_generator.MOODS
MOOD_HITS: dict[str, Hit] = {
    "desolate": _mood(
        "desolate",
        {"metal": 2, "dielectric": 1, "surface": 1},
        presets={"metal.brushed_aluminum": 3, "dielectric.rubber": 1, "surface.matte_clay": 1},
        paid={"metal.galvanized": 1, "metal.aged_brass": 1},
        deltas={"roughness": 0.28, "coat": -0.15, "anisotropy": -0.2, "darken": 0.18},
    ),
    "sublime": _mood(
        "sublime",
        {"glass": 2, "metal": 1, "layered": 1},
        presets={"metal.chrome": 2, "glass.clear": 2, "layered.lacquer": 1},
        deltas={"roughness": -0.12, "coat": 0.2},
    ),
    "menacing": _mood(
        "menacing",
        {"metal": 2, "emissive": 1, "layered": 1},
        presets={"metal.chrome": 1, "emissive.neon": 1, "layered.car_paint": 1},
        deltas={"roughness": 0.08, "darken": 0.25, "emission": 6.0},
    ),
    "melancholy": _mood(
        "melancholy",
        {"dielectric": 2, "fabric": 1, "metal": 1},
        presets={
            "dielectric.rubber": 1,
            "metal.brushed_aluminum": 1,
            "fabric.cotton": 1,
        },
        deltas={"roughness": 0.18, "desaturate": 0.25, "sheen": -0.1, "darken": 0.08},
    ),
    "uncanny": _mood(
        "uncanny",
        {"emissive": 2, "glass": 1, "layered": 1},
        presets={"emissive.neon": 2, "glass.frosted": 1, "layered.lacquer": 1},
        paid={"glass.thin_film": 2},
        deltas={"coat": 0.15, "emission": 8.0, "roughness": 0.05},
    ),
}

# Narrative / state tags from the generator pools.
TAG_HITS: dict[str, Hit] = {
    "derelict": _mood(
        "derelict",
        {"metal": 3, "dielectric": 1},
        presets={"metal.brushed_aluminum": 3},
        paid={"metal.galvanized": 2, "metal.aged_brass": 1},
        deltas={"roughness": 0.22, "coat": -0.2, "anisotropy": -0.25, "darken": 0.12},
    ),
    "abandoned": _mood(
        "abandoned",
        {"metal": 2, "dielectric": 1},
        presets={"metal.brushed_aluminum": 2, "dielectric.rubber": 1},
        paid={"metal.galvanized": 1},
        deltas={"roughness": 0.18, "darken": 0.1, "coat": -0.1},
    ),
    "uninhabited": _mood(
        "uninhabited",
        {"metal": 1},
        deltas={"roughness": 0.1, "darken": 0.06},
    ),
    "deconstructing": _mood(
        "deconstructing",
        {"metal": 2},
        presets={"metal.brushed_aluminum": 2},
        deltas={"roughness": 0.2, "anisotropy": -0.1},
    ),
    "constructing": _mood(
        "constructing",
        {"metal": 2},
        presets={"metal.chrome": 1, "metal.brushed_aluminum": 1},
        deltas={"roughness": -0.08},
    ),
    "active": _mood(
        "active",
        {"metal": 1, "emissive": 1},
        presets={"emissive.warm_led": 1, "metal.chrome": 1},
        deltas={"roughness": -0.06, "emission": 4.0},
    ),
    "contested": _mood(
        "contested",
        {"metal": 1, "layered": 1},
        deltas={"roughness": 0.06},
    ),
    "synthetic": _mood(
        "synthetic",
        {"metal": 1, "emissive": 1},
        presets={"metal.chrome": 1, "emissive.neon": 1},
    ),
    "organic": _mood(
        "organic",
        {"fabric": 2, "dielectric": 1},
        presets={"fabric.cotton": 2, "dielectric.rubber": 1},
        paid={"fabric.silk": 1},
        deltas={"sheen": 0.15},
    ),
    "posthuman": _mood(
        "posthuman",
        {"emissive": 1, "metal": 1},
        presets={"emissive.neon": 1},
    ),
    "singularity": _mood(
        "singularity",
        {"emissive": 2, "layered": 1},
        presets={"emissive.neon": 2},
        deltas={"emission": 24.0, "darken": 0.2},
    ),
    "exotic_matter": _mood(
        "exotic_matter",
        {"glass": 2, "layered": 1},
        presets={"glass.clear": 1, "layered.lacquer": 1},
        paid={"glass.thin_film": 2},
        deltas={"transmission": 0.0, "coat": 0.25},
    ),
    "anomaly": _mood(
        "anomaly",
        {"emissive": 1, "glass": 1},
        presets={"emissive.neon": 1, "glass.frosted": 1},
        deltas={"emission": 8.0},
    ),
    "simulation": _mood(
        "simulation",
        {"emissive": 2, "glass": 1},
        presets={"emissive.neon": 2},
        deltas={"emission": 12.0},
    ),
    "orbital": _mood("orbital", {"metal": 1}),
    "stellar": _mood(
        "stellar",
        {"metal": 1, "emissive": 1},
        deltas={"emission": 3.0},
    ),
    "black_hole": _mood(
        "black_hole",
        {"layered": 2, "metal": 1},
        presets={"layered.car_paint": 2, "metal.chrome": 1},
        deltas={"darken": 0.4, "metallic": 0.2},
    ),
    "planetary": _mood("planetary", {"dielectric": 1, "metal": 1}),
    "interstellar": _mood("interstellar", {"metal": 1}),
}

# Palette fragment keywords. Longer phrases first — matcher uses this order.
PALETTE_HITS: tuple[Hit, ...] = (
    _swatch(
        "oxidized copper",
        (0.46, 0.24, 0.12, 1.0),
        {"metal": 4},
        presets={"metal.brushed_aluminum": 4},
        paid={"metal.aged_brass": 4},
        weight=3.0,
    ),
    _swatch(
        "phosphor green",
        (0.18, 1.0, 0.32, 1.0),
        {"emissive": 4},
        presets={"emissive.neon": 4},
        weight=2.5,
    ),
    _swatch(
        "ember-orange",
        (1.0, 0.32, 0.06, 1.0),
        {"emissive": 3, "metal": 1},
        presets={"emissive.warm_led": 3},
        weight=2.0,
    ),
    _swatch(
        "sterile white",
        (0.92, 0.93, 0.95, 1.0),
        {"metal": 2, "glass": 1},
        presets={"metal.chrome": 2, "glass.clear": 1},
    ),
    _swatch(
        "molten gold",
        (0.83, 0.55, 0.12, 1.0),
        {"metal": 3, "emissive": 1},
        presets={"metal.chrome": 2},
        paid={"metal.aged_brass": 3},
        weight=2.0,
    ),
    _swatch(
        "oil-slick",
        (0.06, 0.1, 0.08, 1.0),
        {"layered": 3, "glass": 1},
        presets={"layered.lacquer": 2, "glass.frosted": 1},
        paid={"glass.thin_film": 3, "layered.wet_asphalt": 1},
        deltas={"coat": 0.2, "metallic": 0.25},
        weight=2.0,
    ),
    _swatch(
        "corroded teal",
        (0.16, 0.38, 0.34, 1.0),
        {"metal": 3},
        presets={"metal.brushed_aluminum": 3},
        paid={"metal.galvanized": 2},
        deltas={"roughness": 0.12},
        weight=2.0,
    ),
    _swatch(
        "faded ochre",
        (0.55, 0.38, 0.16, 1.0),
        {"dielectric": 2, "metal": 1},
        presets={"dielectric.rubber": 2},
    ),
    _swatch(
        "bone-white",
        (0.86, 0.82, 0.74, 1.0),
        {"dielectric": 2, "fabric": 1},
        presets={"dielectric.hard_plastic": 2, "fabric.cotton": 1},
    ),
    _swatch(
        "ash-grey",
        (0.34, 0.34, 0.35, 1.0),
        {"dielectric": 2, "metal": 1},
        presets={"dielectric.rubber": 2, "metal.brushed_aluminum": 1},
    ),
    _swatch(
        "ice-blue",
        (0.55, 0.72, 0.82, 1.0),
        {"metal": 2, "glass": 1},
        presets={"metal.chrome": 2},
        paid={"metal.anodized_blue": 3},
    ),
    _swatch(
        "deep shadow",
        (0.04, 0.035, 0.03, 1.0),
        {"metal": 1, "layered": 1},
        deltas={"darken": 0.12},
        weight=0.6,
    ),
    _swatch(
        "gunmetal",
        (0.22, 0.25, 0.28, 1.0),
        {"metal": 3},
        presets={"metal.brushed_aluminum": 3},
        paid={"metal.galvanized": 3},
        weight=2.0,
    ),
    _swatch(
        "obsidian",
        (0.02, 0.02, 0.025, 1.0),
        {"layered": 3, "metal": 1},
        presets={"layered.car_paint": 2, "metal.chrome": 1},
        deltas={"darken": 0.15, "metallic": 0.2},
        weight=2.0,
    ),
    _swatch(
        "iridescent",
        (0.35, 0.55, 0.62, 1.0),
        {"glass": 2, "layered": 2},
        presets={"glass.frosted": 1, "layered.lacquer": 1},
        paid={"glass.thin_film": 3},
        deltas={"coat": 0.15},
        weight=1.2,
    ),
    _swatch(
        "earth tones",
        (0.32, 0.24, 0.16, 1.0),
        {"dielectric": 2, "fabric": 1},
        presets={"dielectric.rubber": 2, "fabric.cotton": 1},
    ),
    _swatch(
        "silver",
        (0.9, 0.91, 0.93, 1.0),
        {"metal": 3},
        presets={"metal.chrome": 4},
        weight=2.0,
    ),
    _swatch(
        "crimson",
        (0.42, 0.04, 0.035, 1.0),
        {"metal": 2, "layered": 1},
        presets={"layered.car_paint": 2, "metal.chrome": 1},
        weight=1.5,
    ),
    _swatch(
        "carbon",
        (0.04, 0.04, 0.045, 1.0),
        {"dielectric": 2, "layered": 1},
        presets={"dielectric.hard_plastic": 2, "layered.car_paint": 1},
        deltas={"roughness": 0.1},
    ),
    _swatch(
        "rust",
        (0.5, 0.18, 0.07, 1.0),
        {"metal": 3},
        presets={"metal.brushed_aluminum": 3},
        paid={"metal.galvanized": 2, "metal.aged_brass": 1},
        deltas={"roughness": 0.1},
        weight=2.0,
    ),
    _swatch(
        "char",
        (0.07, 0.06, 0.055, 1.0),
        {"metal": 2, "dielectric": 1},
        presets={"metal.brushed_aluminum": 1, "dielectric.rubber": 1},
        deltas={"darken": 0.1},
    ),
    _swatch(
        "violet",
        (0.32, 0.14, 0.55, 1.0),
        {"glass": 2, "emissive": 1},
        presets={"glass.clear": 1, "emissive.neon": 1},
    ),
    _swatch(
        "teal",
        (0.12, 0.48, 0.46, 1.0),
        {"glass": 2, "metal": 1},
        presets={"glass.clear": 2},
        paid={"glass.smoked": 1},
    ),
    _swatch(
        "glass",
        (0.95, 0.97, 0.98, 1.0),
        {"glass": 3},
        presets={"glass.clear": 3},
        weight=1.5,
    ),
)

PALETTE_HITS = tuple(sorted(PALETTE_HITS, key=lambda hit: (-len(hit.name), hit.name)))

LIGHTING_HITS: tuple[Hit, ...] = (
    _mood(
        "emergency lighting",
        {"emissive": 3},
        presets={"emissive.neon": 3},
        deltas={"emission": 10.0},
    ),
    _mood(
        "bioluminescence",
        {"emissive": 3},
        presets={"emissive.neon": 2},
        deltas={"emission": 8.0},
    ),
    _mood(
        "holographic",
        {"emissive": 3},
        presets={"emissive.neon": 3},
        deltas={"emission": 16.0},
    ),
    _mood(
        "fusion",
        {"emissive": 2, "metal": 1},
        presets={"emissive.warm_led": 2},
        deltas={"emission": 36.0},
    ),
    _mood(
        "worklights",
        {"emissive": 1, "metal": 1},
        presets={"emissive.warm_led": 2},
        deltas={"emission": 6.0},
    ),
    _mood(
        "dying star",
        {"emissive": 1, "metal": 1},
        presets={"emissive.warm_led": 2},
        deltas={"emission": 8.0, "darken": 0.08},
    ),
    _mood(
        "starlight",
        {"metal": 2},
        presets={"metal.brushed_aluminum": 1, "metal.chrome": 1},
    ),
    _mood(
        "bare metal",
        {"metal": 2},
        presets={"metal.brushed_aluminum": 2},
    ),
    _mood(
        "god-rays",
        {"glass": 1, "emissive": 1},
        presets={"glass.clear": 1},
        deltas={"transmission": 0.0},
    ),
    _mood("caustics", {"glass": 2}, presets={"glass.clear": 2}),
    _mood("rim light", {"metal": 1, "layered": 1}, deltas={"coat": 0.05}),
)

COMPOSITION_HITS: tuple[Hit, ...] = (
    _mood(
        "debris-field",
        {"metal": 1},
        presets={"metal.brushed_aluminum": 1},
        deltas={"roughness": 0.06},
    ),
    _mood("tumbling spacesuit", {"dielectric": 1, "fabric": 1}),
    _mood("sacred", {"glass": 1, "layered": 1}, deltas={"coat": 0.08}),
    _mood("corridor", {"metal": 1, "emissive": 1}),
)


def collect_hits(
    *,
    moods: Any = (),
    tags: Any = (),
    palette: str = "",
    lighting: str = "",
    composition: str = "",
) -> list[Hit]:
    """Resolve every matching rule for a brief."""
    mood_set = {str(m).strip().lower() for m in moods if str(m).strip()}
    tag_set = {str(t).strip().lower() for t in tags if str(t).strip()}
    # Generator --mood implies the tag; treat moods as tags too.
    tag_set |= mood_set

    hits: list[Hit] = []
    seen: set[str] = set()

    def _add(hit: Hit) -> None:
        if hit.name in seen:
            return
        seen.add(hit.name)
        hits.append(hit)

    for mood in sorted(mood_set & MOODS):
        _add(MOOD_HITS[mood])
    for tag in sorted(tag_set):
        if tag in MOODS:
            continue
        rule = TAG_HITS.get(tag)
        if rule is not None:
            _add(rule)

    palette_text = palette.lower()
    for rule in PALETTE_HITS:
        if rule.name in palette_text:
            _add(rule)

    light_text = lighting.lower()
    for rule in LIGHTING_HITS:
        if rule.name in light_text:
            _add(rule)

    comp_text = composition.lower()
    for rule in COMPOSITION_HITS:
        if rule.name in comp_text:
            _add(rule)

    return hits
