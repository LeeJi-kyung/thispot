"""Contract tests for /api/analyze-photo.

Blue photo (RGB 46,116,230): H≈217°, distance to blue (240°) = 23° → score = 1-23/180 ≈ 0.87
"""

import io

from fastapi.testclient import TestClient
from PIL import Image

from app.main import app

client = TestClient(app)


def _solid_image(rgb: tuple[int, int, int], size: tuple[int, int] = (200, 200)) -> bytes:
    img = Image.new("RGB", size, rgb)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _post_photo(rgb: tuple[int, int, int], target_color: str = "blue") -> dict:
    img_bytes = _solid_image(rgb)
    response = client.post(
        "/api/analyze-photo",
        data={
            "user_id": "test_user",
            "session_id": "test_session",
            "target_color": target_color,
            "lat": "37.5",
            "lng": "127.0",
        },
        files={"photo": ("test.png", img_bytes, "image/png")},
    )
    assert response.status_code == 200
    return response.json()


# ── Blue photo against blue mission ──────────────────────────────────────────

def test_blue_photo_detected_color():
    body = _post_photo((46, 116, 230))
    assert body["status"] == "ok"
    assert body["data"]["vision_result"]["detected_color"] == "blue"


def test_blue_photo_match_score_approx_087():
    body = _post_photo((46, 116, 230))
    score = body["data"]["vision_result"]["match_score"]
    assert 0.84 <= score <= 0.92, f"Expected ≈0.87, got {score}"


def test_blue_photo_is_matched():
    body = _post_photo((46, 116, 230))
    assert body["data"]["vision_result"]["is_matched"] is True


def test_blue_photo_object_label_sky():
    body = _post_photo((46, 116, 230))
    assert body["data"]["vision_result"]["object_label"] == "sky"


# ── Green photo against green mission ────────────────────────────────────────

def test_green_photo_matches_green_mission():
    # RGB(34,139,34) = forest green, H≈120°, score=1.0 against green
    body = _post_photo((34, 139, 34), target_color="green")
    vr = body["data"]["vision_result"]
    assert vr["detected_color"] == "green"
    assert vr["is_matched"] is True
    assert vr["match_score"] >= 0.70


def test_green_photo_object_label_grass():
    body = _post_photo((34, 139, 34), target_color="green")
    assert body["data"]["vision_result"]["object_label"] == "grass"


# ── Off-color: red photo against blue mission ─────────────────────────────────

def test_red_photo_does_not_match_blue_mission():
    # Red (H≈0°) vs blue (240°): dist=120°, score=1-120/180=0.33
    body = _post_photo((220, 50, 50), target_color="blue")
    vr = body["data"]["vision_result"]
    assert vr["is_matched"] is False
    assert vr["match_score"] < 0.70


# ── Response contract ─────────────────────────────────────────────────────────

def test_response_envelope():
    body = _post_photo((46, 116, 230))
    assert "data" in body
    assert "error" in body
    assert "status" in body
    assert body["error"] is None


def test_agent_trace_order():
    body = _post_photo((46, 116, 230))
    trace = body["data"]["agent_trace"]
    assert len(trace) >= 2
    assert trace[0]["agent"] == "VisionMissionAgent"
    assert trace[1]["agent"] == "DiscoveryAgent"


def test_agent_trace_fields():
    body = _post_photo((46, 116, 230))
    for entry in body["data"]["agent_trace"]:
        assert "agent" in entry
        assert "status" in entry
        assert "message" in entry
        assert entry["status"] == "completed"


def test_discovery_result_present():
    body = _post_photo((46, 116, 230))
    dr = body["data"]["discovery_result"]
    assert "is_new_spot" in dr
    assert "shared_user_percent" in dr
    assert "message" in dr


def test_health_endpoint():
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
