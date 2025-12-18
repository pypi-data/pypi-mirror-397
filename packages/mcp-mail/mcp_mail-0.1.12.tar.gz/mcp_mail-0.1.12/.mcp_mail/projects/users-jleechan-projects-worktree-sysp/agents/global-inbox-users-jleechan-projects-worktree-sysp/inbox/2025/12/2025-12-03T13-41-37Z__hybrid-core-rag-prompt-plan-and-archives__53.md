---json
{
  "ack_required": false,
  "attachments": [],
  "bcc": [],
  "cc": [
    "global-inbox-users-jleechan-projects-worktree-sysp"
  ],
  "created": "2025-12-03T13:41:37.938438+00:00",
  "from": "syspv",
  "id": 53,
  "importance": "normal",
  "project": "/Users/jleechan/projects/worktree_sysp",
  "project_slug": "users-jleechan-projects-worktree-sysp",
  "subject": "Hybrid core+RAG prompt plan and archives",
  "thread_id": null,
  "to": [
    "sysp"
  ]
}
---

Hi sysp,

Context: We need a hybrid prompt approach (pinned core header + retrieval) to avoid truncation losses. No code changes yet beyond removing nonexistent commands.

What I’ve done:
- Archived prompt versions: `prompt_archive/older/` (origin/main) and `prompt_archive/dec_2025/` (current).
- Design + impl plan: `roadmap/rag_hybrid_prompt_design.md` (self-contained overview of WorldArchitect.AI + hybrid design) and `roadmap/rag_hybrid_impl_plan.md` (tasks, deliverables). Both also copied to `~/Downloads/`.
- Prompt cleanup: removed `rewind list` and `save state` commands from `mvp_site/prompts/mechanics_system_instruction.md` (they weren’t implemented).
- Size snapshot: prompts are now 45,982 bytes vs 173,664 bytes original (~73.5% reduction). If we aim for ~50% without RAG, keep core schema/safety/time/dice/XP essentials; defer world-gen/long narrative guidance.
- MCP mail: registered agent `syspv` (me) for coordination.

Next steps you could pick up:
1) If staying non-RAG: trim further per “essentials” list in design doc.
2) If RAG: implement build/retriever per `rag_hybrid_impl_plan.md` (core header, hybrid BM25+dense, assembly, tests, logging).

Ping me if you want specific chunk priorities or to align on embedding backend.

— syspv
