from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


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
        "target_color": "yellow",
        "mission_title": "Yellow Energy Walk",
        "mission_text": "Find yellow moments during today's walk.",
        "character_outfit_color": "yellow",
    }


def test_analyze_photo_contract() -> None:
    response = client.post(
        "/api/analyze-photo",
        data={
            "user_id": "demo_user",
            "session_id": "session_123",
            "target_color": "blue",
            "lat": "37.5665",
            "lng": "126.9780",
        },
        files={"photo": ("photo.jpg", b"demo-photo", "image/jpeg")},
    )
    body = response.json()

    assert response.status_code == 200
    assert body["vision_result"]["detected_color"] == "blue"
    assert body["vision_result"]["match_score"] == 0.87
    assert body["vision_result"]["is_matched"] is True
    assert body["vision_result"]["object_label"] == "sky"
    assert "discovery_result" in body
    assert body["agent_trace"][0]["agent"] == "VisionMissionAgent"
    assert body["agent_trace"][1]["agent"] == "DiscoveryAgent"


def test_finish_walk_contract_and_static_outputs() -> None:
    response = client.post(
        "/api/finish-walk",
        json={
            "user_id": "demo_user",
            "session_id": "session_123",
            "target_color": "blue",
            "distance_m": 1240,
            "steps": 1843,
            "duration_sec": 720,
            "photo_ids": ["photo_1", "photo_2"],
            "best_match_score": 0.87,
            "is_new_spot": True,
        },
    )
    body = response.json()

    assert response.status_code == 200
    assert body["badge"]["title"] == "Blue First Finder"
    assert body["badge"]["rarity"] == "rare"
    assert body["summary"]["subtitle"] == "1.24km - 1,843 steps - 87% color match"
    assert body["report"]["type"] in {"image", "video"}
    assert body["report"]["image_url"].endswith("/outputs/reports/session_123.jpg")
    assert body["report"]["thumbnail_url"].endswith("/outputs/reports/session_123_thumb.jpg")
    assert body["agent_trace"][0]["agent"] == "RewardAgent"
    assert body["agent_trace"][1]["agent"] == "ContentGenerationAgent"

    assert client.get("/assets/character/base.png").status_code == 200
    assert client.get("/outputs/reports/session_123.jpg").status_code == 200
    assert client.get("/outputs/reports/session_123_thumb.jpg").status_code == 200
