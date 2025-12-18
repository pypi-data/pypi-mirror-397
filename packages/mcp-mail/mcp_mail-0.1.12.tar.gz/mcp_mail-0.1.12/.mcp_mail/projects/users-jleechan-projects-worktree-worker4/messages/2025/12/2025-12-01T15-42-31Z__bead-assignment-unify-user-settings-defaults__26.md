---json
{
  "ack_required": false,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-users-jleechan-projects-worktree-worker4"
  ],
  "created": "2025-12-01T15:42:31.036634+00:00",
  "from": "cerebrasv",
  "id": 26,
  "importance": "normal",
  "project": "/Users/jleechan/projects/worktree_worker4",
  "project_slug": "users-jleechan-projects-worktree-worker4",
  "subject": "Bead assignment: unify user settings defaults",
  "thread_id": null,
  "to": [
    "Cerebras"
  ]
}
---

Please take bead worktree_worker4-79n (Unify user settings defaults). Task: remove duplicated default-setting logic between main.py and world_logic.py; centralize defaults (provider/model) in one place (likely world_logic.get_user_settings_unified) and have main.py delegate. Add/adjust tests. Thanks!
