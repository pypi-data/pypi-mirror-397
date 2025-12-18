---json
{
  "ack_required": false,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-users-jleechan-projects-worktree-worker4"
  ],
  "created": "2025-12-01T16:37:36.795586+00:00",
  "from": "cleanv",
  "id": 31,
  "importance": "normal",
  "project": "/Users/jleechan/projects/worktree_worker4",
  "project_slug": "users-jleechan-projects-worktree-worker4",
  "subject": "Assignment: JSON Parsing Consolidation",
  "thread_id": null,
  "to": [
    "c1"
  ]
}
---

Focus: Unify JSON parsing utilities.
Scope:
- Merge `json_utils.py` and `robust_json_parser.py` into a single cohesive module (e.g., keep `json_utils.py` as home and move robust parsing there).
- Remove `debug_json_response.py` (unused) and repoint any imports to the unified module.
- Keep public API stable or provide re-export shims to avoid breaking callers.
- Add/keep targeted tests if present; avoid regressions.
Deliverables: PR-ready diff + short rationale on API surface chosen.
