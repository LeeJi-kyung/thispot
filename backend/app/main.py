import tempfile
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from app.agents import discovery_agent  # noqa: E402
from app.agents.vision_mission_agent import VisionMissionAgent  # noqa: E402
from app.harness.trace import make_trace  # noqa: E402
from app.models.schemas import ok  # noqa: E402

app = FastAPI(title="ThiSpot Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_vision_agent = VisionMissionAgent()


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
    try:
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp.write(raw)
            tmp_path = Path(tmp.name)
        vision_result, vision_trace = _vision_agent.run(tmp_path, target_color)
    except Exception:
        vision_result, vision_trace = _vision_agent.fallback(target_color)
    finally:
        if tmp_path is not None:
            tmp_path.unlink(missing_ok=True)

    discovery_result, discovery_msg = discovery_agent.run(target_color, lat, lng)

    data = {
        "vision_result": vision_result.model_dump(),
        "discovery_result": discovery_result.model_dump(),
        "agent_trace": [
            vision_trace.model_dump(),
            make_trace("DiscoveryAgent", discovery_msg),
        ],
    }
    return ok(data)
