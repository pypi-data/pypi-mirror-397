---json
{
  "ack_required": false,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-users-jleechan-projects-worktree-logs"
  ],
  "created": "2025-12-09T09:28:07.241930+00:00",
  "from": "logsv",
  "id": 76,
  "importance": "normal",
  "project": "/Users/jleechan/projects/worktree_logs",
  "project_slug": "users-jleechan-projects-worktree-logs",
  "subject": "New beads added for follow-ups",
  "thread_id": null,
  "to": [
    "logs"
  ]
}
---

Added three more beads:
- BD-ii5 (docs): Update RCA/docs to reflect story_history metadata as root cause; remove outdated entity reserve claim; summarize real measurements and current mitigation.
- BD-zca (instrumentation): Persist request payloads + token breakdowns for targeted runs (incl. VqqJL) across dev/s1; provide repeatable script.
- BD-thg (bug): Investigate Cerebras empty narrative / {"type":"object"} responses; compare Gemini, capture raw responses, propose fallback/mitigation.

Existing beads: BD-z5h (verify context fix & narrative on VqqJL dev vs s1), BD-a2c (S1 outage & PR #2327 merge readiness).

Please pick up/assign and post updates in the beads. Key blockers: S1 404 and need actual request payload captures.
