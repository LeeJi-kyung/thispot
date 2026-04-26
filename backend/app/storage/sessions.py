from __future__ import annotations

import re
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile


APP_DIR = Path(__file__).resolve().parents[1]
UPLOAD_DIR = APP_DIR / "uploads"

SESSION_PHOTOS: dict[str, list[Path]] = {}


def ensure_storage_dirs() -> None:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def safe_id(value: str, default: str = "session_123") -> str:
    clean = re.sub(r"[^A-Za-z0-9_.-]+", "_", value or default).strip("._")
    return clean or default


async def save_uploaded_photo(session_id: str, photo: UploadFile) -> Path:
    ensure_storage_dirs()
    clean_session = safe_id(session_id)
    original_name = safe_id(photo.filename or "photo.jpg", "photo.jpg")
    suffix = Path(original_name).suffix.lower() or ".jpg"
    path = UPLOAD_DIR / f"{clean_session}_{uuid4().hex}{suffix}"
    content = await photo.read()
    path.write_bytes(content)
    SESSION_PHOTOS.setdefault(clean_session, []).append(path)
    return path


def get_photo_paths(session_id: str, photo_ids: list[str] | None = None) -> list[Path]:
    clean_session = safe_id(session_id)
    paths = SESSION_PHOTOS.get(clean_session, [])
    if not photo_ids:
        return paths
    wanted = {safe_id(photo_id) for photo_id in photo_ids}
    return [path for path in paths if path.stem in wanted or path.name in wanted]
