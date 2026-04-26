import io

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image

from app.agents import discovery_agent, vision_mission_agent
from app.harness.trace import make_trace
from app.models.schemas import ok

app = FastAPI(title="ThiSpot Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
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
    try:
        raw = await photo.read()
        image = Image.open(io.BytesIO(raw))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image file.")

    vision_result, vision_msg = vision_mission_agent.run(image, target_color)
    discovery_result, discovery_msg = discovery_agent.run(target_color, lat, lng)

    trace = [
        make_trace("VisionMissionAgent", vision_msg),
        make_trace("DiscoveryAgent", discovery_msg),
    ]

    data = {
        "vision_result": vision_result.model_dump(),
        "discovery_result": discovery_result.model_dump(),
        "agent_trace": trace,
    }
    return ok(data)
