# ThiSpot Agent Roster

These are the shared agents for the ThiSpot MVP. Each agent must expose typed input/output, append trace messages, and support deterministic fallback data for the live demo.

## 1. PersonalWalkAgent

Purpose: choose today's mission color and character color styling.

Input:

```json
{
  "user_id": "demo_user",
  "previous_colors": ["red", "green", "blue"]
}
```

Output:

```json
{
  "target_color": "yellow",
  "mission_title": "Yellow Energy Walk",
  "mission_text": "Find yellow moments during today's walk.",
  "character_outfit_color": "yellow"
}
```

Rule: select from `red, orange, yellow, green, blue, indigo, violet`; prefer colors not present in the last 3 records.

## 2. VisionMissionAgent

Purpose: verify whether a captured photo proves today's color mission and explain what was found.

Skills:

- ImageColorSkill: extract dominant RGB and palette.
- ColorMatchSkill: compare palette against target color.
- ObjectLabelSkill: return a simple object label from image metadata, a vision model, or deterministic fallback.

Output:

```json
{
  "detected_color": "blue",
  "match_score": 0.87,
  "is_matched": true,
  "object_label": "sky",
  "feedback": "Blue sky detected. This fits today's mission."
}
```

MVP rule: `match_score >= 0.70` means success.

## 3. DiscoveryAgent

Purpose: use GPS and vision result to decide whether the user found a new/shared color spot.

Skills:

- GeoDistanceSkill: compute nearest mock spot distance.
- SpotSimilaritySkill: combine distance, color, and object label.

MVP rule:

```text
same color within 50m -> shared spot
no same color within 50m -> new spot
```

Output:

```json
{
  "is_new_spot": true,
  "shared_user_percent": 8,
  "message": "New Blue Spot discovered."
}
```

## 4. RewardAgent

Purpose: generate badge and result copy from walk summary.

Output:

```json
{
  "title": "Blue Finder",
  "description": "You found today's blue during your walk.",
  "rarity": "rare"
}
```

Badge priority:

```text
new spot + match >= 0.85 -> rare First Finder badge
match >= 0.70 -> standard Finder badge
otherwise -> Try Again badge
```

## 5. ContentGenerationAgent

Purpose: create a short-form recap video or image report after walk completion.

Inputs:

```text
character asset
target color
walk summary
captured photos
route snapshot or mock route
badge
```

Minimum output:

```json
{
  "type": "video",
  "video_url": "http://localhost:8000/outputs/videos/session_123.mp4",
  "image_url": "http://localhost:8000/outputs/reports/session_123.jpg",
  "thumbnail_url": "http://localhost:8000/outputs/reports/session_123_thumb.jpg"
}
```

Fallback: if MP4 export fails, return an image report. If image rendering also fails, return a static demo report URL.

## 6. WalkHarnessOrchestrator

Purpose: run agents, preserve trace, and return API-compatible responses.

Photo analysis sequence:

```text
VisionMissionAgent
-> DiscoveryAgent
-> response with trace
```

Finish-walk sequence:

```text
RewardAgent
-> ContentGenerationAgent
-> response with trace
```

Trace format:

```json
{
  "agent": "VisionMissionAgent",
  "status": "completed",
  "message": "Blue sky detected - 87% match"
}
```
