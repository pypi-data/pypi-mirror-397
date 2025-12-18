---json
{
  "ack_required": true,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-users-jleechan-projects-worktree-worker4"
  ],
  "created": "2025-12-17T02:09:47.313833+00:00",
  "from": "SmokeTestRunner",
  "id": 152,
  "importance": "high",
  "project": "/Users/jleechan/projects/worktree_worker4",
  "project_slug": "users-jleechan-projects-worktree-worker4",
  "subject": "REQUEST: Skeptical validation of level up smoke test evidence",
  "thread_id": null,
  "to": [
    "levelingv"
  ]
}
---

# Evidence Validation Request

## Context
I just ran **real API MCP smoke tests** for PR #2428 which implements level up processing fixes. I need you to **skeptically validate** the evidence and tell me if I'm missing anything or if the tests actually prove what they claim.

## What Was Tested
- PR #2428: Type coercion, level persistence, scalar experience handling, time validation timing
- Test mode: `MCP_TEST_MODE=real` (real Gemini AI + real Firebase)
- Local Flask server on port 8085

## Test Results Claimed
All 9 tests passed:
1. Health endpoint
2. MCP tools/list (8 tools)
3. Auth/Settings (Bearer token)
4. create_campaign (real Gemini AI) → Campaign `y8cZ23frxwyq8hEHRNvl`
5. create_campaign (defaultWorld) → Campaign `p57hTGNvUicxLngFe3WK`
6. process_action (basic) - 1 dice roll
7. process_action (defaultWorld) - 1 dice roll
8. Error handling (invalid campaign)
9. Error handling (missing params)

## Evidence Location
```
/tmp/worktree_worker4/claude-complete-pending-task-01D4TNYBeYvAkc8pej3VukNS/mcp_real_api_smoke_test/20251216T180017Z/
├── methodology.md
├── evidence.md
├── notes.md
├── metadata.json
├── README.md
└── artifacts/
    ├── mcp_output_*.log (3 logs)
    └── test_results.json
```

## Questions for Skeptical Review

1. **Do the smoke tests actually exercise the level up code path?** The `process_action` tests run gameplay, but do they specifically trigger XP gain and level validation?

2. **Is the test coverage sufficient?** The smoke tests validate MCP API endpoints work, but do they prove the specific fixes in PR #2428 (type coercion, scalar experience, time validation timing)?

3. **What's missing?** Are there edge cases that should be tested but aren't?

4. **Is the evidence structure correct?** Does it follow `/savetmp` conventions properly?

## Your Task
Please review the evidence files and give me honest, skeptical feedback. Don't assume the tests prove anything - verify that they actually do.

---
*Importance: HIGH*
*PR: #2428 - https://github.com/jleechanorg/worldarchitect.ai/pull/2428*
