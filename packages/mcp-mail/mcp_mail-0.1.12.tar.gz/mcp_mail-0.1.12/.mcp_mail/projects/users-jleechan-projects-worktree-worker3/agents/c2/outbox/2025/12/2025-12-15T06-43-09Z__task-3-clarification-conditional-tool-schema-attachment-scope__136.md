---json
{
  "ack_required": false,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-users-jleechan-projects-worktree-worker3"
  ],
  "created": "2025-12-15T06:43:09.292572+00:00",
  "from": "c2",
  "id": 136,
  "importance": "normal",
  "project": "/Users/jleechan/projects/worktree_worker3",
  "project_slug": "users-jleechan-projects-worktree-worker3",
  "subject": "Task 3 clarification: conditional tool/schema attachment scope",
  "thread_id": null,
  "to": [
    "codex"
  ]
}
---

## Task 3 Analysis: Conditional Tool/Schema Attachment

Completed Tasks 1 & 2:
- ✅ Bracket-aware parsing confirmed sufficient (json_utils.py:26-76)
- ✅ Added reprompt mechanism for missing fields (llm_service.py:3498-3561)

**Task 3 Implementation Options:**

With JSON-first flows, tools are NOT sent to API. The only "tool schema" is the `tool_requests` section in `game_state_instruction.md` (~200-300 tokens).

**Option A: Conditional System Instruction (Complex)**
- Add dice-likelihood heuristic
- Modify PromptBuilder to conditionally include/exclude tool_requests section
- Requires changes to prompt building pipeline
- Token savings: ~200-300 tokens per call

**Option B: Skip for Now (Simple)**
- Current JSON-first already optimizes by not sending tools to API
- Token savings minimal vs implementation complexity
- Could revisit if token limits become a problem

**Questions:**
1. Is Option A worth the complexity for ~200-300 token savings?
2. Should I focus on Task 4 (jp2 coordination) instead?
3. Is there another interpretation of "conditional tool/schema attachment" I'm missing?

Current implementation changes in llm_service.py:
- Added `_check_missing_required_fields()` helper
- Added `_build_reprompt_for_missing_fields()` helper
- Added reprompt logic after `parse_structured_response()`
- Tests pass (179/181, 2 pre-existing failures)
