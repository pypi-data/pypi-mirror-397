---json
{
  "ack_required": true,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-worktree-worker3"
  ],
  "created": "2025-12-11T20:27:08.627460+00:00",
  "from": "coordinator",
  "id": 87,
  "importance": "normal",
  "project": "worktree_worker3",
  "project_slug": "worktree-worker3",
  "subject": "[TASK] Update llm_service.py Routing + Strategy Selection",
  "thread_id": null,
  "to": [
    "c3"
  ]
}
---

# Task: Update LLM Service Routing

**Bead:** `worktree_worker3-620`
**Priority:** P2
**Branch:** `claude/refactor-llm-to-code-01Sr4NxrZzuzRJ2XDSVFPm9s`

## Context
Tool loops are now restored. Need to wire up `llm_service.py` to use the correct
provider's `generate_content_with_tool_loop()` based on model/provider.

## Your Task

### 1. Update `mvp_site/constants.py`
```python
# Models that support tool use (function calling)
MODELS_WITH_TOOL_USE = {
    # Cerebras
    "qwen-3-235b-a22b-instruct-2507",
    "zai-glm-4.6",
    "llama-3.3-70b",
    # OpenRouter
    "meta-llama/llama-3.1-70b-instruct",
}

# Gemini 3 models (support code_execution + JSON together)
GEMINI_3_MODELS = {
    "gemini-3-pro-preview",
}

def get_dice_roll_strategy(model_name: str, provider: str) -> str:
    """Determine dice rolling strategy for a model."""
    if provider == "gemini":
        if model_name in GEMINI_3_MODELS:
            return "code_execution"  # Single-phase
        return "tool_use_phased"  # Two-phase for 2.x
    if model_name in MODELS_WITH_TOOL_USE:
        return "tool_use"
    return "precompute"  # Fallback
```

### 2. Update `mvp_site/llm_service.py`
In `_call_llm_api()`, route to the correct provider:

```python
from mvp_site.game_state import DICE_ROLL_TOOLS

def _call_llm_api(...):
    strategy = get_dice_roll_strategy(model_name, provider)
    
    if provider == "gemini":
        if strategy == "code_execution":
            # Gemini 3: code_execution + JSON in one call
            return gemini_provider.generate_json_mode_content(
                ..., enable_code_execution=True
            )
        else:
            # Gemini 2.x: two-phase
            return gemini_provider.generate_content_with_tool_loop(
                ..., tools=DICE_ROLL_TOOLS
            )
    
    elif provider == "cerebras":
        return cerebras_provider.generate_content_with_tool_loop(
            ..., tools=DICE_ROLL_TOOLS
        )
    
    elif provider == "openrouter":
        return openrouter_provider.generate_content_with_tool_loop(
            ..., tools=DICE_ROLL_TOOLS
        )
```

### 3. Update Tests
Ensure `mvp_site/tests/test_code_execution_dice_rolls.py` has tests for:
- Strategy selection by provider
- Tool loop invocation

## Files to Modify
- `mvp_site/constants.py`
- `mvp_site/llm_service.py`
- `mvp_site/tests/test_code_execution_dice_rolls.py`

## Acceptance Criteria
- [ ] `get_dice_roll_strategy()` returns correct strategy per provider/model
- [ ] `_call_llm_api()` routes to correct provider's tool loop
- [ ] `DICE_ROLL_TOOLS` passed to all tool loop calls
- [ ] Tests verify routing logic
