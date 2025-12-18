---json
{
  "ack_required": true,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-worktree-worker3"
  ],
  "created": "2025-12-11T20:27:07.858608+00:00",
  "from": "coordinator",
  "id": 86,
  "importance": "normal",
  "project": "worktree_worker3",
  "project_slug": "worktree-worker3",
  "subject": "[TASK] Delete Pre-Computed Dice Logic",
  "thread_id": null,
  "to": [
    "c2"
  ]
}
---

# Task: Delete Pre-Computed Dice Code

**Bead:** `worktree_worker3-0go`
**Priority:** P2
**Branch:** `claude/refactor-llm-to-code-01Sr4NxrZzuzRJ2XDSVFPm9s`

## Context
The pre-computed dice approach never fully worked:
- Hardcoded STR-based attacks
- Hardcoded 1d8 damage for all weapons
- Brittle keyword-based detection

We're reverting to LLM-driven tool loops where the LLM decides what dice to roll.

## Your Task
Delete all pre-computed dice code that was added in commit `31ae35a66`.

### Files to Clean

**1. `mvp_site/game_state.py`** - Remove lines ~1000-1573:
- `ATTACK_PATTERNS`, `SKILL_CHECK_PATTERNS`, `SAVING_THROW_PATTERNS`
- `ADVANTAGE_PATTERNS`, `DISADVANTAGE_PATTERNS`
- `SKILL_ABILITIES` mapping
- `detect_action_type()` function
- `_compute_attack_roll()` function
- `_compute_damage_roll()` function
- `_compute_skill_check()` function
- `compute_combat_results()` function

**2. `mvp_site/llm_service.py`** - Remove pre-computed injection:
- Lines ~1567-1604 (the `detect_action_type` / `compute_combat_results` call)
- Remove imports: `compute_combat_results`, `detect_action_type`

**3. `mvp_site/prompts/game_state_instruction.md`** - Remove:
- `pre_computed_results` instruction section (if present)

**4. Delete test file:**
- `mvp_site/tests/test_precomputed_dice.py`

## DO NOT Delete
- `DICE_ROLL_TOOLS` - Keep this (tool definitions)
- `execute_dice_tool()` - Keep this (tool executor)
- `generate_pre_rolled_dice()` - Keep this (fallback)
- `roll_dice()`, `calculate_attack_roll()`, etc. - Keep these

## Acceptance Criteria
- [ ] All `detect_action_type` references removed
- [ ] All `compute_combat_results` references removed
- [ ] `test_precomputed_dice.py` deleted
- [ ] No grep matches for `pre_computed_results` in codebase
- [ ] Tests still pass (run `./run_tests.sh`)
