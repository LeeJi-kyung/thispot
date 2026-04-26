from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from app.models.schemas import (
    ArchivedPhoto,
    FinishWalkRequest,
    FinishWalkResponse,
    WalkArchiveItem,
)
from app.storage.json_store import JsonStore
from app.storage.sessions import UPLOAD_DIR, accepted_photo_records, safe_id


ARCHIVE_STORE = JsonStore("walk_archive.json", {"walks": []})


def archive_completed_walk(
    *,
    request: FinishWalkRequest,
    response: FinishWalkResponse,
    base_url: str,
) -> WalkArchiveItem:
    now = datetime.now(UTC)
    clean_user = safe_id(request.user_id, "user")
    clean_session = safe_id(request.session_id)
    archive_id = f"walk_{clean_session}"
    item = WalkArchiveItem(
        archive_id=archive_id,
        user_id=clean_user,
        session_id=clean_session,
        created_at=now.isoformat(),
        date=now.date().isoformat(),
        target_color=request.target_color.lower(),
        distance_m=request.distance_m,
        steps=request.steps,
        duration_sec=request.duration_sec,
        best_match_score=request.best_match_score,
        is_new_spot=request.is_new_spot,
        photos=[
            _archived_photo(record=record, base_url=base_url)
            for record in accepted_photo_records(clean_session, limit=3)
        ],
        badge=response.badge,
        summary=response.summary,
        report=response.report,
    )

    def upsert(payload: dict) -> None:
        walks = payload.setdefault("walks", [])
        dumped = item.model_dump(mode="json")
        for index, walk in enumerate(walks):
            if (
                walk.get("user_id") == clean_user
                and walk.get("session_id") == clean_session
            ):
                created_at = walk.get("created_at")
                date = walk.get("date")
                walks[index] = {
                    **dumped,
                    "created_at": created_at or dumped["created_at"],
                    "date": date or dumped["date"],
                }
                return
        walks.append(dumped)

    ARCHIVE_STORE.update(upsert)
    return item


def list_archived_walks(user_id: str, *, limit: int = 50) -> list[WalkArchiveItem]:
    clean_user = safe_id(user_id, "user")
    walks = [
        walk
        for walk in ARCHIVE_STORE.read().get("walks", [])
        if walk.get("user_id") == clean_user
    ]
    walks.sort(key=lambda walk: walk.get("created_at", ""), reverse=True)
    return [WalkArchiveItem.model_validate(walk) for walk in walks[:limit]]


def _archived_photo(*, record: dict, base_url: str) -> ArchivedPhoto:
    image_path = Path(record.get("image_path", ""))
    image_url = _image_url(image_path=image_path, base_url=base_url)
    return ArchivedPhoto(
        photo_id=str(record.get("photo_id", "")),
        image_url=image_url,
        match_score=float(record.get("match_score", 0.0)),
        object_label=str(record.get("object_label", "")),
        lat=record.get("lat"),
        lng=record.get("lng"),
    )


def _image_url(*, image_path: Path, base_url: str) -> str:
    try:
        relative = image_path.resolve().relative_to(UPLOAD_DIR.resolve())
    except (OSError, ValueError):
        return ""
    return f"{base_url.rstrip('/')}/uploads/{relative.name}"
