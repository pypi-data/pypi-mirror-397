---json
{
  "ack_required": true,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-worktree-worker3"
  ],
  "created": "2025-12-11T20:27:07.051755+00:00",
  "from": "coordinator",
  "id": 85,
  "importance": "high",
  "project": "worktree_worker3",
  "project_slug": "worktree-worker3",
  "subject": "[TASK] Add Gemini Provider Tool Loop with Phase Separation",
  "thread_id": null,
  "to": [
    "c1"
  ]
}
---

# Task: Add Gemini Tool Loop

**Bead:** `worktree_worker3-8pt`
**Priority:** P1
**Branch:** `claude/refactor-llm-to-code-01Sr4NxrZzuzRJ2XDSVFPm9s`

## Context
Revert is complete (`ad0024660`). Tool loops restored for Cerebras/OpenRouter.
Gemini needs special handling due to API limitation.

## The Problem
Gemini API rejects: `"Function calling with a response mime type: 'application/json' is unsupported"`
- Gemini 2.x: Cannot use tools + JSON mode together
- Gemini 3: CAN use code_execution + JSON mode together

## Your Task
Implement `generate_content_with_tool_loop()` in `mvp_site/llm_providers/gemini_provider.py`

### For Gemini 3 (gemini-3-pro-preview):
```python
# Single phase - code_execution + JSON mode together
response = model.generate_content(
    prompt,
    tools=[{"code_execution": {}}],
    generation_config={
        "response_mime_type": "application/json",
        "response_schema": schema
    }
)
```

### For Gemini 2.x (gemini-2.0-flash, gemini-2.5-flash):
```python
# Phase 1: tools ON, JSON OFF
response1 = generate_content(prompt, tools=DICE_ROLL_TOOLS, json_mode=False)
tool_results = execute_tools(response1.tool_calls)

# Phase 2: tools OFF, JSON ON  
response2 = generate_json_mode_content(prompt + tool_results, tools=None)
```

## Files to Modify
- `mvp_site/llm_providers/gemini_provider.py`
- `mvp_site/constants.py` (add GEMINI_3_MODELS set)

## Acceptance Criteria
- [ ] Gemini 3 uses single-phase code_execution + JSON
- [ ] Gemini 2.x uses two-phase separation
- [ ] Function signature matches Cerebras/OpenRouter pattern
- [ ] Tests pass

## Reference
- Roadmap: `roadmap/unified_two_phase_dice_architecture.md`
- Cerebras tool loop: `mvp_site/llm_providers/cerebras_provider.py:generate_content_with_tool_loop()`
