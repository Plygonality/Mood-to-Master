"""Frozen Master-Node category interfaces and free preset values.

Tracks Master-Node 0.1.0. This package does not import that add-on: tests and
the mapper run without Blender. Socket names and free preset IDs must stay in
lockstep with https://github.com/Plygonality/Master-Node
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

CATEGORIES = (
    "surface",
    "metal",
    "dielectric",
    "glass",
    "fabric",
    "emissive",
    "layered",
)

# Tie-break when category votes draw. Megastructure look-dev leans metal.
CATEGORY_PRIORITY = (
    "metal",
    "layered",
    "emissive",
    "glass",
    "dielectric",
    "fabric",
    "surface",
)


@dataclass(frozen=True)
class SocketSpec:
    name: str
    kind: str
    default: Any
    min: float | None = None
    max: float | None = None


@dataclass(frozen=True)
class Aliases:
    """Logical look knobs → category socket names."""

    color: str
    roughness: str
    coat: str | None = None
    coat_roughness: str | None = None
    anisotropy: str | None = None
    emission: str | None = None
    transmission: str | None = None
    sheen: str | None = None
    metallic: str | None = None


def _float(name: str, default: float, lo: float = 0.0, hi: float = 1.0) -> SocketSpec:
    return SocketSpec(name, "FLOAT", default, min=lo, max=hi)


def _color(name: str, default: tuple[float, float, float, float]) -> SocketSpec:
    return SocketSpec(name, "COLOR", list(default))


SOCKETS: dict[str, tuple[SocketSpec, ...]] = {
    "surface": (
        _color("Base Color", (0.8, 0.8, 0.8, 1.0)),
        _float("Metallic", 0.0),
        _float("Roughness", 0.4),
        _float("IOR", 1.5, 1.0, 2.5),
        _color("Emission Color", (0.0, 0.0, 0.0, 1.0)),
        _float("Emission Strength", 0.0, 0.0, 50.0),
        _float("Alpha", 1.0),
    ),
    "metal": (
        _color("Color", (0.72, 0.72, 0.74, 1.0)),
        _float("Roughness", 0.25),
        _float("Anisotropy", 0.0),
        _float("Rotation", 0.0),
        _float("Coat Weight", 0.0),
        _float("Coat Roughness", 0.03),
    ),
    "dielectric": (
        _color("Color", (0.18, 0.18, 0.2, 1.0)),
        _float("Roughness", 0.45),
        _float("Specular", 0.5),
        _float("IOR", 1.45, 1.0, 2.5),
        _float("Coat Weight", 0.0),
        _float("Coat Roughness", 0.05),
        _float("Sheen Weight", 0.0),
        _color("Sheen Tint", (1.0, 1.0, 1.0, 1.0)),
    ),
    "glass": (
        _color("Color", (1.0, 1.0, 1.0, 1.0)),
        _float("Roughness", 0.0),
        _float("IOR", 1.45, 1.0, 2.5),
        _float("Transmission", 1.0),
    ),
    "fabric": (
        _color("Color", (0.35, 0.22, 0.18, 1.0)),
        _float("Roughness", 0.7),
        _float("Sheen Weight", 0.6),
        _float("Sheen Roughness", 0.4),
        _color("Sheen Tint", (0.95, 0.9, 0.85, 1.0)),
        _float("Subsurface", 0.05),
    ),
    "emissive": (
        _color("Color", (1.0, 0.85, 0.55, 1.0)),
        _float("Strength", 8.0, 0.0, 200.0),
        _float("Surface Roughness", 0.4),
        _color("Surface Color", (0.0, 0.0, 0.0, 1.0)),
    ),
    "layered": (
        _color("Base Color", (0.05, 0.12, 0.35, 1.0)),
        _float("Base Roughness", 0.35),
        _float("Metallic", 0.15),
        _float("Coat Weight", 1.0),
        _float("Coat Roughness", 0.03),
        _float("Coat IOR", 1.5, 1.0, 2.5),
        _color("Coat Tint", (1.0, 1.0, 1.0, 1.0)),
    ),
}

ALIASES: dict[str, Aliases] = {
    "surface": Aliases(
        color="Base Color",
        roughness="Roughness",
        emission="Emission Strength",
        metallic="Metallic",
    ),
    "metal": Aliases(
        color="Color",
        roughness="Roughness",
        coat="Coat Weight",
        coat_roughness="Coat Roughness",
        anisotropy="Anisotropy",
    ),
    "dielectric": Aliases(
        color="Color",
        roughness="Roughness",
        coat="Coat Weight",
        coat_roughness="Coat Roughness",
        sheen="Sheen Weight",
    ),
    "glass": Aliases(
        color="Color",
        roughness="Roughness",
        transmission="Transmission",
    ),
    "fabric": Aliases(
        color="Color",
        roughness="Roughness",
        sheen="Sheen Weight",
    ),
    "emissive": Aliases(
        color="Color",
        roughness="Surface Roughness",
        emission="Strength",
    ),
    "layered": Aliases(
        color="Base Color",
        roughness="Base Roughness",
        coat="Coat Weight",
        coat_roughness="Coat Roughness",
        metallic="Metallic",
    ),
}

# Free preset value packs from Master-Node 0.1.0. Paid names are hints only.
PRESETS: dict[str, dict[str, Any]] = {
    "surface.default": {
        "Base Color": [0.8, 0.8, 0.8, 1.0],
        "Metallic": 0.0,
        "Roughness": 0.4,
        "IOR": 1.5,
        "Emission Strength": 0.0,
        "Alpha": 1.0,
    },
    "surface.matte_clay": {
        "Base Color": [0.55, 0.48, 0.42, 1.0],
        "Metallic": 0.0,
        "Roughness": 0.85,
        "IOR": 1.4,
        "Emission Strength": 0.0,
        "Alpha": 1.0,
    },
    "metal.chrome": {
        "Color": [0.95, 0.95, 0.97, 1.0],
        "Roughness": 0.02,
        "Anisotropy": 0.0,
        "Rotation": 0.0,
        "Coat Weight": 0.0,
        "Coat Roughness": 0.03,
    },
    "metal.brushed_aluminum": {
        "Color": [0.72, 0.73, 0.75, 1.0],
        "Roughness": 0.28,
        "Anisotropy": 0.65,
        "Rotation": 0.0,
        "Coat Weight": 0.0,
        "Coat Roughness": 0.03,
    },
    "dielectric.hard_plastic": {
        "Color": [0.12, 0.13, 0.15, 1.0],
        "Roughness": 0.35,
        "Specular": 0.5,
        "IOR": 1.46,
        "Coat Weight": 0.0,
        "Sheen Weight": 0.0,
    },
    "dielectric.rubber": {
        "Color": [0.04, 0.04, 0.045, 1.0],
        "Roughness": 0.72,
        "Specular": 0.25,
        "IOR": 1.51,
        "Coat Weight": 0.0,
        "Sheen Weight": 0.15,
    },
    "glass.clear": {
        "Color": [1.0, 1.0, 1.0, 1.0],
        "Roughness": 0.0,
        "IOR": 1.45,
        "Transmission": 1.0,
    },
    "glass.frosted": {
        "Color": [0.95, 0.96, 0.97, 1.0],
        "Roughness": 0.35,
        "IOR": 1.45,
        "Transmission": 1.0,
    },
    "fabric.cotton": {
        "Color": [0.62, 0.58, 0.52, 1.0],
        "Roughness": 0.78,
        "Sheen Weight": 0.25,
        "Sheen Roughness": 0.55,
        "Subsurface": 0.02,
    },
    "fabric.velvet": {
        "Color": [0.12, 0.04, 0.08, 1.0],
        "Roughness": 0.55,
        "Sheen Weight": 0.9,
        "Sheen Roughness": 0.22,
        "Sheen Tint": [0.55, 0.2, 0.3, 1.0],
        "Subsurface": 0.08,
    },
    "emissive.warm_led": {
        "Color": [1.0, 0.72, 0.38, 1.0],
        "Strength": 12.0,
        "Surface Roughness": 0.35,
        "Surface Color": [0.02, 0.02, 0.02, 1.0],
    },
    "emissive.neon": {
        "Color": [0.15, 0.85, 1.0, 1.0],
        "Strength": 40.0,
        "Surface Roughness": 0.15,
        "Surface Color": [0.0, 0.02, 0.04, 1.0],
    },
    "layered.lacquer": {
        "Base Color": [0.28, 0.16, 0.08, 1.0],
        "Base Roughness": 0.45,
        "Metallic": 0.0,
        "Coat Weight": 0.85,
        "Coat Roughness": 0.08,
        "Coat IOR": 1.48,
        "Coat Tint": [1.0, 0.95, 0.88, 1.0],
    },
    "layered.car_paint": {
        "Base Color": [0.04, 0.1, 0.32, 1.0],
        "Base Roughness": 0.28,
        "Metallic": 0.35,
        "Coat Weight": 1.0,
        "Coat Roughness": 0.02,
        "Coat IOR": 1.5,
        "Coat Tint": [1.0, 1.0, 1.0, 1.0],
    },
}

PRESET_CATEGORY = {preset_id: preset_id.split(".", 1)[0] for preset_id in PRESETS}

DEFAULT_PRESET = {
    "surface": "surface.default",
    "metal": "metal.brushed_aluminum",
    "dielectric": "dielectric.hard_plastic",
    "glass": "glass.clear",
    "fabric": "fabric.cotton",
    "emissive": "emissive.warm_led",
    "layered": "layered.lacquer",
}

PAID_PRESETS = {
    "metal.aged_brass": "metal",
    "metal.anodized_blue": "metal",
    "metal.galvanized": "metal",
    "glass.smoked": "glass",
    "glass.thin_film": "glass",
    "fabric.silk": "fabric",
    "fabric.denim": "fabric",
    "layered.wet_asphalt": "layered",
}


def socket_map(category: str) -> dict[str, SocketSpec]:
    if category not in SOCKETS:
        raise KeyError(f"unknown category: {category}")
    return {spec.name: spec for spec in SOCKETS[category]}


def aliases_for(category: str) -> Aliases:
    try:
        return ALIASES[category]
    except KeyError as exc:
        raise KeyError(f"unknown category: {category}") from exc
