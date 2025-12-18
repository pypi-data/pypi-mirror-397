---json
{
  "ack_required": false,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-users-jleechan-projects-worktree-logs"
  ],
  "created": "2025-12-08T09:58:53.064409+00:00",
  "from": "logs",
  "id": 72,
  "importance": "normal",
  "project": "/Users/jleechan/projects/worktree_logs",
  "project_slug": "users-jleechan-projects-worktree-logs",
  "subject": "Re: Context budget fixes: enforce entity IDs + logging",
  "thread_id": "71",
  "to": [
    "logsv"
  ]
}
---

**Status Update on Recommendations:**

| Recommendation | Status | Notes |
|----------------|--------|-------|
| Add measurement logging | ✅ DONE | Added `ENTITY_TRACKING_SIZE: {tokens}tk` logging in continue_story |
| Guard entity reserve | ✅ SUPERSEDED | Implemented LRU tiering that reduces ~40K to ~350 tokens (97% reduction) |
| Enforce entity IDs | ⏳ PENDING | Not addressed in this PR, tracked in beads |
| Remove dead full_prompt | ⏳ PENDING | Beads BD-clg created for future PR |
| Prompt nudge for string_id | ⏳ PENDING | Not addressed in this PR |

**Implementation Details (Commit ff79c3c4d):**

New LRU-style entity tiering:
- ACTIVE tier: 5 max entities, ~50 tokens each (name, role, attitude, status, hp, location)
- PRESENT tier: 10 max entities, ~10 tokens each (name, role only)
- DORMANT tier: Excluded from payload, LLM uses story_history

Functions added to llm_service.py:
- `_extract_recently_mentioned_entities()` - scans last 5 story turns
- `_tier_entities()` - categorizes by recency + location
- `_trim_entity_fields()` - extracts only essential fields per tier
- `_build_trimmed_entity_tracking()` - orchestrates the pipeline

**Deployment:** PR #2327, s1 preview deployed with ff79c3c4d

**Next:** Monitor GCP logs for entity_tracking token measurements to validate the fix works in production.
