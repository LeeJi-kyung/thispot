---
name: architecture-contract
description: "ThiSpot iOS/backend API contract, schemas, routes, and integration rules."
---

# ThiSpot Architecture Contract Skill

Use this skill before implementation and during integration.

## Required Contract

The iOS app and Python backend must follow `skills/README.md`.

Backend base URL:

```text
http://localhost:8000
```

Routes:

```text
POST /api/login-demo
POST /api/recommend-color
POST /api/analyze-photo
POST /api/finish-walk
GET  /outputs/videos/{file}
GET  /outputs/reports/{file}
GET  /assets/character/{file}
```

## Shared Trace

Every agent endpoint must return `agent_trace` when an agent runs.

```json
{
  "agent": "VisionMissionAgent",
  "status": "completed",
  "message": "Blue sky detected - 87% match"
}
```

## Integration Rule

Never change response field names without updating:

1. `skills/README.md`
2. backend Pydantic schemas
3. iOS API models
4. demo fixtures

## Done Criteria

- iOS can call all 4 POST routes or mock them.
- Backend returns deterministic fixture responses.
- Vision mission proof and content generation can improve the fixture, but cannot break the schema.
