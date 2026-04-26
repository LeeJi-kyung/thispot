# ThiSpot Backend

FastAPI harness backend for the ThiSpot MVP.

## Setup

Recommended demo path: run the backend in Docker so Python, `ffmpeg`, and
dependency versions are fixed.

```bash
cd backend
docker compose up --build
```

Then open `http://localhost:8000/health`.

The compose file uses Docker named volumes for uploads and generated reports.
This avoids macOS bind-mount write errors during Pillow/ffmpeg rendering.

Local setup requires Python 3.12 or 3.13. Do not use the system `python3` if it
resolves to Python 3.7.

```bash
cd backend
python3.13 -m venv .venv313
source .venv313/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

If `.venv313` already exists, activate it directly and run the same `uvicorn`
command.

## Gemini Short-Form Direction

`ContentGenerationAgent` uses Gemini when `GEMINI_API_KEY` is set. Gemini creates
the short-form storyboard, captions, style, and downstream video prompt. If the
key is missing or the API call fails, the backend returns a deterministic demo
storyboard so the app and demo keep working.

```bash
export GEMINI_API_KEY="your-key"
export GEMINI_MODEL="gemini-2.5-flash"
```

## Verify

```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/api/login-demo -H "Content-Type: application/json" -d '{"nickname":"Hayoon"}'
curl -X POST http://localhost:8000/api/recommend-color -H "Content-Type: application/json" -d '{"user_id":"demo_user","previous_colors":["red","green","blue"]}'
curl -X POST http://localhost:8000/api/finish-walk -H "Content-Type: application/json" -d '{"user_id":"demo_user","session_id":"session_123","target_color":"blue","distance_m":1240,"steps":1843,"duration_sec":720,"photo_ids":[],"best_match_score":0.87,"is_new_spot":true}'
```

Run contract tests inside Docker:

```bash
docker compose run --rm api pytest -q
```

## Routes

- `GET /health`
- `POST /api/login-demo`
- `POST /api/recommend-color`
- `POST /api/analyze-photo`
- `POST /api/finish-walk`
- `GET /outputs/reports/{filename}`
- `GET /outputs/videos/{filename}`
- `GET /assets/character/{filename}`

The backend uses deterministic demo fallbacks. `VisionMissionAgent` is intentionally a stub for the hackathon demo and does not perform real image analysis.
