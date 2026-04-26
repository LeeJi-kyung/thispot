import os
from pathlib import Path

from app.agents.content_generation_agent import ContentGenerationAgent
from app.agents.discovery_agent import DiscoveryAgent
from app.agents.personal_walk_agent import PersonalWalkAgent
from app.agents.reward_agent import RewardAgent
from app.agents.vision_mission_agent import VisionMissionAgent
from app.models.schemas import (
    AgentTrace,
    AnalyzePhotoResponse,
    Character,
    ContentGenerationInput,
    DiscoveryResult,
    FinishWalkRequest,
    FinishWalkResponse,
    GenerationJob,
    LoginDemoResponse,
    RecommendColorRequest,
    RecommendColorResponse,
    Summary,
    VisionResult,
)
from app.storage.generation_jobs import complete_generation_job, create_generation_job, get_generation_job
from app.storage.sessions import accepted_photo_paths, get_photo_paths, record_photo_proof


class WalkHarnessOrchestrator:
    def __init__(self, base_url: str = "http://localhost:8000") -> None:
        self.base_url = os.getenv("THISPOT_BASE_URL", base_url).rstrip("/")
        self.personal_walk_agent = PersonalWalkAgent()
        self.vision_agent = VisionMissionAgent()
        self.discovery_agent = DiscoveryAgent()
        self.reward_agent = RewardAgent()
        self.content_agent = ContentGenerationAgent()

    def login_demo(self, nickname: str) -> LoginDemoResponse:
        return LoginDemoResponse(
            user_id="demo_user",
            nickname=nickname or "Hayoon",
            character=Character(
                name="Spotter",
                base_image_url=f"{self.base_url}/assets/character/base.png",
            ),
        )

    def recommend_color(self, request: RecommendColorRequest) -> RecommendColorResponse:
        try:
            return self.personal_walk_agent.run(request)
        except Exception:
            return RecommendColorResponse(
                target_color="blue",
                mission_title="Blue Energy Walk",
                mission_text="Find blue moments during today's walk.",
                character_outfit_color="blue",
            )

    def analyze_photo(
        self,
        *,
        user_id: str,
        session_id: str,
        target_color: str,
        lat: float | None,
        lng: float | None,
        photo_id: str,
        photo_path: Path,
    ) -> AnalyzePhotoResponse:
        trace: list[AgentTrace] = []
        try:
            vision_result, vision_trace = self.vision_agent.run(photo_path, target_color)
        except Exception:
            vision_result, vision_trace = self.vision_agent.fallback(target_color)
        trace.append(vision_trace)

        try:
            discovery_result, discovery_trace = self.discovery_agent.run(
                target_color=target_color,
                lat=lat,
                lng=lng,
                vision_result=vision_result,
            )
        except Exception:
            discovery_result, discovery_trace = self.discovery_agent.fallback(target_color)
        trace.append(discovery_trace)
        proof_result = record_photo_proof(
            session_id=session_id,
            photo_id=photo_id,
            image_path=photo_path,
            vision_result=vision_result,
            lat=lat,
            lng=lng,
        )
        if proof_result.accepted:
            self.discovery_agent.record_verified_spot(
                user_id=user_id,
                session_id=session_id,
                photo_id=photo_id,
                target_color=target_color,
                lat=lat,
                lng=lng,
                vision_result=vision_result,
            )

        return AnalyzePhotoResponse(
            photo_id=photo_id,
            proof_result=proof_result,
            vision_result=vision_result,
            discovery_result=discovery_result,
            agent_trace=trace,
        )

    def analyze_photo_fallback(self, target_color: str = "blue") -> AnalyzePhotoResponse:
        vision_result, vision_trace = self.vision_agent.fallback(target_color)
        discovery_result, discovery_trace = self.discovery_agent.fallback(target_color)
        return AnalyzePhotoResponse(
            photo_id="photo_fallback",
            proof_result=record_photo_proof(
                session_id="session_123",
                photo_id="photo_fallback",
                image_path=Path("fallback.jpg"),
                vision_result=vision_result,
                lat=None,
                lng=None,
            ),
            vision_result=vision_result,
            discovery_result=discovery_result,
            agent_trace=[vision_trace, discovery_trace],
        )

    def finish_walk(self, request: FinishWalkRequest) -> FinishWalkResponse:
        trace: list[AgentTrace] = []
        try:
            badge, reward_trace = self.reward_agent.run(
                target_color=request.target_color,
                best_match_score=request.best_match_score,
                is_new_spot=request.is_new_spot,
            )
        except Exception:
            badge, reward_trace = self.reward_agent.fallback(request.target_color)
        trace.append(reward_trace)

        accepted_paths = accepted_photo_paths(request.session_id, limit=5)
        if len(accepted_paths) < 5:
            raise ValueError(
                "MISSION_NOT_COMPLETE: Collect 5 accepted color proofs before finishing this walk."
            )
        photo_paths = [
            str(path)
            for path in (accepted_paths or get_photo_paths(request.session_id, request.photo_ids))
        ]
        generation_job = create_generation_job(status="running", message="Local report generation running")
        try:
            report, content_trace = self.content_agent.run(
                ContentGenerationInput(
                    session_id=request.session_id,
                    target_color=request.target_color,
                    character_id="spotter",
                    distance_m=request.distance_m,
                    steps=request.steps,
                    duration_sec=request.duration_sec,
                    best_match_score=request.best_match_score,
                    photo_paths=photo_paths,
                    badge_title=badge.title,
                )
            )
            report.generation_job_id = generation_job.job_id
            complete_generation_job(
                generation_job.job_id,
                report=report,
                status=content_trace.status if content_trace.status in {"completed", "fallback"} else "completed",
                message=content_trace.message,
            )
        except Exception:
            report, content_trace = self.content_agent.fallback(request.session_id)
            report.generation_job_id = generation_job.job_id
            complete_generation_job(
                generation_job.job_id,
                report=report,
                status="fallback",
                message=content_trace.message,
            )
        trace.append(content_trace)

        return FinishWalkResponse(
            badge=badge,
            report=report,
            summary=self._summary(request),
            agent_trace=trace,
        )

    def generation_job(self, job_id: str) -> GenerationJob | None:
        return get_generation_job(job_id)

    def finish_walk_fallback(self) -> FinishWalkResponse:
        request = FinishWalkRequest()
        badge, reward_trace = self.reward_agent.fallback(request.target_color)
        report, content_trace = self.content_agent.fallback(request.session_id)
        return FinishWalkResponse(
            badge=badge,
            report=report,
            summary=self._summary(request),
            agent_trace=[reward_trace, content_trace],
        )

    def _summary(self, request: FinishWalkRequest) -> Summary:
        color_name = request.target_color.capitalize()
        distance_km = request.distance_m / 1000
        match_percent = int(round(request.best_match_score * 100))
        spot_message = (
            f"New {color_name} Spot discovered."
            if request.is_new_spot
            else f"Shared {color_name} Spot found nearby."
        )
        return Summary(
            title=f"{color_name} Walk Complete",
            subtitle=(
                f"{distance_km:.2f}km - {request.steps:,} steps - "
                f"{match_percent}% color match"
            ),
            spot_message=spot_message,
            share_caption=f"I found today's {request.target_color} with ThiSpot.",
        )
