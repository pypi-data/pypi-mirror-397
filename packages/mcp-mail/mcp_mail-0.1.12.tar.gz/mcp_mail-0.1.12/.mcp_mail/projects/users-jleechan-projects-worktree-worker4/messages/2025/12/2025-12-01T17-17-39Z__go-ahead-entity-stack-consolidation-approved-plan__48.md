---json
{
  "ack_required": false,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-users-jleechan-projects-worktree-worker4"
  ],
  "created": "2025-12-01T17:17:39.198294+00:00",
  "from": "cleanv",
  "id": 48,
  "importance": "normal",
  "project": "/Users/jleechan/projects/worktree_worker4",
  "project_slug": "users-jleechan-projects-worktree-worker4",
  "subject": "Go ahead: Entity stack consolidation (approved plan)",
  "thread_id": null,
  "to": [
    "c2"
  ]
}
---

Approved plan — please implement now:

1) Delete the stray `entity_validation.py` you added earlier.
2) In-place merge per your revised plan (no new module names):
   - Move `filter_unknown_entities`/`is_unknown_entity` into `entity_validator.py`; drop the import from `entity_utils.py`.
   - Move `EntityPreloader` + `LocationEntityEnforcer` into `entity_instructions.py`; keep existing globals.
   - Convert `entity_utils.py` to a shim re-exporting those two functions from `entity_validator.py`.
   - Convert `entity_preloader.py` to a shim re-exporting from `entity_instructions.py`.
   - Keep `entity_tracking.py` unchanged.
3) Remove the 4 dead methods in `narrative_sync_validator.py` (`_compile_patterns`, `_analyze_entity_presence`, `_extract_physical_states`, `_detect_scene_transitions`).
4) Run the entity test suite you listed (97 tests) and report results.

Please push only these changes and send a short summary + test output. Thanks!
