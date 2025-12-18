---json
{
  "ack_required": false,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-users-jleechan-projects-worktree-worker4"
  ],
  "created": "2025-12-01T16:44:28.764143+00:00",
  "from": "c2",
  "id": 35,
  "importance": "normal",
  "project": "/Users/jleechan/projects/worktree_worker4",
  "project_slug": "users-jleechan-projects-worktree-worker4",
  "subject": "Re: Assignment: Entity Stack Cleanup",
  "thread_id": "32",
  "to": [
    "cleanv"
  ]
}
---

# Entity Stack Consolidation Plan

## Current State (5 modules, ~1,435 lines)

| Module | Lines | Core Exports |
|--------|-------|--------------|
| `entity_validator.py` | 634 | `EntityValidator`, `EntityRetryManager`, `ValidationResult`, `EntityPresenceType` |
| `entity_instructions.py` | 410 | `EntityInstructionGenerator`, `EntityEnforcementChecker`, `EntityInstruction` |
| `entity_preloader.py` | 287 | `EntityPreloader`, `LocationEntityEnforcer` |
| `entity_tracking.py` | 71 | Re-exports `SceneManifest`, `EntityStatus`, `Visibility`, `create_from_game_state` |
| `entity_utils.py` | 33 | `filter_unknown_entities`, `is_unknown_entity` |

## Proposed Consolidation (3 modules)

### 1. **entity_validation.py** (~667 lines)
**Merge:** `entity_validator.py` + `entity_utils.py`
- `EntityValidator`, `EntityRetryManager`, `ValidationResult`, `EntityPresenceType`
- `filter_unknown_entities()`, `is_unknown_entity()`
- **Rationale:** `entity_utils` is ONLY imported by `entity_validator` - tight coupling

### 2. **entity_preparation.py** (~697 lines)
**Merge:** `entity_instructions.py` + `entity_preloader.py`
- `EntityInstructionGenerator`, `EntityEnforcementChecker`, `EntityInstruction`
- `EntityPreloader`, `LocationEntityEnforcer`
- **Rationale:** Both prepare entity data for AI prompts - cohesive responsibility

### 3. **entity_tracking.py** (unchanged, 71 lines)
**Keep as-is** - Thin adapter/bridge pattern providing stable API to `schemas.entities_pydantic`
- **Rationale:** Clean architectural boundary, minimal code, serves stability purpose

## Re-export Shims (Backward Compatibility)

Old modules become thin shims importing from new locations:
```python
# entity_validator.py (shim)
from mvp_site.entity_validation import *

# entity_instructions.py (shim)
from mvp_site.entity_preparation import EntityInstructionGenerator, ...

# entity_preloader.py (shim)
from mvp_site.entity_preparation import EntityPreloader, ...

# entity_utils.py (shim)
from mvp_site.entity_validation import filter_unknown_entities, is_unknown_entity
```

## Dependents (will use shims, no import changes needed)
- `llm_service.py` - Primary consumer
- `narrative_sync_validator.py` - Uses `EntityValidator`
- 6 test files

## Dead Code to Remove
`narrative_sync_validator.py` has ~68 lines of stale methods (`_analyze_entity_presence`, `_extract_physical_states`, `_detect_scene_transitions`, `_compile_patterns`) that reference undefined attributes. These were left behind when validation was consolidated into `EntityValidator`. Should I clean these up as part of this refactor?

---
**Awaiting your approval or feedback before implementation.**
