from typing import Any

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


class APIResponse(BaseModel):
    data: Any
    error: str | None = None
    status: str


def ok(data: Any) -> dict:
    return {"data": data, "error": None, "status": "ok"}


def err(message: str) -> dict:
    return {"data": None, "error": message, "status": "error"}
