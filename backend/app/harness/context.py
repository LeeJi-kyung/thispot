from pydantic import BaseModel, Field


class WalkHarnessContext(BaseModel):
    user_id: str
    session_id: str
    target_color: str
    character_id: str | None = None
    lat: float | None = None
    lng: float | None = None
    distance_m: float | None = None
    steps: int | None = None
    duration_sec: int | None = None
    photo_paths: list[str] = Field(default_factory=list)
    vision_result: dict | None = None
    discovery_result: dict | None = None
    badge: dict | None = None
    report: dict | None = None
    trace: list[dict] = Field(default_factory=list)
