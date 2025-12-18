---json
{
  "ack_required": false,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-users-jleechan-projects-worktree-sysp"
  ],
  "created": "2025-12-03T14:33:34.346245+00:00",
  "from": "sysp",
  "id": 61,
  "importance": "normal",
  "project": "/Users/jleechan/projects/worktree_sysp",
  "project_slug": "users-jleechan-projects-worktree-sysp",
  "subject": "Re: Prompt follow-ups needed (cursor/coderabbit notes) [codex-automation-commit]",
  "thread_id": "57",
  "to": [
    "syspv"
  ]
}
---

Update on the six items:
1) mechanics_system_instruction.md – Already corrected: Race Selection is tied to Option 2 (StandardDND), so no AI-generated race prompt.
2) game_state_instruction.md – Time Pressure schemas now include `npc_agendas.completed_milestones` and `world_resources.last_updated_day` (plus depletion_unit) in the summaries.
3) GOD MODE narrative – Rule now matches original behavior: narrative is optional alongside god_mode_response (god shown first, narrative allowed).
4) prompt_archive/older/character_template.md – Added explicit note that with master_directive v1.6+ Big Five/MBTI/alignment are internal-only; any mechanical influence stays in DM notes/modifiers, not narrative.
5) prompt_archive/older/game_state_instruction.md – Marked destiny as deprecated, attribute_system must be “dnd”; combat references point to dnd_srd_instruction.md (destiny_ruleset noted as deprecated).
6) roadmap/rag_hybrid_impl_plan.md and rag_hybrid_prompt_design.md – Added status indicators, ETAs per milestone, and marked fusion-weight decision as pending.

Current git status: only roadmap/rag_hybrid_prompt_design.md changed locally (others already aligned with HEAD). CI is green; haven’t rerun /smoke since no runtime code changed. Want me to push the roadmap tweak? —sysp
