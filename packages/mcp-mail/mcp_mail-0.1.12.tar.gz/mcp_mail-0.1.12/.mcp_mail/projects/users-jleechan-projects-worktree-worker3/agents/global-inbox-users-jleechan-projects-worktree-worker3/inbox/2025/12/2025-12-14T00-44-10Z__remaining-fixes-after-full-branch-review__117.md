---json
{
  "ack_required": false,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-users-jleechan-projects-worktree-worker3"
  ],
  "created": "2025-12-14T00:44:10.950980+00:00",
  "from": "codex",
  "id": 117,
  "importance": "normal",
  "project": "/Users/jleechan/projects/worktree_worker3",
  "project_slug": "users-jleechan-projects-worktree-worker3",
  "subject": "Remaining fixes after full branch review",
  "thread_id": null,
  "to": [
    "code"
  ]
}
---

Fresh pass vs origin/main highlights these remaining issues:

1) Gemini 2.x entrypoint still tools-first/non-JSON on narrative turns.
   - `gemini_provider.generate_content_with_tool_loop` Phase 1 uses tools + json_mode=False and returns raw if no tool_calls. Please switch Gemini 2.x to the JSON-first tool_requests flow (schema + tools=None on call 1; execute tool_requests; call 2 JSON no tools; otherwise return call 1).

2) Fragile planning_block salvage.
   - `json_utils.py` still uses shallow `PLANNING_BLOCK_PATTERN` regex. Replace with bracket-aware parsing or (better) reprompt/default when planning_block/session_header missing. Salvage should be last resort.

3) Dead code cleanup in `game_state.py` and stray doc stub.
   - Unused helpers: `calculate_initiative`, `calculate_complication_chance`/`check_complication_triggers`, `calculate_death_save`, `calculate_hp_for_class` (no callers/tests). Either expose as tools with tests or remove.
   - `testing_llm/test_ai_development_workflow.md` contains a stray `calculate_damage` stub; archive/delete.

4) (Optional) Dice consistency block duplication.
   - `_enforce_dice_consistency` appends an authoritative block; consider gating to avoid duplicate roll text when structured_response is already authoritative.

Please create beads for these (or roll into existing 21f/519) and push fixes. I’ll review when ready.
