from pathlib import Path

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.harness.orchestrator import WalkHarnessOrchestrator
from app.models.schemas import (
    AnalyzePhotoResponse,
    FinishWalkRequest,
    FinishWalkResponse,
    LoginDemoRequest,
    LoginDemoResponse,
    RecommendColorRequest,
    RecommendColorResponse,
)
from app.skills.report_render_skill import ReportRenderSkill
from app.storage.sessions import ensure_storage_dirs, save_uploaded_photo


APP_DIR = Path(__file__).resolve().parent
REPORTS_DIR = APP_DIR / "outputs" / "reports"
VIDEOS_DIR = APP_DIR / "outputs" / "videos"
CHARACTER_DIR = APP_DIR / "assets" / "character"


app = FastAPI(title="ThiSpot Backend", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = WalkHarnessOrchestrator()


def ensure_demo_assets() -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
    CHARACTER_DIR.mkdir(parents=True, exist_ok=True)
    ensure_storage_dirs()
    ReportRenderSkill().ensure_demo_assets()


ensure_demo_assets()

app.mount("/outputs/reports", StaticFiles(directory=REPORTS_DIR), name="reports")
app.mount("/outputs/videos", StaticFiles(directory=VIDEOS_DIR), name="videos")
app.mount("/assets/character", StaticFiles(directory=CHARACTER_DIR), name="character")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "thispot-backend"}


@app.post("/api/login-demo", response_model=LoginDemoResponse)
def login_demo(request: LoginDemoRequest) -> LoginDemoResponse:
    return orchestrator.login_demo(request.nickname)


@app.post("/api/recommend-color", response_model=RecommendColorResponse)
def recommend_color(request: RecommendColorRequest) -> RecommendColorResponse:
    return orchestrator.recommend_color(request)


@app.post("/api/analyze-photo", response_model=AnalyzePhotoResponse)
async def analyze_photo(
    user_id: str = Form("demo_user"),
    session_id: str = Form("session_123"),
    target_color: str = Form("blue"),
    lat: float | None = Form(None),
    lng: float | None = Form(None),
    photo: UploadFile = File(...),
) -> AnalyzePhotoResponse:
    try:
        photo_path = await save_uploaded_photo(session_id, photo)
        return orchestrator.analyze_photo(
            user_id=user_id,
            session_id=session_id,
            target_color=target_color,
            lat=lat,
            lng=lng,
            photo_path=photo_path,
        )
    except Exception:
        return orchestrator.analyze_photo_fallback(target_color)


@app.post("/api/finish-walk", response_model=FinishWalkResponse)
def finish_walk(request: FinishWalkRequest) -> FinishWalkResponse:
    try:
        return orchestrator.finish_walk(request)
    except Exception:
        return orchestrator.finish_walk_fallback()
