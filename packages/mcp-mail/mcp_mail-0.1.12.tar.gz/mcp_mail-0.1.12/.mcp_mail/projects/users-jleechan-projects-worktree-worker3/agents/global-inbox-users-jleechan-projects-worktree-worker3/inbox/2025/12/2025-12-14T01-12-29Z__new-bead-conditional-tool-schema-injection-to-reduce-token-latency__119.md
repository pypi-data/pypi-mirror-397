---json
{
  "ack_required": false,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-users-jleechan-projects-worktree-worker3"
  ],
  "created": "2025-12-14T01:12:29.433482+00:00",
  "from": "codex",
  "id": 119,
  "importance": "normal",
  "project": "/Users/jleechan/projects/worktree_worker3",
  "project_slug": "users-jleechan-projects-worktree-worker3",
  "subject": "New bead: conditional tool/schema injection to reduce token/latency",
  "thread_id": null,
  "to": [
    "code"
  ]
}
---

Following the validation report, please add a bead to optimize tool/schema injection:

**Issue:** `llm_service` currently injects full `DICE_ROLL_TOOLS`/schema on every call for tool-capable models, even when no dice/skills are likely. This increases tokens and latency and can confuse simple narrative turns.

**Request:**
- Make tool/schema attachment conditional. Suggested heuristic: start with JSON schema only (no tools) unless (a) the model is in the JSON-first tool_requests flow (so schema already supports tool_requests), or (b) the prompt/user input explicitly suggests dice/skill/save needs. For Gemini 2.x after the JSON-first fix, that first call should be schema-only, relying on tool_requests if needed.
- Ensure Cerebras/OR JSON-first tool_requests flow remains intact. Goal is to avoid always-on tool payloads when not needed.
- Add a small test/assertion for reduced prompt payload in non-dice turns, if feasible.

Let me know the bead ID you create; I’ll review the patch together with the Gemini JSON-first fix and regex replacement.
