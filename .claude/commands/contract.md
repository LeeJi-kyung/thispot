# /contract

Use before splitting ThiSpot work across cmux lanes.

Read:

- `skills/README.md`
- `skills/.agents/skills/architecture-contract/SKILL.md`

Verify:

- iOS and backend agree on all 4 POST routes
- multipart field names match
- response fields match exactly
- every backend agent response includes `agent_trace`
- fallback demo values and character asset are fixed
