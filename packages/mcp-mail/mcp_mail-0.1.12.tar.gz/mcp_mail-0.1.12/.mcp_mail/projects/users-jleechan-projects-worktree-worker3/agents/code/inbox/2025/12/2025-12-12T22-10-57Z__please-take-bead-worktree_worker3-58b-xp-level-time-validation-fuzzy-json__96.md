---json
{
  "ack_required": false,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-users-jleechan-projects-worktree-worker3"
  ],
  "created": "2025-12-12T22:10:57.028171+00:00",
  "from": "codev",
  "id": 96,
  "importance": "normal",
  "project": "/Users/jleechan/projects/worktree_worker3",
  "project_slug": "users-jleechan-projects-worktree-worker3",
  "subject": "Please take bead worktree_worker3-58b (XP/level/time validation + fuzzy JSON)",
  "thread_id": null,
  "to": [
    "code"
  ]
}
---

Could you pick up bead **worktree_worker3-58b** (Harden narrative/XP/time validation and fuzzy JSON extraction)? Key tasks:
- Add fuzzy narrative extraction fallback on malformed JSON.
- Update mechanics_system_instruction.md to include the 5e XP table and tell the LLM to treat XP/level as authoritative from the system (don’t recompute).
- Add GameState validation hooks: level/XP consistency (auto-correct or strict), time monotonicity check.
- Add unit tests for XP→level consistency, mismatch correction/strict mode, and time monotonicity.

I also dropped a handoff prompt with details at `~/Downloads/level_xp_validation_prompt.txt` on this machine. Let me know if you need anything else.
