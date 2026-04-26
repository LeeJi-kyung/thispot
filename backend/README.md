# ThiSpot Backend

FastAPI harness backend for the ThiSpot MVP.

Mission colors: `red`, `orange`, `yellow`, `green`, `blue`, `violet`,
`white`, `black`.

## Setup

Recommended demo path: run the backend in Docker so Python, `ffmpeg`, and
dependency versions are fixed.

```bash
cd backend
docker compose up --build
```

Then open `http://localhost:8000/health`.

The compose file uses Docker named volumes for app data, uploads, and generated
reports. This keeps sessions, proof progress, generation jobs, and discovered
GPS spots available across container restarts.

Generated absolute URLs use `THISPOT_BASE_URL`, defaulting to
`http://localhost:8000`.

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

`VisionMissionAgent` and `ContentGenerationAgent` use Gemini when
`GEMINI_API_KEY` is set. Vision uses Gemini to judge whether the uploaded photo
proves the target color mission. Content generation uses Gemini for storyboard,
captions, style, and downstream video prompt. If the key is missing or the API
call fails, the backend uses deterministic/local fallbacks and marks the related
agent trace as `fallback`.

```bash
export GEMINI_API_KEY="your-key"
export GEMINI_MODEL="gemini-2.5-flash"
```

Gemini output is exposed in the public `report` response as `shortform_prompt`,
`style`, `caption`, and `storyboard`. If Gemini is unavailable or fails, the
same fields are filled by a deterministic local plan and `agent_trace` marks the
content step as `fallback`.

## Instagram Story Share Contract

`/api/finish-walk` returns report fields that let iOS enable the Instagram Story
share button without guessing which artifact to use:

```json
{
  "status": "completed",
  "type": "video",
  "video_url": "http://localhost:8000/outputs/videos/session_123.mp4",
  "image_url": "http://localhost:8000/outputs/reports/session_123.jpg",
  "thumbnail_url": "http://localhost:8000/outputs/reports/session_123_thumb.jpg",
  "share_media_url": "http://localhost:8000/outputs/videos/session_123.mp4",
  "share_media_type": "video",
  "can_share_to_instagram_story": true
}
```

If MP4 generation is unavailable, `share_media_url` points to `image_url` and
`share_media_type` is `image`. iOS should enable the share button when
`can_share_to_instagram_story` is true and `status` is `completed` or
`fallback`.

## Verify

```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/api/login-demo -H "Content-Type: application/json" -d '{"nickname":"Hayoon"}'
curl -X POST http://localhost:8000/api/recommend-color -H "Content-Type: application/json" -d '{"user_id":"demo_user","previous_colors":["red","green","blue"]}'
curl -X POST http://localhost:8000/api/analyze-photo -F user_id=demo_user -F session_id=session_123 -F target_color=blue -F photo=@/absolute/path/to/photo.jpg
curl -X POST http://localhost:8000/api/finish-walk -H "Content-Type: application/json" -d '{"user_id":"demo_user","session_id":"session_123","target_color":"blue","distance_m":1240,"steps":1843,"duration_sec":720,"photo_ids":[],"best_match_score":0.87,"is_new_spot":true}'
curl http://localhost:8000/api/walk-archive/demo_user
curl http://localhost:8000/api/generation-jobs/{generation_job_id}
```

For real photo testing, upload one or more photos with the same `session_id`,
then call `/api/finish-walk` with `photo_ids: []`. Only accepted proofs count,
and `/api/finish-walk` returns `409 MISSION_NOT_COMPLETE` until the session has
5 accepted proofs. The backend uses those accepted proof photos for the
generated report/MP4.

## GPS Discovery

`/api/analyze-photo` accepts optional `lat` and `lng`. Accepted proofs with GPS
are persisted as color spots in `app/data/spots.json`. A later accepted proof
with the same target color within 50m is returned as a shared spot; otherwise it
creates a new spot. This replaces fixed mock spots while keeping the public
`discovery_result` contract unchanged.

## Walk Archive

Successful `/api/finish-walk` calls are archived in `app/data/walk_archive.json`.
Use `GET /api/walk-archive/{user_id}` to fetch previous walks for the profile.
Each archive item includes:

- `created_at` and `date`
- `target_color`
- `distance_m`, `steps`, `duration_sec`, `best_match_score`
- accepted proof photo URLs from `/uploads/{filename}`
- generated `report`
- `badge` and `summary`

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
- `GET /api/walk-archive/{user_id}`
- `GET /api/generation-jobs/{job_id}`
- `GET /outputs/reports/{filename}`
- `GET /outputs/videos/{filename}`
- `GET /assets/character/{filename}`
- `GET /uploads/{filename}`

Provider fallbacks are explicit in `agent_trace`. `VisionMissionAgent` uses
Gemini when `GEMINI_API_KEY` is configured and falls back to local Pillow color
matching if Gemini is unavailable. If verification cannot run at all, the photo
is not accepted as mission proof.
