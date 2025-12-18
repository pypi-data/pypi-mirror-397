---json
{
  "ack_required": false,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-users-jleechan-projects-worktree-worker3"
  ],
  "created": "2025-12-11T20:55:49.893534+00:00",
  "from": "coordinator",
  "id": 91,
  "importance": "normal",
  "project": "/Users/jleechan/projects/worktree_worker3",
  "project_slug": "users-jleechan-projects-worktree-worker3",
  "subject": "Update: Gemini 3 now uses code_execution + JSON",
  "thread_id": null,
  "to": [
    "codev"
  ]
}
---

## Correction: Gemini 3 code_execution + JSON Enabled

User directed that Gemini 3 SHOULD use code_execution + JSON together. Updated in commit `5320d0142`.

### Changes

**1. `gemini_provider.py`** - Added `generate_content_with_code_execution()`:
```python
# Single-phase for Gemini 3: code_execution + JSON together
config.tools = [types.Tool(code_execution={})]
config.response_mime_type = "application/json"
```

**2. `llm_service.py`** - Routing:
```python
if model_name in constants.GEMINI_3_MODELS:
    return gemini_provider.generate_content_with_code_execution(...)
```

**3. `constants.py`** - Updated table:
```
│ gemini-3-pro-preview│ ✅ Yes │ ✅ Yes │ ✅ YES │ code_execution│
│ gemini-2.x          │ ✅ Yes │ ✅ Yes │ ❌ No  │ tool_use_phased│
```

### Architecture Summary

| Model | Strategy | Phases | Method |
|-------|----------|--------|--------|
| **Gemini 3.x** | code_execution | **1** | Model runs Python in sandbox |
| Gemini 2.x | tool_use_phased | 2 | Tools→JSON phase separation |
| Cerebras/OpenRouter | tool_use | 1-2 | Function calling |

### PR

https://github.com/jleechanorg/worldarchitect.ai/pull/2353
