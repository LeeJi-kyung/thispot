---
name: frontend-polish
description: "ThiSpot SwiftUI iOS client flow, character UI, walk tracking, camera, and result report."
---

# ThiSpot iOS Client Skill

Use this skill for the SwiftUI iOS app.

## Owns

```text
ThiSpot/Models/WalkModels.swift
ThiSpot/Models/AgentModels.swift
ThiSpot/Services/APIClient.swift
ThiSpot/Services/WalkTrackingService.swift
ThiSpot/ViewModels/WalkSessionViewModel.swift
ThiSpot/Views/*
```

## Required Screens

1. Demo login/start screen with character
2. Today's color mission screen
3. Character outfit/theme color update
4. Walk tracking screen with distance, steps, timer
5. In-app camera/photo capture
6. VisionMissionAgent timeline/result
7. Walk result screen
8. Badge and short video/image report preview

## iOS Stack

```text
SwiftUI
CoreLocation
CoreMotion / CMPedometer
Photos or camera capture
MapKit optional
AVPlayer for recap video preview
ShareLink / UIActivityViewController for sharing
```

## API Integration

Use the contract in `skills/README.md`.

The app must support mock responses through one switch:

```swift
let useMockBackend = true
```

## Demo UX Rules

- Keep the flow one-handed and linear.
- Always show visible agent progress.
- Never block the demo if backend fails; show fixture data.
- Result screen must include distance, steps, duration, photo count, match score, badge, spot message, and report preview.
