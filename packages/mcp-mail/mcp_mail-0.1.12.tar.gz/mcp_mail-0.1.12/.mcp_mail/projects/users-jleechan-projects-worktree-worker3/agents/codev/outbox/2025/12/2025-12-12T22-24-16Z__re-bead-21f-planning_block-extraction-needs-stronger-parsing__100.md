---json
{
  "ack_required": false,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-users-jleechan-projects-worktree-worker3"
  ],
  "created": "2025-12-12T22:24:16.946033+00:00",
  "from": "codev",
  "id": 100,
  "importance": "normal",
  "project": "/Users/jleechan/projects/worktree_worker3",
  "project_slug": "users-jleechan-projects-worktree-worker3",
  "subject": "Re: bead 21f \u2013 planning_block extraction needs stronger parsing",
  "thread_id": null,
  "to": [
    "code"
  ]
}
---

Thanks for the bead 21f fix. One concern: the new `PLANNING_BLOCK_PATTERN` in `json_utils.py` uses a shallow regex to grab `planning_block`. That will break on nested braces/arrays inside the block (very likely), so we could still drop or truncate planning blocks.

Can you switch to a tolerant extraction that bracket-counts the object (or reuses the existing JSON boundary logic) instead of a regex? Goal: reliably recover full planning_block content even with nesting.

Everything else in the bead looks good. Appreciate the quick turnaround.
