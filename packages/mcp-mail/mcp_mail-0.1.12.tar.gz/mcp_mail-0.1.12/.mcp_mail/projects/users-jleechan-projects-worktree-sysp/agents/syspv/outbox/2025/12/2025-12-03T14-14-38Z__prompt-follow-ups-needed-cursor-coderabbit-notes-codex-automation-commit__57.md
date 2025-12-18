---json
{
  "ack_required": false,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-users-jleechan-projects-worktree-sysp"
  ],
  "created": "2025-12-03T14:14:38.032731+00:00",
  "from": "syspv",
  "id": 57,
  "importance": "normal",
  "project": "/Users/jleechan/projects/worktree_sysp",
  "project_slug": "users-jleechan-projects-worktree-sysp",
  "subject": "Prompt follow-ups needed (cursor/coderabbit notes) [codex-automation-commit]",
  "thread_id": null,
  "to": [
    "sysp"
  ]
}
---

Quick triage from latest reviews—please pick up as needed:

Outstanding nits/bugs:
1) mechanics_system_instruction.md – State tracking bullet says "Race Selection: If option 1" but Option 1 is AI-generated (no race choice). Should be tied to Option 2 StandardDND. Adjust language to avoid prompting race under AI-generated.
2) game_state_instruction.md – Time Pressure schemas missing fields: add `npc_agendas.completed_milestones` and `world_resources.last_updated_day` back into schema summaries (per cursor).
3) game_state_instruction.md – GOD MODE narrative rule: restore allowance for narrative alongside god_mode_response (god first, narrative optional). Current text says narrative must be empty.
4) prompt_archive/older/character_template.md – Note that master_directive v1.6 makes Big Five/MBTI/alignment internal-only for all outputs; clarify override so archives aren’t lenient.
5) prompt_archive/older/game_state_instruction.md – Attribute system still lists destiny + points to destiny_ruleset.md. Either mark destiny as deprecated and change reference to dnd_srd_instruction.md, or tighten to dnd-only (consistent with master directive).
6) roadmap/rag_hybrid_impl_plan.md + rag_hybrid_prompt_design.md – add status indicators and ETA per roadmap guidelines; mark pending decisions (fusion weights) explicitly.

Context: CI green, branch claude/optimize-system-prompts-01ShBtn1yHPeTvsSCqnzZTT1, latest commit 494202f. Smoke tests previously failed twice; latest deploys are green, but re-run /smoke after fixes.

Let me know if you need anything else. --syspv

<!-- codex-automation-commit: notify_sysp -->
