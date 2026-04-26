---
name: git-workflow
description: "ThiSpot cmux multi-agent workflow, lane ownership, prompts, and merge rules."
---

# ThiSpot cmux Multi-Agent Workflow Skill

Use this skill to coordinate parallel work.

## Lanes

```text
Lane A: iOS Client
Skill: frontend-polish
Owns: SwiftUI flow, character UI, walk tracking, camera, API client, result/report UI

Lane B: Vision Mission Agent
Skill: systematic-debugging
Owns: VisionMissionAgent, image analyzer, object feedback, /api/analyze-photo vision output

Lane C: Harness + Content
Skill: api-backend + deployment
Owns: FastAPI app, orchestrator, recommend color, discovery, reward, content generation

Lane D: Integrator
Skill: demo-readiness + code-review + test-first-contract
Owns: contract checks, fallback fixtures, demo rehearsal
```

## cmux Prompts

```text
@ios Read skills/README.md and skills/.agents/skills/frontend-polish/SKILL.md. Build the ThiSpot SwiftUI flow using mock API responses first, then wire backend routes.

@vision Read skills/README.md and skills/.agents/skills/systematic-debugging/SKILL.md. Implement the Python VisionMissionAgent and make /api/analyze-photo return the exact contract.

@backend Read skills/README.md, skills/.agents/skills/api-backend/SKILL.md, and skills/.agents/skills/deployment/SKILL.md. Implement FastAPI harness, discovery/reward logic, and video/image report generation.

@integrator Read skills/README.md, skills/.agents/skills/test-first-contract/SKILL.md, and skills/.agents/skills/demo-readiness/SKILL.md. Run contract checks and keep the 90-second demo path green.
```

## Merge Rule

Each lane may work independently with mocks. Integration starts only after:

```text
iOS has mock report preview screen
backend has /api/login-demo and /api/recommend-color
vision lane has /api/analyze-photo compatible output
content lane has /api/finish-walk compatible output
```

## Status Format

Every lane reports:

```text
Done:
Blocked:
Contract changes:
Demo risk:
Next 30 minutes:
```
