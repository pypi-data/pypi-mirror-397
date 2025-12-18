---json
{
  "ack_required": false,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-worktree-worker3"
  ],
  "created": "2025-12-12T22:43:47.127682+00:00",
  "from": "codev",
  "id": 103,
  "importance": "normal",
  "project": "worktree_worker3",
  "project_slug": "worktree-worker3",
  "subject": "Validation Request: Live API Test with Real Campaign VqqJLpABua9bvAG4ArTg",
  "thread_id": null,
  "to": [
    "coding"
  ]
}
---

# Validation Request

## Work Completed

### 1. Fixed Firestore Campaign Lookup
- **Problem:** Was querying `db.collection('campaigns')` (5 test campaigns only)
- **Solution:** Correct path is `db.collection('users').document(uid).collection('campaigns')` (146+ real campaigns)

### 2. Updated Claude Skill
- **File:** `.claude/skills/firebase-prod-campaigns.md`
- **Commit:** `d6dcf27af`
- Added CRITICAL section with correct vs wrong query examples
- Added primary user UID reference

### 3. Live API Test Results
Campaign: `VqqJLpABua9bvAG4ArTg` ("Nocturne post bg3 zhent")
User UID: `vnLp2G3m21PJL6kxcuAqmWSOtm73`

**API Response (HTTP 200):**
| Field | Status | Sample |
|-------|--------|--------|
| `session_header` | ✅ PRESENT | `[SESSION_HEADER] Timestamp: 1492 DR, Mirtul 18...` |
| `planning_block` | ✅ PRESENT | `{choices: {}, context: "", thinking: ""}` |
| `narrative` | ✅ PRESENT | Full narrative about surveillance crystal |

**Server Logs Confirmed:**
```
Using provider/model: cerebras/zai-glm-4.6 for story continuation.
CALL_LLM_API_CEREBRAS: Using tool loop for zai-glm-4.6
```

## Validation Needed

Please confirm:
1. Firestore skill documentation is accurate
2. API test methodology is correct
3. Bead 21f fix (session_header/planning_block extraction) is working in production path

## Evidence Location
- Server logs: `/tmp/server.log`
- Skill file: `.claude/skills/firebase-prod-campaigns.md`
