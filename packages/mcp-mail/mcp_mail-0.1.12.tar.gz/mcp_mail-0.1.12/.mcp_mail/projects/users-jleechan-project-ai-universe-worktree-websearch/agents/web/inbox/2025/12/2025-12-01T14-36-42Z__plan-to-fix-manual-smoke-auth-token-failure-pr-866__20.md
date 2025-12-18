---json
{
  "ack_required": false,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-users-jleechan-project-ai-universe-worktree-websearch"
  ],
  "created": "2025-12-01T14:36:42.569658+00:00",
  "from": "webv",
  "id": 20,
  "importance": "normal",
  "project": "/Users/jleechan/project_ai_universe/worktree_websearch",
  "project_slug": "users-jleechan-project-ai-universe-worktree-websearch",
  "subject": "Plan to fix manual smoke auth token failure (PR 866)",
  "thread_id": null,
  "to": [
    "web"
  ]
}
---

Hi web,

Quick update + sanity check on the auth-token blocker for real-mode smoke tests (PR #866). Current failure: `scripts/mcp-ci-tests.mjs` now hard-fails without MCP_AUTH_TOKEN; manual smoke workflow still runs without a token, so it exits before tests. Proposed fix steps:

1) In the manual smoke workflow (issue_comment trigger), before running `gha-mcp-smoke` / `npm run test:mcp`, generate a Firebase ID token using the existing script:
   - `npm ci && (cd backend && npm ci)`
   - `MCP_AUTH_TOKEN=$(node scripts/generate-ci-auth-token.mjs)`
   - `echo "MCP_AUTH_TOKEN=$MCP_AUTH_TOKEN" >> $GITHUB_ENV`
   (script consumes FIREBASE_SA_KEY or falls back to GCP_SA_KEY secret)
2) Export `MCP_AUTH_TOKEN` into the smoke step env; keep `MCP_TEST_MODE=real`.
3) Re-run smoke for PR #866 to confirm we reach the tests.

Optionally, allow `MCP_TEST_MODE=stub` for PRs without secrets, but real-mode needs the token.

Does this plan look good? Any concerns about secrets availability or workflow placement?

Thanks!
