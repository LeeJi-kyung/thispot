from io import BytesIO
from uuid import uuid4

from fastapi.testclient import TestClient
from PIL import Image

from app.main import app
from app.skills.report_render_skill import ReportRenderSkill


client = TestClient(app)


def image_bytes(rgb: tuple[int, int, int]) -> bytes:
    buffer = BytesIO()
    Image.new("RGB", (80, 80), rgb).save(buffer, format="JPEG")
    return buffer.getvalue()


def test_health() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "thispot-backend"}


def test_login_demo_contract() -> None:
    response = client.post("/api/login-demo", json={"nickname": "Hayoon"})
    body = response.json()

    assert response.status_code == 200
    assert body["user_id"] == "demo_user"
    assert body["nickname"] == "Hayoon"
    assert body["character"]["name"] == "Spotter"
    assert body["character"]["base_image_url"].endswith("/assets/character/base.png")


def test_recommend_color_contract() -> None:
    response = client.post(
        "/api/recommend-color",
        json={"user_id": "demo_user", "previous_colors": ["red", "green", "blue"]},
    )
    body = response.json()

    assert response.status_code == 200
    assert body == {
        "target_color": "red",
        "mission_title": "Red Energy Walk",
        "mission_text": "Find red moments during today's walk.",
        "character_outfit_color": "red",
    }


def test_recommend_color_is_demo_red_for_any_history() -> None:
    for previous_colors in [
        ["blue", "yellow", "orange"],
        ["red", "blue", "yellow", "orange"],
        ["red", "green", "blue", "yellow", "orange"],
    ]:
        response = client.post(
            "/api/recommend-color",
            json={"user_id": "demo_user", "previous_colors": previous_colors},
        )
        body = response.json()

        assert response.status_code == 200
        assert body["target_color"] == "red"


def test_analyze_photo_contract() -> None:
    session_id = f"session_analyze_contract_{uuid4().hex}"
    response = client.post(
        "/api/analyze-photo",
        data={
            "user_id": "demo_user",
            "session_id": session_id,
            "target_color": "blue",
            "lat": "37.5665",
            "lng": "126.9780",
        },
        files={"photo": ("photo.jpg", image_bytes((59, 130, 246)), "image/jpeg")},
    )
    body = response.json()

    assert response.status_code == 200
    assert body["photo_id"].startswith("photo_")
    assert body["proof_result"]["accepted"] is True
    assert body["proof_result"]["accepted_count"] >= 1
    assert body["proof_result"]["required_count"] == 3
    assert body["proof_result"]["remaining_count"] <= 2
    assert body["proof_result"]["completion_unlocked"] in {False, True}
    assert body["vision_result"]["detected_color"] == "blue"
    assert body["vision_result"]["match_score"] >= 0.70
    assert body["vision_result"]["is_matched"] is True
    assert body["vision_result"]["object_label"]
    assert "discovery_result" in body
    assert body["agent_trace"][0]["agent"] == "VisionMissionAgent"
    assert body["agent_trace"][1]["agent"] == "DiscoveryAgent"


def test_rejected_photo_does_not_count_as_accepted_proof() -> None:
    session_id = f"session_rejected_proof_{uuid4().hex}"
    response = client.post(
        "/api/analyze-photo",
        data={
            "user_id": "demo_user",
            "session_id": session_id,
            "target_color": "blue",
        },
        files={"photo": ("photo.jpg", image_bytes((239, 68, 68)), "image/jpeg")},
    )
    body = response.json()

    assert response.status_code == 200
    assert body["proof_result"]["accepted"] is False
    assert body["proof_result"]["accepted_count"] == 0
    assert body["proof_result"]["remaining_count"] == 3
    assert body["proof_result"]["completion_unlocked"] is False


def test_analyze_photo_supports_white_and_black_colors() -> None:
    for color, label in [("white", "cloud"), ("black", "shadow")]:
        response = client.post(
            "/api/analyze-photo",
            data={
                "user_id": "demo_user",
                "session_id": f"session_{color}_{uuid4().hex}",
                "target_color": color,
            },
            files={
                "photo": (
                    "photo.jpg",
                    image_bytes((241, 245, 249) if color == "white" else (15, 23, 42)),
                    "image/jpeg",
                )
            },
        )
        body = response.json()

        assert response.status_code == 200
        assert body["vision_result"]["detected_color"] == color
        assert "object_label" in body["vision_result"]


def test_analyze_photo_rejects_wrong_multipart_field_name() -> None:
    response = client.post(
        "/api/analyze-photo",
        data={
            "user_id": "demo_user",
            "session_id": "session_123",
            "target_colour": "blue",
        },
        files={"photo": ("photo.jpg", image_bytes((59, 130, 246)), "image/jpeg")},
    )

    assert response.status_code == 422


def test_analyze_photo_rejects_invalid_uploads() -> None:
    response = client.post(
        "/api/analyze-photo",
        data={
            "user_id": "demo_user",
            "session_id": "session_123",
            "target_color": "blue",
        },
        files={"photo": ("photo.txt", b"not an image", "text/plain")},
    )

    assert response.status_code == 415

    response = client.post(
        "/api/analyze-photo",
        data={
            "user_id": "demo_user",
            "session_id": "session_123",
            "target_color": "blue",
        },
        files={"photo": ("photo.jpg", b"not an image", "image/jpeg")},
    )

    assert response.status_code == 400


def test_finish_walk_contract_and_static_outputs(monkeypatch) -> None:
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    session_id = f"session_finish_contract_{uuid4().hex}"
    user_id = f"archive_user_{uuid4().hex}"
    photo_ids = []
    for _ in range(3):
        photo_response = client.post(
            "/api/analyze-photo",
            data={
                "user_id": user_id,
                "session_id": session_id,
                "target_color": "blue",
                "lat": "37.5665",
                "lng": "126.9780",
            },
            files={"photo": ("photo.jpg", image_bytes((59, 130, 246)), "image/jpeg")},
        )
        assert photo_response.status_code == 200
        proof_body = photo_response.json()
        photo_ids.append(proof_body["photo_id"])

    assert proof_body["proof_result"]["accepted_count"] == 3
    assert proof_body["proof_result"]["remaining_count"] == 0
    assert proof_body["proof_result"]["completion_unlocked"] is True

    response = client.post(
        "/api/finish-walk",
        json={
            "user_id": user_id,
            "session_id": session_id,
            "target_color": "blue",
            "distance_m": 1240,
            "steps": 1843,
            "duration_sec": 720,
            "photo_ids": photo_ids,
            "best_match_score": 0.87,
            "is_new_spot": True,
        },
    )
    body = response.json()

    assert response.status_code == 200
    assert body["badge"]["title"] == "Blue First Finder"
    assert body["badge"]["rarity"] == "rare"
    assert "image_url" in body["badge"]
    assert body["badge"]["image_url"] is None
    assert body["summary"]["subtitle"] == "1.24km - 1,843 steps - 87% color match"
    assert {
        "status",
        "type",
        "video_url",
        "image_url",
        "thumbnail_url",
        "share_media_url",
        "share_media_type",
        "can_share_to_instagram_story",
        "generation_job_id",
        "shortform_prompt",
        "style",
        "caption",
        "storyboard",
    }.issubset(body["report"])
    assert body["report"]["type"] in {"image", "video"}
    assert body["report"]["status"] in {"completed", "fallback"}
    assert body["report"]["image_url"].endswith(f"/outputs/reports/{session_id}.jpg")
    assert body["report"]["thumbnail_url"].endswith(f"/outputs/reports/{session_id}_thumb.jpg")
    assert body["report"]["share_media_url"]
    assert body["report"]["share_media_type"] in {"image", "video"}
    assert body["report"]["can_share_to_instagram_story"] is True
    if body["report"]["type"] == "video":
        assert body["report"]["share_media_url"] == body["report"]["video_url"]
        assert body["report"]["share_media_type"] == "video"
    else:
        assert body["report"]["share_media_url"] == body["report"]["image_url"]
        assert body["report"]["share_media_type"] == "image"
    assert body["report"]["shortform_prompt"]
    assert body["report"]["style"] == "color-hunt vlog recap"
    assert body["report"]["caption"].startswith("POV:")
    assert len(body["report"]["storyboard"]) == 5
    assert body["report"]["generation_job_id"]
    assert body["agent_trace"][0]["agent"] == "RewardAgent"
    assert body["agent_trace"][1]["agent"] == "ContentGenerationAgent"
    assert body["agent_trace"][1]["status"] == "fallback"

    assert client.get("/assets/character/base.png").status_code == 200
    assert client.get(f"/outputs/reports/{session_id}.jpg").status_code == 200
    assert client.get(f"/outputs/reports/{session_id}_thumb.jpg").status_code == 200
    share_path = body["report"]["share_media_url"].replace("http://localhost:8000", "")
    assert client.get(share_path).status_code == 200

    job_response = client.get(f"/api/generation-jobs/{body['report']['generation_job_id']}")
    job_body = job_response.json()

    assert job_response.status_code == 200
    assert job_body["status"] == "fallback"
    assert job_body["report"]["image_url"] == body["report"]["image_url"]

    archive_response = client.get(f"/api/walk-archive/{user_id}")
    archive_body = archive_response.json()

    assert archive_response.status_code == 200
    assert archive_body["user_id"] == user_id
    assert archive_body["total"] == 1
    archived = archive_body["items"][0]
    assert archived["session_id"] == session_id
    assert archived["date"]
    assert archived["target_color"] == "blue"
    assert archived["distance_m"] == 1240
    assert archived["steps"] == 1843
    assert archived["duration_sec"] == 720
    assert archived["best_match_score"] == 0.87
    assert archived["badge"]["title"] == body["badge"]["title"]
    assert archived["summary"]["title"] == body["summary"]["title"]
    assert archived["report"]["image_url"] == body["report"]["image_url"]
    assert len(archived["photos"]) == 3
    first_photo_path = archived["photos"][0]["image_url"].replace("http://localhost:8000", "")
    assert first_photo_path.startswith("/uploads/")
    assert client.get(first_photo_path).status_code == 200


def test_finish_walk_requires_three_accepted_proofs() -> None:
    session_id = f"session_not_complete_{uuid4().hex}"
    for _ in range(2):
        response = client.post(
            "/api/analyze-photo",
            data={
                "user_id": "demo_user",
                "session_id": session_id,
                "target_color": "blue",
            },
            files={"photo": ("photo.jpg", image_bytes((59, 130, 246)), "image/jpeg")},
        )
        assert response.status_code == 200

    response = client.post(
        "/api/finish-walk",
        json={
            "user_id": "demo_user",
            "session_id": session_id,
            "target_color": "blue",
            "distance_m": 1240,
            "steps": 1843,
            "duration_sec": 720,
            "photo_ids": [],
            "best_match_score": 0.87,
            "is_new_spot": True,
        },
    )

    assert response.status_code == 409
    assert "MISSION_NOT_COMPLETE" in response.json()["detail"]


def test_gps_discovery_records_new_then_shared_spot() -> None:
    lat = 11 + (uuid4().int % 1000) / 10000
    lng = 121 + (uuid4().int % 1000) / 10000

    first = client.post(
        "/api/analyze-photo",
        data={
            "user_id": "gps_user_a",
            "session_id": f"session_gps_a_{uuid4().hex}",
            "target_color": "green",
            "lat": str(lat),
            "lng": str(lng),
        },
        files={"photo": ("photo.jpg", image_bytes((34, 197, 94)), "image/jpeg")},
    )
    first_body = first.json()

    assert first.status_code == 200
    assert first_body["proof_result"]["accepted"] is True
    assert first_body["discovery_result"]["is_new_spot"] is True

    second = client.post(
        "/api/analyze-photo",
        data={
            "user_id": "gps_user_b",
            "session_id": f"session_gps_b_{uuid4().hex}",
            "target_color": "green",
            "lat": str(lat + 0.00001),
            "lng": str(lng + 0.00001),
        },
        files={"photo": ("photo.jpg", image_bytes((34, 197, 94)), "image/jpeg")},
    )
    second_body = second.json()

    assert second.status_code == 200
    assert second_body["proof_result"]["accepted"] is True
    assert second_body["discovery_result"]["is_new_spot"] is False
    assert second_body["discovery_result"]["shared_user_percent"] > 8
    assert second_body["discovery_result"]["message"] == "Shared Green Spot found nearby."


def test_generation_job_not_found() -> None:
    response = client.get("/api/generation-jobs/missing")

    assert response.status_code == 404


def test_static_demo_report_does_not_render_on_fallback(monkeypatch) -> None:
    def fail_render(*args, **kwargs):
        raise AssertionError("static fallback must not call render_image_report")

    monkeypatch.setattr(ReportRenderSkill, "render_image_report", fail_render)

    report = ReportRenderSkill().static_demo_report()

    assert report.image_url.endswith("/outputs/reports/static_demo_report.jpg")
    assert report.thumbnail_url.endswith("/outputs/reports/static_demo_report_thumb.jpg")
