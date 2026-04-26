from typing import Any, Literal

from pydantic import BaseModel


class ColorEntry(BaseModel):
    name: str
    hex: str
    rgb: list[int]
    percent: float
    category: str | None = None  # one of 8 categories or "none"


class VisionResult(BaseModel):
    detected_color: str
    match_score: float
    is_matched: bool
    object_label: str
    feedback: str


class DiscoveryResult(BaseModel):
    is_new_spot: bool
    shared_user_percent: int
    message: str


class AgentTrace(BaseModel):
    agent: str
    status: str
    message: str


class AnalyzePhotoData(BaseModel):
    vision_result: VisionResult
    discovery_result: DiscoveryResult
    agent_trace: list[AgentTrace]


# ── Finish-walk models ────────────────────────────────────────────────────────

class ShortformScene(BaseModel):
    scene: int
    caption: str
    visual: str
    transition: str


class ShortformPlan(BaseModel):
    style: str
    caption: str
    shortform_prompt: str
    storyboard: list[ShortformScene]


class Badge(BaseModel):
    title: str
    description: str
    rarity: Literal["common", "rare", "epic", "legendary"]
    image_url: str | None = None


class Summary(BaseModel):
    title: str
    subtitle: str
    spot_message: str
    share_caption: str


class Report(BaseModel):
    status: Literal["completed", "fallback", "queued"]
    type: Literal["video", "image", "job"]
    video_url: str | None = None
    image_url: str
    thumbnail_url: str
    shortform_prompt: str
    style: str
    caption: str
    storyboard: list[ShortformScene]
    job_id: str | None = None


class FinishWalkRequest(BaseModel):
    user_id: str
    session_id: str
    target_color: str
    distance_m: int
    steps: int
    duration_sec: int
    photo_ids: list[str] = []
    best_match_score: float
    is_new_spot: bool


class FinishWalkResponse(BaseModel):
    badge: Badge
    summary: Summary
    report: Report
    agent_trace: list[AgentTrace]


class ContentGenerationInput(BaseModel):
    session_id: str
    target_color: str
    distance_m: int
    steps: int
    duration_sec: int
    best_match_score: float
    photo_paths: list[str] = []
    badge_title: str


# ── Response helpers ──────────────────────────────────────────────────────────

class APIResponse(BaseModel):
    data: Any
    error: str | None = None
    status: str


def ok(data: Any) -> dict:
    return {"data": data, "error": None, "status": "ok"}


def err(message: str) -> dict:
    return {"data": None, "error": message, "status": "error"}
