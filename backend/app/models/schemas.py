from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class AgentTrace(BaseModel):
    agent: str
    status: Literal["completed", "fallback", "failed"]
    message: str


class Character(BaseModel):
    name: str
    base_image_url: str


class LoginDemoRequest(BaseModel):
    nickname: str = "Hayoon"


class LoginDemoResponse(BaseModel):
    user_id: str
    nickname: str
    character: Character


class RecommendColorRequest(BaseModel):
    user_id: str = "demo_user"
    previous_colors: list[str] = Field(default_factory=list)


class RecommendColorResponse(BaseModel):
    target_color: str
    mission_title: str
    mission_text: str
    character_outfit_color: str


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


class AnalyzePhotoResponse(BaseModel):
    vision_result: VisionResult
    discovery_result: DiscoveryResult
    agent_trace: list[AgentTrace]


class FinishWalkRequest(BaseModel):
    user_id: str = "demo_user"
    session_id: str = "session_123"
    target_color: str = "blue"
    distance_m: float = 1240
    steps: int = 1843
    duration_sec: int = 720
    photo_ids: list[str] = Field(default_factory=list)
    best_match_score: float = 0.87
    is_new_spot: bool = True


class Badge(BaseModel):
    title: str
    description: str
    rarity: Literal["standard", "rare", "common"]


class Report(BaseModel):
    type: str
    video_url: str
    image_url: str
    thumbnail_url: str


class Summary(BaseModel):
    title: str
    subtitle: str
    spot_message: str
    share_caption: str


class FinishWalkResponse(BaseModel):
    badge: Badge
    report: Report
    summary: Summary
    agent_trace: list[AgentTrace]


class WalkHarnessContext(BaseModel):
    user_id: str = "demo_user"
    session_id: str = "session_123"
    target_color: str = "blue"
    character_id: str | None = None
    lat: float | None = None
    lng: float | None = None
    distance_m: float | None = None
    steps: int | None = None
    duration_sec: int | None = None
    photo_paths: list[str] = Field(default_factory=list)
    vision_result: VisionResult | None = None
    discovery_result: DiscoveryResult | None = None
    badge: Badge | None = None
    report: Report | None = None
    trace: list[AgentTrace] = Field(default_factory=list)


class ContentGenerationInput(BaseModel):
    session_id: str
    target_color: str
    character_id: str = "spotter"
    distance_m: float = 1240
    steps: int = 1843
    duration_sec: int = 720
    best_match_score: float = 0.87
    photo_paths: list[str] = Field(default_factory=list)
    badge_title: str = "Blue Finder"


class ShortformScene(BaseModel):
    scene: int
    caption: str
    visual: str
    transition: str


class ShortformPlan(BaseModel):
    style: str
    music_direction: str
    share_caption: str
    storyboard: list[ShortformScene]
    generation_prompt: str
