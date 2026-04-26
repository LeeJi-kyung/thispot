---
name: deployment
description: "ThiSpot ContentGenerationAgent for short-form video, image report, and static output serving."
---

# ThiSpot ContentGenerationAgent Skill

Use this skill for the short-form video and image report agent.

## Goal

Create a shareable reward from character, walk photos, route snapshot/mock route, and summary data.

## Input

```json
{
  "session_id": "session_123",
  "target_color": "blue",
  "character_id": "spotter",
  "distance_m": 1240,
  "steps": 1843,
  "duration_sec": 720,
  "best_match_score": 0.87,
  "photo_paths": ["uploads/photo_1.jpg"],
  "badge_title": "Blue Finder"
}
```

## Output

```json
{
  "type": "video",
  "video_url": "http://localhost:8000/outputs/videos/session_123.mp4",
  "image_url": "http://localhost:8000/outputs/reports/session_123.jpg",
  "thumbnail_url": "http://localhost:8000/outputs/reports/session_123_thumb.jpg"
}
```

## MVP Rendering

Preferred: render a 5-8 second slideshow/video.

```text
frame 1: ThiSpot + Today's Color + character
frame 2: best mission photo
frame 3: map/route mock with character walking
frame 4: distance / steps / match score
frame 5: badge + share caption
```

Fallback: generate one Instagram-story-style image report.

Required text:

```text
Today's Color
distance
steps
duration
best match score
badge
ThiSpot logo/name
```

## Static Serving

FastAPI must serve:

```text
/outputs/videos/{filename}
/outputs/reports/{filename}
/assets/character/{filename}
```

## Demo Requirement

The UI only needs to prove that ContentGenerationAgent produced a shareable artifact. If MP4 export is unstable, ship image report first.
