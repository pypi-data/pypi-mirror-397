---json
{
  "ack_required": false,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-users-jleechan-projects-worktree-worker4"
  ],
  "created": "2025-12-01T16:37:40.465171+00:00",
  "from": "cleanv",
  "id": 32,
  "importance": "normal",
  "project": "/Users/jleechan/projects/worktree_worker4",
  "project_slug": "users-jleechan-projects-worktree-worker4",
  "subject": "Assignment: Entity Stack Cleanup",
  "thread_id": null,
  "to": [
    "c2"
  ]
}
---

Focus: Reduce fragmentation in entity modules.
Scope:
- Consolidate `entity_validator.py`, `entity_instructions.py`, `entity_preloader.py`, `entity_tracking.py`, `entity_utils.py` into 2–3 coherent modules (e.g., validation, preparation, tracking).
- Identify and remove any dead or duplicate helpers; keep public interfaces stable or supply re-export shims.
- Avoid breaking tests; adjust imports as needed.
Deliverables: Plan + initial refactor proposal, or PR-ready diff if straightforward.
