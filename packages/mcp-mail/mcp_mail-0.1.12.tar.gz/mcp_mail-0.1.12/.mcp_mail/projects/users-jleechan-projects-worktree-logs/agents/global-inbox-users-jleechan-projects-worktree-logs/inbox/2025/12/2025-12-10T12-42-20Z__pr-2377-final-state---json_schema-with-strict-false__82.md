---json
{
  "ack_required": false,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-users-jleechan-projects-worktree-logs"
  ],
  "created": "2025-12-10T12:42:20.550682+00:00",
  "from": "JsonSchemaFix",
  "id": 82,
  "importance": "high",
  "project": "/Users/jleechan/projects/worktree_logs",
  "project_slug": "users-jleechan-projects-worktree-logs",
  "subject": "PR #2377 Final State - json_schema with strict:false",
  "thread_id": null,
  "to": [
    "User"
  ]
}
---

# PR #2377 Summary: json_schema Migration

## Problem Solved
Cerebras API with legacy `{"type": "json_object"}` was returning schema config `{"type": "object"}` instead of actual content under high token context.

## Solution
Use `json_schema` type with `strict: false` instead of legacy `json_object`.

### Why strict:false?
The game design requires **dynamic choice keys** like:
- `explore_tavern`, `attack_goblin`, `talk_to_innkeeper`
- `god:option_1`, `god:return_story`

These cannot be pre-defined in a strict JSON schema. Strict mode requires ALL object properties to be explicitly listed.

## Final Schema Approach
```python
# Top-level structure enforced
"narrative": {"type": "string"}      # required
"entities_mentioned": {"type": "array"}  # required
"planning_block": {"type": "object"}     # flexible internals

# Internal planning_block structure validated by
# narrative_response_schema.py AFTER response received
```

## Provider Status
| Provider | Mode | Dynamic Keys | 
|----------|------|--------------|
| Cerebras | json_schema strict:false | ✅ Works |
| Gemini | response_json_schema | ✅ Works |
| OpenRouter (Grok) | json_schema strict:false | ✅ Works |
| OpenRouter (Llama) | json_object | ⚠️ No schema enforcement |

## Commits (7 total)
1. `175b76534` - feat(cerebras): migrate to json_schema
2. `6589cc2b3` - fix(openrouter): update grok model
3. `6c49268be` - feat(providers): add json_schema to Gemini/OpenRouter
4. `2188941db` - chore(beads): close BD-fsr
5. `37695594a` - feat(smoke-tests): add openrouter_grok provider
6. `4949ac776` - fix(schema): correct planning_block to object type
7. `99aee74b0` - **fix(schema): use strict:false for dynamic choice keys**

## PR URL
https://github.com/jleechanorg/worldarchitect.ai/pull/2377
