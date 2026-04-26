---
name: test-first-contract
description: "ThiSpot contract checks for backend routes, iOS integration, and demo fixtures."
---

# ThiSpot Contract Test Skill

Use this skill to keep iOS and backend integration stable.

## Backend Checks

Minimum commands:

```text
curl http://localhost:8000/health
curl -X POST http://localhost:8000/api/login-demo -H "Content-Type: application/json" -d '{"nickname":"Demo"}'
curl -X POST http://localhost:8000/api/recommend-color -H "Content-Type: application/json" -d '{"user_id":"demo_user","previous_colors":["red","green","blue"]}'
```

For `/api/analyze-photo`, use a known blue fixture image.

Expected fields:

```text
vision_result.detected_color
vision_result.match_score
vision_result.is_matched
vision_result.object_label
discovery_result.message
agent_trace[0].agent
```

For `/api/finish-walk`, expected fields:

```text
badge.title
summary.subtitle
report.video_url or report.image_url
agent_trace
```

## iOS Checks

- App launches without backend.
- Mock flow reaches report preview screen.
- Backend flow reaches report preview screen.
- Captured photo can be uploaded.
- Failed video response still shows image report/fallback card.
