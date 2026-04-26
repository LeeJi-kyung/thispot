import os
import shutil
import tempfile
import uuid
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

load_dotenv()

from app.agents import discovery_agent  # noqa: E402
from app.agents.content_generation_agent import ContentGenerationAgent  # noqa: E402
from app.agents.reward_agent import RewardAgent  # noqa: E402
from app.agents.vision_mission_agent import VisionMissionAgent  # noqa: E402
from app.harness.trace import make_trace  # noqa: E402
from app.models.schemas import ContentGenerationInput, FinishWalkRequest, Summary, ok  # noqa: E402
from app.skills.image_generate_skill import (  # noqa: E402
    build_badge_prompt,
    extract_structured_keywords,
    generate_badge_image,
)
from app.storage.sessions import get_photo_paths  # noqa: E402

_BASE = Path(__file__).resolve().parents[1]
_OUTPUTS = _BASE / "outputs"
_UPLOADS = _BASE / "uploads"

for _d in [_OUTPUTS / "reports", _OUTPUTS / "videos", _OUTPUTS / "test", _UPLOADS]:
    _d.mkdir(parents=True, exist_ok=True)

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

app = FastAPI(title="ThiSpot Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/outputs", StaticFiles(directory=str(_OUTPUTS)), name="outputs")

_vision_agent = VisionMissionAgent()
_reward_agent = RewardAgent()
_content_agent = ContentGenerationAgent()


def _build_summary(req: FinishWalkRequest) -> Summary:
    dist_km = round(req.distance_m / 1000, 2)
    color = req.target_color.capitalize()
    pct = int(req.best_match_score * 100)
    spot_msg = f"New {color} Spot discovered." if req.is_new_spot else f"{color} Spot confirmed."
    return Summary(
        title=f"{color} Walk Complete",
        subtitle=f"{dist_km}km - {req.steps:,} steps - {pct}% color match",
        spot_message=spot_msg,
        share_caption=f"I found today's {req.target_color} with ThiSpot.",
    )


@app.get("/health")
def health():
    return ok({"message": "ThiSpot backend is running"})


@app.post("/api/analyze-photo")
async def analyze_photo(
    user_id: str = Form(...),
    session_id: str = Form(...),
    target_color: str = Form(...),
    lat: float = Form(...),
    lng: float = Form(...),
    photo: UploadFile = File(...),
):
    raw = await photo.read()

    tmp_path: Path | None = None
    photo_id: str | None = None

    try:
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)

        vision_result, vision_trace = _vision_agent.run(tmp_path, target_color)

        # Persist photo for badge generation at finish-walk
        photo_id = uuid.uuid4().hex[:12]
        session_upload_dir = _UPLOADS / session_id
        session_upload_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy(tmp_path, session_upload_dir / f"{photo_id}.jpg")

    except Exception:
        vision_result, vision_trace = _vision_agent.fallback(target_color)
    finally:
        if tmp_path is not None:
            tmp_path.unlink(missing_ok=True)

    discovery_result, discovery_msg = discovery_agent.run(target_color, lat, lng)

    data = {
        "photo_id": photo_id,
        "vision_result": vision_result.model_dump(),
        "discovery_result": discovery_result.model_dump(),
        "agent_trace": [
            vision_trace.model_dump(),
            make_trace("DiscoveryAgent", discovery_msg),
        ],
    }
    return ok(data)


@app.post("/api/test/generate-badge")
async def test_generate_badge(
    target_color: str = Form(default="blue"),
    photo: UploadFile = File(...),
):
    """Test endpoint — upload a photo and get a badge image back immediately."""
    raw = await photo.read()
    api_key = os.getenv("GEMINI_API_KEY")

    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)

        keywords = extract_structured_keywords([tmp_path], api_key, target_color=target_color) if api_key else []
        prompt = build_badge_prompt(
            title=f"{target_color.capitalize()} Test Badge",
            color=target_color,
            rarity="rare",
            keywords=keywords or None,
        )

        out_path = _OUTPUTS / "test" / f"badge_test_{uuid.uuid4().hex[:8]}.png"
        success = generate_badge_image(prompt, out_path)

    finally:
        if tmp_path:
            tmp_path.unlink(missing_ok=True)

    return ok({
        "success": success,
        "badge_url": f"{BASE_URL}/outputs/test/{out_path.name}" if success else None,
        "keywords": keywords,
        "prompt": prompt,
    })


@app.post("/api/finish-walk")
def finish_walk(req: FinishWalkRequest):
    trace = []

    photo_paths = get_photo_paths(req.session_id, req.photo_ids)

    badge, reward_trace = _reward_agent.run(
        color=req.target_color,
        is_new_spot=req.is_new_spot,
        match_score=req.best_match_score,
        session_id=req.session_id,
        photo_paths=photo_paths or None,
        base_url=BASE_URL,
    )
    trace.append(reward_trace)

    content_input = ContentGenerationInput(
        session_id=req.session_id,
        target_color=req.target_color,
        distance_m=req.distance_m,
        steps=req.steps,
        duration_sec=req.duration_sec,
        best_match_score=req.best_match_score,
        badge_title=badge.title,
    )
    report, content_trace = _content_agent.run(content_input, base_url=BASE_URL)
    trace.append(content_trace)

    return ok(
        {
            "badge": badge.model_dump(),
            "summary": _build_summary(req).model_dump(),
            "report": report.model_dump(),
            "agent_trace": [t.model_dump() for t in trace],
        }
    )
