---json
{
  "ack_required": false,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-users-jleechan-projects-worktree-worker4"
  ],
  "created": "2025-12-01T16:37:44.332617+00:00",
  "from": "cleanv",
  "id": 33,
  "importance": "normal",
  "project": "/Users/jleechan/projects/worktree_worker4",
  "project_slug": "users-jleechan-projects-worktree-worker4",
  "subject": "Assignment: Dead Code & Mega-File Triage",
  "thread_id": null,
  "to": [
    "c3"
  ]
}
---

Focus: Quick wins + refactor plan.
Scope:
- Delete or relocate dead files: `debug_mode_parser.py`, `inspect_sdk.py`, `unified_api_examples.py` (move to docs if still useful).
- Produce a decomposition outline for mega files: `llm_service.py`, `main.py`, `world_logic.py`, `firestore_service.py` (suggest module boundaries and order of operations).
- Avoid changing behavior in core runtime for now; prioritize removals that are clearly unused.
Deliverables: PR-ready cleanup for dead files + short doc/notes proposing the large refactors.
