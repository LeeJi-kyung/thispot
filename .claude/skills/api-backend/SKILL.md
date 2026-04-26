---
name: api-backend
description: "ThiSpot Python FastAPI harness backend, routes, orchestrator, and agent wiring."
---

# ThiSpot Python Harness Backend Skill

Use this skill for the FastAPI backend and shared agent harness.

## Owns

```text
backend/app/main.py
backend/app/models/schemas.py
backend/app/harness/*
backend/app/agents/*
backend/app/skills/*
backend/app/storage/*
backend/app/assets/character/*
backend/app/outputs/*
```

## Required Stack

```text
FastAPI
Pydantic
Pillow
NumPy
MoviePy or ffmpeg-python
uvicorn
```

OpenCV is optional. Do not make OpenCV mandatory for the demo.

## Harness Agents

Implement:

```text
PersonalWalkAgent
VisionMissionAgent
DiscoveryAgent
RewardAgent
ContentGenerationAgent
WalkHarnessOrchestrator
```

## Endpoint Responsibilities

`/api/login-demo`:

- return a deterministic demo user and character

`/api/recommend-color`:

- avoid colors in recent history when possible
- return mission title, mission text, and character outfit color

`/api/analyze-photo`:

- save uploaded photo
- run VisionMissionAgent
- run DiscoveryAgent
- return `vision_result`, `discovery_result`, and `agent_trace`

`/api/finish-walk`:

- run RewardAgent
- run ContentGenerationAgent
- return `badge`, `report`, `summary`, and `agent_trace`

## Reliability Rules

- Every route must return valid JSON even if one agent fails.
- If video generation fails, return an image report.
- If image report generation fails, return static demo report URL.
- If vision analysis fails, return fallback score `0.87` only in demo mode.
