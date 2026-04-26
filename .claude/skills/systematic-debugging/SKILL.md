---
name: systematic-debugging
description: "ThiSpot VisionMissionAgent for photo color matching, object feedback, and mission proof."
---

# ThiSpot VisionMissionAgent Skill

Use this skill for the photo mission-proof agent.

## Goal

Given a target rainbow color and a user photo, verify whether the photo proves today's color mission and explain what object was found.

## Input

```text
image file
target_color: red | orange | yellow | green | blue | indigo | violet
lat/lng optional
```

## Output

```json
{
  "detected_color": "blue",
  "match_score": 0.87,
  "is_matched": true,
  "object_label": "sky",
  "feedback": "Blue sky detected. This fits today's mission."
}
```

## Algorithm

1. Load image with Pillow.
2. Resize for speed.
3. Sample pixels or compute palette.
4. Convert RGB to HSV.
5. Compare target hue range against pixel distribution.
6. Compute score from target-color pixel ratio and hue distance.
7. Return simple object label from heuristic, optional vision model, or deterministic fallback.

## Target Hue Ranges

```text
red:    345-360 or 0-15
orange: 16-40
yellow: 41-65
green:  66-165
blue:   190-250
indigo: 251-275
violet: 276-320
```

Ignore low-saturation and very dark pixels when possible.

## Match Rule

```text
score >= 0.70 -> is_matched true
score <  0.70 -> is_matched false
```

## Demo Fallback

If the analyzer fails, return:

```json
{
  "detected_color": "blue",
  "match_score": 0.87,
  "is_matched": true,
  "object_label": "sky",
  "feedback": "Blue sky detected with demo fallback."
}
```
