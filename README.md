# ThiSpot Agent Skills

This repository defines the shared operating contract for the ThiSpot iOS hackathon MVP.

## Product Definition

**ThiSpot is an AI Color Mission Walk app that turns walking into a daily color mission, verifies real-world photo proof with AI, and generates a character-based short-form reward that users want to share.**

The product is not positioned as a generic walking tracker. The core insight is that people do not keep walking because they know their step count. They keep walking when they have a mission, proof, character progress, and an immediate reward worth sharing.

## Problem

Walking is the easiest exercise, but solo walking is easy to abandon because it is repetitive, lonely, and weakly rewarded. Existing walking apps mostly show numbers such as steps, distance, and calories. Those numbers are useful, but they do not create a strong reason to walk again tomorrow.

ThiSpot solves the motivation gap:

```text
boring solo walk
-> daily color mission
-> AI photo proof
-> character reward
-> shareable short-form memory
-> reason to walk again
```

## Target Users

- 20s users who download fitness apps but do not keep using them
- beginners who find running intimidating but can walk
- users who enjoy taking photos and sharing small daily moments
- people who want a short stress-relief walking routine
- solo walkers who need more mission, discovery, and reward

## Core Demo Flow

```text
App entry / demo login
-> Character appears
-> Today's color mission is recommended
-> Character outfit changes to today's color
-> User starts walking
-> GPS route, step count, and timer begin
-> User captures photos inside the app
-> VisionMissionAgent verifies mission fit
-> User ends walk
-> App shows distance, steps, duration, and photo count
-> DiscoveryAgent reports new/shared color spot
-> RewardAgent awards badge
-> ContentGenerationAgent creates short video or image report
-> User can share to SNS
```

## MVP Priority

Must ship:

1. Demo login or logged-in start state
2. Character on the start screen
3. Today's rainbow color recommendation
4. Character theme/outfit changes to mission color
5. Walk start/end with GPS, steps, timer, or stable fallback
6. In-app photo capture/upload
7. VisionMissionAgent color/object match score
8. Walk result summary
9. Badge reward
10. Short-form video preview or image report generation

Nice to have:

1. Map-based color spot pins
2. First Finder
3. Color Dex
4. Spot Ownership
5. Instagram Story share shortcut

## Tech Stack

```text
iOS: SwiftUI, CoreLocation, CoreMotion, Photos / Camera, MapKit optional, AVPlayer
Backend: Python, FastAPI, Pydantic, Pillow, NumPy, MoviePy or ffmpeg
Harness: typed agents with trace logs
Storage: local mock data and filesystem outputs for demo
```

Do not add real OAuth, production DB, real social graph, complex segmentation, or full generative video for the 7-hour MVP.

## Shared API Contract

Backend runs at `http://localhost:8000`.

### `POST /api/login-demo`

Request:

```json
{
  "nickname": "Hayoon"
}
```

Response:

```json
{
  "user_id": "demo_user",
  "nickname": "Hayoon",
  "character": {
    "name": "Spotter",
    "base_image_url": "http://localhost:8000/assets/character/base.png"
  }
}
```

### `POST /api/recommend-color`

Request:

```json
{
  "user_id": "demo_user",
  "previous_colors": ["red", "green", "blue"]
}
```

Response:

```json
{
  "target_color": "yellow",
  "mission_title": "Yellow Energy Walk",
  "mission_text": "Find yellow moments during today's walk.",
  "character_outfit_color": "yellow"
}
```

### `POST /api/analyze-photo`

Multipart fields:

```text
user_id
session_id
target_color
lat
lng
photo
```

Response:

```json
{
  "vision_result": {
    "detected_color": "blue",
    "match_score": 0.87,
    "is_matched": true,
    "object_label": "sky",
    "feedback": "Blue sky detected. This fits today's mission."
  },
  "discovery_result": {
    "is_new_spot": true,
    "shared_user_percent": 8,
    "message": "New Blue Spot discovered."
  },
  "agent_trace": [
    {
      "agent": "VisionMissionAgent",
      "status": "completed",
      "message": "Blue sky detected - 87% match"
    },
    {
      "agent": "DiscoveryAgent",
      "status": "completed",
      "message": "New Blue Spot discovered"
    }
  ]
}
```

### `POST /api/finish-walk`

Request:

```json
{
  "user_id": "demo_user",
  "session_id": "session_123",
  "target_color": "blue",
  "distance_m": 1240,
  "steps": 1843,
  "duration_sec": 720,
  "photo_ids": ["photo_1", "photo_2"],
  "best_match_score": 0.87,
  "is_new_spot": true
}
```

Response:

```json
{
  "badge": {
    "title": "Blue Finder",
    "description": "You found today's blue during your walk.",
    "rarity": "rare"
  },
  "report": {
    "type": "video",
    "video_url": "http://localhost:8000/outputs/videos/session_123.mp4",
    "image_url": "http://localhost:8000/outputs/reports/session_123.jpg",
    "thumbnail_url": "http://localhost:8000/outputs/reports/session_123_thumb.jpg"
  },
  "summary": {
    "title": "Blue Walk Complete",
    "subtitle": "1.24km - 1,843 steps - 87% color match",
    "spot_message": "New Blue Spot discovered.",
    "share_caption": "I found today's blue with ThiSpot."
  },
  "agent_trace": [
    {
      "agent": "RewardAgent",
      "status": "completed",
      "message": "Blue Finder badge created"
    },
    {
      "agent": "ContentGenerationAgent",
      "status": "completed",
      "message": "Short-form report generated"
    }
  ]
}
```

## Agent Map

```text
PersonalWalkAgent
- picks today's color from rainbow colors
- avoids recent repeats when possible
- updates character outfit/theme color

VisionMissionAgent
- analyzes captured photo
- detects dominant color and simple object label
- verifies mission fit with match score

DiscoveryAgent
- combines GPS, target color, and vision result
- decides new spot vs shared spot
- returns First Finder / shared percent message

RewardAgent
- creates badge and result copy
- uses distance, steps, match score, and new spot status

ContentGenerationAgent
- creates short-form video or image report
- combines character, route, photos, color, and walk summary

WalkHarnessOrchestrator
- runs agent sequence
- stores trace
- returns API-compatible JSON
```

## Business Viability

ThiSpot starts as a B2C walking app, but the stronger business is a color mission platform that moves people into offline spaces.

Revenue paths:

- Brand color challenges: Nike Red Walk, Starbucks Green Walk, Toss Blue Walk
- Local/tourism missions: Seongsu Blue Route, Jeju Green Walk, campus Color Hunt
- Character skins, report templates, seasonal badges
- Company, school, festival, and local government group challenges

GTM:

- university campus color challenge
- company lunch walk challenge
- walking/running crew mission
- local festival color stamp tour
- brand SNS UGC campaign

## Skill Map

```text
.agents/skills/project-intake/SKILL.md          Product scope and sharp positioning
.agents/skills/architecture-contract/SKILL.md   API and model contract
.agents/skills/api-backend/SKILL.md             Python FastAPI harness backend
.agents/skills/systematic-debugging/SKILL.md    VisionMissionAgent
.agents/skills/deployment/SKILL.md              ContentGenerationAgent
.agents/skills/frontend-polish/SKILL.md         iOS SwiftUI client
.agents/skills/test-first-contract/SKILL.md     Contract checks
.agents/skills/demo-readiness/SKILL.md          90-second demo
.agents/skills/code-review/SKILL.md             Integration review
.agents/skills/git-workflow/SKILL.md            cmux multi-agent workflow
```

## cmux Multi-Agent Setup

```text
Lane A - iOS Client
Skill: frontend-polish
Owns: SwiftUI screens, character UI, walk tracking, camera, API integration, result/report UI

Lane B - Vision Mission Agent
Skill: systematic-debugging
Owns: photo upload, color scoring, object feedback, /api/analyze-photo vision output

Lane C - Harness + Content Backend
Skill: api-backend + deployment
Owns: FastAPI app, orchestrator, color recommendation, discovery, reward, video/image report output

Lane D - Integrator/Demo
Skill: demo-readiness + code-review + test-first-contract
Owns: API contract checks, fallback assets, final demo script
```

Recommended cmux prompts:

```text
@ios Read skills/README.md and skills/.agents/skills/frontend-polish/SKILL.md. Build the ThiSpot SwiftUI demo flow with mock API first, then wire backend routes.

@vision Read skills/README.md and skills/.agents/skills/systematic-debugging/SKILL.md. Implement VisionMissionAgent and /api/analyze-photo output exactly as contracted.

@backend Read skills/README.md, skills/.agents/skills/api-backend/SKILL.md, and skills/.agents/skills/deployment/SKILL.md. Implement FastAPI harness, discovery/reward logic, and video/image report generation.

@integrator Read skills/README.md, skills/.agents/skills/test-first-contract/SKILL.md, and skills/.agents/skills/demo-readiness/SKILL.md. Keep the 90-second demo path green and report contract mismatches.
```

## Seven-Hour Plan

```text
0:00-0:20  Freeze API schema, demo color fallback, and character asset fallback
0:20-2:00  iOS mock flow, VisionMissionAgent, finish-walk harness in parallel
2:00-3:30  Wire photo upload, stabilize mission scoring, add report preview/render
3:30-5:00  Connect walk end to reward/report, add trace UI, add discovery result
5:00-6:00  Integration and fallback fixtures
6:00-7:00  Demo polish, rehearsal, backup recording
```

## Demo Must Prove

1. ThiSpot gives a daily color mission.
2. The character visually reacts to today's color.
3. The user starts and ends a walk with distance, steps, and time.
4. VisionMissionAgent analyzes an actual photo and returns a mission fit score.
5. The app shows a new/shared spot result and badge.
6. ContentGenerationAgent produces a shareable short video or image report.
