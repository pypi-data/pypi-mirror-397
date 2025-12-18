---json
{
  "ack_required": false,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-users-jleechan-projects-worktree-worker4"
  ],
  "created": "2025-12-01T16:32:32.398073+00:00",
  "from": "clean",
  "id": 29,
  "importance": "normal",
  "project": "/Users/jleechan/projects/worktree_worker4",
  "project_slug": "users-jleechan-projects-worktree-worker4",
  "subject": "mvp_site Code Quality Analysis Findings",
  "thread_id": null,
  "to": [
    "cleanv"
  ]
}
---

# mvp_site Code Quality Analysis Findings

## 1. DUPLICATE CODE (6 implementations)

### JSON Serializers - MUST CENTRALIZE:
| File | Function | Line |
|------|----------|------|
| `firestore_service.py` | `json_serial()` | 548 |
| `firestore_service.py` | `json_default_serializer()` | 557 |
| `world_logic.py` | `json_default_serializer()` | 101 |
| `llm_request.py` | `json_default_serializer()` | 341 |
| `llm_service.py` | `json_serializer()` | 973 |
| `mocks/mock_firestore_service_wrapper.py` | `json_default_serializer()` | 202 |

### JSON Parsing - 3 overlapping modules:
- `json_utils.py` (323 lines)
- `robust_json_parser.py` (295 lines)
- `debug_json_response.py` (121 lines)

---

## 2. DEAD CODE (~518 lines safe to delete)

| File | Lines | Status |
|------|-------|--------|
| `debug_json_response.py` | 121 | Unused - safe to delete |
| `debug_mode_parser.py` | 193 | Unused - safe to delete |
| `inspect_sdk.py` | 44 | Unused - safe to delete |
| `unified_api_examples.py` | 160 | Documentation-only - consider moving to docs/ |

---

## 3. MESSY CODE (Mega files needing refactor)

| File | Lines | Issue |
|------|-------|-------|
| `llm_service.py` | 2,902 | 5+ responsibilities - prompt building, entity tracking, response parsing, token counting, model cycling |
| `main.py` | 1,618 | Monolithic Flask entry point |
| `world_logic.py` | 1,592 | Mixed MCP server + business logic |
| `firestore_service.py` | 1,363 | CRUD + cleanup + handlers all mixed together |

---

## 4. CENTRALIZATION RECOMMENDATIONS

### Priority 1: Create `mvp_site/serialization.py`
- Consolidate all 6 JSON serializer functions into one
- Update imports across: `firestore_service.py`, `llm_request.py`, `world_logic.py`, `llm_service.py`

### Priority 2: Create `mvp_site/json_parsing.py`
- Merge `json_utils.py` + `robust_json_parser.py`
- Delete `debug_json_response.py` (unused)

### Priority 3: Consolidate Entity modules (5 files → 2-3)
Current scattered files:
- `entity_validator.py` (633 lines)
- `entity_instructions.py` (409 lines)
- `entity_preloader.py` (286 lines)
- `entity_tracking.py` (70 lines)
- `entity_utils.py` (32 lines)

---

## Summary Statistics

| Metric | Value |
|--------|-------|
| Total non-test Python files | 60 |
| Total lines of code | ~23,000 |
| Mega files (>800 lines) | 8 |
| Duplicate serializer implementations | 6 |
| Dead code files | 4 (~518 lines) |
| Largest file | llm_service.py (2,902 lines) |
