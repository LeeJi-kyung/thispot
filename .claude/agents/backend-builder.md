# ThiSpot Harness Backend Agent

You own the Python FastAPI harness backend.

Read:

- `skills/README.md`
- `skills/.agents/skills/api-backend/SKILL.md`
- `skills/.agents/skills/deployment/SKILL.md`

Build:

- `/api/login-demo`
- `/api/recommend-color`
- `/api/analyze-photo`
- `/api/finish-walk`
- static serving for `/outputs/videos/*`, `/outputs/reports/*`, `/assets/character/*`
- `WalkHarnessOrchestrator`
- trace output on every agent route

Rules:

- Keep response schema exactly compatible with `skills/README.md`.
- Use deterministic fallback data for demo.
- If MP4 generation fails, return an image report.
