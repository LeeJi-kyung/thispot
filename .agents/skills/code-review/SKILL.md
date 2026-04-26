---
name: code-review
description: "ThiSpot integration review checklist focused on demo-breaking bugs and contract mismatches."
---

# ThiSpot Integration Review Skill

Use this skill before merging work from cmux lanes.

## Review Priorities

1. Contract compatibility with `skills/README.md`.
2. Demo path cannot crash.
3. Every backend agent route returns `agent_trace`.
4. iOS has mock fallback for backend failure.
5. Vision mission score is stable on the demo photo.
6. Content generation failure still returns an image report.
7. Character asset loads on the first screen and report screen.

## Common Failure Modes

- iOS expects camelCase but backend returns snake_case.
- Multipart field names differ.
- Report URL is relative when iOS expects absolute.
- Backend saves uploads outside writable path.
- GPS permission blocks demo.
- Camera permission blocks demo.
- MP4 generation takes too long.
- Character/report assets are missing from static serving.

## Required Fix Pattern

Prefer compatibility adapters over broad refactors. This is a hackathon MVP; preserve the demo path first.
