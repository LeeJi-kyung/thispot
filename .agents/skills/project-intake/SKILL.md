---
name: project-intake
description: "ThiSpot MVP scope, product positioning, and demo boundaries."
---

# ThiSpot Product Intake

Use this skill when defining or rechecking the MVP scope.

## Mission

Build a 7-hour iOS MVP for ThiSpot:

```text
demo login / character
-> today's rainbow color mission
-> character outfit changes to mission color
-> start GPS/pedometer walk
-> capture mission photos
-> VisionMissionAgent verifies color/object fit
-> finish walk
-> DiscoveryAgent reports new/shared spot
-> RewardAgent awards badge
-> ContentGenerationAgent creates short video or image report
```

## Sharp Positioning

ThiSpot is not a generic walking tracker. It targets the motivation gap: solo walking is easy to start but hard to repeat because existing apps mostly reward users with numbers.

The product loop is:

```text
mission -> proof -> character reward -> shareable memory -> repeat
```

## Non-Negotiable Demo Claims

1. The app turns walking into a daily color mission.
2. The character reacts to today's color.
3. The user captures a real photo during the walk.
4. VisionMissionAgent verifies the real-world mission proof.
5. The final reward is shareable: short video or image report.

## Out of Scope

- Real OAuth
- Production database
- Real social graph
- Complex segmentation
- Full generative video model
- LLM-based color recommendation

## Fallback Story

If hardware or APIs fail, demo with fixed values:

```text
target color: blue
character: Spotter in blue outfit
distance: 1.24km
steps: 1,843
duration: 12m
match score: 87%
object: sky
spot: New Blue Spot discovered
badge: Blue Finder
report: image card fallback
```
