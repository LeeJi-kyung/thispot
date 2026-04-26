---
name: demo-readiness
description: "ThiSpot 90-second demo script, backup assets, and judge-facing story."
---

# ThiSpot Demo Readiness Skill

Use this skill for the final 90-second demo path.

## 30-Second Problem

Existing walking apps tell users how far they walked, but that is not why most people keep walking. Solo walking is boring, and there is no immediate reward worth sharing. ThiSpot adds a daily color mission, AI photo proof, and character-based reward content so walking becomes something users want to repeat.

## 90-Second Script

```text
1. Open ThiSpot: character appears.
2. Today's color mission is Blue.
3. Character outfit changes to blue.
4. Tap Start Walk: GPS/steps/timer screen begins.
5. Capture a blue sky photo inside the app.
6. VisionMissionAgent shows "Blue sky detected - 87% match".
7. End walk: result shows 1.24km, 1,843 steps, 12m, 2 photos.
8. Discovery message appears: "New Blue Spot discovered."
9. RewardAgent awards "Blue Finder".
10. ContentGenerationAgent creates short video or image report.
```

## Required Backup Assets

- one blue demo photo
- one character asset
- one pre-rendered report image
- one pre-rendered video if possible
- fixed backend fixture response
- screen recording fallback

## Kill Criteria

If MP4 generation takes more than 20 minutes to stabilize, ship image report. If GPS/steps are unstable, use demo fallback values while keeping the tracking UI.

## Judge-Facing Claim

ThiSpot is not just a walking tracker. It turns walking into a color mission, verifies real-world discoveries with AI, and converts the workout into a shareable character-based reward.
