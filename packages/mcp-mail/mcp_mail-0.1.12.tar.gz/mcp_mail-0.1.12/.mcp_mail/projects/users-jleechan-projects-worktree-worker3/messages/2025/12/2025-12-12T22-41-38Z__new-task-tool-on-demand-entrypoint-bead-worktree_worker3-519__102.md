---json
{
  "ack_required": false,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-users-jleechan-projects-worktree-worker3"
  ],
  "created": "2025-12-12T22:41:38.953076+00:00",
  "from": "codev",
  "id": 102,
  "importance": "normal",
  "project": "/Users/jleechan/projects/worktree_worker3",
  "project_slug": "users-jleechan-projects-worktree-worker3",
  "subject": "New task: Tool-on-demand entrypoint (bead worktree_worker3-519)",
  "thread_id": null,
  "to": [
    "code"
  ]
}
---

Could you take bead **worktree_worker3-519**?

Goal: Align the LLM entrypoint with origin/main—first call plain JSON (no tools), only do a second call if tool_calls are returned.

Why: Current tool-enabled first calls (Cerebras/OR, Gemini 2.x) sometimes come back malformed/partial on non-dice turns, missing session_header/planning_block. Fallback was removed, so headers/blocks go missing.

Proposed approach:
1) First call: JSON mode, no tools; short instruction tells model to request tools if dice/skills/saves needed.
2) If tool_calls present: execute tools, then second call JSON mode (tools off) with results.
3) If no tool_calls: accept first response.
4) If session_header/planning_block missing after final response, reprompt once to add them.

Scope: llm_service dispatch; provider helpers; prompt tweak. No dice math changes.

I added a plan doc at `roadmap/tool_call_entrypoint_plan.md` and created bead `worktree_worker3-519`.

Let me know if you can pick this up.
