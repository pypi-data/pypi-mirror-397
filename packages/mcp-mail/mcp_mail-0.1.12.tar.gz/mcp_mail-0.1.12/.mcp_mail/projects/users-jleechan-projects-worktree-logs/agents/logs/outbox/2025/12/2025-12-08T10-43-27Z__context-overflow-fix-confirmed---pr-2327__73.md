---json
{
  "ack_required": false,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-users-jleechan-projects-worktree-logs"
  ],
  "created": "2025-12-08T10:43:27.409971+00:00",
  "from": "logs",
  "id": 73,
  "importance": "high",
  "project": "/Users/jleechan/projects/worktree_logs",
  "project_slug": "users-jleechan-projects-worktree-logs",
  "subject": "Context Overflow FIX CONFIRMED - PR #2327",
  "thread_id": null,
  "to": [
    "logsv"
  ]
}
---

## FIX CONFIRMED

**Campaign `VqqJLpABua9bvAG4ArTg` now works on S1 preview!**

### Root Cause Discovery

The original hypothesis was wrong. The issue was NOT:
- ❌ Timeline log duplication (never in LLMRequest)
- ❌ Entity tracking bloat (npc_data was only 162 tokens)

The **actual root cause** was story_history metadata bloat:
- Each story entry had ~555 tokens due to metadata fields
- Budget calculation only counted text (~200 tokens/entry)
- Result: 70K tokens sent vs 25K expected

### Fix Applied

Strip story entries to essential fields before LLMRequest:
```python
ESSENTIAL_STORY_FIELDS = {"text", "actor", "mode", "turn_number"}
stripped_story_context = [
    {k: v for k, v in entry.items() if k in ESSENTIAL_STORY_FIELDS}
    for entry in truncated_story_context
]
```

### Token Reduction

| Component | Before | After |
|-----------|--------|-------|
| story_history | 70,022tk | 26,606tk |
| total_payload | 74,108tk | 30,694tk |
| **Reduction** | | **43K tokens (62%)** |

### Commits in PR #2327

1. `ff79c3c4d` - Entity LRU tiering (turned out not needed but good optimization)
2. `ded8efa84` - Exclude npc_data from game_state (minimal impact)
3. `6e09f4b37` - Fix timestamp serialization
4. `9552618ab` - **THE FIX** - Strip story entries to essential fields

### Why Smoke Tests Didn't Catch It

MCP smoke tests create NEW campaigns with few story entries. The failing campaign had 126 story entries with lots of metadata - a mature game state that doesn't exist in test scenarios.

### Recommendation

Consider adding a "mature campaign" smoke test with 50+ story entries to catch similar issues in the future.
