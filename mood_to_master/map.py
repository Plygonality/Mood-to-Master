"""Resolve generator moods/tags into a Master-Node value map."""

from __future__ import annotations

import json
import random
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any

from mood_to_master.catalog import (
    CATEGORIES,
    CATEGORY_PRIORITY,
    DEFAULT_PRESET,
    PAID_PRESETS,
    PRESET_CATEGORY,
    PRESETS,
    SOCKETS,
    SocketSpec,
    aliases_for,
    socket_map,
)
from mood_to_master.rules import MOODS, Color, Hit, collect_hits

FORMAT = "mood-to-master"
FORMAT_VERSION = 1
QUANT = 6

DELTA_KEYS = (
    "roughness",
    "coat",
    "coat_roughness",
    "anisotropy",
    "emission",
    "transmission",
    "sheen",
    "metallic",
)


@dataclass(frozen=True)
class Look:
    """A bindable Master-Node look.

    ``values`` is the map Plygon-mcp / ``master_node.live.set_param`` writes.
    """

    category: str
    preset: str
    values: dict[str, Any]
    deltas: dict[str, float]
    hits: tuple[str, ...]
    paid_preset: str | None = None

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "format": FORMAT,
            "version": FORMAT_VERSION,
            "category": self.category,
            "preset": self.preset,
            "paid_preset": self.paid_preset,
            "hits": list(self.hits),
            "deltas": {k: _q(v) for k, v in self.deltas.items()},
            "values": _jsonable(self.values),
        }
        return data

    def dumps(self) -> str:
        return json.dumps(self.to_dict(), indent=2) + "\n"

    def set_param_items(self) -> list[dict[str, Any]]:
        """One ``set_param(name, value)`` call per socket, catalog order."""
        order = [spec.name for spec in SOCKETS[self.category]]
        items = []
        for name in order:
            if name in self.values:
                items.append({"name": name, "value": _jsonable(self.values[name])})
        for name, value in self.values.items():
            if name not in {row["name"] for row in items}:
                items.append({"name": name, "value": _jsonable(value)})
        return items


def map_look(
    *,
    moods: Iterable[str] = (),
    tags: Iterable[str] = (),
    palette: str = "",
    lighting: str = "",
    composition: str = "",
) -> Look:
    """Map a brief onto category + preset + socket value map."""
    hits = collect_hits(
        moods=moods,
        tags=tags,
        palette=palette,
        lighting=lighting,
        composition=composition,
    )
    if not hits:
        hits = [Hit(name="default", category_votes={"metal": 1})]
    return _resolve(hits)


def map_concept(concept: Mapping[str, Any]) -> Look:
    """Map a Hard-SciFi-idea-generator concept (Fragment dict or plain dicts)."""
    tags: set[str] = set()
    palette = lighting = composition = ""
    for axis, frag in concept.items():
        text, frag_tags = _frag_fields(frag)
        tags |= frag_tags
        if axis == "palette":
            palette = text
        elif axis == "lighting":
            lighting = text
        elif axis == "composition":
            composition = text
    moods = tags & MOODS
    return map_look(
        moods=moods,
        tags=tags,
        palette=palette,
        lighting=lighting,
        composition=composition,
    )


def generate_and_map(
    seed: int,
    *,
    require: Iterable[str] = (),
    avoid: Iterable[str] = (),
    mood: Iterable[str] = (),
) -> tuple[Look, dict[str, Any]]:
    """Run the idea generator (if installed) and map the resulting concept."""
    try:
        import hard_scifi_idea_generator as gen
    except ImportError as exc:
        raise RuntimeError(
            "hard-scifi-idea-generator is not installed. "
            "pip install git+https://github.com/Plygonality/Hard-SciFi-idea-generator.git"
        ) from exc

    require_tags = frozenset(require) | frozenset(mood)
    generator = gen.ConceptGenerator(
        require=require_tags,
        avoid=frozenset(avoid),
    )
    concept = generator.generate(random.Random(seed))
    return map_concept(concept), concept


def _frag_fields(frag: Any) -> tuple[str, set[str]]:
    if hasattr(frag, "text"):
        tags = set(getattr(frag, "tags", frozenset()) or [])
        return str(frag.text), {str(t) for t in tags}
    if isinstance(frag, Mapping):
        raw = frag.get("tags") or []
        if isinstance(raw, str):
            tags = set(raw.split())
        else:
            tags = {str(t) for t in raw}
        return str(frag.get("text") or ""), tags
    return str(frag), set()


def _resolve(hits: list[Hit]) -> Look:
    category = _pick_category(hits)
    preset = _pick_preset(hits, category)
    paid = _pick_paid(hits, category)
    values = _base_values(category, preset)
    aliases = aliases_for(category)
    sockets = socket_map(category)

    color, color_weight_sum = _blend_colors(hits)
    if color is not None and color_weight_sum > 0:
        values[aliases.color] = list(color)

    summed: dict[str, float] = {}
    for hit in hits:
        for key, amount in hit.deltas.items():
            summed[key] = summed.get(key, 0.0) + amount

    darken = min(max(summed.pop("darken", 0.0), 0.0), 0.75)
    desaturate = min(max(summed.pop("desaturate", 0.0), 0.0), 0.8)

    applied: dict[str, float] = {}
    for key in DELTA_KEYS:
        amount = summed.get(key)
        if not amount:
            continue
        socket_name = getattr(aliases, key)
        if not socket_name:
            continue
        current = values.get(socket_name, sockets[socket_name].default)
        values[socket_name] = _clamp_float(sockets[socket_name], float(current) + amount)
        applied[socket_name] = amount

    if darken or desaturate:
        values[aliases.color] = _grade_color(values[aliases.color], darken, desaturate)
        if darken:
            applied["darken"] = darken
        if desaturate:
            applied["desaturate"] = desaturate

    values = {name: _quantize(sockets[name], value) for name, value in values.items()}
    return Look(
        category=category,
        preset=preset,
        paid_preset=paid,
        values=values,
        deltas=applied,
        hits=tuple(hit.name for hit in hits),
    )


def _pick_category(hits: list[Hit]) -> str:
    scores: dict[str, int] = {cat: 0 for cat in CATEGORIES}
    for hit in hits:
        for cat, votes in hit.category_votes.items():
            if cat in scores:
                scores[cat] += votes
    best = max(scores.values())
    if best <= 0:
        return "metal"
    tied = [cat for cat, score in scores.items() if score == best]
    for cat in CATEGORY_PRIORITY:
        if cat in tied:
            return cat
    return tied[0]


def _pick_preset(hits: list[Hit], category: str) -> str:
    scores: dict[str, int] = {
        preset_id: 0
        for preset_id, cat in PRESET_CATEGORY.items()
        if cat == category
    }
    if not scores:
        return DEFAULT_PRESET[category]
    for hit in hits:
        for preset_id, votes in hit.preset_bias.items():
            if preset_id in scores:
                scores[preset_id] += votes
    best = max(scores.values())
    if best <= 0:
        return DEFAULT_PRESET[category]
    tied = sorted(pid for pid, score in scores.items() if score == best)
    default = DEFAULT_PRESET[category]
    if default in tied:
        return default
    return tied[0]


def _pick_paid(hits: list[Hit], category: str) -> str | None:
    scores: dict[str, int] = {
        preset_id: 0 for preset_id, cat in PAID_PRESETS.items() if cat == category
    }
    if not scores:
        return None
    for hit in hits:
        for preset_id, votes in hit.paid_bias.items():
            if preset_id in scores:
                scores[preset_id] += votes
    best = max(scores.values())
    if best <= 0:
        return None
    tied = sorted(pid for pid, score in scores.items() if score == best)
    return tied[0]


def _base_values(category: str, preset_id: str) -> dict[str, Any]:
    values: dict[str, Any] = {}
    packed = PRESETS.get(preset_id, {})
    for spec in SOCKETS[category]:
        if spec.name in packed:
            values[spec.name] = _copy(packed[spec.name])
        else:
            values[spec.name] = _copy(spec.default)
    return values


def _blend_colors(hits: list[Hit]) -> tuple[Color | None, float]:
    acc = [0.0, 0.0, 0.0, 0.0]
    weight = 0.0
    for hit in hits:
        if hit.color is None:
            continue
        w = hit.color_weight
        for i in range(4):
            acc[i] += hit.color[i] * w
        weight += w
    if weight <= 0:
        return None, 0.0
    blended = tuple(acc[i] / weight for i in range(4))
    return blended, weight  # type: ignore[return-value]


def _grade_color(color: Any, darken: float, desaturate: float) -> list[float]:
    rgba = [float(c) for c in list(color)]
    while len(rgba) < 4:
        rgba.append(1.0)
    r, g, b, a = rgba[:4]
    if desaturate:
        luma = 0.2126 * r + 0.7152 * g + 0.0722 * b
        r = r + (luma - r) * desaturate
        g = g + (luma - g) * desaturate
        b = b + (luma - b) * desaturate
    if darken:
        scale = 1.0 - darken
        r *= scale
        g *= scale
        b *= scale
    return [
        _clamp(r, 0.0, 1.0),
        _clamp(g, 0.0, 1.0),
        _clamp(b, 0.0, 1.0),
        _clamp(a, 0.0, 1.0),
    ]


def _clamp_float(spec: SocketSpec, value: float) -> float:
    lo = spec.min if spec.min is not None else value
    hi = spec.max if spec.max is not None else value
    return _clamp(value, lo, hi)


def _quantize(spec: SocketSpec, value: Any) -> Any:
    if spec.kind == "COLOR":
        seq = [float(c) for c in list(value)]
        if len(seq) == 3:
            seq.append(1.0)
        return [_q(_clamp(c, 0.0, 1.0)) for c in seq[:4]]
    return _q(float(value))


def _jsonable(value: Any) -> Any:
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    if isinstance(value, float):
        return _q(value)
    return value


def _copy(value: Any) -> Any:
    if isinstance(value, list):
        return list(value)
    if isinstance(value, tuple):
        return list(value)
    return value


def _q(value: float) -> float:
    return round(float(value), QUANT)


def _clamp(value: float, lo: float, hi: float) -> float:
    return lo if value < lo else hi if value > hi else value
