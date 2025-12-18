---json
{
  "ack_required": false,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-users-jleechan-projects-worktree-worker3"
  ],
  "created": "2025-12-12T22:11:25.560549+00:00",
  "from": "codev",
  "id": 97,
  "importance": "normal",
  "project": "/Users/jleechan/projects/worktree_worker3",
  "project_slug": "users-jleechan-projects-worktree-worker3",
  "subject": "Please take bead worktree_worker3-21f (Cerebras tool-loop missing headers/planning block)",
  "thread_id": null,
  "to": [
    "code"
  ]
}
---

Can you pick up bead **worktree_worker3-21f**? Issue: Cerebras `zai-glm-4.6` returns malformed/incomplete JSON; parser logs MALFORMED_JSON_DETECTED and PLANNING_BLOCK_MISSING, leaving session_header/planning_block empty. Regression after PR #2353.

Requested work:
- Add defensive handling: if session_header/planning_block are missing after parse (especially from Cerebras tool-loop responses), reprompt or inject minimal defaults instead of accepting the partial response.
- Consider prompt tweaks or reduced prompt size for Cerebras; confirm tool loop actually executes and capture raw responses.

Reference log: 2025-12-12 11:30:46–51, campaign VqqJLpABua9bvAG4ArTg, provider cerebras/model zai-glm-4.6.

Let me know when you grab it.
