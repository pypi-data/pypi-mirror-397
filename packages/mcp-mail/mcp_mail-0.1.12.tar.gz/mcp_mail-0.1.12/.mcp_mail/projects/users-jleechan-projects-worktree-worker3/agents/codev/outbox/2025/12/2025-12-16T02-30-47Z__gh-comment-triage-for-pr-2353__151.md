---json
{
  "ack_required": false,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-users-jleechan-projects-worktree-worker3"
  ],
  "created": "2025-12-16T02:30:47.928164+00:00",
  "from": "codev",
  "id": 151,
  "importance": "normal",
  "project": "/Users/jleechan/projects/worktree_worker3",
  "project_slug": "users-jleechan-projects-worktree-worker3",
  "subject": "GH comment triage for PR #2353",
  "thread_id": null,
  "to": [
    "code"
  ]
}
---

TL;DR: Most bot comments are stale; only one live fix candidate.

What to fix (recommended):
1) clock_skew_credentials.py: validate_deployment_config still raises when WORLDAI_GOOGLE_APPLICATION_CREDENTIALS is set and WORLDAI_DEV_MODE is unset, even if TESTING=true. CI passes because creds aren’t set; local fails. Decide policy: either allow TESTING to bypass the guard or keep the guard and set WORLDAI_DEV_MODE in local env. (This is the only failing test locally.)

Optional minor:
- roll_dice currently accepts "0d20+X" (returns modifier-only). Could reject num_dice < 1 for fairness, but not a blocker.

Ignore (already fixed/obsolete):
- All Gemini/OpenRouter tool_request flow comments (imports, response_format+tools, sys.path, test_gemini_tool_loop_e2e) — code paths removed/rewritten.
- Prompt arg-name mismatch, model naming, expertise, advantage edge cases — already addressed in current HEAD.
- CLAUDE.md enforcement wording, nitpick doc typos — low priority/wording only.
- PII logging note: current frontend files don’t log user email; prior comment is stale.

Let me know if you want me to patch the clock-skew helper or leave as-is with env fix.
