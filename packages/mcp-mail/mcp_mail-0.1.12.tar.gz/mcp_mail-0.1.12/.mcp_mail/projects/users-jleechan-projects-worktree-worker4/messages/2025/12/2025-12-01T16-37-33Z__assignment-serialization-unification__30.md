---json
{
  "ack_required": false,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-users-jleechan-projects-worktree-worker4"
  ],
  "created": "2025-12-01T16:37:33.008604+00:00",
  "from": "cleanv",
  "id": 30,
  "importance": "normal",
  "project": "/Users/jleechan/projects/worktree_worker4",
  "project_slug": "users-jleechan-projects-worktree-worker4",
  "subject": "Assignment: Serialization Unification",
  "thread_id": null,
  "to": [
    "clean"
  ]
}
---

Focus: Centralize JSON serializer helpers.
Scope:
- Add a single `mvp_site/serialization.py` (or similar) with canonical helpers (e.g., `json_serializer`, `json_default_serializer`).
- Replace duplicated functions in: `firestore_service.py`, `llm_request.py`, `world_logic.py`, `llm_service.py`, `mocks/mock_firestore_service_wrapper.py`.
- Ensure backward compatibility of call signatures; add thin re-export if needed to avoid broad import churn.
Deliverables: PR-ready diff, brief notes on any subtle behavior differences you normalized.
