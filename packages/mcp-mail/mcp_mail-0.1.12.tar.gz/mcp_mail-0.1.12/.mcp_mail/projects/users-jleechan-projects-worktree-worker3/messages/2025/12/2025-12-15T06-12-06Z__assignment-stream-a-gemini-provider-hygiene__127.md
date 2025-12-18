---json
{
  "ack_required": false,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-users-jleechan-projects-worktree-worker3"
  ],
  "created": "2025-12-15T06:12:06.953884+00:00",
  "from": "codex",
  "id": 127,
  "importance": "normal",
  "project": "/Users/jleechan/projects/worktree_worker3",
  "project_slug": "users-jleechan-projects-worktree-worker3",
  "subject": "Assignment: Stream A (Gemini/provider hygiene)",
  "thread_id": null,
  "to": [
    "code"
  ]
}
---

Please take Stream A:
- Gemini provider cleanup: system_instruction should be string (not Part), add defensive tool validation, ensure history passed in JSON-first flow, remove sys.path hack/new test file by moving tests into existing files and cleaning unused imports; keep JSON-first tool_requests routing. 
- Provider hygiene: openrouter response_format+tools conditional/documentation; move any remaining inline execute_dice_tool imports to module scope (cerebras has one); add type checks in execute_tool_requests; fix test arg key to `notation`.
- Remove remaining tools-first codepaths (bead 3w8) once Gemini path is aligned.

Mark beads: jp2, 4ds, 3w8. Ping with PR/commits; I’ll review.
