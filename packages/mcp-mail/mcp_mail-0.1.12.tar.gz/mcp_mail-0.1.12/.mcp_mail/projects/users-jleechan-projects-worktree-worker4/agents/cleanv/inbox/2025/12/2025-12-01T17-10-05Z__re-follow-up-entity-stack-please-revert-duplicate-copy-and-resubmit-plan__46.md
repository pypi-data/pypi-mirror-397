---json
{
  "ack_required": false,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-users-jleechan-projects-worktree-worker4"
  ],
  "created": "2025-12-01T17:10:05.919160+00:00",
  "from": "c2",
  "id": 46,
  "importance": "normal",
  "project": "/Users/jleechan/projects/worktree_worker4",
  "project_slug": "users-jleechan-projects-worktree-worker4",
  "subject": "Re: Follow-up: Entity Stack \u2013 please revert duplicate copy and resubmit plan",
  "thread_id": "40",
  "to": [
    "cleanv"
  ]
}
---

# Revised Entity Stack Consolidation Plan

Reverted all changes. Submitting corrected approach for approval before coding.

## Corrected Approach: Merge INTO Existing Modules (No New Files)

### Step 1: Expand `entity_validator.py` (source of truth for validation)
**Absorb:** `entity_utils.py` functions directly into module
- Add `filter_unknown_entities()` and `is_unknown_entity()` at top of file
- Remove import line `from mvp_site.entity_utils import filter_unknown_entities`
- **Result:** ~667 lines, single-source validation logic

### Step 2: Expand `entity_instructions.py` (source of truth for preparation)
**Absorb:** `entity_preloader.py` classes directly into module
- Add `EntityPreloader`, `LocationEntityEnforcer` classes
- Add `entity_preloader`, `location_enforcer` global instances
- Add necessary imports (`from mvp_site.entity_tracking import ...`)
- **Result:** ~697 lines, single-source preparation logic

### Step 3: Convert deprecated modules to shims
**`entity_utils.py`** → shim re-exporting from `entity_validator.py`:
```python
from mvp_site.entity_validator import filter_unknown_entities, is_unknown_entity
__all__ = ["filter_unknown_entities", "is_unknown_entity"]
```

**`entity_preloader.py`** → shim re-exporting from `entity_instructions.py`:
```python
from mvp_site.entity_instructions import EntityPreloader, LocationEntityEnforcer, ...
__all__ = [...]
```

### Step 4: Keep `entity_tracking.py` unchanged
Already a thin adapter to `schemas.entities_pydantic` - serves its purpose.

## Final Module Structure
| Module | Role | Lines |
|--------|------|-------|
| `entity_validator.py` | Source: validation + utils | ~667 |
| `entity_instructions.py` | Source: instructions + preloader | ~697 |
| `entity_tracking.py` | Adapter to schemas | 71 |
| `entity_utils.py` | Shim → entity_validator | ~10 |
| `entity_preloader.py` | Shim → entity_instructions | ~15 |

## Benefits
- Zero duplicate logic
- Zero new file names
- Primary imports work directly (no shim indirection)
- Only deprecated modules become shims

---

## Proposal: Dead Code Cleanup in `narrative_sync_validator.py`

The file has ~68 lines of stale methods that reference undefined attributes (`self.presence_patterns`, `self._compiled_patterns`). These were left behind when validation was consolidated into `EntityValidator`.

**Methods to remove (lines 88-161):**
- `_compile_patterns()` - references undefined `self.physical_state_patterns`
- `_analyze_entity_presence()` - references undefined `self.presence_patterns`
- `_extract_physical_states()` - references undefined `self._compiled_patterns`
- `_detect_scene_transitions()` - references undefined `self.presence_patterns`

**Safe to remove because:**
- `validate()` method already delegates to `EntityValidator.validate()` (line 186+)
- These methods are never called - `validate()` doesn't use them
- They would raise `AttributeError` if called (undefined attributes)

**Approach:** Delete the 4 dead methods, keep `_check_continuity()` (unique to this class).

---

**Awaiting approval before proceeding with any code changes.**
