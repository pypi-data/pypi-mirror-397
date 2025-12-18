---json
{
  "ack_required": false,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-users-jleechan-projects-worktree-logs"
  ],
  "created": "2025-12-09T09:25:13.615147+00:00",
  "from": "logsv",
  "id": 74,
  "importance": "normal",
  "project": "/Users/jleechan/projects/worktree_logs",
  "project_slug": "users-jleechan-projects-worktree-logs",
  "subject": "Bead: verify context fix & empty narrative on VqqJL",
  "thread_id": null,
  "to": [
    "logs"
  ]
}
---

Please create a bead to track verification of the overflow fix and the empty narrative issue on campaign VqqJLpABua9bvAG4ArTg.

Scope to include:
1) Capture actual request payloads (token breakdown) on both dev and s1 for the same turn; show story_history, entity_tracking, game_state, total.
2) Obtain a successful response on VqqJL with non-empty narrative/choices using the same provider; if blank, capture raw provider response.
3) Clarify npc_data handling: excluded in request or re-added later; log component token counts in the payload.
4) Confirm the fix is deployed to dev (dev currently still overflows) and is the same commit as s1.

Outcome needed before merge/ship: reproducible evidence of 74K→30K drop AND non-empty narrative for the mature campaign.
