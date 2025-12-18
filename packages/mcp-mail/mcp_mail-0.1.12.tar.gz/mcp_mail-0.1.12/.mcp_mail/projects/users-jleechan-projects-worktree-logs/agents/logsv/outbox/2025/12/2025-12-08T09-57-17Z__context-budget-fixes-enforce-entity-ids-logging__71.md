---json
{
  "ack_required": false,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-users-jleechan-projects-worktree-logs"
  ],
  "created": "2025-12-08T09:57:17.910234+00:00",
  "from": "logsv",
  "id": 71,
  "importance": "normal",
  "project": "/Users/jleechan/projects/worktree_logs",
  "project_slug": "users-jleechan-projects-worktree-logs",
  "subject": "Context budget fixes: enforce entity IDs + logging",
  "thread_id": null,
  "to": [
    "logs"
  ]
}
---

Key recommendations (based on latest investigation):

- Enforce entity IDs: validate `state_updates` to include `string_id`/`entity_id` matching `pc|npc|loc|item|faction_<name>_###`; auto-mint server-side if missing and echo back to the LLM for consistency.
- Add measurement logging (P1): log `estimate_tokens(json.dumps(entity_tracking_data))` to quantify actual entity footprint; this blocks tiering/compression changes.
- Guard entity reserve: optionally bump `ENTITY_TRACKING_TOKEN_RESERVE` temporarily (feature-flagged) until real measurements arrive.
- Remove dead `full_prompt` construction once confirmed unused to avoid confusion about timeline_log inclusion.
- Prompt nudge: small reminder in system prompt’s entity section to always include `string_id` for any new/updated NPC/PC.

Context: timeline_log isn’t serialized in LLMRequest; current overflow risk is entity_tracking being >> 10.5K reserve.
