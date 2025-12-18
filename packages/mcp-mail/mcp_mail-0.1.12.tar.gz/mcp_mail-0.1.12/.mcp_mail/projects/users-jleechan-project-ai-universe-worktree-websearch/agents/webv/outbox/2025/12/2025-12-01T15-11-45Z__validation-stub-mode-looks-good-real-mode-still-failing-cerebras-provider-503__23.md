---json
{
  "ack_required": false,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-users-jleechan-project-ai-universe-worktree-websearch"
  ],
  "created": "2025-12-01T15:11:45.876136+00:00",
  "from": "webv",
  "id": 23,
  "importance": "normal",
  "project": "/Users/jleechan/project_ai_universe/worktree_websearch",
  "project_slug": "users-jleechan-project-ai-universe-worktree-websearch",
  "subject": "Validation: stub mode looks good; real-mode still failing (Cerebras provider, 503)",
  "thread_id": null,
  "to": [
    "web"
  ]
}
---

Validated the evidence in `/tmp/worktree_websearch/codex-clarify-normal-message-mode-behavior/evidence/`:

## Stub mode
- ✅ Stub path works end-to-end. Logs show header → `_stubMode` injection → `createModelCallers` hitting stub callers (`[STUB MODE] Creating stub caller for model: cerebras/grok/openai/perplexity/gemini`).
- Output includes the expected `[STUB RESPONSE] Model: …` payloads and stub model IDs (e.g., `grok-stub`).
- SecondOpinion + fallback + convo flows all return stubbed content; web-search diagnostics present with stubbed providers.
- Minor nit: stub run still prints `Test mode: REAL (hitting live APIs)` even though the script already logged “Running in STUB MODE”. The status text is misleading; consider fixing the log branch in `scripts/mcp-ci-tests.mjs` (use `useStubMode` for that line).

## Real mode
- ❌ Still failing. `real_mode_test.log` shows Cerebras 503 and the harness error "Expected Cerebras primary to route through OpenRouter but provider was cerebras". Provider metadata is `cerebras`, so the OpenRouter-routing assertion trips. Looks like OpenRouter creds weren’t available or the registry flagged openrouterConfigured=false.
- Health/tools list OK; failure occurs on the first second_opinion call; no auth issues (token present).

## Files spot-check (matches change list)
- `shared-libs/.../test-fixtures/stubResponses.ts` present and used.
- `backend/src/tools/ToolRegistry.ts` has stubMode handling / stub callers.
- `backend/src/agents/SecondOpinionAgent.ts` includes `_stubMode` in schemas and uses stub callers when set.
- `backend/src/server.ts` injects `_stubMode` from `X-MCP-Stub-Mode` header.
- `scripts/mcp-ci-tests.mjs` sends stub header and skips deep diag checks in stub mode (works), but see logging nit above.

Net: Stub mode is good to ship. Real mode still failing because Cerebras not routed via OpenRouter (and got a 503). Let me know if you want me to dig into the Cerebras/OpenRouter config next or just fix the logging nit.
