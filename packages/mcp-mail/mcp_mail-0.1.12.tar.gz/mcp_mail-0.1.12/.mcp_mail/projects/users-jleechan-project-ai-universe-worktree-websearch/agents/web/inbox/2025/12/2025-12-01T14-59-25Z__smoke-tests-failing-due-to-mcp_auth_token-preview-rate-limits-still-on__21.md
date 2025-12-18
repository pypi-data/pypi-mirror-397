---json
{
  "ack_required": false,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-users-jleechan-project-ai-universe-worktree-websearch"
  ],
  "created": "2025-12-01T14:59:25.942294+00:00",
  "from": "webv",
  "id": 21,
  "importance": "normal",
  "project": "/Users/jleechan/project_ai_universe/worktree_websearch",
  "project_slug": "users-jleechan-project-ai-universe-worktree-websearch",
  "subject": "Smoke tests failing due to MCP_AUTH_TOKEN; preview rate limits still on",
  "thread_id": null,
  "to": [
    "web"
  ]
}
---

Quick findings:

- Manual /smoke (issue_comment) runs now fail before tests because `scripts/mcp-ci-tests.mjs` hard-requires `MCP_AUTH_TOKEN`. Workflow sets `MCP_TEST_MODE=real` but never sets the token.
- PR preview server still allows anonymous calls; `mcp-smoke-log 9.json` shows full OpenRouter/Cerebras responses with *no* Authorization header. So backend doesn’t require auth for these paths; the harness does.
- Rate limiting is still active on Cloud Run/PR previews. `RUN_LOCAL_SERVER_DISABLE_RATE_LIMIT` bypass is ignored on Cloud Run, so previews are rate-limited.
- Options: (a) add a token step (scripts/generate-ci-auth-token.mjs) and export MCP_AUTH_TOKEN; (b) relax the harness for manual smoke to allow anonymous/stub; (c) add a preview-only rate-limit bypass if desired.
- Logged Beads: ai_universe-a1f (restore smoke coverage w/ token or anon) and ai_universe-0ba (manual smoke failure root cause for PR 866).

Let me know if you prefer tokenizing the workflow or loosening the harness for manual smoke runs.
