# ThiSpot MVP Architecture

## System Boundary

```text
iOS app
  - demo login / character start screen
  - today's color mission
  - character outfit/theme color update
  - GPS / pedometer walk tracking
  - in-app camera
  - agent timeline
  - walk result, badge, short video or image report

Python backend
  - FastAPI routes
  - agent harness orchestrator
  - vision mission proof
  - mock spot discovery
  - badge generation
  - short-form video or image report generation
```

The backend is the source of truth for agent outputs. The iOS app must support mock responses while backend lanes are still in progress.

## Core Data Flow

```text
demo login
-> PersonalWalkAgent creates mission
-> iOS starts walk and captures photo
-> VisionMissionAgent verifies photo proof
-> DiscoveryAgent checks spot status
-> iOS ends walk
-> RewardAgent creates badge
-> ContentGenerationAgent creates report
-> iOS shows shareable reward
```

## Backend Layout

```text
backend/
  app/
    main.py
    models/schemas.py
    harness/context.py
    harness/orchestrator.py
    harness/trace.py
    agents/personal_walk_agent.py
    agents/vision_mission_agent.py
    agents/discovery_agent.py
    agents/reward_agent.py
    agents/content_generation_agent.py
    skills/image_color_skill.py
    skills/color_match_skill.py
    skills/object_label_skill.py
    skills/geo_distance_skill.py
    skills/spot_similarity_skill.py
    skills/badge_skill.py
    skills/report_render_skill.py
    storage/mock_spots.py
    storage/sessions.py
    assets/character/
    outputs/videos/
    outputs/reports/
    uploads/
```

## iOS Layout

```text
ThiSpot/
  Models/
    WalkModels.swift
    AgentModels.swift
  Services/
    APIClient.swift
    WalkTrackingService.swift
    CameraService.swift
  ViewModels/
    WalkSessionViewModel.swift
  Views/
    LoginStartView.swift
    ColorMissionView.swift
    WalkTrackingView.swift
    CameraCaptureView.swift
    AgentTimelineView.swift
    WalkResultView.swift
    ReportPreviewView.swift
```

## Canonical Data Models

Core walk session:

```json
{
  "user_id": "demo_user",
  "session_id": "session_123",
  "target_color": "blue",
  "distance_m": 1240,
  "steps": 1843,
  "duration_sec": 720
}
```

Vision mission result:

```json
{
  "detected_color": "blue",
  "match_score": 0.87,
  "is_matched": true,
  "object_label": "sky",
  "feedback": "Blue sky detected. This fits today's mission."
}
```

Agent trace:

```json
{
  "agent": "ContentGenerationAgent",
  "status": "completed",
  "message": "Short-form report generated"
}
```

## Harness Context

```python
class WalkHarnessContext(BaseModel):
    user_id: str
    session_id: str
    target_color: str
    character_id: str | None = None
    lat: float | None = None
    lng: float | None = None
    distance_m: float | None = None
    steps: int | None = None
    duration_sec: int | None = None
    photo_paths: list[str] = []
    vision_result: dict | None = None
    discovery_result: dict | None = None
    badge: dict | None = None
    report: dict | None = None
    trace: list[dict] = []
```

## Failure Policy

- GPS unavailable: use demo route while keeping walk UI active.
- Step count unavailable: use simulated steps.
- Camera unavailable: use bundled demo photo.
- Backend unavailable: use mock agent result in iOS.
- MP4 generation fails: return image report.
- Image report generation fails: return static demo report URL.

## Quality Gates

1. `/api/recommend-color` returns in under 300ms.
2. `/api/analyze-photo` accepts multipart upload and returns `vision_result`, `discovery_result`, `agent_trace`.
3. `/api/finish-walk` returns `badge`, `summary`, `report`, `agent_trace`.
4. iOS can complete the demo with backend down by using fixed mock responses.
5. Demo fallback target is `blue`, match score `0.87`, distance `1.24km`, steps `1,843`.
6. Content generation failure falls back to an image report.
