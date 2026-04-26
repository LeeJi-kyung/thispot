from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from app.skills.geo_distance_skill import GeoDistanceSkill
from app.storage.json_store import JsonStore
from app.storage.sessions import safe_id


SPOT_STORE = JsonStore("spots.json", {"spots": []})
MERGE_RADIUS_M = 50


def nearest_same_color_spot(
    *,
    target_color: str,
    lat: float | None,
    lng: float | None,
) -> tuple[dict, float] | None:
    if lat is None or lng is None:
        return None

    distance_skill = GeoDistanceSkill()
    candidates: list[tuple[dict, float]] = []
    for spot in SPOT_STORE.read().get("spots", []):
        if str(spot.get("color", "")).lower() != target_color.lower():
            continue
        spot_lat = spot.get("lat")
        spot_lng = spot.get("lng")
        if spot_lat is None or spot_lng is None:
            continue
        distance = distance_skill.distance_meters(lat, lng, float(spot_lat), float(spot_lng))
        candidates.append((spot, distance))

    return min(candidates, key=lambda item: item[1]) if candidates else None


def record_verified_spot(
    *,
    user_id: str,
    session_id: str,
    photo_id: str,
    target_color: str,
    object_label: str,
    lat: float | None,
    lng: float | None,
) -> dict | None:
    if lat is None or lng is None:
        return None

    now = datetime.now(UTC).isoformat()
    clean_user = safe_id(user_id, "user")
    clean_session = safe_id(session_id)
    clean_photo = safe_id(photo_id, "photo")

    def upsert(payload: dict) -> dict:
        spots = payload.setdefault("spots", [])
        nearest = nearest_same_color_spot(target_color=target_color, lat=lat, lng=lng)
        nearest_id = nearest[0]["spot_id"] if nearest and nearest[1] <= MERGE_RADIUS_M else None

        for spot in spots:
            if spot.get("spot_id") != nearest_id:
                continue
            spot["updated_at"] = now
            spot["sighting_count"] = int(spot.get("sighting_count", 0)) + 1
            spot["object_label"] = object_label or spot.get("object_label", "")
            _append_unique(spot.setdefault("user_ids", []), clean_user)
            _append_unique(spot.setdefault("session_ids", []), clean_session)
            _append_unique(spot.setdefault("photo_ids", []), clean_photo)
            return spot

        new_spot = {
            "spot_id": f"spot_{uuid4().hex[:12]}",
            "color": target_color.lower(),
            "object_label": object_label,
            "lat": lat,
            "lng": lng,
            "created_at": now,
            "updated_at": now,
            "sighting_count": 1,
            "user_ids": [clean_user],
            "session_ids": [clean_session],
            "photo_ids": [clean_photo],
        }
        spots.append(new_spot)
        return new_spot

    return SPOT_STORE.update(upsert)


def shared_user_percent(spot: dict | None) -> int:
    if not spot:
        return 8
    unique_users = len(spot.get("user_ids", []))
    sightings = int(spot.get("sighting_count", 0))
    return min(95, max(8, 8 + unique_users * 6 + sightings * 3))


def _append_unique(values: list[str], value: str) -> None:
    if value not in values:
        values.append(value)
