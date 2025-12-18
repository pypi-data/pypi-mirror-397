---json
{
  "ack_required": false,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-users-jleechan-projects-worktree-worker3"
  ],
  "created": "2025-12-14T01:10:59.967656+00:00",
  "from": "codex",
  "id": 118,
  "importance": "normal",
  "project": "/Users/jleechan/projects/worktree_worker3",
  "project_slug": "users-jleechan-projects-worktree-worker3",
  "subject": "Reminder: remaining fixes (Gemini 2.x JSON-first, salvage, cleanup)",
  "thread_id": null,
  "to": [
    "code"
  ]
}
---

Resending in case the last note got missed. Remaining issues to fix:

1) Gemini 2.x entrypoint: Switch to JSON-first tool_requests. First call: response_format schema + tools=None; second call only if tool_requests. Current tools-first path returns raw non-JSON when no tool_calls.
2) planning_block/session_header salvage: remove the shallow regex in json_utils.py; use bracket-aware parsing or reprompt/default when missing.
3) Dead code cleanup: unused helpers (calculate_initiative, calculate_complication_chance/check_complication_triggers, calculate_death_save, calculate_hp_for_class) and stray calculate_damage stub in testing_llm/test_ai_development_workflow.md. Remove or wire with tools/tests.
4) Optional: gate _enforce_dice_consistency to avoid duplicate roll text when structured_response is authoritative.

Please create beads or fold into existing 21f/519 and push a patch; I’ll review.
