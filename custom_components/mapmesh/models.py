"""Data models and mappers for MapMe API responses."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class MapMeBadge:
    """A single badge from the MapMe API."""

    id: str
    name: str
    icon: str
    tier: str
    desc: str
    label: str | None = None
    color: str | None = None
    value: int | None = None
    next_threshold: int | None = None


@dataclass(frozen=True, slots=True)
class MapMeUserData:
    """Parsed user profile from the MapMe API."""

    pubkey: str
    name: str
    hardware: str
    rank: int
    points: int
    total_samples: int
    unique_hexes: int
    rx_hexes: int
    active_days: int
    unique_repeaters: int
    pioneer_hexes: int
    first_seen: int
    last_seen: int
    days_since_first: int
    badges: tuple[MapMeBadge, ...]
    road_trip_peak: int | None
    grinder_peak: int | None


def _badge_from_dict(data: dict[str, Any]) -> MapMeBadge:
    return MapMeBadge(
        id=data["id"],
        name=data["name"],
        icon=data.get("icon", ""),
        tier=data.get("tier", ""),
        desc=data.get("desc", ""),
        label=data.get("label"),
        color=data.get("color"),
        value=data.get("value"),
        next_threshold=data.get("next"),
    )


def parse_user_response(data: dict[str, Any]) -> MapMeUserData:
    """Parse raw API JSON into a MapMeUserData object."""
    stats = data.get("stats", {})
    badges = tuple(_badge_from_dict(b) for b in data.get("badges", []))

    road_trip_peak: int | None = None
    grinder_peak: int | None = None
    for badge in badges:
        if badge.id == "road_trip":
            road_trip_peak = badge.value
        elif badge.id == "grinder":
            grinder_peak = badge.value

    return MapMeUserData(
        pubkey=data["pubkey"],
        name=data["name"],
        hardware=data.get("hardware", ""),
        rank=int(data["rank"]),
        points=int(data["points"]),
        total_samples=int(stats.get("totalSamples", 0)),
        unique_hexes=int(stats.get("uniqueHexes", 0)),
        rx_hexes=int(stats.get("rxHexes", 0)),
        active_days=int(stats.get("activeDays", 0)),
        unique_repeaters=int(stats.get("uniqueRepeaters", 0)),
        pioneer_hexes=int(stats.get("pioneerHexes", 0)),
        first_seen=int(stats.get("firstSeen", 0)),
        last_seen=int(stats.get("lastSeen", 0)),
        days_since_first=int(stats.get("daysSinceFirst", 0)),
        badges=badges,
        road_trip_peak=road_trip_peak,
        grinder_peak=grinder_peak,
    )


def badge_to_dict(badge: MapMeBadge) -> dict[str, Any]:
    """Serialize a badge for entity attributes."""
    result: dict[str, Any] = {
        "id": badge.id,
        "name": badge.name,
        "icon": badge.icon,
        "tier": badge.tier,
        "desc": badge.desc,
    }
    if badge.label is not None:
        result["label"] = badge.label
    if badge.color is not None:
        result["color"] = badge.color
    if badge.value is not None:
        result["value"] = badge.value
    if badge.next_threshold is not None:
        result["next"] = badge.next_threshold
    return result


def profile_attributes(data: MapMeUserData) -> dict[str, Any]:
    """Build profile sensor attributes for the Lovelace card."""
    return {
        "name": data.name,
        "hardware": data.hardware,
        "pubkey": data.pubkey,
        "rank": data.rank,
        "points": data.points,
        "total_samples": data.total_samples,
        "unique_hexes": data.unique_hexes,
        "rx_hexes": data.rx_hexes,
        "active_days": data.active_days,
        "unique_repeaters": data.unique_repeaters,
        "pioneer_hexes": data.pioneer_hexes,
        "days_since_first": data.days_since_first,
        "first_seen": data.first_seen,
        "last_seen": data.last_seen,
        "road_trip_peak": data.road_trip_peak,
        "grinder_peak": data.grinder_peak,
        "badges": [badge_to_dict(b) for b in data.badges],
    }
