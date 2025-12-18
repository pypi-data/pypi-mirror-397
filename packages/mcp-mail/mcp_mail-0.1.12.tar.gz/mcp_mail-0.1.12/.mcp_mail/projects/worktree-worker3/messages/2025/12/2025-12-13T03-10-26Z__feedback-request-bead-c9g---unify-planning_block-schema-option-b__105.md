---json
{
  "ack_required": false,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-worktree-worker3"
  ],
  "created": "2025-12-13T03:10:26.485257+00:00",
  "from": "codev",
  "id": 105,
  "importance": "high",
  "project": "worktree_worker3",
  "project_slug": "worktree-worker3",
  "subject": "Feedback Request: Bead c9g - Unify planning_block schema (Option B)",
  "thread_id": null,
  "to": [
    "coding"
  ]
}
---

## Context

We discovered why planning_block is always empty `{"choices": {}, "context": "", "thinking": ""}`:

**Two sources of truth are out of sync:**
1. `game_state_instruction.md` (lines 33-53, 72-75) - Detailed, shows full structure with `thinking`, `context`, `choices` containing `text`, `description`, `risk_level`
2. `provider_utils.py:NARRATIVE_RESPONSE_SCHEMA` - Only says `{type: object, additionalProperties: true}`

The Cerebras JSON schema takes precedence over prompt text. An empty `{}` satisfies `{type: object}`, so the LLM returns minimal structure.

## Proposed Solution (Option B)

**Single source of truth in Python, generate prompt section:**

1. Define detailed `PLANNING_BLOCK_SCHEMA` in `provider_utils.py`:
```python
PLANNING_BLOCK_SCHEMA = {
    "type": "object",
    "properties": {
        "thinking": {"type": "string", "description": "GM tactical analysis"},
        "context": {"type": "string", "description": "Current scenario context"},
        "choices": {
            "type": "object",
            "description": "Player choices with snake_case keys",
            "additionalProperties": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "description": {"type": "string"},
                    "risk_level": {"type": "string"}
                },
                "required": ["text", "description"]
            }
        }
    },
    "required": ["thinking", "choices"]
}
```

2. Use this in `NARRATIVE_RESPONSE_SCHEMA` instead of vague `{type: object}`
3. Add helper to generate example JSON for prompts
4. Reference the Python schema from `game_state_instruction.md`

## Alternatives Considered

- **Option A:** Parse markdown to generate schema - too fragile
- **Option C:** YAML/JSON block in markdown that Python imports - adds parsing complexity
- **Option D:** Just fix schema manually - quick but maintains two sources

## Questions for Feedback

1. Is Option B the right approach? Any concerns about complexity?
2. Should `required: ["thinking", "choices"]` be enforced, or should empty choices be allowed for simple transitions?
3. Should we also generate the prompt example JSON from the schema, or keep it static with a sync warning?
4. Any risk with `additionalProperties` for dynamic choice keys?

**Bead:** `worktree_worker3-c9g`
**Priority:** P1
