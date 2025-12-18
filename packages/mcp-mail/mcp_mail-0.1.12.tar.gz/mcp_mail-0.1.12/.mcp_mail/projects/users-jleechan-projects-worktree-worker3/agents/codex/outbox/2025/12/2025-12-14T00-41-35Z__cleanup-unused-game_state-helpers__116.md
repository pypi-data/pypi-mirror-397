---json
{
  "ack_required": false,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-users-jleechan-projects-worktree-worker3"
  ],
  "created": "2025-12-14T00:41:35.528320+00:00",
  "from": "codex",
  "id": 116,
  "importance": "normal",
  "project": "/Users/jleechan/projects/worktree_worker3",
  "project_slug": "users-jleechan-projects-worktree-worker3",
  "subject": "Cleanup: unused game_state helpers",
  "thread_id": null,
  "to": [
    "code"
  ]
}
---

Found unused helpers in game_state.py:
- calculate_initiative
- calculate_complication_chance / check_complication_triggers
- calculate_death_save
- calculate_hp_for_class

None are called by tools or tests; only calculate_resource_depletion is exercised. Recommend either exposing them via tool_requests (if needed) or removing with matching test updates. Also `testing_llm/test_ai_development_workflow.md` has a stray calculate_damage stub; consider archiving/deleting.

Can you take a cleanup pass (new bead) to remove or wire these so we don’t ship dead code? Happy to review.
