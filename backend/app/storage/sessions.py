from __future__ import annotations

from io import BytesIO
import re
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException
from fastapi import UploadFile
from PIL import Image, UnidentifiedImageError

from app.models.schemas import ProofResult, VisionResult
from app.storage.json_store import JsonStore


APP_DIR = Path(__file__).resolve().parents[1]
UPLOAD_DIR = APP_DIR / "uploads"
MAX_UPLOAD_BYTES = 8 * 1024 * 1024
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
REQUIRED_PROOFS = 5

SESSION_STORE = JsonStore("sessions.json", {"sessions": {}})


def ensure_storage_dirs() -> None:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def safe_id(value: str, default: str = "session_123") -> str:
    clean = re.sub(r"[^A-Za-z0-9_.-]+", "_", value or default).strip("._")
    return clean or default


async def save_uploaded_photo(session_id: str, photo: UploadFile) -> tuple[str, Path]:
    ensure_storage_dirs()
    if photo.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=415, detail="photo must be a JPEG, PNG, or WebP image")

    clean_session = safe_id(session_id)
    original_name = safe_id(photo.filename or "photo.jpg", "photo.jpg")
    suffix = Path(original_name).suffix.lower() or ".jpg"
    photo_id = f"photo_{uuid4().hex[:12]}"
    path = UPLOAD_DIR / f"{clean_session}_{photo_id}{suffix}"

    chunks: list[bytes] = []
    total_size = 0
    while True:
        chunk = await photo.read(1024 * 1024)
        if not chunk:
            break
        total_size += len(chunk)
        if total_size > MAX_UPLOAD_BYTES:
            raise HTTPException(status_code=413, detail="photo exceeds 8MB limit")
        chunks.append(chunk)

    content = b"".join(chunks)
    if not content:
        raise HTTPException(status_code=400, detail="photo is empty")

    try:
        Image.open(BytesIO(content)).verify()
    except (UnidentifiedImageError, OSError):
        raise HTTPException(status_code=400, detail="photo file is not a valid image")

    path.write_bytes(content)
    def append_photo(payload: dict) -> None:
        session = _session_record(payload, clean_session)
        session.setdefault("photos", []).append(str(path))

    SESSION_STORE.update(append_photo)
    return photo_id, path


def record_photo_proof(
    *,
    session_id: str,
    photo_id: str,
    image_path: Path,
    vision_result: VisionResult,
    lat: float | None,
    lng: float | None,
) -> ProofResult:
    clean_session = safe_id(session_id)
    accepted = bool(vision_result.is_matched and vision_result.match_score >= 0.70)
    def append_proof(payload: dict) -> None:
        session = _session_record(payload, clean_session)
        session.setdefault("proofs", []).append(
            {
                "photo_id": safe_id(photo_id),
                "image_path": str(image_path),
                "accepted": accepted,
                "match_score": vision_result.match_score,
                "detected_color": vision_result.detected_color,
                "object_label": vision_result.object_label,
                "lat": lat,
                "lng": lng,
            }
        )

    SESSION_STORE.update(append_proof)
    return proof_progress(clean_session, latest_accepted=accepted)


def proof_progress(session_id: str, latest_accepted: bool = False) -> ProofResult:
    clean_session = safe_id(session_id)
    proofs = _proofs(clean_session)
    raw_accepted_count = sum(1 for proof in proofs if proof["accepted"])
    accepted_count = min(REQUIRED_PROOFS, raw_accepted_count)
    remaining_count = max(0, REQUIRED_PROOFS - accepted_count)
    return ProofResult(
        accepted=latest_accepted,
        accepted_count=accepted_count,
        required_count=REQUIRED_PROOFS,
        remaining_count=remaining_count,
        completion_unlocked=accepted_count >= REQUIRED_PROOFS,
    )


def accepted_photo_paths(session_id: str, limit: int | None = None) -> list[Path]:
    clean_session = safe_id(session_id)
    paths = [
        Path(proof["image_path"])
        for proof in _proofs(clean_session)
        if proof["accepted"]
    ]
    return paths[:limit] if limit else paths


def accepted_photo_records(session_id: str, limit: int | None = None) -> list[dict]:
    clean_session = safe_id(session_id)
    proofs = [proof for proof in _proofs(clean_session) if proof["accepted"]]
    return proofs[:limit] if limit else proofs


def get_photo_paths(session_id: str, photo_ids: list[str] | None = None) -> list[Path]:
    clean_session = safe_id(session_id)
    stored_paths = [Path(path) for path in _session_record(SESSION_STORE.read(), clean_session).get("photos", [])]
    disk_paths = sorted(UPLOAD_DIR.glob(f"{clean_session}_*"))
    paths = list(dict.fromkeys([*stored_paths, *disk_paths]))
    if not photo_ids:
        return paths
    wanted = {safe_id(photo_id) for photo_id in photo_ids}
    return [
        path
        for path in paths
        if path.stem in wanted
        or path.name in wanted
        or any(path.stem.endswith(f"_{photo_id}") for photo_id in wanted)
    ]


def _session_record(payload: dict, session_id: str) -> dict:
    sessions = payload.setdefault("sessions", {})
    return sessions.setdefault(session_id, {"photos": [], "proofs": []})


def _proofs(session_id: str) -> list[dict]:
    payload = SESSION_STORE.read()
    return list(_session_record(payload, session_id).get("proofs", []))
