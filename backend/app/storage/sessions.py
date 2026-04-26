"""In-memory session store and photo path resolver."""

from pathlib import Path

_sessions: dict[str, dict] = {}

_UPLOADS = Path(__file__).resolve().parents[2] / "uploads"


def get_session(session_id: str) -> dict | None:
    return _sessions.get(session_id)


def set_session(session_id: str, data: dict) -> None:
    _sessions[session_id] = data


def get_photo_paths(session_id: str, photo_ids: list[str]) -> list[Path]:
    """Resolve photo_ids to absolute file paths that exist on disk."""
    paths = []
    for photo_id in photo_ids:
        p = _UPLOADS / session_id / f"{photo_id}.jpg"
        if p.exists():
            paths.append(p)
    return paths
